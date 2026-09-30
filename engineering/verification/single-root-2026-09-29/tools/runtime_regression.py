"""Compare full ordered bridge output across a storage-only migration."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import time
import orjson

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent.parent

def main():
    mode = argparse.ArgumentParser()
    mode.add_argument('phase', choices=['before','after'])
    args = mode.parse_args()
    rawroot = ROOT.with_name(ROOT.name+'-Local')/'data/raw' if args.phase=='before' else ROOT/'apps/chart/state/data/raw'
    results=[]
    for symbol in ('XAUUSD','USOIL'):
        candidates=[p for p in rawroot.rglob('*.json') if not p.name.endswith('.meta.json') and symbol in p.name]
        raw=min(candidates,key=lambda p:p.stat().st_size)
        data=raw.read_bytes();rows=orjson.loads(data);first=min(r['time'] for r in rows);last=max(r['time'] for r in rows)
        cmd=[sys.executable,'-B',str(ROOT/'engine/bridge/trading_pipeline.py')]
        for flag,name in [('reaction-engine','reaction_engine'),('blue-line-engine','blue_line_detector'),('a-zone-engine','a_zone_detector'),('s-zone-engine','s_zone_detector'),('e-zone-engine','e_zone_detector'),('lifecycle-engine','lifecycle_engine')]:
            cmd += ['--'+flag,str(ROOT/'engine/pipeline'/f'{name}.py')]
        cmd += ['--data',str(raw),'--timeframe','30','--from-time',str(first),'--to-time',str(last),'--direction','both','--bridge-output']
        stdout=OUT/f'{args.phase}-{symbol}.json';stderr=OUT/f'{args.phase}-{symbol}.stderr.log'
        started=time.perf_counter()
        with stdout.open('wb') as f,stderr.open('wb') as e:
            result=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=e)
        assert result.returncode==0, f'Bridge failed for {symbol}: {stderr}'
        payload=orjson.loads(stdout.read_bytes());timings=payload.pop('timings',None);stable=orjson.dumps(payload)
        normalized=OUT/f'{args.phase}-{symbol}.stable.json';normalized.write_bytes(stable)
        equal=None if args.phase=='before' else stable==(OUT/f'before-{symbol}.stable.json').read_bytes()
        record=dict(symbol=symbol,raw=raw.name,rows=len(rows),raw_sha256=hashlib.sha256(data).hexdigest(),
                    timeframe=30,direction='both',complete_input=True,wall_seconds=round(time.perf_counter()-started,3),
                    stable_sha256=hashlib.sha256(stable).hexdigest(),equal=equal,return_code=result.returncode,
                    stage_counts={d:{k:len(v) for k,v in x.items() if isinstance(v,list)} for d,x in payload['directions'].items()})
        results.append(record)
        (OUT/f'{args.phase}-runtime-regression.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
        print(json.dumps(record),flush=True)
        if equal is False:
            raise AssertionError(f'Stable output changed: {symbol}')

if __name__=='__main__':main()
