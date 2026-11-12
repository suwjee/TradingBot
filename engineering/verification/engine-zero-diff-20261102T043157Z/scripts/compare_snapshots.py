"""Compare every native snapshot directly, including ordered fields and aliases."""
from __future__ import annotations
import argparse
import gzip
import json
from matrix import EVIDENCE, first_diff, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("before_phase")
    parser.add_argument("after_phase")
    parser.add_argument("case")
    args = parser.parse_args()
    directories = [EVIDENCE / phase / "snapshot" / args.case for phase in (args.before_phase, args.after_phase)]
    indexes = [json.loads((directory / "snapshot-index.json").read_bytes()) for directory in directories]
    statuses = [json.loads((directory / "metadata.json").read_bytes()) for directory in directories]
    result = {"case": args.case, "before": str(directories[0]), "after": str(directories[1]), "stages": []}
    first = first_diff(indexes[0], indexes[1])
    if first:
        result.update({"status": "FAIL", "first_difference": first})
    elif not all(item["status"] == "PASS" and item.get("stable_bytes_equal_to_cli") for item in statuses):
        result.update({"status": "FAIL", "reason": "Native collection did not reproduce normal CLI output"})
    else:
        for item in indexes[0]:
            raw = [gzip.decompress((directory / item["path"]).read_bytes()) for directory in directories]
            difference = first_diff(json.loads(raw[0]), json.loads(raw[1]))
            result["stages"].append({"index": item["index"], "stage": item["stage"], "bytes_equal": raw[0] == raw[1],
                                     "typed_ordered_content_equal": difference is None, "first_difference": difference})
        equal = all(item["bytes_equal"] and item["typed_ordered_content_equal"] for item in result["stages"])
        result.update({"status": "PASS" if equal else "FAIL", "stable_difference_count": 0 if equal else None})
    path = directories[1] / "native-comparison.json"
    save(path, result)
    print(json.dumps({"case": args.case, "status": result["status"], "stages": len(result["stages"]), "report": str(path)}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
