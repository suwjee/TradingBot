import copy,gzip,io,json
from decimal import Decimal
from pathlib import Path
import pytest
from ledger_delta_v9 import ABSENT,Observer,apply_delta,encode,make_delta,snapshot,verify_replay,b64

@pytest.mark.parametrize('a,b',[(b'',b'a'),(b'a',b''),(b'a',b'a'),(b'abc',b'abXc'),(b'abXc',b'abc'),(b'abc',b'xbc'),(b'abc',b'abx'),(b'abc',b'xyz'),(b'abc',b'abcd'),('طلا'.encode(),'نفت'.encode())])
def test_roundtrip(a,b):
    d=make_delta(a,b);assert apply_delta(a,d)==b;assert apply_delta(b,d,True)==a

@pytest.mark.parametrize('a,b',[(Decimal('1.00'),Decimal('1.0')),(Decimal('-0.00'),Decimal('0.00')),(1,True),(1,1.0),(-0.0,0.0),([1,2],[2,1]),([1],(1,)),({1:2,3:4},{3:4,1:2}),({1},frozenset({1})),(b'1','1')])
def test_exact_type_and_order(a,b):assert snapshot(a)!=snapshot(b)

def test_alias_and_nested_mutation():
    x=[];a=[x,x];b=[[],[]];assert snapshot(a)!=snapshot(b)
    old=snapshot(a);x.append(Decimal('1.200'));new=snapshot(a);assert apply_delta(old,make_delta(old,new))==new

def test_cycle_and_unsupported():
    x=[];x.append(x);assert b'"ref",0' in snapshot(x)
    with pytest.raises(TypeError):snapshot(object())

@pytest.mark.parametrize('field,value',[('prefix',-1),('suffix',True),('before_sha256','x'),('after_sha256','x'),('old','AAAA'),('new','%%%'),('after_bytes',999),('before_bytes',999)])
def test_corrupt_delta(field,value):
    d=make_delta(b'abc',b'aXc');d[field]=value
    with pytest.raises((ValueError,TypeError)):apply_delta(b'abc',d)

def fixture():
    a,b=snapshot({}),snapshot({(1,2):{'price':Decimal('1.230')}})
    rows=[];checks=[];last=ABSENT
    for i,(point,target) in enumerate([('entry',a),('return',b),('final',b)],1):
        fields={'ordinal':i,'owner':1,'class':'Owner','direction':'bullish','method':'final' if point=='final' else 'method','point':point}
        rows.append({**fields,'delta':make_delta(last,target)});checks.append({**fields,'snapshot':b64(target)});last=target
    return rows,checks

def files(tmp_path,a,b):
    ps=[tmp_path/'delta.gz',tmp_path/'full.gz']
    for p,rows in zip(ps,[a,b]):
        with gzip.open(p,'wb') as f:
            for row in rows:f.write(encode(row)+b'\n')
    return ps

def test_replay(tmp_path):
    a,b=fixture();r=verify_replay(*files(tmp_path,a,b));assert r['status']=='PASS' and r['boundaries']==3 and r['changed_boundaries']==2

@pytest.mark.parametrize('change',['removed','reordered','wrong_snapshot','wrong_owner','wrong_method','wrong_ordinal','missing_final','duplicate_final','bad_point','bad_delta'])
def test_replay_rejects(tmp_path,change):
    a,b=fixture()
    if change=='removed':a.pop(1)
    elif change=='reordered':a[0],a[1]=a[1],a[0]
    elif change=='wrong_snapshot':b[1]['snapshot']=b[0]['snapshot']
    elif change=='wrong_owner':b[1]['owner']=2
    elif change=='wrong_method':b[1]['method']='other'
    elif change=='wrong_ordinal':a[1]['ordinal']=3
    elif change=='missing_final':a.pop();b.pop()
    elif change=='duplicate_final':a.append(dict(a[-1],ordinal=4));b.append(dict(b[-1],ordinal=4))
    elif change=='bad_point':a[1]['point']=b[1]['point']='unknown'
    elif change=='bad_delta':a[1]['delta']['after_sha256']='0'*64
    with pytest.raises(ValueError):verify_replay(*files(tmp_path,a,b))
