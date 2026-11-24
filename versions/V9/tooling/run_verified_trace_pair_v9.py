#!/usr/bin/env python3
"""Portable, sequential, fail-closed V9 selected-trace pair runner.

The case manifest pins RAW bytes and Original/V8.1 source files. No production
source is written. No test is declared complete before process exit and audit.
No artificial calculation timeout. The full semantic-state gate remains open.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path
import psutil
from strict_golden import stable_payload
from strict_trace_gate_v9 import compare
from audit_trace_coverage import inspect, SCHEMAS
from verify_streamed_stage_sidecars import audit as audit_stage
SCHEMAS.add('tradingbot.v9.internal-observer.v9')
HERE=Path(__file__).resolve().parent

def hash_file(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def source_check(path, expected):
    observed={p.relative_to(path).as_posix():hash_file(p)
              for package in ('bridge','pipeline')
              for p in (path/package).rglob('*.py')}
    if observed!=expected:raise ValueError('Source SHA manifest mismatch: '+str(path))
    return len(observed)

def write(path, obj):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2)+'\n');tmp.replace(path)

def run(raw, root, variant, case, out):
    if source_check(root,case['source_sha256'][variant])!=15:raise ValueError('Expected 15 runtime modules')
    stem=out/variant; trace=Path(str(stem)+'.trace.jsonl.gz'); manifest=Path(str(trace)+'.manifest.json')
    native=Path(str(stem)+'.native.json'); profile=Path(str(stem)+'.profile.json')
    cmd=[sys.executable,'-B',str(HERE/'semantic_trace_v9.py'),'--engine-root',str(root),
         '--raw',str(raw),'--from-time',str(case['first_time']),'--to-time',str(case['last_time']),
         '--trace-out',str(trace),'--summary',str(manifest),'--stage-profile',str(profile)]
    start=time.perf_counter();cpu=0.0;rss=0
    with native.open('wb') as fo,Path(str(stem)+'.stderr.log').open('wb') as fe:
        proc=subprocess.Popen(cmd,stdout=fo,stderr=fe,env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'})
        try:
            p=psutil.Process(proc.pid)
            while proc.poll() is None:
                try:
                    c=p.cpu_times();cpu=max(cpu,c.user+c.system);rss=max(rss,p.memory_info().rss)
                except psutil.NoSuchProcess:break
                time.sleep(.05)
            rc=proc.wait()
        except BaseException:
            proc.terminate();proc.wait();raise
    if rc:raise RuntimeError(f'{variant}: process exit {rc}; inspect stderr')
    wall=time.perf_counter()-start
    stable,schema=stable_payload(native.read_bytes()); sha=hashlib.sha256(stable).hexdigest()
    if sha!=case['stable_output_sha256']:raise AssertionError('Golden stable hash mismatch: '+variant)
    if source_check(root,case['source_sha256'][variant])!=15 or hash_file(raw)!=case['raw_sha256']:
        raise AssertionError('Source/RAW changed during run')
    integrity=inspect(trace); stages=audit_stage(manifest)
    if integrity['integrity']!='PASS' or integrity['missing_required'] or stages['status']!='PASS_INTEGRITY_ONLY':
        raise AssertionError('Trace integrity or required fields failure: '+variant)
    write(Path(str(stem)+'.integrity.json'),integrity);write(Path(str(stem)+'.stage_integrity.json'),stages)
    return {'variant':variant,'native_exit':rc,'stable_sha256':sha,'timing_schema':schema,
            'wall_observer_on_s':wall,'sampled_cpu_s':cpu,'sampled_peak_rss_mib':rss/2**20,
            'events':integrity['raw_events'],'trace_sha256':hash_file(trace),'integrity':'PASS',
            'stage_sidecars':stages['checked_stage_sidecars'],'stage_profile':profile.name}

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--raw',type=Path,required=True);p.add_argument('--original-engine',type=Path,required=True);p.add_argument('--v81-engine',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    raw=a.raw.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    if any(out.iterdir()):raise ValueError('Output directory must be empty; preserve evidence from prior runs')
    case=json.loads(a.case.read_text());r={'status':'INCOMPLETE','full_semantic_state_status':'INCOMPLETE','case':case['name'],'rows':[]}
    dest=out/'pair_report.json';write(dest,r)
    try:
        if hash_file(raw)!=case['raw_sha256']:raise ValueError('RAW SHA mismatch')
        # Count and range from pinned manifest; full input hash prevents prefix substitution.
        for variant,root in [('original',a.original_engine.resolve()),('v81',a.v81_engine.resolve())]:
            print('START',variant,case['name'],flush=True);row=run(raw,root,variant,case,out);r['rows'].append(row);write(dest,r);print('END',variant,row['events'],flush=True)
        if r['rows'][0]['timing_schema']!=r['rows'][1]['timing_schema']:raise AssertionError('Timing schema mismatch')
        c=compare(out/'original.trace.jsonl.gz',out/'v81.trace.jsonl.gz');write(out/'strict_comparison.json',c)
        r['stable_output_status']='PASS';r['selected_event_status']=c['selected_event_status'];r['status']='FAIL' if c['selected_event_status']=='FAIL' else 'INCOMPLETE'
        r['reason']='Selected events do not establish all semantic mutations/Live state.';write(dest,r)
        return 1 if r['status']=='FAIL' else 2
    except (Exception,KeyboardInterrupt) as exc:
        r['status']='INCOMPLETE' if isinstance(exc,(KeyboardInterrupt,RuntimeError,OSError)) else 'FAIL';r['error']=repr(exc);write(dest,r);raise
if __name__=='__main__':raise SystemExit(main())
