# CP335 — W2 Reaction queue reconciliation

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`. Re-review of 24 existing transition IDs; no duplicate transitions. W2 remains open.

## CP323-S01 — RE01–RE04

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L35-L174) · [Owner specification](../01_Reaction_Engine.md)

Records separate index, native display time and exact datetime; Candle frozen, Candidate mutable, Reset/analysis/result frozen but nested lists not. Native doji GREEN via Open<=Close. Base retains sequence references and shared indexes; actual first two main times or 1 second duration, rejects nonpositive. Time index body at 175–182 is outside row, linked separately.

Handoff: Bridge native candle color and configured chronology duration must not be conflated with inferred detector duration.

## CP323-S02 — RE05–RE09

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L184-L244) · [Owner specification](../01_Reaction_Engine.md)

Lower windows half-open, owner mapping upper bound minus one within selected position range and timestamp before next actual open/last+TF. Main extrema inclusive, switch indexed at difference>=16, reflected sequence queries original opposite extreme and exact copy_negate; strict improvements preserve first tie. Preceding GREEN run requires immediate previous GREEN, bounded by detector start.

Handoff: Shared index earliest tie and main_source_for_time selected-owner predicate are distinct from MarketChronology.main_index clamp.

## CP323-S03 — RE10–RE13

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L246-L341) · [Owner specification](../01_Reaction_Engine.md)

Breakout start truthy intrabar_start else top source+1 when earlier than First, else top source; end Break+TF exclusive. Strict first crossing and min prefix through crossing inclusive; missing source owner/null crossing null. Mode A boundary anchor if nonnull else leg floor. Main equality preserves; both main predicates use lower position with invalidation <= breakout; neither evidence invalidates. Confirmed Reset race analogous but different initial guards. Post-confirmation begins event+1us, no substitute main crossing.

Handoff: Blue uses default confirmation accessor, not this analysis result; reset record may have exact or absent second time.

## CP323-S04 — RE15

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L346-L503) · [Owner specification](../01_Reaction_Engine.md)

Standalone scan restores initial cursor subset only, copies candidate. Strict confirmed Reset checked before candidate, clears state and records owner First; invalidation clears candidate without Reset. Opposite edge strictly updated then Break. first_only returns immediately after append before remainder Reset. Otherwise post-reset records exact lower display, resets leg state; RED Break seeds B from full main values without requiring exact analysis.

Handoff: Standalone helper first_only and Unified normal successor differ; don't import standalone remainder policy into Unified.

## CP323-S05 — RE15

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L504-L639) · [Owner specification](../01_Reaction_Engine.md)

New leg freezes Low; RED after GREEN reset and Low>=reset Low opens A, preceding GREEN peak wins equality. Subsequent GREEN→RED gate clears invalidation anchor only when previous and current lows both strictly below it; candidate checks anchor floor else prior/leg floor. Failed RED replaces anchor, DOJI/NEUTRAL tag clears (native doji GREEN). Mode B running peak wins equal; update strictly. Retain initial cursor only when requested on exhaustion.

Handoff: First-color and reset context semantics precede published geometry; no market doji reclassification.

## CP323-S06 — RE16–RE29

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L642-L785) · [Owner specification](../01_Reaction_Engine.md)

Reflect price via copy_negate and exchange high/low and role tags; preserve time/index/display and non-GREEN/RED tags. Candidate replacement swaps box source and prices, optional anchor/leg prices; other fields including metadata retained. Sequence cache exact identity, per-position cached reflected rows, no refresh in view itself. Bearish reference shares original times and reflected index, returned Reset level negated.

Handoff: Role reflection not public candle color; cache correctness conditional on sequence lifetime/immutability.

## CP323-S07 — RE30

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L788-L883) · [Owner specification](../01_Reaction_Engine.md)

Presentation clone, missing Break or invalid bounds returns unchanged before direction validation. Clip only if opposite source==Break, seed First main then strict pre-Break extrema, scan lower Break open to end and update opposite before same-row confirmation; absent strict hit returns clone. First==Break seeds full main extreme, so clipping is not universal.

Handoff: Public clone and native canonical append are separate; behavior containment uses published box, not rewritten native geometry.

## CP324-S29 — RE62 canonical_order_stop

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L1305-L1367) · [Owner specification](../20_Indexes_And_Caching.md)

Mode A scan from anchor else First-1 clamped stage start; extend backward through correct context tag, strict main outer extrema through Break inclusive. Mode non-A requires reaction_number>1, previous ordinal−2 semantic outer edge and stored source, no re-extremization or internal/healthy flag check here. Source time main timestamp.

Handoff: S/E common stop provider; independent number zero can enter Mode A but non-A zero raises. Stop level/source are not confirmation or strict crossing.

## CP323-S10 — RE69–RE70

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L1481-L1551) · [Owner specification](../01_Reaction_Engine.md)

LiveBehavior validates dirty range. Reuse entry only same ordinal geometry tuple incl string prices and Break<dirty; recompute otherwise. Changed positions by full entry inequality; retain surviving unchanged pairs, recompute changed inner vs all outer or unchanged inner vs changed outer, supports multiple owners. Reapply mutable metadata, commit cache after successful application, no rollback of mutations.

Handoff: Optional behavior service, not active public live worker by mere existence; Blue internal flag is monotone on retained object.

## CP323-S11 — RE71–RE75

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L1554-L1680) · [Owner specification](../01_Reaction_Engine.md)

Bounded fallback A-stop closure validates exact direction and uses key (gate_index,end_index) ignoring gate_event; first adjacent role transition from max(1,gate), context expands backward to 0; cache candidate tuple from Unified detection with First threshold, returns cached object reference, not clone. Unified stores output direction without local validation, lazy direction helpers, per-direction ledgers and distinct caches.

Handoff: A-stop consumer applies exact initial confirmation threshold later; fallback closure ignores exact event by design, not universal direct geometry service.

## CP323-P01 — RE76

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L1681-L1721) · [Owner specification](../01_Reaction_Engine.md)

Conditional opposite reference recomputation from last Reset to candidate First when Break exists and adjacent anchor. Exact opposite Break==anchor match; bullish anchor low>=First low replaces top, bearish anchor high<=First high replaces bottom. No explicit check replacement extends prior candidate edge, so comment about never shrinking is not a predicate.

Handoff: Actual boundary assignment, not guarantee of monotonic box extension; canonical confirmation edge separate from opposite recomputation.

## CP323-P02 — RE76

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L1723-L1761) · [Owner specification](../01_Reaction_Engine.md)

If Break nonnull recalc opposite main extrema First..Break inclusive; if Break owns extreme and analysis available replace with exact analysis extreme/source, otherwise preserve full-main result. Mutates supplied candidate before shallow replacement append; null Break still appended. Always returns true in shown implementation.

Handoff: Ledger snapshot and caller object geometry may differ from earlier local analysis; downstream stop uses canonical source, not a pure public clone.

## CP323-P03 — RE77

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L1763-L1778) · [Owner specification](../01_Reaction_Engine.md)

Append main index/display, nullable second display, supplied broken level and originating First; no recovery, normalization or dedup in helper.

Handoff: Blue/Order_B/S use separate downstream exact event resolution; ordinary dedup is caller-side.

## CP323-S12 — RE78–RE79

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L1781-L1851) · [Owner specification](../01_Reaction_Engine.md)

Refine only opposite edge whose source is current candle and analysis nonnull; returns analysis even if no refinement. Unified same-Break successor requires correct main tag and exact analysis; strict post-confirmation breach rejects. Then uses entire Break lower rows; High max key uses negative timestamp.timestamp() epoch FLOAT, Low min uses datetime, first full-key tie. Return B with both main sources and intrabar_start main open; confirmed argument unused.

Handoff: Separate geometry ownership phases; don't claim exact datetime tie for high when epoch float collapses distinct instants.

## CP323-S13 — RE80–RE82

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L1853-L1944) · [Owner specification](../01_Reaction_Engine.md)

Retained route asserts expected cursor type and uses reflected reference for ordinary bearish, mirrors result once. Trend isolated bootstrap first boundary candle can be First; before First strict fixed confirmation-side improvement; no prior boundary invalidation. Continue after creation, cannot confirm same First. Opposite edge strict update before Break; refine; exhaustion saves trend cursor if requested; empty window returns before save.

Handoff: Reversal independent segment flags select initial bootstrap; loop position vs Candle.index may differ for noncoherent custom inputs.

## CP323-S14 — RE83–RE86

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L1947-L2051) · [Owner specification](../01_Reaction_Engine.md)

Normal post-Reset First search strictly after Reset and beyond blocked_through; proper colors and builder. Confirmed result returns in First traversal order, earlier unresolved candidate sets pending and allows later candidates; invalidation blocks through its main, exhaustion returns null,true. Geometry-only scan ignores invalidation; cache lookup with copy on hit, no write in method; first complete in First traversal order.

Handoff: Do not conflate ordinary search, permissive geometry, or concurrent Order geometry; raw completed geometry not accepted physical Order.

## CP323-S15 — RE87–RE90

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L2053-L2215) · [Owner specification](../01_Reaction_Engine.md)

Break list cache by direction and ledger length; no sort or duplicate check. Gate valid start<=gate<limit; key direction/gate/limit/exact event, FIFO bounded copy cache. Bisect_left selects prior owner or first equal Break if local confirmation<=gate; local intrabar start un-clamped, fallback main open. No owner sets no-history; otherwise outer extent First..max(First,gate−1), gate opposite edge. Lower search half-open; outward wins equal position; restart owning main+1, continue gate+1. Reconstruct missing anchor index OR value from max prior Reset strictly before new First, assigns all three fields.

Handoff: Caller order/unique Break invariants are not enforced; E/Order consumer canonical identity and decision gates separate.

## CP323-S16 — RE91–RE94

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L2217-L2417) · [Owner specification](../01_Reaction_Engine.md)

Concurrent candidates start from first allowed color transition after reset bound. Reject invalidation before mutation; earliest confirming MAIN wins, smallest First within same main, not sort by exact lower times. Builder context and prior First-color runs bounded by reset; local strict First floor/ceiling, frozen outer anchor Reset..First−1. Outer invalidation race checks lower outward first, no evidence defaults invalidation. Geometry scan returns candidate, no append.

Handoff: Order_A/E need their own canonical identity and owner-stop gate; strict invalidation and geometry-only relaxation distinct.

## CP323-P04 — RE95–RE97

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L2420-L2456) · [Owner specification](../01_Reaction_Engine.md)

Result aliases actual direction ledger lists, no initial => fresh empty lists. detect invokes retain_cursor false; initial append before threshold early return; no post-confirmation Reset processing if early return.

Handoff: Threshold is First index gate, not confirmation horizon, and not a complete lifecycle run.

## CP323-P05 — RE97

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L2457-L2515) · [Owner specification](../01_Reaction_Engine.md)

After initial append, set next Break+1, running directional edge/source at Break. Re-analyze mutated initial candidate; reset level exact analysis extreme else opposite edge. Post-confirmation Reset appends exact display and pending index; else shared remainder seed. Return scan cursor.

Handoff: Order callbacks using early threshold do not necessarily observe same-Break Reset; distinguish local previous candidate from public clone.

## CP323-P06 — RE98

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L2517-L2573) · [Owner specification](../01_Reaction_Engine.md)

Pending Reset or previous strict opposite-edge breach; if competing candidate strict Break run direction-specific reset race. Select pending or current main; snapshot prior cursor/counts only retain_cursor and no earliest_open, before recording. Clear pending and derive reset level from previous box. Duplicate suppressed only by last Reset owner First equality.

Handoff: Exact previous pending event may already be recorded; main reset path does not invent exact lower time.

## CP323-P07 — RE98

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L2574-L2650) · [Owner specification](../01_Reaction_Engine.md)

Append Reset unless already recorded; retained direct search sets earliest_open when unresolved earlier First; nonretained uses first direct same-direction. Missing structural/Break breaks. Mode A clear both cross-direction flags; source includes false-append path though helper always true. Early First threshold after append; re-analyze Break, exact level else box; post-reset append exact display. Actual next pending/reset and remainder assignments 2651–2658 in next historical span.

Handoff: No opposite-direction unlocking rule; prior span ends mid explanatory comment, linked adjacent actual assignments.

## CP323-P08 — RE98

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L2651-L2761) · [Owner specification](../01_Reaction_Engine.md)

Post-reset clears candidate and sets pending Break else remainder; continue structural route. Normal candidate updates opposite edge strictly before strict Break, refine then compute exact post-reset before canonical append; early threshold checked after append. Copy previous, update running edge; exact Reset or remainder. Fresh B uses running edge on equality and opposite extrema start after earlier winning source. Bearish candidate constructor crosses boundary into P09.

Handoff: Preserve exact event/source versus main cursor; no inferred complete bearish constructor within this span.

## CP323-P09 — RE98

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/reaction_engine.py#L2762-L2783) · [Owner specification](../01_Reaction_Engine.md)

Finish bearish candidate fields at 2762–2769, then separate exact bullish/bearish running-extreme strict improvements and index increment. Retained checkpoint earliest_open or final cursor/counts, return direction result. Prior P08/P09 together cover complete source; no new record needed.

Handoff: Continuation may rewind earliest unresolved Reset; early threshold returns before final cursor assignment.

## Findings and closure boundary

- CP335-F01: Commentary in RE76 about never shrinking is not enforced by an explicit monotonic comparison; actual adjacent-anchor assignment and canonical recomputation documented. No production defect asserted.
- CP335-F02: High tie uses native epoch float in same-Break successor; original CP323-S12 wording about earliest timestamp must be qualified by float key. Detailed RE79 already records this.
- CP335-F03: CP323-S01 stops at shared time-index declaration; add body link. P07/P08 and P08/P09 split at state/constructor boundaries; preserve original IDs and link adjacent rows.
- CP335-F04: Order gate main-break list cache assumes caller order/length; no universal guarantee of unique exact confirmations. Direct normal, permissive geometry and concurrent Order search have different ordering and invalidation. Existing RE84–RE94 precise.

Cumulative queue review: 36/185. Seven remaining accessor sites; no overall W2 acceptance. Original historical records retained; no runtime, RAW payload or production change.

[Evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP335_W2_Reaction_Queue_Reconciliation.json).
