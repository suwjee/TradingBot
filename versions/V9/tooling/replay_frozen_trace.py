#!/usr/bin/env python3
"""Re-audit a completed, pinned execution artifact without rerunning the Engine.

The caller must authenticate the archive itself (the CI workflow pins its ZIP
SHA256). All member files are then verified against the recorded inventory,
including original native outputs and every referenced sidecar. Only local
filesystem path fields of the integrity report may differ after extraction.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from safe_sidecar import sidecar_path
from single_pass_trace_gate import audit_pair, strict_decode
from strict_golden import stable_payload


def read_json(path):
    return strict_decode(Path(path).read_bytes())


def hash_file(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def exact_json(value):
    # Object key order of reports (not engine events) is not semantic. Array
    # order, field types, strings, float signs and Decimal spellings stay exact.
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def same(a,b,label):
    if exact_json(a)!=exact_json(b):
        raise AssertionError(f'Archived and re-audited {label} differ')


def local_report(report, expected_trace_name):
    """Only path fields known to depend on extraction location are normalized."""
    import copy
    value=copy.deepcopy(report)
    def basename(name):
        if not isinstance(name,str):raise TypeError('Invalid report path')
        return name.replace('\\','/').rsplit('/',1)[-1]
    value['path']=basename(value['path'])
    if value['path']!=expected_trace_name:raise ValueError('Wrong trace identity in report')
    for key in ('verified_immutable_chronology_sidecars','verified_ordered_collection_sidecars'):
        for item in value[key]:item['file']=basename(item['file'])
    return value


def verify_inventory(result):
    inventory_path=result/'artifact-manifest.json'
    rows=read_json(inventory_path)
    if not isinstance(rows,list) or not rows:raise ValueError('Missing artifact inventory')
    names=set()
    for item in rows:
        name=item['file']
        if name in names:raise ValueError('Duplicate artifact inventory entry')
        path=sidecar_path(result,name);names.add(name)
        if type(item['bytes']) is not int or path.stat().st_size!=item['bytes'] or hash_file(path)!=item['sha256']:
            raise ValueError('Artifact inventory mismatch: '+name)
    actual={p.name for p in result.iterdir() if p.is_file() and not p.is_symlink()}
    expected=names|{'artifact-manifest.json','execution-summary.json'}
    if actual!=expected or any(not p.is_file() or p.is_symlink() for p in result.iterdir()):
        raise ValueError('Artifact inventory does not match extracted directory')
    return len(rows),hash_file(inventory_path)


def replay(result, case_path, frozen_path, bars):
    result=Path(result).resolve(strict=True)
    start=time.perf_counter();case=read_json(case_path);frozen=read_json(frozen_path)
    if type(case.get('records')) is not int or case['records']!=bars:
        raise ValueError('Wrong frozen case size')
    spec=frozen['scales'][str(bars)]
    for k in ('raw_sha256','stable_output_sha256'):
        same(case[k],spec[k],'pinned '+k)
    same(case['source_sha256'],frozen['source_sha256'],'pinned source closure')
    n,manifest_sha=verify_inventory(result)
    old=read_json(result/'pair_report.json');summary=read_json(result/'execution-summary.json')
    if old.get('error') or old.get('stable_output_status')!='PASS' or old.get('selected_event_status') not in ('PASS','INCOMPLETE'):
        raise ValueError('Archived execution was not a completed pair')
    if summary.get('complete_pair_execution')!='PASS' or summary.get('runner_exit') not in (0,2):
        raise ValueError('Archived execution summary is not complete')
    same(summary['bars'],bars,'summary candle count');same(summary['input_sha256'],case['raw_sha256'],'summary input hash')
    same(summary['rows'],old['rows'],'summary rows');same(summary['stable_output_status'],old['stable_output_status'],'summary Golden status');same(summary['selected_event_status'],old['selected_event_status'],'summary selected status')
    if [r['variant'] for r in old['rows']]!=['original','v81']:raise ValueError('Wrong source order')
    stable_bytes=None
    for row in old['rows']:
        variant=row['variant']
        if row['native_exit']!=0 or row['integrity']!='PASS':raise ValueError('Incomplete archived variant')
        stable,schema=stable_payload((result/(variant+'.native.json')).read_bytes())
        digest=hashlib.sha256(stable).hexdigest();same(digest,case['stable_output_sha256'],'Golden SHA256');same(digest,row['stable_sha256'],'row SHA256');same(schema,row['timing_schema'],'telemetry schema')
        if stable_bytes is None:stable_bytes=stable
        elif stable!=stable_bytes:raise AssertionError('Archived native stable bytes differ')
        same(hash_file(result/(variant+'.trace.jsonl.gz')),row['trace_sha256'],'archived trace SHA256')
    del stable_bytes,stable
    setup_wall=time.perf_counter()-start
    audit_start=time.perf_counter();new=audit_pair(result/'original.trace.jsonl.gz',result/'v81.trace.jsonl.gz');audit_wall=time.perf_counter()-audit_start
    same(new['comparison'],read_json(result/'strict_comparison.json'),'strict comparison')
    same(new['comparison']['selected_event_status'],old['selected_event_status'],'selected status')
    for row,report in zip(old['rows'],new['reports'],strict=True):
        v=row['variant'];name=v+'.trace.jsonl.gz'
        same(local_report(report['integrity'],name),local_report(read_json(result/(v+'.integrity.json')),name),v+' integrity')
        same(report['stage_integrity'],read_json(result/(v+'.stage_integrity.json')),v+' stage integrity')
        same(report['integrity']['raw_events'],row['events'],v+' event count');same(report['stage_integrity']['checked_stage_sidecars'],row['stage_sidecars'],v+' stage count')
    n2,sha2=verify_inventory(result)
    if (n2,sha2)!=(n,manifest_sha):raise AssertionError('Archive inventory changed during replay')
    return {'replay_status':'PASS','scope':'Exact re-audit of completed archived pair; no new Engine execution or universal semantic claim',
            'bars':bars,'raw_sha256':case['raw_sha256'],'stable_output_sha256':case['stable_output_sha256'],
            'native_stable_bytes_equal':True,'full_legacy_report_equality':True,'artifact_member_count':n,'artifact_manifest_sha256':manifest_sha,
            'archive_setup_and_hash_validation_s':setup_wall,'fused_audit_wall_s':audit_wall,'total_wall_s':time.perf_counter()-start,
            'python':sys.version,'host':platform.platform(),'comparison':new['comparison'],'full_semantic_state_status':'INCOMPLETE'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',type=Path,required=True);p.add_argument('--case',type=Path,required=True);p.add_argument('--frozen',type=Path,required=True);p.add_argument('--bars',type=int,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.resolve().is_relative_to(a.result.resolve()):raise ValueError('Write replay report outside immutable evidence')
    report=replay(a.result,a.case,a.frozen,a.bars);a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
