"""Capture zero-difference performance baselines for TradingBot Engine.

Runs the live bridge on selected RAW datasets and records wall time, peak RSS,
stable-output digests, and stage counts. RAW is read-only.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import orjson

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "engine"
LOCAL_STATE = Path(
    os.environ.get("TRADINGBOT_LOCAL_STATE_ROOT", ROOT / "apps" / "chart" / "state")
)
RAW_ROOT = LOCAL_STATE / "data" / "RAW"

PRODUCTION_MODULES = (
    "engine/bridge/trading_pipeline.py",
    "engine/pipeline/reaction_engine.py",
    "engine/pipeline/blue_line_detector.py",
    "engine/pipeline/a_zone_detector.py",
    "engine/pipeline/s_zone_detector.py",
    "engine/pipeline/e_zone_detector.py",
    "engine/pipeline/lifecycle_engine.py",
    "engine/pipeline/order_audit_engine.py",
    "engine/pipeline/direction_policy.py",
    "engine/pipeline/core_utils.py",
)

SIZE_LIMIT_BYTES = 10 * 1024 * 1024  # user-requested benchmark/test scope

STAGES = (
    "reactions",
    "resets",
    "blueLines",
    "aZones",
    "sZones",
    "eZones",
    "stopAlls",
    "orderAudit",
)

# Representative workloads. Paths are relative to RAW_ROOT.
DEFAULT_CASES = (
    {
        "name": "xauusd-30s-smoke",
        "raw": "FOREXCOM/XAUUSD/RAW FOREXCOM_XAUUSD 30S FROM 2026-09-28 20-44-00 TO 2026-09-29 11-45-30.json",
        "timeframe": 30,
    },
    {
        "name": "xauusd-5s-medium",
        "raw": "FOREXCOM/XAUUSD/RAW FOREXCOM_XAUUSD 5S FROM 2026-09-16 22-35-00 TO 2026-09-17 19-15-35.json",
        "timeframe": 5,
    },
    {
        "name": "usoil-5s-medium",
        "raw": "FXCM/USOIL/RAW FXCM_USOIL 5S FROM 2026-09-21 22-50-00 TO 2026-09-24 00-26-20.json",
        "timeframe": 5,
    },
    {
        "name": "usoil-5s-candidate-heavy",
        "raw": "FXCM/USOIL/RAW FXCM_USOIL 5S FROM 2026-09-21 22-54-30 TO 2026-09-29 10-51-55.json",
        "timeframe": 5,
    },
    {
        "name": "xauusd-5s-wide",
        "raw": "FOREXCOM/XAUUSD/RAW FOREXCOM_XAUUSD 5S FROM 2026-09-22 11-00-00 TO 2026-09-29 11-55-05.json",
        "timeframe": 5,
    },
    {
        "name": "usoil-5s-long",
        "raw": "BaseLine/RAW FXCM_USOIL 5S FROM 2026-08-21 04-00-00 TO 2026-09-29 11-46-20.json",
        "timeframe": 5,
    },
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_hashes() -> dict[str, str]:
    return {
        path: sha256_bytes((ROOT / path).read_bytes())
        for path in PRODUCTION_MODULES
    }


def peak_rss_tracker(pid: int):
    if os.name != "nt":
        return None
    import ctypes

    class ProcessMemoryCounters(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_uint32),
            ("PageFaultCount", ctypes.c_uint32),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", ctypes.c_uint32), ("dwHighDateTime", ctypes.c_uint32)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.GetProcessTimes.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(FILETIME),
        ctypes.POINTER(FILETIME),
        ctypes.POINTER(FILETIME),
        ctypes.POINTER(FILETIME),
    ]
    psapi.GetProcessMemoryInfo.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ProcessMemoryCounters),
        ctypes.c_uint32,
    ]
    handle = kernel.OpenProcess(0x1000 | 0x0010, 0, pid)
    if not handle:
        return None

    def sample():
        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        peak = None
        if psapi.GetProcessMemoryInfo(
            handle, ctypes.byref(counters), ctypes.sizeof(counters)
        ):
            peak = int(counters.PeakWorkingSetSize)
        creation = FILETIME()
        exit_t = FILETIME()
        kernel_t = FILETIME()
        user_t = FILETIME()
        cpu = None
        if kernel.GetProcessTimes(
            handle,
            ctypes.byref(creation),
            ctypes.byref(exit_t),
            ctypes.byref(kernel_t),
            ctypes.byref(user_t),
        ):
            def ft(v):
                return (v.dwHighDateTime << 32) | v.dwLowDateTime
            cpu = (ft(kernel_t) + ft(user_t)) / 1e7
        return peak, cpu

    def close() -> None:
        kernel.CloseHandle(handle)

    return sample, close


def run_case(
    name: str,
    raw_path: Path,
    timeframe: int,
    direction: str,
    output_dir: Path,
    repeats: int,
    bridge_output: bool,
    timeout_seconds: int,
    max_raw_bytes: int,
) -> dict:
    # Size gate runs BEFORE any Engine invocation or RAW content read.
    raw_size = raw_path.stat().st_size
    if raw_size >= max_raw_bytes:
        return {
            "name": name,
            "direction": direction,
            "status": "NOT APPLICABLE",
            "reason": "DATASET_SIZE_LIMIT",
            "size_bytes": raw_size,
            "limit_bytes": max_raw_bytes,
            "rawPath": str(raw_path),
        }

    raw_bytes = raw_path.read_bytes()
    rows = orjson.loads(raw_bytes)
    first = min(int(row["time"]) for row in rows)
    last = max(int(row["time"]) for row in rows)
    row_count = len(rows)
    raw_hash = sha256_bytes(raw_bytes)
    del rows, raw_bytes

    command = [
        sys.executable,
        "-B",
        str(ENGINE / "bridge" / "trading_pipeline.py"),
        "--reaction-engine",
        str(ENGINE / "pipeline" / "reaction_engine.py"),
        "--blue-line-engine",
        str(ENGINE / "pipeline" / "blue_line_detector.py"),
        "--a-zone-engine",
        str(ENGINE / "pipeline" / "a_zone_detector.py"),
        "--s-zone-engine",
        str(ENGINE / "pipeline" / "s_zone_detector.py"),
        "--e-zone-engine",
        str(ENGINE / "pipeline" / "e_zone_detector.py"),
        "--lifecycle-engine",
        str(ENGINE / "pipeline" / "lifecycle_engine.py"),
        "--data",
        str(raw_path),
        "--timeframe",
        str(timeframe),
        "--from-time",
        str(first),
        "--to-time",
        str(last),
        "--direction",
        direction,
    ]
    if bridge_output:
        command.append("--bridge-output")

    runs = []
    last_payload = None
    last_normalized = None
    stdout_path = output_dir / f"{name}.{direction}.stdout.json"
    stderr_path = output_dir / f"{name}.{direction}.stderr.log"
    for index in range(repeats):
        started = time.perf_counter()
        with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                stdout=stdout_handle,
                stderr=stderr_handle,
            )
            tracker = peak_rss_tracker(process.pid)
            peak = None
            cpu_seconds = None
            if tracker is not None:
                sample, close = tracker
                while process.poll() is None:
                    current_peak, current_cpu = sample()
                    if current_peak is not None:
                        peak = max(peak or 0, current_peak)
                    if current_cpu is not None:
                        cpu_seconds = current_cpu
                    time.sleep(0.05)
                final_peak, final_cpu = sample()
                if final_peak is not None:
                    peak = max(peak or 0, final_peak)
                if final_cpu is not None:
                    cpu_seconds = final_cpu
                close()
            return_code = process.wait(timeout=timeout_seconds)
        wall = time.perf_counter() - started
        if return_code != 0:
            return {
                "name": name,
                "direction": direction,
                "status": "FAIL",
                "returnCode": return_code,
                "stderrTail": stderr_path.read_text(encoding="utf-8", errors="replace")[-2000:],
                "rawPath": str(raw_path),
            }
        stdout = stdout_path.read_bytes()
        payload = orjson.loads(stdout)
        timings = payload.get("timings")
        payload.pop("timings", None)
        normalized = orjson.dumps(payload)
        last_payload = payload
        last_normalized = normalized
        runs.append(
            {
                "wallSeconds": wall,
                "cpuSeconds": cpu_seconds,
                "peakWorkingSetBytes": peak,
                "stdoutBytes": len(stdout),
                "timings": timings,
            }
        )

    assert last_payload is not None and last_normalized is not None
    directions = last_payload.get("directions", {})
    result = directions.get(direction, {})
    counts = {
        stage: len(result.get(stage) or [])
        for stage in STAGES
    }
    if "orderAudit" in result:
        counts["orderAuditCauses"] = sum(
            len(item.get("causes") or []) for item in result["orderAudit"]
        )
    stage_digests = {}
    for stage in STAGES:
        value = result.get(stage)
        if value is None:
            continue
        stage_digests[stage] = {
            "count": len(value),
            "sha256": sha256_bytes(
                orjson.dumps(value)
            ),
        }

    archive_name = f"{name}.{direction}.normalized.json.gz"
    with (output_dir / archive_name).open("wb") as raw_handle:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_handle, mtime=0) as handle:
            handle.write(last_normalized)

    walls = sorted(run["wallSeconds"] for run in runs)
    cpus = sorted(run["cpuSeconds"] for run in runs if run.get("cpuSeconds") is not None)
    median_wall = walls[len(walls) // 2] if walls else None
    median_cpu = cpus[len(cpus) // 2] if cpus else None
    return {
        "name": name,
        "direction": direction,
        "status": "PASS",
        "rawPath": str(raw_path),
        "rawSha256": raw_hash,
        "rawRows": row_count,
        "rawFirst": first,
        "rawLast": last,
        "timeframe": timeframe,
        "bridgeOutput": bridge_output,
        "repeats": repeats,
        "runs": runs,
        "medianWallSeconds": median_wall,
        "medianCpuSeconds": median_cpu,
        "minWallSeconds": walls[0] if walls else None,
        "maxWallSeconds": walls[-1] if walls else None,
        "peakWorkingSetBytes": max(
            (run["peakWorkingSetBytes"] or 0) for run in runs
        )
        if runs
        else None,
        "normalizedSha256": sha256_bytes(last_normalized),
        "normalizedBytes": len(last_normalized),
        "counts": counts,
        "stageDigests": stage_digests,
        "normalizedArchive": archive_name,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--direction",
        choices=("bullish", "bearish", "both"),
        default="both",
    )
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument(
        "--max-raw-bytes",
        type=int,
        default=SIZE_LIMIT_BYTES,
        help="Skip RAW files with size >= this many bytes (default 10 MiB)",
    )
    parser.add_argument("--bridge-output", action="store_true")
    parser.add_argument("--select", action="append", default=[])
    parser.add_argument(
        "--case",
        action="append",
        default=[],
        help="name=relpath@timeframe override; if set, replaces default cases",
    )
    args = parser.parse_args()

    cases = []
    if args.case:
        for item in args.case:
            name, rest = item.split("=", 1)
            rel, tf = rest.rsplit("@", 1)
            cases.append({"name": name, "raw": rel, "timeframe": int(tf)})
    else:
        cases = list(DEFAULT_CASES)

    if args.select:
        cases = [case for case in cases if any(token in case["name"] for token in args.select)]

    args.output.mkdir(parents=True, exist_ok=True)
    directions = ("bullish", "bearish") if args.direction == "both" else (args.direction,)

    manifest = {
        "status": "INCOMPLETE",
        "pythonVersion": sys.version,
        "sourceHashes": source_hashes(),
        "cases": [],
    }
    manifest_path = args.output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    for case in cases:
        raw_path = RAW_ROOT / case["raw"]
        if not raw_path.exists():
            record = {
                "name": case["name"],
                "status": "FAIL",
                "error": f"RAW missing: {raw_path}",
            }
            manifest["cases"].append(record)
            print(f"{case['name']}: FAIL missing RAW", flush=True)
            continue
        for direction in directions:
            print(
                f"running {case['name']} {direction} rows~ raw={raw_path.name}",
                flush=True,
            )
            record = run_case(
                case["name"],
                raw_path,
                case["timeframe"],
                direction,
                args.output,
                args.repeats,
                args.bridge_output,
                args.timeout_seconds,
                args.max_raw_bytes,
            )
            manifest["cases"].append(record)
            status = record["status"]
            wall = record.get("medianWallSeconds")
            digest = (record.get("normalizedSha256") or "")[:16]
            print(
                f"{case['name']} {direction}: {status} wall={wall} digest={digest}",
                flush=True,
            )
            manifest_path.write_text(
                json.dumps(manifest, indent=2), encoding="utf-8"
            )

    executed = [c for c in manifest["cases"] if c.get("status") in ("PASS", "FAIL")]
    skipped = [c for c in manifest["cases"] if c.get("status") == "NOT APPLICABLE"]
    if not manifest["cases"]:
        manifest["status"] = "INCOMPLETE"
    elif any(c.get("status") == "FAIL" for c in executed):
        manifest["status"] = "FAIL"
    elif executed and all(c.get("status") == "PASS" for c in executed):
        manifest["status"] = "PASS"
    else:
        manifest["status"] = "INCOMPLETE"
    manifest["skippedBySizeLimit"] = [
        {
            "name": c.get("name"),
            "direction": c.get("direction"),
            "size_bytes": c.get("size_bytes"),
            "reason": c.get("reason"),
        }
        for c in skipped
    ]
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"manifest status={manifest['status']} -> {manifest_path}", flush=True)
    return 0 if manifest["status"] in ("PASS", "INCOMPLETE") and not any(
        c.get("status") == "FAIL" for c in manifest["cases"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
