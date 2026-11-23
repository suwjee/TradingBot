#!/usr/bin/env python3
"""Test-only in-process semantic event observer for pinned and V8.1 TradingBot.

No production module is edited, no output object is mutated or sorted. This is
selected function entry/return coverage, NOT proof of complete internal trace.
"""
from __future__ import annotations

import argparse
import collections
import dataclasses
import functools
import gzip
import hashlib
import importlib.util
import json
import os
import sys
import traceback
import time
import psutil
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

SCHEMA = 'tradingbot.v9.internal-observer.v2'
TRACED = {
    'reaction_engine': {'_append_reaction', '_append_reset', 'canonical_order_stop', 'detect'},
    'blue_line_detector': {'_build_reset_blue_line', 'detect_blue_lines', 'detect', 'update'},
    'a_zone_detector': {'_detect_ordinary_a', '_zone', 'detect_a_zones', 'detect'},
    's_zone_detector': {'_resolve_candidate', '_build_order_backed_zone', 'detect_s_zones', 'detect', 'reconcile_shared_order_stops'},
    'e_zone_detector': {'_zone', '_build_zone', '_discover_candidate_chains', '_reconcile_candidate_chains',
                         '_compute_reconciliation', '_parent_stop', '_register_order_audit', 'detect',
                         'rebuild_accepted_order_audit', 'continuation_chain_from_s'},
    'order_audit_engine': {'_register_order_audit', 'order_candidates', '_direct_parent_stop_order',
                           '_compute_direct_parent_stop_order', '_rebuild_accepted_order_audit', 'rebuild_accepted_order_audit',
                           'discover_order_b_reset_legs', 'cross_order'},
    'lifecycle_engine': {'_detect_events', 'detect', 'detect_stopalls', 'reconcile_stopall_lifecycle', 'update'},
    'PL_PH_detector': {'detect_bullish', 'detect_bearish', 'update'},
}
WATCHED_STATE = {
    'e_zone_detector': ('_last_candidate_zones', '_accepted_e_source_identities', 'order_audit',
                        'visual_lifecycle_starts', '_consumed_s_evidence'),
    's_zone_detector': ('_accepted_s_source_identities',),
    'reaction_engine': (),
    'order_audit_engine': ('order_audit',),
}
class Unsupported(Exception):
    pass

def stable_object(obj, depth=0, max_depth=12, allow_namespace=False):
    """Lossless for supported primitives/dataclasses/ordered mappings/sequences.
    Raise for unsupported representations rather than fabricating semantic parity.
    """
    if depth > max_depth:
        raise Unsupported('nested_depth_exceeded')
    if obj is None or type(obj) in (str, int, bool):
        return obj
    if type(obj) is float:
        return {'$float_repr': repr(obj)}
    if isinstance(obj, Decimal):
        return {'$decimal': str(obj)}
    if isinstance(obj, datetime):
        return {'$datetime': obj.isoformat(sep=' ')}
    if isinstance(obj, date):
        return {'$date': obj.isoformat()}
    if isinstance(obj, SimpleNamespace):
        if not allow_namespace:
            raise Unsupported('namespace_seen_in_non_ledger_hot_path')
        return {'$simple_namespace': [[k,stable_object(v,depth+1,max_depth,allow_namespace)]
                                     for k,v in vars(obj).items()]}
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {'$class': type(obj).__module__ + '.' + type(obj).__qualname__,
                '$fields': [[f.name, stable_object(getattr(obj, f.name), depth+1, max_depth, allow_namespace)] for f in dataclasses.fields(obj)]}
    if isinstance(obj, (tuple,list)):
        return {'$tuple' if isinstance(obj,tuple) else '$list': [stable_object(x,depth+1,max_depth,allow_namespace) for x in obj]}
    if isinstance(obj, dict):
        return {'$mapping': [[stable_object(k,depth+1,max_depth,allow_namespace),stable_object(v,depth+1,max_depth,allow_namespace)] for k,v in obj.items()]}
    if isinstance(obj, (set,frozenset)):
        # No set sorting: exact iteration representation is retained, and marked as
        # non-canonical because hash ordering is not a semantic ordering.
        return {'$unordered_set_NONCANONICAL': [stable_object(x,depth+1,max_depth,allow_namespace) for x in obj]}
    raise Unsupported('unsupported_type:' + type(obj).__module__+'.'+type(obj).__qualname__)

def representation(obj, *, allow_namespace=False, max_depth=12):
    try: return {'status': 'complete_supported', 'value': stable_object(obj,0,max_depth,allow_namespace)}
    except (Unsupported, RecursionError) as e:
        return {'status':'partial_unrepresentable', 'reason':str(e), 'type':type(obj).__name__}


