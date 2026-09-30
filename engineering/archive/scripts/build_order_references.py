"""Build standalone directional references from current Engine source."""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
ALGORITHMS = ENGINE / "algorithms"
MODULES = (
    "pipeline/reaction_engine.py",
    "pipeline/blue_line_detector.py",
    "pipeline/a_zone_detector.py",
    "pipeline/s_zone_detector.py",
    "pipeline/e_zone_detector.py",
    "pipeline/order_audit_engine.py",
    "pipeline/lifecycle_engine.py",
    "bridge/trading_pipeline.py",
    "pipeline/direction_policy.py",
    "pipeline/core_utils.py",
)


def section(source: str, number: int) -> str:
    pattern = re.compile(rf"(?ms)^## {number}\. .*?(?=^## {number + 1}\. )")
    match = pattern.search(source)
    if match is None:
        raise ValueError(f"Missing section {number} in template reference")
    return match.group().rstrip() + "\n\n"


def source_metadata(relative: str) -> tuple[str, int, int, int, str, str, str]:
    data = (ENGINE / relative).read_bytes()
    decoded = data.decode("utf-8")
    tree = ast.parse(decoded)
    classes = sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
    functions = sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(tree))
    version = next(
        (match.group(1) for match in re.finditer(
            r'^\w+_VERSION = "([^"]+)"', decoded, re.MULTILINE
        )),
        "not declared",
    )
    implementation = next(
        (match.group(1) for match in re.finditer(
            r'^\w+_IMPLEMENTATION_VERSION = "([^"]+)"', decoded, re.MULTILINE
        )),
        version,
    )
    return (
        hashlib.sha256(data).hexdigest(), len(decoded.splitlines()),
        classes, functions, version, implementation, decoded,
    )


