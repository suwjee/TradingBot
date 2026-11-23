import csv,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];O=W/'output';rows=json.loads((O/'V9_SYNTHETIC_PARITY.json').read_text());rows.sort(key=lambda x:x['bars'])
for i,r in enumerate(rows):
 r['original_T_over_previous']=None if i==0 else round(r['baseline_wall_s']/rows[i-1]['baseline_wall_s'],4)
 r['v81_T_over_previous']=None if i==0 else round(r['candidate_wall_s']/rows[i-1]['candidate_wall_s'],4)
 r['size_ratio']=None if i==0 else round(r['bars']/rows[i-1]['bars'],4)
 r['v81_time_exponent_between_sizes']=None if i==0 else round(math.log(r['candidate_wall_s']/rows[i-1]['candidate_wall_s'])/math.log(r['bars']/rows[i-1]['bars']),3)
 a=json.loads((O/f'synthetic_{r["bars"]}_v81.json').read_bytes())
 r['E_stages_seconds_v81']=round(sum(v for k,v in a['timings']['phasesMs'].items() if k.startswith('E •'))/1000,4)
 r['E_stage_fraction_v81']=round(r['E_stages_seconds_v81']/(a['timings']['bridgeTotalMs']/1000),4)
(O/'V9_SYNTHETIC_SCALING_ANALYSIS.json').write_text(json.dumps({'synthetic_seed':20261123,'scope':'full RAW native both; one unpaired run per source/size; ratios are descriptive not a universal asymptotic proof','scaling':rows},indent=2))
big=rows[-1];E=big['E_stages_seconds_v81'];total=json.loads((O/'synthetic_1000000_v81.json').read_bytes())['timings']['bridgeTotalMs']/1000
assumptions=[('E candidate discovery/_zone indexing','E-stage wall',E,0.10,'Identical event/stop/order and tie order required; no patch implemented'),
('OrderAudit registration/query secondary indexing','E-stage wall (overlapping)',E,0.05,'Owned ledger unchanged, invalidate on S/E/StopAll/OrderB feedback'),
('First Parent Stop/Crossing RAW lookup indexing','E-stage wall (overlapping)',E,0.04,'First native RAW crossing, strict equality and ownership preserved'),
('E reconciliation heap/active source index','E-stage wall (overlapping)',E,0.03,'No change to heap tie, event chronology, accepted E ledger'),
('PHPL/serialization allocation reuse','total bridge wall',total,0.02,'No changes to stable JSON byte order, Decimal strings, Live visibility')]
with (O/'V9_BOTTLENECK_SAVED_TIME_ESTIMATES_1M.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['candidate','budget_reference','budget_seconds_measured','hypothetical_fraction_reduced','scenario_saved_seconds_at_1m','status','guard'])
 w.writeheader()
 for name,budget,v,fraction,guard in assumptions:
  w.writerow({'candidate':name,'budget_reference':budget,'budget_seconds_measured':round(v,3),
  'hypothetical_fraction_reduced':fraction,'scenario_saved_seconds_at_1m':round(v*fraction,3),
  'status':'ESTIMATE scenario only; NOT measured patch gain; budgets overlap; DO NOT ADD','guard':guard})
with (O/'V9_COMPLEXITY_MAP.md').open('a') as f:
 f.write(f'''\n### Completed 1M synthetic scaling — observed\n\n- Same generator/seed, native BOTH in a single process, all four input sizes, original vs untouched V8.1 stable output **4/4 PASS**. Reference and candidate both consumed the entire native files.\n- 1M original **{big['baseline_wall_s']:.3f}s**, peak RSS **{big['baseline_rss']:.1f} MiB**; V8.1 **{big['candidate_wall_s']:.3f}s**, peak RSS **{big['candidate_rss']:.1f} MiB**. Ratio original/V8.1 **{big['baseline_wall_s']/big['candidate_wall_s']:.3f}×** in *one order-uncorrected observation*; no promotion claim.\n- Observed 500k→1M full invocation runtime ratios: original **{big['original_T_over_previous']:.3f}×**, V8.1 **{big['v81_T_over_previous']:.3f}×**, with input size 2×. The synthetic path exhibits superlinear empirical growth in this interval; this alone **does not prove `O(N²)`** or distinguish input-signal-density from an algorithmic lower bound. See `V9_SYNTHETIC_SCALING_ANALYSIS.json`.\n- V8.1 1M measured E phases total **{E:.3f}s** / bridge **{total:.3f}s** (**{E/total:.1%}**). Frozen original E stages **{sum(v for k,v in json.loads((O/'synthetic_1000000_original.json').read_bytes())['timings']['phasesMs'].items() if k.startswith('E •'))/1000:.3f}s**. These are phase wall-time telemetry, not nested Python cProfile sums.\n\n### V10–V11 saved-time-at-1M **ESTIMATE scenario**, not actual speedup\n\n`V9_BOTTLENECK_SAVED_TIME_ESTIMATES_1M.csv` gives a rankable, assumption-labelled *what-if scenario*: if an unimplemented accelerator removed 10% of the measured 202.877-second E budget with **zero semantic drift**, it would save about 20.29 seconds on this specific 1M V8.1 invocation. Other examples assume removing 5% of that overlapping budget for OrderAudit (10.14s), 4% Parent Stop (8.12s), 3% reconciliation (6.09s), or 2% total Bridge time in PH/PL/serialization (7.44s). These opportunities are *not independent* and **must not be added**; true spend is not yet isolated to functions in 1M profiling. This is merely a prioritized experiment-design hypothesis, with all identity/tie/chronology guards mandatory. A real V10 optimization must be separately measured in repeated AB/BA runs.\n''')
print('V9 synthetic scaling 1M',big['original_T_over_previous'],big['v81_T_over_previous'],'E seconds',E)
