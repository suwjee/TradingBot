from pathlib import Path
import json

p = Path(r"D:\My-Projects\TradingBot\engineering\verification\perf-zero-diff-2026-10-02\profiles")
for f in sorted(p.glob("*.summary.json")):
    s = json.loads(f.read_text(encoding="utf-8"))
    print("====", f.name, "wall", round(s["wallSeconds"], 2), "====")
    print("-- top self --")
    for r in s["topSelf"][:18]:
        print(
            f"{r['tottime']:8.3f} {r['cumtime']:8.3f} {r['calls']:8d}  {r['func']}  {r['file']}:{r['line']}"
        )
    print("-- top cum --")
    for r in s["topCumulative"][:12]:
        print(
            f"{r['cumtime']:8.3f} {r['tottime']:8.3f} {r['calls']:8d}  {r['func']}  {r['file']}:{r['line']}"
        )
    print()
