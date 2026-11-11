#!/usr/bin/env python3
"""One-time, pinned migration. Never deletes or writes the source repository.
Run only on a clean destination checkout. Firmware/host payloads are excluded.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

SOURCE_REPO = 'MarcinKowalik-AGH/Zortrax-m300-Klipper'
SOURCE_COMMIT = '1f58160e2d0e81c462648e57fa0ee69123313a4f'
BUNDLE_SHA = '3b60cd1ec9d324d5c2ed5a2aec7ced13560d13eff56734167bede1655e4333a4'
BUNDLE_NAME = 'Zortrax_M300_Classic_0p20_MicroSwiss_R3.orca_printer'
DEST_REPO = 'MarcinKowalik-AGH/Zortrax-m300-Orca-Slicer'

README = '''# Zortrax-m300-Orca-Slicer

Profile **OrcaSlicer dla Zortrax M300 Classic z Klipperem**. Osobne repozytorium slicera; bez firmware MCU, hosta, Fluidd i instalatorów drukarki.

## Pobranie i import

**[Profil R3 — dysza 0,4 mm, warstwa 0,20 mm](profiles/Zortrax_M300_Classic_0p20_MicroSwiss_R3.orca_printer?raw=true)**

OrcaSlicer: **File → Import → Import Configs**. Wybierz plik `.orca_printer`, następnie drukarkę `Zortrax M300 0.4 nozzle`, proces `0.20mm Standard @Zortrax M300 0.4 nozzle` i materiał z dopiskiem `@Zortrax M300`. Przy ponownym imporcie zastąp wcześniejsze presety o tych samych nazwach. Nie importuj archiwum audytowego jako konfiguracji.

Pakiet zawiera **1 drukarkę, 1 proces oraz 18 wpisów filamentów**. 17 profili przeszło programowy test generowania G-code w silniku OrcaSlicer 2.3.2. **Z-PEEK jest wpisem katalogowym, niedopuszczonym do druku**; sama flaga slicera nie blokuje niezawodnie generowania G-code. Wynik slicingu nie potwierdza przydatności każdego materiału na rzeczywistym M300. Nie wykonano testu GUI na komputerze użytkownika ani fizycznego wydruku.

## Podział projektów

| Tutaj: OrcaSlicer | [Zortrax-m300-Klipper](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper) |
|---|---|
| Presety drukarki, procesu i materiałów | Host, MCU, OLED i Fluidd |
| Wywołania START_PRINT / END_PRINT / PAUSE | Implementacje makr i procedur |
| Temperatury materiałowe, M83, nastawy PA | Egzekwowanie limitów grzania, homing, mesh |
| Testy importowanych ustawień i wygenerowanego G-code | Testy sterowania drukarką i instalatory |

**Import presetu nie aktualizuje Klippera.** Stół ma w profilach nastawy do 105°C. Egzekwowanie limitu 105°C po stronie drukarki wymaga odpowiedniego hosta R3; w repozytorium hosta pozostaje osobnym zadaniem. Nie zwiększono limitu hotendu. Micro Swiss oznacza przygotowanie do zestawu M2580-04, nie potwierdzoną kalibrację zamontowanego hotendu.

`M83` pozostaje włączone. Pressure Advance jest jawnie zerowane przed START_PRINT, a następnie ustawiane z filamentu. Dostarczone `PA=0` jest neutralnym ustawieniem **do czasu pomiaru**, nie wynikiem kalibracji. Adaptive PA jest wyłączone. Zachowano prędkości, przyspieszenia, flow ratio i retrakcje R3 bez zmian.

## Dokumentacja i źródła

- [Instrukcja oraz rozdział odpowiedzialności host/profil](docs/INSTALL_PL.md)
- [Micro Swiss, limit stołu i strojenie PA](docs/MICROSWISS_R3_PL.md)
- [Oryginalny wynik walidacji R3](evidence/VALIDATION_RESULTS_R3_SOURCE.json)
- [Oryginalne wyniki G-code R3](evidence/ORCA_RUNTIME_RESULTS_R3.json)
- [Manifest migracji i pochodzenie każdego pliku](MIGRATION.json)

`profiles/` zawiera plik do importu, `presets/` jego edytowalne pliki JSON, `tests/` niezależne testy slicera, `evidence/` raporty, a `archive/` oryginalny pakiet źródeł i starsze raporty. Aktywne profile nie są budowane z repozytorium Klippera.

## Weryfikacja i rozwój

```bash
python3 tools/validate_profiles.py
python3 tools/build_bundle.py --output /tmp/m300-test.orca_printer
# Z zainstalowanym OrcaSlicer 2.3.2:
python3 tests/audit_r3.py --orca /sciezka/do/AppRun --bundle profiles/Zortrax_M300_Classic_0p20_MicroSwiss_R3.orca_printer --out /tmp/m300-orca-audit
```

GitHub Actions wykonuje kontrolę struktury oraz slicing dwuwieżowego modelu na przypiętym binarium OrcaSlicer 2.3.2. Sprawdza start/koniec, temperatury, M83, retrakcję, Z-hop i przekazywanie PA. Nie wykonuje kompilacji ani instalacji Klippera. Metadane `type` i `from=system` są adapterem CLI wyłącznie w kopiach testowych; pakiet importowy pozostaje pakietem użytkownika.

Migracja z commita `1f58160e2d0e81c462648e57fa0ee69123313a4f` repozytorium M300 zachowuje profil R3 **bajt w bajt**, bez zmiany parametrów. Historia oryginalnych commitów pozostaje w repozytorium źródłowym; jej identyfikatory i sumy plików zapisano w manifeście. Licencję kodu zachowano z projektu źródłowego.
'''

VALIDATE = r'''#!/usr/bin/env python3
"""Offline structural and source/bundle consistency checks, no printer access."""
import hashlib,json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NAME='Zortrax_M300_Classic_0p20_MicroSwiss_R3.orca_printer'

def main():
    bundle=ROOT/'profiles'/NAME
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        names=z.namelist();assert len(names)==len(set(names))==21
        m=json.loads(z.read('bundle_structure.json'))
        assert len(m['printer_config'])==len(m['process_config'])==1
        assert len(m['filament_config'])==18
        assert set(names)==set(['bundle_structure.json']+m['printer_config']+m['process_config']+m['filament_config'])
        for name in names:
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            assert (ROOT/'presets'/name).read_bytes()==z.read(name),name
        p=json.loads(z.read(m['printer_config'][0]));q=json.loads(z.read(m['process_config'][0]))
        assert len(p)==144 and len(q)==334
        assert p['gcode_flavor']=='klipper' and p['use_relative_e_distances']=='1'
        assert p['machine_end_gcode'].strip()=='END_PRINT'
        assert p['machine_pause_gcode'].strip()=='PAUSE'
        assert 'START_PRINT EXTRUDER_TEMP=' in p['machine_start_gcode']
        assert 'SET_PRESSURE_ADVANCE ADVANCE=0' in p['machine_start_gcode']
        assert q['layer_height']=='0.2' and q['post_process']==[]
        assert q['compatible_printers']==[p['name']]
        unsupported=[]
        for name in m['filament_config']:
            f=json.loads(z.read(name));assert len(f)==123
            assert f['compatible_printers']==[p['name']]
            assert f['filament_settings_id']==[f['name']]
            assert f['enable_pressure_advance']==['1'] and f['pressure_advance']==['0']
            assert f['adaptive_pressure_advance']==['0']
            for k,v in f.items():
                if '_plate_temp' in k:assert 0<=float(v[0])<=105,(name,k)
            if f['name'].startswith('Z-PEEK '):unsupported.append(f['name'])
            else:
                assert float(f['nozzle_temperature'][0])<=265
                assert float(f['nozzle_temperature_initial_layer'][0])<=265
        assert len(unsupported)==1
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        digest,path=line.split('  ',1)
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    assert not any((ROOT/n).exists() for n in ['host','mcu','frontend'])
    print(json.dumps({'status':'PASS','printer':1,'process':1,'materials':18,'schema_fields':[144,334,123],'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'hardware_test':False}))

if __name__=='__main__':main()
'''

BUILD = r'''#!/usr/bin/env python3
"""Build an Orca bundle only from local JSON presets; no host modifications."""
import argparse,hashlib,json,zipfile
from pathlib import Path

def main():
    root=Path(__file__).resolve().parents[1]
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    manifest=json.loads((root/'presets/bundle_structure.json').read_text())
    names=manifest['printer_config']+manifest['process_config']+manifest['filament_config']+['bundle_structure.json']
    assert len(names)==len(set(names))==21
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in names:
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            raw=(root/'presets'/name).read_bytes();json.loads(raw)
            info=zipfile.ZipInfo(name,(2026,11,11,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,raw)
    with zipfile.ZipFile(a.output) as z:assert z.testzip() is None
    print(hashlib.sha256(a.output.read_bytes()).hexdigest()+'  '+str(a.output))

if __name__=='__main__':main()
'''

INSTALL = '''# Instalacja profilu — M300 Classic

Importuj plik z katalogu `profiles`, nie cały ZIP źródeł repozytorium. W OrcaSlicer wybierz **File → Import → Import Configs**. Zastąp poprzednie presety o tych samych nazwach, wybierz `Zortrax M300 0.4 nozzle`, jeden proces `0.20mm Standard` i odpowiedni filament `@Zortrax M300`.

Nie zmieniono parametrów druku podczas migracji. Dysza: 0,4 mm; filament: 1,75 mm; warstwa: 0,20 mm; E względne. Do druku wymagane są istniejące makra START_PRINT, END_PRINT oraz PAUSE w hoście M300. Pliki profili nie zawierają firmware ani instalatora hosta.

## Sterowanie drukarką jest w innym repozytorium

[Zortrax-m300-Klipper](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper) zawiera procedury, konfigurację hosta i niezależne zabezpieczenia termiczne. Zmiany hosta R3 są opisane w [PR #14](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper/pull/14). Sam import nie instaluje limitu stołu 105°C na drukarce. Przed użyciem sprawdź stan własnej instalacji i wersję hosta; nie uruchamiaj aktualizacji podczas druku.

PA=0 pozostaje neutralne do kalibracji danego filamentu. Nie wprowadzono offsetu temperatury dla Micro Swiss. Z-PEEK jest katalogiem, nie zatwierdzonym materiałem. Z-SUPPORT nie umożliwia równoczesnego druku drugiego materiału podporowego na jednogłowicowej M300.

Sprawdzono generowanie G-code, nie fizyczną jakość/bezpieczeństwo zmontowanej maszyny. Nadzorowane testy temperatur, purge, homingu, meshu, ekstruzji i przyczepności pozostają po stronie urządzenia. `MESH=AUTO` ładuje zapisaną siatkę; nie wykonuje nowego pomiaru.
'''


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def write(root,path,text):
    target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--target',type=Path,default=Path.cwd());a=ap.parse_args()
    source=a.source.resolve();root=a.target.resolve()
    if (root/'MIGRATION.json').exists():raise SystemExit('Migration already completed; refusing overwrite')
    actual=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    assert actual==SOURCE_COMMIT,(actual,SOURCE_COMMIT)
    original=source/'orca/Zortrax_M300_Classic_0p20_18_filaments.orca_printer'
    assert sha(original)==BUNDLE_SHA
    for folder in ('profiles','presets','docs','tests','evidence','archive','tools'):(root/folder).mkdir(exist_ok=True)
    dest=root/'profiles'/BUNDLE_NAME;shutil.copyfile(original,dest)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        for name in z.namelist():
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
        z.extractall(root/'presets')
    original_files=sorted(p for p in (source/'orca').rglob('*') if p.is_file())
    assert len(original_files)==11,len(original_files)
    snapshot=root/'archive/orca_source_R3_1f58160.zip'
    with zipfile.ZipFile(snapshot,'w',zipfile.ZIP_DEFLATED) as z:
        for path in original_files:z.write(path,path.relative_to(source).as_posix())
    with zipfile.ZipFile(snapshot) as z:
        assert z.testzip() is None
        for path in original_files:assert z.read(path.relative_to(source).as_posix())==path.read_bytes()
    mapping={
        'ORCA_RUNTIME_AUDIT_R2.md':'docs/archive/ORCA_RUNTIME_AUDIT_R2.md',
        'VALIDATION_M300_0p20.md':'docs/archive/VALIDATION_M300_0p20.md',
        'README.md':'docs/archive/README_BEFORE_SPLIT.md',
        'ORCA_RUNTIME_RESULTS_R2.json':'evidence/ORCA_RUNTIME_RESULTS_R2.json',
        'ORCA_RUNTIME_RESULTS_R3.json':'evidence/ORCA_RUNTIME_RESULTS_R3.json',
        'VALIDATION_RESULTS.json':'evidence/VALIDATION_RESULTS_R3_SOURCE.json',
    }
    for old,new in mapping.items():
        path=root/new;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/'orca'/old,path)
    ms=(source/'orca/MICROSWISS_R3_PL.md').read_text()
    ms='> Po rozdzieleniu repozytoriów ten plik opisuje integrację. Host, limity i instalatory są w [Zortrax-m300-Klipper](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper), a tutaj wyłącznie profile i testy slicera. Oryginał dokumentu zachowano w archive/orca_source_R3_1f58160.zip.\n\n'+ms
    write(root,'docs/MICROSWISS_R3_PL.md',ms)
    utils=(source/'orca/tests/audit_slice.py').read_text().split('\ndef main():',1)[0]
    assert 'def inspect_gcode(' in utils and 'from repair_r2 import repair\n' in utils
    utils=utils.replace('from repair_r2 import repair\n','')
    utils=utils.replace('R2 repairs are explicit.','Extracted reusable checks; this module does not repair or rewrite profiles.')
    write(root,'tests/gcode_checks.py',utils)
    audit=(source/'orca/tests/audit_r3.py').read_text()
    assert 'from audit_slice import inspect_gcode, test_stl' in audit
    audit=audit.replace('from audit_slice import inspect_gcode, test_stl','from gcode_checks import inspect_gcode, test_stl')
    assert 'host_unit_tests=756,' in audit
    audit=audit.replace('host_unit_tests=756,','historical_host_unit_tests=756,host_tests_executed_here=False,')
    write(root,'tests/audit_r3.py',audit)
    write(root,'README.md',README);write(root,'docs/INSTALL_PL.md',INSTALL)
    write(root,'tools/validate_profiles.py',VALIDATE);write(root,'tools/build_bundle.py',BUILD)
    shutil.copyfile(source/'LICENSE',root/'LICENSE')
    write(root,'.gitignore','.migration-source/\n__pycache__/\n*.pyc\n.audit/\ndist/\n')
    sums=[dest,snapshot]
    write(root,'SHA256SUMS',''.join(sha(p)+'  '+p.relative_to(root).as_posix()+'\n' for p in sums))
    record=dict(source_repository=SOURCE_REPO,source_commit=SOURCE_COMMIT,
        destination_repository=DEST_REPO,migration_date='2026-11-11',
        profile_path=dest.relative_to(root).as_posix(),profile_sha256=BUNDLE_SHA,
        profile_byte_identical=True,source_history_rewritten=False,
        source_history_url='https://github.com/'+SOURCE_REPO+'/commits/'+SOURCE_COMMIT+'/orca',
        source_snapshot=snapshot.relative_to(root).as_posix(),
        source_files=[dict(path=p.relative_to(source).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in original_files],
        test_adaptations=['Extract common G-code helpers without R2 repair entrypoint','Replace hardcoded executed host-test count with explicitly historical metadata'],
        excluded_from_destination=['host','mcu','frontend','host installers','tools/apply_m300_r3.py'],
        source_cleanup='Separate checked operation after destination commit readback')
    write(root,'MIGRATION.json',json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    subprocess.run(['python3',str(root/'tools/validate_profiles.py')],check=True)
    print(json.dumps(record,ensure_ascii=False))

if __name__=='__main__':main()
