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
import types
import psutil
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

SCHEMA = 'tradingbot.v9.internal-observer.v9'
_CONTEXT_WRITER=None

def stream_file_sha256(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

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
    if isinstance(obj, bytes):
        # The input is SHA-pinned and stored separately, not an ambiguous
        # decoded string; digest + byte length are the stable source reference.
        return {'$immutable_bytes_source':{'length':len(obj),'sha256':hashlib.sha256(obj).hexdigest()}}
    if isinstance(obj, types.ModuleType):
        # Imported source is independently pinned by 15 Git blob hashes.
        return {'$module_import_identity':obj.__name__}
    if isinstance(obj, timedelta):
        return {'$timedelta_total_microseconds':(obj.days*86400+obj.seconds)*1000000+obj.microseconds}
    if type(obj).__name__=='MarketChronology' and type(obj).__module__=='reaction_engine':
        if _CONTEXT_WRITER is None:
            raise Unsupported('market_chronology_requires_trace_sidecar')
        return {'$immutable_chronology_ref':_CONTEXT_WRITER.save_chronology(obj)}
    if isinstance(obj, datetime):
        return {'$datetime': obj.isoformat(sep=' ')}
    if isinstance(obj, date):
        return {'$date': obj.isoformat()}
    if isinstance(obj, SimpleNamespace):
        if not allow_namespace:
            raise Unsupported('namespace_seen_in_non_ledger_hot_path')
        return {'$simple_namespace': [[k,stable_object(v,depth+1,max_depth,allow_namespace)]
                                     for k,v in vars(obj).items()]}
    if _CONTEXT_WRITER is not None and isinstance(obj,(list,tuple,dict)) and len(obj)>=32:
        # Large immutable Candle views and source Reaction Candidate ledgers
        # are copied once into independent lossless snapshot sidecars. The
        # original container order and every original dataclass field remain
        # present. Mutable Candidate freshness is separately flagged as a
        # coverage caveat; it is NOT silently asserted immutable.
        representative=(next(iter(obj.values())) if isinstance(obj,dict) else obj[0])
        if (dataclasses.is_dataclass(representative) and
            type(representative).__module__=='reaction_engine' and
            type(representative).__name__ in ('Candle','Candidate')):
            return {'$ordered_collection_snapshot':_CONTEXT_WRITER.save_collection(obj, fresh=_CONTEXT_WRITER.force_fresh_collections)}
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
    writer=_CONTEXT_WRITER
    previous=writer.force_fresh_collections if writer else False
    if writer: writer.force_fresh_collections=True
    try:
        for field in fields:
            if hasattr(instance,field):
                ans['fields'][field]=representation(getattr(instance,field),allow_namespace=True,max_depth=32)
            else:
                ans['fields'][field]={'status':'not_present'}
    finally:
        if writer: writer.force_fresh_collections=previous
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
        self.context_refs={}
        self.context_files=[]
        self.collection_refs={}
        # Bounded LRU: retain source identity only while a strong reference is
        # held. Eviction deletes id->ref, so Python id reuse can NEVER lead to
        # an incorrect recycled snapshot. A later encounter is serialized again.
        self.collection_objects=collections.OrderedDict()
        self.collection_weights={}
        self.collection_retained_estimate=0
        self.collection_retention_budget=64*1024*1024
        self.collection_max_objects=8
        self.collection_evictions=0
        self.collection_nonretained=0
        self.collection_files=[]
        self.stage_output_files=[]
        self.force_fresh_collections=False
    def save_collection(self,source, fresh=False):
        key=id(source)
        sample=(next(iter(source.values())) if isinstance(source,dict) else source[0])
        is_mutable=type(sample).__name__!='Candle'
        if key in self.collection_refs:
            # Strict proof against id reuse: same object held strongly for every
            # active mapping, or there is no entry and we capture a fresh copy.
            if self.collection_objects.get(key) is not source:
                raise AssertionError('V5 collection identity unexpectedly changed')
            self.collection_objects.move_to_end(key)
            if not (fresh and is_mutable):
                return self.collection_refs[key]
        ordinal=len(self.collection_files)+1
        dest=Path(str(self.dest)+f'.collection.{ordinal:04d}.jsonl.gz')
        entries=source.items() if isinstance(source,dict) else enumerate(source)
        n=0;bytes_count=0;digest=hashlib.sha256()
        fp=dest.open('wb')
        try:
            with gzip.GzipFile(fileobj=fp,mode='wb',filename='',mtime=0,compresslevel=5) as z:
                for position,value in entries:
                    row={'source_ordinal':n,'source_key':stable_object(position,0,32,allow_namespace=True),
                         'source_value':stable_object(value,0,32,allow_namespace=True)}
                    payload=json.dumps(row,ensure_ascii=False,separators=(',',':')).encode()+b'\n'
                    digest.update(payload);z.write(payload);n+=1;bytes_count+=len(payload)
        finally:fp.close()
        element_type=type(sample).__name__
        immutable=(element_type=='Candle')
        summary={'file':dest.name,'entry_count':n,'container_kind':type(source).__name__,
                 'element_type':element_type,'source_candle_frozen':immutable,
                 'candidate_content_is_snapshot_at_first_use_only':not immutable and not fresh,
                 'fresh_boundary_snapshot':bool(fresh and is_mutable),
                 'jsonl_sha256':digest.hexdigest(),'gzip_sha256':stream_file_sha256(dest),
                 'uncompressed_bytes':bytes_count,
                 'snapshot_ordinal':ordinal}
        self.collection_files.append(summary)
        # Snapshot ordinal and memory-cache generation are implementation
        # details; semantic event references use content digests and lengths.
        stable_ref={k:v for k,v in summary.items() if k in
                   ('entry_count','container_kind','element_type','jsonl_sha256','source_candle_frozen',
                    'candidate_content_is_snapshot_at_first_use_only','fresh_boundary_snapshot')}
        if key in self.collection_objects:
            # Replace the snapshot for an explicitly refreshed mutable ledger.
            self.collection_refs[key]=stable_ref
            return stable_ref
        # This estimate is intentionally conservative. It limits strong
        # reference retention, NOT actual Engine memory or input history.
        weight=64+len(source)*(256 if immutable else 512)
        if weight>self.collection_retention_budget:
            self.collection_nonretained+=1
            # No memo entry is created, so later encounters cannot reuse an
            # out-of-date or id-colliding snapshot.
            return stable_ref
        while self.collection_objects and (
            len(self.collection_objects)>=self.collection_max_objects or
            self.collection_retained_estimate+weight>self.collection_retention_budget
        ):
            old_key,_=self.collection_objects.popitem(last=False)
            self.collection_refs.pop(old_key,None)
            self.collection_retained_estimate-=self.collection_weights.pop(old_key)
            self.collection_evictions+=1
        self.collection_objects[key]=source
        self.collection_refs[key]=stable_ref
        self.collection_weights[key]=weight
        self.collection_retained_estimate+=weight
        return stable_ref
    def safe_stage_value(self, value, label, depth=0):
        """Lossless recursive composition; stream EACH large nested sequence.

        This avoids the unsafe case of a tiny dict containing a million-element
        list and never materializes a huge stable_object tree in Python RAM.
        """
        if depth>32:
            return {'status':'partial_unrepresentable','reason':'stage_nested_depth_exceeded'}
        if isinstance(value,(list,tuple,dict)):
            if len(value)>12000:
                return self.save_large_stage_result(value,label)
            if isinstance(value,dict):
                values=[];complete=True
                for k,v in value.items():
                    kr=representation(k,allow_namespace=True,max_depth=32)
                    vr=self.safe_stage_value(v,label+'/'+str(k)[:50],depth+1)
                    complete=complete and kr['status']=='complete_supported' and vr['status']=='complete_supported'
                    values.append([kr.get('value',{'$unrepresentable':kr.get('reason')}),
                                   vr.get('value',{'$unrepresentable':vr.get('reason')})])
                return {'status':'complete_supported' if complete else 'partial_unrepresentable',
                        'value':{'$mapping':values}}
            values=[];complete=True
            for k,v in enumerate(value):
                vr=self.safe_stage_value(v,label+'/'+str(k),depth+1)
                complete=complete and vr['status']=='complete_supported'
                values.append(vr.get('value',{'$unrepresentable':vr.get('reason')}))
            return {'status':'complete_supported' if complete else 'partial_unrepresentable',
                    'value':{'$tuple' if isinstance(value,tuple) else '$list':values}}
        if dataclasses.is_dataclass(value) and not isinstance(value,type):
            flds=[];complete=True
            for field in dataclasses.fields(value):
                vr=self.safe_stage_value(getattr(value,field.name),label+'/'+field.name,depth+1)
                complete=complete and vr['status']=='complete_supported'
                flds.append([field.name,vr.get('value',{'$unrepresentable':vr.get('reason')})])
            return {'status':'complete_supported' if complete else 'partial_unrepresentable',
                    'value':{'$class':type(value).__module__+'.'+type(value).__qualname__,'$fields':flds}}
        return representation(value,allow_namespace=True,max_depth=32)

    def save_large_stage_result(self, value, label):
        """Lossless ordered stage return snapshot streamed record-by-record.

        Never materialize a million-element stable_object or json.dumps() in
        RAM. The digest in the stage event references the exact event-order
        sidecar, whose entire gzip and JSONL contents remain auditable.
        """
        ordinal=len(self.stage_output_files)+1
        dest=Path(str(self.dest)+f'.stage.{ordinal:04d}.jsonl.gz')
        entries=value.items() if isinstance(value,dict) else enumerate(value)
        digest=hashlib.sha256();uncompressed=0;count=0;partial=0
        with dest.open('wb') as raw:
            with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0,compresslevel=5) as zipf:
                for key,element in entries:
                    # Stable semantic output representation per element;
                    # original data is never sorted, modified or rounded.
                    rep=self.safe_stage_value(element,label+"/"+str(count),1)
                    if rep['status']!='complete_supported':partial+=1
                    row={'source_ordinal':count,
                         'source_key':representation(key,allow_namespace=True,max_depth=32),
                         'source_value':rep}
                    payload=json.dumps(row,ensure_ascii=False,separators=(',',':')).encode()+b'\n'
                    zipf.write(payload);digest.update(payload)
                    uncompressed+=len(payload);count+=1
        summary={'file':dest.name,'label':label,'record_count':count,
                 'container_kind':type(value).__name__,'partial_elements':partial,
                 'jsonl_sha256':digest.hexdigest(),
                 'gzip_sha256':stream_file_sha256(dest),
                 'uncompressed_bytes':uncompressed}
        self.stage_output_files.append(summary)
        return {'status':'complete_supported' if partial==0 else 'partial_unrepresentable',
                'value':{'$ordered_stage_output_ref':{'label':label,'count':count,
                         'container_kind':type(value).__name__,
                         'jsonl_sha256':digest.hexdigest(),
                         'partial_elements':partial}}}

    def save_chronology(self, chronology):
        """Lossless, deterministically ordered, separately compressed raw Candle data.

        Caches intentionally excluded; Candle state is the authoritative
        immutable underlying source. id() is an internal runtime memo only,
        NEVER emitted as an event identity.
        """
        key=id(chronology)
        if key in self.context_refs:return self.context_refs[key]
        ordinal=len(self.context_files)+1
        dest=Path(str(self.dest)+f'.chronology.{ordinal:04d}.jsonl.gz')
        raw_hash=hashlib.sha256();uncompressed=0;count=0
        fp=dest.open('wb')
        try:
            with gzip.GzipFile(fileobj=fp,mode='wb',filename='',mtime=0,compresslevel=5) as z:
                for name,sequence in (('main',chronology.candles),('lower_5s',chronology.seconds)):
                    for n,candle in enumerate(sequence):
                        row={'type':name,'ordinal':n,'source_candle':stable_object(candle,0,32,allow_namespace=True)}
                        payload=json.dumps(row,ensure_ascii=False,separators=(',',':')).encode('utf8')+b'\n'
                        z.write(payload);raw_hash.update(payload)
                        uncompressed+=len(payload);count+=1
        finally:fp.close()
        summary={'sidecar':dest.name,'record_count':count,
                 'main_count':len(chronology.candles),'lower_count':len(chronology.seconds),
                 'timeframe_us':int(chronology.timeframe.total_seconds()*1000000),
                 'jsonl_sha256':raw_hash.hexdigest(),
                 'gzip_sha256':stream_file_sha256(dest),
                 'uncompressed_bytes':uncompressed,
                 'meaning':'IMMUTABLE_INPUT_CANDLES_ONLY; derived caches not part of semantic state'}
        self.context_files.append(summary)
        # This content-addressed descriptor can be compared without mutable
        # Python process identity or sidecar path differences.
        descriptor={k:v for k,v in summary.items() if k in ('record_count','main_count','lower_count','timeframe_us','jsonl_sha256')}
        self.context_refs[key]=descriptor
        return descriptor
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
        m={'schema':SCHEMA,'coverage':'SELECTED_IN_PROCESS_RETURNS_AND_AUTHORITATIVE_BOUNDARIES; BOUNDED_STRONG_REF_LRU; NOT_ALL_MUTATIONS',
           'events':self.ordinal,'jsonl_sha256':self.digest.hexdigest(),
           'gzip_sha256':stream_file_sha256(self.dest),
           'uncompressed_bytes':self.uncompressed,'index':self.checkpoints,
           'families':dict(self.counts),'unsupported_counts':dict(self.unsupported),
           'chronology_input_sidecars':self.context_files,
           'ordered_collection_sidecars':self.collection_files,
           'ordered_stage_output_sidecars':self.stage_output_files,
           'strong_collection_retention_estimate_bytes':self.collection_retained_estimate,
           'strong_collection_retention_budget_bytes':self.collection_retention_budget,
           'collection_lru_evictions':self.collection_evictions,
           'collection_nonretained_snapshot_count':self.collection_nonretained}
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
            in_repr=representation(input_args,allow_namespace=True)
            if kwargs:in_repr={'status':'complete_supported','value':{'$args':in_repr,'$kwargs':representation(kwargs,allow_namespace=True)}}
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
                    fn=underlying.__func__;wrapped=decorate(fn,name,obj.__name__+'.'+method)                    setattr(obj,method,staticmethod(wrapped) if isinstance(underlying,staticmethod) else classmethod(wrapped))
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
    global _CONTEXT_WRITER
    _CONTEXT_WRITER=writer
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
                         'result':writer.safe_stage_value(returned,label)})
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