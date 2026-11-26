# W3 B03-03 — Blue continuation, visibility and local union (CP368)

Pinned source: [Blue Line lines 462–590](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/blue_line_detector.py#L462-L590), terminal blank 591, blob `f25efc55bbc387c6a3a592ffe3ff87ee12cf6891`. Local BL11–BL18 and exact Blue local union only.

## Ordered semantics

- **G1 / BL11, L462–473:** Class docstring describes caller-supplied event and market frontier; not proof of actual caller integration. Constructor accepts resets default empty tuple.
- **G2 / BL11, L474–477:** Exact direction membership guard before storing direction and fresh one-element default checkpoint list.
- **G3 / BL11, L478–482:** Run BL09 from zero using stored initial checkpoint and fresh output, append to stored checkpoint list. _lines assigned only after tail success; constructor failure can leave partially initialized object if externally retained.
- **G4 / BL12, L483–486:** Return new shallow list via copy, preserve Blue object identity and order; not recalculation or deep snapshot.
- **G5 / BL13, L487–490:** Accept revised reaction/reset/chronology and required first_changed; optional first_dirty_main null; no separate type validation.
- **G6 / BL13, L491–492:** Validate chained 0<=first_changed<len(checkpoints), then if valid compare first_changed>len(reactions); equality with reaction count accepted. First failure short-circuits later checks; no automatic recovery.
- **G7 / BL13, L493–497:** Dirty main not None enables set construction from revised resets only. For each reset read/convert index for >= dirty before owner First access; equality included. Duplicate owner keys collapse; removed resets invisible.
- **G8 / BL13, L498–503:** Scan revised reaction positions zero to original first_changed exclusive; Break int>=dirty first, only false evaluates First membership in affected reset owner set. Rewind to earliest encountered qualifying position then break.
- **G9 / BL13, L504–506:** Select old checkpoint at final frontier; shallow slice retained checkpoint prefix inclusive and line prefix through stored line_count exclusive. No consistency check between line_count, reaction equality, source freshness or dirty index.
- **G10 / BL13, L507–511:** Replay only when revised suffix exists; local slices passed to BL09, retained references shared. Empty suffix truncates without reading chronology through tail. Tail failure leaves stored lists un-replaced, but no guarantee for referenced objects or external chronology cache.
- **G11 / BL13, L512–516:** Assign checkpoint list then line list, then return result property (new shallow copy). Failure in result copy is after publication; no rollback. Stored prefix object aliases are not isolated from later internal marking.
- **G12 / BL14, L517–525:** Fresh list comprehension visits input in order, reads truthy calculation_valid default true, only if true reads behavior_internal default false and negates. Invalid short-circuits internal lookup. Original refs; no mutation, sorting or ordinal reassignment.
- **G13 / BL15, L526–539:** Accept full line/owner/behavior sequences; local interiors None and indexed false per invocation. Docstring healthy description is not additional runtime predicate.
- **G14 / BL16, L541–545:** Fresh windows list; iterate supplied behavior reactions, read optional First then confirmation with null defaults; both fetched before guard.
- **G15 / BL16, L546–550:** Missing either time skips candidate; otherwise exact datetime and tzinfo None required for both, short-circuit in source order. Any nonexact/aware time returns None and discards earlier windows for this index build.
- **G16 / BL16, L551–553:** Append original payload ref with time pair; construct index even empty. No sort/health/first<=confirmation validation; native core index splits on decreasing start or end and preserves traversal order.
- **G17 / BL17, L554–556:** Get reaction_number default zero, falsy becomes zero, convert int then guard <1 or >len(owner_reactions); upper bound read only if first false.
- **G18 / BL17, L557–559:** Outside range false; otherwise owner ordinal minus one, read optional internal flag default false and truthiness. Not physical First/Break identity.
- **G19 / BL18, L560–566:** Read source time, rendered price, semantic extreme before testing nulls in order. Any None returns false before Decimal or index creation. Existing true line flag does not bypass this test when owner false.
- **G20 / BL18, L567–568:** Convert rendered via Decimal(str) first, then semantic via Decimal(str), unlike direct Decimal in BL03–BL08. Failures propagate.
- **G21 / BL18, L569–571:** If not indexed, call index builder, assign returned index or None, then set indexed true. Builder exception occurs before indexed update; successful None disables future builds in this call.
- **G22 / BL18, L572–574:** Default candidate sequence all supplied reactions. Only index present AND exact naive source datetime use enclosing(source_time,source_time). Index built before source datetime type check. Query native strict-start inclusive-end candidates in run order.
- **G23 / BL18, L575–581:** Iterate candidate sequence in returned order; fetch both optional times again, skip missing then source<=First or source>confirmation. Thus strict start and inclusive confirmation; indexed candidate recheck is not freshness proof for omitted candidates.
- **G24 / BL18, L582–583:** For time-eligible candidate read required public bottom then top, string-convert then Decimal each; missing/malformed required bounds raise, no skip or normalization.
- **G25 / BL18, L584–587:** Require both prices strictly within same candidate box; semantic chained comparison first, then rendered only if semantic passes; equal boundaries excluded. First success true, exhaustion false; no explicit direction, validity or health gate.
- **G26 / BL15, L588–591:** Visit original lines in input order; owner ordinal test first, geometry only if false. On either true force original behavior_internal=True despite frozen dataclass. Never clear flag; existing true not a skip gate. Invalid lines also eligible; earlier mutations survive later failure, alias effects can reach retained lists.

## Reconciliation

431 canonical category rows (129 W1, 302 additional), 8 supplements from [B03-03](../../../Audit/Phase_07/Semantic_Closure_B03_03.json), two synthetic filters. Prior CP366–367 plus CP368 form exact disjoint local union: 1524/1524 category rows, 437/437 W1, 1087/1087 additional, 24 historical supplements. All row coordinates, operations and W1 identity links match canonical source-indexed records. This is scoped local semantic review plus exact accounting, not cross-owner acceptance or runtime proof.

[Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP368_W3_Blue_Continuation_Visibility_Local_Forensic_Register.json) · [Bounded consumer register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP368_W3_Blue_Continuation_Visibility_Consumer_Boundaries.json) · [Exact union](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP368_W3_Blue_Local_Exact_Union_Verification.json) · [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP368_Completion.json).

CP368-F01 documentation qualification. Preserve B03-03-F01/F02 and all prior evidence; five W3 findings open. Next A Zone B03-04 lines 1–215. No RAW payload, project execution, ZIP or production changes.
