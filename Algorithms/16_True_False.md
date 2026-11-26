# Independent True/False

TF annotates final rows only, never feeds formation. Source priority primary > StopAll > E > S. See [exact contract](22_True_False_Exact_Contract.md).

## 8. True/False evaluation

### 8.1 Scope, ordering and output ownership

Evaluate Basic S/E, StopAll, and the directional primary numbers independently. This step annotates the already-serialized final behavior rows. Within a published segment, clear previously added verdict, repair and repeat fields on the four input collections. For each source time choose the first valid row by this collection priority:

1. Directional primary collection, `primaryLows` for bullish or `primaryHighs` for bearish.
2. `stopAlls`.
3. `eZones`.
4. `sZones`.

The winner is the first eligible row within the selected collection. A row with `calculationValid: false` cannot win. After choosing owners, order rows by complete source epoch. The opposite primary collection is outside this pass. A donor suppressed at the same source cannot also produce an independent Basic verdict. The optional nested `bridgeOutput` projection is separate from the native arrays and does not receive these annotations. Its projected StopAll source is `formedAt.time` in Tehran display form, while the native row uses epoch `sourceTime`. Aggregate arrays and their owning segment arrays share the same final row objects.

The native calculation can have access to accepted history before the display start. The verdict evaluator sees only the source rows included in the published segment. Cropping earlier source rows can change its available Basic parents and StopAll baseline. Re-evaluation after a live append uses the new published result and exact close evidence for the current horizon. No separate client-side label history is authoritative.

### 8.2 Basic classification and engulf reset

Maintain a lookup of already assigned verdicts by source time and an active record per exact rank. The active record holds the latest occurrence, a verdict repetition count, and a separately maintained repair count. Rank is kind/family priority and, for E, its integer continuation number.

1. Before the first admitted S in that segment, an admitted E has no Basic classification and retains a neutral null verdict.
2. Every admitted S is T. A later E normally alternates from its already-assessed published parent, T to F or F to T. If the parent has no assigned published Basic verdict at that point, fall back to E number parity, odd F and even T. Therefore a simple S → E1 → E2 → E3 chain is T, F, T, F.
3. Before counting the new occurrence, check lower-rank records. If at least one lower rank has at least two qualifying occurrences of the same exact rank and same T/F label, the incoming larger behavior is an engulf. Assign that new behavior T even if its ordinary E parent alternation would yield F.
4. An occurrence of higher rank displaces lower-rank records. A lower-rank intervening behavior normally leaves a higher-rank repeat intact. If the intervening behavior itself starts an engulf, its global verdict restart applies. A same-rank occurrence with a different label starts a new repeat count.
5. On an engulf clear all surviving verdict repetition counts. The incoming behavior seeds its own new count of 1. Keep earlier assigned labels available for parent lookup. Keep separate F repair history. The new T marks the incoming behavior and does not rewrite the earlier displayed labels.

Thus two smaller S Blue objects can cause an S Red or E1 Blue to be the first T of a fresh count. An older S Red from before that reset cannot combine with the new S Red for the next repetition even if the two are of the same type and label.

### 8.3 Basic F repair

Use the finest available RAW and a strict crossing of the reference level. In bullish a lower Low repairs the reference. In bearish a higher High repairs the reference. Equality does not qualify, and the RAW Close need not cross. The reference's original market direction governs its test even after a reversal.

- For a repeated same-rank F record, the latest occurrence supplies the active reference. Look for the first strict crossing at or after that occurrence's source time. A crossing belonging to an older occurrence strictly before the new source may remain historical evidence. If the older occurrence's repair was at or after the new source, remove that attribution when the new reference supersedes it.
- When a larger Basic behavior displaces a singleton lower-rank F, the larger behavior's source time supplies the singleton's earliest search time. An already-classified F can be repaired even when the newer behavior has its own T verdict.
- Search through the end of the last visible main bucket, inclusive, using RAW rows actually supplied in that window. The bridge computes an inclusive horizon of visible bucket start + analysis duration - 1 second. Lower RAW from within that bucket is allowed. Re-evaluate as the horizon advances.
- Publish the first eligible crossing as `trueFalseRepairTime` on the owner row. The original Basic T/F label remains as assessed. A prior segment can supply a historical reference only if its source row is in the published result.
- Each eligible F reference is searched independently. The Engine does not wait for one F to be repaired before evaluating another, and no global newest-first or oldest-first queue exists. If a single RAW event strictly crosses several separately eligible references after their own search starts, each may receive that same epoch in `trueFalseRepairTime`. The rule that the latest occurrence represents a repeated F group still applies within that group.

