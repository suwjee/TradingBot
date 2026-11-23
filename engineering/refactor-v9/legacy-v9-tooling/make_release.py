#!/usr/bin/env python3
"""Create integrity-checked, deterministic-ish V9 test-only deliverables; do not alter Source/RAW."""
import csv,hashlib,json,os,sys,zipfile,shutil,subprocess,tempfile,py_compile
from pathlib import Path
W=Path(__file__).resolve().parents[1];O=W/'output';SRC=W/'v81/engine'
DELIVERY=Path('/mnt/data/V9_delivery');DELIVERY.mkdir(exist_ok=True)
M=json.loads((W/'tooling/inputs_verified.json').read_text());freeze=json.loads((O/'V9_FREEZE_AUDIT.json').read_text())
real=json.loads((O/'V9_REAL_PARITY.json').read_text());sy=json.loads((O/'V9_SYNTHETIC_PARITY.json').read_text()) if (O/'V9_SYNTHETIC_PARITY.json').exists() else []
trace=json.loads((O/'V9_TRACE_COVERAGE.json').read_text()) if (O/'V9_TRACE_COVERAGE.json').exists() else None
live=json.loads((O/'V9_LIVE_VERIFICATION.json').read_text()) if (O/'V9_LIVE_VERIFICATION.json').exists() else {}
edge=json.loads((O/'V9_EDGE_CASES.json').read_text()) if (O/'V9_EDGE_CASES.json').exists() else {}
e_trace=[json.loads((O/f'V9_E_INTERNAL_{which}.json').read_text()) for which in ('XAU','OIL') if (O/f'V9_E_INTERNAL_{which}.json').exists()]
stage_trace=[json.loads((O/f'V9_NATIVE_STAGES_{which}.json').read_text()) for which in ('XAU','OIL') if (O/f'V9_NATIVE_STAGES_{which}.json').exists()]
allocation=json.loads((O/'V9_TRACEMALLOC_SAMPLE_ENGINE.json').read_text()) if (O/'V9_TRACEMALLOC_SAMPLE_ENGINE.json').exists() else {}
mutations=json.loads((O/'V9_FIRST_DIFF_TESTS.json').read_text());api=json.loads((O/'V9_PUBLIC_CONTRACT_AUDIT.json').read_text())
scaling_complete=len(sy)==4 and all(x['status']=='PASS' for x in sy);real_complete=len(real)==7 and all(x['status']=='PASS' for x in real)
boundary_complete=bool(trace and trace['all_boundary_pass'])
TOTAL=sum(x['wall_s'] for x in real)
samples=[{'bars':x['bars'],'original_s':x['baseline_wall_s'],'v81_s':x['candidate_wall_s'],'ratio':round(x['baseline_wall_s']/x['candidate_wall_s'],5) if x['candidate_wall_s'] else None,
          'rss_mib_original':x['baseline_rss'],'rss_mib_v81':x['candidate_rss'],'status':x['status']} for x in sy]
for i,row in enumerate(samples):
 if i and row['bars']==2*samples[i-1]['bars']:
  row['original_T2N_over_TN']=round(row['original_s']/samples[i-1]['original_s'],4)
  row['v81_T2N_over_TN']=round(row['v81_s']/samples[i-1]['v81_s'],4)
 else:
  row['original_T2N_over_TN']=None;row['v81_T2N_over_TN']=None
