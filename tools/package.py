#!/usr/bin/env python3
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
 (target/'SHA256SUMS').write_text(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name+'\n')
 print(json.dumps({'package':str(path),'bytes':path.stat().st_size,'profile_revision':'R7.1','host_changed':False}))
if __name__=='__main__':main()
