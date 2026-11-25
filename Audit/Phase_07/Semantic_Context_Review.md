# Phase 07 — direct semantic context review, checkpoint 06

Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Status **INCOMPLETE**. This checkpoint changes the review method: every source interval in a completed batch is read and assigned a language-neutral context, checked against existing procedure contracts, then each original branch/comparison/arithmetic/call ID is joined to that context. This is materially stronger than lexical tags or mere rule overlap. A shared context can cover nested operands and does not certify downstream dynamic dispatch.

- [Batch 01 — shared utilities, T/F, Live Transport and package surfaces](Semantic_Context_Batch_01.json).
- [Batch 02 — Blue Line](Semantic_Context_Blue.json).
- [Machine-readable coverage and pending modules](Semantic_Context_Progress.json).

| Module | Reviewed contexts | Branch sites | Comparisons | Arithmetic | Calls |
|---|---:|---:|---:|---:|---:|
| __init__.py | 1 | 0 | 0 | 0 | 0 |
| __init__.py | 1 | 0 | 0 | 0 | 0 |
| __init__.py | 4 | 1 | 1 | 0 | 4 |
| core_utils.py | 8 | 13 | 5 | 3 | 21 |
| direction_policy.py | 8 | 7 | 13 | 0 | 6 |
| true_false.py | 23 | 46 | 30 | 10 | 41 |
| live_pipeline.py | 41 | 50 | 32 | 14 | 97 |
| blue_line_detector.py | 42 | 106 | 77 | 58 | 196 |
| Total | 128 | 223 | 158 | 85 | 365 |

## Clarifications

- Live worker transport lineage requires strictly increasing new RAW times, whereas the bucket append wrapper accepts equal times and rejects only decreases. Native dynamic callbacks, conversion exceptions and rollback ownership remain explicit.
- T/F retains first valid behavior at each source time; primary events flush only the StopAll buffer, not the basic S/E buffer. Repair horizon is inclusive, while price crossing is strict.
- Blue's exact confirmation cutoff is inclusive. Missing lower prefix skips the Break row entirely. Same lower row penetration precedes the Break predicate in evaluation, without asserting intrarow price motion. Invalid Reset Blue remains available to A.
- **CH83 range correction:** the full Blue continuation update is lines 487–514. The prior cited 469–495 interval did not include its entire rewind/commit path. New context records include it; prior evidence is preserved rather than silently replaced.

## Pending direct reviews

| Module | Branch sites | Comparisons |
|---|---:|---:|
| trading_pipeline.py | 552 | 333 |
| PL_PH_detector.py | 214 | 141 |
| a_zone_detector.py | 180 | 135 |
| e_zone_detector.py | 334 | 218 |
| lifecycle_engine.py | 286 | 194 |
| order_audit_engine.py | 551 | 374 |
| reaction_engine.py | 555 | 453 |
| s_zone_detector.py | 238 | 171 |

Remaining 2910 branch/control sites, 2019 comparisons, 989 arithmetic rows, and 4755 calls do not yet have direct context review in this new ledger. Earlier CH01–CH123 remains applicable, but does not close these gaps. Phase 08 remains blocked. No RAW reads, execution, benchmarks or main changes.
