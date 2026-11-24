#!/usr/bin/env python3
"""Family-local diagnostic of read-only observed risk-method return streams.

No canonical normalization of source events, no claiming full semantic equivalence.
Exact scalar returns and count-only state deltas are reported separately.
"""
from __future__ import annotations
import argparse,collections,gzip,hashlib,json,itertools
from pathlib import Path

SCHEMA='tradingbot.v9.risk-return-call-coverage.v1'


def read(path):
    ordinal=0
    with gzip.open(path,'rt',encoding='utf8') as stream:
        for line in stream:
            ordinal+=1
            row=json.loads(line)
            if row.get('schema')!=SCHEMA or row.get('event_ordinal')!=ordinal:
                raise AssertionError('invalid or noncontiguous trace '+str(path)+':'+str(ordinal))
            yield row

def hash_all(path):
    counts=collections.Counter();returns=collections.defaultdict(hashlib.sha256)
    states=collections.defaultdict(hashlib.sha256)
    partial=collections.Counter()
    for row in read(path):
        fam=row['module']+':'+row['method'];counts[fam]+=1
        data=json.dumps(row['return'],separators=(',',':'),ensure_ascii=False).encode()+b'\n'
        returns[fam].update(data)
        state=json.dumps({'pre':row['pre_selected_state'],'post':row['post_selected_state']},
                         separators=(',',':'),ensure_ascii=False).encode()+b'\n'
        states[fam].update(state)
        if row['return']['coverage'] not in ('EXACT_SCALAR','EXACT_REPR_NONPRICE_ONLY'):
            partial[fam]+=1
    return {'counts':counts,'return_digests':{k:v.hexdigest() for k,v in returns.items()},
            'count_state_digests':{k:v.hexdigest() for k,v in states.items()},'partial':partial}

def first_diff(a,b,fam):
    af=(x for x in read(a) if x['module']+':'+x['method']==fam)
    bf=(x for x in read(b) if x['module']+':'+x['method']==fam)
    for idx,(x,y) in enumerate(itertools.zip_longest(af,bf),1):
        if x is None or y is None:return {'family_local_ordinal':idx,'reason':'missing_call','original':x,'candidate':y}
        for field in ('return','pre_selected_state','post_selected_state'):
            if x[field]!=y[field]:
                def truncate(z):return json.dumps(z,ensure_ascii=False)[:800]
                return {'family_local_ordinal':idx,'field':field,'original_event_ordinal':x['event_ordinal'],
                        'candidate_event_ordinal':y['event_ordinal'],
                        'original_value_excerpt':truncate(x[field]),
                        'candidate_value_excerpt':truncate(y[field])}
    return None

def compare(a,b,out):
    aa=hash_all(a);bb=hash_all(b)
    union=set(aa['counts'])|set(bb['counts']);summary=[]
    differences=[]
    for fam in sorted(union):
        count_eq=aa['counts'][fam]==bb['counts'][fam]
        ret_eq=count_eq and aa['return_digests'].get(fam)==bb['return_digests'].get(fam)
        state_eq=count_eq and aa['count_state_digests'].get(fam)==bb['count_state_digests'].get(fam)
        row={'family':fam,'calls_original':aa['counts'][fam],'calls_v81':bb['counts'][fam],
             'same_number_of_calls':count_eq,'returns_equal_in_family_order':ret_eq,
             'selected_state_counts_equal_in_family_order':state_eq,
             'returns_partial_original':aa['partial'][fam],'returns_partial_v81':bb['partial'][fam]}
        summary.append(row)
        if not(count_eq and ret_eq and state_eq):differences.append(fam)
    first={fam:first_diff(a,b,fam) for fam in differences[:6]}
    out_obj={'status':'DIAGNOSTIC_ONLY_NOT_FULL_SEMANTIC_PASS',
      'scope':'One complete 15,061-row OIL RAW, native 30/5/both, full 81 AST-risk function families',
      'family_count':len(union),'equal_call_count_families':sum(x['same_number_of_calls'] for x in summary),
      'equal_return_families':sum(x['returns_equal_in_family_order'] for x in summary),
      'equal_selected_state_count_families':sum(x['selected_state_counts_equal_in_family_order'] for x in summary),
      'families_with_any_difference':len(differences),'first_differences':first,
      'source_events_preserved':True,
      'limits':['Grouping method returns by family discards cross-family invocation order in this diagnostic only.',
        'Large dictionaries/lists and nested state only COUNT_ONLY, so identical counts are not exact state equivalence.',
        'Different cache call counts are implementation observations; they are not automatically trading differences.',
        'Full Live and all mutations inside functions are not observed.'],
      'families':summary}
    Path(out).write_text(json.dumps(out_obj,indent=2))
    print({k:v for k,v in out_obj.items() if k in ('status','family_count','equal_return_families','equal_selected_state_count_families','families_with_any_difference')})
    return 0
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('original');p.add_argument('v81');p.add_argument('--out',required=True);a=p.parse_args()
    raise SystemExit(compare(a.original,a.v81,a.out))