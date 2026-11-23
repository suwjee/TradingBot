#!/usr/bin/env python3
"""Derive emitted (not attempted) stage counts from stable serialized native outputs.
No source or intermediate cache is touched. Missing internal counters remain null.
"""
from pathlib import Path
import json, csv
from strict_golden import stable_payload
W=Path(__file__).resolve().parents[1];OUT=W/'output'
M=json.loads((W/'tooling/inputs_verified.json').read_text())
FIELDS=['raw_file','bars','reactions','resets','blueLines','aZones','sZones','eZones','stopAlls','orderAudit','ph','pl','candidate_attempts','candidate_rejected','scanned_historical_rows','cache_hit','cache_miss','heap_ops','sorts','allocations','notes']
def extract(p,bars,name):
    obj=json.loads(stable_payload(p.read_bytes())[0]);counts={k:0 for k in ['reactions','resets','blueLines','aZones','sZones','eZones','stopAlls','orderAudit']}
    for d in ('bullish','bearish'):
        assert d in obj['directions'];body=obj['directions'][d]
        for k in counts:
            assert isinstance(body[k],list)
            counts[k]+=len(body[k])
    row={'raw_file':name,'bars':bars,**counts,'ph':None,'pl':None,'candidate_attempts':None,'candidate_rejected':None,'scanned_historical_rows':None,'cache_hit':None,'cache_miss':None,'heap_ops':None,'sorts':None,'allocations':None,'notes':'Counts are visible emitted arrays summed across both directions. No internal candidate/cache/heap/sort counters instrumented. PH/PL nested bridge not counted.'}
    return row
rows=[]
for item in M['datasets']:
    stem=Path(item['file']).stem.replace(' ','_');p=OUT/(stem+'.v81.json')
    if p.exists():rows.append(extract(p,item['records'],item['file']))
for n in (100000,250000,500000,1000000):
    p=OUT/f'synthetic_{n}_v81.json'
    if p.exists() and p.stat().st_size>1024:rows.append(extract(p,n,p.name))
with (OUT/'V9_EMITTED_STAGE_COUNTS.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
(OUT/'V9_EMITTED_STAGE_COUNTS.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
print('recorded',len(rows),'full native output stage counts')
