"""Read-only actual StopAll event transition observer, scoped, not universal state proof."""
import argparse, collections, gzip, hashlib, json, sys, time, resource
from pathlib import Path
from types import SimpleNamespace
from ledger_delta_v9 import snapshot, source_check, sha
from semantic_trace_v9 import execute

NESTED={'StopAllDetector._detect_events.<locals>.process_s_event','StopAllDetector._detect_events.<locals>.process_e_event'}
OUTER={'StopAllDetector._detect_events','reconcile_stopall_lifecycle','finalize_behavior_visibility','resolve_order_context','filter_internal_behavior_outputs','LiveStopAllContinuation.update'}

def state(loc):
    return (loc['owner'],loc['pending_stop'],loc['active'])

class Observer:
    def __init__(self,path,stream):
        self.path=str(path.resolve()); self.stream=stream; self.pending={}; self.counts=collections.Counter(); self.ordinal=0; self.digest=hashlib.sha256()
    def emit(self,method,point,direction,value):
        self.ordinal+=1
        # The canonical typed payload contains all Decimal digits, original sequence order and aliases.
        data=snapshot((self.ordinal,method,point,direction,value))+b'\n'
        self.stream.write(data);self.digest.update(data);self.counts[method+':'+point]+=1
    def trace(self,frame,event,arg):
        if event!='call' or frame.f_code.co_filename!=self.path:return None
        method=frame.f_code.co_qualname
        if method not in NESTED|OUTER:return None
        loc=frame.f_locals
        frame.f_trace_lines=False
        direction=loc.get('direction',getattr(loc.get('self'),'direction',getattr(loc.get('self'),'_direction',None)))
        self.pending[id(frame)]=(method,direction,None)
        if method in NESTED:
            item=loc['s_item'] if 's_item' in loc else loc['e_item']; output=loc['output']
            self.pending[id(frame)]=(method,direction,len(output))
            self.emit(method,'entry',direction,(item,state(loc),len(output)))
        elif method=='StopAllDetector._detect_events':
            self.emit(method,'entry',direction,(loc['events'],loc['checkpoint'],loc['output']))
        return self.local
    def local(self,frame,event,arg):
        if event=='exception':
            self.counts['exception:'+frame.f_code.co_qualname]+=1
            raise ValueError('observed lifecycle call raised')
        if event=='return':
            method,direction,pre_count=self.pending.pop(id(frame)); loc=frame.f_locals
            if method in NESTED:
                output=loc['output']
                if len(output)<pre_count:raise ValueError('unexpected output shrink')
                self.emit(method,'return',direction,(state(loc),pre_count,len(output),output[pre_count:]))
            elif method=='StopAllDetector._detect_events':
                self.emit(method,'return',direction,(loc['output'],loc['checkpoints']))
            elif method=='reconcile_stopall_lifecycle':
                self.emit(method,'return',direction,(arg,loc['detector'].sequence_resets))
            elif method=='LiveStopAllContinuation.update':
                obj=loc['self'];self.emit(method,'return',direction,(arg,obj._event_keys,obj._checkpoints,obj._output,obj._result,obj._covered_until))
            else:self.emit(method,'return',direction,arg)
        return self.local

def main():
    p=argparse.ArgumentParser();p.add_argument('--engine-root',type=Path,required=True);p.add_argument('--raw',type=Path,required=True);p.add_argument('--case',type=Path,required=True);p.add_argument('--variant',choices=['original','v81'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    c=json.loads(a.case.read_text());root=a.engine_root.resolve();source_check(root,c['source_sha256'][a.variant]);rawsha=sha(a.raw.read_bytes());assert rawsha==c['raw_sha256'];a.out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();cpu=time.process_time();trace=a.out/'trace.jsonl.gz'
    with gzip.open(trace,'xb',compresslevel=3) as f:
        ob=Observer(root/'pipeline/lifecycle_engine.py',f);assert sys.gettrace() is None;sys.settrace(ob.trace)
        try:rc=execute(SimpleNamespace(engine_root=root,raw=a.raw,from_time=c['first_time'],to_time=c['last_time'],trace_out=None,stage_profile=None,meter_output=None,summary=None))
        finally:sys.settrace(None)
    source_check(root,c['source_sha256'][a.variant]);assert not ob.pending and rc==0 and sha(a.raw.read_bytes())==rawsha and ob.ordinal>0
    r=dict(variant=a.variant,records=c['records'],raw_sha256=rawsha,source_sha256=c['source_sha256'][a.variant],native_exit=rc,events=ob.ordinal,counts=dict(ob.counts),jsonl_sha256=ob.digest.hexdigest(),gzip_sha256=sha(trace.read_bytes()),wall_s=time.perf_counter()-start,cpu_s=time.process_time()-cpu,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,scope='StopAll process S/E entry and return, output appends and selected lifecycle boundary returns; not every mutation inside call, cache or arbitrary Live')
    (a.out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
