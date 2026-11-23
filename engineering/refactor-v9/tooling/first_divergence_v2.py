#!/usr/bin/env python3
"""Forensic earliest GLOBAL semantic divergence without event reordering.

Preserves original event positions, pointer paths, order and Decimal lexemes.
Implementation-only event families are reported as excluded; cannot claim
full internal trace proof. No float tolerance and no event-time sorting.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json
from pathlib import Path
from global_semantic_trace_compare import IMPL_ONLY,FIELDS


def rows(path):
    ordinal=0
    with gzip.open(path,'rt',encoding='utf8') as fp:
        for line in fp:
            ordinal+=1
            r=json.loads(line)
            if r.get('schema') not in ('tradingbot.v9.internal-observer.v1','tradingbot.v9.internal-observer.v2') or r.get('event_ordinal')!=ordinal:
                raise ValueError('Invalid event ordinals at '+str(ordinal))
            if r['stage']+':'+r['method'] in IMPL_ONLY:continue
            yield r

def first_path(a,b,pointer='$'):
    if type(a) is not type(b):return pointer,a,b
    if isinstance(a,dict):
        for k in a:
            if k not in b:return pointer+'.'+str(k),a[k],'<missing>'
            ret=first_path(a[k],b[k],pointer+'.'+str(k))
            if ret:return ret
        for k in b:
            if k not in a:return pointer+'.'+str(k),'<missing>',b[k]
        return None
    if isinstance(a,(tuple,list)):
        for i,(x,y) in enumerate(zip(a,b)):
            ret=first_path(x,y,f'{pointer}[{i}]')
            if ret:return ret
        if len(a)!=len(b):return pointer+'.length',len(a),len(b)
        return None
    if a!=b:return pointer,a,b
    return None

def project(row):
    if row is None:return None
    return {k:row[k] for k in FIELDS if k in row}

def provenance_fields(row):
    if row is None:return None
    v=row.get('entity_provenance') or row.get('first_entity_provenance') or {}
    wanted=('source_time','source_index','parent_type','parent_source_time',
            'parent_source_index','decision_event_time','number','family')
    return {k:v[k] for k in wanted if k in v}

def first_diff(path_a,path_b,context_radius=2,compare_inputs=False):
    from itertools import zip_longest
    from collections import deque
    before=deque(maxlen=context_radius)
    a=rows(path_a);b=rows(path_b)
    for index,(row_a,row_b) in enumerate(zip_longest(a,b),1):
        projection_a=project(row_a);projection_b=project(row_b)
        if compare_inputs and row_a and row_b:
            projection_a['inputs']=row_a.get('inputs');projection_b['inputs']=row_b.get('inputs')
        diff=first_path(projection_a,projection_b)
        if diff:
            pointer,left,right=diff
            result={'status':'FAIL','compared_position':index,'first_field':pointer,
                    'original':{'stage':row_a.get('stage'),'method':row_a.get('method'),
                                'direction':row_a.get('direction'),'event_ordinal':row_a.get('event_ordinal'),
                                'raw_time':row_a.get('raw_epoch_derived',row_a.get('raw_time_observed')),'entity_provenance':provenance_fields(row_a)} if row_a else None,
                    'candidate':{'stage':row_b.get('stage'),'method':row_b.get('method'),
                                 'direction':row_b.get('direction'),'event_ordinal':row_b.get('event_ordinal'),
                                 'raw_time':row_b.get('raw_epoch_derived',row_b.get('raw_time_observed')),'entity_provenance':provenance_fields(row_b)} if row_b else None,
                    'original_value':left,'candidate_value':right,
                    'prior_context':list(before),
                    'following_context':[],'compare_inputs':compare_inputs,
                    'scope':'selected method-return events, not all in-process state'}
            for _ in range(context_radius):
                nxt_a=next(a,None);nxt_b=next(b,None)
                if nxt_a is None and nxt_b is None:break
                result['following_context'].append({'original':project(nxt_a),'candidate':project(nxt_b)})
            return result
        before.append({'original':projection_a,'candidate':projection_b})
    return {'status':'PASS','compared_positions':index if 'index' in locals() else 0,
            'scope':'selected global method-return events; exclusions remain unverified'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--original',required=True);p.add_argument('--candidate',required=True);p.add_argument('--out',required=True);p.add_argument('--compare-inputs',action='store_true');a=p.parse_args()
    r=first_diff(a.original,a.candidate,compare_inputs=a.compare_inputs);Path(a.out).write_text(json.dumps(r,indent=2,ensure_ascii=False));print(r['status'],r.get('first_field'),r.get('compared_positions'));raise SystemExit(r['status']=='FAIL')
