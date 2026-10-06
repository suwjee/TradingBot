"""Observation-only hooks: original functions and return values are unchanged."""
from pathlib import Path
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from time import perf_counter
import argparse, importlib.util, json, sys

OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
from run_raw_matrix import command

def normalize(value):
    if isinstance(value,datetime): return value.isoformat(sep=' ')
    if isinstance(value,Decimal): return str(value)
    if is_dataclass(value): return normalize(asdict(value))
    if isinstance(value,dict): return {str(k):normalize(v) for k,v in value.items()}
    if isinstance(value,(tuple,list,set,frozenset)): return [normalize(v) for v in value]
    if value is None or isinstance(value,(str,int,float,bool)): return value
    if hasattr(value,'__dict__'): return normalize(vars(value))
    return repr(value)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--raw-index',type=int,default=8)
    parser.add_argument('--timeframe',type=int,default=30)
    parser.add_argument('--order-ties',action='store_true')
    args=parser.parse_args()
    raw=json.loads((OUT/'raw-registry.json').read_text(encoding='utf-8'))[args.raw_index]
    path=OUT/'package/bridge/trading_pipeline.py'
    spec=importlib.util.spec_from_file_location('audit_bridge',path)
    bridge=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=bridge
    spec.loader.exec_module(bridge)
    engine_args=bridge.parse_arguments(command(Path(raw['path']),args.timeframe,raw['first'],raw['last'])[3:])
    events=[]
    timings={}
    engines=bridge.load_engines(engine_args,timings)
    market=bridge.prepare_market_context(engine_args,engines,timings)
    if args.order_ties:
        first_original=engines.e_zone.EZoneDetector._first_order
        zone_original=engines.e_zone.EZoneDetector._zone
        pending=[]
        def first_order_trace(self,*params,**kwargs):
            result=first_original(self,*params,**kwargs)
            candidates=[x for x in self.order_candidates(*params,**kwargs) if x[6] is not None]
            expected=min(candidates,key=lambda x:(x[6][2],-int(x[1].first_idx)),default=None)
            if result is not None and expected is not None and result[1].first_idx!=expected[1].first_idx:
                pending.append({'kind':'order-tie-subroute','direction':self.direction,'parentStop':normalize(params[0]),
                                'actualFirst':result[1].first_idx,'actualBreak':result[1].break_idx,
                                'expectedFirst':expected[1].first_idx,'expectedBreak':expected[1].break_idx,
                                'actualConfirmation':normalize(result[2]),'expectedConfirmation':normalize(expected[2]),
                                'sameStrictStop':normalize(expected[6][2]),
                                'actualRoutes':normalize(result[7]),'expectedRoutes':normalize(expected[7])})
            return result
        def zone_trace(self,*params,**kwargs):
            before=len(pending)
            result=zone_original(self,*params,**kwargs)
            for issue in pending[before:]:
                issue['zone']=normalize(result)
                issue['wrongOrderSurvivesZone']=result is not None and result.order_first_index==issue['actualFirst']
                events.append(issue)
            del pending[before:]
            return result
        engines.e_zone.EZoneDetector._first_order=first_order_trace
        engines.e_zone.EZoneDetector._zone=zone_trace
    full_original=bridge.calculate_full_direction_state
    def full_trace(*params,**kwargs):
        state=full_original(*params,**kwargs)
        direction=params[0]
        events.append({'kind':'full-direction-pass','direction':direction,
                       'inputOrderBLegs':normalize(kwargs.get('order_b_legs',())),
                       'allA':normalize(state.a_zones),'eligibleA':normalize(state.s_detector.eligible_a_zones),
                       'ownershipWindows':normalize(state.s_detector.a_ownership_windows),
                       'initialS':normalize(state.initial_s_zones),'sCandidates':normalize(state.s_candidates),
                       'acceptedS':normalize(state.s_zones),'E':normalize(state.e_zones),
                       'invalidA':normalize(state.invalid_a_identities),'invalidS':normalize(state.invalid_s_identities)})
        return state
    bridge.calculate_full_direction_state=full_trace
    original=engines.e_zone.discover_accepted_order_b_reset_legs
    def discovery(*params,**kwargs):
        result=original(*params,**kwargs)
        events.append({'kind':'order-b-discovery','direction':params[0],
                       'acceptedAInput':normalize(params[5]),'invalidA':normalize(params[6]),
                       'acceptedS':normalize(params[7]),'acceptedE':normalize(params[8]),
                       'acceptedStopAll':normalize(params[9]),'legs':normalize(result)})
        return result
    engines.e_zone.discover_accepted_order_b_reset_legs=discovery
    started=perf_counter()
    state=bridge.prepare_pipeline_state(engine_args,engines,market,timings)
    payload=bridge.build_response_payload(engine_args,engines,market,state,timings,started)
    target=OUT/'traces'
    target.mkdir(exist_ok=True)
    name=f'raw-{args.raw_index:02d}-{args.timeframe}s'+('-ties' if args.order_ties else '')
    (target/(name+'.events.json')).write_text(json.dumps(events,indent=2),encoding='utf-8')
    (target/(name+'.payload.json')).write_text(json.dumps(payload,separators=(',',':')),encoding='utf-8')
    payload.pop('timings',None)
    prior=OUT/f'raw-{args.timeframe}s'/f'raw-{args.raw_index:02d}-{args.timeframe}s-1.stdout.json'
    equality=None
    if prior.exists():
        baseline=json.loads(prior.read_bytes())
        baseline.pop('timings',None)
        equality=payload==baseline
        if not equality: raise AssertionError('Observation hooks changed stable output')
    print(json.dumps({'events':len(events),'stableUninstrumentedEquality':equality,
                      'wallSeconds':perf_counter()-started,'path':str(target/(name+'.events.json'))}))

if __name__=='__main__': main()
