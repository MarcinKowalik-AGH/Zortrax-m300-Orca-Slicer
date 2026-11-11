#!/usr/bin/env python3
"""Native vendor Zortrax/M300 presets; provenance separates OEM data and adaptation."""
import copy,hashlib,io,json,uuid,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIAMETERS=['0.2','0.3','0.4','0.6']
BASE='profiles/Zortrax_M300_Classic_0p20_MicroSwiss_R3.orca_printer'
CATALOG_ONLY={'Z-PEEK','Z-PEI 1010','Z-PEI 9085','Z-SUPPORT High-Temp','Z-SUPPORT ATP 130'}
META={'type','instantiation','setting_id'}
def num(x):return format(round(float(x),6),'.6f').rstrip('0').rstrip('.') or '0'
def enc(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def write(path,data):
 path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(enc(data) if isinstance(data,(dict,list)) else data)
def archive(files):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for n,data in sorted(files.items()):
   info=zipfile.ZipInfo(n,(2026,11,11,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
 return b.getvalue()
def system(obj,kind):
 obj.update(type=kind,instantiation='true',setting_id=str(uuid.uuid5(uuid.NAMESPACE_URL,'zortrax-m300-r5/'+kind+'/'+obj['name'])),**{'from':'system'})
 return obj

def main():
 with zipfile.ZipFile(ROOT/BASE) as z:raw={n:json.loads(z.read(n)) for n in z.namelist()}
 manifest=raw['bundle_structure.json'];bp=raw[manifest['printer_config'][0]];bq=raw[manifest['process_config'][0]]
 bases={raw[n]['name'].split(' @')[0]:raw[n] for n in manifest['filament_config']}
 classic=json.loads((ROOT/'sources/ZSUITE_classic.json').read_text())['records']
 beta=json.loads((ROOT/'sources/ZSUITE_beta4.json').read_text())['records']
 materials=sorted(set(bases)|{r['material'] for r in beta if r['material'].startswith('Z-')})
 groups=[('classic','M300'),('classic','M200'),('classic','Inventure'),('beta4','M300Plus'),('beta4','M300Dual'),('beta4','M200Plus'),('beta4','Inventure'),('beta4','Endureal')]
 rows=classic+beta
 def select(mat,d,h):
  for version,printer in groups:
   candidates=[r for r in rows if r['source']==version and r['printer']==printer and r['material']==mat and r.get('infill','Standard')=='Standard']
   if not candidates:continue
   nozzle=min({r['nozzle'] for r in candidates},key=lambda n:abs(n-d));candidates=[r for r in candidates if r['nozzle']==nozzle]
   quality=next((q for q in ['Normal','Default','High','Draft'] if any(r.get('quality','Default')==q for r in candidates)),candidates[0].get('quality','Default'))
   candidates=[r for r in candidates if r.get('quality','Default')==quality]
   def height(r):return round(r['values'].get('SliceThickness',r['layer']),6)
   candidates.sort(key=height);nearest=min(candidates,key=lambda r:abs(height(r)-h))
   lower=[r for r in candidates if height(r)<=h+1e-6];upper=[r for r in candidates if height(r)>=h-1e-6]
   left=lower[-1] if lower else nearest;right=upper[0] if upper else nearest
   values=copy.deepcopy(nearest['values']);interpolated=[]
   if height(left)<h<height(right):
    t=(h-height(left))/(height(right)-height(left))
    for k,v in values.items():
     if any(s in k for s in ['Speed','Feed','Offset','Increment']) and k in left['values'] and k in right['values']:
      values[k]=left['values'][k]+t*(right['values'][k]-left['values'][k]);interpolated.append(k)
   src={k:nearest[k] for k in ['source','printer','material','nozzle','layer','quality','infill']}
   src.update(effective_source_layer=height(nearest),target_layer=h,target_nozzle=d,
      nozzle_adaptation='same diameter' if abs(nozzle-d)<1e-6 else 'geometric rescaling; not an OEM nozzle preset',
      height_method='linear interpolation' if interpolated else 'exact effective layer' if abs(height(nearest)-h)<1e-6 else 'nearest available layer; not interpolation',interpolated_fields=interpolated)
   return values,src
  return {},dict(source='project_R3_fallback',material=mat,target_layer=h,target_nozzle=d,reason='No named material table recovered in either installer')
 def value(v,*keys):
  for k in keys:
   if k in v:return v[k]
  return None
 def material_base(mat):
  if mat in bases:return bases[mat]
  return bases['Z-SUPPORT Premium'] if mat.startswith('Z-SUPPORT') else bases['Z-PEEK'] if mat.startswith('Z-PEI') else bases['Z-ULTRAT']
 vendor={'name':'Zortrax','version':'02.03.02.05','force_update':'0','description':'Zortrax M300 native Orca integration; source-derived and interpolated community profiles, not an official manufacturer release.',
  'machine_model_list':[{'name':'Zortrax M300','sub_path':'machine/Zortrax M300.json'}],'machine_list':[],'process_list':[],'filament_list':[]}
 model={'type':'machine_model','name':'Zortrax M300','model_id':'ZORTRAX_M300_CLASSIC','family':'Zortrax M300','machine_tech':'FFF','nozzle_diameter':';'.join(DIAMETERS),
  'default_materials':';'.join('Z-PLA Pro @Zortrax M300 '+d for d in DIAMETERS),'bed_model':'','bed_texture':'','hotend_model':'','url':'https://support.zortrax.com/m-series-specification/'}
 native={'Zortrax/machine/Zortrax M300.json':enc(model)};evidence={};summary=[];bundles={}
 for ds in DIAMETERS:
  d=float(ds);h=.1 if ds=='0.2' else .2;tag=ds.replace('.','p');pname='Zortrax M300 '+ds
  qname=f'{h:.2f}mm Standard @Zortrax M300 {ds}';p=copy.deepcopy(bp)
  p.update(name=pname,printer_settings_id=pname,printer_model='Zortrax M300',printer_variant=ds,nozzle_diameter=[ds],
    min_layer_height=[{'0.2':'0.05','0.3':'0.075','0.4':'0.09','0.6':'0.15'}[ds]],max_layer_height=[num(.75*d)],default_print_profile=qname,default_filament_profile=['Z-PLA Pro @Zortrax M300 '+ds])
  p['printer_notes']='Native Zortrax / M300 vendor integration. Community adaptation from Z-SUITE 2.32 and beta4; see field-level provenance. Physical nozzle and Klipper nozzle_diameter must both equal '+ds+'. Limits and PA calibration are not upgraded by this profile.'
  p['file_start_gcode']=f'; Zortrax M300 nozzle {ds}, layer {num(h)}; source-derived integration R5\n'
  system(p,'machine');native['Zortrax/machine/'+pname+'.json']=enc(p);vendor['machine_list'].append({'name':pname,'sub_path':'machine/'+pname+'.json'})
  per_files={'printer/'+pname+'.json':enc(dict(p,**{'from':'User'}))};mnames=[];qnames=[]
  def process(mat,name):
   v,source=select(mat,d,h);q=copy.deepcopy(bq);changes={}
   q.update(name=name,print_settings_id=name,compatible_printers=[pname],layer_height=num(h),initial_layer_print_height=num(h),filename_format=f'{{input_filename_base}}_M300_N{tag}_{{filament_preset[0]}}.gcode')
   for k in ['line_width','outer_wall_line_width','top_surface_line_width','internal_solid_infill_line_width']:q[k]=num(1.1*d)
   for k in ['inner_wall_line_width','sparse_infill_line_width']:q[k]=num(1.2*d)
   q['initial_layer_line_width']=num(1.25*d);q['support_line_width']=ds
   maps={'outer_wall_speed':['SL_ContourSpeed','Model.StandardLayer.SL_ContourSpeed'],
    'inner_wall_speed':['IV_ContourSpeed','Model.StandardLayer.SL_InnerContourSpeed'],
    'sparse_infill_speed':['IV_InfillSpeed','Model.Invisible.IV_InfillSpeed'],
    'internal_solid_infill_speed':['VD_InfillSpeed','Model.VisibleDefTop.VDT_InfillSpeed'],
    'top_surface_speed':['VT_InfillSpeed','Model.VisibleTop.VT_InfillSpeed'],
    'bridge_speed':['BR_InfillSpeed','Model.Bridge.BR_InfillSpeed'],
    'initial_layer_speed':['FL_ContourSpeed','Model.FirstLayerNoRaft.FLNR_ContourSpeed'],
    'initial_layer_infill_speed':['FL_InfillSpeed','Model.FirstLayerNoRaft.FLNR_InfillSpeed'],
    'support_speed':['SB_Speed','Support.SupportBase.SB_Speed'],
    'support_interface_speed':['SS_Speed','Support.SupportSurface.SS_Speed'],
    'travel_speed':['IdleMoveSpeed','Model.Retraction.R_IdleMoveSpeed']}
   for key,ks in maps.items():
    x=value(v,*ks)
    if x is not None and x>0:q[key]=num(min(300,x/60));changes[key]={'raw':x,'conversion':'mm/min / 60','result':q[key],'source':source}
   q['notes']='R5 Zortrax M300. '+('Shared process based on Z-PLA Pro; choose named material process for its extracted feature speeds.' if mat=='Z-PLA Pro' and 'Standard' in name else 'Material-specific process: '+mat+'.')+' Geometric widths, raft algorithm and accelerations are Orca/Klipper adaptations, not a claim of byte-equivalent OEM toolpaths.'
   system(q,'process');evidence[name]={'source':source,'fields':changes,'remaining_field_policy':'Complete R3 process schema retained; widths scaled 1.10/1.20/1.25*d, height 0.10 for d0.2 else0.20; host accelerations unchanged; unmapped feed/path fields are preserved only in source evidence.'}
   native['Zortrax/process/'+name+'.json']=enc(q);vendor['process_list'].append({'name':name,'sub_path':'process/'+name+'.json'})
   return q
  default=process('Z-PLA Pro',qname);per_files['process/'+qname+'.json']=enc(dict(default,**{'from':'User'}));qnames.append('process/'+qname+'.json')
  for mat in materials:
   original=material_base(mat);f=copy.deepcopy(original);fname=mat+' @Zortrax M300 '+ds
   f.update(name=fname,filament_settings_id=[fname],filament_vendor=['Zortrax'],filament_id='P'+hashlib.sha256(fname.encode()).hexdigest()[:12],compatible_printers=[pname])
   v,source=select(mat,d,h);fields={};warnings=[];unsupported=mat in CATALOG_ONLY
   def put(key,x,rawkey,why='source value'):
    f[key]=[num(x)];fields[key]={'value':f[key][0],'source_field':rawkey,'method':why}
   t=value(v,'TempExtruder','Material.Temperatures.TempExtruder');bed=value(v,'TempBed','Material.Temperatures.TempBed')
   if t is None:t=float(f['nozzle_temperature'][0])
   if bed is None:bed=float(f['hot_plate_temp'][0])
   actual_t=t if unsupported else min(265,t)
   if actual_t!=t:warnings.append(f'OEM nozzle {num(t)}C cannot be used under current host limit; {num(actual_t)}C is an unqualified thermal adaptation, not the OEM setting.')
   for k in ['nozzle_temperature','nozzle_temperature_initial_layer']:put(k,actual_t,'TempExtruder',f'{source["source"]}; raw={num(t)}; current working ceiling265 for non-catalog entries')
   f['nozzle_temperature_range_low']=[num(max(170,actual_t-20))];f['nozzle_temperature_range_high']=[num(actual_t+20 if unsupported else min(270,actual_t+20))]
   for k in f:
    if '_plate_temp' in k:put(k,min(105,bed),'TempBed',f'raw={num(bed)}; bed setpoint ceiling105')
   if bed>105:warnings.append('Source bed/chamber above M300 limits; catalogue-only material.')
   retract=value(v,'R_Back','Model.Retraction.R_Back','Support.Retraction.R_BackSupport')
   if retract is not None:put('filament_retraction_length',retract,'R_Back')
   for target,keys in [('filament_retraction_speed',['R_BackSpeed','Model.Retraction.R_BackSpeed','Support.Retraction.R_BackSupportSpeed']),('filament_deretraction_speed',['R_ForwardSpeed','Model.Retraction.R_ForwardSpeed','Support.Retraction.R_ForwardSupportSpeed'])]:
    x=value(v,*keys)
    if x is not None and x>0:
     put(target,min(45,x/60),' / '.join(keys),'mm/min /60, capped by host extrude-only velocity45mm/s')
     if x/60>45:warnings.append(f'{target}: source {num(x/60)}mm/s limited to45mm/s; host limit unchanged.')
   forward=value(v,'R_Forward');extra=value(v,'Model.Retraction.R_ForwardDiff','Support.Retraction.R_ForwardSupportDiff')
   if forward is not None and retract is not None:extra=max(0,forward-retract)
   if extra is not None:put('filament_retract_restart_extra',extra,'R_Forward-R_Back or R_ForwardDiff')
   for target,keys in [('filament_z_hop',['R_LiftZHeight','Model.Retraction.R_LiftZHeight']),('filament_retraction_minimum_travel',['R_MinLenght','Model.Retraction.R_MinLength'])]:
    x=value(v,*keys)
    if x is not None:put(target,x,' / '.join(keys))
   fan=value(v,'AutofanFixedSpeed','Model.Cooling.AutofanFixedSpeed');enabled=value(v,'AutofanFixedEnabled','Model.Cooling.AutofanFixedEnabled')
   if fan is not None and enabled:
    fan=fan*100 if source.get('source')=='classic' else fan
    for k in ['fan_min_speed','fan_max_speed']:put(k,min(100,max(0,fan)),'AutofanFixedSpeed','classic fraction*100; beta percentage')
   f['filament_printable']=['0' if unsupported else '1'];f['filament_is_support']=['1' if mat.startswith('Z-SUPPORT') else '0']
   f['enable_pressure_advance']=['1'];f['pressure_advance']=['0'];f['adaptive_pressure_advance']=['0']
   if mat in ['Z-ABS','Z-ABS 2']:f['filament_type']=['ABS']
   if mat.startswith('Z-PEI'):f['filament_type']=['PEI']
   if mat.startswith('Z-SUPPORT'):f['filament_type']=['PVA']
   for k in ['activate_chamber_temp_control','activate_air_filtration','chamber_temperature']:f[k]=['0']
   f['filament_notes']=[('CATALOG ONLY / NOT FOR M300 PRINTING. ' if unsupported else '')+'Zortrax material; native M300 Orca integration R5. Source: '+source.get('source','')+' / '+source.get('printer','project baseline')+'. '+source.get('nozzle_adaptation','')+'. '+' '.join(warnings)+' Flow multiplier/MVS remain unmeasured project defaults; OEM feed numbers are not treated as flow ratio. PA=0 requires calibration. This is not an official Zortrax Orca release.']
   system(f,'filament');assert set(original)<=set(f),'Lost filament field'
   native['Zortrax/filament/'+fname+'.json']=enc(f);vendor['filament_list'].append({'name':fname,'sub_path':'filament/'+fname+'.json'})
   per_files['filament/'+fname+'.json']=enc(dict(f,**{'from':'User'}));mnames.append('filament/'+fname+'.json')
   evidence[fname]={'source':source,'mapped_fields':fields,'warnings':warnings,'catalog_only':unsupported,
      'all_field_origins':{k:('mapped: '+fields[k]['method'] if k in fields else 'native metadata/name' if k in META|{'from','name','compatible_printers','filament_settings_id','filament_id','filament_vendor'} else 'project baseline / explicit R5 integration, not asserted OEM') for k in f}}
   if not unsupported:
    specific=f'{h:.2f}mm {mat} @Zortrax M300 {ds}';q=process(mat,specific)
    per_files['process/'+specific+'.json']=enc(dict(q,**{'from':'User'}));qnames.append('process/'+specific+'.json')
   summary.append({'nozzle':ds,'material':mat,'name':fname,'source':source,'nozzle_temperature':actual_t,'source_temperature':t,'bed_temperature':min(105,bed),'catalog_only':unsupported,'warnings':warnings})
  per_files['bundle_structure.json']=enc({'bundle_id':'Zortrax_M300_'+tag+'_R5','bundle_type':'printer config bundle','printer_preset_name':pname,'printer_config':['printer/'+pname+'.json'],'process_config':qnames,'filament_config':mnames,'version':'02.03.02.05'})
  bundle_name='Zortrax_M300_'+tag+'_R5.orca_printer';bundles[bundle_name]=archive(per_files);write('profiles/R5/'+bundle_name,bundles[bundle_name])
 native['Zortrax.json']=enc(vendor)
 for path,data in native.items():write('native/'+path,data)
 report={'revision':'R5','vendor':'Zortrax','model':'Zortrax M300','native_format':True,'official_zortrax_release':False,
  'source_priority':['classic named manufacturer table','beta4 named manufacturer table','project baseline and explicit geometric interpolation/extrapolation'],
  'classic_M300_records':sum(r['printer']=='M300' for r in classic),'beta_records':len(beta),'diameters':DIAMETERS,'materials':materials,
  'machine_count':len(vendor['machine_list']),'filament_count':len(vendor['filament_list']),'process_count':len(vendor['process_list']),
  'field_counts_base':{'machine':len(bp),'process':len(bq),'filament':len(next(iter(bases.values())))},'catalog_only_materials':sorted(CATALOG_ONLY),
  'profiles':summary,'GUI_import_test':False,'physical_test':False,'host_changed':False}
 write('evidence/R5_PROVENANCE.json',evidence);write('evidence/R5_CATALOG.json',report)
 native['INSTALL_NATIVE.py']=(ROOT/'tools/install_native_r5.py').read_bytes()
 native['INSTRUKCJA_PL.md']=(ROOT/'docs/R5_NATIVE_PL.md').read_bytes()
 write('profiles/R5/Zortrax_M300_NATIVE_R5.zip',archive(native))
 files=dict(bundles);files['Zortrax_M300_NATIVE_R5.zip']=archive(native);files['R5_CATALOG.json']=enc(report);files['INSTRUKCJA_PL.md']=native['INSTRUKCJA_PL.md']
 write('profiles/R5/M300_R5_KOMPLET.zip',archive(files))
 hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'profiles/R5').iterdir() if p.is_file() and p.name!='SHA256SUMS'}
 write('profiles/R5/SHA256SUMS',''.join(hashes[n]+'  '+n+'\n' for n in sorted(hashes)).encode())
 print(json.dumps({k:report[k] for k in ['revision','machine_count','filament_count','process_count','classic_M300_records','beta_records']}))
if __name__=='__main__':main()
