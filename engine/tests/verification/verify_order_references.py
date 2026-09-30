"""Verify current directional references against every exact Engine Python file."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "engine"
PATTERN = re.compile(rb"<!-- EXACT-SOURCE-BEGIN:([^\r\n]+) -->\r?\n````python\r?\n(.*?)````\r?\n<!-- EXACT-SOURCE-END:\1 -->", re.DOTALL)

def verify(path: Path) -> int:
    content = path.read_bytes()
    matches = list(PATTERN.finditer(content))
    actual_paths = {source.relative_to(ENGINE).as_posix(): source
                    for source in [ENGINE / "__init__.py", *sorted((ENGINE / "bridge").rglob("*.py")), *sorted((ENGINE / "pipeline").rglob("*.py"))] if "__pycache__" not in source.parts}
    embedded_paths = [match[1].decode("utf-8") for match in matches]
    assert len(embedded_paths) == len(set(embedded_paths)), f"Duplicate embedded source: {path}"
    assert set(embedded_paths) == set(actual_paths), f"Embedded inventory differs: {path}"
    for match in matches:
        relative, embedded = match[1].decode("utf-8"), match[2]
        actual = actual_paths[relative].read_bytes()
        assert embedded == actual, f"Exact source bytes differ: {relative}"
        section = content[content.rfind(b"### 16.", 0, match.start()):match.start()]
        declared = re.search(rb"\*\*SHA-256:\*\* `([a-f0-9]{64})`", section)
        size = re.search(rb"\*\*Bytes:\*\* `(\d+)`", section)
        lines = re.search(rb"\*\*LF count:\*\* `(\d+)`", section)
        assert declared and declared[1].decode() == hashlib.sha256(actual).hexdigest(), relative
        assert size and int(size[1]) == len(actual), relative
        assert lines and int(lines[1]) == actual.count(b"\n"), relative
        compile(embedded.decode("utf-8-sig"), relative, "exec", dont_inherit=True)
    return len(matches)

if __name__ == "__main__":
    paths = sorted((ENGINE / "algorithms").glob("*Source_Synchronized.md"))
    directions = [re.search(rb"\*\*Target Direction:\*\* `([^`]+)`", path.read_bytes())[1].decode().casefold()
                  for path in paths]
    assert sorted(directions) == ["bearish", "bullish"], "Unique current directional references are required"
    print(json.dumps({path.name: verify(path) for path in paths}, indent=2))
