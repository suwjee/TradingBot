"""Synchronize discovered production Source without rewriting other reference prose."""
from __future__ import annotations
import ast
from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT/"engine"


def inventory():
    return sorted([ENGINE/"__init__.py", *(ENGINE/"bridge").rglob("*.py"),
                   *(ENGINE/"pipeline").rglob("*.py")],
                  key=lambda p:p.relative_to(ENGINE).as_posix().casefold())


def symbols(path):
    tree=ast.parse(path.read_bytes())
    lines=[f"#### `{path.relative_to(ENGINE).as_posix()}`"]
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            returns=" -> "+ast.unparse(node.returns) if node.returns else ""
            lines.append(f"- Function `{node.name}({ast.unparse(node.args)}){returns}` (L{node.lineno}-L{node.end_lineno}).")
        elif isinstance(node,ast.ClassDef):
            fields=[f"{part.target.id}: {ast.unparse(part.annotation)}" for part in node.body
                    if isinstance(part,ast.AnnAssign) and isinstance(part.target,ast.Name)]
            methods=[f"{part.name}({ast.unparse(part.args)})" for part in node.body
                     if isinstance(part,(ast.FunctionDef,ast.AsyncFunctionDef))]
            lines.append(f"- Class `{node.name}` (L{node.lineno}-L{node.end_lineno}).")
            if fields:lines.append("  - Fields: "+", ".join(f"`{v}`" for v in fields)+".")
            if methods:lines.append("  - Methods: "+", ".join(f"`{v}`" for v in methods)+".")
    return "\n".join(lines)+"\n"


RULES = """### 13.10 Approved bullish setup annotations (UNRELEASED)

This user-approved addition is bullish only. It produces chart schematics, T/F assessments and reference-break provenance; it does not execute, simulate, size, close or manage trades. Existing Reaction/Reset/Blue/A/S/E/StopAll/Order/primary formation remains authoritative and unchanged. `pipeline/bullish_setup_engine.py` owns these new calculations; the Bridge only projects their finalized results.

1. Consume native accepted full-history S/E/StopAll groups and logical primary-low cycle events. Confirmation events determine eligibility; retrospective source timestamps identify anchors and never substitute for confirmation. Keep independent cycle identity, overlapping StopAll ancestry and native S-donor resets. StopAll's native strict-stop event is inclusive of its confirmation RAW row. A successor must be strictly before the current stop to confirm T.
2. The initial StopAll-1 may draw a Buy schematic on its first confirmed S/E. Entry is the Close of the candle containing that confirmation; SL is the StopAll Low. Every accepted S/E family/color/number qualifies as a behavior.
3. The ONLY direct-StopAll-confirmation exception is StopAll-1 with a behavior, followed by its F outcome and confirmation of its StopAll-2. Draw that StopAll-2 schematic at its confirmation candle Close with its own Low as SL, without waiting for another S/E. Do not generalize this exception to 4/6 or ignored repeated-prefix candidates.
4. StopAll stopped after behavior becomes F; stopped without behavior remains T. Behavior alone never confirms F. A successor confirmed before the stop confirms T. Within the evaluated scope, F propagates through its parity immediately to new members and retrospectively to prior members, including earlier T labels. Inherited F still records its later actual stop. Failed behavior labels receive red F. Historical schematics are retained; no position lifecycle is inferred from their later classifications.
5. A later movement repeats the prior movement's full reached StopAll extent, including its F final member. Ignore that repeated prefix for new entry/parity decisions; begin independent examination at n+1. Maintain causal native predecessor sets rather than flattening interleaved StopAll numbering. The first confirmed T family has entry priority until it fails; the independently valid second family then becomes eligible. An ignored prefix's F cannot contaminate the fresh scope. Eligible later StopAlls wait for their first post-confirmation S/E and use its confirmation Close and their own Low.
6. Freeze H_ref as maximum High from the preceding PL confirmation candle through StopAll-1 confirmation candle, inclusive. Before any PL, use the bullish regime's initial candle as the start. Equality never crosses. Both evaluated parities F and a subsequent strict High > H_ref require a larger movement. New native StopAll numbering is not created by that reference break.
7. A larger StopAll examination beyond the repeated extent, or an eligible larger confirmed PL, can advance the movement. If PL arrives before the waiting StopAll entry, enter the PL phase. Wait for the first confirmed post-PL S/E; entry is its confirmation candle Close and SL is that PL Low. Advance PL numbers within a native cycle; retain independent cycles. For coincident physical PL roles already confirmed at the same instant, use the largest known logical number. A later role promotion cannot rewrite an earlier physical setup decision.
8. Initial R = Entry - SL must be positive; target = Entry + 4R using Decimal prices. Outputs contain `positionSetups`, `stopAllAssessments`, `behaviorAssessments`, `setupReferenceBreaks`, `setupPhase` and `setupVersion`. Entry candle time, actual confirmation event and candle-close event remain separate. Projected cycle IDs match absolute regime identities. Calculate before presentation clipping.
9. Chart presentation uses existing position geometry: initial width50 chart intervals, editable time span, independent TP/SL, green target/red stop at10% opacity, dynamic10px boxed R:R. These are indicator-owned objects and user edits are presentation overrides; they do not alter calculated levels or independent manual drawings. Source fingerprinting includes the new Engine module.

Verification evidence and reproduction helpers: `engineering/verification/bullish-setups-20261102/`. Market timestamps appear only in verification fixtures, never in production rules. Source/Reference fidelity, unit tests, scoped RAW acceptance and browser interaction are distinct evidence layers; no universal error-free result is claimed.

"""


