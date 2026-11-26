# CP342 — W2 Bridge serialization and chronology queue reconciliation

Pinned source `c99b4c957e932d9ee70c492ca03ce80711447fc1`, blob `e1e65ba960c5f726f9a05e2ab89e4457b65e5735`. W2 NOT_ACCEPTED. 19 direct records, 3 CP322 accessors. Native confirmation is not the same as proof of the returned timestamp.

## CP323-S25 — TB22–24

Selection uses raw reset index and raw Reaction First; either bound null bypasses int conversion, both inclusive. Transform invoked only for selected raw Reaction if non-null, raw/public pair retained; resets first, then reactions in encounter order. Supplied non-null selected_items bypasses selection and transform including empty tuple. Legacy uses public geometry and mode, reset display/optional second time, prices native strings.

Handoff: No detection or validity re-evaluation; nested projector uses raw proof and public geometry from same pair.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L374-L438). B09 overlap occurrences: 28.

## CP329-S01 — TB25

Filter before field conversions by source index inclusive only when both bounds exist. Preserve direction/kind, original reaction ordinal, strike counts, line and source extreme strings, optional Fibonacci/broken levels via exact None guard; main start/end epochs.

Handoff: No Blue stop-event reconstruction; additive path passes preselected list with absent bounds.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L441-L458). B09 overlap occurrences: 15.

## CP329-S02 — TB26

Emit all supplied A in order, two Blue ordinals, source/stop main times/levels, continuation source/level, trigger main/exact, Reaction First/Break main, source price string. calculationValid constant true; no exact Blue stop event fields or local validity gate.

Handoff: A eligibility belongs to preceding lifecycle/range, not this field.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L461-L485). B09 overlap occurrences: 15.

## CP329-S03 — TB27

Required A stop main/exact fields and source/decision epochs, optional Order geometry/time/price and Reset time use explicit None guards, preserving zero. Index/ordinal fields passed as stored. No causes fields in legacy S. Constant calculationValid=true.

Handoff: Optional Order is not necessarily a native accepted identity; upstream final audit invariant validates physical pair only if both present.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L488-L550). B09 overlap occurrences: 39.

## CP329-S04 — TB28

Parent type/source/price/stop fields required; Order cause tuple materialized as list (no null fallback), optional parent cause event separate, remaining Order geometry/timestamps required and string/epoch conversion, own source and decision fields. No calculationValid.

Handoff: E creation vs consumption provenance preserved; serializer does not validate ledger cause.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L553-L594). B09 overlap occurrences: 22.

## CP329-S05 — TB29

Gate event/type, stopped owner key/count, underlying E distinct from source/decision and own stop. Order causes list required; optional geometry/time uses None guards. Own stopTime/EventTime uses truthiness only. Donor metadata intentionally omitted from legacy.

Handoff: StopAll parent/donor not interchangeable with stopped group; nested view has separate donor fields.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L596-L660). B09 overlap occurrences: 41.

## CP329-S06 — TB30–33

None or non-datetime/non-string -> null; string unchanged, datetime components formatted to seconds without timezone conversion or microseconds. Direction str().title(); mode exact string A/B only; color membership None/empty (not general falsiness), else title-case.

Handoff: Presentation formatting not validation or price normalization.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L663-L688). B09 overlap occurrences: 21.

## CP329-S10 — TB41–42 / CP322-E02

Null prepared or First/Break outside full main bounds returns null. Both indices int-converted; crossed if nonnull indexed for main/exact stop; call bridge proof with physical order direction/default true. Main First/Break rendered even outside display start; exact confirmation proof has only exclusive upper horizon. Formation Order uses recorded int pair and final audit map, no fallback identity.

Handoff: Order direction physical not conceptual owner. Native provider may return Break-open fallback; proof may accept that time if exact equal-time row independently crosses even when it was outside native scan start. Does not prove native firstness.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L821-L871). B09 overlap occurrences: 36.

## CP329-S11 — TB43

Require supplied strict_stop_event and source_time nonnull. Iterate final identity map; parent-stop exact type/source/event then family (requested None accepts None or empty). Reset-leg exact post type or E/StopAll base case-sensitive prefix (not numeric parser), exact post source/stop, no family constraint. Unknown skip; repeated matching causes same identity count once; exactly one physical match projects, conflict/absent null.

Handoff: Current Order is creator-cause projection, not formation Order or selection by chronology/nearest geometry. Caller proves actual behavior stop; helper itself trusts argument and formatter may return null.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L873-L926). B09 overlap occurrences: 54.

## CP329-S12 — TB44

Require physical formatter nonnull else RuntimeError before cause iteration. Parent-stop required keys, family display color and recorded cause times. Reset-leg maps datetime instances only, other values unchanged; unknown kinds skipped. Box missing timestamp null, missing price string 'None'. Stop source distinct from hit time/proof.

Handoff: Audit view projects accepted causes; cause event formatting is not independently horizon/proof-filtered. No new physical identity.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L928-L985). B09 overlap occurrences: 36.

## CP329-S14 — TB48–49 / CP322-E03/E04

Non-scale -> source time and null event. Scale int one-based ordinal and full Break bounds; explicit intrabar false; conversion errors outside proof guard. Public Reaction uses raw First/Break directly (no local bounds guard, negative indexing native), raw candle tag/time and proof with default true; public object supplies mode and box geometry only.

