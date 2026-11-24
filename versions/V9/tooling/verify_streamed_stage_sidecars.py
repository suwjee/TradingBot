#!/usr/bin/env python3
"""Independent V9 per-stage lossless JSONL gzip audit (test-only; no source mutation)."""
from __future__ import annotations
import argparse,gzip,hashlib,json
from pathlib import Path
from safe_sidecar import sidecar_path

def audit(summary_path:Path):
    manifest=json.loads(summary_path.read_text())
    root=summary_path.parent
    files=manifest.get('ordered_stage_output_sidecars',[])
    rows=[];failed=[]
    for meta in files:
        sha=hashlib.sha256();gzipsha=hashlib.sha256();raw_bytes=0;count=0;partial=0
        try:
            path=sidecar_path(root, meta['file'])
            with path.open('rb') as raw:
                while b:=raw.read(1<<20): gzipsha.update(b)
            with gzip.open(path,'rb') as gz:
                for line in gz:
                    j=json.loads(line)
                    if j['source_ordinal']!=count:raise ValueError('noncontiguous source ordinal')
                    if 'source_key' not in j or 'source_value' not in j:raise ValueError('missing source metadata')
                    if j['source_value']['status']!='complete_supported':partial+=1
                    sha.update(line);raw_bytes+=len(line);count+=1
            if gzipsha.hexdigest()!=meta['gzip_sha256']:raise ValueError('gzip SHA256 mismatch')
            if sha.hexdigest()!=meta['jsonl_sha256']:raise ValueError('JSONL SHA256 mismatch')
            if count!=meta['record_count']:raise ValueError('entry count mismatch')
            if raw_bytes!=meta['uncompressed_bytes']:raise ValueError('uncompressed bytes mismatch')
            if partial!=meta['partial_elements']:raise ValueError('partial coverage mismatches manifest')
            rows.append({'file':path.name,'records':count,'partial_elements':partial,'status':'PASS'})
        except Exception as exc:
            failed.append({'file':str(meta.get('file','<missing>')),'error':str(exc)})
    return {'status':'PASS_INTEGRITY_ONLY' if not failed else 'FAIL',
            'checked_stage_sidecars':len(rows),'expected_stage_sidecars':len(files),
            'rows':rows,'errors':failed,
            'coverage':'sidecar integrity only; no claim that every internal Engine state is traced'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=audit(a.manifest);a.out.write_text(json.dumps(r,indent=2));print(r['status'],len(r['rows']),len(r['errors']))
    raise SystemExit(r['status']!='PASS_INTEGRITY_ONLY')
