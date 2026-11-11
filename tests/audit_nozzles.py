#!/usr/bin/env python3
"""Offline Orca 2.3.2 audit for nozzle variants. No printer access or deployment.
Only metadata type/from are adapted in scratch CLI files, as in the R3 audit.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import zipfile
from gcode_checks import test_stl, override, scalar

ROOT = Path(__file__).resolve().parents[1]
NUMBER = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)'
WORDS = re.compile(r'([A-Z])('+NUMBER+r')')
WIDTHS = ('line_width', 'outer_wall_line_width', 'inner_wall_line_width',
          'sparse_infill_line_width', 'internal_solid_infill_line_width',
          'top_surface_line_width', 'initial_layer_line_width', 'support_line_width')


def inspect(text, effective, p, q, f, expected_pa):
    errors = []
    diameter = float(p['nozzle_diameter'][0])
    for key, expected in [('nozzle_diameter', diameter), ('filament_diameter', 1.75),
                          ('layer_height', .2), ('initial_layer_print_height', .2),
                          ('filament_flow_ratio', float(f['filament_flow_ratio'][0])),
                          ('filament_max_volumetric_speed', float(f['filament_max_volumetric_speed'][0]))]:
        if not math.isclose(float(scalar(effective.get(key, ['nan']))), expected, abs_tol=1e-8):
            errors.append('Incorrect effective '+key)
    for key in WIDTHS:
        if str(scalar(effective.get(key))) != q[key]: errors.append('Width mismatch: '+key)
    commands = [line.split(';', 1)[0].strip() for line in text.splitlines() if line.split(';', 1)[0].strip()]
    expected_start = 'START_PRINT EXTRUDER_TEMP=%s BED_TEMP=%s MESH=AUTO' % (
        f['nozzle_temperature_initial_layer'][0], f['hot_plate_temp_initial_layer'][0])
    starts = [i for i, line in enumerate(commands) if line.startswith('START_PRINT ')]
    if len(starts) != 1 or commands[starts[0]] != expected_start: errors.append('Incorrect START_PRINT')
    if commands.count('END_PRINT') != 1: errors.append('Missing or duplicate END_PRINT')
    start = starts[0] if starts else -1
    if any(re.match(r'M(?:104|109|140|190)\b', line) for line in commands[:max(0, start)]):
        errors.append('Duplicated pre-start heating')
    pa = []
    for i, line in enumerate(commands):
        if line.startswith('SET_PRESSURE_ADVANCE '):
            m = re.search(r'\bADVANCE=('+NUMBER+')', line)
            if m: pa.append((i, float(m[1])))
    if not any(i < start and v == 0 for i, v in pa): errors.append('PA not zeroed before start')
    if not any(i > start and abs(v-expected_pa) < 1e-8 for i, v in pa): errors.append('Per-filament PA not applied')
    if any(line.split()[0] in {'M82', 'G10', 'G11', 'M201', 'M203', 'M205'} for line in commands):
        errors.append('Unexpected extrusion/firmware-limit command')
    if any('ACCEL_TO_DECEL=' in line for line in commands): errors.append('Obsolete ACCEL_TO_DECEL')
    feed = None; relative_e = False; absolute_xyz = True; position = [None, None, None]
    retracts = []; unretracts = []; hops = []; xy_extrusions = 0
    layer_z = None; max_accel = 0.; peak_area = 0.; peak_flow = 0.; excessive_area = []
    filament_area = math.pi*1.75**2/4
    area_limit = 4*diameter**2
    small_extrude_allowance = diameter*area_limit/filament_area
    for raw in text.splitlines():
        if raw.startswith(';Z:'): layer_z = float(raw[3:])
        code = raw.split(';', 1)[0].strip()
        if not code: continue
        command = code.split()[0]
        if command == 'M83': relative_e = True
        elif command == 'M82': relative_e = False
        elif command == 'G90': absolute_xyz = True
        elif command == 'G91': absolute_xyz = False
        if command == 'M204':
            m = re.search(r'\bS('+NUMBER+')', code)
            if m: max_accel = max(max_accel, float(m[1]))
        for m in re.finditer(r'\bACCEL=('+NUMBER+')', code): max_accel = max(max_accel, float(m[1]))
        if command not in ('G0', 'G1', 'G92'): continue
        values = {key: float(value) for key, value in WORDS.findall(code)}
        previous = position[:]
        for idx, axis in enumerate('XYZ'):
            if axis in values:
                position[idx] = values[axis] if absolute_xyz or command == 'G92' else (
                    previous[idx]+values[axis] if previous[idx] is not None else None)
        if command == 'G92': continue
        if 'F' in values: feed = values['F']/60
        e = values.get('E', 0.)
        if e and not relative_e: errors.append('Extrusion without M83')
        if e < 0: retracts.append((-e, feed))
        elif e > 0 and not any(axis in values for axis in 'XYZ'): unretracts.append((e, feed))
        elif e > 0:
            xy_extrusions += 1
            if all(v is not None for v in previous[:2]+position[:2]):
                xy = math.hypot(position[0]-previous[0], position[1]-previous[1])
                dz = position[2]-previous[2] if position[2] is not None and previous[2] is not None else 0.
                distance = math.hypot(xy, dz)
                if distance > 1e-7:
                    area = e*filament_area/distance; peak_area = max(peak_area, area)
                    if feed is not None: peak_flow = max(peak_flow, area*feed)
                    # Match Klipper's short-extrusion exception: gross failures only.
                    if area > area_limit*1.001 and e > small_extrude_allowance*1.001:
                        excessive_area.append(raw)
        if 'normal lift Z' in raw and 'Z' in values and layer_z is not None:
            hops.append(values['Z']-layer_z)
    length = float(override(f,p,'retraction_length'))
    speed = float(override(f,p,'retraction_speed'))
    despeed = float(override(f,p,'deretraction_speed')) or speed
    hop = float(override(f,p,'z_hop'))
    for data, wanted_speed, label in [(retracts,speed,'retraction'), (unretracts,despeed,'unretraction')]:
        if not data: errors.append('Missing '+label)
        elif any(abs(a-length)>1e-4 or b is None or abs(b-wanted_speed)>1e-4 for a,b in data):
            errors.append('Incorrect '+label+' length or speed')
    if not hops or any(abs(x-hop)>1e-4 for x in hops): errors.append('Incorrect Z hop')
    if not xy_extrusions: errors.append('No positive XY extrusion')
    if not 0 < max_accel <= 700: errors.append('Acceleration outside existing limits')
    if excessive_area: errors.append('Extrusion exceeds nozzle-dependent Klipper default cross section')
    mvs = float(f['filament_max_volumetric_speed'][0])
    # Tiny path rounding can bias E / length; report peak, do not claim a physical flow measurement.
    bed_after = float(f['hot_plate_temp'][0]); bed_first = float(f['hot_plate_temp_initial_layer'][0])
    if bed_after != bed_first and not any(re.fullmatch(r'M140 S'+str(int(bed_after)), line) for line in commands):
        errors.append('Missing normal-layer bed temperature')
    return {'errors': sorted(set(errors)), 'nozzle': diameter, 'widths': {k:q[k] for k in WIDTHS},
        'start': expected_start, 'pa_values': [v for i,v in pa], 'retraction_mm': length,
        'retraction_speed': speed, 'deretraction_speed': despeed, 'retractions': len(retracts),
        'unretractions': len(unretracts), 'z_hop': hop, 'verified_hops': len(hops),
        'positive_xy_extrusions': xy_extrusions, 'max_acceleration': max_accel,
        'peak_commanded_cross_section_mm2': round(peak_area,6), 'klipper_default_cross_section_mm2': area_limit,
        'cross_section_violations': excessive_area[:3], 'peak_nominal_flow_estimate_mm3_s': round(peak_flow,6),
        'configured_mvs_mm3_s': mvs, 'physical_flow_measured': False}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--orca',required=True); ap.add_argument('--out',required=True)
    args=ap.parse_args(); out=Path(args.out).resolve(); out.mkdir(parents=True,exist_ok=True)
    record=json.loads((ROOT/'NOZZLES.json').read_text())
    env=dict(os.environ, LIBGL_ALWAYS_SOFTWARE='1', WEBKIT_DISABLE_DMABUF_RENDERER='1')
    model=out/'two_towers.stl'; test_stl(model)
    results=[]; names_seen=set(); filament_names_seen=set(); per_variant=[]
    for variant in record['variants']:
        diameter=variant['diameter']; tag=diameter.replace('.','p')
        bundle=ROOT/variant['bundle']
        assert hashlib.sha256(bundle.read_bytes()).hexdigest()==variant['sha256']
        scratch=out/tag/'presets'; scratch.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(bundle) as z:
            assert z.testzip() is None and len(z.namelist())==21
            data={n:json.loads(z.read(n)) for n in z.namelist()}
        manifest=data['bundle_structure.json']
        p=data[manifest['printer_config'][0]]; q=data[manifest['process_config'][0]]
        assert len(p)==144 and len(q)==334
        assert p['name'] not in names_seen; names_seen.add(p['name'])
        assert p['nozzle_diameter']==[diameter] and q['layer_height']=='0.2'
        assert q['compatible_printers']==[p['name']] and p['default_print_profile']==q['name']
        assert p['machine_pause_gcode'].strip()=='PAUSE' and q['post_process']==[]
        for kind, field in [('machine','printer_config'),('process','process_config'),('filament','filament_config')]:
            for name in manifest[field]:
                obj=copy.deepcopy(data[name]); obj['type']=kind; obj['from']='system'
                target=scratch/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(obj))
        for name in manifest['filament_config']:
            f=data[name]
            assert len(f)==123 and f['compatible_printers']==[p['name']]
            assert f['name'] not in filament_names_seen; filament_names_seen.add(f['name'])
            assert f['pressure_advance']==['0'] and f['adaptive_pressure_advance']==['0']
            for k,v in f.items():
                if '_plate_temp' in k: assert 0<=float(v[0])<=105
        entries=[(name,0.,False) for name in manifest['filament_config']]
        pla=next(n for n in manifest['filament_config'] if 'Z-PLA Pro ' in n)
        entries.append((pla,.035,True))
        variant_rows=[]
        for index,(name,pa,trial) in enumerate(entries):
            f=copy.deepcopy(data[name]); f['pressure_advance']=[str(pa)]
            folder=out/tag/(f'{index:02d}_'+re.sub('[^a-zA-Z0-9_-]','_',f['name'])+('_PA_TRIAL' if trial else ''))
            folder.mkdir(parents=True,exist_ok=True)
            filament_path=scratch/name
            if trial:
                clone=copy.deepcopy(f); clone['type']='filament'; clone['from']='system'
                filament_path=folder/'trial_filament.json'; filament_path.write_text(json.dumps(clone))
            effective_path=folder/'effective.json'
            cmd=[args.orca,'--load-settings',str(scratch/manifest['printer_config'][0])+';'+str(scratch/manifest['process_config'][0]),
                '--load-filaments',str(filament_path),'--export-settings',str(effective_path),'--slice','0',
                '--outputdir',str(folder),str(model)]
            run=subprocess.run(cmd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
            (folder/'orca.log').write_text(run.stdout)
            files=list(folder.glob('*.gcode')); text=files[0].read_text() if files else ''
            effective=json.loads(effective_path.read_text()) if effective_path.exists() else {}
            details=inspect(text,effective,p,q,f,pa) if text else {'errors':['No G-code generated']}
            if run.returncode: details['errors'].append('Orca returncode '+str(run.returncode))
            unsupported=f['name'].startswith('Z-PEEK ')
            status='UNSUPPORTED_CATALOG_ONLY' if unsupported else ('FAIL' if details['errors'] else 'PASS')
            row={'nozzle':diameter,'filament':f['name'],'pa_trial':trial,'status':status,
                 'returncode':run.returncode,'gcode_bytes':len(text),'details':details,
                 'log_tail':run.stdout[-1500:] if status=='FAIL' else ''}
            results.append(row); variant_rows.append(row)
            print(json.dumps({'nozzle':diameter,'filament':f['name'],'pa_trial':trial,'status':status,'errors':details['errors']}),flush=True)
            (out/'results.json').write_text(json.dumps(results,indent=2))
        per_variant.append({'nozzle':diameter,'bundle_sha256':variant['sha256'],
            'material_pass':sum(x['status']=='PASS' and not x['pa_trial'] for x in variant_rows),
            'material_fail':sum(x['status']=='FAIL' and not x['pa_trial'] for x in variant_rows),
            'catalog_only':sum(x['status']=='UNSUPPORTED_CATALOG_ONLY' for x in variant_rows),
            'pa_trial':variant_rows[-1]['status']})
    summary={'status':'PASS' if all(x['material_pass']==17 and x['material_fail']==0 and x['pa_trial']=='PASS' for x in per_variant) else 'FAIL',
        'revision':'R4','orca':'2.3.2','variants':per_variant,'printer_count':len(names_seen),'material_entries':len(filament_names_seen),
        'software_material_pass':sum(x['material_pass'] for x in per_variant),'unsupported_entries':3,
        'pa_tests_pass':sum(x['pa_trial']=='PASS' for x in per_variant),'baseline_0p4_unchanged':record['baseline_0p4_unchanged'],
        'metadata_adapter':['type','from=system'],'gui_import_test':False,'hardware_test':False,'host_changed':False,
        'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'tested_commit':os.environ.get('GITHUB_SHA')}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('NOZZLE_SUMMARY='+json.dumps(summary),flush=True)
    assert summary['status']=='PASS', 'Nozzle slicing checks failed; see results/logs'

if __name__=='__main__': main()
