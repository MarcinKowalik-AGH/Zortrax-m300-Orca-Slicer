"""Current profile/source/table contracts. No printer connection."""
import json,unittest,sys,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from catalog import build
from validate import validate
class CurrentProfileTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.outputs,cls.tables=build();cls.vendor=json.loads((ROOT/'profiles/Zortrax.json').read_text())
 def test_full_repository_contract(self):self.assertEqual(validate()['status'],'PASS')
 def test_all_152_source_rows_once(self):
  ids=[r['source_id'] for r in self.tables['mapped']];self.assertEqual(len(ids),152);self.assertEqual(len(set(ids)),152)
 def test_only_oem_classic_point_four(self):self.assertEqual({r['zsuite_nozzle_mm'] for r in self.tables['mapped']},{.4})
 def test_recovered_labels_not_overwritten(self):
  rs=[r for r in self.tables['mapped'] if r['zsuite_displayed_layer_mm']==.19];self.assertTrue(rs);self.assertTrue(all(r['zsuite_SliceThickness_mm']==.2 for r in rs))
 def test_thirty_processes_and_104_filaments(self):self.assertEqual((len(self.tables['processes']),len(self.tables['filaments'])),(30,104))
 def test_19_zortrax_and_7_generic_per_nozzle(self):
  for d in ('0.2','0.3','0.4','0.6'):
   rs=[r for r in self.tables['filaments'] if r['nozzle_mm']==d];self.assertEqual(sum(r['material'].startswith('Z-') for r in rs),19);self.assertEqual(sum(r['material'].startswith('Generic ') for r in rs),7)
 def test_normal_pla_pro_six_speed_matches(self):
  rs=[r for r in self.tables['speeds'] if r['zsuite_quality']=='Normal'];self.assertEqual(len(rs),6);self.assertTrue(all(r['same_numeric_speed'] for r in rs))
 def test_high_quality_is_not_source_high(self):self.assertTrue(any(not r['same_numeric_speed'] for r in self.tables['speeds'] if r['zsuite_quality']=='High'))
 def test_no_false_point_39_profile(self):
  rs=[r for r in self.tables['mapped'] if r['zsuite_displayed_layer_mm']==.39];self.assertEqual(len(rs),2);self.assertTrue(all(r['orca_process']=='No supplied process for 0.4 mm nozzle' for r in rs))
 def test_shell_not_automatically_converted(self):
  rs=[r for r in self.tables['mapped'] if r['zsuite_infill_mode']=='Shell'];self.assertEqual(len(rs),75);self.assertTrue(all('no automatic Shell conversion' in r['required_manual_changes'] for r in rs))
 def test_no_invented_pcabs_generic(self):
  rs=[r for r in self.tables['mapped'] if r['zsuite_material']=='PCABS-based filament'];self.assertTrue(all('No direct' in r['orca_filament'] for r in rs))
 def test_pla_point_four_current_and_source_bed(self):
  r=next(r for r in self.tables['filaments'] if r['filament']=='Z-PLA @Zortrax M300 0.4')
  self.assertEqual(r['source_bed_c'],30)
  self.assertEqual((r['initial_hotend_c'],r['initial_bed_c']),('230','70'))
  self.assertEqual((r['hotend_c'],r['bed_c']),('210','50'))
  for name in ('Z-PLA','Z-PLA Pro','Generic PLA'):
   for nozzle in ('0.2','0.3','0.4','0.6'):
    x=next(r for r in self.tables['filaments'] if r['filament']==name+' @Zortrax M300 '+nozzle)
    self.assertEqual((x['initial_hotend_c'],x['initial_bed_c']),('230','70'))
 def test_only_below_floor_materials_are_raised(self):
  changed=('Z-SEMIFLEX','Z-GLASS','Z-PETG')
  preserved={'Z-PHA':'55','Generic TPU':'50','Z-FLEX':'50','Z-ASA Pro':'65','Z-ULTRAT Plus':'100'}
  for nozzle in ('0.2','0.3','0.4','0.6'):
   for name in changed:
    r=next(r for r in self.tables['filaments'] if r['filament']==name+' @Zortrax M300 '+nozzle)
    self.assertEqual((r['initial_bed_c'],r['bed_c']),('40','35'))
   for name,temperature in preserved.items():
    r=next(r for r in self.tables['filaments'] if r['filament']==name+' @Zortrax M300 '+nozzle)
    self.assertEqual((r['initial_bed_c'],r['bed_c']),(temperature,temperature))
 def test_high_temperature_reference_not_marked_qualified(self):
  rs=[r for r in self.tables['filaments'] if r['material'] in ('Z-PEEK','Z-PEI 1010','Z-PEI 9085')];self.assertEqual(len(rs),12);self.assertTrue(all('do not print' in r['host_305c_status'] for r in rs))
 def test_generated_docs_are_current(self):
  for name,text in self.outputs.items():self.assertEqual((ROOT/name).read_bytes(),text.encode())
 def test_m300_bed_texture_asset_exists(self):
  model=json.loads((ROOT/'profiles/Zortrax/machine/Zortrax M300 Classic.json').read_text())
  self.assertEqual(model['bed_texture'],'model/Zortrax_M300_Classic_bed.svg')
  asset=ROOT/'profiles/Zortrax'/model['bed_texture']
  self.assertTrue(asset.is_file())
  drawing=ET.fromstring(asset.read_bytes())
  self.assertEqual(drawing.tag,'{http://www.w3.org/2000/svg}svg')
  circles=[e for e in drawing.iter('{http://www.w3.org/2000/svg}circle') if e.get('r')=='2.18']
  self.assertEqual(len(circles),11556)
  xs=sorted({float(e.get('cx')) for e in circles})
  ys=sorted({float(e.get('cy')) for e in circles})
  self.assertEqual((len(xs),len(ys)),(108,107))
  self.assertTrue(all(abs(xs[i+1]-xs[i]-9.6)<1e-8 for i in range(len(xs)-1)))
  self.assertTrue(all(abs(ys[i+1]-ys[i]-9.6)<1e-8 for i in range(len(ys)-1)))
 def test_profile_names_preserved(self):
  self.assertTrue(any(e['name']=='Z-PLA Pro @Zortrax M300 0.4' for e in self.vendor['filament_list']));self.assertTrue(any(e['name']=='0.20mm Standard @Zortrax M300 Classic 0.4 nozzle' for e in self.vendor['process_list']))
if __name__=='__main__':unittest.main()
