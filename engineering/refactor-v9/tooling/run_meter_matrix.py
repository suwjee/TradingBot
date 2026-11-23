#!/usr/bin/env python3
"""Run complete 7 RAW in native BOTH mode against AST-metered test-only V8.1.

All accounting generated from executed loops/sorts/heap/cache sites, not timing
profiling. No assumptions about histogram counts, output baseline or operations.
"""
import argparse,csv,hashlib,json,os,subprocess,sys,time
from pathlib import Path
import psutil
TOOL=Path(__file__).resolve().parent
WORK=Path('/mnt/data/V9_work')
sys.path.insert(0,str(WORK/'tooling'))
from strict_golden import stable_match,sha256
INPUTS=json.loads((WORK/'tooling/inputs_verified.json').read_text())['datasets']
REFERENCE=WORK/'golden/runs/github_baseline'
METERS={'v81':Path('/mnt/data/V9_continue/metered_v81/engine'),'original':Path('/mnt/data/V9_continue/metered_orig/engine')}

def one(item,variant,dest):
    raw=Path('/mnt/data')/item['file'];dest=Path(dest);dest.mkdir(exist_ok=True,parents=True)
    if sha256(raw.read_bytes())!=item['raw_sha256']:raise RuntimeError('RAW SHA mismatch '+str(raw))
    stem=raw.stem.replace(' ','_');pfx=dest/(variant+'.'+stem)
    cmd=[sys.executable,'-B',str(TOOL/'semantic_trace.py'),
         '--engine-root',str(METERS[variant]),'--raw',str(raw),
         '--from-time',str(item['first_time']),'--to-time',str(item['last_time']),
         '--meter-output',str(pfx)+'.counters.json']
    now=time.perf_counter();cpu_peak=0.0;rss_peak=0;polls=0
    with (Path(str(pfx)+'.native.json')).open('wb') as stdout,(Path(str(pfx)+'.stderr.log')).open('wb') as stderr:
        proc=subprocess.Popen(cmd,stdout=stdout,stderr=stderr,env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'})
        ps=psutil.Process(proc.pid)
        while proc.poll() is None:
            try:
                t=ps.cpu_times();cpu_peak=max(cpu_peak,t.user+t.system)
                rss_peak=max(rss_peak,ps.memory_info().rss)
                polls+=1
            except psutil.NoSuchProcess:break
            time.sleep(0.025)
        rc=proc.wait()
    timing=time.perf_counter()-now
    if rc:raise RuntimeError(f'{variant} {item["id"]} exit={rc}; stderr tail '+Path(str(pfx)+'.stderr.log').read_text()[-800:])
    original=REFERENCE/(stem+'.json');contract=json.loads((REFERENCE/(stem+'.metrics.json')).read_text())
    result=stable_match(original.read_bytes(),Path(str(pfx)+'.native.json').read_bytes(),contract)
    if not(result['bytes_equal'] and result['timing_schema_equal']):raise AssertionError(f'meter changed stable bytes for {variant} {item["id"]}: {result}')
    counts=json.loads(Path(str(pfx)+'.counters.json').read_text())['counts']
    by_kind={}
    for key,n in counts.items():
        op=key.split(':')[-1];by_kind[op]=by_kind.get(op,0)+n
    row={'dataset_id':item['id'],'raw_file':item['file'],'bars':item['records'],
         'variant':variant,'instrumented':True,'stable_sha256':result['candidate_stable_sha256'],
         'golden_stable_sha256':result['golden_stable_sha256'],'stable_pass':True,
         'wall_s_instrumented':round(timing,6),'sampled_cpu_s':round(cpu_peak,5),'rss_mib':round(rss_peak/1048576,3),
         'operation_count_selected':sum(counts.values()),'operation_counts_by_type':by_kind,
         'per_site_counters_path':str(pfx)+'.counters.json',
         'coverage':'SELECTED_LOOP_SITES_ONLY / no comprehension loop tracing'}
    Path(str(pfx)+'.summary.json').write_text(json.dumps(row,indent=2))
    return row

def run(variant,indices,dest):
    out=Path(dest);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    p=out/('V9_METER_'+variant.upper()+'_RESULTS.json')
    for i in indices:
        item=INPUTS[i]
        print('START',variant,item['id'],flush=True)
        try:r=one(item,variant,out)
        except Exception as exc:
            r={'dataset_id':item['id'],'variant':variant,'status':'FAIL','error':repr(exc)}
        else:r['status']='PASS'
        rows.append(r);p.write_text(json.dumps(rows,indent=2))
        print('COMPLETE',variant,item['id'],r.get('status'),r.get('wall_s_instrumented'),flush=True)
        if r['status']!='PASS':return 1
    return 0
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--variant',choices=('original','v81'),default='v81');a.add_argument('--indices',default='0,1,2,3,4,5,6');a.add_argument('--out',type=Path,default=Path('/mnt/data/V9_continue/results/meter'))
    o=a.parse_args();sys.exit(run(o.variant,[int(n) for n in o.indices.split(',')],o.out))
