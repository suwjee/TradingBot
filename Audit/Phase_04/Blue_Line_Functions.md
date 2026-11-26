# Phase 04 — Blue Line function contracts (checkpoint 02)

Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Source identity: engine/pipeline/blue_line_detector.py, blob `f25efc55bbc387c6a3a592ffe3ff87ee12cf6891`, version 2.4.1. All 18 named declarations, including nested visibility helpers, are described here. Owner: Blue geometry, strike count, spacing, Reset validity and Blue visibility, not downstream A/S/E lifecycle. No execution.

## Shared interpretation

B = bullish, R = bearish. Directional extreme = Low for B, High for R. Better and stop = strictly smaller for B, strictly larger for R. Confirmation-side extreme = High for B, Low for R. Decimal conversions below distinguish direct conversion from string conversion. No added rounding or finite-input guard. Unless a function catches an error explicitly, input access, conversion, indexing, comparison and dependency failures propagate. Outputs preserve the order described, not arbitrary set iteration. Record interfaces: [declared schemas](../../Contracts/Declared_Record_Schemas.md). ScaleStrike is frozen/slotted (source_index, source_time, extreme). BlueLine is frozen/slotted, defaults calculation_valid=true and behavior_internal=false; no native runtime annotation validation. _BlueCheckpoint is frozen/slotted: previous reaction and count null, healthy count and line count zero by default. The fixed ratio is Decimal 0.618. No price precision policy is introduced by documentation.

## BL01 — _is_color (51–52)

Input candle-like record, color. Read required tag, convert to string, uppercase it, compare to provided color without normalizing that argument. Return Boolean. Missing tag raises; no OHLC recomputation.

## BL02 — _main_candle (55–59)

Input index-to-candle map and index. Return original map value. On KeyError only, raise ValueError with missing index in message and preserve causal exception. Other errors propagate. No nearest-candle fallback.

## BL03 — _stops_on_index (62–75)

Resolve direction policy (invalid direction raises), directly Decimal-convert line source_extreme. Traverse positional slice of candles from max(0,start_index) through end_index inclusive, preserving sequence order. Directly Decimal-convert each directional extreme. On first strict penetration return whether that candle's integer index equals end_index; return false when absent. Earlier crossing causes false even if final candle also penetrates. Input indices are slice positions, not a search by candle.index. No mutation.

## BL04 — fibonacci_level (78–84)

Resolve direction centrally. Let r=Decimal("0.618"), ref=reference. B: directly convert box_top to T, return T − r × (T − ref). R: directly convert box_bottom to U, return U + r × (ref − U). Preserve arithmetic order and current Decimal context. Reference is used as supplied. No quantization.

## BL05 — _intrabar_pending_confirmation (87–142)

Inputs direction, chronology, reaction, comparison extreme, start_time, break_time, main map. Resolve direction; obtain exact reaction confirmation via chronology default argument behavior. Query lower bounds from start_time to break_time+timeframe (right exclusive by dependency); use returned lower slice. Empty => null. Directly convert confirmation-side box level. Traverse lower rows in supplied order, stop at first timestamp strictly after confirmation. For each row, add it to eligible list if its directional extreme strictly improves comparison extreme. Then check whether same row strictly crosses the confirmation-side box level (B High>top; R Low<bottom). If both crossing and nonempty eligible list, choose minimum Low / maximum High among accumulated eligible rows, retaining first on equal extrema. Same-row penetration is eligible before crossing check; do not invent order inside that lower row. Map decisive row timestamp via chronology.main_index; missing mapped candle (including null value) => ValueError. Return ScaleStrike with mapped candle integer index and timestamp, but decisive LOWER row extreme (direct Decimal). If no qualifying crossing return null. Local lists only.

## BL06 — count_scale_strikes (145–230)

