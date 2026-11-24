#!/usr/bin/env python3
"""Index the exact archived test-only trace sources without rewriting any bytes.

Manifest status is not semantic completeness: independently verified selected
trace equality does not prove all untraced engine-state transitions.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path

INPUTS=Path('/mnt/data/V9_work/tooling/inputs_verified.json')

def main(root,independent,out):
    root=Path(root);datasets=json.loads(INPUTS.read_text())['datasets']
    audits={}
    if Path(independent).is_file():
        report=json.loads(Path(independent).read_text())
        for row in report.get('rows',[]):
            audits[row['id']]=row
    rows=[];missing=[]
    for item in datasets:
        stem=Path(item['file']).stem.replace(' ','_')
        for variant in ('original','v81'):
            basename=variant+'.'+stem
            path=root/(basename+'.trace.jsonl.gz')
            manifest=Path(str(path)+'.manifest.json')
            native=root/(basename+'.native.json')
            stage=root/(basename+'.stage_cpu_rss.json')
            if not all(x.exists() for x in (path,manifest,native,stage)):
                missing.append(basename);continue
            data=json.loads(manifest.read_text())
            sidecars=data['chronology_input_sidecars']+data['ordered_collection_sidecars']
            missing_sidecars=[];sidecar_bytes=0
            for sc in sidecars:
                name=sc.get('sidecar',sc.get('file'))
                sp=path.parent/name
                if not sp.is_file():missing_sidecars.append(name)
                else:sidecar_bytes+=sp.stat().st_size
            name=path.name
            independent_row=audits.get(name)
            integrity=(independent_row is not None and
                       independent_row['jsonl_sha256']==data['jsonl_sha256'] and
                       independent_row['event_count']==data['events'])
            rows.append({'dataset':item['id'],'variant':variant,'raw_file':item['file'],
                        'original_raw_sha256':item['raw_sha256'],'raw_rows':item['records'],
                        'compressed_trace_path':str(path),'compressed_bytes':path.stat().st_size,
                        'declared_compressed_sha256':data['gzip_sha256'],
                        'declared_uncompressed_sha256':data['jsonl_sha256'],
                        'event_count':data['events'],'chronology_sidecars':len(data['chronology_input_sidecars']),
                        'collection_sidecars':len(data['ordered_collection_sidecars']),
                        'sidecar_total_bytes':sidecar_bytes,
                        'sidecars_all_present':not missing_sidecars,'missing_sidecars':missing_sidecars,
                        'independently_full_integrity_audited':bool(integrity),
                        'coverage':data['coverage'],
                        'semantic_state_complete':False})
    count=len(rows);audit_count=sum(x['independently_full_integrity_audited'] for x in rows)
    all_ok=(count==14 and not missing and audit_count==14 and all(x['sidecars_all_present'] for x in rows))
    result={'status':'PASS_ARCHIVE_INTEGRITY_ONLY' if all_ok else 'INCOMPLETE',
            'expected_trace_files':14,'files_present':count,'independently_verified':audit_count,
            'missing':missing,'rows':rows,'trace_semantic_coverage':'INCOMPLETE; no all-mutation-state equivalence'}
    target=Path(out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2))
    print({'status':result['status'],'present':count,'audited':audit_count})
    return 0 if all_ok else 2
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--trace-root',default='/mnt/data/V9_final/trace');p.add_argument('--integrity-matrix',default='/mnt/data/V9_completion_20261124/V9_TRACE_INTEGRITY_MATRIX.json');p.add_argument('--out',required=True);a=p.parse_args();raise SystemExit(main(a.trace_root,a.integrity_matrix,a.out))