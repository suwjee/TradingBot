#!/usr/bin/env python3
"""Deterministic 5s synthetic adversarial fixtures: compare pinned original vs V8.1.
No trade rules or actual RAW bytes altered. Supported-case parity only; invalid cases explicitly NOT PASS.
"""
import hashlib,json,os,subprocess,sys,random
from pathlib import Path
from strict_golden import stable_payload
from run_real_matrix import cmd
W=Path(__file__).resolve().parents[1];O=W/'output';fixtures=O/'synthetic_edge_fixtures';fixtures.mkdir(exist_ok=True)
source=Path('/mnt/data/RAW FXCM_USOIL 5S FROM 2026-10-22 19-25-25 TO 2026-10-23 19-25-25.json')
data=json.loads(source.read_bytes())[:1100]
cases={}
cases['ordinary_prefix']=list(data)
x=[dict(r) for r in data]
for i in range(0,len(x),11):x[i]['close']=x[i]['open']
cases['doji_close_equal_open_every_11']=x
x=[dict(r) for r in data]
for i in range(0,len(x),19):x[i].update({'high':x[i]['open'],'low':x[i]['open'],'close':x[i]['open']})
cases['flat_candle_equal_extrema_every_19']=x
x=[dict(r) for i,r in enumerate(data) if (i+1)%17!=0];cases['missing_raw_times_every_17']=x
x=[dict(r) for r in data];x.insert(55,dict(x[54]));cases['duplicate_epoch_source']=x
x=[dict(r) for r in data]
for i in range(0,len(x),37):
 r=x[i];r['high']=max(r['high'],r['open'],r['close']);r['low']=min(r['low'],r['open'],r['close'])
cases['strict_boundary_unmodified_tie']=x
out=[]
for name,rows in cases.items():
 path=fixtures/(name+'.json');payload=json.dumps(rows,separators=(',',':')).encode();path.write_bytes(payload)
 item={'first_time':rows[0]['time'],'last_time':rows[-1]['time']}
 checks=[]
 for label,root in [('original',W/'golden/github_engine_commit_01d54ecf/engine'),('v81',W/'v81/engine')]:
  process=subprocess.run(cmd(root,path,item),stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'},timeout=90)
  result={'variant':label,'exit':process.returncode,'stderr_tail':process.stderr[-500:].decode(errors='replace')}
  if process.returncode==0:
   try:
    stable,schema=stable_payload(process.stdout)
    result.update(stable_sha256=hashlib.sha256(stable).hexdigest(),telemetry_schema=schema)
   except Exception as e:result.update(parsing_error=repr(e))
  checks.append(result)
 accepted=all(x['exit']==0 and 'stable_sha256' in x for x in checks)
 parity=accepted and checks[0]['stable_sha256']==checks[1]['stable_sha256'] and checks[0]['telemetry_schema']==checks[1]['telemetry_schema']
 status=('PASS' if parity else ('FAIL' if accepted else 'INCOMPLETE'))
 entry={'case':name,'raw_records':len(rows),'input_sha256':hashlib.sha256(payload).hexdigest(),'raw_source':'synthetic transformations of immutable OIL raw prefix in a separate file',
        'status':status,'parity':parity if accepted else None,'details':checks}
 out.append(entry);print(name,status,flush=True)
 (O/'V9_EDGE_CASES.json').write_text(json.dumps({'status':'PASS' if all(r['status']=='PASS' for r in out) else 'INCOMPLETE',
    'scope':'6 deterministic short synthetic input variants, not universal property-based proof','results':out},indent=2,ensure_ascii=False))
