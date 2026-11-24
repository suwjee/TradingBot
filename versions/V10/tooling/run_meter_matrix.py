import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
from strict_golden import stable_payload
p=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--cases',nargs='+',type=int,required=True);ap.add_argument('--tooling',type=Path,required=True);ap.add_argument('--engine',type=Path,required=True);ap.add_argument('--golden-dir',type=Path,required=True);ap.add_argument('--raw-dir',type=Path,required=True);a=ap.parse_args()
for n in a.cases:
 c=a.tooling/f'case-{n}.json';case=json.loads(c.read_text());out=p/str(n);out.mkdir(exist_ok=False);raw=a.raw_dir/case['name'];gold=a.golden_dir/(Path(case['name']).stem.replace(' ','_')+'.stable.json')
 cmd=[sys.executable,'-B',str(p/'v10_query_meter.py'),'--engine-root',str(a.engine),'--raw',str(raw),'--case',str(c),'--report',str(out/'report.json')]
 with (out/'native.json').open('wb') as f,(out/'stderr.log').open('wb') as err:rc=subprocess.run(cmd,stdout=f,stderr=err,env={**os.environ,'PYTHONPATH':str(a.tooling),'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'}).returncode
 if rc:raise RuntimeError((n,rc,(out/'stderr.log').read_text()[-4000:]))
 stable,schema=stable_payload((out/'native.json').read_bytes());ref=gold.read_bytes();r=json.loads((out/'report.json').read_text());r.update(golden_bytes_equal=stable==ref,golden_sha256=hashlib.sha256(ref).hexdigest(),stable_sha256=hashlib.sha256(stable).hexdigest(),timing_schema=schema,command=cmd)
 assert stable==ref and r['stable_sha256']==case['stable_output_sha256'];(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(n, r['wall_observed_s'], r['counts'].get('_compute_direct_parent_stop_order'),r['confirmation_skip_histogram'],flush=True)
