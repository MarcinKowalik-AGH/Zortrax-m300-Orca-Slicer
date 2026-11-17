#!/usr/bin/env python3
"""Generate or verify the complete current-tree SHA256SUMS manifest."""
import argparse,hashlib,difflib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','__pycache__','out','dist'}
def files(root=ROOT):
 return sorted(p for p in root.rglob('*') if p.is_file() and not (set(p.relative_to(root).parts)&SKIP) and p.name not in ('SHA256SUMS','.DS_Store') and p.suffix!='.pyc')
def expected(root=ROOT):return ''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\n' for p in files(root))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();p=ROOT/'SHA256SUMS';text=expected()
 if a.write:p.write_text(text)
 elif not p.exists() or p.read_text()!=text:
  actual=p.read_text() if p.exists() else ''
  difference=''.join(difflib.unified_diff(actual.splitlines(True),text.splitlines(True),fromfile='SHA256SUMS',tofile='computed',n=0))
  raise SystemExit('Checksum manifest missing/stale; review mismatches:\\n'+difference[:12000])
 print('PASS: '+str(len(files()))+' current files covered by SHA256SUMS')
if __name__=='__main__':main()
