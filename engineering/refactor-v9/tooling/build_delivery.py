#!/usr/bin/env python3
"""Reproducibly package only test-only V9 continuation evidence. No engine writes."""
from __future__ import annotations
import csv,hashlib,json,os,shutil,sys,zipfile
from pathlib import Path
R=Path('/mnt/data/V9_continue');W=Path('/mnt/data/V9_work');D=R/'packages';D.mkdir(parents=True,exist_ok=True)
TOOL_DIR=R/'tooling';O=R/'results'

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

input_manifest=json.loads((W/'tooling/inputs_verified.json').read_text());data=[]
for item in input_manifest['datasets']:
 p=Path('/mnt/data')/item['file'];val=sha(p)
 data.append({'file':item['file'],'expected_sha256':item['raw_sha256'],'actual_sha256':val,'bytes':p.stat().st_size,'status':'PASS' if val==item['raw_sha256'] else 'FAIL'})
if any(x['status']!='PASS' for x in data):raise RuntimeError('RAW SHA mismatch')

stem_paths=list((O/'meter').glob('*.summary.json'))
meters=[json.loads(p.read_text()) for p in stem_paths]
meters=[x for x in meters if x.get('variant')=='v81' and x.get('stable_pass')]
meters.sort(key=lambda x:x['dataset_id'])
if len(meters)!=5:raise RuntimeError('Expected five completed metered runs: '+str(len(meters)))
with (D/'V9_METER_COMPLETE_5_OF_7.csv').open('w',newline='') as fp:
 flds=['dataset_id','bars','variant','wall_s_instrumented','sampled_cpu_s','rss_mib','operation_count_selected','stable_pass']
 writer=csv.DictWriter(fp,fieldnames=flds);writer.writeheader();writer.writerows([{k:x[k] for k in flds} for x in meters])
(O/'V9_METER_MERGED_5_OF_7.json').write_text(json.dumps(meters,indent=2))

old_manifest=json.loads((W/'output/MANIFEST.json').read_text())
mutations=json.loads((O/'V9_INTERNAL_MUTATION_TESTS.json').read_text())
paired=json.loads((O/'abba100k/paired_report.json').read_text())
trace_summaries={}
for variant in ('orig','v81'):
 for prefix in ('oil15k','xau15k'):
  f=O/(prefix+'_'+(variant if prefix=='oil15k' else ('original' if variant=='orig' else 'v81'))+'.summary.json')
  trace_summaries[f.stem]=json.loads(f.read_text())['events']
