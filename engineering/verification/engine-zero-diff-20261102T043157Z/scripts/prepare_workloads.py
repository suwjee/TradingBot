"""Create the audit matrix; original market RAW files remain immutable."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys

EVIDENCE = Path(__file__).resolve().parents[1]
ROOT = EVIDENCE.parents[2]
inputs = json.loads((EVIDENCE / "discovery" / "raw-inputs-before.json").read_bytes())
fixture_root = EVIDENCE / "discovery" / "derived-fixtures"
fixture_root.mkdir(exist_ok=True)
subprocess.run([sys.executable, "-B", str(ROOT / "engine/tests/benchmarks/generate_fixture.py"), str(fixture_root), "1200"], check=True)
smoke = fixture_root / "synthetic-1200.json"
rows = json.loads(smoke.read_bytes())
cases = []
for direction in ("bullish", "bearish"):
    for timeframe in (5, 30):
        cases.append({"id": f"synthetic1200-{timeframe}s-{direction}", "input": str(smoke),
                      "kind": "synthetic", "timeframe": timeframe, "direction": direction,
                      "from_time": rows[0]["time"], "to_time": rows[-1]["time"], "rows": len(rows), "repeats": 5})
for index, item in enumerate(inputs):
    name = ["xau-oct26", "usoil-month", "usoil-oct19", "usoil-oct22", "xau-sep28"][index]
    for direction in ("bullish", "bearish"):
        for timeframe in ([30, 60] if name in {"xau-oct26", "usoil-oct22"} else [30]):
            cases.append({"id": f"{name}-{timeframe}s-{direction}", "input": item["path"],
                          "kind": "real-raw-complete", "timeframe": timeframe, "direction": direction,
                          "from_time": item["first_time"], "to_time": item["last_time"],
                          "rows": item["rows"], "repeats": 5})
    if name == "usoil-oct22":
        for direction in ("bullish", "bearish"):
            cases.append({"id": f"{name}-5s-{direction}-legacy-no-primary", "input": item["path"],
                          "kind": "real-raw-complete", "timeframe": 5, "direction": direction,
                          "from_time": item["first_time"], "to_time": item["last_time"],
                          "rows": item["rows"], "primary": "disabled", "bridge_output": False, "repeats": 5})
        cases.append({"id": "usoil-oct22-30s-both-no-stopall", "input": item["path"],
                      "kind": "real-raw-complete", "timeframe": 30, "direction": "both",
                      "from_time": item["first_time"], "to_time": item["last_time"],
                      "rows": item["rows"], "stopall": False, "repeats": 5})
        cases.append({"id": "usoil-oct22-30s-bearish-narrow-view", "input": item["path"],
                      "kind": "real-raw-complete-narrow-presentation", "timeframe": 30, "direction": "bearish",
                      "from_time": int(item["last_time"]) - 3600, "to_time": item["last_time"],
                      "rows": item["rows"], "repeats": 5})
path = EVIDENCE / "discovery" / "workloads.json"
if path.exists():
    raise RuntimeError("Preserve initial workload selection")
path.write_text(json.dumps(cases, indent=2), encoding="utf-8")
print(f"Prepared {len(cases)} scenarios; original RAW not modified")
