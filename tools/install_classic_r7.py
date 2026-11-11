#!/usr/bin/env python3
"""Mac-only R7 installation with no AppConfig edits or printer connection.
Default is a plan. Install first; enable M300 through Orca's own UI. Only then
--archive-offline archives the four known imported bundles. No broad deletion.
"""
import argparse,copy,datetime,hashlib,json,os,re,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GROUPS=('machine_model_list','machine_list','filament_list','process_list')
MODEL='Zortrax M300 Classic'
OFFLINE=re.compile(r'^offline_M300_Classic_0\.[3468]_v1$')

def read(p):
 v=json.loads(Path(p).read_text(encoding='utf-8-sig'))
 if not isinstance(v,dict):raise ValueError('Not a JSON object: '+str(p))
 return v

def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def digest(p):
 if not p.exists():return None
 if p.is_file():return hashlib.sha256(p.read_bytes()).hexdigest()
 return {str(f.relative_to(p)):digest(f) for f in sorted(p.rglob('*')) if f.is_file()}

def safe(root,relative):
 rel=Path(relative)
 if rel.is_absolute() or '..' in rel.parts or not rel.parts:raise ValueError('Unsafe path')
 path=root
 for part in rel.parts:
  path=path/part
  if path.is_symlink():raise ValueError('Symlink refused: '+str(path))
 if path.is_dir() and any(p.is_symlink() for p in path.rglob('*')):raise ValueError('Nested symlink refused')
 return path

def classic(s):
 s=re.sub(r'[_-]',' ',str(s)).lower()
 return bool(re.search(r'\bm300\b',s)) and not bool(re.search(r'\bm300\s*(plus|dual)\b',s))

def scoped(obj):
 if obj.get('printer_model') and not classic(obj['printer_model']):return False
 cp=obj.get('compatible_printers',[])
 if isinstance(cp,str):cp=[cp] if cp else []
 if not isinstance(cp,list):raise ValueError('Unknown compatible_printers format')
 if cp and not all(classic(x) for x in cp):return False
 return classic(obj.get('name','')) or classic(obj.get('printer_model','')) or bool(cp)

def install_plan(root,source):
 root=Path(root).resolve();source=Path(source).resolve()
 # Read the current config to identify an existing installation, but NEVER write it.
 read(safe(root,'OrcaSlicer.conf'))
 vendor=read(source/'Zortrax.json')
 if [len(vendor[k]) for k in GROUPS]!=[1,4,104,30]:raise ValueError('Not the complete R7 vendor')
 writes={};remove=set();names=set()
 for group in GROUPS:
  for e in vendor[group]:
   p=safe(source/'Zortrax',e['sub_path']);obj=read(p)
   if obj['name']!=e['name'] or not scoped(obj):raise ValueError('Source scope/index mismatch')
   writes['system/Zortrax/'+e['sub_path']]=p.read_bytes();names.add(obj['name'])
 old=safe(root,'system/Zortrax.json');merged=copy.deepcopy(vendor)
 if old.exists():
  previous=read(old)
  if previous.get('name')!='Zortrax':raise ValueError('Unexpected existing vendor')
  for group in GROUPS:
   retained=[]
   for e in previous.get(group,[]):
    rel='system/Zortrax/'+e['sub_path'];path=safe(root,rel);obj=read(path) if path.is_file() else {'name':e['name']}
    if scoped(obj):remove.add(rel)
    else:
     if not path.is_file():raise ValueError('Missing unrelated Zortrax file; refusing to replace index')
     if rel in writes:raise ValueError('Unrelated source collision')
     retained.append(e)
   merged[group]=retained+merged[group]
 writes['system/Zortrax.json']=enc(merged)
 if safe(root,'system/Zortrax.opc').exists():remove.add('system/Zortrax.opc')
 remove.difference_update(writes)
 writes={r:b for r,b in writes.items() if not safe(root,r).is_file() or safe(root,r).read_bytes()!=b}
 remove={r for r in remove if safe(root,r).exists()}
 return make_plan(root,writes,remove,'install')

def archive_plan(root):
 root=Path(root).resolve();cfg=read(safe(root,'OrcaSlicer.conf'))
 enabled=any(isinstance(x,dict) and x.get('vendor')=='Zortrax' and x.get('model')==MODEL for x in cfg.get('models',[]))
 if not enabled:raise ValueError('Najpierw wlacz M300 Classic w Orca przez Select/Remove printers, sprawdz liste i zamknij program. Stare pakiety pozostaja.')
 remove=set();warnings=[]
 user=safe(root,'user')
 if user.is_dir():
  for account in user.iterdir():
   if not account.is_dir():continue
   local=safe(root,str(account.relative_to(root))+'/_local')
   if not local.is_dir():continue
   for folder in local.iterdir():
    if not folder.is_dir():continue
    safe(root,folder.relative_to(root))
    meta=folder/'bundle_metadata.json'
    if not meta.is_file():meta=folder/'bundle_structure.json'
    if not meta.is_file():continue
    md=read(meta);name=md.get('name',md.get('bundle_id',''))
    if not OFFLINE.fullmatch(name):continue
    objs=[read(p) for p in folder.rglob('*.json') if p!=meta]
    machines=[j for j in objs if j.get('type')=='machine' or 'nozzle_diameter' in j]
    if not machines or not all(scoped(j) for j in machines):
     warnings.append('Zachowano nierozpoznany/mieszany pakiet: '+name);continue
    presets=[j for j in objs if j.get('type') in ('machine','process','filament') or 'compatible_printers' in j]
    if any(j.get('compatible_printers') and not scoped(j) for j in presets):
     warnings.append('Zachowano wspoldzielone presety: '+name);continue
    remove.add(str(folder.relative_to(root)))
 p=make_plan(root,{},remove,'archive-offline');p['warnings']=warnings;return p

