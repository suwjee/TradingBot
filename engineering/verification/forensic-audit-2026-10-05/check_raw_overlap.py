"""Compare overlapping input facts without selecting between conflicting peers."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import json, orjson
from run_raw_matrix import OUT

def main():
    registry=json.loads((OUT/'raw-registry.json').read_text(encoding='utf-8'))
    groups=defaultdict(list)
    for i,r in enumerate(registry):
        symbol='XAUUSD' if 'XAUUSD' in r['path'] else 'USOIL'
        groups[(symbol,r['nominalSeconds'])].append((i,r))
    summary=[]
    for group,members in groups.items():
        union={}; matches=conflicts=0; examples=[]
        for i,record in members:
            rows=orjson.loads(Path(record['path']).read_bytes())
            for row in rows:
                t=int(row['time'])
                values=tuple(Decimal(str(row[k])) for k in ('open','high','low','close'))
                prior=union.get(t)
                if prior is not None:
                    if prior[0]!=values:
                        conflicts+=1
                        if len(examples)<5: examples.append({'time':t,'leftRawIndex':prior[1],'rightRawIndex':i,
                                                           'left':list(map(str,prior[0])),'right':list(map(str,values))})
                    else: matches+=1
                else: union[t]=(values,i)
        summary.append({'symbol':group[0],'nominalSeconds':group[1],'rawIndices':[i for i,r in members],
                        'unionRows':len(union),'equalPeerRows':matches,'conflictingPeerRows':conflicts,'examples':examples,
                        'authority':'finest timeframe takes chronology precedence; same-timeframe conflicts remain unresolved'})
        print(json.dumps(summary[-1]),flush=True)
    (OUT/'raw-overlap-results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')

if __name__=='__main__':main()
