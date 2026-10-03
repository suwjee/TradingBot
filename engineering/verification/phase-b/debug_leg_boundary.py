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

print("main len", len(main), "first", main[0], "last", main[-1])
direction = "bullish"
for order in payload["directions"]["bullish"]["orderAudit"]:
    for cause in order["causes"]:
        if cause.get("kind") != "reset-leg":
            continue
        current = cause["resetReactionIdentity"]
        source_start = cause["anchorBehaviorSourceIndex"]
        print("\ncause sample:")
        print(" anchorSource", source_start, "resetIdentity", current)
        print(" recorded legBoundary", cause["legBoundary"], "src", cause["legBoundarySourceIndex"], cause["legBoundarySourceTime"])
        print(" main[source_start]", main[source_start] if source_start < len(main) else "OOR")
        print(" main[current1]", main[current[1]] if current[1] < len(main) else "OOR")
        if source_start < len(main) and current[1] < len(main):
            prices = [main[i][1] for i in range(source_start, current[1] + 1)]
            boundary = min(prices)
            source_index = source_start + prices.index(boundary)
            print(" reconstructed", boundary, source_index, main[source_index][0])
            print(" match", Decimal(cause["legBoundary"]) == boundary)
        break
    else:
        continue
    break
