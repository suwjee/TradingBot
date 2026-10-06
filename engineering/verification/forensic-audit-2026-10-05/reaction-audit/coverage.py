"""Persist exact Source coverage and independent reference-tail equality proof."""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
names=("reaction_engine.py","blue_line_detector.py","a_zone_detector.py","direction_policy.py","core_utils.py")
files=[]
for name in names:
    p=ROOT/"package"/"pipeline"/name
    blob=p.read_bytes();src=blob.decode("utf-8-sig");tree=ast.parse(src)
    symbols=[]
    def walk(node,prefix=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
                qual=prefix+child.name
                symbols.append({"name":qual,"kind":type(child).__name__,"start":child.lineno,"end":child.end_lineno,"status":"READ_FULL"})
                walk(child,qual+".")
            else:walk(child,prefix)
    walk(tree)
    files.append({"path":str(p),"sha256":hashlib.sha256(blob).hexdigest(),"lines":len(src.splitlines()),
                  "status":"READ_FULL","symbols":symbols})
bull=(ROOT/"bullish-rules.md").read_text(encoding="utf-8-sig").splitlines()
bear=(ROOT/"bearish-rules.md").read_text(encoding="utf-8-sig").splitlines()
assert len(bull)==len(bear)==726
diff=[{"line":i+1,"bullish":a,"bearish":b} for i,(a,b) in enumerate(zip(bull,bear)) if a!=b]
record={"source_files":files,"total_source_lines":sum(f["lines"] for f in files),
        "references":{"bullish":"READ_FULL 1-726","bearish":"READ_FULL 1-190; all differences READ_FULL; remaining lines VERIFIED_DUPLICATE at same line number",
                      "line_counts":726,"differing_lines":diff,"identical_tail_lines":sum(a==b for a,b in zip(bull[190:],bear[190:]))},
        "supporting_reads":{"package/bridge/trading_pipeline.py":[[8,210],[1669,1782]],
                            "engine/tests/unit/test_hpzr2_regression.py":"READ_FULL",
                            "engine/tests/unit/test_order_audit_lifecycle_contracts.py":[[1,108]]},
        "limitations":["No full-engine counterfactual execution", "No production accepted-Order consequence proved for RX-H01", "Root owns independent refutation and final classification"]}
repo=ROOT.parents[2]
for f in files:
    live=repo/"engine"/"pipeline"/Path(f["path"]).name
    assert hashlib.sha256(live.read_bytes()).hexdigest()==f["sha256"],str(live)
record["assigned_live_source_matches_frozen_package"]="PASS 5 of 5"
raw_evidence=Path(__file__).with_name("raw-evidence.json")
if raw_evidence.exists():
    raws=json.loads(raw_evidence.read_text(encoding="utf-8"))
    for case in raws:
        p=repo/Path(case["raw"])
        assert hashlib.sha256(p.read_bytes()).hexdigest()==case["sha256"],str(p)
    record["audited_raw_hashes_unchanged"]=f"PASS {len(raws)} of {len(raws)}"
out=Path(__file__).with_name("coverage.json");out.write_text(json.dumps(record,indent=2),encoding="utf-8")
print(json.dumps({"coverage":str(out),"source_files":len(files),"source_lines":record["total_source_lines"],
                  "symbols":sum(len(f["symbols"]) for f in files),"reference_differences":len(diff),
                  "verified_identical_bearish_tail_lines":record["references"]["identical_tail_lines"]}))
