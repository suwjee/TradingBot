"""Compare two complete selected-RAW regression manifests without tolerance."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

import orjson


def first_difference(left: object, right: object, path: str = "$" ) -> str | None:
    if type(left) is not type(right):
        return f"{path}: type {type(left).__name__} != {type(right).__name__}"
    if isinstance(left, dict):
        left_keys = list(left)
        right_keys = list(right)
        if left_keys != right_keys:
            return f"{path}: ordered keys {left_keys} != {right_keys}"
        for key in left_keys:
            difference = first_difference(left[key], right[key], f"{path}.{key}")
            if difference is not None:
                return difference
        return None
    if isinstance(left, list):
        if len(left) != len(right):
            return f"{path}: length {len(left)} != {len(right)}"
        for index, (a, b) in enumerate(zip(left, right)):
            difference = first_difference(a, b, f"{path}[{index}]")
            if difference is not None:
                return difference
        return None
    return None if left == right else f"{path}: {left!r} != {right!r}"


def compare(before_dir: Path, after_dir: Path) -> dict[str, object]:
    before = json.loads((before_dir / "manifest.json").read_text(encoding="utf-8"))
    after = json.loads((after_dir / "manifest.json").read_text(encoding="utf-8"))
    if before["status"] != "PASS" or after["status"] != "PASS":
        raise ValueError("Both regression manifests must have PASS status")
    if len(before["cases"]) != len(after["cases"]):
        raise ValueError("Regression case counts differ")
    checked: list[dict[str, object]] = []
    for index, (old, new) in enumerate(zip(before["cases"], after["cases"]), 1):
        for key in (
            "rawPath", "rawSha256", "rawRows", "rawFirstEpoch", "rawLastEpoch",
            "timeframeSeconds", "direction", "bridgeOutput",
        ):
            if old[key] != new[key]:
                raise ValueError(f"Case {index} input mismatch at {key}")
        old_data = gzip.decompress((before_dir / old["normalizedPayloadPath"]).read_bytes())
        new_data = gzip.decompress((after_dir / new["normalizedPayloadPath"]).read_bytes())
        difference = None
        if old_data != new_data:
            difference = first_difference(orjson.loads(old_data), orjson.loads(new_data))
            if difference is None:
                difference = "Serialized bytes differ despite equal parsed objects"
        checked.append({
            "case": index,
            "rawPath": old["rawPath"],
            "status": "PASS" if difference is None else "FAIL",
            "firstDifference": difference,
            "beforeSha256": old["normalizedSha256"],
            "afterSha256": new["normalizedSha256"],
            "beforeWallSeconds": old["wallSeconds"],
            "afterWallSeconds": new["wallSeconds"],
            "beforePeakWorkingSetBytes": old["peakWorkingSetBytes"],
            "afterPeakWorkingSetBytes": new["peakWorkingSetBytes"],
        })
    return {
        "status": "PASS" if all(item["status"] == "PASS" for item in checked) else "FAIL",
        "stableOutputDiffCount": sum(item["status"] != "PASS" for item in checked),
        "cases": checked,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = compare(args.before, args.after)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(result["status"], "stable output differences:", result["stableOutputDiffCount"])
    for item in result["cases"]:
        if item["firstDifference"] is not None:
            print(f"Case {item['case']}: {item['firstDifference']}")
    raise SystemExit(0 if result["status"] == "PASS" else 1)