release='INCOMPLETE' # full internal semantic event trace & instrumentation safe ON/OFF NOT proved.
manifest={'version':'V9','release_kind':'TOOLING_ONLY','status':release,'performance_promotion':'NOT PROMOTED',
          'correctness_oracle_git_commit':M['baseline_git_commit'], 'golden_zip_sha256':'080175abbd7a3895596230b40783062901deb38c0cc8dd3b97fc058ef21cbb88',
          'previous_performance_reference':'V8.1','production_python_files_changed':0,'raw_files_modified':0,
          'unprofiled_real_full_raw_pass':real_complete,'real_files_passed':sum(x['status']=='PASS' for x in real),'real_files_total':len(M['datasets']),
          'synthetic_scales_complete':scaling_complete,'synthetic_scales_passed':sum(x['status']=='PASS' for x in sy),
          'boundary_trace_scope':'STAGE_BOUNDARY_ONLY','boundary_traces_7_of_7_pass':boundary_complete,'full_semantic_internal_trace':'NOT RUN',
          'live_three_cases_pass':live.get('status')=='PASS' and len(live.get('cases',[]))==3,
          'six_synthetic_edges_pass':edge.get('status')=='PASS' and len(edge.get('results',[]))==6,
          'deep_E_selected':len(e_trace)==2 and all(x.get('status')=='PASS' for x in e_trace),
          'native_stage_selected':len(stage_trace)==2 and all(x.get('status')=='PASS' for x in stage_trace),
          'tracemalloc_sample_parity':allocation.get('parity',False),
          'verifier_mutation_all_pass':mutations['all_test_assertions_pass'],'static_api_compile_equal':api['static_api_match'] and not api['compile_errors'],
          'environment':freeze['environment'],'real_wall_s_sum':round(TOTAL,6),'synthetic':samples,
          'go_nogo':'NO-GO for declaring TOOLING VERIFIED, since full internal semantic trace + 1M complete + Live/edge verification + full per-operation profiles are all required. Completed items separately recorded.',
          'limitation':'single unpaired synthetic performance observation per source/size; no V9 production speedup implied',
          'data_source_archives':[x['archive'] for x in freeze['archives']]}
