#!/usr/bin/env python3
"""Independent lossless integrity/coverage audit over compressed V9 observer JSONL.

Fail closed on checksum, exact event ordinal/count, index offset, stage start/end
pairing. Do not claim all hidden states were traced: report every unsupported
semantic value and named not-in-scope category.
"""
from __future__ import annotations
import argparse,collections,csv,gzip,hashlib,json
from pathlib import Path

SCHEMAS={'tradingbot.v9.internal-observer.v1','tradingbot.v9.internal-observer.v2','tradingbot.v9.internal-observer.v3'}

def inspect(path):
    path=Path(path)
    manifest_path=Path(str(path)+'.manifest.json')
    manifest=json.loads(manifest_path.read_text())
    digest=hashlib.sha256(); families=collections.Counter()
    missing=collections.Counter();partials=collections.Counter();nonsafe=collections.Counter()
    boundary=collections.Counter();coverage=collections.Counter();stages=[];stack=[]
    uncompressed=0;count=0;expected_index={x['event_ordinal']:x['uncompressed_byte_offset'] for x in manifest['index']}
    with gzip.open(path,'rb') as inp:
        for raw in inp:
            count+=1
            if count in expected_index and uncompressed!=expected_index[count]:
                raise AssertionError(f'index offset mismatch at event {count}: {path}')
            uncompressed+=len(raw);digest.update(raw)
            row=json.loads(raw)
            if row.get('schema') not in SCHEMAS or row.get('event_ordinal')!=count:
                raise AssertionError(f'event format/ordinal at {count}: {path}')
            family=row.get('stage','?')+':'+row.get('method','?')
            families[family]+=1
            for field in ('direction','result'):
                if field not in row:missing[field+':'+family]+=1
            for field in ('result','inputs','pre_inputs','lifecycle_new_events'):
                z=row.get(field)
                if isinstance(z,dict) and z.get('status')!='complete_supported':
                    partials[field+':'+family+':'+str(z.get('status','unknown'))]+=1
            if 'authoritative_boundary_state' in row:
                boundary[family]+=1
                for point,group in row['authoritative_boundary_state'].items():
                    if not group:continue
                    for field,x in group.get('fields',{}).items():
                        status=x.get('status','unclassified')
                        coverage[point+':'+family+':'+field+':'+status]+=1
                        if status!='complete_supported':
                            partials['authoritative_boundary:'+point+':'+family+':'+field+':'+status]+=1
            if row.get('method')=='timed.stage_start':
                label=row.get('phase_label');stack.append(label);stages.append(('start',label,count))
            elif row.get('method')=='timed.stage_end':
                label=row.get('phase_label');stages.append(('end',label,count))
                if not stack or stack.pop()!=label:
                    raise AssertionError(f'Unbalanced stage boundary {count}: {label}: {path}')
            if '$unordered_set_NONCANONICAL' in str(row):nonsafe['unordered_set_in_trace']+=1
    if stack:raise AssertionError(f'Unclosed stage boundaries in {path}')
    if count!=manifest['events'] or digest.hexdigest()!=manifest['jsonl_sha256']:
        raise AssertionError(f'event count/hash mismatch in {path}')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=manifest['gzip_sha256']:
        raise AssertionError(f'gzip digest mismatch in {path}')
    if uncompressed!=manifest['uncompressed_bytes']:raise AssertionError('uncompressed bytes mismatch')
    if dict(families)!=manifest['families']:
        raise AssertionError('family counts do not match manifest')
    sidecar_results=[]
    for desc in manifest.get('chronology_input_sidecars',[]):
        f=path.parent/desc['sidecar']
        if hashlib.sha256(f.read_bytes()).hexdigest()!=desc['gzip_sha256']:
            raise AssertionError('Chronology sidecar gzip SHA mismatch '+str(f))
        n=0;h=hashlib.sha256();byte_count=0;by_kind=collections.Counter()
        with gzip.open(f,'rb') as inp:
            for raw in inp:
                row=json.loads(raw);by_kind[row['type']]+=1
                if row['ordinal']!=by_kind[row['type']]-1:
                    raise AssertionError('Sidecar chronology ordinal not sequential')
                h.update(raw);byte_count+=len(raw);n+=1
        if n!=desc['record_count'] or n!=desc['main_count']+desc['lower_count']:
            raise AssertionError('Sidecar chronology record count inconsistent')
        if h.hexdigest()!=desc['jsonl_sha256'] or byte_count!=desc['uncompressed_bytes']:
            raise AssertionError('Sidecar chronology JSONL digest/size mismatch')
        sidecar_results.append({'file':str(f),'verified':'PASS','record_count':n,
            'main_count':by_kind['main'],'lower_count':by_kind['lower_5s'],
            'sha256':h.hexdigest()})
    collections_verified=[]
    for desc in manifest.get('ordered_collection_sidecars',[]):
        f=path.parent/desc['file']
        if hashlib.sha256(f.read_bytes()).hexdigest()!=desc['gzip_sha256']:
            raise AssertionError('Ordered source collection sidecar gzip SHA mismatch')
        n=0;length=0;h=hashlib.sha256()
        with gzip.open(f,'rb') as stream:
            for raw in stream:
                row=json.loads(raw)
                if row.get('source_ordinal')!=n:raise AssertionError('Collection sidecar ordinal drift')
                n+=1;h.update(raw);length+=len(raw)
        if n!=desc['entry_count'] or length!=desc['uncompressed_bytes'] or h.hexdigest()!=desc['jsonl_sha256']:
            raise AssertionError('Collection sidecar has corrupt length or digest')
        collections_verified.append({'file':str(f),'status':'PASS','record_count':n,
                  'type':desc['element_type'],
                  'mutable_candidate_first_use_snapshot_only':desc['candidate_content_is_snapshot_at_first_use_only']})
    return {'path':str(path),'integrity':'PASS','sha256_jsonl':digest.hexdigest(),
            'raw_events':count,'verified_immutable_chronology_sidecars':sidecar_results,
            'verified_ordered_collection_sidecars':collections_verified,'stages_pair_count':len(stages)//2,
            'stages':stages,'families':dict(families),'full_authoritative_boundaries':dict(boundary),
            'ledger_field_coverage':dict(coverage),'unsupported_items':dict(partials),
            'missing_required':dict(missing),'nondeterministic_legacy_set_markers':dict(nonsafe),
            'semantic_completeness':'NOT VERIFIED: only selected method calls, stages and selected authoritative state snapshots'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--roots',nargs='+',required=True)
    p.add_argument('--out',required=True);p.add_argument('--filename-pattern',default='*.trace.jsonl.gz');a=p.parse_args()
    files=[]
    for root in a.roots:
        files+=list(Path(root).glob(a.filename_pattern))
    if not files:raise ValueError('no traces found')
    rows=[];fail=[]
    for path in sorted(files):
        print('AUDIT',path,flush=True)
        try:rows.append(inspect(path))
        except Exception as exc:
            fail.append({'path':str(path),'status':'FAIL','reason':repr(exc)})
        dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps({'status':'FAIL' if fail else 'INCOMPLETE_SEMANTIC_COVERAGE','files_audited':len(rows),'rows':rows,'failures':fail},indent=2))
    if fail:return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
