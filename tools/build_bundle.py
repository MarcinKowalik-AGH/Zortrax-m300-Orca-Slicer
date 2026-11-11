#!/usr/bin/env python3
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