def entity_fields(obj):
    fields = ('source_time','source_index','decision_event_time','stop_event_time',
              'first_time','confirmation_time','event_time','index','first_idx',
              'parent_type','parent_source_time','parent_source_index','number','color',
              'order_first_index','order_break_index','family','direction')
    return {k: representation(getattr(obj,k)) for k in fields if hasattr(obj,k)}


def event_epoch(obj):
    for k in ('decision_event_time','stop_event_time','source_time','event_time','confirmation_time','time'):
        if hasattr(obj,k):
            v=getattr(obj,k)
            if isinstance(v,datetime):
                if v.tzinfo is None:
                    return {'raw_time_local_iran':v.isoformat(sep=' '),'raw_epoch_derived':int(v.replace(tzinfo=ZoneInfo('Asia/Tehran')).timestamp())}
                return {'raw_time_local_iran':v.isoformat(sep=' '),'raw_epoch_derived':int(v.timestamp())}
            if type(v) in (int,str):return {'raw_time_observed':v}
    return {}


def state_snapshot(module_name, inst):
    result={}
    for k in WATCHED_STATE.get(module_name, ()):
        if hasattr(inst,k):
            v=getattr(inst,k)
            if isinstance(v,(list,tuple,dict,set,frozenset)):
                result[k]={'count':len(v)}
                # Full state only once in a detector-scope finalization event,
                # rather than multiplying its whole O(N) ledger per call.
            else:result[k]=representation(v)
    return result

# These are authoritative ledgers, NOT performance caches. A complete
# read-only view is attempted only at coarse stage boundaries to avoid
# quadratic logging cost in the candidate hot loops.
AUTHORITATIVE_BOUNDARIES = {
    'e_zone_detector': {
        'detect': ('order_audit','_accepted_e_source_identities',
                   '_last_candidate_zones','visual_lifecycle_starts',
                   '_consumed_s_evidence'),
        'rebuild_accepted_order_audit': ('order_audit',),
    },
    's_zone_detector': {
        'detect': ('order_audit','a_ownership_windows'),
    },
    'order_audit_engine': {
        'rebuild_accepted_order_audit': ('order_audit',),
    },
}

def authoritative_boundary_snapshot(stage, method, instance):
    if instance is None:return None
    short_name=method.split('.')[-1]
    fields=AUTHORITATIVE_BOUNDARIES.get(stage,{}).get(short_name)
    if not fields:return None
    ans={'coverage':'EXACT_ORDERED_LEDGER_CONTENT_IF_SUPPORTED',
         'fields':{}}
    for field in fields:
        if hasattr(instance,field):
            ans['fields'][field]=representation(getattr(instance,field),allow_namespace=True,max_depth=32)
        else:
            ans['fields'][field]={'status':'not_present'}
    return ans

class EventWriter:
    def __init__(self, dest):
        self.dest=Path(dest)
        self.dest.parent.mkdir(parents=True, exist_ok=True)
        self.fp=self.dest.open('wb')
        self.gz=gzip.GzipFile(fileobj=self.fp,mode='wb',filename='',mtime=0,compresslevel=5)
        self.ordinal=0
        self.uncompressed=0
        self.digest=hashlib.sha256()
        self.counts=collections.Counter()
        self.unsupported=collections.Counter()
        self.checkpoints=[]
        self.active=False
    def emit(self, payload):
        if self.active:raise RuntimeError('Recursive Trace emission')
        self.active=True
        try:
            self.ordinal+=1
            payload={'schema':SCHEMA,'event_ordinal':self.ordinal,**payload}
            raw=json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf8')+b'\n'
            if self.ordinal==1 or (self.ordinal-1)%2000==0:
                self.checkpoints.append({'event_ordinal':self.ordinal,'uncompressed_byte_offset':self.uncompressed})
            self.gz.write(raw);self.digest.update(raw)
            self.uncompressed+=len(raw)
            self.counts[payload.get('stage','unclassified')+':'+payload.get('method','?')]+=1
            for name in ('result','inputs'):
                if payload.get(name,{}).get('status') == 'partial_unrepresentable':
                    self.unsupported[name+':'+payload['stage']+':'+payload['method']]+=1
        finally:self.active=False
    def close(self):
        self.gz.close();self.fp.close()
        m={'schema':SCHEMA,'coverage':'SELECTED_IN_PROCESS_CALL_RETURN_WITH_SELECTED_FULL_AUTHORITATIVE_BOUNDARIES',
           'events':self.ordinal,'jsonl_sha256':self.digest.hexdigest(),
           'gzip_sha256':hashlib.sha256(self.dest.read_bytes()).hexdigest(),
           'uncompressed_bytes':self.uncompressed,'index':self.checkpoints,
           'families':dict(self.counts),'unsupported_counts':dict(self.unsupported)}
        (Path(str(self.dest)+'.manifest.json')).write_text(json.dumps(m,indent=2),encoding='utf8')
        return m


