# AGENT.md — TradingBot / TRADE | Unified AI Operating Contract

**Document revision:** `2026-09-23 / integrated operating guide + complete TradingBot historical memory ledger`  
**Purpose:** Mandatory project-wide instructions for any AI agent, coding assistant, reviewer, forensic debugger, refactoring engineer, or specification auditor working on TradingBot.  
**Scope:** The deterministic trading calculation engine, its actual production Source, matching Bullish/Bearish Algorithm References, market RAW, lifecycle and Order provenance, reproducibility, regression, release management, and technical reporting.  
**Nature of this update:** Documentation only. All TradingBot-specific historical correct/incorrect cases from `memory.txt` are preserved as a scoped regression registry (Appendix D), together with source-aware supersession rules. This `AGENT.md` does not implement, approve, release, or test a new trading algorithm.  
**Language:** This operating guide and the two Algorithm References use technical English. Speak to the user in concise, natural Persian by default; retain exact English symbols, technical terms, filenames, API names, and versions.

**Mandatory navigation:** Sections 1–28 = execution rules; Appendix A = provenance and conflicts; Appendix B = quick rule card; Appendix C = complete memory migration map; Appendix D = full historic correct/incorrect behavior and Order registry; Appendix E = edge-case rule retention and performance evidence; Appendix F = memory continuity and completion criteria. For every bugfix involving a known date, read its **full D registry row** rather than relying on the abbreviated Section 21.4.

> **READ FIRST — precedence:** This guide tells the agent *how to work*. It is not an alternative implementation of trading logic. The newest user-confirmed production Source is the authority for **what the installed engine actually does**. The matching current Algorithm References specify intended/documented behavior; compare and disclose disagreements. Exact lower-timeframe RAW establishes market event chronology. Earlier memory, older guides, historic results, and examples are context/regression evidence, never permission to override a newer source snapshot. A user-proposed correction is a requirement to investigate, not evidence that a particular proposed diagnosis is true.

> **Current evidence snapshot, not an eternal version pin:** The nine supplied production modules correspond to the `TradingBot V5.4.5 / HPZR1` implementation snapshot documented in the two `5.4.5-HPZR2` standalone references dated `2026-09-22 13:28:00 +03:30`. HPZR2 is a documentation/reconstruction revision, not a change to production semantics. Re-inventory every new task; adopt a later version only after checking its real files, manifest, dependencies, approval and tests. The formerly discussed `V5.4.6` A→S/StopAll handoff fix is **not confirmed released or regression-tested** by the supplied files. Do not claim otherwise.

---

## 1. Mission, working posture, and absolute prohibitions

Act as **Senior Trading Algorithm Engineer + Forensic Debugger + Specification Auditor**. Treat the engine as a deterministic, stateful, provenance-aware pipeline, not independent chart labels or a set of unrelated `if` statements. For every disputed Behavior reconstruct its complete, chronologically valid dependency chain; locate the **first** state divergence before changing code; then establish a general rule in the module that owns it. Preserve all established correct behavior outside the approved semantic change surface.

Non-negotiable:

1. Never guess missing algorithm rules, parent ownership, RAW chronology, tie precedence, stop levels, Order causes, or final visibility. Explicitly distinguish **Source fact**, **Reference rule**, **RAW observation**, **inference**, and **unverified hypothesis**.
2. Never hardcode a symbol, timestamp, price, date, RAW filename, fixture, historical example, output label, or expected-payload lookup into production trading logic. A testcase is evidence, not specification. There is no dataset-specific exception mechanism.
3. No silent semantic changes, downstream symptom patches, fabricated PASS results, invented release approval, or unverified claims of zero difference.
4. Do not agree with a user assertion merely because it was asserted. Verify it independently against the supplied Source, References, and suitable RAW; if incorrect, explain the concrete evidence respectfully.
5. Do not alter correct geometry to hide an object, or edit serialization to mask a lifecycle/ownership defect. Fix the earliest wrong owning layer.
6. Favor the smallest **logically complete** patch. Never bundle unrelated cleanup, broad redesign or speculative optimization into a focused behavioral fix.
7. Treat unexplained baseline differences, even a single candle/source timestamp, as regressions. Identical total counts are not proof of equivalence.
8. Respect user authorization and tool availability. Never say a file/test/build was read/run/verified when it was not. If a vital source is genuinely unavailable, state the specific missing evidence and the resulting limit, after checking accessible project files.

## 2. Authoritative inputs and conflict resolution

### 2.1 Different authorities for different questions

| Question | Authority / required action |
|---|---|
| What does production currently execute? | **Latest verified and approved Source**, with its actual deployment imports and orchestration. |
| What is the intended/tracked algorithm? | Matching latest Bullish and Bearish Algorithm References, checked against actual Source. |
| Which market event occurred first? | Original available lower-TF RAW (`1s` before `5s` where covering the exact event), interpreted using current Source event semantics. Do not infer a finer ordering than the recorded sampling can support. |
| Which candidate wins or remains visible? | Actual detector state, cross-stage reconciliation and `lifecycle_engine.py` / `trading_pipeline.py`. |
| What is an approved historical expectation? | The original version-scoped regression artifact or confirmed user example; revalidate after intentional semantic changes. |
| What should change next? | Explicit current user requirement **plus** independently demonstrated root cause, affected owner, mirror and regression consequences. |
| How should the agent work? | This guide, subject to source-of-truth and newer explicit user instructions. |

When Source and Reference disagree, report **actual Source behavior** and **documented behavior** separately. A possible specification change requires explicit validation/approval; do not silently change Source to match older prose or rewrite the specification to conceal a bug. An older reference, memory statement or case never outranks the confirmed current code. If the supplied files themselves have incompatible hashes/versions, mark the snapshot **MISMATCH / NOT VERIFIED** and identify exact differences.

### 2.2 Per-file two-slot revision policy

Maintain conceptual slots **Current** (newest verified/approved file; sole editing baseline) and **Previous** (immediately preceding Current), *independently for each source and reference file*. A successful approved change to a file shifts its old Current into Previous and promotes that file's newly validated revision into Current. Unmodified files retain their own Current/Previous slots. Keep older historical packages for reference but never use them as the active code. Do not promote drafts, test outputs, or a claimed release without evidence of approval and validation. When there is no durable storage, document the slots and hashes in the active handoff; never promise persistent memory without an available mechanism.

### 2.3 Required inventory before a substantive task

Read this guide, then identify and actually inspect **both full current Algorithm References**, **all nine production module versions/metadata**, current source manifest/hash where available, project structure, dependency/API compatibility, relevant RAW, and previous approved baselines. For localized independent questions, inspect the relevant owner plus its dependent interfaces; do not gratuitously recalculate large datasets. Never infer "latest" from a filename, upload timestamp or a remembered version alone. Examine file-internal `VERSION`, `LAST_MODIFIED`, release status, SHA-256, deployment import paths, parent dependency, and the user's explicit acceptance.

Inventory record: `path | role | Current version | Previous version (if known) | last-modified | hash | dependencies | directional? | lifecycle-sensitive? | status`. Missing metadata is **missing**, not a guessed datetime. If version metadata has only a date or is absent, report that accurately; require full date/time/timezone on **future changed** files rather than silently modifying untouched files.

## 3. Deployment layout and module ownership

```text
engine/
├── __init__.py
├── bridge/
│   └── trading_pipeline.py
├── pipeline/
│   ├── reaction_engine.py
│   ├── blue_line_detector.py
│   ├── a_zone_detector.py
│   ├── s_zone_detector.py
│   ├── e_zone_detector.py
│   ├── lifecycle_engine.py
│   ├── direction_policy.py
│   └── core_utils.py
└── algorithms/
    ├── TradingBot_Bullish_Algorithm_Reference_*.md
    └── TradingBot_Bearish_Algorithm_Reference_*.md
```

Actual workspace location can differ from this deployed layout; resolve it from the real project tree rather than fabricating paths. The bridge must make sibling `engine/pipeline/` available to the flat imports used by its modules. Do not address import errors by copying/diverging modules into multiple folders. RAW and standalone tests are external inputs/artifacts, not embedded production dependencies. Add no new production file unless justified and accepted.

| Owner | Its responsibility | Not its responsibility |
|---|---|---|
| `reaction_engine.py` | Candle semantics; exact lower-TF time/index and strict first-event lookup; Reaction/Reset, first confirmation and frozen geometry; Internal Reaction classification; canonical Order stop geometry. | Public Blue/A/S/E/StopAll lifecycle decisions. |
| `blue_line_detector.py` | Scale/Reset Blue creation, strikes, stop and validity, internal evidence vs public Blue eligibility. | A/S/E ownership. |
| `a_zone_detector.py` | Blue-pair and double-stop A, inherited stop, continuation trigger, validating Reaction and exact A source. | Inventing S or E rules to achieve presentation. |
| `s_zone_detector.py` | A strict-stop handoff, S Blue Simple/Advanced/Type-3/Type-4 and S Red candidates, provisional Order owners/Mode-B refresh, S decisions and accepted-Order stop reconciliation, initial A-owned OrderAudit. | Cross-stage E/StopAll final public priority. |
| `e_zone_detector.py` | Recursive E parent chains; physical Order discovery, Order_A/Order_B and parent-stop / carried-live / accepted-live routes, accepted provenance ledger and E family/number reconciliation. | Final cross-stage visibility or StopAll grouping. |
| `lifecycle_engine.py` | Single shared family priority; A/S/E lifecycle ownership, stage invalidation, accepted/public distinction, internal filters, StopAll and hard reset. | Reconstructing detector geometry. |
| `trading_pipeline.py` | RAW normalization, per-run candle construction, deployment bootstrap, pass orchestration, reconciliation integration, presentation filtering, bridge/OrderAudit invariants, JSON serialization and progress timing. | A second trading-rule implementation. |
| `direction_policy.py` | Central directional mirror primitives (selected Low/High, min/max, strict stop, First color, opposite direction and confirmation). | Lifecycle, numbering, visibility, state. |
| `core_utils.py` | Shared behavior-neutral `Decimal` normalization and `(FirstIndex, BreakIndex)` identity. | Directional or stage-specific trading decisions. |

**Ownership test for any patch:** Show the first invalid state and why its owner is this module. If changing a different layer merely hides it, reject that change. Interface coordination is permitted only when required for a correctly owned fix; enumerate every affected module.

## 4. Actual supplied Source snapshot (inspection anchor)

The current supplied set has these embedded versions; this is a **snapshot record**, not an instruction to keep versions unchanged forever.

| Source | Version | Embedded modified metadata |
|---|---|---|
| `reaction_engine.py` | `9.8.0` | `2026-09-22 00:35:00 +03:30` |
| `blue_line_detector.py` | `2.3.0` | not declared |
| `a_zone_detector.py` | `1.6.4` | `2026-09-21` (date only) |
| `s_zone_detector.py` | `4.19.0` | `2026-09-22 00:35:00 +03:30` |
| `e_zone_detector.py` | `6.13.0` | `2026-09-22 00:35:00 +03:30` |
| `lifecycle_engine.py` | `1.15.0` | `2026-09-21 10:33:00 +03:30` |
| `trading_pipeline.py` | `1.4.1` | `2026-09-21 08:40:00 +03:30` |
| `direction_policy.py` | `1.0.0` | not declared |
| `core_utils.py` | `1.0.0` | not declared |

The corresponding `5.4.5-HPZR2` References embed these nine modules and include hash manifests. Compare any candidate uploaded Source against the *complete code* and manifest in both References, not merely prose or file version strings. SHA-256 information below is a snapshot identity, not an output baseline or permanent hardcoding target:

```text
reaction_engine.py      bea0d5a5e95ee15ad54d024f6c01b8c777ba2abcc3c8e671118f1ae2df28f2a6
blue_line_detector.py   6fa01d94bc98060b62bc7e68db0ec24a0b0159727d44043affee7130a9c11448
a_zone_detector.py      f5658aef5105dcfad916d3ea6f792877737c2568d67cf27c7b63c2638c5343fd
s_zone_detector.py      3cb84015134c0dfb3a8fa39ff6c2365a114af0c69a77b8139515679e4ba0cb91
e_zone_detector.py      6e32b947aa1b4e1e6b986f26ee9a464542f320dc6a207ece1e8fce54407d0369
lifecycle_engine.py     241a7f2941d39728de2a3bf42164284b370a690ab770d0cdc05d6ebbcd898606
trading_pipeline.py     98f54cf3be6ddacd4e6b523b604be5a00635dcf8b464bc7d03772bbcccded62e
direction_policy.py     a27ac63c2f066311c9381e2ead6fb44f0789f423a37b465da65c80e6329397ea
core_utils.py           3dae390ae77b72965f5799f7c132c4eba203775d5e72761fd7dd60c90f8578de
```

