# CP292 — Current chronology rebaseline supplement

Baseline: `c99b4c957e932d9ee70c492ca03ce80711447fc1`. **RB07 INCOMPLETE**; scoped source review only. This supplement refines existing CH37–CH45 and CH120–CH123; it does not replace historical evidence or assert full site-level equivalence.

## C01 — CH37

Projection horizon excludes its end; duplicate lower rows at the exact recorded event time are inspected for a directional strict crossing. No substitute search or main fallback promotion.

[Pinned source engine/bridge/trading_pipeline.py:690–739](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L690-L739)

## C02 — CH38

Independent main segment is [start,stop); lower boundaries use bisect-left at both ends. Reindex unless indexed mode has a zero start for the respective sequence; clamp visible range independently and accumulate index offset.

[Pinned source engine/bridge/trading_pipeline.py:1826–1857](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1826-L1857)

## C03 — CH38

Index windows flatten to the retained base. First-cross queries clamp to local half-open range and return null for empty range; extrema reject invalid range. Translate returned positions back to local indexes.

[Pinned source engine/bridge/trading_pipeline.py:1788–1823](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1788-L1823)

## C04 — CH39

Equal epoch may dirty the last lower bucket; same main bucket dirties its tail; timeframe one shares the dirty frontier. Exceptions during staged replay restore prior suffixes and time and remove newly installed price keys.

[Pinned source engine/bridge/trading_pipeline.py:225–295](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L225-L295)

## C05 — CH40

Continuation validates positive integral times and nondecreasing order, extends request end to last time, then stages buckets. Any BaseException during calculation or validation progress resets retained views after rollback; external progress side effects not reverted.

