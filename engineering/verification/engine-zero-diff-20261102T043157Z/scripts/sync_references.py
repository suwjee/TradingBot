"""Synchronize implementation evidence only; never rewrite trading teaching."""
from __future__ import annotations
import ast
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

EVIDENCE = Path(__file__).resolve().parents[1]
ROOT = EVIDENCE.parents[2]
ENGINE = ROOT / "engine"
PATTERN = re.compile(rb"<!-- EXACT-SOURCE-BEGIN:([^\r\n]+) -->\r?\n````python\r?\n(.*?)````\r?\n<!-- EXACT-SOURCE-END:\1 -->", re.S)


def main():
    # Reuse only the previously maintained AST index formatter, never its old
    # semantic-migration/main routines. Current Source supplies every value.
    helper = ROOT / "engineering/verification/bullish-transition-2026-11-01/sync_references.py"
    spec = importlib.util.spec_from_file_location("historical_index_formatter", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    initial = {row["path"].removeprefix("engine/"): row["sha256"] for row in json.loads((EVIDENCE / "discovery/source-manifest-before.json").read_bytes())}
    paths = [ENGINE / "__init__.py", *sorted((ENGINE / "bridge").rglob("*.py")), *sorted((ENGINE / "pipeline").rglob("*.py"))]
    sources = {path.relative_to(ENGINE).as_posix(): path.read_bytes() for path in paths}
    changed = {relative: data for relative, data in sources.items() if hashlib.sha256(data).hexdigest() != initial.get(relative)}
    assert changed, "No implementation changes to synchronize"
    stamp = datetime.now(ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds")
    for reference in sorted((ENGINE / "algorithms").glob("*Source_Synchronized.md")):
        data = reference.read_bytes()
        text = data.decode("utf-8")
        for relative, raw in changed.items():
            source = raw.decode("utf-8")
            digest = hashlib.sha256(raw).hexdigest()
            pattern = re.compile(r"(<!-- EXACT-SOURCE-BEGIN:"+re.escape(relative)+r" -->\r?\n````python\r?\n)(.*?)(````\r?\n<!-- EXACT-SOURCE-END:"+re.escape(relative)+r" -->)", re.S)
            text, count = pattern.subn(lambda match: match[1] + source + match[3], text)
            assert count == 1, (reference, relative, count)
            begin = text.index(f"<!-- EXACT-SOURCE-BEGIN:{relative} -->")
            metadata_start = text.rfind("**SHA-256:**", 0, begin)
            text = text[:metadata_start]+f"**SHA-256:** `{digest}`  \n**Bytes:** `{len(raw)}`  \n**LF count:** `{raw.count(bytes([10]))}`\n\n"+text[begin:]
            versions = dict(re.findall(r'(?m)^(\w+VERSION) = "([^"]+)"', source))
            api = next((value for key,value in versions.items() if "IMPLEMENTATION" not in key), "unversioned")
            impl = next((value for key,value in versions.items() if "IMPLEMENTATION" in key), None)
            version = api + (f" (impl {impl})" if impl and impl != api else "")
            row_pattern = r"(\| `"+re.escape(relative)+r"` \| [^|]+ \| )`[^`]+` \| \d+ \| \d+ \| `[0-9a-f]+` \|"
            text, count = re.subn(row_pattern, lambda match: match[1]+f"`{version}` | {len(source.splitlines())} | {len(raw)} | `{digest}` |", text)
            assert count == 1, (reference, relative, count)
            index_start = text.index(f"#### `{relative}`", text.index("### 13.5"))
            following = text.find("\n#### `", index_start+1)
            section_end = text.find("\n## ", index_start+1)
            finish = min(position for position in [following, section_end] if position >= 0)
            text = text[:index_start]+module.index_block(relative, source)+text[finish+1:]
        text = re.sub(r"(?m)^(\*\*(?:Last Modified|last_modified_at):\*\* `)[^`]+", lambda match: match[1]+stamp, text)
        marker_start, marker_end = "<!-- ENGINE-AUDIT-IMPLEMENTATION-BEGIN -->", "<!-- ENGINE-AUDIT-IMPLEMENTATION-END -->"
        note = f"""{marker_start}
### Current Engine implementation audit (UNRELEASED)

- **Preparatory serialization repair:** the merged multi-regime Bridge projection preserves first-appearance field order using an ordered key collector. This removes process-hash-dependent mapping order; calculation values, types, Decimal strings, physical identities, provenance and arrays are unchanged by this repair. Public API version fields remain unchanged.
- **Implementation-only optimization:** the carried-Order query reuses its eagerly extracted parent creation list, reduces multiple parents to their original earliest event and appends every B confirmation eagerly. This reduces redundant temporary allocation and generator work without changing native selection, time boundaries, error precedence, Order identity, cache validity, result order or public output. No new retained cache or trading rule is introduced.
- **Authority:** the user delegated this separately disclosed repair after the original exact baseline exposed two mapping-order failures. The original failed baseline is preserved; it is not relabeled zero-difference. Optimization, if retained, must compare against a separately named stable post-repair baseline.
- **Evidence:** `engineering/verification/engine-zero-diff-20261102T043157Z/` contains original outputs, first differences, independent review and actual test/measurement records. No release/publication is claimed. Final optimization/RAW status must be read from that run's final report, not inferred from Source synchronization.
- **Source synchronization timestamp:** `{stamp}`. Only implementation evidence and exact embedded Source/index/manifest representation are synchronized here; existing trading-rule text and pre-existing documented ambiguities remain unchanged.
{marker_end}

"""
        if marker_start in text:
            left, right = text.index(marker_start), text.index(marker_end)+len(marker_end)
            text = text[:left]+note.rstrip()+text[right:]
        else:
            position = text.index("### Current local extension")
            text = text[:position]+note+text[position:]
        reference.write_bytes(text.encode("utf-8"))
        print(f"{reference.name}: synchronized {list(changed)}")


if __name__ == "__main__":
    main()