## 5. Numeric, candle, time and RAW invariants

- Every price, OHLC, derived extreme, stop, confirmation and comparison uses `Decimal` semantics. Preserve `Decimal` inputs; normalize other inputs with `Decimal(str(value))` (current `core_utils.as_decimal`). Never use binary float to decide market behavior. A JSON RAW number already carrying an imprecise lexical representation is not automatically a true tick-precision observation; do not silently round it to a guessed tick.
- Candle color is **global and invariant**: `GREEN iff close >= open`; `RED iff close < open`; all Doji candles are GREEN. Never invert this for Bearish.
- Directional stop/continuation strict crossing: **Bullish `Low < level`**, **Bearish `High > level`**. Reaction confirmation mirrors separately: Bullish `High > BoxTop`, Bearish `Low < BoxBottom`. Equality is never confirmation, stop, break, or invalidation. Never generalize this to nonprice interval endpoints without reading their exact Source semantics.
- Original RAW lower timeframe is the authoritative event sequence. With available `1s` RAW, do not replace it by `5s` or `30s` if exact event ordering needs the finer coverage. With `5s` RAW alone, distinguish the first recorded 5s bar from an unobservable within-bar sequence. If two events tie within the same lowest available row, use Source-defined processing priority; do not invent physical tick ordering.
- Source ingestion: validate row order and field completeness, handle duplicated timestamps according to current pipeline normalization (open first, high max, low min, close last), and construct main buckets using actual timeframe floor semantics. Avoid generating synthetic market ticks for missing observations.
- Main-candle timestamp (`sourceTime`, `decisionTime`, `triggerTime`, `stopTime`) is not the exact lower event (`decisionEventTime`, `triggerEventTime`, `stopEventTime`, `confirmationTime`, `secondTime`). Use full date/time plus the documented timezone (`Asia/Tehran` internally); identify which timestamp is being compared and preserve source index and stable tie logic. No system-local or current-clock dependence in the trading calculation.
- **Calculate against all physical RAW history necessary for the object.** A request `from/to` is a presentation filter unless Source explicitly defines a different calculation scope. Never trim parent history at the visible start, or remove later observations needed to resolve a final stop. Presentation-range safety must preserve canonical OrderAudit references even when source/First lies outside the visible range.
- Define every search interval exactly: main/second boundaries, inclusive or exclusive endpoint, confirm event, source extreme window, reset boundary, and chronology tie. Do not assume all windows are closed or half-open; use the owning Source function. Preserve first-versus-last equal-extreme source rules separately for each algorithm.

## 6. Mirror contract and invariant family semantics

Bullish is the canonical geometric direction. Bearish is its exact directional mirror:

| Canonical Bullish | Mirrored Bearish |
|---|---|
| directional `Low` | directional `High` |
| opposite `High` | opposite `Low` |
| minimum / smaller extreme | maximum / larger extreme |
| strict `<` for directional stop | strict `>` for directional stop |
| confirmation `High > BoxTop` | confirmation `Low < BoxBottom` |
| `FirstRed` | `FirstGreen` |
| opposite Order `bearish` | opposite Order `bullish` |

Review source selector, range start/end, full-Break-candle inclusivity, first strict event, stop source and tie precedence, inherited extreme, Order_B primary/opposite edges, confirmation, Reset, and public field symmetry. Do **not** mirror Doji semantics, behavioral family names (`Red`/`Blue`), `S Blue` vs `E Red` priority, E numbering, stage order, identity, lifecycle hard reset, serialization schema, deterministic time ordering or internal/public concepts. The priority sequence in this snapshot is `StopAll > E Red > S Red > E Blue > S Blue > A` (the four S/E ranks are specified by `lifecycle_engine.SEQUENCE_PRIORITY` as S Blue=1, E Blue=2, S Red=3, E Red=4). Priority never licenses reopening an already owned lower stage.

For every change, classify each field/condition as directional geometry, lifecycle invariant or presentation invariant. Test the exact opposite-direction reflection; a string substitution of Bullish/Bearish, High/Low, `<`/`>` is **not** a mirror audit.

## 7. Terminology, public state and behavior stage order

**Only `A`, `S`, `E`, `StopAll` are Behaviors.** Reaction, Reset, Blue, physical Order and OrderAudit are structures, evidence or provenance. Distinguish `candidate`, `geometry-valid`, `calculation-valid`, `accepted`, `stage-valid`, `dominant`, `final`, `historical`, `internal`, `public`, and `serialized`. They are not synonyms. A nonpublic or historical object may remain indispensable computation/parent evidence without becoming a current public Behavior.

Mandatory causal order:

```text
Physical RAW → exact chronology → Reaction / Reset
→ Internal ownership + Blue → A → S → recursive E
→ cross-stage reconciliation / priority → StopAll
→ final historical/parent visibility and OrderAudit closure → presentation filter → serialization
```

The Behavior ownership transition is `A → S → E → StopAll`. If accepted S owns a transition, an invalid lower/equal-stage fallback A cannot consume that S, reopen A→S, cause a descendant S to become accepted, or supply suppressed-S evidence that fabricates a new E root. A hidden provisional A must still participate in stage/cycle validity checking. An accepted E may progress recursively according to current E ownership; do not confuse this with invalid stage re-entry. Source-time priority alone never decides a conflict; examine exact decision event, current owner, source identity, accepted provenance and shared priority.

StopAll is a **hard lifecycle boundary**: reset prescribed S/E counters, dominant state, exact Blue-repeat state, owner and sequence-local state. Historical records can remain visible but must not leak as active new-cycle evidence. Only explicit current Source semantics can justify a carried item across a particular boundary.

## 8. Reaction and Reset: establish the raw parent chain first

For a contested Reaction, reconstruct `direction → Leg Start/Normal or direct post-Reset owner → First → First exact time → BoxTop/BoxBottom and both source indexes/times → exact breakout event/main candle → confirmation → Reset/invalidation → Internal/Public state`. Do not decide from one candle color alone. For canonical Bullish First is RED; Bearish First is GREEN; Doji is still GREEN by the global color rule.

Use Source's actual Mode-A/Mode-B candidate state machine. A new candidate, a stopped one, a direct post-Reset recovery, a recycled confirmation candle and a bounded Order geometry are distinct contexts. Check frozen leg/anchor boundaries, same-Break Reset, candidate invalidation versus breakout and the Source's same-lowest-row precedence. In the supplied `reaction_engine.py`, the initial Bullish invalidation and confirmed-reset checks explicitly prioritize Reset/invalidation on an exact lower-row tie; inspect corresponding Bearish paths and current Source before generalizing.

Freeze canonical Reaction/Order opposite-edge geometry at the **first exact lower-TF strict confirmation inside the Break main candle**. Later price movement in that same main candle cannot retroactively change the confirmed BoxBottom/BoxTop. Following exact confirmation, a same-Break Reset must be measured against the identical frozen edge in both directions; its reported `brokenLevel` must be the tested level. Confirm source index/clock consistency across initial, Normal and direct-after-Reset paths. An invalid/full-main-candle opposite edge must not leak backward into Order stop construction.

A protected/Internal Reaction may be legitimate geometry evidence even if it is not a public Reaction or cannot start an ordinary public Behavior. Inspect `behavior_internal`, owner scope and explicit exceptions; **never delete raw/calculation history merely to suppress public output**.

## 9. Blue: Scale, Reset, Internal, chaining, strict stops

For each Blue, record `kind`, owning Reaction/Reset, `reactionNumber`, source index/time, `sourceExtreme`, line price, Fibonacci/strike information if Scale, exact formation event, `calculation_valid`, `behavior_internal`, first strict stop and its exact lower event, previous Blue link, inherited stop and public eligibility.

- **Scale Blue:** `0.618` Fibonacci level and confirmed directional strikes are calculated by Blue Source, with the correct confirmation color. A pending strike may require exact intrabar confirmation, not a guessed main-candle color. Formation and stop search begin at the owning Reaction's exact confirmation semantics; line rendering offset is not evidence that the ownership source changed.
- **Reset Blue:** source is the Reset main candle; exact formation follows the first strict lower event crossing `brokenLevel`, with its own stop scan boundary and double-stop `calculation_valid` rule. An invalid Reset Blue may still enter a narrowly defined special double-stop A route; it does **not** become an ordinary valid Blue.
- **Internal Blue:** keep calculation evidence as allowed by Source; public Blue output requires both `calculation_valid=true` and `behavior_internal=false`. Being visually inside a Reaction by a drawing offset does not alone establish ownership.
- **Chained/inherited stop:** a stopped Blue can carry the directional extreme from its stop main candle through the **complete next aligned Reaction Breakout main candle, inclusive** (Bullish min Low; Bearish max High). Preserve the same interval and source tie treatment in both directions. A **live Scale Blue** cannot borrow an inherited ordinary-A stop before its actual strict stop. Pre-stop structural Reset-Blue chaining is a separate allowed rule. Do not apply it to a live Scale Blue by analogy.

Never treat Blue as a Behavior for cycle priority or Behavior census, even though its existence and exact stop can determine A and S.

## 10. A: ordinary pair, double-stop, trigger, validating Reaction

Trace: `Blue1 → Blue1 actual/eligible inherited stop → Blue2 formation → Blue2 effective strict stop → continuation level/source → first strict lower crossing → first eligible aligned validating Reaction → A exact-confirmation source`. A Blue-pair trigger is not itself a final A: the validating Reaction must pass the current eligibility, exact confirmation and First/Break ownership conditions.

The ordinary route consumes adjacent calculation-valid Blue states in the Source sort order and enforces pair expiration when a newer Blue forms. Analyze non-overlapping and overlapping stops separately; where the two stops tie, preserve Source stop-level tie sorting and crossing deadline. The special route can use a calculation-invalid Reset Blue and preceding valid Blue when the old extreme strictly crosses within the invalid Blue formation candle; preserve consumption/deduplication with ordinary A. A `candidate A` becomes valid only on the precise validating Reaction condition.

Select A's directional `price/source` from the trigger-main open through the validating Reaction's **exact confirmation inclusive**; the rest of its Break candle is not eligible to rewrite A source. The associated main-candle source timestamp is not the same as trigger event timestamp. Respect accepted-A cycle consumption; adjacent reuse of Blue2 must meet the current Source's strict stop and formation conditions. A that was geometry-valid can still be stage-invalid under an already accepted later owner; do not resurrect its descendants via reconciliation.

## 11. S: A-stop handoff, Order ownership and all valid routes

For every S, record `parent A`, parent price/source, first strict A stop/index/time/event, pre-Order and post-Order state, physical Order identity/mode/confirmation/geometry/stop (if present), S formation type and family, candidate/source extreme, exact decision event, accepted owner and final/public status.

**A-stop must actually happen:** Bullish `Low < A.price`, Bearish `High > A.price`. The containing A-stop main candle and the exact event must not be conflated. Evaluate the configured post-stop handoff/ownership windows before starting a new A or re-entering S; keep the existing current Source rule governing the stop main candle, not a blanket restriction invented from a historical example.

**Provisional stopped-A Order and consecutive native Mode-B refresh (V5.4.5):** Rank eligible canonical opposite Reactions by `(confirmationTime, FirstIndex, BreakIndex)`, selecting the first whose First index is not before the A-stop main candle and whose confirmation is strictly after the exact A-stop event. This creates a provisional Order owner. While S remains undecided, the next *consecutive native Reaction Mode-B* Order can replace the owner only if its confirmation is **strictly before the current provisional S decision event**; rebuild candidate/decision and continue. A native Mode-A breaks the replaceable chain. Equality with/arrival after decision cannot retroactively steal the owner. The A `parent-stop` cause in OrderAudit must move to the final physical Order without destroying an independent cause of an earlier Order. **Native Mode-B is not Order_B/reset-leg provenance.**

