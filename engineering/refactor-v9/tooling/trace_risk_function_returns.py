#!/usr/bin/env python3
"""Test-only read-only provenance of AST mutation-risk method returns.

This extends observation coverage without editing engine or claiming that
partial function return summaries are complete semantic state transition traces.
"""
from __future__ import annotations
import argparse,collections,dataclasses,gzip,hashlib,json,sys,time
from pathlib import Path
from datetime import date,datetime
from decimal import Decimal
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import semantic_trace_v3 as observer

SCHEMA='tradingbot.v9.risk-return-call-coverage.v1'
WATCH=('order_audit','_accepted_e_source_identities','_accepted_s_source_identities',
       '_last_candidate_zones','_sequence_resets','_sequence_reset_times',
       '_consumed_s_evidence','visual_lifecycle_starts','_source_ledgers',
       '_stopall_events','_primary_highs','_primary_lows','reactions','resets')

def scalar(v):
    if v is None or type(v) in (bool,int,str):return {'type':type(v).__name__,'value':v,'coverage':'EXACT_SCALAR'}
    if isinstance(v,Decimal):return {'type':'Decimal','value':str(v),'coverage':'EXACT_SCALAR'}
    if isinstance(v,(date,datetime)):return {'type':type(v).__name__,'value':v.isoformat(),'coverage':'EXACT_SCALAR'}
    if type(v) is float:return {'type':'float','value':repr(v),'coverage':'EXACT_REPR_NONPRICE_ONLY'}
    if isinstance(v,dict):return {'type':'mapping','length':len(v),'coverage':'COUNT_ONLY'}
    if isinstance(v,(list,tuple,set,frozenset)):return {'type':type(v).__name__,'length':len(v),'coverage':'COUNT_ONLY'}
    if dataclasses.is_dataclass(v) and not isinstance(v,type):
        fields={}
        for f in dataclasses.fields(v):
            k=f.name
            if k in ('source_time','source_index','event_time','decision_event_time','direction','parent_type','parent_source_time','parent_source_index','number','index','first_idx','color','status','accepted','value'):
                fields[k]=scalar(getattr(v,k))
        return {'type':type(v).__module__+'.'+type(v).__qualname__,'fields':fields,'coverage':'SAMPLED_DOMAIN_FIELDS_ONLY'}
    return {'type':type(v).__module__+'.'+type(v).__name__,'coverage':'UNSUPPORTED_EXPLICIT'}

def watched(obj):
    if not hasattr(obj,'__dict__'):return {}
    d=vars(obj)
    result={}
    for k in WATCH:
        if k in d:
            v=d[k]
            if isinstance(v,(dict,list,tuple,set,frozenset)):
                result[k]={'type':type(v).__name__,'length':len(v),'coverage':'COUNT_ONLY'}
            else:result[k]=scalar(v)
    return result

def run(engine,raw,first,last,inventory,trace,manifest):
    engine=Path(engine).resolve();raw=Path(raw).resolve();trace=Path(trace)
    inv=json.loads(Path(inventory).read_text())
    risk={(Path(x['file']).name,x['function'].split('.')[-1]) for x in inv['untraced_mutators']}
    active={};counts=collections.Counter();unsupported=collections.Counter();digest=hashlib.sha256();n=0
    trace.parent.mkdir(exist_ok=True,parents=True)
    with trace.open('wb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0,compresslevel=3) as z:
            def profiler(frame,event,arg):
                nonlocal n
                if event not in ('call','return'):return
                code=frame.f_code
                fn=code.co_filename
                if not fn.startswith(str(engine)):return
                k=(Path(fn).name,code.co_name)
                if k not in risk:return
                if event=='call':
                    inst=frame.f_locals.get('self')
                    active[id(frame)]=watched(inst) if inst is not None else {}
                else:
                    pre=active.pop(id(frame),{})
                    inst=frame.f_locals.get('self')
                    post=watched(inst) if inst is not None else {}
                    r=scalar(arg)
                    n+=1
                    ev={'schema':SCHEMA,'event_ordinal':n,'module':k[0],'method':k[1],
                        'source_first_line':code.co_firstlineno,
                        'return':r,'pre_selected_state':pre,'post_selected_state':post}
                    value=json.dumps(ev,separators=(',',':'),ensure_ascii=False).encode()+b'\n'
                    z.write(value);digest.update(value)
                    counts[k[0]+':'+k[1]]+=1
                    if r['coverage'] not in ('EXACT_SCALAR','EXACT_REPR_NONPRICE_ONLY'):unsupported[r['coverage']]+=1
            previous=sys.getprofile();sys.setprofile(profiler)
            try:
                rc=observer.execute(SimpleNamespace(engine_root=engine,raw=raw,
                  from_time=int(first),to_time=int(last),trace_out=None,summary=None,meter_output=None,stage_profile=None))
            finally:
                sys.setprofile(previous)
    m={'schema':SCHEMA,'coverage':'ALL_AST_RISK_METHOD_RETURNS_WITH_SCALAR_EXACT_COUNT_ONLY_COMPLEX_TYPES',
       'engine_root':str(engine),'raw':str(raw),'native_exit_code':rc,
       'events':n,'uncompressed_sha256':digest.hexdigest(),
       'gzip_sha256':hashlib.sha256(trace.read_bytes()).hexdigest(),
       'families':dict(counts),'partial_return_families':dict(unsupported),
       'not_proven':'All mutation order, exact mutable domain state, chronology, arbitrary Live state.'}
    Path(manifest).write_text(json.dumps(m,indent=2))
    return rc
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('engine','raw','first','last','inventory','trace','manifest'):
        p.add_argument('--'+name,required=True)
    a=p.parse_args()
    raise SystemExit(run(a.engine,a.raw,a.first,a.last,a.inventory,a.trace,a.manifest))