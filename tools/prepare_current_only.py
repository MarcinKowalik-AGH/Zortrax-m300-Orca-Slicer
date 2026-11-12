#!/usr/bin/env python3
"""One-shot cleanup of the isolated, authorized GitHub Actions checkout only.
The script removes itself. It never runs against a user Mac or printer.
"""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='18d68bb161631004e6909a0f7585fe552b15b302'
REPO='MarcinKowalik-AGH/Zortrax-m300-Orca-Slicer'
BRANCH='maintenance/current-only-english'

def main():
 if os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!=REPO or os.environ.get('GITHUB_REF')!='refs/heads/'+BRANCH:
  raise SystemExit('CI-only preparation; refusing this environment')
 if Path(os.environ.get('GITHUB_WORKSPACE','')).resolve()!=ROOT or not (ROOT/'.git').is_dir():raise SystemExit('Not the expected isolated Git checkout')
 if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise SystemExit('Checkout is not clean')
 out={}
 def read(p):return (ROOT/p).read_bytes()
 def text(p):return read(p).decode()
 def put(p,value):out[p]=value if isinstance(value,bytes) else value.encode()
 def obj(p,value):put(p,json.dumps(value,ensure_ascii=False,indent=2)+'\n')
 def replace(s,a,b):
  if a not in s:raise ValueError('Expected baseline text missing: '+a[:100])
  return s.replace(a,b)
 # Capture all inputs before retiring the old tree.
 profiles={p.relative_to(ROOT/'native_r7').as_posix():p.read_bytes() for p in sorted((ROOT/'native_r7').rglob('*.json'))}
 assert len(profiles)==140
 vendor=json.loads(profiles['Zortrax.json']);assert vendor['version']=='02.05.00.08'
 assert [len(vendor[k]) for k in ('machine_model_list','machine_list','process_list','filament_list')]==[1,4,30,104]
 for name,data in profiles.items():put('profiles/'+name,data)
 put('LICENSE',read('LICENSE'))
 put('.gitignore','__pycache__/\n*.pyc\n.DS_Store\n/dist/\n/out/\n')
 obj('CURRENT.json',{'profile_revision':'R7.1','repository_layout':'current-only','layout_date':'2026-11-12','orca_target_version':'2.5.0','vendor_version':vendor['version'],'profile_directory':'profiles','installer':'install.py','source_baseline_commit':BASE,'profile_data_changed_by_cleanup':False,'machine_models':1,'nozzle_variants':4,'processes':30,'filaments':104,'zortrax_materials_per_nozzle':19,'generic_materials_per_nozzle':7,'previous_versions':'Git history only. No history rewrite; no host-repository changes.'})
 obj('evidence/PROFILE_BASELINE.json',{'baseline_commit':BASE,'scope':'All 140 current profile bytes and identities are unchanged; paths move from native_r7/ to profiles/.','sha256':{n:hashlib.sha256(b).hexdigest() for n,b in profiles.items()}})
 for old,new in [('ZSUITE_classic.json','zsuite_classic.json'),('ZSUITE_beta4.json','zsuite_beta4.json')]:put('sources/'+new,read('sources/'+old))
 oldprov=json.loads(text('evidence/R6_PROVENANCE.json'));prov={}
 for entry in vendor['filament_list']:
  name=entry['name']
  if name not in oldprov:continue
  prov[name]={k:oldprov[name][k] for k in ('source','mapped_fields','warnings')}
  if name=='Z-PLA @Zortrax M300 0.4':prov[name]['current_override']={'fields':'all *_plate_temp and *_plate_temp_initial_layer','source_bed_c':30,'current_bed_c':50,'reason':'User-reported print start on 2026-11-11; not an OEM value or completed-print qualification.'}
 assert len(prov)==76;obj('sources/filament_provenance.json',prov)
 manifest=json.loads(text('sources/SOURCE_MANIFEST_R5.json'))
 manifest['scope']='Extracted numerical evidence, not old installable releases; retained so current documentation remains auditable.'
 manifest['extraction_code_history']='https://github.com/'+REPO+'/tree/'+BASE+'/tools'
 manifest['files']={n:hashlib.sha256(out['sources/'+n]).hexdigest() for n in ('zsuite_classic.json','zsuite_beta4.json','filament_provenance.json')}
 obj('sources/MANIFEST.json',manifest)
 # Preserve the proven installer transaction and receipt format, translate messages.
 s=text('tools/install_classic_r7.py')
 s=replace(s,'ROOT=Path(__file__).resolve().parents[1]','ROOT=Path(__file__).resolve().parent')
 s=replace(s,"ROOT/'native_r7'","ROOT/'profiles'")
 translations={
 'Mac-only R7 installation':'Mac-only current-profile installation',
 'Not the complete R7 vendor':'Not the complete current M300 vendor',
 'Najpierw wlacz M300 Classic w Orca przez Select/Remove printers, sprawdz liste i zamknij program. Stare pakiety pozostaja.':'First enable M300 Classic using Select/Remove printers in Orca, verify it, then quit. Old bundles have not been changed.',
 'Zachowano nierozpoznany/mieszany pakiet: ':'Preserved unknown or mixed bundle: ',
 'Zachowano wspoldzielone presety: ':'Preserved shared presets: ',
 'Tylko lokalny Mac. Nie Orange Pi ani SSH.':'Local macOS Terminal only. Not Orange Pi or SSH.',
 'Bez sudo.':'Do not use sudo or run as root.',
 'Zamknij Orca przez Cmd+Q.':'Quit OrcaSlicer using Cmd+Q first.',
 'PRZYWROCONO pliki R7; OrcaSlicer.conf nie zmieniono.':'RESTORED profile files; OrcaSlicer.conf was not modified.',
 'Nie rozpoznano katalogu konfiguracji Orca.':'The OrcaSlicer configuration directory was not recognized.',
 'TYLKO MAC / ORCA. Nie zmieniam OrcaSlicer.conf, Creality, Inventure ani Klippera.':'MAC / ORCA ONLY. OrcaSlicer.conf, Creality, Inventure and Klipper are not modified.',
 'Tryb:':'Mode:', 'Pliki do zapisania:':'Files to write:', 'Elementy do archiwum:':'Items to archive:',
 'Archiwum:':'Archive:', 'UWAGA:':'WARNING:',
 'PLAN; bez zmian. Dodaj --apply, aby zastosowac.':'PLAN ONLY; no changes. Add --apply to install.',
 'GOTOWE. Kopia:':'DONE. Backup:', 'brak zmian':'no changes',
 'Uruchom Orca > Select/Remove printers > Zortrax > Zortrax M300 Classic. Zaznacz dysze. Dopiero po sprawdzeniu mozna uzyc --archive-offline.':'Open Orca > Select/Remove printers > Zortrax > Zortrax M300 Classic and enable nozzle variants. Only after checking the model, use --archive-offline if needed.'}
 for a,b in translations.items():s=replace(s,a,b)
 put('install.py',s)
 s=text('tests/test_classic_r7_install.py').replace("ROOT/'tools/install_classic_r7.py'","ROOT/'install.py'").replace("ROOT/'native_r7'","ROOT/'profiles'")
 put('tests/test_install.py',s)
 s=text('tests/gcode_checks.py');helpers=s[s.index('def test_stl('):s.index('def inspect_gcode(')]
 s=text('tests/audit_native_r6.py');inspect=s[s.index('def inspect('):s.index('\ndef main():')]
 put('tests/gcode_checks.py','"""Offline Orca 2.5 checks; never send generated test files to a printer."""\nimport math,re\nNUMBER=r\'[+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)\'\nWORDS=re.compile(r\'([A-Z])(\'+NUMBER+r\')\')\n\n'+helpers+'\n'+inspect)
 s=text('tests/audit_classic_r7.py').replace('from audit_native_r6 import inspect','from gcode_checks import inspect').replace("ROOT/'native_r7'","ROOT/'profiles'").replace("'revision':'R7'","'revision':'R7.1'").replace('R7_SUMMARY','CURRENT_SUMMARY')
 put('tests/audit_slicer.py',s)
 for old,new in [('tests/check_native_loader_r7.py','tests/check_native_loader.py'),('tools/catalog_current.py','tools/catalog.py'),('tools/validate_current.py','tools/validate.py'),('tools/record_current_validation.py','tools/record_validation.py'),('tests/test_current_contract.py','tests/test_profiles.py'),('tools/current_workflow.yml','.github/workflows/validate.yml')]:put(new,read(old))
 # Reuse detailed English content, replacing historical paths with current ones.
 def current_links(s):
  for a,b in [('PROFILE_GUIDE_R7.md','PROFILES.md'),('INSTALL_R7.md','INSTALLATION.md'),('ZSUITE_TO_ORCA_R7.md','ZSUITE_TO_ORCA.md'),('../evidence/R7_PROCESS_CATALOG.json','tables/processes.csv'),('native_r7/','profiles/'),('tools/install_classic_r7.py','install.py')]:s=s.replace(a,b)
  return s
 s=current_links(text('docs/PROFILE_GUIDE_R7.md'))
 s=s.replace('- Prior R3–R6 preset bundles are historical baselines; they remain available under `profiles/`, `archive/`, `evidence/` and `docs/*_PL.md`, **not** as recommended current installers.','- Previous releases are retained only in Git history. This tree contains one current profile set and installer.')
 s+='\n## Current validation and cleanup\n\nAll 140 profile files are preserved byte-for-byte. The older test figures above describe historical R7; current checks are recorded separately in [validation evidence](VALIDATION.md). Repository cleanup does not perform a new physical test or change the operator\'s host.\n'
 put('docs/PROFILES.md',s)
 put('docs/INSTALLATION.md',current_links(text('docs/INSTALL_R7.md'))+'\n## Current tree and rollback\n\nUse the single root `install.py`; versioned installers and old ZIPs have been retired from this tree. The receipt format is preserved. With Orca closed, run `python3 install.py --restore /full/path/to/backup` to restore a recorded backup; the installer refuses to overwrite later edits. See [current validation](VALIDATION.md).\n')
 s=text('docs/ZSUITE_TO_ORCA_R7.md');a=s.index('## 5. Parameter dictionary: Z-SUITE → OrcaSlicer');b=s.index('## 6. Worked conversion',a)
 put('docs/SETTINGS_REFERENCE.md','# Settings dictionary: Z-SUITE → OrcaSlicer\n\nThese are functional correspondences, not proof of identical OEM toolpaths. Copy the source project\'s actual values and inspect the result; a process name is not the full former Z-SUITE selection.\n\n'+s[a:b].replace('## 5. Parameter dictionary: Z-SUITE → OrcaSlicer','## Parameter dictionary')+'\n## Host versus slicer\n\n`position_min`, `safe_z`, `approach_distance`, PC7 release, mesh measurement, thermal protection and homing are **host configuration**, not slicer settings. Relative extrusion, temperature requests and the `START_PRINT` call are slicer integration points. Source `...Feed` fields cannot be copied as flow ratio or MVS without a validated conversion.\n\n[Full crosswalk](ZSUITE_TO_ORCA.md) · [Profile guide](PROFILES.md).\n')
 put('README.md',README)
 put('CHANGELOG.md',CHANGELOG)
 put('docs/VALIDATION.md',VALIDATION)
 put('sources/README.md',SOURCE_README)
 obj('evidence/VALIDATION.json',{'status':'PENDING_CURRENT_CI','profile_revision':'R7.1','note':'This placeholder is replaced only after current static, unit, slicing and native-loader checks pass. Historical results are not reused.'})
 put('tools/checksums.py',CHECKSUMS)
 put('tools/package.py',PACKAGE)
 # No data outside this disposable repository checkout can be removed.
 for p in ROOT.iterdir():
  if p.name=='.git':continue
  if p.is_symlink():raise SystemExit('Refusing repository root symlink: '+str(p))
  if p.is_dir():shutil.rmtree(p)
  else:p.unlink()
 for name,data in out.items():
  p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 subprocess.run([sys.executable,'tools/catalog.py'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'tools/checksums.py','--write'],cwd=ROOT,check=True)
 print(json.dumps({'status':'CURRENT_TREE_PREPARED','profile_json_files':len(profiles),'numerical_profile_changes':0,'old_versions':'Git history only','host_changed':False}))

