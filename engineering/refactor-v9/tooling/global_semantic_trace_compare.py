#!/usr/bin/env python3
"""Fail-closed GLOBAL sequence comparator for selected observable V9 semantic method returns.

Unlike family-local digest, this rejects cross-family reordering. Report is NOT
full event coverage and does not silently normalize or sort any sequence.
"""
from __future__ import annotations
import argparse,collections,gzip,hashlib,json
from pathlib import Path

IMPL_ONLY={
 'order_audit_engine:OrderAuditEngineMixin._direct_parent_stop_order',
 'order_audit_engine:OrderAuditEngineMixin._compute_direct_parent_stop_order',
 'order_audit_engine:OrderAuditEngineMixin.order_candidates',
 'order_audit_engine:OrderAuditEngineMixin._register_order_audit',
 'e_zone_detector:EZoneDetector._parent_stop',
}
FIELDS=('stage','method','direction','phase_label','result','pre_state','post_state','authoritative_boundary_state','lifecycle_new_events','lifecycle_output_count_before','lifecycle_output_count_after','entity_provenance','first_entity_provenance',
        'raw_time_local_iran','raw_epoch_derived','raw_time_observed',
        'decision','rejection_reason')


def records(path):
    raw_count=0;excluded=collections.Counter();partial=collections.Counter()
    with gzip.open(path,'rt',encoding='utf8') as file:
        for line in file:
            raw_count+=1
            row=json.loads(line)
            if row.get('schema') not in ('tradingbot.v9.internal-observer.v1','tradingbot.v9.internal-observer.v2'):
                raise ValueError(f'Wrong schema event {raw_count} in {path}')
            if type(row.get('event_ordinal')) is not int or row['event_ordinal']!=raw_count:
                raise ValueError(f'Noncontiguous global event ordinal {raw_count} in {path}')
            family=row['stage']+':'+row['method']
            if family in IMPL_ONLY:
                excluded[family]+=1
                continue
            if (row.get('result',{}).get('status')!='complete_supported'
                or row.get('inputs',{}).get('status')!='complete_supported'):
                partial[family]+=1
            result={key:row[key] for key in FIELDS if key in row}
            yield {'original_event_ordinal':raw_count,'family':family,
                'payload':result,'inputs':row.get('inputs')}


def report(first,second,max_details=4):
    a=records(first);b=records(second)
    hd_a=hashlib.sha256();hd_b=hashlib.sha256()
    diff=[];input_only=[];equal=0;overall=0
    while True:
        x=next(a,None);y=next(b,None)
        if x is None and y is None:break
        overall+=1
        for rec,hashobj in ((x,hd_a),(y,hd_b)):
            if rec is not None:
                hashobj.update(json.dumps(rec['payload'],ensure_ascii=False,separators=(',',':')).encode()+b'\n')
        if x is None or y is None or x['payload']!=y['payload']:
            if len(diff)<max_details:
                diff.append({'global_compared_ordinal':overall,
                             'original':x,'candidate':y})
        else:
            equal+=1
            if x['inputs']!=y['inputs'] and len(input_only)<max_details:
                input_only.append({'global_compared_ordinal':overall,
                                   'family':x['family'],'original_event_ordinal':x['original_event_ordinal'],
                                   'candidate_event_ordinal':y['original_event_ordinal']})
    return {'status':'PASS' if not diff and equal==overall else 'FAIL',
            'coverage':'SELECTED_GLOBAL_CROSS_FAMILY_METHOD_RETURN_SEQUENCE_ONLY; NOT FULL SEMANTIC STATE',
            'total_compared_positions':overall,'positions_equal':equal,
            'original_sha256':hd_a.hexdigest(),'candidate_sha256':hd_b.hexdigest(),
            'first_mismatches':diff,'first_input_drifts':input_only,
            'known_exclusion_families':sorted(IMPL_ONLY),
            'not_in_scope':['cache_hit_tie_staleness','untraced candidate branches',
                            'whole accepted ledger pre_post snapshots','full Live continuation','untraced decisions']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('original');p.add_argument('candidate');p.add_argument('--out',required=True);a=p.parse_args()
    r=report(a.original,a.candidate);Path(a.out).write_text(json.dumps(r,indent=2))
    print(r['status'],r['total_compared_positions'],r['positions_equal'])
    raise SystemExit(r['status']!='PASS')
