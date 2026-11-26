# BL — Blue Line formation and visibility (V3)


**Contract conventions.** B = bullish, R = bearish. Directional extreme X is Low for B and High for R; a strict improvement or stop is X < level for B and X > level for R. Confirmation uses High > top for B and Low < bottom for R. Main position/time, exact lower event, physical identity and ordinal are different fields. Preserve Decimal representation, original arithmetic order, stable traversal, and native failures unless an explicit fallback is specified. Use [declared record interfaces](../../Contracts/Declared_Record_Schemas.md) and [index/chronology services](20_Indexes_And_Caching.md). Procedure labels below name semantic operations, not required implementation symbols.


## BL-M01 — Inputs, outputs and formulas

Input native ordered same-direction Reactions and Resets, chronology. Output includes all Scale and Reset Blue records, even invalid or internal. A uses semantic sourceExtreme, not the drawing price. For each Reaction use Mode A anchor_value if non-null else leg_boundary_value (missing both is error); clear previous count. Other modes require prior Reaction and reference prior BoxBottom B/BoxTop R. Compute in this exact order with Decimal ratio 0.618:
- B: Top − (0.618 × (Top − reference)).
- R: Bottom + (0.618 × (reference − Bottom)).
For last confirmed strike's owning main candle: Scale drawing B = Low + (High−Low)/3, R = High − (High−Low)/3. Reset drawing same with divisor 5. Interval source time ± one timeframe. The strike extreme can be a lower-row price, while drawing uses full main OHLC.

## BL-M02 — Strike procedure

Walk every integer main-map key First..Break inclusive (native alignment of stored indices and chronology positions is a caller contract). Break uses lower extreme only through RE61's returned confirmation time inclusive (which can fall back to Break open); no lower rows means skip the entire Break including its color check. Threshold is last confirmed strike or Fibonacci level. A strict improvement beyond threshold establishes pending strike if no pending or strictly better than pending. Equal does not replace. Matching supplied main tag (GREEN B, RED R) confirms the pending strike; the same main candle can create and confirm it. Break's extreme is clipped, but its main tag is not clipped or recomputed at the confirmation cutoff. If still pending at end, search lower rows from pending source main time to Break main end, not past confirmation. Gather improved directional extremes before or on first confirmation-side strict crossing with eligible evidence; choose first traversed among equal most-directional extremes (earliest only under native ordered input). The eligible crossing need not occur exactly at the returned confirmation time or on the Break main. The row can qualify on both predicates; do not invent inside-row order. Map lower timestamp to a native chronology position, then use that position as the main-map key; preserve the mapped stored index/main time and lower price, not the exact lower timestamp. Unconfirmed pending does not count.

## BL-M03 — Sequence, spacing and Reset validity

Maintain previous Reaction, prior strike count, hasBlue (= any output including invalid/internal), intervening counter. Process in Reaction input order, ordinal from 1. Emit Scale iff prior count exists and current count grows, AND no Blue exists or counter >=1. Emission resets counter; otherwise if any Blue exists increment once for this Reaction (including internal owners; the counter name does not implement a separate healthy predicate). Then visit matching Reset records in original order. A Reset is eligible iff no Blue or counter>=1. Each emission resets counter; consequently a same-Reaction Scale prevents Reset, and multiple same-group Resets cannot all emit. Mode A resets prior count only, not spacing.
Reset Blue source main uses directional extreme and brokenLevel. Invalid only if previous Blue exists and its first strict stop after previous source through Reset is exactly on this Reset source index and Reset extends strictly beyond prior sourceExtreme. Emit invalid record nonetheless; A double-stop depends on it. No separate previous-valid check. Store checkpoint after each Reaction only when checkpoint capture was requested.

## BL-M04 — Internal/public selection and replay

An owner ordinal with behavior_internal true marks Blue internal. Otherwise both semantic and drawing prices must lie strictly inside same behavior Reaction public box, with behaviorFirst < sourceTime <= confirmation. No explicit healthy flag in geometry predicate; caller supplies candidate reactions. Missing Blue source time/prices or Reaction times do not qualify; missing or malformed required public box bounds on a time-eligible candidate raise natively. Never clear an existing true flag. Public filter is calculation_valid (default true) and not behavior_internal (default false), in original order. Live replay rewinds to first affected Reaction or Reset owner before supplied changed position; reuse only retained prefix and resume spacing/count; return shallow list. Do not remove invalid evidence before A.

