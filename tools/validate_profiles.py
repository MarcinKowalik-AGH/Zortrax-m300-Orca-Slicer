#!/usr/bin/env python3
"""Offline structural and source/bundle consistency checks, no printer access."""
import hashlib,json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NAME='Zortrax_M300_Classic_0p20_MicroSwiss_R3.orca_printer'

def main():
    bundle=ROOT/'profiles'/NAME
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        names=z.namelist();assert len(names)==len(set(names))==21
        m=json.loads(z.read('bundle_structure.json'))
        assert len(m['printer_config'])==len(m['process_config'])==1
        assert len(m['filament_config'])==18
        assert set(names)==set(['bundle_structure.json']+m['printer_config']+m['process_config']+m['filament_config'])
        for name in names:
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            assert (ROOT/'presets'/name).read_bytes()==z.read(name),name
        p=json.loads(z.read(m['printer_config'][0]));q=json.loads(z.read(m['process_config'][0]))
        assert len(p)==144 and len(q)==334
        assert p['gcode_flavor']=='klipper' and p['use_relative_e_distances']=='1'
        assert p['machine_end_gcode'].strip()=='END_PRINT'
        assert p['machine_pause_gcode'].strip()=='PAUSE'
        assert 'START_PRINT EXTRUDER_TEMP=' in p['machine_start_gcode']
        assert 'SET_PRESSURE_ADVANCE ADVANCE=0' in p['machine_start_gcode']
        assert q['layer_height']=='0.2' and q['post_process']==[]
        assert q['compatible_printers']==[p['name']]
        unsupported=[]
        for name in m['filament_config']:
            f=json.loads(z.read(name));assert len(f)==123
            assert f['compatible_printers']==[p['name']]
            assert f['filament_settings_id']==[f['name']]
            assert f['enable_pressure_advance']==['1'] and f['pressure_advance']==['0']
            assert f['adaptive_pressure_advance']==['0']
            for k,v in f.items():
                if '_plate_temp' in k:assert 0<=float(v[0])<=105,(name,k)
            if f['name'].startswith('Z-PEEK '):unsupported.append(f['name'])
            else:
                assert float(f['nozzle_temperature'][0])<=265
                assert float(f['nozzle_temperature_initial_layer'][0])<=265
        assert len(unsupported)==1
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        digest,path=line.split('  ',1)
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    assert not any((ROOT/n).exists() for n in ['host','mcu','frontend'])
    print(json.dumps({'status':'PASS','printer':1,'process':1,'materials':18,'schema_fields':[144,334,123],'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'hardware_test':False}))

if __name__=='__main__':main()
