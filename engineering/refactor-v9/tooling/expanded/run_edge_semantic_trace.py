#!/usr/bin/env python3
"""Full native BOTH semantic Trace test for 6 immutable synthetic adversarial variants."""
from __future__ import annotations
import argparse,json,hashlib,os,subprocess,sys,time
from pathlib import Path
BASE=Path('/mnt/data/V9_work');HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'tooling'));from strict_golden import sha256,stable_payload
from global_semantic_trace_compare import report
from audit_trace_coverage import inspect
INPUTS=json.loads((BASE/'output/V9_EDGE_CASES.json').read_text())['results']
INPUTDIR=BASE/'output/synthetic_edge_fixtures'
ROOTS={'original':Path('/mnt/data/V9_continue/metered_orig_v2/engine'),
       'v81':Path('/mnt/data/V9_continue/metered_v81_v2/engine')}

def one(item,variant,out):
    name=item['case'];root=ROOTS[variant];raw=INPUTDIR/(name+'.json');assert sha256(raw.read_bytes())==item['input_sha256']
    rows=json.loads(raw.read_text());stem=out/(name+'.'+variant)
    command=[sys.executable,'-B',str(HERE/'semantic_trace_v3.py'),
             '--engine-root',str(root),'--raw',str(raw),'--from-time',str(rows[0]['time']),
             '--to-time',str(rows[-1]['time']),'--trace-out',str(stem)+'.trace.jsonl.gz']
    with Path(str(stem)+'.native.json').open('wb') as stream,Path(str(stem)+'.stderr.log').open('wb') as err:
        run=subprocess.run(command,stdout=stream,stderr=err,
                  env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':'/mnt/data/V9_continue/tooling'},timeout=240)
    if run.returncode:raise RuntimeError('observer error '+Path(str(stem)+'.stderr.log').read_text()[-1000:])
    stable,schema=stable_payload(Path(str(stem)+'.native.json').read_bytes())
    ref=next(x for x in item['details'] if x['variant']==variant)
    if sha256(stable)!=ref['stable_sha256'] or schema!=ref['telemetry_schema']:
        raise AssertionError('Stable output or timing schema differs from frozen edge test')
    check=inspect(Path(str(stem)+'.trace.jsonl.gz'))
    return {'case':name,'variant':variant,'stable_pass':True,'input_sha256':item['input_sha256'],
            'trace_verified':check['integrity']=='PASS','trace_events':check['raw_events'],
            'trace':str(stem)+'.trace.jsonl.gz',
            'full_immutable_input_sidecar_count':len(check['verified_immutable_chronology_sidecars'])}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);opts=p.parse_args();opts.out.mkdir(parents=True,exist_ok=True)
    rows=[];allcomparisons=[]
    for item in INPUTS:
        pair={}
        for variant in ROOTS:
            print('EDGE START',item['case'],variant,flush=True)
            try:r=one(item,variant,opts.out);r['status']='PASS'
            except Exception as e:r={'case':item['case'],'variant':variant,'status':'FAIL','error':repr(e)}
            rows.append(r)
            if r['status']=='PASS':pair[variant]=r
            print('EDGE END',item['case'],variant,r['status'],flush=True)
        if len(pair)==2:
            cmp=report(pair['original']['trace'],pair['v81']['trace'])
            allcomparisons.append({'case':item['case'],'status':cmp['status'],
                                   'globally_compared':cmp['total_compared_positions'],
                                   'input_drifts':len(cmp['first_input_drifts'])})
            print('EDGE COMPARE',item['case'],cmp['status'],cmp['positions_equal'],flush=True)
        final={'status':'INCOMPLETE' if len(rows)<len(INPUTS)*2 else 'PASS',
               'rows':rows,'comparisons':allcomparisons,'scope':'Six deterministic edge fixtures; not exhaustive fuzz'}
        (opts.out/'edge_trace_report.json').write_text(json.dumps(final,indent=2))
    final['status']='PASS' if all(x['status']=='PASS' for x in rows+allcomparisons) else 'FAIL'
    (opts.out/'edge_trace_report.json').write_text(json.dumps(final,indent=2));return 0 if final['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
