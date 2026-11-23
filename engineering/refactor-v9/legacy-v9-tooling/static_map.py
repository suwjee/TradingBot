#!/usr/bin/env python3
"""AST-derived import/call map, source references, and complexity-risk hotspots (no execution effects)."""
import ast, json,csv,subprocess,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1]; R=W/'v81/engine';OUT=W/'output'
FILES=list(sorted((R/'pipeline').glob('*.py')))+list(sorted((R/'bridge').glob('*.py')))
risks=[];nodes=[];edges=[];symbols={};import_edges=[]
for p in FILES:
 mod=str(p.relative_to(R))
 s=p.read_text();t=ast.parse(s,filename=mod)
 for node in ast.walk(t):
  if isinstance(node,(ast.Import,ast.ImportFrom)):
   targets=[]
   if isinstance(node,ast.Import):targets=[a.name for a in node.names]
   elif node.module:targets=[node.module]
   for target in targets:import_edges.append({'caller_module':mod,'import':target,'line':node.lineno})
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
   nested_loops=0;loops=0;sorts=0;calls=[]
   for child in ast.walk(node):
    if isinstance(child,(ast.For,ast.While,ast.AsyncFor,ast.comprehension)):
     loops+=1
     if any(isinstance(gr,(ast.For,ast.While,ast.AsyncFor,ast.comprehension)) and gr is not child for gr in ast.walk(child)):
      nested_loops+=1
    if isinstance(child,ast.Call):
     name=child.func.attr if isinstance(child.func,ast.Attribute) else child.func.id if isinstance(child.func,ast.Name) else '?'
     calls.append((name,child.lineno))
     if name in ('sorted','sort'):sorts+=1
   item={'module':mod,'function':node.name,'start':node.lineno,'end':node.end_lineno,'span_lines':node.end_lineno-node.lineno+1,'loops':loops,'loop_with_nested_loop':nested_loops,'sort_calls':sorts,'calls':len(calls)}
   nodes.append(item);symbols.setdefault(node.name,[]).append(item)
   if loops>3 or nested_loops>0 or sorts>0:
    risks.append(item)
   for name,line in calls:edges.append({'caller':f'{mod}:{node.name}:{node.lineno}','callee_symbol':name,'callsite':f'{mod}:{line}'})
# source-level high-risk authoritative names in the actual checked V8.1 source
queries=['_discover_candidate_chains','_zone','order_candidates','_register_order_audit','_parent_stop',
         '_compute_reconciliation','calculate_full_direction_state','calculate_direction_with_order_b_feedback',
         'reconcile_shared_order_stops','calculate_primary_structures','main']
landmarks={q:[{'module':x['module'],'line':x['start'],'end_line':x['end'],'loops':x['loops'],'sort_calls':x['sort_calls']} for x in symbols.get(q,[])] for q in queries}
(OUT/'V9_SOURCE_FLOW.json').write_text(json.dumps({'source_root':'V8.1 verified ZIP (not production patch)',
 'nodes':nodes,'edges':edges,'imports':import_edges,'landmarks':landmarks},indent=2))
with (OUT/'V9_COMPLEXITY_RISKS.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['module','function','start','end','span_lines','loops','loop_with_nested_loop','sort_calls','calls']);writer.writeheader();writer.writerows(sorted(risks,key=lambda x:(x['loop_with_nested_loop'],x['loops'],x['sort_calls'],x['span_lines']),reverse=True))
# Inter-module call graph is approximate: name-based unresolved calls must never be treated as definitive wiring.
modules={x['module'] for x in nodes};g=['digraph TradingBot {','rankdir=LR;','node [shape=box,fontsize=10,fontname="Helvetica"];']
for m in sorted(modules):g.append('"'+m+'";')
for imp in import_edges:
 target=imp['import'].rsplit('.',1)[-1]; caller=imp['caller_module']
 for module in modules:
  if module!=caller and module.endswith('/'+target+'.py'):
   g.append('"'+caller+'" -> "'+module+'" [label="import L'+str(imp['line'])+'",color="gray"];')
for source,targets in [('bridge/trading_pipeline.py',['reaction_engine','blue_line_detector','a_zone_detector','s_zone_detector','e_zone_detector','lifecycle_engine','order_audit_engine','PL_PH_detector']),
                       ('bridge/live_pipeline.py',['trading_pipeline'])]:
 for target in targets:
  for module in modules:
   if module.endswith('/'+target+'.py'):
    if not any('"'+source+'" -> "'+module+'"' in row for row in g):g.append('"'+source+'" -> "'+module+'" [style=dotted,label="runtime dependency (inspect callsites)"];')
g.append('}')
dot=OUT/'V9_CALL_GRAPH.dot';dot.write_text('\n'.join(g));
subprocess.run(['dot','-Tsvg',str(dot),'-o',str(OUT/'V9_CALL_GRAPH.svg')],check=True)
subprocess.run(['dot','-Tpng',str(dot),'-o',str(OUT/'V9_CALL_GRAPH.png')],check=True)
print(json.dumps({'modules':len(modules),'functions':len(nodes),'callsites':len(edges),'risk_functions':len(risks),'landmarks':landmarks},ensure_ascii=False))
