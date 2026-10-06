# Reaction, Reset, Blue, A, direction and numeric forensic audit

Audit snapshot: 2026-10-05, Asia/Tehran. This is a read-only subsystem audit of the extracted authoritative package. Production Source and RAW were not edited. All executable probes and output live in this directory. Root audit owns package integrity, complete-engine regression, transport, independent refutation and the final classification.

## Finding ledger

| ID | Classification | First affected stage | Consequence proved here | Source |
|---|---|---|---|---|
| RX-01 | Confirmed implementation discrepancy | Reaction | Initial confirmation cannot seed the eligible next Mode-B First; both-direction synthetic reproduction and a genuine Bullish RAW missing identity | `reaction_engine.py:2148-2157`, `2183-2195` |
| BL-01 | Confirmed implementation discrepancy, two paths | Blue strike state | Directional extremes after exact Reaction confirmation can affect strike count, strike source, rendered line and downstream A provenance | `blue_line_detector.py:162-188`, `103-135` |
| RX-02 | Confirmed implementation discrepancy | Reaction/Reset chronology | A missing second main bucket changes inferred timeframe; Reset is attributed to a prior main candle in both directions | `reaction_engine.py:121-124`, `278-283`, `2174-2193` |
| RX-H01 | High-confidence method-contract discrepancy; production consequence unproven | Bounded Order geometry | Within one Break main candle the helper chooses earlier First even when its exact confirmation is later | `reaction_engine.py:1917-1924`, `1987-1988` |

These are discrepancies against the active prose and shared implementation contracts. The existing Reference Source embeds are semantically aligned with the defective implementation after newline normalization; semantic alignment does not refute the prose discrepancies. No fix direction was silently chosen when Source and prose differ. Independent refutation by a different audit agent remains the root audit's gate for final acceptance.

Final parent byte review: **strict Reference Source byte synchronization FAIL; semantic alignment of the twelve existing embeds PASS**. Eleven nonempty embeds use CRLF while maintained live/package files use LF; only the empty root `__init__.py` embed is byte-exact. All twelve existing embeds match after newline normalization and have equal Python ASTs. A thirteenth embedded `bridge/__init__.py` has no current live/package file, so it is an additional authority gap. Evidence is recorded in `../reference-byte-analysis.json` and `../check_reference_bytes.py`. This distinction does not affect **package versus live byte equality, which remains PASS for all twelve existing files**.

## RX-01: initial confirmation skips eligible Mode-B continuation

The active Bullish and Bearish References Section 4.4, line 80, allow a correctly colored confirmation main candle to become the next First when the post-confirmation remainder does not Reset. The shared implementation explicitly states that every confirmation opens Normal search at `reaction_engine.py:1589-1591`. Non-initial post-Reset confirmations invoke `_candidate_from_confirmation_remainder` at `2308-2310`; ordinary confirmations invoke it at `2349-2351` and `2387-2389`.

Initial confirmation instead sets `index = initial.break_idx + 1` and `candidate = None` at `2148-2157`, handles a possible intrabar Reset, then enters the next candle without invoking the remainder helper. The omission occurs before Blue, lifecycle, visibility or serialization.

Deterministic synthetic input has four 30-second candles, each with consistent 5-second aggregate geometry. Bullish main OHLC are `(8.5,10,8,9)`, `(9,9.5,8.5,8.7)`, `(10.5,11,8.6,9.5)`, `(9.5,12,8.7,11.5)`. There is no post-confirmation Reset. Unified canonical identities are `[(1,2)]`; the full shared directional state machine produces `[(1,2),(2,3)]`. The exact price/color reflection reproduces the same omission for Bearish. The first divergent object is Reaction identity `(2,3)`; a final-output count comparison alone is unnecessary to establish this omission.

Genuine RAW reproduction uses `RAW FOREXCOM_XAUUSD 5S FROM 2026-09-16 22-35-00 TO 2026-09-17 19-15-35.json`, complete supplied input at 30 seconds. First Bullish Reaction begins `2026-09-16 22:42:00`, confirms `22:44:05`, and has Break main candle `22:44:00`. The existing remainder helper produces an eligible Mode-B First at index `18`, `22:44:00`, with BoxTop `4249.81` and BoxBottom `4244.635`. The next main candle `22:44:30`, index `19`, strictly confirms it without an intervening Reset. Canonical identity `(18,19)` is absent. The actual first divergence is therefore upstream Reaction identity, not public visibility.

