"""Capture the source and frozen-input identities used by this execution."""
import ast
from datetime import datetime
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
SCRATCH = ROOT / "apps/chart/state/tmp/engine-refactor-20261117"


def sources(engine):
    files = [engine / "__init__.py", *sorted((engine / "bridge").rglob("*.py")), *sorted((engine / "pipeline").rglob("*.py"))]
    result = {}
    for path in files:
        if "__pycache__" in path.parts:
            continue
        raw = path.read_bytes()
        tree = ast.parse(raw)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imports.append(node.module)
            elif isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
        result[path.relative_to(engine).as_posix()] = dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
            lines=len(raw.splitlines()), imports=sorted(set(x for x in imports if x)))
    return result


def main():
    manifests = {variant: sources(SCRATCH / variant / "engine") for variant in ("original", "removed", "optimized")}
    current = sources(ROOT / "engine")
    assert current == manifests["optimized"], "Measured snapshot differs from final live production Source"
    for name in manifests["removed"]:
        if name not in ("bridge/trading_pipeline.py", "bridge/live_pipeline.py"):
            assert manifests["removed"][name] == manifests["original"][name], name
    assert set(manifests["original"]) - set(manifests["removed"]) == {"pipeline/bullish_setup_engine.py"}
    inputs = []
    for path in sorted((SCRATCH / "inputs").glob("*-full.json")):
        raw = path.read_bytes()
        rows = json.loads(raw)
        inputs.append(dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
            rows=len(rows), start_epoch=rows[0]["time"], end_epoch=rows[-1]["time"],
            finest_positive_step_seconds=min(b["time"] - a["time"] for a, b in zip(rows, rows[1:]) if b["time"] > a["time"])))
    result = dict(captured_at=datetime.now(ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds"),
        sources=manifests, inputs=inputs, current_matches_measured_snapshot=True,
        archive_policy="engine/engine.zip retained unchanged as historical package; not loaded or used as authority",
        authority_limitation="Connected Vault capture is dated 2026-10-27 and scoped; current exact References and live Source reviewed. External Vault snapshots were not rebuilt.")
    (EVIDENCE / "source-input-manifest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("PASS source snapshots, isolated feature-removal baseline, and frozen input identities")


if __name__ == "__main__":
    main()