Inputs direction, reaction, chronology, reference, optional candle map default null. Compute BL04 first (validates direction). Build map by integer candle.index if absent; later duplicate keys overwrite. Convert reaction first_idx/break_idx to integers; collect every positional integer index in inclusive interval using BL02 (missing => error, empty interval subsequently fails at last-candle selection). Confirming tag GREEN for B, RED for R. Obtain exact confirmation and Break main-candle lower bounds; retain only lower rows timestamp <= confirmation. Break extreme = directional min/max of directly converted retained prices, null if none; never use full Break OHLC as substitute. Iterate reaction main candles:
- Threshold = most recent confirmed strike extreme or Fibonacci level when none.
- Current extreme = clipped Break extreme when candle.index equals break_idx; otherwise main Low/High, directly converted.
- Null extreme skips the entire row including color confirmation.
- When extreme strictly beats threshold and pending absent OR also strictly beats pending extreme, replace pending with current main identity/time/extreme. Equal extreme does not replace earlier pending.
- If pending exists and BL01 returns matching confirming color, append pending and clear it. Same main candle can create and confirm pending.
At end if pending exists, call BL05 with latest confirmed threshold or Fibonacci level, pending source time, Break main timestamp and map. Append returned strike only if non-null. Return pair (level, ordered confirmed strikes); unconfirmed pending is not returned. All local lists are fresh, no source-row edits.

## BL07 — _build_scale_blue_line (233–268)

Inputs direction, reaction number, previous count, level, strikes, main map, chronology, internal flag. Last strike required; look up its main candle. Convert High then Low directly to Decimal. B drawing price = Low + (High−Low)/Decimal(3); non-bullish branch = High−(High−Low)/Decimal(3). Return BlueLine with direction, kind scale, supplied reaction number, previous count, length of strikes, supplied Fibonacci level, decisive source identity/time/extreme, broken_level=null, drawing price, start/end = decisive source time ± timeframe, internal flag, default valid=true. Source extreme is strike extreme (possibly lower row); drawing uses whole main OHLC. No policy lookup here or separate validation.

## BL08 — _build_reset_blue_line (271–323)

Input direction, reaction number, reset, previous line or null, candles and map, chronology, internal flag. Integer reset.index selects source. Convert High then Low directly. Drawing price same geometry as BL07 but divisor Decimal(5). Invalid iff previous line exists AND BL03 first stop from previous source_index+1 through reset_index is on reset index AND source Low<previous source extreme (B) / High>previous source extreme (else). Short-circuit; equality does not invalidate. Return Reset Blue even when invalid; kind reset, strike counts and Fibonacci null, source index/time from reset candle, source extreme main Low/High, directly converted reset.broken_level, drawing price, start/end ± timeframe, calculated validity and internal flag. Does not discard invalid Blue or check previous valid status.

## BL09 — _calculate_blue_tail (333–444)

Inputs direction, ordered reactions, chronology, resets, keyword-only start, checkpoint, caller-owned output list, optional checkpoint list default null. Build candle map by integer index; group resets by integer from_first_idx preserving reset input order. Restore previous reaction/count and healthy counter; has_blue = truthiness of output (includes invalid/internal). Iterate reactions suffix from start (whole sequence if start falsy); assign 1-based reaction number start+1 onward.
1. Read bool behavior_internal default false. If string mode is exactly A: reference = anchor_value if non-null, else leg_boundary_value; both absent => ValueError. Directly Decimal-convert, clear previous_count only. Else require previous reaction, otherwise ValueError; reference = previous box_bottom B / box_top else, directly converted.
2. BL06 returns level and strikes. Scale candidate iff prior count non-null and count strictly increases. Emit BL07 only if candidate AND no prior Blue OR healthy counter>=1 (the latter disjunction is grouped under candidate). On emit set has_blue=true, healthy=0, scale_emitted=true. If has_blue and no Scale emitted increment healthy by 1.
3. Traverse matching reset group. Skip each reset if has_blue AND healthy<1; otherwise emit BL08 with last output line or null; set has_blue=true and healthy=0. Thus no second reset from the same group after emission unless state permits it; Scale emission suppresses same-reaction Reset.
4. Set previous reaction/current count. If checkpoint list supplied, append new record with shallow copy of reaction, count, healthy, output length.
Return same output list. Exceptions may leave caller lists partially mutated; no rollback here. Spacing state does not reset merely because a mode A appears.

