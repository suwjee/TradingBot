"""Read-only native V8.1 query metering. Counts executed source sites, not estimates."""
import argparse, ast, collections, hashlib, json, os, resource, sys, time
from pathlib import Path
from types import SimpleNamespace
from run_verified_trace_pair_v9 import source_check, hash_file
from semantic_trace_v9 import execute

# Only named, independently source-pinned sites; count body entry, not loop tests.
TARGETS={
 'order_audit_engine.py': {
 '_compute_direct_parent_stop_order': {'confirmation_query':'while (direct_position < len(self.opposite_reactions) and self._opposite_confirmations[direct_position] <= confirmation_after):\n    direct_position += 1', 'blocked_skip':'direct_position += 1'},
 '_direct_parent_stop_order': {'cache_hit':'return cached'},
 'order_candidates': {'cache_hit':'return list(cached)','reset_leg_eligible':'reaction = leg.physical_reaction'},
 '_first_healthy_direct_geometry': {'geometry_attempt':'candidate = self.direct_geometry_finder(self.order_direction, search_index, self.end_index, search_event)','reset_row':'if search_event < reset_time <= confirmation:\n    reset_before_confirmation = reset_time\n    break'},
 '_carried_orders_for_parent': {'cache_hit':'return list(cached)','ledger_row':'if created_events is not None and (not created_events):\n    continue','initial_row':'confirmation = record[1]'},
 '_cross_order': {'cache_hit':'return self._cross_order_cache[cache_key]'},
 },
 'e_zone_detector.py': {'_discover_candidate_chains':{'chain_attempt':'zone = self._zone(family, number, parent_type, parent, stop_event, e_owned_source_times=owned_sources, pre_registered_s=parent_type == \'S\')','candidate_append':'candidates.append(zone)'}, '_zone':{}, '_compute_reconciliation':{}}
}
def topology(root):
    result={}
    for filename,fns in TARGETS.items():
        path=root/'pipeline'/filename; tree=ast.parse(path.read_bytes())
        for name,sites in fns.items():
            matches=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name]
            if len(matches)!=1:raise ValueError(f'{filename}:{name}: ambiguous definition')
            fn=matches[0]; lines={}
            if name=='_compute_direct_parent_stop_order':
                branches=[n for n in fn.body if isinstance(n,ast.If) and ast.unparse(n.test)=='confirmation_after is not None']
                if len(branches)!=1 or len(branches[0].body)!=1 or not isinstance(branches[0].body[0],ast.While):raise ValueError('confirmation topology changed')
                loop=branches[0].body[0]
                if ast.unparse(loop.test)!='direct_position < len(self.opposite_reactions) and self._opposite_confirmations[direct_position] <= confirmation_after':raise ValueError('predicate changed')
                lines[loop.lineno]='confirmation_query';lines[loop.body[0].lineno]='confirmation_skip'
                other=[n for n in fn.body if isinstance(n,ast.While)]
                if len(other)!=1:raise ValueError('blocked loop changed')
                inc=[n for n in other[0].body if isinstance(n,ast.AugAssign) and ast.unparse(n)=='direct_position += 1']
                if len(inc)!=1:raise ValueError('blocked increment changed')
                lines[inc[0].lineno]='blocked_skip'
            else:
                for label,syntax in sites.items():
                    target=ast.unparse(ast.parse(syntax).body[0]); candidates=[n for n in ast.walk(fn) if isinstance(n,ast.stmt) and ast.unparse(n)==target]
                    if len(candidates)!=1:raise ValueError(f'{name}:{label}: {len(candidates)} sites')
                    lines[candidates[0].lineno]=label
            result[(str(path.resolve()),fn.name)]=lines
    return result

class Meter:
    def __init__(self,sites):self.sites=sites;self.counts=collections.defaultdict(collections.Counter);self.pending={};self.skip_hist=collections.Counter();self.sequence_hist=collections.Counter()
    def trace(self,frame,event,arg):
        if event!='call':return None
        k=(frame.f_code.co_filename,frame.f_code.co_name)
        if k not in self.sites:return None
        self.counts[k[1]]['calls']+=1
        self.pending[id(frame)]=[k,0,False]
        return self.local
    def local(self,frame,event,arg):
        k,skips,entered=self.pending[id(frame)]; c=self.counts[k[1]]
        if event=='line':
            label=self.sites[k].get(frame.f_lineno)
            if label=='confirmation_query':
                if not entered:
                    c[label]+=1;self.pending[id(frame)][2]=True
                    self.sequence_hist[len(frame.f_locals['self'].opposite_reactions)]+=1
            elif label:
                c[label]+=1
                if label=='confirmation_skip':self.pending[id(frame)][1]+=1
        elif event=='return':
            c['returns']+=1
            if entered:self.skip_hist[skips]+=1
            self.pending.pop(id(frame))
        return self.local

def main():
    p=argparse.ArgumentParser();p.add_argument('--engine-root',type=Path,required=True);p.add_argument('--raw',type=Path,required=True);p.add_argument('--case',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();case=json.loads(a.case.read_text());source_check(a.engine_root,case['source_sha256']['v81'])
    if hash_file(a.raw)!=case['raw_sha256']:raise ValueError('RAW mismatch')
    m=Meter(topology(a.engine_root)); args=SimpleNamespace(engine_root=a.engine_root,raw=a.raw,from_time=case['first_time'],to_time=case['last_time'],trace_out=None,summary=None,stage_profile=None,meter_output=None)
    t=time.perf_counter();cpu=time.process_time();sys.settrace(m.trace)
    try:rc=execute(args)
    finally:sys.settrace(None)
    wall=time.perf_counter()-t;cpu=time.process_time()-cpu
    source_check(a.engine_root,case['source_sha256']['v81'])
    if rc or m.pending or hash_file(a.raw)!=case['raw_sha256']:raise ValueError('incomplete or changed input')
    report={'records':case['records'],'raw_sha256':case['raw_sha256'],'source_sha256':case['source_sha256']['v81'],'status':'COMPLETE_METER','native_exit':rc,'wall_observed_s':wall,'cpu_observed_s':cpu,'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'counts':{k:dict(v) for k,v in m.counts.items()},'confirmation_skip_histogram':dict(m.skip_hist),'confirmation_sequence_length_histogram':dict(m.sequence_hist),'sites':{Path(k[0]).name+':'+k[1]:v for k,v in m.sites.items()},'scope':'source-site executed counts; reset_leg_eligible counts yielded legs, not hidden generator scans; confirmation_skip counts rejected rows, not final successful comparison; not full-state trace or unprofiled performance'}
    a.report.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
