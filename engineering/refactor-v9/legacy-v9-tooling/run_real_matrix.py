#!/usr/bin/env python3
"""Native 30S/BOTH full RAW verifications; independent psutil sampled CPU and RSS."""
import csv,json,os,subprocess,sys,time,hashlib,psutil
from pathlib import Path
from strict_golden import stable_payload,sha256,stable_match
W=Path(__file__).resolve().parents[1]
ROOT=W/'v81/engine';REF=W/'golden/runs/github_baseline';OUT=W/'output';OUT.mkdir(exist_ok=True)
M=json.loads((W/'tooling/inputs_verified.json').read_text())
FIELDS=['raw_file','raw_sha256','bars','source_commit','previous_version','candidate_version','timeframe_s','raw_timeframe_s','direction','output_stable_sha256','golden_stable_sha256','stable_bytes_equal','trace_equal','timing_schema_equal','wall_s','cpu_s','peak_rss_mib','exit_code','status','first_diff_location','notes']
def cmd(root,f,item):
 p=root/'pipeline';args=[sys.executable,'-B',str(root/'bridge/trading_pipeline.py')]
 for flag,file in [('reaction-engine','reaction_engine.py'),('blue-line-engine','blue_line_detector.py'),('a-zone-engine','a_zone_detector.py'),('s-zone-engine','s_zone_detector.py'),('e-zone-engine','e_zone_detector.py'),('lifecycle-engine','lifecycle_engine.py')]:args+=['--'+flag,str(p/file)]
 args+=['--data',str(f),'--timeframe','30','--raw-timeframe','5','--direction','both','--from-time',str(item['first_time']),'--to-time',str(item['last_time']),'--blue-lines','enabled','--a-zones','enabled','--s-zones','enabled','--pl-ph','enabled','--bridge-output']
 return args

def run(item,root=ROOT,tag='v81',sample_ms=25,profile=False):
 f=Path('/mnt/data')/item['file'];stem=f.stem.replace(' ','_');prefix=OUT/(stem+'.'+tag)
 r={k:None for k in FIELDS};r.update({'raw_file':f.name,'raw_sha256':item['raw_sha256'],'bars':item['records'],'source_commit':M['baseline_git_commit'],
 'previous_version':'V8.1','candidate_version':'V9-TOOLING/unchanged-V8.1','timeframe_s':30,'raw_timeframe_s':5,'direction':'both',
 'trace_equal':None,'status':'INCOMPLETE','notes':''})
 if not f.is_file() or sha256(f.read_bytes())!=item['raw_sha256']:r.update(status='FAIL',notes='missing or corrupted RAW');return r
 command=cmd(root.resolve(),f.resolve(),item)
 if profile:command=command[:2]+['-m','cProfile','-o',str(prefix)+'.pstats']+command[2:]
 out=Path(str(prefix)+'.json');err=Path(str(prefix)+'.stderr.log')
 start=time.perf_counter_ns();cpu=0;rss=0;polls=0
 with out.open('wb') as fout,err.open('wb') as ferr:
  proc=subprocess.Popen(command,stdout=fout,stderr=ferr,env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'})
  ps=psutil.Process(proc.pid)
  while proc.poll() is None:
   try:
    c=ps.cpu_times();cpu=max(cpu,c.user+c.system)
    rss=max(rss,ps.memory_info().rss);polls+=1
   except psutil.NoSuchProcess:break
   time.sleep(sample_ms/1000)
  exitcode=proc.wait()
 wall=(time.perf_counter_ns()-start)/1e9
 r.update({'wall_s':round(wall,6),'cpu_s':round(cpu,6),'peak_rss_mib':round(rss/2**20,3),'exit_code':exitcode,'notes':'sampled CPU/RSS 25ms; cProfile ON' if profile else 'sampled CPU/RSS 25ms; native unprofiled'})
 if exitcode!=0:r.update(status='FAIL',notes=r['notes']+'; ENGINE EXIT '+str(exitcode));return r
 try:
  reference=REF/(stem+'.json');metrics=json.loads((REF/(stem+'.metrics.json')).read_text())
  result=stable_match(reference.read_bytes(),out.read_bytes(),metrics)
  r.update({'output_stable_sha256':result['candidate_stable_sha256'],'golden_stable_sha256':result['golden_stable_sha256'],
  'stable_bytes_equal':result['bytes_equal'],'timing_schema_equal':result['timing_schema_equal'],
  'first_diff_location':result['first_diff_byte'],'status':'PASS' if result['bytes_equal'] and result['timing_schema_equal'] and result['golden_stable_sha256']==item['stable_output_sha256'] else 'FAIL'})
  obj=json.loads(out.read_bytes())
  Path(str(prefix)+'.stage_timings.json').write_text(json.dumps(obj['timings'],indent=2))
 except Exception as e:r.update(status='FAIL',notes=r['notes']+'; '+repr(e))
 return r

def save(rows):
 (OUT/'V9_REAL_PARITY.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
 with (OUT/'V9_PROFILING.csv').open('w',newline='',encoding='utf8') as fp:
  w=csv.DictWriter(fp,fieldnames=FIELDS);w.writeheader();w.writerows(rows)

if __name__=='__main__':
 a=sys.argv[1:];target=a[0] if a else 'ALL';sample='profile' in a;rows=[]
 for item in M['datasets']:
  if target not in ('ALL',item['id']):continue
  row=run(item,profile=sample,tag='v81profile' if sample else 'v81')
  rows.append(row);save(rows)
  print(json.dumps({'id':item['id'],'status':row['status'],'wall_s':row['wall_s'],'rss_mib':row['peak_rss_mib'],'equal':row['stable_bytes_equal']},ensure_ascii=False),flush=True)
 if any(x['status']!='PASS' for x in rows):sys.exit(1)