README='''# Zortrax M300 Classic — OrcaSlicer

**Current profiles: R7.1 · Target slicer: OrcaSlicer 2.5.0 · Current release only.**

Native system profiles for the **Zortrax M300 Classic with the project's Klipper port**. This community integration uses recovered Z-SUITE data and explicit engineering adaptations; it is not an official Zortrax Orca release, or an OEM-firmware/M300 Plus/M300 Dual/Inventure preset.

**This repository installs slicer profiles on the Mac only. It never updates the Orange Pi, Klipper, MCU, bootloader, UART, OLED or Fluidd.**

## One current profile set

| Component | Contents |
|---|---|
| Printer | One Zortrax M300 Classic model |
| Nozzle variants | 0.2 / 0.3 / 0.4 / 0.6 mm |
| Processes | 30 quality presets, matched to nozzle geometry |
| Filaments | 104: 19 Zortrax + 7 Generic names for each nozzle |
| Active files | [profiles/](profiles/) — the only installable preset set |
| Installer | [install.py](install.py) — the only supported installer |
| Correspondence | [Detailed Z-SUITE → Orca mapping](docs/ZSUITE_TO_ORCA.md) and [CSV tables](docs/tables/README.md) |

Classic M300 source records contain **only the 0.4 mm nozzle**. Other variants are project adaptations for mechanically fitted nozzles; M300 Plus/Dual support does not establish Classic support. No Creality motion settings were copied.

## Documentation

| Guide | Purpose |
|---|---|
| [Installation and connection](docs/INSTALLATION.md) | Local Mac setup, other-printer preservation, selection, Moonraker, backups and rollback |
| [Printer/process/filament guide](docs/PROFILES.md) | Nozzle geometry, quality families, material provenance, start/end and PA |
| [Z-SUITE profile tables](docs/ZSUITE_TO_ORCA.md) | Source labels, all 152 M300 combinations, closest processes, temperatures and speed differences |
| [Settings dictionary](docs/SETTINGS_REFERENCE.md) | What transfers, what needs manual review, and unresolved mappings |
| [Validation](docs/VALIDATION.md) | Current software evidence versus limited operator-reported hardware results |

## Update on the Mac

Save your projects and **quit OrcaSlicer using Cmd+Q**. Run in the **Mac's local Terminal**, not SSH to the Orange Pi:

```bash
git -C "$HOME/Zortrax-m300-Orca-Slicer" pull --ff-only origin main &&
python3 "$HOME/Zortrax-m300-Orca-Slicer/install.py" --apply
```

For a first checkout, use the installation guide. No sudo is needed. The installer preserves `OrcaSlicer.conf`, independent user presets and other printer brands. Enable **Zortrax → Zortrax M300 Classic** in Orca's own **Select/Remove printers** dialog and leave Creality/Inventure selected. Backups and the optional old-offline-bundle archive operation are reversible.

**Use root `install.py` only.** Old versioned installers, global-config repair tools and R3–R6 ZIPs have been removed from the current tree. Earlier files remain recoverable in [Git history](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Orca-Slicer/tree/18d68bb161631004e6909a0f7585fe552b15b302); history has not been rewritten.

## Quick process correspondence — nozzle 0.4 mm

| Z-SUITE selection | Current Orca starting point | Important distinction |
|---|---|---|
| 0.09 fine detail | 0.08mm SuperDetail | Different height, not an exact replacement |
| 0.14 High | 0.12mm Detail | Thinner approximation |
| 0.14 Normal | 0.16mm Optimal | Slightly thicker approximation |
| 0.19 Normal | 0.20mm Standard | Six speeds match the cited Z-PLA Pro Normal example, not the whole profile |
| 0.19 High | 0.20mm High Quality | Three walls and different speeds, not the OEM High table |
| 0.19 Draft | A user copy of 0.20mm Standard | No supplied 0.20 Draft; compare speeds explicitly |
| 0.29 | 0.28mm SuperDraft | Different height and default 10% infill |

Choose the same material, then copy the old project's actual infill density/pattern, shells, supports and raft choices. **Source displayed layer labels and recovered SliceThickness are shown separately.** The [complete generated table](docs/ZSUITE_TO_ORCA.md) includes every recovered Classic M300 row without inventing missing equivalents.

## No print-setting changes in this cleanup

All **140 current profile JSON files are preserved byte-for-byte**, including names, IDs and numerical settings. The existing R7.1 Z-PLA **0.4 mm** preset requests **210°C nozzle / 50°C bed**, whereas the recovered source bed value is 30°C. This remains a user-reported start-test override, not a new cleanup change or OEM recommendation. Other Z-PLA nozzle variants retain 30°C.

`M83`, `START_PRINT`/`END_PRINT`/`PAUSE`, `MESH=AUTO` and **PA=0 pending calibration** remain unchanged. The separate [Klipper project](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper) owns homing, PC7 contact release, Z range and mesh compensation. No purge lines are relocated.

**PEEK/PEI are visible reference entries, not printable materials on a 305°C target-limit setup.** Their 400/370/360°C requests exceed it. Slicing success is not hardware qualification; Generic and other materials still need physical calibration.

## Current layout

```text
profiles/                 one current native vendor and preset set
install.py                guarded, reversible macOS installer
docs/                     English guides and generated CSV tables
sources/                  extracted numerical evidence and provenance
tests/                    installer, profile, slicing and loader checks
tools/                    catalog, checksums, packaging and validation
evidence/                 current baseline hashes and test results
.github/workflows/        one current validation workflow
```

Source databases are evidence, not old installable versions. No OEM installers, DLLs, fonts or old profile ZIPs are distributed. [Current change notes](CHANGELOG.md) · [validation scope](docs/VALIDATION.md).
'''
CHANGELOG='''# Current release notes

## R7.1 — current-only repository cleanup, 12 November 2026

This is a repository/documentation cleanup, not a new numerical print calibration. All 140 current profile JSON files, identities and settings match the baseline commit `18d68bb161631004e6909a0f7585fe552b15b302` byte-for-byte.

The current tree now contains one `profiles/` directory, one English `install.py`, one validation workflow, current test evidence and English documentation. Old R3–R6 bundles, duplicate native directories, obsolete generators, repair installers, Polish manuals and historical test summaries were removed from the working tree. They remain in Git history; no history rewrite or host-repository modification was performed.

The migration reference is generated from actual source and preset files. It contains 30 process rows, 104 filament/nozzle rows, all 152 recovered Classic M300 combinations and 18 PLA Pro feature-speed comparisons. Source/displayed heights, other-printer origins, missing equivalents, shell-mode limitations and source/current temperatures are explicit.

The safe installer retains its transaction, backup format and preservation of other printers and OrcaSlicer.conf. Only its entry point/source path and messages changed. Installation must happen locally on a Mac with Orca closed; cleanup does not install anything on the user's computer.

The pre-existing 0.4 mm Z-PLA 50°C bed override remains distinguished from its 30°C source. PA remains zero; high-temperature references remain visible but unqualified. Fresh software checks are recorded in [current evidence](evidence/VALIDATION.json), not copied from older pass summaries.

[README](README.md) · [crosswalk](docs/ZSUITE_TO_ORCA.md).
'''
VALIDATION='''# Validation and evidence boundaries

The authoritative current run is [evidence/VALIDATION.json](../evidence/VALIDATION.json). It records the tested commit and workflow, rather than relabeling old passes.

| Check | Establishes | Does not establish |
|---|---|---|
| 140 preset baseline hashes | Current numerical settings and IDs are unchanged | Physical quality |
| Index/field validation | One model, four variants, 30 processes, 104 filaments | Compatibility with untested future slicers |
| Source/table audit | All 152 source combinations retained and current values read from files | Full execution of the OEM slicing pipeline |
| Installer regression tests | Scoped writes, other-printer/global-config preservation, idempotence and rollback in temporary directories | Already-installed state on the user's Mac |
| OrcaSlicer 2.5.0 runtime | 30 process + 104 filament + four PA checks = 138 jobs | 138 physical prints or permission to print PEEK/PEI |
| Linux/Xvfb native GUI loader | Processes/filaments loaded and four variants visible | User's macOS GUI tested |

The workflow never connects to a printer or executes generated G-code. It uses a checksum-pinned Orca 2.5.0 binary. Current unit tests include 14 installer and 15 source/profile contracts. High-temperature reference filaments are sliced only for software inspection.

## Operator evidence — 11 November 2026

The user reported a Benchy starting after a Klipper-side correction. The preceding failure was `Move out of range: 3.000 10.000 -0.089 [0.000]` during purge with an active `m300_pads` mesh. Nominal purge Z=0.28 mm plus a local correction near -0.369 mm was rejected by the former zero lower axis bound.

The operator's final **host** configuration was:

```ini
[stepper_z]
position_min: -0.5

[m300_calibration]
safe_z: 5
approach_distance: 6.5
probe_search_margin: 1
```

These are not Orca settings and are not installed here. They preserve center-contact homing, purge placement and active mesh. A test on one machine does not qualify the mechanical range on all M300 printers. PC7-release clearance is separate.

The recorded print target was Z-PLA / nozzle 0.4 / 210°C nozzle / 50°C bed; the recovered source bed was 30°C. CANCEL_PRINT parked the head and Ready/IDLE was observed. A later successful start was reported. **Print completion and first-layer quality have not been confirmed here.**

Historical test results remain in Git history. Current evidence is generated only after the cleaned tree passes static, unit, slicing and loader checks. [Profiles](PROFILES.md) · [crosswalk](ZSUITE_TO_ORCA.md) · [source checksums](../sources/MANIFEST.json).
'''
SOURCE_README='''# Numerical source evidence

These files are the evidence needed to audit the current profiles, not old installable releases.

| File | Contents |
|---|---|
| [zsuite_classic.json](zsuite_classic.json) | 448 recovered records, including 152 Classic M300 selections |
| [zsuite_beta4.json](zsuite_beta4.json) | 214 recovered records from named other Zortrax models |
| [filament_provenance.json](filament_provenance.json) | Exact selected source metadata/mapping for the 76 current named Zortrax filament presets |
| [MANIFEST.json](MANIFEST.json) | Original binary/installer checksums and retained numerical-file hashes |

Record source, model, material, nozzle, displayed layer, quality and infill labels are preserved. Missing fields are not silently invented. The original extraction code remains accessible through the manifest's pinned Git-history link. No vendor installer, DLL, font or image asset is distributed.

The only retained numerical-source override is explicitly marked: Z-PLA / nozzle 0.4 has current bed 50°C rather than source 30°C, based on a reported print start. No source data were edited to disguise that difference. Other-model data do not prove Classic compatibility. [Generated correspondence](../docs/ZSUITE_TO_ORCA.md).
'''
CHECKSUMS='''#!/usr/bin/env python3
"""Generate or verify the complete current-tree SHA256SUMS manifest."""
import argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','__pycache__','out','dist'}
def files(root=ROOT):
 return sorted(p for p in root.rglob('*') if p.is_file() and not (set(p.relative_to(root).parts)&SKIP) and p.name not in ('SHA256SUMS','.DS_Store') and p.suffix!='.pyc')
def expected(root=ROOT):return ''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\\n' for p in files(root))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();p=ROOT/'SHA256SUMS';text=expected()
 if a.write:p.write_text(text)
 elif not p.exists() or p.read_text()!=text:raise SystemExit('Checksum manifest missing/stale or a file changed. Review before regenerating.')
 print('PASS: '+str(len(files()))+' current files covered by SHA256SUMS')
if __name__=='__main__':main()
'''
PACKAGE='''#!/usr/bin/env python3
"""Build one current portable profile/source package; never install."""
import hashlib,json,zipfile
from pathlib import Path
from checksums import files,expected
ROOT=Path(__file__).resolve().parents[1]
def main():
 assert (ROOT/'SHA256SUMS').read_text()==expected(),'Review and refresh checksums first'
 target=ROOT/'dist';target.mkdir(exist_ok=True);path=target/'Zortrax_M300_Classic_CURRENT.zip'
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in [*files(),ROOT/'SHA256SUMS']:
   info=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),(2026,11,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
 (target/'SHA256SUMS').write_text(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name+'\\n')
 print(json.dumps({'package':str(path),'bytes':path.stat().st_size,'profile_revision':'R7.1','host_changed':False}))
if __name__=='__main__':main()
'''
if __name__=='__main__':main()
