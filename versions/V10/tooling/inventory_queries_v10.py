"""Read-only V8.1 query inventory and concrete source-call locations; no dynamic dispatch claim."""
import ast,argparse,csv,json,pstats,hashlib
from pathlib import Path
from ledger_delta_v9 import source_check

QUERIES={
 '_discover_candidate_chains':('E accepted chain discovery','MUTABLE','recursion, candidate order and parent identity; owner changes on reconciliation','profile first; not a pure range lookup'),
 '_zone':('E candidate decision','MUTABLE','first acceptable Order, strict stops, disowned-S; exact pre/post ownership','never cache whole decision without state epoch'),
 '_compute_reconciliation':('E heap/accepted map','MUTABLE','heap chronological ties, revalidation and regeneration','no change to priority keys'),
 'order_candidates':('OrderAudit candidate set','MUTABLE','gate/start/deadline, reset-leg and parent-stop owner; stable sorted ties','existing detector-local cache; sequence resets clear'),
 '_compute_direct_parent_stop_order':('Order_A historical search','CONDITIONAL','first >= gate then confirmations strictly > threshold, blocked first exception; compare independent vs geometric','candidate confirmation skip only; native frequency unknown'),
 '_first_healthy_direct_geometry':('Order_A geometry and reset veto','MUTABLE','restart on first reset with search_event < reset <= confirmation; native candidate identity','geometry callback not assumed pure'),
 '_order_b_legs_after':('Order_B immutable leg view','CONDITIONAL','strict first > start, original insertion order; no future leg selection','existing bisect + ordered fallback'),
 '_iter_post_stop_accepted_orders':('OrderAudit physical ledger','MUTABLE','stop time then confirmation then descending first index; reset eligibility at query time','existing lazy initial/audit merge, append/pending, rebuild invalidation'),
 '_carried_orders_for_parent':('OrderAudit physical ledger','MUTABLE','lifecycle_start < created < parent_stop, confirmation <= stop, crossed >= stop; stable tie','existing creation index, cause-sensitive invalidation'),
 '_first_parent_stop':('native RAW chronology','CONDITIONAL','strict crossing with [start,end) and first RAW index, exact Decimal','V8.1 pass-local pure cache; separate Live route'),
 '_search_first':('LowerTimeframeIndex','CONDITIONAL','strict threshold, chronological earliest, [left,right); no min/max winner swap','existing segment tree; no redundant new range tree'),
 '_range_query':('LowerTimeframeIndex','CONDITIONAL','[left,right); earliest position on exact tie','existing extrema tree; preserve exception on empty')}

def run(root,case,profile,out):
 source_check(root,case['source_sha256']['v81']);stats=pstats.Stats(str(profile)).stats;nodes=[];calls=[];mut=[];imports=[]
 for p in sorted([*root.glob('bridge/*.py'),*root.glob('pipeline/*.py')]):
  rel=p.relative_to(root).as_posix();tree=ast.parse(p.read_bytes());
  for x in ast.walk(tree):
   if isinstance(x,(ast.Import,ast.ImportFrom)):imports.append({'file':rel,'line':x.lineno,'syntax':ast.unparse(x)})
   if isinstance(x,ast.Call):
    q=x.func.attr if isinstance(x.func,ast.Attribute) else x.func.id if isinstance(x.func,ast.Name) else None
    if q in QUERIES:calls.append({'file':rel,'line':x.lineno,'target_symbol':q})
    if q in ('clear','append','extend','add','remove','pop','update','setdefault','discard','insert','sort','heappush','heappop','insort'):mut.append({'file':rel,'line':x.lineno,'kind':'potential mutation call','syntax':ast.unparse(x)[:180]})
   if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name in QUERIES:
    owner,purity,contract,guard=QUERIES[x.name];match=[v for k,v in stats.items() if k[2]==x.name and k[1]==x.lineno and Path(k[0]).name==p.name];data=match[0] if len(match)==1 else None
    nodes.append({'file':rel,'line':x.lineno,'end_line':x.end_lineno,'query':x.name,'owner':owner,'purity':purity,'contract':contract,'guard':guard,'loops':sum(isinstance(y,(ast.For,ast.While,ast.comprehension)) for y in ast.walk(x)),'profile_calls':data[1] if data else None,'exclusive_s':data[2] if data else None,'cumulative_s':data[3] if data else None})
   if isinstance(x,(ast.Assign,ast.AugAssign,ast.AnnAssign,ast.Delete)):
    targets=x.targets if isinstance(x,(ast.Assign,ast.Delete)) else [x.target]
    for target in targets:
     if isinstance(target,(ast.Attribute,ast.Subscript)):mut.append({'file':rel,'line':x.lineno,'kind':'potential assignment/delete','syntax':ast.unparse(target)[:180]})
 out.mkdir(parents=True,exist_ok=True);(out/'source-site-inventory.json').write_text(json.dumps({'scope':'Conservative syntax inventory, not all aliases/dynamic dispatch or executed semantic mutations','imports':imports,'query_calls':calls,'potential_mutations':mut},indent=2)+'\n');
 with (out/'V10_HISTORICAL_QUERY_INVENTORY.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(nodes[0]));w.writeheader();w.writerows(nodes)
 (out/'query-summary.json').write_text(json.dumps({'status':'SCOPED_INVENTORY','query_definitions':len(nodes),'name_matched_callsites':len(calls),'potential_mutation_sites':len(mut),'profile_case':15061,'profile_scope':'one V8.1 cProfile invocation, not exclusive range query microtime or full scale','source_sha256':case['source_sha256']['v81']},indent=2)+'\n');print(len(nodes),len(calls),len(mut),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--case',type=Path,required=True);p.add_argument('--profile',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.root,json.loads(a.case.read_text()),a.profile,a.out)
