# Phase 07 — Lifecycle and StopAll direct context review, checkpoint 10

Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. **INCOMPLETE.** Continuation of [checkpoint 09](Semantic_Context_Review_09.md).

[Lifecycle direct context ledger](Semantic_Context_Lifecycle.json) partitions the pinned source and links original site IDs to semantic contexts, compared with [Lifecycle](../../Algorithms/V3/10_Lifecycle.md) and [StopAll](../../Algorithms/V3/11_StopAll.md).

## Important distinctions

- StopAll exact owner arms at count>=2. Source ordering E before S on exact source tie is distinct from decision-event ordering.
- A Red S after a confirmed armed Blue owner may promote immediately without a price stop or Mode B; the alternate completed-stop route requires Mode B. E donor exception permits same-main strict crossing or exact parent identity match, only no later than E decision.
- Active StopAll own stop at or before E decision qualifies; new number is highest stopped number+1, gate earliest stop. Promotion gate and donor's own subsequent stop are separate.
- For A invalidity, rank latest stop-owning main first, then module priority and number. S visibility after reset instead ranks exact stop first. A provenance boundary filter selects priority first; these three rankings are deliberately not merged.
- Prior A triggers strictly after an A owner's stop bypass that owner. Interior exception uses complete main extreme and an aligned confirmed Reaction strictly before new A source.
- Blocked Order First interval includes A source and excludes exact stop; E exception requires matching accepted exact stop and later confirmation, and never removes inherited veto globally.
- Consumed S evidence and restoration of historical A/S lineage do not grant new calculation ownership. Final E/StopAll collisions use source index, while StopAll S input compares exact physical index/time.
- Reconciliation publishes StopAll sequence resets once; it does not retroactively rebuild E. Internal-output helper currently copies lists without applying extra filtering.
- Live StopAll retains only unchanged prefix before dirty event and re-resolves unresolved or dirty stops; coverage is last lower event plus one microsecond.

| Metric | Newly reviewed | Cumulative | Pending |
|---|---:|---:|---:|
| Source files | 1 | 13 | 3 |
| Contexts | 70 | 443 | — |
| branches | 286 | 1475 | 1658 |
| comparisons | 194 | 1017 | 1160 |
| arithmetic | 104 | 510 | 564 |
| calls | 595 | 2457 | 2663 |

[Machine-readable cumulative progress](Semantic_Context_Progress_10.json).

Reaction, Order Audit and Trading Pipeline remain pending direct review. Shared semantic contexts are not independent nested-expression certification. Phase 08 blocked. No RAW reads, engine execution, benchmark or production edits.
