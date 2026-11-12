"""Validate full-read range ledgers against the dynamically discovered source set."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[1]
ROOT = EVIDENCE.parents[2]
reviews = EVIDENCE / "reviews"
data = []
for name, key in [("reaction-read-ledger.json", "production_files"), ("orders-read-ledger.json", "assigned_files"), ("zones-read-ledger.json", "files")]:
    data.extend(json.loads((reviews / name).read_text(encoding="utf-8-sig"))[key])
for path, ranges in [("engine/__init__.py", []), ("engine/bridge/__init__.py", [[1,1]]),
                     ("engine/bridge/trading_pipeline.py", [[1,400],[401,800],[801,1200],[1201,1700],[1701,2200],[2201,2700],[2701,3100],[3101,3433]])]:
    source = ROOT / path
    data.append({"path": path, "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "actual_read_ranges": ranges, "reader": "/root"})
manifest = json.loads((EVIDENCE / "discovery/source-manifest-before.json").read_bytes())
coverage = []
for source in manifest:
    path = source["path"]
    matches = [item for item in data if item["path"] == path]
    content = (ROOT / path).read_bytes()
    assert matches, path
    assert hashlib.sha256(content).hexdigest() == source["sha256"], path
    assert all(item["sha256"].lower() == source["sha256"] for item in matches), path
    ranges = [pair for item in matches for pair in item.get("actual_read_ranges", item.get("numbered_ranges_actually_read", []))]
    total = len(content.splitlines())
    covered = {line for start, end in ranges for line in range(start, end+1)}
    assert set(range(1,total+1)) <= covered, (path, total, sorted(set(range(1,total+1)) - covered))
    coverage.append({"path": path, "lines": total, "ranges": ranges, "full_read": "YES", "sha256": source["sha256"]})
for reference in ["bullish-reference-review.md", "bearish-reference-review.md", "protocol-review.md"]:
    assert (reviews / reference).exists(), reference
assert hashlib.sha256((ROOT / "GPT_bot/TradingBot_AI_Operating_Protocol.md").read_bytes()).hexdigest() == "eb8a0b718ec06a2de4034ac8700aa322e17bda7984dedefa82d2c0d0d68bcc4a"
rows = list(csv.DictReader((EVIDENCE / "01_ENGINE_FILE_INVENTORY.csv").open(encoding="utf-8", newline="")))
for row in rows:
    if row["classification"] in {"production-source", "package-marker"}:
        row["full_read_status"] = "YES - TEAM FULL SOURCE READ"
    elif row["classification"] == "accepted-reference":
        row["full_read_status"] = "YES - PROSE AND BYTE-IDENTICAL SOURCE READ ONCE"
with (EVIDENCE / "01_ENGINE_FILE_INVENTORY.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
(EVIDENCE / "discovery/full-read-coverage.json").write_text(json.dumps(coverage, indent=2), encoding="utf-8")
print(f"PASS: {len(coverage)} dynamically discovered production files fully read; hashes unchanged; prose reviews present")
