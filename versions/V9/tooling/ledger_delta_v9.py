"""Test-only reversible deltas for observed OrderAudit boundary snapshots.
No claim about intra-boundary transitions or complete Live state.
"""
from __future__ import annotations
import argparse, base64, collections, dataclasses, datetime as dt, gzip, hashlib, itertools, json, struct, sys, time
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

def encode(v): return json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')
def sha(v): return hashlib.sha256(v).hexdigest()
def b64(v): return base64.b64encode(v).decode('ascii')
def un64(v): return base64.b64decode(v,validate=True)

def snapshot(value):
    """Exact typed graph; references are traversal-local, not process addresses."""
    seen={}
    def visit(x):
        t=type(x)
        if x is None:return ['none']
        if t is bool:return ['bool',x]
        if t is int:return ['int',str(x)]
        if t is str:return ['str',x]
        if t is float:return ['float64',struct.pack('>d',x).hex()]
        if t is Decimal:
            a=x.as_tuple();return ['decimal',a.sign,list(a.digits),a.exponent]
        if t is bytes:return ['bytes',b64(x)]
        if t is dt.datetime:
            tz=x.tzinfo
            if tz is not None and type(tz) is not dt.timezone and type(tz).__module__!='zoneinfo':raise TypeError('Unsupported timezone')
            return ['datetime',x.isoformat(),x.fold,None if tz is None else [type(tz).__module__,type(tz).__qualname__,getattr(tz,'key',None),x.tzname()]]
        if t is dt.date:return ['date',x.isoformat()]
        if t is dt.timedelta:return ['timedelta',x.days,x.seconds,x.microseconds]
        if t not in (dict,list,tuple,set,frozenset,SimpleNamespace) and not (dataclasses.is_dataclass(x) and not isinstance(x,type)):raise TypeError('Unsupported snapshot type '+t.__module__+'.'+t.__qualname__)
        k=id(x)
        if k in seen:return ['ref',seen[k][0]]
        n=len(seen);seen[k]=(n,x)
        if t is dict:return ['dict',n,[[visit(k),visit(v)] for k,v in x.items()]]
        if t in (list,tuple,set,frozenset):return [t.__name__,n,[visit(v) for v in x]]
        if t is SimpleNamespace:return ['namespace',n,[[k,visit(v)] for k,v in vars(x).items()]]
        return ['dataclass',n,t.__module__+'.'+t.__qualname__,[[f.name,visit(getattr(x,f.name))] for f in dataclasses.fields(x)]]
    return encode(visit(value))

def make_delta(before,after):
    p=0;lim=min(len(before),len(after))
    while p<lim and before[p]==after[p]:p+=1
    s=0
    while s<lim-p and before[-s-1]==after[-s-1]:s+=1
    return {'prefix':p,'suffix':s,'old':b64(before[p:len(before)-s]),'new':b64(after[p:len(after)-s]),'before_sha256':sha(before),'after_sha256':sha(after),'before_bytes':len(before),'after_bytes':len(after)}

def apply_delta(current,d,reverse=False):
    source,target=('after','before') if reverse else ('before','after');old,new=('new','old') if reverse else ('old','new')
    if len(current)!=d[source+'_bytes'] or sha(current)!=d[source+'_sha256']:raise ValueError('base snapshot mismatch')
    p,s=d['prefix'],d['suffix']
    if type(p) is not int or type(s) is not int or min(p,s)<0 or p+s>len(current):raise ValueError('invalid splice bounds')
    a,b=un64(d[old]),un64(d[new]);end=len(current)-s
    if current[p:end]!=a:raise ValueError('old segment differs')
    result=current[:p]+b+current[end:]
    if len(result)!=d[target+'_bytes'] or sha(result)!=d[target+'_sha256']:raise ValueError('target snapshot mismatch')
    return result