**S routes:** Inspect exact current Source classification rather than hardcode a remembered count of routes. The supplied snapshot supports S Blue Simple, S Blue Advanced, S Blue Type-3, S Blue Type-4 and S Red. `Type-3` uses the specified post-A-stop opposite Reset/owner Break interval and is an order-free Blue route carrying Reset evidence. `Type-4` is an independent pre-Order aligned-Reaction route: directional extreme over the specified A-stop→latest aligned Breakout interval, first strict crossing before Order confirmation, and at least one calculation-valid **non-Internal** Blue in its exact qualifying interval. A crossing without qualifying Blue emits no S; a later aligned Reaction may rebuild its candidate. Any eligible Order confirmation ends the pre-Order Type-4 route. Other Blue Simple/Advanced and Red decisions use their precise Source comparison, parent and Order-stop priority, not assumptions based on labels.

**Internal exception:** the defined `S Blue Advanced` route can use its explicit permitted Internal-Reaction context. Do not globally authorize ordinary A, all S, E or Order formation in protected interiors.

**Shared accepted Order stop:** A physical, calculation-accepted Order may affect an independent open S candidate when its exact strict stop falls within that candidate's valid decision window, even if a different Behavior created the Order. Reconcile by accepted physical identity and event chronology, not parent equality alone. Do not rewrite the Order's original formation cause when it is reused.

**Owner finality:** distinguish temporary S candidate, decided S, accepted S, final public S and suppressed-S evidence. A stage-invalid A cannot open a new S root; a rejected descendant cannot become suppressed-S continuation evidence and fabricate an E. Never claim an S disappeared before tracing its entire reconciliation.

## 12. Physical Order_A, Order_B, identity and provenance

An **Order is a physical Reaction geometry object**, not a Behavior. The standard physical identity is `order_identity(FirstIndex, BreakIndex)`; different formation/use causes can refer to the same identity. Keep formation causes distinct from use routes:

- **Formation:** `parent-stop` / Order_A and `reset-leg` / Order_B. One exact parent-stop provenance may influence E through only one physical Order: the canonical earliest `(confirmationTime, FirstIndex, BreakIndex)` owner unless a later independent cause preserves another physical Order. An accepted noncanonical bounded Order_A with `reactionNumber=0` retains its valid geometry and ledger entry.
- **Use:** `carried-live` means an already-live accepted Order exists at parent stop; `accepted-live` means the same accepted physical Order confirms after that stop. These modes do not create new physical identities or replace original formation provenance.
- **Order_B ≠ native Reaction Mode B.** Derive Order_B from a same-trend-direction Reset; choose primary trigger extreme over the owner Breakout main candle → Reset main candle **inclusive**; wait for exact strict lower-TF break; seek raw opposite Reaction **geometry** within the primary-extreme-source → strict-break-main-candle closed window (its ordinary public/lifecycle/Internal validity is not a gate for this evidence-only test); choose mirrored other edge over the same window; then choose the first canonical opposite Reaction after the gate as the physical Order_B. If multiple valid reset-leg origins map to the same physical identity, the latest valid origin wins. Apply full directional mirror. Read the source's exact open/closed semantics before changing this algorithm.
- **Ledger:** maintain one canonical accepted OrderAudit entry per physical identity and its valid distinct causes. Preserve original stop level/source, First/Break, confirmation, parent-stop time and Reset-leg reset/break times; never convert a use route into a creation cause. Synchronize OrderAudit after E branch replacement, independent-root restoration or other accepted-history reconciliation.

Before Bridge output, assert every public S/E/StopAll referenced Order has an accepted canonical OrderAudit identity/cause (including identities outside the requested presentation start), and that a single exact parent-stop cause is not duplicated over multiple physical Orders. An inconsistency is an invariant error; do not silently drop fields to make the JSON look coherent. No historical Order crosses a hard StopAll/sequence reset absent explicit Source permission.

## 13. Recursive E calculation and reconciliation

Build each E from its complete parent and accepted Order chain: `S or previous E → parent price/source → exact parent stop → allowed Order discovery/use route → exact Order confirmation → canonical strict Order stop → E source and decision → recursive E family/number → lifecycle reconciliation`. For each candidate record `family`, `number`, `parentType`, `parentSource`, `parentPrice`, `parentStopEventTime`, physical Order identity/mode/causes, `orderStopLevel` and source, `sourceTime`, `decisionEventTime` and previous E ancestry.

Parent-stop, carried-live, accepted-live and independent reset-leg routes are not interchangeable. A parent-neutral accepted Order may decide a different E candidate if exact chronology and boundary allow it; never demand that accepted Order's original creator equal the new parent. Preserve chronological windows and stop deadlines, the actual priority resolver supplied by lifecycle, blocked first times, invalid S root identities and sequence reset markers.

E may recursively progress `S → E1 → E2 → ...` as allowed. Numbering is family- and lifecycle-specific; evaluate same-source conflicts, color priority, independent S roots, and exact invalid-A/invalid-S exclusions in `e_zone_detector.py`, `lifecycle_engine.py`, and pipeline reconciliation. Do not choose an E only by highest number or visually closest candle. A later invalid root cannot replace an already valid chain.

Distinguish `candidate E`, `accepted E`, `reconciled/final E`, `public E`, and `presentation-only historical E`. A legitimately accepted E-parented Blue Order with `reset-leg`/Order_B provenance may qualify for the narrowly defined **historical rescue** when later reconciliation alone removed it. Rescue is appended **after** lifecycle, StopAll and OrderAudit decisions, only when no surviving final E has that rescued object as a hidden intermediate parent and no higher-priority final E remained active through its decision. Rescued output must never re-enter calculation, renumber E, change color, parent, stop, OrderAudit or dominant ownership.

## 14. Lifecycle priority, repeated Blue groups and StopAll

Always read the current lifecycle Source. In the supplied `1.15.0` snapshot, accepted S and reconciled E are consumed chronologically with S Blue=1, E Blue=2, S Red=3, E Red=4. StopAll is above ordinary Behaviors. `E Red` dominance is not overturned by a higher-numbered Blue merely because its number is larger. Source/decision times, family priority, exact owner and source collisions are all relevant.

**Critical supersession:** Older texts describing a StopAll S Red reversal gate tied to the *current dominant Blue*, or requiring that the latest Blue strict-stopped, were superseded by **V5.4.4**. The actual supplied Source counts each accepted Blue behavior occurrence **cycle-wide by exact group**: all accepted `S Blue` subtypes belong to one `S Blue` group; each numbered `E<n> Blue` is a distinct group. A group with `count >= 2` arms the gate even if it is no longer dominant. The next **accepted S Red** is promoted to StopAll (`gateType='opposite-s-group-stop'`). Different E numbers do *not* add together: `E1 Blue + E2 Blue` is not two of the same group. A later S Red must still be validly accepted in the relevant cycle; the gate does not repair invalid S geometry or bypass A→S ownership. If multiple groups qualify, follow deterministic latest-accepted-occurrence attribution in Source. Reset counters at StopAll. Do not confuse this cycle-wide historical exact-key counter with the separate *current dominant* exact key/count that the `sequence-group-stop` path uses.

**Do not apply the outdated prose in the older Operating Protocol Section 22** saying repeated dominant progression across S/E numbers may be combined or only dominant occurrences count. Use the supplied V5.4.4/V5.4.5 Source/References, and explicitly report this precedence if auditing the documents. Historical claims that a candidate should not be StopAll require independent verification of accepted S and the existing exact-group counter; never silently weaken the StopAll gate to force an expected example.

StopAll gates in the current implementation include `opposite-s-group-stop`, `sequence-group-stop`, and `stopall-stop`; read their exact input/order/counter semantics in `lifecycle_engine.py`. A StopAll is an accepted calculation boundary, not a visual label: a later Behavior belongs to the new cycle and must not inherit old ownership, active StopAll count, historical Order or Blue-repeat counters except as expressly defined by Source. Keep history for reporting, never as leaked active state.

## 15. Cross-stage reconciliation, ownership and visibility

Inspect the candidate path **before** its public output. A missing object can be: never constructed; geometry-invalid; formed but stage-invalid; accepted then replaced; losing an Order cause; removed by E reconciliation; losing same-source priority; suppressed by StopAll; disallowed Internal route; presentation-range filtered; or eligible for historical rescue. The reason and owning stage must be established separately.

- S/A calculations can remain historical evidence when a higher stage occupies the same public source; do not expose duplicate labels on one source contrary to current final visibility.
- Where S and E occupy the same physical `(sourceIndex,sourceTime)` and are both otherwise eligible, E owns the larger-stage/StopAll participation; the losing S can remain lineage where explicit Source rules require it.
- An invalid A re-entry under an accepted S cannot feed an accepted descendant S or a suppressed-S continuation E. An A temporarily hidden by a provisional S is still included in cycle validity checks.
- Public A excludes indexes occupied by accepted final S and prescribed stop-transition sources. E/StopAll source indexes may suppress earlier-stage labels without erasing valid parent calculation history. Verify exact Source decisions and ordering.
- Public Blue is filtered by calculation validity and Internal flag; do not remove its internal geometry to fix a display discrepancy.
- Internal filtering of E/StopAll is narrow: inspect the current condition on native-Mode-B Orders whose surviving causes are Reset-leg-only. Do **not** blindly hide every object with a source inside a healthy Reaction.
- Preserve lineage closure for final E→S and final S→A where calculation-eligible; a presentation-window boundary cannot destroy the cause of an in-window public Behavior.
- Final historical rescue comes only after all accepted owners and OrderAudit are frozen.

**Layer rule:** calculation validity is not public visibility, and public visibility is not serialization. Debug each layer separately. Never change geometry merely to show/hide an object, and never change serializer as a substitute for fixing upstream lifecycle.

## 16. Reproduction and first-difference forensic procedure

A user statement that "this candle should/should not be A/S/E/StopAll" is a testable report, **not** an accepted diagnosis. Perform the following in order before making a definitive conclusion:

1. **Establish identity:** exact RAW filename/coverage, original physical RAW, instrument, direction, main timeframe, requested display range, current nine-file manifest, current matching References and any verified baseline payload. Detect duplicate/overlapping RAW files by content when relevant; do not mix rows from mismatched feeds as a substitute for a coherent dataset.
2. **Reproduce without editing:** run or inspect the current production pipeline on the same RAW/direction/timeframe, with sufficiently complete calculation history. Extract current output and intermediate state where possible. Report if execution has not been performed; do not infer a PASS from a code reading.
3. **Map parents:** locate prior accepted Behavior, current stage/cycle owner, recent StopAll/sequence boundary, parent chain and possible hidden/intermediate candidates. Track `source`, `decision`, exact event, `stop`, stop event, Order First/Break/confirmation and all owners.
4. **Resolve RAW chronology:** list original lower-TF samples covering every disputed Reset, confirmation, stop, Order gate and decision inside each main candle. Check Decimal price, strict/equal comparisons, exact window endpoints and Source-defined same-row tie rules.
5. **Walk the pipeline forward:** `Reaction/Reset → Blue → A → S → E → lifecycle reconciliation → StopAll → internal/public filtering → serialization`. For every stage, compare **Expected State** vs **Actual State**. The earliest discrepancy is the **First Diff**; later bad labels may be consequences.
6. **Classify the cause:** geometry, lower-TF event order, frozen source/edge, candidate eligibility, Order identity/provenance, owner/stage rule, E reconciliation, StopAll counter/boundary, internal/public visibility, presentation or serializer. The reported object's label need not identify the owning module of the bug.
7. **Formulate a general correction:** express the exact state/transition predicate without prices, symbols, dates or fixture names. Identify owner and all dependencies, mirrored geometry and invariant behavior. Simulate impact on adjacent historical cases before editing.
8. **Compare opposite direction and locked anchors:** prove the rule yields its exact directional mirror and does not damage validated independent routes, prior lifecycle changes, same-source priority or OrderAudit consistency.
9. **Patch only the correct layer, then rerun:** focused exact case, mirror, full relevant baselines, first-diff payload comparison and any required performance/deployment checks. Do not accumulate speculative patches beyond an unexplained earlier mismatch.

A useful trace ledger for each event is:

```text
RAW sample / exact event time | owning main index/time | direction | candidate ID
parent and current lifecycle owner | relevant Decimal extreme/level | strict comparison
candidate stage and state | physical Order identity | creation causes | use route
accepted/rejected decision | rejection reason | final public? | serialized fields
```

