#!/usr/bin/env python3
"""Validate current profiles, provenance, generated tables and documentation offline."""
import hashlib,json,re
from pathlib import Path
from urllib.parse import unquote
from catalog import build
ROOT=Path(__file__).resolve().parents[1]
def validate(root=ROOT):
 current=json.loads((root/'CURRENT.json').read_text());v=json.loads((root/'profiles/Zortrax.json').read_text());baseline=json.loads((root/'evidence/PROFILE_BASELINE.json').read_text())
 ps={str(p.relative_to(root/'profiles')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'profiles').rglob('*.json')}
 assert ps==baseline['sha256'],'Preset bytes differ from the reviewed R7.1 baseline'
 assert len(ps)==140 and v['version']==current['vendor_version']=='02.05.00.08'
 assert [len(v[k]) for k in ('machine_model_list','machine_list','process_list','filament_list')]==[1,4,30,104]
 names=set();settings=set();machines={};processes={};filaments={}
 for key,kind in [('machine_model_list','machine_model'),('machine_list','machine'),('process_list','process'),('filament_list','filament')]:
  for entry in v[key]:
   p=root/'profiles/Zortrax'/entry['sub_path'];assert p.resolve().is_relative_to((root/'profiles/Zortrax').resolve())
   obj=json.loads(p.read_text());assert obj['name']==entry['name'] and obj['type']==kind
   assert obj['name'] not in names;names.add(obj['name'])
   if kind=='machine_model':continue
   assert obj['from']=='system' and obj['instantiation']=='true' and obj.get('inherits')!=''
   assert obj['setting_id'] not in settings;settings.add(obj['setting_id'])
   if kind=='machine':machines[obj['name']]=obj
   if kind=='process':processes[obj['name']]=obj
   if kind=='filament':filaments[obj['name']]=obj
 for m in machines.values():
  d=m['printer_variant'];assert d in ('0.2','0.3','0.4','0.6') and m['nozzle_diameter']==[d]
  assert m['printer_model']=='Zortrax M300 Classic' and m['use_relative_e_distances']=='1'
  assert m['machine_end_gcode'].strip()=='END_PRINT' and m['machine_pause_gcode'].strip()=='PAUSE'
  start=m['machine_start_gcode'];assert 'M83' in start and 'MESH=AUTO' in start and start.count('START_PRINT ')==1
  assert not any(x in start for x in ('FORCE_MOVE','SET_KINEMATIC_POSITION','SET_GCODE_OFFSET','SAVE_CONFIG','BED_MESH_CLEAR'))
  assert m['default_print_profile'] in processes
 for q in processes.values():
  assert len(q['compatible_printers'])==1;m=machines[q['compatible_printers'][0]]
  assert float(m['min_layer_height'][0])<=float(q['layer_height'])<=float(m['max_layer_height'][0])+1e-8
  assert q['post_process']==[]
 for f in filaments.values():
  assert len(f['compatible_printers'])==1 and f['compatible_printers'][0] in machines
  assert not f['name'].startswith('Z-SUPPORT') and f['filament_is_support']==['0']
  assert f['pressure_advance']==['0'] and f['adaptive_pressure_advance']==['0']
  assert all(float(value[0])<=105 for key,value in f.items() if '_plate_temp' in key)
 for d in ('0.2','0.3','0.4','0.6'):
  f=filaments['Z-PLA @Zortrax M300 '+d];assert f['hot_plate_temp']==(['50'] if d=='0.4' else ['30'])
 manifest=json.loads((root/'sources/MANIFEST.json').read_text())
 for name,sha in manifest['files'].items():assert hashlib.sha256((root/'sources'/name).read_bytes()).hexdigest()==sha
 outputs,tables=build(root)
 for name,text in outputs.items():assert (root/name).read_bytes()==text.encode(),'Generated table differs: '+name
 for path in [root/'README.md',root/'CHANGELOG.md',*sorted((root/'docs').rglob('*.md')),*sorted((root/'sources').glob('*.md'))]:
  for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
   if '://' in target or target.startswith('#'):continue
   target=unquote(target.split('#')[0]);assert (path.parent/target).exists(),f'Broken link in {path.name}: {target}'
 forbidden=('archive','native','native_r7','profiles/R5','profiles/R6','tools/repair_macos_r6.py','tools/install_native_r6.py')
 assert not any((root/p).exists() for p in forbidden),'Obsolete distribution remains'
 assert not list(root.rglob('*_PL.md')) and not list(root.rglob('*.orca_printer'))
 assert not any(p.suffix.lower() in ('.ttf','.otf','.woff','.woff2','.dll','.exe') for p in root.rglob('*'))
 return {'status':'PASS','profile_revision':current['profile_revision'],'profile_json_files':len(ps),'model_count':1,'machine_count':len(machines),'process_count':len(processes),'filament_count':len(filaments),'source_rows':len(tables['mapped']),'profile_bytes_unchanged':True,'host_access':False}
if __name__=='__main__':print(json.dumps(validate(),indent=2))
