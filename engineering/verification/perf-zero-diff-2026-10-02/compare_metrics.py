from pathlib import Path
import json

base = Path(r"D:\My-Projects\TradingBot\engineering\verification\perf-zero-diff-2026-10-02\baseline\manifest.json")
cand = Path(r"D:\My-Projects\TradingBot\engineering\verification\perf-zero-diff-2026-10-02\candidate5\manifest.json")
b = json.loads(base.read_text())
c = json.loads(cand.read_text())
print("BASELINE")
for case in b["cases"]:
    if case.get("status") != "PASS":
        print(case.get("name"), case.get("status"), case.get("reason"))
        continue
    timings = (case.get("runs") or [{}])[0].get("timings") or {}
    phases = timings.get("phasesMs") if isinstance(timings, dict) else None
    total = timings.get("bridgeTotalMs") if isinstance(timings, dict) else None
    # rebuilt baseline may not have run timings
    print(case["name"], case["direction"], "wall", round(case.get("medianWallSeconds") or 0, 3),
          "bridgeTotal", total, "digest", case.get("normalizedSha256", "")[:12])
    if not total:
        print("  (no phase timings in rebuilt baseline)")

print("\nCANDIDATE5")
for case in c["cases"]:
    timings = (case.get("runs") or [{}])[0].get("timings") or {}
    phases = timings.get("phasesMs") if isinstance(timings, dict) else {}
    total = timings.get("bridgeTotalMs") if isinstance(timings, dict) else None
    print(case["name"], case["direction"], "wall", round(case.get("medianWallSeconds") or 0, 3),
          "bridgeTotal", total, "digest", case.get("normalizedSha256", "")[:12])
    if phases:
        interesting = {k: v for k, v in phases.items() if v and v > 20}
        print("  >20ms:", interesting)