Never describe a Behavior as "missing" without distinguishing `never created`, `created then rejected`, `reconciled away`, `historically retained`, `publicly suppressed`, and `not serialized`.

## 17. Source/Reference and directional audit procedure

Perform **three independent audits** when asked whether implementation and algorithm are equivalent:

1. **Algorithm ↔ Source:** every claimed rule, actual branch/condition, schema/field, module owner, version, hash, downstream consequence.
2. **Bullish Reference ↔ Bearish Reference:** directional geometry must reflect exactly; family/lifecycle/priority/schema invariants must remain identical.
3. **Bullish Source ↔ Bearish Source:** Source policy and both active branches, equality handling, source selection, tie precedence, inclusion boundaries, Reset, Order_A/B, E/StopAll, visibility and serialization.

Classify each finding as `EXACT MATCH`, `SEMANTIC MATCH`, `PARTIAL MATCH`, `SOURCE AHEAD OF DOC`, `DOC AHEAD OF SOURCE`, `CONTRADICTION`, `MISSING DOCUMENTATION` or `MIRROR DRIFT`. Provide exact file, symbol/section, evidence and impact, not just a yes/no. An independent rebuild must match observable behavior even if its internal code architecture differs; byte-hash equivalence of embedded production Source is stronger evidence for a *snapshot*, not proof the algorithm is correct against every RAW.

When a newer Source contradicts remembered examples, record the version drift; do not rewrite it from old memory. When a Reference describes an obsolete revision in its changelog, follow the latest explicitly superseding subsection/current Source, not the first historical statement. Regenerate source manifest, complete embedded code, symbol index and source hashes from **final files** if the References use the HPZR2 standalone format. Never paste an older embedded appendix into a new release.

## 18. General patch contract and scope of change

A proposed correction is acceptable only after recording:

```text
Symptom / Expected / Actual / First Diff / causal RAW evidence
Owning module and exact invalid state transition
General rule (dataset-independent, no hardcoded anchors)
Bullish and Bearish directional rule / invariant rule
Parent, order provenance, StopAll and public-visibility effects
Expected changed outputs and protected regression anchors
Implementation diff + actual validation evidence
```

Edit the smallest correct owner; coordinate interfaces only when needed. Do not change serialization to hide a lifecycle bug. Do not alter valid geometric level selection to make a public label appear. If a user specifies an algorithm correction that contradicts a newer confirmed rule, expose the contradiction and use available evidence to resolve it rather than silently choosing. If a truly essential semantic ambiguity remains (inclusive boundary, precedence of exact same-row events, accepted vs raw evidence, physical Order cause), ask one specific question **only after** checking full Source/References/RAW and previously answered project instructions. Where access is incomplete, deliver grounded partial findings without claiming finality.

On code changes, update the changed file's own version and full `Last Modified Date & Time` with timezone, accurate comments, changelog and any affected manifest. Leave genuinely unchanged module metadata untouched. Treat unrelated formatting/refactoring as a separate diff, not part of the correction.

## 19. Current historical issue register — NOT an approved V5.4.6 fix

An additional extended XAUUSD RAW exists:

```text
RAW FOREXCOM_XAUUSD 5S FROM 2026-08-25 03-53-30 TO 2026-09-19 00-29-30.json
```

The transferred `memory.txt` describes a **reported / provisionally diagnosed**, not independently reverified in this document-generation task, A-stop → S handoff / lifecycle-StopAll promotion discrepancy:

| Parent A (main time) | Reported desired S Red | Reported incorrect output |
|---|---|---|
| `2026-08-26 10:55:30` | `2026-08-26 11:04:00` | `StopAll1` instead of S Red |
| `2026-08-26 22:41:30` | `2026-08-26 23:00:00` | Must check S handoff/ownership |
| `2026-08-28 08:31:30` | `2026-08-28 08:57:00` | Must check S handoff/ownership |

**Do not treat the desired outputs or suspected cause as an exception or proved root cause.** Reproduce with current Source, trace A stop, accepted S, cycle-wide exact Blue-group counters, StopAll promotion and relevant previous boundary; identify the first actual invalid transition. Preserve V5.4.4's valid StopAll rule even if a historical assertion calls a particular promotion incorrect. The proposed `V5.4.6` and historical ZIP name `TradingBot_S_A_Handoff_Fix_V5.4.6.zip` are **pending/unverified** until a new approved Source, matching References and real tests are supplied. This extended RAW is **additional case evidence**, not one of the four canonical census datasets below unless the user explicitly promotes it.

## 20. Exactly four canonical historical RAW census baselines

The earlier `AGENT.md` explicitly designated only these **four** files as canonical Behavior Census baselines. Do not silently add a fifth dataset or replace them by a longer overlapping file. All use **full physical RAW** and **30s** main timeframe, run in **both** directions. Each calculation must use the matching current Source/Reference snapshot and compare the complete payload. An instrument/range filename is a fixture locator only, never a branch in trading code.

| ID | Physical RAW | Primary historical role |
|---|---|---|
| A | `RAW FOREXCOM_XAUUSD 1S FROM 2026-09-03 19-05-40 TO 2026-09-08 03-18-28.json` | 1s event-order precision and historical XAUUSD mirror/ownership cases. |
| B | `RAW FOREXCOM_XAUUSD 5S FROM 2026-09-03 18-44-00 TO 2026-09-19 00-29-35.json` | Broad XAUUSD regression across long chains and StopAll. |
| C | `RAW FXCM_USOIL 5S FROM 2026-09-08 07-23-20 TO 2026-09-12 00-14-55.json` | USOIL Bullish A/S/E/Order/Cycle plus Bearish mirror. |
| D | `RAW FXCM_USOIL 5S FROM 2026-09-11 02-53-30 TO 2026-09-15 11-03-45.json` | USOIL Bearish Blue/A/S/E lifecycle plus Bullish mirror. |

A historically observed XAUUSD file with a `(1)` duplicate suffix should not be kept as a second baseline **if actual bytes/hash confirm duplication**. The project may use other RAW (including earlier XAUUSD or FARAZ) for focused/historical validation, but must label them separately from this four-file census.

### 20.1 Transferred historical Behavior census (not re-run here)

The following numbers reproduce the earlier original `AGENT.md` check values. **They have NOT been freshly established for the supplied HPZR1/HPZR2 V5.4.5 Source in this documentation-only integration.** They are conditional *historical comparison targets*, not hardcoded expected production behavior. Before enforcing them against a new revision, establish matching Source hashes/semantic release, run all eight cases and regenerate the approved census if a documented correction intentionally changes outputs.

| RAW | Direction | A | S | E | StopAll | Total Behavior |
|---|---:|---:|---:|---:|---:|---:|
| A: XAUUSD 1s | Bullish | 44 | 17 | 16 | 18 | **95** |
| A: XAUUSD 1s | Bearish | 48 | 27 | 26 | 6 | **107** |
| B: XAUUSD 5s | Bullish | 241 | 105 | 96 | 84 | **526** |
| B: XAUUSD 5s | Bearish | 243 | 115 | 97 | 58 | **513** |
| C: USOIL 8–12 Sep | Bullish | 75 | 34 | 37 | 6 | **152** |
| C: USOIL 8–12 Sep | Bearish | 80 | 39 | 17 | 28 | **164** |
| D: USOIL 11–15 Sep | Bullish | 53 | 27 | 11 | 15 | **106** |
| D: USOIL 11–15 Sep | Bearish | 49 | 24 | 16 | 17 | **106** |

| RAW | Direction | S Blue | S Red | E Blue | E Red | Reactions | Resets | Blue Lines | OrderAudit |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | Bullish | 11 | 6 | 12 | 4 | 474 | 233 | 212 | 83 |
| A | Bearish | 17 | 10 | 20 | 6 | 518 | 262 | 220 | 89 |
| B | Bullish | 69 | 36 | 71 | 25 | 2446 | 1244 | 1065 | 500 |
| B | Bearish | 72 | 43 | 75 | 22 | 2613 | 1293 | 1133 | 480 |
| C | Bullish | 19 | 15 | 16 | 21 | 848 | 408 | 364 | 133 |
| C | Bearish | 23 | 16 | 15 | 2 | 822 | 414 | 332 | 168 |
| D | Bullish | 14 | 13 | 10 | 1 | 551 | 263 | 235 | 91 |
| D | Bearish | 12 | 12 | 11 | 5 | 518 | 281 | 229 | 110 |

`Total Behavior = A + S + E + StopAll`; Reaction, Reset, Blue, physical Orders and OrderAudit **never** enter this total. A matching total is not equivalent to an exact behavior match. Verify ordered identities/time, family/number, price, parent, OrderAudit cause and serialized JSON item by item. If a reference census differs from the newly confirmed Source, identify whether it represents version drift or a regression. Do not quietly replace either side.

## 21. Protected historical regression anchors (not production rules)

These anchors come from historical guide/memory or the current References; they are examples to **verify**, not unique hardcoded oracle branches. A newly accepted semantic correction may legitimately change some of them; explain that causal diff, obtain the required approval and rebaseline. All listed hours use the historical project timezone context. A shortened date must be resolved within the stated RAW/context before comparison.

### 21.1 XAUUSD historical/Bearish and Source snapshot

- `2026-09-03 19:30:00 A → 19:42:00 S Blue → 20:00:30 E1 Blue`; internal `S Blue Advanced @ 2026-09-03 21:06:00` has an explicit eligible route; `23:16:30 E1 Blue` is a historical anchor.
- `2026-09-04 01:33:00 A`, `02:36:00` StopAll, `05:11:30` Blue visibility, `07:03:00 S Red`, `16:57:30 A`, `20:19:00 A`, `22:25:30 A`, `23:24:30 A`, `2026-09-07 01:38:00 A`: verify exact owners and no invalid duplicate re-entry.
- Accepted opposite Order near `2026-09-04 17:45:30` and downstream E Red chain `18:05:30 → 18:50:00` must be checked as physical Order/parent chronology, not inserted manually.
- V5.4.4 anchor: after `StopAll10 @ 2026-09-03 18:49:30`, repeated `E1 Blue` at `20:00:30`, `21:17:00`, `23:22:30`, `2026-09-04 01:48:30` arms **one exact numbered group**; the accepted S Red `2026-09-04 02:36:00` undergoes the source-defined promotion. Different E numbers do not add to that group.
- V5.4.5 Mode-B continuation chain after `A @ 2026-09-09 03:33:30`: native Mode-B opposite Orders `04:16:00 → 04:17:30 → 04:20:30 → 04:24:00`; final owner produces `S Red @ 04:29:30`, not erroneous `S Blue @ 04:45:00`; downstream `E1 Red @ 05:15:30`, StopAll `06:23:00`. Check coverage in applicable RAW and avoid using shortened timestamps without the full date.

### 21.2 USOIL Bullish

- `2026-09-09 07:11:30 A` is historical valid; subsequent false A re-entries `08:28:00`, `08:48:30`, `09:15:00` must be absent in the corresponding accepted lifecycle. `09:00:00` E Red is a check.
- Blue→A source chain `2026-09-09 19:06:30 → 19:20:30` must preserve A's causal source.
- `2026-09-10 05:48:30` Order_B is independent and must not be deleted simply because an earlier Order exists; only physical identity/provenance and lifecycle may decide.
- `2026-09-10 09:03:00 E4 Red` and accepted S Red chronology near `09:34:30` are connected regression checks.
- `2026-09-10 13:56:00 E1 Blue → 14:26:30 E2 Blue` must not be displaced by invalid `13:51:00 S Red`. `2026-09-10 17:49:30 S Blue` is a historical accepted path.
- `2026-09-11 01:50:00 A → 02:35:30 S Blue → 02:42:30 Order → 02:44:00 E1 Blue` is a full parent/Order regression chain.

### 21.3 USOIL Bearish

- Transfer/chained Blue around `2026-09-11 09:23:00` needs correct inherited/active stop conditions before any A.
- `2026-09-11 16:19:00` Blue E must not be replaced by lower-priority/internal S Red candidate evidence.
- `2026-09-11 17:43:00 S Blue` is accepted in its recorded cycle; `18:01:30` must not re-enter as invalid A under that owner.

