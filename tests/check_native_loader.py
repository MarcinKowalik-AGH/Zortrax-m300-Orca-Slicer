#!/usr/bin/env python3
"""Check INFO-level evidence from an actual isolated Orca GUI startup.
The previous summary regex targeted a DEBUG-level line not emitted by the
release binary. Require all134 process/filament registrations, four visible
machine variants, successful system-machine selection and the generated cache.
"""
import argparse,json,re
from pathlib import Path

def check(source,gui):
 vendor=json.loads((source/'Zortrax.json').read_text())
 logs='\n'.join(p.read_text(errors='replace') for p in (gui/'log').glob('*') if p.is_file())
 registered=set(re.findall(r'set_printer_hold_alias\s+preset name : (.*?) remove action: false insert success: true',logs))
 visible=set(re.findall(r'set_visible_from_appconfig: name (.*?), is_visible set to 1',logs))
 expected={kind:{e['name'] for e in vendor[kind]} for kind in ('machine_list','process_list','filament_list')}
 missing_process=sorted(expected['process_list']-registered)
 missing_filaments=sorted(expected['filament_list']-registered)
 missing_machines=sorted(expected['machine_list']-visible)
 selected=re.findall(r'select_preset: machine select success,.*?name (.*?), is_system 1, is_default 0',logs)
 selected=[s for s in selected if s in expected['machine_list']]
 errors=[line for line in logs.splitlines() if '[error]' in line and ('Zortrax' in line or 'M300 Classic' in line)]
 cache=gui/'system/Zortrax.opc'
 # Native GUI is launched from a disposable copy of the *installed*, not source,
 # profiles. The Bed Shape dialog uses an absolute bed_custom_texture filename.
 texture_files=[]
 texture_paths_valid=True
 for d in ('0.2','0.3','0.4','0.6'):
  preset_path=gui/'system/Zortrax/machine'/('Zortrax M300 Classic '+d+' nozzle.json')
  try:
   machine=json.loads(preset_path.read_text())
   filename=Path(machine['bed_custom_texture'])
   good=(filename.is_absolute() and filename.is_file()
         and filename.resolve()==(gui/'vendor/Zortrax/model/Zortrax_M300_Classic_bed.png').resolve()
         and filename.read_bytes().startswith(bytes.fromhex('89504e470d0a1a0a')))
   texture_paths_valid &= bool(good)
   texture_files.append({'nozzle':d,'path':str(filename),'valid':bool(good)})
  except (OSError,ValueError,KeyError,TypeError):
   texture_paths_valid=False
   texture_files.append({'nozzle':d,'valid':False})
 result={'native_loader_pass':not(missing_process or missing_filaments or missing_machines or errors) and bool(selected) and cache.is_file() and cache.stat().st_size>1000 and texture_paths_valid,
  'registered_processes':len(expected['process_list']&registered),'registered_filaments':len(expected['filament_list']&registered),
  'visible_machine_variants':len(expected['machine_list']&visible),'selected_native_machine':selected[-1] if selected else None,
  'missing_processes':missing_process,'missing_filaments':missing_filaments,'missing_machine_variants':missing_machines,
  'native_errors':errors,'cache_generated':cache.is_file(),'bed_texture_paths_valid':texture_paths_valid,'bed_texture_variants':texture_files,'actual_gui_platform':'Linux Xvfb','mac_user_install_test':False}
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--gui',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 result=check(a.source,a.gui);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
 if not result['native_loader_pass']:raise SystemExit('Native GUI registration checks failed')
