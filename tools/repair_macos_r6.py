#!/usr/bin/env python3
"""Mac-only local M300 preset cleanup and native R6 activation; no printer access.
Default: show plan. --apply creates a private local backup before any change.
--restore BACKUP restores only if affected paths have not subsequently changed.
Python >=3.8; standard library only. Never run this on the Orange Pi.
"""
import argparse
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

DIAMETERS = ('0.2', '0.3', '0.4', '0.6')
GROUPS = ('machine_model_list', 'machine_list', 'filament_list', 'process_list')


def load(path):
    with Path(path).open(encoding='utf-8-sig') as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise ValueError('Expected JSON object: '+str(path))
    return obj


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2)+'\n').encode('utf-8')


def classic(value):
    text = re.sub(r'[_-]+', ' ', str(value)).lower()
    return bool(re.search(r'\bm300\b', text)) and not bool(re.search(r'\bm300\s*(?:plus|dual)\b', text))


def owned(obj, known=()):
    compat = obj.get('compatible_printers', [])
    if isinstance(compat, str):
        compat = [compat] if compat else []
    if not isinstance(compat, list):
        raise ValueError('Unsupported compatible_printers format')
    if compat and not all(classic(v) or v in known for v in compat):
        return False  # Shared profiles must not be removed.
    model = obj.get('printer_model', '')
    if model and not classic(model):
        return False
    fields = (obj.get('name', ''), model, obj.get('inherits', ''))
    return any(classic(v) or v in known for v in fields if isinstance(v, str)) or bool(compat)


def safe(root, rel):
    rel = Path(rel)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise ValueError('Unsafe relative path: '+str(rel))
    p = root
    for part in rel.parts:
        p = p/part
        if p.is_symlink():
            raise ValueError('Refusing symlink: '+str(p))
    if p.is_dir():
        for child in p.rglob('*'):
            if child.is_symlink():
                raise ValueError('Refusing symlink inside '+str(p))
    return p


def fingerprint(p):
    if not p.exists():
        return None
    if p.is_file():
        return {'file': hashlib.sha256(p.read_bytes()).hexdigest()}
    return {'tree': {str(x.relative_to(p)): hashlib.sha256(x.read_bytes()).hexdigest()
                     for x in sorted(p.rglob('*')) if x.is_file()}}