### 21.4 Historical memory-only additional checks

**Full detail is mandatory:** Appendix D.1–D.7 records every concrete historical `memory.txt` valid/invalid A/S/E/StopAll, Order, Blue, Reset and FARAZ case, with prices/stop sources, source-versus-decision chronology and missing-date/fixture caveats. Appendix E preserves the associated general rules. The short entries above are an index only; they are **not** the complete list. Pending August XAUUSD anchors remain reported/unverified unless reproduced with current Source; the historical FARAZ and V1.x cases retain their own distinct version/RAW scopes.

## 22. Mandatory tests and equivalence criteria

On any **semantic Source change**, the validation evidence must cover:

1. Python syntax/compile of all changed modules; import/bootstrap in the **real `engine/bridge` + `engine/pipeline` deployment layout**, not only a flat folder. Check dependent class/function signatures, public exports, file paths and required dependencies.
2. Exact reported case with complete relevant RAW, Decimal values and strict comparisons, exact event chronology, full parent chain, prior/current lifecycle owner, Order geometry/provenance and public output.
3. Opposite-direction exact-mirror test. Validate reflection of actual geometry and equal treatment of invariant family/priority/schema.
4. All four canonical RAW baselines in both directions (eight runs) when feasible for a behavioral release. Compare A/S/E/StopAll counts and S/E family split, all ordered Behavior identities/source and decision timestamps, prices/levels, parent links, Reaction/Reset/Blue/OrderAudit diagnostic counts and **full final JSON/payload hashes**.
5. Timestamp-level locked positive/negative anchor checks, stage invalidation, Internal exception, historical rescue, strict tie/equality and StopAll hard-boundary counter reset. Confirm physical identity uniqueness, single exact parent-stop cause and bridge closure.
6. Full-range vs reduced presentation-range consistency: matching in-range final objects with preserved outside-range parents/OrderAudit lineage. Check field names/types/nulls, string Decimal representation, epoch/timezone, ordering and stable tie keys.
7. For indexing/cache/large-loop changes, profile at least one stress dataset and compare runtime, memory and exact payload. A faster result with one unexplained semantic difference is a **failed refactor**.

**Zero-difference refactor:** require exact equivalence of all observable behaviors, order, parents, stops, provenance, lifecycle, public visibility and serialization, plus relevant internal diagnostics. No intent-based exception. The HPZR1 history reported eight direction runs with hash-identical outputs on four datasets; it also explicitly reported that the largest 309,906-row historical baseline could not finish its *old* unoptimized comparison within a 240-second environment ceiling. Do **not** retroactively record that incomplete full before/after comparison as PASS. Performance history (`61.54s → 31.65s`, approximately `1.94×` in the reported aggregate) is historical context, not a fresh measurement or guarantee.

**If tests cannot complete:** report completed case/result, exact incomplete case, failure/timeout reason, impact, and remaining checks. Do not mark `DONE`, `PASS`, `ZERO DIFFERENCE` or `100% verified`. A deliverable may be explicitly labeled *unverified draft* if the user wants it despite incomplete verification; it must not be represented as a production release.

### 22.1 First-diff comparison is mandatory

An identical census can hide one missing and one false Behavior. Sort by exact decision/confirmation and stable identity; compare one stage at a time. Classify every diff as intended semantic correction, necessary mirrored consequence, demonstrable downstream correction, version drift, or unexplained regression. Stop on the first unexplained diff. Restart the full trace after repairing that first state; do not tune later output symptom-by-symptom.

### 22.2 Suggested regression report fields

```text
Source hash/versions | RAW SHA-256 | direction | main/lower timeframe | timezone
complete calculation range | visible range | number of records | run duration
A, S Blue, S Red, E Blue, E Red, StopAll, Total Behavior
Reaction, Reset, public/internal Blue, OrderAudit counts
ordered Behavior payload hash | full JSON hash | exact differences | PASS/FAIL/NOT RUN
```

The test harness belongs outside production Source. Record progress/timing to the established telemetry channel without contaminating JSON stdout; do not alter order/geometry to make comparisons convenient.

## 23. High-performance implementation discipline

Correctness and deterministic lifecycle ownership outrank speed. Optimize proven hotspots; never weaken semantics for faster output.

- Parse RAW once; normalize Decimal once with safe type+value cache; construct lower/main candles and sorted time arrays once per run. Preserve duplicate timestamp aggregation, source identity and original chronology.
- Prefer `bisect` on immutable sorted timestamps, indexed first-less/first-greater, range min/max structures, suffix/prefix indexes, monotonic forward scans and per-run cached confirmation/Reset/Order-stop/candidate lookups over repeated nested full-history scans.
- Scope caches to immutable input, direction, timeframe, relevant exact range and **every semantic key**. A key must distinguish canonical vs bounded/noncanonical Order geometry and provenance, and a cache must not reuse accepted state from another lifecycle, dataset, direction or run.
- Avoid global mutable cross-run ownership state, object-ID cache collisions, repeated full-history sorting, repeated history-prefix list creation, repeated E-by-E all-Order scans, unintended O(N²)/O(N³) behavior or serialization-time geometry recomputation. If a global cache exists in current Source, inspect its identity/lifetime safety before changing it.
- Reuse the current exact lower-timeframe indexed implementation; do not approximate with 30s OHLC, floats, rounded prices, skipped candidates, changed search boundaries, invalid equality or lossy event coalescing.
- Preserve stable sort keys, especially `(confirmationTime, FirstIndex, BreakIndex)`, stable geometry tie rules, accepted ledger insertion/provenance and final JSON ordering.
- Profile actual stage timings before optimization; isolate an optimization-only diff; prove byte-/semantic-level zero difference against its own pre-change baseline; measure performance only after correctness. If a function becomes faster by dropping valid historical evidence, it has failed.

## 24. Version control, metadata, Source/Reference synchronization

For **each modified file independently**:

1. Start from its Current approved version and save its immediately preceding revision as Previous; ensure dependent files share a compatible accepted snapshot.
2. Apply minimum owner-correct edit, with a concise accurate changelog entry specifying the semantic contract and regression consequences; increment version following project convention.
3. Use a **full timezone-aware Last Modified Date & Time** for future changed production/reference documents; do not invent missing older metadata or touch unchanged modules just to stamp them.
4. Update **both** Bullish and Bearish References for any change to behavior, directional mirror, lifecycle, public output/serialization or embedded Source. Their code snapshots/manifests/source-symbol maps must be regenerated from final production bytes. Documentation-only changes must not claim production behavior changed.
5. Record exact current versions, hash, compatibility, old→new changes, known expected output changes, benchmark limitations and user approval status. Never describe a proposed next release as current.
6. Keep document-only release revision distinct from engine semantic version. Version strings and timestamp metadata are provenance and integrity information, not trading-rule predicates.

Three audit statuses must remain visible: actual Source behavior, matching intended Reference rule, and user-requested potential change. If they disagree, describe drift, not a fictitious unified interpretation. A historical Reference change note may describe a superseded rule; explicitly locate its replacement in the latest Source.

## 25. Packaging and artifact delivery

**Production change ZIP:** unless explicitly asked otherwise, package only production Source files *actually modified* plus the matching updated Bullish/Bearish References required by that change. Preserve the project-relative deployment path if useful. Exclude unmodified modules, obsolete references, backup copies, RAW, tests, temporary traces, profiling dumps, generated JSON and `__pycache__`. Verify the ZIP contents against the intended change list, then compute its SHA-256 if possible. Do not package a production-approved release when required focused, mirrored or baseline checks have failed or not run; clearly label a requested incomplete artifact as a draft.

**Documentation-only tasks:** deliver only the requested document(s); do not create a source/release ZIP or imply that a `AGENT.md` update changed engine behavior. If a user explicitly requests a one-file handoff, the single updated `AGENT.md` is sufficient; no unnecessary files or test data. Use the exact requested filename and do not silently overwrite other project assets.

## 26. Technical response and report format

The user generally prefers concise, direct, natural Persian with exact technical English terms, correct Persian half-spaces and punctuation; keep code, exact symbols, full timestamps, filenames and release strings unchanged. Do not patronize or add boilerplate praise. For a simple question, answer simply. For forensic claims, be deep enough that the conclusion can be reproduced; do not simply cite a function name without explaining the relevant condition and causal state. Do not force the user to restate rules already present in the project.

Preferred disputed-Behavior report (omit fields only when genuinely irrelevant):

```text
Result: Verified correct / Verified wrong / Unverified
Expected: [claimed and/or Source-derived; label its status]
Actual: [reproduced Source output]
First Diff: [first exact event, invalid state, file:function:condition]
Root Cause: [proved causal logic or explicitly provisional hypothesis]
Correct General Rule: [state transition, not fixture condition]
Mirror Impact: [Bullish and Bearish; what stays invariant]
Affected Module(s): [owner and interface dependencies]
Regression Risk: [protected previous paths/counters/Order/visibility]
Recommended Patch: [smallest correct semantic change]
Tests: [RUN/PASS/FAIL/NOT RUN with real evidence]
```

For a human-readable event, give `Behavior, Direction, FormedAt, Price, Parent, Stopped Previous, Reason, DecisionAt, exact lower event, Order identity/mode/causes/stop, Reaction, Lifecycle Owner, Next Effect`. A table/trace is appropriate for multi-event ordering; avoid clutter for routine replies. If the problem is not proved, say what is established, where the first unresolved discrepancy lies and exactly what evidence is missing. Never extrapolate a new trading rule from generic finance knowledge.

## 27. Session onboarding and handoff

At the start of substantial TradingBot work:

1. Read this `AGENT.md` completely, then **both complete** current standalone Algorithm References, including Reaction, Reset, Blue, A/S/E, Order_A/B, lifecycle, StopAll, reconciliation, internal/public status, historical rescue, serialization, mirror, ownership and relevant embedded Source/manifest. Do not stop at introductions.
2. Inventory/read current nine production modules, versions, actual deployment/orchestration and dependency compatibility. Identify the real cross-stage priority table, `direction_policy` mirror primitives and relevant RAW.
3. Determine the user's exact task, reported timeframe/direction, calculation/presentation range and most recent user-confirmed Current/Previous revisions. Do not re-ask established information.
4. For bugs, reproduce and trace the complete RAW→serialization path. For audits, perform the three independent equivalence checks. For refactors, capture full pre-change payload first. For document-only tasks, read evidence and state clearly what was not executed.
5. Preserve known successful examples as version-scoped regression anchors, not algorithm branches. Carry forward only approved files/results to the next handoff.

Minimum useful project handoff: this guide; all nine Current production files in the bridge/pipeline layout; both matching Current Bullish/Bearish References; the four canonical RAW where their regression runs are needed; plus relevant additional case RAW and real current regression artifacts. If Source files are unavailable but a matching HPZR2 Reference's embedded code/hash is confirmed, it may support reconstruction of **that exact documented snapshot**, not a claim about an unseen newer build.

## 28. Release gate / definition of DONE

A behavioral correction is **DONE** only when the general root cause, first divergence, owner, exact relevant RAW chronology, Decimal/strict comparisons, all affected parent and Order provenance, opposite-direction mirror, lifecycle/StopAll boundary, visibility and serialization are established; a small correct Source change is implemented; affected References exactly reflect it; focused and required regression checks are actually executed with no unexplained differences; and the requested release artifact is verified.

Pre-delivery checklist:

- [ ] Identified actual latest Current/Previous and compatible nine-file Source/Reference manifest.
- [ ] Independently reproduced the reported case (or explicitly marked unverified).
- [ ] Found first erroneous state rather than patching downstream labels.
- [ ] Root cause and general dataset-independent rule proved.
- [ ] Changed only correct owner and necessary interfaces; no fixture/time/price/symbol hardcodes.
- [ ] Decimal, Doji GREEN, strict equality exclusion and exact RAW chronology preserved.
- [ ] Bullish/Bearish geometry mirrors; invariant family/priority/schema does not mirror.
- [ ] A→S→E→StopAll ownership, invalid-descendant exclusions and recursive E remain correct.
- [ ] Physical Order identity, creation/use provenance, OrderAudit and bridge closure checked.
- [ ] StopAll exact Blue-group semantics, active owner and hard boundary checked.
- [ ] Historical/calculation/internal/public/presentation distinctions checked.
- [ ] Reported case, mirror and applicable old/new anchors checked with exact event-level comparison.
- [ ] Four canonical baseline datasets, both directions, checked or limitations recorded.
- [ ] Compile/import/deployment, final payload and any relevant performance tests completed.
- [ ] Both current References/embedded code/manifest synchronized if needed.
- [ ] Only changed files' versions/full modified metadata updated.
- [ ] Requested output/ZIP contains intended files only; SHA-256 recorded when available.
- [ ] Every reported PASS or DONE corresponds to actual executed verification; unverified drafts are labeled.

