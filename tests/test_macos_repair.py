import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('repair', ROOT/'tools/repair_macos_r6.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
SOURCE = ROOT/'native'


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(r.encoded(data))


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'OrcaSlicer'
        self.root.mkdir()
        self.cfg = {'preset_folder':'default', 'language':'pl_PL', 'opaque_secret':'LOCAL_ONLY_TEST',
            'models':[{'vendor':'Creality','model':'Creality K2 Plus','nozzle_diameter':'0.4;0.6'},
                      {'vendor':'Zortrax','model':'Zortrax Inventure','nozzle_diameter':'0.4'}],
            'filaments':['Creality PLA','Z-PLA Pro @Zortrax Inventure','Z-PLA Pro @Zortrax M300'],
            'presets':{'printer':'Zortrax M300 Classic Klipper 0.6 nozzle', 'print':'Old M300', 'filaments':['Old PLA M300']}}
        save(self.root/'OrcaSlicer.conf', self.cfg)
        for d in ('0.3','0.4','0.6','0.8'):
            b=self.root/'user/default/_local'/('offline_M300_Classic_'+d+'_v1')
            save(b/'bundle_metadata.json', {'name':'M300 '+d,'id':b.name})
            save(b/'machine/printer.json', {'type':'machine','name':'Zortrax M300 Classic Klipper '+d+' nozzle','printer_model':'Zortrax M300','nozzle_diameter':[d]})
            save(b/'filament/PLA.json', {'name':'Z-PLA Pro @Zortrax M300','compatible_printers':['Zortrax M300 Classic Klipper '+d+' nozzle']})
        save(self.root/'user/default/machine/old.json',{'name':'My M300 clone','printer_model':'Zortrax M300'})
        (self.root/'user/default/machine/old.info').write_text('calibration metadata')
        save(self.root/'user/default/filament/tuned.json',{'name':'My measured PLA','inherits':'Z-PLA Pro @Zortrax M300'})
        save(self.root/'user/default/machine/creality.json', {'name':'Creality K2 Plus','printer_model':'Creality K2 Plus','notes':'I compared this with M300'})
        save(self.root/'user/default/machine/inventure.json', {'name':'Zortrax Inventure','printer_model':'Zortrax Inventure'})
        save(self.root/'user/default/filament/shared.json', {'name':'M300 and Creality shared','compatible_printers':['Zortrax M300 0.4','Creality K2 Plus']})
        save(self.root/'system/Creality.json', {'name':'Creality','sentinel':42})
        save(self.root/'user/default/_local/creality_bundle/machine/K2.json',{'type':'machine','name':'Creality K2 Plus','printer_model':'Creality K2 Plus'})
        save(self.root/'user/another_account/machine/M300.json',{'name':'Zortrax M300 0.4','printer_model':'Zortrax M300'})

    def test_plan_does_not_write(self):
        old=snapshot(self.root);p=r.plan(self.root,SOURCE)
        self.assertEqual(snapshot(self.root),old);self.assertEqual(p['nozzle'],'0.6')
        self.assertEqual(len([x for x in p['deletes'] if '/_local/' in x]),4)

    def test_cleanup_and_full_native_install(self):
        backup=r.apply(r.plan(self.root,SOURCE))
        self.assertIsNotNone(backup)
        self.assertFalse(any((self.root/'user/default/_local').glob('offline_M300*')))
        self.assertFalse((self.root/'user/default/machine/old.json').exists())
        self.assertTrue((backup/'before/user/default/machine/old.info').exists())
        self.assertTrue((backup/'before/user/default/filament/tuned.json').exists())
        v=r.load(self.root/'system/Zortrax.json')
        self.assertEqual([len(v[k]) for k in r.GROUPS],[1,4,76,80])
        self.assertFalse(any(x['name'].startswith('Z-SUPPORT') for x in v['filament_list']))
        self.assertEqual(len(list((self.root/'system/Zortrax/filament').glob('*.json'))),76)

    def test_other_printers_shared_profiles_accounts_unchanged(self):
        old=snapshot(self.root);r.apply(r.plan(self.root,SOURCE))
        for rel in ['system/Creality.json','user/default/machine/creality.json', 'user/default/machine/inventure.json',
                    'user/default/filament/shared.json', 'user/default/_local/creality_bundle/machine/K2.json',
                    'user/another_account/machine/M300.json']:
            self.assertEqual((self.root/rel).read_bytes(),old[rel])

    def test_activation_and_selected_nozzle(self):
        r.apply(r.plan(self.root,SOURCE));c=r.load(self.root/'OrcaSlicer.conf')
        self.assertEqual(c['presets']['printer'],'Zortrax M300 0.6')
        self.assertEqual(c['presets']['print'],'0.20mm Standard @Zortrax M300 0.6')
        self.assertEqual(c['presets']['filaments'],['Z-PLA Pro @Zortrax M300 0.6'])
        self.assertEqual(c['models'][:2],self.cfg['models'])
        self.assertEqual(c['models'][-1]['nozzle_diameter'],'0.2;0.3;0.4;0.6')
        self.assertEqual(len([x for x in c['filaments'] if '@Zortrax M300 ' in x]),76)
        self.assertEqual(c['opaque_secret'],'LOCAL_ONLY_TEST')
        self.assertIn('Creality PLA',c['filaments'])
        self.assertIn('Z-PLA Pro @Zortrax Inventure',c['filaments'])

    def test_idempotent(self):
        r.apply(r.plan(self.root,SOURCE));p=r.plan(self.root,SOURCE)
        self.assertEqual(p['writes'],{});self.assertEqual(p['deletes'],[])
        self.assertIsNone(r.apply(p))

    def test_exact_restore(self):
        old=snapshot(self.root);backup=r.apply(r.plan(self.root,SOURCE));r.restore(backup)
        self.assertEqual(snapshot(self.root),old)

    def test_restore_refuses_later_edits(self):
        backup=r.apply(r.plan(self.root,SOURCE));(self.root/'OrcaSlicer.conf').write_text('{}')
        with self.assertRaisesRegex(ValueError,'Later edits'):r.restore(backup)
        self.assertEqual((self.root/'OrcaSlicer.conf').read_text(),'{}')

    def test_plan_refuses_symlinks(self):
        q=self.root/'user/default/_local/offline_M300_Classic_0.6_v1/extra'
        q.symlink_to(self.root/'system',target_is_directory=True)
        old=snapshot(self.root)
        with self.assertRaisesRegex(ValueError,'symlink'):r.plan(self.root,SOURCE)
        self.assertEqual(snapshot(self.root),old)

    def test_preserves_inventure_in_same_vendor_and_expires_own_cache(self):
        inv={'name':'Zortrax Inventure','type':'machine_model'}
        save(self.root/'system/Zortrax/machine/Inventure.json',inv)
        old={'name':'Zortrax', 'version':'old', 'machine_model_list':[{'name':'Zortrax Inventure','sub_path':'machine/Inventure.json'}],
             'machine_list':[], 'filament_list':[], 'process_list':[]}
        save(self.root/'system/Zortrax.json',old)
        (self.root/'system/Zortrax.opc').write_bytes(b'old cache')
        r.apply(r.plan(self.root,SOURCE));v=r.load(self.root/'system/Zortrax.json')
        self.assertIn(old['machine_model_list'][0],v['machine_model_list'])
        self.assertEqual(r.load(self.root/'system/Zortrax/machine/Inventure.json'),inv)
        self.assertFalse((self.root/'system/Zortrax.opc').exists())

    def test_mixed_local_bundle_not_removed(self):
        p=self.root/'user/default/_local/offline_M300_Classic_0.6_v1/machine/K2.json'
        save(p,{'type':'machine','printer_model':'Creality K2 Plus','name':'Creality K2 Plus'})
        p=r.plan(self.root,SOURCE);self.assertTrue(p['warnings'])
        self.assertNotIn('user/default/_local/offline_M300_Classic_0.6_v1',p['deletes'])

    def test_bad_config_is_not_changed(self):
        (self.root/'OrcaSlicer.conf').write_text('not JSON');old=snapshot(self.root)
        with self.assertRaises(ValueError):r.plan(self.root,SOURCE)
        self.assertEqual(snapshot(self.root),old)

    def test_select_02_layer(self):
        p=r.plan(self.root,SOURCE,'0.2');r.apply(p)
        self.assertEqual(r.load(self.root/'OrcaSlicer.conf')['presets']['print'],'0.10mm Standard @Zortrax M300 0.2')

    def test_subscribed_bundle_not_deleted(self):
        q=self.root/'user/default/_subscribed/test/machine/M300.json'
        save(q,{'type':'machine','name':'Zortrax M300 0.4','printer_model':'Zortrax M300'})
        p=r.plan(self.root,SOURCE);r.apply(p);self.assertTrue(q.exists());self.assertTrue(p['warnings'])

    def test_transaction_rolls_back_on_write_error(self):
        old=snapshot(self.root);real_atomic=r.atomic
        def fail_once(path,data):
            if path.name=='OrcaSlicer.conf':raise OSError('simulated write failure')
            return real_atomic(path,data)
        with patch.object(r,'atomic',side_effect=fail_once):
            with self.assertRaises(OSError):r.apply(r.plan(self.root,SOURCE))
        self.assertEqual(snapshot(self.root),old)

    def test_plan_lease(self):
        p=r.plan(self.root,SOURCE);(self.root/'OrcaSlicer.conf').write_text('{}')
        with self.assertRaisesRegex(ValueError,'Files changed'):r.apply(p)

    def test_os_and_ssh_guard(self):
        with patch.object(r.sys,'platform','linux'):
            with self.assertRaisesRegex(ValueError,'Orange Pi'):r.require_mac_and_closed()
        with patch.object(r.sys,'platform','darwin'),patch.dict(os.environ,{'SSH_CONNECTION':'test'}):
            with self.assertRaisesRegex(ValueError,'SSH'):r.require_mac_and_closed()

    def test_running_app_guard(self):
        with patch.object(r.sys,'platform','darwin'),patch.dict(os.environ,{'SSH_CONNECTION':'','SSH_TTY':''}), \
             patch.object(r.os,'geteuid',return_value=501),patch.object(r.subprocess,'run',return_value=type('Result',(),{'stdout':'/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer\n'})()):
            with self.assertRaisesRegex(ValueError,'Cmd'):r.require_mac_and_closed()

    def test_plus_dual_excluded(self):
        self.assertFalse(r.classic('Zortrax M300 Plus 0.4'))
        self.assertFalse(r.classic('Zortrax M300Dual'))
        self.assertTrue(r.classic('offline_M300_Classic_0.6_v1'))
        self.assertTrue(r.classic('Zortrax M300 0.4'))


if __name__=='__main__':unittest.main()
