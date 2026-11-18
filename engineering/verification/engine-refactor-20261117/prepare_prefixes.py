"""Derive bounded fixtures by slicing original JSON bytes, preserving price lexemes."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
INPUTS = ROOT / "apps/chart/state/tmp/engine-refactor-20261117/inputs"


def main():
    records = []
    decoder = json.JSONDecoder(parse_float=Decimal)
    for symbol in ("USOIL", "XAUUSD"):
        source = (INPUTS / (symbol + "-full.json")).read_bytes()
        bom = 3 if source.startswith(b"\xef\xbb\xbf") else 0
        text = source[bom:].decode("utf-8")
        position = text.index("[") + 1
        rows = []
        for index in range(8000):
            while text[position].isspace() or text[position] == ",":
                position += 1
            row, position = decoder.raw_decode(text, position)
            rows.append(row)
        boundary = bom + len(text[:position].encode("utf-8"))
        fixture = source[:boundary] + b"]"
        parsed = json.loads(fixture.removeprefix(b"\xef\xbb\xbf"), parse_float=Decimal)
        assert repr(parsed) == repr(rows)
        target = INPUTS / (symbol + "-8000.json")
        target.write_bytes(fixture)
        records.append(dict(symbol=symbol, rows=8000, source_sha256=hashlib.sha256(source).hexdigest(),
                            fixture_sha256=hashlib.sha256(fixture).hexdigest(),
                            derivation="Exact original JSON byte prefix through row8000, followed only by closing bracket"))
    (EVIDENCE / "prefix-fixtures.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print("PASS two8000-row prefixes preserve original price lexemes byte-for-byte")


if __name__ == "__main__":
    main()