def instrument_module(module, writer):
    name=module.__name__
    if name not in TRACED:return
    selected=TRACED[name]
    def decorate(func,stage,method):
        @functools.wraps(func)
        def observer(*args,**kwargs):
            self_obj=args[0] if args and hasattr(args[0],'__dict__') and not dataclasses.is_dataclass(args[0]) else None
            before=state_snapshot(stage,self_obj) if self_obj is not None else {}
            before_ledger=authoritative_boundary_snapshot(stage,method,self_obj)
            # Only semantically significant mutating entry points read their
            # pre-call arguments. Avoid copying historical arrays per hot-loop.
            include_pre=(stage=='lifecycle_engine' and method.endswith('._detect_events'))
            pre_inputs=representation(args[1:] if self_obj is not None else args) if include_pre else None
            life_output=None;life_before_len=None
            if include_pre and len(args)>3 and isinstance(args[3],list):
                life_output=args[3]
                life_before_len=len(life_output)
            if stage=='e_zone_detector' and method.endswith('._zone'):
                try:
                    import v9_meter
                    v9_meter.LAST_REASON=None
                except ImportError:pass
            output=func(*args,**kwargs)
            after=state_snapshot(stage,self_obj) if self_obj is not None else {}
            after_ledger=authoritative_boundary_snapshot(stage,method,self_obj)
            observed_direction=getattr(self_obj,'direction',None)
            if observed_direction is None:
                observed_direction=next((v for v in args if v in ('bullish','bearish')),None) if args else None
            input_args=args[1:] if self_obj is not None else args
            # Bound representation limit is explicit; no partial trace counts as full verification.
            in_repr=representation(input_args)
            if kwargs:in_repr={'status':'complete_supported','value':{'$args':in_repr,'$kwargs':representation(kwargs)}}
            r_repr=representation(output)
            time_hints=event_epoch(output) if not isinstance(output,(list,tuple)) else (event_epoch(output[0]) if output else {})
            event={'stage':stage,'method':method,'direction':observed_direction,
                   'inputs':in_repr,'result':r_repr,
                   'pre_state':before,'post_state':after,**time_hints}
            if pre_inputs is not None:
                event['pre_inputs']=pre_inputs
            if life_output is not None:
                event['lifecycle_new_events']=representation(life_output[life_before_len:])
                event['lifecycle_output_count_before']=life_before_len
                event['lifecycle_output_count_after']=len(life_output)
                if len(life_output)<life_before_len:
                    event['lifecycle_existing_state_changed_unverified']=True
            if before_ledger is not None or after_ledger is not None:
                event['authoritative_boundary_state']={'pre':before_ledger,'post':after_ledger}
            if hasattr(output, '__dataclass_fields__'):
                event['entity_provenance']=entity_fields(output)
            elif isinstance(output,(tuple,list)) and output and hasattr(output[0], '__dataclass_fields__'):
                event['first_entity_provenance']=entity_fields(output[0])
            if output is None:
                event['decision']='no_result_or_rejected_undetermined'
                if stage=='e_zone_detector' and method.endswith('._zone'):
                    try:
                        import v9_meter
                        if v9_meter.LAST_REASON:event['rejection_reason']=v9_meter.LAST_REASON
                    except ImportError:pass
            elif output is False:event['decision']='false_return_unknown_reason'
            writer.emit(event)
            return output
        return observer
    for key,obj in vars(module).copy().items():
        if isinstance(obj,type) and getattr(obj,'__module__',None)==name:
            for method in selected:
                if method not in obj.__dict__: continue
                underlying=obj.__dict__[method]
                if isinstance(underlying,(staticmethod,classmethod)):
                    fn=underlying.__func__;wrapped=decorate(fn,name,obj.__name__+'.'+method)
                    setattr(obj,method,staticmethod(wrapped) if isinstance(underlying,staticmethod) else classmethod(wrapped))
                elif callable(underlying):setattr(obj,method,decorate(underlying,name,obj.__name__+'.'+method))
        elif key in selected and callable(obj) and getattr(obj,'__module__',None)==name:
            setattr(module,key,decorate(obj,name,key))


