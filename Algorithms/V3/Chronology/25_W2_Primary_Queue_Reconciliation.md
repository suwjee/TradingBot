# CP340 — W2 Primary Queue Semantic Reconciliation

**Status:** PASS_SCOPED after publication; W2 NOT_ACCEPTED.

Pinned source: `c99b4c957e932d9ee70c492ca03ce80711447fc1`, `33ecb3671c7808c7f92b494d39ac5b156a8cd67e`. Entry `c7f5b4d1d7b852a485c4b7afb2f307e26bef6613`.

## CP328-S13 — P18–19

Source: `engine/pipeline/PL_PH_detector.py:457–487`.

Replay retains prior steps in order strictly before frontier=min(dirty, first old/new differing activation after equal prefix). No prior returns current list alias. Strict cross key event,string level,above; current hit includes null; prior non-null hit strictly before dirty reused, else prior membership rewinds left to max(original upper bound,dirty lower bound); absent prior key scans entire strict-after-event window.

**Handoff:** Dirty evidence caller-owned; string Decimal representation intentionally preserved; no numerical-key normalization or independent runtime equivalence.

B08 overlapping link occurrences: 34.

## CP328-S14 — P20–21

Source: `engine/pipeline/PL_PH_detector.py:490–515`.

Refresh MBL own stop by supplied strict later crossing from original trigger/floor; falsy hit maps null pair, unchanged pair returns original checkpoint; otherwise shallow replacement only of stop fields and nested result. Activation cycle id uses donor raw formatting; reference main High, min Low second index through gate inclusive earliest tie, own stop after activation, phase PH.

**Handoff:** Frozen source and activation event not rewritten by stop refresh; bullish reflection swaps price geometry but not chronology or donor identity.

B08 overlapping link occurrences: 19.

## CP328-S15 — P22 steps 1–3

Source: `engine/pipeline/PL_PH_detector.py:518–553`.

Prospect replaces result with fresh highs/lows/post-PL3 lists only, other references retained; phase/number registers local. Seek strict above/below after cursor; both absent wait, equal exact events ambiguous, earliest picks phase and gate. before_event gate rejects cursor>=boundary. PH resets to1 on reset/no highs; PL increments.

**Handoff:** No commit on null proposal; native scheduler separately arbitrates decision vs reversal; no inferred intrarow order.

B08 overlapping link occurrences: 40.

## CP328-S16 — P22 steps 4–5

Source: `engine/pipeline/PL_PH_detector.py:554–574`.

Invoke Orders callback with role/number/gate/cursor; P11 PH confirmation>=gate, PL First>=gate main and confirmation>gate. Continuing PH requires parent-stop OR reset-leg with non-null boxTop strictly > high level; all stop>confirmation. Min exact stop,-First,Break. Cancellation PH floor below, PL high-level above; cancel_is_next if PL>3 or absent winner or earlier cancellation. Callback result not independently checked stop>gate here; P25 native service does.

**Handoff:** Candidate creation causes differ from use route and Reaction mode; speculative Order race not ledger commit. Same event ambiguity handled in following P22 branches.

B08 overlapping link occurrences: 32.

## CP328-S24 — P36–39

Source: `engine/pipeline/PL_PH_detector.py:743–768`.

Point projection uses id local cache, prior pair reuse only old original is same object. Otherwise swap PH/PL, Decimal.copy_negate price, reflect Order direction/stop and exchanged box edges, replace first cycle-id occurrence (not prefix-only), recursively project truthy identity_source. Save original/projected pair current run when non-null. No recursion cycle guard.

**Handoff:** Native callbacks receive actual projected point with untouched physical indexes, time and causes. P43 adapter present even if native callback absent; pending invalidation conditional on adapter presence, not native side effect.

B08 overlapping link occurrences: 26.

## Findings and scope

- CP340-F01 / REVIEWED_NO_ACTIVE_SPEC_CHANGE_REQUIRED: Detailed P18–22 and P36–39 agree with pinned implementation, including null cache membership, prospective local registers, role-specific gating and object-identity reflection. Historical CP328 procedure reference supplemented, not replaced.
- CP340-F02 / OPEN_CROSS_OWNER: Bridge owner commits, relabeling, serialization, live prefix, F05 and CP333-R01/R02 remain to reconcile.

Queue: 138/185; remaining 47. Supplemental accessors: 6/9; remaining 3. W1 B08: 670/670 retained, 151 overlapping link occurrences. Runtime and RAW NOT_RUN. CP341 / W2 Trading Pipeline queue semantic reconciliation: rereview all 45 queued Trading Pipeline records (split by functional ownership if needed) and remaining CP322-E02/E03/E04, pinned Bridge source, W1/B09, active serialization/chronology/lifecycle/Order/Primary contracts. Follow with 2 Live records and complete semantic resolution of CP331-F05, CP333-R01/R02 before W2 acceptance; W3/W4 gated.
