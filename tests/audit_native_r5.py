#!/usr/bin/env python3
"""Offline native-profile and G-code audit using the real pinned Orca binary.
Does not execute START_PRINT, connect to a printer or qualify physical materials.
Unlike legacy tests, native system presets need no metadata adapter.
"""
import argparse,copy,hashlib,json,math,os,re,subprocess,zipfile
from pathlib import Path
from gcode_checks import test_stl,override,scalar
ROOT=Path(__file__).resolve().parents[1]
NUMBER=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)'
WORDS=re.compile(r'([A-Z])('+NUMBER+r')')


def inspect(g,ef,p,q,f,pa):
 errors=[];ds=float(p['nozzle_diameter'][0]);h=float(q['layer_height'])
 for k,want in [('nozzle_diameter',ds),('filament_diameter',1.75),('layer_height',h),('filament_flow_ratio',float(f['filament_flow_ratio'][0]))]:
  if not math.isclose(float(scalar(ef.get(k,['nan']))),want,abs_tol=1e-6):errors.append('Effective '+k)
 for k in ['line_width','outer_wall_line_width','inner_wall_line_width','sparse_infill_line_width','top_surface_line_width']:
  if not math.isclose(float(scalar(ef.get(k,['nan']))),float(q[k]),abs_tol=1e-6):errors.append('Effective '+k)
 commands=[l.split(';',1)[0].strip() for l in g.splitlines() if l.split(';',1)[0].strip()]
 expected='START_PRINT EXTRUDER_TEMP=%s BED_TEMP=%s MESH=AUTO'%(f['nozzle_temperature_initial_layer'][0],f['hot_plate_temp_initial_layer'][0])
 starts=[i for i,l in enumerate(commands) if l.startswith('START_PRINT ')]
 if len(starts)!=1 or commands[starts[0]]!=expected:errors.append('START_PRINT temperatures')
 start=starts[0] if starts else -1
 if commands.count('END_PRINT')!=1:errors.append('END_PRINT')
 if any(re.match(r'M(?:104|109|140|190)\b',l) for l in commands[:max(0,start)]):errors.append('Duplicate preheat')
 if any(l.split()[0] in ['M82','G10','G11','M201','M203','M205'] or 'ACCEL_TO_DECEL=' in l for l in commands):errors.append('Unwanted firmware command')
 pas=[]
 for i,l in enumerate(commands):
  if l.startswith('SET_PRESSURE_ADVANCE '):
   m=re.search(r'\bADVANCE=('+NUMBER+')',l)
   if m:pas.append((i,float(m[1])))
 if not any(i<start and v==0 for i,v in pas):errors.append('PA reset before purge')
 if not any(i>start and abs(v-pa)<1e-7 for i,v in pas):errors.append('Filament PA after start')
 feed=None;relative=False;absolute=True;position=[None]*3;layer_z=None
 retracts=[];returns=[];hops=[];positive=0;maxacc=0;area_peak=0;area_fail=[]
 area_limit=4*ds*ds;filament_area=math.pi*1.75**2/4;small_e=ds*area_limit/filament_area
 for raw in g.splitlines():
  if raw.startswith(';Z:'):layer_z=float(raw[3:])
  code=raw.split(';',1)[0].strip()
  if not code:continue
  cmd=code.split()[0]
  if cmd=='M83':relative=True
  if cmd=='M82':relative=False
  if cmd=='G90':absolute=True
  if cmd=='G91':absolute=False
  if cmd=='M204':
   m=re.search(r'\bS('+NUMBER+')',code)
   if m:maxacc=max(maxacc,float(m[1]))
  for m in re.finditer(r'\bACCEL=('+NUMBER+')',code):maxacc=max(maxacc,float(m[1]))
  if cmd not in ['G0','G1','G92']:continue
  words={k:float(v) for k,v in WORDS.findall(code)};old=position[:]
  for idx,axis in enumerate('XYZ'):
   if axis in words:position[idx]=words[axis] if absolute or cmd=='G92' else old[idx]+words[axis] if old[idx] is not None else None
  if cmd=='G92':continue
  if 'F' in words:feed=words['F']/60
  e=words.get('E',0)
  if e and not relative:errors.append('Extrusion without M83')
  if e<0:retracts.append((-e,feed))
  elif e>0 and not any(k in words for k in 'XYZ'):returns.append((e,feed))
  elif e>0:
   positive+=1
   if all(v is not None for v in old[:2]+position[:2]):
    distance=math.hypot(position[0]-old[0],position[1]-old[1])
    if distance>1e-6:
     area=e*filament_area/distance;area_peak=max(area_peak,area)
     if area>area_limit*1.001 and e>small_e*1.001:area_fail.append(raw)
  if 'normal lift Z' in raw and 'Z' in words and layer_z is not None:hops.append(words['Z']-layer_z)
 length=float(override(f,p,'retraction_length'));extra=float(override(f,p,'retract_restart_extra'))
 speed=float(override(f,p,'retraction_speed'));back=float(override(f,p,'deretraction_speed')) or speed
 hop=float(override(f,p,'z_hop'))
 for values,want_length,want_speed,label in [(retracts,length,speed,'retract'),(returns,length+extra,back,'return')]:
  if not values:errors.append('No '+label)
  elif any(abs(l-want_length)>0.001 or v is None or abs(v-want_speed)>0.02 for l,v in values):errors.append('Wrong '+label+' amount/feed')
 if hop>0 and (not hops or any(abs(z-hop)>1e-4 for z in hops)):errors.append('Wrong Z hop')
 if not positive:errors.append('No printed extrusion')
 if not 0<maxacc<=700:errors.append('Acceleration outside host limits')
 if area_fail:errors.append('Nozzle-dependent extrusion cross-section exceeded')
 return dict(errors=sorted(set(errors)),start=expected,nozzle=ds,layer_height=h,pressure_advance_commands=pas,
  retraction_length=length,restart_extra=extra,retract_speed=speed,return_speed=back,retract_count=len(retracts),return_count=len(returns),
  z_hop=hop,hop_count=len(hops),positive_xy_extrusions=positive,max_acceleration=maxacc,
  peak_cross_section=area_peak,default_cross_section_limit=area_limit,cross_section_errors=area_fail[:3])


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--orca',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True);root=ROOT/'native';v=json.loads((root/'Zortrax.json').read_text())
 catalog=json.loads((ROOT/'evidence/R5_CATALOG.json').read_text());unsupported=set(catalog['catalog_only_materials'])
 assert len(v['machine_list'])==4 and len(v['filament_list'])==100 and len(v['process_list'])==84
 ids=set();objects={}
 for group in ['machine_model_list','machine_list','process_list','filament_list']:
  for item in v[group]:
   path=root/'Zortrax'/item['sub_path'];j=json.loads(path.read_text());assert j['name']==item['name']
   objects[j['name']]=(path,j)
   if group!='machine_model_list':
    assert j['from']=='system' and j['instantiation']=='true' and j['inherits']==''
    assert j['setting_id'] not in ids;ids.add(j['setting_id'])
    assert 'custom' not in j['name'].lower()
 results=[];stl=out/'two_towers.stl';test_stl(stl)
 env=dict(os.environ,LIBGL_ALWAYS_SOFTWARE='1',WEBKIT_DISABLE_DMABUF_RENDERER='1')
 for ds in ['0.2','0.3','0.4','0.6']:
  pname='Zortrax M300 '+ds;mp,p=objects[pname];h=.1 if ds=='0.2' else .2
  assert p['nozzle_diameter']==[ds] and p['printer_variant']==ds
  assert p['machine_pause_gcode'].strip()=='PAUSE' and p['use_relative_e_distances']=='1'
  assert len(p)==147 and h<float(ds)*.8
  cases=[]
  for mat in catalog['materials']:
   fn=mat+' @Zortrax M300 '+ds;fp,f=objects[fn];assert len(f)==126 and f['compatible_printers']==[pname]
   assert f['filament_vendor']==['Zortrax'] and f['filament_settings_id']==[fn]
   assert f['pressure_advance']==['0'] and f['adaptive_pressure_advance']==['0']
   assert all(float(val[0])<=105 for key,val in f.items() if '_plate_temp' in key)
   if mat in unsupported:
    assert f['filament_printable']==['0'];results.append(dict(nozzle=ds,material=mat,status='CATALOG_ONLY_NOT_SLICED'));continue
   assert float(f['nozzle_temperature_initial_layer'][0])<=265
   cases.append((mat,f'{h:.2f}mm {mat} @Zortrax M300 {ds}',0.,'material'))
  cases.extend([('Z-PLA Pro',p['default_print_profile'],0.,'default'),('Z-PLA Pro',p['default_print_profile'],.035,'pa_trial')])
  for mat,qn,pa,kind in cases:
   qp,q=objects[qn];fp,f=objects[mat+' @Zortrax M300 '+ds];assert len(q)==337 and q['compatible_printers']==[pname]
   folder=out/(ds.replace('.','p')+'_'+re.sub('[^A-Za-z0-9_-]','_',mat)+'_'+kind);folder.mkdir(exist_ok=True)
   test_f=copy.deepcopy(f)
   if pa:
    test_f['pressure_advance']=[str(pa)];fp=folder/'trial.json';fp.write_text(json.dumps(test_f))
   eff=folder/'effective.json'
   cmd=[a.orca,'--load-settings',str(mp)+';'+str(qp),'--load-filaments',str(fp),'--export-settings',str(eff),'--slice','0','--outputdir',str(folder),str(stl)]
   run=subprocess.run(cmd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180);(folder/'orca.log').write_text(run.stdout)
   files=list(folder.glob('*.gcode'));g=files[0].read_text(errors='replace') if files else ''
   ef=json.loads(eff.read_text()) if eff.exists() else {}
   detail=inspect(g,ef,p,q,test_f,pa) if g else {'errors':['No G-code generated']}
   if run.returncode:detail['errors'].append('Orca exit '+str(run.returncode))
   row=dict(nozzle=ds,material=mat,process=qn,kind=kind,status='FAIL' if detail['errors'] else 'PASS',gcode_bytes=len(g),details=detail)
   results.append(row);print(json.dumps({k:row[k] for k in ['nozzle','material','kind','status']}),detail['errors'],flush=True)
   (out/'results.json').write_text(json.dumps(results,indent=2))
 summary=dict(revision='R5',orca_version='2.3.2',native_index='PASS',metadata_adapter=False,
  material_pass=sum(r.get('kind')=='material' and r['status']=='PASS' for r in results),
  default_process_pass=sum(r.get('kind')=='default' and r['status']=='PASS' for r in results),
  pa_trial_pass=sum(r.get('kind')=='pa_trial' and r['status']=='PASS' for r in results),
  fail_count=sum(r['status']=='FAIL' for r in results),catalog_only_count=sum(r['status']=='CATALOG_ONLY_NOT_SLICED' for r in results),
  GUI_import_test=False,physical_test=False,host_changed=False,source_commit=os.environ.get('GITHUB_SHA'),workflow_run_id=os.environ.get('GITHUB_RUN_ID'))
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('SUMMARY='+json.dumps(summary),flush=True)
 assert summary['material_pass']==80 and summary['default_process_pass']==4 and summary['pa_trial_pass']==4 and summary['fail_count']==0

if __name__=='__main__':main()
