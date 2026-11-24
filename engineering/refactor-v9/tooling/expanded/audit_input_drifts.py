#!/usr/bin/env python3
"""Unmasked evidence of all input-only drifts in selected V9 global events.

A return-value match never excuses an unexamined difference in inputs. This
reports the exact earliest structural path, without sorting or canonicalizing
source args. Differences are not silently deleted or auto-approved.
"""
from __future__ import annotations
import argparse,collections,gzip,json
from pathlib import Path
from global_semantic_trace_compare import IMPL_ONLY,FIELDS
from first_divergence_v2 import first_path

def filtered(path):
    count=0
    with gzip.open(path,'rt',encoding='utf8') as stream:
        for line in stream:
            count+=1
            item=json.loads(line)
            if item['event_ordinal']!=count:raise ValueError('Noncontiguous event ordinal')
            if item['stage']+':'+item['method'] in IMPL_ONLY:continue
            yield item

def inspect(a,b):
    x=filtered(a);y=filtered(b);counter=collections.Counter();fields=collections.Counter();examples=[];n=0;in_drifts=0;semantic_mismatch=0
    from itertools import zip_longest
    for index,(first,second) in enumerate(zip_longest(x,y),1):
        n=index
        if first is None or second is None:
            semantic_mismatch+=1
            if len(examples)<20: examples.append({'index':index,'missing_event':True})
            continue
        family=first['stage']+':'+first['method']
        if family!=second['stage']+':'+second['method']:
            semantic_mismatch+=1
            if len(examples)<20:examples.append({'index':index,'family_original':family,'family_candidate':second['stage']+':'+second['method']})
            continue
        if first.get('inputs')!=second.get('inputs'):
            in_drifts+=1;counter[family]+=1
            diff=first_path(first.get('inputs'),second.get('inputs'))
            if diff:
                path,value_original,value_candidate=diff
                fields[family+':'+path]+=1
                if len(examples)<20:
                    import json as _j
                    def limited(v):
                        s=_j.dumps(v,ensure_ascii=False,default=str)
                        return s[:2000]+'…' if len(s)>2000 else s
                    examples.append({'index':index,'original_ordinal':first['event_ordinal'],
                                     'candidate_ordinal':second['event_ordinal'],'family':family,
                                     'first_field':path,
                                     'original_value_excerpt':limited(value_original),
                                     'candidate_value_excerpt':limited(value_candidate),
                                     'direction':first.get('direction')})
    return {'coverage':'SELECTED EVENT INPUTS; discrepancies are preserved as OPEN findings, not normalized',
            'comparable_positions':n,'semantic_families_sequence_mismatch':semantic_mismatch,
            'input_drift_positions':in_drifts,'by_method':dict(counter),'by_first_path':dict(fields),
            'first_examples':examples,'all_input_context_proved_equal':in_drifts==0 and semantic_mismatch==0}

def main():
    p=argparse.ArgumentParser();p.add_argument('original');p.add_argument('candidate');p.add_argument('--out',required=True);a=p.parse_args()
    result=inspect(a.original,a.candidate)
    Path(a.out).write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print('comparisons:',result['comparable_positions'],'input_drifts:',result['input_drift_positions'])
    return 0
if __name__=='__main__':raise SystemExit(main())
