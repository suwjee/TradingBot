"""Compare original calculation content; allow only the disclosed key-order delta."""
from __future__ import annotations
import gzip
import json
import re
from matrix import EVIDENCE, save
from diagnose_determinism import differences


def main():
    cases = json.loads((EVIDENCE / "discovery/workloads.json").read_bytes())
    report = {"comparison": "Original BEFORE versus repaired-before run01; all typed values and ordered arrays preserved", "cases": []}
    for case in cases:
        paths = [EVIDENCE / phase / case["id"] / "run-01.stable.json.gz" for phase in ("before", "repaired-before")]
        if not paths[1].exists():
            report["cases"].append({"case": case["id"], "status": "NOT RUN", "reason": "Repaired baseline still collecting"})
            continue
        raw = [gzip.decompress(path.read_bytes()) for path in paths]
        found = differences(json.loads(raw[0]), json.loads(raw[1]))
        allowed = [item for item in found if item["kind"] == "mapping-key-order" and re.fullmatch(r"\$\.directions\.(bullish|bearish)\.bridgeOutput", item["path"])]
        unexpected = [item for item in found if item not in allowed]
        report["cases"].append({"case": case["id"], "status": "PASS" if not unexpected else "FAIL", "raw_stable_bytes_equal": raw[0] == raw[1],
                                 "approved_mapping_order_differences": allowed, "unexpected_difference_count": len(unexpected), "unexpected_differences": unexpected})
    report["status"] = "PASS" if all(item["status"] == "PASS" for item in report["cases"]) else "FAIL" if any(item["status"] == "FAIL" for item in report["cases"]) else "INCOMPLETE"
    save(EVIDENCE / "discovery/preparatory-repair-comparison.json", report)
    print(json.dumps({"status": report["status"], "cases": len(report["cases"]), "completed": sum(item["status"] == "PASS" for item in report["cases"]),
                      "unexpected_differences": sum(item.get("unexpected_difference_count", 0) for item in report["cases"])}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
