#!/usr/bin/env python3
"""Install the Zortrax vendor into an existing OrcaSlicer user configuration.
Default is a read-only plan. Close Orca first; use --apply to copy the vendor.
No network access, no printer access, no MCU/host settings are modified.
"""
import argparse,datetime,json,os,shutil,sys,tempfile
from pathlib import Path


def default_config():
 if sys.platform=='darwin':return Path.home()/'Library/Application Support/OrcaSlicer'
 if os.name=='nt':return Path(os.environ.get('APPDATA',str(Path.home())))/'OrcaSlicer'
 return Path(os.environ.get('XDG_CONFIG_HOME',str(Path.home()/'.config')))/'OrcaSlicer'


def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--config-dir',type=Path,default=default_config())
 ap.add_argument('--source',type=Path,default=Path(__file__).resolve().parent)
 ap.add_argument('--apply',action='store_true')
 ap.add_argument('--replace-existing-vendor',action='store_true')
 a=ap.parse_args();root=a.config_dir.expanduser().resolve();src=a.source.resolve()
 if not root.is_dir():raise SystemExit('Orca configuration folder does not exist. Start Orca first or pass --config-dir.')
 if not (src/'Zortrax.json').is_file() or not (src/'Zortrax').is_dir():
  # Repository use: script is under tools/, native files are separate.
  candidate=Path(__file__).resolve().parents[1]/'native'
  if (candidate/'Zortrax.json').is_file():src=candidate
  else:raise SystemExit('Extract the complete native ZIP, including Zortrax.json and Zortrax/.')
 vendor=json.loads((src/'Zortrax.json').read_text())
 assert vendor['name']=='Zortrax' and len(vendor['machine_list'])==4
 for group in ['machine_model_list','machine_list','process_list','filament_list']:
  for item in vendor[group]:
   p=(src/'Zortrax'/item['sub_path']).resolve()
   if not p.is_relative_to(src/'Zortrax') or not p.is_file():raise SystemExit('Invalid vendor sub_path')
   if json.loads(p.read_text())['name']!=item['name']:raise SystemExit('Vendor index/name mismatch')
 target=root/'system';old=target/'Zortrax.json';old_dir=target/'Zortrax'
 if target.exists() and not target.resolve().is_relative_to(root):raise SystemExit('Refusing an external system symlink')
 if (old.exists() or old_dir.exists()) and not a.replace_existing_vendor:
  raise SystemExit('Existing Zortrax vendor found. Export calibrated presets first, then use --replace-existing-vendor; a backup will be retained.')
 print('Source:',src);print('Target:',target)
 print('4 printers, 76 filament entries, 80 process presets. Manufacturer Zortrax; community integration with explicit provenance.')
 print('User presets, Orca.conf and the printer host will NOT be edited.')
 if not a.apply:
  print('PLAN ONLY. Close OrcaSlicer, then rerun with --apply.');return
 target.mkdir(exist_ok=True)
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
 backup=root/'vendor-backups'/('Zortrax_'+stamp);backup.mkdir(parents=True)
 for name in ['Zortrax.json','Zortrax']:
  p=target/name
  if p.is_symlink():raise SystemExit('Refusing vendor symlink: '+str(p))
  if p.is_dir():shutil.copytree(p,backup/name)
  elif p.exists():shutil.copy2(p,backup/name)
 with tempfile.TemporaryDirectory(prefix='zortrax-stage-',dir=root) as tmp:
  stage=Path(tmp);shutil.copytree(src/'Zortrax',stage/'Zortrax');shutil.copy2(src/'Zortrax.json',stage/'Zortrax.json')
  try:
   if old_dir.exists():shutil.rmtree(old_dir)
   shutil.move(str(stage/'Zortrax'),str(old_dir));os.replace(stage/'Zortrax.json',old)
  except Exception:
   if old_dir.exists():shutil.rmtree(old_dir)
   old.unlink(missing_ok=True)
   if (backup/'Zortrax').exists():shutil.copytree(backup/'Zortrax',old_dir)
   if (backup/'Zortrax.json').exists():shutil.copy2(backup/'Zortrax.json',old)
   raise
 (backup/'INSTALLATION.json').write_text(json.dumps({'target':str(target),'revision':'R6','source':str(src)},indent=2))
 print('Installed. Backup:',backup)
 print('Restart Orca; use Add/Remove printers to enable Zortrax -> Zortrax M300 -> 0.2/0.3/0.4/0.6.')
 print('Do not install the User .orca_printer copies under the same names at the same time.')

if __name__=='__main__':main()
