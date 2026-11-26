# Phase 07 — direct semantic context review, checkpoint 07

Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Status **INCOMPLETE**. Continuation of [checkpoint 06 review](Semantic_Context_Review.md). A and Primary were read from their exact pinned source blobs and compared with the existing full procedure contracts. Their semantic intervals partition all source lines; the crosswalk's native branch, comparison, arithmetic and call identities are retained and joined to context at each focus start.

- [A Zone context ledger](Semantic_Context_A.json)
- [Primary PH/PL, MBL, trend transition and native Order gate context ledger](Semantic_Context_Primary.json)
- [Cumulative progress](Semantic_Context_Progress_07.json)

## Direct findings

- A: lower crossing search is start-inclusive and end-exclusive, but its extreme query is end-inclusive. Empty lower fallback differs: crossing scans main opens at/after start; range extremes include containing mains. Recorded stop expiry permits equality, but ordinary crossing does not; the simultaneous-stop route can trigger exactly at expiry.
- A: Scale formation uses exact confirmation with intrabar start disabled, Reset stop scan starts at source main end; invalid Blues count toward ordinals and can supply the special double-stop route. Exact and effective main stop provenance are distinct. Reuse uses owner-specific strict settled gates, including original query key and lower-evidence presence.
- Primary: PH accepts same-event confirmation while PL requires a strictly later confirmation and a First index at or beyond gate. Reversal wins equal-time activation and decision; activation wins equal-time decision; decisions tie by cycle index. A same-row opposing strict crossing does not establish a price path: it yields ambiguity where the actual source checks it.
- Primary: physical reconciliation filters decisions by inclusive horizon before choosing role winner and independent earliest identity. Source extreme deliberately includes entire main trigger/decision candles. Live dirty event therefore rewinds to containing main open; schedule changes may rewind further.
- Primary bullish mirror negates prices by Decimal copy_negate, swaps High/Low and PH/PL, not time or physical identity. Native callbacks see projected points.
- Source-range corrections preserve previous evidence: CH86 source freeze includes executable lines 606–611; CH87 ordinary lifecycle includes both advancement branches through 732; CH88 filter is 734–797; CH114 seed yield is 284; CH115 global scheduler includes PH promotion/callback/pending invalidation/reversal recomputation through 418.

| Module | Contexts | Branch sites | Comparisons | Arithmetic | Calls |
|---|---:|---:|---:|---:|---:|
| A Zone | 56 | 180 | 135 | 69 | 324 |
| Primary | 49 | 214 | 141 | 48 | 267 |
| Cumulative (10/16 files) | 233 | 617 | 434 | 202 | 956 |

## Remaining modules

| Module | Branch sites | Comparisons | Arithmetic | Calls |
|---|---:|---:|---:|---:|
| trading_pipeline.py | 552 | 333 | 162 | 1229 |
| e_zone_detector.py | 334 | 218 | 104 | 453 |
| lifecycle_engine.py | 286 | 194 | 104 | 595 |
| order_audit_engine.py | 551 | 374 | 123 | 844 |
| reaction_engine.py | 555 | 453 | 279 | 590 |
| s_zone_detector.py | 238 | 171 | 100 | 453 |
| Total | 2516 | 1743 | 872 | 4164 |

All previous structural evidence remains immutable. Phase 07 is not complete and Phase 08 remains blocked. No RAW access, execution or benchmark. No change to production source.
