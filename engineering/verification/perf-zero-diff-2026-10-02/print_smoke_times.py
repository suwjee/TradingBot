from pathlib import Path
import json
m = json.loads(Path(r"D:\My-Projects\TradingBot\engineering\verification\perf-zero-diff-2026-10-02\candidate5\manifest.json").read_text())
for c in m["cases"]:
    if c.get("name") != "xauusd-30s-smoke":
        continue
    print(c["name"], c["direction"], round(c["medianWallSeconds"], 3), c.get("counts"))
    print("  phases", c["runs"][0].get("timings"))
