#!/usr/bin/env python3
"""Original pinned source and unmodified V8.1: native BOTH, no early stop/warm-up truncation."""
import csv,hashlib,json,os,psutil,subprocess,sys,time
from pathlib import Path
from strict_golden import stable_payload,sha256
from run_real_matrix import cmd
W=Path(__file__).resolve().parents[1];OUT=W/'output';S=json.loads((OUT/'V9_SYNTHETIC_INPUTS.json').read_text())
ref=W/'golden/github_engine_commit_01d54ecf/engine';v81=W/'v81/engine'
fields=['generator_sha256','seed','bars','raw_sha256','baseline_output_sha256','candidate_output_sha256','baseline_wall_s','candidate_wall_s','baseline_cpu_s','candidate_cpu_s','baseline_rss','candidate_rss','parity','baseline_exit','candidate_exit','status','notes']

def execute(item,root,tag):
 f=Path(item['file']);prefix=OUT/f'synthetic_{item["bars"]}_{tag}'
 m={'first_time':item['first_time'],'last_time':item['last_time']}
 argv=cmd(root,f,m)
 start=time.perf_counter();rss=0;cpu=0
 with Path(str(prefix)+'.json').open('wb') as out,Path(str(prefix)+'.stderr.log').open('wb') as err:
  p=subprocess.Popen(argv,stdout=out,stderr=err,env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'})
  ph=psutil.Process(p.pid)
  while p.poll() is None:
   try:
    cpu=max(cpu,sum(ph.cpu_times()[:2]));rss=max(rss,ph.memory_info().rss)
   except psutil.NoSuchProcess:break
   time.sleep(0.04)
  exit_code=p.wait()
 secs=time.perf_counter()-start
 print(json.dumps({'bars':item['bars'],'variant':tag,'seconds':round(secs,3),'exit':exit_code,'rss_mib':round(rss/1048576,1)}),flush=True)
 return {'wall':round(secs,4),'cpu':round(cpu,4),'rss':round(rss/1048576,3),'exit':exit_code,'out':str(prefix)+'.json'}

def save(rows):
 (OUT/'V9_SYNTHETIC_PARITY.json').write_text(json.dumps(rows,indent=2))
 with (OUT/'V9_SYNTHETIC_PROFILING.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

if __name__=='__main__':
 requested=set(int(x) for x in sys.argv[1:]) if len(sys.argv)>1 else {x['bars'] for x in S}
 rows=[]
 for item in S:
  if item['bars'] not in requested:continue
  row={k:None for k in fields};row.update({k:item[k] for k in ('seed','bars','raw_sha256','generator_sha256')});row.update(status='INCOMPLETE',notes='Native 30S/BOTH all stages; one unprofiled run per source; 40ms RSS sampling')
  try:
   if sha256(Path(item['file']).read_bytes())!=item['raw_sha256']:raise ValueError('Synthetic RAW SHA mismatch')
   rb=execute(item,ref,'original');row.update({'baseline_wall_s':rb['wall'],'baseline_cpu_s':rb['cpu'],'baseline_rss':rb['rss'],'baseline_exit':rb['exit']})
   if rb['exit']!=0:raise ValueError('Golden original subprocess failed')
   gold,_=stable_payload(Path(rb['out']).read_bytes());row['baseline_output_sha256']=sha256(gold)
   rc=execute(item,v81,'v81');row.update({'candidate_wall_s':rc['wall'],'candidate_cpu_s':rc['cpu'],'candidate_rss':rc['rss'],'candidate_exit':rc['exit']})
   if rc['exit']!=0:raise ValueError('V8.1 subprocess failed')
   cand,_=stable_payload(Path(rc['out']).read_bytes());row['candidate_output_sha256']=sha256(cand)
   refschema=stable_payload(Path(rb['out']).read_bytes())[1];candschema=stable_payload(Path(rc['out']).read_bytes())[1]
   row.update({'parity':cand==gold and candschema==refschema,'status':'PASS' if cand==gold and candschema==refschema else 'FAIL'})
  except Exception as e:row.update(status='FAIL',notes=row['notes']+'; '+repr(e))
  rows.append(row);save(rows)
  print(json.dumps({'bars':item['bars'],'status':row['status'],'parity':row['parity']}),flush=True)
 if any(x['status']!='PASS' for x in rows):sys.exit(1)
