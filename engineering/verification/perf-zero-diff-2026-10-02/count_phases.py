from pathlib import Path
import re, json

def events(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    out = []
    for m in re.finditer(r"QG_PROGRESS:(\{.*?\})", text):
        try:
            out.append(json.loads(m.group(1)))
        except Exception:
            pass
    return out

root = Path(r"D:\My-Projects\TradingBot\engineering\verification\perf-zero-diff-2026-10-02")
for label in ("baseline", "candidate5"):
    for f in sorted((root / label).glob("xauusd-5s-medium.bullish.stderr.log")):
        evs = events(f)
        print("====", label, f.name, "====")
        counts = {}
        sums = {}
        for ev in evs:
            if ev.get("status") != "completed":
                continue
            lab = ev.get("label")
            counts[lab] = counts.get(lab, 0) + 1
            sums[lab] = sums.get(lab, 0) + (ev.get("durationMs") or 0)
        for lab, n in counts.items():
            if n > 1 or (sums.get(lab) or 0) > 30:
                print(f"  n={n:2d} sum={sums[lab]:8.1f}  {lab}")
