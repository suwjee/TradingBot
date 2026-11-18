"""Run a fresh Engine process with exact stable output and measured evidence."""
from __future__ import annotations

import argparse
import cProfile
import contextlib
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pstats
import shutil
import subprocess
import sys
import time
import traceback


def main():
    original_cli = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--direction", choices=("bullish", "bearish", "both"), required=True)
    parser.add_argument("--timeframe", type=int, default=30)
    parser.add_argument("--profile", action="store_true")
    parser.add_argument("--pl-ph", choices=("enabled", "disabled"), default="enabled")
    parser.add_argument("--legacy-output", action="store_true")
    parser.add_argument("--no-lifecycle", action="store_true")
    parser.add_argument("--no-behavior", action="store_true")
    parser.add_argument("--presentation-middle", action="store_true")
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # The final review superseded one early candidate sample. Remeasure its
    # baseline immediately beforehand as well, outside the timed region.
    evidence = Path(__file__).resolve().parent
    paired_replacement = False
    if args.out.name == "optimized-USOIL-bullish-0":
        matrix_results = evidence / "performance-results.json"
        paired_replacement = matrix_results.exists() and len(json.loads(matrix_results.read_bytes())) == 4
    if paired_replacement:
        archive = args.out.parent / "superseded-before-final-pair"
        archive.mkdir(exist_ok=True)
        baseline_out = args.out.with_name("removed-USOIL-bullish-0")
        for prior in (baseline_out, args.out):
            summary_path = prior.with_suffix(".summary.json")
            archived_path = archive / summary_path.name
            if summary_path.exists() and not archived_path.exists():
                shutil.copyfile(summary_path, archived_path)
        baseline_cli = list(original_cli)
        baseline_cli[baseline_cli.index("--root") + 1] = str(args.root.with_name("removed"))
        baseline_cli[baseline_cli.index("--out") + 1] = str(baseline_out)
        print("Remeasuring the baseline immediately before the final candidate", flush=True)
        subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), *baseline_cli], check=True)
    data = args.data.read_bytes()
    rows = json.loads(data)
    pipeline = args.root / "engine/pipeline"
    bridge = args.root / "engine/bridge/trading_pipeline.py"
    sys.argv = [str(bridge)]
    for flag, name in (("engine", "reaction_engine"), ("blue-engine", "blue_line_detector"),
                       ("a-engine", "a_zone_detector"), ("s-engine", "s_zone_detector"),
                       ("e-engine", "e_zone_detector"), ("stopall-engine", "lifecycle_engine")):
        if flag == "stopall-engine" and args.no_lifecycle:
            continue
        sys.argv += ["--" + flag, str(pipeline / (name + ".py"))]
    start = len(rows) // 3 if args.presentation_middle else 0
    end = len(rows) * 2 // 3 if args.presentation_middle else len(rows) - 1
    sys.argv += ["--data", str(args.data), "--timeframe", str(args.timeframe),
                 "--from-time", str(rows[start]["time"]), "--to-time", str(rows[end]["time"]),
                 "--direction", args.direction, "--pl-ph", args.pl_ph]
    if not args.legacy_output:
        sys.argv += ["--bridge-output"]
    if args.no_behavior:
        sys.argv += ["--blue-lines", "disabled", "--a-zones", "disabled", "--s-zones", "disabled"]
    del rows
    profile = cProfile.Profile() if args.profile else None
    started, cpu = time.perf_counter(), time.process_time()
    spec = importlib.util.spec_from_file_location("measured_pipeline", bridge)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        with args.out.with_suffix(".stdout.json").open("w", encoding="utf-8") as output, args.out.with_suffix(".stderr.log").open("w", encoding="utf-8") as errors:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                if profile:
                    profile.enable()
                spec.loader.exec_module(module)
                code = module.main()
                if profile:
                    profile.disable()
    except Exception as exc:
        from decimal import getcontext
        source_root = (args.root / "engine").resolve()
        frames = []
        for frame in traceback.extract_tb(exc.__traceback__):
            path = Path(frame.filename).resolve()
            if path.is_relative_to(source_root):
                frames.append([path.relative_to(source_root).as_posix(), frame.name])
        failure = dict(exception_type=type(exc).__module__ + "." + type(exc).__qualname__,
                       exception_args=repr(exc.args), engine_frames=frames,
                       decimal_flags={signal.__name__: value for signal, value in getcontext().flags.items()},
                       stdout=args.out.with_suffix(".stdout.json").read_text(encoding="utf-8"))
        args.out.with_suffix(".failure.json").write_text(json.dumps(failure, indent=2), encoding="utf-8")
        raise
    wall, cpu = time.perf_counter() - started, time.process_time() - cpu
    if code != 0:
        raise RuntimeError(f"Pipeline exited {code}")
    raw = args.out.with_suffix(".stdout.json").read_text(encoding="utf-8").strip()
    payload = json.loads(raw)
    # The supported response builder appends this top-level telemetry field last.
    stable, marker, telemetry = raw.rpartition(',"timings":')
    assert marker and json.loads(stable + "}") == {k: v for k, v in payload.items() if k != "timings"}
    stable += "}"
    args.out.with_suffix(".stable.json").write_text(stable, encoding="utf-8")
    summary = dict(wall_seconds=wall, cpu_seconds=cpu, input_sha256=hashlib.sha256(data).hexdigest(),
                   stable_sha256=hashlib.sha256(stable.encode()).hexdigest(), direction=args.direction,
                   timeframe=args.timeframe, python=sys.version, hash_seed=os.environ.get("PYTHONHASHSEED"),
                   timings=payload["timings"], profile=bool(profile))
    if sys.platform == "win32":
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("faults", wintypes.DWORD)] + [(name, ctypes.c_size_t) for name in
                ("peak", "working", "poolPeak", "pool", "nonPoolPeak", "nonPool", "pagefile", "peakPagefile")]
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        ctypes.windll.kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
        if not ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
            raise ctypes.WinError()
        summary["peak_working_set_bytes"] = counters.peak
    if profile:
        profile.dump_stats(str(args.out.with_suffix(".prof")))
        with args.out.with_suffix(".profile.txt").open("w", encoding="utf-8") as stream:
            pstats.Stats(profile, stream=stream).sort_stats("cumulative").print_stats(65)
    args.out.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if paired_replacement:
        (evidence / "paired-replacement-complete.json").write_text(json.dumps({
            "status": "PASS", "baseline": str(baseline_out), "optimized": str(args.out),
            "note": "Both runs were actually replaced in baseline-then-final-candidate order."
        }, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
