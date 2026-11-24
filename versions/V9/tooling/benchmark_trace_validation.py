#!/usr/bin/env python3
"""Same-host ABBA benchmark of selected-trace audit, not Engine performance.

Read immutable existing traces, run each validator in a fresh subprocess and
require full report equality (including exact canonical stream hashes). The
reference tooling directory must point to the pre-optimization Git snapshot.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, statistics, subprocess, sys, time
from pathlib import Path


def run_child(mode,tooling,paths):
    code='''import json,sys,time,resource
from pathlib import Path
sys.path.insert(0,sys.argv[1]);mode=sys.argv[2];a,b=map(Path,sys.argv[3:5]);start=time.perf_counter()
if mode=='legacy':
 from audit_trace_coverage import inspect,SCHEMAS
 from strict_trace_gate_v9 import compare,SCHEMA
 from verify_streamed_stage_sidecars import audit
 SCHEMAS.add(SCHEMA)
 report={'reports':[{'integrity':inspect(p),'stage_integrity':audit(Path(str(p)+'.manifest.json'))} for p in (a,b)],'comparison':compare(a,b)}
else:
 from single_pass_trace_gate import audit_pair
 report=audit_pair(a,b)
print(json.dumps({'wall_s':time.perf_counter()-start,'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024 if sys.platform!='darwin' else 1024**2),'report':report},ensure_ascii=False))'''
    p=subprocess.run([sys.executable,'-B','-c',code,str(tooling),mode,*map(str,paths)],check=True,capture_output=True,text=True,env={**os.environ,'PYTHONHASHSEED':'0'})
    return json.loads(p.stdout)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('candidate',type=Path);p.add_argument('--reference-tooling',type=Path,required=True);p.add_argument('--blocks',type=int,default=3);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.blocks<1:raise ValueError('at least one complete ABBA block')
    paths=[a.original.resolve(),a.candidate.resolve()]; rows=[]; reference=None
    manifests=[Path(str(path)+'.manifest.json') for path in paths]
    # Pin every file referred to by either trace manifest before/after, not only main streams.
    from safe_sidecar import sidecar_path
    files=set(paths+manifests)
    for m in manifests:
        meta=json.loads(m.read_text())
        for key,field in [('chronology_input_sidecars','sidecar'),('ordered_collection_sidecars','file'),('ordered_stage_output_sidecars','file')]:
            files.update(sidecar_path(m.parent,x[field]) for x in meta.get(key,[]))
    def hashes():
        result={}
        for f in sorted(files):
            with f.open('rb') as s:result[str(f)]=hashlib.file_digest(s,'sha256').hexdigest()
        return result
    before=hashes()
    for block in range(a.blocks):
        for mode in ('legacy','fused','fused','legacy'):
            r=run_child(mode,a.reference_tooling.resolve() if mode=='legacy' else Path(__file__).resolve().parent,paths)
            report=r.pop('report'); canonical=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
            if reference is None:reference=canonical; reference_report=report
            elif canonical!=reference:raise AssertionError('Full audit/comparator report diverged')
            rows.append({'block':block+1,'mode':mode,**r});print(block+1,mode,r,flush=True)
    if hashes()!=before:raise AssertionError('Trace input bytes changed')
    med={m:statistics.median(x['wall_s'] for x in rows if x['mode']==m) for m in ('legacy','fused')}
    result={'status':'PASS','scope':'post-capture validation only; same frozen input files, full report equality; not a native Engine speedup','host':platform.platform(),'python':sys.version,'blocks':a.blocks,'runs':rows,'median_wall_s':med,'time_reduction_pct':(1-med['fused']/med['legacy'])*100,'speedup_ratio':med['legacy']/med['fused'],'input_hashes':before,'report_sha256':hashlib.sha256(reference).hexdigest(),'comparison':reference_report['comparison'],'audited_sidecars':[x['stage_integrity']['checked_stage_sidecars'] for x in reference_report['reports']]}
    a.out.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