def plan(root, source, nozzle=None):
    root, source = Path(root).resolve(), Path(source).resolve()
    conf = safe(root, 'OrcaSlicer.conf')
    cfg = load(conf)
    vendor = load(source/'Zortrax.json')
    if vendor.get('name') != 'Zortrax':
        raise ValueError('Unexpected source vendor')
    counts = [len(vendor.get(k, [])) for k in GROUPS]
    if counts != [1, 4, 76, 80]:
        raise ValueError('Expected complete R6: 1 model / 4 printers / 76 filaments / 80 processes')
    incoming = {}
    for group in GROUPS:
        for entry in vendor[group]:
            p = safe(source/'Zortrax', entry['sub_path'])
            obj = load(p)
            if obj.get('name') != entry['name'] or not owned(obj):
                raise ValueError('Source index/scope mismatch: '+str(p))
            if group != 'machine_model_list' and obj.get('from') != 'system':
                raise ValueError('Expected native system profile: '+str(p))
            incoming['system/Zortrax/'+entry['sub_path']] = p.read_bytes()
    new_names = {e['name'] for k in GROUPS for e in vendor[k]}
    deletes, warnings, removed_names = set(), [], set()

    # Orca2.5 loads local bundles from user/<account>/_local/<id>.
    account = cfg.get('preset_folder') or 'default'
    if not isinstance(account, str) or len(Path(account).parts) != 1 or account in ('.', '..'):
        raise ValueError('Invalid active preset_folder')
    accounts = {'default', account}
    for account in sorted(accounts):
        user = safe(root, 'user/'+account)
        local = user/'_local'
        if local.is_dir():
            for bundle in sorted(local.iterdir()):
                if not bundle.is_dir():
                    continue
                safe(root, bundle.relative_to(root))
                machines = []
                for p in bundle.rglob('*.json'):
                    obj = load(p)
                    if obj.get('type') == 'machine' or 'nozzle_diameter' in obj:
                        machines.append(obj)
                chosen = [obj for obj in machines if owned(obj)]
                if chosen and len(chosen) == len(machines):
                    deletes.add(str(bundle.relative_to(root)))
                    for p in bundle.rglob('*.json'):
                        name = load(p).get('name')
                        if isinstance(name, str):
                            removed_names.add(name)
                elif chosen:
                    warnings.append('Mixed bundle retained (contains other printers): '+bundle.name)
        subscribed = user/'_subscribed'
        if subscribed.is_dir():
            for p in subscribed.rglob('*.json'):
                if owned(load(p)):
                    warnings.append('Subscribed M300 bundle retained; unsubscribe through File > Preset Bundle.')
                    break
        profiles = []
        for category in ('machine', 'printer', 'filament', 'process', 'print'):
            folder = user/category
            if folder.is_dir():
                for p in sorted(folder.glob('*.json')):
                    safe(root, p.relative_to(root))
                    profiles.append((p, load(p)))
        # Track descendants of removed M300 presets without touching generic/shared presets.
        changed = True
        while changed:
            changed = False
            for p, obj in profiles:
                rel = str(p.relative_to(root))
                if rel not in deletes and owned(obj, removed_names | new_names):
                    deletes.add(rel)
                    if isinstance(obj.get('name'), str):
                        removed_names.add(obj['name'])
                    sidecar = p.with_suffix('.info')
                    if sidecar.is_file():
                        deletes.add(str(sidecar.relative_to(root)))
                    changed = True

    # Replace M300 entries only, retaining Inventure/M200/Plus/Dual entries in Zortrax.
    old_index_path = safe(root, 'system/Zortrax.json')
    merged = copy.deepcopy(vendor)
    if old_index_path.exists():
        previous = load(old_index_path)
        if previous.get('name') != 'Zortrax':
            raise ValueError('Unexpected existing Zortrax index')
        merged = copy.deepcopy(previous)
        for key, val in vendor.items():
            if key not in GROUPS:
                merged[key] = copy.deepcopy(val)
        retained_paths = set()
        for group in GROUPS:
            keep = []
            for entry in previous.get(group, []):
                p = safe(root, 'system/Zortrax/'+entry['sub_path'])
                obj = load(p) if p.exists() else {'name': entry['name']}
                if owned(obj) or entry['name'] in new_names:
                    deletes.add(str(p.relative_to(root)))
                else:
                    if not p.is_file():
                        raise ValueError('Missing unrelated Zortrax profile: '+str(p))
                    keep.append(entry)
                    retained_paths.add(str(p.relative_to(root)))
            merged[group] = keep + copy.deepcopy(vendor[group])
        if retained_paths.intersection(incoming):
            raise ValueError('Source collides with a non-M300 profile')
        deletes.difference_update(retained_paths)
    incoming['system/Zortrax.json'] = encoded(merged)
    # Orca2.5 may load an older .opc before parsing the JSON: retire ONLY this vendor cache.
    if safe(root, 'system/Zortrax.opc').exists():
        deletes.add('system/Zortrax.opc')

    models = cfg.get('models') or []
    filaments = cfg.get('filaments') or []
    selected = cfg.get('presets') or {}
    if not isinstance(models, list) or not isinstance(filaments, list) or not isinstance(selected, dict):
        raise ValueError('Unknown Orca2.5 configuration schema; no changes made')
    if not all(isinstance(v, dict) for v in models) or not all(isinstance(v, str) for v in filaments):
        raise ValueError('Unknown model/filament selection format')
    old_selected = selected.get('printer', '')
    if nozzle is None:
        hits = re.findall(r'0\.[2346](?!\d)', old_selected) if classic(old_selected) else []
        nozzle = hits[-1] if hits else '0.4'
    if nozzle not in DIAMETERS:
        raise ValueError('Unsupported nozzle selection')
    cfg['models'] = [v for v in models if not classic(v.get('model', ''))]
    cfg['models'].append({'vendor': 'Zortrax', 'model': 'Zortrax M300', 'nozzle_diameter': ';'.join(DIAMETERS)})
    cfg['filaments'] = list(dict.fromkeys([v for v in filaments if not classic(v) and v not in removed_names]
                                         + [v['name'] for v in vendor['filament_list']]))
    cfg['presets'] = copy.deepcopy(selected)
    cfg['presets'].update(printer='Zortrax M300 '+nozzle,
                          print=('0.10' if nozzle == '0.2' else '0.20')+'mm Standard @Zortrax M300 '+nozzle,
                          filaments=['Z-PLA Pro @Zortrax M300 '+nozzle])
    incoming['OrcaSlicer.conf'] = encoded(cfg)
    deletes.difference_update(incoming)
    writes = {r: data for r, data in incoming.items()
              if not safe(root, r).is_file() or safe(root, r).read_bytes() != data}
    deletes = {r for r in deletes if safe(root, r).exists()}
    touched = sorted(set(writes) | deletes)
    return {'root': root, 'writes': writes, 'deletes': sorted(deletes),
            'before': {r: fingerprint(safe(root, r)) for r in touched},
            'nozzle': nozzle, 'warnings': sorted(set(warnings)), 'source_counts': counts}


def erase(path):
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.m300-repair-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        if path.exists():
            shutil.copymode(path, tmp)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def restore_files(root, backup, before):
    for rel in sorted(before, key=lambda r: len(Path(r).parts), reverse=True):
        p = safe(root, rel)
        erase(p)
        if before[rel] is not None:
            original = safe(backup/'before', rel)
            p.parent.mkdir(parents=True, exist_ok=True)
            if original.is_dir():
                shutil.copytree(original, p)
            else:
                shutil.copy2(original, p)