Handoff: Exact proof is against native raw level/time, not public clipped level; native search start differs for Scale versus Reaction; proof may be null while main remains.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1045-L1108). B09 overlap occurrences: 48.

## CP329-S15 — TB50–51

Reset previous First bounds only; occurrence display and second time read as recorded, no crossing verification. Blue normalized scale/reset mapping, line/source extreme strings, formation helper; standalone stop main and event always null, price sourceExtreme, brokenLevel only reset.

Handoff: No standalone Blue stop evidence retained; no synthetic second detector. Reset display provenance not same as strict Order_B Reset recovery.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1111-L1167). B09 overlap occurrences: 33.

## CP329-S18 — TB54

Call existing E parent_stop('S',item) adapter, then exact strict proof. Only lowercased blue gets Type1–4 map; display color formatted independently, current cause family original str(color). Parent A uses recorded source/price/stop and physical formation Order; own stop and current Order separate.

Handoff: Adapter can execute native stop search; read-only projection is not zero computation. Parent main stop visible independently of exact proof.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1272-L1325). B09 overlap occurrences: 34.

## CP329-S19 — TB55–56

Source index/time both read before exact null guard, int index without bounds; exact stored parent type chooses S/E/StopAll map with physical pair. S contributes color; E color/number; StopAll number; unknown/missing retains null metadata. FormedAt and stoppedAt always from E's recorded parent data.

Handoff: No temporal-nearest join; nested historical reference not independent public record.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1328-L1377). B09 overlap occurrences: 36.

## CP329-S20 — TB57

E stop adapter then proof, type/direction/formatted family and int number, recorded source; parent exact type/source pair and formation Order independent; current exact E<number> and original str(family) with proven own stop. Own main/event proof separate.

Handoff: No mutation or reconstruction of native E ledger; callback may query existing detector.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1380-L1424). B09 overlap occurrences: 22.

## CP329-S21 — TB58

Map gate labels to Type1/2/3 exact. Donor type/color/number/source time and optional price from retained metadata, donor stop independently via proof; no substitution of gate event. Own strict event proof used for current StopAll<number>, family None. Formation Order from physical pair; own stop separate.

Handoff: CP339 corrected S donor cause contract; projection does not promote or create StopAll.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1427-L1493). B09 overlap occurrences: 33.

## CP329-S22 — TB59

Use detector main candle times of int First and Break as epoch pair; direct indexing no bounds check. Stable sort caller; exact confirmation/cause/stop not sort key.

Handoff: Physical identity and presentation order distinct.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1496-L1503). B09 overlap occurrences: 6.

## CP329-S23 — TB60

Use E detector order_direction if nonnull else exact bullish opposite fallback. Audit map last duplicate physical pair; full Blue dictionary fallback only absent key, sorted ordinal. Projection attrs fallback only missing (not empty/null); S full alone, E/StopAll full then selected override. Pair computed once, absent skipped; raw full reactions. Eight arrays fresh, exactly selected order; error propagates, no local shortened list.

Handoff: Nested full references do not republish out-of-range parents; final selected audit may not contain all internal creation history.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1506-L1608). B09 overlap occurrences: 46.

## CP329-S25 — TB62

Legacy accepted audit only prepared records; parent-stop required family raw and epoch times, reset-leg datetime-only conversion, unknown omitted. Truthy behavior_public_number overrides native ordinal before int; First/Break main from detector candles, box source times display_epoch; stop price string and crossed triple exact nonnull guards. Stable sort First/Break epoch.

Handoff: Legacy stopHit fields not proof/horizon-revalidated here; nested proof is distinct, no new filtering or ranking.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1679-L1729). B09 overlap occurrences: 52.

## Accessors

- **CP322-E02**: Physical Order First/Break bounds full main, native physical direction default true. Native confirmation cache key includes direction/flag/First/Break/box strings/intrabar start. Native first strict scan or Break-open fallback; bridge independently proves only returned timestamp, opposite strict stop predicate, exclusive upper view horizon; no lower horizon or recheck native start.
- **CP322-E03**: Scale Blue int ordinal 1..len and bounded Break; false intrabar starts at Break open; non-scale returns source time/null without proof. Native fallback may fail strict proof. Main time separate. No clipped public price.
- **CP322-E04**: Raw First/Break and raw candidate with default true; public geometry and mode separate. Direct candle indexing outside proof catch; native fallback can be accepted by equal-time proof if excluded native start, not a proof of native firstness.

## Findings

- CP342-F01: TB38 wording could imply native fallback is categorically excluded from proof. Native resolver may return open; proof validates that timestamp alone. With later intrabar start, open may satisfy strict predicate although outside native scan. No substitute event or firstness proof. This is a source-derived conditional case, not an observed RAW result.
- CP342-F02: Read-only projection may invoke native stop lookup; no new detector or cause creation, not zero search execution. Legacy fields and nested proof have different guards.
- CP342-F03: 9 Bridge and 2 Live queue records remain; accessor coverage complete by linked/reviewed ID, not W2 acceptance. F05/R01/R02 open.

CP343 / W2 Trading Pipeline orchestration, horizon and Primary projection: 9 remaining Bridge queue records (CP323-P27, CP323-S32, CP329-S26/S27/S28/S29/S30/S31/S32), then 2 Live records. All three remaining accessor sites reviewed; F05 and CP333-R01/R02 remain OPEN, W2 not accepted.
