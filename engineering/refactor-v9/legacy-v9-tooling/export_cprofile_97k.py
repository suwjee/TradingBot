import csv,json,pstats
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parents[1];O=W/'output';p=next(O.glob('*97k.pstats'));s=pstats.Stats(str(p));rows=[]
for (file,line,func),(primitive,total,selftime,cumulative,callers) in s.stats.items():
 file=file.replace(str(W/'v81/engine')+'/','engine/')
 rows.append({'function':func,'file':file,'line':line,'primitive_calls':primitive,'calls':total,'exclusive_s':round(selftime,7),'inclusive_s':round(cumulative,7),'engine':file.startswith('engine/')})
rows.sort(key=lambda x:x['inclusive_s'],reverse=True)
with (O/'V9_CPROFILE_FUNCTIONS_97K.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
selected=[x for x in rows if x['engine']];selected.sort(key=lambda x:x['exclusive_s'],reverse=True)
fig,ax=plt.subplots(figsize=(11,5.8));top=selected[:16][::-1]
ax.barh(range(len(top)),[x['exclusive_s'] for x in top]);ax.set_yticks(range(len(top)),[f"{x['function']} ({Path(x['file']).name}:{x['line']})" for x in top],fontsize=7)
ax.set_xlabel('Self CPU seconds in profiled 97,930-RAW execution');ax.set_title('V9 separate cProfile 97k — exclusive call CPU times');fig.tight_layout();fig.savefig(O/'V9_CPROFILE_EXCLUSIVE_97K.png',dpi=150)
functions=['_discover_candidate_chains','_zone','order_candidates','_register_order_audit','_compute_reconciliation','_cross_order']
selected=[x for x in rows if x['engine'] and x['function'] in functions]
(O/'V9_HOT_FUNCTION_COUNTS_97K.json').write_text(json.dumps({'raw_records':97930,'cprofile_total_cpu_s':round(s.total_tt,5),'scope':'profiled process only; separate from wall benchmark','rows':selected},indent=2))
print({'total_cpu':round(s.total_tt,4),'functions':len(rows),'hot':len(selected)})
