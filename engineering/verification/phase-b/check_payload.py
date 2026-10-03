from pathlib import Path
import json

p = Path("engineering/verification/phase-b/baseline/USOIL-bearish-30s-full.json")
b = p.read_bytes()
t = b.decode("utf-16") if b[:2] == b"\xff\xfe" else b.decode("utf-8")
print("size", p.stat().st_size, "text_len", len(t))
print("starts", t[:150])
print("has_error_token", "error" in t[:200])
if t.startswith("{") and "error" in t[:200]:
    print(t[:300])
else:
    data = json.loads(t)
    bull = data.get("directions", {})
    print("directions", list(bull))
    for d, payload in bull.items():
        print(d, {k: (len(v) if isinstance(v, list) else type(v).__name__) for k, v in payload.items()})
