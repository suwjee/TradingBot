# Phase 07 — Checkpoint 76 / W1 B06-04

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `b0739ea55223699dbc6f8213f908206cfd17ff08`. **Local review PASS; Phase 07 INCOMPLETE; Phase 08 BLOCKED.** E07, lines 220–311; 102 original rows, 4 supplemental items, 2 local clarifications. E cumulative 198/1109.

[Individual evidence](Semantic_Closure_B06_04.json), [immutable crosswalk](Decision_Site_Crosswalk_03.json), [context ledger](Semantic_Context_E.json), [active E contract](../../Algorithms/V3/09_E_Zone.md). Exact pinned blob `240369edf3352006082efe094eb68ac027d6689f`; original IDs, spans and procedures matched. No full Phase 02 inventory reread claimed.

## Live reconciliation dependency signature, rewind and restart

- B06-04-S1: Presence versus truthiness; red before blue priority; original candidate order. ([source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L225-L242)).
- B06-04-S2: Key retains group insertion order and object IDs; accepted set replaced, lifecycle set unioned. ([source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L248-L265)).
- B06-04-S3: Previous passed even on validity mismatch; terminal fallback assumes nonempty ordered steps. ([source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L271-L291)).
- B06-04-S4: Only first compute is caught for reopen; cache only unreopened; evidence contains mutable dicts. ([source](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L292-L309)).

- B06-04-F1: Clarify empty mapping and dependency evaluation order. Active contract line 59 amended.
- B06-04-F2: Specify terminal step assumption, prior argument and retry exception scope. Active contract line 60 amended.

W2/W3/W4 open. No RAW read, Engine execution, benchmark, or production change.
