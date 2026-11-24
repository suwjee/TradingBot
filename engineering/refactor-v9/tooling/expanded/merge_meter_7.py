#!/usr/bin/env python3
from pathlib import Path
import csv,json,collections,hashlib
ROOT=Path('/mnt/data/V9_final')
PREV=Path('/mnt/data/V9_continue/results/meter')
NEXT=ROOT/'meter'
INPUTS=json.loads(Path('/mnt/data/V9_work/tooling/inputs_verified.json').read_text())['datasets']
rows=[];site_agg=collections.Counter()
for item in INPUTS:
    stem=Path(item['file']).stem.replace(' ','_');basename='v81.'+stem
    location=(NEXT if int(item['id']) in (3,6) else PREV)
    met=location/(basename+'.summary.json');cnt=location/(basename+'.counters.json')
    if not (met.is_file() and cnt.is_file()):raise SystemExit('missing metered dataset '+str(item['id']))
    data=json.loads(met.read_text());counts=json.loads(cnt.read_text())['counts']
    if not data['stable_pass'] or data['stable_sha256']!=item['stable_output_sha256']:
        raise SystemExit('bad stable equality '+str(item['id']))
    if sum(counts.values())!=data['operation_count_selected']:
        raise SystemExit('bad operation sum '+str(item['id']))
    site_agg.update(counts)
    row={'dataset_id':item['id'],'records':item['records'],'raw_file':item['file'],
         'stable_sha256':data['stable_sha256'],'stable_pass':True,
         'wall_instrumented_s':data['wall_s_instrumented'],'cpu_sampled_s':data['sampled_cpu_s'],
         'rss_mib':data['rss_mib'],'operations_selected':data['operation_count_selected'],
         **{z:int(data['operation_counts_by_type'].get(z,0)) for z in ['for_iteration','while_iteration','cache_hit','cache_miss','sorted','list.sort','heapify','heappop','heappush']},
         'scope':'SELECTED AST loop and operation sites, not all Python operations'}
    rows.append(row)
report={'status':'PASS','scope':'V8.1 test-only AST-instrumented only','total_raw':sum(x['records'] for x in rows),
        'total_selected_operations':sum(x['operations_selected'] for x in rows),
        'input_dataset_count':len(rows),'source_production_modified':False,
        'global_site_ranked':[{'site':p,'operations':n} for p,n in site_agg.most_common()],
        'rows':rows}
ROOT.mkdir(exist_ok=True,parents=True)
(ROOT/'V9_METER_COMPLETE_7_OF_7.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
with (ROOT/'V9_METER_COMPLETE_7_OF_7.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('PASS',len(rows),'raw',sum(x['records'] for x in rows),'operations',sum(x['operations_selected'] for x in rows))
for x in report['global_site_ranked'][:12]: print(x)
