from pathlib import Path
import json
m = json.loads(Path(r"D:\My-Projects\TradingBot\engineering\verification\perf-zero-diff-2026-10-02\candidate6\manifest.json").read_text())
for c in m["cases"]:
    print(
        c.get("name"),
        c.get("direction"),
        "wall",
        round(c.get("medianWallSeconds") or 0, 3),
        "cpu",
        round(c.get("medianCpuSeconds") or 0, 3),
        c.get("normalizedSha256", "")[:12],
    )
