#!/usr/bin/env python3
"""Record actual current CI results; never reuse historical pass counts."""
import argparse,hashlib,json,os,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BINARY_SHA='d13eb0a9cd618ed080ab6b82c64c0a60c4501aac91e88d5ac2c3b526fb141a7c'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out
 static=json.loads((out/'static.json').read_text());slicing=json.loads((out/'slicing/summary.json').read_text());loader=json.loads((out/'loader.json').read_text())
 log=(out/'unit-tests.log').read_text();m=re.search(r'Ran (\d+) tests',log)
 if not m or not re.search(r'\nOK\s*$',log):raise SystemExit('Unit tests did not pass')
 assert int(m[1])==29 and static['status']=='PASS' and slicing['tests']==138 and slicing['pass']==138 and slicing['fail']==0 and loader['native_loader_pass']
 profile_hash=hashlib.sha256(''.join(p.relative_to(ROOT/'profiles').as_posix()+'\0'+hashlib.sha256(p.read_bytes()).hexdigest()+'\n' for p in sorted((ROOT/'profiles').rglob('*.json'))).encode()).hexdigest()
 report={'status':'PASS','profile_revision':'R7.1','repository_layout':'current-only','tested_source_commit':os.environ.get('GITHUB_SHA'),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'workflow_url':'https://github.com/MarcinKowalik-AGH/Zortrax-m300-Orca-Slicer/actions/runs/'+os.environ.get('GITHUB_RUN_ID','local'),'orca_target_version':'2.5.0','orca_appimage_sha256':BINARY_SHA,'profile_set_sha256':profile_hash,'static':static,'unit_tests':int(m[1]),'slicing':{'cases':slicing['tests'],'pass':slicing['pass'],'fail':slicing['fail'],'process_cases':30,'filament_cases':104,'pa_cases':4},'native_loader':loader,'profile_data_changed_by_cleanup':False,'host_changed':False,'hardware_tests_executed_by_this_run':0,'mac_user_install_test':False,'operator_evidence':'User reported a print starting on 2026-11-11 after a host-side Z-range correction; completion and quality not confirmed here.'}
 evidence=ROOT/'evidence';(evidence/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copyfile(out/'slicing/results.json',evidence/'SLICING_RESULTS.json');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