Scope limit: this audit did not replace the missing Reaction and rerun the full S/E/Order/StopAll pipeline. Later market outputs can change through canonical membership, strike comparison, numbering and Order discovery; their exact extent is NOT RUN here.

## BL-01: Break-candle strike eligibility is not frozen at the first confirmation

Both active References Section 5.2, line 106, cap Break-candle intrabar strike confirmation through the strict Reaction-confirmation lower row, inclusive. The reconstruction matrix line 617 repeats that cap. The code has two bypasses:

1. `count_scale_strikes` updates pending from complete main OHLC, including the Break candle, then confirms immediately when that main candle has the confirming color (`162-188`). Only pending left after this loop reaches the lower-timeframe helper (`190-202`). An extreme attained after the first Reaction confirmation can therefore become a completed strike directly.
2. `_intrabar_pending_confirmation` stops at a strict Reaction break only when `eligible` is nonempty (`118`). If the first strict Reaction confirmation has no eligible strike, it continues into later lower rows. A later strike plus another price row beyond the same confirmation edge can then create a strike after the owning Reaction already confirmed.

The synthetic probes deliberately put every pre-confirmation Low above Fibonacci `8.764`, so the reference requires zero eligible Bullish strikes. Confirmation occurs at `2026-10-05 12:01:00`; Low `5` first occurs at `12:01:15`. A confirming-color GREEN Break returns a strike `5` through the first bypass. A RED Break with the same first-confirmation/later-extreme order returns the same strike through the intrabar bypass. Both exact directional mirrors return High `-5` instead of zero strikes. These inputs also correspond to healthy first confirmation followed by a later Reset; no malformed OHLC is required.

Five genuine RAW instances were found across the two complete 5-second files. All times below are full local Asia/Tehran candle datetimes:

| RAW start | Direction / Reaction number | Break main | First strict confirmation | Actual strike | Eligible Break extreme | First later attaining row |
|---|---|---|---|---:|---:|---|
| 2026-09-16 22:35:00 | Bullish 58 | 2026-09-17 05:30:30 | 2026-09-17 05:30:35 | 4298.815 | 4299.06 | 2026-09-17 05:30:45 |
| 2026-09-29 01:30:30 | Bullish 44 | 2026-09-29 05:07:30 | 2026-09-29 05:07:35 | 4126.985 | 4127.07 | 2026-09-29 05:07:50 |
| 2026-09-29 01:30:30 | Bullish 131 | 2026-09-29 13:02:00 | 2026-09-29 13:02:00 | 4139.78 | 4140.96 | 2026-09-29 13:02:15 |
| 2026-09-29 01:30:30 | Bearish 42 | 2026-09-29 07:00:00 | 2026-09-29 07:00:00 | 4140.305 | 4139.515 | 2026-09-29 07:00:20 |
| 2026-09-29 01:30:30 | Bearish 109 | 2026-09-29 13:00:30 | 2026-09-29 13:00:30 | 4141.495 | 4140.815 | 2026-09-29 13:00:40 |

The eligible Break extreme is not necessarily the whole Reaction's eligible strike extreme; earlier main candles remain eligible. `raw-evidence.json` preserves actual strikes and the separate result when only Break extremes are capped. Bullish 44 count changes `1 -> 0`, Bullish 131 `2 -> 1`, Bearish 109 `1 -> 0`. None of these five rows directly emits a Scale Blue because the surrounding strike-growth/spacing state suppresses that immediate emission. This is not evidence that the strike-state defect is harmless.

A separate oracle namespace executes unchanged `detect_blue_lines` sequencing with a local count wrapper that limits Break OHLC extremes to the first canonical confirmation. It does not modify the imported module, production files, canonical Reaction objects or RAW. It is a bounded diagnostic oracle, not a deployed correction or independent replacement algorithm.

The first Blue calculation-output difference on the `2026-09-29` file is Bearish ordinal `146`, Reaction `249`, confirmed `2026-09-30 03:23:05`:

