"""Run resumable, fresh-process comparisons for two TradingBot Engine trees."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
RUNNER = ROOT / "engineering/verification/engine-refactor-20261117/run_case.py"
DIRECTIONS = ("bullish", "bearish", "both")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_fingerprint(root: Path) -> str:
    files = {
        path.relative_to(root).as_posix(): sha(path.read_bytes())
        for path in (root / "engine").rglob("*.py")
        if "tests" not in path.parts and "__pycache__" not in path.parts
    }
    if not files:
        raise ValueError(f"No Engine files under {root}")
    return sha(json.dumps(files, sort_keys=True).encode())


def chart_timeframes() -> list[int]:
    source = (ROOT / "apps/chart/src/main.js").read_text(encoding="utf-8")
    block = source.split("const TF = [", 1)[1].split("];", 1)[0]
    return sorted(map(int, re.findall(r"\bs: (\d+)", block)), reverse=True)


def first_difference(before, after, where="$") -> dict | None:
    if type(before) is not type(after):
        return {"path": where, "baseline_type": type(before).__name__, "candidate_type": type(after).__name__}
    if isinstance(before, dict):
        if list(before) != list(after):
            return {"path": where, "baseline_keys": list(before), "candidate_keys": list(after)}
        entries = ((before[key], after[key], f"{where}.{key}") for key in before)
    elif isinstance(before, list):
        if len(before) != len(after):
            return {"path": where, "baseline_length": len(before), "candidate_length": len(after)}
        entries = ((left, right, f"{where}[{i}]") for i, (left, right) in enumerate(zip(before, after)))
    else:
        return None if before == after else {"path": where, "baseline": before, "candidate": after}
    for left, right, path in entries:
        result = first_difference(left, right, path)
        if result:
            return result
    return None


def measure(root, row, timeframe, direction, output, opt):
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable, "-B", str(RUNNER), "--root", str(root), "--data", row["path"],
        "--out", str(output), "--timeframe", str(timeframe), "--direction", direction,
    ]
    if opt.profile:
        command.append("--profile")
    env = {**os.environ, "PYTHONHASHSEED": "0", "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        completed = subprocess.run(command, capture_output=True, timeout=opt.timeout, env=env)
    except subprocess.TimeoutExpired:
        return {"status": "INCOMPLETE", "timeout_seconds": opt.timeout}, None
    if completed.returncode:
        output.with_suffix(".error.log").write_bytes(completed.stderr)
        failure = output.with_suffix(".failure.json")
        detail = json.loads(failure.read_bytes()) if failure.exists() else {}
        return {"status": "FAIL", "exit_code": completed.returncode, **detail}, None

    stable_file = output.with_suffix(".stable.json")
    data = stable_file.read_bytes()
    summary = json.loads(output.with_suffix(".summary.json").read_bytes())
    assert sha(data) == summary["stable_sha256"] and summary["input_sha256"] == row["sha256"]
    with gzip.open(output.with_suffix(".stable.json.gz"), "wb", compresslevel=2) as stream:
        stream.write(data)
    stable_file.unlink()
    output.with_suffix(".stdout.json").unlink()
    return {"status": "PASS", "stable_bytes": len(data), **summary}, data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, default=ROOT)
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--frames", type=int, nargs="+")
    parser.add_argument("--inputs", type=int, nargs="+", help="Zero-based indexes in the input manifest")
    parser.add_argument("--directions", choices=DIRECTIONS, nargs="+", default=DIRECTIONS)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--profile", action="store_true")
    opt = parser.parse_args()
    if min(opt.runs, opt.timeout) < 1:
        parser.error("Runs and timeout must be positive.")
    frames = opt.frames or chart_timeframes()
    inputs = json.loads(opt.input_manifest.read_bytes())
    if opt.inputs is not None:
        inputs = [inputs[index] for index in opt.inputs]
    for row in inputs:
        if sha(Path(row["path"]).read_bytes()) != row["sha256"]:
            raise ValueError(f"RAW digest changed for {row['path']}")
    roots = {"baseline": opt.baseline.resolve(), "candidate": opt.candidate.resolve()}
    pin = {name: source_fingerprint(root) for name, root in roots.items()}
    opt.evidence_dir.mkdir(parents=True, exist_ok=True)
    progress = opt.evidence_dir / "results.jsonl"
    complete = set()
    if progress.exists():
        for line in progress.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record["sources"] != pin or record["profile"] != opt.profile:
                raise ValueError("Existing evidence was produced with a different Source or profiler mode.")
            if record["status"] == "PASS":
                complete.add(tuple(record["case"]))

    with progress.open("a", encoding="utf-8") as log:
        for frame in frames:
            for row in inputs:
                for direction in opt.directions:
                    for run in range(opt.runs):
                        case = (row["sha256"], frame, direction, run)
                        if case in complete:
                            continue
                        folder = opt.evidence_dir / row["sha256"][:16] / f"{frame}-{direction}" / str(run)
                        outcomes, output = {}, {}
                        order = tuple(roots) if run % 2 == 0 else tuple(reversed(roots))
                        for name in order:
                            outcomes[name], output[name] = measure(roots[name], row, frame, direction, folder / name, opt)
                        if {name: source_fingerprint(root) for name, root in roots.items()} != pin:
                            raise RuntimeError("An Engine tree changed during the comparison.")
                        statuses = {item["status"] for item in outcomes.values()}
                        difference = None
                        if statuses == {"PASS"}:
                            equal = output["baseline"] == output["candidate"]
                            status = "PASS" if equal else "FAIL"
                            if not equal:
                                difference = first_difference(json.loads(output["baseline"]), json.loads(output["candidate"]))
                                if difference is None:
                                    difference = {"path": "$", "reason": "Stable JSON bytes differ"}
                        else:
                            status = "FAIL" if "FAIL" in statuses else "INCOMPLETE"
                        record = {"case": case, "row_count": row["row_count"], "sources": pin,
                                  "profile": opt.profile, "status": status, "difference": difference, "runs": outcomes}
                        log.write(json.dumps(record) + "\n")
                        log.flush()
                        print(row["row_count"], frame, direction, run, status, flush=True)


if __name__ == "__main__":
    main()
