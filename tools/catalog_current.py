#!/usr/bin/env python3
"""Generate English migration tables from current presets and extracted source data.
No host access or profile mutation. Process suggestions are not OEM equivalence.
"""
import argparse,csv,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEEDS=[('Outer wall','SL_ContourSpeed','outer_wall_speed'),('Inner wall','IV_ContourSpeed','inner_wall_speed'),('Sparse infill','IV_InfillSpeed','sparse_infill_speed'),('Top surface','VT_InfillSpeed','top_surface_speed'),('Bridge','BR_InfillSpeed','bridge_speed'),('Travel','IdleMoveSpeed','travel_speed')]
EXTERNAL={'ABS-based filament':'Generic ABS','PLA-based filament':'Generic PLA','PETG-based filament':'Generic PETG'}
def load(p):return json.loads(p.read_text())
def scalar(v):return v[0] if isinstance(v,list) else v
def fmt(v):
 if v is None:return 'not recovered'
 return f'{v:.6f}'.rstrip('0').rstrip('.') if isinstance(v,float) else str(v)
def md(headers,rows):
 def cell(v):return fmt(v).replace('|','\\|').replace('\n',' ')
 return '\n'.join(['| '+' | '.join(map(cell,headers))+' |','| '+' | '.join('---' for _ in headers)+' |']+['| '+' | '.join(map(cell,row))+' |' for row in rows])+'\n'
def csv_text(rows):
 s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue()
def suggested(layer,quality):
 h=round(layer,2)
 if h==.09:return '0.08mm SuperDetail'
 if h==.14:return '0.12mm Detail' if quality=='High' else '0.16mm Optimal'
 if h==.19:return '0.20mm High Quality' if quality=='High' else '0.20mm Standard'
 if h==.29:return '0.28mm SuperDraft'
 return ''
def match_raw(source,records):
 keys=('source','printer','material','nozzle','layer','quality','infill')
 if not all(k in source for k in keys):return None
 return next((r for r in records if all(r[k]==source[k] for k in keys)),None)