METHODS={
 'order_audit_engine.py':{'OrderAuditEngineMixin.'+s for s in ('_initialize_order_audit','_clear_order_audit','register_order_b_reset_legs','_reparent_primary_high_causes','_register_primary_point','_reconcile_primary_labels','_register_order_audit','_rebuild_accepted_order_audit','rebuild_accepted_order_audit','ensure_accepted_order_audit')}|{'SOrderAuditMixin._record_a_order_audit','SOrderAuditMixin._audit_stopped_a'},
 'e_zone_detector.py':{'EZoneDetector.__init__','EZoneDetector.detect'},
 's_zone_detector.py':{'SZoneDetector.__init__','SZoneDetector.detect','SZoneDetector._detect'},
}
ABSENT=encode(['absent'])
class Observer:
    def __init__(self,root,stream,checkpoints):
        self.paths={str((root/'pipeline'/name).resolve()):methods for name,methods in METHODS.items()};self.stream=stream;self.checkpoints=checkpoints;self.owners={};self.active={};self.calls=collections.Counter();self.outer=collections.Counter();self.gaps=[];self.ordinal=0;self.delta_bytes=0;self.snapshot_bytes=0;self.changed=0;self.index_checks=0
    @staticmethod
    def fresh(obj):return snapshot(obj.order_audit) if hasattr(obj,'order_audit') else ABSENT
    def record(self,st,method,point):
        obj=st['obj']
        if hasattr(obj,'_order_audit_confirmation_index'):
            ledger=obj.order_audit; idx=obj._order_audit_confirmation_index
            expected=sorted((v['confirmation_time'], k[0], k[1]) for k,v in ledger.items())
            if type(idx) is not list or snapshot(idx)!=snapshot(expected):
                raise ValueError('OrderAudit secondary index inconsistent at '+method+':'+point)
            self.index_checks+=1
        actual=self.fresh(obj);before=st['last'];d=make_delta(before,actual)
        if apply_delta(before,d)!=actual or apply_delta(actual,d,True)!=before:raise AssertionError('replay is not byte exact')
        self.ordinal+=1;self.changed+=before!=actual
        row={'ordinal':self.ordinal,'owner':st['owner'],'class':type(st['obj']).__name__,'direction':getattr(st['obj'],'direction',None),'method':method,'point':point,'delta':d}
        payload=encode(row)+b'\n';self.stream.write(payload);self.delta_bytes+=len(payload)
        cp=encode({**{k:v for k,v in row.items() if k!='delta'},'snapshot':b64(actual)})+b'\n';self.checkpoints.write(cp);self.snapshot_bytes+=len(cp)
        st['last']=actual
        if point in ('entry','final') and before!=actual:self.gaps.append({'ordinal':self.ordinal,'owner':st['owner'],'method':method,'point':point})
    def trace(self,frame,event,arg):
        if event!='call':return None
        methods=self.paths.get(frame.f_code.co_filename);method=frame.f_code.co_qualname
        if not methods or method not in methods:return None
        self.calls[method]+=1;obj=frame.f_locals['self'];k=id(obj)
        if k not in self.owners:self.owners[k]={'obj':obj,'owner':len(self.owners)+1,'last':ABSENT,'depth':0}
        st=self.owners[k];outer=st['depth']==0;st['depth']+=1
        if outer:self.outer[method]+=1;self.record(st,method,'entry')
        self.active[id(frame)]=(st,method,outer);frame.f_trace_lines=False
        return self.local
    def local(self,frame,event,arg):
        if event=='exception':self.calls['exception:'+frame.f_code.co_qualname]+=1
        if event=='return':
            st,method,outer=self.active.pop(id(frame));st['depth']-=1
            if outer:self.record(st,method,'return')
        return self.local
    def finish(self):
        if self.active or any(x['depth'] for x in self.owners.values()):raise ValueError('unclosed boundaries')
        for st in self.owners.values():self.record(st,'final','final')