## Detailed Blue procedures

### BL01 — _is_color

Input candle-like record, color. Read required tag, convert to string, uppercase it, compare to provided color without normalizing that argument. Return Boolean. Missing tag raises; no OHLC recomputation.

### BL02 — _main_candle

Input index-to-candle map and index. Return original map value. On KeyError only, raise ValueError with missing index in message and preserve causal exception. Other errors propagate. No nearest-candle fallback.

### BL03 — _stops_on_index

Resolve direction policy (invalid direction raises), directly Decimal-convert line source_extreme. Traverse positional slice of candles from max(0,start_index) through end_index inclusive, preserving sequence order. Directly Decimal-convert each directional extreme. On first strict penetration return whether that candle's integer index equals end_index; return false when absent. Earlier crossing causes false even if final candle also penetrates. Input indices are slice positions, not a search by candle.index. No mutation.

### BL04 — fibonacci_level

Resolve direction centrally. Let r=Decimal("0.618"), ref=reference. B: directly convert box_top to T, return T − r × (T − ref). R: directly convert box_bottom to U, return U + r × (ref − U). Preserve arithmetic order and current Decimal context. Reference is used as supplied. No quantization.

### BL05 — _intrabar_pending_confirmation

Inputs direction, chronology, reaction, comparison extreme, start_time, break_time, main map. Resolve direction; obtain RE61 reaction confirmation time via chronology default argument behavior (first strict lower crossing, or Break-open fallback if absent; not proof of an observed crossing). Query lower bounds from start_time to break_time+timeframe (right exclusive by dependency); use returned lower slice. Empty => null. Directly convert confirmation-side box level. Traverse lower rows in supplied order, stop at first timestamp strictly after confirmation. For each row, add it to eligible list if its directional extreme strictly improves comparison extreme. Then check whether same row strictly crosses the confirmation-side box level (B High>top; R Low<bottom). If both crossing and nonempty eligible list, choose minimum Low / maximum High among accumulated eligible rows, retaining first on equal extrema. Same-row penetration is eligible before crossing check; do not invent order inside that lower row. Map decisive row timestamp via chronology.main_index; missing mapped candle (including null value) => ValueError. Return ScaleStrike with mapped candle integer index and timestamp, but decisive LOWER row extreme (direct Decimal). If no qualifying crossing return null. The pending-source window is not clipped to the RE61 intrabar start, and a qualifying crossing may precede its returned cutoff; the cutoff itself may be a cached Break-open fallback. Local lists only; chronology may mutate its own cache.

### BL06 — count_scale_strikes

Inputs direction, reaction, chronology, reference, optional candle map default null. Compute BL04 first (validates direction). Build map by integer candle.index if absent; later duplicate keys overwrite. Convert reaction first_idx/break_idx to integers; collect every integer map key in inclusive interval using BL02 (missing => error, empty interval subsequently fails at last-candle selection). Confirming tag GREEN for B, RED for R. Obtain RE61 confirmation time (including Break-open fallback if no strict crossing) and Break main-candle lower bounds; retain only lower rows timestamp <= that returned time. Break extreme = directional min/max of directly converted retained prices, null if none; never use full Break OHLC as substitute. Iterate reaction main candles:
- Threshold = most recent confirmed strike extreme or Fibonacci level when none.
- Current extreme = clipped Break extreme when candle.index equals break_idx; otherwise main Low/High, directly converted.
- Null extreme skips the entire row including color confirmation.
- When extreme strictly beats threshold and pending absent OR also strictly beats pending extreme, replace pending with current main identity/time/extreme. Equal extreme does not replace earlier pending.
- If pending exists and BL01 returns matching confirming color, append pending and clear it. Same main candle can create and confirm pending. BL01 reads the supplied main tag, including for Break, without recomputing a color from lower prefix OHLC; price clipping does not imply clipping the color decision.
At end if pending exists, call BL05 with latest confirmed threshold or Fibonacci level, pending source time, Break main timestamp and map. Append returned strike only if non-null. Return pair (level, ordered confirmed strikes); unconfirmed pending is not returned. All local lists are fresh, no source-row edits by this procedure. The native chronology may update its confirmation cache. A caller-supplied non-null map is not validated or copied; Break extreme is chosen by stored candle index equality, while RE61 separately addresses its candle sequence by position. The native caller must maintain alignment.

