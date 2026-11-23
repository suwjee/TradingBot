#!/usr/bin/env python3
"""Extract prefixes from archived deterministic synthetic 1M without modifying the original file."""
from pathlib import Path
import json,hashlib
W=Path(__file__).resolve().parents[1]
base=W/'synthetic/synthetic_RAW/SYNTHETIC_XAUUSD_5S_1M_seed20261123.json'
raw=base.read_bytes();assert raw[:1]==b'[' and raw[-1:]==b']'
expected='e121e42430cb72800677e55e1412069af3edef1f336ae0ecdc414642936cf60b'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)==expected
seed=20261123
source=W/'synthetic/generate_synthetic_1m.py'
meta=[];at=0
for n in [100_000,250_000,500_000]:
 while at<n:
  # delimiter marks the end of each flat object; no nested JSON in this generator
  if at==0: cur=raw.find(b'},{',1)
  else: cur=raw.find(b'},{',cur+3)
  if cur<0:raise ValueError(f'Premature EOF row={at}')
  at+=1
  if at==n:break
 # cur is the ending } of row n and separator ,{; prefix includes } then ].
 blob=raw[:cur+1]+b']'
 path=W/'synthetic'/f'SYNTHETIC_XAUUSD_5S_{n}_seed20261123.json'
 path.write_bytes(blob)
 a=json.loads(blob);assert len(a)==n
 meta.append({'bars':n,'file':str(path),'raw_sha256':sha(blob),'first_time':a[0]['time'],'last_time':a[-1]['time'],'seed':seed,'generator_sha256':sha(source.read_bytes())})
 print(n,len(blob),sha(blob),flush=True)
# Full synthetic remains original and immutable.
meta.append({'bars':1_000_000,'file':str(base),'raw_sha256':sha(raw),'first_time':1767225600,
             'last_time':json.loads(raw[raw.rfind(b'{'): -1])['time'],'seed':seed,'generator_sha256':sha(source.read_bytes())})
(W/'output/V9_SYNTHETIC_INPUTS.json').write_text(json.dumps(meta,indent=2));print('ALL READY',flush=True)
