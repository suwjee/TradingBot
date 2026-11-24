"""Mutations for fused verifier; legacy comparator/audit as regression oracle."""
from collections import Counter
from pathlib import Path
import copy, gzip, hashlib, json
import pytest
from audit_trace_coverage import inspect
from strict_trace_gate_v9 import compare, SCHEMA
from verify_streamed_stage_sidecars import audit as stage_audit
from single_pass_trace_gate import audit_pair
from test_strict_trace_gate_v9 import event,rep


def sha(data):return hashlib.sha256(data).hexdigest()


def write_trace(path, rows, raw_override=None):
    rows=[{'schema':SCHEMA,'event_ordinal':i,**r} for i,r in enumerate(rows,1)]
    raw=b''.join(json.dumps(r,ensure_ascii=False,separators=(',',':')).encode()+b'\n' for r in rows) if raw_override is None else raw_override
    path.write_bytes(gzip.compress(raw,mtime=0))
    manifest={'events':len(rows),'jsonl_sha256':sha(raw),'gzip_sha256':sha(path.read_bytes()),
              'uncompressed_bytes':len(raw),'families':dict(Counter(r['stage']+':'+r['method'] for r in rows)),
              'index':[{'event_ordinal':1,'uncompressed_byte_offset':0}] if rows else []}
    mp=Path(str(path)+'.manifest.json');mp.write_text(json.dumps(manifest))
    return mp,manifest


def reference(a,b):
    return {'comparison':compare(a,b),'reports':[{'integrity':inspect(p),'stage_integrity':stage_audit(Path(str(p)+'.manifest.json'))} for p in (a,b)]}


@pytest.mark.parametrize('kind,want',[('equal','PASS'),('decimal','FAIL'),('type','FAIL'),('order','FAIL'),('deleted','FAIL'),('unknown_input','FAIL'),('partial','INCOMPLETE'),('unordered','INCOMPLETE'),('known_hint','PASS'),('known_hint_wrong','FAIL'),('pre_state','FAIL'),('excluded','PASS'),('missing_input','INCOMPLETE'),('float_negative_zero','FAIL'),('nested_map_order','FAIL')])
def test_equivalence(tmp_path,kind,want):
    left=[event('one'),event('two')];right=copy.deepcopy(left)
    if kind=='decimal':right[0]['result']['value']['$decimal']='100.0100'
    elif kind=='type':left[0]['result']=rep(True);right[0]['result']=rep(1)
    elif kind=='order':right.reverse()
    elif kind=='deleted':right.pop()
    elif kind=='unknown_input':right[0]['inputs']=rep('changed')
    elif kind=='partial':left[0]['inputs']=right[0]['inputs']=rep({'inner':{'status':'partial_unrepresentable'}})
    elif kind=='unordered':left[0]['inputs']=right[0]['inputs']=rep({'$unordered_set_NONCANONICAL':[1,2]})
    elif kind.startswith('known_hint'):
        a=event('EZoneDetector._zone',rep({'$args':rep({'$tuple':['family',1,'S']}),'$kwargs':rep({'$mapping':[['another',1]]})}));a['stage']='e_zone_detector';b=copy.deepcopy(a);b['inputs']['value']['$kwargs']['value']['$mapping'].append(['pre_registered_s',kind=='known_hint']);left[0]=a;right[0]=b
    elif kind=='pre_state':right[0]['pre_state']={'n':1}
    elif kind=='excluded':
        x=event('EZoneDetector._parent_stop');x['stage']='e_zone_detector';left.insert(1,x)
    elif kind=='missing_input':del left[0]['inputs'];del right[0]['inputs']
    elif kind=='float_negative_zero':left[0]['result']=rep(0.0);right[0]['result']=rep(-0.0)
    elif kind=='nested_map_order':left[0]['result']=rep({'a':1,'b':2});right[0]['result']=rep({'b':2,'a':1})
    a,b=tmp_path/'a.gz',tmp_path/'b.gz';write_trace(a,left);write_trace(b,right)
    r=audit_pair(a,b);assert r==reference(a,b);assert r['comparison']['selected_event_status']==want;assert r['comparison']['full_semantic_state_status']=='INCOMPLETE'