def apply(p):
    root = p['root']
    if not p['before']:
        return None
    if any(fingerprint(safe(root, r)) != old for r, old in p['before'].items()):
        raise ValueError('Files changed after planning; close Orca and retry')
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    backup = root.parent/('OrcaSlicer-M300-backup-'+stamp)
    backup.mkdir(mode=0o700)
    for rel, old in p['before'].items():
        if old is None:
            continue
        target = backup/'before'/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        original = safe(root, rel)
        if original.is_dir():
            shutil.copytree(original, target)
        else:
            shutil.copy2(original, target)
        if fingerprint(target) != old:
            raise ValueError('Backup verification failed; original files unchanged')
    receipt = {'revision': 'R6-MAC-REPAIR-1', 'root': str(root), 'before': p['before'],
               'removed_paths': p['deletes'], 'selected_nozzle': p['nozzle'], 'state': 'PREPARED'}
    atomic(backup/'RECEIPT.json', encoded(receipt))
    try:
        for rel in p['deletes']:
            erase(safe(root, rel))
        for rel, data in p['writes'].items():
            atomic(safe(root, rel), data)
        receipt['after'] = {r: fingerprint(safe(root, r)) for r in p['before']}
        receipt['state'] = 'INSTALLED'
        atomic(backup/'RECEIPT.json', encoded(receipt))
    except Exception:
        restore_files(root, backup, p['before'])
        receipt['state'] = 'ROLLED_BACK'
        atomic(backup/'RECEIPT.json', encoded(receipt))
        raise
    return backup


def restore(backup):
    backup = Path(backup).resolve()
    receipt = load(backup/'RECEIPT.json')
    if receipt.get('revision') != 'R6-MAC-REPAIR-1' or receipt.get('state') != 'INSTALLED':
        raise ValueError('Not an installed repair receipt')
    root = Path(receipt['root']).resolve()
    if root.name != 'OrcaSlicer' or backup.parent != root.parent:
        raise ValueError('Backup/target path mismatch')
    for rel, state in receipt['after'].items():
        if fingerprint(safe(root, rel)) != state:
            raise ValueError('Later edits detected; refusing to overwrite: '+rel)
    for rel, state in receipt['before'].items():
        if state is not None and fingerprint(safe(backup/'before', rel)) != state:
            raise ValueError('Damaged backup: '+rel)
    restore_files(root, backup, receipt['before'])
    receipt['state'] = 'RESTORED'
    atomic(backup/'RECEIPT.json', encoded(receipt))


def require_mac_and_closed():
    if sys.platform != 'darwin' or os.environ.get('SSH_CONNECTION') or os.environ.get('SSH_TTY'):
        raise ValueError('STOP: uruchom w lokalnym Terminalu Maca, NIE przez SSH ani na Orange Pi.')
    if os.geteuid() == 0:
        raise ValueError('Uruchom bez sudo, jako zwykły użytkownik Maca.')
    result = subprocess.run(['ps', '-axo', 'comm='], check=True, stdout=subprocess.PIPE, text=True)
    for line in result.stdout.splitlines():
        if Path(line.strip()).name.lower() in ('orcaslicer', 'orca-slicer'):
            raise ValueError('Zapisz projekt i zamknij OrcaSlicer przez Cmd+Q, potem powtórz.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config-dir', type=Path, default=Path.home()/'Library/Application Support/OrcaSlicer')
    ap.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1]/'native')
    ap.add_argument('--nozzle', choices=DIAMETERS)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--restore', type=Path)
    a = ap.parse_args()
    try:
        require_mac_and_closed()
        if a.restore:
            restore(a.restore)
            print('Przywrócono konfigurację sprzed naprawy. Klipper nie był zmieniany.')
            return
        root = a.config_dir.expanduser().resolve()
        if root.name != 'OrcaSlicer' or not (root/'OrcaSlicer.conf').is_file():
            raise ValueError('Nie znaleziono aktywnej konfiguracji Orca. Sprawdź Help > Show Configuration Folder.')
        p = plan(root, a.source, a.nozzle)
        print('TYLKO ORCA NA MACU. Bez SSH, grzania i zmian Klippera.')
        print('Wyłączenie starych elementów M300:', len(p['deletes']))
        for rel in p['deletes']:
            print('  Do kopii:', rel)
        print('Pliki do zapisania:', len(p['writes']))
        print('Aktywacja: 4 drukarki, 76 filamentów, 80 procesów; domyślnie dysza', p['nozzle'])
        for warning in p['warnings']:
            print('UWAGA:', warning)
        if not a.apply:
            print('PLAN BEZ ZMIAN. Zastosowanie: powtórz z --apply.')
            return
        require_mac_and_closed()
        backup = apply(p)
        print('GOTOWE. Kopia:', backup if backup else 'Brak zmian — R6 już aktywne.')
        print('Uruchom Orca i nowy projekt; System presets: Zortrax M300 0.2 / 0.3 / 0.4 / 0.6.')
        print('Inne marki i profile Inventure pozostawiono. Nie otwieraj starego 3MF do sprawdzenia listy.')
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        ap.exit(1, 'Naprawa zatrzymana: '+str(exc)+'\n')


if __name__ == '__main__':
    main()