(O/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
(O/'PARITY.json').write_text(json.dumps({'status':'PASS' if real_complete else 'INCOMPLETE','scope':'7 native V8.1 output stable byte comparisons against pinned Golden, timing schema validated',
    'real_raw':real,'synthetic':sy,'internal_trace_equal':None,'note':'No universal behavior, candidate rejection, or chronology proof from stage-boundary snapshots.'},indent=2,ensure_ascii=False))
(O/'TRACE_DIFF.json').write_text(json.dumps({'status':'PASS' if boundary_complete else 'INCOMPLETE','scope':'STAGE_BOUNDARY_ONLY',
    'all_boundary_equal':boundary_complete,'full_internal_trace_equal':None,'coverage_status':'TRACE_COVERAGE_PARTIAL',
    'first_divergence':None if boundary_complete else 'not complete; inspect per-file V9_TRACE_COVERAGE.json',
    'mutation_tests':mutations['all_test_assertions_pass']},indent=2))
shutil.copy2(O/'V9_PROFILING.csv',O/'PERF.csv')
synlines=[]
for row in samples:
 synlines.append(f"- {row['bars']:,}: original {row['original_s']:.3f}s vs V8.1 {row['v81_s']:.3f}s, ratio original/V8.1 {row['ratio']:.3f}x, parity `{row['status']}`, RSS {row['rss_mib_original']:.1f} / {row['rss_mib_v81']:.1f} MiB.")
readme=f'''# TradingBot V9 — tooling-only release (2026-11-24)

**Release status: `{release}`. This package does NOT claim `TOOLING VERIFIED`, `PARITY_VERIFIED` (all required gates) or performance promotion.**

## Identity, scope and no-change warranty

- Original Golden commit `{M['baseline_git_commit']}`; validated 15 Git blobs and Golden ZIP SHA256 against frozen manifest.
- V8.1 unchanged is the last verified *performance reference*; no V9 production Source patch exists.
- Seven immutable 5s RAW files totaling 791174 rows, all stages on, `--timeframe 30 --raw-timeframe 5 --direction both` in one Engine invocation per file.
- **Seven native full RAW Golden output comparisons: {sum(x['status']=='PASS' for x in real)}/7 PASS**. Unprofiled total wall observation {TOTAL:.3f}s; this is not a release speedup versus any version.
- **Synthetic {sum(x['status']=='PASS' for x in sy)}/{4} complete equal source comparisons**. Synthetic JSON derived from deterministic generator seed, no 5-minute RAW interpolation.
- **Stage-boundary traces: {'7/7 equal' if boundary_complete else 'NOT COMPLETED'}**. This is projected trace from already serialized outputs, NOT full internal semantic execution trace. **`TRACE_COVERAGE_PARTIAL`**.
- Verifier mutation/control tests: {sum(x['test_status']=='PASS' for x in mutations['tests'])}/{len(mutations['tests'])} passed.
- Selected internal E trace XAU+OIL: {'2/2 PASS' if len(e_trace)==2 and all(x.get('status')=='PASS' for x in e_trace) else 'INCOMPLETE'}; native stage-return snapshots {'2/2 PASS' if len(stage_trace)==2 and all(x.get('status')=='PASS' for x in stage_trace) else 'INCOMPLETE'}. This is *selected coverage*, not 7 full-event traces.
- Live seed/append, mismatch and changed-source error paths: {'3/3 PASS' if live.get('status')=='PASS' else 'INCOMPLETE'}. Six separate adversarial synthetic cases: {'6/6 PASS' if edge.get('status')=='PASS' else 'INCOMPLETE'}.
- Test-only tracemalloc+GC sampled 15k raw: {'PASS' if allocation.get('parity') else 'INCOMPLETE'}, profile isolated from production runs.
- Upstream verifier issue: requires native JSON to end in `}}` rather than `}}\\n`; and does not reject additional top-level `timings` keys. The test-only strict comparator fixes this, frozen ZIP/GitHub code unchanged.
- Static public CLI/API/signature audit: {'PASS' if api['static_api_match'] and not api['compile_errors'] else 'INCOMPLETE'}.

## Synthetic measurements (single non-paired runs — not statistically stable)

{chr(10).join(synlines) if synlines else 'No completed synthetic comparisons.'}

## Files and reproducibility

TOOLING ZIP contains all standalone tool source files, deterministic trace specification, complexity/state map and audit; VERIFICATION ZIP contains actual fresh native result JSON for every completed verification, CPU and RSS observations, synthetic outputs, gzip stage-boundary traces when present, source/trace manifests, cProfile and charts. The raw input bytes and original protected Golden baseline ZIP are intentionally NOT duplicated: retrieve the byte-pinned files separately. Test-only scripts have working directory defaults rooted in the execution workspace; to reproduce, place the two original source trees, frozen Golden ZIP and seven RAWs at the paths in scripts or adapt those paths *in a copy of tooling*, never in production. Set `PYTHONHASHSEED=0`, use Python 3.13 and the original flags.

### Standalone trace comparison

`python tooling/first_divergence.py --expected BASELINE.jsonl.gz --actual V81.jsonl.gz --context 2 --output first_diff.json`

### Reproduced status and gaps

`V9.0 PASS`, `V9.1 STATIC PASS`, `V9.2 STAGE_BOUNDARY PASS if complete; FULL INTERNAL TRACE NOT RUN`, `V9.3 REAL PASS + SYNTHETIC {sum(x['status']=='PASS' for x in sy)}/4; cProfile on 15k only; no complete scanned-row / cache-hit / heap-op counters`, `V9.4 INCOMPLETE`. Live/edge/memory sample status recorded in audit. `TOOLING VERIFIED` is not permitted.
'''
(O/'README.md').write_text(readme)
checks='''# Engine V9 verification audit (tooling only)

## Final gates

'''
gates={'Pinned Golden ZIP checksum/CRC/SHA256SUMS':'PASS','15 immutable GitHub blob hashes':'PASS','7 complete original RAW input hashes/counts':'PASS',
       'Golden stable self-check':'PASS','7 V8.1 full RAW native both-direction parity':'PASS' if real_complete else 'INCOMPLETE',
       'Synthetic 100k / 250k / 500k / 1M parity':'PASS' if scaling_complete else 'INCOMPLETE',
       'Verifier mutation suite':'PASS' if mutations['all_test_assertions_pass'] else 'FAIL',
       'Full semantic internal trace all seven':'NOT RUN','Stage boundary extracted equality':'PASS' if boundary_complete else 'INCOMPLETE',
       'CLI/API static audit':'PASS' if api['static_api_match'] else 'INCOMPLETE',
       'Selected E internal two small cases':'PASS' if len(e_trace)==2 and all(x.get('status')=='PASS' for x in e_trace) else 'INCOMPLETE',
       'Selected Stage-return two small cases':'PASS' if len(stage_trace)==2 and all(x.get('status')=='PASS' for x in stage_trace) else 'INCOMPLETE',
       'Live seed/append/error 3 cases':'PASS' if live.get('status')=='PASS' else 'INCOMPLETE',
       'Synthetic edge variants 6 cases':'PASS' if edge.get('status')=='PASS' else 'INCOMPLETE',
       'Isolated tracemalloc/GC profile parity':'PASS' if allocation.get('parity') else 'INCOMPLETE',
       'Production runtime source changed':'NO','Repeated AB/BA paired bench at 1M':'NOT RUN','Cache/scanned/heap/alloc high-volume instrumented counters':'NOT RUN'}
for k,v in gates.items():checks+=f'- **{k}**: `{v}`\n'
checks+='''
## Findings & methodology

The pinned original source, the separate V8.1 current performance reference, the same seven unchanged 5s RAW, and native both-direction processing were verified independently. Native final serialized output is compared after stripping *only the trailing numeric telemetry values*, with timing keys/order/type and all non-timing bytes preserved. Exact syntax, direction, chronology, Decimal representation, entity/source identity, OrderAudit, state and output ordering are all covered **to the extent serialized in native final JSON**.

`V9_STAGE_PROFILE.csv` contains real measured per-stage sum, whereas `V9_CPROFILE_FUNCTIONS.csv` reports exclusive (self) and inclusive (cumulative) CPU times, which must not be added across parent/child call stacks. Peak RSS comes from a 25/40ms sample and may underestimate true peak. One synthetic run per size/version is insufficient for stable speedup promotion.

Full internal semantically meaningful E candidate rejection / ownership / parent Stop / Live transition execution traces are **not implemented**. Stage-output projection is not a substitute. ON/OFF Engine final stable parity can be established for the *post-hoc* extractor only (no in-process instrumentation was used). Full-event lossless tracing, tested source-specific counters, allocation profiles across the full scale, repeated paired benchmark and formal edge coverage remain outstanding. That is why V9 status is `INCOMPLETE` even if all observed output SHA checks pass.

## Rejected shortcuts and safety

No trading source was refactored. No feature stage was disabled or a dataset truncated. No Decimal rounding, float conversion, OHLC-based intrabar chronology reconstruction, special-case file/price branch or independent bullish/bearish process merge was used. The existing V8.2 experiment is not promoted. The frozen original and V8.1 Source ZIPs were not overwritten.
'''
(O/'ENGINE_V9_AUDIT.md').write_text(checks)
# select file tree
small={}
for p in (W/'tooling').glob('*.py'):small['tooling/'+p.name]=p
for p in [W/'tooling/inputs_verified.json', O/'README.md',O/'ENGINE_V9_AUDIT.md',O/'V9_COMPLEXITY_MAP.md',O/'V9_GOLDEN_TRACE_SPEC.md',O/'CHANGELOG.md',O/'REJECTED_EXPERIMENTS.md',O/'MANIFEST.json',O/'V9_FIRST_DIFF_TESTS.json',O/'V9_FREEZE_AUDIT.json',O/'V9_PUBLIC_CONTRACT_AUDIT.json',O/'V9_SOURCE_FLOW.json',O/'V9_CALL_GRAPH.dot',O/'V9_CALL_GRAPH.svg',O/'V9_COMPLEXITY_RISKS.csv',O/'V9_CPROFILE_FUNCTIONS.csv',O/'V9_HOT_FUNCTION_COUNTS.json',O/'V9_CPROFILE_EXCLUSIVE.png',O/'V9_CPROFILE_FUNCTIONS_97K.csv',O/'V9_CPROFILE_EXCLUSIVE_97K.png',O/'V9_HOT_FUNCTION_COUNTS_97K.json',O/'V9_SYNTHETIC_SCALING_ANALYSIS.json',O/'V9_BOTTLENECK_SAVED_TIME_ESTIMATES_1M.csv',O/'V9_SYNTHETIC_SCALING.png',O/'V9_STAGE_WALL_PROFILE.png']:
 if p.exists():small[('verification/' if p.parent==O else 'tooling/')+p.name]=p
big={}
for p in sorted(O.iterdir()):
 if p.is_file() and p.suffix in ('.json','.csv','.md','.pstats','.png','.svg','.dot') or p.is_file() and p.name.endswith('.stderr.log'):
  big['verification/'+p.name]=p
for p in (O/'stage_boundary_traces').glob('*') if (O/'stage_boundary_traces').exists() else []:
 if p.is_file():big['verification/stage_boundary_traces/'+p.name]=p
for p in sorted(O.glob('*.v81.json')):big['verification/native_outputs/'+p.name]=p
for p in sorted(O.glob('synthetic_*_original.json')):big['verification/native_outputs/'+p.name]=p
for p in sorted(O.glob('synthetic_*_v81.json')):big['verification/native_outputs/'+p.name]=p
for file,sha in freeze['v81_source_sha256'].items():big['verified_source_V8.1/engine/'+file]=SRC/file
for file in freeze['source_blobs']:big['verified_source_golden/engine/'+file]=W/'golden/github_engine_commit_01d54ecf/engine'/file

def write_zip(filename,files):
 dest=DELIVERY/filename;hashes=[]
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for key,p in sorted(files.items()):
   content=p.read_bytes();sha=hashlib.sha256(content).hexdigest();hashes.append((key,sha))
   z.writestr(key,content)
  z.writestr('SHA256SUMS.txt', ''.join(f'{s}  {k}\n' for k,s in hashes).encode())
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None
  for key,sha in hashes:
   assert hashlib.sha256(z.read(key)).hexdigest()==sha,key
 return {'name':dest.name,'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'entries':len(hashes)+1,'crc_sha256sums_verified':True}
artifacts=[write_zip('TradingBot_Engine_V9_30S_BOTH_TOOLING_20261124.zip',small),
           write_zip('TradingBot_Engine_V9_30S_BOTH_VERIFICATION_20261124.zip',big)]
for a in artifacts:
 (DELIVERY/(a['name']+'.sha256')).write_text(a['sha256']+'  '+a['name']+'\n')
# extraction + import and compile smoke
with tempfile.TemporaryDirectory() as t:
 for a in artifacts:
  name=a['name'];sub=Path(t)/name;sub.mkdir()
  with zipfile.ZipFile(a['path']) as z:z.extractall(sub)
  for p in sub.rglob('*.py'):
   py_compile.compile(str(p),doraise=True)
  a['compile_smoke']='PASS'
(DELIVERY/'V9_ARCHIVE_AUDIT.json').write_text(json.dumps({'status':release,'archives':artifacts,'source_code_untouched':True,'golden_oracle_unchanged':True},indent=2))
print(json.dumps({'status':release,'real_passed':sum(x['status']=='PASS' for x in real),'synthetic_passed':sum(x['status']=='PASS' for x in sy),'boundary_trace_all_pass':boundary_complete,'archives':artifacts},indent=2))
