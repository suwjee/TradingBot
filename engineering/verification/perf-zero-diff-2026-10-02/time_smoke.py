from pathlib import Path
import subprocess, sys, time, json, os

ROOT = Path(r"D:\My-Projects\TradingBot")
ENGINE = ROOT / "engine"
raw = ROOT / "apps/chart/state/data/RAW/FOREXCOM/XAUUSD/RAW FOREXCOM_XAUUSD 30S FROM 2026-09-28 20-44-00 TO 2026-09-29 11-45-30.json"
import orjson
rows = orjson.loads(raw.read_bytes())
first, last = int(rows[0]["time"]), int(rows[-1]["time"])
cmd = [
    sys.executable, "-B", str(ENGINE / "bridge/trading_pipeline.py"),
    "--engine", str(ENGINE / "pipeline/reaction_engine.py"),
    "--blue-engine", str(ENGINE / "pipeline/blue_line_detector.py"),
    "--a-engine", str(ENGINE / "pipeline/a_zone_detector.py"),
    "--s-engine", str(ENGINE / "pipeline/s_zone_detector.py"),
    "--e-engine", str(ENGINE / "pipeline/e_zone_detector.py"),
    "--lifecycle-engine", str(ENGINE / "pipeline/lifecycle_engine.py"),
    "--data", str(raw), "--timeframe", "30",
    "--from-time", str(first), "--to-time", str(last),
    "--direction", "bullish",
]
walls = []
for i in range(5):
    t0 = time.perf_counter()
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=ROOT)
    dt = time.perf_counter() - t0
    walls.append(dt)
    print(f"run{i} {dt:.4f}s exit={p.returncode}", flush=True)
print("median", sorted(walls)[len(walls)//2])
