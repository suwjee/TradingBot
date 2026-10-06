"""Persist exact symbol coverage for manually read S/E source files."""
import ast
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
AUDIT=OUT.parent
records=[]
for filename in ("s_zone_detector.py","e_zone_detector.py"):
    path=AUDIT/"package/pipeline"/filename
    body=path.read_bytes()
    tree=ast.parse(body,filename=str(path))
    definitions=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            definitions.append({"name":node.name,"kind":type(node).__name__,"start":node.lineno,"end":node.end_lineno,
                                "study":"READ_FULL","verification":"source review; see rule matrix and bounded probes"})
    records.append({"path":str(path),"sha256":hashlib.sha256(body).hexdigest(),"lines":len(body.splitlines()),"study":"READ_FULL",
                    "definitions":sorted(definitions,key=lambda r:(r["start"],r["end"]))})
bull=(AUDIT/"bullish-rules.md").read_text(encoding="utf-8").splitlines()
bear=(AUDIT/"bearish-rules.md").read_text(encoding="utf-8").splitlines()
assert len(bull)==len(bear)==726
assert bull[329:]==bear[329:]
docs=[{"path":str(AUDIT/"bullish-rules.md"),"lines":726,"study":"READ_FULL"},
      {"path":str(AUDIT/"bearish-rules.md"),"lines":726,"study":"READ_FULL 1-329; VERIFIED_DUPLICATE 330-726 against read Bullish prose",
       "duplicate_span_equal":True}]
output={"owned_modules":records,"references":docs,
        "dependency_read_spans":[{"path":"package/pipeline/order_audit_engine.py","spans":[[1,1613],[1818,1947]],"study":"READ_FULL within spans; 1614-1817 outside S/E direct call closure delegated to root"},
                                 {"path":"package/pipeline/reaction_engine.py","spans":[[974,1202]],"study":"READ_FULL MarketChronology; whole Reaction owner delegated"},
                                 {"path":"package/pipeline/direction_policy.py","spans":[[1,70]],"study":"READ_FULL"},
                                 {"path":"package/pipeline/core_utils.py","spans":[[1,26]],"study":"READ_FULL"},
                                 {"path":"package/bridge/trading_pipeline.py","spans":[[123,210],[1865,2349]],"study":"READ_FULL within spans; bridge owner delegated"},
                                 {"path":"package/pipeline/lifecycle_engine.py","spans":[[613,815]],"study":"READ_FULL within span; broader lifecycle owner delegated"},
                                 {"path":"engine/tests/unit/test_order_audit_lifecycle_contracts.py","study":"READ_FULL; executed 37 passed, 2 xfailed"}]}
(OUT/"coverage.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
table=["# S/E complete source symbol reading coverage", "", "Every definition below belongs to a source file read completely. Reading status does not assert universal behavioral verification.", ""]
for record in records:
    table.extend([f"## {Path(record['path']).name}", "", "| Definition | Kind | Exact source lines | Study |", "|---|---|---:|---|"])
    table.extend(f"| `{d['name']}` | {d['kind']} | {d['start']}-{d['end']} | READ_FULL |" for d in record["definitions"])
    table.append("")
(OUT/"FUNCTION-COVERAGE.md").write_text("\n".join(table),encoding="utf-8")
print(json.dumps({"modules":len(records),"definitions":sum(len(r["definitions"]) for r in records),"references":docs}))
