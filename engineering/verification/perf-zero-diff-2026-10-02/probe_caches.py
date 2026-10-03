"""One-shot cache hit-rate probe on a medium workload."""
from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

import orjson

ROOT = Path(r"D:\My-Projects\TradingBot")
ENGINE = ROOT / "engine"
raw = ROOT / "apps/chart/state/data/RAW/FOREXCOM/XAUUSD/RAW FOREXCOM_XAUUSD 5S FROM 2026-09-16 22-35-00 TO 2026-09-17 19-15-35.json"
rows = orjson.loads(raw.read_bytes())
first, last = int(rows[0]["time"]), int(rows[-1]["time"])

sys.path[:0] = [str(ENGINE / "pipeline"), str(ENGINE / "bridge")]

# Patch caches to count hits
import order_audit_engine as oae

stats = {"carried_hit": 0, "carried_miss": 0, "post_hit": 0, "post_miss": 0, "direct_hit": 0, "direct_miss": 0}

orig_carried = oae.OrderAuditEngineMixin._carried_orders_for_parent
orig_post = oae.OrderAuditEngineMixin._post_stop_accepted_orders_for_parent
orig_direct = oae.OrderAuditEngineMixin._direct_parent_stop_order

def carried(self, parent, parent_stop):
    key = (getattr(parent, "decision_event_time", None), parent_stop)
    if key[0] is not None and key in self._carried_orders_cache:
        stats["carried_hit"] += 1
    else:
        stats["carried_miss"] += 1
    return orig_carried(self, parent, parent_stop)

def post(self, parent, parent_stop):
    key = (parent_stop, len(self._order_audit_confirmation_index))
    if key in self._post_stop_orders_cache:
        stats["post_hit"] += 1
    else:
        stats["post_miss"] += 1
    return orig_post(self, parent, parent_stop)

def direct(self, start, continuous_deadline, allow_bounded_continue):
    key = (start, continuous_deadline, allow_bounded_continue)
    if key in self._direct_parent_stop_cache:
        stats["direct_hit"] += 1
    else:
        stats["direct_miss"] += 1
    return orig_direct(self, start, continuous_deadline, allow_bounded_continue)

oae.OrderAuditEngineMixin._carried_orders_for_parent = carried
oae.OrderAuditEngineMixin._post_stop_accepted_orders_for_parent = post
oae.OrderAuditEngineMixin._direct_parent_stop_order = direct

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
spec = importlib.util.spec_from_file_location("trading_pipeline_probe", bridge)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
    spec.loader.exec_module(module)
    code = module.main()
print("exit", code)
print(stats)