def build(direction: str, version: str, output: Path) -> None:
    opposite = "bearish" if direction == "bullish" else "bullish"
    title = direction.title()
    old = (
        ALGORITHMS /
        f"TradingBot_{title}_Algorithm_Reference_V5.4.13_HPZR1_OrderAB.md"
    ).read_text(encoding="utf-8")
    clock = datetime.now(ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S %z")
    clock = clock[:-2] + ":" + clock[-2:]
    metadata = [(relative, source_metadata(relative)) for relative in MODULES]
    manifest = "\n".join(
        f"| `{relative}` | `{meta[4]}` | `{meta[5]}` | {meta[1]} | {meta[2]} | {meta[3]} | `{meta[0]}` |"
        for relative, meta in metadata
    )
    introduction = f"""# TradingBot {title} Algorithm Reference — Standalone Order_A and Order_B Contract

**Document Version:** `{version}`  
**Last Modified Date & Time:** `{clock}`  
**Status:** `Phase 2 implementation-only refactor of the verified Phase 1 Order_A/B contract.`  
**Behavior Changes:** `NONE`  
**Algorithm Changes:** `NONE`  
**Target Direction:** `{direction}`  
**Opposite Physical Order Direction:** `{opposite}`  
**Internal Timezone:** `Asia/Tehran`  
**Validation Main Timeframe:** `30 seconds`; the production rule does not hardcode it.

This reference contains the complete current production source as an appendix. Its semantic text defines intended behavior; the embedded source records the executable implementation. If they disagree, stop and report the mismatch. The Phase 1 reference is the fixed behavior baseline; historical Order_A-only references and archives do not define current Order_B behavior.

## 0. Authority, scope and invariants

- A, S, E and StopAll are behaviors. Reaction, Reset, Blue, Order_A, Order_B and OrderAudit are calculation or provenance objects.
- Price comparisons use `Decimal`; strict `<` and `>` exclude equality.
- The selected physical RAW file supplies the entire lower-timeframe chronology. A Bridge call with a 5-second RAW input uses that same 5-second file even when an overlapping 1-second file exists elsewhere.
- Full selected RAW is calculation scope; the requested from/to range is presentation scope.
- Physical Order identity is `(FirstIndex, BreakIndex)`. Native Reaction Mode A/B is independent of Order_A/Order_B creation type.
- The public identity and exact chronology rules are shared between Bullish and Bearish. Price fields and strict comparators mirror explicitly; behavior priority and family colors do not mirror.
- Order_A is created by an accepted parent strict stop. Order_B is created by a valid post-stop Reset leg and a later valid opposite Reaction. A physical Order may carry both causes.
- `carried-live` and `accepted-live` are Order use routes, not creation causes.

## 1. Production module inventory and exact hashes

| Module | Runtime contract version | Implementation version | Lines | Classes | Functions/methods | SHA-256 |
|---|---|---|---:|---:|---:|---|
{manifest}

The {len(MODULES)} source blocks in the appendix are embedded without edits. Line counts and hashes refer to the files in the current Engine checkout at generation time. Runtime contract versions remain unchanged so serialized output remains identical; implementation versions identify the refactor in source and this reference.

## 2. Stage order and calculation boundary

`RAW normalization → both-direction Reaction/Reset → Internal-Reaction ownership → Blue → A → S → E/Order_A → accepted lifecycle → dominant post-stop Order_B → Order feedback reconciliation → StopAll → visibility → OrderAudit → serialization`.

The feedback calculation repeats accepted S/E/StopAll state only while proven Order_B causes change. Reaction/Reset and initial Blue/A/S geometry are fixed for the selected RAW. A nonconvergent feedback sequence fails explicitly. The bridge orchestrates these stages; it does not derive trading geometry or create an Order in serialization.

The architecture now assigns Reaction/Reset to `reaction_engine.py`, Blue to `blue_line_detector.py`, A to `a_zone_detector.py`, S formation to `s_zone_detector.py`, E formation to `e_zone_detector.py`, lifecycle/StopAll to `lifecycle_engine.py`, and physical Order creation, reuse, strict stop lookup, causes, and OrderAudit preparation to `order_audit_engine.py`. `trading_pipeline.py` retains orchestration and serialization projection. The E and S detectors inherit narrow Order methods from the dedicated module; `resolve_order_context` remains lifecycle-owned because it arbitrates behavior eligibility. The Vite source fingerprint includes the new Order module and shared primitives.

"""
    unchanged = "".join(section(old, number) for number in range(3, 10))
    unchanged = unchanged.replace(
        "There is no Order-type-specific Internal-Reaction filter in the Current Order_A-only model.",
        "Internal-Reaction evidence remains available where the owning calculation stage permits it.",
    )
    unchanged = unchanged.replace(
        "An already accepted physical Order_A may participate in an S decision through shared accepted-Order chronology when its confirmation/strict stop window satisfies the S rule. `accepted-live` and `carried-live` describe use of an existing Order_A only; they do not alter, replace, or invent its original `parent-stop` creation provenance. Arbitrary opposite Reactions that were never accepted as physical Order_A objects cannot be promoted by this route.",
        "An already accepted physical Order_A or Order_B may participate in an S decision through shared accepted-Order chronology when its confirmation and strict stop window satisfies the S rule. `accepted-live` and `carried-live` describe use of an existing physical Order; they preserve its original creation causes. Arbitrary opposite Reactions that were never accepted as a physical Order cannot be promoted by this route.",
    )
    order_section = f"""## 10. E and Order engines — {title}

### 10.1 Order_A retained

The accepted A/S/E/StopAll parent strict stop can create one parent-stop Order_A under the existing direct geometric gate. The first eligible canonical opposite Reaction owns that exact parent-stop cause. The S bounded and E fresh-trend search allowances remain existing subroutes. An exact parent-stop cannot be consumed by two identities. Existing Order_A confirmation, stop, ownership and geometry are unchanged by the new Order_B rule.

### 10.2 Dominant post-stop space

Order_B can form only after the strict stop of a calculation-accepted A, S, E or StopAll that owns the dominant lifecycle transition. At each stop, the accepted behavior active under the fixed priority `StopAll > E Red > S Red > E Blue > S Blue > A` owns the transition. For multiple accepted stops in one main candle, use the current lifecycle priority, number and source tie rules. A still-active stronger behavior prevents a weaker stopped behavior from opening an Order_B space. The next dominant post-stop transition or next calculation-accepted A formation closes the current search window. A candidate incomplete at the next A formation expires permanently.

### 10.3 Same-direction Reaction pair and Reset

Within that post-stop window, the current `{title}` Reaction must be valid and Reset at its exact lower-timeframe Reset event. When the Reaction engine records `second_time`, use it. When it records only the main-candle display time, resolve the Reset to the first strict crossing of `broken_level` inside that Reset main candle from the selected RAW. A Reset with no provable selected-RAW crossing is ineligible for Order_B. Choose the immediately preceding valid `{title}` Reaction by strict confirmation chronology. Both Reaction confirmations occur after the dominant stop; the previous confirms before the current, and the current confirms before its Reset. A later valid preceding Reaction replaces an earlier one for this pair. No fixed timestamp, symbol, candle fingerprint or fixture determines the pair.

### 10.4 Inclusive leg boundary

The main-candle range begins at the Previous Reaction Breakout candle and ends at the current Reset Reaction Breakout candle, both inclusive. For Bullish, the boundary is the minimum Low; for Bearish, the maximum High. Equal extreme prices retain the first source main candle, matching current source tie selection. Record the boundary value, source index and source time.

### 10.5 Strict break and opposite Reaction

After the exact Reset event, the selected RAW must first cross the leg boundary strictly: Bullish requires `Low < leg floor`; Bearish requires `High > leg ceiling`. Equality does not cross. A crossing at the same lower candle timestamp as the Reset cannot prove `Reset < break`. The first valid opposite Reaction after that crossing is the physical Order_B. Its **First main candle start time** must be strictly later than the exact break event, including when confirmation occurs in a later main candle. An opposite First in the break's own 30-second candle is invalid. Its confirmation must occur before the next calculation-accepted A formation and before the next dominant post-stop transition.

### 10.6 Physical stop, identity and reuse

Order_B uses the same `MarketChronology.canonical_order_stop` as any physical Order, selected by the opposite Reaction's native Mode A/B and canonical reaction number. Its strict stop event is determined on the selected RAW input. The physical identity is `(FirstIndex, BreakIndex)`; multiple valid Reset-leg sequences leading to the same identity merge onto one OrderAudit row. If Order_A and Order_B share that identity, both creation causes remain. E and shared S reconciliation may consume the accepted physical Order by exact confirmation/strict-stop chronology. Carried and accepted reuse never manufacture a new creation cause.

### 10.7 E source and recursive decision

An eligible Order's first strict stop competes with other eligible Order stops by exact lower-timeframe chronology. The winning stop defines E decision. The E source is the directional extreme over the complete parent-stop through Order-stop main-candle interval, inclusive. Accepted parent, family, numbering, same-source conflict, independent S-root restoration and hard StopAll boundaries retain the current lifecycle rules. The feedback pass reruns dependent E/StopAll stages until accepted Order_B causes stabilize; earlier history is not inferred from serialization.

## 11. OrderAudit and provenance

One row represents one canonical physical Order. `parent-stop` records Order_A with `parentType`, `parentFamily`, `eventTime` and `parentSourceTime`. `reset-leg` records Order_B with post-behavior type/source/stop, previous and reset Reaction identities and breakout/confirmation times, Reset main index and broken level, exact Reset time, leg boundary and source, exact strict break, and physical identity/confirmation. Every valid Reset-leg cause is retained in deterministic stop/Reset/break order. Parent-stop causes retain their existing order and single-owner invariant. The final audit merges causes by physical identity and retains precise native Reaction mode, box geometry, canonical stop level/source and strict stop-hit chronology.

The public legacy `orderAudit` timestamps use epoch seconds. Bridge Output projects the same final audit with full `YYYY-MM-DD HH:MM:SS` Tehran datetimes. A public S/E/StopAll referencing a physical Order must resolve to an accepted OrderAudit identity. Current-order projection uses exact stop-linked causes and returns null for ambiguous multiple physical creators.

"""
    lifecycle = section(old, 12) + section(old, 13)
    ending = f"""## 14. Final visibility and directional mirror

Calculation eligibility precedes presentation filtering. Final A/S/E/StopAll visibility cannot create or erase a physical Order cause. A selected display range retains all calculation history needed by its public Order identities. Internal Reaction classification preserves source geometry for calculations permitted by the owning stage. The opposite direction is computed through its own Reaction detector and mirrored directional policy; invariant priority, identity, cause names and serialization keys remain the same.

| Rule | Bullish | Bearish |
|---|---|---|
| Same-direction Reaction | Bullish | Bearish |
| Physical Order_B Reaction | Bearish | Bullish |
| Leg boundary | minimum Low | maximum High |
| Strict leg crossing | `Low < floor` | `High > ceiling` |
| Strict behavior stop | `Low < level` | `High > level` |
| Equal-price crossing | invalid | invalid |
| Equal boundary source | first in inclusive range | first in inclusive range |
| Order identity and cause merge | `(FirstIndex, BreakIndex)` | same |

## 15. Reconstruction and verification contract

Reconstruction must preserve complete selected RAW chronology, Decimal decisions, exact event ordering, First main-candle timing, inclusive leg geometry, strict equality, source-index ties, accepted A cutoff, dominant post-stop owner, canonical Order stop, parent-stop ownership, identity merge, every valid Reset-leg cause, S/E/StopAll feedback, visibility and serialized ordering. A Phase 2 refactor is valid only when ordered stable output objects match the Phase 1 final baseline exactly after removing solely top-level runtime `timings`.

No production branch may depend on a known timestamp, symbol, price, RAW filename, fixture ID or expected output. Do not infer a trading rule from examples. Bridge projection is presentation only. Graph navigation is evidence, never calculation authority.

## 16. Exact production source snapshot

The following blocks reconstruct the complete current production Engine calculation implementation used by this reference. Each block's SHA-256 matches the module inventory above.

"""
    blocks = "".join(
        f"### 16.{index} `{relative}`\n\n**SHA-256:** `{meta[0]}`\n\n```python\n{meta[6]}```\n\n"
        for index, (relative, meta) in enumerate(metadata, start=1)
    )
    end = """## 17. Source recovery

Extract each Section 16 Python fence without modifying its newline bytes and compare its SHA-256 with Section 1. The source blocks complement the semantic text; a prose/source disagreement must be reported and resolved before declaring the reference synchronized.
"""
    output.write_text(
        introduction + unchanged + order_section + lifecycle + ending + blocks + end,
        encoding="utf-8", newline="\n",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="5.4.14-HPZR1")
    parser.add_argument("--suffix", default="V5.4.14_HPZR1_OrderAB_Refactor")
    args = parser.parse_args()
    for direction in ("bullish", "bearish"):
        output = ALGORITHMS / (
            f"TradingBot_{direction.title()}_Algorithm_Reference_{args.suffix}.md"
        )
        build(direction, args.version, output)
        print(output)
