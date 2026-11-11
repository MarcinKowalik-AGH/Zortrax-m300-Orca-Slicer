import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r7_install',ROOT/'tools/install_classic_r7.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class R7InstallTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)/'OrcaSlicer';self.root.mkdir()
  self.cfg={'models':[{'vendor':'Creality','model':'Creality K2 Plus','nozzle_diameter':'0.4'}],
   'filaments':['Generic PLA @Creality K2-all'],'presets':{'printer':'Creality K2 Plus 0.4 nozzle','print':'my strength mod','filaments':['Generic PLA @Creality K2-all']},'preset_folder':'default','other_account':'keep'}
  self.write('OrcaSlicer.conf',self.cfg)
  self.write('system/Creality.json',{'name':'Creality','keep':True})
  self.write('user/default/process/my strength mod.json',{'name':'strength mod','compatible_printers':['Creality K2 Plus 0.4 nozzle']})
  self.write('user/default/machine/K2.json',{'name':'My K2','printer_model':'Creality K2 Plus'})
  self.source=ROOT/'native_r7'
 def write(self,rel,obj):
  p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(m.enc(obj));return p
 def protected(self):
  return {r:(self.root/r).read_bytes() for r in ['OrcaSlicer.conf','system/Creality.json','user/default/process/my strength mod.json','user/default/machine/K2.json']}
 def bundle(self,id,name,foreign=False):
  rel='user/default/_local/'+id
  self.write(rel+'/bundle_metadata.json',{'name':name})
  self.write(rel+'/machine.json',{'type':'machine','name':'Old M300','printer_model':'Zortrax M300 Classic','nozzle_diameter':['0.4']})
  if foreign:self.write(rel+'/other.json',{'type':'machine','name':'Creality K2 Plus','printer_model':'Creality K2 Plus'})
  return rel
 def activate(self):
  j=m.read(self.root/'OrcaSlicer.conf');j['models'].append({'vendor':'Zortrax','model':m.MODEL,'nozzle_diameter':'0.2;0.3;0.4;0.6'});self.write('OrcaSlicer.conf',j)
 def test_plan_is_read_only(self):
  before=m.digest(self.root);m.install_plan(self.root,self.source);self.assertEqual(m.digest(self.root),before)
 def test_config_and_creality_unchanged(self):
  before=self.protected();m.apply(m.install_plan(self.root,self.source));self.assertEqual(self.protected(),before)
 def test_complete_native_structure(self):
  m.apply(m.install_plan(self.root,self.source));v=m.read(self.root/'system/Zortrax.json');self.assertEqual([len(v[k]) for k in m.GROUPS],[1,4,104,30])
 def test_idempotent(self):
  m.apply(m.install_plan(self.root,self.source));self.assertEqual(m.install_plan(self.root,self.source)['before'],{})
 def test_exact_restore(self):
  before=m.digest(self.root);b=m.apply(m.install_plan(self.root,self.source));m.restore(b);self.assertEqual(m.digest(self.root),before)
 def test_no_archive_before_activation(self):
  self.bundle('abc','offline_M300_Classic_0.4_v1')
  with self.assertRaises(ValueError):m.archive_plan(self.root)
 def test_four_offline_only(self):
  old=[self.bundle(str(i),'offline_M300_Classic_'+d+'_v1') for i,d in enumerate(('0.3','0.4','0.6','0.8'))]
  other=self.bundle('unrelated','my-precious-calibration')
  self.activate();before=self.protected();b=m.apply(m.archive_plan(self.root));self.assertEqual(self.protected(),before)
  self.assertTrue((self.root/other).exists());self.assertTrue(all(not (self.root/r).exists() for r in old))
  m.restore(b);self.assertTrue(all((self.root/r).exists() for r in old))
 def test_mixed_bundle_is_retained(self):
  rel=self.bundle('mixed','offline_M300_Classic_0.4_v1',True);self.activate();p=m.archive_plan(self.root);self.assertNotIn(rel,p['remove']);self.assertTrue(p['warnings'])
 def test_preserve_inventure_vendor(self):
  sub='machine/Inventure.json';self.write('system/Zortrax/'+sub,{'name':'Inventure','printer_model':'Zortrax Inventure'})
  self.write('system/Zortrax.json',{'name':'Zortrax','machine_list':[{'name':'Inventure','sub_path':sub}]})
  m.apply(m.install_plan(self.root,self.source));self.assertTrue((self.root/'system/Zortrax'/sub).exists())
  self.assertEqual(len(m.read(self.root/'system/Zortrax.json')['machine_list']),5)
 def test_symlink_refused(self):
  (self.root/'system/Zortrax').symlink_to(Path(self.tmp.name),target_is_directory=True)
  with self.assertRaises(ValueError):m.install_plan(self.root,self.source)
 def test_later_config_edit_rejected_before_apply(self):
  p=m.install_plan(self.root,self.source);self.cfg['later']='yes';self.write('OrcaSlicer.conf',self.cfg)
  with self.assertRaises(ValueError):m.apply(p)
 def test_restore_refuses_modified_native_file(self):
  b=m.apply(m.install_plan(self.root,self.source));(self.root/'system/Zortrax.json').write_text('{}')
  with self.assertRaises(ValueError):m.restore(b)
 def test_failure_rolls_back(self):
  before=m.digest(self.root);original=m.atom
  def fail(path,data):
   if str(path).endswith('system/Zortrax.json'):raise OSError('simulated write failure')
   return original(path,data)
  with patch.object(m,'atom',side_effect=fail):
   with self.assertRaises(OSError):m.apply(m.install_plan(self.root,self.source))
  self.assertEqual(m.digest(self.root),before)
 def test_no_ssh_or_linux(self):
  with patch.object(m.sys,'platform','linux'):
   with self.assertRaises(ValueError):m.guard()
  with patch.object(m.sys,'platform','darwin'),patch.dict(m.os.environ,{'SSH_CONNECTION':'test'}):
   with self.assertRaises(ValueError):m.guard()
if __name__=='__main__':unittest.main()
