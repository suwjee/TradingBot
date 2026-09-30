from __future__ import annotations
import argparse
import contextlib
import ctypes
import hashlib
import importlib.util
import io
import json
import sys
import time
import tracemalloc
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("engine_root", type=Path)
parser.add_argument("data", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--direction", default="both")
parser.add_argument("--timeframe", type=int, default=30)
parser.add_argument("--bridge-output", action="store_true")
parser.add_argument("--trace", action="store_true")
args = parser.parse_args()
bridge = args.engine_root / "engine" / "bridge" / "trading_pipeline.py"
pipeline = args.engine_root / "engine" / "pipeline"
argv = [
    str(bridge),
    "--engine", str(pipeline / "reaction_engine.py"),
    "--blue-engine", str(pipeline / "blue_line_detector.py"),
    "--a-engine", str(pipeline / "a_zone_detector.py"),
    "--s-engine", str(pipeline / "s_zone_detector.py"),
    "--e-engine", str(pipeline / "e_zone_detector.py"),
    "--stopall-engine", str(pipeline / "lifecycle_engine.py"),
    "--data", str(args.data),
    "--timeframe", str(args.timeframe),
    "--from-time", "1789430400",
    "--to-time", str(1789430400 + (len(json.loads(args.data.read_bytes())) - 1) * 5),
    "--direction", args.direction,
]
if args.bridge_output:
    argv.append("--bridge-output")
sys.argv = argv
if args.trace:
    tracemalloc.start(10)
started = time.perf_counter()
cpu_started = time.process_time()
spec = importlib.util.spec_from_file_location("trading_pipeline_benchmark", bridge)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
with contextlib.redirect_stdout(io.StringIO()) as captured_stdout, contextlib.redirect_stderr(io.StringIO()) as captured_stderr:
    spec.loader.exec_module(module)
    code = module.main()
wall = time.perf_counter() - started
cpu = time.process_time() - cpu_started
if code != 0:
    raise RuntimeError(f"bridge exit {code}")
raw = captured_stdout.getvalue().strip()
payload = json.loads(raw)
args.output.write_text(raw + "\n", encoding="utf-8")
normalized = dict(payload)
normalized.pop("timings", None)
exact = json.dumps(normalized, separators=(",", ":"), ensure_ascii=True)
args.output.with_suffix(".normalized.json").write_text(exact + "\n", encoding="utf-8")
summary = {
    "wall_seconds": wall,
    "cpu_seconds": cpu,
    "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(),
    "normalized_sha256": hashlib.sha256(exact.encode()).hexdigest(),
    "output_bytes": len(raw.encode()),
    "timings": payload.get("timings"),
}
if args.trace:
    current, peak = tracemalloc.get_traced_memory()
    summary["python_alloc_current_bytes"] = current
    summary["python_alloc_peak_bytes"] = peak
    summary["allocation_top"] = [str(stat) for stat in tracemalloc.take_snapshot().statistics("lineno")[:15]]
if sys.platform == "win32":
    from ctypes import wintypes
    class ProcessMemoryCounters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
    ctypes.windll.kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb)
    summary["peak_working_set_bytes"] = counters.PeakWorkingSetSize
args.output.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))


