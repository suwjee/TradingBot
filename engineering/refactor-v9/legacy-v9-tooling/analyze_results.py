#!/usr/bin/env python3
"""Observed stage telemetry and synthetic scaling, no fabricated timings."""
import csv,json,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parents[1];O=W/'output'
rows=json.loads((O/'V9_REAL_PARITY.json').read_text());stages=[]
for row in rows:
 stem=Path(row['raw_file']).stem.replace(' ','_');path=O/(stem+'.v81.stage_timings.json')
 if not path.exists():continue
 phases=json.loads(path.read_text())['phasesMs']
 E=sum(v for k,v in phases.items() if k.startswith('E •'))
 groups={'E':E,'Reaction':sum(v for k,v in phases.items() if k.startswith('Reaction geometry') or k.startswith('Internal Reaction ownership')),
         'A':sum(v for k,v in phases.items() if k.startswith('A •')),
         'S':sum(v for k,v in phases.items() if k.startswith('S •')),
         'PHPL':sum(v for k,v in phases.items() if k.startswith('PH/PL')),
         'InputNormalization':sum(v for k,v in phases.items() if k in ('Read source file','Parse source JSON','Normalize raw candles','Build lower candle views','Build timeframe candle views'))}
 stages.append({'raw_file':row['raw_file'],'bars':row['bars'],'wall_s':row['wall_s'],'timing_bridge_s':sum(phases.values())/1000,
               **{k+'_s':round(v/1000,6) for k,v in groups.items()},'E_fraction_wall':round(E/1000/row['wall_s'],6),
               'source':'OBSERVED V8.1 native phased timings; stage totals cumulative by label'})
with (O/'V9_STAGE_PROFILE.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=stages[0].keys());writer.writeheader();writer.writerows(stages)
if stages:
 fig,ax=plt.subplots(figsize=(10,5))
 x=range(len(stages));ax.bar(x,[r['E_s'] for r in stages],label='E stages (cumulative measured)')
 ax.bar(x,[max(0,r['wall_s']-r['E_s']) for r in stages],bottom=[r['E_s'] for r in stages],label='All other elapsed (derived)')
 ax.set_xticks(list(x),[r['raw_file'].split(' FROM ')[1][:10] + (' OIL' if 'USOIL' in r['raw_file'] else ' XAU') for r in stages],rotation=25)
 ax.set_ylabel('Elapsed time (seconds)');ax.set_title('V9 fresh run: whole invocation vs cumulative E stage telemetry');ax.legend();fig.tight_layout();fig.savefig(O/'V9_STAGE_WALL_PROFILE.png',dpi=140);plt.close(fig)
 s=json.loads((O/'V9_SYNTHETIC_PARITY.json').read_text()) if (O/'V9_SYNTHETIC_PARITY.json').exists() else []
 good=[a for a in s if a['status']=='PASS'];good.sort(key=lambda x:x['bars'])
 if len(good)>1:
  fig,ax=plt.subplots(figsize=(8,5))
  ax.plot([x['bars'] for x in good],[x['baseline_wall_s'] for x in good],marker='o',label='Frozen original (observed)')
  ax.plot([x['bars'] for x in good],[x['candidate_wall_s'] for x in good],marker='o',label='V8.1 (observed)')
  ax.set_xlabel('Synthetic 5s raw records');ax.set_ylabel('Invocation wall time (seconds)');ax.set_title('Synthetic scaling — observed completed runs only');ax.legend();fig.tight_layout();fig.savefig(O/'V9_SYNTHETIC_SCALING.png',dpi=140);plt.close(fig)
 print(json.dumps({'real7':len(stages),'total_wall':round(sum(r['wall_s'] for r in stages),2),'total_E_phase_s':round(sum(r['E_s'] for r in stages),2),
                   'synthetic_completed':len(good)}))
