"""Regenerate complete exact Source evidence and the approved removal contract."""
from __future__ import annotations
import ast
from datetime import datetime
import hashlib
from pathlib import Path
import re
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "engine"


def index_block(relative, source):
    tree = ast.parse(source)
    lines = [f"#### `{relative}`"]
    def visit(node, prefix=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines.append(f"- Function `{prefix}{child.name}({ast.unparse(child.args)})` (L{child.lineno}-L{child.end_lineno}).")
                visit(child, prefix + child.name + ".")
            elif isinstance(child, ast.ClassDef):
                lines.append(f"- Class `{prefix}{child.name}` (L{child.lineno}-L{child.end_lineno}).")
                visit(child, prefix + child.name + ".")
            elif isinstance(child, (ast.Assign, ast.AnnAssign)) and isinstance(node, (ast.Module, ast.ClassDef)):
                lines.append(f"- Assignment `{ast.unparse(child)}` (L{child.lineno}).")
            else:
                visit(child, prefix)
    visit(tree)
    return "\n".join(lines) + "\n\n"


def main():
    paths = [ENGINE / "__init__.py", *sorted((ENGINE / "bridge").rglob("*.py")), *sorted((ENGINE / "pipeline").rglob("*.py"))]
    paths = [p for p in paths if "__pycache__" not in p.parts]
    sources = {p.relative_to(ENGINE).as_posix(): p.read_bytes() for p in paths}
    stamp = datetime.now(ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds")
    for reference in sorted((ENGINE / "algorithms").glob("*Source_Synchronized.md")):
        text = reference.read_bytes().decode("utf-8")
        owners = dict(re.findall(r"(?m)^\| `([^`]+)` \| ([^|]+) \|", text))
        manifest = ["## 1. Source manifest", "", "| Module | Owner | Version | Lines | Bytes | SHA-256 |", "|---|---|---|---:|---:|---|"]
        snapshots, indexes = [], []
        for number, (relative, raw) in enumerate(sources.items(), 1):
            source = raw.decode("utf-8")
            versions = dict(re.findall(r'(?m)^(\w+VERSION) = "([^"]+)"', source))
            api = next((v for k, v in versions.items() if "IMPLEMENTATION" not in k), "unversioned")
            impl = next((v for k, v in versions.items() if "IMPLEMENTATION" in k), None)
            version = api + (f" (impl {impl})" if impl and impl != api else "")
            digest = hashlib.sha256(raw).hexdigest()
            owner = owners.get(relative, "Production module").strip()
            manifest.append(f"| `{relative}` | {owner} | `{version}` | {len(source.splitlines())} | {len(raw)} | `{digest}` |")
            indexes.append(index_block(relative, source))
            snapshots.append(f"### 16.{number} `{relative}` — {owner}\n\n**SHA-256:** `{digest}`  \n**Bytes:** `{len(raw)}`  \n**LF count:** `{raw.count(bytes([10]))}`\n\n<!-- EXACT-SOURCE-BEGIN:{relative} -->\n````python\n{source}````\n<!-- EXACT-SOURCE-END:{relative} -->\n")
        manifest += ["", f"Generated Source-inventory evidence at `{stamp}`. Recursive live production discovery includes package markers and all production Python under Bridge and Pipeline; tests, historical archives and caches are excluded. The observed inventory is evidence, not a permanent ownership list.", "", "Section 16 embeds the exact bytes represented by this manifest.", ""]
        start, end = text.index("## 1. Source manifest"), text.index("## 2. Authoritative pipeline")
        text = text[:start] + "\n".join(manifest) + "\n" + text[end:]
        start, end = text.index("### 13.5 "), text.index("### 13.6 ")
        text = text[:start] + "### 13.5 Complete module/class symbol and schema coverage\n\n" + "".join(indexes) + text[end:]
        start, end = text.index("### 13.10 "), text.index("## 14. Verification scope")
        text = text[:start] + """### 13.10 Removed assessment and trading-position extension

The current explicit user instruction removes automatic T/F assessments, reference-break assessment and trading-position setup calculation. The six former public direction fields (`setupVersion`, `setupPhase`, `positionSetups`, `stopAllAssessments`, `behaviorAssessments`, `setupReferenceBreaks`) are absent, including independent calculation segments. The standalone setup module and live stage are removed. No future assessment/entry rule is inferred.

Native Reaction/Reset/Blue/A/S/E/StopAll, physical Order/OrderAudit, primary structures and ordinary Boolean validity flags retain their existing calculation contracts. Chart manual Long/Short tools and Manual Review verdict choices are also removed under the same explicit instruction; they never define native indicator calculation.

Implementation-only optimizations preserve the post-removal baseline: exact Decimal values/representations, strict boundaries, first-equal sources, physical identity, provenance, lifecycle and stable serialization order. Evidence and measured limitations belong to `engineering/verification/engine-refactor-20261117/`; former setup verification remains Historical evidence.

""" + text[end:]
        local_heading = ("### Current local addition - bullish setup annotations"
                         if "### Current local addition - bullish setup annotations" in text
                         else "### Current local change - assessment removal and implementation refactor")
        start = text.index(local_heading)
        end = text.index("### Current local correction", start)
        text = text[:start] + """### Current local change - assessment removal and implementation refactor (UNRELEASED)

The user removes all automatic T/F and trading-position setup behavior; Section 13.10 defines the removed public fields. Manual Long/Short and Manual Review verdict controls are removed in Chart. Native calculation remains governed by the existing accepted rules. The separate optimization compares against a frozen post-removal baseline; no historical whole-project rollback is performed. Fresh verification, direct equality, runtime and peak-memory measurements are recorded under `engineering/verification/engine-refactor-20261117/`.

""" + text[end:]
        text = re.sub(r"(?m)^(\*\*(?:Last Modified|last_modified_at):\*\* `)[^`]+", lambda m: m[1] + stamp, text)
        text = text.replace("; bullish setup annotations`", "; assessment and position extension removed`")
        text = text.replace("### Current Engine implementation audit (UNRELEASED)",
                            "### Earlier Engine implementation audit (2026-11-02; HISTORICAL)")
        text = re.sub(r"(?m)^\*\*Status:\*\*.*$", "**Status:** `ACTIVE SOURCE-SYNCHRONIZED LOCAL CHANGE — assessments/positions removed; implementation refactor; UNRELEASED`  ", text)
        text = re.sub(r"(?m)^\*\*Production Source Behavioral Change:\*\*.*$", "**Production Source Behavioral Change:** `YES — assessment and trading-position extension removed; subsequent optimization preserves the post-removal baseline`  ", text)
        text = text[:text.index("## 16. Exact Production Source snapshot")] + "## 16. Exact Production Source snapshot\n\nEvery discovered production Python file in the live Engine package, Bridge and Pipeline is embedded byte-for-byte. Reconstruct by the exact-source markers; do not reformat source. Sections 1 and 13.5 derive from this same live set.\n\n" + "\n".join(snapshots)
        reference.write_bytes(text.encode("utf-8"))
        print(reference.name, "synchronized", len(sources), "production files")


if __name__ == "__main__":
    main()
