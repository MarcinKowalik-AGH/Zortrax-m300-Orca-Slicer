#!/usr/bin/env python3
"""R7 software slicing only, not physical qualification. Uses native system JSONs."""
import argparse,copy,json,os,re,subprocess
from pathlib import Path
from gcode_checks import inspect
from gcode_checks import test_stl
ROOT=Path(__file__).resolve().parents[1]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--orca',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
 src=ROOT/'profiles';vendor=json.loads((src/'Zortrax.json').read_text());objects={}
 for group in ('machine_list','process_list','filament_list'):
  for e in vendor[group]:
   path=src/'Zortrax'/e['sub_path'];obj=json.loads(path.read_text());assert obj['name']==e['name'] and obj['from']=='system';objects[obj['name']]=(path,obj)
 assert len(vendor['machine_model_list'])==1
 model=json.loads((src/'Zortrax'/vendor['machine_model_list'][0]['sub_path']).read_text())
 assert model['nozzle_diameter']=='0.2;0.3;0.4;0.6'
 matrices=[];cases=[]
 for e in vendor['machine_list']:
  pp,p=objects[e['name']];d=p['printer_variant'];assert p['printer_model']=='Zortrax M300 Classic'
  procs=[x for x in vendor['process_list'] if objects[x['name']][1]['compatible_printers']==[p['name']]]
  fils=[x for x in vendor['filament_list'] if objects[x['name']][1]['compatible_printers']==[p['name']]]
  assert len(fils)==26
  for x in procs:
   qp,q=objects[x['name']];assert float(p['min_layer_height'][0])<=float(q['layer_height'])<=float(p['max_layer_height'][0])
   assert float(q['initial_layer_print_height'])<=float(p['max_layer_height'][0])
   cases.append((p['name'],x['name'],f'Generic PLA @Zortrax M300 {d}',0.,'process'))
  for x in fils:
   f=objects[x['name']][1];assert not f['name'].startswith('Z-SUPPORT');assert f['filament_is_support']==['0']
   cases.append((p['name'],p['default_print_profile'],x['name'],0.,'filament'))
  cases.append((p['name'],p['default_print_profile'],f'Generic PLA @Zortrax M300 {d}',.035,'pa_trial'))
  matrices.append({'nozzle':d,'processes':[x['name'] for x in procs],'filaments':len(fils)})
 model_file=out/'two_towers.stl';test_stl(model_file)
 env=dict(os.environ,LIBGL_ALWAYS_SOFTWARE='1',WEBKIT_DISABLE_DMABUF_RENDERER='1')
 results=[]
 for index,(pn,qn,fn,pa,kind) in enumerate(cases):
  pp,p=objects[pn];qp,q=objects[qn];fp,original_f=objects[fn];f=copy.deepcopy(original_f)
  folder=out/f'{index:03d}_{kind}';folder.mkdir(exist_ok=True)
  if pa:
   f['pressure_advance']=[str(pa)];fp=folder/'trial.json';fp.write_text(json.dumps(f))
  ef=folder/'effective.json'
  cmd=[a.orca,'--load-settings',str(pp)+';'+str(qp),'--load-filaments',str(fp),'--export-settings',str(ef),'--slice','0','--outputdir',str(folder),str(model_file)]
  r=subprocess.run(cmd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
  (folder/'orca.log').write_text(r.stdout)
  files=list(folder.glob('*.gcode'));g=files[0].read_text(errors='replace') if files else ''
  actual=json.loads(ef.read_text()) if ef.exists() else {}
  detail=inspect(g,actual,p,q,f,pa) if g else {'errors':['No G-code']}
  if r.returncode:detail['errors'].append('Exit '+str(r.returncode))
  for k in ('wall_loops','sparse_infill_density','top_shell_layers','bottom_shell_layers'):
   if str(actual.get(k))!=str(q[k]):detail['errors'].append('Effective mismatch '+k)
  result={'printer':pn,'process':qn,'filament':fn,'test':kind,'status':'FAIL' if detail['errors'] else 'PASS','bytes':len(g),'details':detail}
  results.append(result);print(json.dumps({k:result[k] for k in ('printer','process','filament','test','status')}),detail['errors'],flush=True)
  (out/'results.json').write_text(json.dumps(results,indent=2))
 summary={'revision':'R7.1','engine':'OrcaSlicer 2.5.0','model_count':1,'nozzle_variants':4,'filament_count':104,'process_count':30,'matrices':matrices,
  'tests':len(results),'pass':sum(r['status']=='PASS' for r in results),'fail':sum(r['status']=='FAIL' for r in results),
  'hardware_test':False,'mac_user_gui_test':False,'klipper_changed':False,'metadata_adapter':False,
  'note':'High-temperature filaments are listed and sliced for software checks only; not qualified at M300305/105 limits.',
  'workflow_run':os.environ.get('GITHUB_RUN_ID'),'source_commit':os.environ.get('GITHUB_SHA')}
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print('CURRENT_SUMMARY',json.dumps(summary));assert summary['tests']==138 and summary['fail']==0
if __name__=='__main__':main()
