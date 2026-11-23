#!/usr/bin/env python3
"""Build never-promotable test-only AST-instrumented copy of exact source snapshot."""
from __future__ import annotations
import argparse,ast,hashlib,json,shutil
from pathlib import Path
TARGET={
 'pipeline/e_zone_detector.py':{'_discover_candidate_chains','_zone','_compute_reconciliation',
                                 '_reconcile_candidate_chains','_first_parent_stop','_search_parent_stop',
                                 '_build_zone','detect','_parent_stop'},
 'pipeline/order_audit_engine.py':{'order_candidates','_register_order_audit',
                                   '_compute_direct_parent_stop_order','_direct_parent_stop_order',
                                   '_rebuild_accepted_order_audit','rebuild_accepted_order_audit'},
 'pipeline/reaction_engine.py':{'_append_reaction','_append_reset','_detect','detect'},
 'pipeline/lifecycle_engine.py':{'detect_stopalls','_detect_events','reconcile_stopall_lifecycle'},
 'pipeline/PL_PH_detector.py':{'detect_bullish','detect_bearish'},
 'pipeline/s_zone_detector.py':{'_resolve_candidate','_detect','reconcile_shared_order_stops'},
}
OPS={'sorted','heappop','heappush','heapify','insort'}
class Meter(ast.NodeTransformer):
    def __init__(self,path):self.path=path;self.current=[];self.tags=set()
    def visit_FunctionDef(self,node):
        self.current.append(node.name)
        node=self.generic_visit(node)
        self.current.pop()
        return node
    visit_AsyncFunctionDef=visit_FunctionDef
    def enabled(self):return bool(self.current and self.current[-1] in TARGET[self.path])
    def tag(self,n,op):
        value=f'{self.path}:{self.current[-1]}:{n.lineno}:{op}'
        self.tags.add(value);return value
    def add_tick(self,node,op):
        if not self.enabled():return node
        tick=ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id='_v9_meter',ctx=ast.Load()),attr='tick',ctx=ast.Load()),args=[ast.Constant(self.tag(node,op))],keywords=[]))
        node.body.insert(0,ast.copy_location(tick,node))
        return node
    def visit_For(self,node):
        node=self.generic_visit(node)
        return self.add_tick(node,'for_iteration')
    def visit_While(self,node):
        node=self.generic_visit(node)
        return self.add_tick(node,'while_iteration')
    def visit_If(self,node):
        node=self.generic_visit(node)
        if self.enabled() and self.path=='pipeline/e_zone_detector.py' and self.current[-1]=='_zone':
            condition=ast.unparse(node.test)
            if 'order_match is None' in condition:
                self.add_tick(node,'reject_no_eligible_order')
            elif '_order_created_only_by_disowned_s' in condition:
                self.add_tick(node,'skip_disowned_s_order')
        if (self.enabled() and self.current[-1]=='_first_parent_stop'
             and isinstance(node.test,ast.Compare) and isinstance(node.test.left,ast.Name)
             and node.test.left.id=='cached' and len(node.test.ops)==1
             and isinstance(node.test.ops[0],ast.IsNot)):
            self.add_tick(node,'cache_hit')
            if not node.orelse:
                node.orelse=[ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id='_v9_meter',ctx=ast.Load()),attr='tick',ctx=ast.Load()),args=[ast.Constant(self.tag(node,'cache_miss'))],keywords=[]))]
            else:
                node.orelse.insert(0,ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id='_v9_meter',ctx=ast.Load()),attr='tick',ctx=ast.Load()),args=[ast.Constant(self.tag(node,'cache_miss'))],keywords=[])))
        return node
    def visit_Call(self,node):
        node=self.generic_visit(node)
        if not self.enabled():return node
        op=None
        if isinstance(node.func,ast.Name) and node.func.id in OPS:op=node.func.id
        elif isinstance(node.func,ast.Attribute) and node.func.attr=='sort':op='list.sort'
        if op is None:return node
        t=self.tag(node,op)
        call=ast.Call(func=ast.Attribute(value=ast.Name(id='_v9_meter',ctx=ast.Load()),attr='tap',ctx=ast.Load()),
                  args=[ast.Constant(t),node.func]+node.args,keywords=node.keywords)
        return ast.copy_location(call,node)

def sha(b):return hashlib.sha256(b).hexdigest()
def build(src,out):
    src=Path(src).resolve();out=Path(out).resolve()
    if out.exists():raise SystemExit('Refusing to overwrite existing instrumentation copy: '+str(out))
    out.mkdir(parents=True)
    manifest={'original_root':str(src),'instrumented_root':str(out),'never_production':True,'modules':{},'operation_site_counts':{}}
    for rel in sorted(x.relative_to(src) for x in src.rglob('*') if x.is_file() and x.suffix=='.py'):
        source=src/rel;dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        b=source.read_bytes(); relname=str(rel)
        if relname in TARGET:
            tree=ast.parse(b,filename=str(source));trans=Meter(relname);tree=trans.visit(tree)
            idx=0
            if tree.body and isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) and isinstance(tree.body[0].value.value,str):idx=1
            if len(tree.body)>idx and isinstance(tree.body[idx],ast.ImportFrom) and tree.body[idx].module=='__future__':idx+=1
            tree.body.insert(idx,ast.Import(names=[ast.alias(name='v9_meter',asname='_v9_meter')]))
            ast.fix_missing_locations(tree)
            payload=(ast.unparse(tree)+'\n').encode()
            compile(payload,str(dest),'exec')
            dest.write_bytes(payload)
            manifest['operation_site_counts'][relname]=sorted(trans.tags)
        else:
            shutil.copy2(source,dest)
            payload=b
        manifest['modules'][relname]={'original_sha256':sha(b),'instrumented_sha256':sha(payload),
                                       'changed_in_test_copy':b!=payload}
    (out/'V9_TEST_INSTRUMENTATION.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    print(json.dumps({'instrumented':list(manifest['operation_site_counts']),
     'source_modules':len(manifest['modules']),'instrumented_sites':sum(map(len,manifest['operation_site_counts'].values()))}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);args=p.parse_args()
    build(args.source,args.out)
