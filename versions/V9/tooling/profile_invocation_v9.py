"""Separate, reproducible native/cProfile/allocation observations; never combine timing samples."""
import argparse,cProfile,gc,json,os,resource,sys,time,tracemalloc,pstats
from pathlib import Path
from types import SimpleNamespace
from ledger_delta_v9 import source_check,sha
from semantic_trace_v9 import execute

def main():
 p=argparse.ArgumentParser();p.add_argument('--engine-root',type=Path,required=True);p.add_argument('--raw',type=Path,required=True);p.add_argument('--case',type=Path,required=True);p.add_argument('--variant',choices=['original','v81'],required=True);p.add_argument('--mode',choices=['native','cprofile','alloc'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();c=json.loads(a.case.read_text());source_check(a.engine_root,c['source_sha256'][a.variant]);assert sha(a.raw.read_bytes())==c['raw_sha256'];a.out.mkdir(parents=True,exist_ok=False)
 args=SimpleNamespace(engine_root=a.engine_root,raw=a.raw,from_time=c['first_time'],to_time=c['last_time'],trace_out=None,stage_profile=None,meter_output=None,summary=None)
 profile=cProfile.Profile() if a.mode=='cprofile' else None;g0=gc.get_stats();n0=gc.get_count();start=time.perf_counter();cpu=time.process_time()
 if a.mode=='alloc':tracemalloc.start(4)
 rc=profile.runcall(execute,args) if profile else execute(args)
 wall=time.perf_counter()-start;cpu=time.process_time()-cpu
 report={'variant':a.variant,'mode':a.mode,'records':c['records'],'raw_sha256':c['raw_sha256'],'source_sha256':c['source_sha256'][a.variant],'wall_s':wall,'cpu_s':cpu,'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'gc_before':g0,'gc_after':gc.get_stats(),'gc_count_before':n0,'gc_count_after':gc.get_count(),'native_exit':rc,'concurrency_note':'Can run with other tasks; no paired native speedup or rigorous overhead claim.'}
 if a.mode=='alloc':
  current,peak=tracemalloc.get_traced_memory();snap=tracemalloc.take_snapshot();tracemalloc.stop();stats=snap.statistics('lineno');report.update(traced_current_bytes=current,traced_peak_bytes=peak,live_blocks_at_snapshot=sum(x.count for x in stats),top_allocations=[{'frame':str(x.traceback[0]).replace(str(a.engine_root.resolve())+'/','engine/'),'bytes':x.size,'blocks':x.count} for x in stats[:30]])
 if profile:
  profile.dump_stats(str(a.out/'profile.pstats'));stats=pstats.Stats(profile).stats;report['profile_functions']=len(stats);report['top_exclusive']=[{'source':str(k[0]).replace(str(a.engine_root.resolve())+'/','engine/'),'line':k[1],'function':k[2],'primitive_calls':v[0],'calls':v[1],'exclusive_s':v[2],'cumulative_s':v[3]} for k,v in sorted(stats.items(),key=lambda x:x[1][2],reverse=True)[:40]]
  report['note']='Exclusive and cumulative differ; do not sum cumulative across call tree.'
 source_check(a.engine_root,c['source_sha256'][a.variant]);assert rc==0 and sha(a.raw.read_bytes())==c['raw_sha256'];(a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