def make_plan(root,writes,remove,mode):
 allowed=set(writes)|set(remove)
 if any(r=='OrcaSlicer.conf' or not (r.startswith('system/Zortrax') or (mode=='archive-offline' and '/_local/' in r)) for r in allowed):raise ValueError('Refused scope')
 return {'root':root,'writes':writes,'remove':sorted(remove),'before':{r:digest(safe(root,r)) for r in sorted(allowed)},'mode':mode,'conf_hash':digest(root/'OrcaSlicer.conf'),'warnings':[]}

def atom(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix='.m300-r7-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def erase(p):
 if p.is_dir():shutil.rmtree(p)
 elif p.exists():p.unlink()

def restore_before(root,backup,before):
 for rel in sorted(before,reverse=True):
  p=safe(root,rel);erase(p)
  if before[rel] is not None:
   src=safe(backup/'before',rel);p.parent.mkdir(parents=True,exist_ok=True)
   if src.is_dir():shutil.copytree(src,p)
   else:shutil.copy2(src,p)

def apply(p):
 root=p['root']
 if not p['before']:return None
 if digest(root/'OrcaSlicer.conf')!=p['conf_hash'] or any(digest(safe(root,r))!=h for r,h in p['before'].items()):raise ValueError('Files changed after planning')
 backup=root.parent/('OrcaSlicer-M300-R7-'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'));backup.mkdir(mode=0o700)
 for rel,state in p['before'].items():
  if state is None:continue
  src=safe(root,rel);dst=backup/'before'/rel;dst.parent.mkdir(parents=True,exist_ok=True)
  if src.is_dir():shutil.copytree(src,dst)
  else:shutil.copy2(src,dst)
  if digest(dst)!=state:raise ValueError('Backup verification failed; no active file changed')
 receipt={'schema':'M300-R7','root':str(root),'mode':p['mode'],'before':p['before'],'conf_hash':p['conf_hash'],'state':'PREPARED'}
 atom(backup/'RECEIPT.json',enc(receipt))
 try:
  for rel in p['remove']:erase(safe(root,rel))
  for rel,data in p['writes'].items():atom(safe(root,rel),data)
  assert digest(root/'OrcaSlicer.conf')==p['conf_hash'],'Orca config changed concurrently'
  receipt.update(state='INSTALLED',after={r:digest(safe(root,r)) for r in p['before']});atom(backup/'RECEIPT.json',enc(receipt))
 except BaseException:
  restore_before(root,backup,p['before']);receipt['state']='ROLLED_BACK';atom(backup/'RECEIPT.json',enc(receipt));raise
 return backup

def restore(path):
 backup=Path(path).resolve();j=read(backup/'RECEIPT.json');root=Path(j['root']).resolve()
 if j.get('schema')!='M300-R7' or j.get('state')!='INSTALLED' or root.parent!=backup.parent:raise ValueError('Not an installed R7 receipt')
 for rel,h in j['after'].items():
  if digest(safe(root,rel))!=h:raise ValueError('Later edit; not overwritten: '+rel)
 for rel,h in j['before'].items():
  if h is not None and digest(safe(backup/'before',rel))!=h:raise ValueError('Damaged backup')
 restore_before(root,backup,j['before']);j['state']='RESTORED';atom(backup/'RECEIPT.json',enc(j))

def guard():
 if sys.platform!='darwin' or os.environ.get('SSH_CONNECTION') or os.environ.get('SSH_TTY'):raise ValueError('Tylko lokalny Mac. Nie Orange Pi ani SSH.')
 if os.geteuid()==0:raise ValueError('Bez sudo.')
 for line in subprocess.check_output(['ps','-axo','comm='],text=True).splitlines():
  if Path(line.strip()).name.lower() in ('orcaslicer','orca-slicer'):raise ValueError('Zamknij Orca przez Cmd+Q.')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--config-dir',type=Path,default=Path.home()/'Library/Application Support/OrcaSlicer')
 ap.add_argument('--source',type=Path,default=ROOT/'native_r7');ap.add_argument('--apply',action='store_true');ap.add_argument('--archive-offline',action='store_true');ap.add_argument('--restore',type=Path)
 a=ap.parse_args()
 try:
  guard()
  if a.restore:restore(a.restore);print('PRZYWROCONO pliki R7; OrcaSlicer.conf nie zmieniono.');return
  root=a.config_dir.expanduser().resolve()
  if root.name!='OrcaSlicer' or not (root/'OrcaSlicer.conf').is_file():raise ValueError('Nie rozpoznano katalogu konfiguracji Orca.')
  p=archive_plan(root) if a.archive_offline else install_plan(root,a.source)
  print('TYLKO MAC / ORCA. Nie zmieniam OrcaSlicer.conf, Creality, Inventure ani Klippera.')
  print('Tryb:',p['mode'],'Pliki do zapisania:',len(p['writes']),'Elementy do archiwum:',len(p['remove']))
  for rel in p['remove']:print('Archiwum:',rel)
  for warning in p['warnings']:print('UWAGA:',warning)
  if not a.apply:print('PLAN; bez zmian. Dodaj --apply, aby zastosowac.');return
  backup=apply(p);print('GOTOWE. Kopia:',backup or 'brak zmian')
  if not a.archive_offline:print('Uruchom Orca > Select/Remove printers > Zortrax > Zortrax M300 Classic. Zaznacz dysze. Dopiero po sprawdzeniu mozna uzyc --archive-offline.')
 except Exception as e:ap.exit(1,'STOP: '+str(e)+'\n')
if __name__=='__main__':main()
