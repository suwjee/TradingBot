"""Execute immutable packaged engine unchanged and preserve complete evidence."""
from pathlib import Path
import argparse, gzip, hashlib, json, subprocess, sys, time

OUT=Path(__file__).resolve().parent
STAGES=('reactions','resets','blueLines','aZones','sZones','eZones','stopAlls','orderAudit','bridgeOutput')

def command(raw,tf,first,last,direction='both'):
    engine=OUT/'package'
    result=[sys.executable,'-B',str(engine/'bridge/trading_pipeline.py')]
    for flag,name in [('engine','reaction_engine'),('blue-engine','blue_line_detector'),
                      ('a-engine','a_zone_detector'),('s-engine','s_zone_detector'),
                      ('e-engine','e_zone_detector'),('stopall-engine','lifecycle_engine')]:
        result += ['--'+flag,str(engine/'pipeline'/f'{name}.py')]
    return result+['--data',str(raw),'--timeframe',str(tf),'--from-time',str(first),
                  '--to-time',str(last),'--direction',direction,'--bridge-output']

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--indices',default='all')
    parser.add_argument('--timeframes',default='30')
    parser.add_argument('--label',default='raw-matrix')
    parser.add_argument('--repeat',type=int,default=1)
    parser.add_argument('--registry',default='raw-registry.json')
    args=parser.parse_args()
    registry=json.loads((OUT/args.registry).read_text(encoding='utf-8'))
    selected=list(range(len(registry))) if args.indices=='all' else [int(x) for x in args.indices.split(',')]
    target=OUT/args.label
    target.mkdir(exist_ok=True)
    records=[]
    manifest=target/'manifest.json'
    for i in selected:
      raw=registry[i]
      for tf in map(int,args.timeframes.split(',')):
       prior=None
       for repeat in range(args.repeat):
        name=f'raw-{i:02d}-{tf}s-{repeat+1}'
        cmd=command(Path(raw['path']),tf,raw['first'],raw['last'])
        record={'name':name,'rawIndex':i,'rawPath':raw['path'],'rawSha256':raw['sha256'],
                'rawRows':raw['rows'],'timeframe':tf,'direction':'both','command':cmd,'status':'INCOMPLETE'}
        records.append(record)
        manifest.write_text(json.dumps(records,indent=2),encoding='utf-8')
        print(f'START {name} rows={raw["rows"]}',flush=True)
        started=time.perf_counter()
        stdout=target/(name+'.stdout.json')
        with stdout.open('wb') as output,(target/(name+'.stderr.log')).open('wb') as errors:
            process=subprocess.run(cmd,stdout=output,stderr=errors,timeout=3600)
        record['wallSeconds']=time.perf_counter()-started
        record['exitCode']=process.returncode
        record['rawSha256After']=hashlib.sha256(Path(raw['path']).read_bytes()).hexdigest()
        payload=json.loads(stdout.read_bytes())
        if process.returncode==0:
            payload.pop('timings',None)
            stable=json.dumps(payload,ensure_ascii=True,separators=(',',':')).encode()
            with gzip.open(target/(name+'.stable.json.gz'),'wb') as saved: saved.write(stable)
            record['stableSha256']=hashlib.sha256(stable).hexdigest()
            record['counts']={direction:{stage:len(body.get(stage,[])) for stage in STAGES}
                              for direction,body in payload['directions'].items()}
            record['execution']='PASS'
            record['rawUnchanged']='PASS' if record['rawSha256After']==raw['sha256'] else 'FAIL'
            if prior is not None:
                record['repeatObjectsEqual']=json.loads(prior)==payload
                record['repeatBytesEqual']=prior==stable
                record['determinism']='PASS' if prior==stable else 'FAIL'
            prior=stable
            # Execution completion is not a semantic PASS.
            record['status']='PASS' if record['rawUnchanged']=='PASS' else 'FAIL'
            record['semanticVerification']='INCOMPLETE - evaluated in invariant pass'
        else:
            record['execution']='FAIL'
            record['error']=payload
            record['status']='FAIL'
        manifest.write_text(json.dumps(records,indent=2),encoding='utf-8')
        print(f'END {name} {record["status"]} {record["wallSeconds"]:.2f}s',flush=True)

if __name__=='__main__': main()