## BL10 — detect_blue_lines (447–459)

Validate direction membership exactly bullish/bearish; else ValueError. Call BL09 with start=0, fresh default checkpoint and empty output, resets default empty tuple. Return list, no checkpoint capture.

## BL11 — LiveBlueLineContinuation.__init__ (470–481)

Same exact direction validation as BL10. Store direction, create checkpoint list containing default checkpoint. Run BL09 with fresh list and checkpoint capture; retain returned lines. Constructor has no separate return.

## BL12 — LiveBlueLineContinuation.result (484–485)

Property returns shallow copy of retained line list; line records are shared objects. Does not recalculate.

## BL13 — LiveBlueLineContinuation.update (487–514)

Inputs revised reactions/chronology/resets, keyword-only first_changed, optional first_dirty_main null. Require 0 <= first_changed < current checkpoint count AND first_changed <= new reaction count; else ValueError. If dirty main provided, collect reset owner first indices for resets whose own index >= dirty. Scan earlier reaction positions [0,first_changed); rewind to first whose break index >= dirty OR first index belongs to affected reset owners. Select corresponding old checkpoint, keep checkpoint prefix inclusive and line prefix up to checkpoint.line_count (shallow slices). If revised suffix nonempty replay BL09 with these local lists. Replace retained checkpoint and line lists only after replay success; return BL12. No timeframe validation or own dirty-event discovery beyond these guards.

## BL14 — public_blue_lines (517–524)

Fresh list of original objects in input order satisfying bool(calculation_valid default true) AND NOT bool(behavior_internal default false); second condition short-circuited if invalid. No mutation or sorting.

## BL15 — mark_internal_blue_lines (526–590)

Inputs line sequence, owner reactions, all behavior reactions. Start lazy interior index null and indexed=false. Define BL16–18 closures. Traverse lines in input order: if owner internal OR geometry internal (short-circuit), forcibly set behavior_internal=true on original line despite frozen record. Never clear existing true; no validity filter. No separate return, no rollback; previous mutations survive exceptions. Owner and geometry tests are alternatives, direction invariant. Drawing offset alone does not qualify.

## BL16 — mark_internal_blue_lines.index_interiors (541–552)

Collect windows from all behavior reactions in order. Read behavior_first_time and behavior_confirmation_time default null; skip if either null. If either non-exact datetime or timezone-aware, return null immediately (disable index globally). Otherwise append first/confirmation/reaction triple. Return ChronologicalContainmentIndex even with empty windows; no reordering or checking first<=confirmation. See [C01–C02](Checkpoint_01.md). Errors propagate.

## BL17 — mark_internal_blue_lines.owner_is_internal (554–558)

Compute integer reaction_number using missing or falsy value -> 0. Outside 1..owner count => false. Otherwise return truthiness of indexed owner behavior_internal default false. No reaction identity check beyond ordinal.

## BL18 — mark_internal_blue_lines.geometry_is_internal (560–586)

Read source_time, line_price and source_extreme with null defaults. Any null => false before index creation. Convert drawing and semantic price via Decimal(string). Lazily call BL16 at most once for this outer invocation; store result then indexed=true. Candidates default all reactions; if index exists and source_time exact naive datetime, query enclosing(source_time,source_time). For each candidate read first/confirmation; skip missing. Require first < source_time <= confirmation. Convert behavior_public_box_bottom and top via Decimal(string); return true only if both semantic and rendered prices strictly between same bottom/top. Equal box boundaries fail. Else false. No explicit healthy flag test here; source's actual candidate collection is caller responsibility. Cached index is per outer invocation, not global. Geometry branch does not use direction.

## Coverage boundary

All 18 named declarations are individually described; 4 class declarations are accounted for by record or constructor/property contracts. Anonymous scopes (2 lambdas, 2 dict comprehensions, 3 list comprehensions, 1 generator and 1 set comprehension) are addressed in their containing descriptions. Later review must reconcile every Phase 02 node-level traceability record and upstream dependency (chronology and Reaction confirmation, lower indices, core utility) without treating nominal method name as exact receiver binding. No runtime evidence.