### 8.4 StopAll series, shorter series and confirmation close

Reset the StopAll verdict state at the source of each finalized directional primary, at the calculation start, and with a new independent regime. Partition published StopAlls within that history at an equal or decreasing native number. The first published number in a new segment or series is its starting number. An ordinary series alternates T/F by the distance from that number, with an even offset producing T. Native object numbering belongs to the owner stages and is separate from the verdict calculation.

1. Keep two comparison endpoints for the current group. The first is the last number of the immediately preceding published series. The second is the largest last number among all earlier series in the same history. A shorter group supplies the first endpoint for the next group and leaves the historical maximum intact.
2. Begin the group at T, alternating by native number distance from its first published number. A group that ends below the first endpoint has ordinary T/F and carries no N/A. Neither comparison qualifies if its exact endpoint is absent. Intermediate earlier endpoints below the historical maximum do not supply additional matches.
3. When a StopAll exactly reaches either endpoint and its confirmation main candle has closed, flag the current prefix through it as repeated and assign the group's original alternating T/F to that prefix. Previous groups retain their own verdicts. If both endpoints are equal, one confirmed match flags the prefix once.
4. After any confirmed match, the first higher published number in the same group starts a fresh count at T. Continue alternating by distance from that number. When the current group later confirms its larger historical endpoint, extend N/A through it and recalculate the newly covered rows from the group's original start. The first higher number after the larger endpoint starts another fresh count at T. Any native restart or directional primary boundary applies before counting a row as part of the current series.
5. In the live/manual Bridge, a matching StopAll satisfies the close gate when its `decisionTime + analysisDuration` is at or before the lesser of `lastVisibleMainStart + analysisDuration` and `lastSuppliedRawStart + rawDuration`. Use the confirmation candle's `decisionTime`. Vite supplies the selected RAW duration in seconds. The direct CLI accepts `--raw-timeframe` and defaults to 1 second. Direct calls on finalized row sets can omit the closure callback.

The corrected A–G schematic in one primary-delimited history yields the following after each applicable endpoint confirms and closes. A bracketed entry carries both N/A and its T/F.

| Group | Prior group endpoint | Largest prior endpoint | Current display |
|---|---:|---:|---|
| A | None | None | T, F, T |
| B | 3 | 3 | [N/A + T], [N/A + F], [N/A + T] |
| C | 3 | 3 | T, F |
| D | 2 | 3 | [N/A + T], [N/A + F], [N/A + T], T |
| E | 4 | 4 | T |
| F | 1 | 4 | [N/A + T], T |
| G | 2 | 4 | [N/A + T], [N/A + F], [N/A + T], [N/A + F], T |

In F, number 2 starts a fresh count. In G, number 2 belongs to the repeated prefix and is F. When G reaches 4, it covers all four numbers from the D endpoint, including the two already marked after matching F. Beyond an even matched endpoint, the first new odd number is T. Beyond an odd matched endpoint, the first new even number is T.

For lengths 1 → 2 → 2, the middle series' second StopAll is T and the final series' second StopAll is N/A + F. If the preceding and largest endpoint is 3 and the published numbers are 1, 2, 4, 5, the labels remain T, F, F, T. The published prefix cannot match a missing exact endpoint.

### 8.5 Directional primary verdicts and nullability

Only the final PL in bullish and final PH in bearish participate in this track. Final number 1 is T. Final numbers 2 and 3 are F. A valid admitted directional point at another native number is neutral. Each admitted directional primary still resets the StopAll verdict history. The opposite primary does not reset that history.

| Public field | Meaning |
|---|---|
| `trueFalse: "T"` or `"F"` | Final verdict on the assessed source owner. |
| `trueFalse: null` | Assessed source owner with no assigned T/F, such as a directional primary outside 1–3 or an E before the first admitted S. |
| absent `trueFalse` | Row outside the verdict projection, suppressed/noneligible source owner, or a legacy payload. |
| `trueFalseRepeated: true` | StopAll's repeated prefix flag. The same row retains its T/F. Non-repeated rows omit this flag. |
| `trueFalseRepairTime` | Exact first recognized repair RAW event time in Unix seconds. Its absence means no published repair evidence. |
