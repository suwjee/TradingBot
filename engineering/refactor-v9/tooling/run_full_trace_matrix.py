#!/usr/bin/env python3
"""Full-length native BOTH runs; instrumented test-only selected internal event trace.

Reports the difference between full input coverage and partial semantic event
coverage. This is NOT a full internal state oracle; never claim otherwise.
"""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
import psutil

HERE=Path(__file__).resolve().parent
sys.path.insert(0,'/mnt/data/V9_work/tooling')
from strict_golden import stable_match,sha256
sys.path.insert(0,str(HERE))
from global_semantic_trace_compare import report as global_report

INPUTS=json.loads(Path('/mnt/data/V9_work/tooling/inputs_verified.json').read_text())['datasets']
ROOTS={
    'original':Path('/mnt/data/V9_work/golden/github_engine_commit_01d54ecf/engine'),
    'v81':Path('/mnt/data/V9_work/v81/engine'),
}
GOLDEN=Path('/mnt/data/V9_work/golden/runs/github_baseline')
OBSERVER=Path('/mnt/data/V9_continue/tooling/semantic_trace.py')


def run_variant(item,variant,root):
    stem=Path(item['file']).stem.replace(' ','_')
    out=root/(variant+'.'+stem)
    raw=Path('/mnt/data')/item['file']
    if sha256(raw.read_bytes()) != item['raw_sha256']:
        raise ValueError('RAW SHA mismatch')
    cmd=[sys.executable,'-B',str(OBSERVER),'--engine-root',str(ROOTS[variant]),
         '--raw',str(raw),'--from-time',str(item['first_time']),
         '--to-time',str(item['last_time']),'--trace-out',str(out)+'.trace.jsonl.gz',
         '--summary',str(out)+'.trace.manifest.json']
    started=time.perf_counter();peak_rss=0;cpu=0;polls=0
    with Path(str(out)+'.native.json').open('wb') as f,Path(str(out)+'.stderr.log').open('wb') as err:
        proc=subprocess.Popen(cmd,stdout=f,stderr=err,env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'})
        p=psutil.Process(proc.pid)
        while proc.poll() is None:
            try:
                peak_rss=max(peak_rss,p.memory_info().rss)
                t=p.cpu_times();cpu=max(cpu,t.user+t.system)
                polls+=1
            except psutil.NoSuchProcess:break
            time.sleep(.05)
        rc=proc.wait()
    wall=time.perf_counter()-started
    if rc:raise RuntimeError('execution error '+str(rc)+': '+Path(str(out)+'.stderr.log').read_text()[-4000:])
    prefix=GOLDEN/stem
    contract=json.loads(Path(str(prefix)+'.metrics.json').read_text())
    equality=stable_match(Path(str(prefix)+'.json').read_bytes(),Path(str(out)+'.native.json').read_bytes(),contract)
    if not (equality['bytes_equal'] and equality['timing_schema_equal']):
        raise AssertionError('Stable output != Frozen Golden: '+str(equality))
    m=json.loads(Path(str(out)+'.trace.manifest.json').read_text())
    if m['gzip_sha256']!=sha256(Path(str(out)+'.trace.jsonl.gz').read_bytes()):
        raise AssertionError('Trace file SHA mismatch')
    return {'variant':variant,'item':item['id'],'raw_records':item['records'],
            'stable_pass':True,'stable_output_sha256':equality['candidate_stable_sha256'],
            'trace_path':str(out)+'.trace.jsonl.gz','trace_jsonl_sha256':m['jsonl_sha256'],
            'trace_events':m['events'],'unsupported_counts':m['unsupported_counts'],
            'coverage':m['coverage'],'sampled_cpu_s':cpu,
            'sampled_peak_rss_mib':round(peak_rss/2**20,2),'wall_instrumented_s':round(wall,4)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--indices',default='0,1,2,3,4,5,6');p.add_argument('--variants',default='original,v81');a=p.parse_args()
    a.out.mkdir(exist_ok=True,parents=True)
    dest=a.out/'trace_matrix_report.json';rows=[]
    for idx in map(int,a.indices.split(',')):
        item=INPUTS[idx];pair={}
        for variant in a.variants.split(','):
            print('START',item['id'],variant,flush=True)
            try:
                row=run_variant(item,variant,a.out)
                pair[variant]=row
                row['status']='PASS'
            except Exception as exc:
                row={'variant':variant,'item':item['id'],'status':'FAIL','error':repr(exc)}
            rows.append(row)
            dest.write_text(json.dumps({'coverage':'SELECTED INTERNAL OBSERVER, NOT ALL INTERNAL STATES',
                      'status':'INCOMPLETE','runs':rows},indent=2))
            print('END',item['id'],variant,row['status'],row.get('trace_events'),flush=True)
        if all(x in pair for x in ('original','v81')):
            c=global_report(pair['original']['trace_path'],pair['v81']['trace_path'])
            cmp_path=a.out/(item['id']+'.global_semantic_comparison.json')
            cmp_path.write_text(json.dumps(c,indent=2))
            rows.append({'item':item['id'],'comparison_status':c['status'],
                         'globally_comparable_events':c['total_compared_positions'],
                         'globally_identical_events':c['positions_equal'],
                         'known_gaps':c['not_in_scope'],'comparison_path':str(cmp_path)})
            dest.write_text(json.dumps({'coverage':'SELECTED INTERNAL OBSERVER; no complete oracle',
                     'status':'INCOMPLETE','runs':rows},indent=2))
            print('GLOBAL',item['id'],c['status'],c['positions_equal'],'/',c['total_compared_positions'],flush=True)
    return int(any(x.get('status')=='FAIL' or x.get('comparison_status')=='FAIL' for x in rows))

if __name__=='__main__':raise SystemExit(main())
