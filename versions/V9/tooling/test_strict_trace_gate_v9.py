import copy,gzip,json,tempfile,unittest
from pathlib import Path
from strict_trace_gate_v9 import compare,SCHEMA

def rep(v):return {'status':'complete_supported','value':v}
def event(method='Example._run',inputs=None):
    return {'stage':'example','method':method,'direction':'bullish','inputs':rep('input') if inputs is None else inputs,'result':rep({'$decimal':'100.010'}),'pre_state':{},'post_state':{}}

def write(p, rows):
    with gzip.open(p,'wt',encoding='utf-8') as f:
        for n,row in enumerate(rows,1):f.write(json.dumps({'schema':SCHEMA,'event_ordinal':n,**row})+'\n')

class StrictGate(unittest.TestCase):
    def run_pair(self,left,right,want):
        with tempfile.TemporaryDirectory() as t:
            a,b=Path(t)/'a.gz',Path(t)/'b.gz';write(a,left);write(b,right);r=compare(a,b)
        self.assertEqual(r['selected_event_status'],want,r);self.assertEqual(r['full_semantic_state_status'],'INCOMPLETE');return r
    def test_identical(self):self.run_pair([event()],[event()],'PASS')
    def test_empty(self):self.run_pair([],[],'FAIL')
    def test_input_change(self):self.run_pair([event()],[event(inputs=rep('changed'))],'FAIL')
    def test_decimal(self):
        a=event();b=copy.deepcopy(a);b['result']['value']['$decimal']='100.011';self.run_pair([a],[b],'FAIL')
    def test_bool_int(self):
        a=event();a['result']=rep(True);b=copy.deepcopy(a);b['result']=rep(1);self.run_pair([a],[b],'FAIL')
    def test_nested_partial(self):
        a=event();a['inputs']=rep({'inner':{'status':'partial_unrepresentable','reason':'test'}});self.run_pair([a],[a],'INCOMPLETE')
    def test_unordered(self):
        a=event();a['inputs']=rep({'$unordered_set_NONCANONICAL':[1,2]});self.run_pair([a],[a],'INCOMPLETE')
    def test_pre_inputs_change(self):
        a=event();a['pre_inputs']=rep(1);b=copy.deepcopy(a);b['pre_inputs']=rep(2);self.run_pair([a],[b],'FAIL')
    def test_missing_input(self):
        a=event();del a['inputs'];self.run_pair([a],[a],'INCOMPLETE')
    def test_missing_event(self):self.run_pair([event(),event('two')],[event()],'FAIL')
    def test_cross_family_order(self):self.run_pair([event('one'),event('two')],[event('two'),event('one')],'FAIL')
    def test_unbalanced_boundary(self):
        a={'stage':'trading_pipeline','method':'timed.stage_start','direction':'unclassified','phase_label':'A','result':rep(None)};self.run_pair([a],[a],'FAIL')
    def test_exact_known_hint(self):
        a=event('EZoneDetector._zone',rep({'$args':rep({'$tuple':['family',1,'S']}),'$kwargs':rep({'$mapping':[['another',1]]})}));a['stage']='e_zone_detector';b=copy.deepcopy(a);b['inputs']['value']['$kwargs']['value']['$mapping'].append(['pre_registered_s',True]);r=self.run_pair([a],[b],'PASS');self.assertEqual(r['known_exact_v81_call_hint_drifts'],1)
        b['inputs']['value']['$kwargs']['value']['$mapping'][1][1]=False;self.run_pair([a],[b],'FAIL')
    def test_duplicate_key(self):
        with tempfile.TemporaryDirectory() as t:
            a,b=Path(t)/'a.gz',Path(t)/'b.gz';write(a,[event()]);
            with gzip.open(b,'wt') as f:f.write('{"schema":"'+SCHEMA+'","event_ordinal":1,"event_ordinal":1}\n')
            self.assertEqual(compare(a,b)['selected_event_status'],'FAIL')
    def test_excluded_only(self):
        a=event('_parent_stop');a['stage']='e_zone_detector';a['method']='EZoneDetector._parent_stop';self.run_pair([a],[a],'FAIL')
if __name__=='__main__':unittest.main(verbosity=2)
