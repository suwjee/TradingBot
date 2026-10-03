import time, sys
from pathlib import Path
ENGINE = Path(r"D:\My-Projects\TradingBot\engine")
sys.path[:0] = [str(ENGINE / "pipeline"), str(ENGINE / "bridge")]
t0 = time.perf_counter()
import orjson
t1 = time.perf_counter()
import importlib.util
t2 = time.perf_counter()
for name, rel in [
    ("reaction_engine", "pipeline/reaction_engine.py"),
    ("blue_line_detector", "pipeline/blue_line_detector.py"),
    ("a_zone_detector", "pipeline/a_zone_detector.py"),
    ("s_zone_detector", "pipeline/s_zone_detector.py"),
    ("e_zone_detector", "pipeline/e_zone_detector.py"),
    ("lifecycle_engine", "pipeline/lifecycle_engine.py"),
    ("order_audit_engine", "pipeline/order_audit_engine.py"),
    ("core_utils", "pipeline/core_utils.py"),
    ("direction_policy", "pipeline/direction_policy.py"),
]:
    path = ENGINE / rel
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
t3 = time.perf_counter()
print(f"orjson {t1-t0:.3f} setup {t2-t1:.3f} load_modules {t3-t2:.3f} total {t3-t0:.3f}")
