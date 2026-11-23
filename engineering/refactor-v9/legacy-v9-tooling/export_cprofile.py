#!/usr/bin/env python3
"""Export separate cProfile function/self/cumulative metrics, not sum of nested cumtime.
Flame-ish ranked plot is explicitly a cumulative-call-time bar, NOT a stack flamegraph.
"""
import csv,json,pstats
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parents[1];O=W/'output';path=next(O.glob('*.pstats'))
s=pstats.Stats(str(path));rows=[]
for (file,line,name),(cc,nc,tt,ct,callers) in s.stats.items():
    file=file.replace(str(W/'v81/engine')+'/','engine/')
    if file.startswith(str(W)):file=file.replace(str(W),'V9_work')
    rows.append({'file':file,'line':line,'function':name,'primitive_calls':cc,'total_calls':nc,'self_s':round(tt,7),'cumulative_s':round(ct,7),'is_engine':file.startswith('engine/')})
rows.sort(key=lambda x:x['cumulative_s'],reverse=True)
with (O/'V9_CPROFILE_FUNCTIONS.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
engine=[x for x in rows if x['is_engine'] and x['self_s']>0]
engine.sort(key=lambda x:x['self_s'],reverse=True)
fig,ax=plt.subplots(figsize=(11,6))
plot=engine[:15][::-1]; labels=[f"{x['function']} ({Path(x['file']).name}:{x['line']})" for x in plot]
ax.barh(range(len(plot)),[x['self_s'] for x in plot]);ax.set_yticks(range(len(plot)),labels,fontsize=7)
ax.set_xlabel('Exclusive CPU time in cProfile seconds');ax.set_title('V9: 15,542 RAW cProfile — exclusive function time (NOT stacked)')
fig.tight_layout();fig.savefig(O/'V9_CPROFILE_EXCLUSIVE.png',dpi=150);plt.close(fig)
key=['_discover_candidate_chains','_zone','order_candidates','_register_order_audit','_compute_reconciliation','_cross_order','detect']
chosen=[x for x in rows if x['is_engine'] and x['function'] in key]
(O/'V9_HOT_FUNCTION_COUNTS.json').write_text(json.dumps({'source_file':path.name,'profiled_raw_records':15542,'profile_kind':'cProfile separate from wall benchmarks','cprofile_total_s':s.total_tt,'nested_cumulative_seconds_cannot_be_summed':True,'hot_functions':chosen},indent=2))
print('saved',len(rows),'functions; hot tracked',len(chosen),'cProfile total CPU',s.total_tt)
