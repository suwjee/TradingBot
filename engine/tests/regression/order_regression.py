"""Run complete selected-RAW Order regressions and freeze ordered JSON evidence."""

from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import orjson


ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "engine"
LOCAL_STATE = Path(os.environ.get("TRADINGBOT_LOCAL_STATE_ROOT", ROOT / "apps" / "chart" / "state"))
RAW_ROOT = LOCAL_STATE / "data" / "raw"
sys.path.insert(0, str(ROOT / "engine" / "tests" / "verification"))
from verify_order_b_raw import verify


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


def child_peak_rss(pid: int) -> int | None:
    if os.name != "nt":
        return None
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    psapi.GetProcessMemoryInfo.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(ProcessMemoryCounters), ctypes.c_uint32,
    ]
    handle = kernel.OpenProcess(0x1000 | 0x0010, 0, pid)
    if not handle:
        return None
    try:
        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        if not psapi.GetProcessMemoryInfo(
            handle, ctypes.byref(counters), ctypes.sizeof(counters)
        ):
            return None
        return int(counters.PeakWorkingSetSize)
    finally:
        kernel.CloseHandle(handle)


def source_hashes() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [ENGINE / "__init__.py", *sorted((ENGINE / "bridge").rglob("*.py")), *sorted((ENGINE / "pipeline").rglob("*.py"))]
    }


def raw_files() -> list[Path]:
    return [
        path for path in sorted(RAW_ROOT.rglob("*.json"))
        if not path.name.endswith(".meta.json")
    ]


def run_one(raw_path: Path, output_dir: Path, index: int, timeframe: int) -> dict[str, object]:
    data = raw_path.read_bytes()
    rows = orjson.loads(data)
    first = min(int(row["time"]) for row in rows)
    last = max(int(row["time"]) for row in rows)
    raw_hash = hashlib.sha256(data).hexdigest()
    row_count = len(rows)
    del rows, data

    stem = f"case-{index:02d}"
    payload_path = output_dir / f"{stem}.json"
    stderr_path = output_dir / f"{stem}.stderr.log"
    command = [
        sys.executable, "-B", str(ENGINE / "bridge/trading_pipeline.py"),
        "--reaction-engine", str(ENGINE / "pipeline/reaction_engine.py"),
        "--blue-line-engine", str(ENGINE / "pipeline/blue_line_detector.py"),
        "--a-zone-engine", str(ENGINE / "pipeline/a_zone_detector.py"),
        "--s-zone-engine", str(ENGINE / "pipeline/s_zone_detector.py"),
        "--e-zone-engine", str(ENGINE / "pipeline/e_zone_detector.py"),
        "--lifecycle-engine", str(ENGINE / "pipeline/lifecycle_engine.py"),
        "--blue-lines", "enabled", "--a-zones", "enabled",
        "--s-zones", "enabled", "--bridge-output",
        "--data", str(raw_path), "--timeframe", str(timeframe),
        "--from-time", str(first), "--to-time", str(last),
        "--direction", "both",
    ]
    started = time.perf_counter()
    with payload_path.open("wb") as output, stderr_path.open("wb") as errors:
        process = subprocess.Popen(command, cwd=ROOT, stdout=output, stderr=errors)
        peak_rss = None
        while process.poll() is None:
            current = child_peak_rss(process.pid)
            if current is not None:
                peak_rss = max(peak_rss or 0, current)
            time.sleep(0.1)
        return_code = process.returncode
    wall_seconds = round(time.perf_counter() - started, 3)
    record: dict[str, object] = {
        "rawPath": str(raw_path),
        "rawSha256": raw_hash,
        "rawRows": row_count,
        "rawFirstEpoch": first,
        "rawLastEpoch": last,
        "timeframeSeconds": timeframe,
        "direction": "both",
        "bridgeOutput": True,
        "wallSeconds": wall_seconds,
        "peakWorkingSetBytes": peak_rss,
        "returnCode": return_code,
        "stderrPath": stderr_path.name,
    }
    if return_code != 0:
        record["status"] = "FAIL"
        record["errorTail"] = stderr_path.read_text(encoding="utf-8", errors="replace")[-2500:]
        return record
    payload = orjson.loads(payload_path.read_bytes())
    record["timings"] = payload.pop("timings", None)
    normalized = orjson.dumps(payload)
    record["normalizedSha256"] = hashlib.sha256(normalized).hexdigest()
    record["counts"] = {
        direction: {
            **{
                key: len(values)
                for key, values in result.items() if isinstance(values, list)
            },
            "orderBCausesByPostStop": dict(Counter(
                cause["postBehaviorType"]
                for item in result["orderAudit"] for cause in item["causes"]
                if cause["kind"] == "reset-leg"
            )),
        }
        for direction, result in payload["directions"].items()
    }
    record["rawCauseValidation"] = verify(raw_path, payload_path, timeframe)
    archive_path = output_dir / f"{stem}.json.gz"
    with archive_path.open("wb") as output:
        with gzip.GzipFile(filename="", mode="wb", fileobj=output, mtime=0) as archive:
            archive.write(normalized)
    record["normalizedPayloadPath"] = archive_path.name
    record["status"] = "PASS"
    payload_path.unlink()
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeframe", type=int, default=30)
    parser.add_argument("--raw", type=Path, action="append")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    files = args.raw if args.raw else raw_files()
    manifest: dict[str, object] = {
        "status": "INCOMPLETE",
        "pythonVersion": sys.version,
        "sourceHashes": source_hashes(),
        "referenceHashes": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((ENGINE / "algorithms").glob("*Source_Synchronized.md"))
        },
        "cases": [],
    }
    manifest_path = args.output / "manifest.json"
    for index, path in enumerate(files, start=1):
        print(f"[{index}/{len(files)}] {path.name}", flush=True)
        try:
            case = run_one(path, args.output, index, args.timeframe)
        except Exception as exc:
            case = {"rawPath": str(path), "status": "FAIL", "error": repr(exc)}
        manifest["cases"].append(case)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  {case['status']} {case.get('wallSeconds', 'n/a')} s", flush=True)
    manifest["status"] = (
        "PASS" if all(item["status"] == "PASS" for item in manifest["cases"])
        else "FAIL"
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(manifest["status"])
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