**Do not make an output correct for one candle by breaking another valid candle. The first incorrect state, exact Source, physical RAW and demonstrable regression impact govern the fix.**

---

## Appendix A — Integrated-source provenance and resolution of conflicts

This guide integrates three prior instruction sources: (1) original library `AGENT.md — Trade Project Operating Guide` (30 sections, historical census/anchors); (2) supplied `TradingBot_AI_Operating_Protocol(1).md` (64 sections of forensic execution and reporting); (3) supplied `memory.txt` (TradingBot-specific context, historical release/bug notes, writing/interaction preferences). The current nine Python Source modules and the two supplied `5.4.5-HPZR2` comprehensive standalone References were used as the **authoritative behavior correction layer**. Personal profile and unrelated Server, Zabbix, security, motorcycle, historical, political or other life-context material in `memory.txt` is intentionally not copied into a TradingBot agent instructions file; it is not a trading algorithm rule.

Explicit conflict handling:

| Historical statement | Current resolution |
|---|---|
| Prior protocol Section 22 suggests dominant-Blue progression across E numbers / dominant-only counting for S Red StopAll. | Superseded: Source `lifecycle_engine.py` `1.15.0` and V5.4.4+ References count **accepted exact Blue group** occurrences cycle-wide; different E numbers do not combine, dominance and latest strict stop are not extra gate conditions. |
| Older V5.4.2/5.4.3 notes require current dominant Blue and/or latest strict stop for the S Red reversal gate. | Historical change notes only; use explicitly superseding V5.4.4 behavior and present Source. |
| Original `AGENT.md` says its old census represents its then-Current source. | Preserve recorded numbers but treat as **historical and unverified** for the newly supplied HPZR1/HPZR2 snapshot until executed with exact matching Source. |
| `memory.txt` suggests A-stop→S discrepancy and `V5.4.6` fix. | Pending test hypothesis, not approved release or hardcoded expected behavior. Reproduce and verify Source including current valid StopAll gate before making any correction. |
| Original guide demands full Last Modified for every changed file, while some supplied untouched modules have date-only/no modified metadata. | Report actual snapshot metadata without inventing it. Require full timezone-aware metadata on **future edits**, but never stamp untouched files to make them appear newer. |
| Only four canonical census RAW vs additional August XAUUSD RAW. | Keep original four baselines unchanged; use August RAW for separate focused validation unless the user explicitly changes the baseline registry. |
| Earlier Source/refactor details or historical filenames differ from current embedded/source versions. | Verify file-by-file Current, Previous, hash, dependencies and matching release. Never promote memory or old ZIP over confirmed Current. |

## Appendix B — Quick immutable rule card

```text
TRADING BEHAVIORS       A, S, E, StopAll only.
TRADING STAGES          RAW → Reaction/Reset → Blue → A → S → E → StopAll → visibility → JSON.
CANDLE COLOR            GREEN iff Close >= Open; RED iff Close < Open. Doji GREEN.
DECIMAL                 Use Decimal, never binary-float price decisions.
BULLISH STRICT STOP     Low < Level; Reaction confirmation High > BoxTop.
BEARISH STRICT STOP     High > Level; Reaction confirmation Low < BoxBottom.
EQUALITY                Not a crossing.
MIRROR                  Low↔High; min↔max; <↔>; FirstRed↔FirstGreen.
INVARIANT               Family labels, Doji, stage/priority, identity, lifecycle, schema.
PHYSICAL ORDER ID       (FirstIndex, BreakIndex); preserve original formation causes.
ORDER_B                 Independent reset-leg cause; NOT native Reaction Mode B.
STOPALL                 Hard boundary; cycle-wide accepted EXACT Blue-group repetition.
CURRENT GROUPS          S Blue one group; E1 Blue/E2 Blue/... separate numbered groups.
FIRST DIFF              First wrong state wins. Fix owner, not a downstream symptom.
RAW                     Lower-TF event chronology; full calculation history.
REGRESSION              Exact case + mirror + old anchors + both directions of 4 baselines.
REFACTOR                Observably zero-difference or FAIL / NOT VERIFIED.
NEW RELEASE             Only after real Source/Reference sync, tests and approval.
```

---

## Appendix C — Exhaustive TradingBot memory-to-agent migration: evidence classes and interpretation

This appendix is **part of the mandatory agent contract**, not optional reading. It preserves the TradingBot-specific material in `memory.txt` at the level of concrete rules, versions, behavior examples, exact timestamps, prices, validation scope, provenance and known uncertainties. Sections 1–28 of this guide remain the operational rules; the current verified Source and matching References control the actual implementation. Historical observations in this appendix are **regression assertions tied to their original dataset, direction and version**, not a means to hardcode the algorithm. A claim in transferred memory is not upgraded to an independently passed test by being included here.

**Evidence classification used below:**

- **CURRENT SOURCE / REFERENCE RULE:** inspected in the supplied `V5.4.5 / HPZR1` nine-file Source and/or matching `HPZR2` References. Re-inventory when a newer Current file arrives.
- **HISTORICAL ACCEPTED:** explicitly recorded as correct or incorrect in earlier project memory or the former `AGENT.md`; retain as a protected, version-scoped regression assertion, not a fresh run result.
- **HISTORICAL CONDITIONAL:** recorded for an older release, separate RAW, or incompletely identified test range. Verify its original scope/expectation artifact before treating it as an active release gate.
- **REPORTED / PENDING:** user-reported desired result, with unconfirmed current Source result or first divergence; investigate rather than presume an approved new rule.
- **SUPERSEDED:** earlier wording no longer authoritative where it conflicts with the newer Source/Reference. Keep its reason and historical example so a later agent does not accidentally reinstate it.

**Temporal normalization:** A time without a full date is reproduced **exactly as the memory recorded it** and scoped to its dataset/sequence. Do not invent a calendar day for an isolated `04:12:30`, or infer that two adjacent example blocks refer to one day. Once original RAW/expected output identifies the date, record the resolved full `Asia/Tehran` timestamp in a new regression artifact; never silently rewrite the archived value. Exact lower-TF timestamps are distinct from main-candle/source timestamps.

### C.1 Coverage map for the original `memory.txt`

| Original memory section(s) | Fully retained in this guide |
|---|---|
| 3–6, 9–14, 19–28, 35–44, 46–48, 56, 58–60, 63–69, 73–75 | Normative project operating requirements in Sections 1–18, 22–28 and detailed clarifications below. |
| 7–8, 71–72 | Pending V5.4.6 case register (Section 19 and Appendix D.6), explicitly not an approved release. |
| 15–16 | Exact-group Blue repeat and dominance, including V5.4.4 supersession and historical E1 Red example (Section 14 and Appendix D.5). |
| 17–18, 20–25 | Candidate→accepted A, post-A-stop, internal Blue, visibility, shared Order-stop, S Red, S Blue Type-4, final same-source E ownership (Sections 8–15 and Appendix E). |
| 26–28, 31–33 | Order identity, Mode-A/native Mode-B vs independent Order_B, E chain and exact behavior/Order regression entries (Sections 11–14 and Appendix D). |
| 29–34, 45 | Four current historical census datasets, additional historical RAW/FARAZ and older V1.x anchors (Section 20 and Appendix D). |
| 38–40, 49 onward where relevant to communication | Version/release/reference/ZIP rules and project-context transfer (Sections 24–28, Appendix F). |
| 1–2, 49–55, 57, 70 (non-TradingBot personal/other-project details) | Not made trading instructions. The relevant language, precision, evidence, no-guess and response preferences are in Sections 1, 26–28. Other personal domains are deliberately outside a TradingBot `AGENT.md`. |

This mapping does **not** substitute for the full chronological registry below. The earlier abbreviated Section 21.4 is superseded by Appendix D; do not treat a short summary as the complete set of protected historical examples.

## Appendix D — Full historic correct/incorrect Behavior and Order registry

**Registry use:** Before any code change, select the matching RAW/direction/Source revision; obtain original expectation where available; independently reproduce current state; then compare exact object identity, formation/decision/stop chronology, parent, Order cause, lifecycle owner and final serialized representation. `Expected` and `Forbidden` are memory assertions, not output injection instructions. A `False`, `NOT` or `wrong` entry must be checked for the exact reported scenario, not globally banned by its timestamp. **No record in D is a production `if` predicate.**

### D.1 XAUUSD historical 1s (canonical census A) — Bearish 30s

Physical file: `RAW FOREXCOM_XAUUSD 1S FROM 2026-09-03 19-05-40 TO 2026-09-08 03-18-28.json`. Historic detailed oracle filename: `TradingBot_Bearish_30s_Valid_Invalid_Behaviors_V1.txt` (not supplied here; retrieve it when comparing its exact older release). At one project stage, the accepted A/S/E in this dataset were considered **immutable under unrelated Reaction/Reset/Blue/StopAll corrections**, unless an explicitly accepted later rule superseded their outputs. All rows are historical accepted/conditional assertions until reproduced on the precise relevant revision.

| Recorded event / chain | Historical expected outcome and causal note |
|---|---|
| `2026-09-03 19:30:00 A → 19:42:00 S Blue → 20:00:30 E1 Blue` | Preserve this accepted parent/stage chain; require exact timeline and identities. |
| `2026-09-03 21:06:00 S Blue Advanced` | The explicit Internal-Reaction route remains eligible; do not suppress merely because it is internal. |
| `2026-09-03 23:16:30 E1 Blue` | Accepted historical E anchor. |
| `2026-09-04 01:33:00 A` | Expected valid. `2026-09-04 01:35:30 A` was marked false; **S Blue** was the expected downstream type. |
| `2026-09-04 02:36:00 StopAll` | Historical accepted promotion; verify exact cycle-wide Blue-group counter under V5.4.4+ (see D.5). |
| `2026-09-04 05:11:30 Blue` | Visibility/Blue state must be checked; do not fix by deleting calculation Blue. |
| `2026-09-04 06:26:00 A`, `07:07:30 A` | Historical **false A** assertions. Preserve current owner/cycle constraints. |
| `2026-09-04 07:03:00 S Red` | Historical accepted S Red anchor. |
| `2026-09-04 16:57:30 A` | Correct A. `2026-09-04 16:58:30 A` is **false**: the earlier A source is frozen at exact Reaction confirmation. |
| `2026-09-04 16:58:00` Bearish Reaction | Valid First/Reaction; exact Breakout is `16:58:38` in 1s RAW; the Break-main remainder must not rewrite A's earlier source. |
| `2026-09-04 17:45:30` Order | Correct physical Order; recorded Order stop `4419.235`; accepted `E1 Red @ 18:05:30` followed by `E Red @ 18:50:00` in the historical chain. Check Order stop geometry and cause, not merely Order label. |
| `2026-09-04 19:59:30` Order | Correct; stop-source main candle `19:59:00`. `20:04:00` Order marked **incorrect** in the same scenario. |
| `2026-09-04 20:19:00 A` | Correct. No stale, invalid or superseded Order ownership may recreate a deleted Order downstream. |
| `2026-09-04 22:25:30 A`, `23:24:30 A`; `2026-09-07 01:38:00 A` | Additional protected historic A anchors. |
| `2026-09-07 10:14:00` | Recorded `up/reset` chronology case, **not** automatically a Behavior; inspect exact Reset event and owner. |
| `2026-09-04 17:13:30` native Order Mode B | Historic Order explicitly labeled `Mode B`: stop is BoxBottom with recorded source time `17:12:00`. The memory label alone does **not** prove this Order has independent Order_B/reset-leg provenance; confirm the native Reaction mode, formation causes, physical identity and dataset before treating it as a current oracle. |

### D.2 USOIL 5s 11–15 September (canonical census D) — Bearish 30s