def strict_json(raw):
    def pairs(items):
        r={}
        for k,v in items:
            if k in r:raise ValueError('duplicate key')
            r[k]=v
        return r
    def constant(v):raise ValueError('nonfinite JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)

def verify_replay(dp,cp):
    current={};count=0;changed=0;active={};final=set()
    with gzip.open(dp,'rb') as a,gzip.open(cp,'rb') as b:
        for left,right in itertools.zip_longest(a,b):
            if left is None or right is None:raise ValueError('checkpoint count mismatch')
            d,c=strict_json(left),strict_json(right);count+=1
            fields={'ordinal','owner','class','direction','method','point'}
            if set(d)!=fields|{'delta'} or set(c)!=fields|{'snapshot'} or any(encode(d[k])!=encode(c[k]) for k in fields):raise ValueError('checkpoint metadata mismatch')
            if type(d['ordinal']) is not int or d['ordinal']!=count or type(d['owner']) is not int or d['owner']<=0:raise ValueError('ordinal/owner mismatch')
            owner=d['owner'];point=d['point']
            if owner in final:raise ValueError('event after owner final')
            if point=='entry':
                if owner in active:raise ValueError('nested outer boundary')
                active[owner]=d['method']
            elif point=='return':
                if active.pop(owner,None)!=d['method']:raise ValueError('unmatched return')
            elif point=='final':
                if owner not in current or owner in active or d['method']!='final':raise ValueError('bad final')
                final.add(owner)
            else:raise ValueError('invalid boundary point')
            prior=current.get(d['owner'],ABSENT);target=un64(c['snapshot']);after=apply_delta(prior,d['delta'])
            if after!=target or apply_delta(after,d['delta'],True)!=prior:raise ValueError('independent checkpoint mismatch')
            changed+=prior!=after;current[d['owner']]=after
    if not count or active or final!=set(current):raise ValueError('empty or unclosed trace')
    return {'status':'PASS','boundaries':count,'changed_boundaries':changed,'owners':len(current),'final_sha256':{str(k):sha(v) for k,v in current.items()}}

def source_check(root,expected):
    found={p.relative_to(root).as_posix():sha(p.read_bytes()) for directory in ('bridge','pipeline') for p in (root/directory).rglob('*.py')}
    if len(found)!=15 or found!=expected:raise ValueError('frozen source mismatch')

def main():
    from semantic_trace_v9 import execute
    p=argparse.ArgumentParser();p.add_argument('--engine-root',type=Path,required=True);p.add_argument('--raw',type=Path,required=True);p.add_argument('--case',type=Path,required=True);p.add_argument('--variant',choices=['original','v81'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    root=a.engine_root.resolve();case=json.loads(a.case.read_text());a.out.mkdir(parents=True,exist_ok=False)
    source_check(root,case['source_sha256'][a.variant]);rawhash=sha(a.raw.read_bytes())
    if rawhash!=case['raw_sha256'] or sys.gettrace() is not None:raise ValueError('RAW or trace precondition')
    start=time.perf_counter();cpu=time.process_time();dp=a.out/'delta.jsonl.gz';cp=a.out/'checkpoints.jsonl.gz'
    with gzip.open(dp,'xb',compresslevel=3) as d,gzip.open(cp,'xb',compresslevel=3) as c:
        obs=Observer(root,d,c);sys.settrace(obs.trace)
        try:rc=execute(SimpleNamespace(engine_root=root,raw=a.raw,from_time=case['first_time'],to_time=case['last_time'],trace_out=None,stage_profile=None,meter_output=None,summary=None))
        finally:sys.settrace(None)
        obs.finish()
    source_check(root,case['source_sha256'][a.variant])
    if rc or sha(a.raw.read_bytes())!=rawhash:raise ValueError('native exit or RAW changed')
    replay=verify_replay(dp,cp)
    report={'variant':a.variant,'native_exit':rc,'source_sha256':case['source_sha256'][a.variant],'raw_sha256':rawhash,'records':case['records'],'wall_s':time.perf_counter()-start,'cpu_s':time.process_time()-cpu,'calls':dict(obs.calls),'outer_calls':dict(obs.outer),'gaps':obs.gaps,'index_checks':obs.index_checks,'replay':replay,'delta_uncompressed_bytes':obs.delta_bytes,'checkpoint_uncompressed_bytes':obs.snapshot_bytes,'delta_gzip_bytes':dp.stat().st_size,'checkpoint_gzip_bytes':cp.stat().st_size,'delta_gzip_sha256':sha(dp.read_bytes()),'checkpoint_gzip_sha256':sha(cp.read_bytes()),'scope':'Outer OrderAudit method boundary snapshots, exact typed graph and observed set iteration; no intra-boundary, cross-snapshot identity or complete Live proof.','full_semantic_state_status':'INCOMPLETE'}
    (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
