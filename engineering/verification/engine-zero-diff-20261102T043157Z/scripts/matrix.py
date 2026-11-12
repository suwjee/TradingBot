"""Sequential cold-CLI measurements with complete raw output and exact comparisons."""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import gzip
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

EVIDENCE = Path(__file__).resolve().parents[1]
ROOT = EVIDENCE.parents[2]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def phase_source_guard(phase: str, source_root: Path) -> dict:
    engine = source_root / "engine"
    paths = [engine / "__init__.py", *sorted((engine / "bridge").rglob("*.py")), *sorted((engine / "pipeline").rglob("*.py"))]
    current = {path.relative_to(source_root).as_posix(): file_sha(path) for path in paths}
    directory = EVIDENCE / phase
    directory.mkdir(exist_ok=True)
    target = directory / "source-manifest.json"
    if target.exists():
        if json.loads(target.read_bytes()) != current:
            raise RuntimeError(f"Source changed within immutable phase {phase}")
    else:
        if phase == "before":
            initial = {item["path"]: item["sha256"] for item in json.loads((EVIDENCE / "discovery/source-manifest-before.json").read_bytes())}
            if initial != current:
                raise RuntimeError("BEFORE must match original pre-edit source capture")
        elif list(directory.rglob("*.metrics.json")):
            raise RuntimeError("Cannot retroactively infer Source for existing non-before evidence")
        save(target, current)
    return current


def command(case: dict, source_root: Path = ROOT) -> list[str]:
    pipeline = source_root / "engine" / "pipeline"
    cmd = [sys.executable, "-B", str(source_root / "engine" / "bridge" / "trading_pipeline.py")]
    for flag, name in [("--engine", "reaction_engine.py"), ("--blue-engine", "blue_line_detector.py"),
                       ("--a-engine", "a_zone_detector.py"), ("--s-engine", "s_zone_detector.py"),
                       ("--e-engine", "e_zone_detector.py")]:
        cmd.extend([flag, str(pipeline / name)])
    if case.get("stopall", True):
        cmd.extend(["--stopall-engine", str(pipeline / "lifecycle_engine.py")])
    cmd.extend(["--data", case["input"], "--timeframe", str(case["timeframe"]),
                "--from-time", str(case["from_time"]), "--to-time", str(case["to_time"]),
                "--direction", case["direction"], "--pl-ph", case.get("primary", "enabled")])
    if case.get("bridge_output", True):
        cmd.append("--bridge-output")
    return cmd


def calculation_arguments(cmd: list[str]) -> list[str]:
    """Keep all calculation parameters; normalize only frozen-source root paths."""
    arguments = cmd[3:]
    module_flags = {"--engine", "--blue-engine", "--a-engine", "--s-engine", "--e-engine", "--stopall-engine"}
    return [Path(value).name if index and arguments[index-1] in module_flags else value
            for index, value in enumerate(arguments)]


class MemoryCounters(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("faults", wintypes.DWORD),
                *[(name, ctypes.c_size_t) for name in ["peak", "working", "peak_paged", "paged",
                                                       "peak_nonpaged", "nonpaged", "pagefile", "peak_pagefile"]]]


class ProcessMetrics:
    def __init__(self, process: subprocess.Popen) -> None:
        self.handle = wintypes.HANDLE(int(process._handle))
        self.memory = MemoryCounters()
        self.memory.cb = ctypes.sizeof(self.memory)
        self.peak = 0
        self.cpu = None
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.psapi = ctypes.WinDLL("psapi", use_last_error=True)
        self.psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
        self.kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, *[ctypes.POINTER(wintypes.FILETIME)] * 4]

    def update(self) -> None:
        if self.psapi.GetProcessMemoryInfo(self.handle, ctypes.byref(self.memory), ctypes.sizeof(self.memory)):
            self.peak = max(self.peak, self.memory.peak)
        times = [wintypes.FILETIME() for _ in range(4)]
        if self.kernel.GetProcessTimes(self.handle, *[ctypes.byref(item) for item in times]):
            self.cpu = sum((item.dwHighDateTime << 32) | item.dwLowDateTime for item in times[2:]) / 10_000_000


