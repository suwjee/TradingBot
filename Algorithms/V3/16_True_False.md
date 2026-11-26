# True/False — final published behavior annotation (V3)

**Conventions:** B = bullish, R = bearish. Preserve Decimal representation and arithmetic order, native exception behavior, main time versus exact lower event, order and nulls. Record definitions are in [declared interfaces](../../Contracts/Declared_Record_Schemas.md). Procedure IDs designate semantic operations, not required implementation symbols. No runtime equivalence asserted.


## TF-M01 — Presentation-only input and scope

After all calculation, public visibility, regime and primary ownership rules, annotate each final segment independently. This pass mutates published dictionaries only, never native geometry or physical Order ownership. The three fields are trueFalse, trueFalseRepairTime, trueFalseRepeated. Remove prior annotation keys from every visited row even if invalid or donor. Choose one record per sourceTime by first insertion in priority traversal: primaryLows for B / primaryHighs otherwise, StopAll, E, S. Explicit Boolean false calculationValid excluded. A, Blue and opposite-side secondary points are not visited. Sort selected rows by source time. Non-winning rows do not acquire a neutral annotation. Selected rows begin with verdict null.

## TF-M02 — Two independent sequences

Scan selected rows; directional primary numbers 1/2/3 receive T/F/F; others null. Each primary flushes pending StopAll recurrence and clears its buffer; StopAll rows append. Then evaluate Basic on the entire sorted selected stream including boundary rows, followed by trailing StopAll. Every selected StopAll or directional primary resets active Basic price references and started flag, zeros base_count and verdict_count, but retains repair_count and latest-row references. Basic starts at first S after each boundary. S or any strictly smaller rank with base_count>=2 yields T independent of labels and price crossing. Otherwise E inverts the largest smaller rank strictly crossed price reference, using latest eligible reference within rank; odd F/even T only if no reference. Same-rank same-verdict display repetition and repair are independent; display_restart suppresses current display count accumulation, not base_count. Strict price frontier recurrence: [exact contract](22_True_False_Exact_Contract.md).

StopAll uses separate number series: equal/decreasing number starts new series; T/F alternates relative to current verdict_start. Track largest prior series end and immediate prior end; repeated prefix gets retrospective repeated=true and group-relative parity only when matching a boundary and confirmation is closed. Next number can restart verdict parity; a larger match can absorb interim verdicts. The exact recurrence and repair conditions are [True/False exact contract](22_True_False_Exact_Contract.md). StopAll closed test: decision main epoch + requested timeframe <= min(visible end main + timeframe, last RAW epoch + raw timeframe). Timing/serialization fields are not trading outputs.


## TF-M03 — Chart presentation (v2.8.7)

Foundation S/E passes repeated only when trueFalseRepeated is exactly true; a star uses the Secondary N/A color, the Foundation verdict label font, and appears above both direction marker sides when verdict is not N/A and the label is visible. StopAll retains its own repeated N/A/T/F path. Chart does not calculate verdicts. See [source renderer](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/apps/chart/src/chart/indicator-renderer.js#L18-L31) and [label helper](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/apps/chart/src/chart/true-false-label.js#L1-L61).
