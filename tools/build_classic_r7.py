#!/usr/bin/env python3
"""R7: model/variant UI and quality-based processes. No printer or config access.
Layout follows the user's K2 screenshot, not K2 motion/temperature parameters.
R6 remains the immutable numerical baseline. New quality labels are adaptations,
not claims that these exact process families were published in Z-SUITE.
"""
import argparse,copy,hashlib,json,math,shutil,uuid,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL='Zortrax M300 Classic'
DIAMETERS=('0.2','0.3','0.4','0.6')
COMMON=[(.08,'SuperDetail'),(.12,'Detail'),(.16,'Optimal'),(.20,'High Quality'),(.20,'Standard'),(.20,'Strength'),(.24,'Draft'),(.28,'SuperDraft')]
PROCESS_SPECS={
 '0.2':[(.06,'Fine'),(.08,'SuperDetail'),(.10,'Standard'),(.12,'Detail'),(.16,'Optimal')],
 '0.3':COMMON[:-1], '0.4':COMMON,
 '0.6':COMMON[1:]+[(.32,'Coarse'),(.36,'Draft'),(.42,'SuperDraft')],
}
GENERIC={
 'PLA':('Z-PLA Pro',210,60,100,8,'PLA'),
 'PETG':('Z-PETG',240,80,40,6,'PETG'),
 'ABS':('Z-ABS',250,100,20,8,'ABS'),
 'ASA':('Z-ASA Pro',255,100,20,8,'ASA'),
 'TPU':('Z-FLEX',225,50,60,3,'TPU'),
 'PA':('Z-NYLON',260,90,20,6,'PA'),
 'PC':('Z-PCABS',280,105,20,6,'PC'),
}

def encoded(obj):
 # Native vendor loader distinguishes no parent from an explicitly empty
 # parent name. CLI --load-settings accepted the latter, the GUI does not.
 # These are flat complete presets: remove only this empty metadata key.
 if isinstance(obj,dict) and obj.get('from')=='system' and obj.get('inherits')=='':
  obj=copy.deepcopy(obj);del obj['inherits']
 return (json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
def scalar(x):return format(float(x),'.6f').rstrip('0').rstrip('.')
def pid(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,'m300-classic-r7/'+name))
def process_name(d,h,label):return f'{h:.2f}mm {label} @{MODEL} {d} nozzle'
def printer_name(d):return f'{MODEL} {d} nozzle'


