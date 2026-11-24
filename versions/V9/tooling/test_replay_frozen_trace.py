import hashlib,json
from pathlib import Path
import pytest
from replay_frozen_trace import replay, hash_file
from test_single_pass_trace_gate import write_trace, reference
from test_strict_trace_gate_v9 import event
from strict_golden import stable_payload


def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n')


def inventory(root):
    write(root/'artifact-manifest.json',[{'file':p.name,'bytes':p.stat().st_size,'sha256':hash_file(p)} for p in sorted(root.iterdir()) if p.name not in ('artifact-manifest.json','execution-summary.json')])


def fixture(tmp):
    result=tmp/'result';result.mkdir();rows=[]
    native=b'{"timeframe":30,"directions":{"bullish":[],"bearish":[]},"timings":{"phasesMs":{"phase":1.2},"bridgeTotalMs":1.3}}'
    stable,schema=stable_payload(native);digest=hashlib.sha256(stable).hexdigest()
    for v in ('original','v81'):
        trace=result/(v+'.trace.jsonl.gz');write_trace(trace,[event()]);(result/(v+'.native.json')).write_bytes(native)
        rows.append({'variant':v,'native_exit':0,'integrity':'PASS','stable_sha256':digest,'timing_schema':schema,'trace_sha256':hash_file(trace),'events':1,'stage_sidecars':0})
    ref=reference(result/'original.trace.jsonl.gz',result/'v81.trace.jsonl.gz')
    write(result/'strict_comparison.json',ref['comparison'])
    for v,r in zip(('original','v81'),ref['reports']):
        write(result/(v+'.integrity.json'),r['integrity']);write(result/(v+'.stage_integrity.json'),r['stage_integrity'])
    pair={'stable_output_status':'PASS','selected_event_status':'PASS','rows':rows,'status':'INCOMPLETE'};write(result/'pair_report.json',pair)
    case={'records':1,'source_sha256':{'original':{},'v81':{}},'raw_sha256':'a'*64,'stable_output_sha256':digest}
    write(result/'execution-summary.json',{'complete_pair_execution':'PASS','runner_exit':2,'bars':1,'input_sha256':case['raw_sha256'],'rows':rows,'stable_output_status':'PASS','selected_event_status':'PASS'})
    inventory(result);write(tmp/'case.json',case);write(tmp/'frozen.json',{'source_sha256':case['source_sha256'],'scales':{'1':{'raw_sha256':case['raw_sha256'],'stable_output_sha256':digest}}})
    return result,tmp/'case.json',tmp/'frozen.json'


def test_replay_exact(tmp_path):
    result,case,frozen=fixture(tmp_path);r=replay(result,case,frozen,1)
    assert r['replay_status']=='PASS';assert r['native_stable_bytes_equal'];assert r['full_semantic_state_status']=='INCOMPLETE'


@pytest.mark.parametrize('kind',['hash','extra','missing','traversal','duplicate','report','typed_report','case','summary','native','integrity_path'])
def test_replay_rejects(tmp_path,kind):
    result,case,frozen=fixture(tmp_path)
    if kind=='hash':(result/'original.native.json').write_bytes(b'bad')
    elif kind=='extra':(result/'untracked.txt').write_text('extra')
    elif kind=='missing':(result/'original.native.json').unlink()
    elif kind in ('traversal','duplicate'):
        f=result/'artifact-manifest.json';m=json.loads(f.read_text());m.append(dict(m[0]));m[-1]['file']='../outside' if kind=='traversal' else m[-1]['file'];write(f,m)
    elif kind in ('report','typed_report'):
        f=result/'strict_comparison.json';m=json.loads(f.read_text());m['compared_positions']=2 if kind=='report' else True;write(f,m);inventory(result)
    elif kind=='case':m=json.loads(case.read_text());m['raw_sha256']='b'*64;write(case,m)
    elif kind=='summary':f=result/'execution-summary.json';m=json.loads(f.read_text());m['complete_pair_execution']='FAIL';write(f,m)
    elif kind=='native':f=result/'original.native.json';f.write_bytes(f.read_bytes().replace(b'"bullish":[]',b'"bullish":[1]'));inventory(result)
    elif kind=='integrity_path':f=result/'original.integrity.json';m=json.loads(f.read_text());m['path']='/unrelated/other.gz';write(f,m);inventory(result)
    with pytest.raises((ValueError,AssertionError,OSError,EOFError,KeyError)):replay(result,case,frozen,1)
