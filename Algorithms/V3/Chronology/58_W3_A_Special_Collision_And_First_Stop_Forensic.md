# W3 B03-08 — A special collision and first stop (CP373)

Pinned [source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L734-L847), blob 431934d2fb597238d5281a769c29fdb51747868b.

- G1 / A19 L734–739: Inputs special and ordinary lists; no ownership mutation or external acceptance at entry.
- G2 / A19 L740–744: Set of ordinary reaction_number only if nonnull, reads field twice for included rows; native hash/equality, not integer coercion.
- G3 / A19 L745–750: New special list preserves input order and references; exclude members of ordinary number set; null ordinary excluded from set.
- G4 / A19 L751–757: For each surviving special, collect strictly earlier ordinary source_time from original ordinary list, excluding equal source. Fresh list per special.
- G5 / A19 L758–762: Max by source_time, first equal maximum in iteration order, null default.
- G6 / A19 L763–770: Only if prior nonnull call virtual A22 with exclusive special First end and Blue1 source not_before; true discards special. No alternate prior, no recross. Preserve survivors.
- G7 / A19 L772–781: Materialize all surviving special integer ordinal sets and exact trigger events before filtering ordinary. Duplicate ordinals collapse within set; no per-special acceptance mutation.
- G8 / A19 L782–786: If no consumed_special leave ordinary list reference unchanged; else construct fresh ordinary list, any short-circuits.
- G9 / A19 L787–795: For each ordinary and each surviving special evaluate strict later trigger first; only then integer-convert both ordinary ordinals and intersect. Truthy intersection removes ordinary. Equal trigger alone cannot remove. No special-vs-special resolution.
- G10 / A19 L796–797: Return ordinary and special list references; original zone records unmodified locally; provider calls may change caches.
- G11 / A20 L798–804: Build valid states then ordinary list; generate special candidates only after ordinary succeeds. Resolve collision once via virtual A19; failure propagates.
- G12 / A20 L805–809: Concatenate ordinary then special, stable ascending sort source_time then exact trigger_event_time. Equal keys retain ordinary before special and original within-list order. No public visibility/lifecycle gate.
- G13 / A21 L810–812: Forward kwargs directly to AZone constructor, no normalization or validation beyond native constructor; live override may reuse records.
- G14 / A22 L813–825: First-stop cycle test uses supplied end and optional not_before; not a universal stop query. Docstring rejects later recross as new cycle.
- G15 / A22 L826–828: Read candles[zone.source_index].index, int then plus one, not source_index+1; if >= len return false, no lower bound check, negative indexing remains native.
- G16 / A22 L829–833: Read zone.price then start candle timestamp, invoke virtual A07 from next stored-index position to exclusive end. Lower/main fallback contract A07 applies.
- G17 / A22 L834–837: Null first hit false; otherwise not_before null short-circuits, else exact event>=bound. First hit before bound false, no second search.
- G18 / A23 L838–847: Construct base detector and immediately call detect, no persistent A history at helper; underlying chronology/index provider can retain cache.

237 canonical rows, 59 W1, 178 additional, six historical supplements. CP373-F01 documentation resolved. Six prior cross-owner findings remain OPEN. No runtime or lifecycle acceptance.

[Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP373_W3_A_Special_Collision_Local_Forensic_Register.json) · [Consumer boundaries](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP373_W3_A_Special_Collision_Consumer_Boundaries.json) · [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP373_Completion.json).
