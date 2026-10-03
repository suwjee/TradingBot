from pathlib import Path
import json
from decimal import Decimal
import orjson

ROOT = Path(r"D:\My-Projects\TradingBot")
raw = orjson.loads((ROOT / "apps/chart/state/data/RAW/BaseLine/RAW FXCM_USOIL 5S FROM 2026-08-21 04-00-00 TO 2026-09-29 11-46-20.json").read_bytes())
payload = json.loads((ROOT / "engineering/verification/phase-b/baseline/utf8/USOIL-bullish.json").read_text(encoding="utf-8"))
timeframe = 30
main = []
for row in raw:
    timestamp = int(row["time"])
    low = Decimal(str(row["low"]))
    high = Decimal(str(row["high"]))
    bucket = timestamp // timeframe * timeframe
    if main and main[-1][0] == bucket:
        prior = main[-1]
        main[-1] = (bucket, min(prior[1], low), max(prior[2], high))
    else:
        main.append((bucket, low, high))

direction = "bullish"
failures = 0
checked = 0
for oi, order in enumerate(payload["directions"]["bullish"]["orderAudit"]):
    for ci, cause in enumerate(order["causes"]):
        if cause.get("kind") != "reset-leg":
            continue
        checked += 1
        current = cause["resetReactionIdentity"]
        source_start = cause["anchorBehaviorSourceIndex"]
        try:
            assert source_start <= current[1]
            prices = [main[i][1] for i in range(source_start, current[1] + 1)]
            boundary = min(prices)
            source_index = source_start + prices.index(boundary)
            assert Decimal(cause["legBoundary"]) == boundary
            assert cause["legBoundarySourceIndex"] == source_index
            assert cause["legBoundarySourceTime"] == main[source_index][0]
        except Exception as exc:
            failures += 1
            if failures <= 5:
                print("FAIL", oi, ci, exc)
                print("  anchor", source_start, "reset", current)
                print("  recorded", cause["legBoundary"], cause["legBoundarySourceIndex"], cause["legBoundarySourceTime"])
                prices = [main[i][1] for i in range(source_start, current[1] + 1)] if source_start <= current[1] else []
                if prices:
                    boundary = min(prices)
                    source_index = source_start + prices.index(boundary)
                    print("  recon", boundary, source_index, main[source_index][0])
print("checked", checked, "failures", failures)
