#!/usr/bin/env python3
"""Independent file hash and embedded manifest audit (no source modifications)."""
import os,json,sys,platform,hashlib,zipfile,subprocess,psutil
from pathlib import Path
from strict_golden import sha256,verify_freeze
W=Path(__file__).resolve().parents[1];P=Path('/mnt/data/V9_inputs');OUT=W/'output'
M=json.loads((W/'tooling/inputs_verified.json').read_text())
archive_checks=[]
for p in P.glob('*.zip'):
 with zipfile.ZipFile(p) as z:
  crc=z.testzip();entries=z.namelist();bad=[]
  if 'SHA256SUMS.txt' in entries:
   for ln in z.read('SHA256SUMS.txt').decode().splitlines():
    if not ln.strip():continue
    digest,name=ln.split(None,1)
    name=name.lstrip(' *')
    if name not in entries or sha256(z.read(name))!=digest:bad.append(name)
  archive_checks.append({'archive':p.name,'bytes':p.stat().st_size,'sha256':sha256(p.read_bytes()),'crc':'PASS' if crc is None else 'FAIL',
                         'manifest_sha256':'PASS' if not bad else 'FAIL','manifest_bad_files':bad,'entries':len(entries)})
origin=W/'golden/github_engine_commit_01d54ecf/engine';source=W/'v81/engine'
expected_git={'bridge/__init__.py':'7cce7308316bd9e00f1a3687a6a84e0f1adb22d4','bridge/live_pipeline.py':'e1f1e7d3414a75ed073b67ff2ded3a5a481f6182','bridge/trading_pipeline.py':'7b28fa7e93c8980c082cb277fb75556959b1abcf',
'pipeline/PL_PH_detector.py':'33ecb3671c7808c7f92b494d39ac5b156a8cd67e','pipeline/__init__.py':'656ba15cfbd7edab34a66cd5bc907171940af38c','pipeline/a_zone_detector.py':'431934d2fb597238d5281a769c29fdb51747868b','pipeline/blue_line_detector.py':'f25efc55bbc387c6a3a592ffe3ff87ee12cf6891','pipeline/core_utils.py':'38a1053510c5fb114e1b4290de00a2d3b27fc373','pipeline/direction_policy.py':'f7d047abde0eb884905f86c1d2beeaaec3f6e07a','pipeline/e_zone_detector.py':'240369edf3352006082efe094eb68ac027d6689f','pipeline/lifecycle_engine.py':'2885dcbd3af108baadde7510ffd7968ad735c57e','pipeline/order_audit_engine.py':'6ddb93ba097ef137af2405ef15356b6f6bcf97de','pipeline/reaction_engine.py':'9adffb832ffa231ba0cb01de507a30fbe62be0b0','pipeline/s_zone_detector.py':'53460e68538ac790ab969084c1c7101e5ca833d7','pipeline/true_false.py':'d569d16bc493b9eb5da75ed5594c168751856b6f'}
blob=lambda b:hashlib.sha1(b'blob '+str(len(b)).encode()+b'\x00'+b).hexdigest()
for name in expected_git:
 assert blob((origin/name).read_bytes())==expected_git[name],name
 assert (source/name).is_file()
source_hash={name:sha256((source/name).read_bytes()) for name in expected_git}
changed=[name for name in expected_git if (origin/name).read_bytes()!=(source/name).read_bytes()]
raws=[]
for d in M['datasets']:
 f=Path('/mnt/data')/d['file'];digest=sha256(f.read_bytes());rows=json.loads(f.read_bytes())
 raws.append({'file':f.name,'raw_sha256':digest,'expected_sha256':d['raw_sha256'],'row_count':len(rows),'expected_rows':d['records'],
              'first_time':rows[0]['time'],'last_time':rows[-1]['time'],'status':'PASS' if (digest==d['raw_sha256'] and len(rows)==d['records'] and rows[0]['time']==d['first_time'] and rows[-1]['time']==d['last_time']) else 'FAIL'})
report={'golden_commit':M['baseline_git_commit'],'source_blobs':expected_git,'source_github_pinned_status':'PASS',
        'frozen_zip_stable_outputs_status':'PASS' if verify_freeze(P/'TradingBot_GitHubMain_Baseline_30s_Both_01d54ecf_20261123_v1.zip',M) else 'FAIL',
        'archives':archive_checks,'v81_changed_modules_vs_pinned_original':changed,'v81_source_sha256':source_hash,
        'raws':raws,'total_raw_rows':sum(x['row_count'] for x in raws),'environment':{
         'python':sys.version,'psutil':psutil.__version__,'os':platform.platform(),'cpu_affinity':psutil.Process().cpu_affinity(),
         'PYTHONHASHSEED':os.environ.get('PYTHONHASHSEED','unset, subprocess uses 0'),
         'thread_environment':{k:v for k,v in os.environ.items() if 'THREAD' in k or k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')},
         'memory_total_mib':round(psutil.virtual_memory().total/2**20,2),'rss_main_mib':round(psutil.Process().memory_info().rss/2**20,3)}}
(OUT/'V9_FREEZE_AUDIT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print({'archives':len(archive_checks),'all_crc':all(x['crc']=='PASS' for x in archive_checks),'all_embedded_checksums':all(x['manifest_sha256']=='PASS' for x in archive_checks),'raws':len(raws),'raw_rows':report['total_raw_rows'],'changed_modules':changed})
