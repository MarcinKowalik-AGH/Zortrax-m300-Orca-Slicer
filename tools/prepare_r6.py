"""Upgrade R5 source generator to Orca2.5.0 and 305/105 operating envelope.
All non-support materials stay visible/selectable with genuine temperatures.
No printer access or firmware installation; 305C is not a PEEK print claim.
"""
from pathlib import Path
import json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]

def main():
    script=(ROOT/'tools/build_native_r5.py').read_text().replace('R5','R6').replace('r5','r6')
    script=script.replace("CATALOG_ONLY={'Z-PEEK','Z-PEI 1010','Z-PEI 9085','Z-SUPPORT High-Temp','Z-SUPPORT ATP 130'}",'CATALOG_ONLY=set()')
    script=script.replace("materials=sorted(set(bases)|{r['material'] for r in beta if r['material'].startswith('Z-')})", "materials=sorted(m for m in (set(bases)|{r['material'] for r in beta if r['material'].startswith('Z-')}) if not m.startswith('Z-SUPPORT'))")
    script=script.replace("'02.03.02.05'", "'02.05.00.06'")
    script=script.replace("obj.update(type=kind,instantiation='true',", "obj.update(version='2.5.0.0',type=kind,instantiation='true',")
    script=script.replace("actual_t=t if unsupported else min(265,t)","actual_t=t  # Retain genuine material requirement, including PEEK400/PEI360-370.")
    script=script.replace("current working ceiling265 for non-catalog entries", "OEM value retained; host setpoint ceiling305 enforced separately")
    script=script.replace("num(actual_t+20 if unsupported else min(270,actual_t+20))", "num(actual_t+20 if actual_t>305 else min(305,actual_t+20))")
    script=script.replace("if bed>105:warnings.append('Source bed/chamber above M300 limits; catalogue-only material.')", "if bed>105:warnings.append(f'Source bed {num(bed)}C exceeds configured105C; listed but not qualified at reduced bed temperature.')\n   if actual_t>305:warnings.append(f'VISIBLE/SELECTABLE: required nozzle {num(actual_t)}C exceeds this305C machine. START_PRINT must reject before heat or motion; no claim of305C printability.')")
    script=script.replace("'catalog_only':unsupported,'warnings':warnings}", "'catalog_only':False,'within_305_limit':actual_t<=305,'source_bed_temperature':bed,'warnings':warnings}")
    script=script.replace("'host_changed':False}", "'host_changed':False,'orca_version':'2.5.0','target_limits':{'extruder':305,'heater_bed':105},'hardware_test_source':'user report 2026-11-11; not a test of every material'}")
    (ROOT/'tools/build_native_r6.py').write_text(script)
    installer=(ROOT/'tools/install_native_r5.py').read_text().replace('R5','R6')
    installer=installer.replace('100 filament entries, 84 process presets','76 filament entries, 80 process presets')
    (ROOT/'tools/install_native_r6.py').write_text(installer)
    test=(ROOT/'tests/audit_native_r5.py').read_text().replace('R5','R6').replace('2.3.2','2.5.0')
    test=test.replace("len(v['filament_list'])==100 and len(v['process_list'])==84", "len(v['filament_list'])==76 and len(v['process_list'])==80")
    test=test.replace("assert float(f['nozzle_temperature_initial_layer'][0])<=265", "assert float(f['nozzle_temperature_initial_layer'][0])<=450\n   assert not mat.startswith('Z-SUPPORT') and f['filament_is_support']==['0'] and f['filament_printable']==['1']")
    test=test.replace("summary['material_pass']==80", "summary['material_pass']==76")
    (ROOT/'tests/audit_native_r6.py').write_text(test)
    if (ROOT/'native').exists():shutil.rmtree(ROOT/'native')
    subprocess.run([sys.executable,str(ROOT/'tools/build_native_r6.py')],check=True)
    c=json.loads((ROOT/'evidence/R6_CATALOG.json').read_text())
    assert len(c['materials'])==19 and not any(n.startswith('Z-SUPPORT') for n in c['materials'])
    assert (c['machine_count'],c['filament_count'],c['process_count'])==(4,76,80)
    assert {'Z-PEEK','Z-PEI 1010','Z-PEI 9085','Z-HIPS'} <= set(c['materials'])
    # Old presets are retained solely as provenance, not the active selector.
    snapshot=ROOT/'archive/pre_R6'
    for name in ('presets','nozzle_presets'):
        if (ROOT/name).exists():
            snapshot.mkdir(parents=True,exist_ok=True)
            if (snapshot/name).exists():shutil.rmtree(snapshot/name)
            shutil.move(str(ROOT/name),str(snapshot/name))
    for name in ('validate.yml','nozzle-validation.yml','native-r5.yml'):
        p=ROOT/'.github/workflows'/name
        if p.exists():
            dst=ROOT/'archive/pre_R6/workflows'/name;dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.move(str(p),str(dst))
    print(json.dumps({'revision':'R6','materials':c['materials'],'printers':4,'filaments':76,'processes':80,'support_profiles':0}))

if __name__=='__main__':main()
