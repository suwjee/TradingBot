# CP378 — S A ownership eligibility

Pinned source: `53460e68538ac790ab969084c1c7101e5ca833d7`; B04-04 587–695. 312 category rows, 96 W1, 216 additional, 7 supplements; 1720 prior rows revalidated without overlap.

### W3 CP378 — post-Order candidate and A ownership eligibility (S24–S28)

- **S24 (587–598)**: Signature/docstring describes post-Order candidate, but native gates below control; no standalone exact chronology proof.
- **S24 (599–603)**: Read integer First, bisect main opens at confirmation, clamp downward to First then upward to selected start. Read anchor index and value before anchor guard.
- **S24 (604–610)**: Anchor nonnull and int(anchor)>=start selects it; repeated native int conversion, positional candle lookup then Decimal anchor value. No explicit upper/First bound or exact anchor event check; native failures propagate.
- **S24 (611–619)**: Otherwise call S13 earliest-equal inclusive main candidate first; map confirmation containing main position. If containing<start, scan lower remainder [confirmation,containing open+timeframe), not preconfirmation extreme.
- **S24 (620–627)**: Replace candidate on strict directional improvement OR equality, using containing positional index and main timestamp rather than lower row timestamp or native Candle.index. Return selected tuple; no new stop proof.
- **S25 (628–636)**: Read A source and normalized price; search full source main lower half-open window; return first equal trend extreme timestamp, else source-open fallback. No A-stop lower gate or observed-event guarantee.
- **S26 (637–642)**: Resolve source event once; iterate ownership windows in insertion order, matching inclusive start and open/exclusive end. Skip nonmatches.
- **S26 (643–651)**: First matching window: nonnull trigger strictly after start returns False immediately, before Blue reads; equality does not preempt. No later window reconciliation.
- **S26 (652–661)**: Read five optional Blue/source fields even with open end, after trigger exception. Comment describes decided-S Reset-pair preemption, operative ordered predicate follows.
- **S26 (662–673)**: Require closed end, all five values present, start<Blue1 source, Blue1 stop<Blue2 source, source_time==Blue2 stop, then S27. No independent Blue2 source>start or validation of pair chronology beyond predicates.
- **S26 (674–677)**: Qualifying Reset-pair returns False; otherwise first matching window returns True. No matching window returns False. This is S eligibility, not global accepted lifecycle.
- **S27 (678–685)**: Convert both Blue ordinals (default 0, subtract 1) before first bounds guard; invalid position returns False, native conversion failures propagate. Original trend Blue list, not filtered public list.
- **S27 (686–690)**: Exact string kind reset for first then second, short circuit; no calculation_valid/internal gate or physical pair identity test.
- **S28 (691–695)**: Property constructs fresh list of original sorted A records not owned by S; no ownership mutation or final lifecycle acceptance.

The local predicates, not their comments, define the scoped source contract. Provider geometry and cross-owner accepted-ledger proof remain independent.
