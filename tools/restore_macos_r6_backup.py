#!/usr/bin/env python3
"""Undo only paths recorded by R6-MAC-REPAIR-1; never install printer presets.
Run locally on a Mac with Orca closed. Default is a read-only plan. --apply
first copies every affected current path to a new private rescue folder, so
an Orca.conf rewritten after the repair is retained rather than discarded.
No network, sudo, SSH, printer connection, heating or Klipper operations.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def read_json(path):
    with path.open(encoding='utf-8-sig') as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError('Nieprawidlowy format JSON: ' + str(path))
    return value


def checked(base, rel):
    name = Path(rel)
    if not isinstance(rel, str) or name.is_absolute() or not name.parts or '..' in name.parts or '\\' in rel:
        raise ValueError('Niebezpieczna sciezka w kopii')
    p = base
    for part in name.parts:
        p = p / part
        if p.is_symlink():
            raise ValueError('Dowiazanie symboliczne; niczego nie nadpisano: ' + str(p))
    if p.exists() and not (p.is_file() or p.is_dir()):
        raise ValueError('Nieobslugiwany typ pliku')
    if p.is_dir():
        for child in p.rglob('*'):
            if child.is_symlink() or not (child.is_file() or child.is_dir()):
                raise ValueError('Nieobslugiwany element w ' + str(p))
    return p


def fingerprint(path):
    if not path.exists():
        return None
    if path.is_file():
        return {'file': hashlib.sha256(path.read_bytes()).hexdigest()}
    return {'tree': {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted(path.rglob('*')) if p.is_file()}}


def permitted(rel):
    parts = Path(rel).parts
    if rel in ('OrcaSlicer.conf', 'system/Zortrax.json', 'system/Zortrax.opc'):
        return True
    if len(parts) >= 3 and parts[:2] == ('system', 'Zortrax'):
        return True
    if len(parts) == 4 and parts[0] == 'user' and parts[2] in (
            '_local', 'machine', 'printer', 'filament', 'process', 'print'):
        return True
    return False


def require_mac_closed():
    if sys.platform != 'darwin' or os.environ.get('SSH_CONNECTION') or os.environ.get('SSH_TTY'):
        raise ValueError('Uruchom w lokalnym Terminalu Maca, nie na Orange Pi ani w SSH.')
    if os.geteuid() == 0:
        raise ValueError('Nie uzywaj sudo.')
    p = subprocess.run(['ps', '-axo', 'comm='], check=True, stdout=subprocess.PIPE, text=True)
    if any(Path(line.strip()).name.lower() in ('orcaslicer', 'orca-slicer') for line in p.stdout.splitlines()):
        raise ValueError('Najpierw zapisz projekt i zamknij OrcaSlicer przez Cmd+Q.')


def validate(backup, expected_root):
    backup = Path(backup).expanduser().absolute()
    expected_root = Path(expected_root).expanduser().absolute()
    if backup.is_symlink() or expected_root.is_symlink() or (backup / 'before').is_symlink():
        raise ValueError('Dowiazanie kopii lub konfiguracji jest niedozwolone.')
    if not backup.is_dir() or not expected_root.is_dir():
        raise ValueError('Nie znaleziono kopii lub katalogu konfiguracji.')
    backup, root = backup.resolve(), expected_root.resolve()
    receipt = read_json(checked(backup, 'RECEIPT.json'))
    if (receipt.get('revision') != 'R6-MAC-REPAIR-1'
            or receipt.get('state') not in ('INSTALLED', 'RESTORED')):
        raise ValueError('To nie jest kopia poprzedniej operacji R6.')
    if (Path(receipt.get('root', '')).resolve() != root or root.name != 'OrcaSlicer'
            or backup.parent != root.parent):
        raise ValueError('Kopia pochodzi z innego katalogu. Niczego nie zmieniono.')
    before, after = receipt.get('before'), receipt.get('after')
    if (not isinstance(before, dict) or not isinstance(after, dict)
            or not 1 <= len(before) <= 2000 or set(before) != set(after)
            or not isinstance(before.get('OrcaSlicer.conf'), dict)):
        raise ValueError('Niepelny rejestr kopii.')
    before = dict(before)
    paths = list(before)
    for rel in paths:
        if not permitted(rel):
            raise ValueError('Nieoczekiwany zakres przywracania: ' + rel)
        checked(root, rel)
        if before[rel] is not None:
            source = checked(backup / 'before', rel)
            if fingerprint(source) != before[rel]:
                raise ValueError('Uszkodzona kopia: ' + rel)
        for other in paths:
            if other != rel and Path(rel) in Path(other).parents:
                raise ValueError('Nakladajace sie sciezki kopii.')
    # Validate the saved configuration, but restore its original bytes unchanged.
    saved_config = read_json(checked(backup / 'before', 'OrcaSlicer.conf'))
    if 'models' in saved_config and not isinstance(saved_config['models'], list):
        raise ValueError('Nieznany format zapisanej konfiguracji; przerwano.')
    # A cache can have been generated by the subsequent Orca launch. Quarantine
    # only Zortrax's generated cache, never Creality or another vendor cache.
    cache = 'system/Zortrax.opc'
    if cache not in before and checked(root, cache).exists():
        before[cache] = None
    return root, backup, before


def copy_path(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, target)
    else:
        shutil.copy2(source, target)


def remove_path(path):
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def restore_one(root, rel, state, source_root):
    dest = checked(root, rel)
    if state is None:
        remove_path(dest)
        return
    source = checked(source_root, rel)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source.is_file():
        fd, tmp = tempfile.mkstemp(prefix='.orca-restore-', dir=str(dest.parent))
        os.close(fd)
        try:
            shutil.copy2(source, tmp)
            if dest.is_dir():
                shutil.rmtree(dest)
            os.replace(tmp, dest)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    else:
        remove_path(dest)
        shutil.copytree(source, dest)


def recover(backup, expected_root, apply=False):
    root, backup, desired = validate(backup, expected_root)
    current = {rel: fingerprint(checked(root, rel)) for rel in desired}
    changed = [r for r in desired if desired[r] != current[r]]
    # Restore the main configuration last, after old presets have been restored.
    changed.sort(key=lambda r: (r == 'OrcaSlicer.conf', r))
    print('TYLKO COFNIECIE ZMIAN ORCA NA MACU. Bez instalacji M300 i bez Klippera.')
    print('Kopia zrodlowa:', backup)
    print('Liczba zapisow do odtworzenia/usuniecia:', len(changed))
    if not changed:
        print('Wskazane pliki sa juz zgodne z kopia sprzed naprawy.')
        return None
    if not apply:
        print('PLAN BEZ ZMIAN. Aby przywrocic, dodaj --apply.')
        return None
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    rescue = root.parent / ('OrcaSlicer-przed-cofnieciem-' + stamp)
    rescue.mkdir(mode=0o700)
    # Copy, check every byte, and preflight the state before any active write.
    for rel in changed:
        if current[rel] is not None:
            copy_path(checked(root, rel), checked(rescue / 'current', rel))
            if fingerprint(checked(rescue / 'current', rel)) != current[rel]:
                raise ValueError('Blad dodatkowej kopii. Konfiguracja aktywna pozostaje bez zmian.')
    if any(fingerprint(checked(root, r)) != current[r] for r in changed):
        raise ValueError('Konfiguracja zmienila sie podczas kopii. Zamknij Orca.')
    report = {'operation': 'RESTORE_PRE_R6_MAC_REPAIR', 'root': str(root), 'source_backup': str(backup),
              'state': 'PREPARED', 'saved_current': {r: current[r] for r in changed},
              'desired': {r: desired[r] for r in changed}}
    report_path = rescue / 'RECOVERY.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    attempted = []
    try:
        for rel in changed:
            attempted.append(rel)
            restore_one(root, rel, desired[rel], backup / 'before')
            if fingerprint(checked(root, rel)) != desired[rel]:
                raise ValueError('Nie zgadza sie odtworzony plik: ' + rel)
        report['state'] = 'RESTORED'
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    except Exception:
        for rel in reversed(attempted):
            restore_one(root, rel, current[rel], rescue / 'current')
        report['state'] = 'ROLLED_BACK_RECOVERY'
        report_path.write_text(json.dumps(report, indent=2) + '\n')
        raise
    print('COFNIETO ZMIANY R6. Odtworzono zapisane pliki i OrcaSlicer.conf sprzed naprawy.')
    print('Dodatkowa kopia stanu sprzed cofniecia:', rescue)
    print('Oryginalna kopia pozostala nietknieta. Uruchom Orca i sprawdz Creality.')
    return rescue


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--backup', type=Path, required=True)
    ap.add_argument('--config-dir', type=Path, default=Path.home() / 'Library/Application Support/OrcaSlicer')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    try:
        require_mac_closed()
        recover(args.backup, args.config_dir, args.apply)
    except Exception as exc:
        ap.exit(1, 'Przywracanie zatrzymane: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