@pytest.mark.parametrize('kind',['count','offset','jsonl_hash','gzip_hash','bytes','families','truncated','duplicate_key','nonfinite','unbalanced','missing_required','missing_sidecar','sidecar_escape','stage_corruption','stage_missing_field','collection_corruption','chronology_corruption'])
def test_corruption(tmp_path,kind):
    a,b=tmp_path/'a.gz',tmp_path/'b.gz';write_trace(a,[event()]);mp,m=write_trace(b,[event()])
    if kind in ('count','offset','jsonl_hash','gzip_hash','bytes','families'):
        if kind=='count':m['events']+=1
        elif kind=='offset':m['index'][0]['uncompressed_byte_offset']=1
        elif kind=='jsonl_hash':m['jsonl_sha256']='0'*64
        elif kind=='gzip_hash':m['gzip_sha256']='0'*64
        elif kind=='bytes':m['uncompressed_bytes']+=1
        elif kind=='families':m['families']={}
    elif kind=='truncated':b.write_bytes(b.read_bytes()[:-4])
    elif kind in ('duplicate_key','nonfinite'):
        raw=gzip.decompress(b.read_bytes()).replace(b'"event_ordinal":1',b'"event_ordinal":1,"event_ordinal":1' if kind=='duplicate_key' else b'"event_ordinal":1,"nan":NaN');mp,m=write_trace(b,[event()],raw)
    elif kind=='unbalanced':mp,m=write_trace(b,[{'stage':'trading_pipeline','method':'timed.stage_start','direction':'unclassified','phase_label':'A','result':rep(None)}])
    elif kind=='missing_required':e=event();del e['direction'];mp,m=write_trace(b,[e])
    else:
        side=tmp_path/'side.gz';obj={'source_ordinal':0,'source_key':rep(0),'source_value':rep(1)}
        if kind=='stage_missing_field':del obj['source_key']
        raw=json.dumps(obj).encode()+b'\n';side.write_bytes(gzip.compress(raw,mtime=0));desc={'file':side.name,'gzip_sha256':sha(side.read_bytes()),'jsonl_sha256':sha(raw),'uncompressed_bytes':len(raw),'record_count':1,'partial_elements':0}
        if kind=='sidecar_escape':desc['file']='../side.gz'
        if kind=='missing_sidecar':side.unlink()
        if kind=='stage_corruption':desc['jsonl_sha256']='0'*64
        if kind=='collection_corruption':desc.update(entry_count=1,element_type='Candle',candidate_content_is_snapshot_at_first_use_only=False,gzip_sha256='0'*64);m['ordered_collection_sidecars']=[desc]
        elif kind=='chronology_corruption':desc.update(sidecar=side.name,main_count=1,lower_count=0,gzip_sha256='0'*64);m['chronology_input_sidecars']=[desc]
        else:m['ordered_stage_output_sidecars']=[desc]
    mp.write_text(json.dumps(m))
    with pytest.raises((ValueError,AssertionError,OSError,EOFError,KeyError)):audit_pair(a,b)


@pytest.mark.parametrize('raw',[b'{"s":"$unordered_set_NONCANONICAL"}',b'{"s":"\\u0024unordered_set_NONCANONICAL"}',b'{"s":"$unordered\\u005fset_NONCANONICAL"}',b'{"s":"\\\\u0024unordered_set_NONCANONICAL"}',b'{"s":"$unordered_set_","t":"NONCANONICAL"}',b'{"s":"ordinary"}',b'{"$unordered_set_NONCANONICAL":[1,2]}','{"s":"$unordered_set_NONCANONICAL"}'.encode('utf-16'),b'\xef\xbb\xbf{"s":"ordinary"}'])
def test_legacy_marker_exact(raw):
    from audit_trace_coverage import has_legacy_set_marker, SET_MARKER
    row=json.loads(raw)
    assert has_legacy_set_marker(raw,row)==(SET_MARKER in str(row))


@pytest.mark.parametrize('raw', [
    b'{"a":{"status":"partial_unrepresentable"}}',
    b'{"a":{"status":"unclassified"}}',
    b'{"a":{"status":"unsupported"}}',
    b'{"a":{"status":"un\\u0073upported"}}',
    b'{"a":{"sta\\u0074us":"unsupported"}}',
    b'{"a":{"\\u0024unrepresentable":7}}',
    b'{"a":{"$unordered_set_NONCANONICAL":[1,2]}}',
    b'{"a":[{"a":{"$unrepresentable":null}}, {"status":"unsupported"}]}',
    b'{"a":"unclassified"}',
    b'{"a":{"status":"complete_supported","value":null}}',
    b'{"status":123}',
    b'{"ordinary":[1,2,3,4]}',
    b'{"escaped":"\\\\u0073"}',
])
def test_representation_guard_no_false_negative(raw):
    from strict_trace_gate_v9 import check_rep
    from single_pass_trace_gate import may_contain_representation_issue, strict_decode
    issues=Counter();check_rep(strict_decode(raw),'family',issues)
    assert not issues or may_contain_representation_issue(raw)
    if b'ordinary' in raw: assert not may_contain_representation_issue(raw)


def test_fused_unicode_escape_issues(tmp_path):
    a,b=tmp_path/'a.gz',tmp_path/'b.gz'
    row=event();row['inputs']=rep({'inner':{'status':'unsupported','$unrepresentable':'x'}})
    write_trace(a,[row]);raw=gzip.decompress(a.read_bytes()).replace(b'unsupported',b'un\\u0073upported').replace(b'$unrepresentable',b'\\u0024unrepresentable')
    write_trace(b,[row],raw)
    result=audit_pair(a,b)
    assert result==reference(a,b)
    assert result['comparison']['selected_event_status']=='INCOMPLETE'
    assert result['comparison']['original_representation_issues']==result['comparison']['candidate_representation_issues']
