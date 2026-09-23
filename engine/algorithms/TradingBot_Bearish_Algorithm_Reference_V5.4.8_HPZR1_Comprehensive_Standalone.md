# TradingBot Bearish Algorithm Reference — Comprehensive Standalone Rebuild & Exact Implementation Specification

**Document Version:** `5.4.8-HPZR1`  
**Last Modified Date & Time:** `2026-09-23 10:19:31 +03:30`  
**Status:** `Updated V5.4.8 production reconstruction specification; bearish direction; documentation-only HPZR2 synchronization over the unchanged HPZR1 production source snapshot`  
**Target Direction:** `bearish`  
**Opposite/Order Direction:** `bullish`  
**Primary computational example timeframe:** any integer timeframe >= 1 second; 30s is the project validation timeframe but is not hardcoded  
**Internal timezone:** `Asia/Tehran`  
**Mirror Contract:** `Bearish is not an independently drifting algorithm. It is the exact directional mirror of canonical Bullish: Low↔High, minimum↔maximum, <↔>, FirstRed↔FirstGreen, Bullish↔Bearish; invariant lifecycle/priority/serialization rules do not mirror.`  

> **Normative rule:** This document is written from the current production Source snapshot, not from older Algorithm Reference wording. If an older reference conflicts with this file, this file represents the Source behavior captured by the manifest below. The goal is implementation equivalence: a competent engineer must be able to reconstruct the calculation engine without having the original Source files.

> **5.4.5-HPZR2 standalone-reference regeneration (2026-09-22):** Documentation/reconstruction revision only. **Production Source changes: NONE. Algorithm changes: NONE. Calculation changes: NONE. Behavioral changes: NONE. Serialization changes: NONE.** All nine current production modules were re-read in full; the Source-symbol appendix is regenerated from the current syntax tree and current line positions; explicit Direction-Invariant, standalone dependency/Public-API, cache-scope, direct source-recovery, and mandatory verification sections are added. The complete current code for all nine project-owned modules remains embedded directly in this file, so no external Source directory is required.


> **5.4.8-HPZR1 immutable first stopped-A Order_A owner (2026-09-23):** Each stopped A assigns its exact `parent-stop` cause to the FIRST canonical opposite Reaction confirmed strictly after the A stop (First at/after the stop main candle). This physical identity is final. Subsequent native Mode-B confirmations NEVER refresh the A-owned Order_A, regardless of the provisional S decision. S uses that first Order when the order-backed route owns the handoff. Another Order may participate only through a separately proven creation cause, e.g. an independent parent-stop or Reset-leg/Order_B; `accepted-live` and `carried-live` are use routes, not creation causes. One physical Order may correctly hold several distinct independent parent-stop causes. This supersedes the V5.4.5 consecutive Mode-B stopped-A refresh rule, but does not change native Reaction modes, Order_B formation, exact price/chronology, shared accepted-Order stops, E parent-stop owner ranking, StopAll, or serialization. This ownership invariant applies identically to Bullish and Bearish. The August 25 09:32:30 Bearish A retains physical First/Break (689,693); the historical September 9 Mode-B refresh example is a previous-version result, not a current expected output. All historical examples remain test evidence rather than production branches.

> **5.4.7-HPZR1 Red-boundary stale-Blue reversal correction (2026-09-23):** The `opposite-s-group-stop` evidence counter is pending-reversal state, not an indefinite historical count through unrelated accepted Red behaviors. Process accepted S/E in the established chronological source order; after an eligible Mode-B S Red has been evaluated, any accepted Red S clears pending Blue-repeat counts (including an ineligible native Mode-A S Red). Any accepted Red E that remains E also clears those pending counts after the separate E-driven StopAll decisions. Later Blue S/E occurrences may re-arm a fresh exact-key repeat gate. StopAll still clears all counters and active owners. Native Mode-B eligibility, exact E-number/S grouping, deterministic gate metadata, Decimal/strict price geometry, E-driven StopAll priority and counters, physical Order identity, and serialization are unchanged. Both market directions use this identical direction-invariant Red-boundary rule. A price/timestamp/dataset-specific exception is forbidden. The four August XAUUSD Bearish cases are test evidence; the independent September 4 Bearish repeated-Blue StopAll remains valid.

> **5.4.6-HPZR1 accepted-S native Order Mode-B eligibility correction (2026-09-23):** The independent accepted-S `opposite-s-group-stop` reversal gate now requires an accepted `S Red` whose forming physical Order has native `order_mode == "B"` (the opposite Reaction mode, not the independent Order_B/reset-leg provenance). An accepted S Red with a native Mode-A Order or no formation Order remains S Red even when older exact Blue behavior-group counts have reached two. For a Mode-B S Red, the existing hard-cycle exact Blue-group counts, latest-group tie-breaking, gate metadata, and StopAll hard reset are unchanged. E-driven `sequence-group-stop` and `stopall-stop` are unaffected. This eligibility condition is direction-invariant and does not alter Reaction, Reset, Blue, A, S formation, E formation, Order identity, strict crossing, or serialization. The three August XAUUSD Bearish 30s S Red anchors are validation cases only; the condition never checks a timestamp, symbol, RAW name, or expected output.

> **5.4.5-HPZR1 high-performance zero-difference refactor (2026-09-22):** This revision changes implementation performance only. **Algorithm changes: NONE. Calculation/behavior rules: NONE. Serialization schema/order: NONE.** The authoritative 5.4.5 behavior remains unchanged. Production performance changes are scoped to three existing files only: `reaction_engine.py` replaces repeated lower-timeframe containment scans/history-prefix allocation with exact indexed range/first-event lookups; `s_zone_detector.py` pre-indexes immutable Reaction/Reset/Blue chronology, caches repeated A-stop→Order searches, and uses exact lower-timeframe range indexes for repeated strict-cross queries; `e_zone_detector.py` adds per-run canonical Order-stop caching, immutable initial-Order indexes, physical-identity indexes, a confirmation-time side index for the accepted Order ledger, and collapses repeated Order_B Reset-leg origins to the already-authoritative latest cause per physical `(FirstIndex, BreakIndex)`. All caches/indexes are run-scoped; no dataset/timestamp/symbol-specific branch or global mutable cross-run trading state is introduced. Four complete regression datasets are final-payload hash-identical before/after; the largest 309,906-row XAUUSD RAW completes in the optimized build in both directions, while the unmodified baseline build exceeds this execution environment's 240-second ceiling during initial E calculation and therefore is explicitly reported as an incomplete full-baseline comparison rather than a false PASS.

> **4.0.1 exact-mirror correction (2026-09-17):** chained Blue inherited-stop chronology is now identical in Bullish and Bearish. For a stopped Blue, the carried directional extreme is frozen from the stop main candle through the **complete** next same-direction Reaction Breakout main candle, inclusive. Bullish uses minimum Low; Bearish uses maximum High. No direction-specific time-window exception remains.

> **5.0.1 historical-output preservation (2026-09-19):** E calculation ownership and all existing reconciliation winners remain unchanged. A presentation-only historical rescue now preserves an E-parented Blue Order carrying `reset-leg` / `Order_B` provenance that was accepted in an earlier authoritative E pass but disappeared only during later reconciliation, provided it is not a hidden intermediate parent of a surviving final E and no higher-priority final E remains active through its decision. Rescued history is appended only after lifecycle/StopAll/OrderAudit decisions and therefore cannot renumber, recolor, re-parent, stop, or otherwise modify previously accepted behaviors.

> **5.1.1 S-Red / dominant-Blue StopAll correction (2026-09-19; historical accepted-S gate, superseded by 5.4.4):** The accepted-S reversal gate is family-invariant across market direction. The active dominant Blue **key itself** must repeat: progression across E numbers is replacement, not accumulation. Thus `E1 Blue → E2 Blue → E3 Blue` means one current E3 Blue occurrence. A later accepted S Red may be promoted to `StopAll1` only when that exact current Blue key has count >= 2 and its latest dominant occurrence has strictly stopped before the S decision. Repeated S Blue follows the same exact-key principle. Red/Blue labels, family priority, hard StopAll reset, and serialization remain direction-invariant; only strict price geometry mirrors.


> **5.1.2 Order-ownership / Bridge-consistency correction (2026-09-20):** One exact `parent-stop` provenance can now influence E calculation through only one physical Order identity. E candidate construction enforces the same single-consumption rule already required by OrderAudit *before* Order-stop deadlines and E representatives are selected: the earliest Order ranked by `(confirmationTime, FirstIndex, BreakIndex)` owns the `parent-stop`; a later physical Order is removed unless it survives through an independent cause such as `reset-leg`. Carried-live provenance and accepted noncanonical bounded `Order_A` geometry (`reactionNumber=0`) are retained in the accepted Order ledger. Whenever later pipeline reconciliation replaces an E branch or restores an independent accepted E root, OrderAudit is synchronized to that final accepted history. Before Bridge serialization, every public S/E/StopAll Order identity must exist in canonical OrderAudit and one exact parent-stop provenance may not map to multiple physical Orders; violation is a hard invariant error rather than a silent inconsistent payload. StopAll calculation code was unchanged in that historical revision; current stage-qualified counting semantics are defined by 5.4.2 and Section 15F.

> **5.2.0 canonical Order_B rebuild (2026-09-20):** The previous Order_B/reset-leg implementation is removed and superseded. Order_B is now an independent formation cause rather than a synonym for native Reaction Mode B. It starts from a Reset of the **same trend direction**, derives the primary trigger extreme from the owner Breakout main candle through the Reset main candle inclusive, waits for the exact lower-timeframe strict break of that extreme, requires only raw opposite-direction Reaction **geometry** inside the closed primary-extreme-source → strict-break-main-candle interval, derives the mirrored other edge on that same closed interval, and assigns the first canonical opposite Reaction after the gate as the physical Order_B. Normal Reset validity/lifecycle/public/Internal status is ignored only for the evidence geometry test. If several valid Order_B origins map to one physical Order, the latest valid Reset-leg cause is authoritative. Bullish/Bearish are exact directional mirrors. Bridge consistency is also presentation-range safe: a public S/E/StopAll may retain the canonical OrderAudit identity/cause it references even when that Order First or accepted A source lies before the requested presentation start.

> **5.3.0 shared accepted Order-stop correction (2026-09-20):** Order confirmation is now explicitly parent-neutral across calculation-accepted behavior state. A physical Order accepted through A, S, E, StopAll, or Reset-leg/Order_B provenance may decide a different open S/E candidate when its exact strict Order stop falls inside that candidate's valid chronology; the creating parent does not have to equal the candidate parent. S reconciliation now uses only accepted physical identity + exact stop chronology and no longer blocks an otherwise-valid Order because it belongs to a newer independent parent. E adds a dedicated post-parent-stop `accepted-live` route for Orders confirmed after the candidate parent stopped, while preserving carried-live for Orders already active at the stop. `accepted-live`/`carried-live` are use provenance only: original parent-stop/reset-leg creation causes remain authoritative in OrderAudit. Hard StopAll/sequence resets remain absolute boundaries. Bullish/Bearish apply the same ownership/chronology rule with only strict price comparisons mirrored.

> **5.4.0 cycle/stage-order ownership correction (2026-09-20):** The normative behavior pass order `A → S → E → StopAll` is now enforced when an accepted S owns a transition. If a fallback A is rejected as an equal/lower re-entry under that S owner, the rejected A may no longer consume the S and thereby reopen a second A→S branch. That A identity is marked stage-invalid; S candidates descending from it are removed from accepted S and excluded from later suppressed-S continuation evidence, so they cannot fabricate a new E root or override an already accepted E chain. This fixes the Bearish `S Blue 17:43:00 → erroneous A 18:01:30` case and its exact Bullish mirror where an invalid S Red branch displaced `E2 Blue 14:26:30`. The correction is deliberately scoped: Reaction/Reset, Blue, A geometry, valid S geometry, Order_A, canonical Order_B, shared accepted Order-stop logic, E source geometry, and StopAll rules are unchanged.

> **5.4.1 exact same-Break Reset mirror correction (2026-09-21):** Post-confirmation Reset ownership is now fully symmetric in every UnifiedReactionDetector path. Whenever exact lower-timeframe confirmation analysis is available, both Bullish and Bearish freeze `analysis.extreme` as the opposite edge for the remainder of that same Break main candle. A same-Break Reset is detected against that exact frozen edge and its published `brokenLevel` is the identical level used for detection. This removes the former Bearish-only fallback to the completed main-candle `BoxTop` in initial, direct post-Reset, and Normal confirmation paths. Bullish calculation semantics are unchanged. The correction is intentionally narrow: Blue, A, S, E, StopAll, Order_B, lifecycle priority, family labels, Doji handling, and serialization rules are unchanged; only downstream results causally affected by corrected Bearish Reaction/Reset chronology may differ.

> **5.4.2 live-Scale A / stage-qualified dominant-Blue correction (2026-09-21):** Two independent ownership defects are corrected without changing Reaction/Reset, Blue formation, S/E geometry, Order_A/Order_B, strict crossing, family priority, or serialization. First, ordinary A inherited-stop geometry may not be borrowed by a still-live **Scale Blue**: when the previous Blue is Scale and has not actually strict-stopped before the following Blue forms, `_inherited_stop()` returns no carried level and ordinary pair logic must wait for real Blue stop chronology. Reset-Blue pre-stop structural chaining remains unchanged. This rule is direction-neutral and therefore mirrors automatically. Second, lifecycle dominant-Blue counting is stage-qualified under the invariant `A → S → E → StopAll`: when the first accepted E Blue replaces an S Blue owner, E-stage Blue dominance starts at **one**, rather than counting the superseded S Blue and the new E Blue as two simultaneous dominant occurrences. In V5.4.2, later E-stage Blue occurrences still accumulated at stage scope; **V5.4.3 supersedes that part** with exact-key counting, so advancing from E1 to E2/E3 replaces the key instead of incrementing one shared Blue counter. Same-key S sequence counting for `sequence-group-stop` remains unchanged. Every StopAll remains a hard reset of S/E counters and dominant-Blue state. Regression anchors include Bearish XAUUSD 30s `A 11:15:30 → S Red 11:54:30`, `StopAll1 13:20:30`, `StopAll2 15:20:30`, and after that boundary `E1 Blue 16:21:30 → S Red 17:43:00 → E1 Red 17:56:30`. These timestamps are validation evidence only and are never production branches.

> **5.4.3 cycle / exact-Order / exact-key StopAll / S-Blue Type-4 correction (2026-09-21):** Four scoped production corrections are applied as one lifecycle-consistent revision. (1) Cycle validation now consumes every S-eligible A identity, including an A temporarily hidden by a provisional S; later S reconciliation may not resurrect an equal/lower A behind an already accepted larger-stage owner. (2) Canonical Reaction/Order opposite-edge geometry is frozen at the **first exact lower-timeframe strict confirmation inside the Break main candle**: prices later in that same main candle may not retroactively rewrite BoxBottom/BoxTop. This is symmetric Bullish/Bearish and is now calculation-authoritative, not presentation-only. (3) The accepted-S reversal StopAll gate counts repetitions of the **exact current dominant Blue behavior key**, not progression across E numbers: `E1 Blue → E2 Blue → E3 Blue` leaves one current `E3 Blue`; a later S Red may become StopAll only after that same current Blue key has occurred at least twice and its latest occurrence has strictly stopped. The same exact-key principle remains available to repeated `S Blue`. Every StopAll is still a hard reset. (4) A new independent `S Blue Type-4` route exists only after A strict-stop and before any opposite Order forms: from the A-stop main candle through the Breakout main candle of the latest confirmed same-direction Reaction, select the directional extreme (Bearish maximum High; Bullish minimum Low) as the current S candidate; if it is strictly crossed before any Order and at least one calculation-valid non-Internal Blue exists from the candidate-source main candle through that exact crossing, emit S Blue Type-4. A crossing without qualifying Blue emits no S and a later aligned Reaction rebuilds the candidate; any Order confirmation ends Type-4 eligibility. These are semantic rules only; no timestamp/fixture branch is permitted.

> **5.4.4 cycle-wide exact-Blue-repeat StopAll correction (2026-09-21):** The accepted-S reversal gate is no longer tied to the current dominant Blue owner or to a strict stop of that latest Blue occurrence. From calculation start, or from the most recent StopAll hard boundary, count every **accepted occurrence of each exact Blue behavior group independently**: all `S Blue` occurrences share one group, while `E1 Blue`, `E2 Blue`, `E5 Blue`, etc. are separate numbered groups. Any one group reaching `count >= 2` arms the reversal gate; the **next accepted `S Red`** is promoted to StopAll with `gateType='opposite-s-group-stop'` (historical rule; V5.4.6 adds native Mode-B eligibility and V5.4.7 ends the armed interval on an accepted Red behavior), even if another behavior has since become dominant. Different E numbers never add together (`E1 Blue + E2 Blue` is not two similar behaviors). Every StopAll clears all cycle-wide Blue-repeat counters. E-driven `sequence-group-stop` and `stopall-stop` rules remain unchanged. This rule is direction-invariant; only strict price geometry mirrors. Historical regression anchor (superseded as an output assertion): the older Bullish `2026-09-04 02:36:00` example was documented for this gate. In the current full-file baseline and updated Source, no Bullish S/E/StopAll occupies that source; the Bearish `StopAll1 @ 2026-09-04 02:36:00` has a native Mode-B Order and remains a valid retained observation. Exact-key counting and the new Mode-B eligibility apply in both directions. Timestamps are validation evidence only and must never be hardcoded.






> **5.4.5 consecutive native Mode-B stopped-A Order refresh correction (historical; superseded by V5.4.8 first-Order_A ownership):** The first canonical opposite Order confirmed after an A strict stop still opens the provisional A→S Order owner. However, while that S remains undecided, consecutive **native Reaction Mode-B** Orders belong to one replaceable continuation chain: if the next Mode-B confirms strictly before the current provisional S decision event, Order ownership refreshes to that newer Mode-B and the S candidate/decision is rebuilt from the newer Order geometry. The refresh repeats until no later consecutive Mode-B confirms before the recalculated S decision. A native Mode-A Order terminates this replaceable Mode-B chain and may not be crossed by the refresh; likewise an Order confirming at or after the current S decision cannot retroactively steal ownership. OrderAudit moves the stopped-A parent-stop cause from provisional earlier Order identities to the final refreshed physical Order, preserving the one-cause/one-physical-Order bridge invariant. The rule is direction-neutral and contains no timestamp/symbol-specific branch. Regression anchor on XAUUSD 30s: `A 2026-09-09 03:33:30` resolves through consecutive Mode-B Orders `04:16:00 → 04:17:30 → 04:20:30 → 04:24:00`; the final Order keeps stop source `04:21:00`, producing `S Red 04:29:30`, removing the incorrect `S Blue 04:45:00`, then yielding `E1 Red 05:15:30` and existing lifecycle promotion to `StopAll 06:23:00`. These timestamps are validation evidence only.


## 0. How to use this document / reconstruction guarantee

This document is intentionally designed as a **complete engineering reconstruction manual**, not as a high-level strategy description. It contains three independent layers of specification:

1. **Semantic algorithm specification** — the trading/market rules, chronology, lifecycle ownership, priorities, invariants, and directional rules.
2. **Function-level reconstruction contract** — exact pseudocode, state transitions, branch precedence, tie-breaking, data-object schemas, public serialization, and the authoritative pipeline pass order.
3. **Exact production implementation snapshot** — the complete text of every Python production module used by this snapshot, embedded verbatim in Section 26 with SHA-256 markers.

A rebuild may use a different architecture or programming language, but if exact behavioral equivalence is required it must preserve every observable semantic rule described here. If the prose appears ambiguous, the exact embedded source snapshot and its SHA-256 identity are the final disambiguation mechanism for this document version.

### 0.1 What counts as a "behavior"

In project terminology, **only `A`, `S`, `E`, and `StopAll` are behaviors**. `Reaction`, `Reset`, and `Blue Line` are calculation/market-structure evidence and are not called behaviors. `Order`/`OrderAudit` are trading-geometry/provenance objects used by S/E/StopAll calculations.

### 0.2 Hard invariants that apply everywhere

- All price comparisons use `Decimal`; no binary-float decision is permitted.
- Candle color is `GREEN` when `close >= open`; therefore every exact Doji is GREEN.
- Strict crossings are strict: equality never stops/confirms/breaks a level.
- Exact lower-timeframe chronology wins whenever multiple events occur inside one main candle.
- No timestamp-, symbol-, price-, RAW-name-, fixture-, or expected-output-specific branch is allowed.
- Full physical RAW is calculation scope; request `from/to` bounds are presentation scope only.
- Directional price geometry mirrors; lifecycle/family priority, serialization structure, Doji rule, and other explicitly invariant rules do **not** mirror.
- Internal Reaction evidence remains calculation-visible except where a rule explicitly prohibits one scoped public/Order route.
- A StopAll is a hard lifecycle boundary for ownership/history downstream.
- Behavior stage ownership is invariant: `A → S → E → StopAll`. A rejected earlier-stage fallback cannot consume a later-stage accepted owner or feed descendants into a later stage.

### 0.3 Complete module inventory in this snapshot

| File | Lines | Classes | Functions/methods (including nested helpers) | Optional SHA-256 |
|---|---:|---:|---:|---|
| `reaction_engine.py` | 2406 | 13 | 77 | `bea0d5a5e95ee15ad54d024f6c01b8c777ba2abcc3c8e671118f1ae2df28f2a6` |
| `blue_line_detector.py` | 458 | 2 | 13 | `6fa01d94bc98060b62bc7e68db0ec24a0b0159727d44043affee7130a9c11448` |
| `a_zone_detector.py` | 782 | 3 | 22 | `f5658aef5105dcfad916d3ea6f792877737c2568d67cf27c7b63c2638c5343fd` |
| `s_zone_detector.py` | 1562 | 2 | 49 | `7714025b3f43087b09844df6feeef4eef0ec72eeb841115293df4c126fd202ee` |
| `e_zone_detector.py` | 2876 | 3 | 75 | `6e32b947aa1b4e1e6b986f26ee9a464542f320dc6a207ece1e8fce54407d0369` |
| `lifecycle_engine.py` | 1706 | 2 | 42 | `84bed2e674f855a4d2dc52960840eddc6d8f058ff247b893a319eecdc36e152d` |
| `trading_pipeline.py` | 1923 | 6 | 37 | `98f54cf3be6ddacd4e6b523b604be5a00635dcf8b464bc7d03772bbcccded62e` |
| `direction_policy.py` | 70 | 1 | 6 | `a27ac63c2f066311c9381e2ead6fb44f0789f423a37b465da65c80e6329397ea` |
| `core_utils.py` | 29 | 0 | 3 | `3dae390ae77b72965f5799f7c132c4eba203775d5e72761fd7dd60c90f8578de` |

All nine module texts are embedded in full in Section 26. Integrity hashes are recorded for extraction checking only; they are not a substitute for reading and semantic synchronization.

## 1. Source baseline / rebuild identity

The table below describes the exact production modules embedded by this documentation revision. The SHA-256 column is optional integrity metadata only; semantic synchronization is established by direct source reading/comparison.

| Module | Source version | Last modified declared by module | Lines | Role | Optional SHA-256 |
|---|---:|---|---:|---|---|
| `reaction_engine.py` | `9.8.0` | `2026-09-22 00:35:00 +03:30` | 2406 | Authoritative Reaction/Reset geometry, candle semantics, lower-timeframe chronology, canonical Order-stop geometry, and Internal-Reaction classification. | `bea0d5a5e95ee15ad54d024f6c01b8c777ba2abcc3c8e671118f1ae2df28f2a6` |
| `blue_line_detector.py` | `2.3.0` | `not declared by module` | 458 | Scale/Reset Blue detection, strike state, Blue validity, line construction, and Internal/Public Blue ownership. | `6fa01d94bc98060b62bc7e68db0ec24a0b0159727d44043affee7130a9c11448` |
| `a_zone_detector.py` | `1.6.4` | `2026-09-21` | 782 | A behavior formation from Blue-pair/double-stop state, inherited stops, trigger chronology, and A source ownership. | `f5658aef5105dcfad916d3ea6f792877737c2568d67cf27c7b63c2638c5343fd` |
| `s_zone_detector.py` | `4.20.0` | `2026-09-23 10:19:31 +03:30` | 1562 | A-to-S handoff, S formation families, stopped-A Orders, shared accepted-Order stop reconciliation, and initial OrderAudit. | `7714025b3f43087b09844df6feeef4eef0ec72eeb841115293df4c126fd202ee` |
| `e_zone_detector.py` | `6.13.0` | `2026-09-22 00:35:00 +03:30` | 2876 | Recursive E formation, parent-stop/Order_A/Order_B/accepted-live/carried-live routes, E reconciliation, and accepted Order provenance. | `6e32b947aa1b4e1e6b986f26ee9a464542f320dc6a207ece1e8fce54407d0369` |
| `lifecycle_engine.py` | `1.15.2` | `2026-09-23 09:55:12 +03:30` | 1706 | Cross-stage behavior lifecycle, priority, visibility, StopAll state, cycle boundaries, and ownership arbitration. | `84bed2e674f855a4d2dc52960840eddc6d8f058ff247b893a319eecdc36e152d` |
| `trading_pipeline.py` | `1.4.1` | `2026-09-21 08:40:00 +03:30` | 1923 | Production orchestration, RAW normalization, engine loading, full-range calculation, reconciliation passes, filtering, telemetry, and JSON serialization. | `98f54cf3be6ddacd4e6b523b604be5a00635dcf8b464bc7d03772bbcccded62e` |
| `direction_policy.py` | `1.0.0` | `not declared by module` | 70 | Direction-neutral Bullish/Bearish price-geometry policy primitives. | `a27ac63c2f066311c9381e2ead6fb44f0789f423a37b465da65c80e6329397ea` |
| `core_utils.py` | `1.0.0` | `not declared by module` | 29 | Small shared stateless primitives for Decimal normalization and physical Order identity. | `3dae390ae77b72965f5799f7c132c4eba203775d5e72761fd7dd60c90f8578de` |

A rebuild intended to reproduce this specification must preserve the semantics, schemas, boundary rules, chronology, ordering, and serialization of this exact production snapshot.

## 2. System architecture and authoritative stage order

The engine is a deterministic multi-stage calculation pipeline. The stages are:

`RAW normalization → both-direction Reaction/Reset geometry → Internal-Reaction ownership → Bearish Blue → Bearish A → Bearish S + stopped-A Order audit → Bearish E + Order reconciliation → lifecycle hierarchy → StopAll → final A/S/E visibility → public serialization`.

Even when only `Bearish` output is requested, both Bullish and Bearish **Reaction** streams are required whenever behavior modules are active, because S/E Orders use the opposite direction's Reaction/Reset geometry. Do not replace this with a one-direction shortcut.

When E is enabled and S is enabled, the pipeline first builds full-RAW geometry and full-range behavior state, performs S/E/lifecycle reconciliation, and only then filters objects to the requested presentation main-candle indexes.

### Calculation range versus presentation range

`from-time` and `to-time` are **presentation boundaries only**. The entire physical RAW file is parsed, normalized and calculated. Open Reaction/Blue/A/S/E state may resolve after `to-time`; truncating calculation at the visible range is non-conforming because it can manufacture provisional states that do not exist in a full-file run.

Main-candle source indexes and behavior ordinals therefore belong to the full RAW calculation, not to a sliced request.

## 3. Raw data, Decimal, time and candle construction

### 3.1 Input rows

Each raw row has `time`, `open`, `high`, `low`, `close`. `time` is an epoch-second integer.

### 3.2 Price normalization

Every price is converted with semantics equivalent to `Decimal(str(value))`; an already-Decimal value is preserved. Never use a binary float for a strict trading comparison.

### 3.3 Duplicate raw timestamps

Raw rows sharing the same exact second are collapsed into one lower candle: Open=first row Open, High=max, Low=min, Close=last row Close.

### 3.4 Main timeframe buckets

For timeframe `T` seconds, `bucket_time = time` when `T=1`; otherwise `bucket_time = floor(time/T)*T`. Within one bucket: Open=first raw Open, High=max, Low=min, Close=last raw Close.

### 3.5 Timezone

Epoch timestamps are converted to `Asia/Tehran`, then held internally as naive datetimes representing Tehran wall time. Public epoch serialization interprets those naive datetimes as Tehran again.

### 3.6 Candle color

`GREEN` iff `close >= open`; otherwise `RED`. Equality/Doji is therefore always GREEN. This rule is global and must not be mirrored or changed.

## 3A. Direction-Invariant Rules

The following rules are shared by Bullish and Bearish and **must not be directionally swapped**:

- Candle color is global: `GREEN if close >= open else RED`; therefore **every Doji (`close == open`) is GREEN**.
- Strictness is global: a level is crossed only by a strict inequality; equality never confirms, stops, breaks, or invalidates a level.
- All algorithmic price values use exact `Decimal` semantics; binary floating-point approximations are not an alternative algorithm.
- Full physical RAW is the calculation authority; request `from/to` bounds are presentation filters, not historical-state truncation rules.
- Exact lower-timeframe chronology is authoritative whenever event ordering inside a main candle matters.
- Behavior taxonomy is fixed: only `A`, `S`, `E`, and `StopAll` are behaviors. Reaction, Reset, Blue, Order, and OrderAudit are not behaviors.
- Red/Blue family names are invariant and are never swapped because market direction changes.
- E numbering semantics are invariant.
- Lifecycle priority is invariant: `StopAll > E Red > S Red > E Blue > S Blue > A`.
- StopAll semantics and hard-boundary reset behavior are invariant.
- Physical Order identity is invariant: `(FirstIndex, BreakIndex)`.
- Creation provenance and use provenance remain distinct in both directions.
- Internal/public visibility is separate from calculation eligibility in both directions.
- Stage order, stable chronology, output ordering, null/non-null meaning, JSON schema, and serialization ordering are invariant.
- Exact Blue-repeat grouping for StopAll is invariant: all accepted `S Blue` occurrences share one group; each numbered `E<n> Blue` is a separate exact group.

Only directional market geometry mirrors (`Low↔High`, `min↔max`, `<↔>`, `BoxBottom↔BoxTop`, FirstRed↔FirstGreen, Bullish↔Bearish). Do not change an invariant merely to make a synthetic mirror test look more symmetrical.

## 4. Direction policy for Bearish

| Semantic | Bearish value |
|---|---|
| Trend extreme attribute | `high` (High) |
| Opposite extreme attribute | `low` (Low) |
| Strict stop/cross | `High > level` |
| Better directional extreme | larger / maximum |
| Reaction First color | `GREEN` |
| Context color | `RED` |
| Reaction confirmation | `Low < BoxBottom` |
| Opposite Order direction | `bullish` |
| Scale-strike confirming candle color | `RED` |

A strict cross never accepts equality.

## 5. Shared chronology contract

### 5.1 Main-index mapping

An exact lower event belongs to the greatest main-candle timestamp `<= eventTime`. If an event precedes all main candles, normal calls fail; explicitly clamped lifecycle calls map to index 0.

### 5.2 Lower windows

The canonical lower window is half-open `[start,end)`. Exact inclusive endpoints are implemented only where the rule explicitly states inclusion.

### 5.3 Reaction confirmation time

For Bearish, scan the Reaction Break main candle from `intrabar_start` when enabled, otherwise from Break candle open, and return the first lower event satisfying `Low < BoxBottom`. If no lower event is available/found, the Break main timestamp is the fallback.

The A engine intentionally calls confirmation with `use_intrabar_start=False`; S/E/public Reaction chronology uses the exact intrabar start when present.

### 5.4 Reset time

If Reset has `secondTime`, that exact lower timestamp is authoritative; otherwise use its main display time/timestamp.

## 6. Reaction and Reset engine — Bearish

### 6.1 Core Reaction object

A Reaction Candidate stores First, BoxTop provenance/value, BoxBottom provenance/value, Mode (`A` or `B`), optional anchor/leg boundary, Break, exact intrabar start, cross-direction flags, public-number/public-box metadata and `behavior_internal`.

### 6.2 Initial Mode-A detection

The first proven Leg-Start is discovered with the directional detector. For Bearish:

- First must be `GREEN` and is normally preceded by `RED` context.
- The context run is extended backward across consecutive `RED` candles.
- Candidate outer confirmation edge and inner/opposite edge are derived from the complete local leg according to the formulas below.
- A frozen leg boundary may invalidate Mode A before confirmation.

For Bullish specifically: context run peak and FirstRed determine BoxTop; BoxBottom begins at FirstRed Low and may move lower while waiting; strict confirmation is `High > BoxTop`; frozen leg floor/anchor is invalidated by `Low < floor` before confirmation.

For Bearish, the implementation is the exact reflected Bullish state machine: reflect prices around zero (`high'=-low`, `low'=-high`, `open'=-open`, `close'=-close`) and swap GREEN/RED tags for detector-internal logic, run Bullish detection, then mirror the resulting Candidate/Reset back. This means Bearish confirmation is `Low < BoxBottom`, its evolving opposite edge is BoxTop, and its frozen ceiling is invalidated by `High > ceiling` before confirmation.

### 6.3 Same-main-candle race: Mode-A invalidation vs confirmation

If the main candle cannot both invalidate and confirm, use the obvious main OHLC result. If both are possible, inspect lower events. Invalidation is searched before confirmation; an exact finest-event tie is invalidation-first. A later breakout/breakdown cannot resurrect a structurally invalid candidate.

### 6.4 Confirmed Reaction box ownership

After a Candidate confirms, canonical calculation geometry is:

- Bullish: BoxTop stays the discovered confirmation edge; BoxBottom becomes the minimum Low from First through Break inclusive.
- Bearish: BoxBottom stays the discovered confirmation edge; BoxTop becomes the maximum High from First through Break inclusive.

The exact lower confirmation analysis may refine an opposite edge that was sourced by the Break candle so prices after confirmation cannot retroactively contaminate exact confirmation ownership.

### 6.5 Public Reaction geometry

Public serialization uses a clone/frozen public Candidate. When the opposite edge source is the Break candle, freeze that edge using lower data only through the exact confirmation event. This prevents post-confirmation remainder prices from rewriting the published reaction that caused the confirmation.

### 6.6 Reset before confirmation

Once a prior confirmed Reaction has an opposite boundary, a strict directional break of that boundary is a Reset. If Reset and a waiting candidate's confirmation are both possible in one main candle, compare exact lower events. Reset wins when its first strict event occurs before or at the confirmation event under the detector's ordering rule.

For Bearish, Reset condition is `High > previous confirmed BoxTop`.

### 6.7 Post-confirmation same-Break Reset

After strict confirmation, inspect only the remainder of that same Break main candle. Freeze the exact-confirmation opposite edge. If a later lower event strictly crosses that frozen opposite edge, record a Reset with `index = Break main candle`, `secondTime = exact reset event`, `brokenLevel = frozen edge`, and `fromFirstIndex = confirmed First`.

Implementation invariant: when exact confirmation analysis exists, `analysis.extreme` is the frozen opposite edge in **both** directions and in every initial/direct/Normal confirmation path. Bullish uses the exact confirmation-side minimum Low as appropriate to its geometry; Bearish uses the exact mirrored maximum High. The level passed to same-Break Reset detection and the serialized `brokenLevel` must be the same exact value.

That Break main candle belongs to the closed/reset transition and **cannot** simultaneously seed the next Normal Reaction First.

### 6.8 Reusing a confirmation candle as the next Mode-B First

If no post-confirmation Reset exists and the Break candle has the required new-First color (`RED` Bullish, `GREEN` Bearish), the whole main confirmation candle may become the next Mode-B First. Its box extrema are calculated from the full main candle's lower events; this is intentional current behavior.

### 6.9 Normal Mode-B search

After a confirmed Bearish Reaction, keep a running trend-side outer extreme. When a `GREEN` candle becomes eligible:

- Bearish: BoxBottom = min(running trough, FirstGreen Low); BoxTop = maximum High from the BoxBottom source (exclusive when earlier) through FirstGreen.
- While waiting, update the opposite edge only if a new more-extreme value is made.
- Confirm strictly with `Low < BoxBottom`.

### 6.10 Direct same-direction recovery after Reset

A Reset reopens Mode A in the **same requested direction**. Opposite-direction patterns do not gate this search. The first structurally healthy same-direction geometry after the Reset becomes Mode A. Direct and anchor/context interpretations are compared by actual confirmation chronology; the chronologically earliest valid confirmation wins.

### 6.11 Frozen owner boundary for direct/Order geometry

Mode-A/direct post-Reset geometry is dead if the frozen owning leg boundary is strictly broken before confirmation. Bullish uses floor invalidation before `High > BoxTop`; Bearish uses ceiling invalidation before `Low < BoxBottom`. Same-finest-event tie is invalidation-first. This rule applies to canonical/direct parent-stop Order geometry. Order_B evidence geometry is deliberately geometry-only and therefore does not apply normal Reset/invalidation acceptance; the final physical Order_B must still be a canonical opposite Reaction.

### 6.12 Canonical Order stop geometry

An Order is always an opposite-direction Reaction (`Bullish` for this Bearish behavior stream).

- Order Mode A: find the true leg outer boundary from its anchor/context through Break inclusive. For Bearish Order use maximum High; for Bullish Order use minimum Low. Context scan extends backward over the Order's context color.
- Order Mode B: inherit the previous healthy opposite Reaction semantic outer edge: Bearish Order uses previous BoxTop; Bullish Order uses previous BoxBottom.
- A Mode-B Order with no previous healthy Reaction is invalid.

### 6.13 Bounded Order-gate search

Stopped-A and E parent/reset logic may request the first opposite Reaction after an exact gate. The canonical healthy Reaction identity is authoritative. Local/bounded geometry is a search mechanism; it must not jump over an earlier canonical valid Reaction. A Reaction whose First is in the main candle containing the gate may be eligible only if its exact confirmation is strictly after the gate when that caller requires post-gate ownership.

### 6.14 Internal Reaction classification

After both directional Reaction streams are calculated, build public box/confirmation metadata. A Reaction is `behavior_internal=true` only if:

1. its First is strictly after an opposite Reaction First;
2. its confirmation is no later than the opposite Reaction confirmation;
3. its published box is geometrically contained in the opposite published box; and
4. every lower event from inner First through inner confirmation stays inside the outer public box.

Internal Reaction evidence remains calculation-valid. Order_B evidence geometry explicitly ignores Internal/public status. A separate downstream lifecycle filter remains narrowly scoped to a **native Mode-B, behavior-internal physical Order whose surviving causes are all Reset-leg**; that filter occurs after formation/cause merging.

## 7. Blue Line engine — Bearish

### 7.1 Fibonacci level

`F = BoxBottom + 0.618*(reference-BoxBottom)`.

### 7.2 Scale strikes

Process each Reaction from First through Break inclusive. The comparison extreme is the last confirmed strike extreme, or Fibonacci level if none. A new pending strike appears when the current High is strictly more directional (larger / maximum) than the comparison extreme. If a still more directional value appears before confirmation, replace the pending strike.

A pending strike confirms when a main candle is `RED`. If a pending strike remains at the Break, inspect lower events up to strict Reaction confirmation and confirm it intrabar only when eligible chronology supports it.

### 7.3 Scale Blue emission

A Scale Blue candidate exists when this Reaction's confirmed strike count is greater than the previous Reaction's strike count. Emit it only if there has never been a Blue, or at least one healthy Reaction has completed since the last Blue. Source = decisive last strike.

Line drawing price: `High - (High-Low)/3`. `sourceExtreme` is the semantic stop extreme; drawing price does not own stops.

### 7.4 Reset Blue

A Reset belonging to a Reaction can create Reset Blue only under the same spacing rule: after an existing Blue there must be at least one healthy Reaction since the previous Blue. Source = Reset main candle. `sourceExtreme = High`. Line drawing price: `High - (High-Low)/5`. `brokenLevel = Reset.brokenLevel`.

### 7.5 Reset Blue double-stop validity

A Reset Blue is `calculation_valid=false` when all are true: a previous Blue exists; the previous Blue's first strict stop in the inspected interval occurs on this Reset's main index; and this Reset candle strictly crosses the previous Blue's semantic source extreme in the direction (`High > level`). Such an invalid Blue is hidden from normal public Blue output but retained as structural evidence for the special double-stop A route.

### 7.6 Internal Blue

Blue is internal if its owning Reaction is internal, or if both its semantic `sourceExtreme` and rendered `linePrice` lie strictly inside the same protected healthy Reaction interior at the relevant time. Drawing offset alone never changes ownership. Internal Blue remains calculation evidence but is filtered from public Blue serialization.

## 8. A engine — Bearish

### 8.1 Blue state and stop

Only calculation-valid Blue Lines enter ordinary Blue states. Blue ordinal is based on sorted calculation lines `(reactionNumber, sourceTime, kind)`.

Scale Blue formation = its owning Reaction Break main index and exact Reaction confirmation event; stop scanning starts at that exact event. Reset Blue formation = Reset source index and the first exact strict lower event crossing its `brokenLevel`; its stop scanning starts at the next main-candle boundary (`source main time + timeframe`).

A Blue stop is the first strict `High > level` against `sourceExtreme`.

### 8.2 Ordinary adjacent-Blue pair

Ordinary A pairs adjacent valid Blue states. A third Blue formation can expire a still-unresolved pair; pair logic must respect that deadline.

The pair's trigger is resolved by `_pair_trigger` semantics:

1. Blue-1 must have a strict stop.
2. Prefer an inherited/chained stop level only when Blue-1 is eligible for carried-stop ownership. In particular, a **Scale Blue that is still live when Blue-2 forms cannot borrow a hypothetical inherited stop** from an intervening Bearish Reaction; its real strict stop chronology must resolve first. Reset-Blue pre-stop structural chaining remains unchanged.
3. Otherwise if Blue-1 stopped before Blue-2 formed, freeze the directional extreme between Blue-1 stop and Blue-2 source, then test crossing during Blue-2 formation; if not crossed, wait for Blue-2's own stop and then the continuation level crossing.
4. If Blue stops overlap or occur after Blue-2 formation, order the two strict stop events. Exact-time tie is deterministically ordered by stop level (`higher` first in Bullish via `-level`, `lower` first in Bearish via `level` in the Source sort key), then trigger at the second stop event; otherwise wait after the second stop for a strict crossing of the first stop event extreme.

The first validating Bearish Reaction must have confirmation `>= triggerEventTime` and First `>= max(Blue1StopTime, Blue2StopTime)`.

### 8.3 Inherited/chained Blue stop

A prior Blue may carry a continuation stop according to `_inherited_stop`. A **Scale Blue** may enter this carried route only after it has actually strict-stopped before the current Blue forms; an open Scale Blue keeps its own `sourceExtreme` authoritative. Once eligible, use the first aligned Bearish Reaction whose First is strictly after the applicable stop window start and whose Break is before current Blue formation. The established Reset-Blue pre-stop structural route is unchanged.

For a **chained** stopped Bearish Blue, the inherited-stop extreme range ends at the **end of the complete next Bearish Reaction Breakout main candle** (`breakTime + timeframe - 1 microsecond`). This exactly mirrors Bullish; the directional extreme is `maximum High` rather than `minimum Low`.

The inherited level is `maximum High` over that exact source interval; its source index/time are preserved. If a chained/inherited level exists, the pair triggers only after Blue-2 formation strictly crosses that inherited level.

### 8.4 A exact-confirmation source ownership

The A candidate opens on the trigger main candle. The validating Reaction confirms the candidate, but prices after exact confirmation in that same Break candle belong to later chronology. Select A `price/source` as the `maximum High` from **trigger main-candle open through exact validating Reaction confirmation inclusive**. Do not use later remainder prices.

### 8.5 Cycle and adjacent reuse

After A is accepted, its validating Reaction Break closes the current Blue pair cycle. Ordinarily Blue states whose formation is at/before that Break cannot immediately restart the same cycle. Adjacent reuse of Blue-2 as the next pair bridge is allowed only if the just-created A itself strictly stops and the next Blue formation is at/after that stop event.

### 8.6 Special double-stop A

An invalid Reset Blue may pair with the most recent preceding valid Blue. On the invalid Blue's formation main candle, the previous valid Blue `sourceExtreme` must be strictly crossed within that candle. That exact crossing is the trigger. The first validating Bearish Reaction must confirm at/after trigger and have First at/after invalid Blue formation. A source is selected using the exact-confirmation rule above.

Special A is removed if it uses a validating Reaction already consumed by ordinary A. A special A can also suppress later ordinary A candidates that reuse its consumed Blue ordinals. A prior ordinary A whose first strict stop belongs to the current special lifecycle can invalidate the special candidate as defined by `_a_was_stopped_before`.

## 9. S engine — Bearish

S begins only after a calculation-eligible A strictly stops on `High > level` against A price. The exact lower event is `aStopEventTime`; its containing main candle is `aStopTime/index`.

### 9.1 Immutable first opposite Order_A after A stop

Select the earliest canonical `Bullish` Reaction whose First main index is not before the A-stop main index and whose exact confirmation is strictly after `aStopEventTime`. Rank by `(confirmationTime, FirstIndex, BreakIndex)`. The first Order is the FINAL Order_A owner of that stopped A; it is never provisional.

Use only that first canonical Order for the stopped-A order-backed S candidate and its decision. No later native Mode-B or Mode-A Reaction can refresh it, even while S is undecided. The later physical Order can survive through an independently valid `parent-stop` or `reset-leg` creation cause; any `accepted-live`/`carried-live` use must preserve its true original creation provenance. The shared accepted-Order stop reconciliation is unchanged.

OrderAudit permanently associates this stopped-A `parent-stop` cause with the first physical Order identity `(FirstIndex,BreakIndex)`. One parent-stop cause cannot move or duplicate. Different independent causes may legitimately share one physical Order. No timestamp-specific exceptions are allowed.

### 9.2 Type-3 S (no new Order before decision)

Before the newly selected opposite Order confirmation (or end of range if none), a pre-existing opposite Reaction may Reset after A stop. Use inclusive owner Break → Reset main geometry to select the directional `High` (last candle wins on equal extreme). Find first strict candidate crossing before the deadline. Type-3 is valid only if at least one Bearish Reaction confirms after A stop and no later than that crossing. Type-3 is always `S Blue`, `formationType=type3`, and carries Reset provenance but no Order geometry.

### 9.3 Type-4 S Blue — aligned-Reaction candidate before any Order

Type-4 is an independent **order-free** S Blue route. It begins only after A has strictly stopped and ends immediately when the first eligible opposite Order confirms. For each same-direction Reaction that confirms after the exact A-stop and before that Order deadline, rebuild the current candidate from the closed main-candle interval **A-stop main candle → that latest Reaction Breakout main candle**. Bearish selects the maximum High; Bullish mirrors with minimum Low. Equal extremes use the maintained candidate helper's last-candle ownership.

After the Reaction confirms, find the first strict directional crossing of that candidate before the next aligned-Reaction confirmation or Order deadline. The candidate becomes valid `S Blue`, `formationType=type4`, only when at least one calculation-valid, non-Internal trend Blue exists from the candidate-source main candle through the exact crossing event; a Blue on the crossing main candle qualifies only if its exact formation is no later than the crossing. If the candidate crosses without a qualifying Blue and no Order has formed, emit no S; the next aligned Reaction rebuilds/transfers the candidate over the same A-stop origin. If an Order forms first, Type-4 exits and ordinary Order-backed S logic owns the handoff.

### 9.4 Pre-Order versus post-Order candidate ownership

The legacy geometry classifier compares A-stop candle directional extreme with the opposite Order boundary. If it says `before`, keep before. If it says `after` and an already-valid nested same-direction Reaction exists inside the Order, preserve `after` so an Advanced S is not stolen. Otherwise compute the actual candidate from the exact A-stop remainder through Order First and resolve the candidate's exact lower formation event. If that event is strictly earlier than Order First main timestamp, classify `before`; equality remains `after`.

### 9.5 Candidate geometry

- Pre-Order Simple candidate: directional extreme from exact A-stop remainder through Order First inclusive; equal extremes in helper variants use the function's declared first/last ownership.
- Post-Order Simple candidate: directional extreme from opposite Order Break through the aligned first subsequent Bearish Reaction Break inclusive; equal extreme is assigned to the **last** candle.
- Advanced candidate: when a complete nested Bearish Reaction exists wholly inside the opposite Order before Order confirmation, source the candidate from the Order's opposite semantic box edge (`BoxBottom source` for Bullish trend, `BoxTop source` for Bearish trend); candidate may decide only from the nested trend confirmation onward.

### 9.6 S decision race

Start at Order confirmation and inspect lower events chronologically. Candidate strict cross uses the Bearish directional extreme (`High > level`). `Order is Bullish, so stop crosses on Low < orderStopLevel`.

At each lower event:

1. if candidate and Order stop both strictly cross in that same event: candidate is invalid, return no S;
2. else if Order stop crosses first: `S Red`;
3. else if candidate crosses and either its aligned Reset Blue has formed by that event **or** any ordinary Bearish Reaction confirmed after active behavior start and no later than the event: `S Blue`;
4. in pre-Order Simple provisional mode only, an unqualified candidate cross returns `fallback`, abandoning the pre-Order ownership and re-evaluating the normal post-Order Simple/Advanced route.

If no lower data is available, the same logic is applied on main candles, preserving strictness and branch order.

For Red S, unless a valid pre-Order candidate explicitly owns the Red source, recompute S source/price from the directional extreme over Order Break main candle through Red decision main candle inclusive.

### 9.7 A-to-S ownership windows

Once A strictly stops, S opens an ownership window. A candidates whose own trigger began at/before that A-stop boundary remain part of the handoff and cannot re-enter as fresh A. A whose trigger begins strictly after the boundary may be independently eligible but still faces global behavior hierarchy. After S decision, the window ends just after the exact decision event.

A special fresh Reset-Blue/Reset-Blue A pair can preempt an already-decided S ownership window only under the exact conditions implemented by `_a_owned_by_s`: both Blues born after S ownership begins, Blue-1 stops before Blue-2 forms, A source equals Blue-2 stop main time, and both pair members are Reset Blues. This is a structural route, not a hierarchy bypass.

### 9.8 Shared accepted Order-stop reconciliation

An already-open S candidate may be decided Red by **any calculation-accepted physical Order**, regardless of which A/S/E/StopAll/Order_B originally created that Order. Parent identity is not an eligibility requirement.

Deduplicate accepted Orders by physical `(FirstIndex,BreakIndex)` identity and prefer the richer accepted ledger entry when it already carries exact `stop_cross` chronology. For each S candidate:

1. Resolve the accepted Order's exact confirmation and strict Order-stop event using the canonical mirrored Order stop rule.
2. The Order may have confirmed **before** the S source and remained live, or it may confirm **after** the S source. Both are valid.
3. Require `orderConfirmation < orderStopEvent` and `S.sourceTime <= orderStopEvent < S.currentDecisionEventTime`.
4. Do **not** require the Order's creation parent to equal the S candidate's parent and do not impose a later parent-specific terminal confirmation boundary.
5. Rank eligible Orders by `(orderStopEvent, confirmationTime, FirstIndex, BreakIndex)`; the earliest exact strict Order stop wins.
6. Freeze the existing S source/time/price. Replace only the S family with Red, the winning Order provenance, and the exact decision chronology.

`accepted-live`/shared use never rewrites Order creation provenance. The physical Order keeps its original accepted `parent-stop` and/or `reset-leg` cause in OrderAudit. Arbitrary opposite Reactions that were never accepted as physical Orders are never promoted by this rule.

## 10. E engine — Bearish

E recursively consumes accepted S and E parents. E uses the same `high` directional stop semantics and opposite `Bullish` Order geometry.

### 10.1 Parent strict stop

For an S/E parent, find the first strict `High > level` of its `price` starting from the parent's relevant source/decision chronology. The exact lower event and containing main index are parent-stop provenance.

### 10.2 Order routes

E Order resolution is physical-Order based. Four use routes can participate in the same E decision race, all keyed by `(FirstIndex,BreakIndex)`:

- **parent-stop/direct Order_A cause** — a new opposite Bullish Order created directly because the current accepted parent strictly stopped;
- **carried-live accepted Order** — an already accepted Order that confirmed before the current parent stop and is still live at that stop;
- **post-stop accepted-live Order** — an already accepted physical Order whose exact confirmation occurs after the current parent stop. Its creation parent may be A, S, E, StopAll, or independent Reset-leg/Order_B structure; it does **not** have to equal the candidate parent;
- **Reset-leg Order_B cause** — the canonical same-direction Bearish Reset-leg formation described below.

`Order_A`/`Order_B` are creation causes, not native Reaction modes. `carried-live` and `accepted-live` are **use provenance only**. They never relabel the physical Order's original accepted creation cause in OrderAudit.

For a post-stop accepted-live Order to participate, its exact confirmation must be strictly after the current parent stop, its own strict Order stop must occur strictly after confirmation, and no hard sequence reset/StopAll boundary may lie in `(parentStopEvent, orderStopEvent]`. Bullish/Bearish use the same chronology rule; only the canonical strict Order-stop price comparison mirrors.

All routes enter the same stop-event race. One exact parent-stop creation cause still belongs to only one physical Order; sharing an already accepted Order as confirmation does not consume or duplicate its creation provenance.

### 10.3 Canonical Order_B Reset-leg formation — Bearish

Order_B is built from a **Bearish Reaction Reset**, not from a Bullish/opposite Reset:

1. Take one Bearish Reset and resolve its owning Bearish Reaction through `from_first_idx`.
2. From the owner Reaction's **Breakout main candle through the Reset main candle, inclusive**, find the **minimum Low**. This is the Reset-leg floor / trigger level. The first main candle that owns that minimum is the floor-source candle.
3. Starting at the exact Reset event, scan lower-timeframe data for the first strict `Low < floor`. Equality does not qualify. Preserve both the exact lower event and its containing 30s/main candle.
4. Define the evidence interval as the **closed main-candle range from the floor-source candle through the strict-break main candle, inclusive**.
5. In that closed interval, require at least one **raw Bullish Reaction geometry**. Geometry alone is sufficient: normal Reset validity, lifecycle acceptance, public visibility and Internal-Reaction status are deliberately ignored for this evidence test.
6. Over the same closed interval, compute the **maximum High**. This is the Reset-leg ceiling. The first candle that owns the maximum is retained as its source.
7. After the strict-break gate, select the **first canonical Bullish Reaction** whose First belongs to the gate main candle or a later main candle and whose exact confirmation is strictly after the exact lower-timeframe floor break. That canonical Reaction is the physical `Order_B`.
8. Store Order_B cause provenance as `reset-leg(resetTime, boundaryBreakTime)`, where the legacy public field `boundaryBreakTime` now means the exact strict break of the Reset-leg **floor**. If the same physical Order has several valid Order_B origins, the latest valid `(resetTime, strictBreakEventTime)` is authoritative in final OrderAudit.

The scoped lifecycle rule remains separate from formation: after cause merging, an internal native Mode-B Reaction whose only accepted causes are Reset-leg can be filtered from public Order ownership. That filter does **not** change the geometry-only evidence rule above, and a valid parent-stop cause on the same physical Order is not erased.

### 10.4 Canonical Order stop

Use the shared Reaction chronology's canonical Order stop rule from §6.12. Never reimplement a different S/E stop rule.

### 10.5 E source, shared accepted Order confirmation, and decision

For each stopped parent, E may use a direct/inherited/carried Order or a parent-neutral accepted-live Order. An Order confirming the E does **not** need to have been created by the same parent.

The accepted-live ledger is composed from calculation-accepted stopped-A Orders plus accepted S/E/StopAll/Order_B physical Orders already present in canonical OrderAudit. A post-stop accepted Order is eligible only when its confirmation is after the parent stop, its strict Order stop is later than both confirmation and parent stop, and no hard sequence reset occurs between the parent stop and that Order stop.

Representatives with known strict Order stops compete by exact stop chronology; earliest Order stop wins, with deterministic First-index tie handling. The E source is then the directional `maximum High` over the complete main-candle interval from the parent-stop main candle through the winning Order-stop main candle, inclusive. Lower-timeframe data decides **when** stops happen; it does not truncate either boundary main candle's OHLC.

`accepted-live` is use provenance only. Final OrderAudit must restore/preserve the winner's original accepted creation cause from the prior accepted ledger or stopped-A ledger. If no original accepted creation cause can be proven, the system must not fabricate one.

### 10.6 Recursive chains

A stopped S can open E1. A stopped E can recursively open E(n+1). Recursive search ends if no valid Order/zone exists, a source would repeat, or a hard sequence reset/StopAll boundary lies between parent and child.

Consumed non-public S evidence may continue an already-stopped larger E. In that case the first child inherits the larger E's reconciled family and `number+1`; subsequent descendants are rebuilt natively from the promoted E. If this continuation decides earlier than an existing descendant branch, replace the later descendant branch without deleting unrelated E lineages.

### 10.7 Family and number reconciliation

Candidate discovery may produce competing Red/Blue lineages. Reconciliation maintains active accepted E state chronologically. Important invariants:

- family follows the accepted stopped parent when that parent is active;
- a still-unbroken Red S can supersede Blue E, but S does not supersede active Red E;
- Red behavioral priority is higher than Blue and is applied **before** chronology can discard a same-source Red candidate;
- when accepted parents are stopped, new number is `max(stopped same-family number)+1`; otherwise a new family/root begins at 1;
- StopAll sequence reset boundaries clear active E continuation and may retype a child parent as `StopAll` for lineage semantics;
- a lower-priority event remains valid evidence/output where allowed but cannot replace/separate the active dominant sequence.

### 10.8 Same-source E conflict

Exactly one accepted E behavior may own physical `(sourceIndex,sourceTime)`. Red E outranks Blue E regardless of number. Within a family, higher number outranks lower. Exact tie preserves first accepted provenance. Final E list is sorted by `(sourceTime,sourceIndex,decisionEventTime)`.

### 10.9 Independent S roots

After dominant E reconciliation, calculation-valid direct E1 roots of accepted S can be restored so independent E formation is not erased by dominance. However an S whose own physical source is already owned by accepted E is not kept alive to manufacture a competing later E1.

### 10.10 Invalid-A / invalid-S exact same-source cross-family root rule (E 6.6.2)

An S whose parent A later becomes calculation-invalid is retained as geometry, OrderAudit, and continuation evidence. It is **not** globally deleted before E. However, if that invalid S has exact identity `(sourceTime,sourceIndex)` equal to a native accepted E continuation and the invalid S would open a competing **different-family** E1 root, suppress that cross-family root. Same-family continuation/evidence remains allowed.

This rule prevents a provisional same-source S from retroactively recoloring a valid E continuation while preserving Order provenance and all unrelated S/E behavior.

## 11. OrderAudit contract

OrderAudit is identity-based, not cause-based. One physical Order `(FirstIndex,BreakIndex)` can have multiple accepted causes, and `Order_A`/`Order_B` cause classification is independent of native Reaction `mode`.

1. Merge stopped-A audit and E audit entries by physical identity.
2. Filter A causes to calculation-accepted A sources.
3. Resolve/retain exact strict Order stop crossing (`stopHit*`) from canonical Reaction stop geometry.
4. One exact parent-stop provenance `(parentType,parentFamily,eventTime,parentSourceTime)` may be consumed by only one physical Order: the earliest ranked by `(confirmationTime,FirstIndex,BreakIndex)`. A later Order may remain only if it has another independent cause such as Reset-leg/Order_B.
5. For Reset-leg/Order_B, only identities already relevant to accepted S/E/A Order state are enriched into final OrderAudit. If the same physical Order has several valid Order_B origins, keep the latest `(resetTime, strictBreakEventTime)` cause and remove older Reset-leg causes for that identity.
6. After causes are merged, keep the existing narrow lifecycle filter: reject a behavior-internal physical Order with native `mode=B` only when every surviving cause is Reset-leg. A valid parent-stop cause on the same identity prevents this Reset-leg-only rejection.

The public `boundaryBreakTime` field name is retained for compatibility. In V5.2.0 Reset-leg causes it is the exact lower-timeframe strict break of the primary Reset-leg trigger extreme (Bearish floor / Bullish ceiling), not the old opposite-Reset boundary semantics.

`carried-live` and `accepted-live` are use provenance only and are never serialized as replacement creation causes in OrderAudit. Original accepted parent-stop/reset-leg causes are recovered from the accepted ledgers; if none can be proven, no cause is fabricated.

OrderAudit uses full-RAW accepted A provenance. Presentation clipping cannot delete an Order identity required by a public S/E/StopAll inside the requested range: `prepare_order_audit(..., required_identities=...)` keeps those referenced identities even if their Order First lies before `start_index`.

## 12. Lifecycle hierarchy and calculation eligibility

The global priority is invariant and **does not mirror**:

`StopAll (5) > E Red (4) > S Red (3) > E Blue (2) > S Blue (1) > A (smallest)`.

A/S/E/StopAll native detection may proceed independently, but final calculation eligibility is resolved by strict-stop chronology and this hierarchy.

### 12.1 A after stopped behavior and stage-order ownership

The lifecycle stage order is invariant and **must be respected before cross-family priority is allowed to act**:

`A → S → E → StopAll`.

For each accepted S/E/StopAll strict stop, assign the transition to the containing main candle. When evaluating a later A, choose the most recent relevant stopped transition first; priority/number only resolve owners stopped on that same transition. If A price is not strictly beyond the dominant stopped owner's price in the trend direction, A remains valid. If it is strictly beyond, it is the equal/lower leg-head candidate and is normally calculation-invalid.

A is also the smallest owner for A→A: if new A `triggerEventTime <= previous A strict-stop event`, it overlaps the old transition and is invalid; if its trigger starts strictly after that stop, the old A does not block it, subject to all later-stage owners.

**Accepted-S stage lock:** when the dominant owner is S and a fallback A is rejected by this equal/lower cycle rule, that rejected A must **not consume the S owner**. The accepted S remains authoritative for the current transition. Otherwise the pipeline can incorrectly reopen `A → S` behind an already accepted S and fabricate a second S branch in the same lifecycle.

Only A identities rejected specifically by this S-stage lock are marked `stage-invalid`. Any S candidate whose `a_source_time` belongs to such a stage-invalid A is calculation-invalid for later E/StopAll ownership and is removed from accepted S. It may not create a new E root, change E family/number, or replace the already accepted S/E chain. Cycle validation must receive **every S-eligible A identity**, not only A objects currently visible after provisional S suppression. A temporarily hidden by an S candidate cannot bypass the cycle check and later resurrect when that provisional S is reconciled away.

The historical interior-leg provenance exception remains unchanged for the cases where it actually qualifies under the existing source logic; V5.4.0 does not globally remove that mechanism. The new rule is narrowly about an A that has already been rejected under **S ownership**: that rejected A cannot advance/consume S and its S descendants cannot re-enter later stages.

This rule is direction-invariant. Bullish/Bearish mirror only price geometry; stage ordering and lifecycle ownership do not mirror.

### 12.2 S after larger-module stops

An active larger behavior does not automatically disable internal A/S calculation. Once the currently relevant larger module and candidate S's parent A have stopped before S ownership event, compare current lifecycle ownership. Higher-priority new S may supersede a stopped lower-priority S. Equal/lower S that becomes the strict next directional leg extreme is consumed under the closed transition rules. Older historical modules before a newer external E/StopAll source do not own the newer lifecycle forever.

### 12.3 Same-source S versus E for module engines and StopAll

If S and accepted E occupy the same physical `(sourceIndex,sourceTime)`, E owns that source for larger-module/StopAll participation. The losing S may remain lineage/evidence where explicitly needed but must not separately create sequence grouping.

## 13. StopAll engine

StopAll consumes lifecycle-visible S and reconciled E chronologically. The invariant priority table remains `S Blue=1`, `E Blue=2`, `S Red=3`, `E Red=4`; Red/Blue labels never mirror by market direction.

Maintain the exact current dominant S key/count and E key/count for the existing E-driven `sequence-group-stop` rule. **Separately**, maintain pending Blue-repeat counters keyed by accepted behavior group: `S Blue` is one key regardless of subtype, while each numbered Blue E is a separate key (`E1 Blue`, `E2 Blue`, `E5 Blue`, ...). Blue occurrences increment their exact key regardless of current dominance, but an accepted Red S or E resolves the pending Blue reversal and clears only these Blue-repeat counters. A hard StopAll resets both the pending counters and all active owner state. Different E numbers never add together.

When an accepted `S Red` arrives, evaluate its forming Order mode and pending exact-key Blue repeats **before** ordinary S replacement. A native Mode-B Order plus any exact Blue group with `count >= 2` promotes that S Red to StopAll with `gateType='opposite-s-group-stop'`. Otherwise, retain it as S Red and clear pending Blue evidence, even if its Order is Mode A or absent; a later S cannot reuse the resolved Blue group. An accepted Red E likewise clears pending evidence after independent `stopall-stop` and `sequence-group-stop` checks. No extra latest-Blue stop/dominance condition exists, and multiple qualified groups use the latest accepted occurrence for deterministic metadata. E-driven StopAll state is not cleared by an ordinary Red S/E.

Before each E decision: ingest earlier S events; strictly stop active StopAll objects and, if one stops, create the next numbered StopAll from the current E (`stopall-stop`); otherwise preserve the same-key E/S `sequence-group-stop` gate; if no StopAll is created, update the active E key/count under the priority table. Any accepted StopAll is a hard boundary: all active S/E exact-key owner state and all pending Blue-repeat counters reset to zero.

Bearish strict stops use `High > level`; Bullish mirrors with `Low < level`. StopAll chronology and key-count semantics themselves are direction-invariant.

## 14. Final visibility and lineage closure

1. Initial visible A excludes source indexes occupied by final S and excludes the S-stop transition main candle.
2. Detect/reconcile StopAll from lifecycle-visible S/E.
3. Restore independent accepted S E1 roots without rewriting dominant StopAll sequence.
4. Apply final behavior visibility: StopAll source index suppresses E on same source; final E/StopAll source indexes suppress A and S labels on same source.
5. Preserve lineage: if final E references an S parent, keep that historical S only when it was calculation-eligible; if final S references an A parent, keep that A history unless its source is occupied by E/StopAll.
6. After all lifecycle, StopAll, Internal-Reaction, and OrderAudit ownership is fixed, append eligible presentation-only historical E rescues. These objects must not feed back into StopAll, active ownership, numbering, family/color reconciliation, S/A visibility, or OrderAudit provenance.
7. Remove calculation-invalid S identities from final S.
8. Remove S descendants of an A marked stage-invalid by accepted-S ownership. Such S candidates are not continuation evidence and cannot be used to build a later E root.
9. A provenance that straddles the strict stop of the dominant current module is removed unless it rebuilt entirely after the boundary according to `visible_a_zones_after_module_boundaries`.
10. Internal-Reaction filtering hides **only** forbidden internal native-Mode-B E/StopAll Orders whose surviving Order causes are Reset-leg-only. A/S and other E/StopAll are not hidden merely because their source point lies inside a healthy Reaction interior.
11. Public Blue output contains only `calculation_valid=true` and `behavior_internal=false` Blue Lines.

## 15. Direction-specific mirror table

| Concept | Bullish | Bearish |
|---|---|---|
| Directional extreme/stop | Low, strict `<` | High, strict `>` |
| First Reaction color | RED | GREEN |
| Context color | GREEN | RED |
| Reaction confirmation | High `>` BoxTop | Low `<` BoxBottom |
| Better source extreme | minimum | maximum |
| Fibonacci | `Top - .618*(Top-ref)` | `Bottom + .618*(ref-Bottom)` |
| Scale line | `Low + range/3` | `High - range/3` |
| Reset line | `Low + range/5` | `High - range/5` |
| Opposite Order | Bearish | Bullish |
| Mode-B Order stop | previous BoxTop | previous BoxBottom |
| Candidate/behavior stop | Low `<` price | High `>` price |

**Exact mirror rule:** A chained stopped Bearish Blue uses the complete next Bearish Reaction Breakout main candle (`breakTime + timeframe - 1 microsecond`) and freezes the `maximum High`. Bullish uses the identical time window and freezes the `minimum Low`.



## 15A. Exact full-pipeline reconstruction sequence

The following pass order is **normative**. A rebuild that computes the same local detector candidates but changes these reconciliation passes can produce different final behavior. In particular, a later-stage accepted owner cannot be consumed merely because an earlier-stage fallback candidate was rejected.

```text
prepare_market_context:
    parse complete RAW
    build exact-second candles and selected-timeframe candles
    build one shared lower-timeframe index
    compute visible start/end indexes only for later serialization

prepare_pipeline_state:
    build bounded stopped-A Order geometry finder for Bullish and Bearish
    if any behavior module is enabled:
        calculate BOTH Bullish and Bearish full-RAW Reaction/Reset streams
        classify cross-direction Internal Reactions
    if E engine exists and S is enabled:
        for each requested output direction:
            calculate_full_direction_state(direction)

calculate_full_direction_state(bearish):
    Blue = detect_blue_lines(direction, trend Reactions, trend Resets)
    A = detect_a_zones(direction, trend Reactions, Blue)
    S_detector = SZoneDetector(trend Reactions, opposite Reactions/Resets, Blue, A)
    S_candidates = S_detector.detect()

    E_detector(initial S_candidates, initial stopped-A OrderAudit)
    E = E_detector.detect()

    valid_S = lifecycle.s_zones_for_module_engines(S_candidates, E)
    if valid_S differs:
        rebuild E using valid_S
        block Order First times belonging to removed S candidates

    candidate_A = lifecycle.visible_a_zones(S_detector.eligible_A, valid_S)
    candidate_A = lifecycle.visible_a_zones_after_s_stops(candidate_A, valid_S)

    stage_invalid_A = empty identity set
    calculation_A, invalid_A = lifecycle.split_a_zones_by_dominant_stops(
        ..., stage_invalid_a_identities=stage_invalid_A
    )
    invalid_S = every original S candidate whose a_source_time is any invalid_A source

    stage_invalid_S = every original S candidate whose a_source_time is a stage_invalid_A source
    remove stage_invalid_S from currently accepted S

    accepted stopped-A Orders, blocked First times = lifecycle.resolve_order_context(...)
    rebuild E with:
        accepted stopped-A Orders
        blocked Order First times
        invalid_S_root_identities

    reconcile open S against later accepted physical Order stops
    if any S provenance/decision changed:
        rebuild E once more with reconciled S

    calculation_S_candidates = S_candidates excluding stage_invalid_S
    find suppressed lower-priority S evidence from calculation_S_candidates
        that belongs to a stopped larger E
    for each such S evidence:
        build native continuation chain from the E owner
        replace only the owner's later descendant branch if new continuation decides earlier

    remove invalid_S from accepted S list (retain non-stage-invalid originals only where existing lineage/evidence rules require them)
    store full-range Blue/A/S/E detector state

finalize_direction_visibility:
    rebuild visible A against accepted S
    if StopAll enabled: detect StopAll ONCE from reconciled E + StopAll-eligible S
    restore independent S-owned E1 roots without rewriting StopAll history
    finalize A/S/E lineage visibility and same-source occupancy
    mark/hide public internal Blue
    apply scoped internal native-Mode-B Reset-leg-only Order prohibition to E/StopAll
    prepare and deduplicate OrderAudit
    only now filter objects to requested presentation indexes
    serialize
```

### Why the repeated E passes exist

E depends on accepted S, accepted Order provenance, invalid A/S ownership, stage-invalid S descendants, and shared Order-stop decisions. Each pass resolves one dependency. Do not collapse these passes into one speculative E run unless an alternative implementation proves the same fixed inputs and exact output. StopAll is deliberately **not** in a global E↔StopAll fixed-point loop; its accepted prefix is historical and immutable once formed.

## 15B. E Order creation and shared accepted-Order confirmation — function-level

### Parent stop / direct Order_A route

For any S/E parent, strict parent stop is the first lower-timeframe `High > parent.price` from the applicable source/range start. The first lower event owns `parentStopEventTime`; map it to a main candle for `parentStopIndex/Time`.

Direct parent-stop search remains separate from Order_B. `_direct_parent_stop_order` and the narrow fresh-trend continuation route may produce a `parent-stop` creation cause. One exact parent-stop provenance can be spent by only one physical Order; `_enforce_single_parent_stop_owner` keeps the earliest `(confirmationTime,FirstIndex,BreakIndex)` owner and strips that cause from later identities unless another independent cause survives.

### Carried-live accepted Orders

`_carried_orders_for_parent(parent,parent_stop)` preserves accepted Orders already live inside the current parent lifecycle. Their original creation cause is retained in the ledger; `carried-live` is only use provenance.

### Post-stop parent-neutral accepted Orders

`_post_stop_accepted_orders_for_parent(parent,parent_stop)` closes the systemic gap fixed in E `6.8.0`:

1. Parent identity is deliberately ignored for eligibility.
2. Scan both accepted stopped-A `initial_order_audit` and the current accepted physical `order_audit` ledger.
3. Deduplicate by physical Reaction identity `(FirstIndex,BreakIndex)`.
4. Require exact `confirmationTime > parentStopEventTime`.
5. Resolve canonical strict Order stop. Require `orderStopEvent > confirmationTime` and `orderStopEvent > parentStopEventTime`.
6. Reject the shared use if a hard sequence reset/StopAll lies in `(parentStopEventTime, orderStopEvent]`.
7. Rank physical Orders deterministically by `(orderStopEvent, confirmationTime, -FirstIndex)` for the representative list.
8. Emit use provenance `accepted-live`; if the physical Order also has accepted Reset-leg provenance, retain `reset-leg` alongside the use marker.
9. Never create a new parent-stop cause for the current candidate. Final audit recovers the physical Order's original creation provenance from the accepted ledgers.

The implementation is direction invariant. `_cross_order` supplies the exact mirrored price rule for the opposite Bullish Order.

### `OrderBFormation` — canonical Reset-leg state

The E engine precomputes canonical Order_B formations with `_build_order_b_formations()`. Each formation stores Reset time/index, owning Bearish Reaction First/Break indexes, trigger level and source, exact strict-break chronology, the mirrored other-edge extreme/source, raw opposite-geometry identity, and the final canonical Bullish Order Reaction/confirmation.

### Order_B Step 1 — same-direction Reset owner and trigger extreme

`_order_b_reset_leg(reset, reset_time)` resolves the Reset's owning **Bearish Reaction** through `from_first_idx`. Over the closed main-candle interval `owner.break_idx .. reset.index`, `_main_range_extreme` takes the **minimum Low**. This is the Reset-leg floor; equal extrema preserve the earliest owning main candle.

### Order_B Step 2 — exact strict break

`_order_b_strict_break(reset_time, level)` begins at the exact Reset chronology and finds the first strict `Low < floor`. Equality never qualifies.

### Order_B Step 3 — closed evidence interval and mirrored other edge

Evidence is exactly the closed main-candle range `primary-extreme source .. strict-break main candle`, both endpoints inclusive. `_order_b_opposite_extreme(...)` computes `maximum High` over the same closed interval.

### Order_B Step 4 — raw opposite Reaction geometry only

`_order_b_geometry_evidence(...)` searches bounded raw Bullish Reaction geometry only. Normal Reset validity, lifecycle acceptance, public visibility and Internal-Reaction status are not required for this evidence test.

### Order_B Step 5 — physical Order_B after the gate

`_first_order_b_reaction_after_break(...)` selects the first canonical Bullish Reaction whose First belongs to the gate main candle or later and whose exact confirmation is strictly after the exact lower-timeframe gate event. That canonical Reaction is the physical Order_B; its native mode can be A or B.

### Order_B Step 6 — cause ownership and latest-cause rule

`_order_b_orders(start)` exposes canonical Order_B physical Orders. `_order_b_evidence(...)` and `_enrich_order_audit_reset_causes()` retain only the latest valid `(resetTime,strictBreakEventTime)` Reset-leg cause on one physical Order.

### Shared E decision race

Direct, inherited, carried-live, post-stop accepted-live, and Reset-leg-capable physical Orders all reduce to Order matches with exact strict stop chronology. Only physical Orders accepted by their own creation path can enter shared accepted-live use; arbitrary opposite Reaction geometry cannot.

The winning Order is the eligible representative with the earliest exact strict Order-stop event under the current continuous/hard-reset deadline. Its parent does not have to match the E candidate parent. Sharing never consumes a second parent-stop creation cause and never rewrites the Order's original owner.

### Scoped internal-Order visibility rule

Order_B formation itself does not reject internal geometry evidence. Later lifecycle/OrderAudit preparation keeps the narrow filter: a physical Order whose native Reaction `mode=B` is behavior-internal is rejected only when every surviving creation cause is Reset-leg. A valid parent-stop creation cause on the same identity prevents that Reset-leg-only rejection. `accepted-live` is use provenance and does not count as a new creation cause.

## 15C. E zone construction and recursive chain contract

### Direct / inherited / carried / accepted-live representatives

For an S parent there may be an explicitly unconsumed inherited Order. For any parent there may be an already-live carried Order and a post-stop accepted-live Order from the accepted physical Order ledgers. A direct Order remains the normal fresh parent-stop/Order_B search route.

The post-stop accepted-live representative is parent-neutral: it may have been created by A, S, E, StopAll, or Reset-leg/Order_B, provided it is already calculation-accepted and no hard reset lies between the candidate parent stop and its strict Order stop.

Candidate representatives with known strict stop crossings compete on exact chronology. Earliest strict Order stop wins; deterministic confirmation/First ordering resolves ties. Use provenance never overwrites creation provenance.

### E decision/source

`decisionEventTime = max(parentStopEventTime, winningOrderStopEventTime)`. Map to its main candle for decision index/time. Source ownership is complete-main-candle based: include the main candle containing the parent stop through the main candle containing the winning Order stop, inclusive, and select `maximum High`. Lower-timeframe chronology decides stop order but never truncates boundary-candle OHLC.

### Provisional chains

### Provisional chains

Before recursive chain discovery, register stopped-S Order opportunities so Orders formed during an E parent lifetime remain available. Every fully formed S with a strict stop opens a provisional E chain:

```text
family = S.color
number = 1
parent = S
while parent has valid E zone and sourceIndex not repeated in this chain:
    append zone
    if zone has no strict stop: break
    parent = zone
    number += 1
```

### Invalid-S-root collision (current E 6.13.0; behavior preserved from the earlier implementation)

After all provisional chains exist, collect physical identities of E zones whose parent is E, grouped by family. For every S identity marked invalid because its A parent failed final lifecycle eligibility: if that exact `(sourceTime,sourceIndex)` already has an E-parent continuation of a **different family**, block the **entire provisional chain rooted at that invalid S**. Do not block when continuation family is the same. The S remains available to OrderAudit/evidence elsewhere.

## 15D. E reconciliation — exact ownership rules

Group candidate zones by `sourceIndex`, order groups by earliest `(sourceTime, decisionEventTime)`, and maintain:

- `numbered`: historical accepted output;
- `active`: currently active E owners only; a stopped owner is removed from active but remains historical;
- `sequence_start`: hard StopAll reset source time, if any.

### Candidate Order validity

A candidate is invalid if `_blocked_by_gate_owned_order` says a later nested direct Order_A lost to a gate-owned initial Order. Additionally, an E-parent Blue candidate carrying `reset-leg` / Order_B provenance may be invalidated when its child source is also reachable from an S-owned candidate that decides no later than that child. Primary reconciliation keeps this legacy ownership rule unchanged. Historical-output preservation is handled separately: an E-parented Blue `Order_B` that was accepted during an earlier authoritative E pass may be retained for presentation when a later pass removes it, but only if it is not merely a hidden intermediate parent of a surviving final E and no higher-priority final E remains active through the candidate decision. This rescue never re-enters calculation ownership.

### Parent active

For S-parent candidate:

- find exact S parent; reject if absent;
- reject if S or its A source is at/before hard `sequence_start`;
- if no prior numbered E in current sequence, parent is active;
- otherwise S can reopen only when rebuilt after the latest E (`S.source > priorE.source` and `S.a_source >= priorE.source`) or when a still-unconsumed Red S owns a transition over a prior Blue E under the source condition.

For E-parent candidate: parent is active if it is the hard sequence-start source, is present in `active`, or can recursively trace through a skipped parent that was invalid only by Order logic without creating a cycle.

### Does candidate stop an active E?

Only when candidate decision occurs strictly after prior decision and `new.price > prior.price`.

### Prevent lower-priority S stealing active continuation

A candidate directly from S is removed when it stops an active owner and that owner is Red or candidate family is Blue, **and** that owner has an E child whose decision is no earlier than the S candidate's decision. Red S can supersede Blue E; no S supersedes active Red E.

Also suppress an E-parent Blue candidate if a later Red S source exists after its parent and that Red S decision occurs before the candidate parent's stop event.

### Choose winner at one physical source

Compute ownership priority from active parent family when parent is E, otherwise candidate family. Pick minimum key:

`(-behaviorPriority, decisionEventTime, parentStopEventTime)`

So Red-family behavioral priority is resolved **before** chronology; chronology breaks ties within equal priority.

If winner's stated E parent is not active but accepted Reset evidence exists for the winner's physical Order, rewrite its Order provenance to Reset-leg only.

### Assign accepted family/number

Let `parent_family` be active E parent's reconciled family when available, else candidate family. Partition active owners strictly stopped by winner into Red/Blue. Then:

```text
if parent_family == red:
    family = red
    number = max(stopped red numbers)+1 if any else 1
elif any stopped red:
    family = red
    number = max(stopped red numbers)+1
elif parent_family == blue:
    family = blue
    number = max(stopped blue numbers)+1 if any else 1
elif any stopped blue:
    family = blue
    number = max(stopped blue numbers)+1
else:
    family = candidate.family
    number = 1
```

Remove every strictly stopped active owner from `active`, append numbered winner. If winner source time is a StopAll sequence reset, clear active and set `sequence_start`; otherwise add winner to active. The detector may record future-conflict historical rescue evidence, but such evidence is presentation-only. Across the pipeline's repeated E passes, accepted E-parented Blue Reset-leg/Order_B history is accumulated; after the final E calculation pass, missing earlier accepted history is eligible for public rescue only when it is not a hidden parent of a surviving final E and is not dominated by a higher-priority final E that remains active through its decision. If an E child points to an E source that is a sequence reset, publish `parentType=StopAll`.

### Final same-source conflict resolver

Key=`(sourceIndex,sourceTime)`. Higher `sequence_priority('e', family)` wins (Red over Blue); same family higher number wins; exact tie keeps first object. Sort final by `(sourceTime,sourceIndex,decisionEventTime)`.

## 15E. Lifecycle function-level reconstruction rules

### `s_zones_for_module_engines`

Walk S by source time against prior accepted E + prior kept S. If newest prior module has priority >= incoming S and incoming A source predates that module, reject. Otherwise compare both incoming `a_price` and S `price` against prior module price using strict Bearish boundary; if either is strictly beyond, reject. Higher-priority incoming S is allowed to supersede lower-priority prior behavior.

### `s_zones_for_stopall`

Start with `s_zones_for_module_engines`; additionally remove S whose exact `(sourceIndex,sourceTime)` is occupied by accepted E.

### Invalid leg-head Order block

For each calculation-invalid A that still has a future strict stop, block opposite Reaction First times in `[invalidA.sourceTime, invalidA.stopEvent)`. An accepted stopped-A Order First is removed from this block because accepted calculation ownership is authoritative.

### `consumed_s_evidence_after_larger_stop`

Among original S candidates removed from accepted S:

- find latest prior E before candidate A source;
- require candidate priority < E owner priority;
- require E exact stop strictly before candidate A source;
- require candidate A to form strictly after that stop;
- compare Close of E-stop main candle to Close of candidate S source main candle and require strict Bearish continuation beyond it;
- keep only earliest such suppressed S per E owner.

That S becomes non-public continuation evidence via `continuation_chain_from_s`.

### `split_a_zones_by_dominant_stops`

Build stopped-owner records from S/E/StopAll and, when provided, A strict stops. Each record owns exact stop event + containing main index. For each A in source order:

1. collect unconsumed owners whose source precedes A and whose stop main index is not after A source;
2. for A→A owner, ignore old A if new `triggerEventTime` is strictly after old A stop; otherwise old transition still overlaps;
3. choose dominant primarily by **latest stop main index**, then behavior priority, number, source time/index;
4. if A price does not strictly cross dominant price in the trend direction, keep A;
5. apply the existing interior-leg provenance test exactly as implemented;
6. otherwise mark A calculation-invalid;
7. **if the dominant owner is S, do not consume that S.** Record this rejected A identity in `stage_invalid_a_identities` and leave S as the authoritative owner of the transition;
8. only for non-S dominant owners, consume eligible stopped owners with priority <= dominant priority as before.

After this function returns, derive `stage_invalid_s_identities` from S candidates whose `a_source_time` belongs to a stage-invalid A. Remove those S descendants from accepted S before final E rebuilding, and exclude them from `consumed_s_evidence_after_larger_stop`. This is the exact enforcement of the normative `A → S → E → StopAll` pass order: a rejected fallback A cannot reopen A/S calculation behind an accepted S.

This V5.4.0 change is deliberately scoped. It does not alter Reaction, Blue, A geometry, S decision geometry, Order_A, Order_B, accepted-live Order sharing, or E source geometry.

### `visible_s_zones_after_module_resets`

Walk S chronologically. Determine S ownership event from exact candidate source event when available. Restrict historical external owners to the current lifecycle beginning at the newest prior E/StopAll source. Consider only owners whose strict stop is <= S ownership event. For lower-priority S versus latest external owner, a strict Close continuation beyond that external stop-main Close can consume/reject it under source logic. Dominant stopped owner is selected by latest exact stop event, then priority/number/source. Higher-priority S vs stopped S can supersede. Otherwise if S price is not strictly beyond dominant price, keep; if strictly beyond, consume lower/equal stopped owners and reject this immediate re-entry.

### `visible_a_zones_after_module_boundaries`

For A with prior stopped S/E: choose dominant stopped prior. If any provenance time among `(blue1Source, blue2Source, continuationSource, validatingReactionFirst)` begins before the dominant exact boundary event, the A straddles the old lifecycle and is hidden.

### Final lineage closure

StopAll source indexes remove E at same source. Final E/StopAll source indexes occupy the main candle over A/S. Historical S referenced by accepted E is restored for lineage; historical A referenced by accepted S is restored for lineage, then same-source E/StopAll occupancy still wins. Calculation-invalid S identities never return to final public S.

## 15F. StopAll exact state machine pseudocode

```text
s_key=None; s_count=0; latest_s=None
e_key=None; e_count=0; latest_e=None
blue_repeat_count={}      # (S,None) or (E,number) -> accepted occurrence count
blue_repeat_latest={}     # same key -> latest accepted behavior object
active_stopalls=[]

record_blue(B):
    if B is S Blue: key=(S,None)
    elif B is E Blue: key=(E,B.number)
    else: return
    blue_repeat_count[key] += 1
    blue_repeat_latest[key] = B

hard_reset():
    clear current S/E owner keys/counts
    clear blue_repeat_count and blue_repeat_latest
    reset active StopAll ownership as required by the creating gate

process_s(S):
    if S.color == Red and S.order_mode == B:
        qualified = every exact Blue key with blue_repeat_count[key] >= 2
        if qualified:
            key = qualified key whose latest accepted occurrence is latest
            promote S -> StopAll using key/count metadata
            hard_reset(); return

    if S.color == Red:
        clear pending Blue-repeat counters (not dominant S/E owner state)
    if S.color == Blue:
        record_blue(S)

    if no e_key and s_key == S.color:
        s_count += 1; latest_s=S
    elif priority(S) > active_priority:
        s_key=S.color; s_count=1; latest_s=S
        e_key=None; e_count=0; latest_e=None

for E in chronological E:
    ingest every earlier S with process_s

    if an active StopAll strictly stopped by E.decision:
        create next numbered StopAll from E; hard_reset(); continue

    # Existing E-driven sequence-group-stop is unchanged and still uses
    # current dominant same-key S/E repetition plus strict-stop chronology.
    if current same-key E count >=2 (or, with no E key, same-key S count >=2):
        if latest matching current owner strictly stopped by E.decision:
            create StopAll1 from E with sequence-group-stop; hard_reset(); continue

    # Only an E that remains E (was not promoted above) participates in the
    # pending accepted-S reversal counter.
    if E.family == Red:
        clear pending Blue-repeat counters (not dominant S/E owner state)
    if E.family == Blue:
        record_blue(E)

    new_key=(E.family,E.number)
    if new_key == e_key:
        e_count += 1; latest_e=E
    elif E can replace/advance current owner:
        e_key=new_key; e_count=1; latest_e=E
        s_key=None; s_count=0; latest_s=None

after final E: ingest remaining S
finally compute each StopAll's own first strict directional stop
```

The accepted-S reversal gate uses **pending repetition of the same exact Blue behavior group**. `S Blue × 2`, `E1 Blue × 2`, or `E5 Blue × 2` each independently qualify; different E numbers never add together. This qualification lasts only until the next accepted Red S/E or hard StopAll. The first accepted S Red with a native Mode-B Order and qualifying pending Blue group promotes to StopAll. A Mode-A/no-Order S Red remains S Red but clears the obsolete pending evidence. A Red E also clears it without changing E-driven priority/sequence counters. Another Blue group may re-arm thereafter. The mirror changes only directional price geometry.

## 16. Public serialization contract

All timestamps serialized by behavior objects are epoch seconds obtained by interpreting the engine's naive internal datetime as `Asia/Tehran`. Decimal prices are serialized as strings, never binary floats.

### Response envelope

The top-level response contains: `engine`, `version`, `pipelineVersion`, `blueLineVersion`, `aVersion`, `sVersion`, `eVersion`, `stopAllVersion`, enablement flags, `timeframe`, `actualFrom`, `actualTo`, `directions`, and timing telemetry. `actualFrom/actualTo` are the selected *presentation* main-candle range, not the calculation range.

### Reaction
`firstIndex`, `firstTime`, `boxTopSourceIndex`, `boxTopSourceTime`, `boxTop`, `boxBottomSourceIndex`, `boxBottomSourceTime`, `boxBottom`, `breakIndex`, `breakTime`, `mode`.

### Reset
`index`, `time`, `secondTime`, `brokenLevel`, `fromFirstIndex`.

### Blue Line
`direction`, `kind`, `reactionNumber`, `previousStrikeCount`, `strikeCount`, `fibonacciLevel`, `sourceIndex`, `sourceTime`, `sourceExtreme`, `brokenLevel`, `linePrice`, `startTime`, `endTime`.

### A
`direction`, `blue1Ordinal`, `blue2Ordinal`, `blue1SourceTime`, `blue2SourceTime`, `blue1StopTime`, `blue2StopTime`, `blue1StopLevel`, `blue2StopLevel`, `continuationLevel`, `continuationSourceIndex`, `continuationSourceTime`, `triggerIndex`, `triggerTime`, `triggerEventTime`, `reactionNumber`, `reactionFirstTime`, `reactionBreakTime`, `sourceIndex`, `sourceTime`, `price`, `calculationValid=true`.

### S
`direction`, `color`, `formationType`, `aOrdinal`, `aSourceIndex`, `aSourceTime`, `aPrice`, `aStopIndex`, `aStopTime`, `aStopEventTime`, all Order geometry/provenance fields, `resetReactionNumber`, `resetTime`, `sourceIndex`, `sourceTime`, `price`, `decisionIndex`, `decisionTime`, `decisionEventTime`, `calculationValid=true`.

### E
`direction`, `family`, `number`, parent identity/provenance, all Order geometry/provenance fields, `sourceIndex`, `sourceTime`, `price`, `decisionIndex`, `decisionTime`, `decisionEventTime`.

### StopAll
`direction`, `number`, source/decision fields, gate fields, stopped behavior fields, underlying E family/number, complete Order geometry/provenance, and strict stop fields `stopIndex`, `stopTime`, `stopEventTime`.

### OrderAudit
One physical Order identity is `(firstIndex, breakIndex)`. Output fields are `direction`, `reactionNumber`, `reactionMode`, Reaction box fields, `stopLevel`, `stopSourceIndex`, `stopSourceTime`, `stopHitIndex`, `stopHitTime`, `stopHitEventTime`, and `causes`. Causes are either `parent-stop` (`parentType`, `parentFamily`, `eventTime`, `parentSourceTime`) or `reset-leg` (`resetTime`, `boundaryBreakTime`). For V5.2.0 Order_B, `boundaryBreakTime` is the exact strict break of the Reset-leg floor. Output is sorted by `(firstTime, breakTime)`.

The final Bridge has a hard consistency invariant: every public S/E/StopAll that carries an Order must reference a physical identity `(firstIndex,breakIndex)` present in the final canonical OrderAudit. Final E branch replacement or independent-root restoration must synchronize the accepted Order ledger before serialization. Conversely, one exact parent-stop cause may not appear on two different physical Order identities. Accepted carried-live and noncanonical bounded direct Order geometry (`reactionNumber=0`) must remain auditable; the Bridge must never invent a replacement Order merely to satisfy serialization.



## 17. Determinism, ordering and tie-breaking

1. Use `Decimal(str(value))` for every non-Decimal numeric input; never decide strict crosses using binary floating point.
2. Main candle indexes are full-RAW indexes. Never renumber after applying a presentation window.
3. Lower-timeframe windows are half-open `[start, end)` unless a rule explicitly makes an endpoint inclusive by adding one microsecond or by scanning through an event position.
4. Every stop, breakout/breakdown, confirmation, Reset and decision that can be resolved on lower data must use the first strict lower-timeframe event.
5. Equality is not a strict cross. Doji is GREEN because `close >= open`.
6. When invalidation and confirmation occur at the same finest event and the relevant routine checks invalidation first, invalidation wins.
7. A candidate/decision that simultaneously crosses the S candidate and Order stop at the same lower event is invalid (`None`), not Red and not Blue.
8. Same-source E conflict: Red family outranks Blue family; within one family, larger E number outranks smaller; an exact tie keeps the earlier accepted object/provenance.
9. Behavior priority is invariant by market direction: `StopAll > E Red > S Red > E Blue > S Blue > A`.
10. Chronology is primary when ownership is not a same-event priority tie. Old high-priority objects cannot own all later legs forever.

## 18. Forbidden shortcuts and hard requirements

A conforming reconstruction MUST NOT contain timestamp-, symbol-, price-, RAW-file-, fixture-, or expected-output-specific branches. It MUST NOT hardcode reference cases. It MUST calculate both directional Reaction streams when downstream A/S/E logic is enabled, because opposite-direction Reaction/Reset geometry is an input to Order logic. It MUST retain internal Reaction evidence for calculation and apply only the specifically defined public/internal filters. It MUST compute on the complete physical RAW and use `from/to` solely for output selection.

Caches, segment trees, bisect tables, and memoization are performance mechanisms. They may be replaced by linear scans **only if** first-event, extrema, equality, and tie behavior are bit-for-bit semantically identical.

## 19. Rebuild acceptance checklist

A replacement engine is conforming only if all of these are true:

- raw normalization, Decimal conversion, Tehran timestamp conversion, bucket alignment and Doji classification match this document;
- both Reaction streams and exact lower-timeframe confirmation/Reset chronology match;
- Blue Scale/Reset formation and calculation/public validity match;
- A ordinary, double-stop, chained-stop, trigger and exact-confirmation source ownership match;
- S Type-3/Simple/Advanced decisions and accepted-Order reconciliation match;
- E parent-stop, carried-live, and parent-neutral accepted-live routes match; Order_B uses the V5.2.0 same-direction Reset owner, Breakout→Reset inclusive primary extreme, exact strict break, closed primary-source→strict-break geometry-only opposite evidence, first canonical opposite Reaction after the gate, latest-reset-cause rule, and exact Bullish/Bearish mirror; recursive chaining, family/number reconciliation, same-source resolution and invalid-S-root rules match;
- behavior hierarchy, post-stop lifecycle ownership, internal-Reaction scope and StopAll hard boundaries match;
- OrderAudit cause merging, parent-stop single consumption and stop-hit chronology match;
- every public S/E/StopAll Order identity exists in final OrderAudit, and no exact parent-stop provenance maps to two physical Orders;
- final visibility and serialization match exactly;
- requested presentation range does not change full-RAW calculation identities;
- no fixture-specific production logic exists.

## 20. Source-symbol coverage appendix
This appendix is generated from the **current HPZR2 documentation snapshot over the actual production source text**. The line numbers below are regenerated from the current nine modules, not inherited from an older Reference. Hashes are not used to decide semantic synchronization; they are only optional integrity metadata. All module-level classes, functions, methods, nested helper functions, and important module constants discovered from the current Python syntax tree are indexed so implementation helpers are not silently omitted.
### 20.1 `reaction_engine.py`

| Symbol | Kind | Line | Contract summary |
|---|---|---:|---|
| `REACTION_ENGINE_VERSION` | constant | 21 | Module constant. Value in this snapshot: `'9.8.0'`. |
| `REACTION_ENGINE_LAST_MODIFIED` | constant | 22 | Module constant. Value in this snapshot: `'2026-09-22 00:35:00 +03:30'`. |
| `_SEQUENCE_TIME_INDEXES` | constant | 24 | Module constant. Value in this snapshot: `{}`. |
| `Candle` | class | 27 | Source symbol required by the production implementation. |
| `Candidate` | class | 39 | Source symbol required by the production implementation. |
| `ResetEvent` | class | 67 | Source symbol required by the production implementation. |
| `IntrabarAnalysis` | class | 76 | Source symbol required by the production implementation. |
| `DetectionResult` | class | 83 | Source symbol required by the production implementation. |
| `classify_candle_color` | function | 91 | Match Lightweight Charts: Open <= Close is an up/green candle. |
| `opposite_direction` | function | 96 | Return the exact Bullish/Bearish mirror direction. |
| `DetectorBase` | class | 101 | Source symbol required by the production implementation. |
| `DetectorBase.__init__` | method | 102 | Source symbol required by the production implementation. |
| `DetectorBase._shared_time_index` | method | 127 | Build one immutable-source timestamp index per calculation process. |
| `DetectorBase.seconds_between` | method | 137 | Source symbol required by the production implementation. |
| `DetectorBase.main_source_for_time` | method | 142 | Source symbol required by the production implementation. |
| `DetectorBase.minimum_low` | method | 155 | Source symbol required by the production implementation. |
| `DetectorBase.maximum_high` | method | 164 | Source symbol required by the production implementation. |
| `BullishDetector` | class | 174 | Source symbol required by the production implementation. |
| `BullishDetector.green_run_peak_before` | method | 175 | Source symbol required by the production implementation. |
| `BullishDetector.breakout_analysis` | method | 185 | Source symbol required by the production implementation. |
| `BullishDetector.mode_a_invalidation_before_breakout` | method | 211 | Source symbol required by the production implementation. |
| `BullishDetector.confirmed_reset_before_breakout` | method | 247 | Source symbol required by the production implementation. |
| `BullishDetector.post_breakout_reset` | method | 267 | Source symbol required by the production implementation. |
| `BullishDetector.detect` | method | 282 | Source symbol required by the production implementation. |
| `mirror_candle` | function | 560 | Internal coordinate/role adapter; never reclassify a market candle here. |
| `mirror_candidate` | function | 580 | Mirror geometry while preserving invariant dynamic gate state. |
| `mirror_analysis` | function | 599 | Source symbol required by the production implementation. |
| `_ReflectedCandles` | class | 608 | Read-only coordinate view with one-time mirror caching. |
| `_ReflectedCandles.__init__` | method | 616 | Source symbol required by the production implementation. |
| `_ReflectedCandles.__len__` | method | 620 | Source symbol required by the production implementation. |
| `_ReflectedCandles.__getitem__` | method | 623 | Source symbol required by the production implementation. |
| `_REFLECTED_VIEWS` | constant | 633 | Module constant. Value in this snapshot: `{}`. |
| `_reflected_view` | function | 636 | Source symbol required by the production implementation. |
| `BearishDetector` | class | 646 | Execute the Bullish reference state machine in reflected coordinates. |
| `BearishDetector.__init__` | method | 654 | Source symbol required by the production implementation. |
| `BearishDetector.red_run_bottom_before` | method | 668 | Source symbol required by the production implementation. |
| `BearishDetector.breakdown_analysis` | method | 672 | Source symbol required by the production implementation. |
| `BearishDetector.invalidation_high_break_before_breakdown` | method | 677 | Source symbol required by the production implementation. |
| `BearishDetector.confirmed_reset_before_breakdown` | method | 682 | Source symbol required by the production implementation. |
| `BearishDetector.post_breakdown_reset` | method | 688 | Source symbol required by the production implementation. |
| `BearishDetector.detect` | method | 695 | Source symbol required by the production implementation. |
| `published_reaction_candidate` | function | 706 | Return a presentation clone with Break-candle geometry frozen at confirmation. |
| `_decimal_value` | function | 804 | Normalize external numeric values without binary-float arithmetic. |
| `LowerTimeframeIndex` | class | 809 | Immutable segment index for exact first strict High/Low crossings. |
| `LowerTimeframeIndex.__init__` | method | 816 | Source symbol required by the production implementation. |
| `LowerTimeframeIndex.first_less` | method | 857 | Source symbol required by the production implementation. |
| `LowerTimeframeIndex.first_greater` | method | 860 | Source symbol required by the production implementation. |
| `LowerTimeframeIndex.range_minimum` | method | 863 | Return the minimum Low and earliest owning position in [left, right). |
| `LowerTimeframeIndex.range_maximum` | method | 867 | Return the maximum High and earliest owning position in [left, right). |
| `LowerTimeframeIndex._range_query` | method | 871 | Source symbol required by the production implementation. |
| `LowerTimeframeIndex._first` | method | 909 | Source symbol required by the production implementation. |
| `_LOWER_TIMEFRAME_INDEXES` | constant | 929 | Module constant. Value in this snapshot: `{}`. |
| `shared_lower_timeframe_index` | function | 934 | Reuse one immutable lower-timeframe index per source sequence. |
| `ReflectedLowerTimeframeIndex` | class | 947 | Price-reflected view over a lower-timeframe index without rebuilding it. |
| `ReflectedLowerTimeframeIndex.__init__` | method | 952 | Source symbol required by the production implementation. |
| `ReflectedLowerTimeframeIndex.first_less` | method | 956 | Source symbol required by the production implementation. |
| `ReflectedLowerTimeframeIndex.first_greater` | method | 959 | Source symbol required by the production implementation. |
| `ReflectedLowerTimeframeIndex.range_minimum` | method | 962 | Source symbol required by the production implementation. |
| `ReflectedLowerTimeframeIndex.range_maximum` | method | 966 | Source symbol required by the production implementation. |
| `MarketChronology` | class | 971 | Shared immutable market-time services for downstream behavior engines. |
| `MarketChronology.__init__` | method | 990 | Source symbol required by the production implementation. |
| `MarketChronology.opposite_direction` | method | 1013 | Expose the shared mirror-direction contract to downstream engines. |
| `MarketChronology.main_index` | method | 1017 | Map an exact lower-timeframe timestamp to its owning main candle. |
| `MarketChronology.lower_bounds` | method | 1026 | Source symbol required by the production implementation. |
| `MarketChronology.lower_window` | method | 1037 | Source symbol required by the production implementation. |
| `MarketChronology._reset_cache_key` | method | 1044 | Return a stable Reset identity suitable for chronology caches. |
| `MarketChronology._reaction_cache_key` | method | 1056 | Return a stable physical/geometry identity for confirmation caches. |
| `MarketChronology.reset_time` | method | 1070 | Return the exact Reset event time, preserving legacy provenance. |
| `MarketChronology.reaction_confirmation` | method | 1089 | Return the first strict lower-timeframe Reaction confirmation. |
| `MarketChronology.canonical_order_stop` | method | 1137 | Return canonical opposite-Order stop provenance for S and E. |
| `build_behavior_reaction_views` | function | 1202 | Mark true cross-direction Reaction interiors for downstream behavior. |
| `build_behavior_reaction_views.path_is_contained` | nested function | 1222 | Source symbol required by the production implementation. |
| `directional_a_stop_order_finder` | function | 1313 | Build the cached bounded opposite-Reaction resolver used after A stop. |
| `directional_a_stop_order_finder.find` | nested function | 1327 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector` | class | 1376 | Unified v9 directional post-Reset engine. |
| `UnifiedReactionDetector.__init__` | method | 1386 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector.bull` | method | 1411 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector.bear` | method | 1419 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector._append_reaction` | method | 1426 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector._append_reset` | method | 1508 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector._refine` | method | 1526 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector._candidate_from_confirmation_remainder` | method | 1547 | Reuse a correctly colored confirmation candle for the next reaction. |
| `UnifiedReactionDetector._first_initial` | method | 1632 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector._first_direct_same_direction_after_reset` | method | 1645 | Return the first structurally owned reaction after Reset. |
| `UnifiedReactionDetector._first_geometry_after_reset` | method | 1683 | Return the first complete raw Reaction geometry after a boundary. |
| `UnifiedReactionDetector.first_geometry_after_reset` | method | 1736 | Public lifecycle API for post-Reset geometry discovery. |
| `UnifiedReactionDetector._reaction_break_indices` | method | 1743 | Cached ascending `break_idx` values mirroring `all_reactions[direction]`. |
| `UnifiedReactionDetector.first_order_reaction_after_gate` | method | 1758 | Return direct Order_A geometry from continuous Reaction context. |
| `UnifiedReactionDetector.first_order_reaction_after_gate.confirmed_no_later_than_gate` | nested function | 1770 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector._earliest_confirmed_geometry` | method | 1892 | Return the geometry whose strict confirmation occurs first. |
| `UnifiedReactionDetector._build_direct_candidate` | method | 1966 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector._scan_direct_candidate` | method | 2024 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector._owner_boundary_before_confirmation` | method | 2054 | Return whether structural alignment is lost before confirmation. |
| `UnifiedReactionDetector._result` | method | 2095 | Source symbol required by the production implementation. |
| `UnifiedReactionDetector.detect` | method | 2104 | Source symbol required by the production implementation. |

### 20.2 `blue_line_detector.py`

| Symbol | Kind | Line | Contract summary |
|---|---|---:|---|
| `BLUE_LINE_VERSION` | constant | 18 | Module constant. Value in this snapshot: `'2.3.0'`. |
| `FIBONACCI_RATIO` | constant | 19 | Module constant. Value in this snapshot: `Decimal('0.618')`. |
| `ScaleStrike` | class | 23 | Source symbol required by the production implementation. |
| `BlueLine` | class | 30 | Source symbol required by the production implementation. |
| `_is_color` | function | 48 | Source symbol required by the production implementation. |
| `_main_candle` | function | 52 | Source symbol required by the production implementation. |
| `_stops_on_index` | function | 59 | Source symbol required by the production implementation. |
| `fibonacci_level` | function | 75 | Source symbol required by the production implementation. |
| `_intrabar_pending_confirmation` | function | 84 | Source symbol required by the production implementation. |
| `count_scale_strikes` | function | 139 | Return the exact 0.618 level and confirmed strikes for one reaction. |
| `_build_scale_blue_line` | function | 207 | Build one scale Blue from its decisive confirmed strike. |
| `_build_reset_blue_line` | function | 245 | Build one Reset Blue while preserving the established double-stop rule. |
| `detect_blue_lines` | function | 299 | Detect scale and Reset Blue Lines over authoritative engine events. |
| `public_blue_lines` | function | 407 | Return only calculation-valid, public Blue Lines for serialization. |
| `mark_internal_blue_lines` | function | 416 | Mark Blue Lines that are private to protected Reaction interiors. |
| `mark_internal_blue_lines.owner_is_internal` | nested function | 429 | Source symbol required by the production implementation. |
| `mark_internal_blue_lines.geometry_is_internal` | nested function | 435 | Source symbol required by the production implementation. |

### 20.3 `a_zone_detector.py`

| Symbol | Kind | Line | Contract summary |
|---|---|---:|---|
| `A_ZONE_VERSION` | constant | 20 | Module constant. Value in this snapshot: `'1.6.4'`. |
| `A_ZONE_LAST_MODIFIED_DATE` | constant | 21 | Module constant. Value in this snapshot: `'2026-09-21'`. |
| `BlueState` | class | 25 | Source symbol required by the production implementation. |
| `AZone` | class | 38 | Source symbol required by the production implementation. |
| `AZoneDetector` | class | 62 | Source symbol required by the production implementation. |
| `AZoneDetector.__init__` | method | 63 | Source symbol required by the production implementation. |
| `AZoneDetector.extreme_name` | method | 92 | Source symbol required by the production implementation. |
| `AZoneDetector._strict_cross` | method | 95 | Source symbol required by the production implementation. |
| `AZoneDetector._better` | method | 98 | Source symbol required by the production implementation. |
| `AZoneDetector._main_index` | method | 101 | Source symbol required by the production implementation. |
| `AZoneDetector._lower_window` | method | 104 | Source symbol required by the production implementation. |
| `AZoneDetector._first_crossing` | method | 109 | Source symbol required by the production implementation. |
| `AZoneDetector._range_extreme` | method | 151 | Source symbol required by the production implementation. |
| `AZoneDetector._formation` | method | 185 | Source symbol required by the production implementation. |
| `AZoneDetector._reset_formation_time` | method | 202 | Return the exact strict Reset event that makes a Reset Blue exist. |
| `AZoneDetector._build_blue_states` | method | 214 | Source symbol required by the production implementation. |
| `AZoneDetector._double_stop_a_candidates` | method | 243 | Source symbol required by the production implementation. |
| `AZoneDetector._pair_trigger` | method | 305 | Source symbol required by the production implementation. |
| `AZoneDetector._reaction_confirmation_time` | method | 465 | Source symbol required by the production implementation. |
| `AZoneDetector._first_reaction_after` | method | 470 | Source symbol required by the production implementation. |
| `AZoneDetector._inherited_stop` | method | 488 | Source symbol required by the production implementation. |
| `AZoneDetector._a_source` | method | 541 | Return A ownership frozen at the exact confirming Reaction event. |
| `AZoneDetector._detect_ordinary_a` | method | 562 | Resolve the ordinary adjacent-Blue A lifecycle. |
| `AZoneDetector._filter_special_a` | method | 672 | Resolve special double-stop A ownership against ordinary A state. |
| `AZoneDetector.detect` | method | 736 | Return ordinary and special A zones after one ownership resolution. |
| `AZoneDetector._a_was_stopped_before` | method | 748 | Return whether A's *first* strict stop belongs to this lifecycle. |
| `detect_a_zones` | function | 774 | Source symbol required by the production implementation. |

### 20.4 `s_zone_detector.py`

| Symbol | Kind | Line | Contract summary |
|---|---|---:|---|
| `S_ZONE_VERSION` | constant | 21 | Module constant. Value in this snapshot: `'4.20.0'`. |
| `S_ZONE_LAST_MODIFIED` | constant | 22 | Module constant. Value in this snapshot: `'2026-09-23 10:19:31 +03:30'`. |
| `SZone` | class | 26 | Source symbol required by the production implementation. |
| `SZoneDetector` | class | 64 | Source symbol required by the production implementation. |
| `SZoneDetector.__init__` | method | 65 | Source symbol required by the production implementation. |
| `SZoneDetector._main_index` | method | 192 | Source symbol required by the production implementation. |
| `SZoneDetector._lower_window` | method | 195 | Source symbol required by the production implementation. |
| `SZoneDetector._reaction_confirmation_time` | method | 200 | Source symbol required by the production implementation. |
| `SZoneDetector.reaction_confirmation_time` | method | 205 | Public chronology API used by cross-stage lifecycle ownership. |
| `SZoneDetector._reset_time` | method | 212 | Source symbol required by the production implementation. |
| `SZoneDetector._a_confirmation_time` | method | 215 | Source symbol required by the production implementation. |
| `SZoneDetector._trend_extreme` | method | 223 | Source symbol required by the production implementation. |
| `SZoneDetector._a_stopped` | method | 228 | Source symbol required by the production implementation. |
| `SZoneDetector._first_a_stop` | method | 231 | Source symbol required by the production implementation. |
| `SZoneDetector.first_a_stop` | method | 267 | Public lifecycle API for the first strict A stop. |
| `SZoneDetector._first_order_after` | method | 274 | Return the immutable first opposite Order_A after A-stop. |
| `SZoneDetector._order_matches_after` | method | 286 | Return canonical opposite Orders after one A stop in chronology. |
| `SZoneDetector._resolved_order_backed_zone` | method | 307 | Resolve S using the original first physical Order_A. |
| `SZoneDetector._record_a_order_audit` | method | 325 | Attach one stopped-A creation cause to a physical Order identity. |
| `SZoneDetector._audit_stopped_a` | method | 359 | Record the independent order gender created by one stopped A. |
| `SZoneDetector._candidate_source` | method | 371 | Source symbol required by the production implementation. |
| `SZoneDetector._candidate_source_last` | method | 386 | Return the directional extreme, assigning equality to the last candle. |
| `SZoneDetector._first_trend_reaction_after_order` | method | 406 | Source symbol required by the production implementation. |
| `SZoneDetector._nested_trend_reaction` | method | 418 | Source symbol required by the production implementation. |
| `SZoneDetector._simple_candidate` | method | 448 | Use the inclusive order-Break to aligned-Break interval. |
| `SZoneDetector._type3_reset_leg` | method | 457 | Return the independent Type-3 inclusive Break-to-Reset geometry. |
| `SZoneDetector._type3_has_trend_reaction` | method | 473 | Source symbol required by the production implementation. |
| `SZoneDetector._first_type3` | method | 482 | Find the first no-order Type-3 Reset-leg S decision before a new order. |
| `SZoneDetector._type4_has_blue` | method | 532 | Return whether a public calculation-valid Blue exists in Type-4 window. |
| `SZoneDetector._first_type4` | method | 543 | Find the first order-free S Blue Type-4 decision after A stop. |
| `SZoneDetector._build_type4_zone` | method | 613 | Build the order-free Blue Type-4 continuation for one stopped A. |
| `SZoneDetector._candidate_after_order` | method | 666 | Find a candidate strictly after the order is confirmed. |
| `SZoneDetector._a_source_event_time` | method | 707 | Locate the source extreme, including an A-stop main candle. |
| `SZoneDetector._a_owned_by_s` | method | 716 | Source symbol required by the production implementation. |
| `SZoneDetector._a_pair_is_reset_reset` | method | 757 | Whether both Blue Lines that define A are Reset Blues. |
| `SZoneDetector.eligible_a_zones` | method | 771 | A candidates outside stopped-parent S ownership, before rendering. |
| `SZoneDetector._candidate_timing` | method | 775 | Resolve pre/post-Order ownership without stealing Advanced S. |
| `SZoneDetector._candidate_before_order` | method | 820 | Use the lowest/highest leg extreme from A-stop through order First. |
| `SZoneDetector._candidate_event_time` | method | 864 | Return the first lower-timeframe event that forms the candidate. |
| `SZoneDetector.candidate_event_time` | method | 879 | Public lifecycle API for exact S candidate provenance. |
| `SZoneDetector._blue_formation_time` | method | 886 | Source symbol required by the production implementation. |
| `SZoneDetector._candidate_cross_has_blue` | method | 916 | Return whether the candidate cross has its aligned Reset Blue. |
| `SZoneDetector._has_ordinary_trend_reaction` | method | 933 | Return whether ordinary aligned geometry completed in the leg. |
| `SZoneDetector._order_stop` | method | 944 | Source symbol required by the production implementation. |
| `SZoneDetector._candidate_crossed` | method | 955 | Source symbol required by the production implementation. |
| `SZoneDetector._order_stop_crossed` | method | 959 | Source symbol required by the production implementation. |
| `SZoneDetector._decision` | method | 964 | Source symbol required by the production implementation. |
| `SZoneDetector._build_type3_zone` | method | 1090 | Build the order-free Blue Type-3 continuation for one stopped A. |
| `SZoneDetector._build_order_backed_zone` | method | 1148 | Resolve Simple/Advanced S ownership after a stopped A finds an Order. |
| `SZoneDetector.detect` | method | 1319 | Source symbol required by the production implementation. |
| `SZoneDetector._shared_order_stop_cross` | method | 1396 | Return the first strict stop of an accepted Order after confirmation. |
| `SZoneDetector.reconcile_shared_order_stops` | method | 1422 | Resolve open S candidates with any accepted physical Order stop. |
| `detect_s_zones` | function | 1539 | Source symbol required by the production implementation. |

### 20.5 `e_zone_detector.py`

| Symbol | Kind | Line | Contract summary |
|---|---|---:|---|
| `E_ZONE_VERSION` | constant | 22 | Module constant. Value in this snapshot: `'6.13.0'`. |
| `E_ZONE_LAST_MODIFIED` | constant | 23 | Module constant. Value in this snapshot: `'2026-09-22 00:35:00 +03:30'`. |
| `EZone` | class | 27 | Source symbol required by the production implementation. |
| `OrderBFormation` | class | 75 | One complete reset-leg Order_B setup under the canonical mirror rule. |
| `EZoneDetector` | class | 98 | Source symbol required by the production implementation. |
| `EZoneDetector.__init__` | method | 99 | Source symbol required by the production implementation. |
| `EZoneDetector._reset_time` | method | 276 | Source symbol required by the production implementation. |
| `EZoneDetector._main_index` | method | 279 | Source symbol required by the production implementation. |
| `EZoneDetector._first_cross_position` | method | 283 | Return the first strict lower-timeframe crossing in [left, right). |
| `EZoneDetector._stop_value` | method | 300 | Source symbol required by the production implementation. |
| `EZoneDetector._first_parent_stop` | method | 304 | Source symbol required by the production implementation. |
| `EZoneDetector._confirmation_for` | method | 317 | Source symbol required by the production implementation. |
| `EZoneDetector._confirmation` | method | 320 | Source symbol required by the production implementation. |
| `EZoneDetector._reaction_first_time` | method | 323 | Source symbol required by the production implementation. |
| `EZoneDetector._main_range_extreme` | method | 326 | Return the first candle owning the requested closed-range extreme. |
| `EZoneDetector._order_b_reset_leg` | method | 347 | Return the same-direction Reset owner and its trigger extreme. |
| `EZoneDetector._order_b_strict_break` | method | 375 | Return the first exact strict break of the reset-leg trigger level. |
| `EZoneDetector._order_b_opposite_extreme` | method | 397 | Return the other reset-leg edge on the closed trigger->break range. |
| `EZoneDetector._order_b_geometry_evidence` | method | 415 | Return raw opposite Reaction geometry inside the closed leg range. |
| `EZoneDetector._first_order_b_reaction_after_break` | method | 439 | Return the first canonical opposite Reaction after the Order_B gate. |
| `EZoneDetector._build_order_b_formations` | method | 456 | Build every Order_B from same-direction Reset-leg geometry. |
| `EZoneDetector._order_b_orders` | method | 577 | Return canonical Order_B Orders whose Reaction forms at/after start. |
| `EZoneDetector._order_b_candidate_matches` | method | 595 | Return one final Reset-leg candidate per physical Order after start. |
| `EZoneDetector._order_b_evidence` | method | 605 | Return the latest eligible Order_B cause for one physical Reaction. |
| `EZoneDetector._replacement_order` | method | 627 | Return the first later Order_B that forms before the owner stops. |
| `EZoneDetector._order_stop` | method | 652 | Source symbol required by the production implementation. |
| `EZoneDetector.order_stop` | method | 680 | Public audit API for canonical Order stop provenance. |
| `EZoneDetector._first_healthy_direct_geometry` | method | 687 | Return the first healthy geometry after an A/S/E strict stop. |
| `EZoneDetector._trend_leg_direct_order` | method | 766 | Return bounded direct Order_A after a newly confirmed trend leg. |
| `EZoneDetector._direct_parent_stop_order` | method | 815 | Select the direct parent-stop Order without Order_B evidence. |
| `EZoneDetector._merge_order_candidate` | method | 900 | Merge one provenance cause into a single physical Order identity. |
| `EZoneDetector._enforce_single_parent_stop_owner` | method | 943 | Keep one physical Order owner for the exact parent-stop cause. |
| `EZoneDetector.order_candidates` | method | 986 | Return every valid E-space Order formed before this E decision. |
| `EZoneDetector._first_order` | method | 1091 | Source symbol required by the production implementation. |
| `EZoneDetector._has_sequence_reset_between` | method | 1106 | Return whether a known hard reset lies in ``(start, end]``. |
| `EZoneDetector._blue_parent_superseded` | method | 1116 | A confirmed later Red S closes an older Blue-E order lifecycle. |
| `EZoneDetector._index_order_audit_identity` | method | 1128 | Index one newly accepted physical Order by confirmation chronology. |
| `EZoneDetector._clear_order_audit` | method | 1137 | Source symbol required by the production implementation. |
| `EZoneDetector._register_order_audit` | method | 1141 | Source symbol required by the production implementation. |
| `EZoneDetector._enrich_order_audit_reset_causes` | method | 1264 | Attach canonical Order_B provenance to already relevant Orders. |
| `EZoneDetector.visual_order_lifecycle` | method | 1324 | Return only orders admitted by the E lifecycle, including live ones. |
| `EZoneDetector._parent_stop` | method | 1366 | Source symbol required by the production implementation. |
| `EZoneDetector.parent_stop` | method | 1374 | Public lifecycle API for the first strict parent stop. |
| `EZoneDetector._cross_order` | method | 1381 | Source symbol required by the production implementation. |
| `EZoneDetector.cross_order` | method | 1401 | Public audit API for an Order stop crossing. |
| `EZoneDetector._unconsumed_s_orders` | method | 1408 | Return every Blue-S Order whose stop did not decide the S itself. |
| `EZoneDetector._initial_order_records` | method | 1445 | Materialize immutable initial OrderAudit geometry once per run. |
| `EZoneDetector._initial_record_match` | method | 1503 | Source symbol required by the production implementation. |
| `EZoneDetector._initial_order_match` | method | 1516 | Source symbol required by the production implementation. |
| `EZoneDetector._gate_owned_initial_order` | method | 1531 | Keep an A-owned order that starts in the parent-stop candle. |
| `EZoneDetector._carried_orders_for_parent` | method | 1553 | Return every Order formed and left live inside this parent lifecycle. |
| `EZoneDetector._post_stop_accepted_orders_for_parent` | method | 1617 | Return accepted physical Orders confirmed after this parent stopped. |
| `EZoneDetector._post_stop_accepted_orders_for_parent.add_match` | nested function | 1624 | Source symbol required by the production implementation. |
| `EZoneDetector._blocked_by_gate_owned_order` | method | 1709 | Reject only a nested Order_A, while preserving its child lineage. |
| `EZoneDetector._reset_evidence_for_order` | method | 1719 | Source symbol required by the production implementation. |
| `EZoneDetector._extreme_between` | method | 1738 | Source symbol required by the production implementation. |
| `EZoneDetector._zone` | method | 1754 | Source symbol required by the production implementation. |
| `EZoneDetector.set_consumed_s_evidence` | method | 1869 | Register non-public S evidence that continues a stopped larger E. |
| `EZoneDetector._apply_consumed_s_evidence` | method | 1881 | Source symbol required by the production implementation. |
| `EZoneDetector.continuation_chain_from_s` | method | 1899 | Build the E continuation opened by one S consumed by a stopped E. |
| `EZoneDetector.replace_with_earlier_continuation` | method | 1938 | Replace an owner's not-yet-decided descendant branch when an earlier one wins. |
| `EZoneDetector.replace_with_earlier_continuation.descends_from_owner` | nested function | 1947 | Source symbol required by the production implementation. |
| `EZoneDetector.resolve_same_source_conflicts` | method | 1981 | Keep exactly one accepted E behavior for each physical source candle. |
| `EZoneDetector.resolve_same_source_conflicts.outranks` | nested function | 1999 | Source symbol required by the production implementation. |
| `EZoneDetector.restore_independent_s_roots` | method | 2025 | Restore calculation-valid E1 roots owned directly by accepted S. |
| `EZoneDetector._discover_candidate_chains` | method | 2085 | Build provisional recursive E chains from every stopped S parent. |
| `EZoneDetector._reconcile_candidate_chains` | method | 2177 | Resolve competing E chains into the accepted chronological lifecycle. |
| `EZoneDetector._reconcile_candidate_chains.valid_order` | nested function | 2220 | Source symbol required by the production implementation. |
| `EZoneDetector._reconcile_candidate_chains.invalidated_only_by_future_s` | nested function | 2240 | Source symbol required by the production implementation. |
| `EZoneDetector._reconcile_candidate_chains.parent_active` | nested function | 2256 | Source symbol required by the production implementation. |
| `EZoneDetector._reconcile_candidate_chains.stopped_by` | nested function | 2328 | Source symbol required by the production implementation. |
| `EZoneDetector._reconcile_candidate_chains.ownership_priority` | nested function | 2384 | Source symbol required by the production implementation. |
| `EZoneDetector._reconcile_candidate_chains.collect_lineage` | nested function | 2478 | Source symbol required by the production implementation. |
| `EZoneDetector._historical_rescue_candidates` | method | 2514 | Return presentation-only historical E objects suppressed by future conflicts. |
| `EZoneDetector._historical_rescue_candidates.suppressed_by_future_child_conflict` | nested function | 2542 | Source symbol required by the production implementation. |
| `EZoneDetector._rebuild_accepted_order_audit` | method | 2601 | Rebuild Order Audit from accepted S/E/StopAll state only. |
| `EZoneDetector.rebuild_accepted_order_audit` | method | 2790 | Rebuild the canonical Order ledger after external E reconciliation. |
| `EZoneDetector.ensure_accepted_order_audit` | method | 2805 | Add audit coverage for externally restored accepted E zones. |
| `EZoneDetector.detect` | method | 2827 | Discover, reconcile and audit recursive E lifecycles. |
| `detect_e_zones` | function | 2843 | Source symbol required by the production implementation. |

### 20.6 `lifecycle_engine.py`

| Symbol | Kind | Line | Contract summary |
|---|---|---:|---|
| `STOP_ALL_VERSION` | constant | 21 | Module constant. Value in this snapshot: `'1.15.2'`. |
| `STOP_ALL_LAST_MODIFIED` | constant | 22 | Module constant. Value in this snapshot: `'2026-09-23 09:25:00 +03:30'`. |
| `SEQUENCE_PRIORITY` | constant | 25 | Module constant. Value in this snapshot: `{('s', 'blue'): 1, ('e', 'blue'): 2, ('s', 'red'): 3, ('e', 'red'): 4}`. |
| `sequence_priority` | function | 33 | Return the single authoritative cross-stage behavior priority. |
| `StopAll` | class | 39 | Source symbol required by the production implementation. |
| `StopAllDetector` | class | 81 | Source symbol required by the production implementation. |
| `StopAllDetector.__init__` | method | 82 | Source symbol required by the production implementation. |
| `StopAllDetector._strict_stop` | method | 103 | Source symbol required by the production implementation. |
| `StopAllDetector._e_key` | method | 120 | Source symbol required by the production implementation. |
| `StopAllDetector._dominates_e` | method | 124 | Source symbol required by the production implementation. |
| `StopAllDetector._sequence_priority` | method | 134 | Source symbol required by the production implementation. |
| `StopAllDetector._active_sequence_priority` | method | 138 | Source symbol required by the production implementation. |
| `StopAllDetector._stopall_from_e` | method | 147 | Source symbol required by the production implementation. |
| `StopAllDetector._optional_int` | method | 206 | Source symbol required by the production implementation. |
| `StopAllDetector._optional_decimal` | method | 210 | Source symbol required by the production implementation. |
| `StopAllDetector._stopall_from_s` | method | 213 | Promote the accepted opposite-color S into a fresh StopAll1. |
| `StopAllDetector._blue_repeat_key` | method | 307 | Return the pending-reversal exact Blue behavior-group key. |
| `StopAllDetector._record_blue_repeat` | method | 323 | Source symbol required by the production implementation. |
| `StopAllDetector._opposite_s_stopall_gate` | method | 332 | Return Blue-repeat metadata when accepted S Red must become StopAll. |
| `StopAllDetector.detect` | method | 379 | Source symbol required by the production implementation. |
| `StopAllDetector.detect.reset_cycle_blue_repeats` | nested function | 395 | Source symbol required by the production implementation. |
| `StopAllDetector.detect.process_s_event` | nested function | 399 | Source symbol required by the production implementation. |
| `detect_stopalls` | function | 585 | Source symbol required by the production implementation. |
| `prepare_order_audit` | function | 597 | Resolve calculation-valid Order Audit identities before serialization. |
| `accepted_audit_entry` | function | 756 | Return an E-facing A audit entry for one accepted A provenance. |
| `resolve_order_context` | function | 785 | Resolve accepted stopped-A Orders against provisional Order blocks. |
| `visible_a_zones_after_s_stops` | function | 837 | Suppress the A candle that contains an already-confirmed S stop. |
| `module_priority` | function | 853 | Return the confirmed behavioral ownership priority. |
| `module_identity` | function | 867 | Source symbol required by the production implementation. |
| `module_stop_event` | function | 876 | Resolve the strict one-second stop event of an S/E/StopAll object. |
| `strictly_beyond_boundary` | function | 890 | Source symbol required by the production implementation. |
| `dominant_module` | function | 895 | Source symbol required by the production implementation. |
| `split_a_zones_by_dominant_stops` | function | 908 | Separate visible A labels from A objects allowed into downstream math. |
| `blocked_orders_while_invalid_leg_heads_are_live` | function | 1111 | Return order First times owned by a still-live invalid leg head. |
| `consumed_s_evidence_after_larger_stop` | function | 1134 | Return the earliest suppressed S evidence that continues each stopped E. |
| `s_zones_for_module_engines` | function | 1211 | Preserve the established S eligibility contract consumed by E/StopAll. |
| `s_zones_for_stopall` | function | 1241 | Return accepted S state that may participate in StopAll grouping. |
| `visible_s_zones_after_module_resets` | function | 1260 | Apply dominant-behavior ownership to successive S candidates. |
| `reconcile_stopall_lifecycle` | function | 1429 | Freeze StopAll boundaries from the accepted chronological E state. |
| `visible_a_zones_after_module_boundaries` | function | 1462 | Require A provenance to rebuild after the dominant strict stop. |
| `reaction_number_is_internal` | function | 1509 | Return whether a numbered Reaction resolves to a protected internal owner. |
| `order_identity_is_internal` | function | 1523 | Return whether a behavior's physical Order Reaction is internal. |
| `point_is_inside_healthy_reaction` | function | 1532 | Return True only for a strict protected Reaction interior. |
| `forbidden_internal_order_b` | function | 1555 | Reject only an internal Reset-leg *Mode-B* Order owner. |
| `filter_internal_behavior_outputs` | function | 1575 | Apply only the scoped Internal-Reaction Order_B prohibition. |
| `finalize_behavior_visibility` | function | 1605 | Resolve the final A/S/E lineage closure after StopAll reconciliation. |
| `visible_a_zones` | function | 1700 | Return A objects whose source candle is not occupied by a final S. |

### 20.7 `trading_pipeline.py`

| Symbol | Kind | Line | Contract summary |
|---|---|---:|---|
| `_ENGINE_ROOT` | constant | 30 | Module constant. Value in this snapshot: `Path(__file__).resolve().parents[1]`. |
| `_PIPELINE_DIR` | constant | 31 | Module constant. Value in this snapshot: `_ENGINE_ROOT / 'pipeline'`. |
| `_DTFMT` | constant | 38 | Module constant. Value in this snapshot: `'{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'`. |
| `TRADING_PIPELINE_VERSION` | constant | 41 | Module constant. Value in this snapshot: `'1.4.1'`. |
| `TRADING_PIPELINE_LAST_MODIFIED` | constant | 42 | Module constant. Value in this snapshot: `'2026-09-21 08:40:00 +03:30'`. |
| `TEHRAN` | constant | 44 | Module constant. Value in this snapshot: `ZoneInfo('Asia/Tehran')`. |
| `emit_progress` | function | 47 | Send machine-readable lifecycle events without contaminating JSON stdout. |
| `timed` | function | 55 | Measure an existing pipeline phase without changing its inputs or output. |
| `load_module` | function | 67 | Source symbol required by the production implementation. |
| `load_engine` | function | 77 | Source symbol required by the production implementation. |
| `local_datetime` | function | 84 | Source symbol required by the production implementation. |
| `epoch` | function | 96 | Source symbol required by the production implementation. |
| `display_epoch` | function | 108 | Convert an engine display/native timestamp once per pipeline process. |
| `build_candle_buckets` | function | 120 | Normalize raw rows once, preserving lower and selected-timeframe buckets. |
| `build_candle_buckets.cached_decimal` | nested function | 129 | Source symbol required by the production implementation. |
| `build_candle_objects` | function | 178 | Create maintained engine candles from already-normalized buckets. |
| `_index_selected` | function | 208 | Source symbol required by the production implementation. |
| `serialize` | function | 216 | Source symbol required by the production implementation. |
| `serialize_blue_lines` | function | 250 | Source symbol required by the production implementation. |
| `serialize_a_zones` | function | 270 | Source symbol required by the production implementation. |
| `serialize_s_zones` | function | 297 | Source symbol required by the production implementation. |
| `serialize_e_zones` | function | 362 | Source symbol required by the production implementation. |
| `serialize_stopalls` | function | 413 | Source symbol required by the production implementation. |
| `validate_order_audit_bridge` | function | 488 | Assert that public behavior Order provenance matches canonical OrderAudit. |
| `serialize_order_audit` | function | 556 | Serialize already-resolved Order Audit identities without business filtering. |
| `EngineBundle` | class | 611 | Source symbol required by the production implementation. |
| `MarketContext` | class | 621 | Source symbol required by the production implementation. |
| `parse_arguments` | function | 630 | Parse and validate the production pipeline command line. |
| `load_engines` | function | 697 | Load every configured calculation engine exactly once. |
| `prepare_market_context` | function | 731 | Read, isolate, normalize and index the selected raw-data range. |
| `PipelineState` | class | 812 | Mutable calculation state shared across direction serialization passes. |
| `FullDirectionState` | class | 832 | Authoritative full-range behavior state for one trend direction. |
| `create_e_detector` | function | 846 | Construct one E detector from the shared geometry/lifecycle contract. |
| `create_e_detector.bounded_geometry` | nested function | 863 | Return raw Reaction geometry inside a closed main-candle range. |
| `create_e_detector.direct_geometry` | nested function | 871 | Source symbol required by the production implementation. |
| `calculate_full_direction_state` | function | 900 | Run Blue→A→S→E calculation and lifecycle reconciliation for one direction. |
| `calculate_full_direction_state.collect_accepted_e_history` | nested function | 958 | Source symbol required by the production implementation. |
| `calculate_full_direction_state.collect_historical_e_rescues` | nested function | 983 | Source symbol required by the production implementation. |
| `calculate_full_direction_state.blocked_by_dominant_final_e` | nested function | 1253 | Source symbol required by the production implementation. |
| `prepare_pipeline_state` | function | 1293 | Run shared calculation stages once and retain reusable detector state. |
| `DirectionRangeState` | class | 1410 | Unserialized calculation state for one requested direction/range. |
| `DirectionVisibilityState` | class | 1423 | Final public behavior state after lifecycle and internal-Reaction rules. |
| `calculate_direction_range_state` | function | 1434 | Collect detector output for one requested direction before visibility rules. |
| `finalize_direction_visibility` | function | 1536 | Apply lifecycle, range and Internal-Reaction rules to detector output. |
| `serialize_direction_payload` | function | 1753 | Serialize one direction without applying any trading rule. |
| `serialize_direction_payload.build_payload` | nested function | 1777 | Source symbol required by the production implementation. |
| `build_direction_output` | function | 1807 | Calculate, finalize and serialize one requested trend direction. |
| `build_response_payload` | function | 1832 | Build the public response envelope around serialized direction outputs. |
| `main` | function | 1885 | Source symbol required by the production implementation. |

### 20.8 `direction_policy.py`

| Symbol | Kind | Line | Contract summary |
|---|---|---:|---|
| `DIRECTION_POLICY_VERSION` | constant | 11 | Module constant. Value in this snapshot: `'1.0.0'`. |
| `DirectionPolicy` | class | 21 | Source symbol required by the production implementation. |
| `DirectionPolicy.opposite_direction` | method | 29 | Source symbol required by the production implementation. |
| `DirectionPolicy.strict_cross` | method | 32 | Source symbol required by the production implementation. |
| `DirectionPolicy.better_extreme` | method | 35 | Source symbol required by the production implementation. |
| `DirectionPolicy.choose_extreme` | method | 38 | Source symbol required by the production implementation. |
| `DirectionPolicy.confirmation_cross` | method | 41 | Reaction confirmation mirror: high>top vs low<bottom. |
| `policy_for` | function | 49 | Source symbol required by the production implementation. |
| `BULLISH` | constant | 57 | Module constant. Value in this snapshot: `DirectionPolicy(direction='bullish', extreme_attr='low', opposite_extreme_attr='high', first_reaction_tag='RED', context_tag='GREEN')`. |
| `BEARISH` | constant | 64 | Module constant. Value in this snapshot: `DirectionPolicy(direction='bearish', extreme_attr='high', opposite_extreme_attr='low', first_reaction_tag='GREEN', context_tag='RED')`. |

### 20.9 `core_utils.py`

| Symbol | Kind | Line | Contract summary |
|---|---|---:|---|
| `CORE_UTILS_VERSION` | constant | 5 | Module constant. Value in this snapshot: `'1.0.0'`. |
| `as_decimal` | function | 11 | Preserve Decimal values and normalize other numeric inputs losslessly. |
| `order_identity` | function | 19 | Return the canonical physical Order/Reaction geometry identity. |
| `reaction_identity` | function | 24 | Return ``(FirstIndex, BreakIndex)`` for a Reaction-like object. |

### 20.10 Dataclass/object schemas present in the source snapshot

#### `Candle` (`reaction_engine.py`, source line 27)

| Field | Type | Source line |
|---|---|---:|
| `index` | `int` | 28 |
| `timestamp` | `datetime` | 29 |
| `display_time` | `str` | 30 |
| `tag` | `str` | 31 |
| `open` | `Decimal` | 32 |
| `high` | `Decimal` | 33 |
| `low` | `Decimal` | 34 |
| `close` | `Decimal` | 35 |

#### `Candidate` (`reaction_engine.py`, source line 39)

| Field | Type | Source line |
|---|---|---:|
| `first_idx` | `int` | 40 |
| `first_time` | `str` | 41 |
| `box_top_source_idx` | `int` | 42 |
| `box_top_source_time` | `str` | 43 |
| `box_top` | `Decimal` | 44 |
| `box_bottom_source_idx` | `int` | 45 |
| `box_bottom_source_time` | `str` | 46 |
| `box_bottom` | `Decimal` | 47 |
| `mode` | `str` | 48 |
| `anchor_idx` | `int | None` | 49 |
| `anchor_value` | `Decimal | None` | 50 |
| `leg_boundary_value` | `Decimal | None` | 51 |
| `break_idx` | `int | None` | 52 |
| `break_time` | `str | None` | 53 |
| `intrabar_start` | `datetime | None` | 54 |
| `cross_direction_origin` | `bool` | 55 |
| `cross_direction_chain_owner` | `bool` | 56 |
| `order_gate_decision` | `str | None` | 57 |
| `behavior_public_number` | `int | None` | 58 |
| `behavior_public_box_top` | `Decimal | None` | 59 |
| `behavior_public_box_bottom` | `Decimal | None` | 60 |
| `behavior_confirmation_time` | `datetime | None` | 61 |
| `behavior_first_time` | `datetime | None` | 62 |
| `behavior_internal` | `bool` | 63 |

#### `ResetEvent` (`reaction_engine.py`, source line 67)

| Field | Type | Source line |
|---|---|---:|
| `index` | `int` | 68 |
| `display_time` | `str` | 69 |
| `second_time` | `str | None` | 70 |
| `broken_level` | `Decimal` | 71 |
| `from_first_idx` | `int` | 72 |

#### `IntrabarAnalysis` (`reaction_engine.py`, source line 76)

| Field | Type | Source line |
|---|---|---:|
| `event_second` | `Candle` | 77 |
| `extreme` | `Decimal` | 78 |
| `extreme_source` | `Candle` | 79 |

#### `DetectionResult` (`reaction_engine.py`, source line 83)

| Field | Type | Source line |
|---|---|---:|
| `direction` | `str` | 84 |
| `reactions` | `list[Candidate]` | 85 |
| `resets` | `list[ResetEvent]` | 86 |
| `start_index` | `int` | 87 |
| `end_index` | `int` | 88 |

#### `ScaleStrike` (`blue_line_detector.py`, source line 23)

| Field | Type | Source line |
|---|---|---:|
| `source_index` | `int` | 24 |
| `source_time` | `datetime` | 25 |
| `extreme` | `Decimal` | 26 |

#### `BlueLine` (`blue_line_detector.py`, source line 30)

| Field | Type | Source line |
|---|---|---:|
| `direction` | `str` | 31 |
| `kind` | `str` | 32 |
| `reaction_number` | `int` | 33 |
| `previous_strike_count` | `int | None` | 34 |
| `strike_count` | `int | None` | 35 |
| `fibonacci_level` | `Decimal | None` | 36 |
| `source_index` | `int` | 37 |
| `source_time` | `datetime` | 38 |
| `source_extreme` | `Decimal` | 39 |
| `broken_level` | `Decimal | None` | 40 |
| `line_price` | `Decimal` | 41 |
| `start_time` | `datetime` | 42 |
| `end_time` | `datetime` | 43 |
| `calculation_valid` | `bool` | 44 |
| `behavior_internal` | `bool` | 45 |

#### `BlueState` (`a_zone_detector.py`, source line 25)

| Field | Type | Source line |
|---|---|---:|
| `ordinal` | `int` | 26 |
| `line` | `object` | 27 |
| `formation_index` | `int` | 28 |
| `formation_time` | `datetime` | 29 |
| `stop_index` | `int | None` | 30 |
| `stop_time` | `datetime | None` | 31 |
| `stop_event_time` | `datetime | None` | 32 |
| `stop_level` | `Decimal` | 33 |
| `stop_event_extreme` | `Decimal | None` | 34 |

#### `AZone` (`a_zone_detector.py`, source line 38)

| Field | Type | Source line |
|---|---|---:|
| `direction` | `str` | 39 |
| `blue_1_ordinal` | `int` | 40 |
| `blue_2_ordinal` | `int` | 41 |
| `blue_1_source_time` | `datetime` | 42 |
| `blue_2_source_time` | `datetime` | 43 |
| `blue_1_stop_time` | `datetime` | 44 |
| `blue_2_stop_time` | `datetime` | 45 |
| `blue_1_stop_level` | `Decimal` | 46 |
| `blue_2_stop_level` | `Decimal` | 47 |
| `continuation_level` | `Decimal` | 48 |
| `continuation_source_index` | `int` | 49 |
| `continuation_source_time` | `datetime` | 50 |
| `trigger_index` | `int` | 51 |
| `trigger_time` | `datetime` | 52 |
| `trigger_event_time` | `datetime` | 53 |
| `reaction_number` | `int` | 54 |
| `reaction_first_time` | `datetime` | 55 |
| `reaction_break_time` | `datetime` | 56 |
| `source_index` | `int` | 57 |
| `source_time` | `datetime` | 58 |
| `price` | `Decimal` | 59 |

#### `SZone` (`s_zone_detector.py`, source line 26)

| Field | Type | Source line |
|---|---|---:|
| `direction` | `str` | 27 |
| `color` | `str` | 28 |
| `formation_type` | `str` | 29 |
| `a_ordinal` | `int` | 30 |
| `a_source_index` | `int` | 31 |
| `a_source_time` | `datetime` | 32 |
| `a_price` | `Decimal` | 33 |
| `a_stop_index` | `int` | 34 |
| `a_stop_time` | `datetime` | 35 |
| `a_stop_event_time` | `datetime` | 36 |
| `order_direction` | `str | None` | 37 |
| `order_reaction_number` | `int | None` | 38 |
| `order_mode` | `str | None` | 39 |
| `order_first_index` | `int | None` | 40 |
| `order_first_time` | `datetime | None` | 41 |
| `order_break_index` | `int | None` | 42 |
| `order_break_time` | `datetime | None` | 43 |
| `order_confirmation_time` | `datetime | None` | 44 |
| `order_box_top` | `Decimal | None` | 45 |
| `order_box_top_source_index` | `int | None` | 46 |
| `order_box_top_source_time` | `datetime | None` | 47 |
| `order_box_bottom` | `Decimal | None` | 48 |
| `order_box_bottom_source_index` | `int | None` | 49 |
| `order_box_bottom_source_time` | `datetime | None` | 50 |
| `order_stop_level` | `Decimal | None` | 51 |
| `order_stop_source_index` | `int | None` | 52 |
| `order_stop_source_time` | `datetime | None` | 53 |
| `reset_reaction_number` | `int | None` | 54 |
| `reset_time` | `datetime | None` | 55 |
| `source_index` | `int` | 56 |
| `source_time` | `datetime` | 57 |
| `price` | `Decimal` | 58 |
| `decision_index` | `int` | 59 |
| `decision_time` | `datetime` | 60 |
| `decision_event_time` | `datetime` | 61 |

#### `EZone` (`e_zone_detector.py`, source line 27)

| Field | Type | Source line |
|---|---|---:|
| `direction` | `str` | 28 |
| `family` | `str` | 29 |
| `number` | `int` | 30 |
| `parent_type` | `str` | 31 |
| `parent_source_index` | `int` | 32 |
| `parent_source_time` | `datetime` | 33 |
| `parent_price` | `Decimal` | 34 |
| `parent_stop_index` | `int` | 35 |
| `parent_stop_time` | `datetime` | 36 |
| `parent_stop_event_time` | `datetime` | 37 |
| `order_direction` | `str` | 38 |
| `order_reaction_number` | `int` | 39 |
| `order_mode` | `str` | 40 |
| `order_causes` | `tuple[str, ...]` | 41 |
| `order_parent_stop_cause_time` | `datetime | None` | 42 |
| `order_reset_leg_reset_time` | `datetime | None` | 43 |
| `order_reset_leg_break_time` | `datetime | None` | 44 |
| `order_first_index` | `int` | 45 |
| `order_first_time` | `datetime` | 46 |
| `order_break_index` | `int` | 47 |
| `order_break_time` | `datetime` | 48 |
| `order_confirmation_time` | `datetime` | 49 |
| `order_box_top` | `Decimal` | 50 |
| `order_box_top_source_index` | `int` | 51 |
| `order_box_top_source_time` | `datetime` | 52 |
| `order_box_bottom` | `Decimal` | 53 |
| `order_box_bottom_source_index` | `int` | 54 |
| `order_box_bottom_source_time` | `datetime` | 55 |
| `order_stop_level` | `Decimal` | 56 |
| `order_stop_source_index` | `int` | 57 |
| `order_stop_source_time` | `datetime` | 58 |
| `source_index` | `int` | 59 |
| `source_time` | `datetime` | 60 |
| `price` | `Decimal` | 61 |
| `decision_index` | `int` | 62 |
| `decision_time` | `datetime` | 63 |
| `decision_event_time` | `datetime` | 64 |

#### `OrderBFormation` (`e_zone_detector.py`, source line 75)

| Field | Type | Source line |
|---|---|---:|
| `reset_time` | `datetime` | 78 |
| `reset_index` | `int` | 79 |
| `owner_first_index` | `int` | 80 |
| `owner_break_index` | `int` | 81 |
| `trigger_level` | `Decimal` | 82 |
| `trigger_source_index` | `int` | 83 |
| `trigger_source_time` | `datetime` | 84 |
| `strict_break_index` | `int` | 85 |
| `strict_break_time` | `datetime` | 86 |
| `strict_break_event_time` | `datetime` | 87 |
| `opposite_extreme` | `Decimal` | 88 |
| `opposite_extreme_source_index` | `int` | 89 |
| `opposite_extreme_source_time` | `datetime` | 90 |
| `evidence_first_index` | `int` | 91 |
| `evidence_break_index` | `int` | 92 |
| `order_reaction_number` | `int` | 93 |
| `order_reaction` | `object` | 94 |
| `order_confirmation_time` | `datetime` | 95 |

#### `StopAll` (`lifecycle_engine.py`, source line 39)

| Field | Type | Source line |
|---|---|---:|
| `direction` | `str` | 40 |
| `number` | `int` | 41 |
| `source_index` | `int` | 42 |
| `source_time` | `datetime` | 43 |
| `price` | `Decimal` | 44 |
| `decision_index` | `int` | 45 |
| `decision_time` | `datetime` | 46 |
| `decision_event_time` | `datetime` | 47 |
| `gate_type` | `str` | 48 |
| `gate_event_time` | `datetime` | 49 |
| `stopped_behavior_type` | `str` | 50 |
| `stopped_behavior_key` | `str` | 51 |
| `stopped_behavior_count` | `int` | 52 |
| `underlying_e_family` | `str | None` | 53 |
| `underlying_e_number` | `int | None` | 54 |
| `order_direction` | `str | None` | 55 |
| `order_reaction_number` | `int | None` | 56 |
| `order_mode` | `str | None` | 57 |
| `order_causes` | `tuple[str, ...]` | 58 |
| `order_parent_stop_cause_time` | `datetime | None` | 59 |
| `order_reset_leg_reset_time` | `datetime | None` | 60 |
| `order_reset_leg_break_time` | `datetime | None` | 61 |
| `order_first_index` | `int | None` | 62 |
| `order_first_time` | `datetime | None` | 63 |
| `order_break_index` | `int | None` | 64 |
| `order_break_time` | `datetime | None` | 65 |
| `order_confirmation_time` | `datetime | None` | 66 |
| `order_box_top` | `Decimal | None` | 67 |
| `order_box_top_source_index` | `int | None` | 68 |
| `order_box_top_source_time` | `datetime | None` | 69 |
| `order_box_bottom` | `Decimal | None` | 70 |
| `order_box_bottom_source_index` | `int | None` | 71 |
| `order_box_bottom_source_time` | `datetime | None` | 72 |
| `order_stop_level` | `Decimal | None` | 73 |
| `order_stop_source_index` | `int | None` | 74 |
| `order_stop_source_time` | `datetime | None` | 75 |
| `stop_index` | `int | None` | 76 |
| `stop_time` | `datetime | None` | 77 |
| `stop_event_time` | `datetime | None` | 78 |

#### `EngineBundle` (`trading_pipeline.py`, source line 611)

| Field | Type | Source line |
|---|---|---:|
| `reaction` | `object` | 612 |
| `blue_line` | `object` | 613 |
| `a_zone` | `object` | 614 |
| `s_zone` | `object` | 615 |
| `e_zone` | `object | None` | 616 |
| `lifecycle` | `object | None` | 617 |

#### `MarketContext` (`trading_pipeline.py`, source line 621)

| Field | Type | Source line |
|---|---|---:|
| `seconds` | `list[object]` | 622 |
| `candles` | `list[object]` | 623 |
| `lower_index` | `object` | 624 |
| `chronology` | `object` | 625 |
| `start_index` | `int` | 626 |
| `end_index` | `int` | 627 |

#### `PipelineState` (`trading_pipeline.py`, source line 812)

| Field | Type | Source line |
|---|---|---:|
| `directions` | `tuple[str, ...]` | 815 |
| `results` | `dict[str, object]` | 816 |
| `reusable_full_context` | `bool` | 817 |
| `initial_order_geometry` | `dict[str, object]` | 818 |
| `internal_reaction_identities` | `dict[str, set[tuple[int, int]]]` | 819 |
| `full_e_zones` | `dict[str, list[object]]` | 820 |
| `full_e_detectors` | `dict[str, object]` | 821 |
| `full_s_detectors` | `dict[str, object]` | 822 |
| `full_lines_by_direction` | `dict[str, list[object]]` | 823 |
| `full_a_by_direction` | `dict[str, list[object]]` | 824 |
| `invalid_a_identities_by_direction` | `dict[str, set[tuple[datetime, int]]]` | 825 |
| `invalid_s_identities_by_direction` | `dict[str, set[tuple[datetime, int]]]` | 826 |
| `full_s_by_direction` | `dict[str, list[object]]` | 827 |
| `full_s_candidates_by_direction` | `dict[str, list[object]]` | 828 |

#### `FullDirectionState` (`trading_pipeline.py`, source line 832)

| Field | Type | Source line |
|---|---|---:|
| `e_zones` | `list[object]` | 835 |
| `e_detector` | `object` | 836 |
| `s_detector` | `object` | 837 |
| `blue_lines` | `list[object]` | 838 |
| `a_zones` | `list[object]` | 839 |
| `invalid_a_identities` | `set[tuple[datetime, int]]` | 840 |
| `invalid_s_identities` | `set[tuple[datetime, int]]` | 841 |
| `s_zones` | `list[object]` | 842 |
| `s_candidates` | `list[object]` | 843 |

#### `DirectionRangeState` (`trading_pipeline.py`, source line 1410)

| Field | Type | Source line |
|---|---|---:|
| `blue_lines` | `list[object]` | 1413 |
| `a_zones` | `list[object]` | 1414 |
| `s_candidates` | `list[object]` | 1415 |
| `accepted_s_zones` | `list[object]` | 1416 |
| `e_zones` | `list[object]` | 1417 |
| `invalid_a_identities` | `set[tuple[datetime, int]]` | 1418 |
| `invalid_s_identities` | `set[tuple[datetime, int]]` | 1419 |

#### `DirectionVisibilityState` (`trading_pipeline.py`, source line 1423)

| Field | Type | Source line |
|---|---|---:|
| `blue_lines` | `list[object]` | 1426 |
| `a_zones` | `list[object]` | 1427 |
| `s_zones` | `list[object]` | 1428 |
| `e_zones` | `list[object]` | 1429 |
| `stopalls` | `list[object]` | 1430 |
| `prepared_order_audit` | `list[object]` | 1431 |

#### `DirectionPolicy` (`direction_policy.py`, source line 21)

| Field | Type | Source line |
|---|---|---:|
| `direction` | `Direction` | 22 |
| `extreme_attr` | `Literal['low', 'high']` | 23 |
| `opposite_extreme_attr` | `Literal['high', 'low']` | 24 |
| `first_reaction_tag` | `Literal['RED', 'GREEN']` | 25 |
| `context_tag` | `Literal['GREEN', 'RED']` | 26 |

## 21. Standalone reconstruction boundary, dependencies, Public API, and cache scope

### 21.1 No external project-source dependency

This Reference is independently reconstructable. All project-owned algorithm source required by the production engine is embedded in Section 26. A reader does **not** need the original Source directory, Git history, another Reference, archived code, conversation history, or hidden developer memory.

### 21.2 Runtime dependencies that are not project-owned source

The reconstructed implementation relies on Python standard-library modules used by the embedded source, including `argparse`, `array`, `bisect`, `dataclasses`, `datetime`, `decimal`, `importlib.util`, `json`, `pathlib`, `sys`, `time`, `types`, `typing`, and `zoneinfo`. The only non-standard-library runtime package imported by the current production snapshot is `orjson`, used by `trading_pipeline.py` for final JSON output. The Reference does not embed Python or third-party package source code.

Project-owned cross-module imports are fully satisfied by the nine embedded modules: `core_utils` and `direction_policy` are shared helpers; the remaining engine modules are dynamically loaded/orchestrated by `trading_pipeline.py`.

### 21.3 Production command-line/Public API

`trading_pipeline.py` exposes `main()` and `parse_arguments()` as the production command-line entry path. The current CLI accepts:

- `--reaction-engine` / `--engine` (required path)
- `--blue-line-engine` / `--blue-engine` (required path)
- `--a-zone-engine` / `--a-engine` (required path)
- `--s-zone-engine` / `--s-engine` (required path)
- `--e-zone-engine` / `--e-engine` (optional path)
- `--lifecycle-engine` / `--stopall-engine` (optional path)
- `--blue-lines enabled|disabled` (default `enabled`)
- `--a-zones enabled|disabled` (default `enabled`)
- `--s-zones enabled|disabled` (default `enabled`)
- `--data` (required RAW JSON path)
- `--timeframe` (required integer, must be at least one second)
- `--from-time` (required epoch-second presentation lower bound)
- `--to-time` (required epoch-second presentation upper bound)
- `--direction bullish|bearish|both` (required)

The input RAW object is a JSON array of rows containing `time`, `open`, `high`, `low`, and `close`. The pipeline normalizes the full physical RAW before range filtering. Progress telemetry is emitted to stderr with the `QG_PROGRESS:` prefix so stdout remains reserved for the final JSON payload.

### 21.4 Global mutable state and cache safety

Performance indexes/caches are implementation details, not trading rules. Calculation-sensitive caches must preserve all algorithmic context and may not leak mutable lifecycle state across directions or RAW runs. The current source contains immutable-source reuse helpers (for example shared timestamp/lower-timeframe indexes and pipeline datetime conversion caches) and per-detector/per-run Order/search caches. They are valid only while they preserve exact first-event, boundary, equality, ownership, provenance, ordering, and Decimal semantics.

Never introduce a module-level trading-state cache keyed only by a candle index, source index, direction, or similarly incomplete identity. Such a cache can contaminate multiple RAW files or Bullish/Bearish runs because indexes repeat across calculations.

## 22. Complete terminology and object/lifecycle glossary

### 22.1 Market chronology terms

- **Main candle:** the selected computational timeframe candle (30 seconds in primary regression examples, but the engine accepts any positive integer-second timeframe).
- **Lower candle / exact event:** normalized one-second data used to resolve the first strict crossing and same-main-candle ordering.
- **First:** the main candle that opens a Reaction candidate.
- **Break / Breakout / Breakdown candle:** the main candle containing the strict confirmation crossing of the Reaction box.
- **Confirmation event:** the exact lower-timeframe event that first strictly crosses the confirmation boundary.
- **Reset event:** the exact event that strictly crosses the previous confirmed opposite box boundary and closes/restarts Reaction ownership.
- **Source:** the main candle/time/price chosen by a behavior or structural object as its canonical price provenance.
- **Decision:** the exact event that resolves an undecided S/E/StopAll outcome.
- **Stop:** the first strict directional crossing of an accepted behavior/order/line level after its eligible start.

### 22.2 Reaction modes

- **Mode A:** leg-start/direct-after-reset Reaction. It owns a frozen leg boundary and can be structurally invalidated before confirmation if that boundary is strictly crossed first.
- **Mode B:** normal continuation Reaction after an already-confirmed Reaction sequence. Its box construction is based on the current running directional context and previous confirmed Reaction state.

### 22.3 Blue Line types

- **Scale Blue:** generated when a Reaction's confirmed Fibonacci strike count increases relative to the preceding Reaction and spacing/health rules permit a new line.
- **Reset Blue:** generated from a valid Reset event when Blue spacing permits. It carries the Reset broken level and can be calculation-invalid under the double-stop rule while still participating in the special A route defined by the A engine.
- **Internal Blue:** a Blue whose owner/source geometry belongs to protected internal Reaction space. It can remain calculation evidence while public visibility is filtered.

### 22.4 A behavior types

The code serializes A with one common `AZone` schema rather than a public subtype field, but there are two formation routes:

1. **Ordinary adjacent-Blue A** — formed from two eligible adjacent Blue states after the exact stop/continuation chronology is satisfied and a qualifying same-direction Reaction confirms the candidate.
2. **Special double-stop A** — formed when an invalid Reset Blue and the preceding valid Blue satisfy the same-main-candle strict crossing route, then a qualifying Reaction validates the candidate.

A's final source is not automatically the trigger candle: source/price is the directional extreme from trigger-main-candle start through the **exact confirming Reaction event**, inclusive. Prices after exact confirmation inside the same Break main candle cannot retroactively move A.

### 22.5 S behavior formation families

- **Type3:** S resolves in the A-stop window before a qualifying new opposite Order is needed/available, according to the exact Type3 evidence route in `s_zone_detector.py`.
- **Simple:** S candidate geometry comes from the ordinary aligned trend/Order interval rather than a nested Reaction owner.
- **Advanced:** a nested same-direction Reaction wholly inside the opposite Order before Order confirmation owns the S candidate geometry.

S color (`red`/`blue`) is a behavior family label and is **not** synonymous with market direction. Family priority is invariant across Bullish/Bearish calculations.

### 22.6 E behavior concepts

- **Parent:** an accepted S or E whose strict stop opens the possibility of the next E.
- **Parent-stop Order:** an opposite-direction Order discovered/owned because a parent behavior stopped.
- **Carried-live Order:** an already-accepted physical Order that remains eligible for a newer parent under exact lifecycle rules.
- **Reset-leg Order_B:** an independent Order cause created when a **Bearish Reaction Reset** yields a Breakout→Reset inclusive minimum-Low floor, that floor is later strictly broken (`Low < floor`), raw **Bullish Reaction geometry** exists in the closed floor-source→strict-break-main-candle interval, and the first canonical Bullish Reaction after the gate is assigned as the physical Order_B. The same closed interval supplies the maximum-High ceiling. Reset validity/lifecycle/Internal status is ignored only for the evidence geometry test.
- **Direct Order_A:** direct post-parent-stop geometry, including the narrow fresh-trend-leg route after a stopped E.
- **Shared accepted Order use:** a physical Order already accepted by another behavior/structure may decide the current S/E candidate when exact stop chronology is valid. The creating parent need not match. `carried-live` means already active at the candidate parent stop; `accepted-live` means confirmed after it. Both are use provenance only.
- **Order cause vs Reaction mode:** `Order_A`/`Order_B` describe why the physical Order exists. `Reaction.mode` describes the Reaction engine geometry (`A` or `B`). They are independent fields/concepts.
- **E family:** `red` or `blue`; Red family has higher invariant sequence priority than Blue family.
- **E number:** recursive position inside the accepted family chain (E1, E2, E3, ...), assigned after candidate-chain reconciliation rather than by naive chronological counting.

### 22.7 StopAll

StopAll is a behavior generated by three lifecycle gates: (1) E-driven `sequence-group-stop`, (2) E-driven `stopall-stop`, and (3) accepted-S `opposite-s-group-stop`. For gate (3), counting is **pending per exact accepted Blue behavior group**, independent of current dominance: `S Blue` shares one group while each E number is distinct. Any one group reaching `count >= 2` may promote the next accepted `S Red` with a native Mode-B Order to StopAll, provided no intervening accepted Red S/E has resolved the pending evidence. Every ordinary accepted Red S (including Mode A) and accepted Red E clears these pending repeats. Different E numbers never add together. No extra latest-Blue strict-stop condition is imposed. E-driven same-key `sequence-group-stop` retains its separate current-owner count and strict-stop chronology. StopAll is a hard boundary that clears all counters and active owners.

### 22.8 OrderAudit

OrderAudit is not a separate market behavior. It is the canonical ledger of physical Orders keyed by `(FirstIndex, BreakIndex)`, with merged causes/provenance and exact strict stop-hit chronology. One physical Order can have multiple accepted causes, but one exact parent-stop provenance cannot be consumed twice to create multiple physical Orders.

## 23. Directional rule matrix and full behavior transition catalog — Bearish

### 23.1 Mechanical directional map

| Concept | Bearish rule | Bullish mirror |
|---|---|---|
| Directional extreme | maximum / High | minimum / Low |
| Strict behavior/Blue stop | `High > level` | `Low < level` |
| Reaction First color | GREEN | RED |
| Reaction confirm | `Low < BoxBottom` | `High > BoxTop` |
| Reset boundary | previous confirmed BoxTop | previous confirmed BoxBottom |
| Confirmation-side exact scan | Low | High |
| A source extreme | maximum High | minimum Low |
| Chained Blue carried stop | maximum High over complete interval | minimum Low over complete interval |
| Opposite Order direction | Bullish | Bearish |
| Order_B Reset owner | Bearish Reaction Reset | Bullish Reaction Reset |
| Order_B primary extreme | minimum Low, owner Breakout→Reset inclusive | maximum High, owner Breakout→Reset inclusive |
| Order_B strict trigger | `Low < floor` after Reset | `High > ceiling` after Reset |
| Order_B evidence geometry | raw Bullish geometry in closed floor-source→strict-break candle range | raw Bearish geometry in closed ceiling-source→strict-break candle range |
| Order_B other edge | maximum High over same closed evidence range | minimum Low over same closed evidence range |
| Order_B physical Order | first canonical Bullish Reaction after gate | first canonical Bearish Reaction after gate |

### 23.2 Invariant rules that must not be directionally swapped

- Doji is GREEN.
- Red/Blue behavior family labels remain Red/Blue.
- Behavior priority remains `StopAll > E Red > S Red > E Blue > S Blue > A`.
- Same-source Red E family dominance remains higher than Blue E family dominance.
- Order identity remains `(FirstIndex, BreakIndex)`.
- Full-RAW calculation and presentation filtering rules remain unchanged.
- Exact invalidation-first ties stay invalidation-first where the implementation checks them in that order.

### 23.3 End-to-end Bearish behavior flow

```text
Bullish/ Bearish RAW candles
    ↓
Bearish Reaction + Reset geometry (while Bullish Reaction/Reset is also calculated)
    ↓
Bearish Scale/Reset Blue evidence
    ↓
Blue stops + adjacent-pair / double-stop chronology
    ↓
Bearish A candidate → validating Bearish Reaction exact confirmation → accepted A
    ↓ strict High > A.price
A stop
    ↓
first eligible Bullish Order geometry + Type3/Simple/Advanced S logic
    ↓
accepted S Red or S Blue
    ↓ strict High > S.price (and accepted Order routes)
recursive E candidates / parent-stop Order_A, carried-live, and canonical V5.2.0 Reset-leg Order_B routes
    ↓
family/number/same-source/lifecycle reconciliation
    ↓
accepted E1/E2/E3... Red/Blue
    ↓
sequence grouping + strict stops + priority arbitration
    ↓
StopAll1/StopAll2... when qualified
    ↓
final lifecycle visibility + OrderAudit + serialization
```

## 24. Worked validation examples (documentation examples, never production hardcodes)

These examples are included to make chronology and ownership concrete. They are regression fixtures/examples only; a conforming implementation must derive them from general rules and must never branch on their timestamps/prices.

### 24.1 Bearish exact lower-timeframe Reaction confirmation and A ownership

XAUUSD 30s reference shape: A source is `2026-09-04 16:57:30`; the validating Bearish Reaction has FirstGreen `16:58:00`, BoxBottom from `16:57:30`, BoxTop from `16:58:00`, and exact lower-timeframe breakdown confirmation at `16:58:38`. A source ownership freezes at exact confirmation; later remainder prices in the same Break main candle cannot retroactively move A to `16:58:30`.

### 24.2 Bearish Order bounded Mode-A anchor

Reference Order `2026-09-07 10:14:00` keeps its stop source at `10:13:30`. When the bounded gate resolver returns `continue`, a genuinely resolved current-leg Mode-A anchor is authoritative; an older Reset cannot overwrite that anchor merely because historical Reset provenance exists.

### 24.3 Bearish chained Blue carried-stop mirror

For a stopped Bearish Blue, locate the first valid Bearish Reaction after the stop and compute the **maximum High** from the Blue stop main candle through the complete Breakout main candle, inclusive. This is now the exact mirror of Bullish minimum-Low chronology. Historical USOIL reference geometry around Blue `2026-09-11 09:23:00` is an example of the carried-stop route, but the production rule is fully general.

### 24.4 Exact-source E continuation ownership is direction-invariant

The invalid-S same-source cross-family rule does not depend on Bullish/Bearish direction. Family labels remain invariant; only price geometry mirrors. A price-mirrored validation fixture preserves the same `E1 Blue → E2 Blue → E3 Blue` ownership sequence without allowing an invalid Red S root to steal the physical source.

### 24.5 Bearish validation of exact-key S-reversal StopAll ownership

Bearish mirrors price geometry, not Red/Blue family labels. After every hard StopAll boundary, all current owner state and pending Blue-repeat counters restart from zero. `E1 Blue → E2 Blue → E3 Blue` contributes one occurrence to each distinct group, never three occurrences of the same group. A repeated exact group, e.g. `E3 Blue`, may arm a pending reversal until an accepted Red S/E resolves it. An accepted Mode-B S Red promotes to StopAll only while that evidence remains pending; a Mode-A/no-Order S Red remains ordinary S and also clears the pending evidence. Red E clears pending evidence but not independent E-driven StopAll state. This is the direction-invariant V5.4.7 refinement of V5.4.6 native Mode-B eligibility. No timestamp or fixture-specific production branch is allowed.

### 24.6 Canonical Bearish Order_B worked example — XAUUSD 30s

Using `RAW FOREXCOM_XAUUSD 5S FROM 2026-09-03 18-44-00 TO 2026-09-19 00-29-35(1).json` in Bearish 30s calculation:

- Bearish Reaction First: `2026-09-04 09:24:00`; Breakout main candle: `09:24:30`.
- That Bearish Reaction resets on main candle `09:25:30`.
- Breakout→Reset inclusive minimum Low is `4467.370`, owned by main candle `09:25:00`; this is the Reset-leg floor.
- First exact lower-timeframe strict floor break is `2026-09-04 09:42:10` (`Low < 4467.370`), contained in the `09:42:00` main candle.
- Closed evidence interval is therefore `09:25:00 .. 09:42:00`, inclusive.
- Raw Bullish Reaction geometry exists inside that exact interval (First `09:27:00`, Break `09:28:00`). Its later Reset/lifecycle status is irrelevant to this evidence test.
- Maximum High over the same closed interval is `4473.530`, owned by `09:31:30`; this is the Reset-leg ceiling.
- The first canonical Bullish Reaction after the gate has First `09:45:00`, Break `09:45:30`, exact confirmation `09:45:55`; that physical Reaction is Order_B.

These timestamps/prices are regression evidence only and must never be hardcoded.


### 24.7 Shared accepted-Order regression case — XAUUSD Bearish 30s

On `RAW FOREXCOM_XAUUSD 5S FROM 2026-09-03 18-44-00 TO 2026-09-19 00-29-35(1).json`, physical Bullish Order First `2026-09-04 17:45:30` is already accepted from an A parent-stop. Its canonical stop source is `Low 2026-09-04 17:41:30 = 4419.235`, exact confirmation is `17:55:45`, and exact strict Order stop is `18:24:40`. A different Red S parent stopped earlier at `17:13:05`; the Order is still eligible because shared accepted-Order confirmation does not require matching parents. The Bearish E source over the complete parent-stop→Order-stop main-candle interval is `High 2026-09-04 18:05:30 = 4442.395`. The Order retains its original A parent-stop creation cause; the E use is `accepted-live`. These values are regression evidence only and must never be hardcoded.

### 24.8 Cycle/stage-order regression — USOIL Bearish 30s

On `RAW FXCM_USOIL 5S FROM 2026-09-11 02-53-30 TO 2026-09-15 11-03-45.json`, accepted `S Blue @ 2026-09-11 17:43:00` already owns the later stage. The would-be `A @ 2026-09-11 18:01:30` is a rejected fallback A under that S-owned transition and therefore must not become a behavior. The accepted S is not consumed by the rejected A. This example is regression evidence only and must never be timestamp-hardcoded.

### 24.9 V5.4.2 Bearish XAUUSD 30s regression

On `RAW FOREXCOM_XAUUSD 5S FROM 2026-08-25 03-53-30 TO 2026-09-19 00-29-30.json`, the live Scale Blue pair must not create `A 11:07:00`. The valid pair resolves through real Blue stops and creates `A 11:15:30`, then `S Red 11:54:30`; a second S Red at `12:47:00` forms the same-key S sequence, and the qualifying E decision at `13:20:30` becomes `StopAll1`. The later qualifying E at `15:20:30` becomes `StopAll2`. That StopAll is a hard boundary. In the fresh cycle, `E1 Blue 16:21:30` is the dominant owner before the next S transition; after `A 17:36:30` stops, `S Red 17:43:00` becomes the new dominant S behavior rather than an immediate StopAll, followed by `E1 Red 17:56:30`. These timestamps are regression evidence only; no production rule may branch on them.

### 24.10 V5.4.3 Bearish XAUUSD 30s regression

On `RAW FOREXCOM_XAUUSD 5S FROM 2026-08-25 03-53-30 TO 2026-09-19 00-29-30.json`: after `StopAll 2026-08-26 02:21:30`, the higher-priority dominant key is `E1 Red`, repeated at `06:13:30`, `09:00:30`, and `2026-08-27 03:34:30`; lower-priority Blue E progression does not replace that Red owner. Therefore `S Red 2026-08-27 03:55:00` remains accepted and is not StopAll, while the later `A 04:41:30` is cycle-invalid and absent. The Bullish Order whose First is `08:36:30` has canonical `BoxTop=4620.825` from main `08:36:00`, `BoxBottom=4619.565` from main `08:37:00` (exact lower event `08:37:10`), and Breakout main `08:37:30`; the later `08:37:50` low is post-confirmation and cannot rewrite the box. On `2026-08-28`, a single dominant `E3 Blue` is not enough to promote `S Red 03:41:00` to StopAll. After `A 06:22:00` stops, Bearish Reaction `First=06:31:30 / Breakout=06:32:00` produces Type-4 candidate `4587.505` at main `06:30:30`; Blue `06:34:00` forms no later than the exact strict crossing (`06:34:15`), so the candidate becomes `S Blue Type-4`. These timestamps/prices are regression evidence only and must never be hardcoded.

### 24.11 V5.4.4 cycle-wide Blue-repeat StopAll regression

On `RAW FOREXCOM_XAUUSD 5S FROM 2026-08-25 03-53-30 TO 2026-09-19 00-29-30.json`, the historical 5.4.4 Bullish worked example `S Red @ 2026-09-04 02:36:00` is NOT reproduced by the complete full-RAW calculation in either current baseline or V5.4.6. Do not treat it as a current expected Bullish behavior. The actual retained Bearish `StopAll1 @ 2026-09-04 02:36:00` has an accepted native Mode-B formation Order. A valid accepted-S reversal requires an exact Blue group repeated at least twice since the last accepted Red S/E or hard StopAll boundary AND the incoming S Red native Mode-B Order. The same exact-key repeat threshold applies to `S Blue × 2`, `E1 Blue × 2`, `E5 Blue × 2`, or any other single numbered Blue E group, provided the incoming S Red has native Mode-B Order geometry. `E1 Blue + E2 Blue` does not qualify because they are different groups. Bearish uses the identical lifecycle rule; only directional price geometry mirrors. These timestamps are regression evidence only and must never be hardcoded.

### 24.12 V5.4.5 historical Mode-B refresh regression (superseded by V5.4.8)

On `RAW FOREXCOM_XAUUSD 5S FROM 2026-08-25 03-53-30 TO 2026-09-19 00-29-30.json` at 30s, the accepted A at `2026-09-09 03:33:30` strictly stops and opens opposite-Order ownership. The canonical opposite Order stream then confirms consecutive native Mode-B Orders with First times `04:16:00`, `04:17:30`, `04:20:30`, and `04:24:00` while S is still undecided. Under V5.4.5, each later Mode-B confirmed strictly before the current provisional S decision refreshes the stopped-A Order owner, so the final owner is the `04:24:00` Order. Its stop source remains `04:21:00`. Rebuilding S from that final Order produces accepted `S Red @ 04:29:30`; the former `S Blue @ 04:45:00` is not calculation-valid and disappears. Downstream calculation then produces `E1 Red @ 05:15:30`, and the already-existing E same-key `sequence-group-stop` lifecycle gate promotes the `06:23:00` source to StopAll. A native Mode-A Order ends a replaceable Mode-B chain, and no Order confirmed at/after an already-resolved S decision may replace it. The same chronology rule mirrors exactly in both market directions. These timestamps are regression evidence only and must never be hardcoded. Under the current 5.4.8 rule, the initial `04:16:00` Order remains the sole A-owned Order_A; the previously refreshed `04:24:00` Order cannot inherit its cause. Thus the prior `S Red 04:29:30` is not a valid current-version anchor; the complete updated full-RAW Bearish calculation emits `S Blue 04:45:00`. All downstream E/StopAll differences must be traced as connected effects, not silently matched to V5.4.5 history.

## 25. Reconstruction procedure and implementation traps

- Treating a calculation-accepted Order as usable only by the behavior that originally created it; accepted physical Orders are parent-neutral for S/E confirmation when their exact strict stop chronology is eligible.

### 25.1 Recommended implementation order

1. Implement exact Decimal/raw normalization and main/lower candle construction.
2. Implement `direction_policy` and chronology queries (`first_less`, `first_greater`, extrema, main-index mapping).
3. Reproduce both-direction Reaction/Reset output, including exact same-candle races and post-confirmation resets.
4. Add Internal-Reaction classification and published/canonical Reaction views.
5. Implement Blue Scale/Reset logic and internal/public Blue distinction.
6. Implement A ordinary/double-stop/chained-stop logic and exact-confirmation source ownership.
7. Implement S and stopped-A OrderAudit.
8. Implement E Order discovery + recursive chain generation.
9. Implement lifecycle reconciliation and final accepted/invalid A/S/E sets.
10. Implement StopAll once reconciled E/S history is stable.
11. Implement final visibility and serializers last.

### 25.2 Common reconstruction mistakes that change output

- Allowing a rejected fallback A to consume an accepted S and then using S descendants of that rejected A in E/StopAll calculation; this violates the normative `A → S → E → StopAll` stage order.

- Slicing RAW before calculation instead of filtering only at serialization.
- Treating equality as a stop/confirmation.
- Using main-candle OHLC ordering when exact lower chronology is available.
- Letting post-confirmation remainder prices retroactively move A source.
- Reusing a confirmation/Reset main candle as a new normal Reaction First when the exact remainder ownership rule forbids it.
- Dropping internal Reaction/Blue evidence too early.
- Treating all invalid S as irrelevant; some invalid S remains evidence/order provenance even when it cannot create a cross-family E root.
- Counting E numbers before same-source/family/lifecycle reconciliation.
- Recomputing historical StopAll after restoring an independent S-root E branch; accepted StopAll prefix/history has scoped immutability.
- Consuming one exact parent-stop cause more than once for two physical Orders.
- Letting a duplicate later parent-stop Order influence E deadline/selection before single-consumption arbitration.
- Emitting a public S/E/StopAll whose `(orderFirstIndex,orderBreakIndex)` is absent from final OrderAudit, or rebuilding OrderAudit without resynchronizing later accepted E branch/root changes.
- Mirroring Red/Blue family priority; it is invariant and must not swap.
- Reusing the pre-V5.2.0 opposite-Reset Order_B algorithm; Order_B must start from a Reset of the **same trend direction**.
- Treating `Order_B` as `Reaction.mode == B`; formation cause and native Reaction mode are independent.
- Requiring the opposite evidence Reaction to survive normal Reset/lifecycle/public/Internal rules; for Order_B evidence, raw geometry alone is sufficient.
- Searching evidence outside the closed primary-extreme-source→strict-break-main-candle interval, or excluding either endpoint.
- Using a later equal extreme as the source; Order_B extrema retain the first main candle owning the final equal value.
- Keeping multiple Reset-leg causes on one physical Order in final audit; latest valid `(resetTime, strictBreakEventTime)` is authoritative.

### 25.3 Observable-equivalence rule

Performance structures (caches, segment trees, precomputed indexes, bisect tables) may be rewritten. Their replacement is valid only if it returns the same **first** strict event, the same extrema/source tie behavior, and the same accepted object identities/provenance for every input.

### 25.4 HPZR1 performance implementation notes

This document revision is a behavior-preserving implementation snapshot. The following structures are performance details, not new trading rules:

- Immutable lower-timeframe range indexes replace repeated physical-row scans only where they prove the identical strict predicate and preserve first/last tie semantics.
- Immutable Reaction/Reset/Blue chronologies are pre-indexed and bisected instead of rebuilt/scanned for every A/S query.
- E canonical physical Order stop provenance is cached only for exact canonical Reaction objects; noncanonical bounded Order_A geometry remains on the authoritative uncached path.
- Repeated valid Order_B origins mapping to one physical Order are materialized once using the pre-existing rule that the latest valid Reset-leg cause is authoritative.
- `order_audit` remains the authoritative ledger; secondary indexes are lookup accelerators only and never replace authoritative ordering/provenance state.
- All performance caches are scoped to one calculation run. No module-level mutable trading-state cache is added.

**Zero-difference release rule:** these structures are valid only while stage/final regression remains exact. If any behavior, field, ordering, Decimal string, ownership/provenance, or serialized value differs, the optimization is invalid.

## 26. Exact production source snapshot — complete standalone implementation appendix
This section embeds the complete project-owned Python implementation required to reconstruct the current engine. No production module is abbreviated, omitted, replaced with ellipses, or delegated to an external repository. Standard-library and third-party package source code is intentionally not embedded; Section 21 declares those runtime dependencies.
**Authority rule:** the semantic sections explain what the engine must do. The code below is the complete implementation snapshot for low-level reconstruction and disambiguation. During Reference generation, synchronization is verified by direct text comparison and semantic review; SHA-256 markers are retained only as optional integrity metadata.
### 26.1 `reaction_engine.py`

- Source version: `9.8.0`
- Last modified declared by module: `2026-09-22 00:35:00 +03:30`
- Lines: `2406`
- Role: Authoritative Reaction/Reset geometry, candle semantics, lower-timeframe chronology, canonical Order-stop geometry, and Internal-Reaction classification.
- Optional integrity SHA-256: `bea0d5a5e95ee15ad54d024f6c01b8c777ba2abcc3c8e671118f1ae2df28f2a6`

<!-- SOURCE_FILE_BEGIN:reaction_engine.py:SHA256=bea0d5a5e95ee15ad54d024f6c01b8c777ba2abcc3c8e671118f1ae2df28f2a6 -->
```python
"""Authoritative Reaction geometry and shared market chronology.

Owns candle semantics, Bullish/Bearish Reaction and Reset detection, exact
lower-timeframe chronology, canonical Order-stop geometry, and
Internal-Reaction classification. It does not decide Blue/A/S/E/StopAll
visibility or lifecycle priority.
"""

from __future__ import annotations

import bisect
from array import array
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Iterable, Sequence

from direction_policy import policy_for


REACTION_ENGINE_VERSION = "9.8.0"
REACTION_ENGINE_LAST_MODIFIED = "2026-09-22 00:35:00 +03:30"

_SEQUENCE_TIME_INDEXES: dict[int, tuple[Sequence[Candle], list[datetime]]] = {}

@dataclass(frozen=True, slots=True)
class Candle:
    index: int
    timestamp: datetime
    display_time: str
    tag: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal


@dataclass(slots=True)
class Candidate:
    first_idx: int
    first_time: str
    box_top_source_idx: int
    box_top_source_time: str
    box_top: Decimal
    box_bottom_source_idx: int
    box_bottom_source_time: str
    box_bottom: Decimal
    mode: str
    anchor_idx: int | None = None
    anchor_value: Decimal | None = None
    leg_boundary_value: Decimal | None = None
    break_idx: int | None = None
    break_time: str | None = None
    intrabar_start: datetime | None = None
    cross_direction_origin: bool = False
    cross_direction_chain_owner: bool = False
    order_gate_decision: str | None = None
    behavior_public_number: int | None = None
    behavior_public_box_top: Decimal | None = None
    behavior_public_box_bottom: Decimal | None = None
    behavior_confirmation_time: datetime | None = None
    behavior_first_time: datetime | None = None
    behavior_internal: bool = False


@dataclass(frozen=True, slots=True)
class ResetEvent:
    index: int
    display_time: str
    second_time: str | None
    broken_level: Decimal
    from_first_idx: int


@dataclass(frozen=True, slots=True)
class IntrabarAnalysis:
    event_second: Candle
    extreme: Decimal
    extreme_source: Candle


@dataclass(frozen=True, slots=True)
class DetectionResult:
    direction: str
    reactions: list[Candidate]
    resets: list[ResetEvent]
    start_index: int
    end_index: int


def classify_candle_color(open_price: Decimal, close_price: Decimal) -> str:
    """Match Lightweight Charts: Open <= Close is an up/green candle."""
    return "GREEN" if open_price <= close_price else "RED"


def opposite_direction(direction: str) -> str:
    """Return the exact Bullish/Bearish mirror direction."""
    return policy_for(direction).opposite_direction


class DetectorBase:
    def __init__(
        self,
        candles: Sequence[Candle],
        one_second_candles: Sequence[Candle],
        start_index: int,
        end_index: int,
    ) -> None:
        self.candles = candles
        self.seconds = one_second_candles
        self.start_index = start_index
        self.end_index = end_index
        self.main_times = self._shared_time_index(candles)
        self.second_times = self._shared_time_index(one_second_candles)
        self.lower_index = shared_lower_timeframe_index(one_second_candles)
        self._reaction_break_index_cache: dict[str, tuple[int, list[int]]] = {}

        if len(candles) > 1:
            self.timeframe = candles[1].timestamp - candles[0].timestamp
        else:
            self.timeframe = timedelta(seconds=1)

        if self.timeframe.total_seconds() <= 0:
            raise ValueError("Main timeframe must be positive.")

    @staticmethod
    def _shared_time_index(candles: Sequence[Candle]) -> list[datetime]:
        """Build one immutable-source timestamp index per calculation process."""
        key = id(candles)
        cached = _SEQUENCE_TIME_INDEXES.get(key)
        if cached is not None and cached[0] is candles:
            return cached[1]
        times = [candle.timestamp for candle in candles]
        _SEQUENCE_TIME_INDEXES[key] = (candles, times)
        return times

    def seconds_between(self, start: datetime, end: datetime) -> Iterable[Candle]:
        left = bisect.bisect_left(self.second_times, start)
        right = bisect.bisect_left(self.second_times, end)
        return (self.seconds[index] for index in range(left, right))

    def main_source_for_time(self, timestamp: datetime) -> Candle | None:
        position = bisect.bisect_right(self.main_times, timestamp) - 1
        if position < self.start_index or position > self.end_index:
            return None
        end = (
            self.candles[position + 1].timestamp
            if position + 1 < len(self.candles)
            else self.candles[position].timestamp + self.timeframe
        )
        if timestamp < end:
            return self.candles[position]
        return None

    def minimum_low(self, start_index: int, end_index: int) -> tuple[Decimal, Candle]:
        source = self.candles[start_index]
        candles = self.candles
        for index in range(start_index + 1, end_index + 1):
            candle = candles[index]
            if candle.low < source.low:
                source = candle
        return source.low, source

    def maximum_high(self, start_index: int, end_index: int) -> tuple[Decimal, Candle]:
        source = self.candles[start_index]
        candles = self.candles
        for index in range(start_index + 1, end_index + 1):
            candle = candles[index]
            if candle.high > source.high:
                source = candle
        return source.high, source


class BullishDetector(DetectorBase):
    def green_run_peak_before(self, first_red_index: int) -> tuple[Decimal, Candle]:
        run_end = first_red_index - 1
        if run_end < self.start_index or self.candles[run_end].tag != "GREEN":
            raise ValueError("Mode-A FirstRed must immediately follow a GREEN candle.")

        run_start = run_end
        while run_start > self.start_index and self.candles[run_start - 1].tag == "GREEN":
            run_start -= 1
        return self.maximum_high(run_start, run_end)

    def breakout_analysis(
        self, candidate: Candidate, breakout_candle: Candle
    ) -> IntrabarAnalysis | None:
        start_index = (
            candidate.box_top_source_idx + 1
            if candidate.box_top_source_idx < candidate.first_idx
            else candidate.box_top_source_idx
        )
        start = candidate.intrabar_start or self.candles[start_index].timestamp
        end = breakout_candle.timestamp + self.timeframe
        left = bisect.bisect_left(self.second_times, start)
        right = bisect.bisect_left(self.second_times, end)
        crossing = self.lower_index.first_greater(left, right, candidate.box_top)
        if crossing is None:
            return None
        minimum_low, minimum_position = self.lower_index.range_minimum(
            left, crossing + 1
        )
        minimum_time = self.second_times[minimum_position]
        source = self.main_source_for_time(minimum_time)
        if source is None:
            return None
        return IntrabarAnalysis(
            self.seconds[crossing], minimum_low, source
        )

    def mode_a_invalidation_before_breakout(
        self, candidate: Candidate, candle: Candle
    ) -> bool:
        # A Mode-A candidate belongs to the complete leg that opened at the
        # analysis/Reset boundary.  Later lower RED candles are internal
        # BoxBottom updates; only a strict break of the frozen leg floor can
        # invalidate the candidate before its BoxTop breaks.
        invalidation_level = (
            candidate.anchor_value
            if candidate.anchor_value is not None
            else candidate.leg_boundary_value
        )
        if invalidation_level is None:
            return False
        if candle.low >= invalidation_level:
            return False
        if candle.high <= candidate.box_top:
            return True

        end = candle.timestamp + self.timeframe
        left = bisect.bisect_left(self.second_times, candle.timestamp)
        right = bisect.bisect_left(self.second_times, end)
        invalidation = self.lower_index.first_less(
            left, right, invalidation_level
        )
        breakout = self.lower_index.first_greater(
            left, right, candidate.box_top
        )
        if invalidation is None:
            return breakout is None
        if breakout is None:
            return True
        # The legacy loop checks Low first inside one lower-timeframe candle,
        # so invalidation wins a true same-second tie.
        return invalidation <= breakout

    def confirmed_reset_before_breakout(
        self, candidate: Candidate | None, candle: Candle, confirmed_bottom: Decimal
    ) -> bool:
        if candidate is None or candle.high <= candidate.box_top:
            return True

        end = candle.timestamp + self.timeframe
        left = bisect.bisect_left(self.second_times, candle.timestamp)
        right = bisect.bisect_left(self.second_times, end)
        reset = self.lower_index.first_less(left, right, confirmed_bottom)
        breakout = self.lower_index.first_greater(
            left, right, candidate.box_top
        )
        if reset is None:
            return breakout is None
        if breakout is None:
            return True
        # Reset is checked before breakout within one lower-timeframe candle.
        return reset <= breakout

    def post_breakout_reset(
        self,
        analysis: IntrabarAnalysis | None,
        box_bottom: Decimal,
        breakout_candle: Candle,
    ) -> Candle | None:
        if analysis is None:
            return None
        start = analysis.event_second.timestamp + timedelta(microseconds=1)
        end = breakout_candle.timestamp + self.timeframe
        left = bisect.bisect_left(self.second_times, start)
        right = bisect.bisect_left(self.second_times, end)
        position = self.lower_index.first_less(left, right, box_bottom)
        return None if position is None else self.seconds[position]

    def detect(self, *, first_only: bool = False) -> DetectionResult:
        reactions: list[Candidate] = []
        resets: list[ResetEvent] = []
        mode = "A"
        state = "SCANNING"
        last_confirmed_bottom: Decimal | None = None
        last_confirmed_first_idx: int | None = None
        running_peak: Decimal | None = None
        running_peak_src: int | None = None
        leg_open_low: Decimal | None = None
        leg_just_started = True
        anchor_red: Candle | None = None
        anchor_red_origin: str | None = None
        reset_context: Candle | None = None
        candidate: Candidate | None = None

        for index in range(self.start_index, self.end_index + 1):
            candle = self.candles[index]
            reset_detected = (
                last_confirmed_bottom is not None and candle.low < last_confirmed_bottom
            )
            reset_occurs_first = reset_detected
            if reset_detected and state == "WAITING":
                reset_occurs_first = self.confirmed_reset_before_breakout(
                    candidate, candle, last_confirmed_bottom
                )

            if reset_occurs_first:
                resets.append(
                    ResetEvent(
                        index=candle.index,
                        display_time=candle.display_time,
                        second_time=None,
                        broken_level=last_confirmed_bottom,
                        from_first_idx=last_confirmed_first_idx,
                    )
                )
                candidate = None
                last_confirmed_bottom = None
                last_confirmed_first_idx = None
                running_peak = None
                running_peak_src = None
                mode = "A"
                state = "SCANNING"
                leg_open_low = None
                leg_just_started = True
                anchor_red = candle if candle.tag == "RED" else None
                anchor_red_origin = "reset" if candle.tag == "RED" else None
                reset_context = candle
                continue

            if state == "WAITING":
                assert candidate is not None

                if (
                    candidate.mode == "A"
                    and self.mode_a_invalidation_before_breakout(candidate, candle)
                ):
                    candidate = None
                    state = "SCANNING"
                    anchor_red = candle if candle.tag == "RED" else None
                    anchor_red_origin = (
                        "candidate_invalidation" if candle.tag == "RED" else None
                    )
                    continue

                if candle.low < candidate.box_bottom:
                    candidate.box_bottom = candle.low
                    candidate.box_bottom_source_idx = candle.index
                    candidate.box_bottom_source_time = candle.display_time

                if candle.high > candidate.box_top:
                    candidate.break_idx = candle.index
                    candidate.break_time = candle.display_time
                    analysis = self.breakout_analysis(candidate, candle)

                    if (
                        candidate.box_bottom_source_idx == candle.index
                        and analysis is not None
                    ):
                        candidate.box_bottom = analysis.extreme
                        candidate.box_bottom_source_idx = analysis.extreme_source.index
                        candidate.box_bottom_source_time = (
                            analysis.extreme_source.display_time
                        )

                    confirmed = replace(candidate)
                    reactions.append(confirmed)
                    if first_only:
                        return DetectionResult(
                            direction="bullish",
                            reactions=reactions,
                            resets=resets,
                            start_index=self.start_index,
                            end_index=self.end_index,
                        )
                    last_confirmed_bottom = confirmed.box_bottom
                    last_confirmed_first_idx = confirmed.first_idx
                    running_peak = candle.high
                    running_peak_src = candle.index
                    mode = "B"
                    state = "SCANNING"
                    candidate = None

                    reset_second = self.post_breakout_reset(
                        analysis, last_confirmed_bottom, candle
                    )
                    if reset_second is not None:
                        resets.append(
                            ResetEvent(
                                index=candle.index,
                                display_time=candle.display_time,
                                second_time=reset_second.display_time,
                                broken_level=last_confirmed_bottom,
                                from_first_idx=last_confirmed_first_idx,
                            )
                        )
                        last_confirmed_bottom = None
                        last_confirmed_first_idx = None
                        running_peak = None
                        running_peak_src = None
                        mode = "A"
                        state = "SCANNING"
                        leg_open_low = None
                        leg_just_started = True
                        anchor_red = candle if candle.tag == "RED" else None
                        anchor_red_origin = "reset" if candle.tag == "RED" else None
                        reset_context = candle
                        continue

                    if candle.tag == "RED":
                        candidate = Candidate(
                            first_idx=candle.index,
                            first_time=candle.display_time,
                            box_top_source_idx=candle.index,
                            box_top_source_time=candle.display_time,
                            box_top=running_peak,
                            box_bottom_source_idx=candle.index,
                            box_bottom_source_time=candle.display_time,
                            box_bottom=candle.low,
                            mode="B",
                        )
                        state = "WAITING"
                continue

            if mode == "A":
                if leg_just_started:
                    leg_open_low = candle.low
                    leg_just_started = False
                    previous_reset = reset_context
                    reset_context = None
                    if candle.tag == "RED":
                        if (
                            previous_reset is not None
                            and previous_reset.tag == "GREEN"
                            and candle.low >= previous_reset.low
                        ):
                            green_high, green_source = self.green_run_peak_before(
                                candle.index
                            )
                            if green_high >= candle.high:
                                box_top = green_high
                                box_top_source = green_source
                            else:
                                box_top = candle.high
                                box_top_source = candle
                            candidate = Candidate(
                                first_idx=candle.index,
                                first_time=candle.display_time,
                                box_top_source_idx=box_top_source.index,
                                box_top_source_time=box_top_source.display_time,
                                box_top=box_top,
                                box_bottom_source_idx=candle.index,
                                box_bottom_source_time=candle.display_time,
                                box_bottom=candle.low,
                                mode="A",
                                leg_boundary_value=leg_open_low,
                            )
                            state = "WAITING"
                        else:
                            anchor_red = candle
                            anchor_red_origin = "leg_open"
                    continue

                previous = self.candles[index - 1]
                passes = False
                box_top: Decimal | None = None
                box_top_source: Candle | None = None

                if previous.tag == "GREEN" and candle.tag == "RED":
                    if (
                        anchor_red is not None
                        and anchor_red_origin == "candidate_invalidation"
                        and previous.low < anchor_red.low
                        and candle.low < anchor_red.low
                    ):
                        anchor_red = None
                        anchor_red_origin = None

                    if anchor_red is not None:
                        passes = candle.low >= anchor_red.low
                    elif candle.low >= previous.low or candle.low >= leg_open_low:
                        passes = True

                    if passes:
                        green_high, green_source = self.green_run_peak_before(candle.index)
                        if green_high >= candle.high:
                            box_top = green_high
                            box_top_source = green_source
                        else:
                            box_top = candle.high
                            box_top_source = candle

                if passes:
                    assert box_top is not None and box_top_source is not None
                    candidate = Candidate(
                        first_idx=candle.index,
                        first_time=candle.display_time,
                        box_top_source_idx=box_top_source.index,
                        box_top_source_time=box_top_source.display_time,
                        box_top=box_top,
                        box_bottom_source_idx=candle.index,
                        box_bottom_source_time=candle.display_time,
                        box_bottom=candle.low,
                        mode="A",
                        anchor_idx=anchor_red.index if anchor_red else None,
                        anchor_value=anchor_red.low if anchor_red else None,
                        leg_boundary_value=leg_open_low,
                    )
                    state = "WAITING"
                elif candle.tag == "RED":
                    anchor_red = candle
                    anchor_red_origin = "scan"
                elif candle.tag in {"DOJI", "NEUTRAL"}:
                    anchor_red = None
                    anchor_red_origin = None
            else:
                if candle.tag == "RED":
                    box_top = candle.high
                    box_top_source_idx = candle.index
                    if running_peak is not None and running_peak >= box_top:
                        box_top = running_peak
                        box_top_source_idx = running_peak_src

                    bottom_start = (
                        box_top_source_idx + 1
                        if box_top_source_idx < candle.index
                        else candle.index
                    )
                    bottom, bottom_source = self.minimum_low(bottom_start, candle.index)
                    candidate = Candidate(
                        first_idx=candle.index,
                        first_time=candle.display_time,
                        box_top_source_idx=box_top_source_idx,
                        box_top_source_time=self.candles[
                            box_top_source_idx
                        ].display_time,
                        box_top=box_top,
                        box_bottom_source_idx=bottom_source.index,
                        box_bottom_source_time=bottom_source.display_time,
                        box_bottom=bottom,
                        mode="B",
                    )
                    state = "WAITING"

                if running_peak is None or candle.high > running_peak:
                    running_peak = candle.high
                    running_peak_src = candle.index

        return DetectionResult(
            direction="bullish",
            reactions=reactions,
            resets=resets,
            start_index=self.start_index,
            end_index=self.end_index,
        )


def mirror_candle(candle: Candle) -> Candle:
    """Internal coordinate/role adapter; never reclassify a market candle here.

    Input dojis are GREEN in both market directions, matching the chart.
    Swapping that tag inside the Bullish reference makes its RED/FirstRed
    branch implement the original GREEN/FirstGreen Bearish branch. This is
    not permission to treat a market doji as RED or emit a changed chart color.
    """
    return Candle(
        index=candle.index,
        timestamp=candle.timestamp,
        display_time=candle.display_time,
        tag={"GREEN": "RED", "RED": "GREEN"}.get(candle.tag, candle.tag),
        open=candle.open.copy_negate(),
        high=candle.low.copy_negate(),
        low=candle.high.copy_negate(),
        close=candle.close.copy_negate(),
    )


def mirror_candidate(candidate: Candidate | None) -> Candidate | None:
    """Mirror geometry while preserving invariant dynamic gate state."""
    if candidate is None:
        return None
    mirrored = replace(
        candidate,
        box_top=candidate.box_bottom.copy_negate(),
        box_bottom=candidate.box_top.copy_negate(),
        box_top_source_idx=candidate.box_bottom_source_idx,
        box_top_source_time=candidate.box_bottom_source_time,
        box_bottom_source_idx=candidate.box_top_source_idx,
        box_bottom_source_time=candidate.box_top_source_time,
        anchor_value=(candidate.anchor_value.copy_negate()
                      if candidate.anchor_value is not None else None),
        leg_boundary_value=(candidate.leg_boundary_value.copy_negate()
                            if candidate.leg_boundary_value is not None else None),
    )
    return mirrored

def mirror_analysis(analysis: IntrabarAnalysis | None) -> IntrabarAnalysis | None:
    if analysis is None:
        return None
    return IntrabarAnalysis(
        mirror_candle(analysis.event_second), analysis.extreme.copy_negate(),
        mirror_candle(analysis.extreme_source),
    )


class _ReflectedCandles(Sequence[Candle]):
    """Read-only coordinate view with one-time mirror caching.

    Each source candle is mirrored at most once (on first access) and the
    result is cached, so repeated scans reuse the same object instead of
    allocating a fresh mirrored Candle on every access.
    """

    def __init__(self, source: Sequence[Candle]) -> None:
        self.source = source
        self._cache: list[Candle | None] = [None] * len(source)

    def __len__(self) -> int:
        return len(self.source)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(len(self.source)))]
        cached = self._cache[index]
        if cached is None:
            cached = mirror_candle(self.source[index])
            self._cache[index] = cached
        return cached


_REFLECTED_VIEWS: dict[int, tuple[Sequence[Candle], _ReflectedCandles]] = {}


def _reflected_view(source: Sequence[Candle]) -> _ReflectedCandles:
    key = id(source)
    cached = _REFLECTED_VIEWS.get(key)
    if cached is not None and cached[0] is source:
        return cached[1]
    view = _ReflectedCandles(source)
    _REFLECTED_VIEWS[key] = (source, view)
    return view


class BearishDetector(DetectorBase):
    """Execute the Bullish reference state machine in reflected coordinates.

    This is a coordinate adapter, not a second rule implementation. Both the
    initial Leg-Start and opposite-anchor queries use the same reference rules.
    Exact Decimal sign copying avoids context rounding during reflection.
    """

    def __init__(self, candles, one_second_candles, start_index, end_index):
        super().__init__(candles, one_second_candles, start_index, end_index)
        self.reference = BullishDetector(
            candles, one_second_candles, start_index, end_index,
        )
        # Time indexes are invariant under price reflection. Construct them
        # from the original rows; lazily transform OHLC only when consumed.
        # _ReflectedCandles caches each mirrored candle so repeated scans do
        # not re-allocate, while construction stays cheap (important because
        # _append_reaction builds a fresh BearishDetector per reaction).
        self.reference.candles = _reflected_view(candles)
        self.reference.seconds = _reflected_view(one_second_candles)
        self.reference.lower_index = ReflectedLowerTimeframeIndex(self.lower_index)

    def red_run_bottom_before(self, first_green_index):
        value, source = self.reference.green_run_peak_before(first_green_index)
        return value.copy_negate(), mirror_candle(source)

    def breakdown_analysis(self, candidate, breakdown_candle):
        return mirror_analysis(self.reference.breakout_analysis(
            mirror_candidate(candidate), mirror_candle(breakdown_candle),
        ))

    def invalidation_high_break_before_breakdown(self, candidate, candle):
        return self.reference.mode_a_invalidation_before_breakout(
            mirror_candidate(candidate), mirror_candle(candle),
        )

    def confirmed_reset_before_breakdown(self, candidate, candle, confirmed_top):
        return self.reference.confirmed_reset_before_breakout(
            mirror_candidate(candidate), mirror_candle(candle),
            confirmed_top.copy_negate(),
        )

    def post_breakdown_reset(self, analysis, box_top, breakdown_candle):
        result = self.reference.post_breakout_reset(
            mirror_analysis(analysis), box_top.copy_negate(),
            mirror_candle(breakdown_candle),
        )
        return mirror_candle(result) if result is not None else None

    def detect(self, *, first_only: bool = False) -> DetectionResult:
        result = self.reference.detect(first_only=first_only)
        return DetectionResult(
            direction="bearish",
            reactions=[mirror_candidate(candidate) for candidate in result.reactions],
            resets=[replace(reset, broken_level=reset.broken_level.copy_negate())
                    for reset in result.resets],
            start_index=result.start_index, end_index=result.end_index,
        )


def published_reaction_candidate(
    direction: str,
    candidate: Candidate,
    chronology: object,
) -> Candidate:
    """Return a presentation clone with Break-candle geometry frozen at confirmation.

    Detection/lifecycle ownership is intentionally not mutated here.  The public
    Reaction box must not include an opposite-edge extreme that happened later
    inside the same main Break candle after the Reaction had already confirmed.

    Main candles strictly before Break are fully eligible.  Only when the
    full-main-candle opposite extreme is owned by Break do we use one-second
    chronology to keep prices up to and including the first strict confirmation:

      Bullish -> published BoxBottom is the minimum eligible Low before the
                 first strict High > BoxTop breakout.
      Bearish -> published BoxTop is the maximum eligible High before the
                 first strict Low < BoxBottom breakdown.

    Equal extremes retain the earliest main-candle owner.  If lower-timeframe
    data cannot resolve the strict confirmation, preserve the detector geometry
    rather than guessing an intrabar order.
    """
    candles = chronology.candles
    one_second_candles = chronology.seconds
    published = replace(candidate)
    if candidate.break_idx is None:
        return published

    first_index = int(candidate.first_idx)
    break_index = int(candidate.break_idx)
    if first_index < 0 or break_index < first_index or break_index >= len(candles):
        return published

    break_candle = candles[break_index]
    timeframe = chronology.timeframe

    if direction == "bullish":
        # No Break-candle ownership -> the published full-range minimum was
        # already made before confirmation and is therefore chronology-safe.
        if int(candidate.box_bottom_source_idx) != break_index:
            return published
        value = candles[first_index].low
        source = candles[first_index]
        for index in range(first_index + 1, break_index):
            candle = candles[index]
            if candle.low < value:
                value, source = candle.low, candle
        threshold = candidate.box_top
    elif direction == "bearish":
        if int(candidate.box_top_source_idx) != break_index:
            return published
        value = candles[first_index].high
        source = candles[first_index]
        for index in range(first_index + 1, break_index):
            candle = candles[index]
            if candle.high > value:
                value, source = candle.high, candle
        threshold = candidate.box_bottom
    else:
        raise ValueError(f"Unsupported reaction direction: {direction}")

    lo, hi = chronology.lower_bounds(
        break_candle.timestamp, break_candle.timestamp + timeframe
    )
    confirmed = False

    for second in one_second_candles[lo:hi]:
        if direction == "bullish":
            if second.low < value:
                value = second.low
                source = break_candle
            if second.high > threshold:
                confirmed = True
                break
        else:
            if second.high > value:
                value = second.high
                source = break_candle
            if second.low < threshold:
                confirmed = True
                break

    if not confirmed:
        return published

    if direction == "bullish":
        published.box_bottom = value
        published.box_bottom_source_idx = source.index
        published.box_bottom_source_time = source.display_time
    else:
        published.box_top = value
        published.box_top_source_idx = source.index
        published.box_top_source_time = source.display_time
    return published


def _decimal_value(value: object) -> Decimal:
    """Normalize external numeric values without binary-float arithmetic."""
    return value if isinstance(value, Decimal) else Decimal(str(value))


class LowerTimeframeIndex:
    """Immutable segment index for exact first strict High/Low crossings.

    The index is direction-agnostic and shared by A/S/E so heavy 1-second
    inputs are not rescanned for every stop/trigger lookup.
    """

    def __init__(self, candles: Sequence[Candle]) -> None:
        self.candles = candles
        self.times = [getattr(item, "timestamp") for item in candles]
        size = 1
        while size < len(candles):
            size <<= 1
        self.size = size
        self.length = len(candles)
        self.minimum: list[Decimal | None] = [None] * (2 * size)
        self.maximum: list[Decimal | None] = [None] * (2 * size)
        self.minimum_position = array("i", [-1]) * (2 * size)
        self.maximum_position = array("i", [-1]) * (2 * size)
        for position, candle in enumerate(candles):
            node = size + position
            self.minimum[node] = _decimal_value(getattr(candle, "low"))
            self.maximum[node] = _decimal_value(getattr(candle, "high"))
            self.minimum_position[node] = position
            self.maximum_position[node] = position
        for node in range(size - 1, 0, -1):
            left, right = node * 2, node * 2 + 1
            low_left, low_right = self.minimum[left], self.minimum[right]
            high_left, high_right = self.maximum[left], self.maximum[right]
            if low_left is None:
                self.minimum[node] = low_right
                self.minimum_position[node] = self.minimum_position[right]
            elif low_right is None or low_left <= low_right:
                self.minimum[node] = low_left
                self.minimum_position[node] = self.minimum_position[left]
            else:
                self.minimum[node] = low_right
                self.minimum_position[node] = self.minimum_position[right]
            if high_left is None:
                self.maximum[node] = high_right
                self.maximum_position[node] = self.maximum_position[right]
            elif high_right is None or high_left >= high_right:
                self.maximum[node] = high_left
                self.maximum_position[node] = self.maximum_position[left]
            else:
                self.maximum[node] = high_right
                self.maximum_position[node] = self.maximum_position[right]

    def first_less(self, left: int, right: int, level: Decimal) -> int | None:
        return self._first(1, 0, self.size, left, right, level, True)

    def first_greater(self, left: int, right: int, level: Decimal) -> int | None:
        return self._first(1, 0, self.size, left, right, level, False)

    def range_minimum(self, left: int, right: int) -> tuple[Decimal, int]:
        """Return the minimum Low and earliest owning position in [left, right)."""
        return self._range_query(left, right, minimum=True)

    def range_maximum(self, left: int, right: int) -> tuple[Decimal, int]:
        """Return the maximum High and earliest owning position in [left, right)."""
        return self._range_query(left, right, minimum=False)

    def _range_query(
        self, left: int, right: int, *, minimum: bool
    ) -> tuple[Decimal, int]:
        if left < 0 or right > self.length or left >= right:
            raise ValueError("Range contains no lower-timeframe candles.")
        values = self.minimum if minimum else self.maximum
        positions = self.minimum_position if minimum else self.maximum_position
        left += self.size
        right += self.size
        best_value: Decimal | None = None
        best_position = -1
        while left < right:
            if left & 1:
                value = values[left]
                position = positions[left]
                if value is not None and (
                    best_value is None
                    or (value < best_value if minimum else value > best_value)
                    or (value == best_value and position < best_position)
                ):
                    best_value, best_position = value, position
                left += 1
            if right & 1:
                right -= 1
                value = values[right]
                position = positions[right]
                if value is not None and (
                    best_value is None
                    or (value < best_value if minimum else value > best_value)
                    or (value == best_value and position < best_position)
                ):
                    best_value, best_position = value, position
            left >>= 1
            right >>= 1
        if best_value is None or best_position < 0:
            raise ValueError("Range contains no lower-timeframe candles.")
        return best_value, best_position

    def _first(
        self, node: int, start: int, end: int, left: int, right: int,
        level: Decimal, less: bool,
    ) -> int | None:
        if end <= left or right <= start or start >= self.length:
            return None
        extreme = self.minimum[node] if less else self.maximum[node]
        if extreme is None or (extreme >= level if less else extreme <= level):
            return None
        if end - start == 1:
            return start
        middle = (start + end) // 2
        found = self._first(node * 2, start, middle, left, right, level, less)
        if found is not None:
            return found
        return self._first(
            node * 2 + 1, middle, end, left, right, level, less
        )


_LOWER_TIMEFRAME_INDEXES: dict[
    int, tuple[Sequence[Candle], LowerTimeframeIndex]
] = {}


def shared_lower_timeframe_index(
    candles: Sequence[Candle],
) -> LowerTimeframeIndex:
    """Reuse one immutable lower-timeframe index per source sequence."""
    key = id(candles)
    cached = _LOWER_TIMEFRAME_INDEXES.get(key)
    if cached is not None and cached[0] is candles:
        return cached[1]
    index = LowerTimeframeIndex(candles)
    _LOWER_TIMEFRAME_INDEXES[key] = (candles, index)
    return index


class ReflectedLowerTimeframeIndex:
    """Price-reflected view over a lower-timeframe index without rebuilding it."""

    __slots__ = ("base", "times")

    def __init__(self, base: LowerTimeframeIndex) -> None:
        self.base = base
        self.times = base.times

    def first_less(self, left: int, right: int, level: Decimal) -> int | None:
        return self.base.first_greater(left, right, level.copy_negate())

    def first_greater(self, left: int, right: int, level: Decimal) -> int | None:
        return self.base.first_less(left, right, level.copy_negate())

    def range_minimum(self, left: int, right: int) -> tuple[Decimal, int]:
        value, position = self.base.range_maximum(left, right)
        return value.copy_negate(), position

    def range_maximum(self, left: int, right: int) -> tuple[Decimal, int]:
        value, position = self.base.range_minimum(left, right)
        return value.copy_negate(), position


class MarketChronology:
    """Shared immutable market-time services for downstream behavior engines.

    Reaction owns chronology semantics.  A/S/E receive this object rather than
    rebuilding timestamp indexes, lower-timeframe windows, confirmation scans,
    and Reset timestamp parsing independently.
    """

    __slots__ = (
        "candles",
        "seconds",
        "times",
        "second_times",
        "timeframe",
        "lower_index",
        "_confirmation_cache",
        "_reset_time_cache",
    )

    def __init__(
        self,
        candles: Sequence[Candle],
        seconds: Sequence[Candle],
        timeframe_seconds: int,
        lower_index: LowerTimeframeIndex | None = None,
    ) -> None:
        if timeframe_seconds < 1:
            raise ValueError("Timeframe must be at least one second.")
        self.candles = candles
        self.seconds = seconds
        self.times = [getattr(item, "timestamp") for item in candles]
        self.second_times = (
            lower_index.times
            if lower_index is not None
            else [getattr(item, "timestamp") for item in seconds]
        )
        self.timeframe = timedelta(seconds=timeframe_seconds)
        self.lower_index = lower_index or shared_lower_timeframe_index(seconds)
        self._confirmation_cache: dict[tuple[object, ...], datetime] = {}
        self._reset_time_cache: dict[tuple[object, ...], datetime] = {}

    @staticmethod
    def opposite_direction(direction: str) -> str:
        """Expose the shared mirror-direction contract to downstream engines."""
        return opposite_direction(direction)

    def main_index(self, timestamp: datetime, *, clamp: bool = False) -> int:
        """Map an exact lower-timeframe timestamp to its owning main candle."""
        index = bisect.bisect_right(self.times, timestamp) - 1
        if index < 0:
            if clamp:
                return 0
            raise ValueError("Lower-timeframe event precedes the main candles.")
        return index

    def lower_bounds(
        self, start: datetime, end: datetime | None = None
    ) -> tuple[int, int]:
        left = bisect.bisect_left(self.second_times, start)
        right = (
            len(self.seconds)
            if end is None
            else bisect.bisect_left(self.second_times, end)
        )
        return left, right

    def lower_window(
        self, start: datetime, end: datetime | None = None
    ) -> Sequence[Candle]:
        left, right = self.lower_bounds(start, end)
        return self.seconds[left:right]

    @staticmethod
    def _reset_cache_key(reset: object) -> tuple[object, ...]:
        """Return a stable Reset identity suitable for chronology caches."""
        return (
            int(getattr(reset, "index", -1)),
            int(getattr(reset, "from_first_idx", -1)),
            getattr(reset, "second_time", None),
            getattr(reset, "display_time", None),
            getattr(reset, "timestamp", None),
            str(getattr(reset, "broken_level", "")),
        )

    @staticmethod
    def _reaction_cache_key(
        reaction: object, direction: str, use_intrabar_start: bool
    ) -> tuple[object, ...]:
        """Return a stable physical/geometry identity for confirmation caches."""
        return (
            direction,
            bool(use_intrabar_start),
            int(getattr(reaction, "first_idx")),
            int(getattr(reaction, "break_idx")),
            str(getattr(reaction, "box_top")),
            str(getattr(reaction, "box_bottom")),
            getattr(reaction, "intrabar_start", None) if use_intrabar_start else None,
        )

    def reset_time(self, reset: object) -> datetime:
        """Return the exact Reset event time, preserving legacy provenance."""
        cache_key = self._reset_cache_key(reset)
        cached = self._reset_time_cache.get(cache_key)
        if cached is not None:
            return cached
        second = getattr(reset, "second_time", None)
        if second:
            result = datetime.strptime(second, "%Y-%m-%d %H:%M:%S")
        else:
            display = getattr(reset, "display_time", None)
            result = (
                datetime.strptime(display, "%Y-%m-%d %H:%M:%S")
                if display
                else getattr(reset, "timestamp")
            )
        self._reset_time_cache[cache_key] = result
        return result

    def reaction_confirmation(
        self,
        direction: str,
        reaction: object,
        *,
        use_intrabar_start: bool = True,
    ) -> datetime:
        """Return the first strict lower-timeframe Reaction confirmation.

        ``use_intrabar_start=False`` preserves the established A-engine
        chronology contract, which starts its scan at the Break candle open.
        S/E and public Reaction chronology use the exact intrabar start when
        present.
        """
        cache_key = self._reaction_cache_key(
            reaction, direction, use_intrabar_start
        )
        cached = self._confirmation_cache.get(cache_key)
        if cached is not None:
            return cached
        break_index = int(getattr(reaction, "break_idx"))
        break_candle = self.candles[break_index]
        candle_start = getattr(break_candle, "timestamp")
        start = (
            getattr(reaction, "intrabar_start", None) or candle_start
            if use_intrabar_start
            else candle_start
        )
        candle_end = candle_start + self.timeframe
        if start < candle_start or start >= candle_end:
            start = candle_start
        level = _decimal_value(
            getattr(reaction, "box_top" if direction == "bullish" else "box_bottom")
        )
        left, right = self.lower_bounds(start, candle_end)
        field = "high" if direction == "bullish" else "low"
        for position in range(left, right):
            item = self.seconds[position]
            value = _decimal_value(getattr(item, field))
            confirms = value > level if direction == "bullish" else value < level
            if confirms:
                result = getattr(item, "timestamp")
                self._confirmation_cache[cache_key] = result
                return result
        self._confirmation_cache[cache_key] = candle_start
        return candle_start


    def canonical_order_stop(
        self,
        order_direction: str,
        reaction_number: int,
        reaction: object,
        opposite_reactions: Sequence[object],
        *,
        start_index: int = 0,
    ) -> tuple[Decimal, int, datetime]:
        """Return canonical opposite-Order stop provenance for S and E.

        Mode A owns the true leg head/floor from its anchor/context through
        Break inclusive. Mode B inherits the previous healthy opposite
        Reaction's semantic outer box edge. This is the single authoritative
        implementation used by every downstream behavior family.
        """
        if str(getattr(reaction, "mode")) == "A":
            first_index = int(getattr(reaction, "first_idx"))
            break_index = int(getattr(reaction, "break_idx"))
            anchor_index = getattr(reaction, "anchor_idx", None)
            scan_start = (
                max(start_index, int(anchor_index))
                if anchor_index is not None
                else max(start_index, first_index - 1)
            )
            context_tag = "GREEN" if order_direction == "bearish" else "RED"
            while (
                scan_start > start_index
                and getattr(self.candles[scan_start - 1], "tag") == context_tag
            ):
                scan_start -= 1

            attribute = "high" if order_direction == "bearish" else "low"
            source_index = scan_start
            level = _decimal_value(getattr(self.candles[source_index], attribute))
            for candle in self.candles[scan_start + 1 : break_index + 1]:
                candidate = _decimal_value(getattr(candle, attribute))
                better = (
                    candidate > level
                    if order_direction == "bearish"
                    else candidate < level
                )
                if better:
                    source_index = int(getattr(candle, "index"))
                    level = candidate
            return level, source_index, getattr(self.candles[source_index], "timestamp")

        if reaction_number <= 1:
            raise ValueError("Mode-B order reaction has no previous healthy reaction.")
        previous = opposite_reactions[reaction_number - 2]
        if order_direction == "bearish":
            source_index = int(getattr(previous, "box_top_source_idx"))
            return (
                _decimal_value(getattr(previous, "box_top")),
                source_index,
                getattr(self.candles[source_index], "timestamp"),
            )
        source_index = int(getattr(previous, "box_bottom_source_idx"))
        return (
            _decimal_value(getattr(previous, "box_bottom")),
            source_index,
            getattr(self.candles[source_index], "timestamp"),
        )


def build_behavior_reaction_views(
    full_results: dict[str, object],
    chronology: MarketChronology,
):
    """Mark true cross-direction Reaction interiors for downstream behavior."""
    candles = chronology.candles
    seconds = chronology.seconds
    second_times = chronology.second_times
    public: dict[str, list[Candidate]] = {}
    confirmation: dict[str, list[datetime]] = {}
    for direction in ("bullish", "bearish"):
        public[direction] = [
            published_reaction_candidate(direction, item, chronology)
            for item in full_results[direction].reactions
        ]
        confirmation[direction] = [
            chronology.reaction_confirmation(direction, item)
            for item in full_results[direction].reactions
        ]

    def path_is_contained(
        first_time: datetime,
        confirmed_at: datetime,
        bottom: Decimal,
        top: Decimal,
    ) -> bool:
        left = bisect.bisect_left(second_times, first_time)
        right = bisect.bisect_right(second_times, confirmed_at)
        if left >= right:
            return False
        # Algorithm requirement: every physical lower-timeframe candle must
        # remain inside [bottom, top].  The immutable lower-timeframe range
        # index proves the exact same predicate via min(Low) and max(High),
        # without allocating/scanning the full slice for every Reaction pair.
        minimum_low, _ = chronology.lower_index.range_minimum(left, right)
        if minimum_low < bottom:
            return False
        maximum_high, _ = chronology.lower_index.range_maximum(left, right)
        return maximum_high <= top

    blocked: dict[str, set[tuple[int, int]]] = {
        "bullish": set(),
        "bearish": set(),
    }
    for direction in ("bullish", "bearish"):
        opposite = opposite_direction(direction)
        for number, reaction in enumerate(full_results[direction].reactions, start=1):
            reaction.behavior_public_number = number
            published = public[direction][number - 1]
            reaction.behavior_public_box_top = _decimal_value(published.box_top)
            reaction.behavior_public_box_bottom = _decimal_value(published.box_bottom)
            reaction.behavior_confirmation_time = confirmation[direction][number - 1]
            reaction.behavior_first_time = candles[int(getattr(reaction, "first_idx"))].timestamp

        for reaction, published, confirmed_at in zip(
            full_results[direction].reactions,
            public[direction],
            confirmation[direction],
        ):
            inner_first = candles[int(getattr(reaction, "first_idx"))].timestamp
            inner_top = _decimal_value(published.box_top)
            inner_bottom = _decimal_value(published.box_bottom)
            for outer, outer_published, outer_confirmed_at in zip(
                full_results[opposite].reactions,
                public[opposite],
                confirmation[opposite],
            ):
                outer_first = candles[int(getattr(outer, "first_idx"))].timestamp
                if inner_first <= outer_first or confirmed_at > outer_confirmed_at:
                    continue
                outer_top = _decimal_value(outer_published.box_top)
                outer_bottom = _decimal_value(outer_published.box_bottom)
                if (
                    inner_top <= outer_top
                    and inner_bottom >= outer_bottom
                    and path_is_contained(
                        inner_first,
                        confirmed_at,
                        outer_bottom,
                        outer_top,
                    )
                ):
                    blocked[direction].add(
                        (
                            int(getattr(reaction, "first_idx")),
                            int(getattr(reaction, "break_idx")),
                        )
                    )
                    break

    behavior_results = {}
    number_maps = {}
    blocked_first_times = {"bullish": set(), "bearish": set()}
    for direction in ("bullish", "bearish"):
        full = full_results[direction]
        for item in full.reactions:
            identity = (
                int(getattr(item, "first_idx")),
                int(getattr(item, "break_idx")),
            )
            item.behavior_internal = identity in blocked[direction]
        behavior_results[direction] = full
        number_maps[direction] = {
            number: number for number, _item in enumerate(full.reactions, start=1)
        }
        blocked_first_times[direction] = {
            candles[first_idx].timestamp for first_idx, _ in blocked[direction]
        }
    return behavior_results, number_maps, blocked, blocked_first_times


def directional_a_stop_order_finder(
    candles: Sequence[Candle],
    seconds: Sequence[Candle],
    direction: str,
):
    """Build the cached bounded opposite-Reaction resolver used after A stop."""
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    order_direction = opposite_direction(direction)
    first_tag = "GREEN" if order_direction == "bearish" else "RED"
    context_tag = "RED" if order_direction == "bearish" else "GREEN"
    cache: dict[tuple[int, int], Candidate | None] = {}
    detection_cache: dict[tuple[int, int], tuple[Candidate, ...]] = {}

    def find(gate_index: int, gate_event: datetime, end_index: int):
        key = (gate_index, end_index)
        if key in cache:
            return cache[key]
        first = next(
            (
                index
                for index in range(max(1, gate_index), end_index + 1)
                if candles[index].tag == first_tag
                and candles[index - 1].tag == context_tag
            ),
            None,
        )
        if first is None:
            cache[key] = None
            return None
        context = first - 1
        while context > 0 and candles[context - 1].tag == context_tag:
            context -= 1
        detection_key = (context, end_index)
        reactions = detection_cache.get(detection_key, ())
        order = next(
            (
                reaction
                for reaction in reactions
                if int(getattr(reaction, "first_idx")) >= gate_index
            ),
            None,
        )
        if order is None:
            result = UnifiedReactionDetector(
                candles, seconds, context, end_index, order_direction
            ).detect(stop_after_first_at_or_after=gate_index)
            reactions = tuple(result.reactions)
            detection_cache[detection_key] = reactions
            order = next(
                (
                    reaction
                    for reaction in reactions
                    if int(getattr(reaction, "first_idx")) >= gate_index
                ),
                None,
            )
        cache[key] = order
        return order

    return find


class UnifiedReactionDetector(DetectorBase):
    """Unified v9 directional post-Reset engine.

    The proven directional detectors supply only the initial Leg-Start. After
    that first confirmation this class owns Normal search and directional
    post-Reset continuation.  A Reset always searches for the first healthy
    reaction in the same direction as the requested/output leg; patterns in
    the opposite direction never gate or unlock that search.
    """

    def __init__(
        self,
        candles: Sequence[Candle],
        one_second_candles: Sequence[Candle],
        start_index: int,
        end_index: int,
        output_direction: str,
    ) -> None:
        super().__init__(candles, one_second_candles, start_index, end_index)
        self.output_direction = output_direction
        # Directional helpers are created lazily: a bullish-only run must not
        # pay the BearishDetector mirroring cost and vice versa.
        self._bull: BullishDetector | None = None
        self._bear: BearishDetector | None = None
        self.all_reactions: dict[str, list[Candidate]] = {
            "bullish": [],
            "bearish": [],
        }
        self.all_resets: dict[str, list[ResetEvent]] = {
            "bullish": [],
            "bearish": [],
        }
        self._geometry_after_reset_cache: dict[tuple, Candidate | None] = {}

    @property
    def bull(self) -> BullishDetector:
        if self._bull is None:
            self._bull = BullishDetector(
                self.candles, self.seconds, self.start_index, self.end_index
            )
        return self._bull

    @property
    def bear(self) -> BearishDetector:
        if self._bear is None:
            self._bear = BearishDetector(
                self.candles, self.seconds, self.start_index, self.end_index
            )
        return self._bear

    def _append_reaction(self, direction: str, candidate: Candidate) -> bool:
        # A confirmed adjacent opposite-direction Anchor may extend the outer
        # boundary, but it must never shrink the candidate's own box.
        opposite_anchor_is_confirmed = False
        if (
            candidate.break_idx is not None
            and candidate.anchor_idx is not None
            and candidate.anchor_idx + 1 == candidate.first_idx
            and self.all_resets[direction]
        ):
            reset_index = self.all_resets[direction][-1].index
            opposite_detector = (
                BullishDetector if direction == "bearish" else BearishDetector
            )(
                self.candles,
                self.seconds,
                reset_index,
                candidate.first_idx,
            )
            opposite_anchor_is_confirmed = any(
                reaction.break_idx == candidate.anchor_idx
                for reaction in opposite_detector.detect().reactions
            )

        if opposite_anchor_is_confirmed:
            anchor = self.candles[candidate.anchor_idx]
            first = self.candles[candidate.first_idx]
            if direction == "bearish":
                # A RED Leg-Start with a higher ceiling than FirstGreen owns
                # the leg boundary; FirstGreen must keep its own BoxBottom.
                if anchor.high <= first.high:
                    candidate.box_bottom = anchor.low
                    candidate.box_bottom_source_idx = anchor.index
                    candidate.box_bottom_source_time = anchor.display_time
            else:
                # Exact mirror: a GREEN Leg-Start whose floor is below
                # FirstRed owns the leg boundary; FirstRed keeps its BoxTop.
                if anchor.low >= first.low:
                    candidate.box_top = anchor.high
                    candidate.box_top_source_idx = anchor.index
                    candidate.box_top_source_time = anchor.display_time

        # Canonical confirmed-Reaction box ownership.  The directional
        # confirmation edge keeps the structure that discovered the Reaction:
        #   Bullish  -> BoxTop is the breakout edge.
        #   Bearish  -> BoxBottom is the breakdown edge.
        # The opposite edge belongs to First..exact-confirmation chronology.
        # Full main candles strictly before Break are eligible in full.  When
        # the Break candle itself owns the full-range opposite extreme, only
        # lower-timeframe prices up to and including the first strict
        # confirmation event may contribute.  Post-confirmation remainder
        # prices can never retroactively rewrite the Reaction/Order box.
        if candidate.break_idx is not None:
            first_index = int(candidate.first_idx)
            break_index = int(candidate.break_idx)
            break_candle = self.candles[break_index]
            if direction == "bullish":
                bottom, bottom_source = self.minimum_low(first_index, break_index)
                candidate.box_bottom = bottom
                candidate.box_bottom_source_idx = bottom_source.index
                candidate.box_bottom_source_time = bottom_source.display_time
                if bottom_source.index == break_index:
                    analysis = self.bull.breakout_analysis(candidate, break_candle)
                    if analysis is not None:
                        candidate.box_bottom = analysis.extreme
                        candidate.box_bottom_source_idx = analysis.extreme_source.index
                        candidate.box_bottom_source_time = analysis.extreme_source.display_time
            else:
                top, top_source = self.maximum_high(first_index, break_index)
                candidate.box_top = top
                candidate.box_top_source_idx = top_source.index
                candidate.box_top_source_time = top_source.display_time
                if top_source.index == break_index:
                    analysis = self.bear.breakdown_analysis(candidate, break_candle)
                    if analysis is not None:
                        candidate.box_top = analysis.extreme
                        candidate.box_top_source_idx = analysis.extreme_source.index
                        candidate.box_top_source_time = analysis.extreme_source.display_time

        self.all_reactions[direction].append(replace(candidate))
        return True

    def _append_reset(
        self,
        direction: str,
        candle: Candle,
        level: Decimal,
        first_idx: int,
        second_time: str | None = None,
    ) -> None:
        self.all_resets[direction].append(
            ResetEvent(
                index=candle.index,
                display_time=candle.display_time,
                second_time=second_time,
                broken_level=level,
                from_first_idx=first_idx,
            )
        )

    def _refine(
        self, direction: str, candidate: Candidate, candle: Candle
    ) -> IntrabarAnalysis | None:
        helper = self.bull if direction == "bullish" else self.bear
        analysis = (
            helper.breakout_analysis(candidate, candle)
            if direction == "bullish"
            else helper.breakdown_analysis(candidate, candle)
        )
        if analysis is None:
            return None
        if direction == "bullish" and candidate.box_bottom_source_idx == candle.index:
            candidate.box_bottom = analysis.extreme
            candidate.box_bottom_source_idx = analysis.extreme_source.index
            candidate.box_bottom_source_time = analysis.extreme_source.display_time
        if direction == "bearish" and candidate.box_top_source_idx == candle.index:
            candidate.box_top = analysis.extreme
            candidate.box_top_source_idx = analysis.extreme_source.index
            candidate.box_top_source_time = analysis.extreme_source.display_time
        return analysis

    def _candidate_from_confirmation_remainder(
        self,
        direction: str,
        confirmed: Candidate,
        candle: Candle,
        analysis: IntrabarAnalysis | None,
    ) -> Candidate | None:
        """Reuse a correctly colored confirmation candle for the next reaction."""
        required_tag = "RED" if direction == "bullish" else "GREEN"
        if candle.tag != required_tag or analysis is None:
            return None

        # The exact confirmation event splits the Break candle into two
        # ownership phases.  If its remainder strictly breaks the confirmed
        # opposite edge, that main candle belongs to Reset and cannot also be
        # reused as the First of the next Normal reaction.  ``analysis.extreme``
        # is the exact-confirmation opposite edge for both directions.
        remainder_start = analysis.event_second.timestamp + timedelta(microseconds=1)
        remainder_end = candle.timestamp + self.timeframe
        left = bisect.bisect_left(self.second_times, remainder_start)
        right = bisect.bisect_left(self.second_times, remainder_end)
        if direction == "bullish":
            if self.lower_index.first_less(left, right, analysis.extreme) is not None:
                return None
        else:
            if self.lower_index.first_greater(left, right, analysis.extreme) is not None:
                return None
        # A cross-direction Leg-Start confirmation candle may simultaneously
        # become the first candle of the next same-direction reaction. Its
        # decisive second belongs to the new box boundary, so no second,
        # still-more-extreme tick is required. Other confirmations retain the
        # ordinary fresh post-event boundary requirement.
        # Every confirmation opens Normal Search. If its main candle has the
        # required start color, that complete candle is the next First candle,
        # regardless of whether the confirmed reaction was Mode A or Mode B.
        whole_confirmation_candle = True
        remainder_start = (
            candle.timestamp
            if whole_confirmation_candle
            else analysis.event_second.timestamp + timedelta(microseconds=1)
        )
        remainder_end = candle.timestamp + self.timeframe
        seconds = list(self.seconds_between(remainder_start, remainder_end))
        if not seconds:
            return None
        if direction == "bullish":
            top_second = max(seconds, key=lambda item: (item.high, -item.timestamp.timestamp()))
            bottom_second = min(seconds, key=lambda item: (item.low, item.timestamp))
            if (
                not whole_confirmation_candle
                and top_second.high <= analysis.event_second.high
            ):
                return None
            return Candidate(
                first_idx=candle.index,
                first_time=candle.display_time,
                box_top_source_idx=candle.index,
                box_top_source_time=candle.display_time,
                box_top=top_second.high,
                box_bottom_source_idx=candle.index,
                box_bottom_source_time=candle.display_time,
                box_bottom=bottom_second.low,
                mode="B",
                intrabar_start=remainder_start,
            )
        bottom_second = min(seconds, key=lambda item: (item.low, item.timestamp))
        top_second = max(seconds, key=lambda item: (item.high, -item.timestamp.timestamp()))
        if (
            not whole_confirmation_candle
            and bottom_second.low >= analysis.event_second.low
        ):
            return None
        return Candidate(
            first_idx=candle.index,
            first_time=candle.display_time,
            box_top_source_idx=candle.index,
            box_top_source_time=candle.display_time,
            box_top=top_second.high,
            box_bottom_source_idx=candle.index,
            box_bottom_source_time=candle.display_time,
            box_bottom=bottom_second.low,
            mode="B",
            intrabar_start=remainder_start,
        )

    def _first_initial(self, direction: str) -> Candidate | None:
        initial_result = (
            self.bull.detect(first_only=True)
            if direction == "bullish"
            else self.bear.detect(first_only=True)
        )
        return (
            replace(initial_result.reactions[0])
            if initial_result.reactions
            else None
        )


    def _first_direct_same_direction_after_reset(
        self, direction: str, reset_index: int
    ) -> Candidate | None:
        """Return the first structurally owned reaction after Reset.

        The earliest eligible candidate owns the evolving leg until it either
        confirms or its outer leg boundary is strictly crossed. A nested local
        pattern cannot confirm while that owner is unresolved. If the boundary
        breaks first, restart strictly after that event. Bearish is the exact
        price/color mirror of Bullish.
        """
        context_tag = "GREEN" if direction == "bullish" else "RED"
        first_tag = "RED" if direction == "bullish" else "GREEN"
        blocked_through = reset_index

        for first_index in range(reset_index + 1, self.end_index + 1):
            first = self.candles[first_index]
            if first_index <= blocked_through:
                continue
            if first.tag != first_tag or self.candles[first_index - 1].tag != context_tag:
                continue

            candidate = self._build_direct_candidate(
                direction, reset_index, first_index
            )
            if candidate is None:
                continue
            confirmed, invalidation_index = self._scan_direct_candidate(
                direction, candidate, self.end_index
            )
            if confirmed is not None:
                return confirmed
            if invalidation_index is None:
                continue
            blocked_through = invalidation_index

        return None

    def _first_geometry_after_reset(
        self, direction: str, reset_index: int, end_index: int | None = None,
    ) -> Candidate | None:
        """Return the first complete raw Reaction geometry after a boundary.

        This bounded search intentionally ignores normal Reset/invalidation
        acceptance.  It is a geometry-only primitive: First/box/Break structure
        may be used as evidence even when normal Reaction lifecycle rules would
        later Reset or suppress that structure.
        """
        _lim = self.end_index if end_index is None else min(end_index, self.end_index)
        _ck = (direction, reset_index, _lim)
        if _ck in self._geometry_after_reset_cache:
            _cached = self._geometry_after_reset_cache[_ck]
            return replace(_cached) if _cached is not None else None
        first_tag = "RED" if direction == "bullish" else "GREEN"
        context_tag = "GREEN" if direction == "bullish" else "RED"
        limit = self.end_index if end_index is None else min(end_index, self.end_index)
        for first_index in range(reset_index + 1, limit + 1):
            if (
                self.candles[first_index].tag != first_tag
                or self.candles[first_index - 1].tag != context_tag
            ):
                continue
            candidate = self._build_direct_candidate(
                direction, reset_index, first_index
            )
            if candidate is None:
                continue
            for scan in range(first_index + 1, limit + 1):
                candle = self.candles[scan]
                if direction == "bullish":
                    if candle.low < candidate.box_bottom:
                        candidate.box_bottom = candle.low
                        candidate.box_bottom_source_idx = candle.index
                        candidate.box_bottom_source_time = candle.display_time
                    if candle.high > candidate.box_top:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        return candidate
                else:
                    if candle.high > candidate.box_top:
                        candidate.box_top = candle.high
                        candidate.box_top_source_idx = candle.index
                        candidate.box_top_source_time = candle.display_time
                    if candle.low < candidate.box_bottom:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        return candidate
        return None

    def first_geometry_after_reset(
        self, direction: str, reset_index: int, end_index: int
    ) -> Candidate | None:
        """Public lifecycle API for post-Reset geometry discovery."""
        return self._first_geometry_after_reset(direction, reset_index, end_index)


    def _reaction_break_indices(self, direction: str) -> list[int]:
        """Cached ascending `break_idx` values mirroring `all_reactions[direction]`.

        `all_reactions[direction]` is append-only and strictly non-decreasing
        in `break_idx`, so this index list can be reused via bisect instead of
        rescanning the full reaction history on every gate lookup.
        """
        reactions = self.all_reactions[direction]
        cached = self._reaction_break_index_cache.get(direction)
        if cached is not None and cached[0] == len(reactions):
            return cached[1]
        indices = [int(reaction.break_idx) for reaction in reactions]
        self._reaction_break_index_cache[direction] = (len(reactions), indices)
        return indices

    def first_order_reaction_after_gate(
        self,
        direction: str,
        gate_index: int,
        end_index: int | None = None,
        gate_event_time: datetime | None = None,
    ) -> Candidate | None:
        """Return direct Order_A geometry from continuous Reaction context."""
        limit = self.end_index if end_index is None else min(end_index, self.end_index)
        if gate_index < self.start_index or gate_index >= limit:
            return None

        def confirmed_no_later_than_gate(reaction: Candidate) -> bool:
            break_index = int(reaction.break_idx)
            if break_index < gate_index or gate_event_time is None:
                return break_index <= gate_index
            if break_index > gate_index:
                return False
            break_candle = self.candles[break_index]
            start = reaction.intrabar_start or break_candle.timestamp
            end = break_candle.timestamp + self.timeframe
            level = reaction.box_bottom if direction == "bearish" else reaction.box_top
            for lower in self.seconds_between(start, end):
                crossed = (
                    lower.low < level
                    if direction == "bearish"
                    else lower.high > level
                )
                if crossed:
                    return lower.timestamp <= gate_event_time
            return break_candle.timestamp <= gate_event_time

        reactions = self.all_reactions[direction]
        break_indices = self._reaction_break_indices(direction)
        # `break_indices` is non-decreasing and duplicate-free for this
        # engine's reaction stream. Keep only the owning position instead of
        # allocating the complete historical prefix on every gate lookup.
        cut = bisect.bisect_left(break_indices, gate_index)
        owner_position = cut - 1
        if cut < len(reactions) and break_indices[cut] == gate_index:
            if confirmed_no_later_than_gate(reactions[cut]):
                owner_position = cut
        search_start = gate_index + 1
        if owner_position < 0:
            result = self._earliest_confirmed_geometry(
                direction, search_start, limit
            )
            if result is not None:
                result.order_gate_decision = "no-history"
            return result

        owner = reactions[owner_position]
        boundary_end = max(int(owner.first_idx), gate_index - 1)
        gate = self.candles[gate_index]
        if direction == "bearish":
            outer_boundary, _ = self.maximum_high(
                int(owner.first_idx), boundary_end
            )
            gate_boundary = gate.low
        else:
            outer_boundary, _ = self.minimum_low(
                int(owner.first_idx), boundary_end
            )
            gate_boundary = gate.high

        event_start = gate_event_time or gate.timestamp
        event_end = self.candles[limit].timestamp + self.timeframe
        left = bisect.bisect_left(self.second_times, event_start)
        right = bisect.bisect_left(self.second_times, event_end)
        if left >= right:
            return None
        if direction == "bearish":
            outer_position = self.lower_index.first_greater(
                left, right, outer_boundary
            )
            gate_position = self.lower_index.first_less(
                left, right, gate_boundary
            )
        else:
            outer_position = self.lower_index.first_less(
                left, right, outer_boundary
            )
            gate_position = self.lower_index.first_greater(
                left, right, gate_boundary
            )
        if outer_position is None and gate_position is None:
            return None
        # Legacy loop checks the outer/restart predicate first inside each
        # lower-timeframe candle, so restart owns an exact-position tie.
        restart = outer_position is not None and (
            gate_position is None or outer_position <= gate_position
        )
        decision_position = outer_position if restart else gate_position
        assert decision_position is not None
        decision_time = self.second_times[decision_position]
        decision_kind = "restart" if restart else "continue"
        if decision_kind == "restart":
            source = self.main_source_for_time(decision_time)
            if source is None:
                return None
            search_start = int(source.index) + 1
        if search_start > limit:
            return None
        result = self._earliest_confirmed_geometry(
            direction, search_start, limit
        )
        if result is not None:
            result.order_gate_decision = decision_kind
            if decision_kind == "continue" and (
                result.anchor_idx is None or result.anchor_value is None
            ):
                # The gate-bounded geometry already carries the true current
                # forming-leg anchor when one was discovered.  Never overwrite
                # that provenance with an older Reset.  Reconstruction is only
                # a fallback for geometry that genuinely has no anchor.
                prior_resets = [
                    item for item in self.all_resets[direction]
                    if item.index < int(result.first_idx)
                ]
                if prior_resets:
                    reset_index = max(item.index for item in prior_resets)
                    if direction == "bullish":
                        boundary, source = self.minimum_low(
                            reset_index, int(result.first_idx) - 1
                        )
                    else:
                        boundary, source = self.maximum_high(
                            reset_index, int(result.first_idx) - 1
                        )
                    result.anchor_idx = source.index
                    result.anchor_value = boundary
                    result.leg_boundary_value = boundary
        return result

    def _earliest_confirmed_geometry(
        self, direction: str, start_index: int, end_index: int | None = None,
    ) -> Candidate | None:
        """Return the geometry whose strict confirmation occurs first.

        Multiple First candidates may overlap. Order-gender chronology belongs
        to the structure that completes first, not necessarily to the oldest
        still-unconfirmed First candle.
        """
        first_tag = "RED" if direction == "bullish" else "GREEN"
        context_tag = "GREEN" if direction == "bullish" else "RED"
        limit = self.end_index if end_index is None else min(end_index, self.end_index)
        active: list[Candidate] = []
        reset_index = max(self.start_index, start_index - 1)
        for scan in range(start_index, limit + 1):
            candle = self.candles[scan]
            if (
                scan > reset_index
                and candle.tag == first_tag
                and self.candles[scan - 1].tag == context_tag
            ):
                candidate = self._build_direct_candidate(
                    direction, reset_index, scan
                )
                if candidate is not None:
                    active.append(candidate)

            confirmed: list[Candidate] = []
            survivors: list[Candidate] = []
            for candidate in active:
                if scan <= candidate.first_idx:
                    survivors.append(candidate)
                    continue

                # Order geometry is still Reaction geometry.  A candidate that
                # strictly loses the floor/ceiling of the leg that owns it
                # before confirmation is dead; a later breakout/breakdown must
                # never resurrect that invalid structure as an Order Reaction.
                # When invalidation and confirmation compete inside one main
                # candle, the shared lower-timeframe resolver preserves exact
                # chronology (and invalidation-first on a finest-event tie).
                if self._owner_boundary_before_confirmation(
                    direction, candidate, candle
                ):
                    continue

                if direction == "bullish":
                    if candle.low < candidate.box_bottom:
                        candidate.box_bottom = candle.low
                        candidate.box_bottom_source_idx = candle.index
                        candidate.box_bottom_source_time = candle.display_time
                    if candle.high > candidate.box_top:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        confirmed.append(candidate)
                        continue
                else:
                    if candle.high > candidate.box_top:
                        candidate.box_top = candle.high
                        candidate.box_top_source_idx = candle.index
                        candidate.box_top_source_time = candle.display_time
                    if candle.low < candidate.box_bottom:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        confirmed.append(candidate)
                        continue
                survivors.append(candidate)
            active = survivors
            if confirmed:
                return min(confirmed, key=lambda item: item.first_idx)
        return None

    def _build_direct_candidate(
        self, direction: str, reset_index: int, first_index: int
    ) -> Candidate | None:
        context_tag = "GREEN" if direction == "bullish" else "RED"
        first_tag = "RED" if direction == "bullish" else "GREEN"
        first = self.candles[first_index]
        if (
            first_index <= reset_index
            or first.tag != first_tag
            or self.candles[first_index - 1].tag != context_tag
        ):
            return None

        context_start = first_index - 1
        while (
            context_start - 1 >= reset_index
            and self.candles[context_start - 1].tag == context_tag
        ):
            context_start -= 1
        local_start = context_start
        while (
            local_start - 1 >= reset_index
            and self.candles[local_start - 1].tag == first_tag
        ):
            local_start -= 1

        if direction == "bullish":
            local_floor, _ = self.minimum_low(local_start, first_index - 1)
            if first.low < local_floor:
                return None
            box_top, top_source = self.maximum_high(context_start, first_index)
            leg_boundary, leg_source = self.minimum_low(
                reset_index, first_index - 1
            )
            return Candidate(
                first_index, first.display_time,
                top_source.index, top_source.display_time, box_top,
                first_index, first.display_time, first.low,
                mode="A", anchor_idx=leg_source.index,
                anchor_value=leg_boundary, leg_boundary_value=leg_boundary,
            )

        local_ceiling, _ = self.maximum_high(local_start, first_index - 1)
        if first.high > local_ceiling:
            return None
        box_bottom, bottom_source = self.minimum_low(context_start, first_index)
        leg_boundary, leg_source = self.maximum_high(
            reset_index, first_index - 1
        )
        return Candidate(
            first_index, first.display_time,
            first_index, first.display_time, first.high,
            bottom_source.index, bottom_source.display_time, box_bottom,
            mode="A", anchor_idx=leg_source.index,
            anchor_value=leg_boundary, leg_boundary_value=leg_boundary,
        )


    def _scan_direct_candidate(
        self, direction: str, candidate: Candidate, stop_index: int
    ) -> tuple[Candidate | None, int | None]:
        for scan in range(candidate.first_idx + 1, stop_index + 1):
            candle = self.candles[scan]
            confirms = (
                candle.high > candidate.box_top
                if direction == "bullish"
                else candle.low < candidate.box_bottom
            )
            invalidates = self._owner_boundary_before_confirmation(
                direction, candidate, candle
            )
            if invalidates:
                return None, scan
            if direction == "bullish" and candle.low < candidate.box_bottom:
                candidate.box_bottom = candle.low
                candidate.box_bottom_source_idx = candle.index
                candidate.box_bottom_source_time = candle.display_time
            if direction == "bearish" and candle.high > candidate.box_top:
                candidate.box_top = candle.high
                candidate.box_top_source_idx = candle.index
                candidate.box_top_source_time = candle.display_time
            if confirms:
                candidate.break_idx = scan
                candidate.break_time = candle.display_time
                self._refine(direction, candidate, candle)
                return candidate, None
        return None, None

    def _owner_boundary_before_confirmation(
        self, direction: str, candidate: Candidate, candle: Candle
    ) -> bool:
        """Return whether structural alignment is lost before confirmation.

        A Bearish Leg-Start Top must not rise above its outer ceiling.
        A Bullish Leg-Start Bottom must not fall below its outer floor.
        Equality preserves the unresolved candidate. If a strict invalidation
        competes with confirmation in the same main candle, ordered one-second
        data decides which event occurred first.
        """
        boundary = candidate.leg_boundary_value
        if boundary is None:
            return False

        if direction == "bullish":
            reaches_boundary = candle.low < boundary
            confirms = candle.high > candidate.box_top
        else:
            reaches_boundary = candle.high > boundary
            confirms = candle.low < candidate.box_bottom
        if not reaches_boundary:
            return False
        if not confirms:
            return True

        end = candle.timestamp + self.timeframe
        for second in self.seconds_between(candle.timestamp, end):
            if direction == "bullish":
                if second.low < boundary:
                    return True
                if second.high > candidate.box_top:
                    return False
            else:
                if second.high > boundary:
                    return True
                if second.low < candidate.box_bottom:
                    return False
        return True


    def _result(self) -> DetectionResult:
        return DetectionResult(
            direction=self.output_direction,
            reactions=self.all_reactions[self.output_direction],
            resets=self.all_resets[self.output_direction],
            start_index=self.start_index,
            end_index=self.end_index,
        )

    def detect(
        self, *, stop_after_first_at_or_after: int | None = None
    ) -> DetectionResult:
        direction = self.output_direction
        initial = self._first_initial(direction)
        if initial is None:
            return DetectionResult(
                direction=direction,
                reactions=[],
                resets=[],
                start_index=self.start_index,
                end_index=self.end_index,
            )
        self._append_reaction(direction, initial)
        if (
            stop_after_first_at_or_after is not None
            and initial.first_idx >= stop_after_first_at_or_after
        ):
            return self._result()
        previous = initial
        index = initial.break_idx + 1
        running_value = (
            self.candles[initial.break_idx].high
            if direction == "bullish"
            else self.candles[initial.break_idx].low
        )
        running_source = initial.break_idx
        candidate: Candidate | None = None
        initial_break_candle = self.candles[initial.break_idx]
        initial_helper = self.bull if direction == "bullish" else self.bear
        initial_analysis = (
            initial_helper.breakout_analysis(initial, initial_break_candle)
            if direction == "bullish"
            else initial_helper.breakdown_analysis(initial, initial_break_candle)
        )
        # Exact-confirmation geometry owns the post-confirmation remainder in
        # both directions. ``_append_reaction`` may later expand the public
        # opposite edge with the complete Break main candle, but that later
        # presentation geometry must never erase a Reset that occurred after
        # exact confirmation inside the same candle.
        initial_reset_level = (
            initial_analysis.extreme
            if initial_analysis is not None
            else (initial.box_bottom if direction == "bullish" else initial.box_top)
        )
        initial_reset_second = (
            initial_helper.post_breakout_reset(
                initial_analysis, initial_reset_level, initial_break_candle
            )
            if direction == "bullish"
            else initial_helper.post_breakdown_reset(
                initial_analysis, initial_reset_level, initial_break_candle
            )
        )
        pending_reset_index = (
            initial.break_idx if initial_reset_second is not None else None
        )
        if initial_reset_second is not None:
            self._append_reset(
                direction,
                initial_break_candle,
                initial_reset_level,
                initial.first_idx,
                initial_reset_second.display_time,
            )

        while index <= self.end_index:
            candle = self.candles[index]
            reset = pending_reset_index is not None or (
                candle.low < previous.box_bottom
                if direction == "bullish"
                else candle.high > previous.box_top
            )
            candidate_break = candidate is not None and (
                candle.high > candidate.box_top
                if direction == "bullish"
                else candle.low < candidate.box_bottom
            )
            if reset and candidate_break:
                if direction == "bullish":
                    reset = self.bull.confirmed_reset_before_breakout(
                        candidate, candle, previous.box_bottom
                    )
                else:
                    reset = self.bear.confirmed_reset_before_breakdown(
                        candidate, candle, previous.box_top
                    )
            if reset:
                reset_index = (
                    pending_reset_index
                    if pending_reset_index is not None
                    else index
                )
                reset_candle = self.candles[reset_index]
                pending_reset_index = None
                level = previous.box_bottom if direction == "bullish" else previous.box_top
                already_recorded = (
                    self.all_resets[direction]
                    and self.all_resets[direction][-1].from_first_idx
                    == previous.first_idx
                )
                if not already_recorded:
                    self._append_reset(
                        direction, reset_candle, level, previous.first_idx
                    )
                # A Reset reopens the ordinary same-direction ownership gate.
                # The geometric relaxation belongs only to the cross-direction
                # structural/E path and must not relabel every normal Reset.
                direct_candidate = self._first_direct_same_direction_after_reset(
                    direction, reset_index
                )
                # Both paths are valid interpretations of the same requested-
                # direction restart. The chronologically first confirmation
                # wins; a later Anchor-based candidate must never hide an
                # already complete direct post-Reset color sequence.
                structural = direct_candidate
                if structural is None or structural.break_idx is None:
                    break
                structural.mode = "A"
                structural.cross_direction_origin = False
                structural.cross_direction_chain_owner = False
                if not self._append_reaction(direction, structural):
                    candidate = None
                    index = structural.break_idx + 1
                    pending_reset_index = structural.break_idx
                    continue
                if (
                    stop_after_first_at_or_after is not None
                    and structural.first_idx >= stop_after_first_at_or_after
                ):
                    return self._result()
                previous = structural
                index = structural.break_idx + 1
                running_value = (
                    self.candles[structural.break_idx].high
                    if direction == "bullish"
                    else self.candles[structural.break_idx].low
                )
                running_source = structural.break_idx
                break_candle = self.candles[structural.break_idx]
                helper = self.bull if direction == "bullish" else self.bear
                analysis = (
                    helper.breakout_analysis(structural, break_candle)
                    if direction == "bullish"
                    else helper.breakdown_analysis(structural, break_candle)
                )
                reset_level = (
                    analysis.extreme
                    if analysis is not None
                    else (
                        structural.box_bottom
                        if direction == "bullish"
                        else structural.box_top
                    )
                )
                post_reset_second = (
                    helper.post_breakout_reset(
                        analysis, reset_level, break_candle
                    )
                    if direction == "bullish"
                    else helper.post_breakdown_reset(
                        analysis, reset_level, break_candle
                    )
                )
                if post_reset_second is not None:
                    self._append_reset(
                        direction,
                        break_candle,
                        reset_level,
                        structural.first_idx,
                        post_reset_second.display_time,
                    )
                    # The confirmation candle has already reset the reaction
                    # after its exact intrabar confirmation. Its remainder
                    # cannot seed a Normal successor. Restart from the next
                    # main candle as a fresh Leg-Start search.
                    candidate = None
                    pending_reset_index = structural.break_idx
                else:
                    candidate = self._candidate_from_confirmation_remainder(
                        direction, structural, break_candle, analysis
                    )
                continue

            if candidate is not None:
                if direction == "bullish":
                    if candle.low < candidate.box_bottom:
                        candidate.box_bottom = candle.low
                        candidate.box_bottom_source_idx = candle.index
                        candidate.box_bottom_source_time = candle.display_time
                    if candle.high > candidate.box_top:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        analysis = self._refine(direction, candidate, candle)
                        reset_level = (
                            analysis.extreme if analysis is not None else candidate.box_bottom
                        )
                        post_reset_second = self.bull.post_breakout_reset(
                            analysis, reset_level, candle
                        )
                        self._append_reaction(direction, candidate)
                        if (
                            stop_after_first_at_or_after is not None
                            and candidate.first_idx >= stop_after_first_at_or_after
                        ):
                            return self._result()
                        previous = replace(candidate)
                        running_value = candle.high
                        running_source = candle.index
                        if post_reset_second is not None:
                            self._append_reset(
                                direction,
                                candle,
                                reset_level,
                                previous.first_idx,
                                post_reset_second.display_time,
                            )
                            candidate = None
                            pending_reset_index = candle.index
                        else:
                            candidate = self._candidate_from_confirmation_remainder(
                                direction, previous, candle, analysis
                            )
                else:
                    if candle.high > candidate.box_top:
                        candidate.box_top = candle.high
                        candidate.box_top_source_idx = candle.index
                        candidate.box_top_source_time = candle.display_time
                    if candle.low < candidate.box_bottom:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        analysis = self._refine(direction, candidate, candle)
                        reset_level = (
                            analysis.extreme if analysis is not None else candidate.box_top
                        )
                        post_reset_second = self.bear.post_breakdown_reset(
                            analysis, reset_level, candle
                        )
                        self._append_reaction(direction, candidate)
                        if (
                            stop_after_first_at_or_after is not None
                            and candidate.first_idx >= stop_after_first_at_or_after
                        ):
                            return self._result()
                        previous = replace(candidate)
                        running_value = candle.low
                        running_source = candle.index
                        if post_reset_second is not None:
                            self._append_reset(
                                direction,
                                candle,
                                reset_level,
                                previous.first_idx,
                                post_reset_second.display_time,
                            )
                            candidate = None
                            pending_reset_index = candle.index
                        else:
                            candidate = self._candidate_from_confirmation_remainder(
                                direction, previous, candle, analysis
                            )
            else:
                if direction == "bullish" and candle.tag == "RED":
                    top = max(running_value, candle.high)
                    top_source = running_source if running_value >= candle.high else candle.index
                    bottom_start = top_source + 1 if top_source < candle.index else candle.index
                    bottom, bottom_source = self.minimum_low(bottom_start, candle.index)
                    candidate = Candidate(
                        candle.index,
                        candle.display_time,
                        top_source,
                        self.candles[top_source].display_time,
                        top,
                        bottom_source.index,
                        bottom_source.display_time,
                        bottom,
                        mode="B",
                    )
                elif direction == "bearish" and candle.tag == "GREEN":
                    bottom = min(running_value, candle.low)
                    bottom_source = running_source if running_value <= candle.low else candle.index
                    top_start = bottom_source + 1 if bottom_source < candle.index else candle.index
                    top, top_source = self.maximum_high(top_start, candle.index)
                    candidate = Candidate(
                        candle.index,
                        candle.display_time,
                        top_source.index,
                        top_source.display_time,
                        top,
                        bottom_source,
                        self.candles[bottom_source].display_time,
                        bottom,
                        mode="B",
                    )
            if direction == "bullish" and (running_value is None or candle.high > running_value):
                running_value, running_source = candle.high, candle.index
            if direction == "bearish" and (running_value is None or candle.low < running_value):
                running_value, running_source = candle.low, candle.index
            index += 1

        return self._result()


```
<!-- SOURCE_FILE_END:reaction_engine.py -->
### 26.2 `blue_line_detector.py`

- Source version: `2.3.0`
- Last modified declared by module: `not declared by module`
- Lines: `458`
- Role: Scale/Reset Blue detection, strike state, Blue validity, line construction, and Internal/Public Blue ownership.
- Optional integrity SHA-256: `6fa01d94bc98060b62bc7e68db0ec24a0b0159727d44043affee7130a9c11448`

<!-- SOURCE_FILE_BEGIN:blue_line_detector.py:SHA256=6fa01d94bc98060b62bc7e68db0ec24a0b0159727d44043affee7130a9c11448 -->
```python
"""Blue Line calculation over authoritative Reaction output.

Owns Scale and Reset Blue detection, strike/spacing state, Blue stop validity,
and the distinction between calculation state and public Blue visibility. It
does not decide A/S/E lifecycle ownership.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Sequence

from direction_policy import policy_for


BLUE_LINE_VERSION = "2.3.0"
FIBONACCI_RATIO = Decimal("0.618")


@dataclass(frozen=True, slots=True)
class ScaleStrike:
    source_index: int
    source_time: datetime
    extreme: Decimal


@dataclass(frozen=True, slots=True)
class BlueLine:
    direction: str
    kind: str
    reaction_number: int
    previous_strike_count: int | None
    strike_count: int | None
    fibonacci_level: Decimal | None
    source_index: int
    source_time: datetime
    source_extreme: Decimal
    broken_level: Decimal | None
    line_price: Decimal
    start_time: datetime
    end_time: datetime
    calculation_valid: bool = True
    behavior_internal: bool = False


def _is_color(candle: object, color: str) -> bool:
    return str(getattr(candle, "tag")).upper() == color


def _main_candle(candles_by_index: dict[int, object], index: int) -> object:
    try:
        return candles_by_index[index]
    except KeyError as exc:
        raise ValueError(f"Missing main candle index {index}.") from exc


def _stops_on_index(
    direction: str,
    line: object,
    candles: Sequence[object],
    start_index: int,
    end_index: int,
) -> bool:
    policy = policy_for(direction)
    level = Decimal(getattr(line, "source_extreme"))
    for candle in candles[max(0, start_index) : end_index + 1]:
        extreme = Decimal(getattr(candle, policy.extreme_attr))
        if policy.strict_cross(extreme, level):
            return int(getattr(candle, "index")) == end_index
    return False


def fibonacci_level(direction: str, reaction: object, reference: Decimal) -> Decimal:
    policy = policy_for(direction)  # validates direction centrally
    if policy.direction == "bullish":
        top = Decimal(getattr(reaction, "box_top"))
        return top - FIBONACCI_RATIO * (top - reference)
    bottom = Decimal(getattr(reaction, "box_bottom"))
    return bottom + FIBONACCI_RATIO * (reference - bottom)


def _intrabar_pending_confirmation(
    direction: str,
    chronology: object,
    reaction: object,
    comparison_extreme: Decimal,
    start_time: datetime,
    break_time: datetime,
    candles_by_index: dict[int, object],
) -> ScaleStrike | None:
    policy = policy_for(direction)
    end_time = break_time + chronology.timeframe
    left, right = chronology.lower_bounds(start_time, end_time)
    relevant = chronology.seconds[left:right]
    if not relevant:
        return None

    break_level = Decimal(
        getattr(reaction, "box_top" if direction == "bullish" else "box_bottom")
    )
    eligible: list[object] = []
    for second in relevant:
        extreme = Decimal(getattr(second, policy.extreme_attr))
        penetrates = (
            extreme < comparison_extreme
            if direction == "bullish"
            else extreme > comparison_extreme
        )
        if penetrates:
            eligible.append(second)
        breaks = (
            Decimal(getattr(second, "high")) > break_level
            if direction == "bullish"
            else Decimal(getattr(second, "low")) < break_level
        )
        if breaks and eligible:
            decisive = (
                min(eligible, key=lambda item: Decimal(getattr(item, "low")))
                if direction == "bullish"
                else max(eligible, key=lambda item: Decimal(getattr(item, "high")))
            )
            decisive_time = getattr(decisive, "timestamp")
            source_position = chronology.main_index(decisive_time)
            source = candles_by_index.get(source_position)
            if source is None:
                raise ValueError("Cannot map decisive one-second candle to a main candle.")
            return ScaleStrike(
                source_index=int(getattr(source, "index")),
                source_time=getattr(source, "timestamp"),
                extreme=Decimal(
                    getattr(decisive, policy.extreme_attr)
                ),
            )
    return None


def count_scale_strikes(
    direction: str,
    reaction: object,
    chronology: object,
    reference: Decimal,
    candles_by_index: dict[int, object] | None = None,
) -> tuple[Decimal, list[ScaleStrike]]:
    """Return the exact 0.618 level and confirmed strikes for one reaction."""
    level = fibonacci_level(direction, reaction, reference)
    if candles_by_index is None:
        candles_by_index = {
            int(getattr(candle, "index")): candle for candle in chronology.candles
        }
    first_index = int(getattr(reaction, "first_idx"))
    break_index = int(getattr(reaction, "break_idx"))
    reaction_candles = [
        _main_candle(candles_by_index, index)
        for index in range(first_index, break_index + 1)
    ]
    confirming_color = "GREEN" if direction == "bullish" else "RED"
    strikes: list[ScaleStrike] = []
    pending: ScaleStrike | None = None

    for candle in reaction_candles:
        last_extreme = strikes[-1].extreme if strikes else level
        candle_extreme = Decimal(
            getattr(candle, "low" if direction == "bullish" else "high")
        )
        is_new = (
            candle_extreme < last_extreme
            if direction == "bullish"
            else candle_extreme > last_extreme
        )
        if is_new and (
            pending is None
            or (
                candle_extreme < pending.extreme
                if direction == "bullish"
                else candle_extreme > pending.extreme
            )
        ):
            pending = ScaleStrike(
                source_index=int(getattr(candle, "index")),
                source_time=getattr(candle, "timestamp"),
                extreme=candle_extreme,
            )

        if pending is not None and _is_color(candle, confirming_color):
            strikes.append(pending)
            pending = None

    if pending is not None:
        break_candle = reaction_candles[-1]
        intrabar = _intrabar_pending_confirmation(
            direction=direction,
            chronology=chronology,
            reaction=reaction,
            comparison_extreme=strikes[-1].extreme if strikes else level,
            start_time=pending.source_time,
            break_time=getattr(break_candle, "timestamp"),
            candles_by_index=candles_by_index,
        )
        if intrabar is not None:
            strikes.append(intrabar)

    return level, strikes


def _build_scale_blue_line(
    direction: str,
    reaction_number: int,
    previous_count: int,
    level: Decimal,
    strikes: Sequence[ScaleStrike],
    candles_by_index: dict[int, object],
    chronology: object,
    behavior_internal: bool,
) -> BlueLine:
    """Build one scale Blue from its decisive confirmed strike."""
    decisive = strikes[-1]
    source = _main_candle(candles_by_index, decisive.source_index)
    high = Decimal(getattr(source, "high"))
    low = Decimal(getattr(source, "low"))
    line_price = (
        low + (high - low) / Decimal(3)
        if direction == "bullish"
        else high - (high - low) / Decimal(3)
    )
    return BlueLine(
        direction=direction,
        kind="scale",
        reaction_number=reaction_number,
        previous_strike_count=previous_count,
        strike_count=len(strikes),
        fibonacci_level=level,
        source_index=decisive.source_index,
        source_time=decisive.source_time,
        source_extreme=decisive.extreme,
        broken_level=None,
        line_price=line_price,
        start_time=decisive.source_time - chronology.timeframe,
        end_time=decisive.source_time + chronology.timeframe,
        behavior_internal=behavior_internal,
    )


def _build_reset_blue_line(
    direction: str,
    reaction_number: int,
    reset: object,
    previous_line: BlueLine | None,
    candles: Sequence[object],
    candles_by_index: dict[int, object],
    chronology: object,
    behavior_internal: bool,
) -> BlueLine:
    """Build one Reset Blue while preserving the established double-stop rule."""
    reset_index = int(getattr(reset, "index"))
    source = _main_candle(candles_by_index, reset_index)
    high = Decimal(getattr(source, "high"))
    low = Decimal(getattr(source, "low"))
    line_price = (
        low + (high - low) / Decimal(5)
        if direction == "bullish"
        else high - (high - low) / Decimal(5)
    )
    source_time = getattr(source, "timestamp")
    calculation_valid = not (
        previous_line is not None
        and _stops_on_index(
            direction,
            previous_line,
            candles,
            int(getattr(previous_line, "source_index")) + 1,
            reset_index,
        )
        and (
            low < Decimal(getattr(previous_line, "source_extreme"))
            if direction == "bullish"
            else high > Decimal(getattr(previous_line, "source_extreme"))
        )
    )
    return BlueLine(
        direction=direction,
        kind="reset",
        reaction_number=reaction_number,
        previous_strike_count=None,
        strike_count=None,
        fibonacci_level=None,
        source_index=reset_index,
        source_time=source_time,
        source_extreme=low if direction == "bullish" else high,
        broken_level=Decimal(getattr(reset, "broken_level")),
        line_price=line_price,
        start_time=source_time - chronology.timeframe,
        end_time=source_time + chronology.timeframe,
        calculation_valid=calculation_valid,
        behavior_internal=behavior_internal,
    )

def detect_blue_lines(
    direction: str,
    reactions: Sequence[object],
    chronology: object,
    resets: Sequence[object] = (),
) -> list[BlueLine]:
    """Detect scale and Reset Blue Lines over authoritative engine events."""
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    candles = chronology.candles
    candles_by_index = {
        int(getattr(candle, "index")): candle for candle in candles
    }
    resets_by_first: dict[int, list[object]] = {}
    for reset in resets:
        resets_by_first.setdefault(
            int(getattr(reset, "from_first_idx")), []
        ).append(reset)

    output: list[BlueLine] = []
    previous_reaction: object | None = None
    previous_count: int | None = None
    has_blue_line = False
    healthy_reactions_since_blue = 0

    for reaction_number, reaction in enumerate(reactions, start=1):
        behavior_internal = bool(getattr(reaction, "behavior_internal", False))
        if str(getattr(reaction, "mode")) == "A":
            boundary = getattr(reaction, "anchor_value", None)
            if boundary is None:
                boundary = getattr(reaction, "leg_boundary_value", None)
            if boundary is None:
                raise ValueError(
                    "Leg-Start reaction is missing its leg-head boundary."
                )
            reference = Decimal(boundary)
            previous_count = None
        else:
            if previous_reaction is None:
                raise ValueError(
                    "A Normal reaction cannot precede the Leg-Start reaction."
                )
            reference = Decimal(
                getattr(
                    previous_reaction,
                    "box_bottom" if direction == "bullish" else "box_top",
                )
            )

        level, strikes = count_scale_strikes(
            direction,
            reaction,
            chronology,
            reference,
            candles_by_index,
        )
        scale_candidate = (
            previous_count is not None and len(strikes) > previous_count
        )
        scale_emitted = False
        if scale_candidate and (
            not has_blue_line or healthy_reactions_since_blue >= 1
        ):
            output.append(
                _build_scale_blue_line(
                    direction,
                    reaction_number,
                    previous_count,
                    level,
                    strikes,
                    candles_by_index,
                    chronology,
                    behavior_internal,
                )
            )
            has_blue_line = True
            healthy_reactions_since_blue = 0
            scale_emitted = True

        if has_blue_line and not scale_emitted:
            healthy_reactions_since_blue += 1

        for reset in resets_by_first.get(
            int(getattr(reaction, "first_idx")), []
        ):
            if has_blue_line and healthy_reactions_since_blue < 1:
                continue
            output.append(
                _build_reset_blue_line(
                    direction,
                    reaction_number,
                    reset,
                    output[-1] if output else None,
                    candles,
                    candles_by_index,
                    chronology,
                    behavior_internal,
                )
            )
            has_blue_line = True
            healthy_reactions_since_blue = 0

        previous_reaction = reaction
        previous_count = len(strikes)

    return output


def public_blue_lines(lines: Sequence[BlueLine]) -> list[BlueLine]:
    """Return only calculation-valid, public Blue Lines for serialization."""
    return [
        line
        for line in lines
        if bool(getattr(line, "calculation_valid", True))
        and not bool(getattr(line, "behavior_internal", False))
    ]

def mark_internal_blue_lines(
    lines: Sequence[BlueLine],
    owner_reactions: Sequence[object],
    all_behavior_reactions: Sequence[object],
) -> None:
    """Mark Blue Lines that are private to protected Reaction interiors.

    A Blue is internal when its owning Reaction is behavior-internal, or when
    both its calculation-owned ``source_extreme`` and rendered ``line_price``
    fall strictly inside the same healthy Reaction interior.  The drawing
    offset alone never changes ownership.
    """

    def owner_is_internal(line: BlueLine) -> bool:
        number = int(getattr(line, "reaction_number", 0) or 0)
        if number < 1 or number > len(owner_reactions):
            return False
        return bool(getattr(owner_reactions[number - 1], "behavior_internal", False))

    def geometry_is_internal(line: BlueLine) -> bool:
        source_time = getattr(line, "source_time", None)
        line_price = getattr(line, "line_price", None)
        source_extreme = getattr(line, "source_extreme", None)
        if source_time is None or line_price is None or source_extreme is None:
            return False
        rendered = Decimal(str(line_price))
        semantic = Decimal(str(source_extreme))
        for reaction in all_behavior_reactions:
            first = getattr(reaction, "behavior_first_time", None)
            confirmed = getattr(reaction, "behavior_confirmation_time", None)
            if first is None or confirmed is None:
                continue
            if source_time <= first or source_time > confirmed:
                continue
            bottom = Decimal(str(getattr(reaction, "behavior_public_box_bottom")))
            top = Decimal(str(getattr(reaction, "behavior_public_box_top")))
            if bottom < semantic < top and bottom < rendered < top:
                return True
        return False

    for line in lines:
        if owner_is_internal(line) or geometry_is_internal(line):
            object.__setattr__(line, "behavior_internal", True)
```
<!-- SOURCE_FILE_END:blue_line_detector.py -->
### 26.3 `a_zone_detector.py`

- Source version: `1.6.4`
- Last modified declared by module: `2026-09-21`
- Lines: `782`
- Role: A behavior formation from Blue-pair/double-stop state, inherited stops, trigger chronology, and A source ownership.
- Optional integrity SHA-256: `f5658aef5105dcfad916d3ea6f792877737c2568d67cf27c7b63c2638c5343fd`

<!-- SOURCE_FILE_BEGIN:a_zone_detector.py:SHA256=f5658aef5105dcfad916d3ea6f792877737c2568d67cf27c7b63c2638c5343fd -->
```python
"""A-zone calculation from authoritative Reaction and Blue state.

Owns Blue-pair/double-stop A formation, trigger chronology, continuation
geometry, and A source selection. Downstream S/larger-module ownership is
handled by the S and lifecycle engines rather than rewritten here.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Sequence

from core_utils import as_decimal
from direction_policy import policy_for


A_ZONE_VERSION = "1.6.4"
A_ZONE_LAST_MODIFIED_DATE = "2026-09-21"


@dataclass(frozen=True, slots=True)
class BlueState:
    ordinal: int
    line: object
    formation_index: int
    formation_time: datetime
    stop_index: int | None
    stop_time: datetime | None
    stop_event_time: datetime | None
    stop_level: Decimal
    stop_event_extreme: Decimal | None


@dataclass(frozen=True, slots=True)
class AZone:
    direction: str
    blue_1_ordinal: int
    blue_2_ordinal: int
    blue_1_source_time: datetime
    blue_2_source_time: datetime
    blue_1_stop_time: datetime
    blue_2_stop_time: datetime
    blue_1_stop_level: Decimal
    blue_2_stop_level: Decimal
    continuation_level: Decimal
    continuation_source_index: int
    continuation_source_time: datetime
    trigger_index: int
    trigger_time: datetime
    trigger_event_time: datetime
    reaction_number: int
    reaction_first_time: datetime
    reaction_break_time: datetime
    source_index: int
    source_time: datetime
    price: Decimal


class AZoneDetector:
    def __init__(
        self,
        direction: str,
        reactions: Sequence[object],
        blue_lines: Sequence[object],
        chronology: object,
    ) -> None:
        if direction not in {"bullish", "bearish"}:
            raise ValueError("Direction must be 'bullish' or 'bearish'.")
        self.direction = direction
        self.policy = policy_for(direction)
        self.reactions = list(reactions)
        self.blue_lines = sorted(
            blue_lines,
            key=lambda item: (
                int(getattr(item, "reaction_number")),
                getattr(item, "source_time"),
                str(getattr(item, "kind")),
            ),
        )
        self.chronology = chronology
        self.candles = chronology.candles
        self.lower = chronology.seconds
        self.timeframe = chronology.timeframe
        self.candle_times = chronology.times
        self.lower_times = chronology.second_times
        self.lower_index = chronology.lower_index

    @property
    def extreme_name(self) -> str:
        return self.policy.extreme_attr

    def _strict_cross(self, value: Decimal, level: Decimal) -> bool:
        return self.policy.strict_cross(value, level)

    def _better(self, value: Decimal, current: Decimal) -> bool:
        return self.policy.better_extreme(value, current)

    def _main_index(self, timestamp: datetime) -> int:
        return self.chronology.main_index(timestamp)

    def _lower_window(
        self, start: datetime, end: datetime | None
    ) -> Sequence[object]:
        return self.chronology.lower_window(start, end)

    def _first_crossing(
        self,
        level: Decimal,
        start: datetime,
        end: datetime | None,
    ) -> tuple[int, datetime, Decimal] | None:
        left = bisect_left(self.lower_times, start)
        right = len(self.lower) if end is None else bisect_left(self.lower_times, end)
        if right > left and self.lower_index is not None:
            position = (
                self.lower_index.first_less(left, right, level)
                if self.direction == "bullish"
                else self.lower_index.first_greater(left, right, level)
            )
            if position is None:
                return None
            item = self.lower[position]
            event_time = getattr(item, "timestamp")
            value = as_decimal(getattr(item, self.extreme_name))
            return self._main_index(event_time), event_time, value

        lower_items = self.lower[left:right]
        for item in lower_items:
            value = as_decimal(getattr(item, self.extreme_name))
            if self._strict_cross(value, level):
                event_time = getattr(item, "timestamp")
                return self._main_index(event_time), event_time, value
        if lower_items:
            return None

        start_index = max(0, bisect_left(self.candle_times, start))
        end_index = (
            len(self.candles)
            if end is None
            else max(start_index, bisect_left(self.candle_times, end))
        )
        for item in self.candles[start_index:end_index]:
            value = as_decimal(getattr(item, self.extreme_name))
            if self._strict_cross(value, level):
                return int(getattr(item, "index")), getattr(item, "timestamp"), value
        return None

    def _range_extreme(
        self, start: datetime, end: datetime
    ) -> tuple[Decimal, int, datetime]:
        if end < start:
            raise ValueError("Extreme range end precedes its start.")
        lower_items = self._lower_window(start, end + timedelta(microseconds=1))
        if lower_items:
            source = lower_items[0]
            value = as_decimal(getattr(source, self.extreme_name))
            for item in lower_items[1:]:
                candidate = as_decimal(getattr(item, self.extreme_name))
                if self._better(candidate, value):
                    source = item
                    value = candidate
            source_index = self._main_index(getattr(source, "timestamp"))
            return (
                value,
                source_index,
                getattr(self.candles[source_index], "timestamp"),
            )
        start_index = max(0, bisect_right(self.candle_times, start) - 1)
        end_index = min(
            len(self.candles) - 1,
            max(start_index, bisect_right(self.candle_times, end) - 1),
        )
        source = self.candles[start_index]
        value = as_decimal(getattr(source, self.extreme_name))
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = as_decimal(getattr(item, self.extreme_name))
            if self._better(candidate, value):
                source = item
                value = candidate
        return value, int(getattr(source, "index")), getattr(source, "timestamp")

    def _formation(self, line: object) -> tuple[int, datetime, datetime]:
        reaction_number = int(getattr(line, "reaction_number"))
        if reaction_number < 1 or reaction_number > len(self.reactions):
            raise ValueError("Blue Line refers to a missing reaction.")
        if str(getattr(line, "kind")) == "scale":
            reaction = self.reactions[reaction_number - 1]
            index = int(getattr(reaction, "break_idx"))
            event_time = self._reaction_confirmation_time(reaction)
            stop_scan_time = event_time
        else:
            index = int(getattr(line, "source_index"))
            source_time = getattr(self.candles[index], "timestamp")
            event_time = self._reset_formation_time(line, index)
            stop_scan_time = source_time + self.timeframe
        candle = self.candles[index]
        return index, event_time, stop_scan_time

    def _reset_formation_time(self, line: object, source_index: int) -> datetime:
        """Return the exact strict Reset event that makes a Reset Blue exist."""
        source = self.candles[source_index]
        start = getattr(source, "timestamp")
        end = start + self.timeframe
        broken_level = as_decimal(getattr(line, "broken_level"))
        for item in self._lower_window(start, end):
            value = as_decimal(getattr(item, self.extreme_name))
            if self._strict_cross(value, broken_level):
                return getattr(item, "timestamp")
        return start

    def _build_blue_states(self) -> list[BlueState]:
        states: list[BlueState] = []
        for ordinal, line in enumerate(self.blue_lines, start=1):
            if not bool(getattr(line, "calculation_valid", True)):
                continue
            formation_index, formation_time, stop_scan_time = self._formation(line)
            stop_level = as_decimal(getattr(line, "source_extreme"))
            stop = self._first_crossing(
                stop_level,
                stop_scan_time,
                None,
            )
            states.append(
                BlueState(
                    ordinal=ordinal,
                    line=line,
                    formation_index=formation_index,
                    formation_time=formation_time,
                    stop_index=stop[0] if stop else None,
                    stop_time=(
                        getattr(self.candles[stop[0]], "timestamp") if stop else None
                    ),
                    stop_event_time=stop[1] if stop else None,
                    stop_level=stop_level,
                    stop_event_extreme=stop[2] if stop else None,
                )
            )
        return states

    def _double_stop_a_candidates(self) -> list[AZone]:
        result: list[AZone] = []
        previous: tuple[int, object] | None = None
        for ordinal, line in enumerate(self.blue_lines, start=1):
            if bool(getattr(line, "calculation_valid", True)):
                previous = (ordinal, line)
                continue
            if previous is None:
                continue
            previous_ordinal, previous_line = previous
            formation_index = int(getattr(line, "source_index"))
            formation_time = getattr(line, "source_time")
            source_time = getattr(self.candles[formation_index], "timestamp")
            crossing = self._first_crossing(
                as_decimal(getattr(previous_line, "source_extreme")),
                formation_time,
                source_time + self.timeframe,
            )
            if crossing is None or crossing[0] != formation_index:
                continue
            trigger_index, trigger_event_time, _ = crossing
            match = self._first_reaction_after(
                trigger_event_time,
                not_before=formation_time,
            )
            if match is None:
                continue
            reaction_number, reaction = match
            first_index = int(getattr(reaction, "first_idx"))
            break_index = int(getattr(reaction, "break_idx"))
            source = self._a_source(trigger_index, reaction)
            if source is None:
                continue
            source_index, a_source_time, price = source
            result.append(
                AZone(
                    direction=self.direction,
                    blue_1_ordinal=previous_ordinal,
                    blue_2_ordinal=ordinal,
                    blue_1_source_time=getattr(previous_line, "source_time"),
                    blue_2_source_time=getattr(line, "source_time"),
                    blue_1_stop_time=source_time,
                    blue_2_stop_time=source_time,
                    blue_1_stop_level=as_decimal(getattr(previous_line, "source_extreme")),
                    blue_2_stop_level=as_decimal(getattr(line, "source_extreme")),
                    continuation_level=as_decimal(getattr(previous_line, "source_extreme")),
                    continuation_source_index=int(getattr(previous_line, "source_index")),
                    continuation_source_time=getattr(previous_line, "source_time"),
                    trigger_index=trigger_index,
                    trigger_time=getattr(self.candles[trigger_index], "timestamp"),
                    trigger_event_time=trigger_event_time,
                    reaction_number=reaction_number,
                    reaction_first_time=getattr(self.candles[first_index], "timestamp"),
                    reaction_break_time=getattr(self.candles[break_index], "timestamp"),
                    source_index=source_index,
                    source_time=a_source_time,
                    price=price,
                )
            )
            previous = None
        return result

    def _pair_trigger(
        self,
        previous: BlueState,
        current: BlueState,
        expires_at: datetime | None,
    ) -> tuple[
        Decimal,
        int,
        datetime,
        int,
        datetime,
        datetime,
        datetime,
        datetime,
    ] | None:
        if previous.stop_event_time is None or previous.stop_time is None:
            return None
        if (
            expires_at is not None
            and previous.stop_event_time > expires_at
        ):
            return None

        # A following Blue Line inherits the stop level established by the
        # previous line's first aligned Reaction.  The level is the
        # directional extreme from the previous Blue candle through that
        # Reaction breakout, not the following line's own source extreme.
        inherited = self._inherited_stop(previous, current)
        if inherited is not None:
            level, level_index, level_time, reaction_break_time = inherited
            crossing = self._first_crossing(
                level,
                current.formation_time,
                expires_at,
            )
            if crossing is None:
                return None
            trigger_index, trigger_event_time, _ = crossing
            return (
                level,
                level_index,
                level_time,
                trigger_index,
                getattr(self.candles[trigger_index], "timestamp"),
                trigger_event_time,
                level_time,
                getattr(self.candles[trigger_index], "timestamp"),
            )

        if previous.stop_event_time < current.formation_time:
            current_source_time = getattr(
                self.candles[current.formation_index], "timestamp"
            )
            level, level_index, level_time = self._range_extreme(
                previous.stop_event_time,
                current_source_time - timedelta(microseconds=1),
            )
            formation_candle_end = (
                getattr(self.candles[current.formation_index], "timestamp")
                + self.timeframe
            )
            formation_window_end = (
                min(formation_candle_end, expires_at)
                if expires_at is not None
                else formation_candle_end
            )
            formation_crossing = self._first_crossing(
                level,
                current.formation_time,
                formation_window_end,
            )
            if formation_crossing is not None:
                trigger_index, trigger_event_time, _ = formation_crossing
                effective_stop_time = getattr(
                    self.candles[trigger_index], "timestamp"
                )
                return (
                    level,
                    level_index,
                    level_time,
                    trigger_index,
                    effective_stop_time,
                    trigger_event_time,
                    previous.stop_time,
                    effective_stop_time,
                )

            if current.stop_event_time is None or current.stop_time is None:
                return None
            if (
                expires_at is not None
                and current.stop_event_time > expires_at
            ):
                return None
            search_start = current.stop_event_time
            crossing = self._first_crossing(level, search_start, expires_at)
            if crossing is None:
                return None
            trigger_index, trigger_event_time, _ = crossing
            return (
                level,
                level_index,
                level_time,
                trigger_index,
                getattr(self.candles[trigger_index], "timestamp"),
                trigger_event_time,
                previous.stop_time,
                current.stop_time,
            )

        if current.stop_event_time is None or current.stop_time is None:
            return None
        if (
            expires_at is not None
            and current.stop_event_time > expires_at
        ):
            return None
        first, second = sorted(
            (previous, current),
            key=lambda item: (
                item.stop_event_time,
                item.stop_level if self.direction == "bearish" else -item.stop_level,
            ),
        )
        assert first.stop_event_time is not None
        assert second.stop_event_time is not None
        assert first.stop_event_extreme is not None
        assert second.stop_event_extreme is not None
        first_index = int(first.stop_index)
        level = first.stop_event_extreme
        level_time = getattr(self.candles[first_index], "timestamp")

        if first.stop_event_time == second.stop_event_time:
            trigger_index = int(second.stop_index)
            return (
                level,
                first_index,
                level_time,
                trigger_index,
                getattr(self.candles[trigger_index], "timestamp"),
                second.stop_event_time,
                previous.stop_time,
                current.stop_time,
            )

        crossing = self._first_crossing(level, second.stop_event_time, expires_at)
        if crossing is None:
            return None
        trigger_index, trigger_event_time, _ = crossing
        return (
            level,
            first_index,
            level_time,
            trigger_index,
            getattr(self.candles[trigger_index], "timestamp"),
            trigger_event_time,
            previous.stop_time,
            current.stop_time,
        )

    def _reaction_confirmation_time(self, reaction: object) -> datetime:
        return self.chronology.reaction_confirmation(
            self.direction, reaction, use_intrabar_start=False
        )

    def _first_reaction_after(
        self,
        trigger_event_time: datetime,
        *,
        not_before: datetime | None = None,
    ) -> tuple[int, object] | None:
        for number, reaction in enumerate(self.reactions, start=1):
            first_time = getattr(
                self.candles[int(getattr(reaction, "first_idx"))],
                "timestamp",
            )
            if (
                self._reaction_confirmation_time(reaction) >= trigger_event_time
                and (not_before is None or first_time >= not_before)
            ):
                return number, reaction
        return None

    def _inherited_stop(
        self,
        previous: BlueState,
        current: BlueState,
    ) -> tuple[Decimal, int, datetime, datetime] | None:
        if previous.formation_time >= current.formation_time:
            return None
        chained = (
            previous.stop_time is not None
            and previous.stop_event_time is not None
            and previous.stop_event_time < current.formation_time
            and not bool(getattr(previous.line, "behavior_internal", False))
            and not bool(getattr(current.line, "behavior_internal", False))
        )
        # A Scale Blue may not inherit a continuation stop from a Reaction
        # that completes before the following Blue while the Scale Blue itself
        # is still live. Its semantic sourceExtreme remains authoritative until
        # the Scale Blue actually strict-stops. Reset-Blue chaining keeps its
        # established pre-stop structural route. This rule is direction-neutral.
        if not chained and str(getattr(previous.line, "kind")) == "scale":
            return None
        window_start = previous.stop_time if chained else previous.formation_time
        for reaction in self.reactions:
            first_time = getattr(
                self.candles[int(getattr(reaction, "first_idx"))],
                "timestamp",
            )
            break_time = getattr(
                self.candles[int(getattr(reaction, "break_idx"))],
                "timestamp",
            )
            if first_time <= window_start:
                continue
            if break_time >= current.formation_time:
                continue
            # Exact directional mirror: once a prior Blue has strictly
            # stopped, its carried stop uses the directional extreme across
            # the complete stop-candle -> next same-direction Reaction
            # Breakout-candle interval. Bullish freezes the minimum Low;
            # Bearish freezes the maximum High. The complete Breakout main
            # candle is included for both directions.
            range_end = (
                break_time + self.timeframe - timedelta(microseconds=1)
                if chained
                else break_time
            )
            level, level_index, level_time = self._range_extreme(
                window_start,
                range_end,
            )
            return level, level_index, level_time, break_time
        return None

    def _a_source(
        self,
        trigger_index: int,
        reaction: object,
    ) -> tuple[int, datetime, Decimal] | None:
        """Return A ownership frozen at the exact confirming Reaction event.

        The Blue-pair trigger opens the candidate on its main candle.  The
        confirming Reaction validates that candidate, but later prices in the
        same Break candle already belong to subsequent chronology and may not
        retroactively move A.  Source/price are therefore selected from the
        trigger main-candle open through exact lower-timeframe confirmation,
        inclusive.
        """
        start = getattr(self.candles[trigger_index], "timestamp")
        end = self._reaction_confirmation_time(reaction)
        if end < start:
            return None
        value, source_index, source_time = self._range_extreme(start, end)
        return source_index, source_time, value

    def _detect_ordinary_a(self, states: list[BlueState]) -> list[AZone]:
        """Resolve the ordinary adjacent-Blue A lifecycle."""
        output: list[AZone] = []
        cycle_after_index = -1
        bridge_reuse_ordinal: int | None = None
        index = 0

        while index + 1 < len(states):
            previous = states[index]
            current = states[index + 1]
            bridge_pair = (
                bridge_reuse_ordinal is not None
                and previous.ordinal == bridge_reuse_ordinal
            )
            if (
                current.formation_index <= cycle_after_index
                or (
                    previous.formation_index <= cycle_after_index
                    and not bridge_pair
                )
            ):
                if bridge_pair:
                    bridge_reuse_ordinal = None
                index += 1
                continue

            expires_at = (
                states[index + 2].formation_time
                if index + 2 < len(states)
                else None
            )
            trigger = self._pair_trigger(previous, current, expires_at)
            if trigger is None:
                index += 1
                continue

            (
                continuation_level,
                continuation_source_index,
                continuation_source_time,
                trigger_index,
                trigger_time,
                trigger_event_time,
                blue_1_stop_time,
                blue_2_stop_time,
            ) = trigger
            match = self._first_reaction_after(
                trigger_event_time,
                not_before=max(blue_1_stop_time, blue_2_stop_time),
            )
            if match is None:
                break
            reaction_number, reaction = match
            source = self._a_source(trigger_index, reaction)
            if source is None:
                index += 1
                continue
            source_index, source_time, price = source
            break_index = int(getattr(reaction, "break_idx"))
            output.append(
                AZone(
                    direction=self.direction,
                    blue_1_ordinal=previous.ordinal,
                    blue_2_ordinal=current.ordinal,
                    blue_1_source_time=getattr(previous.line, "source_time"),
                    blue_2_source_time=getattr(current.line, "source_time"),
                    blue_1_stop_time=blue_1_stop_time,
                    blue_2_stop_time=blue_2_stop_time,
                    blue_1_stop_level=previous.stop_level,
                    blue_2_stop_level=current.stop_level,
                    continuation_level=continuation_level,
                    continuation_source_index=continuation_source_index,
                    continuation_source_time=continuation_source_time,
                    trigger_index=trigger_index,
                    trigger_time=trigger_time,
                    trigger_event_time=trigger_event_time,
                    reaction_number=reaction_number,
                    reaction_first_time=getattr(
                        self.candles[int(getattr(reaction, "first_idx"))],
                        "timestamp",
                    ),
                    reaction_break_time=getattr(
                        self.candles[break_index], "timestamp"
                    ),
                    source_index=source_index,
                    source_time=source_time,
                    price=price,
                )
            )
            cycle_after_index = break_index

            confirmation_time = self._reaction_confirmation_time(reaction)
            first_stop = self._first_crossing(price, confirmation_time, None)
            allow_adjacent_reuse = (
                first_stop is not None
                and index + 2 < len(states)
                and states[index + 2].formation_time >= first_stop[1]
            )
            if allow_adjacent_reuse:
                bridge_reuse_ordinal = current.ordinal
                index += 1
            else:
                bridge_reuse_ordinal = None
                while (
                    index < len(states)
                    and states[index].formation_index <= cycle_after_index
                ):
                    index += 1
        return output

    def _filter_special_a(
        self,
        special: list[AZone],
        ordinary: list[AZone],
    ) -> tuple[list[AZone], list[AZone]]:
        """Resolve special double-stop A ownership against ordinary A state."""
        ordinary_reactions = {
            item.reaction_number
            for item in ordinary
            if item.reaction_number is not None
        }
        special = [
            item
            for item in special
            if item.reaction_number not in ordinary_reactions
        ]

        filtered_special: list[AZone] = []
        for item in special:
            prior_candidates = [
                prior
                for prior in ordinary
                if prior.source_time < item.source_time
            ]
            prior = max(
                prior_candidates,
                key=lambda zone: zone.source_time,
                default=None,
            )
            if prior is not None and self._a_was_stopped_before(
                prior,
                item.reaction_first_time,
                not_before=item.blue_1_source_time,
            ):
                continue
            filtered_special.append(item)
        special = filtered_special

        consumed_special = [
            (
                {
                    int(getattr(item, "blue_1_ordinal")),
                    int(getattr(item, "blue_2_ordinal")),
                },
                getattr(item, "trigger_event_time"),
            )
            for item in special
        ]
        if consumed_special:
            ordinary = [
                item
                for item in ordinary
                if not any(
                    getattr(item, "trigger_event_time") > trigger_event_time
                    and {
                        int(getattr(item, "blue_1_ordinal")),
                        int(getattr(item, "blue_2_ordinal")),
                    }
                    & consumed_ordinals
                    for consumed_ordinals, trigger_event_time in consumed_special
                )
            ]
        return ordinary, special

    def detect(self) -> list[AZone]:
        """Return ordinary and special A zones after one ownership resolution."""
        states = self._build_blue_states()
        ordinary = self._detect_ordinary_a(states)
        ordinary, special = self._filter_special_a(
            self._double_stop_a_candidates(), ordinary
        )
        return sorted(
            ordinary + special,
            key=lambda item: (item.source_time, item.trigger_event_time),
        )

    def _a_was_stopped_before(
        self,
        zone: AZone,
        end_time: datetime,
        *,
        not_before: datetime | None = None,
    ) -> bool:
        """Return whether A's *first* strict stop belongs to this lifecycle.

        A stop that happened before ``not_before`` completed the prior cycle.
        A later recross of the same price must not be mistaken for a new stop
        owned by the current Blue pair.
        """
        start = int(getattr(self.candles[zone.source_index], "index")) + 1
        if start >= len(self.candles):
            return False
        first_stop = self._first_crossing(
            zone.price,
            getattr(self.candles[start], "timestamp"),
            end_time,
        )
        if first_stop is None:
            return False
        return not_before is None or first_stop[1] >= not_before


def detect_a_zones(
    direction: str,
    reactions: Sequence[object],
    blue_lines: Sequence[object],
    chronology: object,
) -> list[AZone]:
    return AZoneDetector(direction, reactions, blue_lines, chronology).detect()


```
<!-- SOURCE_FILE_END:a_zone_detector.py -->
### 26.4 `s_zone_detector.py`

- Source version: `4.20.0`
- Last modified declared by module: `2026-09-23 10:19:31 +03:30`
- Lines: `1562`
- Role: A-to-S handoff, S formation families, stopped-A Orders, shared accepted-Order stop reconciliation, and initial OrderAudit.
- Optional integrity SHA-256: `7714025b3f43087b09844df6feeef4eef0ec72eeb841115293df4c126fd202ee`

<!-- SOURCE_FILE_BEGIN:s_zone_detector.py:SHA256=7714025b3f43087b09844df6feeef4eef0ec72eeb841115293df4c126fd202ee -->
```python
"""S-zone calculation from authoritative A, Reaction, Blue, and Order state.

Owns A-to-S handoff, S Red/Blue Simple/Advanced/Type3 formation, S decision
chronology, shared accepted-Order stop reconciliation, and the initial Order
audit created by stopped A zones. Larger E/StopAll arbitration remains
lifecycle-owned.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable, Sequence

from core_utils import as_decimal, reaction_identity
from direction_policy import policy_for


S_ZONE_VERSION = "4.20.0"
S_ZONE_LAST_MODIFIED = "2026-09-23 10:19:31 +03:30"


@dataclass(frozen=True, slots=True)
class SZone:
    direction: str
    color: str
    formation_type: str
    a_ordinal: int
    a_source_index: int
    a_source_time: datetime
    a_price: Decimal
    a_stop_index: int
    a_stop_time: datetime
    a_stop_event_time: datetime
    order_direction: str | None
    order_reaction_number: int | None
    order_mode: str | None
    order_first_index: int | None
    order_first_time: datetime | None
    order_break_index: int | None
    order_break_time: datetime | None
    order_confirmation_time: datetime | None
    order_box_top: Decimal | None
    order_box_top_source_index: int | None
    order_box_top_source_time: datetime | None
    order_box_bottom: Decimal | None
    order_box_bottom_source_index: int | None
    order_box_bottom_source_time: datetime | None
    order_stop_level: Decimal | None
    order_stop_source_index: int | None
    order_stop_source_time: datetime | None
    reset_reaction_number: int | None
    reset_time: datetime | None
    source_index: int
    source_time: datetime
    price: Decimal
    decision_index: int
    decision_time: datetime
    decision_event_time: datetime


class SZoneDetector:
    def __init__(
        self,
        direction: str,
        trend_reactions: Sequence[object],
        opposite_reactions: Sequence[object],
        trend_blue_lines: Sequence[object],
        a_zones: Sequence[object],
        chronology: object,
        start_index: int | None = None,
        end_index: int | None = None,
        opposite_resets: Sequence[object] = (),
        initial_order_geometry: Callable[[int, datetime, int], object | None] | None = None,
    ) -> None:
        if direction not in {"bullish", "bearish"}:
            raise ValueError("Direction must be 'bullish' or 'bearish'.")
        self.direction = direction
        self.policy = policy_for(direction)
        self.order_direction = chronology.opposite_direction(direction)
        self.trend_reactions = list(trend_reactions)
        self.opposite_reactions = list(opposite_reactions)
        self.opposite_resets = list(opposite_resets)
        self.initial_order_geometry = initial_order_geometry
        self.trend_blue_lines = list(trend_blue_lines)
        self.a_zones = sorted(
            a_zones,
            key=lambda item: (
                getattr(item, "reaction_break_time"),
                int(getattr(item, "source_index")),
            ),
        )
        self.chronology = chronology
        self.candles = chronology.candles
        self.lower = chronology.seconds
        self.timeframe = chronology.timeframe
        self.candle_times = chronology.times
        self.lower_times = chronology.second_times
        self.lower_index = chronology.lower_index
        self.start_index = 0 if start_index is None else int(start_index)
        self.end_index = (
            len(self.candles) - 1 if end_index is None else int(end_index)
        )
        if not 0 <= self.start_index <= self.end_index < len(self.candles):
            raise ValueError("Invalid S analysis range.")
        self.range_start = self.candle_times[self.start_index]
        self.range_end = self.candle_times[self.end_index] + self.timeframe
        self.order_audit: dict[tuple[int, int], dict[str, object]] = {}
        # The exact A-stop handoff and the post-decision live-S interval are
        # distinct ownership phases.  Pre-decision handoff keeps Behavior
        # Independence for candidates opened after the A stop; once S is
        # decided, ordinary A re-entry is blocked until the S strict stop.
        self.a_ownership_windows: list[tuple[datetime, datetime | None]] = []
        self._reset_blue_formation_by_reaction: dict[int, datetime] = {}
        self._opposite_by_first_index = {
            int(getattr(item, "first_idx")): (number, item)
            for number, item in enumerate(self.opposite_reactions, start=1)
        }
        # Performance implementation detail: the authoritative Order chronology
        # is immutable for this detector run. Build its exact legacy sort order
        # once, then bisect/cache A-stop lookups instead of re-scanning and
        # re-sorting the complete opposite-Reaction history for every A.
        self._opposite_order_matches = sorted(
            (
                self._reaction_confirmation_time(item, self.order_direction),
                int(getattr(item, "first_idx")),
                int(getattr(item, "break_idx")),
                number,
                item,
            )
            for number, item in enumerate(self.opposite_reactions, start=1)
        )
        self._opposite_order_confirmation_times = [
            item[0] for item in self._opposite_order_matches
        ]
        self._order_matches_after_cache: dict[
            datetime, tuple[tuple[int, object, datetime], ...]
        ] = {}

        for line in self.trend_blue_lines:
            if not bool(getattr(line, "calculation_valid", True)):
                continue
            if str(getattr(line, "kind")) != "reset":
                continue
            reaction_number = int(getattr(line, "reaction_number"))
            if reaction_number not in self._reset_blue_formation_by_reaction:
                self._reset_blue_formation_by_reaction[reaction_number] = (
                    self._blue_formation_time(line)
                )

        # Performance implementation detail: immutable chronology indexes.
        # They preserve the exact legacy sort keys and are scoped to this run.
        self._trend_ordered = sorted(
            (
                self._reaction_confirmation_time(item, self.direction),
                int(getattr(item, "first_idx")),
                int(getattr(item, "break_idx")),
                number,
                item,
            )
            for number, item in enumerate(self.trend_reactions, start=1)
        )
        self._trend_ordered_confirmation_times = [item[0] for item in self._trend_ordered]
        self._trend_confirmation_times_sorted = sorted(
            item[0] for item in self._trend_ordered
        )
        self._opposite_confirmation_by_first = {
            int(getattr(item, "first_idx")): self._reaction_confirmation_time(
                item, self.order_direction
            )
            for item in self.opposite_reactions
        }
        self._opposite_reset_events = sorted(
            ((self._reset_time(reset), reset) for reset in self.opposite_resets),
            key=lambda item: item[0],
        )
        self._opposite_reset_event_times = [item[0] for item in self._opposite_reset_events]
        self._opposite_reset_times_by_owner: dict[int, list[datetime]] = {}
        for reset_time, reset in self._opposite_reset_events:
            self._opposite_reset_times_by_owner.setdefault(
                int(getattr(reset, "from_first_idx")), []
            ).append(reset_time)
        self._public_blue_formation_times = sorted(
            self._blue_formation_time(line)
            for line in self.trend_blue_lines
            if bool(getattr(line, "calculation_valid", True))
            and not bool(getattr(line, "behavior_internal", False))
        )

    def _main_index(self, timestamp: datetime) -> int:
        return self.chronology.main_index(timestamp)

    def _lower_window(
        self, start: datetime, end: datetime | None
    ) -> Sequence[object]:
        return self.chronology.lower_window(start, end)

    def _reaction_confirmation_time(
        self, reaction: object, direction: str
    ) -> datetime:
        return self.chronology.reaction_confirmation(direction, reaction)

    def reaction_confirmation_time(
        self, reaction: object, direction: str
    ) -> datetime:
        """Public chronology API used by cross-stage lifecycle ownership."""
        return self._reaction_confirmation_time(reaction, direction)


    def _reset_time(self, reset: object) -> datetime:
        return self.chronology.reset_time(reset)

    def _a_confirmation_time(self, zone: object) -> datetime:
        number = int(getattr(zone, "reaction_number"))
        if number < 1 or number > len(self.trend_reactions):
            raise ValueError("A refers to a missing trend reaction.")
        return self._reaction_confirmation_time(
            self.trend_reactions[number - 1], self.direction
        )

    def _trend_extreme(self, candle: object) -> Decimal:
        return as_decimal(
            getattr(candle, self.policy.extreme_attr)
        )

    def _a_stopped(self, value: Decimal, level: Decimal) -> bool:
        return self.policy.strict_cross(value, level)

    def _first_a_stop(
        self, level: Decimal, start: datetime
    ) -> tuple[int, datetime, datetime] | None:
        scan_start = max(start, self.range_start)
        left = bisect_left(self.lower_times, scan_start)
        right = bisect_left(self.lower_times, self.range_end)
        if right > left and self.lower_index is not None:
            position = (
                self.lower_index.first_less(left, right, level)
                if self.direction == "bullish"
                else self.lower_index.first_greater(left, right, level)
            )
            if position is None:
                return None
            event_time = self.lower_times[position]
            index = self._main_index(event_time)
            return index, getattr(self.candles[index], "timestamp"), event_time

        lower_items = self.lower[left:right]
        for item in lower_items:
            if self._a_stopped(self._trend_extreme(item), level):
                event_time = getattr(item, "timestamp")
                index = self._main_index(event_time)
                return index, getattr(self.candles[index], "timestamp"), event_time
        if lower_items:
            return None
        start_index = max(self.start_index, bisect_left(self.candle_times, start))
        for item in self.candles[start_index : self.end_index + 1]:
            if self._a_stopped(self._trend_extreme(item), level):
                return (
                    int(getattr(item, "index")),
                    getattr(item, "timestamp"),
                    getattr(item, "timestamp"),
                )
        return None

    def first_a_stop(
        self, level: Decimal, start: datetime
    ) -> tuple[int, datetime, datetime] | None:
        """Public lifecycle API for the first strict A stop."""
        return self._first_a_stop(level, start)


    def _first_order_after(
        self, a_stop_event_time: datetime
    ) -> tuple[int, object, datetime] | None:
        """Return the immutable first canonical opposite Order after A-stop.

        Each stopped A creates at most one parent-stop Order_A.  Subsequent
        native Mode-B Reactions cannot refresh that physical identity; they
        may be accepted only through independently valid creation causes.
        """
        matches = self._order_matches_after(a_stop_event_time)
        return matches[0] if matches else None

    def _order_matches_after(
        self, a_stop_event_time: datetime
    ) -> list[tuple[int, object, datetime]]:
        """Expose canonical opposite-Order chronology without changing ownership."""
        cached = self._order_matches_after_cache.get(a_stop_event_time)
        if cached is not None:
            return list(cached)

        gate_index = self._main_index(a_stop_event_time)
        position = bisect_right(
            self._opposite_order_confirmation_times, a_stop_event_time
        )
        matches = tuple(
            (number, reaction, confirmation)
            for confirmation, first_index, _break, number, reaction
            in self._opposite_order_matches[position:]
            if first_index >= gate_index
        )
        self._order_matches_after_cache[a_stop_event_time] = matches
        return list(matches)

    def _resolved_order_backed_zone(
        self,
        zone: object,
        a_ordinal: int,
        a_price: Decimal,
        a_stop: tuple[int, datetime, datetime],
        first_order_match: tuple[int, object, datetime],
    ) -> SZone | None:
        """Resolve S using only the first physical Order_A owned by this A.

        The initial stopped-A OrderAudit retains its original parent-stop
        cause.  A later canonical Reaction never replaces the original
        Order_A, irrespective of its native Reaction Mode or S decision time.
        """
        return self._build_order_backed_zone(
            zone, a_ordinal, a_price, a_stop, first_order_match
        )

    def _record_a_order_audit(
        self,
        zone: object,
        a_stop_event_time: datetime,
        order_match: tuple[int, object, datetime],
    ) -> None:
        """Attach one stopped-A creation cause to a physical Order identity."""
        source_time = getattr(zone, "source_time")
        order_number, order, order_confirmation_time = order_match
        (
            order_stop_level,
            order_stop_source_index,
            order_stop_source_time,
        ) = self._order_stop(order_number, order)
        identity = reaction_identity(order)
        cause = (source_time, a_stop_event_time)
        entry = self.order_audit.get(identity)
        if entry is None:
            entry = {
                "reaction_number": order_number,
                "reaction": order,
                "confirmation_time": order_confirmation_time,
                "stop_level": order_stop_level,
                "stop_source_index": order_stop_source_index,
                "stop_source_time": order_stop_source_time,
                "a_source_time": source_time,
                "a_stop_event_time": a_stop_event_time,
                "a_causes": [],
            }
            self.order_audit[identity] = entry
        a_causes = entry.setdefault("a_causes", [])
        if cause not in a_causes:
            a_causes.append(cause)

    def _audit_stopped_a(self, zone: object) -> None:
        """Record the independent order gender created by one stopped A."""
        a_price = as_decimal(getattr(zone, "price"))
        a_stop = self._first_a_stop(a_price, self._a_confirmation_time(zone))
        if a_stop is None:
            return
        _, _, a_stop_event_time = a_stop
        order_match = self._first_order_after(a_stop_event_time)
        if order_match is None:
            return
        self._record_a_order_audit(zone, a_stop_event_time, order_match)

    def _candidate_source(
        self, start_index: int, end_index: int
    ) -> tuple[int, datetime, Decimal]:
        if end_index < start_index:
            raise ValueError("S candidate range ends before the A stop.")
        source = self.candles[start_index]
        value = self._trend_extreme(source)
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = self._trend_extreme(item)
            better = self.policy.better_extreme(candidate, value)
            if better:
                source = item
                value = candidate
        return int(getattr(source, "index")), getattr(source, "timestamp"), value

    def _candidate_source_last(
        self, start_index: int, end_index: int
    ) -> tuple[int, datetime, Decimal]:
        """Return the directional extreme, assigning equality to the last candle."""
        if end_index < start_index:
            raise ValueError("S candidate range ends before it starts.")
        source = self.candles[start_index]
        value = self._trend_extreme(source)
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = self._trend_extreme(item)
            better_or_equal = (
                candidate <= value
                if self.direction == "bullish"
                else candidate >= value
            )
            if better_or_equal:
                source = item
                value = candidate
        return int(getattr(source, "index")), getattr(source, "timestamp"), value

    def _first_trend_reaction_after_order(
        self, order_confirmation_time: datetime
    ) -> tuple[int, object, datetime] | None:
        for number, reaction in enumerate(self.trend_reactions, start=1):
            confirmation = self._reaction_confirmation_time(
                reaction, self.direction
            )
            if confirmation > order_confirmation_time:
                return number, reaction, confirmation
        return None


    def _nested_trend_reaction(
        self, order: object, order_confirmation_time: datetime
    ) -> tuple[int, object, datetime] | None:
        order_first_index = int(getattr(order, "first_idx"))
        order_break_index = int(getattr(order, "break_idx"))
        order_first = getattr(self.candles[order_first_index], "timestamp")
        order_top = as_decimal(getattr(order, "box_top"))
        order_bottom = as_decimal(getattr(order, "box_bottom"))
        for number, reaction in enumerate(self.trend_reactions, start=1):
            first_index = int(getattr(reaction, "first_idx"))
            break_index = int(getattr(reaction, "break_idx"))
            first = getattr(self.candles[first_index], "timestamp")
            if (
                first <= order_first
                or first_index <= order_first_index
                or break_index > order_break_index
                or first >= order_confirmation_time
            ):
                continue
            confirmation = self._reaction_confirmation_time(
                reaction, self.direction
            )
            wholly_inside = (
                as_decimal(getattr(reaction, "box_top")) <= order_top
                and as_decimal(getattr(reaction, "box_bottom")) >= order_bottom
            )
            if confirmation <= order_confirmation_time and wholly_inside:
                return number, reaction, confirmation
        return None

    def _simple_candidate(
        self, order: object, reaction: object
    ) -> tuple[int, datetime, Decimal]:
        """Use the inclusive order-Break to aligned-Break interval."""
        return self._candidate_source_last(
            int(getattr(order, "break_idx")),
            int(getattr(reaction, "break_idx")),
        )

    def _type3_reset_leg(
        self, reset: object
    ) -> tuple[int, datetime, Decimal] | None:
        """Return the independent Type-3 inclusive Break-to-Reset geometry."""
        owner_match = self._opposite_by_first_index.get(
            int(getattr(reset, "from_first_idx"))
        )
        if owner_match is None:
            return None
        _, owner = owner_match
        start_index = int(getattr(owner, "break_idx"))
        end_index = self._main_index(self._reset_time(reset))
        if end_index < start_index:
            return None
        return self._candidate_source_last(start_index, end_index)

    def _type3_has_trend_reaction(
        self, a_stop_event: datetime, crossing: datetime
    ) -> bool:
        position = bisect_right(self._trend_confirmation_times_sorted, a_stop_event)
        return (
            position < len(self._trend_confirmation_times_sorted)
            and self._trend_confirmation_times_sorted[position] <= crossing
        )

    def _first_type3(
        self,
        a_stop_event: datetime,
        deadline: datetime,
    ) -> tuple[int, datetime, Decimal, int, datetime, int, datetime, datetime] | None:
        """Find the first no-order Type-3 Reset-leg S decision before a new order."""
        winner = None
        left = bisect_right(self._opposite_reset_event_times, a_stop_event)
        right = bisect_left(self._opposite_reset_event_times, deadline)
        for reset_time, reset in self._opposite_reset_events[left:right]:
            owner_first = int(getattr(reset, "from_first_idx"))
            owner_confirmation = self._opposite_confirmation_by_first.get(owner_first)
            if owner_confirmation is None or owner_confirmation > a_stop_event:
                continue
            owner_resets = self._opposite_reset_times_by_owner.get(owner_first, ())
            if owner_resets and owner_resets[0] <= a_stop_event:
                continue
            leg = self._type3_reset_leg(reset)
            if leg is None:
                continue
            source_index, source_time, boundary = leg
            lower_left = bisect_left(self.lower_times, reset_time)
            lower_right = bisect_left(self.lower_times, deadline)
            crossing_position = (
                self.lower_index.first_less(lower_left, lower_right, boundary)
                if self.direction == "bullish"
                else self.lower_index.first_greater(lower_left, lower_right, boundary)
            )
            if crossing_position is None:
                continue
            crossing = self.lower_times[crossing_position]
            if not self._type3_has_trend_reaction(a_stop_event, crossing):
                continue
            decision_index = self._main_index(crossing)
            owner_number = self._opposite_by_first_index[owner_first][0]
            candidate = (
                source_index,
                source_time,
                boundary,
                decision_index,
                getattr(self.candles[decision_index], "timestamp"),
                owner_number,
                reset_time,
                crossing,
            )
            if winner is None or candidate[-1] < winner[-1]:
                winner = candidate
        return winner


    def _type4_has_blue(
        self, candidate_source_index: int, crossing_event: datetime
    ) -> bool:
        """Return whether a public calculation-valid Blue exists in Type-4 window."""
        window_start = self.candle_times[candidate_source_index]
        position = bisect_left(self._public_blue_formation_times, window_start)
        return (
            position < len(self._public_blue_formation_times)
            and self._public_blue_formation_times[position] <= crossing_event
        )

    def _first_type4(
        self,
        a_stop: tuple[int, datetime, datetime],
        deadline: datetime,
    ) -> tuple[int, datetime, Decimal, int, datetime, int, datetime] | None:
        """Find the first order-free S Blue Type-4 decision after A stop.

        Bearish: from the A-stop main candle through the Breakout main candle
        of the latest confirmed Bearish Reaction, the maximum High is the
        current S candidate. Bullish mirrors with minimum Low. The candidate is
        valid only while no opposite Order has formed. If it strict-crosses
        without a qualifying Blue, no S is emitted; a later aligned Reaction
        replaces it with a freshly calculated candidate over the same A-stop
        origin.
        """
        a_stop_index, _a_stop_time, a_stop_event = a_stop
        left = bisect_right(self._trend_ordered_confirmation_times, a_stop_event)
        right = bisect_left(self._trend_ordered_confirmation_times, deadline)
        aligned = [
            (confirmation, number, reaction)
            for confirmation, _first, break_index, number, reaction
            in self._trend_ordered[left:right]
            if break_index >= a_stop_index
        ]

        for position, (confirmation, reaction_number, reaction) in enumerate(aligned):
            break_index = int(getattr(reaction, "break_idx"))
            source_index, source_time, candidate_level = self._candidate_source_last(
                a_stop_index, break_index
            )
            candidate_event = self._candidate_event_time(
                source_index, candidate_level, a_stop_event
            )
            search_start = max(confirmation, candidate_event, a_stop_event)
            next_confirmation = (
                aligned[position + 1][0]
                if position + 1 < len(aligned)
                else deadline
            )
            search_end = min(deadline, next_confirmation)
            if search_start >= search_end:
                continue

            lower_left = bisect_left(self.lower_times, search_start)
            lower_right = bisect_left(self.lower_times, search_end)
            crossing_position = (
                self.lower_index.first_less(lower_left, lower_right, candidate_level)
                if self.direction == "bullish"
                else self.lower_index.first_greater(lower_left, lower_right, candidate_level)
            )
            if crossing_position is None:
                continue
            crossing_event = self.lower_times[crossing_position]
            if not self._type4_has_blue(source_index, crossing_event):
                # The candidate failed without Blue.  While no Order exists,
                # the next aligned Reaction will transfer/rebuild the candidate.
                continue

            decision_index = self._main_index(crossing_event)
            return (
                source_index,
                source_time,
                candidate_level,
                decision_index,
                getattr(self.candles[decision_index], "timestamp"),
                reaction_number,
                crossing_event,
            )
        return None

    def _build_type4_zone(
        self,
        zone: object,
        a_ordinal: int,
        a_price: Decimal,
        a_stop: tuple[int, datetime, datetime],
        type4: tuple[int, datetime, Decimal, int, datetime, int, datetime],
    ) -> SZone:
        """Build the order-free Blue Type-4 continuation for one stopped A."""
        a_stop_index, a_stop_time, a_stop_event_time = a_stop
        (
            source_index, source_time, price, decision_index, decision_time,
            _trend_reaction_number, decision_event_time,
        ) = type4
        return SZone(
            direction=self.direction,
            color="blue",
            formation_type="type4",
            a_ordinal=a_ordinal,
            a_source_index=int(getattr(zone, "source_index")),
            a_source_time=getattr(zone, "source_time"),
            a_price=a_price,
            a_stop_index=a_stop_index,
            a_stop_time=a_stop_time,
            a_stop_event_time=a_stop_event_time,
            order_direction=None,
            order_reaction_number=None,
            order_mode=None,
            order_first_index=None,
            order_first_time=None,
            order_break_index=None,
            order_break_time=None,
            order_confirmation_time=None,
            order_box_top=None,
            order_box_top_source_index=None,
            order_box_top_source_time=None,
            order_box_bottom=None,
            order_box_bottom_source_index=None,
            order_box_bottom_source_time=None,
            order_stop_level=None,
            order_stop_source_index=None,
            order_stop_source_time=None,
            reset_reaction_number=None,
            reset_time=None,
            source_index=source_index,
            source_time=source_time,
            price=price,
            decision_index=decision_index,
            decision_time=decision_time,
            decision_event_time=decision_event_time,
        )


    def _candidate_after_order(
        self,
        order_confirmation_time: datetime,
        reaction: object,
    ) -> tuple[int, datetime, Decimal]:
        """Find a candidate strictly after the order is confirmed.

        A reaction anchor is authoritative only when it is also after the
        order confirmation.  Otherwise the earliest extreme in the candles
        following the confirmation through the reaction First owns the
        candidate.
        """
        first_index = int(getattr(reaction, "first_idx"))
        start_index = bisect_left(self.candle_times, order_confirmation_time)
        start_index = max(self.start_index, min(start_index, first_index))
        anchor_index = getattr(reaction, "anchor_idx", None)
        anchor_value = getattr(reaction, "anchor_value", None)
        if anchor_index is not None and int(anchor_index) >= start_index:
            source = self.candles[int(anchor_index)]
            return (
                int(anchor_index),
                getattr(source, "timestamp"),
                as_decimal(anchor_value),
            )
        candidate = self._candidate_source(start_index, first_index)
        containing_index = self._main_index(order_confirmation_time)
        if containing_index < start_index:
            # Do not discard the valid remainder of an intrabar confirmation
            # candle, or import an extreme that occurred before confirmation.
            remainder = self._lower_window(
                order_confirmation_time,
                self.candle_times[containing_index] + self.timeframe,
            )
            for item in remainder:
                value = self._trend_extreme(item)
                if self._a_stopped(value, candidate[2]) or value == candidate[2]:
                    candidate = (
                        containing_index, self.candle_times[containing_index], value
                    )
        return candidate

    def _a_source_event_time(self, zone: object) -> datetime:
        """Locate the source extreme, including an A-stop main candle."""
        source = getattr(zone, "source_time")
        price = as_decimal(getattr(zone, "price"))
        for item in self._lower_window(source, source + self.timeframe):
            if self._trend_extreme(item) == price:
                return getattr(item, "timestamp")
        return source

    def _a_owned_by_s(self, zone: object) -> bool:
        event_time = self._a_source_event_time(zone)
        for start, end in self.a_ownership_windows:
            if not (start <= event_time and (end is None or event_time < end)):
                continue

            # The exact A-stop handoff owns only candidates whose own trigger
            # began at or before that boundary.  A new A structure whose
            # trigger begins strictly after the handoff is independently
            # eligible; the later lifecycle hierarchy still decides whether
            # it may survive as an equal/smaller behavior.
            trigger_event = getattr(zone, "trigger_event_time", None)
            if trigger_event is not None and trigger_event > start:
                return False

            # A decided S normally owns this continuation. A fresh Reset-Blue
            # pair may open a new A only when the entire pair is born after
            # that S ownership began, Blue-1 has already stopped before Blue-2
            # forms, and Blue-2's stop candle is the A source. Open/undecided S
            # windows never grant this preemption.
            blue_1_source = getattr(zone, "blue_1_source_time", None)
            blue_2_source = getattr(zone, "blue_2_source_time", None)
            blue_1_stop = getattr(zone, "blue_1_stop_time", None)
            blue_2_stop = getattr(zone, "blue_2_stop_time", None)
            source_time = getattr(zone, "source_time", None)
            if (
                end is not None
                and blue_1_source is not None
                and blue_2_source is not None
                and blue_1_stop is not None
                and blue_2_stop is not None
                and source_time is not None
                and start < blue_1_source
                and blue_1_stop < blue_2_source
                and source_time == blue_2_stop
                and self._a_pair_is_reset_reset(zone)
            ):
                return False
            return True
        return False

    def _a_pair_is_reset_reset(self, zone: object) -> bool:
        """Whether both Blue Lines that define A are Reset Blues."""
        first = int(getattr(zone, "blue_1_ordinal", 0)) - 1
        second = int(getattr(zone, "blue_2_ordinal", 0)) - 1
        if not (0 <= first < len(self.trend_blue_lines)):
            return False
        if not (0 <= second < len(self.trend_blue_lines)):
            return False
        return (
            str(getattr(self.trend_blue_lines[first], "kind", "")) == "reset"
            and str(getattr(self.trend_blue_lines[second], "kind", "")) == "reset"
        )

    @property
    def eligible_a_zones(self) -> list[object]:
        """A candidates outside stopped-parent S ownership, before rendering."""
        return [zone for zone in self.a_zones if not self._a_owned_by_s(zone)]

    def _candidate_timing(
        self,
        a_stop_index: int,
        order: object,
        order_confirmation_time: datetime,
        a_stop_event_time: datetime | None = None,
    ) -> str:
        """Resolve pre/post-Order ownership without stealing Advanced S.

        Existing nested same-direction geometry owns the Advanced branch and
        keeps the established price-geometry classification.  Otherwise, when
        that legacy classification says ``after``, exact event chronology may
        prove that the A-stop candidate actually formed strictly before the
        opposite Order First.  Equality remains after-Order.
        """
        stop_extreme = self._trend_extreme(self.candles[a_stop_index])
        boundary = as_decimal(
            getattr(
                order,
                "box_bottom" if self.direction == "bullish" else "box_top",
            )
        )
        if self.direction == "bullish":
            legacy = "after" if boundary <= stop_extreme else "before"
        else:
            legacy = "after" if boundary >= stop_extreme else "before"
        if legacy == "before":
            return legacy

        # Do not let Simple pre-Order chronology steal an already-valid
        # Advanced owner.  This preserves accepted Advanced S provenance.
        if self._nested_trend_reaction(order, order_confirmation_time) is not None:
            return legacy

        if a_stop_event_time is None:
            a_stop_event_time = self.candle_times[a_stop_index]
        candidate = self._candidate_before_order(
            a_stop_index, order, a_stop_event_time=a_stop_event_time
        )
        candidate_event = self._candidate_event_time(
            candidate[0], candidate[2], a_stop_event_time
        )
        order_first_time = self.candle_times[int(getattr(order, "first_idx"))]
        return "before" if candidate_event < order_first_time else "after"

    def _candidate_before_order(
        self,
        a_stop_index: int,
        order: object,
        a_stop_event_time: datetime | None = None,
    ) -> tuple[int, datetime, Decimal]:
        """Use the lowest/highest leg extreme from A-stop through order First."""
        if a_stop_event_time is None:
            a_stop_event_time = self.candle_times[a_stop_index]
        first_index = int(getattr(order, "first_idx"))
        candidate = self._candidate_source(a_stop_index, first_index)
        stop_candle_end = self.candle_times[a_stop_index] + self.timeframe
        eligible_stop_remainder = self._lower_window(
            a_stop_event_time, stop_candle_end
        )
        if not eligible_stop_remainder:
            return candidate
        source = eligible_stop_remainder[0]
        value = self._trend_extreme(source)
        for item in eligible_stop_remainder[1:]:
            item_value = self._trend_extreme(item)
            better = (
                item_value < value
                if self.direction == "bullish"
                else item_value > value
            )
            if better:
                source = item
                value = item_value
        later_candidate = (
            self._candidate_source(a_stop_index + 1, first_index)
            if first_index > a_stop_index
            else None
        )
        if later_candidate is not None:
            better = (
                later_candidate[2] < value
                if self.direction == "bullish"
                else later_candidate[2] > value
            )
            if better:
                return later_candidate
        return a_stop_index, self.candle_times[a_stop_index], value

    def _candidate_event_time(
        self,
        source_index: int,
        level: Decimal,
        not_before: datetime,
    ) -> datetime:
        """Return the first lower-timeframe event that forms the candidate."""
        source_time = self.candle_times[source_index]
        for item in self._lower_window(
            max(source_time, not_before), source_time + self.timeframe
        ):
            if self._trend_extreme(item) == level:
                return getattr(item, "timestamp")
        return max(source_time, not_before)

    def candidate_event_time(
        self, source_index: int, price: Decimal, fallback: datetime
    ) -> datetime:
        """Public lifecycle API for exact S candidate provenance."""
        return self._candidate_event_time(source_index, price, fallback)


    def _blue_formation_time(self, line: object) -> datetime:
        explicit = getattr(line, "formation_time", None)
        if explicit is not None:
            return explicit
        source_index = int(getattr(line, "source_index"))
        source_time = getattr(self.candles[source_index], "timestamp")
        if str(getattr(line, "kind")) != "reset":
            reaction_number = int(getattr(line, "reaction_number"))
            if 1 <= reaction_number <= len(self.trend_reactions):
                return self._reaction_confirmation_time(
                    self.trend_reactions[reaction_number - 1], self.direction
                )
            return source_time
        broken_level = getattr(line, "broken_level", None)
        if broken_level is None:
            return source_time
        end = source_time + self.timeframe
        for item in self._lower_window(source_time, end):
            value = as_decimal(
                getattr(item, "low" if self.direction == "bullish" else "high")
            )
            crossed = (
                value < as_decimal(broken_level)
                if self.direction == "bullish"
                else value > as_decimal(broken_level)
            )
            if crossed:
                return getattr(item, "timestamp")
        return source_time

    def _candidate_cross_has_blue(
        self,
        reaction_number: int,
        event_time: datetime,
    ) -> bool:
        """Return whether the candidate cross has its aligned Reset Blue.

        The Reset Blue belongs to the same-direction reaction, but it does
        not have to be drawn on the candidate candle or on the candle that
        crosses the candidate.  Its exact formation event only needs to be
        no later than the candidate crossing event.
        """
        if reaction_number < 1 or reaction_number > len(self.trend_reactions):
            return False
        formation_time = self._reset_blue_formation_by_reaction.get(reaction_number)
        return formation_time is not None and formation_time <= event_time

    def _has_ordinary_trend_reaction(
        self, behavior_start: datetime, event_time: datetime
    ) -> bool:
        """Return whether ordinary aligned geometry completed in the leg."""
        position = bisect_right(self._trend_confirmation_times_sorted, behavior_start)
        return (
            position < len(self._trend_confirmation_times_sorted)
            and self._trend_confirmation_times_sorted[position] <= event_time
        )


    def _order_stop(
        self, order_number: int, reaction: object
    ) -> tuple[Decimal, int, datetime]:
        return self.chronology.canonical_order_stop(
            self.order_direction,
            order_number,
            reaction,
            self.opposite_reactions,
            start_index=self.start_index,
        )

    def _candidate_crossed(self, candle: object, level: Decimal) -> bool:
        value = self._trend_extreme(candle)
        return self._a_stopped(value, level)

    def _order_stop_crossed(self, candle: object, level: Decimal) -> bool:
        if self.order_direction == "bearish":
            return as_decimal(getattr(candle, "high")) > level
        return as_decimal(getattr(candle, "low")) < level

    def _decision(
        self,
        candidate_level: Decimal,
        order_stop_level: Decimal,
        start: datetime,
        trend_reaction_number: int,
        behavior_start: datetime,
        candidate_start: datetime | None = None,
        fallback_on_unqualified_cross: bool = False,
    ) -> tuple[str, int, datetime, datetime] | None:
        scan_start = max(start, self.range_start)
        left = bisect_left(self.lower_times, scan_start)
        right = bisect_left(self.lower_times, self.range_end)
        if right > left:
            # Order stop is independent of candidate qualification.
            order_position = (
                self.lower_index.first_greater(left, right, order_stop_level)
                if self.order_direction == "bearish"
                else self.lower_index.first_less(left, right, order_stop_level)
            )

            candidate_gate = max(scan_start, candidate_start or scan_start)
            if fallback_on_unqualified_cross:
                qualified_start = candidate_gate
                candidate_family = "fallback"
            else:
                blue_time = (
                    self._reset_blue_formation_by_reaction.get(trend_reaction_number)
                    if 1 <= trend_reaction_number <= len(self.trend_reactions)
                    else None
                )
                trend_position = bisect_right(
                    self._trend_confirmation_times_sorted, behavior_start
                )
                trend_time = (
                    self._trend_confirmation_times_sorted[trend_position]
                    if trend_position < len(self._trend_confirmation_times_sorted)
                    else None
                )
                qualifiers = [
                    value for value in (blue_time, trend_time) if value is not None
                ]
                if not qualifiers:
                    candidate_position = None
                else:
                    qualified_start = max(candidate_gate, min(qualifiers))
                    candidate_family = "blue"
                    candidate_left = bisect_left(self.lower_times, qualified_start, left, right)
                    candidate_position = (
                        self.lower_index.first_less(
                            candidate_left, right, candidate_level
                        )
                        if self.direction == "bullish"
                        else self.lower_index.first_greater(
                            candidate_left, right, candidate_level
                        )
                    )
            if fallback_on_unqualified_cross:
                candidate_left = bisect_left(self.lower_times, qualified_start, left, right)
                candidate_position = (
                    self.lower_index.first_less(candidate_left, right, candidate_level)
                    if self.direction == "bullish"
                    else self.lower_index.first_greater(candidate_left, right, candidate_level)
                )

            if order_position is None and candidate_position is None:
                return None
            if order_position is not None and candidate_position == order_position:
                return None
            if order_position is not None and (
                candidate_position is None or order_position < candidate_position
            ):
                event_time = self.lower_times[order_position]
                index = self._main_index(event_time)
                return (
                    "red", index, getattr(self.candles[index], "timestamp"), event_time
                )
            assert candidate_position is not None
            event_time = self.lower_times[candidate_position]
            if fallback_on_unqualified_cross and (
                self._candidate_cross_has_blue(trend_reaction_number, event_time)
                or self._has_ordinary_trend_reaction(behavior_start, event_time)
            ):
                candidate_family = "blue"
            index = self._main_index(event_time)
            return (
                candidate_family,
                index,
                getattr(self.candles[index], "timestamp"),
                event_time,
            )

        # Preserve the established no-lower-data main-candle fallback exactly.
        start_index = max(
            self.start_index, bisect_right(self.candle_times, start) - 1
        )
        for item in self.candles[start_index : self.end_index + 1]:
            event_time = getattr(item, "timestamp")
            candidate_cross = (
                self._candidate_crossed(item, candidate_level)
                and (candidate_start is None or event_time >= candidate_start)
            )
            order_cross = self._order_stop_crossed(item, order_stop_level)
            if candidate_cross and order_cross:
                return None
            if order_cross:
                return (
                    "red", int(getattr(item, "index")), event_time, event_time
                )
            if (
                candidate_cross
                and (
                    self._candidate_cross_has_blue(trend_reaction_number, event_time)
                    or self._has_ordinary_trend_reaction(behavior_start, event_time)
                )
            ):
                return (
                    "blue", int(getattr(item, "index")), event_time, event_time
                )
            if candidate_cross and fallback_on_unqualified_cross:
                return (
                    "fallback", int(getattr(item, "index")), event_time, event_time
                )
        return None


    def _build_type3_zone(
        self,
        zone: object,
        a_ordinal: int,
        a_price: Decimal,
        a_stop: tuple[int, datetime, datetime],
        type3: tuple[int, datetime, Decimal, int, datetime, int, datetime, datetime],
    ) -> SZone:
        """Build the order-free Blue Type-3 continuation for one stopped A."""
        a_stop_index, a_stop_time, a_stop_event_time = a_stop
        (
            source_index,
            source_time,
            price,
            decision_index,
            decision_time,
            reset_reaction_number,
            reset_time,
            decision_event_time,
        ) = type3
        return SZone(
            direction=self.direction,
            color="blue",
            formation_type="type3",
            a_ordinal=a_ordinal,
            a_source_index=int(getattr(zone, "source_index")),
            a_source_time=getattr(zone, "source_time"),
            a_price=a_price,
            a_stop_index=a_stop_index,
            a_stop_time=a_stop_time,
            a_stop_event_time=a_stop_event_time,
            order_direction=None,
            order_reaction_number=None,
            order_mode=None,
            order_first_index=None,
            order_first_time=None,
            order_break_index=None,
            order_break_time=None,
            order_confirmation_time=None,
            order_box_top=None,
            order_box_top_source_index=None,
            order_box_top_source_time=None,
            order_box_bottom=None,
            order_box_bottom_source_index=None,
            order_box_bottom_source_time=None,
            order_stop_level=None,
            order_stop_source_index=None,
            order_stop_source_time=None,
            reset_reaction_number=reset_reaction_number,
            reset_time=reset_time,
            source_index=source_index,
            source_time=source_time,
            price=price,
            decision_index=decision_index,
            decision_time=decision_time,
            decision_event_time=decision_event_time,
        )

    def _build_order_backed_zone(
        self,
        zone: object,
        a_ordinal: int,
        a_price: Decimal,
        a_stop: tuple[int, datetime, datetime],
        order_match: tuple[int, object, datetime],
    ) -> SZone | None:
        """Resolve Simple/Advanced S ownership after a stopped A finds an Order."""
        a_stop_index, a_stop_time, a_stop_event_time = a_stop
        order_number, order, order_confirmation_time = order_match
        order_stop_level, order_stop_source_index, order_stop_source_time = (
            self._order_stop(order_number, order)
        )
        candidate_timing = self._candidate_timing(
            a_stop_index, order, order_confirmation_time, a_stop_event_time
        )
        pre_order_candidate = (
            self._candidate_before_order(
                a_stop_index,
                order,
                a_stop_event_time=a_stop_event_time,
            )
            if candidate_timing == "before"
            else None
        )

        decision_behavior_start = a_stop_event_time
        decision = None
        use_pre_order_candidate = False
        if pre_order_candidate is not None:
            formation_type = "simple"
            source_index, source_time, price = pre_order_candidate
            red_source = pre_order_candidate
            trend_reaction_number = 0
            candidate_event_time = self._candidate_event_time(
                source_index, price, a_stop_event_time
            )
            decision_behavior_start = candidate_event_time
            decision = self._decision(
                price,
                order_stop_level,
                order_confirmation_time,
                trend_reaction_number,
                decision_behavior_start,
                candidate_event_time,
                fallback_on_unqualified_cross=True,
            )
            if decision is None:
                return None
            if decision[0] != "fallback":
                use_pre_order_candidate = True
            else:
                decision = None

        advanced_blue = False
        if not use_pre_order_candidate:
            decision_behavior_start = a_stop_event_time
            nested_match = self._nested_trend_reaction(
                order, order_confirmation_time
            )
            advanced_blue = nested_match is not None

        if not use_pre_order_candidate and advanced_blue:
            formation_type = "advanced"
            red_source = None
            trend_reaction_number, _, trend_confirmation_time = nested_match
            source_index = int(
                getattr(
                    order,
                    "box_bottom_source_idx"
                    if self.direction == "bullish"
                    else "box_top_source_idx",
                )
            )
            source_time = getattr(self.candles[source_index], "timestamp")
            price = self._trend_extreme(self.candles[source_index])
            decision_candidate_start = trend_confirmation_time
        elif not use_pre_order_candidate:
            formation_type = "simple"
            trend_match = self._first_trend_reaction_after_order(
                order_confirmation_time
            )
            if trend_match is None:
                return None
            trend_reaction_number, trend_reaction, trend_confirmation_time = (
                trend_match
            )
            source_index, source_time, price = self._simple_candidate(
                order, trend_reaction
            )
            red_source = (
                pre_order_candidate
                if pre_order_candidate is not None
                else self._candidate_after_order(
                    order_confirmation_time, trend_reaction
                )
            )
            decision_candidate_start = trend_confirmation_time

        if decision is None:
            decision = self._decision(
                price,
                order_stop_level,
                order_confirmation_time,
                trend_reaction_number,
                decision_behavior_start,
                decision_candidate_start,
            )
        if decision is None:
            return None

        color, decision_index, decision_time, decision_event_time = decision
        order_break_index = int(getattr(order, "break_idx"))
        if color == "red":
            if use_pre_order_candidate and red_source is not None:
                source_index, source_time, price = red_source
            else:
                source_index, source_time, price = self._candidate_source(
                    order_break_index, decision_index
                )

        order_first_index = int(getattr(order, "first_idx"))
        box_top_source_index = int(getattr(order, "box_top_source_idx"))
        box_bottom_source_index = int(getattr(order, "box_bottom_source_idx"))
        return SZone(
            direction=self.direction,
            color=color,
            formation_type=formation_type,
            a_ordinal=a_ordinal,
            a_source_index=int(getattr(zone, "source_index")),
            a_source_time=getattr(zone, "source_time"),
            a_price=a_price,
            a_stop_index=a_stop_index,
            a_stop_time=a_stop_time,
            a_stop_event_time=a_stop_event_time,
            order_direction=self.order_direction,
            order_reaction_number=order_number,
            order_mode=str(getattr(order, "mode")),
            order_first_index=order_first_index,
            order_first_time=getattr(
                self.candles[order_first_index], "timestamp"
            ),
            order_break_index=order_break_index,
            order_break_time=getattr(
                self.candles[order_break_index], "timestamp"
            ),
            order_confirmation_time=order_confirmation_time,
            order_box_top=as_decimal(getattr(order, "box_top")),
            order_box_top_source_index=box_top_source_index,
            order_box_top_source_time=getattr(
                self.candles[box_top_source_index], "timestamp"
            ),
            order_box_bottom=as_decimal(getattr(order, "box_bottom")),
            order_box_bottom_source_index=box_bottom_source_index,
            order_box_bottom_source_time=getattr(
                self.candles[box_bottom_source_index], "timestamp"
            ),
            order_stop_level=order_stop_level,
            order_stop_source_index=order_stop_source_index,
            order_stop_source_time=order_stop_source_time,
            reset_reaction_number=None,
            reset_time=None,
            source_index=source_index,
            source_time=source_time,
            price=price,
            decision_index=decision_index,
            decision_time=decision_time,
            decision_event_time=decision_event_time,
        )

    def detect(self) -> list[SZone]:
        output: list[SZone] = []
        self.a_ownership_windows.clear()
        self.order_audit.clear()
        for zone in self.a_zones:
            self._audit_stopped_a(zone)

        cycle_start_time = self.range_start
        for zone_offset, zone in enumerate(self.a_zones):
            a_ordinal = zone_offset + 1
            if self._a_owned_by_s(zone):
                continue
            source_time = getattr(zone, "source_time")
            if source_time < cycle_start_time or (
                source_time == cycle_start_time and output
            ):
                continue

            next_a_confirmation = (
                self._a_confirmation_time(self.a_zones[zone_offset + 1])
                if zone_offset + 1 < len(self.a_zones)
                else None
            )
            a_price = as_decimal(getattr(zone, "price"))
            a_stop = self._first_a_stop(a_price, self._a_confirmation_time(zone))
            if a_stop is None:
                continue
            _, _, a_stop_event_time = a_stop
            order_match = self._first_order_after(a_stop_event_time)
            if (
                next_a_confirmation is not None
                and a_stop_event_time >= next_a_confirmation
            ):
                continue

            self.a_ownership_windows.append((a_stop_event_time, None))
            no_order_deadline = (
                order_match[2] if order_match is not None else self.range_end
            )
            type3 = self._first_type3(a_stop_event_time, no_order_deadline)
            type4 = self._first_type4(a_stop, no_order_deadline)
            # Type-3 and Type-4 are independent order-free S-Blue routes.
            # Exact decision chronology owns the handoff; preserve established
            # Type-3 precedence only on a true exact-event tie.
            if type3 is not None and (type4 is None or type3[-1] <= type4[-1]):
                s_zone = self._build_type3_zone(
                    zone, a_ordinal, a_price, a_stop, type3
                )
            elif type4 is not None:
                s_zone = self._build_type4_zone(
                    zone, a_ordinal, a_price, a_stop, type4
                )
            elif order_match is not None:
                s_zone = self._resolved_order_backed_zone(
                    zone, a_ordinal, a_price, a_stop, order_match
                )
                if s_zone is None:
                    continue
            else:
                continue

            output.append(s_zone)
            cycle_start_time = s_zone.source_time
            self.a_ownership_windows[-1] = (
                a_stop_event_time,
                max(
                    a_stop_event_time,
                    s_zone.decision_event_time + timedelta(microseconds=1),
                ),
            )

        return sorted(
            output,
            key=lambda item: (item.source_time, item.decision_event_time),
        )


    def _shared_order_stop_cross(
        self, confirmation: datetime, level: Decimal
    ) -> tuple[int, datetime, datetime] | None:
        """Return the first strict stop of an accepted Order after confirmation."""
        scan_start = max(confirmation, self.range_start)
        left = bisect_left(self.lower_times, scan_start)
        right = bisect_left(self.lower_times, self.range_end)
        if right > left and self.lower_index is not None:
            position = (
                self.lower_index.first_greater(left, right, level)
                if self.order_direction == "bearish"
                else self.lower_index.first_less(left, right, level)
            )
            if position is None:
                return None
            event_time = self.lower_times[position]
            index = self._main_index(event_time)
            return index, getattr(self.candles[index], "timestamp"), event_time

        for item in self.lower[left:right]:
            if self._order_stop_crossed(item, level):
                event_time = getattr(item, "timestamp")
                index = self._main_index(event_time)
                return index, getattr(self.candles[index], "timestamp"), event_time
        return None

    def reconcile_shared_order_stops(
        self,
        zones: Sequence[SZone],
        order_entries: Sequence[dict[str, object]],
    ) -> list[SZone]:
        """Resolve open S candidates with any accepted physical Order stop.

        Order confirmation is parent-neutral.  The decisive Order does not have
        to originate from the A/S candidate currently being resolved.  Once a
        physical Order is calculation-accepted, it may decide an S candidate if
        the Order is live in that candidate window and its exact strict stop is
        after the frozen S source but before the candidate's current strict
        decision event.  Creation provenance remains attached to the Order and
        is never rewritten to the S candidate.

        This rule is direction invariant.  The strict Order stop itself is
        resolved by the shared mirrored lower-timeframe chronology.
        """
        deduped: dict[tuple[int, int], dict[str, object]] = {}
        for entry in order_entries:
            reaction = entry.get("reaction")
            if reaction is None:
                continue
            identity = (
                int(getattr(reaction, "first_idx")),
                int(getattr(reaction, "break_idx")),
            )
            current = deduped.get(identity)
            # Prefer the richer accepted E-audit form when it already carries
            # an exact stop crossing.  Physical identity, not parent identity,
            # is authoritative.
            if current is None or (
                current.get("stop_cross") is None
                and entry.get("stop_cross") is not None
            ):
                deduped[identity] = entry

        # Performance implementation detail: physical Order stop chronology is
        # immutable for this reconciliation pass.  The legacy implementation
        # recomputed the same strict crossing once per (S, Order) pair.  Build
        # each exact candidate once, preserve the authoritative winner key
        # (crossEvent, confirmation, FirstIndex, BreakIndex), then bisect by the
        # frozen S decision window.  This changes only lookup complexity.
        shared_candidates: list[tuple[
            datetime, datetime, int, int, dict[str, object],
            tuple[int, datetime, datetime]
        ]] = []
        for identity, entry in deduped.items():
            reaction = entry["reaction"]
            first_index = int(getattr(reaction, "first_idx"))
            confirmation = entry.get("confirmation_time")
            if not isinstance(confirmation, datetime):
                continue
            stop_level = as_decimal(entry["stop_level"])
            crossed = entry.get("stop_cross")
            if not (
                isinstance(crossed, tuple)
                and len(crossed) >= 3
                and isinstance(crossed[2], datetime)
            ):
                crossed = self._shared_order_stop_cross(confirmation, stop_level)
            if crossed is None or not confirmation < crossed[2]:
                continue
            shared_candidates.append((
                crossed[2], confirmation, first_index, identity[1], entry, crossed
            ))
        shared_candidates.sort(key=lambda item: item[:4])
        shared_cross_times = [item[0] for item in shared_candidates]

        output: list[SZone] = []
        for zone in zones:
            left = bisect_left(shared_cross_times, zone.source_time)
            winner = None
            if left < len(shared_candidates):
                candidate = shared_candidates[left]
                if candidate[0] < zone.decision_event_time:
                    winner = candidate

            if winner is None:
                output.append(zone)
                continue

            _, _, _, _, entry, crossed = winner
            reaction = entry["reaction"]
            first_index = int(getattr(reaction, "first_idx"))
            break_index = int(getattr(reaction, "break_idx"))
            top_source = int(getattr(reaction, "box_top_source_idx"))
            bottom_source = int(getattr(reaction, "box_bottom_source_idx"))
            output.append(replace(
                zone,
                color="red",
                order_reaction_number=int(entry.get("reaction_number", 0)),
                order_mode=str(getattr(reaction, "mode")),
                order_first_index=first_index,
                order_first_time=getattr(self.candles[first_index], "timestamp"),
                order_break_index=break_index,
                order_break_time=getattr(self.candles[break_index], "timestamp"),
                order_confirmation_time=entry["confirmation_time"],
                order_box_top=as_decimal(getattr(reaction, "box_top")),
                order_box_top_source_index=top_source,
                order_box_top_source_time=getattr(self.candles[top_source], "timestamp"),
                order_box_bottom=as_decimal(getattr(reaction, "box_bottom")),
                order_box_bottom_source_index=bottom_source,
                order_box_bottom_source_time=getattr(self.candles[bottom_source], "timestamp"),
                order_stop_level=as_decimal(entry["stop_level"]),
                order_stop_source_index=int(entry["stop_source_index"]),
                order_stop_source_time=entry["stop_source_time"],
                reset_reaction_number=None,
                reset_time=None,
                decision_index=int(crossed[0]),
                decision_time=crossed[1],
                decision_event_time=crossed[2],
            ))
        return output



def detect_s_zones(
    direction: str,
    trend_reactions: Sequence[object],
    opposite_reactions: Sequence[object],
    trend_blue_lines: Sequence[object],
    a_zones: Sequence[object],
    chronology: object,
    start_index: int | None = None,
    end_index: int | None = None,
    opposite_resets: Sequence[object] = (),
    initial_order_geometry: Callable[[int, datetime, int], object | None] | None = None,
) -> list[SZone]:
    return SZoneDetector(
        direction,
        trend_reactions,
        opposite_reactions,
        trend_blue_lines,
        a_zones,
        chronology,
        start_index,
        end_index,
        opposite_resets,
        initial_order_geometry,
    ).detect()
```
<!-- SOURCE_FILE_END:s_zone_detector.py -->
### 26.5 `e_zone_detector.py`

- Source version: `6.13.0`
- Last modified declared by module: `2026-09-22 00:35:00 +03:30`
- Lines: `2876`
- Role: Recursive E formation, parent-stop/Order_A/Order_B/accepted-live/carried-live routes, E reconciliation, and accepted Order provenance.
- Optional integrity SHA-256: `6e32b947aa1b4e1e6b986f26ee9a464542f320dc6a207ece1e8fce54407d0369`

<!-- SOURCE_FILE_BEGIN:e_zone_detector.py:SHA256=6e32b947aa1b4e1e6b986f26ee9a464542f320dc6a207ece1e8fce54407d0369 -->
```python
"""Recursive E-zone and Order calculation from authoritative S/Reaction state.

Owns parent-stop, carried-live, accepted-live, and Reset-leg Order discovery;
recursive E chains; accepted Order causes; and E family/number reconciliation.
Cross-stage public visibility and StopAll grouping are delegated to the lifecycle
engine.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Callable, Sequence

from core_utils import as_decimal, order_identity, reaction_identity
from direction_policy import policy_for


E_ZONE_VERSION = "6.13.0"
E_ZONE_LAST_MODIFIED = "2026-09-22 00:35:00 +03:30"


@dataclass(frozen=True, slots=True)
class EZone:
    direction: str
    family: str
    number: int
    parent_type: str
    parent_source_index: int
    parent_source_time: datetime
    parent_price: Decimal
    parent_stop_index: int
    parent_stop_time: datetime
    parent_stop_event_time: datetime
    order_direction: str
    order_reaction_number: int
    order_mode: str
    order_causes: tuple[str, ...]
    order_parent_stop_cause_time: datetime | None
    order_reset_leg_reset_time: datetime | None
    order_reset_leg_break_time: datetime | None
    order_first_index: int
    order_first_time: datetime
    order_break_index: int
    order_break_time: datetime
    order_confirmation_time: datetime
    order_box_top: Decimal
    order_box_top_source_index: int
    order_box_top_source_time: datetime
    order_box_bottom: Decimal
    order_box_bottom_source_index: int
    order_box_bottom_source_time: datetime
    order_stop_level: Decimal
    order_stop_source_index: int
    order_stop_source_time: datetime
    source_index: int
    source_time: datetime
    price: Decimal
    decision_index: int
    decision_time: datetime
    decision_event_time: datetime


OrderMatch = tuple[
    int, object, datetime, Decimal, int, datetime,
    tuple[int, datetime, datetime] | None, tuple[str, ...],
    datetime | None, datetime | None, datetime | None,
]


@dataclass(frozen=True, slots=True)
class OrderBFormation:
    """One complete reset-leg Order_B setup under the canonical mirror rule."""

    reset_time: datetime
    reset_index: int
    owner_first_index: int
    owner_break_index: int
    trigger_level: Decimal
    trigger_source_index: int
    trigger_source_time: datetime
    strict_break_index: int
    strict_break_time: datetime
    strict_break_event_time: datetime
    opposite_extreme: Decimal
    opposite_extreme_source_index: int
    opposite_extreme_source_time: datetime
    evidence_first_index: int
    evidence_break_index: int
    order_reaction_number: int
    order_reaction: object
    order_confirmation_time: datetime


class EZoneDetector:
    def __init__(
        self,
        direction: str,
        trend_reactions: Sequence[object],
        opposite_reactions: Sequence[object],
        s_zones: Sequence[object],
        trend_resets: Sequence[object],
        opposite_resets: Sequence[object],
        chronology: object,
        start_index: int = 0,
        end_index: int | None = None,
        geometry_finder: Callable[[str, int, int], object | None] | None = None,
        direct_geometry_finder: Callable[
            [str, int, int, datetime], object | None
        ] | None = None,
        blocked_order_first_times: set[datetime] | None = None,
        initial_order_audit: dict[tuple[int, int], dict[str, object]] | None = None,
        sequence_resets: dict[datetime, int] | None = None,
        sequence_priority: Callable[[str, str], int] | None = None,
        invalid_s_root_identities: set[tuple[datetime, int]] | None = None,
    ) -> None:
        if direction not in {"bullish", "bearish"}:
            raise ValueError("Direction must be 'bullish' or 'bearish'.")
        self.direction = direction
        self.policy = policy_for(direction)
        if sequence_priority is None:
            raise ValueError("EZoneDetector requires the shared sequence-priority resolver.")
        self.sequence_priority = sequence_priority
        self.invalid_s_root_identities = set(invalid_s_root_identities or set())
        self.sequence_resets = dict(sequence_resets or {})
        self._sequence_reset_times = sorted(self.sequence_resets)
        self.order_direction = chronology.opposite_direction(direction)
        self.chronology = chronology
        self.trend_reactions = list(trend_reactions)
        self.opposite_reactions = list(opposite_reactions)
        self.s_zones = sorted(
            s_zones,
            key=lambda item: (
                getattr(item, "source_time"),
                int(getattr(item, "source_index")),
            ),
        )
        red_s_events = [
            (getattr(item, "source_time"), getattr(item, "decision_event_time"))
            for item in self.s_zones
            if str(getattr(item, "color")) == "red"
        ]
        self._red_s_source_times = [item[0] for item in red_s_events]
        self._red_s_suffix_min_decision: list[datetime] = []
        suffix_min: datetime | None = None
        for _, decision_time in reversed(red_s_events):
            if suffix_min is None or decision_time < suffix_min:
                suffix_min = decision_time
            self._red_s_suffix_min_decision.append(suffix_min)
        self._red_s_suffix_min_decision.reverse()
        self.trend_resets = sorted(trend_resets, key=self._reset_time)
        self.opposite_resets = sorted(opposite_resets, key=self._reset_time)
        self.candles = chronology.candles
        self.lower = chronology.seconds
        self.lower_times = chronology.second_times
        self.lower_index = chronology.lower_index
        self.timeframe = chronology.timeframe
        self.times = chronology.times
        self.start_index = int(start_index)
        self.end_index = len(self.candles) - 1 if end_index is None else int(end_index)
        self.range_start = self.times[self.start_index]
        self.range_end = self.times[self.end_index] + self.timeframe
        self.geometry_finder = geometry_finder
        self.direct_geometry_finder = direct_geometry_finder or geometry_finder
        self.blocked_order_first_times = blocked_order_first_times or set()
        self.initial_order_audit = initial_order_audit or {}
        self._cross_order_cache: dict[
            tuple[datetime, Decimal], tuple[int, datetime, datetime] | None
        ] = {}
        # Performance implementation detail: canonical opposite Reactions are
        # immutable for one run, and their canonical Order stop depends only
        # on that canonical reaction number/geometry plus immutable chronology.
        # Cache only exact canonical objects; bounded/noncanonical Order_A
        # geometry intentionally stays on the authoritative uncached path.
        self._canonical_order_stop_cache: dict[
            int, tuple[Decimal, int, datetime]
        ] = {}
        # Performance implementation detail: the initial A-owned OrderAudit
        # ledger is immutable for one detector run. Materialize its expensive
        # strict-stop lookup once, then keep both chronological indexes and
        # the original physical identity semantics.
        self._initial_order_records_cache: tuple[tuple[
            datetime, datetime, int, object, Decimal, int, datetime,
            tuple[int, datetime, datetime] | None,
        ], ...] | None = None
        self._initial_order_first_times: list[datetime] | None = None
        self._initial_order_confirmation_times: list[datetime] | None = None
        self._initial_order_confirmation_records: tuple[tuple[
            datetime, datetime, int, object, Decimal, int, datetime,
            tuple[int, datetime, datetime] | None,
        ], ...] = ()
        self._initial_orders_by_first_time: dict[datetime, tuple[tuple[
            datetime, datetime, int, object, Decimal, int, datetime,
            tuple[int, datetime, datetime] | None,
        ], ...]] | None = None
        self._order_b_formations_cache: list[OrderBFormation] | None = None
        self._order_b_confirmation_times: list[datetime] | None = None
        self._order_b_by_identity: dict[
            tuple[int, int], tuple[OrderBFormation, ...]
        ] | None = None
        self._order_b_candidate_records: tuple[
            tuple[datetime, int, int, OrderMatch], ...
        ] | None = None
        self._order_b_candidate_confirmation_times: list[datetime] | None = None
        self._order_candidates_cache: dict[
            tuple[datetime, datetime | None, bool, bool, bool], tuple[OrderMatch, ...]
        ] = {}
        self.order_audit: dict[tuple[int, int], dict[str, object]] = {}
        # Performance implementation detail: ``order_audit`` remains the
        # authoritative accepted ledger and preserves insertion/provenance
        # semantics. This secondary chronology index exists only to avoid a
        # full ledger scan when a parent can use only Orders confirmed after
        # its strict stop.
        self._order_audit_confirmation_index: list[
            tuple[datetime, int, int]
        ] = []
        self._trend_first_times = [
            self._reaction_first_time(item) for item in self.trend_reactions
        ]
        self._trend_confirmations = [
            self._confirmation_for(item, self.direction)
            for item in self.trend_reactions
        ]
        self._opposite_first_times = [
            self._reaction_first_time(item) for item in self.opposite_reactions
        ]
        self._opposite_confirmations = [
            self._confirmation(item) for item in self.opposite_reactions
        ]
        self._trend_by_confirmation = sorted(
            zip(
                self._trend_confirmations,
                self._trend_first_times,
                self.trend_reactions,
            ),
            key=lambda item: item[0],
        )
        self._trend_confirmation_times = [item[0] for item in self._trend_by_confirmation]
        self._trend_by_first_index = {
            int(getattr(item, "first_idx")): item
            for item in self.trend_reactions
        }
        self._trend_reset_events = [
            (self._reset_time(item), item) for item in self.trend_resets
        ]
        self._trend_reset_times = [item[0] for item in self._trend_reset_events]
        self._opposite_reset_times_by_first: dict[int, list[datetime]] = {}
        for reset in self.opposite_resets:
            self._opposite_reset_times_by_first.setdefault(
                int(getattr(reset, "from_first_idx")), []
            ).append(self._reset_time(reset))
        self._opposite_by_first_index = {
            int(getattr(item, "first_idx")): item
            for item in self.opposite_reactions
        }
        # Performance implementation detail: retain the first canonical
        # position for each physical identity. Legacy linear searches used
        # ``next(...)``, so first-win semantics are preserved intentionally.
        self._opposite_identity_position: dict[tuple[int, int], int] = {}
        for position, item in enumerate(self.opposite_reactions):
            self._opposite_identity_position.setdefault(
                reaction_identity(item), position
            )
        self.visual_lifecycle_starts: set[datetime] = set()
        # Historical-only E objects that were fully formed but suppressed by
        # a descendant conflict.  They are exposed for presentation only and
        # never participate in lifecycle ownership, StopAll, numbering, or
        # OrderAudit reconstruction.
        self.historical_rescued_zones: list[EZone] = []
        self._consumed_s_evidence: list[tuple[object, tuple[int, datetime]]] = []
        self._last_candidate_zones: list[EZone] = []

    def _reset_time(self, reset: object) -> datetime:
        return self.chronology.reset_time(reset)

    def _main_index(self, value: datetime) -> int:
        return self.chronology.main_index(value, clamp=True)


    def _first_cross_position(
        self, left: int, right: int, level: Decimal, *, less: bool
    ) -> int | None:
        """Return the first strict lower-timeframe crossing in [left, right)."""
        if self.lower_index is not None:
            return (
                self.lower_index.first_less(left, right, level)
                if less
                else self.lower_index.first_greater(left, right, level)
            )
        field = "low" if less else "high"
        for position in range(left, right):
            value = as_decimal(getattr(self.lower[position], field))
            if value < level if less else value > level:
                return position
        return None

    def _stop_value(self, item: object) -> Decimal:
        return as_decimal(getattr(item, self.policy.extreme_attr))


    def _first_parent_stop(
        self, source_time: datetime, level: Decimal
    ) -> tuple[int, datetime] | None:
        left = bisect_left(self.lower_times, max(source_time, self.range_start))
        right = bisect_left(self.lower_times, self.range_end)
        position = self._first_cross_position(
            left, right, level, less=self.direction == "bullish"
        )
        if position is None:
            return None
        event = self.lower_times[position]
        return self._main_index(event), event

    def _confirmation_for(self, reaction: object, direction: str) -> datetime:
        return self.chronology.reaction_confirmation(direction, reaction)

    def _confirmation(self, reaction: object) -> datetime:
        return self._confirmation_for(reaction, self.order_direction)

    def _reaction_first_time(self, reaction: object) -> datetime:
        return getattr(self.candles[int(getattr(reaction, "first_idx"))], "timestamp")

    def _main_range_extreme(
        self,
        start_index: int,
        end_index: int,
        attribute: str,
        *,
        choose_minimum: bool,
    ) -> tuple[Decimal, int, datetime]:
        """Return the first candle owning the requested closed-range extreme."""
        if end_index < start_index:
            raise ValueError("Order_B extreme range ends before it starts.")
        source = self.candles[start_index]
        value = as_decimal(getattr(source, attribute))
        for candle in self.candles[start_index + 1 : end_index + 1]:
            candidate = as_decimal(getattr(candle, attribute))
            better = candidate < value if choose_minimum else candidate > value
            if better:
                source = candle
                value = candidate
        return value, int(getattr(source, "index")), getattr(source, "timestamp")

    def _order_b_reset_leg(
        self, reset: object, reset_time: datetime,
    ) -> tuple[object, Decimal, int, datetime] | None:
        """Return the same-direction Reset owner and its trigger extreme.

        Bearish: from the owner's Breakout candle through the Reset candle,
        inclusive, the minimum Low is the reset-leg floor.
        Bullish: exact mirror, maximum High is the reset-leg ceiling.
        """
        owner = self._trend_by_first_index.get(
            int(getattr(reset, "from_first_idx"))
        )
        if owner is None:
            return None
        break_index = int(getattr(owner, "break_idx"))
        reset_index = int(getattr(reset, "index"))
        if reset_index < break_index:
            return None
        if self.direction == "bearish":
            level, source_index, source_time = self._main_range_extreme(
                break_index, reset_index, "low", choose_minimum=True
            )
        else:
            level, source_index, source_time = self._main_range_extreme(
                break_index, reset_index, "high", choose_minimum=False
            )
        return owner, level, source_index, source_time

    def _order_b_strict_break(
        self, reset_time: datetime, level: Decimal,
    ) -> tuple[int, datetime, datetime] | None:
        """Return the first exact strict break of the reset-leg trigger level.

        Bearish Order_B: Low < reset-leg floor.
        Bullish Order_B: High > reset-leg ceiling.
        """
        left = bisect_left(self.lower_times, max(reset_time, self.range_start))
        right = bisect_left(self.lower_times, self.range_end)
        position = self._first_cross_position(
            left,
            right,
            level,
            less=self.direction == "bearish",
        )
        if position is None:
            return None
        event_time = self.lower_times[position]
        index = self._main_index(event_time)
        return index, self.times[index], event_time

    def _order_b_opposite_extreme(
        self, trigger_source_index: int, strict_break_index: int,
    ) -> tuple[Decimal, int, datetime]:
        """Return the other reset-leg edge on the closed trigger->break range."""
        if self.direction == "bearish":
            return self._main_range_extreme(
                trigger_source_index,
                strict_break_index,
                "high",
                choose_minimum=False,
            )
        return self._main_range_extreme(
            trigger_source_index,
            strict_break_index,
            "low",
            choose_minimum=True,
        )

    def _order_b_geometry_evidence(
        self, trigger_source_index: int, strict_break_index: int,
    ) -> object | None:
        """Return raw opposite Reaction geometry inside the closed leg range.

        Reset validity, lifecycle acceptance, public visibility, and Internal
        status are deliberately ignored for this evidence test.  Geometry
        alone is sufficient, exactly as required by the Order_B contract.
        """
        if self.geometry_finder is None:
            return None
        geometry = self.geometry_finder(
            self.order_direction,
            trigger_source_index,
            strict_break_index,
        )
        if geometry is None:
            return None
        if int(getattr(geometry, "first_idx")) < trigger_source_index:
            return None
        if int(getattr(geometry, "break_idx")) > strict_break_index:
            return None
        return geometry

    def _first_order_b_reaction_after_break(
        self, strict_break_index: int, strict_break_event: datetime,
    ) -> tuple[int, object, datetime] | None:
        """Return the first canonical opposite Reaction after the Order_B gate."""
        gate_time = self.times[strict_break_index]
        position = bisect_left(self._opposite_first_times, gate_time)
        for order_position in range(position, len(self.opposite_reactions)):
            reaction = self.opposite_reactions[order_position]
            first_time = self._opposite_first_times[order_position]
            confirmation = self._opposite_confirmations[order_position]
            if first_time < gate_time:
                continue
            if confirmation <= strict_break_event:
                continue
            return order_position + 1, reaction, confirmation
        return None

    def _build_order_b_formations(self) -> list[OrderBFormation]:
        """Build every Order_B from same-direction Reset-leg geometry.

        Bearish mirror:
          Bearish Reaction Reset -> minimum Low from Breakout..Reset -> first
          strict Low below that floor -> require at least one raw Bullish
          Reaction geometry from the floor candle through the strict-break
          candle, inclusive -> first canonical Bullish Reaction after the gate.

        Bullish is the exact directional mirror using maximum High, strict
        High above it, raw Bearish geometry, and the first canonical Bearish
        Reaction after the gate.
        """
        if self._order_b_formations_cache is not None:
            return self._order_b_formations_cache
        formations: list[OrderBFormation] = []
        for reset_time, reset in self._trend_reset_events:
            leg = self._order_b_reset_leg(reset, reset_time)
            if leg is None:
                continue
            owner, trigger_level, trigger_source_index, trigger_source_time = leg
            strict_break = self._order_b_strict_break(reset_time, trigger_level)
            if strict_break is None:
                continue
            strict_break_index, strict_break_time, strict_break_event = strict_break
            if strict_break_index < trigger_source_index:
                continue
            evidence = self._order_b_geometry_evidence(
                trigger_source_index, strict_break_index
            )
            if evidence is None:
                continue
            order_match = self._first_order_b_reaction_after_break(
                strict_break_index, strict_break_event
            )
            if order_match is None:
                continue
            order_number, order_reaction, order_confirmation = order_match
            opposite_extreme, opposite_source_index, opposite_source_time = (
                self._order_b_opposite_extreme(
                    trigger_source_index, strict_break_index
                )
            )
            formations.append(OrderBFormation(
                reset_time=reset_time,
                reset_index=int(getattr(reset, "index")),
                owner_first_index=int(getattr(owner, "first_idx")),
                owner_break_index=int(getattr(owner, "break_idx")),
                trigger_level=trigger_level,
                trigger_source_index=trigger_source_index,
                trigger_source_time=trigger_source_time,
                strict_break_index=strict_break_index,
                strict_break_time=strict_break_time,
                strict_break_event_time=strict_break_event,
                opposite_extreme=opposite_extreme,
                opposite_extreme_source_index=opposite_source_index,
                opposite_extreme_source_time=opposite_source_time,
                evidence_first_index=int(getattr(evidence, "first_idx")),
                evidence_break_index=int(getattr(evidence, "break_idx")),
                order_reaction_number=order_number,
                order_reaction=order_reaction,
                order_confirmation_time=order_confirmation,
            ))
        formations.sort(key=lambda item: (
            item.order_confirmation_time,
            int(getattr(item.order_reaction, "first_idx")),
            int(getattr(item.order_reaction, "break_idx")),
            item.reset_time,
        ))
        self._order_b_formations_cache = formations
        self._order_b_confirmation_times = [
            item.order_confirmation_time for item in formations
        ]
        by_identity: dict[tuple[int, int], list[OrderBFormation]] = {}
        for item in formations:
            by_identity.setdefault(
                reaction_identity(item.order_reaction), []
            ).append(item)
        self._order_b_by_identity = {
            identity: tuple(items) for identity, items in by_identity.items()
        }

        # Algorithm requirement: several valid Reset-leg origins may map to
        # one physical Order, and the latest valid Reset-leg cause is
        # authoritative. Every origin for one physical canonical Order shares
        # the same reaction number and confirmation time, so collapse that
        # already-established final winner once instead of re-merging duplicate
        # formations inside every parent query.
        latest_by_identity = {
            identity: items[-1]
            for identity, items in self._order_b_by_identity.items()
        }
        candidate_records: list[tuple[datetime, int, int, OrderMatch]] = []
        for identity, item in latest_by_identity.items():
            level, source, source_time = self._order_stop(
                item.order_reaction_number, item.order_reaction
            )
            crossed = self._cross_order(item.order_confirmation_time, level)
            match: OrderMatch = (
                item.order_reaction_number,
                item.order_reaction,
                item.order_confirmation_time,
                level,
                source,
                source_time,
                crossed,
                ("reset-leg",),
                None,
                item.reset_time,
                item.strict_break_event_time,
            )
            candidate_records.append((
                item.order_confirmation_time, identity[0], identity[1], match
            ))
        candidate_records.sort(key=lambda value: value[:3])
        self._order_b_candidate_records = tuple(candidate_records)
        self._order_b_candidate_confirmation_times = [
            item[0] for item in candidate_records
        ]
        return formations

    def _order_b_orders(
        self, start: datetime,
    ) -> list[tuple[int, object, datetime, datetime, datetime]]:
        """Return canonical Order_B Orders whose Reaction forms at/after start."""
        formations = self._build_order_b_formations()
        confirmation_times = self._order_b_confirmation_times or []
        position = bisect_left(confirmation_times, start)
        return [
            (
                item.order_reaction_number,
                item.order_reaction,
                item.order_confirmation_time,
                item.reset_time,
                item.strict_break_event_time,
            )
            for item in formations[position:]
        ]

    def _order_b_candidate_matches(
        self, start: datetime,
    ) -> tuple[tuple[datetime, int, int, OrderMatch], ...]:
        """Return one final Reset-leg candidate per physical Order after start."""
        self._build_order_b_formations()
        records = self._order_b_candidate_records or ()
        times = self._order_b_candidate_confirmation_times or []
        position = bisect_left(times, start)
        return records[position:]

    def _order_b_evidence(
        self, reaction: object, context_start: datetime,
    ) -> tuple[datetime, datetime] | None:
        """Return the latest eligible Order_B cause for one physical Reaction."""
        identity = reaction_identity(reaction)
        self._build_order_b_formations()
        by_identity = self._order_b_by_identity or {}
        evidence = [
            item for item in by_identity.get(identity, ())
            if item.order_confirmation_time >= context_start
        ]
        if not evidence:
            return None
        owner = max(
            evidence,
            key=lambda item: (
                item.reset_time,
                item.strict_break_event_time,
            ),
        )
        return owner.reset_time, owner.strict_break_event_time

    def _replacement_order(
        self,
        owner: object,
        owner_confirmation: datetime,
        owner_stop_event: datetime,
    ) -> tuple[int, object, datetime, datetime] | None:
        """Return the first later Order_B that forms before the owner stops."""
        owner_identity = reaction_identity(owner)
        formations = self._build_order_b_formations()
        confirmation_times = self._order_b_confirmation_times or []
        position = bisect_right(confirmation_times, owner_confirmation)
        for item in formations[position:]:
            if item.order_confirmation_time >= owner_stop_event:
                break
            if reaction_identity(item.order_reaction) == owner_identity:
                continue
            return (
                item.order_reaction_number,
                item.order_reaction,
                item.order_confirmation_time,
                item.reset_time,
            )
        return None


    def _order_stop(
        self, number: int, reaction: object, context_start: datetime | None = None,
    ) -> tuple[Decimal, int, datetime]:
        del context_start  # Provenance never manufactures a context-only stop.
        if (
            1 <= number <= len(self.opposite_reactions)
            and self.opposite_reactions[number - 1] is reaction
        ):
            cached = self._canonical_order_stop_cache.get(number)
            if cached is not None:
                return cached
            result = self.chronology.canonical_order_stop(
                self.order_direction,
                number,
                reaction,
                self.opposite_reactions,
                start_index=self.start_index,
            )
            self._canonical_order_stop_cache[number] = result
            return result
        return self.chronology.canonical_order_stop(
            self.order_direction,
            number,
            reaction,
            self.opposite_reactions,
            start_index=self.start_index,
        )

    def order_stop(
        self, reaction_number: int, reaction: object
    ) -> tuple[Decimal, int, datetime]:
        """Public audit API for canonical Order stop provenance."""
        return self._order_stop(reaction_number, reaction)


    def _first_healthy_direct_geometry(
        self, start: datetime, allow_bounded_continue: bool = False,
    ) -> tuple[int, object, datetime] | None:
        """Return the first healthy geometry after an A/S/E strict stop.

        A candidate completes normally when the active prior reaction is not
        Reset before its confirmation. If that prior reaction is Reset first,
        the search restarts strictly after the Reset candle and the first
        complete geometry owns the new leg.
        """
        if self.direct_geometry_finder is None:
            return None
        # Geometry needs its complete context candle at or after the exact
        # stop event. A First candle that already opened before the lower-time-
        # frame stop cannot be attributed to that stop.
        search_index = self._main_index(start)
        search_event = start
        restarted = False
        while search_index <= self.end_index:
            candidate = self.direct_geometry_finder(
                self.order_direction, search_index, self.end_index, search_event
            )
            if candidate is None:
                return None
            first = self._reaction_first_time(candidate)
            if (
                first in self.blocked_order_first_times
                and first == self.times[self._main_index(start)]
            ):
                search_index = int(getattr(candidate, "first_idx")) + 1
                search_event = first
                continue
            confirmation = self._confirmation_for(
                candidate, self.order_direction
            )
            owner_position = bisect_right(
                self._opposite_confirmations, search_event
            ) - 1
            prior = (
                self.opposite_reactions[owner_position]
                if owner_position >= 0 else None
            )
            reset_before_confirmation = None
            if prior is not None:
                for reset_time in self._opposite_reset_times_by_first.get(
                    int(getattr(prior, "first_idx")), []
                ):
                    if search_event < reset_time <= confirmation:
                        reset_before_confirmation = reset_time
                        break
            if reset_before_confirmation is not None:
                search_index = self._main_index(reset_before_confirmation)
                search_event = reset_before_confirmation
                restarted = True
                continue

            identity = (
                int(getattr(candidate, "first_idx")),
                int(getattr(candidate, "break_idx")),
            )
            canonical_position = self._opposite_identity_position.get(identity)
            if canonical_position is None:
                # Only the S->E parent-stop path may admit a noncanonical
                # bounded Reaction, and only when exact gate chronology proves
                # continuation of the already-open post-Reset leg.
                if (
                    allow_bounded_continue
                    and getattr(candidate, "order_gate_decision", None) == "continue"
                ):
                    return 0, candidate, confirmation
                search_index = int(getattr(candidate, "first_idx")) + 1
                search_event = first
                continue
            candidate = self.opposite_reactions[canonical_position]
            number = canonical_position + 1
            confirmation = self._opposite_confirmations[canonical_position]
            return number, candidate, confirmation
        return None

    def _trend_leg_direct_order(
        self, start: datetime,
    ) -> tuple[int, object, datetime] | None:
        """Return bounded direct Order_A after a newly confirmed trend leg.

        A stopped E may be followed by a fresh same-direction Reaction before
        the next opposite public Reaction exists.  That trend confirmation
        establishes the new forming-leg boundary.  The first bounded opposite
        geometry after that exact confirmation may own direct Order_A when the
        shared gate resolver proves ``continue``.  This is direct
        parent-stop Order_A provenance and is independent of Order_B.
        """
        if self.direct_geometry_finder is None:
            return None
        position = bisect_right(self._trend_confirmation_times, start)
        while position < len(self._trend_by_confirmation):
            confirmation, first_time, trend = self._trend_by_confirmation[position]
            position += 1
            if first_time <= start:
                continue
            if bool(getattr(trend, "behavior_internal", False)):
                continue
            break_index = int(getattr(trend, "break_idx"))
            candidate = self.direct_geometry_finder(
                self.order_direction, break_index, self.end_index, confirmation
            )
            if candidate is None:
                continue
            if getattr(candidate, "order_gate_decision", None) != "continue":
                continue
            candidate_confirmation = self._confirmation_for(
                candidate, self.order_direction
            )
            if self._reaction_first_time(candidate) <= confirmation:
                continue
            identity = (
                int(getattr(candidate, "first_idx")),
                int(getattr(candidate, "break_idx")),
            )
            canonical_position = self._opposite_identity_position.get(identity)
            if canonical_position is not None:
                return (
                    canonical_position + 1,
                    self.opposite_reactions[canonical_position],
                    self._opposite_confirmations[canonical_position],
                )
            return 0, candidate, candidate_confirmation
        return None

    def _direct_parent_stop_order(
        self,
        start: datetime,
        continuous_deadline: datetime | None,
        allow_bounded_continue: bool,
    ) -> tuple[int, object, datetime] | None:
        """Select the direct parent-stop Order without Order_B evidence."""
        gate_time = self.times[self._main_index(start)]
        geometric_direct = self._first_healthy_direct_geometry(
            start, allow_bounded_continue
        )
        direct_position = bisect_left(self._opposite_first_times, gate_time)
        while (
            direct_position < len(self.opposite_reactions)
            and self._opposite_first_times[direct_position]
            in self.blocked_order_first_times
            and self._opposite_first_times[direct_position] == gate_time
        ):
            direct_position += 1

        independent = None
        if direct_position < len(self.opposite_reactions):
            independent = (
                direct_position + 1,
                self.opposite_reactions[direct_position],
                self._opposite_confirmations[direct_position],
            )
        geometric_gate_decision = (
            getattr(geometric_direct[1], "order_gate_decision", None)
            if geometric_direct is not None
            else None
        )
        prefer_geometric = (
            continuous_deadline is not None
            and geometric_direct is not None
            and geometric_gate_decision == "restart"
            and (
                continuous_deadline == self.range_end
                or continuous_deadline < geometric_direct[2]
            )
        )
        independent_cross = None
        if independent is not None:
            independent_level, _, _ = self._order_stop(
                independent[0], independent[1]
            )
            independent_cross = self._cross_order(
                independent[2], independent_level
            )

        direct_pool: list[tuple[int, object, datetime]] = []
        if prefer_geometric:
            direct_pool.append(geometric_direct)
        elif (
            allow_bounded_continue
            and geometric_direct is not None
            and geometric_direct[0] == 0
            and geometric_gate_decision == "continue"
            and (
                independent is None
                or self._reaction_first_time(geometric_direct[1])
                < self._reaction_first_time(independent[1])
            )
        ):
            direct_pool.append(geometric_direct)
        elif (
            geometric_direct is not None
            and independent_cross is None
            and (
                independent is None
                or self._reaction_first_time(geometric_direct[1])
                < self._reaction_first_time(independent[1])
            )
        ):
            direct_pool.append(geometric_direct)
        elif independent is not None:
            direct_pool.append(independent)

        if not direct_pool:
            return None
        return min(
            direct_pool,
            key=lambda item: (self._reaction_first_time(item[1]), item[2]),
        )

    def _merge_order_candidate(
        self,
        by_geometry: dict[tuple[int, int], OrderMatch],
        number: int,
        reaction: object,
        confirmation: datetime,
        cause: str,
        *,
        parent_stop_cause_time: datetime | None = None,
        reset_time: datetime | None = None,
        reset_break: datetime | None = None,
    ) -> OrderMatch:
        """Merge one provenance cause into a single physical Order identity."""
        level, source, source_time = self._order_stop(number, reaction)
        crossed = self._cross_order(confirmation, level)
        key = reaction_identity(reaction)
        existing = by_geometry.get(key)
        existing_causes = existing[7] if existing is not None else ()
        causes = tuple(dict.fromkeys((*existing_causes, cause)))
        if cause == "parent-stop":
            parent_cause = parent_stop_cause_time
            reset_cause_time = existing[9] if existing is not None else None
            reset_cause_break = existing[10] if existing is not None else None
        else:
            parent_cause = existing[8] if existing is not None else None
            reset_cause_time = reset_time
            reset_cause_break = reset_break
        match: OrderMatch = (
            number,
            reaction,
            confirmation,
            level,
            source,
            source_time,
            crossed,
            causes,
            parent_cause,
            reset_cause_time,
            reset_cause_break,
        )
        by_geometry[key] = match
        return match

    def _enforce_single_parent_stop_owner(
        self, by_geometry: dict[tuple[int, int], OrderMatch]
    ) -> None:
        """Keep one physical Order owner for the exact parent-stop cause.

        A single parent stop may open only one physical Order.  When direct
        parent-stop discovery and the E-only fresh-trend route produce
        different identities for the same stop event, the earliest confirmed
        physical Order owns that parent-stop provenance.  A later identity may
        survive only through an independent cause already merged onto it (for
        example Reset-leg); in that case only the duplicate parent-stop cause
        is removed.
        """
        parent_candidates = [
            item for item in by_geometry.values()
            if "parent-stop" in item[7]
        ]
        if len(parent_candidates) <= 1:
            return

        owner = min(
            parent_candidates,
            key=lambda item: (
                item[2],
                int(getattr(item[1], "first_idx")),
                int(getattr(item[1], "break_idx")),
            ),
        )
        owner_identity = reaction_identity(owner[1])
        for identity, item in list(by_geometry.items()):
            if identity == owner_identity or "parent-stop" not in item[7]:
                continue
            remaining_causes = tuple(
                cause for cause in item[7] if cause != "parent-stop"
            )
            if not remaining_causes:
                del by_geometry[identity]
                continue
            by_geometry[identity] = (
                item[0], item[1], item[2], item[3], item[4], item[5], item[6],
                remaining_causes, None, item[9], item[10],
            )

    def order_candidates(
        self,
        start: datetime,
        continuous_deadline: datetime | None = None,
        audit_legacy: bool = False,
        allow_bounded_continue: bool = False,
        allow_trend_leg_continue: bool = False,
    ) -> list[OrderMatch]:
        """Return every valid E-space Order formed before this E decision."""
        cache_key = (
            start,
            continuous_deadline,
            audit_legacy,
            allow_bounded_continue,
            allow_trend_leg_continue,
        )
        cached = self._order_candidates_cache.get(cache_key)
        if cached is not None:
            return list(cached)

        by_geometry: dict[tuple[int, int], OrderMatch] = {}
        direct = self._direct_parent_stop_order(
            start, continuous_deadline, allow_bounded_continue
        )
        if direct is not None:
            self._merge_order_candidate(
                by_geometry,
                *direct,
                "parent-stop",
                parent_stop_cause_time=start,
            )

        if allow_trend_leg_continue:
            trend_direct = self._trend_leg_direct_order(start)
            if trend_direct is not None:
                self._merge_order_candidate(
                    by_geometry,
                    *trend_direct,
                    "parent-stop",
                    parent_stop_cause_time=start,
                )

        # Order_B is independent Reset-leg provenance.  Calculation and
        # audit use the same canonical formation algorithm; ``audit_legacy``
        # is retained only for public API compatibility.
        for _confirmation, first_index, break_index, order_b_match in (
            self._order_b_candidate_matches(start)
        ):
            identity = (first_index, break_index)
            existing = by_geometry.get(identity)
            if existing is None:
                by_geometry[identity] = order_b_match
                continue
            # Match the legacy `_merge_order_candidate` overwrite semantics:
            # Order_B supplies canonical geometry/stop, while an existing
            # parent-stop cause and its exact provenance remain attached.
            existing_causes = existing[7]
            causes = tuple(dict.fromkeys((*existing_causes, "reset-leg")))
            by_geometry[identity] = (
                order_b_match[0], order_b_match[1], order_b_match[2],
                order_b_match[3], order_b_match[4], order_b_match[5],
                order_b_match[6], causes, existing[8],
                order_b_match[9], order_b_match[10],
            )

        # Parent-stop provenance is single-consumption.  Resolve that ownership
        # before any candidate stop is allowed to shrink the E decision horizon;
        # otherwise a later fresh-trend Order can incorrectly win merely because
        # its own stop occurs earlier than the true first Order opened by the
        # same parent stop.  Independent Reset-leg provenance is preserved.
        self._enforce_single_parent_stop_owner(by_geometry)

        known_stops = [
            item[6][2]
            for item in by_geometry.values()
            if item[6] is not None
        ]
        provisional_deadline = min(known_stops) if known_stops else self.range_end
        if continuous_deadline is not None:
            provisional_deadline = min(
                provisional_deadline, continuous_deadline
            )
        stopped = [
            item[6][2]
            for item in by_geometry.values()
            if item[6] is not None
        ]
        decision_deadline = min(stopped) if stopped else self.range_end
        if continuous_deadline is not None:
            decision_deadline = min(decision_deadline, continuous_deadline)
        eligible = [
            item
            for item in by_geometry.values()
            if item[2] <= decision_deadline
        ]
        result = sorted(
            eligible,
            key=lambda item: (
                item[6][2] if item[6] is not None else self.range_end,
                self._reaction_first_time(item[1]),
            ),
        )
        self._order_candidates_cache[cache_key] = tuple(result)
        return result

    def _first_order(
        self, start: datetime, continuous_deadline: datetime | None = None,
        allow_bounded_continue: bool = False,
        allow_trend_leg_continue: bool = False,
    ) -> OrderMatch | None:
        candidates = [
            item for item in self.order_candidates(
                start, continuous_deadline,
                allow_bounded_continue=allow_bounded_continue,
                allow_trend_leg_continue=allow_trend_leg_continue,
            )
            if item[6] is not None
        ]
        return candidates[0] if candidates else None

    def _has_sequence_reset_between(
        self, start: datetime, end: datetime,
    ) -> bool:
        """Return whether a known hard reset lies in ``(start, end]``."""
        position = bisect_right(self._sequence_reset_times, start)
        return (
            position < len(self._sequence_reset_times)
            and self._sequence_reset_times[position] <= end
        )

    def _blue_parent_superseded(self, parent: object, parent_stop: datetime) -> bool:
        """A confirmed later Red S closes an older Blue-E order lifecycle."""
        if str(getattr(parent, "family")) != "blue":
            return False
        position = bisect_right(
            self._red_s_source_times, getattr(parent, "source_time")
        )
        return (
            position < len(self._red_s_suffix_min_decision)
            and self._red_s_suffix_min_decision[position] < parent_stop
        )

    def _index_order_audit_identity(
        self, identity: tuple[int, int], confirmation: datetime,
    ) -> None:
        """Index one newly accepted physical Order by confirmation chronology."""
        first_index, break_index = identity
        item = (confirmation, first_index, break_index)
        position = bisect_right(self._order_audit_confirmation_index, item)
        self._order_audit_confirmation_index.insert(position, item)

    def _clear_order_audit(self) -> None:
        self.order_audit.clear()
        self._order_audit_confirmation_index.clear()

    def _register_order_audit(
        self, parent_type: str, parent: object, parent_stop: datetime,
    ) -> None:
        if self._has_sequence_reset_between(parent.source_time, parent_stop):
            return
        if (
            parent_type == "E"
            and self._blue_parent_superseded(parent, parent_stop)
        ):
            # Enforce the same ownership rule during provisional discovery
            # and final audit. Otherwise a closed branch can seed a carried
            # order into another parent before final reconciliation.
            return
        inherited_owners: list[OrderMatch] = []
        if parent_type == "S":
            inherited_owners = self._unconsumed_s_orders(parent, parent_stop)
        carried_owners = self._carried_orders_for_parent(parent, parent_stop)
        # Exact mirror contract: Bullish and Bearish use the same lifecycle
        # representative/deadline rule; only underlying price comparisons flip.
        inherited_owner = inherited_owners[0] if inherited_owners else None
        carried_owner = carried_owners[0] if carried_owners else None
        continuous_deadline = None
        if parent_type == "S" and carried_owner is None:
            continuous_deadline = (
                inherited_owner[6][2]
                if inherited_owner is not None and inherited_owner[6] is not None
                else self.range_end
            )
        order_search_start = parent_stop
        if (
            parent_type == "S"
            and carried_owner is not None
            and carried_owner[6] is not None
        ):
            order_search_start = max(parent_stop, carried_owner[6][2])
        matches = self.order_candidates(
            order_search_start, continuous_deadline,
            allow_bounded_continue=(parent_type == "S"),
            allow_trend_leg_continue=(parent_type == "E"),
        )
        gate_owned = self._gate_owned_initial_order(parent_stop)
        if gate_owned is not None:
            gate_confirmation = gate_owned[2]
            matches = [
                item for item in matches
                if (
                    "reset-leg" in item[7]
                    or self._reaction_first_time(item[1]) <= gate_confirmation
                )
            ]
        gate_time = self.times[self._main_index(parent_stop)]
        ledger_gate = [
            entry for entry in self.order_audit.values()
            if self._reaction_first_time(entry["reaction"]) == gate_time
            and entry.get("stop_cross") is not None
            and entry["stop_cross"][2] >= parent_stop
        ]
        if ledger_gate:
            owner_confirmation = min(
                entry["confirmation_time"] for entry in ledger_gate
            )
            matches = [
                item for item in matches
                if (
                    "reset-leg" in item[7]
                    or self._reaction_first_time(item[1]) <= owner_confirmation
                )
            ]
        for match in matches:
            number, reaction, confirmation, level, source, source_time = match[:6]
            crossed, causes = match[6], match[7]
            reset_evidence = None
            if "reset-leg" in causes:
                reset_evidence = (
                    (match[9], match[10])
                    if match[9] is not None and match[10] is not None
                    else self._order_b_evidence(reaction, parent_stop)
                )
            # Order_B always resolves to a canonical opposite Reaction.
            # Audit accepts it only when the new same-direction Reset-leg
            # formation cause is proven.
            if "parent-stop" not in causes and reset_evidence is None:
                continue
            key = (
                int(getattr(reaction, "first_idx")),
                int(getattr(reaction, "break_idx")),
            )
            entry = self.order_audit.get(key)
            if entry is None:
                entry = {
                    "reaction_number": number,
                    "reaction": reaction,
                    "confirmation_time": confirmation,
                    "stop_level": level,
                    "stop_source_index": source,
                    "stop_source_time": source_time,
                    "stop_cross": crossed,
                    "causes": set(),
                }
                self.order_audit[key] = entry
                self._index_order_audit_identity(key, confirmation)
            audit_causes = entry["causes"]
            assert isinstance(audit_causes, set)
            if "parent-stop" in causes:
                family = str(getattr(parent, "color", getattr(parent, "family", "")))
                number_value = getattr(parent, "number", None)
                parent_label = parent_type
                if parent_type == "E" and number_value is not None:
                    parent_label = f"E{number_value}"
                if parent.source_time in self.sequence_resets:
                    parent_label = f"StopAll{self.sequence_resets[parent.source_time]}"
                    family = ""
                audit_causes.add(
                    (
                        "parent-stop", parent_label, family, parent_stop,
                        getattr(parent, "source_time"),
                    )
                )
            if reset_evidence is not None:
                audit_causes.add((
                    "reset-leg", reset_evidence[0], reset_evidence[1],
                ))

    def _enrich_order_audit_reset_causes(self) -> None:
        """Attach canonical Order_B provenance to already relevant Orders.

        Order_B formation is independent market structure, but OrderAudit is an
        accepted-behavior ledger rather than a dump of every market structure.
        Therefore only physical Orders already referenced by accepted S/E state
        (including the initial stopped-A audit) are enriched here.  When one
        physical Order has several valid Order_B origins, only the latest
        reset-leg cause is authoritative.
        """
        relevant_identities = set(self.order_audit) | set(self.initial_order_audit)
        if not relevant_identities:
            return
        latest: dict[tuple[int, int], OrderBFormation] = {}
        for item in self._build_order_b_formations():
            identity = reaction_identity(item.order_reaction)
            if identity not in relevant_identities:
                continue
            current = latest.get(identity)
            if current is None or (
                item.reset_time,
                item.strict_break_event_time,
            ) > (
                current.reset_time,
                current.strict_break_event_time,
            ):
                latest[identity] = item

        for identity, item in latest.items():
            entry = self.order_audit.get(identity)
            if entry is None:
                level, source, source_time = self._order_stop(
                    item.order_reaction_number, item.order_reaction
                )
                entry = {
                    "reaction_number": item.order_reaction_number,
                    "reaction": item.order_reaction,
                    "confirmation_time": item.order_confirmation_time,
                    "stop_level": level,
                    "stop_source_index": source,
                    "stop_source_time": source_time,
                    "stop_cross": self._cross_order(
                        item.order_confirmation_time, level
                    ),
                    "causes": set(),
                }
                self.order_audit[identity] = entry
                self._index_order_audit_identity(
                    identity, item.order_confirmation_time
                )
            causes = entry["causes"]
            assert isinstance(causes, set)
            for cause in [cause for cause in causes if cause[0] == "reset-leg"]:
                causes.discard(cause)
            causes.add((
                "reset-leg",
                item.reset_time,
                item.strict_break_event_time,
            ))

    def visual_order_lifecycle(
        self, start: datetime,
    ) -> list[tuple[int, object, datetime, Decimal, int, datetime,
                    tuple[int, datetime, datetime] | None, bool]]:
        """Return only orders admitted by the E lifecycle, including live ones.

        This is presentation/audit output.  It follows the same direct and
        Order_B replacement gates as ``_first_order`` but does not require a
        stop crossing, so a valid still-live order can be drawn without
        changing E calculation.
        """
        position = bisect_left(self._opposite_first_times, start)
        owner = None
        for order_position in range(position, len(self.opposite_reactions)):
            reaction = self.opposite_reactions[order_position]
            first = self._opposite_first_times[order_position]
            confirmation = self._opposite_confirmations[order_position]
            if first >= start and confirmation >= start:
                owner = (order_position + 1, reaction, confirmation, start)
                break
        if owner is None:
            return []

        lifecycle = []
        is_replacement = False
        while owner is not None:
            number, reaction, confirmation, context = owner
            level, source, source_time = self._order_stop(
                number, reaction, context
            )
            crossed = self._cross_order(confirmation, level)
            lifecycle.append(
                (
                    number, reaction, confirmation, level, source,
                    source_time, crossed, is_replacement,
                )
            )
            deadline = crossed[2] if crossed is not None else self.range_end
            owner = self._replacement_order(reaction, confirmation, deadline)
            is_replacement = True
        return lifecycle

    def _parent_stop(self, parent_type: str, parent: object) -> tuple[int, datetime] | None:
        if parent_type == "S":
            start = getattr(parent, "decision_event_time")
        else:
            # An E can only stop after the order-stop event that confirms it.
            start = getattr(parent, "decision_event_time")
        return self._first_parent_stop(start, as_decimal(getattr(parent, "price")))

    def parent_stop(
        self, parent_type: str, parent: object
    ) -> tuple[int, datetime] | None:
        """Public lifecycle API for the first strict parent stop."""
        return self._parent_stop(parent_type, parent)


    def _cross_order(
        self, start: datetime, level: Decimal
    ) -> tuple[int, datetime, datetime] | None:
        cache_key = (start, level)
        if cache_key in self._cross_order_cache:
            return self._cross_order_cache[cache_key]
        left = bisect_left(self.lower_times, max(start, self.range_start))
        right = bisect_left(self.lower_times, self.range_end)
        position = self._first_cross_position(
            left, right, level, less=self.order_direction != "bearish"
        )
        if position is None:
            self._cross_order_cache[cache_key] = None
            return None
        event = self.lower_times[position]
        index = self._main_index(event)
        result = index, getattr(self.candles[index], "timestamp"), event
        self._cross_order_cache[cache_key] = result
        return result

    def cross_order(
        self, confirmation_time: datetime, stop_level: Decimal
    ) -> tuple[int, datetime, datetime] | None:
        """Public audit API for an Order stop crossing."""
        return self._cross_order(confirmation_time, stop_level)


    def _unconsumed_s_orders(
        self, parent: object, parent_stop: datetime
    ) -> list[OrderMatch]:
        """Return every Blue-S Order whose stop did not decide the S itself."""
        if (
            str(getattr(parent, "color")) != "blue"
            or getattr(parent, "order_confirmation_time", None) is None
            or getattr(parent, "order_stop_level", None) is None
        ):
            return []
        confirmation = getattr(parent, "order_confirmation_time")
        stop_level = as_decimal(getattr(parent, "order_stop_level"))
        crossed = self._cross_order(confirmation, stop_level)
        if crossed is None or crossed[2] < parent_stop:
            return []
        reaction = SimpleNamespace(
            mode=getattr(parent, "order_mode"),
            first_idx=getattr(parent, "order_first_index"),
            break_idx=getattr(parent, "order_break_index"),
            box_top=getattr(parent, "order_box_top"),
            box_top_source_idx=getattr(parent, "order_box_top_source_index"),
            box_bottom=getattr(parent, "order_box_bottom"),
            box_bottom_source_idx=getattr(parent, "order_box_bottom_source_index"),
        )
        return [(
            int(getattr(parent, "order_reaction_number")),
            reaction,
            confirmation,
            stop_level,
            int(getattr(parent, "order_stop_source_index")),
            getattr(parent, "order_stop_source_time"),
            crossed,
            ("carried-live",), None, None, None,
        )]



    def _initial_order_records(self) -> tuple[tuple[
        datetime, datetime, int, object, Decimal, int, datetime,
        tuple[int, datetime, datetime] | None,
    ], ...]:
        """Materialize immutable initial OrderAudit geometry once per run.

        Algorithm requirement: physical Order identity and exact strict stop
        chronology remain unchanged. Performance detail: the prior code
        recomputed ``_cross_order`` while rescanning this immutable ledger for
        every E parent. The precomputed records only remove repeated pure work.
        """
        cached = self._initial_order_records_cache
        if cached is not None:
            return cached

        records: list[tuple[
            datetime, datetime, int, object, Decimal, int, datetime,
            tuple[int, datetime, datetime] | None,
        ]] = []
        for entry in self.initial_order_audit.values():
            reaction = entry["reaction"]
            first = self._reaction_first_time(reaction)
            confirmation = entry["confirmation_time"]
            level = as_decimal(entry["stop_level"])
            crossed = self._cross_order(confirmation, level)
            records.append((
                first, confirmation, int(entry["reaction_number"]), reaction,
                level, int(entry["stop_source_index"]),
                entry["stop_source_time"], crossed,
            ))

        records.sort(key=lambda item: (item[0], item[1], int(getattr(item[3], "first_idx")), int(getattr(item[3], "break_idx"))))
        cached = tuple(records)
        self._initial_order_records_cache = cached
        self._initial_order_first_times = [item[0] for item in cached]

        by_first: dict[datetime, list[tuple[
            datetime, datetime, int, object, Decimal, int, datetime,
            tuple[int, datetime, datetime] | None,
        ]]] = {}
        for item in cached:
            by_first.setdefault(item[0], []).append(item)
        self._initial_orders_by_first_time = {
            key: tuple(value) for key, value in by_first.items()
        }

        # A separate confirmation-sorted view supports the post-stop route.
        # The record objects are reused; no duplicate Order representation is
        # constructed.
        confirmation_sorted = sorted(
            cached,
            key=lambda item: (item[1], item[0], int(getattr(item[3], "first_idx")), int(getattr(item[3], "break_idx"))),
        )
        self._initial_order_confirmation_records = tuple(confirmation_sorted)
        self._initial_order_confirmation_times = [item[1] for item in confirmation_sorted]
        return cached

    @staticmethod
    def _initial_record_match(
        record: tuple[
            datetime, datetime, int, object, Decimal, int, datetime,
            tuple[int, datetime, datetime] | None,
        ],
        causes: tuple[str, ...],
    ) -> OrderMatch:
        _first, confirmation, number, reaction, level, source_index, source_time, crossed = record
        return (
            number, reaction, confirmation, level, source_index, source_time,
            crossed, causes, None, None, None,
        )

    def _initial_order_match(
        self, entry: dict[str, object], causes: tuple[str, ...],
    ) -> OrderMatch:
        # Retained for compatibility callers. Hot E paths use the immutable
        # initial-ledger records above so the strict stop is not recomputed.
        reaction = entry["reaction"]
        confirmation = entry["confirmation_time"]
        level = as_decimal(entry["stop_level"])
        crossed = self._cross_order(confirmation, level)
        return (
            int(entry["reaction_number"]), reaction, confirmation, level,
            int(entry["stop_source_index"]), entry["stop_source_time"],
            crossed, causes, None, None, None,
        )

    def _gate_owned_initial_order(
        self, parent_stop: datetime,
    ) -> OrderMatch | None:
        """Keep an A-owned order that starts in the parent-stop candle."""
        gate_time = self.times[self._main_index(parent_stop)]
        self._initial_order_records()
        assert self._initial_orders_by_first_time is not None
        matches: list[OrderMatch] = []
        for record in self._initial_orders_by_first_time.get(gate_time, ()):
            confirmation = record[1]
            if confirmation < parent_stop:
                continue
            crossed = record[7]
            if crossed is None or crossed[2] < parent_stop:
                continue
            matches.append(self._initial_record_match(record, ("carried-live",)))
        return min(
            matches,
            key=lambda item: (item[6][2], self._reaction_first_time(item[1])),
            default=None,
        )

    def _carried_orders_for_parent(
        self, parent: object, parent_stop: datetime,
    ) -> list[OrderMatch]:
        """Return every Order formed and left live inside this parent lifecycle."""
        lifecycle_start = getattr(parent, "decision_event_time", None)
        if lifecycle_start is None:
            return []
        matches: list[OrderMatch] = []
        for entry in self.order_audit.values():
            created_events: list[datetime] = []
            reset_evidence: tuple[datetime, datetime] | None = None
            for cause in entry.get("causes", set()):
                if cause[0] == "parent-stop":
                    created_events.append(cause[3])
                elif cause[0] == "reset-leg":
                    created_events.append(cause[1])
                    reset_evidence = (cause[1], cause[2])
            if not created_events:
                continue
            created = min(created_events)
            confirmation = entry["confirmation_time"]
            crossed = entry.get("stop_cross")
            if (
                created <= lifecycle_start
                or created >= parent_stop
                or confirmation > parent_stop
                or crossed is None
                or crossed[2] < parent_stop
            ):
                continue
            causes = (
                ("carried-live", "reset-leg")
                if reset_evidence is not None
                else ("carried-live",)
            )
            reaction = entry["reaction"]
            matches.append((
                int(entry["reaction_number"]), reaction, confirmation,
                as_decimal(entry["stop_level"]), int(entry["stop_source_index"]),
                entry["stop_source_time"], crossed, causes, None,
                reset_evidence[0] if reset_evidence is not None else None,
                reset_evidence[1] if reset_evidence is not None else None,
            ))

        # Initial A-owned Orders are immutable. Restrict the scan to physical
        # First times inside the same legacy eligibility window, then preserve
        # the exact final stop/First ordering below.
        records = self._initial_order_records()
        assert self._initial_order_first_times is not None
        left = bisect_left(self._initial_order_first_times, lifecycle_start)
        right = bisect_right(self._initial_order_first_times, parent_stop)
        for record in records[left:right]:
            confirmation = record[1]
            if confirmation > parent_stop:
                continue
            crossed = record[7]
            if crossed is None or crossed[2] < parent_stop:
                continue
            matches.append(self._initial_record_match(record, ("carried-live",)))
        return sorted(
            matches,
            key=lambda item: (item[6][2], -int(getattr(item[1], "first_idx"))),
        )

    def _post_stop_accepted_orders_for_parent(
        self, parent: object, parent_stop: datetime,
    ) -> list[OrderMatch]:
        """Return accepted physical Orders confirmed after this parent stopped."""
        del parent
        matches_by_identity: dict[tuple[int, int], OrderMatch] = {}

        def add_match(match: OrderMatch) -> None:
            crossed = match[6]
            if crossed is None or crossed[2] <= parent_stop or crossed[2] <= match[2]:
                return
            if self._has_sequence_reset_between(parent_stop, crossed[2]):
                return
            identity = reaction_identity(match[1])
            current = matches_by_identity.get(identity)
            if current is None or (
                crossed[2], match[2], int(getattr(match[1], "first_idx"))
            ) < (
                current[6][2], current[2], int(getattr(current[1], "first_idx"))
            ):
                matches_by_identity[identity] = match

        # Initial ledger: confirmation and exact strict stop are both already
        # materialized, so no per-parent `_cross_order` work remains.
        self._initial_order_records()
        assert self._initial_order_confirmation_times is not None
        confirmation_records = self._initial_order_confirmation_records
        start = bisect_right(self._initial_order_confirmation_times, parent_stop)
        for record in confirmation_records[start:]:
            add_match(self._initial_record_match(record, ("accepted-live",)))

        # Current E-pass ledger is mutable, but accepted identities are also
        # kept in a confirmation-sorted side index. Only the suffix that can
        # satisfy ``confirmation > parent_stop`` is visited; the authoritative
        # ledger entry/provenance remains the dict above.
        audit_position = bisect_right(
            self._order_audit_confirmation_index,
            (parent_stop, 2**63 - 1, 2**63 - 1),
        )
        for _confirmation, first_index, break_index in (
            self._order_audit_confirmation_index[audit_position:]
        ):
            entry = self.order_audit.get((first_index, break_index))
            if entry is None:
                continue
            reaction = entry.get("reaction")
            confirmation = entry.get("confirmation_time")
            if reaction is None or not isinstance(confirmation, datetime):
                continue
            level_value = entry.get("stop_level")
            source_index = entry.get("stop_source_index")
            source_time = entry.get("stop_source_time")
            if level_value is None or source_index is None or source_time is None:
                continue
            crossed = entry.get("stop_cross")
            if not (
                isinstance(crossed, tuple)
                and len(crossed) >= 3
                and isinstance(crossed[2], datetime)
            ):
                crossed = self._cross_order(confirmation, as_decimal(level_value))

            reset_evidence: tuple[datetime, datetime] | None = None
            for cause in entry.get("causes", set()):
                if (
                    isinstance(cause, tuple) and len(cause) >= 3
                    and cause[0] == "reset-leg"
                    and isinstance(cause[1], datetime) and isinstance(cause[2], datetime)
                ):
                    evidence = (cause[1], cause[2])
                    if reset_evidence is None or evidence > reset_evidence:
                        reset_evidence = evidence
            causes = (
                ("accepted-live", "reset-leg")
                if reset_evidence is not None else ("accepted-live",)
            )
            add_match((
                int(entry.get("reaction_number", 0)), reaction, confirmation,
                as_decimal(level_value), int(source_index), source_time, crossed,
                causes, None,
                reset_evidence[0] if reset_evidence is not None else None,
                reset_evidence[1] if reset_evidence is not None else None,
            ))

        return sorted(
            matches_by_identity.values(),
            key=lambda item: (
                item[6][2], item[2], -int(getattr(item[1], "first_idx")),
            ),
        )


    def _blocked_by_gate_owned_order(self, zone: EZone) -> bool:
        """Reject only a nested Order_A, while preserving its child lineage."""
        if "parent-stop" not in zone.order_causes or "reset-leg" in zone.order_causes:
            return False
        gate_owned = self._gate_owned_initial_order(zone.parent_stop_event_time)
        return (
            gate_owned is not None
            and gate_owned[2] < zone.order_first_time
        )

    def _reset_evidence_for_order(
        self, first_index: int, break_index: int,
    ) -> tuple[datetime, datetime] | None:
        matching = [
            item for item in self._build_order_b_formations()
            if int(getattr(item.order_reaction, "first_idx")) == first_index
            and int(getattr(item.order_reaction, "break_idx")) == break_index
        ]
        if not matching:
            return None
        item = max(
            matching,
            key=lambda value: (
                value.reset_time,
                value.strict_break_event_time,
            ),
        )
        return item.reset_time, item.strict_break_event_time

    def _extreme_between(self, start: datetime, end: datetime) -> tuple[int, datetime, Decimal]:
        # E source ownership is candle-based: include the complete main candle
        # containing the parent stop and the complete main candle containing
        # the order stop. Lower-timeframe chronology decides whether each stop
        # happened, but it must not truncate either boundary candle's OHLC.
        start_index = max(self.start_index, self._main_index(start))
        end_index = min(self.end_index, self._main_index(end))
        source = self.candles[start_index]
        value = self._stop_value(source)
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = self._stop_value(item)
            better = candidate < value if self.direction == "bullish" else candidate > value
            if better:
                source, value = item, candidate
        return int(getattr(source, "index")), getattr(source, "timestamp"), value

    def _zone(
        self, family: str, number: int, parent_type: str,
        parent: object, stop_event: datetime,
    ) -> EZone | None:
        # Every E-space cycle starts at the strict parent stop. The order First
        # must itself strictly cross the active parent/reset boundary.
        inherited = (
            self._unconsumed_s_orders(parent, stop_event)
            if parent_type == "S"
            else []
        )
        gate_owned = self._gate_owned_initial_order(stop_event)
        carried = self._carried_orders_for_parent(parent, stop_event)
        self._register_order_audit(parent_type, parent, stop_event)
        # Parent-neutral shared accepted-Order route: an accepted Order may be
        # confirmed only after this parent stopped and still decide the E when
        # its own strict stop wins chronology.  Its original creation cause is
        # preserved; it is not relabeled as belonging to this parent.
        post_stop_accepted = self._post_stop_accepted_orders_for_parent(
            parent, stop_event
        )
        # A stopped E opens a new direct search at its own stop candle. An
        # older order formed before that event cannot replace the first valid
        # post-stop order. S may still pass its explicitly unconsumed Blue
        # order through the dedicated inheritance rule above.
        # Exact mirror contract: one representative per creation path in both
        # directions, followed by the shared final stop-event race.
        inherited_one = inherited[0] if inherited else None
        carried_one = carried[0] if carried else None
        post_stop_accepted_one = (
            post_stop_accepted[0] if post_stop_accepted else None
        )
        direct = self._first_order(
            stop_event,
            (
                inherited_one[6][2]
                if parent_type == "S" and carried_one is None
                and inherited_one is not None and inherited_one[6] is not None
                else self.range_end
                if parent_type == "S" and carried_one is None
                else None
            ),
            allow_bounded_continue=(parent_type == "S"),
            allow_trend_leg_continue=(parent_type == "E"),
        )
        choices = [
            item for item in (
                direct, inherited_one, carried_one, post_stop_accepted_one
            )
            if item is not None and item[6] is not None
        ]
        order_match = min(
            choices,
            key=lambda item: (item[6][2], -int(getattr(item[1], "first_idx"))),
            default=None,
        )
        if order_match is None:
            return None
        (
            order_number, order, order_confirmation, order_stop,
            stop_source, stop_source_time, crossed, order_causes,
            order_parent_stop_cause_time, order_reset_leg_reset_time,
            order_reset_leg_break_time,
        ) = order_match
        if crossed is None:
            return None
        order_decision_index, order_decision_time, order_decision_event = crossed
        decision_event = max(stop_event, order_decision_event)
        decision_index = self._main_index(decision_event)
        decision_time = getattr(self.candles[decision_index], "timestamp")
        source_index, source_time, price = self._extreme_between(stop_event, decision_event)
        parent_stop_index = self._main_index(stop_event)
        order_first_index = int(getattr(order, "first_idx"))
        top_source = int(getattr(order, "box_top_source_idx"))
        bottom_source = int(getattr(order, "box_bottom_source_idx"))
        return EZone(
            direction=self.direction,
            family=family,
            number=number,
            parent_type=parent_type,
            parent_source_index=int(getattr(parent, "source_index")),
            parent_source_time=getattr(parent, "source_time"),
            parent_price=as_decimal(getattr(parent, "price")),
            parent_stop_index=parent_stop_index,
            parent_stop_time=getattr(self.candles[parent_stop_index], "timestamp"),
            parent_stop_event_time=stop_event,
            order_direction=self.order_direction,
            order_reaction_number=order_number,
            order_mode=str(getattr(order, "mode")),
            order_causes=order_causes,
            order_parent_stop_cause_time=order_parent_stop_cause_time,
            order_reset_leg_reset_time=order_reset_leg_reset_time,
            order_reset_leg_break_time=order_reset_leg_break_time,
            order_first_index=order_first_index,
            order_first_time=getattr(self.candles[order_first_index], "timestamp"),
            order_break_index=int(getattr(order, "break_idx")),
            order_break_time=getattr(self.candles[int(getattr(order, "break_idx"))], "timestamp"),
            order_confirmation_time=order_confirmation,
            order_box_top=as_decimal(getattr(order, "box_top")),
            order_box_top_source_index=top_source,
            order_box_top_source_time=getattr(self.candles[top_source], "timestamp"),
            order_box_bottom=as_decimal(getattr(order, "box_bottom")),
            order_box_bottom_source_index=bottom_source,
            order_box_bottom_source_time=getattr(self.candles[bottom_source], "timestamp"),
            order_stop_level=order_stop,
            order_stop_source_index=stop_source,
            order_stop_source_time=stop_source_time,
            source_index=source_index,
            source_time=source_time,
            price=price,
            decision_index=decision_index,
            decision_time=decision_time,
            decision_event_time=decision_event,
        )

    def set_consumed_s_evidence(
        self, evidence: Sequence[tuple[object, object]],
    ) -> None:
        """Register non-public S evidence that continues a stopped larger E."""
        self._consumed_s_evidence = [
            (
                s_zone,
                (int(getattr(owner, "source_index")), getattr(owner, "source_time")),
            )
            for s_zone, owner in evidence
        ]

    def _apply_consumed_s_evidence(self, zones: Sequence[EZone]) -> list[EZone]:
        result = list(zones)
        for s_zone, owner_id in self._consumed_s_evidence:
            owner = next(
                (
                    item for item in result
                    if (item.source_index, item.source_time) == owner_id
                ),
                None,
            )
            if owner is None:
                continue
            continuation = self.continuation_chain_from_s(owner, s_zone)
            result = self.replace_with_earlier_continuation(
                result, owner, continuation
            )
        return result

    def continuation_chain_from_s(
        self, owner: EZone, s_zone: object,
    ) -> list[EZone]:
        """Build the E continuation opened by one S consumed by a stopped E.

        The S remains a calculation/evidence object, not a new public owner.
        Its first E inherits the stopped larger E's reconciled family and next
        number.  Recursive children are then rebuilt from the promoted E so
        Order discovery and stop chronology remain native E calculations.
        """
        stopped = self._parent_stop("S", s_zone)
        if stopped is None:
            return []
        _, stop_event = stopped
        family = str(getattr(owner, "family"))
        number = int(getattr(owner, "number")) + 1
        parent_type = "S"
        parent: object = s_zone
        chain: list[EZone] = []
        seen_sources: set[int] = set()
        while True:
            zone = self._zone(family, number, parent_type, parent, stop_event)
            if zone is None or zone.source_index in seen_sources:
                break
            parent_source_time = getattr(parent, "source_time")
            if self._has_sequence_reset_between(
                parent_source_time, zone.source_time
            ):
                break
            chain.append(zone)
            seen_sources.add(zone.source_index)
            next_stop = self._parent_stop("E", zone)
            if next_stop is None:
                break
            _, stop_event = next_stop
            parent_type, parent = "E", zone
            number += 1
        return chain

    def replace_with_earlier_continuation(
        self, base_zones: Sequence[EZone], owner: EZone, continuation: Sequence[EZone],
    ) -> list[EZone]:
        """Replace an owner's not-yet-decided descendant branch when an earlier one wins."""
        if not continuation:
            return list(base_zones)
        owner_id = (owner.source_index, owner.source_time)
        by_id = {(item.source_index, item.source_time): item for item in base_zones}

        def descends_from_owner(item: EZone) -> bool:
            current = item
            seen: set[tuple[int, datetime]] = set()
            while current.parent_type == "E":
                parent_id = (current.parent_source_index, current.parent_source_time)
                if parent_id == owner_id:
                    return True
                if parent_id in seen:
                    return False
                seen.add(parent_id)
                parent = by_id.get(parent_id)
                if parent is None:
                    return False
                current = parent
            return False

        direct_children = [
            item for item in base_zones
            if item.parent_type == "E"
            and (item.parent_source_index, item.parent_source_time) == owner_id
        ]
        first = continuation[0]
        if direct_children:
            winner = min(
                direct_children,
                key=lambda item: (item.decision_event_time, item.source_time),
            )
            if first.decision_event_time >= winner.decision_event_time:
                return list(base_zones)

        kept = [item for item in base_zones if not descends_from_owner(item)]
        merged = [*kept, *continuation]
        return self.resolve_same_source_conflicts(merged)

    def resolve_same_source_conflicts(
        self, zones: Sequence[EZone],
    ) -> list[EZone]:
        """Keep exactly one accepted E behavior for each physical source candle.

        Candidate discovery may legitimately reach the same source through
        multiple S/E lineages.  Those alternatives are evidence only; once E
        reconciliation has assigned an accepted family/number, a lower-ranked
        alternative at that *same physical source* is not a second behavior.

        Dominance is the shared project rule: Red E outranks Blue E regardless
        of number, and within the same family the higher E number outranks the
        lower number.  Exact ties preserve the earlier accepted object so this
        resolver never rewrites provenance merely to deduplicate output.
        """
        winners: dict[tuple[int, datetime], EZone] = {}
        order: list[tuple[int, datetime]] = []

        def outranks(candidate: EZone, current: EZone) -> bool:
            candidate_priority = self.sequence_priority("e", candidate.family)
            current_priority = self.sequence_priority("e", current.family)
            if candidate_priority != current_priority:
                return candidate_priority > current_priority
            if candidate.family == current.family and candidate.number != current.number:
                return candidate.number > current.number
            return False

        for zone in zones:
            identity = (int(zone.source_index), zone.source_time)
            current = winners.get(identity)
            if current is None:
                winners[identity] = zone
                order.append(identity)
            elif outranks(zone, current):
                winners[identity] = zone

        result = [winners[identity] for identity in order]
        result.sort(
            key=lambda item: (
                item.source_time, item.source_index, item.decision_event_time,
            )
        )
        return result

    def restore_independent_s_roots(
        self, dominant_zones: Sequence[EZone],
    ) -> list[EZone]:
        """Restore calculation-valid E1 roots owned directly by accepted S.

        E dominance chooses which chain owns larger-module continuation, but
        formation of a new E behavior is independent: every accepted, stopped
        S may still form its own direct E1.  A reconciled dominant zone that
        came from that same S is therefore replaced by the original direct
        root (family/number from the S chain), while missing roots are added.
        Suppressed S evidence consumed by a larger E is not in ``self.s_zones``
        and cannot manufacture a competing E1 through this path.
        """
        # A physical source already owned by an accepted E cannot also keep
        # an S parent alive for downstream E-root restoration. Public lifecycle
        # finality already gives that candle to E; applying the same ownership
        # here prevents a provisional same-source S from manufacturing a later
        # E1 after reconciliation.
        dominant_sources = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in dominant_zones
        }
        accepted_s = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in self.s_zones
            if (int(getattr(item, "source_index")), getattr(item, "source_time"))
            not in dominant_sources
        }
        roots = [
            item for item in self._last_candidate_zones
            if item.parent_type == "S"
            and int(item.number) == 1
            and (item.parent_source_index, item.parent_source_time) in accepted_s
        ]
        result = list(dominant_zones)
        for root in roots:
            parent_id = (root.parent_source_index, root.parent_source_time)
            same_parent = [
                item for item in result
                if item.parent_type == "S"
                and (item.parent_source_index, item.parent_source_time) == parent_id
            ]
            if same_parent:
                winner = min(
                    same_parent,
                    key=lambda item: (item.decision_event_time, item.source_time),
                )
                result = [item for item in result if item is not winner]
                result.append(root)
            elif not any(
                item.source_index == root.source_index
                and item.source_time == root.source_time
                and item.parent_type == root.parent_type
                and item.parent_source_index == root.parent_source_index
                and item.parent_source_time == root.parent_source_time
                for item in result
            ):
                result.append(root)
        return self.resolve_same_source_conflicts(result)

    def _discover_candidate_chains(self) -> list[EZone]:
        """Build provisional recursive E chains from every stopped S parent.

        Calculation-invalid S evidence is still audited normally.  It loses
        only the right to open a *competing cross-family E root* when its exact
        physical source is already occupied by a native E continuation.  This
        prevents a dead A→S branch from retroactively deleting/recoloring the
        existing E chain while preserving same-family provenance and OrderAudit.
        """
        # Discover S-owned orders before walking recursive E chains.  A valid
        # order formed inside an E parent's lifetime must remain available even
        # when that S branch is reconciled later than the E branch.
        for s_zone in self.s_zones:
            stop = self._parent_stop("S", s_zone)
            if stop is not None:
                self._register_order_audit("S", s_zone, stop[1])

        chains: list[tuple[object, list[EZone]]] = []
        candidates: list[EZone] = []
        for s_zone in self.s_zones:
            stop = self._parent_stop("S", s_zone)
            if stop is None:
                continue
            _, stop_event = stop

            # Every fully formed S starts an independent provisional E chain.
            # Final lifecycle eligibility is resolved after all candidate
            # continuations are visible, so exact same-source cross-family
            # collisions can be judged without timestamp/fixture exceptions.
            family = str(getattr(s_zone, "color"))
            number = 1

            parent_type: str = "S"
            parent: object = s_zone
            chain_sources: set[int] = set()
            chain: list[EZone] = []
            while True:
                zone = self._zone(family, number, parent_type, parent, stop_event)
                if zone is None:
                    break
                if zone.source_index in chain_sources:
                    break
                chain.append(zone)
                candidates.append(zone)
                chain_sources.add(zone.source_index)
                parent_type, parent = "E", zone
                next_stop = self._parent_stop("E", zone)
                if next_stop is None:
                    break
                _, stop_event = next_stop
                number += 1
            if chain:
                chains.append((s_zone, chain))

        if not self.invalid_s_root_identities or not candidates:
            return candidates

        continuation_families: dict[tuple[datetime, int], set[str]] = {}
        for zone in candidates:
            if zone.parent_type != "E":
                continue
            identity = (zone.source_time, int(zone.source_index))
            continuation_families.setdefault(identity, set()).add(zone.family)

        blocked_roots: set[tuple[datetime, int]] = set()
        for s_zone, _ in chains:
            identity = (
                getattr(s_zone, "source_time"),
                int(getattr(s_zone, "source_index")),
            )
            if identity not in self.invalid_s_root_identities:
                continue
            s_family = str(getattr(s_zone, "color"))
            if any(
                family != s_family
                for family in continuation_families.get(identity, set())
            ):
                blocked_roots.add(identity)

        if not blocked_roots:
            return candidates

        return [
            zone
            for s_zone, chain in chains
            if (
                getattr(s_zone, "source_time"),
                int(getattr(s_zone, "source_index")),
            ) not in blocked_roots
            for zone in chain
        ]

    def _reconcile_candidate_chains(
        self, candidates: list[EZone]
    ) -> list[EZone]:
        """Resolve competing E chains into the accepted chronological lifecycle."""
        # Resolve competing chains chronologically.  A stopped E is removed
        # from the active set immediately; it remains only as historical
        # output and cannot affect a later family or number.
        by_source: dict[int, list[EZone]] = {}
        for zone in candidates:
            by_source.setdefault(zone.source_index, []).append(zone)
        # A later E continuation can supersede a provisional E that was
        # started directly from an S before the continuation was confirmed.
        # Keep the later, deeper (bullish) / higher (bearish) structure.  This
        # This prevents a provisional S-owned object from consuming the active
        # chain before the later confirmed continuation.
        pending = sorted(
            by_source.values(),
            key=lambda item: (
                min(zone.source_time for zone in item),
                min(zone.decision_event_time for zone in item),
            ),
        )
        numbered: list[EZone] = []
        active: list[EZone] = []
        sequence_start: datetime | None = None

        candidates_by_source_time = {
            (item.source_index, item.source_time): item
            for item in candidates
        }

        children_by_parent: dict[tuple[int, object], list[EZone]] = {}
        s_children_by_source: dict[tuple[int, object], list[EZone]] = {}
        for item in candidates:
            if item.parent_type == "E":
                children_by_parent.setdefault(
                    (item.parent_source_index, item.parent_source_time), []
                ).append(item)
            elif item.parent_type == "S":
                s_children_by_source.setdefault(
                    (item.source_index, item.source_time), []
                ).append(item)

        def valid_order(zone: EZone) -> bool:
            if self._blocked_by_gate_owned_order(zone):
                return False
            if (
                zone.parent_type == "S"
                or "reset-leg" not in zone.order_causes
                or zone.family != "blue"
            ):
                return True
            children = children_by_parent.get(
                (zone.source_index, zone.source_time), []
            )
            for child in children:
                for competing in s_children_by_source.get(
                    (child.source_index, child.source_time), []
                ):
                    if competing.decision_event_time <= child.decision_event_time:
                        return False
            return True

        def invalidated_only_by_future_s(zone: EZone) -> bool:
            if valid_order(zone) or zone.parent_type != "E":
                return False
            children = children_by_parent.get(
                (zone.source_index, zone.source_time), []
            )
            parent_times = {
                competing.parent_source_time
                for child in children
                for competing in s_children_by_source.get(
                    (child.source_index, child.source_time), []
                )
                if competing.decision_event_time <= child.decision_event_time
            }
            return any(value > zone.source_time for value in parent_times)

        def parent_active(zone: EZone, seen: set[tuple[int, datetime]] | None = None) -> bool:
            if zone.parent_type == "S":
                parent_s = next(
                    (
                        item for item in self.s_zones
                        if int(getattr(item, "source_index"))
                        == zone.parent_source_index
                        and getattr(item, "source_time")
                        == zone.parent_source_time
                    ),
                    None,
                )
                if parent_s is None:
                    return False
                if sequence_start is not None and (
                    parent_s.source_time <= sequence_start
                    or parent_s.a_source_time < sequence_start
                ):
                    return False
                prior_e = [
                    item for item in numbered
                    if getattr(item, "source_time")
                    < zone.source_time
                    and (sequence_start is None or item.source_time > sequence_start)
                ]
                if not prior_e:
                    return True
                prior = max(
                    prior_e, key=lambda item: getattr(item, "source_time")
                )
                rebuilt_after_e = (
                    getattr(parent_s, "source_time")
                    > getattr(prior, "source_time")
                    and getattr(parent_s, "a_source_time")
                    >= getattr(prior, "source_time")
                )
                # A still-unconsumed Red S is not invalidated by a nested
                # Blue E. Its later strict stop owns the Red transition.
                dominant_s = (
                    str(getattr(parent_s, "color")) == "red"
                    and prior.family == "blue"
                    and parent_s.source_time < prior.source_time
                    and not any(
                        item.parent_type == "S"
                        and item.parent_source_time == zone.parent_source_time
                        for item in numbered
                    )
                )
                return rebuilt_after_e or dominant_s
            if zone.parent_source_time == sequence_start:
                # The StopAll source is a valid order gate, but never an
                # active E whose family/number could leak across the reset.
                return True
            if any(
                item.source_index == zone.parent_source_index
                and item.source_time == zone.parent_source_time
                for item in active
            ):
                return True
            identity = (zone.parent_source_index, zone.parent_source_time)
            if seen is None:
                seen = set()
            if identity in seen:
                return False
            seen.add(identity)
            skipped_parent = candidates_by_source_time.get(identity)
            return (
                skipped_parent is not None
                and not valid_order(skipped_parent)
                and parent_active(skipped_parent, seen)
            )

        def stopped_by(zone: EZone, prior: EZone) -> bool:
            if zone.decision_event_time <= prior.decision_event_time:
                return False
            if self.direction == "bullish":
                return zone.price < prior.price
            return zone.price > prior.price

        for group in pending:
            eligible = [
                item for item in group
                if valid_order(item) and parent_active(item)
            ]
            if not eligible:
                continue
            # A lower-priority S cannot steal an active E continuation.
            # Red S may supersede Blue E, but no S supersedes Red E.
            # Color follows the accepted stopped parent's reconciled family.
            eligible = [
                item
                for item in eligible
                if not (
                    item.parent_type == "S"
                    and any(
                        stopped_by(item, owner)
                        and (owner.family == "red" or item.family == "blue")
                        and any(
                            child.parent_type == "E"
                            and child.parent_source_index == owner.source_index
                            and child.parent_source_time == owner.source_time
                            and child.decision_event_time
                            >= item.decision_event_time
                            for child in candidates
                        )
                        for owner in active
                    )
                )
            ]
            if not eligible:
                continue
            current_owners = [
                item for item in eligible
                if not (
                    item.parent_type == "E"
                    and item.family == "blue"
                    and any(
                        str(getattr(s_zone, "color")) == "red"
                        and getattr(s_zone, "source_time")
                        > item.parent_source_time
                        and getattr(s_zone, "decision_event_time")
                        < item.parent_stop_event_time
                        for s_zone in self.s_zones
                    )
                )
            ]
            if current_owners:
                eligible = current_owners
            def ownership_priority(item: EZone) -> int:
                parent = next((prior for prior in active
                    if item.parent_type == "E"
                    and prior.source_time == item.parent_source_time), None)
                parent_family = parent.family if parent else item.family
                return self.sequence_priority(item.parent_type, parent_family)

            # One physical E source may be reachable through competing
            # Red/Blue S/E lineages.  Family priority is authoritative at the
            # physical source: Red outranks Blue even when the Blue candidate
            # happens to reach its decision a few lower-timeframe ticks
            # earlier.  Chronology remains the tie-breaker *within* the same
            # behavioral priority.  Applying this before chain reconciliation
            # prevents the dominant Red candidate from being discarded before
            # the final same-source resolver can see it.
            zone = min(
                eligible,
                key=lambda item: (
                    -ownership_priority(item),
                    item.decision_event_time,
                    item.parent_stop_event_time,
                ),
            )
            stopped_by_family: dict[str, list[EZone]] = {"red": [], "blue": []}
            for prior in active:
                if stopped_by(zone, prior):
                    stopped_by_family[prior.family].append(prior)

            parent_identity = (zone.parent_source_index, zone.parent_source_time)
            parent_is_active = (
                zone.parent_type == "S"
                or zone.parent_source_time == sequence_start
            ) or any(
                (item.source_index, item.source_time) == parent_identity
                for item in active
            )
            if not parent_is_active:
                reset_evidence = self._reset_evidence_for_order(
                    zone.order_first_index, zone.order_break_index
                )
                if reset_evidence is not None:
                    zone = replace(
                        zone,
                        order_causes=("reset-leg",),
                        order_parent_stop_cause_time=None,
                        order_reset_leg_reset_time=reset_evidence[0],
                        order_reset_leg_break_time=reset_evidence[1],
                    )

            owner = next((item for item in active
                          if zone.parent_type == "E"
                          and item.source_time == zone.parent_source_time), None)
            # Color follows the accepted stopped parent, not merely the most
            # recent S. A still-unbroken Red S does not recolor a nested E.
            parent_family = owner.family if owner is not None else zone.family

            if parent_family == "red":
                family = "red"
                number = (
                    max(item.number for item in stopped_by_family["red"]) + 1
                    if stopped_by_family["red"]
                    else 1
                )
            elif stopped_by_family["red"]:
                family = "red"
                number = max(item.number for item in stopped_by_family["red"]) + 1
            elif parent_family == "blue":
                family = "blue"
                number = (
                    max(item.number for item in stopped_by_family["blue"]) + 1
                    if stopped_by_family["blue"]
                    else 1
                )
            elif stopped_by_family["blue"]:
                family = "blue"
                number = max(item.number for item in stopped_by_family["blue"]) + 1
            else:
                family = zone.family
                number = 1
            stopped_ids = {
                (item.source_index, item.source_time)
                for values in stopped_by_family.values() for item in values
            }
            active = [
                item for item in active
                if (item.source_index, item.source_time) not in stopped_ids
            ]
            numbered_zone = replace(zone, family=family, number=number)
            numbered.append(numbered_zone)
            if zone.source_time in self.sequence_resets:
                active.clear()
                sequence_start = zone.source_time
            else:
                active.append(numbered_zone)
        def collect_lineage(zone: EZone, seen: set[tuple[int, datetime]]) -> None:
            identity = (zone.source_index, zone.source_time)
            if identity in seen:
                return
            seen.add(identity)
            self.visual_lifecycle_starts.add(zone.parent_stop_event_time)
            if zone.parent_type == "S":
                return
            parent = candidates_by_source_time.get(
                (zone.parent_source_index, zone.parent_source_time)
            )
            if parent is not None:
                collect_lineage(parent, seen)

        numbered_ids = {
            (item.source_index, item.source_time) for item in numbered
        }
        numbered.extend(
            item for item in candidates
            if invalidated_only_by_future_s(item)
            and (item.source_index, item.source_time) not in numbered_ids
            and not self._has_sequence_reset_between(
                item.parent_source_time, item.source_time
            )
        )

        lineage_seen: set[tuple[int, datetime]] = set()
        for zone in numbered:
            collect_lineage(zone, lineage_seen)

        numbered = [replace(item, parent_type="StopAll")
                    if item.parent_type == "E"
                    and item.parent_source_time in self.sequence_resets
                    else item for item in numbered]
        return numbered

    def _historical_rescue_candidates(
        self, candidates: Sequence[EZone], accepted: Sequence[EZone]
    ) -> list[EZone]:
        """Return presentation-only historical E objects suppressed by future conflicts.

        Primary reconciliation is authoritative and remains byte-for-byte
        behaviorally unchanged.  This pass only restores a candidate when:
        * it is an E-parented Blue Order_B object;
        * its Order is not blocked by a gate-owned prohibition;
        * the suppressing S lineage itself formed after this E, so the conflict is truly future-only;
        * its direct E parent is already accepted historical output;
        * no sequence reset lies between parent and candidate; and
        * no accepted behavior already owns the same physical E source.

        Rescued objects are intentionally excluded from calculation ownership.
        """
        children_by_parent: dict[tuple[int, object], list[EZone]] = {}
        s_children_by_source: dict[tuple[int, object], list[EZone]] = {}
        for item in candidates:
            if item.parent_type == "E":
                children_by_parent.setdefault(
                    (item.parent_source_index, item.parent_source_time), []
                ).append(item)
            elif item.parent_type == "S":
                s_children_by_source.setdefault(
                    (item.source_index, item.source_time), []
                ).append(item)

        def suppressed_by_future_child_conflict(zone: EZone) -> bool:
            if zone.parent_type != "E":
                return False
            if "reset-leg" not in zone.order_causes or zone.family != "blue":
                return False
            if self._blocked_by_gate_owned_order(zone):
                return False
            children = children_by_parent.get(
                (zone.source_index, zone.source_time), []
            )
            return any(
                competing.decision_event_time <= child.decision_event_time
                and competing.parent_source_time > zone.source_time
                for child in children
                for competing in s_children_by_source.get(
                    (child.source_index, child.source_time), []
                )
            )

        accepted_ids = {
            (item.source_index, item.source_time) for item in accepted
        }
        rescued: list[EZone] = []
        rescued_ids: set[tuple[int, datetime]] = set()

        while True:
            batch = [
                item for item in candidates
                if suppressed_by_future_child_conflict(item)
                and (item.source_index, item.source_time) not in accepted_ids
                and (item.source_index, item.source_time) not in rescued_ids
                and (item.parent_source_index, item.parent_source_time)
                    in accepted_ids | rescued_ids
                and not self._has_sequence_reset_between(
                    item.parent_source_time, item.source_time
                )
            ]
            if not batch:
                break
            batch = self.resolve_same_source_conflicts(batch)
            added = False
            for item in batch:
                identity = (item.source_index, item.source_time)
                if identity in accepted_ids or identity in rescued_ids:
                    continue
                rescued.append(item)
                rescued_ids.add(identity)
                added = True
            if not added:
                break

        rescued.sort(
            key=lambda item: (
                item.source_time, item.source_index, item.decision_event_time
            )
        )
        return rescued


    def _rebuild_accepted_order_audit(
        self, numbered: list[EZone], supplemental_s_zones: Sequence[object] = (),
    ) -> list[EZone]:
        """Rebuild Order Audit from accepted S/E/StopAll state only."""
        # Audit only accepted S/E state. Provisional candidate chains must not
        # create visible or reported order genders.  Preserve a snapshot of the
        # pre-reconciliation ledger so an accepted carried-live Order can keep
        # its original creation cause even when that creating parent is no
        # longer a public behavior.
        prior_order_audit = {
            identity: {
                **entry,
                "causes": set(entry.get("causes", set())),
            }
            for identity, entry in self.order_audit.items()
        }
        self._clear_order_audit()
        accepted_parents: list[tuple[str, object]] = [
            ("S", item) for item in self.s_zones
        ] + [("StopAll" if item.source_time in self.sequence_resets else "E", item)
             for item in numbered]
        for parent_type, parent in accepted_parents:
            stop = self._parent_stop(parent_type, parent)
            if stop is None:
                continue
            if parent_type == "E":
                # A later accepted Red S owns the behavioral color and closes
                # older Blue-E continuation state. The historical E remains
                # visible, but its later price crossing cannot open an order.
                if self._blue_parent_superseded(parent, stop[1]):
                    continue
            self._register_order_audit(parent_type, parent, stop[1])

        # Every physical Order embedded in an accepted E must remain present in
        # the canonical ledger.  This includes two cases that cannot be rebuilt
        # from final public parents alone:
        #   1) carried-live Orders whose original creating parent became
        #      historical/non-public during reconciliation; and
        #   2) valid bounded fresh-trend geometry with reaction number 0, which
        #      has no canonical opposite-Reaction object.
        for zone in numbered:
            identity = order_identity(zone.order_first_index, zone.order_break_index)
            if identity in self.order_audit:
                continue

            prior_entry = prior_order_audit.get(identity)
            reaction = self._opposite_by_first_index.get(zone.order_first_index)
            if (
                reaction is None
                or int(getattr(reaction, "break_idx", -1)) != zone.order_break_index
            ):
                reaction = SimpleNamespace(
                    mode=zone.order_mode,
                    first_idx=zone.order_first_index,
                    break_idx=zone.order_break_index,
                    box_top=zone.order_box_top,
                    box_top_source_idx=zone.order_box_top_source_index,
                    box_top_source_time=zone.order_box_top_source_time,
                    box_bottom=zone.order_box_bottom,
                    box_bottom_source_idx=zone.order_box_bottom_source_index,
                    box_bottom_source_time=zone.order_box_bottom_source_time,
                    behavior_internal=False,
                )

            causes: set[tuple[object, ...]] = set()
            if prior_entry is not None:
                causes.update(prior_entry.get("causes", set()))

            # An E may carry an A-owned Order that was already accepted before
            # S/E reconciliation.  Initial A audit uses ``a_causes`` rather
            # than the generic E-ledger cause tuple, so translate that original
            # creation provenance when the carried physical Order would
            # otherwise become cause-less after final-parent rebuilding.
            initial_entry = self.initial_order_audit.get(identity)
            if initial_entry is not None:
                a_causes = initial_entry.get("a_causes") or [(
                    initial_entry.get("a_source_time"),
                    initial_entry.get("a_stop_event_time"),
                )]
                for a_source_time, a_stop_time in a_causes:
                    if a_source_time is None or a_stop_time is None:
                        continue
                    causes.add((
                        "parent-stop", "A", None, a_stop_time, a_source_time
                    ))

            if (
                not causes
                and "carried-live" in zone.order_causes
                and zone.parent_type == "S"
            ):
                parent_s = next((
                    item for item in [*self.s_zones, *supplemental_s_zones]
                    if int(getattr(item, "source_index")) == zone.parent_source_index
                    and getattr(item, "source_time") == zone.parent_source_time
                    and getattr(item, "order_first_index", None) == zone.order_first_index
                    and getattr(item, "order_break_index", None) == zone.order_break_index
                ), None)
                if parent_s is not None:
                    causes.add((
                        "parent-stop",
                        "A",
                        None,
                        getattr(parent_s, "a_stop_event_time"),
                        getattr(parent_s, "a_source_time"),
                    ))

            if zone.order_parent_stop_cause_time is not None:
                parent_label = zone.parent_type
                if zone.parent_type == "E":
                    parent_zone = next(
                        (
                            item for item in numbered
                            if item.source_index == zone.parent_source_index
                            and item.source_time == zone.parent_source_time
                        ),
                        None,
                    )
                    if parent_zone is not None:
                        parent_label = f"E{parent_zone.number}"
                if zone.parent_source_time in self.sequence_resets:
                    parent_label = f"StopAll{self.sequence_resets[zone.parent_source_time]}"
                causes.add((
                    "parent-stop",
                    parent_label,
                    "" if zone.parent_source_time in self.sequence_resets else zone.family,
                    zone.parent_stop_event_time,
                    zone.parent_source_time,
                ))
            if (
                zone.order_reset_leg_reset_time is not None
                and zone.order_reset_leg_break_time is not None
            ):
                causes.add((
                    "reset-leg",
                    zone.order_reset_leg_reset_time,
                    zone.order_reset_leg_break_time,
                ))

            # carried-live / accepted-live labels are use provenance, not
            # creation causes. Their original accepted parent-stop/reset-leg
            # cause must therefore come from the preserved ledgers above. If
            # no creation cause can be proven, do not fabricate one.
            if not causes:
                continue

            exact_cross = self._cross_order(
                zone.order_confirmation_time, as_decimal(zone.order_stop_level)
            )
            self.order_audit[identity] = {
                "reaction_number": zone.order_reaction_number,
                "reaction": reaction,
                "confirmation_time": zone.order_confirmation_time,
                "stop_level": zone.order_stop_level,
                "stop_source_index": zone.order_stop_source_index,
                "stop_source_time": zone.order_stop_source_time,
                "stop_cross": exact_cross,
                "causes": causes,
            }
            self._index_order_audit_identity(
                identity, zone.order_confirmation_time
            )

        self._enrich_order_audit_reset_causes()

        # A retained order can have Reset-leg evidence predating its new
        # StopAll gate. Preserve that proven secondary cause in the emitted
        # object as well as the ledger; it never changes selection or weight.
        for index, zone in enumerate(numbered):
            if zone.parent_type != "StopAll":
                continue
            entry = self.order_audit.get(
                order_identity(zone.order_first_index, zone.order_break_index)
            )
            reset_causes = sorted(cause for cause in entry["causes"]
                                  if cause[0] == "reset-leg") if entry else []
            if reset_causes and "reset-leg" not in zone.order_causes:
                cause = reset_causes[0]
                numbered[index] = replace(
                    zone, order_causes=(*zone.order_causes, "reset-leg"),
                    order_reset_leg_reset_time=cause[1],
                    order_reset_leg_break_time=cause[2],
                )

        return sorted(
            numbered,
            key=lambda item: (item.source_time, item.source_index),
        )

    def rebuild_accepted_order_audit(
        self, zones: Sequence[EZone], supplemental_s_zones: Sequence[object] = (),
    ) -> list[EZone]:
        """Rebuild the canonical Order ledger after external E reconciliation.

        The pipeline may replace a final E branch with an earlier continuation
        built from consumed S evidence after ``detect()`` has completed.  That
        accepted branch must become authoritative for OrderAudit as well; this
        public hook keeps calculation ownership in the E engine instead of
        forcing the bridge to reconstruct trading provenance.
        """
        return self._rebuild_accepted_order_audit(
            list(zones), supplemental_s_zones=supplemental_s_zones
        )

    def ensure_accepted_order_audit(
        self, zones: Sequence[EZone], supplemental_s_zones: Sequence[object] = (),
    ) -> list[EZone]:
        """Add audit coverage for externally restored accepted E zones.

        Visibility may restore an independent S-owned E root after StopAll
        reconciliation.  Rebuilding from only that post-StopAll E list would
        incorrectly discard physical Orders still needed by already-created
        StopAll/history, so rebuild the accepted subset and then merge back any
        previously canonical identities that were not superseded.
        """
        preserved = {
            identity: {**entry, "causes": set(entry.get("causes", set()))}
            for identity, entry in self.order_audit.items()
        }
        rebuilt = self._rebuild_accepted_order_audit(
            list(zones), supplemental_s_zones=supplemental_s_zones
        )
        for identity, entry in preserved.items():
            self.order_audit.setdefault(identity, entry)
        return rebuilt

    def detect(self) -> list[EZone]:
        """Discover, reconcile and audit recursive E lifecycles."""
        self._clear_order_audit()
        self.visual_lifecycle_starts.clear()
        candidates = self._discover_candidate_chains()
        self._last_candidate_zones = list(candidates)
        numbered = self._reconcile_candidate_chains(candidates)
        numbered = self._apply_consumed_s_evidence(numbered)
        numbered = self.resolve_same_source_conflicts(numbered)
        numbered = self._rebuild_accepted_order_audit(numbered)
        self.historical_rescued_zones = self._historical_rescue_candidates(
            candidates, numbered
        )
        return numbered


def detect_e_zones(
    direction: str,
    trend_reactions: Sequence[object],
    opposite_reactions: Sequence[object],
    s_zones: Sequence[object],
    trend_resets: Sequence[object],
    opposite_resets: Sequence[object],
    chronology: object,
    start_index: int = 0,
    end_index: int | None = None,
    geometry_finder: Callable[[str, int, int], object | None] | None = None,
    direct_geometry_finder: Callable[[str, int, int, datetime], object | None] | None = None,
    blocked_order_first_times: set[datetime] | None = None,
    initial_order_audit: dict[tuple[int, int], dict[str, object]] | None = None,
    sequence_priority: Callable[[str, str], int] | None = None,
    invalid_s_root_identities: set[tuple[datetime, int]] | None = None,
) -> list[EZone]:
    return EZoneDetector(
        direction,
        trend_reactions,
        opposite_reactions,
        s_zones,
        trend_resets,
        opposite_resets,
        chronology,
        start_index,
        end_index,
        geometry_finder,
        direct_geometry_finder,
        blocked_order_first_times,
        initial_order_audit,
        sequence_priority=sequence_priority,
        invalid_s_root_identities=invalid_s_root_identities,
    ).detect()
```
<!-- SOURCE_FILE_END:e_zone_detector.py -->
### 26.6 `lifecycle_engine.py`

- Source version: `1.15.2`
- Last modified declared by module: `2026-09-23 09:25:00 +03:30`
- Lines: `1706`
- Role: Cross-stage behavior lifecycle, priority, visibility, StopAll state, cycle boundaries, and ownership arbitration.
- Optional integrity SHA-256: `84bed2e674f855a4d2dc52960840eddc6d8f058ff247b893a319eecdc36e152d`

<!-- SOURCE_FILE_BEGIN:lifecycle_engine.py:SHA256=84bed2e674f855a4d2dc52960840eddc6d8f058ff247b893a319eecdc36e152d -->
```python
"""Cross-stage behavior lifecycle, visibility, priority, and StopAll ownership.

Owns the single shared behavior-priority table, accepted-vs-blocked Order
precedence, A/S/E/StopAll public ownership boundaries, Internal-Reaction output
filters, and StopAll detection/reconciliation. It does not reconstruct detector
geometry.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from typing import Sequence

from core_utils import as_decimal, order_identity
from direction_policy import policy_for


STOP_ALL_VERSION = "1.15.2"
STOP_ALL_LAST_MODIFIED = "2026-09-23 09:55:12 +03:30"


SEQUENCE_PRIORITY = {
    ("s", "blue"): 1,
    ("e", "blue"): 2,
    ("s", "red"): 3,
    ("e", "red"): 4,
}


def sequence_priority(kind: str, family: str) -> int:
    """Return the single authoritative cross-stage behavior priority."""
    return SEQUENCE_PRIORITY[(str(kind).lower(), str(family).lower())]


@dataclass(frozen=True, slots=True)
class StopAll:
    direction: str
    number: int
    source_index: int
    source_time: datetime
    price: Decimal
    decision_index: int
    decision_time: datetime
    decision_event_time: datetime
    gate_type: str
    gate_event_time: datetime
    stopped_behavior_type: str
    stopped_behavior_key: str
    stopped_behavior_count: int
    underlying_e_family: str | None
    underlying_e_number: int | None
    order_direction: str | None
    order_reaction_number: int | None
    order_mode: str | None
    order_causes: tuple[str, ...]
    order_parent_stop_cause_time: datetime | None
    order_reset_leg_reset_time: datetime | None
    order_reset_leg_break_time: datetime | None
    order_first_index: int | None
    order_first_time: datetime | None
    order_break_index: int | None
    order_break_time: datetime | None
    order_confirmation_time: datetime | None
    order_box_top: Decimal | None
    order_box_top_source_index: int | None
    order_box_top_source_time: datetime | None
    order_box_bottom: Decimal | None
    order_box_bottom_source_index: int | None
    order_box_bottom_source_time: datetime | None
    order_stop_level: Decimal | None
    order_stop_source_index: int | None
    order_stop_source_time: datetime | None
    stop_index: int | None
    stop_time: datetime | None
    stop_event_time: datetime | None


class StopAllDetector:
    def __init__(
        self,
        direction: str,
        s_zones: Sequence[object],
        e_zones: Sequence[object],
        chronology: object,
    ) -> None:
        if direction not in {"bullish", "bearish"}:
            raise ValueError("Direction must be 'bullish' or 'bearish'.")
        self.direction = direction
        self.s_zones = list(s_zones)
        self.e_zones = sorted(
            e_zones, key=lambda item: (item.source_time, item.source_index)
        )
        self.chronology = chronology
        self.candles = chronology.candles
        self.lower = chronology.seconds
        self.lower_times = chronology.second_times
        self.lower_index = chronology.lower_index
        self.times = chronology.times

    def _strict_stop(
        self, start: datetime, level: Decimal
    ) -> tuple[int, datetime, datetime] | None:
        left = bisect_left(self.lower_times, start)
        right = len(self.lower)
        position = (
            self.lower_index.first_less(left, right, level)
            if self.direction == "bullish"
            else self.lower_index.first_greater(left, right, level)
        )
        if position is None:
            return None
        event = self.lower_times[position]
        index = self.chronology.main_index(event, clamp=True)
        return index, self.times[index], event

    @staticmethod
    def _e_key(item: object) -> tuple[str, int]:
        return str(item.family), int(item.number)

    @staticmethod
    def _dominates_e(new: tuple[str, int], old: tuple[str, int]) -> bool:
        new_family, new_number = new
        old_family, old_number = old
        if new_family == old_family:
            return new_number > old_number
        # Red is always the dominant E family. A higher-numbered Blue E must
        # not separate or replace an active Red group.
        return new_family == "red" and old_family == "blue"

    @classmethod
    def _sequence_priority(cls, kind: str, family: str) -> int:
        return sequence_priority(kind, family)

    @classmethod
    def _active_sequence_priority(
        cls, s_key: str | None, e_key: tuple[str, int] | None,
    ) -> int:
        if e_key is not None:
            return cls._sequence_priority("e", e_key[0])
        if s_key is not None:
            return cls._sequence_priority("s", s_key)
        return 0

    def _stopall_from_e(
        self,
        item: object,
        number: int,
        gate_type: str,
        gate_event: datetime,
        behavior_type: str,
        behavior_key: str,
        behavior_count: int,
    ) -> StopAll:
        return StopAll(
            direction=self.direction,
            number=number,
            source_index=int(item.source_index),
            source_time=item.source_time,
            price=as_decimal(item.price),
            decision_index=int(item.decision_index),
            decision_time=item.decision_time,
            decision_event_time=item.decision_event_time,
            gate_type=gate_type,
            gate_event_time=gate_event,
            stopped_behavior_type=behavior_type,
            stopped_behavior_key=behavior_key,
            stopped_behavior_count=behavior_count,
            underlying_e_family=str(item.family),
            underlying_e_number=int(item.number),
            order_direction=str(item.order_direction),
            order_reaction_number=int(item.order_reaction_number),
            order_mode=str(item.order_mode),
            order_causes=tuple(getattr(item, "order_causes", ())),
            order_parent_stop_cause_time=getattr(
                item, "order_parent_stop_cause_time", None
            ),
            order_reset_leg_reset_time=getattr(
                item, "order_reset_leg_reset_time", None
            ),
            order_reset_leg_break_time=getattr(
                item, "order_reset_leg_break_time", None
            ),
            order_first_index=int(item.order_first_index),
            order_first_time=item.order_first_time,
            order_break_index=int(item.order_break_index),
            order_break_time=item.order_break_time,
            order_confirmation_time=item.order_confirmation_time,
            order_box_top=as_decimal(item.order_box_top),
            order_box_top_source_index=int(item.order_box_top_source_index),
            order_box_top_source_time=item.order_box_top_source_time,
            order_box_bottom=as_decimal(item.order_box_bottom),
            order_box_bottom_source_index=int(item.order_box_bottom_source_index),
            order_box_bottom_source_time=item.order_box_bottom_source_time,
            order_stop_level=as_decimal(item.order_stop_level),
            order_stop_source_index=int(item.order_stop_source_index),
            order_stop_source_time=item.order_stop_source_time,
            stop_index=None,
            stop_time=None,
            stop_event_time=None,
        )

    @staticmethod
    def _optional_int(value: object | None) -> int | None:
        return None if value is None else int(value)

    @staticmethod
    def _optional_decimal(value: object | None) -> Decimal | None:
        return None if value is None else as_decimal(value)

    def _stopall_from_s(
        self,
        item: object,
        behavior_type: str,
        behavior_key: str,
        behavior_count: int,
        underlying_e_key: tuple[str, int] | None,
    ) -> StopAll:
        """Promote the accepted opposite-color S into a fresh StopAll1.

        This is the direction-invariant family reversal gate.  In both
        Bullish and Bearish calculations, only an accepted native Mode-B S Red
        is promoted after two accepted occurrences of the same Blue behavior
        group since the latest accepted Red or StopAll boundary.  The repeated
        group need not remain the current dominant owner.  Directional mirroring is handled
        by strict stop/reaction geometry; Red/Blue family
        labels themselves are invariant.  Type-3 S Blue has no formation
        Order, so StopAll Order provenance remains optional.
        """
        return StopAll(
            direction=self.direction,
            number=1,
            source_index=int(item.source_index),
            source_time=item.source_time,
            price=as_decimal(item.price),
            decision_index=int(item.decision_index),
            decision_time=item.decision_time,
            decision_event_time=item.decision_event_time,
            gate_type="opposite-s-group-stop",
            gate_event_time=item.decision_event_time,
            stopped_behavior_type=behavior_type,
            stopped_behavior_key=behavior_key,
            stopped_behavior_count=behavior_count,
            underlying_e_family=(
                underlying_e_key[0] if underlying_e_key is not None else None
            ),
            underlying_e_number=(
                underlying_e_key[1] if underlying_e_key is not None else None
            ),
            order_direction=getattr(item, "order_direction", None),
            order_reaction_number=self._optional_int(
                getattr(item, "order_reaction_number", None)
            ),
            order_mode=getattr(item, "order_mode", None),
            order_causes=(),
            order_parent_stop_cause_time=getattr(
                item, "a_stop_event_time", None
            ),
            order_reset_leg_reset_time=getattr(item, "reset_time", None),
            order_reset_leg_break_time=None,
            order_first_index=self._optional_int(
                getattr(item, "order_first_index", None)
            ),
            order_first_time=getattr(item, "order_first_time", None),
            order_break_index=self._optional_int(
                getattr(item, "order_break_index", None)
            ),
            order_break_time=getattr(item, "order_break_time", None),
            order_confirmation_time=getattr(
                item, "order_confirmation_time", None
            ),
            order_box_top=self._optional_decimal(
                getattr(item, "order_box_top", None)
            ),
            order_box_top_source_index=self._optional_int(
                getattr(item, "order_box_top_source_index", None)
            ),
            order_box_top_source_time=getattr(
                item, "order_box_top_source_time", None
            ),
            order_box_bottom=self._optional_decimal(
                getattr(item, "order_box_bottom", None)
            ),
            order_box_bottom_source_index=self._optional_int(
                getattr(item, "order_box_bottom_source_index", None)
            ),
            order_box_bottom_source_time=getattr(
                item, "order_box_bottom_source_time", None
            ),
            order_stop_level=self._optional_decimal(
                getattr(item, "order_stop_level", None)
            ),
            order_stop_source_index=self._optional_int(
                getattr(item, "order_stop_source_index", None)
            ),
            order_stop_source_time=getattr(
                item, "order_stop_source_time", None
            ),
            stop_index=None,
            stop_time=None,
            stop_event_time=None,
        )

    @staticmethod
    def _blue_repeat_key(kind: str, number: int | None = None) -> tuple[str, int | None]:
        """Return the pending-reversal exact Blue behavior-group key.

        S Blue is one group regardless of its internal subtype.  Each E number
        is a separate group: E1 Blue, E2 Blue, E5 Blue, ... .  Counts are
        accepted-occurrence counts since the most recent Red S/Red E/StopAll,
        not counts of dominant-owner transitions.
        """
        normalized = str(kind).upper()
        if normalized == "S":
            return ("S", None)
        if normalized != "E" or number is None:
            raise ValueError("Blue repeat key must be S or numbered E.")
        return ("E", int(number))

    @staticmethod
    def _record_blue_repeat(
        counts: dict[tuple[str, int | None], int],
        latest: dict[tuple[str, int | None], object],
        key: tuple[str, int | None],
        item: object,
    ) -> None:
        counts[key] = counts.get(key, 0) + 1
        latest[key] = item

    def _opposite_s_stopall_gate(
        self,
        s_item: object,
        blue_repeat_counts: dict[tuple[str, int | None], int],
        blue_repeat_latest: dict[tuple[str, int | None], object],
    ) -> tuple[str, str, int, tuple[str, int] | None] | None:
        """Return Blue-repeat metadata when accepted S Red must become StopAll.

        Accepted Blue occurrences accumulate per exact S/E group until the
        first accepted Red S, accepted Red E, or hard StopAll boundary.  A Red
        behavior resolves the prior Blue reversal opportunity; a later S Red
        cannot consume its stale evidence.  The incoming S Red must have a
        native Mode-B formation Order; different numbered E groups never add.
        E-driven StopAll counters/priority are independent of this reversal
        evidence and retain their existing semantics.
        """
        if str(getattr(s_item, "color", "")).lower() != "red":
            return None
        # An initial native Mode-A Order opens an independent A→S Red branch;
        # it cannot consume old Blue-repeat evidence to promote that S to
        # StopAll. A continued Mode-B Order may own the reversal gate in the
        # existing hard lifecycle, in either market direction.
        if str(getattr(s_item, "order_mode", "")).upper() != "B":
            return None

        qualified = [
            (key, count, blue_repeat_latest[key])
            for key, count in blue_repeat_counts.items()
            if count >= 2 and key in blue_repeat_latest
        ]
        if not qualified:
            return None

        key, count, _ = max(
            qualified,
            key=lambda entry: (
                getattr(entry[2], "source_time"),
                int(getattr(entry[2], "source_index", -1)),
                1 if entry[0][0] == "E" else 0,
                -1 if entry[0][1] is None else int(entry[0][1]),
            ),
        )
        if key[0] == "S":
            return ("S", "S blue", count, None)
        e_number = int(key[1])
        return ("E", f"E{e_number} blue", count, ("blue", e_number))

    def detect(self) -> list[StopAll]:
        s_events = sorted(
            self.s_zones, key=lambda item: (item.source_time, item.source_index)
        )
        s_position = 0
        s_key: str | None = None
        s_count = 0
        e_key: tuple[str, int] | None = None
        e_count = 0
        dominant_s_item: object | None = None
        dominant_e_item: object | None = None
        active: list[StopAll] = []
        output: list[StopAll] = []
        blue_repeat_counts: dict[tuple[str, int | None], int] = {}
        blue_repeat_latest: dict[tuple[str, int | None], object] = {}

        def reset_cycle_blue_repeats() -> None:
            blue_repeat_counts.clear()
            blue_repeat_latest.clear()

        def process_s_event(s_item: object) -> None:
            nonlocal s_key, s_count, e_key, e_count, dominant_s_item, dominant_e_item, active

            reversal = self._opposite_s_stopall_gate(
                s_item, blue_repeat_counts, blue_repeat_latest
            )
            if reversal is not None:
                behavior_type, behavior_key, behavior_count, underlying_e_key = reversal
                zone = self._stopall_from_s(
                    s_item,
                    behavior_type,
                    behavior_key,
                    behavior_count,
                    underlying_e_key,
                )
                output.append(zone)
                # The S-reversal StopAll starts a fresh lifecycle. Historical
                # StopAll objects remain in output, but no pre-boundary active
                # StopAll may influence numbering or ownership in the new cycle.
                active = [zone]
                s_key = e_key = None
                s_count = e_count = 0
                dominant_s_item = None
                dominant_e_item = None
                reset_cycle_blue_repeats()
                return

            color = str(s_item.color)
            # An accepted Red S resolves the pending Blue-repeat reversal
            # opportunity even if its native Order mode cannot promote it.
            # Later Red S may use only Blue occurrences accepted after it.
            if color == "red":
                reset_cycle_blue_repeats()
            if color == "blue":
                self._record_blue_repeat(
                    blue_repeat_counts,
                    blue_repeat_latest,
                    self._blue_repeat_key("S"),
                    s_item,
                )
            incoming_priority = self._sequence_priority("s", color)
            active_priority = self._active_sequence_priority(s_key, e_key)
            if e_key is None and s_key == color:
                s_count += 1
                dominant_s_item = s_item
            elif incoming_priority > active_priority:
                s_key, s_count = color, 1
                dominant_s_item = s_item
                e_key, e_count = None, 0
                dominant_e_item = None

        for e_item in self.e_zones:
            while s_position < len(s_events) and (
                s_events[s_position].source_time < e_item.source_time
            ):
                process_s_event(s_events[s_position])
                s_position += 1

            e_decision = e_item.decision_event_time
            stopped_active = []
            for item in active:
                stop = self._strict_stop(item.decision_event_time, item.price)
                if stop is not None and stop[2] <= e_decision:
                    stopped_active.append((item, stop))
            if stopped_active:
                highest = max(item.number for item, _ in stopped_active)
                gate_event = min(stop[2] for _, stop in stopped_active)
                zone = self._stopall_from_e(
                    e_item, highest + 1, "stopall-stop", gate_event,
                    "StopAll", f"StopAll{highest}", len(stopped_active),
                )
                stopped_ids = {id(item) for item, _ in stopped_active}
                active = [item for item in active if id(item) not in stopped_ids]
                output.append(zone)
                active.append(zone)
                s_key = e_key = None
                s_count = e_count = 0
                dominant_s_item = None
                dominant_e_item = None
                reset_cycle_blue_repeats()
                continue

            new_key = self._e_key(e_item)
            # Once a dominant group has stopped, this E supplies the winning
            # order only. Its family/number need not match the stopped group.
            qualifies_e = e_key is not None and e_count >= 2
            qualifies_s = (
                e_key is None
                and s_key is not None
                and s_count >= 2
            )
            if qualifies_e or qualifies_s:
                parent = max(
                    (
                        item for item in (
                            self.e_zones if qualifies_e else self.s_zones
                        )
                        if item.source_time < e_item.source_time
                        and (
                            self._e_key(item) == e_key if qualifies_e
                            else str(item.color) == s_key
                        )
                    ),
                    key=lambda item: item.source_time,
                )
                gate = self._strict_stop(
                    parent.decision_event_time, as_decimal(parent.price)
                )
                if gate is not None and gate[2] <= e_decision:
                    zone = self._stopall_from_e(
                        e_item, 1, "sequence-group-stop", gate[2],
                        "E" if qualifies_e else "S",
                        (
                            f"E{e_key[1]} {e_key[0]}" if qualifies_e
                            else f"S {s_key}"
                        ),
                        e_count if qualifies_e else s_count,
                    )
                    output.append(zone)
                    active.append(zone)
                    s_key = e_key = None
                    s_count = e_count = 0
                    dominant_s_item = None
                    dominant_e_item = None
                    reset_cycle_blue_repeats()
                    continue

            # Red E resolves earlier Blue-repeat evidence. It may be a
            # higher-stage replacement of Blue, but cannot leave a stale
            # Blue reversal armed for a later unrelated S Red. Do not reset
            # dominant sequence state: E-driven StopAll gates own that state.
            if new_key[0] == "red":
                reset_cycle_blue_repeats()
            # This E remains accepted after independent StopAll checks.
            if new_key[0] == "blue":
                self._record_blue_repeat(
                    blue_repeat_counts,
                    blue_repeat_latest,
                    self._blue_repeat_key("E", new_key[1]),
                    e_item,
                )

            # Stage ownership is A -> S -> E -> StopAll. When the first E
            # replaces an S owner, E starts a new dominant-stage occurrence;
            # the superseded S is not counted again in current-owner sequence
            # state. Pending Blue-repeat counting is independent above.
            if e_key == new_key:
                e_count += 1
                dominant_e_item = e_item
            else:
                incoming_priority = self._sequence_priority("e", new_key[0])
                active_priority = self._active_sequence_priority(s_key, e_key)
                replaces_active = incoming_priority > active_priority
                advances_e = (
                    e_key is not None
                    and incoming_priority == active_priority
                    and self._dominates_e(new_key, e_key)
                )
                if replaces_active or advances_e:
                    e_key, e_count = new_key, 1
                    dominant_e_item = e_item
                    s_key, s_count = None, 0
                    dominant_s_item = None
            # A lower-priority Sequence event remains valid output but cannot
            # replace or separate the active dominant group.

        # The reversal rule is driven by accepted S itself, so it must still
        # fire when the triggering S occurs after the final accepted E.
        while s_position < len(s_events):
            process_s_event(s_events[s_position])
            s_position += 1

        completed = []
        for item in output:
            stop = self._strict_stop(item.decision_event_time, item.price)
            completed.append(
                replace(
                    item,
                    stop_index=stop[0] if stop else None,
                    stop_time=stop[1] if stop else None,
                    stop_event_time=stop[2] if stop else None,
                )
            )
        return completed


def detect_stopalls(
    direction: str,
    s_zones: Sequence[object],
    e_zones: Sequence[object],
    chronology: object,
) -> list[StopAll]:
    return StopAllDetector(direction, s_zones, e_zones, chronology).detect()

# ---------------------------------------------------------------------------
# Cross-stage lifecycle ownership
# ---------------------------------------------------------------------------

def prepare_order_audit(
    detector,
    start_index: int,
    end_index: int,
    s_detector=None,
    accepted_a_sources: set[datetime] | None = None,
    required_identities: set[tuple[int, int]] | None = None,
):
    """Resolve calculation-valid Order Audit identities before serialization.

    Multiple causes may own the same physical ``(FirstIndex, BreakIndex)``
    Order.  This function keeps one identity, merges all accepted provenance,
    applies calculation eligibility, and resolves the canonical stop crossing.
    It intentionally returns native datetimes/prices; JSON formatting remains
    the pipeline serializer's responsibility.
    """
    combined: list[tuple[dict[str, object], list[dict[str, object]]]] = []
    required_identities = set(required_identities or set())

    if s_detector is not None:
        for entry in s_detector.order_audit.values():
            a_causes = entry.get("a_causes") or [(
                entry["a_source_time"], entry["a_stop_event_time"]
            )]
            if accepted_a_sources is not None:
                a_causes = [
                    cause for cause in a_causes
                    if cause[0] in accepted_a_sources
                ]
            if not a_causes:
                continue
            combined.append((entry, [
                {
                    "kind": "parent-stop",
                    "parentType": "A",
                    "parentFamily": None,
                    "eventTime": stop_time,
                    "parentSourceTime": source_time,
                }
                for source_time, stop_time in a_causes
            ]))

    for entry in detector.order_audit.values():
        causes: list[dict[str, object]] = []
        for cause in sorted(entry["causes"], key=str):
            if cause[0] == "parent-stop":
                causes.append({
                    "kind": cause[0],
                    "parentType": cause[1],
                    "parentFamily": cause[2],
                    "eventTime": cause[3],
                    "parentSourceTime": cause[4],
                })
            else:
                causes.append({
                    "kind": cause[0],
                    "resetTime": cause[1],
                    "boundaryBreakTime": cause[2],
                })
        combined.append((entry, causes))

    merged: dict[tuple[int, int], dict[str, object]] = {}
    output: list[dict[str, object]] = []
    for entry, supplied_causes in combined:
        reaction = entry["reaction"]
        first_index = int(getattr(reaction, "first_idx"))
        identity = order_identity(first_index, getattr(reaction, "break_idx"))
        if (
            not start_index <= first_index <= end_index
            and identity not in required_identities
        ):
            continue
        existing = merged.get(identity)
        if existing is not None:
            existing_causes = existing["causes"]
            existing_causes.extend(
                cause for cause in supplied_causes
                if cause not in existing_causes
            )
            continue
        crossed = entry.get("stop_cross")
        if "stop_cross" not in entry:
            crossed = detector.cross_order(
                entry["confirmation_time"], entry["stop_level"]
            )
        prepared = {
            "entry": entry,
            "reaction": reaction,
            "causes": list(supplied_causes),
            "crossed": crossed,
        }
        merged[identity] = prepared
        output.append(prepared)

    # One exact parent-stop event can open only one physical Order.  Keep the
    # earliest confirmed Order that consumes that parent-stop provenance; a
    # later synthetic/direct reconstruction may still survive if it has an
    # independent cause (for example reset-leg), but it cannot spend the same
    # parent stop a second time.
    parent_owner: dict[tuple[object, object, object, object], dict[str, object]] = {}
    parent_rank: dict[tuple[object, object, object, object], tuple[object, int, int]] = {}
    for item in output:
        reaction = item["reaction"]
        rank = (
            item["entry"]["confirmation_time"],
            int(getattr(reaction, "first_idx")),
            int(getattr(reaction, "break_idx")),
        )
        for cause in item["causes"]:
            if cause.get("kind") != "parent-stop":
                continue
            key = (
                cause.get("parentType"),
                cause.get("parentFamily"),
                cause.get("eventTime"),
                cause.get("parentSourceTime"),
            )
            previous = parent_rank.get(key)
            if previous is None or rank < previous:
                parent_rank[key] = rank
                parent_owner[key] = item

    deduped_output: list[dict[str, object]] = []
    for item in output:
        accepted_causes: list[dict[str, object]] = []
        for cause in item["causes"]:
            if cause.get("kind") != "parent-stop":
                accepted_causes.append(cause)
                continue
            key = (
                cause.get("parentType"),
                cause.get("parentFamily"),
                cause.get("eventTime"),
                cause.get("parentSourceTime"),
            )
            if parent_owner.get(key) is item:
                accepted_causes.append(cause)
        if accepted_causes:
            item["causes"] = accepted_causes
            deduped_output.append(item)
    output = deduped_output

    # Internal Reaction geometry remains calculation-valid for direct
    # parent-stop and carried-live Order ownership.  The explicit prohibition
    # is scoped to Reset-leg Order_B: if every accepted cause of this physical
    # Order is reset-leg and the owning Reaction is behavior-internal, reject
    # it.  Cause merging happens first so a valid parent-stop cause cannot be
    # erased by an internal reset-leg provenance on the same identity.
    return [
        item for item in output
        if not (
            str(getattr(item["reaction"], "mode", "")).upper() == "B"
            and bool(getattr(item["reaction"], "behavior_internal", False))
            and item["causes"]
            and all(cause.get("kind") == "reset-leg" for cause in item["causes"])
        )
    ]


def accepted_audit_entry(
    entry: dict[str, object], accepted_sources: set
) -> dict[str, object] | None:
    """Return an E-facing A audit entry for one accepted A provenance.

    A physical order may be opened by more than one stopped A.  E still
    consumes one identity-keyed entry, so select the first accepted cause
    while retaining the complete cause list for presentation serialization.
    """
    causes = entry.get("a_causes") or [
        (entry["a_source_time"], entry["a_stop_event_time"])
    ]
    selected = next(
        ((source_time, stop_time) for source_time, stop_time in causes
         if source_time in accepted_sources),
        None,
    )
    if selected is None:
        return None
    if (
        selected[0] == entry.get("a_source_time")
        and selected[1] == entry.get("a_stop_event_time")
    ):
        return entry
    adjusted = dict(entry)
    adjusted["a_source_time"] = selected[0]
    adjusted["a_stop_event_time"] = selected[1]
    return adjusted

def resolve_order_context(
    order_audit: dict,
    accepted_a_sources: set[datetime],
    inherited_blocked_first_times: set[datetime],
    invalid_a_zones: Sequence[object],
    pending_s_a_sources: set[datetime],
    opposite_reactions: Sequence[object],
    candles: Sequence[object],
    direction: str,
    stop_finder,
) -> tuple[dict, set[datetime]]:
    """Resolve accepted stopped-A Orders against provisional Order blocks.

    Calculation ownership is authoritative: a canonical Order already accepted
    from stopped-A audit provenance cannot also be vetoed by the provisional
    invalid-leg-head block.  Keep the complete identity-keyed audit entries
    while filtering causes to A sources that remain calculation-eligible.
    """
    accepted_orders = {
        key: accepted
        for key, value in order_audit.items()
        for accepted in [accepted_audit_entry(value, accepted_a_sources)]
        if accepted is not None
    }

    blocked_order_first_times = set(inherited_blocked_first_times)
    blocked_order_first_times.update(
        blocked_orders_while_invalid_leg_heads_are_live(
            [
                item for item in invalid_a_zones
                if getattr(item, "source_time") in pending_s_a_sources
            ],
            opposite_reactions,
            candles,
            direction,
            stop_finder,
        )
    )

    accepted_initial_first_times = {
        getattr(entry["reaction"], "first_time")
        for entry in accepted_orders.values()
    }
    accepted_initial_first_times = {
        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        if isinstance(value, str) else value
        for value in accepted_initial_first_times
    }
    blocked_order_first_times.difference_update(accepted_initial_first_times)
    return accepted_orders, blocked_order_first_times


def visible_a_zones_after_s_stops(a_zones, s_zones, candles):
    """Suppress the A candle that contains an already-confirmed S stop.

    That candle is the S-stop/E transition candle. It may still carry the
    order box's BoxBottom, but it cannot receive a new A label.
    """
    times = [getattr(item, "timestamp") for item in candles]
    stop_indices = {
        bisect_left(times, getattr(item, "decision_event_time"))
        for item in s_zones
    }
    return [
        item for item in a_zones
        if int(getattr(item, "source_index")) not in stop_indices
    ]

def module_priority(item: object) -> int:
    """Return the confirmed behavioral ownership priority.

    StopAll > E red > S red > E blue > S blue.  A is intentionally absent:
    this helper is used only after A has become an S candidate.
    """
    if hasattr(item, "stopped_behavior_type"):
        return 5
    if hasattr(item, "family"):
        return 4 if str(getattr(item, "family")).lower() == "red" else 2
    if hasattr(item, "a_source_time"):
        return 3 if str(getattr(item, "color")).lower() == "red" else 1
    return 0

def module_identity(item: object) -> tuple[object, ...]:
    return (
        type(item).__name__,
        getattr(item, "family", getattr(item, "color", None)),
        getattr(item, "number", None),
        getattr(item, "source_time"),
        getattr(item, "source_index", None),
    )

def module_stop_event(item: object, stop_event_finder=None) -> datetime | None:
    """Resolve the strict one-second stop event of an S/E/StopAll object."""
    explicit = getattr(item, "stop_event_time", None)
    if explicit is not None:
        return explicit
    if stop_event_finder is None:
        return None
    found = stop_event_finder(item)
    if found is None:
        return None
    if isinstance(found, tuple):
        return found[-1]
    return found

def strictly_beyond_boundary(
    price: Decimal, boundary: Decimal, direction: str,
) -> bool:
    return policy_for(direction).strict_cross(price, boundary)

def dominant_module(modules: Sequence[object]) -> object:
    return max(
        modules,
        key=lambda item: (
            module_priority(item),
            int(getattr(item, "number", 0)),
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    )



def split_a_zones_by_dominant_stops(
    a_zones, s_zones, e_zones, stopalls, candles, direction,
    stop_event_finder=None, trend_reactions=None, confirmation_finder=None,
    a_stop_event_finder=None, stage_invalid_a_identities=None,
):
    """Separate visible A labels from A objects allowed into downstream math.

    A/Reaction/Blue discovery remains independent inside every half-leg.  Once
    an accepted S/E/StopAll is strictly stopped, however, the main candle that
    contains that stop begins the next leg comparison.  An A whose source
    extreme is strictly beyond the highest-priority stopped owner is the
    leg-start candidate, but it cannot re-enter calculation as an equal or
    smaller behavior. That candidate consumes the closed owner for subsequent
    half-leg A discovery while remaining absent from the public output.

    Equality is deliberately valid.  Stop chronology is exact at one second,
    while leg ownership is assigned to the containing main candle.
    """
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    candle_times = [getattr(item, "timestamp") for item in candles]
    modules = sorted(
        [*s_zones, *e_zones, *stopalls],
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    )
    stopped = []
    for module in modules:
        stop_event = module_stop_event(module, stop_event_finder)
        if stop_event is None:
            continue
        stop_index = bisect_right(candle_times, stop_event) - 1
        if stop_index < 0:
            continue
        stopped.append((module, stop_index, stop_event))

    # A is the smallest behavior in the lifecycle hierarchy.  A strict stop
    # therefore owns exactly the next equal/lower transition just like a
    # stopped S/E/StopAll does.  This prevents an A from immediately
    # re-entering after the previous A stop while still consuming the closed
    # owner so a later, genuinely new leg may form normally.
    a_owner_identities = set()
    if a_stop_event_finder is not None:
        for a_owner in a_zones:
            found = a_stop_event_finder(a_owner)
            if found is None:
                continue
            stop_event = found[-1] if isinstance(found, tuple) else found
            stop_index = bisect_right(candle_times, stop_event) - 1
            if stop_index < 0:
                continue
            stopped.append((a_owner, stop_index, stop_event))
            a_owner_identities.add(module_identity(a_owner))

    stop_indices = {
        module_identity(module): stop_index
        for module, stop_index, _stop_event in stopped
    }
    stop_events = {
        module_identity(module): stop_event
        for module, _stop_index, stop_event in stopped
    }

    valid = []
    invalid = []
    consumed = set()
    for a_zone in sorted(
        a_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        ),
    ):
        source_index = int(getattr(a_zone, "source_index"))
        eligible = []
        for module, stop_index, _stop_event in stopped:
            identity = module_identity(module)
            if (
                getattr(module, "source_time") >= getattr(a_zone, "source_time")
                or stop_index > source_index
                or identity in consumed
            ):
                continue
            if identity in a_owner_identities:
                # A->A immediate re-entry is defined by chronology, not by a
                # permanent A owner.  If the new A trigger starts only after
                # the previous A strict stop, it belongs to a genuinely new
                # leg and the old A must not block it.  A trigger that starts
                # at/before that stop overlaps the closed A transition and is
                # calculation-invalid.
                trigger_event = getattr(
                    a_zone, "trigger_event_time", getattr(a_zone, "source_time")
                )
                if trigger_event > stop_events[identity]:
                    continue
            eligible.append(module)
        if not eligible:
            valid.append(a_zone)
            continue
        # A historical high-priority E cannot own every later leg forever.
        # The newest main candle containing a strict stop owns the transition;
        # priority and numbering resolve only owners stopped in that candle.
        dominant = max(
            eligible,
            key=lambda item: (
                stop_indices[module_identity(item)],
                module_priority(item),
                int(getattr(item, "number", 0)),
                getattr(item, "source_time"),
                int(getattr(item, "source_index", -1)),
            ),
        )
        crosses_dominant = strictly_beyond_boundary(
            Decimal(str(getattr(a_zone, "price"))),
            Decimal(str(getattr(dominant, "price"))),
            direction,
        )
        if not crosses_dominant:
            valid.append(a_zone)
            continue

        # A confirmed trend Reaction may establish a directional leg head
        # inside the closed owner's range before this A. Preserve that A as an
        # interior-leg behavior, while retaining the existing owner
        # consumption below. This is provenance-based and uses no fixture data.
        interior = False
        if (
            module_identity(dominant) not in a_owner_identities
            and trend_reactions is not None
            and confirmation_finder is not None
            and source_index > 0
            and getattr(a_zone, "reaction_first_time", None) is not None
        ):
            owner_stop = next(
                stop_event for module, stop_index, stop_event in stopped
                if module_identity(module) == module_identity(dominant)
            )
            owner_stop_index = bisect_right(candle_times, owner_stop) - 1
            first_trend_index = bisect_right(
                candle_times, getattr(a_zone, "reaction_first_time")
            ) - 1
            if 0 <= owner_stop_index <= first_trend_index < len(candles):
                extreme_name = "low" if direction == "bullish" else "high"
                head = (
                    min(
                        candles[owner_stop_index:first_trend_index + 1],
                        key=lambda candle: Decimal(str(getattr(candle, extreme_name))),
                    )
                    if direction == "bullish"
                    else max(
                        candles[owner_stop_index:first_trend_index + 1],
                        key=lambda candle: Decimal(str(getattr(candle, extreme_name))),
                    )
                )
                head_extreme = Decimal(str(getattr(head, extreme_name)))
                a_extreme = Decimal(str(getattr(a_zone, "price")))
                if (
                    int(getattr(head, "index", -1)) < source_index
                    and (
                        head_extreme < a_extreme
                        if direction == "bullish"
                        else head_extreme > a_extreme
                    )
                ):
                    interior = any(
                        int(getattr(reaction, "first_idx"))
                        >= int(getattr(head, "index"))
                        and int(getattr(reaction, "first_idx"))
                        <= first_trend_index
                        and int(getattr(reaction, "break_idx")) < source_index
                        and confirmation_finder(reaction, direction)
                        < getattr(a_zone, "source_time")
                        for reaction in trend_reactions
                    )
        if interior:
            valid.append(a_zone)
            # Continue into the common consumption logic below.
            dominant_priority = module_priority(dominant)
            for module in eligible:
                if module_priority(module) <= dominant_priority:
                    consumed.add(module_identity(module))
            continue

        invalid.append(a_zone)
        dominant_priority = module_priority(dominant)
        if hasattr(dominant, "a_source_time"):
            # Stage-order invariant: A -> S -> E -> StopAll.  When S owns the
            # transition, a rejected fallback A cannot consume that S merely
            # by being rejected; otherwise the next A can re-enter behind S
            # and fabricate a second S branch in the same stage.  Keep S as
            # owner until a genuinely later-stage behavior takes ownership.
            if stage_invalid_a_identities is not None:
                stage_invalid_a_identities.add(
                    (getattr(a_zone, "source_time"), int(getattr(a_zone, "source_index")))
                )
            continue
        for module in eligible:
            if module_priority(module) <= dominant_priority:
                consumed.add(module_identity(module))
    return valid, invalid

def blocked_orders_while_invalid_leg_heads_are_live(
    invalid_a_zones, opposite_reactions, candles, direction, stop_finder,
):
    """Return order First times owned by a still-live invalid leg head.

    A strict dominant-boundary crossing can expose a new leg head without
    making its A calculation-valid. Until that head itself stops, an internal
    opposite Reaction cannot take over the larger owner's resumed E space.
    """
    blocked = set()
    for a_zone in invalid_a_zones:
        stop = stop_finder(a_zone)
        if stop is None:
            continue
        stop_event = stop[2]
        source_time = getattr(a_zone, "source_time")
        for reaction in opposite_reactions:
            first_time = getattr(candles[int(getattr(reaction, "first_idx"))], "timestamp")
            if source_time <= first_time < stop_event:
                blocked.add(first_time)
    return blocked


def consumed_s_evidence_after_larger_stop(
    s_candidates, accepted_s_zones, e_zones, direction, stop_event_finder, candles,
):
    """Return the earliest suppressed S evidence that continues each stopped E.

    A lower-priority S remains non-public when it belongs to the continuation
    of the current larger E lifecycle, but its stopped geometry must remain
    available to E.  The parent A must form strictly after the larger E's
    exact stop; an A that straddles that stop belongs to the older handoff and
    cannot advance the E chain.  The source candle must also continue strictly
    beyond the stop-main-candle Close.
    """
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    accepted = {
        (getattr(item, "a_source_time"), getattr(item, "source_time"))
        for item in accepted_s_zones
    }
    candle_times = [getattr(item, "timestamp") for item in candles]
    ordered_e = sorted(
        e_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    )
    earliest_by_owner = {}
    for candidate in sorted(
        s_candidates,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    ):
        identity = (getattr(candidate, "a_source_time"), getattr(candidate, "source_time"))
        if identity in accepted:
            continue
        a_source_time = getattr(candidate, "a_source_time")
        prior = [item for item in ordered_e if getattr(item, "source_time") < a_source_time]
        if not prior:
            continue
        owner = max(
            prior,
            key=lambda item: (
                getattr(item, "source_time"),
                int(getattr(item, "source_index", -1)),
            ),
        )
        if module_priority(candidate) >= module_priority(owner):
            continue
        owner_stop = module_stop_event(owner, stop_event_finder)
        if owner_stop is None or owner_stop >= a_source_time:
            continue
        stop_index = bisect_right(candle_times, owner_stop) - 1
        source_index = int(getattr(candidate, "source_index"))
        if not (0 <= stop_index < len(candles) and 0 <= source_index < len(candles)):
            continue
        stop_close = Decimal(str(getattr(candles[stop_index], "close")))
        source_close = Decimal(str(getattr(candles[source_index], "close")))
        if not strictly_beyond_boundary(source_close, stop_close, direction):
            continue
        owner_id = module_identity(owner)
        current = earliest_by_owner.get(owner_id)
        if current is None or (
            getattr(candidate, "source_time"), int(getattr(candidate, "source_index", -1))
        ) < (
            getattr(current[0], "source_time"), int(getattr(current[0], "source_index", -1))
        ):
            earliest_by_owner[owner_id] = (candidate, owner)
    return sorted(
        earliest_by_owner.values(),
        key=lambda pair: (
            getattr(pair[0], "source_time"),
            int(getattr(pair[0], "source_index", -1)),
        ),
    )

def s_zones_for_module_engines(s_zones, e_zones, direction):
    """Preserve the established S eligibility contract consumed by E/StopAll."""
    ordered_e = sorted(e_zones, key=lambda item: getattr(item, "source_time"))
    visible = []
    for s_zone in sorted(s_zones, key=lambda item: getattr(item, "source_time")):
        prior_modules = [
            item for item in [*ordered_e, *visible]
            if getattr(item, "source_time") < getattr(s_zone, "source_time")
        ]
        if prior_modules:
            prior = max(prior_modules, key=lambda item: getattr(item, "source_time"))
            # A strictly higher-priority behavior may supersede a lower one;
            # equal or lower priority remains owned by the prior lifecycle.
            # This preserves the original hierarchy contract while allowing
            # Red S to outrank Blue S / Blue E in either market direction.
            if module_priority(s_zone) <= module_priority(prior):
                if getattr(s_zone, "a_source_time") < getattr(prior, "source_time"):
                    continue
                boundary = Decimal(str(getattr(prior, "price")))
                if strictly_beyond_boundary(
                    Decimal(str(getattr(s_zone, "a_price"))), boundary, direction
                ):
                    continue
                if strictly_beyond_boundary(
                    Decimal(str(getattr(s_zone, "price"))), boundary, direction
                ):
                    continue
        visible.append(s_zone)
    return visible

def s_zones_for_stopall(s_zones, e_zones, direction):
    """Return accepted S state that may participate in StopAll grouping.

    E reconciliation still consumes the established S eligibility contract.
    StopAll adds one final same-source rule: when an accepted E owns the same
    physical source as an S candidate, E is final and the losing S must not
    be counted as another sequence member.
    """
    visible = s_zones_for_module_engines(s_zones, e_zones, direction)
    e_sources = {
        (int(getattr(item, "source_index")), getattr(item, "source_time"))
        for item in e_zones
    }
    return [
        item for item in visible
        if (int(getattr(item, "source_index")), getattr(item, "source_time"))
        not in e_sources
    ]

def visible_s_zones_after_module_resets(
    s_zones, e_zones, direction, stop_event_finder=None, source_event_finder=None,
    candles=None,
):
    """Apply dominant-behavior ownership to successive S candidates.

    Bullish/bearish half-leg calculations remain active under a larger
    behavior.  But once the currently dominant S/E/StopAll and the candidate
    S's parent A have both stopped, that A belongs to the next larger module
    lifecycle.  The would-be S is therefore consumed, while its historical
    inputs remain available for chart rendering and audits.
    """
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    ordered_external = sorted(
        e_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    )
    visible = []
    consumed = set()
    for s_zone in sorted(
        s_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index", -1)),
        ),
    ):
        a_stop_event = getattr(s_zone, "a_stop_event_time", None)
        ownership_event = a_stop_event
        if direction in {"bullish", "bearish"}:
            # The larger head may stop while the internal S search is open,
            # after A stops but before the candidate's own extreme forms.
            # A later stop after that extreme must not rewrite its ownership.
            ownership_event = (
                source_event_finder(s_zone) if source_event_finder is not None
                else getattr(s_zone, "source_time")
            )
        prior_modules = [
            item for item in [*ordered_external, *visible]
            if getattr(item, "source_time") < getattr(s_zone, "source_time")
            and module_identity(item) not in consumed
        ]
        # A newer E/StopAll source begins the current larger-module lifecycle.
        # Stops belonging to modules sourced before that owner are historical
        # and cannot suppress nested S candidates in the newer lifecycle.
        prior_external = [
            item for item in ordered_external
            if getattr(item, "source_time") < getattr(s_zone, "source_time")
        ]
        if prior_external:
            current_external = max(
                prior_external,
                key=lambda item: (
                    getattr(item, "source_time"),
                    int(getattr(item, "source_index", -1)),
                ),
            )
            lifecycle_start = getattr(current_external, "source_time")
            prior_modules = [
                item for item in prior_modules
                if getattr(item, "source_time") >= lifecycle_start
            ]
        if prior_modules and ownership_event is not None:
            stopped_prior = [
                module for module in prior_modules
                if (
                    module_stop := module_stop_event(module, stop_event_finder)
                ) is not None
                and module_stop <= ownership_event
            ]
            if stopped_prior:
                # A lower-priority S may not re-form inside the next lifecycle
                # of the most recent stopped larger module.  Use the latest
                # stopped E/StopAll owner for this continuation-boundary test;
                # do not let an older, higher-priority historical module steal
                # ownership from the current lifecycle.
                stopped_external = [
                    module for module in stopped_prior
                    if not hasattr(module, "a_source_time")
                ]
                if candles is not None and stopped_external:
                    latest_external = max(
                        stopped_external,
                        key=lambda item: (
                            getattr(item, "source_time"),
                            int(getattr(item, "source_index", -1)),
                        ),
                    )
                    if module_priority(s_zone) < module_priority(latest_external):
                        larger_stop = module_stop_event(
                            latest_external, stop_event_finder
                        )
                        if larger_stop is not None:
                            candle_times = [
                                getattr(candle, "timestamp") for candle in candles
                            ]
                            stop_index = bisect_right(candle_times, larger_stop) - 1
                            source_index = int(getattr(s_zone, "source_index"))
                            if (
                                0 <= stop_index < len(candles)
                                and 0 <= source_index < len(candles)
                            ):
                                stop_close = Decimal(str(
                                    getattr(candles[stop_index], "close")
                                ))
                                source_close = Decimal(str(
                                    getattr(candles[source_index], "close")
                                ))
                                if strictly_beyond_boundary(
                                    source_close, stop_close, direction
                                ):
                                    continue

                # Lifecycle ownership is chronological first.  An old
                # high-priority StopAll/E must not steal the transition from
                # the behavior that stopped most recently before this source.
                # Priority/number only resolve a true same-stop-event tie.
                dominant = max(
                    stopped_prior,
                    key=lambda item: (
                        module_stop_event(item, stop_event_finder),
                        module_priority(item),
                        int(getattr(item, "number", 0)),
                        getattr(item, "source_time"),
                        int(getattr(item, "source_index", -1)),
                    ),
                )
                # A newly confirmed higher-priority S family supersedes a
                # stopped lower-priority owner.  In particular, a Red S must
                # remain visible after a stopped Blue S when its own strict
                # directional extreme is reached.  The existing price/stop
                # consumption rule still applies when the candidate priority
                # is equal or lower, preserving the established lifecycle.
                if (
                    hasattr(s_zone, "a_source_time")
                    and hasattr(dominant, "a_source_time")
                    and module_priority(s_zone) > module_priority(dominant)
                ):
                    visible.append(s_zone)
                    continue
                # A stopped owner advances the lifecycle only when the new S
                # is itself the strict directional extreme of that leg.
                # Equality belongs to the earlier owner and remains valid.
                if not strictly_beyond_boundary(
                    Decimal(str(getattr(s_zone, "price"))),
                    Decimal(str(getattr(dominant, "price"))),
                    direction,
                ):
                    visible.append(s_zone)
                    continue
                # All lower/equal stopped owners involved in this transition
                # leave subsequent calculation ownership together.  The
                # highest-priority object determines the next module number.
                dominant_priority = module_priority(dominant)
                for module in stopped_prior:
                    module_stop = module_stop_event(module, stop_event_finder)
                    if (
                        module_priority(module) <= dominant_priority
                    ):
                        consumed.add(module_identity(module))
                continue
        # An active larger behavior does not disable the independent A/S
        # lifecycle inside the current half-leg.
        visible.append(s_zone)
    return visible

def reconcile_stopall_lifecycle(
    detector, s_zones, e_zones, chronology, direction, timed_step=None
):
    """Freeze StopAll boundaries from the accepted chronological E state.

    StopAll is a hard historical lifecycle boundary.  Once the accepted E/S
    chronology produces a StopAll, future sequence state may not feed back and
    delete or move that already-decided boundary.  The previous global
    fixed-point loop violated that prefix rule: rebuilding E with future reset
    maps could remove an earlier StopAll, then a later pass would recreate it.

    Detect the complete StopAll sequence once from the already reconciled E
    calculation state.  The StopAll detector itself processes events
    chronologically and resets its active sequence whenever a StopAll is
    created, so later StopAll numbers are derived from the hard boundaries in
    the same pass.  Publish the resulting reset map to E for downstream audit
    semantics, but never retroactively rebuild the E prefix from that map.
    """
    measure = timed_step or (lambda _label, work: work())
    visible_s = measure(
        f"Reconcile S visibility - {direction.title()}",
        lambda: s_zones_for_stopall(s_zones, e_zones, direction),
    )
    stopalls = measure(
        f"StopAll - {direction.title()}",
        lambda: detect_stopalls(direction, visible_s, e_zones, chronology),
    )
    detector.sequence_resets = {
        item.source_time: item.number for item in stopalls
    }
    return list(e_zones), stopalls


def visible_a_zones_after_module_boundaries(
    a_zones, s_zones, e_zones, direction, stop_event_finder=None,
):
    """Require A provenance to rebuild after the dominant strict stop.

    A price is deliberately not compared with the old module price.  Reactions
    and Blue Lines remain valid inside every half-leg; only provenance that
    straddles the dominant stop belongs to the closed lifecycle.
    """
    del direction  # Exact-stop ownership is directionally mirrored.
    modules = sorted(
        [*s_zones, *e_zones],
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        ),
    )
    valid = []
    for a_zone in sorted(
        a_zones,
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        ),
    ):
        stopped_prior = [
            module for module in modules
            if getattr(module, "source_time") <= getattr(a_zone, "source_time")
            and (
                stop_event := module_stop_event(module, stop_event_finder)
            ) is not None
            and stop_event <= getattr(a_zone, "source_time")
        ]
        if stopped_prior:
            dominant = dominant_module(stopped_prior)
            boundary_event = module_stop_event(dominant, stop_event_finder)
            provenance_times = (
                getattr(a_zone, "blue_1_source_time"),
                getattr(a_zone, "blue_2_source_time"),
                getattr(a_zone, "continuation_source_time"),
                getattr(a_zone, "reaction_first_time"),
            )
            if min(provenance_times) < boundary_event:
                continue
        valid.append(a_zone)
    return valid

def reaction_number_is_internal(items, number, identities):
    """Return whether a numbered Reaction resolves to a protected internal owner."""
    if number is None:
        return False
    number = int(number)
    if number < 1 or number > len(items):
        return False
    reaction = items[number - 1]
    return order_identity(
        getattr(reaction, "first_idx"),
        getattr(reaction, "break_idx"),
    ) in identities


def order_identity_is_internal(item, internal_identities):
    """Return whether a behavior's physical Order Reaction is internal."""
    first_index = getattr(item, "order_first_index", None)
    break_index = getattr(item, "order_break_index", None)
    if first_index is None or break_index is None:
        return False
    return order_identity(first_index, break_index) in internal_identities


def point_is_inside_healthy_reaction(source_time, price, reactions):
    """Return True only for a strict protected Reaction interior.

    First and published box edges are ownership boundaries, so equality and
    the First timestamp itself remain eligible.
    """
    if source_time is None or price is None:
        return False
    value = as_decimal(price)
    for reaction in reactions:
        first = getattr(reaction, "behavior_first_time", None)
        confirmed = getattr(reaction, "behavior_confirmation_time", None)
        if first is None or confirmed is None:
            continue
        if source_time <= first or source_time > confirmed:
            continue
        bottom = as_decimal(getattr(reaction, "behavior_public_box_bottom"))
        top = as_decimal(getattr(reaction, "behavior_public_box_top"))
        if bottom < value < top:
            return True
    return False


def forbidden_internal_order_b(item, internal_identities):
    """Reject only an internal Reset-leg *Mode-B* Order owner.

    The internal-Reaction prohibition is scoped to Reset-leg Order_B.  A
    Reset-leg provenance can legitimately carry Mode-A geometry after a hard
    lifecycle restart; treating every reset-leg cause as Order_B incorrectly
    deletes valid E/StopAll output. Direct parent-stop and carried-live Orders
    keep their native lifecycle rules as before.
    """
    if str(getattr(item, "order_mode", "")).upper() != "B":
        return False
    if not order_identity_is_internal(item, internal_identities):
        return False
    causes = {str(value) for value in getattr(item, "order_causes", ())}
    return (
        "reset-leg" in causes
        or getattr(item, "order_reset_leg_reset_time", None) is not None
    )


def filter_internal_behavior_outputs(
    a_zones,
    s_zones,
    e_zones,
    stopalls,
    opposite_reactions,
    opposite_internal_identities,
    all_behavior_reactions,
):
    """Apply only the scoped Internal-Reaction Order_B prohibition.

    Internal Reaction geometry and its eligible evidence remain calculation
    valid.  A/S/E/StopAll are not hidden merely because their source point lies
    inside a healthy Reaction interior, and an S is not rejected merely because
    a referenced Reset Reaction is internal.  The explicit prohibition that
    remains is an internal Reset-leg Mode-B Order_B owner for E/StopAll.
    """
    del opposite_reactions, all_behavior_reactions
    visible_a = list(a_zones)
    visible_s = list(s_zones)
    visible_e = [
        item for item in e_zones
        if not forbidden_internal_order_b(item, opposite_internal_identities)
    ]
    visible_stopalls = [
        item for item in stopalls
        if not forbidden_internal_order_b(item, opposite_internal_identities)
    ]
    return visible_a, visible_s, visible_e, visible_stopalls

def finalize_behavior_visibility(
    a_zones,
    s_zones,
    e_zones,
    stopalls,
    direction,
    invalid_s_identities,
    stop_event_finder,
    source_event_finder,
    candles,
    *,
    all_a_zones=None,
):
    """Resolve the final A/S/E lineage closure after StopAll reconciliation."""
    stopall_source_indices = {int(item.source_index) for item in stopalls}
    final_e_zones = [
        item for item in e_zones
        if int(getattr(item, "source_index")) not in stopall_source_indices
    ]
    e_source_indices = {
        int(getattr(item, "source_index")) for item in final_e_zones
    }
    final_s_zones = visible_s_zones_after_module_resets(
        s_zones,
        [*final_e_zones, *stopalls],
        direction,
        stop_event_finder,
        source_event_finder=source_event_finder,
        candles=candles,
    )

    # Presentation is a lineage closure over accepted calculations. If a final
    # E references an S parent, retain that historical S even if it no longer
    # owns downstream lifecycle calculation.
    referenced_s_sources = {
        getattr(item, "parent_source_time")
        for item in final_e_zones
        if str(getattr(item, "parent_type", "")).upper() == "S"
    }
    final_s_identities = {module_identity(item) for item in final_s_zones}
    final_s_zones.extend(
        item for item in s_zones
        if getattr(item, "source_time") in referenced_s_sources
        and module_identity(item) not in final_s_identities
    )
    final_s_zones.sort(
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        )
    )

    final_a_zones = visible_a_zones_after_module_boundaries(
        a_zones,
        final_s_zones,
        [*final_e_zones, *stopalls],
        direction,
        stop_event_finder,
    )
    referenced_a_sources = {getattr(item, "a_source_time") for item in final_s_zones}
    lineage_a_zones = a_zones if all_a_zones is None else all_a_zones
    final_a_identities = {
        (getattr(item, "source_time"), int(getattr(item, "source_index")))
        for item in final_a_zones
    }
    final_a_zones.extend(
        item for item in lineage_a_zones
        if getattr(item, "source_time") in referenced_a_sources
        and (
            getattr(item, "source_time"), int(getattr(item, "source_index"))
        ) not in final_a_identities
    )
    final_a_zones.sort(
        key=lambda item: (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        )
    )

    occupied = e_source_indices | stopall_source_indices
    final_a_zones = [
        item for item in final_a_zones
        if int(getattr(item, "source_index")) not in occupied
    ]
    final_s_zones = [
        item for item in final_s_zones
        if int(getattr(item, "source_index")) not in occupied
        and (
            getattr(item, "source_time"),
            int(getattr(item, "source_index")),
        ) not in invalid_s_identities
    ]
    return final_e_zones, final_s_zones, final_a_zones


def visible_a_zones(a_zones: Sequence[object], s_zones: Sequence[object]) -> list[object]:
    """Return A objects whose source candle is not occupied by a final S."""
    occupied = {int(getattr(item, "source_index")) for item in s_zones}
    return [
        item for item in a_zones
        if int(getattr(item, "source_index")) not in occupied
    ]
```
<!-- SOURCE_FILE_END:lifecycle_engine.py -->
### 26.7 `trading_pipeline.py`

- Source version: `1.4.1`
- Last modified declared by module: `2026-09-21 08:40:00 +03:30`
- Lines: `1923`
- Role: Production orchestration, RAW normalization, engine loading, full-range calculation, reconciliation passes, filtering, telemetry, and JSON serialization.
- Optional integrity SHA-256: `98f54cf3be6ddacd4e6b523b604be5a00635dcf8b464bc7d03772bbcccded62e`

<!-- SOURCE_FILE_BEGIN:trading_pipeline.py:SHA256=98f54cf3be6ddacd4e6b523b604be5a00635dcf8b464bc7d03772bbcccded62e -->
```python
"""Production trading pipeline orchestration, input normalization, and serialization.

Owns request parsing, raw-range isolation, candle construction, engine loading,
stage orchestration, progress/timing telemetry, and JSON serialization. Trading
validity/ownership rules belong to their calculation engines; this module must
not reimplement them.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import orjson
from bisect import bisect_left
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from time import perf_counter
from zoneinfo import ZoneInfo

# This bridge lives in ``engine/bridge`` while the calculation modules live in
# the sibling ``engine/pipeline`` package.  Put that directory on the module
# search path before importing shared helpers or dynamically loading detectors.
# The detector files intentionally keep their flat local imports
# (``core_utils`` / ``direction_policy``), so this single bootstrap point keeps
# every production module aligned with the deployed folder structure.
_ENGINE_ROOT = Path(__file__).resolve().parents[1]
_PIPELINE_DIR = _ENGINE_ROOT / "pipeline"
_pipeline_dir_text = str(_PIPELINE_DIR)
if _pipeline_dir_text not in sys.path:
    sys.path.insert(0, _pipeline_dir_text)

from core_utils import as_decimal, order_identity

_DTFMT = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}"


TRADING_PIPELINE_VERSION = "1.4.1"
TRADING_PIPELINE_LAST_MODIFIED = "2026-09-21 08:40:00 +03:30"

TEHRAN = ZoneInfo("Asia/Tehran")


def emit_progress(status: str, label: str, duration_ms: float | None = None):
    """Send machine-readable lifecycle events without contaminating JSON stdout."""
    event = {"status": status, "label": label}
    if duration_ms is not None:
        event["durationMs"] = round(duration_ms, 2)
    print(f"QG_PROGRESS:{json.dumps(event, separators=(',', ':'))}", file=sys.stderr, flush=True)


def timed(timings: dict[str, float], label: str, work):
    """Measure an existing pipeline phase without changing its inputs or output."""
    started = perf_counter()
    emit_progress("started", label)
    try:
        return work()
    finally:
        duration_ms = (perf_counter() - started) * 1000
        timings[label] = timings.get(label, 0.0) + duration_ms
        emit_progress("completed", label, duration_ms)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load reaction engine: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_engine(path: Path):
    return load_module("reaction_engine", path)


_local_dt_cache: dict[int, datetime] = {}


def local_datetime(epoch: int) -> datetime:
    cached = _local_dt_cache.get(epoch)
    if cached is not None:
        return cached
    result = datetime.fromtimestamp(epoch, TEHRAN).replace(tzinfo=None)
    _local_dt_cache[epoch] = result
    return result


_epoch_cache: dict[datetime, int] = {}


def epoch(local: datetime) -> int:
    cached = _epoch_cache.get(local)
    if cached is not None:
        return cached
    result = int(local.replace(tzinfo=TEHRAN).timestamp())
    _epoch_cache[local] = result
    return result


_display_epoch_cache: dict[str, int] = {}


def display_epoch(value: str | datetime) -> int:
    """Convert an engine display/native timestamp once per pipeline process."""
    if isinstance(value, datetime):
        return epoch(value)
    cached = _display_epoch_cache.get(value)
    if cached is not None:
        return cached
    result = epoch(datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
    _display_epoch_cache[value] = result
    return result


def build_candle_buckets(rows: list[dict], timeframe: int):
    """Normalize raw rows once, preserving lower and selected-timeframe buckets."""
    second_buckets: list[dict] = []
    current_second = None
    buckets: list[dict] = []
    current = None
    to_decimal = as_decimal
    decimal_cache: dict[tuple[type, object], Decimal] = {}

    def cached_decimal(value: object) -> Decimal:
        # Raw prices repeat heavily. Cache by both type and value so values
        # such as ``10`` and ``10.0`` retain their exact string-normalized
        # Decimal representation instead of being conflated by Python's
        # numeric equality rules.
        key = (type(value), value)
        try:
            return decimal_cache[key]
        except KeyError:
            normalized = to_decimal(value)
            decimal_cache[key] = normalized
            return normalized

    for row in rows:
        timestamp = int(row["time"])
        o = cached_decimal(row["open"])
        high = cached_decimal(row["high"])
        low = cached_decimal(row["low"])
        close = cached_decimal(row["close"])
        if current_second is None or current_second["time"] != timestamp:
            current_second = {
                "time": timestamp,
                "open": o,
                "high": high,
                "low": low,
                "close": close,
            }
            second_buckets.append(current_second)
        else:
            current_second["high"] = max(current_second["high"], high)
            current_second["low"] = min(current_second["low"], low)
            current_second["close"] = close
        bucket_time = timestamp if timeframe == 1 else timestamp // timeframe * timeframe
        if current is None or current["time"] != bucket_time:
            current = {
                "time": bucket_time,
                "open": o,
                "high": high,
                "low": low,
                "close": close,
            }
            buckets.append(current)
        else:
            current["high"] = max(current["high"], high)
            current["low"] = min(current["low"], low)
            current["close"] = close
    return second_buckets, buckets


def build_candle_objects(engine, buckets: list[dict]):
    """Create maintained engine candles from already-normalized buckets."""
    candles = []
    append = candles.append
    candle_type = engine.Candle
    classify = engine.classify_candle_color
    local = local_datetime
    fmt = _DTFMT.format
    for index, item in enumerate(buckets):
        stamp = local(item["time"])
        append(candle_type(
            index=index,
            timestamp=stamp,
            display_time=fmt(
                stamp.year,
                stamp.month,
                stamp.day,
                stamp.hour,
                stamp.minute,
                stamp.second,
            ),
            tag=classify(item["open"], item["close"]),
            open=item["open"],
            high=item["high"],
            low=item["low"],
            close=item["close"],
        ))
    return candles


def _index_selected(index: object, start_index: int | None, end_index: int | None) -> bool:
    return (
        start_index is None
        or end_index is None
        or start_index <= int(index) <= end_index
    )


def serialize(result, start_index=None, end_index=None, reaction_transform=None):

    resets = [{
        "index": item.index,
        "time": display_epoch(item.display_time),
        "secondTime": (
            display_epoch(item.second_time)
            if item.second_time is not None
            else None
        ),
        "brokenLevel": str(item.broken_level),
        "fromFirstIndex": item.from_first_idx,
    } for item in result.resets if _index_selected(item.index, start_index, end_index)]
    reactions = []
    for item in result.reactions:
        if not _index_selected(item.first_idx, start_index, end_index):
            continue
        public_item = reaction_transform(item) if reaction_transform is not None else item
        reactions.append({
            "firstIndex": public_item.first_idx,
            "firstTime": display_epoch(public_item.first_time),
            "boxTopSourceIndex": public_item.box_top_source_idx,
            "boxTopSourceTime": display_epoch(public_item.box_top_source_time),
            "boxTop": str(public_item.box_top),
            "boxBottomSourceIndex": public_item.box_bottom_source_idx,
            "boxBottomSourceTime": display_epoch(public_item.box_bottom_source_time),
            "boxBottom": str(public_item.box_bottom),
            "breakIndex": public_item.break_idx,
            "breakTime": display_epoch(public_item.break_time),
            "mode": public_item.mode,
        })
    return reactions, resets


def serialize_blue_lines(items, start_index=None, end_index=None):
    return [{
        "direction": item.direction,
        "kind": item.kind,
        "reactionNumber": item.reaction_number,
        "previousStrikeCount": item.previous_strike_count,
        "strikeCount": item.strike_count,
        "fibonacciLevel": str(item.fibonacci_level) if item.fibonacci_level is not None else None,
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "sourceExtreme": str(item.source_extreme),
        "brokenLevel": str(item.broken_level) if item.broken_level is not None else None,
        "linePrice": str(item.line_price),
        "startTime": epoch(item.start_time),
        "endTime": epoch(item.end_time),
    } for item in items if _index_selected(
        getattr(item, "source_index"), start_index, end_index
    )]


def serialize_a_zones(items):
    return [{
        "direction": item.direction,
        "blue1Ordinal": item.blue_1_ordinal,
        "blue2Ordinal": item.blue_2_ordinal,
        "blue1SourceTime": epoch(item.blue_1_source_time),
        "blue2SourceTime": epoch(item.blue_2_source_time),
        "blue1StopTime": epoch(item.blue_1_stop_time),
        "blue2StopTime": epoch(item.blue_2_stop_time),
        "blue1StopLevel": str(item.blue_1_stop_level),
        "blue2StopLevel": str(item.blue_2_stop_level),
        "continuationLevel": str(item.continuation_level),
        "continuationSourceIndex": item.continuation_source_index,
        "continuationSourceTime": epoch(item.continuation_source_time),
        "triggerIndex": item.trigger_index,
        "triggerTime": epoch(item.trigger_time),
        "triggerEventTime": epoch(item.trigger_event_time),
        "reactionNumber": item.reaction_number,
        "reactionFirstTime": epoch(item.reaction_first_time),
        "reactionBreakTime": epoch(item.reaction_break_time),
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "calculationValid": True,
    } for item in items]


def serialize_s_zones(items):
    return [{
        "direction": item.direction,
        "color": item.color,
        "formationType": item.formation_type,
        "aOrdinal": item.a_ordinal,
        "aSourceIndex": item.a_source_index,
        "aSourceTime": epoch(item.a_source_time),
        "aPrice": str(item.a_price),
        "aStopIndex": item.a_stop_index,
        "aStopTime": epoch(item.a_stop_time),
        "aStopEventTime": epoch(item.a_stop_event_time),
        "orderDirection": item.order_direction,
        "orderReactionNumber": item.order_reaction_number,
        "orderMode": item.order_mode,
        "orderFirstIndex": item.order_first_index,
        "orderFirstTime": (
            epoch(item.order_first_time) if item.order_first_time is not None else None
        ),
        "orderBreakIndex": item.order_break_index,
        "orderBreakTime": (
            epoch(item.order_break_time) if item.order_break_time is not None else None
        ),
        "orderConfirmationTime": (
            epoch(item.order_confirmation_time)
            if item.order_confirmation_time is not None
            else None
        ),
        "orderBoxTop": str(item.order_box_top) if item.order_box_top is not None else None,
        "orderBoxTopSourceIndex": item.order_box_top_source_index,
        "orderBoxTopSourceTime": (
            epoch(item.order_box_top_source_time)
            if item.order_box_top_source_time is not None
            else None
        ),
        "orderBoxBottom": (
            str(item.order_box_bottom) if item.order_box_bottom is not None else None
        ),
        "orderBoxBottomSourceIndex": item.order_box_bottom_source_index,
        "orderBoxBottomSourceTime": (
            epoch(item.order_box_bottom_source_time)
            if item.order_box_bottom_source_time is not None
            else None
        ),
        "orderStopLevel": (
            str(item.order_stop_level) if item.order_stop_level is not None else None
        ),
        "orderStopSourceIndex": item.order_stop_source_index,
        "orderStopSourceTime": (
            epoch(item.order_stop_source_time)
            if item.order_stop_source_time is not None
            else None
        ),
        "resetReactionNumber": item.reset_reaction_number,
        "resetTime": epoch(item.reset_time) if item.reset_time is not None else None,
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "decisionIndex": item.decision_index,
        "decisionTime": epoch(item.decision_time),
        "decisionEventTime": epoch(item.decision_event_time),
        "calculationValid": True,
    } for item in items]


def serialize_e_zones(items):
    return [{
        "direction": item.direction,
        "family": item.family,
        "number": item.number,
        "parentType": item.parent_type,
        "parentSourceIndex": item.parent_source_index,
        "parentSourceTime": epoch(item.parent_source_time),
        "parentPrice": str(item.parent_price),
        "parentStopIndex": item.parent_stop_index,
        "parentStopTime": epoch(item.parent_stop_time),
        "parentStopEventTime": epoch(item.parent_stop_event_time),
        "orderDirection": item.order_direction,
        "orderReactionNumber": item.order_reaction_number,
        "orderMode": item.order_mode,
        "orderCauses": list(item.order_causes),
        "orderParentStopCauseTime": (
            epoch(item.order_parent_stop_cause_time)
            if item.order_parent_stop_cause_time is not None else None
        ),
        "orderResetLegResetTime": (
            epoch(item.order_reset_leg_reset_time)
            if item.order_reset_leg_reset_time is not None else None
        ),
        "orderResetLegBreakTime": (
            epoch(item.order_reset_leg_break_time)
            if item.order_reset_leg_break_time is not None else None
        ),
        "orderFirstIndex": item.order_first_index,
        "orderFirstTime": epoch(item.order_first_time),
        "orderBreakIndex": item.order_break_index,
        "orderBreakTime": epoch(item.order_break_time),
        "orderConfirmationTime": epoch(item.order_confirmation_time),
        "orderBoxTop": str(item.order_box_top),
        "orderBoxTopSourceIndex": item.order_box_top_source_index,
        "orderBoxTopSourceTime": epoch(item.order_box_top_source_time),
        "orderBoxBottom": str(item.order_box_bottom),
        "orderBoxBottomSourceIndex": item.order_box_bottom_source_index,
        "orderBoxBottomSourceTime": epoch(item.order_box_bottom_source_time),
        "orderStopLevel": str(item.order_stop_level),
        "orderStopSourceIndex": item.order_stop_source_index,
        "orderStopSourceTime": epoch(item.order_stop_source_time),
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "decisionIndex": item.decision_index,
        "decisionTime": epoch(item.decision_time),
        "decisionEventTime": epoch(item.decision_event_time),
    } for item in items]


def serialize_stopalls(items):
    return [{
        "direction": item.direction,
        "number": item.number,
        "sourceIndex": item.source_index,
        "sourceTime": epoch(item.source_time),
        "price": str(item.price),
        "decisionIndex": item.decision_index,
        "decisionTime": epoch(item.decision_time),
        "decisionEventTime": epoch(item.decision_event_time),
        "gateType": item.gate_type,
        "gateEventTime": epoch(item.gate_event_time),
        "stoppedBehaviorType": item.stopped_behavior_type,
        "stoppedBehaviorKey": item.stopped_behavior_key,
        "stoppedBehaviorCount": item.stopped_behavior_count,
        "underlyingEFamily": item.underlying_e_family,
        "underlyingENumber": item.underlying_e_number,
        "orderDirection": item.order_direction,
        "orderReactionNumber": item.order_reaction_number,
        "orderMode": item.order_mode,
        "orderCauses": list(item.order_causes),
        "orderParentStopCauseTime": (
            epoch(item.order_parent_stop_cause_time)
            if item.order_parent_stop_cause_time is not None else None
        ),
        "orderResetLegResetTime": (
            epoch(item.order_reset_leg_reset_time)
            if item.order_reset_leg_reset_time is not None else None
        ),
        "orderResetLegBreakTime": (
            epoch(item.order_reset_leg_break_time)
            if item.order_reset_leg_break_time is not None else None
        ),
        "orderFirstIndex": item.order_first_index,
        "orderFirstTime": (
            epoch(item.order_first_time) if item.order_first_time is not None else None
        ),
        "orderBreakIndex": item.order_break_index,
        "orderBreakTime": (
            epoch(item.order_break_time) if item.order_break_time is not None else None
        ),
        "orderConfirmationTime": (
            epoch(item.order_confirmation_time)
            if item.order_confirmation_time is not None else None
        ),
        "orderBoxTop": (
            str(item.order_box_top) if item.order_box_top is not None else None
        ),
        "orderBoxTopSourceIndex": item.order_box_top_source_index,
        "orderBoxTopSourceTime": (
            epoch(item.order_box_top_source_time)
            if item.order_box_top_source_time is not None else None
        ),
        "orderBoxBottom": (
            str(item.order_box_bottom) if item.order_box_bottom is not None else None
        ),
        "orderBoxBottomSourceIndex": item.order_box_bottom_source_index,
        "orderBoxBottomSourceTime": (
            epoch(item.order_box_bottom_source_time)
            if item.order_box_bottom_source_time is not None else None
        ),
        "orderStopLevel": (
            str(item.order_stop_level) if item.order_stop_level is not None else None
        ),
        "orderStopSourceIndex": item.order_stop_source_index,
        "orderStopSourceTime": (
            epoch(item.order_stop_source_time)
            if item.order_stop_source_time is not None else None
        ),
        "stopIndex": item.stop_index,
        "stopTime": epoch(item.stop_time) if item.stop_time else None,
        "stopEventTime": epoch(item.stop_event_time) if item.stop_event_time else None,
    } for item in items]


def validate_order_audit_bridge(
    prepared_items, s_zones, e_zones, stopalls,
) -> None:
    """Assert that public behavior Order provenance matches canonical OrderAudit.

    This is a bridge consistency invariant only; it does not choose, rank, or
    reconstruct Orders.  All trading ownership decisions remain in the
    calculation engines.  Every public S/E/StopAll carrying a physical Order
    identity must reference an identity retained by the already-resolved audit.
    The resolved audit must also keep one owner per exact parent-stop cause.
    """
    audit_identities = {
        order_identity(
            int(getattr(item["reaction"], "first_idx")),
            int(getattr(item["reaction"], "break_idx")),
        )
        for item in prepared_items
    }

    missing: list[str] = []
    for behavior_type, items in (
        ("S", s_zones), ("E", e_zones), ("StopAll", stopalls)
    ):
        for item in items:
            first_index = getattr(item, "order_first_index", None)
            break_index = getattr(item, "order_break_index", None)
            if first_index is None or break_index is None:
                continue
            identity = order_identity(int(first_index), int(break_index))
            if identity in audit_identities:
                continue
            missing.append(
                f"{behavior_type}@{getattr(item, 'source_time', None)!s}"
                f"->{identity}"
            )
    if missing:
        raise RuntimeError(
            "OrderAudit bridge invariant failed; public behavior references "
            "an Order identity absent from canonical audit: " + ", ".join(missing)
        )

    parent_owner: dict[tuple[object, object, object, object], tuple[int, int]] = {}
    duplicate_parent_causes: list[str] = []
    for prepared in prepared_items:
        reaction = prepared["reaction"]
        identity = order_identity(
            int(getattr(reaction, "first_idx")),
            int(getattr(reaction, "break_idx")),
        )
        for cause in prepared["causes"]:
            if cause.get("kind") != "parent-stop":
                continue
            key = (
                cause.get("parentType"),
                cause.get("parentFamily"),
                cause.get("eventTime"),
                cause.get("parentSourceTime"),
            )
            previous = parent_owner.setdefault(key, identity)
            if previous != identity:
                duplicate_parent_causes.append(f"{key!r}:{previous}->{identity}")
    if duplicate_parent_causes:
        raise RuntimeError(
            "OrderAudit bridge invariant failed; one exact parent-stop owns "
            "multiple physical Orders: " + ", ".join(duplicate_parent_causes)
        )


def serialize_order_audit(prepared_items, detector):
    """Serialize already-resolved Order Audit identities without business filtering."""
    output = []
    for prepared in prepared_items:
        entry = prepared["entry"]
        reaction = prepared["reaction"]
        crossed = prepared["crossed"]
        first_index = int(getattr(reaction, "first_idx"))
        causes = []
        for cause in prepared["causes"]:
            if cause["kind"] == "parent-stop":
                causes.append({
                    "kind": cause["kind"],
                    "parentType": cause["parentType"],
                    "parentFamily": cause["parentFamily"],
                    "eventTime": epoch(cause["eventTime"]),
                    "parentSourceTime": epoch(cause["parentSourceTime"]),
                })
            else:
                causes.append({
                    "kind": cause["kind"],
                    "resetTime": epoch(cause["resetTime"]),
                    "boundaryBreakTime": epoch(cause["boundaryBreakTime"]),
                })
        output.append({
            "direction": detector.order_direction,
            "reactionNumber": int(
                getattr(reaction, "behavior_public_number", None)
                or entry["reaction_number"]
            ),
            "reactionMode": str(getattr(reaction, "mode")),
            "firstIndex": first_index,
            "firstTime": epoch(detector.candles[first_index].timestamp),
            "boxTopSourceIndex": int(getattr(reaction, "box_top_source_idx")),
            "boxTopSourceTime": display_epoch(getattr(reaction, "box_top_source_time")),
            "boxTop": str(getattr(reaction, "box_top")),
            "boxBottomSourceIndex": int(getattr(reaction, "box_bottom_source_idx")),
            "boxBottomSourceTime": display_epoch(getattr(reaction, "box_bottom_source_time")),
            "boxBottom": str(getattr(reaction, "box_bottom")),
            "breakIndex": int(getattr(reaction, "break_idx")),
            "breakTime": epoch(
                detector.candles[int(getattr(reaction, "break_idx"))].timestamp
            ),
            "stopLevel": str(entry["stop_level"]),
            "stopSourceIndex": entry["stop_source_index"],
            "stopSourceTime": epoch(entry["stop_source_time"]),
            "stopHitIndex": crossed[0] if crossed is not None else None,
            "stopHitTime": epoch(crossed[1]) if crossed is not None else None,
            "stopHitEventTime": epoch(crossed[2]) if crossed is not None else None,
            "causes": causes,
        })
    return sorted(output, key=lambda item: (item["firstTime"], item["breakTime"]))


@dataclass(frozen=True, slots=True)
class EngineBundle:
    reaction: object
    blue_line: object
    a_zone: object
    s_zone: object
    e_zone: object | None
    lifecycle: object | None


@dataclass(frozen=True, slots=True)
class MarketContext:
    seconds: list[object]
    candles: list[object]
    lower_index: object
    chronology: object
    start_index: int
    end_index: int


def parse_arguments(argv=None):
    """Parse and validate the production pipeline command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reaction-engine",
        "--engine",
        dest="reaction_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--blue-line-engine",
        "--blue-engine",
        dest="blue_line_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--a-zone-engine",
        "--a-engine",
        dest="a_zone_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--s-zone-engine",
        "--s-engine",
        dest="s_zone_engine",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--e-zone-engine",
        "--e-engine",
        dest="e_zone_engine",
        type=Path,
        required=False,
    )
    parser.add_argument(
        "--lifecycle-engine",
        "--stopall-engine",
        dest="lifecycle_engine",
        type=Path,
        required=False,
    )
    parser.add_argument(
        "--blue-lines", choices=("enabled", "disabled"), default="enabled"
    )
    parser.add_argument(
        "--a-zones", choices=("enabled", "disabled"), default="enabled"
    )
    parser.add_argument(
        "--s-zones", choices=("enabled", "disabled"), default="enabled"
    )
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--timeframe", type=int, required=True)
    parser.add_argument("--from-time", type=int, required=True)
    parser.add_argument("--to-time", type=int, required=True)
    parser.add_argument(
        "--direction", choices=("bullish", "bearish", "both"), required=True
    )
    args = parser.parse_args(argv)
    if args.timeframe < 1:
        raise ValueError("Timeframe must be at least one second.")
    return args


def load_engines(args, timings: dict[str, float]) -> EngineBundle:
    """Load every configured calculation engine exactly once."""
    reaction = timed(
        timings, "Load Reaction engine", lambda: load_engine(args.reaction_engine)
    )
    blue_line = timed(
        timings,
        "Load Blue Line engine",
        lambda: load_module("blue_line_detector", args.blue_line_engine),
    )
    a_zone = timed(
        timings, "Load A engine", lambda: load_module("a_zone_detector", args.a_zone_engine)
    )
    s_zone = timed(
        timings, "Load S engine", lambda: load_module("s_zone_detector", args.s_zone_engine)
    )
    e_zone = (
        timed(
            timings,
            "Load E engine",
            lambda: load_module("e_zone_detector", args.e_zone_engine),
        )
        if args.e_zone_engine is not None
        else None
    )
    lifecycle_path = args.lifecycle_engine or (_PIPELINE_DIR / "lifecycle_engine.py")
    lifecycle = timed(
        timings,
        "Load Lifecycle engine",
        lambda: load_module("lifecycle_engine", lifecycle_path),
    )
    return EngineBundle(reaction, blue_line, a_zone, s_zone, e_zone, lifecycle)


def prepare_market_context(
    args, engines: EngineBundle, timings: dict[str, float]
) -> MarketContext:
    """Read, isolate, normalize and index the selected raw-data range."""
    source_bytes = timed(
        timings, "Read source file", lambda: args.data.read_bytes()
    )
    # Match the former ``utf-8-sig`` behavior without decoding the entire raw
    # payload to a Python string before orjson parses it.
    source_bytes = source_bytes.removeprefix(b"\xef\xbb\xbf")
    source_rows = timed(
        timings, "Parse source JSON", lambda: orjson.loads(source_bytes)
    )
    # A requested time range is a presentation window only.  Reaction state
    # can remain open past ``to_time`` and be resolved by later RAW chronology;
    # truncating calculation at the visible end manufactures provisional
    # Reactions/Blue/A state that does not exist in a full-file run.  Calculate
    # on the complete physical RAW and apply from/to only during serialization.
    rows = timed(
        timings,
        "Use full RAW calculation context",
        lambda: source_rows,
    )
    if not rows:
        raise ValueError("The selected range contains no raw candles.")

    second_buckets, timeframe_buckets = timed(
        timings,
        "Normalize raw candles",
        lambda: build_candle_buckets(rows, args.timeframe),
    )
    seconds = timed(
        timings,
        "Build lower candle views",
        lambda: build_candle_objects(engines.reaction, second_buckets),
    )
    lower_index = engines.reaction.shared_lower_timeframe_index(seconds)
    candles = (
        seconds
        if args.timeframe == 1
        else timed(
            timings,
            "Build timeframe candle views",
            lambda: build_candle_objects(engines.reaction, timeframe_buckets),
        )
    )
    chronology = engines.reaction.MarketChronology(
        candles, seconds, args.timeframe, lower_index
    )

    # Resolve the visible main-candle range inside the prefix calculation.
    # Bucket boundaries are epoch-aligned exactly as ``build_candle_buckets``
    # constructs them, which also keeps full-run source indexes/ordinals
    # stable in a short-window request.
    main_bucket_times = [int(item["time"]) for item in timeframe_buckets]
    requested_start_bucket = (
        args.from_time
        if args.timeframe == 1
        else args.from_time // args.timeframe * args.timeframe
    )
    requested_end_bucket = (
        args.to_time
        if args.timeframe == 1
        else args.to_time // args.timeframe * args.timeframe
    )
    start_index = bisect_left(main_bucket_times, requested_start_bucket)
    end_index = bisect_left(main_bucket_times, requested_end_bucket + args.timeframe) - 1
    if start_index >= len(candles) or end_index < start_index:
        raise ValueError("The selected range contains no timeframe candles.")
    end_index = min(end_index, len(candles) - 1)

    return MarketContext(
        seconds=seconds,
        candles=candles,
        lower_index=lower_index,
        chronology=chronology,
        start_index=start_index,
        end_index=end_index,
    )

@dataclass(slots=True)
class PipelineState:
    """Mutable calculation state shared across direction serialization passes."""

    directions: tuple[str, ...]
    results: dict[str, object]
    reusable_full_context: bool
    initial_order_geometry: dict[str, object]
    internal_reaction_identities: dict[str, set[tuple[int, int]]]
    full_e_zones: dict[str, list[object]]
    full_e_detectors: dict[str, object]
    full_s_detectors: dict[str, object]
    full_lines_by_direction: dict[str, list[object]]
    full_a_by_direction: dict[str, list[object]]
    invalid_a_identities_by_direction: dict[str, set[tuple[datetime, int]]]
    invalid_s_identities_by_direction: dict[str, set[tuple[datetime, int]]]
    full_s_by_direction: dict[str, list[object]]
    full_s_candidates_by_direction: dict[str, list[object]]


@dataclass(slots=True)
class FullDirectionState:
    """Authoritative full-range behavior state for one trend direction."""

    e_zones: list[object]
    e_detector: object
    s_detector: object
    blue_lines: list[object]
    a_zones: list[object]
    invalid_a_identities: set[tuple[datetime, int]]
    invalid_s_identities: set[tuple[datetime, int]]
    s_zones: list[object]
    s_candidates: list[object]


def create_e_detector(
    direction: str,
    e_engine,
    full_results: dict[str, object],
    s_zones: list[object],
    chronology,
    geometry_detectors: dict[str, object],
    initial_order_audit,
    lifecycle_engine,
    *,
    blocked_order_first_times: set[datetime] | None = None,
    invalid_s_root_identities: set[tuple[datetime, int]] | None = None,
):
    """Construct one E detector from the shared geometry/lifecycle contract."""
    opposite = chronology.opposite_direction(direction)
    end_index = len(chronology.candles) - 1

    def bounded_geometry(geometry_direction, geometry_start, geometry_end):
        """Return raw Reaction geometry inside a closed main-candle range."""
        return geometry_detectors[geometry_direction].first_geometry_after_reset(
            geometry_direction,
            max(0, geometry_start - 1),
            geometry_end,
        )

    def direct_geometry(
        geometry_direction, geometry_start, geometry_end, gate_event
    ):
        return geometry_detectors[geometry_direction].first_order_reaction_after_gate(
            geometry_direction,
            geometry_start,
            geometry_end,
            gate_event,
        )

    return e_engine.EZoneDetector(
        direction,
        full_results[direction].reactions,
        full_results[opposite].reactions,
        s_zones,
        full_results[direction].resets,
        full_results[opposite].resets,
        chronology,
        0,
        end_index,
        bounded_geometry,
        direct_geometry,
        blocked_order_first_times=blocked_order_first_times,
        initial_order_audit=initial_order_audit,
        sequence_priority=lifecycle_engine.sequence_priority,
        invalid_s_root_identities=invalid_s_root_identities,
    )


def calculate_full_direction_state(
    direction: str,
    engines: EngineBundle,
    market: MarketContext,
    full_results: dict[str, object],
    geometry_detectors: dict[str, object],
    initial_order_geometry: dict[str, object],
    timings: dict[str, float],
) -> FullDirectionState:
    """Run Blue→A→S→E calculation and lifecycle reconciliation for one direction."""
    blue_engine = engines.blue_line
    a_engine = engines.a_zone
    s_engine = engines.s_zone
    e_engine = engines.e_zone
    lifecycle_engine = engines.lifecycle
    assert e_engine is not None
    candles = market.candles
    chronology = market.chronology
    opposite = engines.reaction.opposite_direction(direction)

    blue_lines = timed(
        timings,
        f"Blue Line • {direction.title()}",
        lambda: blue_engine.detect_blue_lines(
            direction,
            full_results[direction].reactions,
            chronology,
            full_results[direction].resets,
        ),
    )
    a_zones = timed(
        timings,
        f"A • {direction.title()}",
        lambda: a_engine.detect_a_zones(
            direction,
            full_results[direction].reactions,
            blue_lines,
            chronology,
        ),
    )
    s_detector = s_engine.SZoneDetector(
        direction,
        full_results[direction].reactions,
        full_results[opposite].reactions,
        blue_lines,
        a_zones,
        chronology,
        0,
        len(candles) - 1,
        full_results[opposite].resets,
        initial_order_geometry=initial_order_geometry[direction],
    )
    s_zones = timed(timings, f"S • {direction.title()}", s_detector.detect)
    s_candidates = list(s_zones)

    historical_e_rescues: list[object] = []
    accepted_e_history: list[object] = []

    def collect_accepted_e_history(zones) -> None:
        existing = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in accepted_e_history
        }
        for item in zones:
            # Keep this safeguard intentionally narrow: only E-parented Blue
            # Orders carrying the independent Order_B/reset-leg cause are
            # eligible for later-pass historical preservation.
            if str(getattr(item, "parent_type", "")).upper() != "E":
                continue
            if str(getattr(item, "family", "")).lower() != "blue":
                continue
            if "reset-leg" not in {
                str(value) for value in getattr(item, "order_causes", ())
            }:
                continue
            identity = (
                int(getattr(item, "source_index")),
                getattr(item, "source_time"),
            )
            if identity not in existing:
                accepted_e_history.append(item)
                existing.add(identity)

    def collect_historical_e_rescues(detector) -> None:
        existing = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in historical_e_rescues
        }
        for item in getattr(detector, "historical_rescued_zones", []):
            identity = (
                int(getattr(item, "source_index")),
                getattr(item, "source_time"),
            )
            if identity not in existing:
                historical_e_rescues.append(item)
                existing.add(identity)

    e_detector = create_e_detector(
        direction,
        e_engine,
        full_results,
        s_zones,
        chronology,
        geometry_detectors,
        s_detector.order_audit,
        lifecycle_engine,
    )
    e_zones = timed(
        timings, f"E • {direction.title()} • initial", e_detector.detect
    )
    collect_historical_e_rescues(e_detector)
    collect_accepted_e_history(e_zones)
    valid_s_zones = lifecycle_engine.s_zones_for_module_engines(
        s_zones, e_zones, direction
    )
    if len(valid_s_zones) != len(s_zones):
        e_detector = create_e_detector(
            direction,
            e_engine,
            full_results,
            valid_s_zones,
            chronology,
            geometry_detectors,
            s_detector.order_audit,
            lifecycle_engine,
            blocked_order_first_times={
                getattr(item, "source_time")
                for item in s_zones
                if item not in valid_s_zones
            },
        )
        e_zones = timed(
            timings,
            f"E • {direction.title()} • S reconciliation",
            e_detector.detect,
        )
        collect_historical_e_rescues(e_detector)
        collect_accepted_e_history(e_zones)
        s_zones = valid_s_zones

    candidate_a = lifecycle_engine.visible_a_zones(
        s_detector.eligible_a_zones, s_zones
    )
    candidate_a = lifecycle_engine.visible_a_zones_after_s_stops(
        candidate_a, s_zones, candles
    )
    stage_invalid_a_identities: set[tuple[datetime, int]] = set()
    # Cycle validation must see every S-eligible A, even when a provisional
    # S candidate temporarily hides that A from presentation.  Otherwise a
    # later S reconciliation can remove the provisional S and accidentally
    # resurrect an A that should have been rejected by the stopped S/E owner.
    lifecycle_a_candidates = list(s_detector.eligible_a_zones)
    _calculation_a, invalid_a = lifecycle_engine.split_a_zones_by_dominant_stops(
        lifecycle_a_candidates,
        s_candidates,
        e_zones,
        [],
        candles,
        direction,
        lambda item: e_detector.parent_stop(
            "S" if hasattr(item, "a_source_time") else "E", item
        ),
        trend_reactions=s_detector.trend_reactions,
        confirmation_finder=s_detector.reaction_confirmation_time,
        a_stop_event_finder=lambda item: s_detector.first_a_stop(
            Decimal(str(getattr(item, "price"))),
            s_detector.reaction_confirmation_time(
                s_detector.trend_reactions[int(getattr(item, "reaction_number")) - 1],
                direction,
            ),
        ),
        stage_invalid_a_identities=stage_invalid_a_identities,
    )
    invalid_a_identities = {
        (getattr(item, "source_time"), int(getattr(item, "source_index")))
        for item in invalid_a
    }
    invalid_a_source_times = {source_time for source_time, _ in invalid_a_identities}
    invalid_s = [
        item for item in s_candidates
        if getattr(item, "a_source_time") in invalid_a_source_times
    ]
    invalid_s_identities = {
        (getattr(item, "source_time"), int(getattr(item, "source_index")))
        for item in invalid_s
    }
    stage_invalid_a_source_times = {
        source_time for source_time, _ in stage_invalid_a_identities
    }
    stage_invalid_s_identities = {
        (getattr(item, "source_time"), int(getattr(item, "source_index")))
        for item in s_candidates
        if getattr(item, "a_source_time") in stage_invalid_a_source_times
    }
    # Only S descendants of an A rejected specifically by S-stage ownership
    # are removed from later-stage calculation.  Other suppressed S evidence
    # keeps its established continuation semantics unchanged.
    s_zones = [
        item for item in s_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in stage_invalid_s_identities
    ]

    accepted_a_sources = {
        getattr(item, "source_time")
        for item in s_detector.eligible_a_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in invalid_a_identities
    }
    pending_s_a_sources = {getattr(item, "a_source_time") for item in s_candidates}
    accepted_orders, blocked_order_first_times = lifecycle_engine.resolve_order_context(
        s_detector.order_audit,
        accepted_a_sources,
        set(getattr(e_detector, "blocked_order_first_times", set())),
        invalid_a,
        pending_s_a_sources,
        full_results[opposite].reactions,
        candles,
        direction,
        lambda item: s_detector.first_a_stop(
            Decimal(str(getattr(item, "price"))),
            getattr(item, "source_time"),
        ),
    )
    e_detector = create_e_detector(
        direction,
        e_engine,
        full_results,
        s_zones,
        chronology,
        geometry_detectors,
        accepted_orders,
        lifecycle_engine,
        blocked_order_first_times=blocked_order_first_times,
        invalid_s_root_identities=invalid_s_identities,
    )
    e_zones = timed(
        timings, f"E • {direction.title()} • final audit", e_detector.detect
    )
    collect_historical_e_rescues(e_detector)
    collect_accepted_e_history(e_zones)

    # A still-open S candidate may be decided by the strict stop of a later
    # calculation-accepted physical Order in the same chronology.  Reconcile
    # against accepted ledgers only; arbitrary opposite Reactions are never
    # promoted into Orders by this pass.  Rebuild E once when S provenance or
    # decision chronology changes because E consumes S as authoritative input.
    shared_order_entries = [
        *accepted_orders.values(),
        *e_detector.order_audit.values(),
    ]
    reconciled_s_zones = s_detector.reconcile_shared_order_stops(
        s_zones, shared_order_entries
    )
    if reconciled_s_zones != s_zones:
        s_zones = reconciled_s_zones
        reconciled_by_identity = {
            (getattr(item, "a_source_time"), getattr(item, "source_time")): item
            for item in s_zones
        }
        s_candidates = [
            reconciled_by_identity.get(
                (getattr(item, "a_source_time"), getattr(item, "source_time")),
                item,
            )
            for item in s_candidates
        ]
        e_detector = create_e_detector(
            direction,
            e_engine,
            full_results,
            s_zones,
            chronology,
            geometry_detectors,
            accepted_orders,
            lifecycle_engine,
            blocked_order_first_times=blocked_order_first_times,
            invalid_s_root_identities=invalid_s_identities,
        )
        e_zones = timed(
            timings,
            f"E • {direction.title()} • shared Order-stop reconciliation",
            e_detector.detect,
        )
        collect_historical_e_rescues(e_detector)
        collect_accepted_e_history(e_zones)

    calculation_s_candidates = [
        item for item in s_candidates
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in stage_invalid_s_identities
    ]
    consumed_s_evidence = lifecycle_engine.consumed_s_evidence_after_larger_stop(
        calculation_s_candidates,
        s_zones,
        e_zones,
        direction,
        lambda item: e_detector.parent_stop("E", item),
        candles,
    )
    for evidence_s, original_owner in consumed_s_evidence:
        owner = next(
            (
                item for item in e_zones
                if int(getattr(item, "source_index")) == int(getattr(original_owner, "source_index"))
                and getattr(item, "source_time") == getattr(original_owner, "source_time")
            ),
            None,
        )
        if owner is None:
            continue
        continuation = e_detector.continuation_chain_from_s(owner, evidence_s)
        e_zones = e_detector.replace_with_earlier_continuation(
            e_zones, owner, continuation
        )

    # Continuation replacement happens after the detector's normal final audit.
    # Rebuild the accepted ledger from the actual final E state so OrderAudit
    # cannot lag behind a branch that the lifecycle has just made authoritative.
    e_zones = e_detector.rebuild_accepted_order_audit(
        e_zones, supplemental_s_zones=[item for item, _ in consumed_s_evidence]
    )

    s_zones = [
        item for item in s_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in invalid_s_identities
    ]

    # Preserve presentation-only historical E acceptance without changing
    # calculation ownership. An earlier accepted E that disappears during a
    # later detector rebuild is recoverable only when it is not merely a
    # hidden intermediate parent of a surviving final E. Hidden intermediate
    # parents remain intentionally non-public; independent accepted history is
    # retained for reporting.
    if accepted_e_history:
        historical_e_rescues.extend(accepted_e_history)
    if historical_e_rescues:
        historical_e_rescues = e_detector.resolve_same_source_conflicts(
            historical_e_rescues
        )
        final_e_ids = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in e_zones
        }
        referenced_e_parent_ids = {
            (
                int(getattr(item, "parent_source_index")),
                getattr(item, "parent_source_time"),
            )
            for item in e_zones
            if str(getattr(item, "parent_type", "")).upper() == "E"
        }
        def blocked_by_dominant_final_e(item) -> bool:
            candidate_priority = lifecycle_engine.sequence_priority(
                "e", str(getattr(item, "family"))
            )
            candidate_decision = getattr(item, "decision_event_time")
            for owner in e_zones:
                if getattr(owner, "source_time") >= getattr(item, "source_time"):
                    continue
                owner_priority = lifecycle_engine.sequence_priority(
                    "e", str(getattr(owner, "family"))
                )
                if owner_priority <= candidate_priority:
                    continue
                stop = e_detector.parent_stop("E", owner)
                if stop is None or stop[1] >= candidate_decision:
                    return True
            return False

        e_detector.historical_rescued_zones = [
            item for item in historical_e_rescues
            if (int(getattr(item, "source_index")), getattr(item, "source_time"))
            not in final_e_ids
            and (int(getattr(item, "source_index")), getattr(item, "source_time"))
            not in referenced_e_parent_ids
            and not blocked_by_dominant_final_e(item)
        ]

    return FullDirectionState(
        e_zones=e_zones,
        e_detector=e_detector,
        s_detector=s_detector,
        blue_lines=blue_lines,
        a_zones=a_zones,
        invalid_a_identities=invalid_a_identities,
        invalid_s_identities=invalid_s_identities,
        s_zones=s_zones,
        s_candidates=s_candidates,
    )


def prepare_pipeline_state(
    args,
    engines: EngineBundle,
    market: MarketContext,
    timings: dict[str, float],
) -> PipelineState:
    """Run shared calculation stages once and retain reusable detector state."""
    engine = engines.reaction
    e_engine = engines.e_zone
    seconds = market.seconds
    candles = market.candles
    chronology = market.chronology
    initial_order_geometry = {
        direction: engine.directional_a_stop_order_finder(
            candles, seconds, direction
        )
        for direction in ("bullish", "bearish")
    }
    directions = ("bullish", "bearish") if args.direction == "both" else (args.direction,)
    behavior_modules_enabled = (
        args.blue_lines == "enabled"
        or args.a_zones == "enabled"
        or args.s_zones == "enabled"
    )
    required_directions = (
        ("bullish", "bearish") if behavior_modules_enabled else directions
    )
    reusable_full_context = e_engine is not None and args.s_zones == "enabled"

    full_e_zones: dict[str, list[object]] = {}
    full_e_detectors: dict[str, object] = {}
    full_s_detectors: dict[str, object] = {}
    full_lines_by_direction: dict[str, list[object]] = {}
    full_a_by_direction: dict[str, list[object]] = {}
    invalid_a_identities_by_direction: dict[str, set[tuple[datetime, int]]] = {}
    invalid_s_identities_by_direction: dict[str, set[tuple[datetime, int]]] = {}
    full_s_by_direction: dict[str, list[object]] = {}
    full_s_candidates_by_direction: dict[str, list[object]] = {}

    if reusable_full_context:
        geometry_detectors = {
            direction: engine.UnifiedReactionDetector(
                candles, seconds, 0, len(candles) - 1, direction
            )
            for direction in ("bullish", "bearish")
        }
        results = {
            direction: timed(
                timings,
                f"Reaction geometry • {direction.title()}",
                detector.detect,
            )
            for direction, detector in geometry_detectors.items()
        }
        _, _, internal_reaction_identities, _ = timed(
            timings,
            "Internal Reaction ownership",
            lambda: engine.build_behavior_reaction_views(results, chronology),
        )
        for direction in directions:
            state = calculate_full_direction_state(
                direction,
                engines,
                market,
                results,
                geometry_detectors,
                initial_order_geometry,
                timings,
            )
            full_e_zones[direction] = state.e_zones
            full_e_detectors[direction] = state.e_detector
            full_s_detectors[direction] = state.s_detector
            full_lines_by_direction[direction] = state.blue_lines
            full_a_by_direction[direction] = state.a_zones
            invalid_a_identities_by_direction[direction] = state.invalid_a_identities
            invalid_s_identities_by_direction[direction] = state.invalid_s_identities
            full_s_by_direction[direction] = state.s_zones
            full_s_candidates_by_direction[direction] = state.s_candidates
    else:
        results = {
            direction: timed(
                timings,
                f"Reaction • {direction.title()}",
                lambda direction=direction: engine.UnifiedReactionDetector(
                    candles, seconds, 0, len(candles) - 1, direction
                ).detect(),
            )
            for direction in required_directions
        }
        if behavior_modules_enabled:
            _, _, internal_reaction_identities, _ = timed(
                timings,
                "Internal Reaction ownership",
                lambda: engine.build_behavior_reaction_views(results, chronology),
            )
        else:
            internal_reaction_identities = {"bullish": set(), "bearish": set()}

    return PipelineState(
        directions=tuple(directions),
        results=results,
        reusable_full_context=reusable_full_context,
        initial_order_geometry=initial_order_geometry,
        internal_reaction_identities=internal_reaction_identities,
        full_e_zones=full_e_zones,
        full_e_detectors=full_e_detectors,
        full_s_detectors=full_s_detectors,
        full_lines_by_direction=full_lines_by_direction,
        full_a_by_direction=full_a_by_direction,
        invalid_a_identities_by_direction=invalid_a_identities_by_direction,
        invalid_s_identities_by_direction=invalid_s_identities_by_direction,
        full_s_by_direction=full_s_by_direction,
        full_s_candidates_by_direction=full_s_candidates_by_direction,
    )


@dataclass(slots=True)
class DirectionRangeState:
    """Unserialized calculation state for one requested direction/range."""

    blue_lines: list[object]
    a_zones: list[object]
    s_candidates: list[object]
    accepted_s_zones: list[object]
    e_zones: list[object]
    invalid_a_identities: set[tuple[datetime, int]]
    invalid_s_identities: set[tuple[datetime, int]]


@dataclass(slots=True)
class DirectionVisibilityState:
    """Final public behavior state after lifecycle and internal-Reaction rules."""

    blue_lines: list[object]
    a_zones: list[object]
    s_zones: list[object]
    e_zones: list[object]
    stopalls: list[object]
    prepared_order_audit: list[object]


def calculate_direction_range_state(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    timings: dict[str, float],
) -> DirectionRangeState:
    """Collect detector output for one requested direction before visibility rules."""
    result = state.results[direction]
    opposite = engines.reaction.opposite_direction(direction)
    start_index = market.start_index
    end_index = market.end_index

    requires_blue_lines = (
        args.blue_lines == "enabled"
        or args.a_zones == "enabled"
        or args.s_zones == "enabled"
    )
    if state.reusable_full_context and requires_blue_lines:
        blue_lines = [
            item
            for item in state.full_lines_by_direction[direction]
            if start_index <= int(getattr(item, "source_index")) <= end_index
        ]
    elif requires_blue_lines:
        blue_lines = timed(
            timings,
            f"Blue Line - {direction.title()}",
            lambda: engines.blue_line.detect_blue_lines(
                direction,
                result.reactions,
                market.chronology,
                result.resets,
            ),
        )
    else:
        blue_lines = []

    requires_a_zones = args.a_zones == "enabled" or args.s_zones == "enabled"
    if state.reusable_full_context and requires_a_zones:
        a_zones = [
            item
            for item in state.full_a_by_direction[direction]
            if start_index <= int(getattr(item, "source_index")) <= end_index
        ]
    elif requires_a_zones:
        a_zones = timed(
            timings,
            f"A - {direction.title()}",
            lambda: engines.a_zone.detect_a_zones(
                direction,
                result.reactions,
                blue_lines,
                market.chronology,
            ),
        )
    else:
        a_zones = []

    s_candidates: list[object] = []
    accepted_s_zones: list[object] = []
    if args.s_zones == "enabled":
        if state.reusable_full_context:
            s_candidates = state.full_s_candidates_by_direction[direction]
            accepted_s_zones = state.full_s_by_direction[direction]
            a_zones = state.full_s_detectors[direction].eligible_a_zones
        else:
            s_detector = engines.s_zone.SZoneDetector(
                direction,
                result.reactions,
                state.results[opposite].reactions,
                blue_lines,
                a_zones,
                market.chronology,
                0,
                len(market.candles) - 1,
                state.results[opposite].resets,
                initial_order_geometry=state.initial_order_geometry[direction],
            )
            s_candidates = timed(
                timings, f"S - {direction.title()}", s_detector.detect
            )
            state.full_s_detectors[direction] = s_detector
            accepted_s_zones = s_candidates
            a_zones = s_detector.eligible_a_zones

    return DirectionRangeState(
        blue_lines=blue_lines,
        a_zones=a_zones,
        s_candidates=s_candidates,
        accepted_s_zones=accepted_s_zones,
        e_zones=list(state.full_e_zones.get(direction, [])),
        invalid_a_identities=state.invalid_a_identities_by_direction.get(
            direction, set()
        ),
        invalid_s_identities=state.invalid_s_identities_by_direction.get(
            direction, set()
        ),
    )


def finalize_direction_visibility(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    direction_state: DirectionRangeState,
    timings: dict[str, float],
) -> DirectionVisibilityState:
    """Apply lifecycle, range and Internal-Reaction rules to detector output."""
    lifecycle_engine = engines.lifecycle
    opposite = engines.reaction.opposite_direction(direction)
    start_index = market.start_index
    end_index = market.end_index

    visible_a_zones = lifecycle_engine.visible_a_zones(
        direction_state.a_zones, direction_state.accepted_s_zones
    )
    visible_a_zones = lifecycle_engine.visible_a_zones_after_s_stops(
        visible_a_zones,
        direction_state.accepted_s_zones,
        market.candles,
    )

    e_zones = list(direction_state.e_zones)
    stopalls: list[object] = []
    stopall_enabled = (
        args.lifecycle_engine is not None
        and engines.e_zone is not None
        and args.s_zones == "enabled"
    )
    if stopall_enabled and direction in state.full_e_detectors:
        e_zones, stopalls = lifecycle_engine.reconcile_stopall_lifecycle(
            state.full_e_detectors[direction],
            direction_state.accepted_s_zones,
            e_zones,
            market.chronology,
            direction,
            lambda label, work: timed(timings, label, work),
        )

    if direction in state.full_e_detectors:
        # Dominant E ownership drives StopAll.  After those hard boundaries are
        # fixed, restore direct E1 roots of accepted S behaviors so independent
        # E formation remains visible without letting lower-priority roots
        # rewrite the dominant StopAll sequence.
        detector = state.full_e_detectors[direction]
        e_zones = detector.restore_independent_s_roots(e_zones)
        # Root restoration is a calculation-valid acceptance step that occurs
        # after the detector's normal ledger rebuild.  Sync only missing audit
        # identities while preserving Orders already needed by StopAll/history.
        e_zones = detector.ensure_accepted_order_audit(e_zones)
        visibility_stop = lambda item: detector.parent_stop(
            "S" if hasattr(item, "a_source_time") else "E", item
        )
    else:
        visibility_stop = lambda item: state.full_s_detectors[direction].first_a_stop(
            Decimal(str(item.price)), item.decision_event_time
        )

    e_zones, visible_s_zones, visible_a_zones = timed(
        timings,
        f"Apply visibility filters - {direction.title()}",
        lambda: lifecycle_engine.finalize_behavior_visibility(
            visible_a_zones,
            direction_state.s_candidates,
            e_zones,
            stopalls,
            direction,
            direction_state.invalid_s_identities,
            visibility_stop,
            lambda item: state.full_s_detectors[direction].candidate_event_time(
                item.source_index, item.price, item.source_time
            ),
            market.candles,
            all_a_zones=direction_state.a_zones,
        ),
    )

    visible_s_zones = [
        item
        for item in visible_s_zones
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]
    visible_a_zones = [
        item
        for item in visible_a_zones
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]
    e_zones = [
        item
        for item in e_zones
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]
    stopalls = [
        item
        for item in stopalls
        if start_index <= int(getattr(item, "source_index")) <= end_index
    ]

    display_a_zones = [
        item
        for item in visible_a_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in direction_state.invalid_a_identities
    ]
    display_s_zones = [
        item
        for item in visible_s_zones
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in direction_state.invalid_s_identities
    ]
    # OrderAudit provenance is calculated on the full RAW, not clipped by the
    # presentation range.  A public S/E/StopAll inside the requested window may
    # legitimately reference an accepted A-owned Order whose First/A source is
    # before ``start_index``.  Keep all calculation-accepted A sources here;
    # presentation filtering is handled separately by required Order identities.
    order_audit_a_sources = {
        getattr(item, "source_time")
        for item in state.full_a_by_direction.get(direction, direction_state.a_zones)
        if (getattr(item, "source_time"), int(getattr(item, "source_index")))
        not in direction_state.invalid_a_identities
    }

    all_behavior_reactions = [
        reaction
        for result_item in state.results.values()
        for reaction in result_item.reactions
    ]
    engines.blue_line.mark_internal_blue_lines(
        direction_state.blue_lines,
        state.results[direction].reactions,
        all_behavior_reactions,
    )
    display_a_zones, display_s_zones, e_zones, stopalls = (
        lifecycle_engine.filter_internal_behavior_outputs(
            display_a_zones,
            display_s_zones,
            e_zones,
            stopalls,
            state.results[opposite].reactions,
            state.internal_reaction_identities.get(opposite, set()),
            all_behavior_reactions,
        )
    )

    # Historical rescue is presentation-only.  It runs after all lifecycle,
    # StopAll, visibility, and OrderAudit ownership calculations so restoring a
    # fully formed historical E can never rewrite an already-correct behavior,
    # number, parent, StopAll sequence, or physical Order provenance.
    if direction in state.full_e_detectors:
        detector = state.full_e_detectors[direction]
        occupied_e_sources = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in e_zones
        }
        occupied_stopall_sources = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in stopalls
        }
        rescued_e_zones = [
            item
            for item in getattr(detector, "historical_rescued_zones", [])
            if start_index <= int(getattr(item, "source_index")) <= end_index
            and (int(getattr(item, "source_index")), getattr(item, "source_time"))
                not in occupied_e_sources
            and (int(getattr(item, "source_index")), getattr(item, "source_time"))
                not in occupied_stopall_sources
            and not lifecycle_engine.forbidden_internal_order_b(
                item, state.internal_reaction_identities.get(opposite, set())
            )
        ]
        if rescued_e_zones:
            e_zones = sorted(
                [*e_zones, *rescued_e_zones],
                key=lambda item: (
                    getattr(item, "source_time"),
                    int(getattr(item, "source_index")),
                    getattr(item, "decision_event_time"),
                ),
            )

    required_order_identities = {
        order_identity(int(first_index), int(break_index))
        for item in [*display_s_zones, *e_zones, *stopalls]
        for first_index, break_index in [(
            getattr(item, "order_first_index", None),
            getattr(item, "order_break_index", None),
        )]
        if first_index is not None and break_index is not None
    }
    prepared_order_audit = (
        lifecycle_engine.prepare_order_audit(
            state.full_e_detectors[direction],
            start_index,
            end_index,
            state.full_s_detectors.get(direction),
            order_audit_a_sources,
            required_order_identities,
        )
        if direction in state.full_e_detectors
        else []
    )
    if direction in state.full_e_detectors:
        validate_order_audit_bridge(
            prepared_order_audit, display_s_zones, e_zones, stopalls
        )
    return DirectionVisibilityState(
        blue_lines=engines.blue_line.public_blue_lines(direction_state.blue_lines),
        a_zones=display_a_zones,
        s_zones=display_s_zones,
        e_zones=e_zones,
        stopalls=stopalls,
        prepared_order_audit=prepared_order_audit,
    )


def serialize_direction_payload(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    visibility: DirectionVisibilityState,
    timings: dict[str, float],
):
    """Serialize one direction without applying any trading rule."""
    result = state.results[direction]
    reactions, resets = timed(
        timings,
        f"Serialize Reaction - {direction.title()}",
        lambda: serialize(
            result,
            market.start_index,
            market.end_index,
            reaction_transform=lambda item: engines.reaction.published_reaction_candidate(
                direction, item, market.chronology
            ),
        ),
    )

    def build_payload():
        return {
            "reactions": reactions,
            "resets": resets,
            "blueLines": serialize_blue_lines(
                visibility.blue_lines if args.blue_lines == "enabled" else [],
                market.start_index,
                market.end_index,
            ),
            "aZones": serialize_a_zones(
                visibility.a_zones if args.a_zones == "enabled" else []
            ),
            "sZones": serialize_s_zones(visibility.s_zones),
            "eZones": serialize_e_zones(visibility.e_zones),
            "stopAlls": serialize_stopalls(visibility.stopalls),
            "orderAudit": (
                serialize_order_audit(
                    visibility.prepared_order_audit,
                    state.full_e_detectors[direction],
                )
                if direction in state.full_e_detectors
                else []
            ),
        }

    return timed(
        timings, f"Serialize output - {direction.title()}", build_payload
    )


def build_direction_output(
    direction: str,
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    timings: dict[str, float],
):
    """Calculate, finalize and serialize one requested trend direction."""
    direction_state = calculate_direction_range_state(
        direction, args, engines, market, state, timings
    )
    visibility = finalize_direction_visibility(
        direction,
        args,
        engines,
        market,
        state,
        direction_state,
        timings,
    )
    return serialize_direction_payload(
        direction, args, engines, market, state, visibility, timings
    )

def build_response_payload(
    args,
    engines: EngineBundle,
    market: MarketContext,
    state: PipelineState,
    timings: dict[str, float],
    pipeline_started: float,
) -> dict[str, object]:
    """Build the public response envelope around serialized direction outputs."""
    e_enabled = engines.e_zone is not None and args.s_zones == "enabled"
    stop_all_enabled = (
        args.lifecycle_engine is not None
        and engines.e_zone is not None
        and args.s_zones == "enabled"
    )
    payload: dict[str, object] = {
        "engine": "reaction_engine.py",
        "version": engines.reaction.REACTION_ENGINE_VERSION,
        "pipelineVersion": TRADING_PIPELINE_VERSION,
        "blueLineVersion": engines.blue_line.BLUE_LINE_VERSION,
        "aVersion": engines.a_zone.A_ZONE_VERSION,
        "sVersion": engines.s_zone.S_ZONE_VERSION,
        "eVersion": engines.e_zone.E_ZONE_VERSION if engines.e_zone else None,
        "stopAllVersion": (
            engines.lifecycle.STOP_ALL_VERSION
            if args.lifecycle_engine is not None
            else None
        ),
        "blueLinesEnabled": args.blue_lines == "enabled",
        "aEnabled": args.a_zones == "enabled",
        "sEnabled": args.s_zones == "enabled",
        "eEnabled": e_enabled,
        "stopAllEnabled": stop_all_enabled,
        "timeframe": args.timeframe,
        "actualFrom": epoch(market.candles[market.start_index].timestamp),
        "actualTo": epoch(market.candles[market.end_index].timestamp),
        "directions": {},
    }
    direction_payloads = payload["directions"]
    assert isinstance(direction_payloads, dict)
    for direction in state.directions:
        direction_payloads[direction] = build_direction_output(
            direction, args, engines, market, state, timings
        )
    payload["timings"] = {
        "phasesMs": {
            label: round(duration, 2) for label, duration in timings.items()
        },
        "bridgeTotalMs": round((perf_counter() - pipeline_started) * 1000, 2),
    }
    return payload


def main() -> int:
    pipeline_started = perf_counter()
    timings: dict[str, float] = {}
    validation_started = perf_counter()
    emit_progress("started", "Validate request")
    args = parse_arguments()
    validation_ms = (perf_counter() - validation_started) * 1000
    timings["Validate request"] = validation_ms
    emit_progress("completed", "Validate request", validation_ms)

    engines = load_engines(args, timings)
    market = prepare_market_context(args, engines, timings)
    state = prepare_pipeline_state(args, engines, market, timings)
    payload = build_response_payload(
        args, engines, market, state, timings, pipeline_started
    )

    emit_progress(
        "completed",
        "Calculation pipeline",
        (perf_counter() - pipeline_started) * 1000,
    )
    encoding_started = perf_counter()
    encoded_payload = json.dumps(payload, separators=(",", ":"))
    emit_progress(
        "completed",
        "Encode response JSON",
        (perf_counter() - encoding_started) * 1000,
    )
    print(encoded_payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        raise SystemExit(1)
```
<!-- SOURCE_FILE_END:trading_pipeline.py -->
### 26.8 `direction_policy.py`

- Source version: `1.0.0`
- Last modified declared by module: `not declared by module`
- Lines: `70`
- Role: Direction-neutral Bullish/Bearish price-geometry policy primitives.
- Optional integrity SHA-256: `a27ac63c2f066311c9381e2ead6fb44f0789f423a37b465da65c80e6329397ea`

<!-- SOURCE_FILE_BEGIN:direction_policy.py:SHA256=a27ac63c2f066311c9381e2ead6fb44f0789f423a37b465da65c80e6329397ea -->
```python
"""Shared, behavior-neutral Bullish/Bearish direction primitives.

This module deliberately contains only price-direction semantics.  It does not
own chronology, lifecycle, numbering, visibility, or trading state.  Keeping
these primitives in one place prevents Bullish/Bearish drift while preserving
the existing algorithms in their owning engines.
"""

from __future__ import annotations

DIRECTION_POLICY_VERSION = "1.0.0"

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

Direction = Literal["bullish", "bearish"]


@dataclass(frozen=True, slots=True)
class DirectionPolicy:
    direction: Direction
    extreme_attr: Literal["low", "high"]
    opposite_extreme_attr: Literal["high", "low"]
    first_reaction_tag: Literal["RED", "GREEN"]
    context_tag: Literal["GREEN", "RED"]

    @property
    def opposite_direction(self) -> Direction:
        return "bearish" if self.direction == "bullish" else "bullish"

    def strict_cross(self, value: Decimal, level: Decimal) -> bool:
        return value < level if self.direction == "bullish" else value > level

    def better_extreme(self, value: Decimal, current: Decimal) -> bool:
        return value < current if self.direction == "bullish" else value > current

    def choose_extreme(self, left: Decimal, right: Decimal) -> Decimal:
        return min(left, right) if self.direction == "bullish" else max(left, right)

    def confirmation_cross(self, value: Decimal, level: Decimal) -> bool:
        """Reaction confirmation mirror: high>top vs low<bottom.

        ``value`` is the already-selected confirmation-side price.
        """
        return value > level if self.direction == "bullish" else value < level


def policy_for(direction: str) -> DirectionPolicy:
    if direction == "bullish":
        return BULLISH
    if direction == "bearish":
        return BEARISH
    raise ValueError("Direction must be 'bullish' or 'bearish'.")


BULLISH = DirectionPolicy(
    direction="bullish",
    extreme_attr="low",
    opposite_extreme_attr="high",
    first_reaction_tag="RED",
    context_tag="GREEN",
)
BEARISH = DirectionPolicy(
    direction="bearish",
    extreme_attr="high",
    opposite_extreme_attr="low",
    first_reaction_tag="GREEN",
    context_tag="RED",
)
```
<!-- SOURCE_FILE_END:direction_policy.py -->
### 26.9 `core_utils.py`

- Source version: `1.0.0`
- Last modified declared by module: `not declared by module`
- Lines: `29`
- Role: Small shared stateless primitives for Decimal normalization and physical Order identity.
- Optional integrity SHA-256: `3dae390ae77b72965f5799f7c132c4eba203775d5e72761fd7dd60c90f8578de`

<!-- SOURCE_FILE_BEGIN:core_utils.py:SHA256=3dae390ae77b72965f5799f7c132c4eba203775d5e72761fd7dd60c90f8578de -->
```python
"""Small behavior-neutral primitives shared by calculation engines."""

from __future__ import annotations

CORE_UTILS_VERSION = "1.0.0"

from decimal import Decimal
from typing import TypeAlias


def as_decimal(value: object) -> Decimal:
    """Preserve Decimal values and normalize other numeric inputs losslessly."""
    return value if isinstance(value, Decimal) else Decimal(str(value))


OrderIdentity: TypeAlias = tuple[int, int]


def order_identity(first_index: object, break_index: object) -> OrderIdentity:
    """Return the canonical physical Order/Reaction geometry identity."""
    return int(first_index), int(break_index)


def reaction_identity(reaction: object) -> OrderIdentity:
    """Return ``(FirstIndex, BreakIndex)`` for a Reaction-like object."""
    return order_identity(
        getattr(reaction, "first_idx"),
        getattr(reaction, "break_idx"),
    )
```
<!-- SOURCE_FILE_END:core_utils.py -->

## 27. Embedded-source recovery and direct synchronization contract

To recover the production implementation from this Markdown file:

1. Locate each `SOURCE_FILE_BEGIN:<name>` marker in Section 26.
2. Copy the complete text in the immediately following Python code fence through its closing fence.
3. Write that text as UTF-8 to `<name>` without editing imports, comments, whitespace-sensitive source text, constants, schemas, or helper code.
4. Recover all nine project-owned modules before attempting to run the pipeline.
5. Compile the recovered modules and install the declared runtime dependency `orjson` if it is not already present.

During generation of this Reference, each recovered code block is compared **directly, character-by-character and line-by-line** with the current production module. Optional SHA-256 values are retained only as integrity metadata and are not the semantic synchronization method.

The embedded code is intentionally complete. No `...`, `code omitted`, `unchanged from previous version`, external repository pointer, or missing project helper is permitted.

## 28. Final canonical reconstruction contract

This file is simultaneously an algorithm specification, engineering reconstruction manual, architecture/data/lifecycle/serialization contract, directional-mirror specification, and a self-contained archive of the complete required project-owned production source.

**Document revision `5.4.8-HPZR1` changes only `s_zone_detector.py` (`4.19.0` → `4.20.0`).** Stopped-A Order_A is now permanently owned by the first opposite canonical Order, without native Mode-B refresh. This changes dependent S/E/StopAll and cause/visibility results; unchanged Reaction, Reset, Blue, A and shared physical Order geometry remain intact. `lifecycle_engine.py` remains at `1.15.2`. This document embeds the updated complete nine-module source snapshot.

A future behavioral revision must update the semantic rules and both standalone direction References together. A future implementation-only refactor must update implementation/performance notes, symbol coverage, source manifest, and embedded source without inventing a new trading rule.

## 29. Mandatory final verification report

The historical 5.4.5-HPZR2 generation audit is retained below for provenance. The V5.4.6-HPZR1 implementation has separately been validated as described above and in Section 29A:

```text
All production files read completely: YES

Bullish semantic audit: PASS
Bearish semantic audit: PASS
Mirror audit: PASS

Doji invariant verified: PASS
Strict crossing verified: PASS
Decimal contract verified: PASS
Lower-TF chronology verified: PASS
Full RAW authority verified: PASS

Reaction documented completely: PASS
Reset documented completely: PASS
Blue documented completely: PASS
A documented completely: PASS
S documented completely: PASS
E documented completely: PASS
StopAll documented completely: PASS
Order documented completely: PASS
OrderAudit documented completely: PASS

Dataclass schemas synchronized: PASS
Serialization synchronized: PASS
Symbol index synchronized: PASS

Complete project-owned production code embedded: PASS
Any omitted required project code: NO
Any external project Source dependency: NO

Standalone reconstruction possible: PASS
```

These PASS states require direct source reading/comparison and compilation/reconstruction checks; they are not inferred merely from matching hashes.

Concrete verification evidence for this documentation revision:

- **Direct embedded-source recovery:** all nine code blocks were extracted from this Reference and compared character-by-character with the current production modules: PASS.
- **Recovered-source compilation:** all nine extracted modules compile successfully: PASS.
- **Standalone recovered execution:** the complete engine extracted independently from this Reference was run on the 36,821-row USOIL 5s regression RAW at 30s for `direction=both`; all stable JSON values matched the current production execution value-by-value, with only runtime timing telemetry excluded from equality: PASS.
- **Current production regression sanity run:** the same RAW completed both Bullish and Bearish full calculation/serialization successfully.
- **Reflected-market mirror validation:** on a 1,304-row / 220-main-candle no-Doji USOIL window, `Bullish(original) ↔ Bearish(reflected)` and `Bearish(original) ↔ Bullish(reflected)` matched field-by-field after the documented geometry mapping, including Reaction/Reset/Blue/A and the route containing S/E/OrderAudit: PASS.
- The no-Doji condition is intentional for the mathematical reflection test because the production invariant `Doji = GREEN` must never be altered merely to force synthetic color symmetry.

## 29A. V5.4.6-HPZR1 verified correction and regression evidence

- Changed production owner: `lifecycle_engine.py` v1.15.1. Only native Mode-B S Red can consume the `opposite-s-group-stop` gate; other gates, chronology, geometry, and public schema are unchanged.
- Full `RAW FOREXCOM_XAUUSD 5S FROM 2026-08-25 03-53-30 TO 2026-09-19 00-29-30.json` (309,906 records) completed both directions at 30s for the unchanged baseline and the new Source.
- Four other complete RAW inputs (XAUUSD 1s, shorter XAUUSD 5s, two USOIL 5s), and one additional August–September XAUUSD prefix, were compared in both directions: 12 direction-runs total. Reaction, Reset, Blue, and A public payloads were identical for each baseline/updated pair.
- Three requested Bearish 30s cases now produce `S Red` at `2026-08-26 11:04:00`, `2026-08-26 23:00:00`, and `2026-08-28 08:56:30`; the third historical request `08:57:00` is not the source price candle.
- All final `opposite-s-group-stop` objects in the complete updated XAUUSD RAW have native Mode-B formation Orders in both directions. The independent `sequence-group-stop` and `stopall-stop` branches are unmodified.
- The physical OrderAudit set is unchanged in complete XAUUSD runs; one additional reset-leg identity is accepted in the first USOIL dataset following downstream reconciliation. This is a dependent output change rather than a geometry rewrite.
- Every embedded code module was compared byte-for-byte with the updated Source/current unchanged peers and compiled. Documentation-only historical expectations that do not reproduce from current complete-RAW Source have been distinguished from current regression assertions.

## 29B. V5.4.7-HPZR1 verified Red-boundary correction

- Changed production owner: `lifecycle_engine.py` v1.15.2; two pending-Blue reset points after accepted Red S/E, without geometry or serialization changes.
- Five complete RAW inputs were run at 30s for both Bullish and Bearish (ten direction runs), with an additional authoritative August–September XAUUSD prefix Bearish run. Full XAUUSD 309,906-row calculation completed in both directions.
- Before/after byte-equivalent serialized Reaction, Reset, Blue, and A for each pair; physical geometry of every common accepted Order is unchanged; all public S/E/StopAll Order identities exist in canonical OrderAudit.
- Bearish complete XAUUSD S Red retained at `2026-08-26 11:04:00`, `2026-08-26 23:00:00`, `2026-08-28 08:56:30`, and corrected at `2026-08-31 12:35:30`; no StopAll occupies those sources.
- Confirmed Bearish StopAll `2026-09-04 02:36:00` retains `opposite-s-group-stop` with repeated `E1 Blue` count four. Other StopAll differences after changed Red boundaries are downstream, not independent geometry changes.
- Native Mode-B prerequisite, strict crossing/Decimal/Doji semantics, exact S/E Blue-group keys, hard StopAll reset, E-driven StopAll gates, and Bullish/Bearish direction-invariant Red boundary remain intact.
- The source manifest/hash, complete embedded nine-module source snapshot, and AST symbol line index were regenerated and checked against production bytes.

## 29C. V5.4.8-HPZR1 immutable Order_A validation

- Modified source: `s_zone_detector.py` v4.20.0 only; native Mode-B stopped-A refresh and cause-reassignment helper removed. Existing first-order chronology and A-to-S decision logic retained.
- Verified both directions on all five available complete RAW inputs at 30s, compared to the V5.4.7 snapshots, plus one focused August 25 input. Identical serialized Reaction, Reset, Blue and A for every comparison; every common Order retains identical physical geometry and confirmation/stop fields. Every public S/E/StopAll Order identity resolves in OrderAudit; exact parent-stop causes have a single physical owner.
- Bearish full XAUUSD: accepted A source `2026-08-25 09:32:30`, first strict A stop `09:36:30`, and canonical first opposite Order First/Break `(689,693)` / First `09:38:00`. Its final OrderAudit retains both this A and independent StopAll1 creation causes. The subsequent `09:42:00` Order receives no recycled A cause. No time/symbol-dependent code exists.
- Full-RAW Bearish `2026-08-26 11:04:00`, `2026-08-26 23:00:00`, and `2026-08-28 08:56:30` remain S Red. The historically requested `2026-08-31 12:35:30` S Red becomes S Blue because the newly authoritative first Order has First `12:31:00` instead of refreshed First `12:34:00`. This is an explicitly disclosed, causally related semantic change under the new first-Order_A rule, not an unrelated geometry mutation.
- The earlier V5.4.5 September 9 `04:29:30` S Red no longer occurs; `04:45:00` S Blue is valid under first-order ownership. Preserve that old result as a historical regression for the superseded revision, not a current expected label.
- StopAll counters, exact strict Decimal crossing, directional mirror, physical Order_B/Reset-leg cause, accepted-live/carried-live use routes, shared Order-stop reconciliation, hard lifecycle boundaries and serialized schema were not modified.
- All nine embedded Source texts and hash manifests must be checked byte-for-byte against this snapshot before deploying. These regression runs establish results for the tested RAWs, not universal correctness for unobserved market data.

## 30. Absolute standalone acceptance rule

The production Source defines the current behavior, but this Reference must independently preserve everything required to understand and rebuild that behavior.

The acceptance equation is:

```text
CURRENT PRODUCTION SOURCE
+
COMPLETE SEMANTIC UNDERSTANDING
+
COMPLETE DIRECTIONAL MIRROR RULES
+
COMPLETE DIRECTION-INVARIANT RULES
+
EXACT CHRONOLOGY / OWNERSHIP / TIES
+
EXACT SCHEMAS / SERIALIZATION
+
FUNCTION-LEVEL RECONSTRUCTION CONTRACT
+
COMPLETE EMBEDDED PROJECT-OWNED SOURCE CODE
=
TRUE STANDALONE ALGORITHM REFERENCE
```

If every original TradingBot production `.py` file disappears, this Reference must still be sufficient to recreate the complete production engine with the same algorithm, event chronology, ownership, provenance, behaviors, output ordering, and serialized values.

**DOJI IS ALWAYS GREEN.**