| Field | Actual Source | Confirmation-capped oracle |
|---|---|---|
| source index/time | `2984`, `2026-09-30 03:23:00` | `2983`, `2026-09-30 03:22:30` |
| source extreme | `4184.335` | `4184.335` |
| line price | `4184.93` | `4184.305` |
| strike count | `1` | `1` |

A later full Break extreme replaces pending ownership and narrows the intrabar helper's start, losing an equally extreme earlier eligible main owner. The first changed A object is ordinal `50`: its Blue-2 source time changes from `03:23:00` to `03:22:30`. Its trigger, Reaction, A source `2026-09-30 03:26:30`, and price `4187.69` remain equal. Counts remain Blue `211`, A `72`, yet object provenance differs. This proves why equal stage counts are insufficient.

This Blue is marked `behavior_internal=True`, so it is suppressed from public Blue output. A consumes the calculation ledger and its provenance still differs. Final public A/S/E/StopAll consequences are NOT RUN. The bounded A output comparison proves the exact changed field and does not claim a changed order or trading signal.

## RX-02: sparse first main timestamps inflate every Reaction intrabar window

Bridge normalization at `trading_pipeline.py:164-177` emits only nonempty epoch-aligned requested timeframe buckets. `MarketChronology` receives the requested seconds explicitly (`1749-1750`). Reaction `DetectorBase` instead infers its timeframe from the first two emitted timestamps (`reaction_engine.py:121-124`). With a missing bucket, these are different contracts.

The synthetic 30-second main starts are `2026-10-05 12:00:00`, `12:01:00`, `12:01:30`, `12:02:00`; the empty `12:00:30` bucket is absent. Main/lower OHLC aggregates are consistent, timestamps ordered, and every occupied main candle has six 5-second rows. A Reaction confirms in main index `2` (`12:01:30`), then the first Reset occurs in main index `3` (`12:02:00`).

The detector infers `60` seconds, so `post_breakout_reset` scans the confirmation candle through `12:02:30`, captures a later row from index `3`, and appends Reset as index `2`, main time `12:01:30`, exact second `12:02:00`. Expected owner is index `3`, main time `12:02:00`. The first divergence is Reset ownership/time; both mirrors reproduce it. Active global chronology line 56 and Section 4.6 line 88 require the owning main candle and selected lower event order to remain consistent.

Natural trigger: any valid sparse supplied input whose first two occupied main buckets are farther apart than the requested timeframe, including a cold selected-range calculation near a market gap. Existing bridge normalization accepts this sparse structure. Root transport audit should independently verify route reachability. No such first-prefix gap was present in the two bounded RAW files tested here; genuine RAW reproduction for this prefix condition is NOT RUN.

## RX-H01: exact confirmation tie selection inside one main candle

`_earliest_confirmed_geometry` says the first strict confirmation wins (`1917-1924`). It collects every candidate confirmed in a main candle but returns `min(confirmed, key=first_idx)` (`1987-1988`), without comparing lower-event confirmation timestamps. Synthetic nested candidates with First indices `1` and `3` both confirm in main `4`: candidate `3` confirms at `12:02:00`, candidate `1` at `12:02:10`; the method returns candidate `1`. Both mirrors reproduce this method behavior.

This is a high-confidence mismatch with the helper's stated selection contract. Production Order_A acceptance separately requires canonical membership, and the later First can be absent from the canonical stream when the initial owner remains healthy. The accepted-Order consequence is therefore unproven. Do not report this as a confirmed physical Order selection bug until the full canonical-membership caller trace establishes it. Active Order_A Section 9.1 line 211 applies earliest canonical confirmation, then FirstIndex, then BreakIndex; geometry-only candidates cannot substitute for that registry.

## Rule-by-rule compliance in assigned scope

