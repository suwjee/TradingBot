# Phase 07 — Checkpoint 16 / W1 B02-02

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `b43341609ab43fe604f48c288d1ee73b5af416eb`.

**Local source review PASS for RE13–RE18 (lines 328–689).** 179 original category rows, 15 supplemental review items, one local documentation omission resolved. B02 cumulative 350/1877; 1527 original rows remain. Phase 07 INCOMPLETE; Phase 08 BLOCKED.

[Individual site evidence](Semantic_Closure_B02_02.json) records each original ID, coordinate, meaning, relevance and contract link. Direct pinned source read preceded comparison with [Reaction procedures](../../Algorithms/V3/01_Reaction_Engine.md) and [state model](../../Algorithms/V3/State_Machines/01_Reaction_Reset.md).

## Verified local behavior

- RE13: null analysis returns null. Search strict Low below confirmed bottom from exact event plus one microsecond to Break main end exclusive; all equal event timestamps excluded. Return original lower candle or null. Do not infer a finer intra-row event order.
- RE14/15: fresh scan starts mode A, empty confirmed lists and null owner/peak/context; optional initial cursor restores only listed fields and copies pending candidate. Main loop inclusive. Detected previous-owner Reset races before candidate changes; main Reset emits null second_time even when race consulted lower evidence. A invalidation consumes main without Reset emission. Strict bottom improvement precedes strict high confirmation; set Break before analysis; current-owner refinement does not retest strict improvement. Append confirmed copy before first_only early return, which bypasses post-break Reset and cursor retention.
- Post-break Reset uses new confirmed bottom and exact lower hit display; clears owner/peak and returns to fresh A. Otherwise RED Break seeds B from full main geometry even without exact analysis. This is not Unified's same-Break seed contract.
- A initial leg freezes floor and consumes reset context; eligible RED after GREEN reset with inclusive Low comparison seeds A. Other RED creates leg_open anchor; non-RED leaves existing anchor. Later A requires GREEN to RED, removes invalidation-origin anchor only with both strict lower Lows, and does not fall back to previous/floor if remaining anchor fails. Absent anchor tests previous then floor inclusively. GREEN run wins top equality. Failed RED updates anchor; DOJI/NEUTRAL explicitly clears; native equal Open/Close still GREEN.
- B chooses prior running peak/source on equality, starts bottom range after earlier top source, and updates running peak after candidate creation; null initializes, strict higher replaces. WAITING never reaches B scan peak update. Normal exhaustion optionally retains pending cursor reference, not confirmed history; restoration copies it.
- RE16–18 reflect roles, prices and source fields without changing market timestamps or indices; sign-copy Decimal prices. RE17 retains all unlisted fields including behavior_public_* metadata; do not invent an extra reflection for those fields. Nulls preserved. Native assertions are conditional on execution configuration.

## Correction

B02-02-F01: active RE15 and RXI14 omitted the explicit null-running-peak initialization at lines 624–626. Both active documents corrected in place without changing their line counts, stable procedure/transition IDs or production source. Prior blob identities preserved in the finding record; historical reports and original crosswalk remain unchanged. Recheck during W3.

## Handoff

Next B02-03 begins line 690 (reflected sequence and Bearish adapters). No runtime, RAW, benchmarks or source modifications. Cross-owner and separate forensic passes remain open.