def generate(root=ROOT):
 baseline=root/'profiles/R6/Zortrax_M300_NATIVE_R6.zip'
 with zipfile.ZipFile(baseline) as z:
  assert z.testzip() is None
  data={n:json.loads(z.read(n)) for n in z.namelist() if n.endswith('.json')}
 vendor=copy.deepcopy(data['Zortrax.json'])
 vendor.update(version='02.05.00.07',description='M300 Classic community integration. One model/four nozzle variants; quality processes from M300 baseline; no K2 motion settings.')
 for group in ('machine_model_list','machine_list','process_list','filament_list'):vendor[group]=[]
 out={};report={'revision':'R7','orca_version':'2.5.0','source_bundle_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),
  'model':MODEL,'diameters':list(DIAMETERS),'quality_processes':[],'generic_materials':list(GENERIC),
  'source_policy':'Zortrax material temperatures/retraction/PA unchanged from R6. Process base R6 Standard; quality/geometric overrides are community adaptations. Generic inputs are uncalibrated starting values.',
  'native_loader_fix':'Empty inherits key omitted for flat system presets; source numerical settings unchanged.',
  'klipper_changed':False,'user_config_modified_by_builder':False}
 model=copy.deepcopy(data['Zortrax/machine/Zortrax M300.json'])
 model.update(name=MODEL,model_id='ZORTRAX_M300_CLASSIC',family='Zortrax',nozzle_diameter=';'.join(DIAMETERS),default_bed_type='High Temp Plate')
 model['default_materials']=';'.join([f'Z-PLA Pro @Zortrax M300 {d}' for d in DIAMETERS]+[f'Generic PLA @Zortrax M300 {d}' for d in DIAMETERS])
 out['Zortrax/machine/'+MODEL+'.json']=encoded(model)
 vendor['machine_model_list'].append({'name':MODEL,'sub_path':'machine/'+MODEL+'.json'})
 for d in DIAMETERS:
  dn=float(d);name=printer_name(d)
  p=copy.deepcopy(data[f'Zortrax/machine/Zortrax M300 {d}.json'])
  default=process_name(d,.10 if d=='0.2' else .20,'Standard')
  p.update(name=name,printer_model=MODEL,printer_settings_id=name,printer_variant=d,setting_id=pid(name),default_print_profile=default,
   min_layer_height=[scalar(.2*dn)],max_layer_height=[scalar(.8*dn)],file_start_gcode=f'; {MODEL} / nozzle {d} / R7\n')
  p['printer_agent']='orca'
  p['printer_notes']='R7 one-model nozzle variant. Existing M300 G-code and motion limits retained. No host update. Select the physically installed nozzle. Quality preset heights must fit nozzle; PA requires calibration.'
  out[f'Zortrax/machine/{name}.json']=encoded(p)
  vendor['machine_list'].append({'name':name,'sub_path':f'machine/{name}.json'})
  source_process=data[f'Zortrax/process/{"0.10" if d=="0.2" else "0.20"}mm Standard @Zortrax M300 {d}.json']
  for height,label in PROCESS_SPECS[d]:
   assert .2*dn-1e-8<=height<=.8*dn+1e-8
   q=copy.deepcopy(source_process);qn=process_name(d,height,label)
   q.update(name=qn,print_settings_id=qn,setting_id=pid(qn),compatible_printers=[name],layer_height=scalar(height),
    initial_layer_print_height=scalar(min(.2,.6*dn,height)),raft_contact_distance=scalar(min(.15,height)),
    filename_format='{input_filename_base}_M300_'+d.replace('.','p')+'_'+str(round(height,2)).replace('.','p')+'.gcode')
   for k in ('line_width','outer_wall_line_width','top_surface_line_width','internal_solid_infill_line_width'):q[k]=scalar(1.1*dn)
   for k in ('inner_wall_line_width','sparse_infill_line_width'):q[k]=scalar(1.2*dn)
   q['initial_layer_line_width']=scalar(1.25*dn);q['support_line_width']=d
   q['support_top_z_distance']=scalar(height);q['support_bottom_z_distance']=scalar(height)
   q['wall_loops']='2';q['sparse_infill_density']='15%'
   top,bottom=.8,.6
   factor=.7 if label in ('Fine','SuperDetail') else .85 if label=='Detail' else .9 if label=='Optimal' else 1.
   for k in ('outer_wall_speed','top_surface_speed'):q[k]=scalar(float(q[k])*factor)
   if label=='High Quality':
    q['wall_loops']='3';top,bottom=1.0,.8
    q['outer_wall_speed']=scalar(float(source_process['outer_wall_speed'])*.75)
    q['top_surface_speed']=scalar(float(source_process['top_surface_speed'])*.5)
   elif label=='Strength':
    q['wall_loops']='4';q['sparse_infill_density']='40%';q['sparse_infill_pattern']='gyroid';top,bottom=1.2,1.0
   elif label in ('Draft','SuperDraft','Coarse'):
    q['sparse_infill_density']='10%';top,bottom=.6,.5
   for k,t in [('top',top),('bottom',bottom)]:
    q[k+'_shell_layers']=str(max(3,math.ceil(t/height-1e-8)));q[k+'_shell_thickness']=scalar(t)
   q['notes']='R7 quality family (not material-specific). Geometry/raft contact and quality overrides adapted for M300; no Creality speeds/accels copied. R6 Standard supplies base speeds; per-material temperature/cooling/MVS stay in filament. NOT claimed exact Z-SUITE material toolpath.'
   out[f'Zortrax/process/{qn}.json']=encoded(q);vendor['process_list'].append({'name':qn,'sub_path':f'process/{qn}.json'})
   report['quality_processes'].append({'nozzle':d,'name':qn,'layer_height':height,'label':label,'wall_loops':int(q['wall_loops']),
    'infill':q['sparse_infill_density'],'outer_wall_speed':q['outer_wall_speed'],'top_surface_speed':q['top_surface_speed'],'line_width':q['line_width'],
    'first_layer_height':q['initial_layer_print_height'],'raft_contact_distance':q['raft_contact_distance']})
  for entry in data['Zortrax.json']['filament_list']:
   f0=data['Zortrax/'+entry['sub_path']]
   if not f0['name'].endswith(' @Zortrax M300 '+d):continue
   f=copy.deepcopy(f0);f['compatible_printers']=[name]
   assert not f['name'].startswith('Z-SUPPORT')
   out['Zortrax/'+entry['sub_path']]=encoded(f);vendor['filament_list'].append(copy.deepcopy(entry))
  for material,(template,temp,bed,fan,mvs,ftype) in GENERIC.items():
   f=copy.deepcopy(data[f'Zortrax/filament/{template} @Zortrax M300 {d}.json'])
   fn=f'Generic {material} @Zortrax M300 {d}'
   f.update(name=fn,filament_settings_id=[fn],filament_vendor=['Generic'],filament_type=[ftype],compatible_printers=[name],
    setting_id=pid(fn),filament_id='P'+hashlib.sha256(fn.encode()).hexdigest()[:12],filament_is_support=['0'],filament_printable=['1'],
    filament_flow_ratio=['1'],filament_max_volumetric_speed=[scalar(mvs)],enable_pressure_advance=['1'],pressure_advance=['0'],adaptive_pressure_advance=['0'])
   f['nozzle_temperature']=[str(temp)];f['nozzle_temperature_initial_layer']=[str(temp)]
   f['nozzle_temperature_range_low']=[str(temp-15)];f['nozzle_temperature_range_high']=[str(min(305,temp+15))]
   for key in f:
    if '_plate_temp' in key:f[key]=[str(bed)]
   f['fan_min_speed']=[str(fan)];f['fan_max_speed']=[str(fan)]
   f['filament_retraction_length']=['0.8' if material=='TPU' else '1']
   f['filament_retraction_speed']=['20' if material=='TPU' else '35'];f['filament_deretraction_speed']=list(f['filament_retraction_speed'])
   f['filament_retract_restart_extra']=['0']
   f['filament_notes']=['Generic starting profile, not manufacturer calibration. Check actual spool temperature/adhesion. Save As e.g. SUNLU PLA @Zortrax M300 '+d+'; keep compatible printer, calibrate flow/PA/retraction. No automatic Klipper changes.']
   sub='filament/'+fn+'.json';out['Zortrax/'+sub]=encoded(f);vendor['filament_list'].append({'name':fn,'sub_path':sub})
 out['Zortrax.json']=encoded(vendor)
 assert len(vendor['machine_model_list'])==1 and len(vendor['machine_list'])==4
 assert len(vendor['filament_list'])==104 and len(vendor['process_list'])==30
 report.update(model_count=1,machine_variant_count=4,filament_count=104,process_count=30,zortrax_materials=19,generic_material_count=7)
 return out,report


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
 outputs,report=generate();target=ROOT/'native_r7'
 if a.check:
  assert {str(p.relative_to(target)) for p in target.rglob('*.json')}==set(outputs)
  assert all((target/p).read_bytes()==b for p,b in outputs.items())
 else:
  if target.exists():shutil.rmtree(target)
  for p,b in outputs.items():q=target/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
  (ROOT/'evidence').mkdir(exist_ok=True);(ROOT/'evidence/R7_PROCESS_CATALOG.json').write_bytes(encoded(report))
 print(json.dumps({k:report[k] for k in ('revision','model_count','machine_variant_count','filament_count','process_count')}))
if __name__=='__main__':main()
