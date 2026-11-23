#!/usr/bin/env python3
"""Unified honest stage-emission and CPU/RSS snapshots, NOT invented internal operation counters."""
import csv,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];O=W/'output'
real=json.loads((O/'V9_REAL_PARITY.json').read_text());sy=json.loads((O/'V9_SYNTHETIC_PARITY.json').read_text())
counts=json.loads((O/'V9_EMITTED_STAGE_COUNTS.json').read_text())
ct={x['raw_file']:x for x in counts}
rows=[]
for rec in real:
 k=rec['raw_file'];d={'record_type':'real_5s','source_variant':'V8.1','verified_against':'pinned original Golden output','profile_instrumentation':'OFF','notes':'Full input, native BOTH, sampled CPU/RSS. '+rec['notes'],**rec}
 d.update({a:b for a,b in ct.get(k,{}).items() if a not in d})
 rows.append(d)
for rec in sy:
 for tag in ('baseline','candidate'):
  k=f"synthetic_{rec['bars']}_v81.json";ident='original' if tag=='baseline' else 'V8.1'
  d={'record_type':'synthetic_5s','source_variant':ident,'verified_against':'full native other source same input','profile_instrumentation':'OFF',
     'raw_file':f'SYNTHETIC_5S_{rec["bars"]}_seed{rec["seed"]}.json','raw_sha256':rec['raw_sha256'],'bars':rec['bars'],
     'source_commit':'01d54ecf0149ebd15de92798be18810b6e2eb791','previous_version':'V8.1','candidate_version':'V9-TOOLING/no-engine-change',
     'timeframe_s':30,'raw_timeframe_s':5,'direction':'both',
     'output_stable_sha256':rec['baseline_output_sha256'] if tag=='baseline' else rec['candidate_output_sha256'],
     'golden_stable_sha256':rec['baseline_output_sha256'],'stable_bytes_equal':rec['parity'],'trace_equal':None,
     'timing_schema_equal':rec['parity'],'wall_s':rec[f'{tag}_wall_s'],'cpu_s':rec[f'{tag}_cpu_s'],
     'peak_rss_mib':rec[f'{tag}_rss'],'exit_code':rec[f'{tag}_exit'],'status':rec['status'],
     'first_diff_location':None,'notes':'Synthetic generator; unprofiled full native; one single run per variant; no stage-level internal counters.'}
  d.update({a:b for a,b in ct.get(k,{}).items() if a not in d})
  rows.append(d)
keys=list(dict.fromkeys(k for row in rows for k in row))
with (O/'V9_PROFILING.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
(O/'V9_PROFILING_SCHEMA.json').write_text(json.dumps({'rows':len(rows),'real_native_v81':len(real),'synthetic_two_sources':2*len(sy),
 'null_internal_op_fields':['candidate_attempts','candidate_rejected','scanned_historical_rows','cache_hit','cache_miss','heap_ops','sorts','allocations'],
 'counts':'visible emitted arrays in final serialized payload, summed for two native directions; not internal attempted calls',
 'cpu':'per-process psutil sample; can slightly undercount','rss':'sampled peak, lower bound'},indent=2))
print('Unified complete profiling rows:',len(rows),'real:',len(real),'synthetic:',2*len(sy))
