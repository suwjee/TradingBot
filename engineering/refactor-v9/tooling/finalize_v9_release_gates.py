#!/usr/bin/env python3
"""Fail-closed V9 completion gate, test-only, no production source mutations.

PASS is scope-specific. Release overall cannot become TOOLING VERIFIED while
full internal semantic coverage remains unproved, even if outputs match.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path

ROOT=Path('/mnt/data/V9_final')
WORK=Path('/mnt/data/V9_work/output')

def read(path):
 try:return json.loads(Path(path).read_text())
 except (OSError,ValueError):return None

def main(out):
 gates=[]
 def gate(name,status,details=None,source=None):
  assert status in ('PASS','FAIL','INCOMPLETE','NOT RUN')
  gates.append({'gate':name,'status':status,'details':details,'source':str(source) if source else None})

 freeze=read(ROOT/'V9_FREEZE_AUDIT.json')
 gate('Pinned commit, baseline ZIP SHA, 15 blobs, 7 RAW', 'PASS' if freeze and freeze.get('status')=='PASS' else 'INCOMPLETE',source=ROOT/'V9_FREEZE_AUDIT.json')
 immutable=read(ROOT/'V9_V81_SOURCE_IMMUTABILITY.json')
 gate('V8.1 source unchanged', 'PASS' if immutable and immutable.get('status')=='PASS' else 'INCOMPLETE',source=ROOT/'V9_V81_SOURCE_IMMUTABILITY.json')
 for text,label in [('V9_REAL_PARITY.json','7/7 Golden output parity'),('V9_SYNTHETIC_PARITY.json','Synthetic 100k/250k/500k/1m Golden parity')]:
  x=read(WORK/text);needed=7 if text=='V9_REAL_PARITY.json' else 4
  valid=(isinstance(x,list) and len(x)==needed and all(z.get('status')=='PASS' for z in x))
  gate(label,'PASS' if valid else 'INCOMPLETE',source=WORK/text)
 counter=read(ROOT/'V9_METER_COMPLETE_7_OF_7.json')
 gate('7/7 real RAW AST selected-site metering','PASS' if counter and counter.get('status')=='PASS' and counter.get('input_dataset_count')==7 else 'INCOMPLETE',source=ROOT/'V9_METER_COMPLETE_7_OF_7.json')
 meter=read('/mnt/data/V9_completion_20261124/V9_SYNTHETIC_METER_COMBINED.json') or read(ROOT/'meter_synthetic/meter_synthetic_report.json')
 metered={(x.get('bars'),x.get('variant')) for x in meter.get('rows',[]) if x.get('status')=='PASS'} if meter else set()
 complete_meters=all((n,v) in metered for n in (100000,250000,500000,1000000) for v in ('original','v81'))
 gate('4 x 2 complete synthetic selected-site meters', 'PASS' if complete_meters else 'INCOMPLETE',{'completed':len(metered),'expected':8},'/mnt/data/V9_completion_20261124/V9_SYNTHETIC_METER_COMBINED.json')
 paired=read(ROOT/'abba1m/paired_report.json')
 gate('3-block synthetic 1m native unprofiled ABBA', 'PASS' if paired and paired.get('status')=='PASS' and len(paired.get('runs',[]))>=12 else 'INCOMPLETE',{'runs':len(paired.get('runs',[])) if paired else 0},ROOT/'abba1m/paired_report.json')
 real=read(ROOT/'abba_real/aggregate.json')
 real_ok=bool(real and real.get('status')=='PASS' and real.get('completed_datasets')==4 and all(d.get('status')=='PASS' and len(d.get('rows',[]))>=12 for d in real.get('datasets',[])))
 gate('4 real datasets x 3-block ABBA/BAAB', 'PASS' if real_ok else 'INCOMPLETE',source=ROOT/'abba_real/aggregate.json')
 trace=read(ROOT/'trace/trace_matrix_report.json')
 complete_runs={(str(x.get('item')),x.get('variant')) for x in trace.get('runs',[]) if x.get('status')=='PASS' and x.get('stable_pass')} if trace else set()
 successful_pairs={str(x.get('item')) for x in trace.get('runs',[]) if x.get('comparison_status')=='PASS'} if trace else set()
 trace_ok=len(complete_runs)==14 and len(successful_pairs)==7
 gate('7 full RAW pair selected internal traces and global comparators','PASS' if trace_ok else 'INCOMPLETE',{'native_trace_runs':len(complete_runs),'expected':14,'global_selected_equal_pairs':len(successful_pairs),'expected_pairs':7,'coverage':'SELECTED ONLY'},ROOT/'trace/trace_matrix_report.json')
 synthetic_trace=read(ROOT/'trace_synthetic/synthetic_trace_report.json')
 syn_ok=bool(synthetic_trace and synthetic_trace.get('full_raw_1m_trace_data_status')=='PASS' and synthetic_trace.get('selected_global_semantic_status')=='PASS')
 gate('Full synthetic 1m selected in-process traces, native output parity','PASS' if syn_ok else 'INCOMPLETE',source=ROOT/'trace_synthetic/synthetic_trace_report.json')
 for path,label,threshold in [(ROOT/'tests/v81_ast_instrumented_official_unit.log','545 official tests on AST V8.1',545),(Path('/mnt/data/V9_completion_20261124/audits/official_full_pytest.log'),'545 official pinned tests',545)]:
  s=path.read_text(errors='replace') if path.is_file() else ''
  gate(label,'PASS' if f'{threshold} passed' in s else 'INCOMPLETE',source=path)
 reg=read(ROOT/'V9_GLOBAL_MUTATION_V3.json');side=read(ROOT/'V9_SIDECAR_MUTATION_TESTS.json')
 gate('Global first-divergence mutation suite','PASS' if reg and (reg.get('status')=='PASS' or reg.get('all_passed') is True) else 'INCOMPLETE',source=ROOT/'V9_GLOBAL_MUTATION_V3.json')
 gate('Hash/sidecar corruption mutation suite','PASS' if side and (side.get('status')=='PASS' or side.get('all_passed') is True) else 'INCOMPLETE',source=ROOT/'V9_SIDECAR_MUTATION_TESTS.json')
 state=read('/mnt/data/V9_completion_20261124/V9_AST_TRACE_GAPS.json')
 missing=state.get('possible_state_mutation_functions_without_selected_trace') if state else None
 gate('All semantic mutators and arbitrary Live state covered losslessly','INCOMPLETE',{'untraced_potential_mutator_functions':missing,'restriction':'Cannot assert full coverage of all possible state transitions from selected wrappers; missing mutation event topology.'},'/mnt/data/V9_completion_20261124/V9_AST_TRACE_GAPS.json')
 counts={s:sum(g['status']==s for g in gates) for s in ('PASS','FAIL','INCOMPLETE','NOT RUN')}
 result={'phase':'V9','branch':'refactor','correctness_oracle':'01d54ecf0149ebd15de92798be18810b6e2eb791',
         'overall':'TOOLING VERIFIED' if counts['INCOMPLETE']==counts['FAIL']==counts['NOT RUN']==0 else 'INCOMPLETE',
         'trace_coverage':'TRACE_COVERAGE_PARTIAL','production_runtime_changed':False,'no_V9_speedup_claim':True,
         'gate_counts':counts,'gates':gates}
 Path(out).parent.mkdir(parents=True,exist_ok=True);Path(out).write_text(json.dumps(result,indent=2,ensure_ascii=False))
 print(json.dumps({'overall':result['overall'],'gate_counts':counts},indent=2));return 0 if result['overall']=='TOOLING VERIFIED' else 2

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();sys.exit(main(a.out))