def build(root=ROOT):
 v=load(root/'profiles/Zortrax.json')
 machines={e['name']:load(root/'profiles/Zortrax'/e['sub_path']) for e in v['machine_list']}
 qs={e['name']:load(root/'profiles/Zortrax'/e['sub_path']) for e in v['process_list']}
 fs={e['name']:load(root/'profiles/Zortrax'/e['sub_path']) for e in v['filament_list']}
 classic=load(root/'sources/zsuite_classic.json')['records'];beta=load(root/'sources/zsuite_beta4.json')['records'];prov=load(root/'sources/filament_provenance.json')
 m300=[(i,r) for i,r in enumerate(classic) if r['printer']=='M300']
 assert len(m300)==152 and len(qs)==30 and len(fs)==104
 processes=[]
 for name,q in qs.items():
  d=machines[q['compatible_printers'][0]]['printer_variant']
  processes.append({'nozzle_mm':d,'process':name,'layer_mm':q['layer_height'],'first_layer_mm':q['initial_layer_print_height'],'walls':q['wall_loops'],'infill_percent':q['sparse_infill_density'],'infill_pattern':q['sparse_infill_pattern'],'outer_width_mm':q['outer_wall_line_width'],'inner_width_mm':q['inner_wall_line_width'],'first_width_mm':q['initial_layer_line_width'],'outer_speed_mm_s':q['outer_wall_speed'],'inner_speed_mm_s':q['inner_wall_speed'],'infill_speed_mm_s':q['sparse_infill_speed'],'top_speed_mm_s':q['top_surface_speed'],'bridge_speed_mm_s':q['bridge_speed'],'travel_speed_mm_s':q['travel_speed'],'default_acceleration_mm_s2':q['default_acceleration'],'outer_acceleration_mm_s2':q['outer_wall_acceleration'],'infill_acceleration_mm_s2':q['sparse_infill_acceleration'],'travel_acceleration_mm_s2':q['travel_acceleration'],'top_layers':q['top_shell_layers'],'bottom_layers':q['bottom_shell_layers'],'top_min_thickness_mm':q['top_shell_thickness'],'bottom_min_thickness_mm':q['bottom_shell_thickness'],'raft_layers':q['raft_layers'],'raft_gap_mm':q['raft_contact_distance'],'support_enabled':q['enable_support'],'support_type':q['support_type'],'source':'profiles/Zortrax/process/'+name+'.json'})
 filaments=[]
 for name,f in sorted(fs.items()):
  p=machines[f['compatible_printers'][0]];d=p['printer_variant'];material=name.split(' @')[0];source=prov.get(name,{}).get('source',{});record=match_raw(source,classic+beta);values=record['values'] if record else {}
  raw_hot=values.get('TempExtruder',values.get('Material.Temperatures.TempExtruder'));raw_bed=values.get('TempBed',values.get('Material.Temperatures.TempBed'))
  def override(k):
   x=scalar(f.get('filament_'+k,['nil']));return scalar(p[k]) if x=='nil' else x
  origin=source.get('source','Generic starter')+' / '+source.get('printer','not OEM')
  if material=='Z-PHA':origin='Project fallback / no named source table recovered'
  filaments.append({'material':material,'nozzle_mm':d,'filament':name,'source_origin':origin,'source_record_nozzle_mm':source.get('nozzle',''),'source_displayed_layer_mm':source.get('layer',''),'source_hotend_c':raw_hot if raw_hot is not None else '','source_bed_c':raw_bed if raw_bed is not None else '','initial_hotend_c':scalar(f['nozzle_temperature_initial_layer']),'hotend_c':scalar(f['nozzle_temperature']),'initial_bed_c':scalar(f['hot_plate_temp_initial_layer']),'bed_c':scalar(f['hot_plate_temp']),'flow_ratio':scalar(f['filament_flow_ratio']),'max_volumetric_mm3_s':scalar(f['filament_max_volumetric_speed']),'pressure_advance':scalar(f['pressure_advance']),'retraction_mm':override('retraction_length'),'retraction_mm_s':override('retraction_speed'),'unretraction_mm_s':override('deretraction_speed'),'restart_extra_mm':override('retract_restart_extra'),'z_hop_mm':override('z_hop'),'fan_min_percent':scalar(f['fan_min_speed']),'fan_max_percent':scalar(f['fan_max_speed']),'host_305c_status':'EXCEEDS 305C: reference only, do not print' if float(scalar(f['nozzle_temperature']))>305 else 'Within stated hotend target ceiling only; not hardware qualification','notes':'Bed 50C is a user-observed 0.4 mm Z-PLA start-test override, not an OEM recommendation.' if name=='Z-PLA @Zortrax M300 0.4' else 'Source and profile are not proof of adhesion, flow, nozzle, chamber or hardware compatibility.','source':'profiles/Zortrax/filament/'+name+'.json'})
 mapped=[]
 for i,r in m300:
  values=r['values'];candidate=suggested(r['layer'],r['quality']);full=candidate+' @Zortrax M300 Classic 0.4 nozzle' if candidate else '';q=qs.get(full)
  material=r['material'];filament=material if material.startswith('Z-') else EXTERNAL.get(material,'');fn=filament+' @Zortrax M300 0.4' if filament else '';f=fs.get(fn)
  row={'source_id':f'classic/records/{i}','zsuite_material':material,'zsuite_nozzle_mm':r['nozzle'],'zsuite_displayed_layer_mm':r['layer'],'zsuite_SliceThickness_mm':round(values['SliceThickness'],6),'zsuite_quality':r['quality'],'zsuite_infill_mode':r['infill'],'orca_filament':fn or 'No direct named Generic; create and qualify a custom material','orca_process':full or 'No supplied process for 0.4 mm nozzle','orca_layer_mm':q['layer_height'] if q else '','match_scope':'Functional process suggestion, NOT complete profile or toolpath equivalence' if q else 'No direct candidate','required_manual_changes':'Copy actual shell, top/bottom and infill settings; no automatic Shell conversion' if r['infill']=='Shell' else 'Copy the actual infill density/pattern, shells, support and raft settings','zsuite_hotend_c':values.get('TempExtruder',''),'orca_hotend_c':scalar(f['nozzle_temperature']) if f else '','zsuite_bed_c':values.get('TempBed',''),'orca_bed_c':scalar(f['hot_plate_temp']) if f else ''}
  for label,k,qk in SPEEDS:
   prefix=qk.replace('_speed','');raw=values.get(k);row['zsuite_'+prefix+'_mm_s']=round(raw/60,6) if raw is not None else '';row['orca_'+prefix+'_mm_s']=q[qk] if q else ''
  mapped.append(row)
 speeds=[]
 for quality in ('Normal','High','Draft'):
  record=next(r for _,r in m300 if r['material']=='Z-PLA Pro' and r['quality']==quality and r['layer']==.19 and r['infill']=='Standard');candidate=suggested(.19,quality);q=qs[candidate+' @Zortrax M300 Classic 0.4 nozzle']
  for feature,k,qk in SPEEDS:
   raw=record['values'][k];a=raw/60;b=float(q[qk]);speeds.append({'zsuite_quality':quality,'orca_process':candidate,'feature':feature,'source_field':k,'source_mm_min':raw,'source_mm_s':round(a,6),'orca_field':qk,'orca_mm_s':b,'delta_mm_s':round(b-a,6),'same_numeric_speed':abs(a-b)<1e-5})
 outputs={'docs/tables/processes.csv':csv_text(processes),'docs/tables/filaments.csv':csv_text(filaments),'docs/tables/zsuite_m300_correspondence.csv':csv_text(mapped),'docs/tables/pla_pro_speed_comparison.csv':csv_text(speeds)}
 quick=[('0.09 High/Normal',.09,.10,'0.08mm SuperDetail',.08,'Thinner functional approximation; no supplied 0.09/0.10 process for nozzle 0.4.'),('0.14 High',.14,.15,'0.12mm Detail',.12,'Thinner approximation, not the recovered High mode.'),('0.14 Normal/Default',.14,.15,'0.16mm Optimal',.16,'Slightly thicker; use a custom 0.14/0.15 process for the chosen numerical target.'),('0.19 Normal/Default',.19,.20,'0.20mm Standard',.20,'Best starting point; six speed fields match only the cited PLA Pro Normal example.'),('0.19 High',.19,.20,'0.20mm High Quality',.20,'Functional equivalent only; three walls and different speeds.'),('0.19 Draft',.19,.20,'0.20mm Standard',.20,'No 0.20 Draft preset; save a copy and compare material-specific speeds.'),('0.29 Normal/Draft',.29,.30,'0.28mm SuperDraft',.28,'Coarse approximation; default infill is 10%, not the Z-SUITE project percentage.'),('0.39 external ABS-family records',.39,.39,'None for nozzle 0.4','—','Only two source records; do not silently change the physical nozzle.')]
 source_materials=[]
 for material in sorted({r['material'] for _,r in m300}):
  rs=[r for _,r in m300 if r['material']==material];target=material+' @Zortrax M300 0.4' if material.startswith('Z-') else (EXTERNAL[material]+' @Zortrax M300 0.4' if material in EXTERNAL else 'No direct Generic; create a separately qualified custom filament')
  source_materials.append((material,', '.join(fmt(h) for h in sorted({r['layer'] for r in rs})),', '.join(sorted({r['quality'] for r in rs})),len(rs),target))
 d4=[r for r in filaments if r['nozzle_mm']=='0.4']
 text='''# Z-SUITE → OrcaSlicer: M300 Classic migration tables

**Current profile set: R7.1 · OrcaSlicer target: 2.5.0.** Values below are generated from committed source records and current preset files, not remembered defaults. Source terminology is preserved: **material, displayed layer, quality and infill mode**. An original Z-SUITE selection is split between **Printer/Variant**, **Filament** and **Process** in Orca.

**There is no complete 1:1 conversion.** A recovered source field, a matching numerical value and a recommended functional process are three different claims. Neither field recovery nor an individual match proves identical toolpaths or print quality. Process suggestions are explicitly project judgments.

## 1. Practical process crosswalk — physically installed 0.4 mm nozzle

The recovered Classic M300 records contain only a **0.4 mm nozzle**. Other Orca variants are project adaptations; M300 Plus/Dual support is not evidence of Classic support.

'''+md(['Z-SUITE selection','Displayed mm','Recovered SliceThickness mm','Suggested Orca process','Orca mm','Difference / action'],quick)+'''
The **SliceThickness column is a recovered configuration field**, not a measurement or proof that the UI label was wrong. Keep 0.09/0.14/0.19/0.29 labels separate from 0.10/0.15/0.20/0.30 fields. To preserve one numeric height, save a user copy and set it explicitly; still review first-layer height, raft gap, shells and speeds.

## 2. Which source material selections exist for Classic M300?

The Classic extraction has **152 M300 records** covering **seven named Z materials and seven external families**. Counts include Standard/Shell modes and multiple qualities; they are not 152 independent polymers. Generic is a starting template, not a copied external-material calibration.

'''+md(['Z-SUITE material/family','Displayed layers mm','Source qualities','Records','Orca filament / action'],source_materials)+'''
Do not silently relabel GLASS-type, ESD v2-based or PCABS-based as Generic PETG, Generic PLA or Generic PC. No exact supplied Generic counterpart is claimed. **Z-PLA and Z-PLA Pro are separate materials.**

## 3. All 30 current processes

Full names append `@Zortrax M300 Classic <diameter> nozzle`. Speeds are nominal stored mm/s, not observed motion. Process geometry, walls, fill, speeds, accelerations, raft and supports depend on nozzle, not only layer height. A 0.16 mm layer exists for all four nozzle sizes; a 0.20 mm process is not supplied for a 0.2 mm nozzle.

'''+md(['Nozzle mm','Process','Layer mm','Walls','Infill','Outer mm/s','Top mm/s','Raft gap mm'],[(r['nozzle_mm'],r['process'].split(' @')[0],r['layer_mm'],r['walls'],r['infill_percent']+' '+r['infill_pattern'],r['outer_speed_mm_s'],r['top_speed_mm_s'],r['raft_gap_mm']) for r in processes])+'''
The [complete process CSV](tables/processes.csv) also contains widths, six speed categories, accelerations, shell counts/thicknesses, support type and first-layer height. High Quality is not the source High table; Strength is 40% gyroid/four walls, not Solid/100%; Draft also changes layer and shell/fill values.

## 4. Speed comparison: Z-PLA Pro, nozzle 0.4, displayed layer 0.19

Recovered `SliceThickness` is approximately 0.20 mm. This example uses **Standard infill mode**. Source mm/min values are divided by 60 and rounded here for readability.

'''+md(['Source quality','Orca process','Feature','Source mm/min','Source mm/s','Orca mm/s','Difference mm/s'],[(r['zsuite_quality'],r['orca_process'],r['feature'],r['source_mm_min'],r['source_mm_s'],r['orca_mm_s'],r['delta_mm_s']) for r in speeds])+'''
All six listed **Normal** speeds match the Standard process in this example only. High Quality and Draft do not. Other source materials have different speed tables. Selecting a different Filament does **not** automatically replace the shared Process speeds. The shared quality family cannot simultaneously reproduce every source material's modes.

## 5. Zortrax filament table — exact selected source versus current values

This table is for **nozzle 0.4 mm**. Source temperatures come from the exact selected record identified by the retained provenance, not generic manufacturer guidance. Other-model origins (M200, Inventure, M300Plus, Endureal) are labeled rather than claimed as Classic OEM settings. Missing data mean not recovered, not zero.

'''+md(['Material','Actual source','Source nozzle °C','Source bed °C','Current nozzle °C','Current bed °C','Qualification'],[(r['material'],r['source_origin'],r['source_hotend_c'] if r['source_hotend_c']!='' else 'not recovered',r['source_bed_c'] if r['source_bed_c']!='' else 'not recovered',r['hotend_c'],r['bed_c'],'REFERENCE ONLY >305C' if float(r['hotend_c'])>305 else 'Not physically qualified') for r in d4 if r['material'].startswith('Z-')])+'''
**Z-PLA 0.4 exception:** 50°C bed replaces the 30°C source baseline based on one user-reported print start at 210/50°C. The other three Z-PLA nozzle presets retain 30°C. This is not a completed-print test or universal manufacturer recommendation. Cleanup changes none of these values.

**PEEK/PEI references:** 400/370/360°C exceed the stated 305°C hotend target limit, and source bed/chamber requirements may also exceed the setup. A capped 105°C profile bed setting does not qualify the material. Do not send these reference-only presets to this host.

## 6. Filament tuning values — all 26 names for nozzle 0.4

`nil` overrides are resolved from the corresponding Printer preset in this table. Flow ratio, MVS and PA are project values, not direct conversions of source `...Feed` fields. Distances are mm; speed is mm/s; MVS is mm³/s.

'''+md(['Material','Flow','MVS','PA','Retract mm','Retract mm/s','Return mm/s','Extra return mm','Z-hop mm'],[(r['material'],r['flow_ratio'],r['max_volumetric_mm3_s'],r['pressure_advance'],r['retraction_mm'],r['retraction_mm_s'],r['unretraction_mm_s'],r['restart_extra_mm'],r['z_hop_mm']) for r in d4])+'''
The [104-row filament CSV](tables/filaments.csv) covers every nozzle size and complete name. The Generic families are PLA/PETG/ABS/ASA/TPU/PA/PC, not brand calibrations. Use Save As for SUNLU or another brand, preserve printer compatibility, and tune the actual spool/nozzle. No dedicated Z-SUPPORT preset is supplied; ordinary same-material support geometry remains available.

## 7. All 152 source combinations, record by record

The [correspondence CSV](tables/zsuite_m300_correspondence.csv) preserves each source array index, material, nozzle, displayed height, `SliceThickness`, quality and infill mode. Each row pairs a suggested current process/filament (or an explicit no-match) with source/current temperatures and six source/current speed categories. Shell rows require manual shell/fill choices; the suggestion is not a completed Shell conversion.

**Example:** Classic M300 / 0.4 / Z-PLA Pro / displayed 0.19 / Normal / 20% rectilinear → `Z-PLA Pro @Zortrax M300 0.4` and `0.20mm Standard @Zortrax M300 Classic 0.4 nozzle`, with infill explicitly changed **15% → 20%** and actual shells/supports/raft reviewed. The 20% is a project example, not recovered from the Standard label.

## 8. Evidence and unresolved mappings

Sources: [Classic records](../sources/zsuite_classic.json), [beta-4 records](../sources/zsuite_beta4.json), [current filament provenance](../sources/filament_provenance.json), [checksums](../sources/MANIFEST.json), [current profiles](../profiles/). Raw evidence can mention other printers or support materials; it does not add installable presets.

The extraction did not execute the full OEM slicing pipeline. Records alone cannot prove identical raft zones, feed semantics, shells, seams or firmware behavior. Missing mappings are not invented. See the [settings dictionary](SETTINGS_REFERENCE.md), [profile guide](PROFILES.md) and [validation scope](VALIDATION.md). Regenerate tables with `python3 tools/catalog.py`; use `--check` to verify without writing.
'''
 outputs['docs/ZSUITE_TO_ORCA.md']=text
 outputs['docs/tables/README.md']='''# Current machine-readable tables

Generated directly from current `profiles/` and `sources/` by `tools/catalog.py`. These are UTF-8 comma-delimited CSV files; decimal values use a dot. GitHub displays them as tables and Excel can import them. They are not extra installable profile versions.

| File | Rows | Purpose |
|---|---:|---|
| [processes.csv](processes.csv) | 30 | All processes: geometry, speeds, accelerations, shell/support/raft values |
| [filaments.csv](filaments.csv) | 104 | All filament/nozzle combinations: source/current temperatures and effective tuning values |
| [zsuite_m300_correspondence.csv](zsuite_m300_correspondence.csv) | 152 | Every recovered M300 selection with an explicitly approximate counterpart |
| [pla_pro_speed_comparison.csv](pla_pro_speed_comparison.csv) | 18 | Six feature speeds for Normal, High and Draft |

[Human-readable comparison](../ZSUITE_TO_ORCA.md). No table asserts identical OEM toolpaths or physical material qualification.
'''
 return outputs,{'processes':processes,'filaments':filaments,'mapped':mapped,'speeds':speeds}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');a=ap.parse_args();outputs,tables=build();stale=[]
 for name,text in outputs.items():
  p=ROOT/name;data=text.encode()
  if a.check:
   if not p.is_file() or p.read_bytes()!=data:stale.append(name)
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 if stale:raise SystemExit('Stale generated tables: '+', '.join(stale))
 print(json.dumps({'status':'PASS','mode':'check' if a.check else 'generate',**{k:len(v) for k,v in tables.items()}}))
if __name__=='__main__':main()