[Pinned source engine/bridge/live_pipeline.py:35–70](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/live_pipeline.py#L35-L70)

## C06 — CH40/CH123

Closed-prefix cache exact key includes direction, absolute offset/end, boundary timestamp, visible bounds and initial trend flags. Reuse iff exclusive absolute end <= first dirty main and a matching entry exists. Publish only used entries after successful stage exit.

[Pinned source engine/bridge/trading_pipeline.py:1756–1785](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1756-L1785)

## C07 — CH120

At most eight feedback passes. Accepted E owns occupied physical source; independent donor only at unoccupied source. Reconcile optional StopAll, restore independent roots, ensure accepted audit, discover legs. Equal identity publishes; previously seen changed identity or exhaustion raises.

[Pinned source engine/bridge/trading_pipeline.py:2569–2645](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L2569-L2645)

## C08 — CH120/CH121

Reusable full context requires E engine and enabled S. Build geometry on physical range for both directions; Primary presence requests both calculation directions. Persist converged E and StopAll, detectors and validity separately from later display.

[Pinned source engine/bridge/trading_pipeline.py:2648–2802](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L2648-L2802)

## C09 — CH122

Copy converged E/StopAll; visibility does not re-run donor restoration or reset-leg discovery. Capture projection before lifecycle visibility; capture Primary groups after lifecycle visibility and before range clipping. Public A/S/E/StopAll source index inclusive; A/S invalidity and internal filtering follow. Accepted out-of-range A provenance and required Order identities retained.

[Pinned source engine/bridge/trading_pipeline.py:2939–3112](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L2939-L3112)

## C10 — CH123

Boundary strictly within current physical segment. Closed history excludes reversal candle; validate Primary3 number, source time and Decimal price even when cached. If no selected historical range, blank lists only after validation. Begin new independent regime at boundary with target trend bootstrap; stop when next transition absent or beyond selected end.

[Pinned source engine/bridge/trading_pipeline.py:3531–3630](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3531-L3630)

## C11 — CH45

Reverse only at transition index <= visible end. Active direction uses maximum (segment start index,direction). Repair through visible last start + timeframe minus one second; closure bound is minimum of through+1 and last lower epoch+RAW duration; StopAll decision plus main timeframe <= closure. Annotate each segment independently.

[Pinned source engine/bridge/trading_pipeline.py:3680–3703](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3680-L3703)

## C12 — CH41

Repair lookup includes through endpoint (bisect-right) and reference start (bisect-left); selects first strict direction-specific lower crossing using Decimal level; returns exact lower epoch or null.

[Pinned source engine/pipeline/true_false.py:18–30](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/true_false.py#L18-L30)

## C13 — CH42

For greater rank, engulf requires any lower base count >=2. Display restart uses distinct verdict counts. Otherwise use highest smaller rank with strictly crossed reference; latest eligible at that rank. Bullish negates Decimal price. Frontier pops older entries >= normalized price; reset clears frontier, base and verdict counts but retains repair count and latest object. Lower-rank removal may repair singleton F; same-verdict F replacement preserves chronology.

[Pinned source engine/pipeline/true_false.py:47–128](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/true_false.py#L47-L128)

## C14 — CH43

Nonincreasing StopAll number restarts group; parity from verdict start. Repeated prefix qualifies at previous series end or largest prior end only if optional confirmation closure passes. A match recomputes prefix parity then restarts verdicts on next row.

[Pinned source engine/pipeline/true_false.py:131–159](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/true_false.py#L131-L159)

## C15 — CH44

Clear previous annotations on all visited rows. Exclude only exact Boolean false from selection. Per source time first row wins in Primary/StopAll/E/S order; sorted source-time events drive Basic resets and primary StopAll group flush. This is presentation precedence, not physical event order.

[Pinned source engine/pipeline/true_false.py:162–188](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/true_false.py#L162-L188)

## C16 — CH41/CH42

Strict price crossing is bullish lower-than, bearish greater-than. Price normalization uses low/high policy; lifecycle and ordering are not direction-policy responsibilities.

[Pinned source engine/pipeline/direction_policy.py:32–70](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/direction_policy.py#L32-L70)

## C17 — CH40

Per-calculation timestamp caches and market indexes clear at entry and finally. Bucket replay stages closed-regime cache only with views and a required delta; fresh RAW function calls normal calculation without supplied cache. No claim of actual runtime dispatch.

[Pinned source engine/bridge/trading_pipeline.py:3713–3767](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3713-L3767)

## C18 — CH40

Byte-prefix continuity verified before append; append lineage requires strictly increasing new RAW times, distinct from continuation's nondecreasing internal validation. Catch-up rows are appended before new rows. Update lineage only after successful pipeline append.

[Pinned source engine/bridge/live_pipeline.py:114–156](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/live_pipeline.py#L114-L156)

## Remaining gate

All 18 previously unmatched scope source identities have been located, including 12 named and six anonymous constructs. Canonical indices are inferred from the contiguous lexical sequence, not independently re-executed. The 589 unmatched site rows remain open. See [scope and chronology evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP292_Chronology_Scope_Review.json). No RAW or runtime tests were run; Phase 07 remains incomplete.

## CP292 follow-up — Changed dependency context

Native configured Reaction index validates sequence identity for prepared registration, retains strict crossing and earliest-position extrema ties, and keeps per-chronology caches separate. The current public main and live calculation entry paths prepare pipeline state without a per-detector live protocol object. Retained views and staged closed-prefix resolution are distinct from that optional interface; conditional finder methods are not claimed active on these entry paths.

Independent E-root restoration updates accepted-source identity state. Native E reexports accepted Order_B discovery and inherits audit-preserving registration from OrderAuditEngineMixin. Lifecycle derives StopAll from donor chronology and publishes reset boundaries without retroactively rebuilding E from future boundaries. Visibility E and S stop results have distinct tuple shapes. True/False repair is strict and bounded on lower timeframe; repeated StopAll prefix relabeling has a separate confirmation closure gate.

See [dependency context review](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP292_Dependency_Context_Review.json) for 14 source-anchored contracts. The historical Remaining gate above describes entry state; [combined gap evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP292_Combined_Gap_Validation.json) accounts for all 589 complement rows. Canonical full-module node/statement/anonymous linkage remains open; RB07 INCOMPLETE.
