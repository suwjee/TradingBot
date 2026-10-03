"""Normalize Phase B payloads to UTF-8 and run verify_order_b_raw."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "engine" / "tests" / "verification"))
from verify_order_b_raw import verify  # noqa: E402


def load_text(path: Path) -> str:
    b = path.read_bytes()
    if b[:2] == b"\xff\xfe":
        return b.decode("utf-16")
    if b[:2] == b"\xfe\xff":
        return b.decode("utf-16-be")
    if b[:3] == b"\xef\xbb\xbf":
        return b.decode("utf-8-sig")
    return b.decode("utf-8")


def main() -> int:
    raw_usoil = ROOT / "apps/chart/state/data/RAW/BaseLine/RAW FXCM_USOIL 5S FROM 2026-08-21 04-00-00 TO 2026-09-29 11-46-20.json"
    raw_xau = ROOT / "apps/chart/state/data/RAW/BaseLine/RAW FOREXCOM_XAUUSD 5S FROM 2026-08-25 03-53-30 TO 2026-09-23 18-01-15.json"
    cases = [
        (
            raw_usoil,
            ROOT / "engineering/verification/phase-a-repro-ustoil-bullish-30s-after.json",
            30,
            "USOIL-bullish",
        ),
        (
            raw_usoil,
            ROOT / "engineering/verification/phase-b/baseline/USOIL-bearish-30s-full.json",
            30,
            "USOIL-bearish",
        ),
        (
            raw_xau,
            ROOT / "engineering/verification/phase-a-baseline-post/XAUUSD-bullish-30s-full.json",
            30,
            "XAUUSD-bullish",
        ),
    ]
    out_dir = ROOT / "engineering/verification/phase-b/baseline/utf8"
    out_dir.mkdir(parents=True, exist_ok=True)
    for raw, payload, tf, label in cases:
        if not payload.exists():
            print(label, "MISSING PAYLOAD")
            continue
        text = load_text(payload)
        utf8_path = out_dir / f"{label}.json"
        utf8_path.write_text(text, encoding="utf-8")
        try:
            counts = verify(raw, utf8_path, tf)
            print(label, "PASS", counts)
        except Exception as exc:
            print(label, "FAIL", type(exc).__name__, exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
