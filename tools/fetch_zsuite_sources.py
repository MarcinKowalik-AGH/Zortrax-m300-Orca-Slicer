#!/usr/bin/env python3
"""Recover only numeric JSON from two reviewed installers; scratch data is disposable."""
import argparse,hashlib,io,json,subprocess,sys,zipfile
from pathlib import Path
from remotezip import RemoteZip
ROOT=Path(__file__).resolve().parents[1]
ROWS={
 'classic':('Zortrax Archive/Software/Windows/Z-SUITE_v2.32.0_Win-1.zip','dedc7d0f4136678d742d3bea0dc8db524db716d3bba702f7118c8c0a66061c3c'),
 'beta4':('Zortrax Archive/Software/Windows/Beta/Z-SUITE-BETA_v4.0.0_Win.exe_.zip','ad2c04816980b38fae4499f1ba54f7c2ccdbacd200b97d3dfd67d399c4d5aa26')}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--scratch',type=Path,required=True);ap.add_argument('--innoextract',required=True);a=ap.parse_args()
 a.scratch.mkdir(parents=True,exist_ok=True);(ROOT/'sources').mkdir(exist_ok=True)
 url='https://archive.org/download/zortrax-archive/Zortrax%20Archive.zip';metadata={}
 with RemoteZip(url,initial_buffer_size=262144,timeout=120) as z:
  for version,(member,digest) in ROWS.items():
   data=z.read(member)
   if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('Input differs from reviewed/uploaded ZIP: '+version)
   with zipfile.ZipFile(io.BytesIO(data)) as inner:
    assert inner.testzip() is None
    names=[n for n in inner.namelist() if n.lower().endswith('.exe')];assert len(names)==1
    exe=inner.read(names[0])
   folder=a.scratch/version;folder.mkdir(exist_ok=True);installer=folder/'setup.exe';installer.write_bytes(exe)
   subprocess.run([a.innoextract,'-e','-d',str(folder/'extracted'),str(installer)],check=True,stdout=subprocess.DEVNULL)
   dll=folder/'extracted/app/Z-SUITE.dll'
   subprocess.run([sys.executable,str(ROOT/'tools/zsuite_numeric.py'),'--version',version,'--dll',str(dll),'--out',str(ROOT/'sources'/('ZSUITE_'+version+'.json'))],check=True)
   metadata[version]={'archive':url,'member':member,'zip_sha256':digest,'exe_sha256':hashlib.sha256(exe).hexdigest(),'dll_sha256':hashlib.sha256(dll.read_bytes()).hexdigest(),'application_executed':False,'fonts_exported':False}
 (ROOT/'sources/SOURCE_MANIFEST_R5.json').write_text(json.dumps(metadata,indent=2)+'\n')
if __name__=='__main__':main()
