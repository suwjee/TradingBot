#!/usr/bin/env python3
"""Fail-closed aggregation of independently completed trace integrity audits.

Never treat output-level or selected-method parity as full semantic equivalence.
All 7 Golden and V8.1 traces are verified against independently decompressed
uncompressed SHA, compressed SHA, exact ordinals, per-sidecar SHA and offsets.
"""
from __future__ import annotations
import argparse,json,collections,hashlib
from pathlib import Path

INPUTS=Path('/mnt/data/V9_work/tooling/inputs_verified.json')
DEFAULT=Path('/mnt/data/V9_completion_20261124/integrity_audits')


def main(out, audit_dir):
    inp=json.loads(INPUTS.read_text())['datasets']
    expected={}
    for item in inp:
        stem=Path(item['file']).stem.replace(' ','_')
        for variant in ('original','v81'):
            key=f'{variant}.{stem}.trace.jsonl.gz'
            expected[key]={'dataset':item['id'],'variant':variant,'rows_5s':item['records'],'id':key}
    files=[]
    for name in ('V9_XAU15K_TRACE_INTEGRITY.json','V9_OIL15K_TRACE_INTEGRITY.json','V9_XAU247K_TRACE_AUDIT.json'):
        p=Path('/mnt/data/V9_completion_20261124')/name
        if p.is_file():files.append(p)
    for f in audit_dir.glob('V9_*INTEGRITY.json'):
        if f.name=='V9_XAU83K_V81_INTEGRITY.json' or f.name=='V9_XAU83K_BOTH_INTEGRITY.json' or f.name=='V9_XAU97K_BOTH_INTEGRITY.json' or f.name=='V9_OIL47K_BOTH_INTEGRITY.json' or f.name=='V9_XAU247K_V81_INTEGRITY.json' or f.name=='V9_OIL284K_ORIGINAL_INTEGRITY.json' or f.name=='V9_OIL284K_V81_INTEGRITY.json':
            files.append(f)
    verified={};errors=[];duplicates=[]
    for file in files:
        try:report=json.loads(file.read_text())
        except (OSError,ValueError) as e:
            errors.append({'audit':str(file),'error':repr(e)});continue
        for f in report.get('failures',[]):errors.append({'audit':str(file),'failure':f})
        for row in report.get('rows',[]):
            key=Path(row.get('path','')).name
            if key not in expected:
                errors.append({'audit':str(file),'unexpected_path':key});continue
            if row.get('integrity')!='PASS':
                errors.append({'audit':str(file),'unverified_path':key});continue
            content={'source':'INDEPENDENT_FULL_GZIP_SIDECAR_EVENT_HASH_AUDIT',
                     **expected[key], 'event_count':row['raw_events'],'jsonl_sha256':row['sha256_jsonl'],
                     'stage_boundary_pairs':row['stages_pair_count'],
                     'verified_chronology_sidecars':len(row['verified_immutable_chronology_sidecars']),
                     'verified_collection_sidecars':len(row['verified_ordered_collection_sidecars']),
                     'coverage':'INTEGRITY_ONLY; SEMANTIC_TRACE_PARTIAL'}
            if key in verified:
                if verified[key]!=content:duplicates.append({'key':key,'audit':str(file),'inconsistent':True})
                continue
            verified[key]=content
    missing=sorted(set(expected)-set(verified))
    if errors or duplicates:status='FAIL'
    elif missing:status='INCOMPLETE'
    else:status='PASS_INTEGRITY_ONLY'
    result={'status':status,'scope':'exactly 7 real RAW x Golden+V8.1, native 30/5/both full history',
            'verified_files':len(verified),'expected_files':len(expected),'missing':missing,
            'errors':errors,'conflicting_duplicate_audits':duplicates,
            'rows':[verified[k] for k in sorted(verified)],
            'release_coverage':'TRACE_COVERAGE_PARTIAL; file integrity does not establish all internal semantic transitions'}
    target=Path(out);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,indent=2))
    print(json.dumps({'status':status,'verified':len(verified),'expected':len(expected),'missing':len(missing)},indent=2))
    return 0 if status=='PASS_INTEGRITY_ONLY' else 2 if status=='INCOMPLETE' else 1

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--audits',default=str(DEFAULT));a=p.parse_args()
    raise SystemExit(main(a.out,Path(a.audits)))