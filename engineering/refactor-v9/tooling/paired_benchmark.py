#!/usr/bin/env python3
"""Unprofiled ABBA runner with pinned native BOTH parity and CPU/RSS sampling.

No speedup certification from fewer than 3 completed ABBA blocks at 1M.
"""
import argparse,hashlib,json,os,psutil,statistics,subprocess,sys,time
from pathlib import Path
BASE=Path('/mnt/data/V9_work')
sys.path.insert(0,str(BASE/'tooling'))
from strict_golden import sha256,stable_payload
from run_real_matrix import cmd
ROOTS={'original':BASE/'golden/github_engine_commit_01d54ecf/engine','v81':BASE/'v81/engine'}
INPUTS=json.loads((BASE/'output/V9_SYNTHETIC_INPUTS.json').read_text())

def run(tag, item, dest, ordinal):
    raw=Path(item['file']);target=Path(dest)/(f'{ordinal:03d}_{tag}')
    command=cmd(ROOTS[tag].resolve(),raw.resolve(),item)
    t=time.perf_counter_ns();cpu=0;rss=0
    with Path(str(target)+'.json').open('wb') as output,Path(str(target)+'.stderr.log').open('wb') as err:
        proc=subprocess.Popen(command,stdout=output,stderr=err,
               env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1'})
        ph=psutil.Process(proc.pid)
        while proc.poll() is None:
            try:
                cpu=max(cpu,sum(ph.cpu_times()[:2]));rss=max(rss,ph.memory_info().rss)
            except psutil.NoSuchProcess:break
            time.sleep(.025)
        rc=proc.wait()
    wall=(time.perf_counter_ns()-t)/1e9
    if rc:raise RuntimeError('Engine error '+str(rc)+' '+str(target))
    stable,schema=stable_payload(Path(str(target)+'.json').read_bytes())
    return {'variant':tag,'ordinal':ordinal,'wall_s':wall,'cpu_s':cpu,'peak_rss_mib':rss/1048576,
           'stable_sha256':sha256(stable),'stable_schema':schema,'exit_code':rc,
           'output':str(target)+'.json'}

def run_blocks(item,blocks,dest):
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
    if sha256(Path(item['file']).read_bytes())!=item['raw_sha256']:raise AssertionError('synthetic raw sha mismatch')
    results=[];summaryfile=dest/'paired_report.json'
    schedule=['original','v81','v81','original']*blocks
    for i,tag in enumerate(schedule):
        print('START',i,tag,item['bars'],flush=True)
        r=run(tag,item,dest,i)
        baseline_sha=results[0]['stable_sha256'] if results else r['stable_sha256']
        baseline_schema=results[0]['stable_schema'] if results else r['stable_schema']
        r['stable_equal_to_original']=r['stable_sha256']==baseline_sha and r['stable_schema']==baseline_schema
        if not r['stable_equal_to_original']:raise AssertionError('exact stable bytes or schema drift at '+str(i))
        results.append(r)
        summaryfile.write_text(json.dumps({'scope':'unprofiled native BOTH 30/5','status':'INCOMPLETE' if i+1<len(schedule) else 'PASS',
                        'scale':item['bars'],'completed':i+1,'scheduled':len(schedule),'runs':results},indent=2))
        print('COMPLETE',i,tag,round(r['wall_s'],3),'stable_equal',r['stable_equal_to_original'],flush=True)
    originals=[r['wall_s'] for r in results if r['variant']=='original']
    candidates=[r['wall_s'] for r in results if r['variant']=='v81']
    out={'scope':'unprofiled native 30s BOTH, one paired host environment','status':'PASS',
         'scale':item['bars'],'blocks':blocks,'runs':results,
         'median_original_wall_s':statistics.median(originals),
         'median_v81_wall_s':statistics.median(candidates),
         'median_speed_ratio':statistics.median(originals)/statistics.median(candidates),
         'repeated_1m_gate_met':item['bars']==1000000 and blocks>=3,
         'non_claim':'No V9 speedup: same frozen V8.1 compared to immutable original.'}
    summaryfile.write_text(json.dumps(out,indent=2))
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bars',type=int,required=True);p.add_argument('--blocks',type=int,default=1);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();item=next(x for x in INPUTS if x['bars']==args.bars)
    r=run_blocks(item,args.blocks,args.out);print('FINAL',r['status'],r['median_speed_ratio'])