def stable_bytes(raw: bytes) -> bytes:
    payload = json.loads(raw)
    # Explicit telemetry only: build_response_payload adds this timing envelope.
    # Preserve all other values, dict insertion order, array order, types/text.
    payload.pop("timings", None)
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode()


def first_diff(left: object, right: object, path: str = "$") -> dict | None:
    if type(left) is not type(right):
        return {"path": path, "before": left, "after": right, "reason": "type"}
    if isinstance(left, dict):
        if list(left) != list(right):
            return {"path": path, "before_keys": list(left), "after_keys": list(right), "reason": "keys/order"}
        for key in left:
            difference = first_diff(left[key], right[key], path + "." + key)
            if difference:
                return difference
    elif isinstance(left, list):
        if len(left) != len(right):
            return {"path": path, "before_length": len(left), "after_length": len(right), "reason": "length"}
        for index, (a, b) in enumerate(zip(left, right)):
            difference = first_diff(a, b, f"{path}[{index}]")
            if difference:
                return difference
    elif left != right:
        return {"path": path, "before": left, "after": right, "reason": "value"}
    return None


def run(case: dict, phase: str, repeat: int, timeout: float, source_root: Path, baseline_phase: str = "before", hash_seed: str | None = None, pycache_prefix: str | None = None) -> dict:
    source_manifest = phase_source_guard(phase, source_root)
    output = EVIDENCE / phase / case["id"]
    output.mkdir(parents=True, exist_ok=True)
    prefix = output / f"run-{repeat:02d}"
    meta_path = prefix.with_suffix(".metrics.json")
    if meta_path.exists():
        saved = json.loads(meta_path.read_bytes())
        if (saved["command"] != command(case, source_root)
                or saved["input_sha256_before"] != file_sha(Path(case["input"]))
                or saved.get("source_manifest", source_manifest) != source_manifest
                or saved.get("explicit_hash_seed") != hash_seed
                or saved.get("pycache_prefix") != pycache_prefix
                or saved.get("baseline_phase") != baseline_phase):
            raise RuntimeError(f"Existing evidence does not match current request/input/Source: {prefix}")
        if (not prefix.with_suffix(".stderr.log").exists()
                or not prefix.with_suffix(".stdout.json").exists()
                or file_sha(prefix.with_suffix(".stdout.json")) != saved["raw_output_sha256"]):
            raise RuntimeError(f"Existing complete-output evidence is missing or changed: {prefix}")
        if saved["status"] == "PASS":
            stable_path = prefix.with_suffix(".stable.json.gz")
            if not stable_path.exists() or sha(gzip.decompress(stable_path.read_bytes())) != saved["stable_sha256"]:
                raise RuntimeError(f"Existing stable evidence is missing or changed: {prefix}")
        return saved
    if prefix.with_suffix(".stdout.json").exists():
        raise RuntimeError(f"Partial prior run must be preserved: {prefix}")
    input_path = Path(case["input"])
    input_before = file_sha(input_path)
    cmd = command(case, source_root)
    metadata = {"case": case["id"], "repeat": repeat, "command": cmd, "cwd": str(ROOT),
                "input_sha256_before": input_before, "source_root": str(source_root),
                "source_manifest": source_manifest,
                "baseline_phase": baseline_phase,
                "explicit_hash_seed": hash_seed,
                "pycache_prefix": pycache_prefix,
                "effective_hash_seed": hash_seed if hash_seed is not None else os.environ.get("PYTHONHASHSEED"),
                "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    started = time.perf_counter()
    timed_out = False
    with prefix.with_suffix(".stdout.json").open("wb") as stdout, prefix.with_suffix(".stderr.log").open("wb") as stderr:
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        if hash_seed is not None:
            environment["PYTHONHASHSEED"] = hash_seed
        if pycache_prefix is not None:
            environment["PYTHONPYCACHEPREFIX"] = pycache_prefix
        process = subprocess.Popen(cmd, cwd=ROOT, stdout=stdout, stderr=stderr,
                                   env=environment, creationflags=subprocess.CREATE_NO_WINDOW)
        metrics = ProcessMetrics(process)
        while process.poll() is None:
            metrics.update()
            if time.perf_counter() - started > timeout:
                process.kill()
                timed_out = True
                break
            time.sleep(0.05)
        process.wait()
        metrics.update()
    metadata.update({"wall_seconds": time.perf_counter() - started, "cpu_seconds": metrics.cpu,
                     "peak_working_set_bytes": metrics.peak, "exit_code": process.returncode,
                     "timeout": timed_out, "input_sha256_after": file_sha(input_path)})
    raw = prefix.with_suffix(".stdout.json").read_bytes()
    metadata.update({"raw_output_bytes": len(raw), "raw_output_sha256": sha(raw)})
    metadata["status"] = "INCOMPLETE" if timed_out else "FAIL" if process.returncode else "PASS"
    if metadata["input_sha256_after"] != input_before:
        metadata["status"] = "FAIL"
        metadata["input_mutated"] = True
    if metadata["status"] == "PASS":
        stable = stable_bytes(raw)
        with gzip.open(prefix.with_suffix(".stable.json.gz"), "wb") as stream:
            stream.write(stable)
        metadata["stable_sha256"] = sha(stable)
        reference = (EVIDENCE / baseline_phase / case["id"] / "run-01.stable.json.gz")
        if phase != baseline_phase and not reference.exists():
            raise RuntimeError(f"Candidate requires a saved original BEFORE payload: {case['id']}")
        if phase != baseline_phase or repeat != 1:
            baseline_meta = json.loads(reference.with_name("run-01.metrics.json").read_bytes())
            if (baseline_meta["status"] != "PASS" or baseline_meta["input_sha256_before"] != input_before
                    or calculation_arguments(baseline_meta["command"]) != calculation_arguments(cmd)
                    or baseline_meta.get("pycache_prefix") != pycache_prefix
                    or baseline_meta.get("explicit_hash_seed") != hash_seed):
                raise RuntimeError(f"Candidate BEFORE context is invalid: {case['id']}")
        if reference.exists():
            saved = gzip.decompress(reference.read_bytes())
            metadata["stable_bytes_equal"] = stable == saved
            metadata["first_difference"] = first_diff(json.loads(saved), json.loads(stable))
            if stable != saved or metadata["first_difference"]:
                metadata["status"] = "FAIL"
        stages = {}
        for direction, group in json.loads(stable).get("directions", {}).items():
            stages[direction] = {key: {"count": len(value), "sha256": sha(json.dumps(value, separators=(",", ":")).encode())}
                                 for key, value in group.items() if isinstance(value, (list, dict))}
        metadata["stages"] = stages
    save(meta_path, metadata)
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase")
    parser.add_argument("--select", default="")
    parser.add_argument("--repeats", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=1800)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--baseline-phase", default="before")
    parser.add_argument("--hash-seed", help="Explicitly recorded auxiliary paired-performance control; never silently pins default baselines")
    parser.add_argument("--pycache-prefix", help="Explicit child-only cache-root control; -B prevents writes")
    args = parser.parse_args()
    cases = json.loads((EVIDENCE / "discovery" / "workloads.json").read_bytes())
    selected = set(args.select.split(",")) if args.select else None
    failed = False
    for case in cases:
        if selected and case["id"] not in selected:
            continue
        for repeat in range(1, (args.repeats or case.get("repeats", 2)) + 1):
            record = run(case, args.phase, repeat, args.timeout, args.source_root, args.baseline_phase, args.hash_seed, args.pycache_prefix)
            print(json.dumps({key: record.get(key) for key in ["case", "repeat", "status", "wall_seconds", "cpu_seconds", "peak_working_set_bytes", "stable_bytes_equal"]}), flush=True)
            if record["status"] != "PASS":
                failed = True
                break
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
