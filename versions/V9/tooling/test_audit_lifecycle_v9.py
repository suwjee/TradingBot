import gzip,hashlib,collections
from decimal import Decimal
import pytest
from ledger_delta_v9 import snapshot,sha
from audit_lifecycle_v9 import inspect,compare
M='StopAllDetector._detect_events.<locals>.process_s_event'
def write(p,rows):
    data=b''.join(snapshot(x)+b'\n' for x in rows)
    with gzip.open(p,'wb') as f:f.write(data)
    return {'events':len(rows),'counts':dict(collections.Counter(x[1]+':'+x[2] for x in rows)),'jsonl_sha256':sha(data),'gzip_sha256':sha(p.read_bytes())}
def rows():return [(1,M,'entry','bullish',(Decimal('10.100'),['a','b'])),(2,M,'return','bullish',(Decimal('10.100'),['a','b']))]
@pytest.mark.parametrize('kind',['decimal','order','direction','delete','append','swap','ordinal'])
def test_divergence(tmp_path,kind):
    a=rows();b=rows();n,m,p,d,v=b[0]
    if kind=='decimal':b[0]=(n,m,p,d,(Decimal('10.10'),v[1]))
    elif kind=='order':b[0]=(n,m,p,d,(v[0],['b','a']))
    elif kind=='direction':b[0]=(n,m,p,'bearish',v)
    elif kind=='delete':b.pop()
    elif kind=='append':b.append((3,M,'entry','bullish',v))
    elif kind=='swap':b.reverse()
    elif kind=='ordinal':b[0]=(3,m,p,d,v)
    write(tmp_path/'a',a);write(tmp_path/'b',b);assert compare(tmp_path/'a',tmp_path/'b')['status']=='FAIL'
@pytest.mark.parametrize('kind',['count','digest','unmatched','ordinal','gzip'])
def test_integrity(tmp_path,kind):
    a=rows();p=tmp_path/'a'
    if kind=='unmatched':a.pop()
    if kind=='ordinal':a[1]=(3,*a[1][1:])
    r=write(p,a)
    if kind=='count':r['events']+=1
    if kind=='digest':r['jsonl_sha256']='0'*64
    if kind=='gzip':r['gzip_sha256']='0'*64
    with pytest.raises(ValueError):inspect(p,r)
def test_self(tmp_path):
    p=tmp_path/'a';r=write(p,rows());assert inspect(p,r)==2 and compare(p,p)['status']=='PASS'
