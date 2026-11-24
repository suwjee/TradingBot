#!/usr/bin/env python3
"""Repeated separate-host-paired native BOTH 30/5 RAW baseline verification.

Two smallest and two largest original 5s RAW datasets, full historical range.
Unprofiled ABBA/BAAB blocks. No speedup is attributed to V9 itself.
"""
from __future__ import annotations
import argparse,json,os,statistics,subprocess,sys,time
from pathlib import Path
import psutil
BASE=Path('/mnt/data/V9_work')
sys.path.insert(0,str(BASE/'tooling'))
from strict_golden import stable_payload,sha256,stable_match
from run_real_matrix import cmd
ORIGINAL={'original':BASE/'golden/github_engine_commit_01d54ecf/engine',
          'v81':BASE/'v81/engine'}
RAW=json.loads((BASE/'tooling/inputs_verified.json').read_text())['datasets']
BASELINE=BASE/'golden/runs/github_baseline'

def one(item,variant,out,n):
    raw=Path('/mnt/data')/item['file'];prefix=out/(f'{n:03d}_{variant}')
    now=time.perf_counter_ns();peak_cpu=0.;peak_rss=0
    with Path(str(prefix)+'.json').open('wb') as stream, Path(str(prefix)+'.stderr.log').open('wb') as err:
        p=subprocess.Popen(cmd(ORIGINAL[variant],raw,item),stdout=stream,stderr=err,
                           env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1'})
        proc=psutil.Process(p.pid)
        while p.poll() is None:
            try:peak_cpu=max(peak_cpu,sum(proc.cpu_times()[:2]));peak_rss=max(peak_rss,proc.memory_info().rss)
            except psutil.NoSuchProcess:break
            time.sleep(.025)
        rc=p.wait()
    if rc:raise RuntimeError('Nonzero native CLI '+str(rc)+': '+Path(str(prefix)+'.stderr.log').read_text()[-800:])
    stem=raw.stem.replace(' ','_');contract=json.loads((BASELINE/(stem+'.metrics.json')).read_text())
    compare=stable_match((BASELINE/(stem+'.json')).read_bytes(),Path(str(prefix)+'.json').read_bytes(),contract)
    if not(compare['bytes_equal'] and compare['timing_schema_equal']):
        raise AssertionError('Golden stable byte/timing schema mismatch: '+str(compare))
    return {'ordinal':n,'dataset':item['id'],'bars':item['records'],'variant':variant,
            'wall_s':round((time.perf_counter_ns()-now)/1e9,5),
            'cpu_s':round(peak_cpu,4),'sampled_peak_rss_mib':round(peak_rss/2**20,4),
            'stable_sha256':compare['candidate_stable_sha256'],'golden_stable_pass':True,
            'telemetry_contract_pass':True,'source':'fresh independent unprofiled native BOTH 30/5'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--indices',default='5,2,3,6');ap.add_argument('--blocks',type=int,default=3)
    opts=ap.parse_args();opts.out.mkdir(parents=True,exist_ok=True)
    all_reports=[]
    # Strongly validated inputs; no artificial subranges, no reaggregation.
    indices=[int(n) for n in opts.indices.split(',')]
    for index in indices:
        item=RAW[index];raw=Path('/mnt/data')/item['file']
        assert sha256(raw.read_bytes())==item['raw_sha256']
        dirname=opts.out/item['id'];dirname.mkdir(parents=True,exist_ok=True)
        schedule=[]
        for b in range(opts.blocks):schedule += (['original','v81','v81','original'] if b%2==0 else ['v81','original','original','v81'])
        rows=[];report_path=dirname/'paired_report.json'
        for i,variant in enumerate(schedule):
            print('START',item['id'],i,variant,flush=True)
            try:row=one(item,variant,dirname,i)
            except Exception as exc:
                row={'ordinal':i,'variant':variant,'status':'FAIL','error':repr(exc)}
                rows.append(row);report_path.write_text(json.dumps({'status':'FAIL','rows':rows},indent=2))
                return 1
            row['status']='PASS';rows.append(row)
            report_path.write_text(json.dumps({'status':'INCOMPLETE' if len(rows)<len(schedule) else 'PASS',
                                             'rows':rows,'scheduled':len(schedule),'completed':len(rows)},indent=2))
            print('END',item['id'],i,variant,row['wall_s'],'PASS',flush=True)
        a=[r['wall_s'] for r in rows if r['variant']=='original'];b=[r['wall_s'] for r in rows if r['variant']=='v81']
        report={'status':'PASS','id':item['id'],'rows':rows,'blocks':opts.blocks,
                'median_original':statistics.median(a),'median_v81':statistics.median(b),
                'observed_speed_ratio':statistics.median(a)/statistics.median(b),
                'warning':'Observational paired baseline, NOT a V9 performance optimization'}
        report_path.write_text(json.dumps(report,indent=2));all_reports.append(report)
        (opts.out/'aggregate.json').write_text(json.dumps({'status':'INCOMPLETE','completed_datasets':len(all_reports),
                                                      'scheduled_datasets':len(indices),'datasets':all_reports},indent=2))
    (opts.out/'aggregate.json').write_text(json.dumps({'status':'PASS','completed_datasets':len(all_reports),
                                                    'scheduled_datasets':len(indices),'datasets':all_reports},indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
