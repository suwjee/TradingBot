from __future__ import annotations
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
count = int(sys.argv[2])
rows = []
price = 100000
seed = 94837
for i in range(count):
    seed = (1664525 * seed + 1013904223) & 0xffffffff
    move = ((seed >> 16) % 9) - 4
    phase = i % 192
    drift = 3 if phase < 64 else (-3 if phase < 128 else 0)
    opening = price
    closing = max(1000, opening + move + drift)
    high = max(opening, closing) + 1 + (seed % 4)
    low = min(opening, closing) - 1 - ((seed >> 4) % 4)
    rows.append({"time": 1789430400 + i * 5, "open": f"{opening / 100:.2f}", "high": f"{high / 100:.2f}", "low": f"{low / 100:.2f}", "close": f"{closing / 100:.2f}"})
    price = closing
(root / f"synthetic-{count}.json").write_text(json.dumps(rows, separators=(",", ":")), encoding="utf-8")
print(root / f"synthetic-{count}.json")
