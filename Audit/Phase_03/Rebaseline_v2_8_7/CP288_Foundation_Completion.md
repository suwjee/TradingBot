# CP288 / RB03 — Foundational contract rebaseline acceptance

Baseline: c99b4c957e932d9ee70c492ca03ce80711447fc1. Status: PASS (foundational delta and declared-interface scope only). CP287 publication exception remains separately WAIVED_NON_BLOCKING.

## Evidence and acceptance

- 16 source paths reconciled against pinned main; 14 unchanged source blobs reuse the previously accepted foundational evidence. Changed Bridge and True/False declaration blocks and changed function scope deltas reviewed against the current source.
- Declared schema: 87 classes, 46 records, 441 fields, 360 required, 81 defaulted, 117 nullable, 18 factories, 14 keyword-only defaults. All 441 catalog rows match name, order, type and default metadata. New fields: PipelineState.full_stopalls_by_direction, FullDirectionState.stopalls, BasicRepeat.base_count. New non-record classes: LiveClosedRegimes and MarketIndexWindow.
- N07: internal T/F Decimal comparison coordinate and strict reference rule, native repair conversion and parent-stop conversion.
- C04/T05/I06/K08a: local coordinates, conditional zero-origin record reuse, indexed windows, transactional closed-prefix reuse.
- P04a/P06a: accepted E donor source ownership, per-pass StopAll reconciliation, stored direction results, visibility and primary handoff, separate repeat counters.
- B05: new bounds, empty/missing distinctions, conditional assertion, transaction and reference equality rules.
- Architecture delta: current feedback stage distinguished from historical synchronized prose. The 14 unchanged modules retain their own local primitive definitions; consumers' context and dependence on accepted E/StopAll, order audit, indexed chronology and T/F ownership must be re-reviewed at RB04/RB07–RB11.

## Current source anchors for changed foundational paths

| Rule | Current source anchor |
|---|---|
| N07/P06a | true_false.py:18–29, 34–38, 47–128, 162–188 |
| C04/T05/I06/K08a | trading_pipeline.py:336–364, 1756–1857, 3531–3630, 3737–3767 |
| P04a | trading_pipeline.py:2569–2645, 2674–2684, 2732–2758, 2791–2802, 2939–3035, 3405–3500 |
| Horizon and final annotation | trading_pipeline.py:3633–3710 |
| Record declarations | CP288_Declared_Schema_Evidence.json (module-specific source locations) |

Old Phase 03 anchors remain historical, not repointed by line number. Current changed-source anchors above supplement them. No claim of full function semantics, exact dynamic dispatch, runtime behavior, or RAW equivalence. Continue RB04 to re-extract changed functions and reconcile transitive context. No engine execution or RAW access.