report={
 'schema':'tradingbot.v9.continuation.v1','date':'2026-11-24','branch':'refactor',
 'release_status':'INCOMPLETE','trace_coverage':'TRACE_COVERAGE_PARTIAL','claim_speedup':False,
 'pinned_correctness_oracle':'01d54ecf0149ebd15de92798be18810b6e2eb791',
 'performance_reference':'V8.1','prod_engine_source_changed':False,'raw_modified':False,
 'old_v9_results':{'freeze':True,'real_golden_stable_pass':'7/7','synthetic_stable_pass':'4/4 (100k,250k,500k,1M)',
     'output_boundary_trace_pass':'7/7','deep_E_selected_pass':True,'live_selected_pass':'3/3',
     'strict_golden_mutation_assertions_pass':'16/16'},
 'new_evidence':{
     'internal_trace_observer_on_off_stable':'2/2 short RAW, original & V8.1 full native both; all four stable equal',
     'internal_trace_scoped_family_sequence_equal':'2/2 PASS for selected family-local outcome comparison, not global chronology',
     'oil_15k_rejection_reasons_observed_each':151,
     'internal_observer_trace_events':trace_summaries,
     'internal_comparator_mutation_tests':f"{sum(x['assertion']=='PASS' for x in mutations['tests'])}/{len(mutations['tests'])}",
     'ast_meter_original_vs_v81_on_oil_15k':'PASS stable bytes',
     'ast_meter_real_v81_completed':[x['dataset_id'] for x in meters],
     'ast_meter_real_v81_complete_count':len(meters),
     'ast_meter_real_v81_incomplete':['3 (247851-row RAW): execution time exceeded tool limit','6 (284184-row RAW): not run'],
     'abba100k_native_runs':'4/4 PASS, one ABBA block',
     'abba100k_median_observed_ratio_no_promotion':round(paired['median_speed_ratio'],6),
     'instrumented_loop_site_counts':{'original':45,'v81':46},
 },
 'unmet_hard_gates':[
     'Lossless full in-process internal trace for all seven RAW and synthetic 1M, with all candidate and lifecycle transitions',
     'Cross-family global chronological tie order and complete pre/post authoritative state parity',
     'Full raw timestamp and exact rejection reason coverage for every candidate/gate and all OrderAudit branches',
     'Global exact scanned historical rows/cache hit-miss/sorts/heap and allocation counters for all high-volume RAW and 1M',
     'Repeated 1M unprofiled ABBA paired benchmarks (at least 3 full blocks)',
     'Full official regression test suite; selected E/Live/edge tests were executed previously, not entire repository test matrix',
     'Large metered RAW completion: instrumented 247851 rows timed out at 300s and 284184 rows not run',
 ],
 'status_rule':'Never label TOOLING VERIFIED or claim full-trace parity until every mandatory gate completes',
 'raw_integrity':data,
}
(D/'V9_CONTINUATION_STATUS.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))

md='''# TradingBot V9 continuation — refactor-branch execution audit

**Final status: `INCOMPLETE` — `TRACE_COVERAGE_PARTIAL` — NO-GO for `TOOLING VERIFIED`.**

All newly authored tooling/report changes were committed **only to the existing `refactor` branch**, under `engineering/refactor-v9/`. The branch was not merged with `main`; no engine runtime file, trading behavior or RAW input was overwritten. The pinned correctness anchor remains `01d54ecf0149ebd15de92798be18810b6e2eb791` and V8.1 remains the unchanged prior performance reference. The older V9 audit previously placed on `main` remains historical and was *copied* into `refactor`; this continuation made **no new `main` modifications**.

## Reused verified V9 baseline evidence

- Golden ZIP SHA/CRC and 15 original Git blob SHA: `PASS`.
- 7/7 complete original-vs-V8.1 native both-direction real RAW outputs at 30s from 5s rows: strict stable JSON and telemetry contract `PASS`.
- All 4 full-length synthetic scales (100k, 250k, 500k, 1M): native stable result parity `PASS` (previous single runs, not ABBA confidence).
- 7/7 stage-boundary JSONL snapshots equal. This is **final-output projection**, not internal event proof.
- Previous 3 Live selected and 6 synthetic edge scenarios passed; strict Golden verifier controlled mutation assertions re-run 16/16 `PASS`.

## Work executed in this continuation

1. Implemented **test-only** dynamic in-process method-result observer, versioned JSONL gzip event manifest, semantic dataclass/Decimal/datetime serializer, family-local deterministic comparator and fail-closed mutation tests. No Engine source edited.
2. Confirmed observer ON output equals pinned Golden on complete 15,061-row USOIL and 15,542-row XAUUSD for **both pinned original and V8.1** (4 complete executions). Collected ~16k/15k internal observer events per original/candidate USOIL and ~14k/14k for XAU.
3. For USOIL, the AST-instrumented `_zone` semantic rejection decision produced **151 identical `NO_ELIGIBLE_ORDER_AFTER_CANONICAL_ROUTE_FILTER` events per source**, without output change.
4. Compared 3,896 USOIL and 3,581 XAU function-return semantic events in **family-local execution order**: all compared families returned equal values and limited pre/post state summary. Excluded implementation-only method call patterns: USOIL 12,476 original invocations, XAU 11,240. The observer also revealed two families with input-level drift (`EZoneDetector._zone` and `SZoneDetector.reconcile_shared_order_stops`). These drifts are preserved in diagnostic reports, **not concealed** as full-pass results.
5. Developed an AST-based test-copy operation meter for selected Python `for`/`while`, sort, heap and E parent-stop cache paths; smoke output remained byte-identical. Complete metered raw jobs: 5/7 V8.1 datasets **PASS**; 247,851-row job hit tool execution timeout, 284,184-row not run. Exact counters are only for instrumented statement sites and exclude comprehensions/uninstrumented functions; these cannot be promoted to whole-Engine operation totals.
6. Executed one complete **unprofiled native 100k ABBA block (Original, V8.1, V8.1, Original), 4/4 stable parity PASS**; observed median Original/V8.1 wall ratio ~1.184 in this small sample. Not a V9 speedup, not a repeated 1M ABBA benchmark, and not a basis for performance promotion.
7. Controlled internal comparator mutation suite **6/6 assertions PASS**. Its deliberate cross-family reorder is *not* detected by the scoped family-local comparison; this known gap is included rather than represented as full chronological trace equality.
8. Added 25 previous V9 verification/profiling tools and eight new observer/counter/benchmark tools to `engineering/refactor-v9/` on the **refactor** branch; pinned source and archived Baseline remain untouched.

## Why V9 is not complete

Hard gates still missing: full lossless in-process event capture of candidate rejection, stage handoff, OrderAudit, Parent Stop/StopAll and pre/post accepted ledgers on **all seven** real RAW and 1M synthetic; trace-global chronological tie comparison (not only family local); complete precise per-operation scanner/cache/sort/heap/allocation statistics, including large metered jobs; three or more 1M ABBA blocks with unprofiled CPUs/RSS; and the full official regression suite. Some tests are **NOT RUN** and one large metered run was **INTERRUPTED BY TOOL TIMEOUT**. The existing successful 7/7 native output parity does not discharge those independent trace/benchmark gates.

## Release decision

`INCOMPLETE / TRACE_COVERAGE_PARTIAL / NO PERFORMANCE PROMOTION`. Preserve V8.1 as the previous performance reference and keep this V9 tooling in `refactor` only. Archive JSON/CSV plus source alongside the preceding V9 TOOLING and VERIFICATION ZIPs in ChatGPT Library `/TradingBot/Versions/V9-2026-11-24/`. No claim of universal semantic equality, no `TOOLING VERIFIED` status and no change to production code.
'''
(D/'V9_CONTINUATION_AUDIT.md').write_text(md)

# Two packages: source/scripts and current verified evidence only.
files_tool=[p for p in TOOL_DIR.iterdir() if p.is_file() and p.suffix=='.py']
files_tool+= [D/'V9_CONTINUATION_AUDIT.md',D/'V9_CONTINUATION_STATUS.json',D/'V9_METER_COMPLETE_5_OF_7.csv']
prev_tools=[p for p in (W/'tooling').iterdir() if p.is_file() and p.suffix in ('.py','.json','.sh')]
tool_entries=[(p,'tooling_new/'+p.name) for p in files_tool if p.suffix=='.py']+[(p,'tooling_prior/'+p.name) for p in prev_tools]
tool_entries +=[(p,'reports/'+p.name) for p in files_tool if p.suffix!='.py']

# Selected raw-byte-verifiable logs. Keep finite; no market RAW/production sources in delivery.
paths=[]
for pat in ('*.internal.jsonl.gz','*.internal.jsonl.gz.manifest.json','*.v2.trace.jsonl.gz',
            '*.v2.trace.jsonl.gz.manifest.json','*.summary.json','*internal*_comparison.json',
            '*.meter.json','V9_INTERNAL_MUTATION_TESTS.json','V9_METER_MERGED_5_OF_7.json'):
    paths.extend(O.glob(pat))
paths.extend((O/'meter').glob('*.counters.json'))
paths.extend((O/'meter').glob('*.summary.json'))
paths.append(O/'abba100k/paired_report.json')
paths += [W/'output/V9_REAL_PARITY.json',W/'output/V9_SYNTHETIC_PARITY.json',W/'output/V9_TRACE_COVERAGE.json',
          W/'output/V9_FIRST_DIFF_TESTS.json',W/'output/V9_FREEZE_AUDIT.json',W/'output/V9_COMPLEXITY_MAP.md',
          W/'output/V9_GOLDEN_TRACE_SPEC.md',W/'output/V9_CPROFILE_FUNCTIONS_97K.csv',W/'output/V9_PROFILING.csv',
          W/'output/V9_STAGE_PROFILE.csv',W/'output/V9_SYNTHETIC_SCALING.png']
seen=set();result_entries=[]
for p in paths:
    if p.exists() and p.is_file() and str(p) not in seen:
        seen.add(str(p))
        rel='continuation/'+p.relative_to(O).as_posix() if p.is_relative_to(O) else 'previous_v9/'+p.name
        result_entries.append((p,rel))
result_entries += [(p,'reports/'+p.name) for p in (D/'V9_CONTINUATION_AUDIT.md',D/'V9_CONTINUATION_STATUS.json',D/'V9_METER_COMPLETE_5_OF_7.csv')]

created=[]
for name,entries in [('TradingBot_V9_REFACTOR_CONTINUATION_TOOLING_20261124.zip',tool_entries),('TradingBot_V9_REFACTOR_CONTINUATION_EVIDENCE_20261124.zip',result_entries)]:
    path=D/name
    ordered=sorted(entries,key=lambda x:x[1])
    sums=''.join(f'{sha(p)}  {member}\n' for p,member in ordered)
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p,member in ordered:z.write(p,member)
        z.writestr('SHA256SUMS.txt',sums)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for row in sums.splitlines():
            h,rel=row.split('  ',1)
            if hashlib.sha256(z.read(rel)).hexdigest()!=h:raise RuntimeError('Archive member SHA mismatch '+rel)
    created.append({'archive':name,'bytes':path.stat().st_size,'sha256':sha(path),'members':len(ordered),
                    'crc':'PASS','member_sha256':'PASS'})
    (D/(name+'.sha256')).write_text(f'{sha(path)}  {name}\n')
(D/'V9_PACKAGES.json').write_text(json.dumps(created,indent=2))
print(json.dumps({'status':'INCOMPLETE','meter_verified':len(meters),'old_v9_7_raw_pass':True,'packages':created},indent=2))
