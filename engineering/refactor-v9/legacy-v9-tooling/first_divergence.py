#!/usr/bin/env python3
"""Streaming earliest difference in native event order (JSONL / JSONL.GZ).
No whole-file event list, no time sorting, no numeric normalization, bounded context memory.
"""
import argparse, gzip, json
from collections import deque
from pathlib import Path
from itertools import zip_longest

def iter_events(path):
    path=Path(path)
    with (gzip.open(path,'rt',encoding='utf8') if path.suffix=='.gz' else path.open('r',encoding='utf8')) as fp:
        for n,ln in enumerate(fp,1):
            if not ln.strip():continue
            d=json.loads(ln)
            if not isinstance(d,dict):raise ValueError('JSONL event must be an object')
            yield n,d

def first_field(a,b,path='$'):
    if type(a) is not type(b):return path
    if isinstance(a,dict):
        if list(a)!=list(b):
            i=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)))
            return f'{path}.<key-order[{i}]>'
        for k in a:
            if a[k]!=b[k]:return first_field(a[k],b[k],f'{path}.{k}')
        return None
    if isinstance(a,list):
        if len(a)!=len(b):return f'{path}.length'
        for i,(x,y) in enumerate(zip(a,b)):
            if x!=y:return first_field(x,y,f'{path}[{i}]')
        return None
    return path if a!=b else None

def compare(expected,actual,context=2):
    if context<0:raise ValueError('context must be >=0')
    a=iter_events(expected);b=iter_events(actual);hist_a=deque(maxlen=context);hist_b=deque(maxlen=context)
    count_a=count_b=0;first=None
    # Sentinel distinguishes a missing event from a real event JSON object.
    sentinel=object()
    for aa,bb in zip_longest(a,b,fillvalue=sentinel):
        if aa is not sentinel:count_a+=1
        if bb is not sentinel:count_b+=1
        ev_a=aa[1] if aa is not sentinel else None;ev_b=bb[1] if bb is not sentinel else None
        if first is None and (aa is sentinel or bb is sentinel or ev_a!=ev_b):
            exemplar=ev_a if ev_a is not None else (ev_b or {})
            first={'event_ordinal':max(count_a,count_b),'stage':exemplar.get('stage'),
                'direction':exemplar.get('direction'),'raw_time':exemplar.get('raw_time'),
                'entity_id':exemplar.get('entity_id'),'field':first_field(ev_a,ev_b),
                'provenance':exemplar.get('provenance'),
                'expected':ev_a,'actual':ev_b,'window':{
                  'expected':list(hist_a)+([ev_a] if ev_a is not None else []),
                  'actual':list(hist_b)+([ev_b] if ev_b is not None else [])}}
            remaining=context
        elif first is not None and remaining>0:
            if ev_a is not None:first['window']['expected'].append(ev_a)
            if ev_b is not None:first['window']['actual'].append(ev_b)
            remaining-=1
        if ev_a is not None:hist_a.append(ev_a)
        if ev_b is not None:hist_b.append(ev_b)
    return {'equal':first is None,'expected_events':count_a,'actual_events':count_b,
            'first_divergence':first,'comparator':'streaming, event-order first, no sorting'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--expected',required=True);p.add_argument('--actual',required=True)
    p.add_argument('--context',type=int,default=2);p.add_argument('--output');args=p.parse_args()
    result=compare(args.expected,args.actual,args.context)
    blob=json.dumps(result,indent=2,ensure_ascii=False)
    if args.output:Path(args.output).write_text(blob)
    else:print(blob)
    raise SystemExit(0 if result['equal'] else 1)
