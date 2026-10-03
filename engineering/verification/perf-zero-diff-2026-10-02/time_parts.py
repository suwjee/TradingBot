"""Time spent inside OrderAudit helpers on medium bullish."""
from __future__ import annotations

import contextlib
import io
import sys
import time
from pathlib import Path

import orjson

ROOT = Path(r"D:\My-Projects\TradingBot")
ENGINE = ROOT / "engine"
raw = ROOT / "apps/chart/state/data/RAW/FOREXCOM/XAUUSD/RAW FOREXCOM_XAUUSD 5S FROM 2026-09-16 22-35-00 TO 2026-09-17 19-15-35.json"
rows = orjson.loads(raw.read_bytes())
first, last = int(rows[0]["time"]), int(rows[-1]["time"])
sys.path[:0] = [str(ENGINE / "pipeline"), str(ENGINE / "bridge")]

import order_audit_engine as oae

acc = {"carried": 0.0, "post": 0.0, "direct": 0.0, "register": 0.0, "candidates": 0.0}
cnt = {"carried": 0, "post": 0, "direct": 0, "register": 0, "candidates": 0}

def wrap(name, fn):
    def inner(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            acc[name] += time.perf_counter() - t0
            cnt[name] += 1
    return inner

oae.OrderAuditEngineMixin._carried_orders_for_parent = wrap(
    "carried", oae.OrderAuditEngineMixin._carried_orders_for_parent
)
oae.OrderAuditEngineMixin._post_stop_accepted_orders_for_parent = wrap(
    "post", oae.OrderAuditEngineMixin._post_stop_accepted_orders_for_parent
)
oae.OrderAuditEngineMixin._direct_parent_stop_order = wrap(
    "direct", oae.OrderAuditEngineMixin._direct_parent_stop_order
)
oae.OrderAuditEngineMixin._register_order_audit = wrap(
    "register", oae.OrderAuditEngineMixin._register_order_audit
)
oae.OrderAuditEngineMixin.order_candidates = wrap(
    "candidates", oae.OrderAuditEngineMixin.order_candidates
)

bridge = ENGINE / "bridge" / "trading_pipeline.py"
pipeline = ENGINE / "pipeline"
sys.argv = [
    str(bridge),
    "--engine", str(pipeline / "reaction_engine.py"),
    "--blue-engine", str(pipeline / "blue_line_detector.py"),
    "--a-engine", str(pipeline / "a_zone_detector.py"),
    "--s-engine", str(pipeline / "s_zone_detector.py"),
    "--e-engine", str(pipeline / "e_zone_detector.py"),
    "--stopall-engine", str(pipeline / "lifecycle_engine.py"),
    "--data", str(raw),
    "--timeframe", "5",
    "--from-time", str(first),
    "--to-time", str(last),
    "--direction", "bullish",
]
import importlib.util
spec = importlib.util.spec_from_file_location("trading_pipeline_time", bridge)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
t0 = time.perf_counter()
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    spec.loader.exec_module(module)
    code = module.main()
wall = time.perf_counter() - t0
print("exit", code, "wall", round(wall, 3))
for k in acc:
    print(f"{k:12s} {acc[k]:7.3f}s  n={cnt[k]}")