### BL07 — _build_scale_blue_line

Inputs direction, reaction number, previous count, level, strikes, main map, chronology, internal flag. Last strike required; look up its main candle. Convert High then Low directly to Decimal. B drawing price = Low + (High−Low)/Decimal(3); non-bullish branch = High−(High−Low)/Decimal(3). Return BlueLine with direction, kind scale, supplied reaction number, previous count, length of strikes, supplied Fibonacci level, decisive source identity/time/extreme, broken_level=null, drawing price, start/end = decisive source time ± timeframe, internal flag, default valid=true. Source extreme is strike extreme (possibly lower row); drawing uses whole mapped main OHLC but time bounds use the decisive strike's stored main time, not the mapped candle's timestamp. No policy lookup here or separate validation.

### BL08 — _build_reset_blue_line

Input direction, reaction number, reset, previous line or null, candles and map, chronology, internal flag. Integer reset.index selects source. Convert High then Low directly. Drawing price same geometry as BL07 but divisor Decimal(5). Invalid iff previous line exists AND BL03 first stop from previous source_index+1 through reset_index is on reset index AND source Low<previous source extreme (B) / High>previous source extreme (else). Short-circuit; equality does not invalidate. Return Reset Blue even when invalid; kind reset, strike counts and Fibonacci null, source index is the converted reset.index map key (not a fresh read of the mapped candle's stored index), source time from the mapped main candle, source extreme main Low/High, directly converted reset.broken_level, drawing price, start/end ± timeframe, calculated validity and internal flag. Does not discard invalid Blue or check previous valid status. Validity uses the main positional stop scan, not an exact lower Reset event; it does not read reset event time. Drawing and mapped timestamp are evaluated before validity, broken level and record time bounds after it. Invalid records still require successful construction.

### BL09 — _calculate_blue_tail

Inputs direction, ordered reactions, chronology, resets, keyword-only start, checkpoint, caller-owned output list, optional checkpoint list default null. Build candle map by integer index (duplicate keys last wins); group original reset references by integer from_first_idx preserving reset input order, no sorting or deduplication. Restore previous reaction/count and healthy counter; has_blue = truthiness of output (includes invalid/internal). Iterate reactions suffix from start (whole sequence if start falsy); assign 1-based reaction number start+1 onward.
1. Read bool behavior_internal default false. If string mode is exactly A: reference = anchor_value if non-null, else leg_boundary_value; both absent => ValueError. Directly Decimal-convert, clear previous_count only. Else require previous reaction, otherwise ValueError; reference = previous box_bottom B / box_top else, directly converted.
2. BL06 returns level and strikes. Scale candidate iff prior count non-null and count strictly increases. Emit BL07 only if candidate AND no prior Blue OR healthy counter>=1 (the latter disjunction is grouped under candidate). On emit set has_blue=true, healthy=0, scale_emitted=true. If has_blue and no Scale emitted increment healthy by 1, even for an internal owner; this counter has no independent healthy predicate.
3. Traverse matching reset group. Skip each reset if has_blue AND healthy<1; otherwise emit BL08 with last output line or null; set has_blue=true and healthy=0. Thus no second reset from the same group after emission unless state permits it; Scale emission suppresses same-reaction Reset.
4. Set previous reaction/current count. If checkpoint list supplied, append new record with shallow copy of reaction, count, healthy, output length.
Return same output list. Output append happens before subsequent spacing-state changes; optional checkpoint is constructed from a shallow copy only after all matching resets. Exceptions (including checkpoint-copy failure) may leave caller lists partially mutated; no rollback here. Tail itself does not validate start or compare prefix length to checkpoint.line_count. Spacing state does not reset merely because a mode A appears.

### BL10 — detect_blue_lines

Validate direction membership exactly bullish/bearish; else ValueError. Call BL09 with start=0, fresh default checkpoint and empty output, resets default empty tuple. Return list, no checkpoint capture.

### BL11 — LiveBlueLineContinuation.__init__

Same exact direction validation as BL10. Store direction, create checkpoint list containing default checkpoint. Run BL09 with fresh list and checkpoint capture; retain returned lines. Constructor has no separate return.

### BL12 — LiveBlueLineContinuation.result

Property returns shallow copy of retained line list; line records are shared objects. Does not recalculate.

### BL13 — LiveBlueLineContinuation.update

Inputs revised reactions/chronology/resets, keyword-only first_changed, optional first_dirty_main null. Require 0 <= first_changed < current checkpoint count AND first_changed <= new reaction count; else ValueError. If dirty main provided, collect reset owner first indices for resets whose own index >= dirty. Scan earlier reaction positions [0,first_changed); rewind to first whose break index >= dirty OR first index belongs to affected reset owners. Select corresponding old checkpoint, keep checkpoint prefix inclusive and line prefix up to checkpoint.line_count (shallow slices). If revised suffix nonempty replay BL09 with these local lists. Replace retained checkpoint list then line list only after replay success; return BL12, whose copy occurs after publication. If suffix empty, truncate without invoking BL09. Failure during replay leaves retained list attributes un-replaced but does not roll back external chronology caches or shared object mutations; failure during result copy occurs after publication. Prefix checkpoint and Blue objects are shared references, not deep rollback snapshots. No timeframe or dirty-main range validation or own dirty-event discovery beyond these guards; removed Reset owners not present in supplied resets must be accounted for by caller's first_changed frontier.

### BL14 — public_blue_lines

Fresh list of original objects in input order satisfying bool(calculation_valid default true) AND NOT bool(behavior_internal default false); second condition short-circuited if invalid. No mutation or sorting.

### BL15 — mark_internal_blue_lines

Inputs line sequence, owner reactions, all behavior reactions. Start lazy interior index null and indexed=false. Define BL16–18 closures. Traverse lines in input order: if owner internal OR geometry internal (short-circuit), forcibly set behavior_internal=true on original line despite frozen record. Never clear existing true; no validity filter and no skip merely because the flag is already true. Earlier mutations can be visible through retained or returned shallow-list aliases. No separate return, no rollback; previous mutations survive exceptions. Owner and geometry tests are alternatives, direction invariant. Drawing offset alone does not qualify.

### BL16 — mark_internal_blue_lines.index_interiors

Collect windows from all behavior reactions in order. Read both behavior_first_time and behavior_confirmation_time default null before the guard; skip if either null. If either non-exact datetime or timezone-aware, return null immediately (disable index globally). Otherwise append first/confirmation/reaction triple. Return ChronologicalContainmentIndex even with empty windows; no reordering or checking first<=confirmation. See C01–C02 in [Index and cache contracts](20_Indexes_And_Caching.md). Errors propagate.

### BL17 — mark_internal_blue_lines.owner_is_internal

Compute integer reaction_number using missing or falsy value -> 0. Outside 1..owner count => false. Otherwise return truthiness of indexed owner behavior_internal default false. No reaction identity check beyond ordinal.

### BL18 — mark_internal_blue_lines.geometry_is_internal

Read source_time, line_price and source_extreme with null defaults. Any null => false before index creation. Convert drawing and semantic price via Decimal(string). Lazily call BL16 at most once on successful build per outer invocation; store result (including null) then indexed=true. Failure in the builder occurs before indexed is updated. This build precedes the source-time exact-type test. Candidates default all reactions; if index exists and source_time exact naive datetime, query enclosing(source_time,source_time). For each candidate re-read first/confirmation; skip missing. This recheck does not restore candidates omitted by a stale index if external time fields mutate. Require first < source_time <= confirmation. Convert behavior_public_box_bottom and top via Decimal(string); return true only if both semantic and rendered prices strictly between same bottom/top. Equal box boundaries fail. Else false. No explicit healthy flag test here; source's actual candidate collection is caller responsibility. Cached index is per outer invocation, not global. Geometry branch does not use direction.
