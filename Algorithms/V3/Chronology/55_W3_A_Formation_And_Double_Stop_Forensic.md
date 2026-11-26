# W3 B03-05 — A formation, Blue states and double-stop (CP370)

Pinned source: [A Zone lines 216–336](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L216-L336), blob `431934d2fb597238d5281a769c29fdb51747868b`. Local A09–A12, bounded native handoffs only.

## Ordered semantics

- **G1 / A09, L216–219:** Convert required Blue reaction_number to int; less than one short-circuits length read, otherwise greater than Reaction count rejects. Ordinal gate applies before kind, including Reset; no physical identity comparison.
- **G2 / A09, L220–224:** Exact string kind scale selects original Reaction at ordinal-1; convert its Break to int, call virtual A14; formation and stop scan start both that returned time (including native fallback, not proof of crossing).
- **G3 / A09, L225–229:** Every other kind takes non-scale branch, convert line.source_index, read positional main timestamp, call virtual A10, then compute nominal main open+timeframe as stop-scan start, not next actual main open.
- **G4 / A09, L230–232:** Read candles[index] even though local variable unused; this read occurs after formation/stop start, may fail. Return index, formation event and stop scan start, distinct fields.
- **G5 / A10, L233–238:** Read main at source_index, get timestamp and compute nominal end before normalizing required broken_level via shared as_decimal. No independent direction or ordinal validation.
- **G6 / A10, L239–243:** Traverse lower_window(start,end) in supplied order, normalize directional price then strict crossing; return first hit's timestamp. If no hit (empty or nonempty), return main open without testing coarse OHLC. No direct index query here, no proof flag.
- **G7 / A11, L244–249:** Fresh local state list. Enumerate entire sorted Blue list from 1, then bool(calculation_valid default true) false skips before reading formation or source price. Ordinal positions include invalid lines; internal flag not tested.
- **G8 / A11, L250–256:** Resolve virtual formation before normalizing semantic source_extreme (not rendered price), call virtual first crossing with formation-dependent stop start and unbounded end. No independent stop revalidation.
- **G9 / A11, L257–262:** Construct BlueState before append, retain original Blue object and full ordinal plus formation index/time.
- **G10 / A11, L263–270:** Test stop tuple truthiness separately for optional fields, not index truthiness (tuple with index 0 valid). Read main timestamp through candles[stop[0]]; returned index must align with position for native fallback. Store exact event time and extreme independently; no hit gives None fields; stop_level always threshold.
- **G11 / A11, L271–273:** Append built state, return fresh ordered list. No mutation of source line by this method, but virtual calls/provider caches can mutate; failed construction does not return partial list.
- **G12 / A12, L274–277:** Initialize fresh special candidate list and nullable retained prior pair. Traverse full sorted Blue sequence, 1-based ordinal independent of valid-only state sequence.
- **G13 / A12, L278–283:** Truthy validity default true replaces previous with ordinal and original line, then continue. Invalid line without retained previous skips; otherwise unpack retained previous. No kind, internal, or Reaction ordinal gate of A09 in this route.
- **G14 / A12, L284–286:** Convert invalid line.source_index; read line.source_time as formation start separately from candles[formation_index].timestamp. These can differ, no equality assertion.
- **G15 / A12, L287–293:** Normalize prior semantic source_extreme, search first crossing from invalid line source_time to nominal source main end exclusive. Only None or returned index unequal to formation_index causes skip; no second search for recross. Retain prior on failure; coarse fallback possible only according to A07.
- **G16 / A12, L294–300:** Unpack trigger index, event timestamp, discard returned extreme. Virtual A15 called with trigger event and not_before=invalid line.source_time, not mapped source main open. No match skips and retains prior.
- **G17 / A12, L301–307:** Unpack matched Reaction ordinal/ref, convert First then Break before virtual A17 source computation. None source skips retaining prior; successful source supplies index, main timestamp, price.
- **G18 / A12, L308–316:** Build zone using virtual A21 before append. Direction and Blue ordinals, each stored Blue source_time (reread), both effective stop main times equal mapped invalid source main timestamp, not necessarily either exact stop event.
- **G19 / A12, L317–321:** Normalize previous source_extreme then invalid source_extreme as stop levels; normalize previous extreme again for continuation; convert previous source_index then read source_time. Preserve evaluation order and distinct provenance, no trigger extreme substitution.
- **G20 / A12, L322–331:** Store trigger index, main timestamp at that index, exact trigger event; matched ordinal and First/Break main times; A source index/time/price; route double-stop. Do not supply optional exact Blue stop event fields, native A21 defaults None. No A acceptance or visibility decision.
- **G21 / A12, L332–336:** Append constructed candidate then set previous None. Failures before append do not clear retained predecessor; exceptions propagate, no partial result returned. A20 later resolves collision, not here.

## Reconciliation

398 canonical category rows (95 W1, 303 additional), 6 historical supplements from [B03-05](../../../Audit/Phase_07/Semantic_Closure_B03_05.json). All W1 identities/spans match CP314, disjoint from CP369. Preserve B03-05-F01–F03 and the five open cross-owner findings. CP370-F01 qualifies active documentation. No runtime, RAW, ZIP or production changes.

[Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP370_W3_A_Formation_Double_Stop_Local_Forensic_Register.json) · [Bounded consumer register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP370_W3_A_Formation_Double_Stop_Consumer_Boundaries.json) · [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP370_Completion.json).

Next A lines 337–591, B03-06.
