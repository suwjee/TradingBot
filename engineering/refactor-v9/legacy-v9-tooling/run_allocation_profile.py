#!/usr/bin/env python3
"""V9 test-only tracemalloc/GC count, separate from unprofiled benchmark.
No production file is changed or imported into existing Engine benchmark process.
"""
import gc,hashlib,json,os,runpy,sys,time,tracemalloc
from pathlib import Path
from run_real_matrix import cmd
from strict_golden import stable_payload
W=Path(__file__).resolve().parents[1];O=W/'output';M=json.loads((W/'tooling/inputs_verified.json').read_text())
item=next(x for x in M['datasets'] if '2026-10-08' in x['file'])
root=W/'v81/engine';raw=Path('/mnt/data')/item['file'];argv=cmd(root,raw,item)
export=O/'V9_TRACEMALLOC_SAMPLE_ENGINE.json';target=O/'V9_TRACEMALLOC_SAMPLE_OUTPUT.json'
counts_before=gc.get_stats();tracked_before=gc.get_count();old_argv=sys.argv
os.environ['PYTHONHASHSEED']='0'
tracemalloc.start(4);start=time.perf_counter_ns();reason=None
try:
 sys.argv=[str(root/'bridge/trading_pipeline.py')]+argv[3:]
 # Use identical process source and input flags, but tracer itself is explicitly excluded from timing baselines.
 with target.open('wb') as fout:
  import contextlib
  with contextlib.redirect_stdout(open(fout.fileno(),'w',encoding='utf-8',closefd=False)):
   try:runpy.run_path(str(root/'bridge/trading_pipeline.py'),run_name='__main__')
   except SystemExit as e:
    if e.code not in (None,0):raise RuntimeError('Engine exit nonzero '+repr(e.code))
except Exception as e:
 reason=repr(e)
finally:
 elapsed=(time.perf_counter_ns()-start)/1e9
 current,peak=tracemalloc.get_traced_memory();snap=tracemalloc.take_snapshot()
 tracemalloc.stop();sys.argv=old_argv
stats=snap.statistics('lineno');top=[{'frame':str(x.traceback[0]).replace(str(root)+'/','engine/'), 'allocated_bytes':x.size,'blocks':x.count} for x in stats[:30]]
report={'profile_method':'tracemalloc.start(4) + gc.get_stats; heavy overhead; separate from unprofiled runs',
 'raw':raw.name,'bars':item['records'],'wall_s_profiled':round(elapsed,6),
 'peak_traced_python_bytes':peak,'final_traced_bytes':current,
 'total_snapshot_blocks':sum(x.count for x in stats),'total_snapshot_allocated_bytes':sum(x.size for x in stats),
 'gc_before':counts_before,'gc_after':gc.get_stats(),'gc_count_before':tracked_before,'gc_count_after':gc.get_count(),
 'top_allocations':top,'error':reason}
if reason is None:
 from strict_golden import stable_match
 ref=W/'golden/runs/github_baseline'/ (raw.stem.replace(' ','_')+'.json');metrics=W/'golden/runs/github_baseline'/(raw.stem.replace(' ','_')+'.metrics.json')
 z=stable_match(ref.read_bytes(),target.read_bytes(),json.loads(metrics.read_text()))
 report['parity']=z['bytes_equal'] and z['timing_schema_equal'];report['stable_sha256']=z['candidate_stable_sha256']
else:report['parity']=False
export.write_text(json.dumps(report,indent=2));print(json.dumps({'profile_wall_s':report['wall_s_profiled'],'peak_traced_mib':round(peak/2**20,3),'blocks':report['total_snapshot_blocks'],'parity':report['parity'],'error':reason}))
if not report['parity']:sys.exit(1)
