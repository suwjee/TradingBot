# CP334 — W2 Blue/A queue reconciliation

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`. Re-review of 12 existing transition IDs and two accessor sites; no duplicate transitions. W2 remains open.

## CP323-S17 — BL01–BL04

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/blue_line_detector.py#L33-L85) · [Owner specification](../03_Blue_Line.md)

Validity and behavior_internal are independent flags. Tag uppercasing does not recompute price color; missing mapped index raises. Direction policy strict stop first hit across positional inclusive slice must own reset index; equality does not stop. Decimal direct conversion and Fibonacci arithmetic retained.

Handoff: A consumes semantic source_extreme; drawing formula not stop level.

## CP323-S18 — BL05–BL06

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/blue_line_detector.py#L87-L230) · [Owner specification](../03_Blue_Line.md)

Default native confirmation called at both 97 and 168; cap lower evidence by <= returned confirmation even if fallback open. Skip entire Break row if missing prefix; pending may confirm on main color. Lower pending rescue scans from pending main source, penetration added before same-row break, first qualifying crossing picks directional extreme with first input tie, maps via main_index and raises if missing.

Handoff: Reaction confirmation provider, A false-flag route and Bridge public proof have different semantics; no inference from full Break OHLC.

## CP323-P12 — BL07

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/blue_line_detector.py#L233-L268) · [Owner specification](../03_Blue_Line.md)

Last confirmed strike required. Drawing uses main High/Low and Decimal divisor 3 with directional arithmetic order; source extreme retains lower strike price and main source time; ± timeframe is drawing interval, not validity duration.

Handoff: A stop uses source_extreme, not drawing price or interval.

## CP323-P13 — BL08

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/blue_line_detector.py#L271-L323) · [Owner specification](../03_Blue_Line.md)

Reset source index maps full main candle; divisor 5. Invalid iff previous output exists and its first strict main stop after its source is on this Reset index and Reset extends strictly past its semantic extreme. Previous validity/internal flags not tested. Emits invalid record; broken_level distinct.

Handoff: A ordinary state excludes invalid; double-stop route still consumes invalid record.

## CP323-P14 — BL09

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/blue_line_detector.py#L325-L444) · [Owner specification](../03_Blue_Line.md)

Mode A resets prior strike count only, requires anchor or leg boundary; other mode requires previous Reaction. Scale strict count increase with spacing; if output exists and scale not emitted counter increments regardless of behavior_internal, calculation-validity of prior Blue or Reset presence. Reset group original order; emit resets spacing, at most one Blue per input ordinal. Output and checkpoint lists caller-owned, partial mutation possible on exception.

Handoff: A retains full Blue ordinals; S/Bridge must not use public filtered ordinals; optional live checkpoint reuse conditional.

## CP323-S21 — A07–A08

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L129-L214) · [Owner specification](../04_A_Zone.md)

Strict crossing lower [start,end), indexed/linear; nonempty miss never coarse fallback. Empty lower scans main starts within bounds. Inclusive extreme adds one microsecond, rejects reversed range, earliest equal input owner. Empty lower uses entire containing main candles; lower returns mapped position, coarse crossing returns candle.index.

Handoff: Native lower index versus linear/coarse owner and exact event proof distinct; no universal intrabar freeze.

## CP323-P16 — A09–A11

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L216-L272) · [Owner specification](../04_A_Zone.md)

Validate Blue reaction ordinal before kind branch; scale uses A confirmation false flag and begins stop at returned exact/fallback value. Other kind independently scans strict broken level in source main and falls back open; stop starts source open+TF. Ordinary state retains original sorted ordinal, skips invalid, records main and exact stop separately.

Handoff: Default Blue/S confirmation not substituted for A false flag; reset display provenance not substituted for strict scan.

## CP323-P17 — A12

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L274-L307) · [Owner specification](../04_A_Zone.md)

Track last valid predecessor; invalid without predecessor ignored. Search strict predecessor threshold from invalid line source_time to actual source main end; crossing must map to invalid source index. Choose first eligible Reaction with confirmation >= trigger and First >= formation. Failure preserves predecessor.

Handoff: Special route depends on invalid Blue retained by producer; next row CP323-S22 completes prior partial output.

## CP323-S22 — A12

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L308-L335) · [Owner specification](../04_A_Zone.md)

Double-stop emitted both effective main stop times equal invalid source main; prior semantic source level becomes continuation. Exact Blue stop event fields remain default null, not inferred from trigger; output route double-stop. Clear predecessor only after successful append; invalid kind not checked.

Handoff: Bridge projection may not promote missing per-Blue exact stop evidence; preserve source and trigger separately.

## CP323-S23 — A13

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L337-L496) · [Owner specification](../04_A_Zone.md)

Require previous exact/main stop; >expiry rejects (equality allowed). Inherited route failure terminal; other route previous stop<formation scans extreme through formation MAIN open minus 1us (may raise reversed), first crossing in formation remainder else actual current stop. Otherwise sort exact event then higher stop level B/lower R using unary minus B; stable tie. Equal exact times trigger directly at second, can equal expiry; distinct use strict cross from second stop to exclusive expiry.

Handoff: Different event and effective main stop representations, trigger not a universal new crossing; A source freeze downstream uses trigger index.

## CP323-P19 — A16–A17

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L533-L611) · [Owner specification](../04_A_Zone.md)

Previous formation strictly earlier. Chain only earlier actual stop and neither internal; unchained Scale excluded, other kind allowed. First strictly after window start, Break strictly before next formation, first native list position; bisect only exact naive ordered guards. Chained uses complete Break, unchained Break open inclusive. A source from trigger MAIN open to returned false-flag confirmation inclusive; reversed returns null.

Handoff: S native default confirmation and A source selection are different; no semantic rounding or post-confirmation lower evidence in nonempty range.

## CP323-P20 — A18

[Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L613-L730) · [Owner specification](../04_A_Zone.md)

Adjacent valid states, third formation expiry. Trigger failure advances, no aligned match breaks, missing source advances. Match confirmation>=trigger, First>=max effective stop mains. Exact stop fields only if original stored main equals effective main, else null; not proof of cause equivalence. After output, cycle frontier Break; adjacent reuse if first strict A stop exists and next formation>=stop; else skip through cycle. Actual increment in while body at 731 lies outside historical row, explicitly linked.

Handoff: Conditional progress under coherent native chronology as CP323 Q2; downstream eligible A and display hiding distinct.

## Accessor review

- CP322-E09, [source line 97](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/blue_line_detector.py#L97): Default flag, returned time bounds pending rescue; inclusive confirmation; strict observed confirmation crossing still required to emit.
- CP322-E10, [source line 168](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/blue_line_detector.py#L168): Default flag, returned time bounds Break lower prefix; missing prefix skips Break entirely; fallback open can retain equal timestamp lower rows.

## Findings and closure boundary

- CP334-F01: Blue spacing name healthy_since_blue is not a predicate that filters internal or invalid-related inputs. Detailed BL09 already accurate; preserve exact counter meaning in supplement.
- CP334-F02: CH13 historical Break-open confirmation wording already qualified in CP323 Q3; active A-M01/A14 accurate. Add direct route distinction and exact fallback without rewriting historical clause.
- CP334-F03: CP323-P20 stops at 730 before actual increment 731. Add 731–732 explicit link; not a duplicate transition or new production error.

CP323-P20 additionally links [731–732](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L731-L732). Original records and historical chronology are immutable. The detailed owner specifications already distinguish the qualified behavior; this supplement makes the actual route explicit. No runtime or RAW payload. 12/185 queue items and 2/9 remaining accessor items reviewed.

[Evidence](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP334_W2_Blue_A_Queue_Reconciliation.json).
