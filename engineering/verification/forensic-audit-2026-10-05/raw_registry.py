"""Read every available canonical RAW dataset and validate factual input structure."""
from pathlib import Path
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib, json, orjson, re

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]

def local(value): return datetime.fromtimestamp(value,ZoneInfo('Asia/Tehran')).isoformat()

def main():
    records=[]
    for path in sorted((ROOT/'apps/chart/state/data/RAW').rglob('*.json')):
        if path.name.endswith('.meta.json'): continue
        content=path.read_bytes()
        rows=orjson.loads(content.removeprefix(b'\xef\xbb\xbf'))
        times=[int(row['time']) for row in rows]
        deltas=Counter(b-a for a,b in zip(times,times[1:]))
        errors=[]
        for i,row in enumerate(rows):
            o,h,l,c=(float(row[k]) for k in ('open','high','low','close'))
            if not (l<=min(o,c)<=max(o,c)<=h):
                if len(errors)<10: errors.append({'index':i,'row':row})
        nominal=re.search(r' (\d+)S FROM',path.name)
        record={'path':str(path),'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),
                'rows':len(rows),'first':times[0],'last':times[-1],
                'firstLocal':local(times[0]),'lastLocal':local(times[-1]),
                'nominalSeconds':int(nominal[1]) if nominal else None,
                'stepCounts':dict(deltas),'duplicateTimes':sum(v for k,v in deltas.items() if k==0),
                'decreasingTimes':sum(v for k,v in deltas.items() if k<0),
                'ohlcErrorExamples':errors,'firstRow':rows[0],'lastRow':rows[-1]}
        meta=path.with_name(path.name+'.meta.json')
        if meta.exists(): record['metadata']=json.loads(meta.read_text(encoding='utf-8-sig'))
        records.append(record)
        print(json.dumps({k:record[k] for k in ('path','rows','firstLocal','lastLocal','nominalSeconds','duplicateTimes','decreasingTimes')}),flush=True)
    (OUT/'raw-registry.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
    # Verify both complete embedded snapshots against actual package bytes, preserving CRLF.
    refs=[]
    for path in (OUT/'package/algorithms').glob('*.md'):
        body=path.read_bytes()
        snapshots=[]
        for match in re.finditer(rb'<!-- EXACT-SOURCE-BEGIN:([^\r\n]+) -->\r?\n````python\r?\n(.*?)````\r?\n<!-- EXACT-SOURCE-END:\1 -->',body,re.S):
            name=match[1].decode()
            code=match[2]
            actual=OUT/'package'/name
            snapshots.append({'path':name,'exists':actual.exists(),'embeddedSha256':hashlib.sha256(code).hexdigest(),
                              'matches':actual.exists() and code==actual.read_bytes()})
        refs.append({'reference':path.name,'embedded':snapshots})
    (OUT/'reference-integrity.json').write_text(json.dumps(refs,indent=2),encoding='utf-8')

if __name__=='__main__': main()
