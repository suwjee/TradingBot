#!/usr/bin/env python3
"""Reconstruct OUTPUT-STAGE boundary traces from both frozen original and untouched V8.1 runs."""
import json,hashlib
from pathlib import Path
from trace_boundary import record
W=Path(__file__).resolve().parents[1];OUT=W/'output';REF=W/'golden/runs/github_baseline';M=json.loads((W/'tooling/inputs_verified.json').read_text());T=OUT/'stage_boundary_traces';T.mkdir(exist_ok=True)
rows=[]
for i,item in enumerate(M['datasets']):
 stem=Path(item['file']).stem.replace(' ','_');ref=REF/(stem+'.json');cand=OUT/(stem+'.v81.json')
 r={'raw_file':item['file'],'raw_sha256':item['raw_sha256'],'coverage':'STAGE_BOUNDARY_ONLY','event_trace_internal':'NOT RUN',
    'boundary_events':0,'boundary_equal':None,'status':'INCOMPLETE'}
 if not cand.exists():r['notes']='V8.1 latest run missing';rows.append(r);continue
 before=(hashlib.sha256(ref.read_bytes()).hexdigest(),hashlib.sha256(cand.read_bytes()).hexdigest())
 for tag,path in [('original',ref),('v81',cand)]:
  trace=T/f'{stem}.{tag}.jsonl.gz';m=record(path,trace);r[tag+'_trace_sha256']=m['jsonl_sha256'];r[tag+'_events']=m['count'];r[tag+'_compressed_sha256']=m['gzip_sha256']
 after=(hashlib.sha256(ref.read_bytes()).hexdigest(),hashlib.sha256(cand.read_bytes()).hexdigest())
 r.update({'boundary_equal':r['original_trace_sha256']==r['v81_trace_sha256'] and r['original_events']==r['v81_events'],
           'boundary_events':r['original_events'],'source_bytes_unchanged_by_tracer':before==after})
 r['status']='PASS' if r['boundary_equal'] and r['source_bytes_unchanged_by_tracer'] else 'FAIL'
 rows.append(r)
 (OUT/'V9_TRACE_COVERAGE.json').write_text(json.dumps({'scope':'Stage-boundary snapshots only. No full-event pre/post state transition capture.',
   'coverage_status':'TRACE_COVERAGE_PARTIAL','rows':rows,'all_boundary_pass':len(rows)==7 and all(x['status']=='PASS' for x in rows)},indent=2,ensure_ascii=False))
 print(item['file'][:43],r['boundary_events'],r['status'],flush=True)