def execute(args):
    root=args.engine_root.resolve()
    sys.path.insert(0,str(root/'bridge'))
    spec=importlib.util.spec_from_file_location('trading_pipeline',root/'bridge/trading_pipeline.py')
    pipeline=importlib.util.module_from_spec(spec)
    sys.modules['trading_pipeline']=pipeline
    spec.loader.exec_module(pipeline)
    writer=EventWriter(args.trace_out) if args.trace_out else None
    stage_metrics=[]
    proc_for_stages=psutil.Process() if args.stage_profile else None
    if writer is not None:
        # Top-level import uses order_audit_engine before load_engines() runs.
        for mod_name in ('order_audit_engine','core_utils'):
            if mod_name in sys.modules:instrument_module(sys.modules[mod_name],writer)
        original_loader=pipeline.load_module
        def observe_loaded(name,path):
            mod=original_loader(name,path)
            instrument_module(mod,writer)
            return mod
        pipeline.load_module=observe_loaded
        # Native stage handoff order is traced in its actual executed order.
        # This wrapper delegates to exactly the original timed() function;
        # output fields and trading state are never replaced or reordered.
        original_timed=pipeline.timed
        def observed_timed(timings,label,work):
            writer.emit({'stage':'trading_pipeline','method':'timed.stage_start',
                         'direction':'unclassified','phase_label':label,
                         'result':{'status':'complete_supported','value':None}})
            if proc_for_stages is not None:
                before_wall=time.perf_counter_ns()
                before_cpu=time.process_time_ns()
                before_rss=proc_for_stages.memory_info().rss
            returned=original_timed(timings,label,work)
            if proc_for_stages is not None:
                after_wall=time.perf_counter_ns()
                after_cpu=time.process_time_ns()
                after_rss=proc_for_stages.memory_info().rss
                stage_metrics.append({'ordinal':len(stage_metrics)+1,
                                      'label':label,'wall_ms':round((after_wall-before_wall)/1e6,5),
                                      'process_cpu_ms':round((after_cpu-before_cpu)/1e6,5),
                                      'rss_before_mib':round(before_rss/1048576,3),
                                      'rss_after_mib':round(after_rss/1048576,3),
                                      'note':'per-stage wall/CPU measured with observer ON; RSS start/end, not peak'})
            writer.emit({'stage':'trading_pipeline','method':'timed.stage_end',
                         'direction':'unclassified','phase_label':label,
                         'result':representation(returned)})
            return returned
        pipeline.timed=observed_timed
    argv=[str(root/'bridge/trading_pipeline.py')]
    names=[('reaction-engine','reaction_engine.py'),('blue-line-engine','blue_line_detector.py'),
           ('a-zone-engine','a_zone_detector.py'),('s-zone-engine','s_zone_detector.py'),
           ('e-zone-engine','e_zone_detector.py'),('lifecycle-engine','lifecycle_engine.py')]
    for flag,name in names:argv+=['--'+flag,str(root/'pipeline'/name)]
    argv+=['--data',str(args.raw),'--timeframe','30','--raw-timeframe','5',
           '--direction','both','--from-time',str(args.from_time),'--to-time',str(args.to_time),
           '--blue-lines','enabled','--a-zones','enabled','--s-zones','enabled','--pl-ph','enabled','--bridge-output']
    sys.argv=argv
    try:return pipeline.main()
    finally:
        if args.meter_output:
            import v9_meter
            v9_meter.save(args.meter_output)
        if writer is not None:
            meta=writer.close()
            if args.summary:
                Path(args.summary).write_text(json.dumps(meta,indent=2),encoding='utf8')
        if args.stage_profile:
            Path(args.stage_profile).parent.mkdir(exist_ok=True,parents=True)
            Path(args.stage_profile).write_text(json.dumps({'coverage':'instrumented phase call CPU and RSS endpoints, not exclusive cProfile time','stages':stage_metrics},indent=2),encoding='utf8')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--engine-root',type=Path,required=True)
    p.add_argument('--raw',type=Path,required=True)
    p.add_argument('--from-time',type=int,required=True)
    p.add_argument('--to-time',type=int,required=True)
    p.add_argument('--trace-out',type=Path)
    p.add_argument('--summary',type=Path)
    p.add_argument('--meter-output',type=Path)
    p.add_argument('--stage-profile',type=Path)
    a=p.parse_args()
    try:sys.exit(execute(a))
    except Exception as ex:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