Physical file: `RAW FXCM_USOIL 5S FROM 2026-09-11 02-53-30 TO 2026-09-15 11-03-45.json`. **Dates below are deliberately omitted where the original memory supplied only a time;** do not manufacture the day.

| Memory time / event | Historical expected outcome / evidence |
|---|---|
| `04:12:30 A` | Expected **visible A**; distinguish valid hidden candidate from public serialization. |
| `04:19:00 Order` | Expected physical Order, native Mode A; recorded stop uses `Low @ 04:15:30`. Verify first/break geometry. |
| `05:11:30 A` | Expected A. |
| `05:57:30 A → 06:01:30 S Red` | Protected A→S handoff chain. |
| `09:23:00 Blue → 09:24:30 Blue stop` | Chained-stop transfer case: next aligned downward Reaction at `09:30:00`, Breakout `09:31:00`; maximum High in specified inclusive interval has source `09:29:00`; carried effective Blue stop recorded as `101.409`. Check Blue owner and exact source. |
| `09:49:00 A` vs `09:53:00 A` | `09:49:00 A` was **incorrect** and `09:53:00 A` **correct** in the transfer scenario. Do not collapse genuine Blue stop/inherited stop conditions. |
| `16:19:00` | Accepted **E2 Blue**, not S Red. This is the same-source/cross-stage priority and invalid S-root regression. |
| `20:02:00` | Accepted **E5 Blue** historical anchor. |
| `20:00:30 Order` | Correct; stop source `19:59:00`. `20:05:30 Order` historically incorrect in its owner/expiration context. |
| `2026-09-11 17:43:00 S Blue` | Accepted; `2026-09-11 18:01:30 A` must **not** re-enter the active S-owned cycle. Source's stage-invalid A descendants cannot spawn another S or E. |

### D.3 USOIL 5s 8–12 September (canonical census C) — Bullish 30s

Physical file: `RAW FXCM_USOIL 5S FROM 2026-09-08 07-23-20 TO 2026-09-12 00-14-55.json`. Where the memory gave a time without date, keep that limitation.

| Memory time / chain | Historical expected outcome / evidence |
|---|---|
| `04:49:00 S Red`, `05:43:30` stop, `05:26:00 E1 Blue` | **Preserve exact recorded times without assuming this is a causal ordering:** the recorded E source precedes the reported S stop. Resolve source vs decision vs stop and the full date from RAW before deriving a parent chain. Do not mechanically assert `S stop → E` in this row. |
| `08:45:30` A stop; `08:55:00 A` | The later A marked **false** in the recorded stop/cycle scenario. Check source and stop main-candle reuse. |
| `09:17:30` | Valid recorded downward Reaction Order_A formation example. |
| `2026-09-09 07:11:30 A` | Correct; false A re-entries `08:28:00`, `08:48:30`, `09:15:00` should not reappear under the accepted owner. |
| `2026-09-09 09:00:00 E4 Red` | Correct, reported strict stop `2026-09-09 09:07:00`, followed by `E5 Red Candidate @ 2026-09-09 09:07:30`. **Candidate is not automatically accepted E5**. |
| `19:06:30 A` | Historically **false** A assertion; candidate/Blue geometry around this time must preserve the accepted later A. |
| `2026-09-09 19:17:00 A` vs `2026-09-09 19:20:30 A` | Historic V1.4.4 mirror fix: `19:17:00` wrong, `19:20:30` correct. If the full date is needed, locate it in the case RAW/reference before comparing. |
| `2026-09-10 05:48:30 Order_B` | Valid independent Reset-leg cause/Order; **do not** delete merely because another valid Order exists. Determine canonical physical identity and causes. |
| `2026-09-10 09:03:00 E4 Red` and `09:34:30 S Red` | Protected historic E/S order and owner relationship; verify chronology rather than imposing a simple parent arrow. |
| `2026-09-10 13:56:00 E1 Blue → 14:26:30 E2 Blue` | Correct recursion; `13:51:00 S Red` is **not** accepted final in the corrected lifecycle and must not replace this E Blue chain. |
| `2026-09-10 17:49:30 S Blue` | Accepted historical S Blue; verify preceding Behavior and current stage ownership. |
| `2026-09-11 01:50:00 A → 02:35:30 S Blue → 02:42:30 Order → 02:44:00 E1 Blue` | Protected chain. Order's recorded stop source `02:40:00`; verify event/source timestamps and OrderAudit provenance. |

### D.4 XAUUSD broad 5s (canonical census B) — Bearish 30s

Physical file: `RAW FOREXCOM_XAUUSD 5S FROM 2026-09-03 18-44-00 TO 2026-09-19 00-29-35.json`. Some earlier XAUUSD 5s expectations instead used the shorter historic file `2026-09-03 19:05:30 → 2026-09-16 00:29:30`. **Do not conflate the two physical files or their full-history state**; use original run/version evidence to identify which contains the listed scenario. An isolated hour has no assured calendar day in the transferred text.

| Memory time / event | Historical expected outcome / evidence |
|---|---|
| `04:29:00` | **E2 Red = true; E2 Blue = false.** The lifecycle must select the accepted correct E family, not duplicate both. |
| `11:18:30` | **E3 Red = true; E3 Blue = false; E1 Red = false; E1 Blue = false** in that particular competing-candidate case. Check exact parent/decision chronology. |
| `2026-09-06 06:23:00` | **E1 Red** historical selection; context includes `S Blue @ 04:45:00` and `S Red @ 05:48:30`. Check which S is accepted and relevant Order ownership before E reconciliation. |
| `21:46:30`, `11:04:30`, `21:40:00`, `22:29:30`, `01:58:30`, `11:25:00`, `14:41:00` | Seven Orders historically **excluded due to expired owner**. These are separate candidate times, not one continuous event sequence. Retest each against original lifecycle; never globally forbid these clock values. |

### D.5 Versioned StopAll, dominant-key, native Mode-B and E-recursion anchors

These cases are cross-cutting and must be tested on their **specific revision and physical RAW**, not merged as a new unconditional algorithm definition.

1. **Cycle-wide Blue-group gate, current V5.4.4+ contract:** Since calculation start or last StopAll boundary, count every *accepted* exact behavior group occurrence; `S Blue × 2` or `E1 Blue × 2` or `E5 Blue × 2` independently arms an S Red reversal gate. Do not add `E1 Blue + E2 Blue`, do not require current dominance or the latest Blue's strict stop for this gate. A later valid **accepted** S Red may promote to `opposite-s-group-stop`. Current dominant owner still matters to other (`sequence-group-stop`) logic, and must not be equated with cumulative historical occurrence count. A repeated accepted `E1 Blue` increments its own group without changing the dominant key. Source/reference explicitly supersedes older dominant-only wording.
2. **Historical current dominance example:** Following StopAll at `2026-08-26 02:21:30`, memory reports `E1 Red` as the dominant behavior, with later accepted `E1 Red` occurrences repeating its same key. No date/time for those later repeats was supplied; treat this as a conceptual/chronology probe, not a pass of an unlisted fixture.
3. **V5.4.4 accepted XAUUSD check:** The reference describes `StopAll10 @ 2026-09-03 18:49:30`; accepted `E1 Blue` repeats `2026-09-03 20:00:30`, `21:17:00`, `23:22:30`, `2026-09-04 01:48:30`; the accepted S Red `2026-09-04 02:36:00` is promoted under the **same exact group, cycle-wide** rule. This supersedes the older requirement for current Blue dominance/strict latest Blue stop.
4. **V5.4.5 Order native-Mode-B refresh:** On the extended August→September XAUUSD 5s case, `A @ 2026-09-09 03:33:30`; provisional canonical opposite Orders in a consecutive native Mode-B chain at `04:16:00`, `04:17:30`, `04:20:30`, `04:24:00`; final Order has stop source `04:21:00`; accepted `S Red @ 04:29:30`, **not** `S Blue @ 04:45:00`; then `E1 Red @ 05:15:30`, StopAll `06:23:00`. Replacement is allowed only for the next consecutive native Mode-B confirmation strictly *before* the current provisional S decision; native Mode A or decision at/before subsequent confirmation terminates refresh. This is **not** reset-leg Order_B. These explicit times are in current References, but are not a newly rerun test in this document update.
5. **Bullish E Red recurrence:** Memory records `E4 Red @ 2026-09-09 09:00:00`, stop `09:07:00`, `E5 Red Candidate @ 09:07:30`. Preserve candidate/accepted distinction and parent stop chronology. This point is repeated in D.3 because it belongs to that fixture.
6. **Current gate precedence:** The Source also has `sequence-group-stop` and `stopall-stop`. Never borrow criteria from `opposite-s-group-stop` and apply them to those other gates. StopAll is a hard state reset, not a mere visible tag.

### D.6 Pending extended-XAUUSD A-stop→S investigation (NOT yet a passed baseline)

Additional physical RAW: `RAW FOREXCOM_XAUUSD 5S FROM 2026-08-25 03-53-30 TO 2026-09-19 00-29-30.json`. Pending release name in memory: `V5.4.6`; proposed artifact name: `TradingBot_S_A_Handoff_Fix_V5.4.6.zip`. Neither a verified new Source nor approved full regression was recorded in the supplied materials.

| Parent A | User-reported desired S | Reported discrepancy to verify |
|---|---|---|
| `2026-08-26 10:55:30` | `S Red @ 2026-08-26 11:04:00` | Reported `StopAll1` instead; reproduce accepted S, cycle-wide counts and latest boundary. |
| `2026-08-26 22:41:30` | `S Red @ 2026-08-26 23:00:00` | Recheck A-stop→S handoff, owner and any StopAll promotion. |
| `2026-08-28 08:31:30` | `S Red @ 2026-08-28 08:57:00` | Same general investigation, not an isolated output override. |

The previous diagnosis that the likely fault lies in **A-stop→S handoff and/or lifecycle/StopAll promotion rather than S geometry alone** is a hypothesis, not a verified first divergence. Source V5.4.4's valid cycle-wide StopAll rule cannot be weakened merely to force the desired label. Only a reproducible earliest invalid owner/state, mirrored general correction and complete regression may justify a new release.

### D.7 Additional historical datasets and expectation availability

| Historic source/fixture | Status, required handling |
|---|---|
| `RAW FARAZ_FOREXCOM_XAUUSD 1S`, epoch coverage `1788449740 → 1789388126`, Bearish `30s`, reported release `V16.4` | Historic regression fixture. Memory also records a historical accepted-behavior scope up to `07:35:30` (date not specified), except explicitly corrected cases. Prior temporary restriction on FARAZ testing dated `2026-09-17` was subsequently **revoked**. Its earlier behavior was considered correct except explicit corrections. An `E5 Blue @ 2026-09-07 18:24:00` was recorded as a correction; source/RAW timestamp compatibility and original oracle must be checked before turning this into a current accepted assertion. Not one of the four census files. |
| `RAW FOREXCOM_XAUUSD 5S FROM 2026-09-03 19:05:30 TO 2026-09-16 00:29:30` | Older Bearish 30s XAUUSD reference range. Distinct historical input, not the canonical broad file by assumption. Its older results require the matching Source release. |
| Historical restricted USOIL run starting `2026-09-08 20:36:00` within 8–12 Sep RAW, Bearish 30s | A *limited historical execution window*, not permission to truncate all current full-RAW calculations or an independent canonical baseline. Keep calculation/presentation scope explicit. |
| Historical V1.4.0, V1.4.2, V1.4.4 packages | Historical only. V1.4.2 recorded `e_zone_detector 6.6.1` same-source E finality; V1.4.4 recorded corrected Bullish A at `19:20:30` versus false `19:17:00`. Do not mix these modules into V5.4.5 Current. |
| Extended XAUUSD August→September RAW | Focused known-issue evidence and current Reference native Mode-B anchor, not an added fifth canonical census unless explicitly approved. |

**Dataset registry rule:** The canonical census is exactly A/B/C/D as defined in Section 20. Additional data may and often must be used for focused chronology or historical regression, but identify its source and scope. A historical fixture being absent is `NOT RUN / DATA UNAVAILABLE`, never a passing test or reason to silently substitute another file.

## Appendix E — Complete transferred memory rule and edge-case preservation

The following supplement makes explicit details that the earlier short `AGENT.md` referred to only indirectly. For each item, the **current Source implementation still wins** if a historical statement has been superseded.

