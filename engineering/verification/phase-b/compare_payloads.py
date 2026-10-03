"""Compare two pipeline payloads for semantic equality, ignoring timings."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def load(path: Path):
    b = path.read_bytes()
    if b[:2] == b"\xff\xfe":
        text = b.decode("utf-16")
    elif b[:2] == b"\xfe\xff":
        text = b.decode("utf-16-be")
    else:
        text = b.decode("utf-8")
    return json.loads(text)


def main() -> int:
    a_path = Path(sys.argv[1])
    b_path = Path(sys.argv[2])
    a = load(a_path)
    b = load(b_path)
    a.pop("timings", None)
    b.pop("timings", None)
    equal = a == b
    print("semantic_equal", equal)
    if equal:
        return 0
    for key in sorted(set(a) | set(b)):
        if a.get(key) != b.get(key):
            print("TOP_DIFF", key)
            if key == "directions":
                for d in sorted(set(a.get(key, {})) | set(b.get(key, {}))):
                    pa = a.get(key, {}).get(d, {})
                    pb = b.get(key, {}).get(d, {})
                    for ck in sorted(set(pa) | set(pb)):
                        va, vb = pa.get(ck), pb.get(ck)
                        if va != vb:
                            la = len(va) if isinstance(va, list) else type(va).__name__
                            lb = len(vb) if isinstance(vb, list) else type(vb).__name__
                            print(" ", d, ck, la, lb)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
