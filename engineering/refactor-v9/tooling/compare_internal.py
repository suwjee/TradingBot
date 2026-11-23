#!/usr/bin/env python3
"""Compare family-local chronological semantic outputs while preserving within-family order.

Known implementation-only call patterns are kept in raw trace, excluded from
semantic equivalence, and explicitly listed as unverified gaps.
"""
from __future__ import annotations
import argparse,collections,gzip,json,hashlib
from pathlib import Path
IMPL_ONLY={
 'order_audit_engine:OrderAuditEngineMixin._direct_parent_stop_order',
 'order_audit_engine:OrderAuditEngineMixin._compute_direct_parent_stop_order',
 'order_audit_engine:OrderAuditEngineMixin.order_candidates',
 'order_audit_engine:OrderAuditEngineMixin._register_order_audit',
 'e_zone_detector:EZoneDetector._parent_stop',
}

def read(path):
    families=collections.defaultdict(list)
    with gzip.open(path,'rt',encoding='utf8') as f:
        for n,line in enumerate(f,1):
            x=json.loads(line)
            tag=x['stage']+':'+x['method']
            families[tag].append((n,x))
    return families

def compare(a,b):
    left=read(a);right=read(b)
    report={'scope':'FAMILY_LOCAL_EVENT_SEQUENCE_NOT_CROSS_FAMILY_GLOBAL_CHRONOLOGY',
            'status':'PASS','families':[], 'excluded_implementation_families':[],
            'not_full_semantic_oracle':True}
    for family in sorted(set(left)|set(right)):
        x=left[family];y=right[family]
        if family in IMPL_ONLY:
            report['excluded_implementation_families'].append({'family':family,'original':len(x),'candidate':len(y),
                                                                 'reason':'method invocation count may differ from implementation-only cache optimization; not treated as semantic parity'})
            continue
        fields=('stage','method','direction','result','pre_state','post_state','raw_time_local_iran','raw_epoch_derived','raw_time_observed','decision')
        fp1=hashlib.sha256();fp2=hashlib.sha256()
        for seq,h in ((x,fp1),(y,fp2)):
            for _,row in seq:
                h.update(json.dumps({k:row[k] for k in fields if k in row},ensure_ascii=False,separators=(',',':')).encode()+b'\n')
        status='PASS' if len(x)==len(y) and fp1.digest()==fp2.digest() else 'FAIL'
        first_diff=None
        if status=='FAIL':
            for i in range(max(len(x),len(y))):
                if i>=len(x) or i>=len(y):first_diff={'index':i,'missing_side':'original' if i>=len(x) else 'candidate'};break
                va={k:x[i][1][k] for k in fields if k in x[i][1]}
                vb={k:y[i][1][k] for k in fields if k in y[i][1]}
                if va!=vb:
                    key=next(k for k in dict.fromkeys((*va,*vb)) if va.get(k)!=vb.get(k))
                    first_diff={'index':i,'field':key,'original_event_ordinal':x[i][0],'candidate_event_ordinal':y[i][0],
                                'before_excerpt':repr(va.get(key))[:600], 'after_excerpt':repr(vb.get(key))[:600]};break
        input_equal = len(x)==len(y) and all(xi[1].get('inputs')==yi[1].get('inputs') for xi,yi in zip(x,y))
        report['families'].append({'family':family,'status':status,'inputs_equal':input_equal,'events_original':len(x),'events_candidate':len(y),
                                   'sha256_original':fp1.hexdigest(),'sha256_candidate':fp2.hexdigest(), 'first_diff':first_diff})
        if status=='FAIL':report['status']='FAIL'
    report['input_drift_families']=[item['family'] for item in report['families'] if not item['inputs_equal']]
    report['compared_event_count']=sum(t['events_original'] for t in report['families'])
    report['excluded_original_event_count']=sum(t['original'] for t in report['excluded_implementation_families'])
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--original',required=True);p.add_argument('--candidate',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();r=compare(a.original,a.candidate)
    Path(a.output).write_text(json.dumps(r,indent=2,ensure_ascii=False));print(json.dumps({'status':r['status'],'families':len(r['families']),
      'failed':[t['family'] for t in r['families'] if t['status']=='FAIL'], 'events_compared':r['compared_event_count'],'events_excluded':r['excluded_original_event_count']}))
    raise SystemExit(r['status']!='PASS')
