#!/usr/bin/env python3
"""Test-only AST operation metering on deterministic 5s synthetic 100k/250k/500k/1M.

Full historical extent, native BOTH direction, complete enabled stages. Verify
byte-stable output against independently produced original and V8.1 snapshots.
All operations marked SELECTED_SITE_ONLY, not complete interpreter counts.
"""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
import psutil
BASE=Path('/mnt/data/V9_work')
sys.path.insert(0,str(BASE/'tooling'))
from strict_golden import sha256,stable_payload
MANIFEST=json.loads((BASE/'output/V9_SYNTHETIC_INPUTS.json').read_text())
ENGINES={'original':Path('/mnt/data/V9_continue/metered_orig_v2/engine'),
         'v81':Path('/mnt/data/V9_continue/metered_v81_v2/engine')}
OBSERVER=Path('/mnt/data/V9_final/tooling/semantic_trace_v3.py')

def run(item,variant,out):
    raw=Path(item['file']);assert sha256(raw.read_bytes())==item['raw_sha256']
    n=item['bars'];path=out/f'{n}.{variant}'
    cmd=[sys.executable,'-B',str(OBSERVER),'--engine-root',str(ENGINES[variant]),
         '--raw',str(raw),'--from-time',str(item['first_time']),'--to-time',str(item['last_time']),
         '--meter-output',str(path)+'.counters.json']
    t0=time.perf_counter();cpu=0.;rss=0
    with Path(str(path)+'.native.json').open('wb') as fout,Path(str(path)+'.stderr.log').open('wb') as ferr:
        p=subprocess.Popen(cmd,stdout=fout,stderr=ferr,env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':'/mnt/data/V9_continue/tooling'})
        proc=psutil.Process(p.pid)
        while p.poll() is None:
            try:
                cpu=max(cpu,sum(proc.cpu_times()[:2]));rss=max(rss,proc.memory_info().rss)
            except psutil.NoSuchProcess:break
            time.sleep(.05)
        rc=p.wait()
    if rc:raise RuntimeError(f'exit={rc} {Path(str(path)+".stderr.log").read_text()[-1000:]}')
    expected=BASE/'output'/f'synthetic_{n}_{variant}.json'
    ref,ref_schema=stable_payload(expected.read_bytes())
    native,schema=stable_payload(Path(str(path)+'.native.json').read_bytes())
    if native!=ref or schema!=ref_schema:
        raise AssertionError(f'Native BOTH stable output or telemetry mismatch {variant} {n}')
    cnt=json.loads(Path(str(path)+'.counters.json').read_text())
    counts=cnt['counts']; kinds={}
    for tag,v in counts.items(): kinds[tag.split(':')[-1]]=kinds.get(tag.split(':')[-1],0)+v
    row={'source':'ACTUAL_INSTRUMENTED_TEST_ONLY', 'bars':n,'variant':variant,
         'stable_pass':True,'stable_sha256':sha256(native),'telemetry_schema_pass':True,
         'selected_instrumented_operations':sum(counts.values()),'by_type':kinds,
         'per_site':str(path)+'.counters.json',
         'process_cpu_s_sampled':round(cpu,5),'peak_rss_mib_sampled':round(rss/2**20,4),
         'observed_metered_wall_s':round(time.perf_counter()-t0,5),
         'coverage':'SELECTED_AST_LOOP_HEAP_SORT_CACHE_SITES; NOT ALL INTERPRETER OPERATIONS'}
    return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--sizes',default='100000,250000,500000,1000000');p.add_argument('--variants',default='original,v81');a=p.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    sizes=set(int(x) for x in a.sizes.split(','));variants=a.variants.split(',')
    rows=[]
    for item in MANIFEST:
        if item['bars'] not in sizes:continue
        for variant in variants:
            print('START',item['bars'],variant,flush=True)
            try:
                row=run(item,variant,out);row['status']='PASS'
            except Exception as ex:
                row={'bars':item['bars'],'variant':variant,'status':'FAIL','error':repr(ex)}
            rows.append(row)
            (out/'meter_synthetic_report.json').write_text(json.dumps({'status':'INCOMPLETE','completed':len(rows),'expected':len(sizes)*len(variants),'rows':rows},indent=2))
            print('END',item['bars'],variant,row['status'],row.get('selected_instrumented_operations'),flush=True)
            if row['status']=='FAIL':return 1
    (out/'meter_synthetic_report.json').write_text(json.dumps({'status':'PASS','completed':len(rows),'expected':len(sizes)*len(variants),'rows':rows},indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
