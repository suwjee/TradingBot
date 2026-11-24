#!/usr/bin/env python3
"""Fail-closed V9 evidence merger: no inferred PASS from missing/partial runs.

No trading-source edits; final release remains INCOMPLETE if semantic coverage is
unverified even when output parity, compressed trace hashes, and tests all pass.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,os,platform,statistics,sys
from pathlib import Path
import psutil
BASE=Path('/mnt/data/V9_final')
PREV=Path('/mnt/data/V9_work/output')

def read(path):
    try:return json.loads(Path(path).read_text())
    except (FileNotFoundError,json.JSONDecodeError):return None

def env():
    return {'python':sys.version,'psutil':psutil.__version__,
            'system':platform.platform(),'machine':platform.machine(),
            'cpu_count_logical':os.cpu_count(),
            'cpu_affinity':sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
            'cgroup_cpu_max':Path('/sys/fs/cgroup/cpu.max').read_text().strip() if Path('/sys/fs/cgroup/cpu.max').is_file() else None,
            'pythonhashseed_for_benchmark_subprocess':'0',
            'benchmark_process_instrumentation':'OFF (own subprocess)'}

def gate(name,condition,evidence,scope=None):
    return {'gate':name,'status':'PASS' if condition is True else ('INCOMPLETE' if condition is None else 'FAIL'),
            'evidence':str(evidence),'scope':scope}

def all_valid_v9_trace(d,expected):
    if not d:return None
    rows=d.get('runs',[])
    native=[x for x in rows if x.get('variant') in ('original','v81')]
    compare=[x for x in rows if x.get('comparison_status')]
    if len(native)<expected*2 or len(compare)<expected:return None
    return all(x.get('status')=='PASS' and x.get('stable_pass') for x in native) and all(x.get('comparison_status')=='PASS' for x in compare)

def main(out):
    p=Path(out);p.mkdir(parents=True,exist_ok=True)
    freeze=read(BASE/'V9_FREEZE_AUDIT.json')
    v81=read(BASE/'V9_V81_SOURCE_IMMUTABILITY.json')
    meter=read(BASE/'V9_METER_COMPLETE_7_OF_7.json')
    original=read(PREV/'V9_REAL_PARITY.json')
    synthetic=read(PREV/'V9_SYNTHETIC_PARITY.json')
    live=read(PREV/'V9_LIVE_VERIFICATION.json')
    edge=read(BASE/'edge_trace/edge_trace_report.json')
    abba=read(BASE/'abba1m/paired_report.json')
    abba_real=read(BASE/'abba_real/aggregate.json')
    trace=read(BASE/'trace/trace_matrix_report.json')
    trace_synthetic=read(BASE/'trace_synthetic/synthetic_trace_report.json')
    meter_synthetic=read(BASE/'meter_synthetic/meter_synthetic_report.json')
    global_mut=read(BASE/'V9_GLOBAL_MUTATION_V3.json')
    sidecar_mut=read(BASE/'V9_SIDECAR_MUTATION_TESTS.json')
    steps=[]
    steps.append(gate('V9.0 frozen Golden archive, 15 blobs, 7 RAW SHA and stable fingerprints',freeze and freeze.get('status')=='PASS',BASE/'V9_FREEZE_AUDIT.json'))
    steps.append(gate('V8.1 production bytes unchanged after AST instrumenting',v81 and v81.get('status')=='PASS',BASE/'V9_V81_SOURCE_IMMUTABILITY.json'))
    steps.append(gate('Full native real RAW parity vs Golden 7/7',
        len(original)==7 and all(x.get('status')=='PASS' for x in original) if isinstance(original,list) else None,PREV/'V9_REAL_PARITY.json'))
    steps.append(gate('Full 4x synthetic native Original/V81 stable parity',
        len(synthetic)==4 and all(x.get('status')=='PASS' for x in synthetic) if isinstance(synthetic,list) else None,PREV/'V9_SYNTHETIC_PARITY.json'))
    steps.append(gate('7/7 real complete operation metering on AST V8.1 with stable parity',meter and meter.get('status')=='PASS',BASE/'V9_METER_COMPLETE_7_OF_7.json','Selected AST sites only'))
    steps.append(gate('4 synthetic scales x two sources AST loop/heap/cache counters',meter_synthetic.get('status')=='PASS' if meter_synthetic and meter_synthetic.get('status')!='INCOMPLETE' else None,BASE/'meter_synthetic/meter_synthetic_report.json','Selected AST sites only'))
    steps.append(gate('3x 1M ABBA unprofiled 12 full native BOTH process runs',abba.get('status')=='PASS' and abba.get('repeated_1m_gate_met') is True if abba and abba.get('status')!='INCOMPLETE' else None,BASE/'abba1m/paired_report.json'))
    steps.append(gate('2 small + 2 large real RAW each 3 ABBA/BAAB blocks',abba_real.get('status')=='PASS' and abba_real.get('completed_datasets')==4 if abba_real and abba_real.get('status')!='INCOMPLETE' else None,BASE/'abba_real/aggregate.json'))
    steps.append(gate('7/7 real Original/V81 compressed internal selected-event traces + semantic comparison',all_valid_v9_trace(trace,7),BASE/'trace/trace_matrix_report.json','Selected semantics, not all hidden state'))
    steps.append(gate('Synthetic 1M Original/V81 selected-event compressed trace + stable parity',trace_synthetic.get('selected_global_semantic_status')=='PASS' and trace_synthetic.get('full_raw_1m_trace_data_status')=='PASS' if trace_synthetic and trace_synthetic.get('full_raw_1m_trace_data_status') else None,BASE/'trace_synthetic/synthetic_trace_report.json','Selected semantics'))
    steps.append(gate('6 deterministic synthetic edge traces Original/V81 globally compared',edge and edge.get('status')=='PASS' and len(edge.get('comparisons',[]))==6,BASE/'edge_trace/edge_trace_report.json'))
    steps.append(gate('10 controlled global semantic comparator mutations',global_mut and global_mut.get('status')=='PASS' and global_mut.get('count')==10,BASE/'V9_GLOBAL_MUTATION_V3.json'))
    steps.append(gate('9 controlled gzip/hash/sidecar event mutations',sidecar_mut and sidecar_mut.get('status')=='PASS' and len(sidecar_mut.get('tests',[]))==9,BASE/'V9_SIDECAR_MUTATION_TESTS.json'))
    steps.append(gate('Official full pinned engine suite on actual V8.1', '545 passed' in (BASE/'tests/v81_pinned_official_unit_correct_layout.log').read_text() if (BASE/'tests/v81_pinned_official_unit_correct_layout.log').is_file() else None,BASE/'tests/v81_pinned_official_unit_correct_layout.log'))
    ast_logs=list((BASE/'tests').glob('*ast_instrumented*log'))
    ast_pass=any('545 passed' in x.read_text() for x in ast_logs)
    steps.append(gate('Official pinned Engine unit tests on AST instrumented V8.1 (545)',ast_pass if ast_logs else None,ast_logs[0] if ast_logs else BASE/'tests/AST_VERIFICATION_NOT_FOUND.log'))
    # Observable outcomes cannot by themselves prove every in-process branch,
    # cache invalidation transition, or arbitrarily mutable Python container.
    steps.append(gate('Complete lossless semantic internal state coverage across arbitrary event paths',None,'V9 contract and trace coverage audit','UNVERIFIED: selected observer still excludes several implementation branches and mutable Candidate revalidation'))
    failed=[x['gate'] for x in steps if x['status']=='FAIL'];pending=[x['gate'] for x in steps if x['status']=='INCOMPLETE']
    report={'phase':'V9','source_oracle':'01d54ecf0149ebd15de92798be18810b6e2eb791',
            'candidate':'unchanged V8.1 source (never promoted as V9 performance) ',
            'branch':'refactor','status':'INCOMPLETE' if pending or failed else 'TOOLING VERIFIED',
            'trace_coverage':'TRACE_COVERAGE_PARTIAL' if pending else 'SEMANTIC_COVERAGE_VERIFIED',
            'no_optimization_promotion':True,
            'gate_count':len(steps),'gate_passes':sum(x['status']=='PASS' for x in steps),
            'gate_pending':pending,'gate_failed':failed,'gates':steps,'execution_environment':env()}
    (p/'V9_RELEASE_GATE.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(report['status'],report['gate_passes'],'/',report['gate_count'],'pending',len(pending),'failed',len(failed))
    return 0 if not failed else 1
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='/mnt/data/V9_final/verification');opts=parser.parse_args()
    raise SystemExit(main(opts.out))
