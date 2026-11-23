#!/usr/bin/env python3
"""Order/byte-preserving, lossless stage-boundary execution trace; NOT an internal semantic trace.
This is a projected snapshot from native serialized Engine output, not a recorder of rejected E candidates.
"""
import argparse, gzip, io, json, hashlib
from pathlib import Path
from strict_golden import stable_payload
SCHEMA='tradingbot.v9.stage-boundary.v1'
TIME_KEYS=('sourceTime','rawTime','time','firstTime','decisionTime','formationTime','breakTime','secondTime','parentSourceTime')
ID_KEYS=('id','number','ordinal','sourceIndex','index','reactionNumber','aOrdinal','eNumber','sNumber','parentSourceIndex')

def event_stream(raw):
    stable,_=stable_payload(raw)
    d=json.loads(stable)
    num=0
    for direction,body in d['directions'].items():
        for stage,payload in body.items():
            if stage=='bridgeOutput' and isinstance(payload,dict):
                children=payload.items()
            else:children=[(None,payload)]
            for substage,records in children:
                if isinstance(records,list):
                    all_items=enumerate(records)
                else:all_items=[(0,records)]
                for offset,item in all_items:
                    num+=1
                    if isinstance(item,dict):
                        raw_time=next((item[k] for k in TIME_KEYS if k in item and item[k] is not None),None)
                        entity=next((str(item[k]) for k in ID_KEYS if k in item),str(offset))
                        provenance={k:v for k,v in item.items() if any(t in k.lower() for t in ('parent','source','ordinal','first','time','stop','accepted','tie','rejection'))}
                    else:raw_time=None;entity=str(offset);provenance={}
                    yield {'schema':SCHEMA,'event_ordinal':num,'direction':direction,'stage':stage,
                           'substage':substage,'row_ordinal':offset,'raw_time':raw_time,
                           'entity_id':entity,'provenance':provenance,'record':item}

def record(src,dest):
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    count=0;indexes=[];h=hashlib.sha256();byte_offset=0
    with dest.open('wb') as raw_fp:
        with gzip.GzipFile(fileobj=raw_fp,mode='wb',filename='',mtime=0,compresslevel=6) as zip_fp:
            for ev in event_stream(Path(src).read_bytes()):
                line=json.dumps(ev,ensure_ascii=False,separators=(',',':')).encode('utf8')+b'\n'
                if count==0 or count%2000==0:indexes.append({'event_ordinal':count+1,'uncompressed_byte_offset':byte_offset})
                h.update(line);zip_fp.write(line);count+=1;byte_offset+=len(line)
    # gzip compressed offsets are not seek offsets; record logical line checkpoints only.
    report={'schema':SCHEMA,'coverage':'STAGE_BOUNDARY_ONLY','count':count,'jsonl_sha256':h.hexdigest(),
            'gzip_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
            'uncompressed_bytes':byte_offset,'index_stride_events':2000,'index':indexes}
    Path(str(dest)+'.manifest.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    return report

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--input',required=True);a.add_argument('--out',required=True);o=a.parse_args();print(json.dumps(record(o.input,o.out),indent=2))
