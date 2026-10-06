"""Derived audit inputs only; original RAW rows and files are never altered."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib, json, orjson
from run_raw_matrix import OUT

def main():
    registry=json.loads((OUT/'raw-registry.json').read_text(encoding='utf-8'))
    overlap=json.loads((OUT/'raw-overlap-results.json').read_text(encoding='utf-8'))
    if any(x['conflictingPeerRows'] for x in overlap): raise ValueError('Peer RAW facts conflict; authority unresolved')
    target=OUT/'derived-inputs'; target.mkdir(exist_ok=True)
    records=[]
    for symbol in ('USOIL','XAUUSD'):
        maps={1:{},5:{}}
        inputs=[]
        for source in registry:
            tf=source['nominalSeconds']
            if symbol not in source['path'] or tf not in maps: continue
            inputs.append({'path':source['path'],'sha256':source['sha256'],'seconds':tf})
            for row in orjson.loads(Path(source['path']).read_bytes()):
                maps[tf].setdefault(int(row['time']),row)
        one=maps[1]
        if one:
            # Finest available stream owns its complete physical coverage interval.
            first_one=min(one); last_one=max(one)
            combined={t:r for t,r in maps[5].items() if t<first_one//5*5 or t>last_one}
            combined.update(one)
        else: combined=maps[5]
        rows=[combined[t] for t in sorted(combined)]
        content=orjson.dumps(rows)
        path=target/(symbol+'-finest-union.derived.json'); path.write_bytes(content)
        record={'path':str(path),'bytes':len(content),'rows':len(rows),'first':rows[0]['time'],'last':rows[-1]['time'],
                'sha256':hashlib.sha256(content).hexdigest(),'inputs':inputs,'derived':True,
                'authority':'Audit-only union of identical peer facts; 1s replaces5s inside complete1s coverage; no invented candles',
                'firstLocal':datetime.fromtimestamp(rows[0]['time'],ZoneInfo('Asia/Tehran')).isoformat(),
                'lastLocal':datetime.fromtimestamp(rows[-1]['time'],ZoneInfo('Asia/Tehran')).isoformat()}
        records.append(record)
        print(json.dumps({k:v for k,v in record.items() if k!='inputs'}),flush=True)
    (OUT/'finest-union-registry.json').write_text(json.dumps(records,indent=2),encoding='utf-8')

if __name__=='__main__':main()
