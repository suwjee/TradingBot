# W3 B03-04 — A constructor, crossing and extreme (CP369)

Pinned source: [A Zone lines 1–215](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L1-L215), blob `431934d2fb597238d5281a769c29fdb51747868b`. Local A01–A08, bounded native handoffs only.

## Ordered semantics

- **G1 / A declarations, L1–24:** A owns Blue pair/double-stop formation, trigger chronology and frozen geometry, not lifecycle admission. Three version/date constants are metadata, no trading decision. Imported native helpers are conditional on bindings.
- **G2 / A declarations, L25–37:** Frozen slotted BlueState retains original line reference; ordinal, formation index/time, main stop and exact stop event/time/price are distinct. Nullable annotations are not validators.
- **G3 / A declarations, L38–65:** Frozen slotted AZone stores direction, Blue ordinals/source/stop times/levels, continuation provenance, trigger main/exact event, Reaction ordinal/times and A source/price. Last three optional fields are keyword-only and default None; comment declares presentation-only intent, actual downstream nonparticipation requires consumer review.
- **G4 / A01, L66–75:** Detector constructor accepts direction, Reaction/Blue sequences and chronology; annotations do not enforce structure.
- **G5 / A01, L76–80:** Exact supported direction membership checked before state assignment; store direction then resolve native policy; list conversion retains Reaction iteration order and element aliases.
- **G6 / A01, L81–88:** Stable ascending sort of all Blue refs by integer reaction_number, required source_time, string kind, evaluated in key order. No validity/internal/kind filtering or ordinal uniqueness check. Equal complete keys keep input order.
- **G7 / A01, L89–95:** Store chronology then retrieve candles, seconds, timeframe, main times, lower times and lower index in order. References are captured, not copied/validated; chronology method calls later may consult different current attributes if reassigned.
- **G8 / A01, L96–103:** Build complete First timestamp array by int first_idx positional indexing, then complete Break array by int break_idx. Negative indexing is native; no local bounds validation or source-index identity assertion. Failures propagate.
- **G9 / A01, L104–110:** Build confirmation array using virtual method call in original Reaction order; base A14 explicitly false intrabar, RE61 fallback/cache allowed. Only after all arrays succeed evaluate separate exact-naive nondecreasing flags First, Break, confirmation in order. Empty arrays pass native predicate; flags not a freshness proof.
- **G10 / A02, L111–114:** Return stored policy.extreme_attr; native bullish Low/bearish High; no separate validation.
- **G11 / A03, L115–117:** Delegate value/level unchanged to stored strict comparator; B < and R >, equality false for finite ordinary prices. No local conversion.
- **G12 / A04, L118–120:** Delegate value/current unchanged to stored strict improvement comparator; equality retains previous. No local conversion.
- **G13 / A05, L121–123:** Delegate to chronology.main_index without clamp argument. Native right bisect minus one, default underflow raises, no upper-bound check; result position, not stored candle.index.
- **G14 / A06, L124–128:** Delegate start and nullable end to chronology.lower_window; native half-open slice from chronology's current arrays, no extra copying/validation.
- **G15 / A07, L129–134:** First crossing accepts supplied Decimal threshold and start/nullable end. No local reversal check or normalization of threshold.
- **G16 / A07, L135–136:** Left bisect captured lower_times at start then end lower bound if nonnull, otherwise length of captured lower sequence. End equality excluded, start equality included under sorted aligned input.
- **G17 / A07, L137–142:** If right>left and index not None, call first_less B or first_greater R on captured index; directional selection by exact self.direction. Index provider owns strictness, clipping and optional crossing-cache mutation.
- **G18 / A07, L143–148:** None position returns None immediately; zero is valid. Fetch captured lower row at returned position, read actual row timestamp then normalize its selected price via as_decimal, map timestamp via virtual A05. Do not re-test crossing against reread price or fall back on index miss. Return main position, exact row time, normalized price.
- **G19 / A07, L150–155:** When indexed path not selected, slice captured lower rows and traverse in supplied order. Read and normalize selected price then strict comparator; first hit reads timestamp and maps to main position. No inside-row ordering inferred.
- **G20 / A07, L156–158:** Any nonempty lower slice with no hit returns None, suppressing main fallback. Only empty slice continues; malformed/reversed ranges can yield empty slice without explicit reversal guard.
- **G21 / A07, L159–164:** Main fallback start=max(0,left bisect captured main opens). Nonnull end uses max(start_index,left bisect end), null uses len(candles). No containing-main predecessor, excludes main opens equal to end.
- **G22 / A07, L165–170:** Scan captured main slice in positional order, normalize selected extreme and strict compare. First hit returns integer stored candle.index then its timestamp and price, unlike lower result main position. Exhaustion None; no local list mutation, but provider index may retain crossings.
- **G23 / A08, L171–176:** Reject end<start before adding one microsecond to end. Equality allowed; native datetime overflow/errors propagate. Adjusted endpoint is exclusive for lower window.
- **G24 / A08, L177–183:** Ask chronology.lower_bounds on supplied start and adjusted end (not directly captured time array). Only left<right and captured index nonnull selects native range_minimum B/range_maximum R.
- **G25 / A08, L184–186:** Query yields price and lower position. Use captured lower_times[position] (not lower row.timestamp) to map via virtual A05 then read captured main candle timestamp. Return provider value as is, no normalization or recheck. Provider min/max resolves equal numeric prices by lowest physical position.
- **G26 / A08, L187–195:** Otherwise call A06 lower window anew; nonempty seed first original row and normalize price. Traverse remaining rows, replace source and value only on strict improvement; equal keeps first traversed including its Decimal representation.
- **G27 / A08, L196–201:** Map selected row's timestamp via A05, return normalized selected price, mapped main position, timestamp from captured main candle at that position, not exact lower time.
- **G28 / A08, L202–206:** Empty lower fallback computes start=max(0,right bisect(main times,start)-1); end=min(len(candles)-1,max(start_index,right bisect(main times,end)-1)). Includes containing main endpoints, unlike A07; no upper clamp on start.
- **G29 / A08, L207–214:** Seed main candle at start unconditionally, even if end<start; empty/out-of-range input can fail. Traverse subsequent positions through inclusive end with strict improvement, equal retains first. Return normalized price, int stored source.index, source.timestamp, not positional index. Entire containing candle geometry may include out-of-window prices; no invented intrabar order.
- **G30 / A08, L215–215:** Partition ends at blank before formation procedure; no extra runtime operation.

## Reconciliation

665 canonical category rows (131 W1, 534 additional), 9 historical supplements from [B03-04](../../../Audit/Phase_07/Semantic_Closure_B03_04.json), all W1 source identities and spans match CP314. Semantic review precedes counting. Preserve B03-04-F01/F02, all Blue and Reaction local qualifications and the five open cross-owner findings. CP369-F01 qualifies active documentation. No runtime, RAW, ZIP or production changes.

[Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP369_W3_A_Constructor_Crossing_Extreme_Local_Forensic_Register.json) · [Bounded consumer register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP369_W3_A_Constructor_Crossing_Extreme_Consumer_Boundaries.json) · [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP369_Completion.json).

Next A lines 216–336, B03-05.
