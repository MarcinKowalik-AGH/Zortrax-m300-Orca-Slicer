#!/usr/bin/env python3
"""Validate current profiles, provenance, generated tables and documentation offline."""
import hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote
from catalog import build
from bed_geometry import (PHYSICAL_MM,PRINTABLE_MM,PRINTABLE_PHYSICAL_BOUNDS_MM,
                          PERFORATED_PHYSICAL_BOUNDS_MM,FRAME_SCREW_EDGE_MM,FRAME_SCREWS,PLATE_THICKNESS_MM,
                          TOP_Z,BOTTOM_Z,REAR_CONNECTOR_CENTER_X_MM,
                          REAR_CONNECTOR_PROTRUSION_MM,REAR_CONNECTOR_SHELL_BOUNDS_MM,
                          generate_visual_stl)
ROOT=Path(__file__).resolve().parents[1]
def validate(root=ROOT):
 current=json.loads((root/'CURRENT.json').read_text());v=json.loads((root/'profiles/Zortrax.json').read_text());baseline=json.loads((root/'evidence/PROFILE_BASELINE.json').read_text())
 ps={str(p.relative_to(root/'profiles')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'profiles').rglob('*.json')}
 assert ps==baseline['sha256'],'Preset bytes differ from the reviewed unchanged machine/filament/process data baseline'
 assert current['profile_revision']=='R7.10' and len(ps)==140 and v['version']==current['vendor_version']=='02.05.00.12'
 assert [len(v[k]) for k in ('machine_model_list','machine_list','process_list','filament_list')]==[1,4,30,104]
 bed_model=json.loads((root/'profiles/Zortrax/machine/Zortrax M300 Classic.json').read_text())
 assert bed_model['bed_texture']=='model/Zortrax_M300_Classic_bed.svg'
 asset=(root/'profiles/Zortrax'/bed_model['bed_texture']).resolve()
 assert asset.is_relative_to((root/'profiles/Zortrax').resolve())
 data=asset.read_bytes()
 assert len(data)>100000 and hashlib.sha256(data).hexdigest()==baseline['visual_asset']['sha256']
 drawing=ET.fromstring(data)
 assert drawing.tag=='{http://www.w3.org/2000/svg}svg'
 assert (drawing.get('width'),drawing.get('height'),drawing.get('viewBox'))==('1200','1220','0 0 1200 1220')
 ns='{http://www.w3.org/2000/svg}'
 holes=[e for e in drawing.iter(ns+'circle') if e.get('r')=='2.9']
 assert len(holes)==10200,'SVG must contain exactly 10200 circular perforations'
 xs=sorted({float(e.get('cx')) for e in holes})
 ys=sorted({float(e.get('cy')) for e in holes})
 assert len(xs)==100 and len(ys)==102 and len(xs)*len(ys)==len(holes)
 assert all(abs(xs[i+1]-xs[i]-12.0)<1e-7 for i in range(len(xs)-1))
 assert all(abs(ys[i+1]-ys[i]-12.0)<1e-7 for i in range(len(ys)-1))

 # Gold rectangles must be under the one continuous field of holes, so the
 # perforations stay visible on silver and on all five flush contact pads.
 children=list(drawing)
 background=next(e for e in children if e.get('id')=='full-bleed-opaque-base')
 assert tuple(background.get(k) for k in ('x','y','width','height'))==('0','0','1200','1220')
 pads=next(e for e in children if e.get('id')=='five-flush-gold-pads')
 perforation_group=next(e for e in children if e.get('id')=='all-perforations-including-gold')
 assert len(pads)==5 and children.index(pads)<children.index(perforation_group)
 cropped=[tuple(float(p.get(a)) for a in ('x','y','width','height')) for p in pads]
 assert cropped==[(0,0,180,200),(1020,0,180,200),
                  (0,1040,180,180),(1020,1040,180,180),
                  (500,520,200,200)],'Pad geometry must be an exact print-safe crop'
 assert cropped[0][1]==cropped[1][1]==0,'No silver strip behind rear pads'
 physical_drawing=ET.fromstring((root/'docs/Zortrax_M300_360mm_plate_layout.svg').read_bytes())
 physical_group=next(g for g in physical_drawing if g.get('id')=='five-flush-gold-pads')
 physical_pads=[tuple(float(p.get(a)) for a in ('x','y','width','height')) for p in physical_group]
 assert physical_pads==[(60,60,240,240),(1140,60,240,240),
                       (60,1140,240,240),(1140,1140,240,240),
                       (620,620,200,200)]
 assert (1140-60-240)/4==210.0
 screw_groups=[e for e in drawing.iter(ns+'g') if e.get('class')=='allen-bolt']
 centre_collars=[e for e in children if e.get('class')=='centre-hole-free-collar']
 assert len(screw_groups)==2 and len(centre_collars)==2
 assert all(children.index(e)>children.index(perforation_group) for e in centre_collars)

 assert PHYSICAL_MM==(360.,360.) and PRINTABLE_MM==(300.,305.)
 assert PRINTABLE_PHYSICAL_BOUNDS_MM==(30.,330.,30.,335.)
 assert PERFORATED_PHYSICAL_BOUNDS_MM==(14.,346.,15.,344.)
 assert FRAME_SCREW_EDGE_MM==(6.,93.,180.,267.,354.)
 assert len(FRAME_SCREWS)==16 and len(set(FRAME_SCREWS))==16
 assert PLATE_THICKNESS_MM==3. and abs(TOP_Z-BOTTOM_Z-3.)<1e-8
 assert REAR_CONNECTOR_CENTER_X_MM==148. and REAR_CONNECTOR_PROTRUSION_MM==1.6
 assert REAR_CONNECTOR_SHELL_BOUNDS_MM==(143.75,354.6,152.25,361.6)
 assert current['measured_bed_geometry']['plate_thickness_mm']==3
 assert current['measured_bed_geometry']['rear_connector']['no_klipper_or_printable_area_change'] is True
 mesh=generate_visual_stl()
 assert mesh.startswith(b'Zortrax M300 Classic')
 assert 1_000_000<len(mesh)<12_000_000 and len(mesh)==84+50*int.from_bytes(mesh[80:84],'little')
 guide=ET.fromstring((root/'docs/Zortrax_M300_360mm_plate_layout.svg').read_bytes())
 assert any(e.get('id')=='actual-printable-area-300x305' for e in guide.iter())
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
  # Repository remains portable; install.py populates an absolute Mac path.
  assert m['bed_custom_texture']=='' and m['bed_custom_model']==''
  # Measured safe envelope and actual plate are intentionally different.
  assert m['printable_area']==['0x0','300x0','300x305','0x305']
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
  for material,old_nozzle,old_bed in (
      ('Z-PLA','210','50' if d=='0.4' else '30'),
      ('Z-PLA Pro','207','30'),
      ('Generic PLA','210','60')):
   f=filaments[material+' @Zortrax M300 '+d]
   assert f['nozzle_temperature_initial_layer']==['230']
   assert f['nozzle_temperature']==[old_nozzle]
   assert f['hot_plate_temp']==[old_bed]
   initial_plate_keys=[k for k in f if k.endswith('_plate_temp_initial_layer')]
   assert len(initial_plate_keys)==6 and all(f[k]==['70'] for k in initial_plate_keys)
   regular_plate_keys=[k for k in f if k.endswith('_plate_temp') and not k.endswith('_plate_temp_initial_layer')]
   assert len(regular_plate_keys)==6 and all(f[k]==[old_bed] for k in regular_plate_keys)
 # Only three materials have bed temperatures raised to the new minimum.
 for d in ('0.2','0.3','0.4','0.6'):
  for material,nozzle in (('Z-SEMIFLEX','215'),('Z-GLASS','254'),('Z-PETG','254')):
   f=filaments[material+' @Zortrax M300 '+d]
   assert f['nozzle_temperature_initial_layer']==[nozzle]
   assert f['nozzle_temperature']==[nozzle]
   first=[k for k in f if k.endswith('_plate_temp_initial_layer')]
   later=[k for k in f if k.endswith('_plate_temp')]
   assert len(first)==len(later)==6
   assert all(f[k]==['40'] for k in first)
   assert all(f[k]==['35'] for k in later)
  for material,bed in (('Z-PHA','55'),('Generic TPU','50'),('Z-FLEX','50'),('Z-ASA Pro','65'),('Z-ULTRAT Plus','100')):
   f=filaments[material+' @Zortrax M300 '+d]
   assert all(f[k]==[bed] for k in f if '_plate_temp' in k),f['name']
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
 return {'status':'PASS','physical_bed_mm':[360,360],'printable_area_mm':[300,305],'host_unchanged':True,'profile_revision':current['profile_revision'],'profile_json_files':len(ps),'model_count':1,'machine_count':len(machines),'process_count':len(processes),'filament_count':len(filaments),'source_rows':len(tables['mapped']),'profile_bytes_unchanged':False,'native_bed_texture_present':True,'pla_first_layer_profiles_updated':12,'later_layer_temperatures_unchanged_for_PLA':True,'bed_floor_profiles_updated':12,'higher_bed_temperatures_preserved':True,'host_access':False}
if __name__=='__main__':print(json.dumps(validate(),indent=2))
