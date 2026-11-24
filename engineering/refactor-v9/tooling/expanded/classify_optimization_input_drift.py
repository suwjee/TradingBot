#!/usr/bin/env python3
"""Identify V8.1 S-parent pre-registration hint without normalizing main trace.

This strictly reports how many original and candidate input records are unequal,
and independently classifies one precisely understood V8.1 fast-path hint.
Neither upstream semantic comparator nor golden verifier drops a field.
"""
from __future__ import annotations
import argparse,collections,copy,gzip,json
from pathlib import Path
from global_semantic_trace_compare import IMPL_ONLY

def selected(path):
    with gzip.open(path,'rt',encoding='utf8') as stream:
        ordinal=0
        for line in stream:
            ordinal+=1
            d=json.loads(line)
            if d['event_ordinal']!=ordinal:raise ValueError('corrupt event ordinals')
            if d['stage']+':'+d['method'] in IMPL_ONLY:continue
            yield d

def exact_hint_only(a,b):
    if a.get('stage')!='e_zone_detector' or a.get('method')!='EZoneDetector._zone':return False
    left=a.get('inputs');right=b.get('inputs')
    if not isinstance(left,dict) or not isinstance(right,dict):return False
    if left.get('status')!='complete_supported' or right.get('status')!='complete_supported':return False
    before=copy.deepcopy(right)
    try:
        kwargs=before['value']['$kwargs']['value']['$mapping']
        found=[x for x in kwargs if x[0]=='pre_registered_s']
        if len(found)!=1 or type(found[0][1]) is not bool:return False
        parent_type=before['value']['$args']['value']['$tuple'][2]
        if found[0][1]!=(parent_type=='S'):return False
        kwargs.remove(found[0])
    except (KeyError,TypeError,ValueError,IndexError):return False
    return left==before and a.get('result')==b.get('result')

def inspect(path_a,path_b):
    import itertools
    compared=0;drifts=0;covered=0;unresolved=0;examples=[];by_family=collections.Counter()
    for x,y in itertools.zip_longest(selected(path_a),selected(path_b)):
        compared+=1
        if x is None or y is None:
            unresolved+=1;continue
        if x.get('inputs')!=y.get('inputs'):
            drifts+=1
            family=x['stage']+':'+x['method'];by_family[family]+=1
            if exact_hint_only(x,y): covered+=1
            else:
                unresolved+=1
                if len(examples)<10:examples.append({'position':compared,'family':family,
                  'original_event_ordinal':x.get('event_ordinal'),'candidate_event_ordinal':y.get('event_ordinal')})
    return {'status':'PASS' if unresolved==0 else 'UNRESOLVED_INPUT_DRIFT',
            'scope':'INDEPENDENT ANALYSIS OF INPUT DIFFERENCES ONLY: NEVER USED TO NORMALIZE EVENT OR GOLDEN EQUALITY',
            'events_compared':compared,'input_drift_events':drifts,
            'V81_pre_registered_s_hint_only_and_same_output':covered,
            'unresolved_input_drift_or_missing_event':unresolved,
            'by_family':dict(by_family),'unresolved_examples':examples,
            'evidence':'V8.1 e_zone_detector.py::_discover_candidate_chains passes pre_registered_s True after pre-registration of S; _zone skips a duplicate physical S-parent registration. This audit checks exact one-kwarg difference and identical result, not universal internal state parity.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('original');p.add_argument('candidate');p.add_argument('--out',required=True);a=p.parse_args()
    report=inspect(a.original,a.candidate)
    Path(a.out).write_text(json.dumps(report,indent=2))
    print(report['status'],'drifts',report['input_drift_events'],'classified',report['V81_pre_registered_s_hint_only_and_same_output'])
    raise SystemExit(report['status']!='PASS')
