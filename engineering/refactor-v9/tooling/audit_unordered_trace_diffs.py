#!/usr/bin/env python3
"""Diagnostic only: quantify unordered-set iteration differences WITHOUT granting semantic PASS.

The archived original trace event ordering and all source payloads remain unchanged.
Never use this normalization to assert complete trading-state parity.
"""
import argparse,collections,copy,gzip,json
from pathlib import Path
import global_semantic_trace_compare_v4 as comp

def transform(value):
    if isinstance(value,dict):
        if '$unordered_set_NONCANONICAL' in value:
            entries=[transform(x) for x in value['$unordered_set_NONCANONICAL']]
            tokens=[json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in entries]
            return {'$unordered_members_DIAGNOSTIC_ONLY': sorted(tokens)}
        return {k:transform(v) for k,v in value.items()}
    if isinstance(value,list):return [transform(x) for x in value]
    return value

def audit(original,candidate):
    x=comp.records(original);y=comp.records(candidate)
    n=0;strict=0;only_unordered=0;semantic=0;first=[];input_drifts=0
    while True:
        a=next(x,None);b=next(y,None)
        if a is None and b is None:break
        n+=1
        if a is None or b is None:
            semantic+=1
            if len(first)<5:first.append({'ordinal':n,'type':'missing event'})
            continue
        if a['payload']==b['payload']:
            strict+=1
            if a['inputs']!=b['inputs']:input_drifts+=1
            continue
        pa=transform(a['payload']);pb=transform(b['payload'])
        if pa==pb:
            only_unordered+=1
            if len(first)<5:first.append({'ordinal':n,'type':'noncanonical set iteration order only','family':a['family']})
        else:
            semantic+=1
            if len(first)<5:first.append({'ordinal':n,'type':'persists after diagnostic set handling','family_original':a['family'],'family_candidate':b['family']})
    return {'status':'DIAGNOSTIC_ONLY_NEVER_FULL_PASS','positions':n,'strict_equal':strict,
        'positions_different_only_by_unordered_set_iteration':only_unordered,
        'positions_different_after_unordered_set_diagnostic':semantic,
        'input_drifts_on_strict_equal_events':input_drifts,'first_observations':first,
        'contract':'Raw event order and unordered iterator records are preserved; diagnostic sorted strings are not comparison authority.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('original');p.add_argument('candidate');p.add_argument('--out',required=True);a=p.parse_args()
    data=audit(a.original,a.candidate);Path(a.out).write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))