| Requirement | Reference lines (both prose files) | Enforcement reviewed | Verdict / evidence |
|---|---|---|---|
| Decimal input and exact identity | 53,57; 66; 592 | `core_utils.py:11-26`, `reaction_engine.py:29-89,807-809` | Implemented for normalized production Candle path; no authoritative binary-float price branch found |
| GREEN Doji in either market direction | 54; 72; 586 | `reaction_engine.py:94-96,563-580,649-706` | Implemented; role reflection is explicit internal machinery, not market color reclassification |
| Strict equality never crosses | 55,58; 577 | all policy branches; Reaction boundary/reset helpers; lower tree; A crossing helpers | Implemented; 2,000 differential checks include exact equal price levels and earliest equal extrema |
| First/context roles, confirmation edges | 70-72; 539-544 | initial reference machine, Bearish coordinate adapter, Unified direct construction | Implemented mechanically; 1,500 complete-history reflected candidate comparisons PASS |
| Frozen initial structural owner/invalidation priority | 76 | `214-268,285-560`, `2079-2117` | Implemented at reviewed branches; same lower-row invalidation wins by explicit order |
| Normal confirmation reuse | 80 | `1557-1640,2148-2195,2308-2310,2349-2351,2387-2389` | Partial / RX-01: absent on initial confirmation |
| Opposite Reaction edge frozen through confirmation | 84 | `_refine`, `_append_reaction`, `published_reaction_candidate` | Implemented at canonical/published ownership paths; fallback preserves geometry when lower proof unavailable |
| Reset first strict opposite-edge break | 88 | confirmed-reset ordering, post-reset helpers, Unified reset loop | Partial / RX-02: correct strict comparisons, incorrect owning main window after a sparse first gap |
| Post-Reset candidate completion selection | 92 | `1655-1691,1991-2117` | Implemented: First-ordered search, invalidation-blocked prefix, unfinished bounded candidate skipped; contradictory legacy method doc noted below |
| Geometry evidence cannot become canonical solely by helper result | 92; 209-211 | `_first_geometry_after_reset` and caller routing | Geometry stays separate here; complete accepted-Order membership adjudication delegated to Order audit |
| Internal ownership requires contained physical path | 96 | `1205-1313` | Implemented using exact lower min/max through confirmation, preserves canonical stream/number |
| Fibonacci reference and formulas | 102; 545 | `blue_line_detector.py:75-81,324-354` | Implemented; Mode A prefers anchor then leg boundary, Mode B uses previous opposite edge |
| Strike strict growth and exact Break cap | 106; 617 | `84-204` | Partial / BL-01; direct confirming-color and later intrabar paths both reproduced |
| Scale growth and healthy-Reaction spacing | 108 | `355-380` | Implemented as described; immediate leak rows may be suppressed while state/source still propagates |
| Reset Blue double-stop and evidence retention | 112 | `59-72,245-297,381-399` | Implemented main-index stop rule and validity flag; invalid calculation line retained for A special route |
| Blue public/internal predicate | 116 | `407-458` | Implemented public filter and exact source/line strict containment |
| Exact Blue formation and strict stop ledger | 122 | `a_zone_detector.py:201-257` | Implemented, scale at canonical confirmation; Reset uses first lower broken-level crossing; Reset source extreme owns complete Reset main candle |
| Adjacent valid Blue direct/inherited A route | 126 | `322-552,575-694` | Implemented directional mirrors; explicit complete boundary handling retained; 3,000 synthetic directional A runs completed |
| Double-stop special A ownership and no ordinary duplicate | 130 | `259-320,696-758` | Implemented route/duplicate filtering; lifecycle consequence of first-stop suppression not globally proved |
| A source frozen through exact Reaction confirmation | 134; 618 | `167-199,482-485,554-573` | Implemented lower-window cap with earliest strict-better source; A intentionally scans confirmation from Break open per shared chronology API |
| A first stop ownership and stale recross prohibition | 138 | `677-683,772-795`; S/lifecycle caller responsibilities | First-stop check implemented; full S handoff owned by separate audit |
| Full supplied calculation, presentation afterward | 47,60; 309 | bridge normalization and supplied full Reaction call; immutable chronology | Callers reviewed for context; root bridge/transport audit owns complete serialization proof |

## State, caches, mirror structure and non-findings

Run-scoped physical Order gate cache keys include direction, gate main index, bounded end and exact gate event; raw geometry is cloned on return and FIFO eviction at 32,768 entries does not decide trading state (`1768-1793`). Reaction break-index cache is length-keyed on append-only detector-owned streams (`1753-1766`). Confirmation cache keys include direction, First/Break, both edges and optional intrabar start (`1059-1071`). Reset cache keys include main/owner/time/broken level (`1047-1056`). No stale-cache trading defect was proven in this subsystem.

