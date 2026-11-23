#!/usr/bin/env python3
"""Independent freeze contract: ZIP, Git blob SHA, 7 original RAW and 7 stable outputs."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path('/mnt/data')
WORK=ROOT/'V9_work'
GOLD=WORK/'golden'
ZIP=ROOT/'V9_inputs/TradingBot_GitHubMain_Baseline_30s_Both_01d54ecf_20261123_v1.zip'
EXPECTED_ZIP='080175abbd7a3895596230b40783062901deb38c0cc8dd3b97fc058ef21cbb88'
SOURCES={'bridge/__init__.py':'7cce7308316bd9e00f1a3687a6a84e0f1adb22d4',
 'bridge/trading_pipeline.py':'7b28fa7e93c8980c082cb277fb75556959b1abcf',
 'bridge/live_pipeline.py':'e1f1e7d3414a75ed073b67ff2ded3a5a481f6182',
 'pipeline/reaction_engine.py':'9adffb832ffa231ba0cb01de507a30fbe62be0b0',
 'pipeline/__init__.py':'656ba15cfbd7edab34a66cd5bc907171940af38c',
 'pipeline/a_zone_detector.py':'431934d2fb597238d5281a769c29fdb51747868b',
 'pipeline/blue_line_detector.py':'f25efc55bbc387c6a3a592ffe3ff87ee12cf6891',
 'pipeline/s_zone_detector.py':'53460e68538ac790ab969084c1c7101e5ca833d7',
 'pipeline/PL_PH_detector.py':'33ecb3671c7808c7f92b494d39ac5b156a8cd67e',
 'pipeline/lifecycle_engine.py':'2885dcbd3af108baadde7510ffd7968ad735c57e',
 'pipeline/core_utils.py':'38a1053510c5fb114e1b4290de00a2d3b27fc373',
 'pipeline/direction_policy.py':'f7d047abde0eb884905f86c1d2beeaaec3f6e07a',
 'pipeline/e_zone_detector.py':'240369edf3352006082efe094eb68ac027d6689f',
 'pipeline/order_audit_engine.py':'6ddb93ba097ef137af2405ef15356b6f6bcf97de',
 'pipeline/true_false.py':'d569d16bc493b9eb5da75ed5594c168751856b6f'}
source_root=GOLD/'github_engine_commit_01d54ecf/engine'
sha=lambda b:hashlib.sha256(b).hexdigest()
source=[]
for name,expected in SOURCES.items():
 b=(source_root/name).read_bytes();actual=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
 source.append({'path':name,'expected_git_blob':expected,'actual_git_blob':actual,'status':'PASS' if actual==expected else 'FAIL'})
manifest=json.loads((WORK/'tooling/inputs_verified.json').read_text())
data=[]
for item in manifest['datasets']:
 raw=ROOT/item['file'];b=raw.read_bytes();actual=sha(b)
 arr=json.loads(b)
 if len(arr)!=item['records']:status='FAIL'
 elif arr[0]['time']!=item['first_time'] or arr[-1]['time']!=item['last_time']:status='FAIL'
 elif actual!=item['raw_sha256']:status='FAIL'
 else:status='PASS'
 stem=raw.stem.replace(' ','_')
 stable=(GOLD/'runs/github_baseline'/(stem+'.stable.json')).read_bytes()
 sh=sha(stable)
 data.append({'file':item['file'],'expected_raw_sha256':item['raw_sha256'],'actual_raw_sha256':actual,
       'records':len(arr),'stable_sha256':sh,'status':status if sh==item['stable_output_sha256'] else 'FAIL'})
zipsha=sha(ZIP.read_bytes())
with zipfile.ZipFile(ZIP) as z:
    crc_member=z.testzip();members=len(z.infolist())
vv=ROOT/'V9_inputs/TradingBot_Engine_V8.1_30S_BOTH_SOURCE_EXPERIMENTAL_20261123.zip'
vsha=sha(vv.read_bytes())
report={'status':'PASS' if all(x['status']=='PASS' for x in data+source) and zipsha==EXPECTED_ZIP and crc_member is None else 'FAIL',
 'commit':'01d54ecf0149ebd15de92798be18810b6e2eb791',
 'original_golden_zip_sha256':zipsha,'original_golden_zip_valid':zipsha==EXPECTED_ZIP,
 'original_zip_crc_first_bad_file':crc_member,'zip_members':members,
 'v81_source_zip_sha256':vsha,'sources':source,'raws':data,'total_rows':sum(x['records'] for x in data),
 'snapshot_no_mutation':True}
Path('/mnt/data/V9_final/V9_FREEZE_AUDIT.json').write_text(json.dumps(report,indent=2))
print(report['status'],len(source),len(data),report['total_rows'],vsha)
if report['status']!='PASS':raise SystemExit(1)
