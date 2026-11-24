#!/usr/bin/env python3
"""AST source inventory: potential mutable-state operations lacking V9 tracing.

Conservative syntax classification (not a proof of effects or full event coverage).
Every result includes exact source position and the plain syntax-derived reason.
"""
from __future__ import annotations
import argparse,ast,collections,hashlib,json
from pathlib import Path
from semantic_trace_v3 import TRACED

MUTATOR_NAMES={'append','extend','insert','remove','pop','clear','update','setdefault','discard','add','sort','reverse'}
STATE_TERMS={'order','audit','parent','source','accepted','reset','stop','reaction','candidate','lifecycle','state','s_zone','e_zone','ownership','blue','trend','cache','reconciliation'}

class FunctionAudit(ast.NodeVisitor):
 def __init__(self,file,source):
  self.file=file;self.source=source;self.functions=[];self.scope=[];self.current=None
 def visit_ClassDef(self,node):
  self.scope.append(node.name)
  for x in node.body:self.visit(x)
  self.scope.pop()
 def visit_FunctionDef(self,node):
  qual='.'.join(self.scope+[node.name]);markers=[]
  for child in ast.walk(node):
   if child is node or isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):continue
   if isinstance(child,(ast.Assign,ast.AugAssign,ast.AnnAssign)):
    targets=getattr(child,'targets',None) or [child.target]
    for target in targets:
     if isinstance(target,ast.Attribute):
      key=ast.unparse(target)
      if any(w in key.lower() for w in STATE_TERMS):markers.append({'line':child.lineno,'operation':'state_attribute_assignment','target':key})
     elif isinstance(target,ast.Subscript):
      key=ast.unparse(target)
      if any(w in key.lower() for w in STATE_TERMS):markers.append({'line':child.lineno,'operation':'state_subscript_assignment','target':key})
   if isinstance(child,ast.Call) and isinstance(child.func,ast.Attribute) and child.func.attr in MUTATOR_NAMES:
    key=ast.unparse(child.func.value)
    if any(w in key.lower() for w in STATE_TERMS):markers.append({'line':child.lineno,'operation':'possible_collection_mutation','target':key+'.'+child.func.attr})
  module=self.file.stem
  inspected=node.name in TRACED.get(module,set())
  self.functions.append({'file':str(self.file),'line':node.lineno,'function':qual,'traced_selected_function_name':inspected,'possible_mutation_points':markers})
  for child in node.body:
   if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):self.visit(child)
 visit_AsyncFunctionDef=visit_FunctionDef

def main(root,out):
 root=Path(root);files=[];all_methods=[]
 for path in sorted((root/'pipeline').glob('*.py'))+sorted((root/'bridge').glob('*.py')):
  source=path.read_bytes();a=FunctionAudit(path.relative_to(root),source);a.visit(ast.parse(source,filename=str(path)));all_methods+=a.functions
  files.append({'path':str(path.relative_to(root)),'sha256':hashlib.sha256(source).hexdigest(),'function_count':len(a.functions)})
 risky=[x for x in all_methods if x['possible_mutation_points']]
 untraced=[x for x in risky if not x['traced_selected_function_name']]
 summary={'status':'AUDIT_ONLY_NOT_EXECUTION_COVERAGE','source_root':str(root),'files':files,'total_functions':len(all_methods),
          'functions_with_possible_state_mutations':len(risky),'possible_state_mutation_functions_without_selected_trace':len(untraced),
          'possible_state_mutation_points_without_selected_trace':sum(len(x['possible_mutation_points']) for x in untraced),
          'untraced_mutators':untraced,
          'note':'Source AST conservative name match; a traced outer function can call untraced inner mutators. Does not prove event coverage or safety.'}
 Path(out).write_text(json.dumps(summary,indent=2,ensure_ascii=False))
 print(json.dumps({k:v for k,v in summary.items() if k not in ('files','untraced_mutators')},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--engine',required=True);p.add_argument('--out',required=True);x=p.parse_args();main(x.engine,x.out)