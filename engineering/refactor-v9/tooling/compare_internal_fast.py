#!/usr/bin/env python3
"""Constant-memory family-local chronological event checksum comparator.

Not a global cross-family semantic execution oracle. Immutable order inside each
family is preserved; no sorting of candidate lists or parent state.
"""
import argparse,collections,gzip,hashlib,json
from pathlib import Path
from compare_internal import IMPL_ONLY
FIELDS=('stage','method','direction','result','pre_state','post_state','raw_time_local_iran','raw_epoch_derived','raw_time_observed','decision','rejection_reason')

def digests(path):
    result=collections.defaultdict(lambda:{'count':0,'hash':hashlib.sha256(),'inputs_hash':hashlib.sha256(),'input_partial':0})
    with gzip.open(path,'rt',encoding='utf8') as fp:
        for expected_ordinal,line in enumerate(fp,1):
            rec=json.loads(line)
            if rec.get('schema') != 'tradingbot.v9.internal-observer.v1':
                raise ValueError('Unexpected internal trace schema at line '+str(expected_ordinal))
            if type(rec.get('event_ordinal')) is not int or rec['event_ordinal']!=expected_ordinal:
                raise ValueError('Non-contiguous event ordinal at line '+str(expected_ordinal))
            k=rec['stage']+':'+rec['method'];state=result[k]
            row={key:rec[key] for key in FIELDS if key in rec}
            state['hash'].update(json.dumps(row,ensure_ascii=False,separators=(',',':')).encode()+b'\n')
            state['inputs_hash'].update(json.dumps(rec.get('inputs'),ensure_ascii=False,separators=(',',':')).encode()+b'\n')
            state['count']+=1
            if rec.get('inputs',{}).get('status')!='complete_supported' or rec.get('result',{}).get('status')!='complete_supported':state['input_partial']+=1
    return {k:{'count':v['count'],'sha256':v['hash'].hexdigest(),'inputs_sha256':v['inputs_hash'].hexdigest(),'unrepresentable':v['input_partial']} for k,v in result.items()}

def compare(a,b):
    x=digests(a);y=digests(b);rows=[]
    for name in sorted(set(x)|set(y)):
        prev=x.get(name,{});nxt=y.get(name,{})
        status='EXCLUDED_IMPLEMENTATION' if name in IMPL_ONLY else ('PASS' if prev.get('sha256')==nxt.get('sha256') and prev.get('count')==nxt.get('count') else 'FAIL')
        rows.append({'family':name,'status':status,'original':prev,'v81':nxt,
                     'inputs_byte_equal':prev.get('inputs_sha256')==nxt.get('inputs_sha256'),
                     'scope':'family-local outcome only; not call interleaving or in-process full lifecycle state'})
    return {'status':'PASS' if all(r['status']!='FAIL' for r in rows) else 'FAIL',
            'coverage':'PARTIAL: SELECTED FAMILY-LOCAL SEMANTIC OUTCOMES',
            'families':rows,'comparable_count':sum(r['original'].get('count',0) for r in rows if r['status']!='EXCLUDED_IMPLEMENTATION'),
            'excluded_count':sum(r['original'].get('count',0) for r in rows if r['status']=='EXCLUDED_IMPLEMENTATION'),
            'input_drift':[r['family'] for r in rows if r['status']!='EXCLUDED_IMPLEMENTATION' and not r['inputs_byte_equal']]}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--original',required=True);p.add_argument('--candidate',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    r=compare(a.original,a.candidate)
    Path(a.output).write_text(json.dumps(r,indent=2),encoding='utf8')
    print(json.dumps({'status':r['status'],'comparable':r['comparable_count'],'excluded':r['excluded_count'],
        'input_drift_families':r['input_drift'],'failed':[x['family'] for x in r['families'] if x['status']=='FAIL']}))
    raise SystemExit(r['status']!='PASS')