def sync(path):
    original=path.read_bytes(); newline=b"\r\n" if b"\r\n" in original[:3000] else b"\n"
    text=original
    roles={m[1].decode():m[2].decode() for m in re.finditer(rb"\| `([^`]+\.py)` \| ([^|]+) \|",original)}
    roles["pipeline/bullish_setup_engine.py"]="Bullish setup annotations"
    stamp=datetime.now(timezone(timedelta(hours=3,minutes=30))).isoformat(timespec="seconds")
    table=["| Module | Owner | Version | Lines | Bytes | SHA-256 |","|---|---|---|---:|---:|---|"]
    blocks=[]
    for number,source in enumerate(inventory(),1):
        relative=source.relative_to(ENGINE).as_posix();raw=source.read_bytes()
        assert not raw or raw.endswith(b"\n"),relative
        tree=ast.parse(raw);versions={}
        for node in tree.body:
            if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant):
                for target in node.targets:
                    if isinstance(target,ast.Name) and target.id.endswith("_VERSION"):
                        versions[target.id]=str(node.value.value)
        primary=next((v for k,v in versions.items() if "IMPLEMENTATION" not in k),"unversioned")
        implementation=next((v for k,v in versions.items() if "IMPLEMENTATION" in k),None)
        version=primary+(f" (impl {implementation})" if implementation else "")
        role=roles.get(relative,"Production module").strip();digest=hashlib.sha256(raw).hexdigest()
        table.append(f"| `{relative}` | {role} | `{version}` | {raw.count(bytes([10]))} | {len(raw)} | `{digest}` |")
        header=(f"### 16.{number} `{relative}` — {role}\n\n**SHA-256:** `{digest}`  \n"
                f"**Bytes:** `{len(raw)}`  \n**LF count:** `{raw.count(bytes([10]))}`\n\n"
                f"<!-- EXACT-SOURCE-BEGIN:{relative} -->\n````python\n").encode().replace(b"\n",newline)
        footer=f"````\n<!-- EXACT-SOURCE-END:{relative} -->\n\n".encode().replace(b"\n",newline)
        blocks.append(header+raw+footer)
    table_start=text.index(b"| Module | Owner | Version | Lines | Bytes | SHA-256 |")
    table_end=text.index(b"Generated Source-inventory evidence",table_start)
    text=text[:table_start]+("\n".join(table)+"\n\n").encode().replace(b"\n",newline)+text[table_end:]
    text=re.sub(rb"Generated Source-inventory evidence at `[^`]+`",f"Generated Source-inventory evidence at `{stamp}`".encode(),text,count=1)
    start=text.index(b"### 13.5 ");end=text.index(b"### 13.6 ",start)
    coverage="### 13.5 Complete module/class symbol and schema coverage\n\nGenerated from current production AST; implementation bodies remain exact in Section16.\n\n"+"\n".join(symbols(p) for p in inventory())+"\n"
    text=text[:start]+coverage.encode().replace(b"\n",newline)+text[end:]
    if b"### 13.10 Approved bullish setup annotations" not in text:
        at=text.index(b"## 14. ")
        text=text[:at]+RULES.encode().replace(b"\n",newline)+text[at:]
    start=text.index(b"## 16. Exact Production Source snapshot")
    body=text.index(b"### 16.1 ",start);end=text.index(b"## 17. ",body)
    text=text[:body]+b"".join(blocks)+text[end:]
    if b"### Current local addition - bullish setup annotations" not in text:
        at=text.index(b"### ",text.index(b"## 0. Revision scope"))
        revision=("### Current local addition - bullish setup annotations (UNRELEASED)\n\n"
                  "The approved bullish chart-schematic rules are implemented by the new setup Engine stage; see Section13.10. Native detector outputs retain their existing authority. This addition does not execute or simulate trades and has no authorized bearish setup mirror.\n\n")
        text=text[:at]+revision.encode().replace(b"\n",newline)+text[at:]
    scope=re.search(rb"\*\*scope:\*\* `([^`]+)`",text)
    if scope and b"bullish setup annotations" not in scope[1]:
        text=text[:scope.start(1)]+scope[1]+b"; bullish setup annotations"+text[scope.end(1):]
    for label in [b"Last Modified",b"last_modified_at"]:
        text=re.sub(rb"\*\*"+label+rb":\*\* `[^`]+`",b"**"+label+b":** `"+stamp.encode()+b"`",text,count=1)
    assert path.read_bytes()==original,"Reference changed concurrently"
    path.write_bytes(text)
    print(path.name,len(blocks),"exact production files")


if __name__=="__main__":
    for reference in sorted((ENGINE/"algorithms").glob("*Source_Synchronized.md")):
        sync(reference)
