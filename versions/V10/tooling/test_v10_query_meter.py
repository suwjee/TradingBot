import collections, sys
from types import SimpleNamespace
from v10_query_meter import Meter

def test_confirmation_branch_and_rows():
    source='''def probe(self, confirmation_after):
    direct_position = 0
    if confirmation_after is not None:
        while direct_position < len(self.opposite_reactions) and self._opposite_confirmations[direct_position] <= confirmation_after:
            direct_position += 1
    return direct_position
'''
    scope={};exec(compile(source,'meter_fixture.py','exec'),scope)
    m=Meter({('meter_fixture.py','probe'):{4:'confirmation_query',5:'confirmation_skip'}})
    o=SimpleNamespace(opposite_reactions=[object() for _ in range(4)],_opposite_confirmations=[1,2,2,4]);empty=SimpleNamespace(opposite_reactions=[],_opposite_confirmations=[])
    sys.settrace(m.trace)
    try:
        assert scope['probe'](o,None)==0
        assert scope['probe'](o,0)==0
        assert scope['probe'](o,2)==3
        assert scope['probe'](o,4)==4
        assert scope['probe'](empty,4)==0
    finally:sys.settrace(None)
    assert not m.pending
    assert m.counts['probe']=={'calls':5,'returns':5,'confirmation_query':4,'confirmation_skip':7}
    assert m.skip_hist=={0:2,3:1,4:1}
    assert m.sequence_hist=={4:3,0:1}

def test_nested_invocations_do_not_share_pending_rows():
    src='''def probe(self, depth):
    if depth:
        probe(self, depth-1)
    return depth
'''
    scope={};exec(compile(src,'nested_fixture.py','exec'),scope)
    m=Meter({('nested_fixture.py','probe'):{3:'recursion'}})
    sys.settrace(m.trace)
    try:assert scope['probe'](None,4)==4
    finally:sys.settrace(None)
    assert m.counts['probe']=={'calls':5,'returns':5,'recursion':4}
    assert not m.pending
