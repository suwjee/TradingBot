"""Read-only diagnosis; diagnostic unordered-map equality never grants PASS."""
from __future__ import annotations
import gzip
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from matrix import EVIDENCE, ROOT, save


def differences(a, b, path="$"):
    result = []
    if type(a) is not type(b):
        return [{"path": path, "kind": "type", "before": type(a).__name__, "after": type(b).__name__}]
    if isinstance(a, dict):
        if set(a) != set(b):
            result.append({"path": path, "kind": "key-membership", "before": list(a), "after": list(b)})
        elif list(a) != list(b):
            result.append({"path": path, "kind": "mapping-key-order", "before": list(a), "after": list(b)})
        for key in a.keys() & b.keys():
            result.extend(differences(a[key], b[key], path + "." + key))
    elif isinstance(a, list):
        if len(a) != len(b):
            result.append({"path": path, "kind": "array-length", "before": len(a), "after": len(b)})
        for index, (left, right) in enumerate(zip(a, b)):
            result.extend(differences(left, right, f"{path}[{index}]"))
    elif a != b:
        result.append({"path": path, "kind": "value", "before": a, "after": b})
    return result


def probe():
    path = ROOT / "engine/bridge/trading_pipeline.py"
    spec = importlib.util.spec_from_file_location("probe_bridge", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    names = ["reactions", "resets", "blueLines", "aZones", "sZones", "eZones", "stopAlls", "orderAudit"]
    first = {"reactions": [{"id": 1}], "bridgeOutput": {name: [] for name in names}}
    last = {"reactions": [{"id": 2}], "bridgeOutput": {name: [] for name in names}}
    output = module.merge_regime_outputs([("bullish", first), ("bullish", last)])
    print(json.dumps(output, separators=(",", ":")))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--probe":
        probe()
        return
    report = {"gate_status": "FAIL", "production_edits": "NONE", "failed_real_cases": [], "hashseed_probe": []}
    for name in ["usoil-month-30s-bearish", "xau-sep28-30s-bullish"]:
        directory = EVIDENCE / "before" / name
        raw = [gzip.decompress((directory / f"run-{number:02d}.stable.json.gz").read_bytes()) for number in (1,2)]
        found = differences(json.loads(raw[0]), json.loads(raw[1]))
        report["failed_real_cases"].append({"case": name, "ordered_stable_bytes_equal": raw[0] == raw[1],
                                             "stable_differences": found, "difference_count": len(found),
                                             "non_order_difference_count": sum(item["kind"] != "mapping-key-order" for item in found)})
    output = EVIDENCE / "discovery/determinism-probe"
    output.mkdir(exist_ok=True)
    for seed in ("0", "1", "2", "3"):
        completed = subprocess.run([sys.executable, "-B", __file__, "--probe"], cwd=ROOT,
                                   env={**os.environ, "PYTHONHASHSEED": seed}, capture_output=True, check=True)
        (output / f"seed-{seed}.stdout.json").write_bytes(completed.stdout)
        (output / f"seed-{seed}.stderr.log").write_bytes(completed.stderr)
        result = json.loads(completed.stdout)
        report["hashseed_probe"].append({"seed": seed, "bridge_output_keys": list(result["bullish"]["bridgeOutput"]), "exit_code": completed.returncode})
    report["root_cause"] = "merge_regime_outputs rebuilds bridgeOutput by iterating bridge_keys, a set of string keys; hash randomization changes insertion order before JSON encoding."
    report["diagnostic_only"] = "Explicit hash seeds are used only to reproduce cause. Original default-environment baselines remain FAIL and are not replaced, sorted or normalized to pass."
    save(EVIDENCE / "discovery/determinism-first-differences.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
