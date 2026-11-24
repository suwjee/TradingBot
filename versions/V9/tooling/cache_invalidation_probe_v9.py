"""Controlled tests of actual pinned E and OrderAudit invalidation method bodies.
No Engine patch. Fixture ownership and assertions are explicit, not a proof of callers.
"""
import argparse, ast, datetime as dt, json, sys, hashlib
from pathlib import Path
from types import SimpleNamespace
from ledger_delta_v9 import source_check,snapshot

def extract(root,file,cls,method,arity):
    path=root/'pipeline'/file;tree=ast.parse(path.read_bytes());c=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
    n=next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name==method and len(n.args.args)==arity)
    n.decorator_list=[];m=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),n],type_ignores=[]);ns={};exec(compile(ast.fix_missing_locations(m),str(path),'exec'),ns);return ns[method],n.lineno

def exercise(root):
    definitions={};methods={}
    for name,file,cls,arity in [('sequence_resets','e_zone_detector.py','EZoneDetector',2),('_invalidate_carried_order_caches','order_audit_engine.py','OrderAuditEngineMixin',1),('_invalidate_post_stop_order_cache','order_audit_engine.py','OrderAuditEngineMixin',1),('_clear_order_audit','order_audit_engine.py','OrderAuditEngineMixin',1)]:
        methods[name],definitions[name]=extract(root,file,cls,name,arity)
    t=dt.datetime(2026,1,1);u=t+dt.timedelta(seconds=5);tests=[]
    for variant in ('empty','populated','repeat','reorder'):
        d=SimpleNamespace(_order_candidates_cache={'x':1},_carried_orders_cache={'y':2},_post_stop_orders_cache={'z':3},_direct_parent_stop_cache={'w':4},_registered_e_parent_stops={('e',1)},_parent_stop_query_cache={'unrelated':5},_cross_order_cache={'unrelated':6},order_audit={('k',1):{'value':1}},_order_audit_confirmation_index=[(t,1,2)],_carried_creation_index={'i':1},_carried_creation_append={'a':2},_post_stop_sorted_audit={'p':3},_post_stop_pending=[(t,1,2)])
        # Shared contract only: V8.1 additionally clears its own registration cache.
        old_ledger=snapshot(d.order_audit);old_pure=snapshot((d._parent_stop_query_cache,d._cross_order_cache));resets={} if variant=='empty' else {u:2,t:1} if variant=='reorder' else {t:1,u:2};n=2 if variant=='repeat' else 1
        for _ in range(n):
            methods['sequence_resets'](d,resets)
            assert snapshot(d._sequence_resets)==snapshot(resets) and d._sequence_resets is not resets and d._sequence_reset_times==sorted(resets)
            assert all(not getattr(d,k) for k in ('_order_candidates_cache','_carried_orders_cache','_post_stop_orders_cache','_direct_parent_stop_cache'))
            assert snapshot(d.order_audit)==old_ledger and snapshot((d._parent_stop_query_cache,d._cross_order_cache))==old_pure
        tests.append({'case':'sequence_resets/'+variant,'status':'PASS','registration_cache_empty':not d._registered_e_parent_stops})
    # Distinguish creation-dependent vs confirmation-dependent caches; preserve authoritative ledger.
    d._carried_orders_cache={'new':1};d._post_stop_orders_cache={'keep':2};old=snapshot(d.order_audit);methods['_invalidate_carried_order_caches'](d)
    assert not d._carried_orders_cache and d._carried_creation_index is None and d._carried_creation_append is None and d._post_stop_orders_cache=={'keep':2} and snapshot(d.order_audit)==old;tests.append({'case':'carried_only','status':'PASS'})
    d._carried_orders_cache={'keep':1};methods['_invalidate_post_stop_order_cache'](d);assert not d._post_stop_orders_cache and d._post_stop_sorted_audit is None and not d._post_stop_pending and d._carried_orders_cache=={'keep':1} and snapshot(d.order_audit)==old;tests.append({'case':'post_stop_only','status':'PASS'})
    d._invalidate_carried_order_caches=lambda:methods['_invalidate_carried_order_caches'](d);d._invalidate_post_stop_order_cache=lambda:methods['_invalidate_post_stop_order_cache'](d);methods['_clear_order_audit'](d);assert not d.order_audit and not d._order_audit_confirmation_index and not d._carried_orders_cache and not d._post_stop_orders_cache;tests.append({'case':'clear_ledger','status':'PASS'})
    return {'sites':definitions,'tests':tests}

def main():
    p=argparse.ArgumentParser();p.add_argument('--original',type=Path,required=True);p.add_argument('--v81',type=Path,required=True);p.add_argument('--case',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();m=json.loads(a.case.read_text());rows={}
    for name,root in [('original',a.original),('v81',a.v81)]:
        source_check(root,m['source_sha256'][name]);rows[name]=exercise(root);source_check(root,m['source_sha256'][name]);assert all(t['status']=='PASS' for t in rows[name]['tests'])
    assert all(not t['registration_cache_empty'] for t in rows['original']['tests'] if t['case'].startswith('sequence_resets/'))
    assert all(t['registration_cache_empty'] for t in rows['v81']['tests'] if t['case'].startswith('sequence_resets/'))
    r={'status':'PASS','total_assertion_cases':sum(len(x['tests']) for x in rows.values()),'scope':'Actual frozen source method bodies extracted via AST; controlled fixtures; no full call-chain or dynamic invalidation coverage','variants':rows,'full_semantic_state_status':'INCOMPLETE'};a.out.write_text(json.dumps(r,indent=2)+'\n');print('cache controlled',r['total_assertion_cases'],'PASS')
if __name__=='__main__':main()
