#!/usr/bin/env python3
"""Read-only runtime coverage of AST-identified state-mutation functions.

This profiler records calls only; it does NOT claim mutation truth or complete
semantic state trace. Uses unchanged source and native 30s/5s/BOTH output.
"""
from __future__ import annotations
import argparse,collections,json,sys
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import semantic_trace_v3 as observer


def run(engine,raw,first,last,inventory,report):
    engine=Path(engine).resolve()
    inv=json.loads(Path(inventory).read_text())
    risks=collections.defaultdict(list)
    for x in inv['untraced_mutators']:
        key=(Path(x['file']).name,x['function'].split('.')[-1])
        risks[key].append({'file':x['file'],'function':x['function'],'line':x['line'],'possible_sites':len(x['possible_mutation_points'])})
    seen=collections.Counter()
    examples={}
    def profiler(frame,event,arg):
        if event!='call':return
        code=frame.f_code
        filename=code.co_filename
        if not filename.startswith(str(engine)):return
        key=(Path(filename).name,code.co_name)
        if key in risks:
            seen[key]+=1
            if key not in examples:
                examples[key]={'executed_first_line':code.co_firstlineno,'source_file':filename}
    old=sys.getprofile()
    sys.setprofile(profiler)
    try:
        rc=observer.execute(SimpleNamespace(engine_root=engine,raw=Path(raw).resolve(),from_time=int(first),to_time=int(last),trace_out=None,summary=None,meter_output=None,stage_profile=None))
    finally:
        sys.setprofile(old)
    rows=[]
    for key,descs in risks.items():
        rows.append({'file_basename':key[0],'function_name':key[1],
                     'calls_observed':seen[key], 'possible_mutations':descs,
                     'runtime_line':examples.get(key,{}).get('executed_first_line')})
    info={'status':'CALL_COVERAGE_ONLY','engine_root':str(engine),'raw':str(raw),
          'source_exit_code':rc,'risk_methods_static':sum(len(q) for q in risks.values()),
          'unique_risk_method_keys':len(risks),'called_risk_method_keys':sum(v>0 for v in seen.values()),
          'runtime_total_calls_on_risk_methods':sum(seen.values()),
          'not_proved':'Mutations, first-event ordering, cache invalidation and semantic equivalence not established by call counters',
          'methods':rows}
    Path(report).write_text(json.dumps(info,indent=2))
    return rc

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for arg in ('engine','raw','first','last','inventory','report'):p.add_argument('--'+arg,required=True)
    a=p.parse_args();sys.exit(run(a.engine,a.raw,a.first,a.last,a.inventory,a.report))