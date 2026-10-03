from pathlib import Path
import json

for label in ("baseline", "final", "final-usoil"):
    p = Path(r"D:\My-Projects\TradingBot\engineering\verification\perf-zero-diff-2026-10-02") / label / "manifest.json"
    if not p.exists():
        continue
    m = json.loads(p.read_text())
    print("====", label, m.get("status"), "====")
    for c in m.get("cases", []):
        if c.get("status") != "PASS":
            print(" ", c.get("name"), c.get("direction"), c.get("status"), c.get("reason"))
            continue
        runs = c.get("runs") or []
        cpus = [r.get("cpuSeconds") for r in runs if r.get("cpuSeconds") is not None]
        peaks = [r.get("peakWorkingSetBytes") for r in runs if r.get("peakWorkingSetBytes")]
        print(
            f"  {c.get('name'):22s} {c.get('direction'):7s} "
            f"wall={c.get('medianWallSeconds'):7.3f} "
            f"cpu={c.get('medianCpuSeconds') or 0:7.3f} "
            f"peakMB={((max(peaks) if peaks else 0)/1048576):6.1f} "
            f"digest={c.get('normalizedSha256','')[:12]}"
        )
