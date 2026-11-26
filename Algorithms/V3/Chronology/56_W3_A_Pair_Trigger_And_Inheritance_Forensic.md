# W3 B03-06 — A pair trigger, alignment and inheritance (CP371)

Pinned source: [A Zone lines 337–591](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L337-L591), blob `431934d2fb597238d5281a769c29fdb51747868b`. Local A13–A16, bounded native handoffs only.

## Ordered semantics

- **G1 / A13, L337–351:** Eight-field optional tuple signature, annotations not runtime validation.
- **G2 / A13, L352–358:** Previous exact stop required first, then main stop; nullable expiry comparison only when supplied; strictly later rejects, equality passes. No general requirement for current stop yet.
- **G3 / A13, L359–366:** Call virtual inheritance after previous-stop admission; nonnull result selects exclusive inherited branch. Unpack four values including inherited Reaction Break time, unused afterwards.
- **G4 / A13, L367–374:** Search inherited level starting at current formation through exclusive expiry, using A07. None returns immediately, no fallback to another route; ignore crossing extreme.
- **G5 / A13, L375–385:** Return inherited level/source, trigger main read from candle index, exact trigger, effective previous stop main equals level source time, effective current equals trigger main (timestamp reread). No equality assertion with actual stops.
- **G6 / A13, L386–393:** Without inherited tuple, previous exact stop strictly earlier than current formation selects early-stop route. Read current formation main open and call A08 from previous exact stop through open minus one microsecond inclusive. Same-main guard can pass while range reverses; A08 raises.
- **G7 / A13, L394–402:** Reread formation main open then add nominal timeframe; if expiry nonnull choose min(nominal end,expiry), else nominal end. No independent reversal guard.
- **G8 / A13, L403–412:** Search from exact current formation to exclusive computed endpoint; nonnull crossing gives trigger index/time, ignore returned extreme, read main timestamp once as effective stop.
- **G9 / A13, L413–423:** Return frozen continuation source, trigger and exact event, previous actual main stop and effective current main stop; current actual stop may be absent.
- **G10 / A13, L424–430:** Only after formation-window miss require current exact then main stop; expiry nonnull and current event > expiry rejects; equality permitted.
- **G11 / A13, L431–445:** Search frozen level from current exact stop through exclusive expiry, None terminal; return continuation, trigger main/time, exact event and both actual main stops. No recourse to two-stop sort.
- **G12 / A13, L446–453:** Remaining branch (previous stop >= current formation) repeats current exact/main and expiry gate before sort.
- **G13 / A13, L454–460:** Stable ascending sort of previous,current by actual exact stop time then stop_level for exact bearish else native unary minus. Unary minus obeys Decimal context, not copy_negate; key evaluated for each state even if times differ; equal full keys retain input order.
- **G14 / A13, L461–464:** Four assertions in source order: first event, second event, first event extreme, second event extreme nonnull. Subject to Python assertions enabled; second extreme required despite not used later.
- **G15 / A13, L465–468:** Convert first sorted stop index to int; freeze its exact stop event extreme and mapped main timestamp as continuation. No extra conversion or scan.
- **G16 / A13, L469–481:** Equal exact stop times yield direct second stop index, main timestamp, second exact event; no additional crossing, may equal expiry. Both effective stop mains remain original previous/current order, not sorted order.
- **G17 / A13, L482–495:** Distinct times search first strict crossing of first exact stop extreme from second exact event through expiry exclusive. None terminal; otherwise return trigger and frozen first-stop source, original previous/current actual main stops.
- **G18 / A14, L496–500:** Base delegate chronology.reaction_confirmation with explicit use_intrabar_start false. Native RE61 scans Break-open window, caches result or fallback; return unchanged, no independent exact-event proof.
- **G19 / A15, L501–511:** Capture local references to reactions, precomputed First times and confirmations. Optional not_before and start_position=0, no local normalization.
- **G20 / A15, L512–519:** Fast admission short-circuit: start>=0, ordered confirmations, exact datetime trigger, tzinfo None, then null not_before or ordered Firsts and exact naive bound. Break ordering flag not used here.
- **G21 / A15, L520–524:** Position=max(start_position,left-bisect confirmations at inclusive trigger); if bound present max with left-bisect Firsts. Return ordinal position+1 and original reaction if position<len, else None; no recheck of stale flag or arrays.
- **G22 / A15, L525–531:** Fallback native range from supplied start (negative not clamped), compare confirmation>=trigger first, then null bound or First>=bound. First qualifying returns number+1 and original reaction, possibly zero/negative ordinal for malformed starts. Exhaustion None; no sorting.
- **G23 / A16, L532–539:** Require previous formation strictly earlier than current; equality rejects before any stop/internal reads.
- **G24 / A16, L540–546:** Chain admission ordered conjunction: previous main stop nonnull, exact stop nonnull, exact stop strictly earlier than current formation, previous internal false, current internal false (default false). No check of current stop.
- **G25 / A16, L547–554:** Only if not chained string-convert previous kind; exact scale rejects, all other kinds remain eligible. Window starts previous actual stop MAIN time if chained, else previous formation; not exact stop event in chained case.
- **G26 / A16, L555–560:** Capture original Reaction and timestamp arrays, start=0. Only ordered Firsts with exact naive window start use right-bisect, excluding equality.
- **G27 / A16, L561–564:** Ordered-limit flag uses Break order and exact naive current formation independently of First optimization.
- **G28 / A16, L565–573:** Loop original positions; read both First and Break before gates. Skip First<=window_start before Break bound. Break>=current formation terminates only if ordered-limit, otherwise skip. Early termination conditional on eligible ordered data.
- **G29 / A16, L574–584:** First eligible Reaction supplies endpoint: chained full nominal Break interval ends at Break open+timeframe minus 1 microsecond, nonchained ends at Break open inclusive. No recheck that chained end precedes formation; full Break may extend beyond it.
- **G30 / A16, L585–591:** Call A08 with window_start and derived inclusive range end; propagate failure, no later candidate fallback. Return price, source main position/index/time and Break main time; no eligible reaction returns None.

## Reconciliation

614 canonical category rows (153 W1, 461 additional), 10 historical supplements from [B03-06](../../../Audit/Phase_07/Semantic_Closure_B03_06.json). All W1 identities/spans match CP314, disjoint from CP369–370. Preserve B03-06-F01–F03 and five open cross-owner findings. CP371-F01 qualifies active documentation. No runtime, RAW, ZIP or production changes.

[Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP371_W3_A_Pair_Trigger_Inheritance_Local_Forensic_Register.json) · [Bounded consumer register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP371_W3_A_Pair_Trigger_Inheritance_Consumer_Boundaries.json) · [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP371_Completion.json).

Next A lines 592–733, B03-07.
