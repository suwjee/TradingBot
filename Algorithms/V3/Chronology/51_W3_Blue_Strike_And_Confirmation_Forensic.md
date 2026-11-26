# W3 B03-01 — Blue strike and confirmation forensic review (CP366)

Pinned source: [Blue Line lines 1–232](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/blue_line_detector.py#L1-L232), blob `f25efc55bbc387c6a3a592ffe3ff87ee12cf6891`. Source-only local contracts BL01–BL06; no runtime or cross-owner acceptance.

## Ordered semantics

- **G1 / BL declarations, L1–24:** Module owns Blue strike/spacing and validity, not downstream A/S/E lifecycle. Imports and native bindings conditional; version constant is not a behavior gate; module constructs exact Decimal from string 0.618.
- **G2 / BL declarations, L25–31:** Frozen slotted ScaleStrike fields separate stored main index/time from extreme; annotations are not validators, no normalization or deep immutability implied.
- **G3 / BL declarations, L32–50:** Frozen slotted BlueLine separates direction/kind/ordinal/count/Fibonacci, semantic source identity and price, broken level and drawing geometry; valid defaults true, internal false independently. Type unions are annotation expressions, not trading math.
- **G4 / BL01, L51–54:** Read required tag, convert to string then uppercase; compare supplied color unchanged. Missing attribute or conversion error propagates; no recalculation from OHLC, no lower-prefix color.
- **G5 / BL02, L55–61:** Return original mapped value for supplied key. Catch only KeyError, raise ValueError with chained cause. No validation of returned value, no nearest fallback.
- **G6 / BL03, L62–68:** Signature declares sequence and integer boundaries but does not validate values.
- **G7 / BL03, L69–70:** Resolve direction first (native policy rejects others), then read and directly Decimal-convert source extreme; not Decimal(str).
- **G8 / BL03, L71–72:** Positional slice begins max(0,start), ends at end+1 with native slice semantics including negative end; no separate right clamp or ordered-index validation. Read selected Low/High, direct Decimal.
- **G9 / BL03, L73–77:** First strict penetration (B low<level, R high>level) terminates and only then converts stored candle index and compares to requested end. Earlier crossing yields false; exhaustion false; finite equality not crossing.
- **G10 / BL04, L78–80:** Validate policy before required edge access; choose branch by returned policy.direction.
- **G11 / BL04, L81–86:** B top minus ratio times (top-reference); R bottom plus ratio times (reference-bottom). Direct conversion of edge, supplied reference unchanged, preserve inner subtraction then multiplication then outer operation and Decimal context.
- **G12 / BL05, L87–96:** Inputs annotated, no local structural validation; policy resolved before chronology request.
- **G13 / BL05, L97–103:** Call default RE61 (native true, cached result or fallback allowed) before computing end=Break timestamp+timeframe; lower_bounds uses pending start through half-open nominal end, not automatically intrabar start. Slice original seconds; empty returns None before reading breakout edge.
- **G14 / BL05, L104–107:** Select required top B/bottom R by exact supplied direction, directly convert, fresh eligible list.
- **G15 / BL05, L108–110:** Traverse supplied lower slice order; first timestamp strictly later than returned confirmation breaks before price reads, equality included. Chronological ordering requires native ordered aligned arrays.
- **G16 / BL05, L111–118:** Read policy-selected extreme, direct Decimal; strict threshold penetration appends original lower row before confirmation check. No pending-price comparison here.
- **G17 / BL05, L119–124:** Compute confirmation predicate on every visited row after possible append, even if eligible empty. B high>top/R low<bottom; then crossing and eligible short circuit. Same row can satisfy both without proving within-row order.
- **G18 / BL05, L125–129:** First crossing with accumulated eligible evidence selects min Low B/max High R; each key directly converted, equal key keeps first traversed. Crossing may precede returned confirmation time or actual Break main if supplied window permits; no equality-to-confirmation requirement.
- **G19 / BL05, L130–134:** Read decisive lower timestamp, map with native main_index default unclamped, then lookup position as main-map key. None/missing map value raises; underflow may raise earlier; no check that mapped stored index equals position.
- **G20 / BL05, L135–144:** Construct strike with integer mapped stored index and mapped main timestamp, but directly converted decisive lower price. Exact lower time not stored in ScaleStrike. Return immediately; no eligible crossing returns None.
- **G21 / BL06, L145–153:** Compute Fibonacci first including policy validation, before map/range inspection. Return contract pair level and confirmed list.
- **G22 / BL06, L154–157:** Build map only if supplied is None, visiting chronology main order, integer index keys; duplicate stored index last wins. Supplied non-None map retained even empty; no copy or consistency check.
- **G23 / BL06, L158–164:** Convert First then Break; enumerate inclusive integer map keys, not direct list slice. Missing key raises during construction. Select confirming tag GREEN B/RED R; no separate color derivation.
- **G24 / BL06, L165–175:** Read final mapped main before RE61 default call; empty reversed range IndexError before call. Break prefix bounds from mapped final main timestamp to nominal end, retained rows <= returned time (including fallback open), not clipped at intrabar_start. RE61 itself indexes chronology.candles by position; map alignment is a caller obligation.
- **G25 / BL06, L176–184:** Only nonempty Break prefix reduces direct Decimal Low/High via min/max in source order; otherwise None, no full-main extreme fallback. Fresh confirmed list and null pending.
- **G26 / BL06, L185–190:** Iterate mapped main order. Threshold last confirmed extreme else Fibonacci; choose Break clipped extreme by integer stored index equality with Break, not loop position; other candles use direct main Low/High. Malformed supplied map can diverge.
- **G27 / BL06, L191–197:** Null extreme skips complete row, including possible color confirmation; otherwise compare strictly against last confirmed threshold, finite equality fails.
- **G28 / BL06, L198–210:** Threshold gate first; only if true test absent pending or strictly better directional extreme, equality retains old. Create pending with current mapped main integer stored index/time and selected extreme. No price rounding.
- **G29 / BL06, L211–215:** After possible replacement, pending nonnull then BL01 color; matching main tag appends pending and clears. Same main can create/confirm; Break price is clipped but main tag is not recalculated at cutoff. No lower color proof.
- **G30 / BL06, L216–226:** Only remaining pending invokes BL05, re-read last mapped main and latest confirmed threshold else level, use pending main source time (not exact lower time or pending extreme), Break main timestamp and existing map. Lower replay can replace pending provenance; no exact-time color check.
- **G31 / BL06, L227–232:** Append nonnull returned strike, otherwise discard unresolved pending at return. Return level and fresh ordered confirmed list; no source mutation by these local operations, but chronology cache may mutate and failures propagate.

## Reconciliation and remaining work

599 canonical category rows (170 W1, 429 additional), 8 historical supplements from [B03-01](../../../Audit/Phase_07/Semantic_Closure_B03_01.json); all 170 historical links match CP314 category, original identity and span. One synthetic filter. This coordinate census supplements the source-first contracts, not independent proof by overlap. CP350 S17/S18, E09/E10, G28 and lower-bound/position handoffs are retained. The source distinguishes main color, clipped lower extreme and actual exact confirmation; no exact-event or arbitrary-callback guarantee.

[Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP366_W3_Blue_Strike_Local_Forensic_Register.json) · [Bounded consumer register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP366_W3_Blue_Strike_Consumer_Boundaries.json) · [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP366_Completion.json).

CP366-F01 documentation qualification; preserve B03-01-F01–F04, all five open W3 findings and RE01–RE107. B03 local remains incomplete; next Blue lines 233–461 (B03-02). No RAW payload, project execution, ZIP or production changes.
