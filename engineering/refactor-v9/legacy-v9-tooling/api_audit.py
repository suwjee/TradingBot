#!/usr/bin/env python3
"""Static public API, CLI literals, function/class signatures of pinned original vs V8.1."""
import ast,json,subprocess,sys,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1];OUT=W/'output'
R={'pinned_original':W/'golden/github_engine_commit_01d54ecf/engine','v81':W/'v81/engine'}
modules=[str(p.relative_to(R['v81'])) for p in R['v81'].rglob('*.py')]
def snapshot(root):
 result={};help=[]
 for rel in modules:
  p=root/rel;t=ast.parse(p.read_bytes());symbols={};cli=[]
  for node in t.body:
   if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and not node.name.startswith('_'):
    symbols[node.name]={'kind':'function','signature_ast':ast.dump(node.args,include_attributes=False), 'returns':ast.dump(node.returns,include_attributes=False) if node.returns else None}
   if isinstance(node,ast.ClassDef) and not node.name.startswith('_'):
    symbols[node.name]={'kind':'class','bases':[ast.unparse(b) for b in node.bases]}
    for method in node.body:
     if isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)) and not method.name.startswith('_'):
      symbols[node.name+'.'+method.name]={'kind':'method','signature_ast':ast.dump(method.args,include_attributes=False)}
   for x in ast.walk(node):
    if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=='add_argument':
     args=[s.value for s in x.args if isinstance(s,ast.Constant) and isinstance(s.value,str)]
     if args:cli.append((args,x.lineno))
  result[rel]={'public_symbols':symbols,'add_argument_options':cli}
 return result
snap={k:snapshot(v) for k,v in R.items()}
compare=[]
for rel in modules:
 for key in ('public_symbols','add_argument_options'):
  left=snap['pinned_original'][rel][key];right=snap['v81'][rel][key]
  if key=='add_argument_options':left=[x[0] for x in left];right=[x[0] for x in right]
  if left!=right:compare.append({'module':rel,'kind':key,'baseline_only':str(set(left)-set(right)) if isinstance(left,dict) else '',
                                'candidate_only':str(set(right)-set(left)) if isinstance(right,dict) else ''})
compile_errors=[]
for label,root in R.items():
 for rel in modules:
  try:compile((root/rel).read_bytes(),str(root/rel),'exec')
  except Exception as e:compile_errors.append({'version':label,'file':rel,'error':repr(e)})
report={'static_api_match':len(compare)==0,'differences':compare,'compile_errors':compile_errors,'source_snapshots':snap,
        'note':'AST public symbol signature + argparse literal audit. Dynamic monkeypatched signatures and all exception behaviour are outside this proof.'}
(OUT/'V9_PUBLIC_CONTRACT_AUDIT.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'static_api_match':report['static_api_match'],'differences':compare,'compile_errors':compile_errors,'modules':len(modules)}))