Process-global `_SEQUENCE_TIME_INDEXES`, `_REFLECTED_VIEWS`, and `_LOWER_TIMEFRAME_INDEXES` hold strong references and have no eviction. They are safe against Python id reuse because cached source identity is checked. They can retain every input in an embedded long-lived process; current CLI calculation processes exit after one request. Report as a conditional resource-retention risk for future module reuse, not a confirmed current trading bug. `_geometry_after_reset_cache` is checked but never populated by the current module; this is ineffective caching, not a semantic failure.

`mirror_candidate` transforms core box sources/values and anchor/leg boundaries with `copy_negate`, preserving context precision during reflection. Public behavior box metadata is not transformed by that helper. Current production calls mirror fresh geometric candidates before cross-direction public metadata is populated; no live consequence from that omission was found. Do not invent a runtime mirror bug from arbitrary direct helper calls.

The `_first_direct_same_direction_after_reset` docstring claims that an unfinished earliest owner blocks nested completion (`1658-1664`), while the current implementation explicitly skips unfinished bounded owners (`1687-1688`). Active Reference Section 4.7 line 92 accurately states the current bounded completion-selection behavior. This is stale local Source commentary, not a code/reference behavioral contradiction.

## Coverage and reproducibility

Assigned Source read in full: `reaction_engine.py` 1-2431, `blue_line_detector.py` 1-458, `a_zone_detector.py` 1-804, `direction_policy.py` 1-70, `core_utils.py` 1-26: **3,789 Source lines**, including every function/class/closure. `coverage.json` includes exact AST function/class bounds for these full reads. Relevant bridge normalization/loading/context and callback routes were read at 8-210, 1669-1782; caller routing searches are recorded. Unit regression reporter `test_hpzr2_regression.py` was fully read; relevant chronology fixture and equality contract `test_order_audit_lifecycle_contracts.py:1-108` reviewed. Current unit files do not directly invoke `count_scale_strikes`, `_candidate_from_confirmation_remainder`, or `_earliest_confirmed_geometry`; independent root unit-suite execution is separate.

Bullish reference prose 1-726 read fully. Bearish 1-190 read fully; every changed line in 191-726 read and every remaining line verified to have identical line content at the same line number as the already read Bullish text. This prose comparison does not claim byte equality of the embedded Source. Both semantic specifications, schemas, mirror/invariant matrices and historical verification claims are covered; the parent's final embedded Source byte/AST results are stated above. No historical PASS claim was substituted for a new execution.

| Command from repository root | Result | Scope |
|---|---|---|
| `python -B engineering/verification/forensic-audit-2026-10-05/reaction-audit/probes.py` | PASS execution; intended defects reproduced | Initial reuse, two Blue cap paths, sparse timeframe, same-main earliest geometry, 2,000 lower-index differential comparisons |
| `python -B engineering/verification/forensic-audit-2026-10-05/reaction-audit/raw_probes.py` | PASS execution; real discrepancies recorded | Two complete 5-second RAW inputs, both directions, 30 seconds; canonical Reaction/Reset/Blue/A only plus isolated eligibility oracle |
| `python -B engineering/verification/forensic-audit-2026-10-05/reaction-audit/fuzz.py` | PASS, seed `530105` | 1,500 valid synthetic histories, exact no-Doji price/role reflection candidate parity; 3,000 directional Reaction→Blue→A executions |

RAW `2026-09-16`: 14,140 rows, 2,360 main candles, SHA-256 `d33c7e2c46440f7a4495bac7d80b38101a635491f0f95b8ea353caa8fdb7d96d`. RAW `2026-09-29`: 25,606 rows, 4,278 main candles, SHA-256 `503445f74ff67e90d78e886f7e0cf478d4e8298ec6faf233747d66d7549a1ce2`. Bytes were read only. Runtime clocks are observational timings, not a benchmark.

Final integrity check `coverage.py`: PASS, all five assigned live Source hashes match the frozen extracted package; PASS, both audited RAW hashes match the bytes read before their probes. The root audit owns the broader repository-wide protected-state verification.

No claimed exhaustive market correctness, no deployment, no source patch, no RAW repair, no full-engine counterfactual run, and no final accepted Order/StopAll conclusion are included in this subsystem result.
