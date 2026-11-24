#!/usr/bin/env python3
"""Full 1M synthetic 5s instrumentation in BOTH mode, test-only.

Fail closed on stable output, input hashes and timing schema; report clearly
that selected method-output events != all mutable engine state.
"""
from __future__ import annotations
import gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
import psutil
ROOT=Path('/mnt/data/V9_work')
sys.path.insert(0,str(ROOT/'tooling'))
from strict_golden import sha256,stable_payload
sys.path.insert(0,str(Path(__file__).resolve().parent))
from global_semantic_trace_compare import report
INPUTS=json.loads((ROOT/'output/V9_SYNTHETIC_INPUTS.json').read_text())
ORIGINAL={'original':Path('/mnt/data/V9_continue/metered_orig_v2/engine'),'v81':Path('/mnt/data/V9_continue/metered_v81_v2/engine')}


def main(out):
    root=Path(out);root.mkdir(parents=True,exist_ok=True)
    item=next(x for x in INPUTS if x['bars']==1000000)
    raw=Path(item['file']);assert sha256(raw.read_bytes())==item['raw_sha256']
    result=[]
    for variant,engine in ORIGINAL.items():
        print('START 1M SYNTHETIC',variant,flush=True)
        base=root/variant
        cmd=[sys.executable,'-B',str(Path(__file__).resolve().parent/'semantic_trace_v3.py'),
             '--engine-root',str(engine),'--raw',str(raw),
             '--from-time',str(item['first_time']),'--to-time',str(item['last_time']),
             '--trace-out',str(base)+'.trace.jsonl.gz',
             '--summary',str(base)+'.manifest.json',
             '--stage-profile',str(base)+'.stage_cpu_rss.json']
        start=time.perf_counter();cpu=0;rss=0
        with Path(str(base)+'.native.json').open('wb') as fout,Path(str(base)+'.stderr.log').open('wb') as ferr:
            proc=subprocess.Popen(cmd,stdout=fout,stderr=ferr,env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':'/mnt/data/V9_continue/tooling'})
            p=psutil.Process(proc.pid)
            while proc.poll() is None:
                try:
                    cpu=max(cpu,sum(p.cpu_times()[:2]));rss=max(rss,p.memory_info().rss)
                    if rss > 2900*1048576:
                        proc.kill();raise MemoryError('Instrumented 1M trace exceeded safe RSS cap 2900 MiB')
                except psutil.NoSuchProcess:break
                time.sleep(.05)
            rc=proc.wait()
        if rc:raise RuntimeError('Engine observer execution error '+str(rc)+' '+Path(str(base)+'.stderr.log').read_text()[-2000:])
        expected=ROOT/'output'/f'synthetic_1000000_{variant}.json'
        ref,ref_schema=stable_payload(expected.read_bytes())
        candidate,schema=stable_payload(Path(str(base)+'.native.json').read_bytes())
        if ref!=candidate or schema!=ref_schema:
            raise AssertionError('Instrumentation altered full 1M stable JSON or telemetry schema')
        m=json.loads(Path(str(base)+'.manifest.json').read_text())
        if m['gzip_sha256']!=sha256(Path(str(base)+'.trace.jsonl.gz').read_bytes()):raise AssertionError('Bad trace SHA')
        r={'variant':variant,'stable_output_sha256':sha256(candidate),
           'golden_input_sha256':item['raw_sha256'],'stable_match':True,
           'events':m['events'],'coverage':m['coverage'],
           'partial_representations':m['unsupported_counts'],
           'wall_instrumented_s':time.perf_counter()-start,'sampled_cpu_s':cpu,
           'sampled_peak_rss_mib':rss/2**20}
        result.append(r)
        (root/'synthetic_trace_report.json').write_text(json.dumps({'status':'INCOMPLETE','rows':result},indent=2))
        print('END 1M',variant,'PASS',m['events'],flush=True)
    compare=report(str(root/'original.trace.jsonl.gz'),str(root/'v81.trace.jsonl.gz'))
    (root/'global_semantic_comparison.json').write_text(json.dumps(compare,indent=2))
    overall={'full_raw_1m_trace_data_status':'PASS' if all(r['stable_match'] for r in result) else 'FAIL',
             'selected_global_semantic_status':compare['status'],
             'coverage':'PARTIAL: no complete 1M in-process state ledger trace',
             'rows':result}
    (root/'synthetic_trace_report.json').write_text(json.dumps(overall,indent=2))
    print('GLOBAL',compare['status'],compare['positions_equal'] if 'positions_equal' in compare else compare['total_compared_positions'],flush=True)
    return 0 if compare['status']=='PASS' else 1
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();raise SystemExit(main(a.out))