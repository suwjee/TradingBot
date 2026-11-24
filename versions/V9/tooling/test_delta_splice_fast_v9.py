import random
import pytest
from ledger_delta_v9 import make_delta,apply_delta
from delta_splice_fast_v9 import make_delta_fast

@pytest.mark.parametrize('a,b',[(b'',b''),(b'',b'a'),(b'a',b''),(b'a',b'a'),(b'abc',b'abcx'),(b'abcd',b'abc'),(b'abc',b'xbc'),(b'abc',b'abx'),(b'ababab',b'abab'),(b'aaa',b'aaaa'),(b'12345',b'12x45'),(b'\x00\xff',b'\xff\x00')])
def test_edge(a,b):
    d=make_delta_fast(a,b);assert d==make_delta(a,b);assert apply_delta(a,d)==b;assert apply_delta(b,d,True)==a

def test_many_reproducible_mutations():
    r=random.Random(20261124)
    for _ in range(2500):
        a=r.randbytes(r.randrange(2048));p=r.randrange(len(a)+1);q=r.randrange(p,len(a)+1);b=a[:p]+r.randbytes(r.randrange(256))+a[q:]
        d=make_delta_fast(a,b);assert d==make_delta(a,b);assert apply_delta(a,d)==b;assert apply_delta(b,d,True)==a

def test_large_and_noop():
    a=b'x'*5000000; b=a[:2000000]+b'y'+a[2000001:];assert make_delta_fast(a,b)==make_delta(a,b);assert make_delta_fast(a,a)==make_delta(a,a)

def test_nonbytes():
    with pytest.raises(TypeError):make_delta_fast(bytearray(b'a'),b'a')