### E.1 A, Blue and post-stop correctness

- After two eligible Blue strict stops, the second event creates an **A candidate**, not necessarily a final A. Validate it with the first Source-eligible aligned Reaction and its required strict Breakout, exact confirmation and source selection. Do not publish the candidate as an accepted A merely because a 30s candle appears to cross.
- A remembered Bullish post-A-stop rule prohibited using the *same A-stop main candle* as a new accepted `A`, `S` or `E` and resumed the next candle. **This is a historical conditional statement, not a blanket new universal restriction.** For every proposed fix check the current Source's actual pre-/post-decision handoff windows, exact intrabar event time and mirror; a valid same-main transition must not be disallowed by importing an obsolete summary. The case `08:45:30` stop vs false `08:55:00 A` is an anchor, not a rule predicate.
- Blue transfer: from an actually strictly stopped Blue, find the next eligible same-direction Reaction; freeze carried extreme over the **stop main candle through the entire following Reaction Breakout main candle, inclusive**, Bullish min Low / Bearish max High. Preserve strict stop source and equal-extreme tie handling. Do not borrow ordinary inherited stop from a live Scale Blue. Reset-Blue's permitted pre-stop structural chain is different.
- Aligned Blue geometry inside an opposite protected Reaction may remain valid **calculation evidence** even if public visibility or Order_B eligibility changes; historical memory says only Order_B may be excluded in one particular route, *not* that all such Orders are excluded. Current Source determines which `behavior_internal`, `calculation_valid` or provenance filters apply. Never erase a Blue just to remove a public label.
- A valid A, Blue, S or E must not disappear simply because a later opposite Reaction's Box visually contains it. Identify whether logical rejection, owner replacement, Internal restriction, public filtering or serialization caused the disappearance; preserve explicit permitted Internal paths (notably S Blue Advanced).

### E.2 S Red, Type-4, shared Order-stop and same-source owner

- A physical Order accepted through one Behavior can validate another independent open S/E candidate when its **exact strict Order-stop event** is inside the other's legal chronology. Original parent equality is **not** a necessary condition. One accepted Order-stop may support several independently eligible candidates; each must satisfy its own time/deadline, stage and lifecycle constraints. The current Source explicitly includes `parent-stop`, `carried-live`, `accepted-live` and `reset-leg` routes; StopAll uses the accepted reconciled history.
- Historic S Red criterion: in Bearish, an otherwise-eligible S candidate remains active until its relevant **High is strictly crossed**; an accepted Order-stop in its open window may decide S Red. Bullish reflects this with Low. This is not a permission to reuse an expired candidate, or to bypass the current Source's event ordering and priority.
- S Blue Type-4 is a **pre-Order** path: start at the actual A-stop main candle, extend through the latest eligible same-direction Reaction Breakout main candle, choose the directional extreme (Bearish max High / Bullish min Low), seek a strict cross *before eligible Order formation*, and require at least one `calculation_valid` **non-Internal Blue** within the Source-defined source→cross interval. No qualifying Blue means no Type-4 S; later aligned Reactions may refresh the candidate. An eligible Order ends this route. The original memory's shorter 'choose the max' description alone is insufficient.
- Once an accepted E owns `(sourceIndex, sourceTime)`, a losing S candidate on that same physical source must **not** later be recycled as the parent of a new E1. Maintain calculation/history evidence only where explicitly allowed; stage/StopAll/public ownership is final as governed by Source. Historic V1.4.2 cited this correction.

### E.3 Physical Order provenance, Mode distinctions and lineage

- Canonical physical identity is normally `(FirstIndex, BreakIndex)` (direction and run context already fixed). Audit `parent`, creator/owner, first/break/confirmation, mode, frozen BoxTop/BoxBottom, strict stop/stop source, creation causes, use route, and lifecycle state. Do not dedupe by approximate timestamp or by a reused label.
- `Order_A` is the A-owned Order route. Native Reaction `Mode A`/`Mode B` classify canonical Reaction geometry; independent **`Order_B` is a reset-leg formation cause**, not a synonym for native Mode B. Do not delete independently valid `Order_B` because another Order already exists. Multiple valid causes can map to one physical Order; keep the latest valid Reset-leg cause when multiple Order_B origins converge, and let one exact parent-stop cause be owned by a single physical identity under the current deterministic ranking.
- Distinguish **creation provenance** (`parent-stop`, `reset-leg`) from **reuse provenance** (`carried-live`, `accepted-live`). Reusing a physical Order for another E/S must not rewrite its original cause. Maintain canonical OrderAudit and enforce public S/E/StopAll references to an existing accepted physical Order, including when its First lies outside the requested presentation range.
- Normal Reset validity/public/Internal status is ignored **only for the expressly allowed raw opposite-Reaction evidence geometry check inside Order_B**; never generalize this permission to all Order or public Behavior generation. After StopAll, do not carry old physical Order ownership across the hard boundary without explicit current Source support.

### E.4 E recursion, StopAll and historical rescue

- E is recursive and parent-sensitive. Track E number, family, current accepted S/E parent, parent stop and exact event, Order identity/cause, inherited/current stop, candidate window, shared Order-stop and current lifecycle owner. E1→E2→E3 progression must not be misread as three simultaneously dominant groups; nor may an invalid A/S branch reopen E after a higher accepted owner takes the transition.
- Red/Blue behavior-family labels and cross-stage priority do **not** flip with market direction. The separate StopAll gates require separate predicates: accepted exact-group S-Red reversal (V5.4.4+), current sequence-group stop, and StopAll stop/retrigger. Never substitute an older 'latest dominant Blue must stop' requirement for V5.4.4's cycle-wide S-Red gate.
- Historical rescue of an earlier accepted E-parented Blue reset-leg/Order_B route, if later lost solely in reconciliation, is **presentation-only**, applied after final E/lifecycle/StopAll and OrderAudit decisions. It cannot create a new stop, renumber E, repaint Red/Blue, alter parents, or override a higher-priority final active E. Preserve the Source-defined exclusion for intermediate parents hidden by a surviving E.
- StopAll resets the prescribed cycle-local counters, dominant owner, repetition history and Order/sequence ownership. Historical E, S, A, Blue and Order objects may persist as records or necessary parent evidence, but must not become active after the boundary by accident.

### E.5 Earlier refactor and performance evidence — historical, not fresh test results

- Historical `V5.4.5 / HPZR1` performance-only changes: `reaction_engine.py 9.8.0`, `s_zone_detector.py 4.19.0`, `e_zone_detector.py 6.13.0`. Indexed lower-TF first/range lookups, pre-indexed immutable events, canonical Order-stop caching, confirmation-time indexes and collapsed repeated same-physical Order_B origins were intended to preserve all observable behavior. Per-run cache scope is mandatory; a cross-run stale cache is a correctness bug.
- Memory reports **eight full direction executions** as zero-difference for the four canonical datasets and aggregate performance changing from `61.54s` to `31.65s` (about `1.94×`). It also expressly says a **complete unoptimized-vs-optimized comparison on 309,906 RAW rows was not established** because the unoptimized baseline exceeded the 240-second environment ceiling; the optimized direction runs alone are not such a comparison. These are historical reported measurements, **not tests rerun during this documentation change**.
- The `HPZR2` Bullish/Bearish References are **documentation-only** standalone reconstructions embedding all nine Source modules and manifest/symbol index. Source, calculation, behavior, serialization and runtime semantics were stated unchanged from HPZR1. Code and document versions must be distinguished. Any later Source edit requires regenerating BOTH embedded copies from final bytes and independently confirming mirror semantics.
- Pure optimization/refactor requires identical ordered Reaction, Reset, Blue, A, S, E, StopAll, canonical OrderAudit, provenance, public visibility, parent/owner, exact timestamps, Decimal formatting and final payload. Performance can never justify dropping valid evidence. Use measured hot paths and run-scoped indexes; avoid nested full scans and speculative architecture rewrite. The same physical RAW plus same Current Source/direction/timeframe must produce deterministic output.

## Appendix F — Project memory continuity and exhaustive completion contract

1. **Current/Previous are per file, not a single project-wide numeric slot.** For every changed module/reference, record Current version/hash/approval and immediately prior Previous; promote only a validated user-accepted update. Do not falsely claim durable memory if the environment cannot retain it. Recover the latest files from the project when the task resumes, then compare version metadata, manifest, actual code and dependencies.
2. **Nine production modules are the default accepted ownership surface.** The historic installed bridge is `engine/bridge/trading_pipeline.py`; the other eight are under `engine/pipeline/`. Do not invent additional production modules for a local patch or copy imports into divergent deployment folders. `AGENT.md` and comprehensive References are documentation, not additional trading engines.
3. **Release metadata is correctness evidence:** bump the version of each actually edited file; use an accurate full timezone-aware modified timestamp and a concise changelog; preserve untouched metadata as-is; synchronize BOTH standalone References, complete final embedded Source, manifest and symbol index for semantic or source changes; correctly label documentation-only changes. The ZIP is versioned and includes only modified production modules plus required References unless another scope is explicitly requested. Test harness, RAW, `__pycache__`, profiler dumps and temporary traces stay out of production ZIP.
4. **Independent three-way verification:** (a) Source vs each Reference; (b) Bullish vs Bearish References; (c) Bullish vs Bearish actual Source branches. Report version drift, missing implementation or mirror mismatch openly. Never silently choose older prose over newer actual code. Preserve code-level eligibility, exact window inclusivity, same-lower-bar tie, shared priority, Internal status, Order_B and StopAll semantics.
5. **Do not claim total confirmation from compilation, SHA-256 or census counts.** `py_compile PASS ≠ full regression PASS`. A matching module hash establishes snapshot identity; an equal Behavior total can hide a swapped correct/incorrect candle. End-to-end validation needs actual RAW chronology, exact case + opposite mirror, full relevant history, structured first-diff ordered payload, all four canonical datasets in both directions where required, OrderAudit invariants, StopAll reset, actual deployment imports, Source/Reference equivalence and appropriate performance checks. Report `RUN/PASS`, `RUN/FAIL`, `NOT RUN`, `BLOCKED` separately with precise limitations.
6. **One earliest invalid state drives a fix.** Report expected vs actual at each stage `RAW → Reaction/Reset → Blue → A → S → E → Lifecycle → StopAll → visibility → serialization`. Identify original source/parent, exact lower event and strict Decimal predicate, accepted vs candidate state, Order cause and stop, gate/counter, current owner and public filtering. Fix the owner, not downstream label; every other changed historical output needs a causal explanation. Avoid timestamp/symbol/price/fixture branches entirely.
7. **Keep project transfer practical:** If short Project Instructions have a character limit (historically reported as 8,000 characters), use them as a compact bootstrap pointing to this full `AGENT.md`, nine Current Source files, both complete Current References and the four canonical RAW baselines; attach other RAW only for relevant cases. Never truncate this specification to fit a bootloader. The original historic `TradingBot_Bearish_30s_Valid_Invalid_Behaviors_V1.txt`, FARAZ oracle and prior complete serialized payloads are useful **when actually available**, but are not fabricated or automatically assumed present.
8. **Communicate in natural concise Persian unless asked otherwise**, preserving exact English filenames, symbols, `Decimal` comparisons, versions and times; keep Algorithm References completely English. For a bug, give `Result / Expected / Actual / First Diff / Root Cause / Correct General Rule / Mirror Impact / Affected Module / Regression Risk / Recommended Patch / Tests`. For a simple question answer briefly. Do not ask for already-provided project facts, falsely claim results, invent a timestamp or assert a guessed cause. When an exact older fixture or expectation is unavailable, describe what is established and label the remaining investigation rather than calling it a pass.
9. **Scope boundary:** `memory.txt` also describes unrelated user-specific interests, cybersecurity, servers, Zabbix and other projects. Those are not trading engine instructions and are not imported as market rules. All material TradingBot-specific decisions, stated expected/forbidden behavior cases, known uncertainties, dataset identities, old-release reminders and regression philosophy are represented in the numbered operating guide and Appendices C–F.

**Final rule:** Preserve the known-good ledger without forcing old expectations over newer verified production rules. This guide is a complete *instruction and historical-evidence register for the provided files*, but remains distinct from running the pipeline and proving every remembered anchor. Do not promote an unexecuted historical example or a draft V5.4.6 fix into a verified current result.
