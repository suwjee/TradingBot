# Phase 07 — Checkpoint 92 / W1 B06-20

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `a4e4555e9fe0a0953041c036d354148c527d5ee3`. **Local partition PASS; E44 outer procedure INCOMPLETE; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E49–E50 (nested in E44), lines 1229–1293; 66 original rows, 4 supplemental items, 3 resolved local clarifications. E cumulative 911/1109.

[Individual evidence](Semantic_Closure_B06_20.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md), [state model](../../Algorithms/V3/State_Machines/05_E_Lifecycle_StopAll.md). Pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original category IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Parent eligibility, sequence reset, ancestry and strict stop relation

- B06-20-S01: S lookup by raw parent pair against normalized S map. Missing/accepted parent rejects; S time<=sequence_start or A time<sequence_start rejects. bisect_left means prior numbered time strictly earlier; equal zone source time excluded. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1230-L1247).
- B06-20-S02: Both rebuilt_after_e and dominant_s variables evaluated separately before final OR; each internal AND short-circuits. Red S dominance requires earlier S, blue prior and unused parent time, not unused physical identity. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1248-L1262).
- B06-20-S03: Non-S branch first compares parent time to sequence_start without null guard, then exact active pair. Reuse supplied seen even empty; mutate before lookup. Only invalid Order but not invalid-S-without-cause permits recursive skipped-parent path; E41 may be evaluated again. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1263-L1285).
- B06-20-S04: Stop relation first rejects decision <= prior (including equal), then strict directional price, with no new market scan or price conversion. [Source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1287-L1292).

## Findings

- B06-20-F01: Clarify lower-bound prior lookup, both boolean variables evaluated and distinct equality rules. Active E contract line 197 amended; rechecked pinned source.
- B06-20-F02: Clarify all non-S dispatch, exact boundary comparison, shared seen mutation and repeated E41 check. Active E contract line 197 amended; rechecked pinned source.
- B06-20-F03: Clarify decision guard before direction/price and raw prices. Active E contract line 200 amended; rechecked pinned source.

Remaining E44 body, W2/W3/W4 open. No RAW payload read, Engine execution, benchmark or production change. Permanent RAW protocol remains unchanged.
