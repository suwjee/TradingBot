"""Compare original serialized bytes, replacing only top-level timing values."""
from __future__ import annotations
import argparse
import json
from matrix import EVIDENCE, calculation_arguments, file_sha, save


def stable_serialized_bytes(raw: bytes) -> bytes:
    """Retain whitespace, number/string lexemes, order and key presence exactly."""
    text = raw.decode("utf-8")
    decoder = json.JSONDecoder()
    index = 0

    def skip_space(position):
        while position < len(text) and text[position] in " \t\r\n":
            position += 1
        return position

    index = skip_space(index)
    if index == len(text) or text[index] != "{":
        raise ValueError("Bridge payload must be a JSON object")
    index = skip_space(index + 1)
    spans = []
    keys = set()
    while text[index] != "}":
        key, index = decoder.raw_decode(text, index)
        if not isinstance(key, str) or key in keys:
            raise ValueError("Duplicate/non-string top-level key cannot be normalized")
        keys.add(key)
        index = skip_space(index)
        if text[index] != ":":
            raise ValueError("Invalid member delimiter")
        start = skip_space(index + 1)
        _, end = decoder.raw_decode(text, start)
        if key == "timings":
            spans.append((start, end))
        index = skip_space(end)
        if text[index] == "}":
            break
        if text[index] != ",":
            raise ValueError("Invalid object delimiter")
        index = skip_space(index + 1)
    if text[skip_space(index + 1):]:
        raise ValueError("Trailing content after Bridge object")
    for start, end in reversed(spans):
        text = text[:start] + "null" + text[end:]
    return text.encode("utf-8")


def first_byte_difference(left, right):
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return {"offset": index, "before_byte": a, "after_byte": b}
    if len(left) != len(right):
        return {"offset": min(len(left), len(right)), "before_length": len(left), "after_length": len(right)}
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before-phase", default="repaired-before")
    parser.add_argument("--after-phase", default="after")
    args = parser.parse_args()
    cases = json.loads((EVIDENCE / "discovery/workloads.json").read_bytes())
    policy = json.loads((EVIDENCE / "discovery/collection-policy.json").read_bytes())["required_repeats"][args.after_phase]
    report = {"method": "Original stdout UTF-8 bytes, replacing only the complete top-level timings VALUE with literal null; all other bytes retained including whitespace/numeric lexemes/string escapes/key order", "comparisons": []}
    for case in cases:
        before = EVIDENCE / args.before_phase / case["id"] / "run-01.stdout.json"
        before_meta = json.loads(before.with_name("run-01.metrics.json").read_bytes())
        if before_meta["status"] != "PASS" or file_sha(before) != before_meta["raw_output_sha256"]:
            raise RuntimeError(f"Invalid baseline evidence: {before}")
        baseline = stable_serialized_bytes(before.read_bytes())
        for repeat in range(1, policy[case["id"]] + 1):
            path = EVIDENCE / args.after_phase / case["id"] / f"run-{repeat:02d}.stdout.json"
            meta_path = path.with_name(f"run-{repeat:02d}.metrics.json")
            if not path.exists() or not meta_path.exists():
                report["comparisons"].append({"case": case["id"], "after": str(path), "status": "INCOMPLETE", "reason": "Required completed repeat missing"})
                continue
            meta = json.loads(meta_path.read_bytes())
            if (meta["status"] != "PASS" or file_sha(path) != meta["raw_output_sha256"]
                    or meta["baseline_phase"] != args.before_phase
                    or meta["input_sha256_before"] != before_meta["input_sha256_before"]
                    or calculation_arguments(meta["command"]) != calculation_arguments(before_meta["command"])
                    or meta.get("explicit_hash_seed") != before_meta.get("explicit_hash_seed")):
                raise RuntimeError(f"Invalid completed candidate context: {path}")
            candidate = stable_serialized_bytes(path.read_bytes())
            difference = first_byte_difference(baseline, candidate)
            report["comparisons"].append({"case": case["id"], "before": str(before), "after": str(path), "status": "PASS" if difference is None else "FAIL", "first_byte_difference": difference})
    report["status"] = ("FAIL" if any(item["status"] == "FAIL" for item in report["comparisons"])
                        else "INCOMPLETE" if any(item["status"] != "PASS" for item in report["comparisons"])
                        else "PASS" if report["comparisons"] else "INCOMPLETE")
    save(EVIDENCE / f"discovery/lexical-{args.before_phase}-vs-{args.after_phase}.json", report)
    print(json.dumps({"status": report["status"], "comparisons": len(report["comparisons"]), "differences": sum(item["status"] == "FAIL" for item in report["comparisons"])}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
