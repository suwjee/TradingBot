# W3 B03-02 — Blue builders, spacing and batch entry (CP367)

Pinned source: [Blue Line lines 233–461](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/blue_line_detector.py#L233-L461), blob `f25efc55bbc387c6a3a592ffe3ff87ee12cf6891`. Local BL07–BL10, bounded native handoffs only.

## Ordered semantics

- **G1 / BL07, L233–243:** Builder signature annotations do not validate inputs or direction; native tail owns admission. No local public/validity filter.
- **G2 / BL07, L244–247:** Last strike by negative index; empty sequence fails before map read. Look up decisive stored source_index then convert mapped main High and Low in that order directly to Decimal. No source timestamp/index consistency assertion.
- **G3 / BL07, L248–252:** Exact bullish branch computes Low+(High-Low)/Decimal(3), otherwise High-(High-Low)/Decimal(3); preserve subtraction/division/addition order and context, full main range, no quantization or policy validation.
- **G4 / BL07, L253–263:** Construct scale record using supplied direction, ordinal, prior count, count of confirmed strikes, supplied Fibonacci, decisive strike stored index/time/extreme; broken_level null. Semantic source price not drawing price or full-main extreme.
- **G5 / BL07, L264–270:** Drawing price plus start/end independently computed from decisive strike time minus/plus chronology.timeframe, not mapped candle time. Pass internal flag unchanged, default calculation_valid true; return only after successful field evaluation.
- **G6 / BL08, L271–281:** Reset builder accepts previous line nullable, no direct kind/owner/direction validation; BL03 validates direction only when reached.
- **G7 / BL08, L282–291:** Read reset.index then int, lookup that key, convert main High then Low, compute divisor-five exact mirrored drawing before reading mapped main timestamp. No reset event timestamp consumed.
- **G8 / BL08, L292–300:** Validity is negated conjunction; previous nonnull first, then BL03 from int(previous source_index)+1 to reset_index inclusive. Positional first strict crossing and stored index check, not exact lower stop. If prior absent no stop scan or direction validation here.
- **G9 / BL08, L301–306:** Only if prior exists and BL03 true evaluate strict extension of full reset main extreme versus directly converted prior semantic extreme (B low<, R high>). Finite equality cannot invalidate; no previous calculation_valid/internal check.
- **G10 / BL08, L307–316:** Always construct Reset record if no failure, even invalid. Counts/Fibonacci null, source_index is converted reset.index map key (not read from mapped candle), source_time mapped main timestamp, source_extreme main Low/High.
- **G11 / BL08, L317–324:** Read and direct Decimal-convert broken_level after validity derivation, retain distinct drawing price, main time ± timeframe, calculated validity and supplied internal. Malformed required fields can fail even for invalid record; no public filtering.
- **G12 / BL checkpoint, L325–332:** Frozen slotted checkpoint defaults previous reaction/count null, spacing and line_count zero. Shallow reference storage; annotations no validators, not independent snapshot of nested state.
- **G13 / BL09, L333–343:** Tail accepts caller output and optional checkpoint list; no start, direction, prefix length, or map-alignment guard inside this helper; native wrappers gate admission.
- **G14 / BL09, L344–347:** Read chronology main list, map stored int index to original object in traversal order; later duplicate key overwrites, map is new but values shared.
- **G15 / BL09, L348–353:** Fresh reset grouping keyed by int(from_first_idx) preserving input iteration order, append original reset refs. No sort, dedup, direction or lifecycle filter.
- **G16 / BL09, L354–358:** Restore previous reaction/count and counter from checkpoint, derive has_blue from caller output truthiness rather than checkpoint.line_count. Invalid/internal count as output. No consistency check.
- **G17 / BL09, L359–360:** Truthy start slices reactions, falsy uses original sequence; enumerate start+1 even if direct helper called with unusual start. Input order controls ordinals.
- **G18 / BL09, L361–362:** Read internal bool default false before converting required mode to string and comparing exact A. Flag is record metadata, not an admission or spacing gate.
- **G19 / BL09, L363–371:** Mode A prefers nonnull anchor, else nonnull leg_boundary; zero retained; missing both raises. Direct Decimal reference conversion before clearing previous_count, no spacing reset.
- **G20 / BL09, L372–383:** All other modes require previous reaction else raise; choose prior box_bottom B/box_top otherwise, direct Decimal. Not a separate mode-B validator.
- **G21 / BL09, L384–390:** Call BL06 with current reaction, direction, chronology, reference and shared map; confirmation cache can change before any output append. Failure propagates.
- **G22 / BL09, L391–397:** Scale candidate only previous_count nonnull then len(strikes)>previous_count; strict count increase. Initialize scale_emitted false. Candidate required before (no Blue or counter>=1).
- **G23 / BL09, L398–412:** Build Scale then append to caller output before setting has_blue, spacing zero, emitted true. Builder or append failure prevents subsequent local state updates; no transaction.
- **G24 / BL09, L414–416:** If has_blue and not scale_emitted increment counter once, including internal reactions; name healthy is not a predicate. Increment precedes reset scan.
- **G25 / BL09, L417–421:** Read current int First to lookup reset group with empty-list default. Each reset skipped when has_blue and counter<1. No event-time sorting or kind check here.
- **G26 / BL09, L422–435:** Pass latest output line (regardless of validity/internal) or null to BL08. Append returned Reset even invalid, then set has_blue true and counter zero; thus same-group subsequent Reset suppressed. Scale also suppresses same-Reaction Reset.
- **G27 / BL09, L437–442:** After all matching resets, set previous reaction to original ref then count len(strikes); if checkpoint list not None, evaluate shallow copy then count/counter/len(output), build checkpoint then append. Copy/checkpoint failure can leave completed output changes; no local rollback.
- **G28 / BL09, L443–446:** Return exact caller-owned output object, no sorting, copying, or public visibility projection. Checkpoint.line_count records prefix length only.
- **G29 / BL10, L447–455:** Public batch detector defaults resets empty tuple, checks direction membership exact supported strings before allocating calculation state. Other malformed values can raise natively.
- **G30 / BL10, L456–461:** Delegate to BL09 with start 0, fresh default checkpoint and fresh output, no checkpoint capture. Return full calculation ledger including invalid/internal; no lifecycle acceptance or public projection.

## Reconciliation

494 canonical category rows (138 W1, 356 additional), 8 historical supplements from [B03-02](../../../Audit/Phase_07/Semantic_Closure_B03_02.json). CP314 crosswalk identity and source spans matched; no duplicate or prior CP366 row. Source-first contracts, not overlap alone. A can consume invalid lines through its separate double-stop route; public projection is separate. CP367-F01 documentation qualification. Preserve five open W3 findings and all historical evidence.

[Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP367_W3_Blue_Builders_Spacing_Local_Forensic_Register.json) · [Bounded consumer register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP367_W3_Blue_Builders_Spacing_Consumer_Boundaries.json) · [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP367_Completion.json).

Next lines 462–591, historical B03-03. No RAW payload, project execution, ZIP or production changes.
