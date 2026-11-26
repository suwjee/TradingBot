# CP329 — W2 projection, serialization and T/F

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`. 243 prior rows retained, 40 new scoped transitions. No runtime or RAW execution.

## CP329-S01 — Legacy Blue

Source: `engine/bridge/trading_pipeline.py:441–458`.

Serialize selected Blue by inclusive source index when bounds supplied; retain order, ordinal and strike counts, explicit nullable Fibonacci/broken level, source extreme/line price strings, main start/end epochs.

## CP329-S02 — Legacy A

Source: `engine/bridge/trading_pipeline.py:461–485`.

All supplied A in input order; Blue pair ordinals/source/stop main times and levels, continuation and trigger main/exact, Reaction First/Break main times, source price string; calculationValid true, no new validity check. Exact Blue stop events not legacy fields.

## CP329-S03 — Legacy S

Source: `engine/bridge/trading_pipeline.py:488–550`.

Serialize color/type, A parent/source/stop triple, optional Order First/Break/confirmation/box/stop-source fields with explicit nullable guards, optional Reset identity/time, source/decision exact/main; price strings, calculationValid true. No reconstruction.

## CP329-S04 — Legacy E

Source: `engine/bridge/trading_pipeline.py:553–594`.

Required parent, Order geometry, source/decision fields; causes list and optional parent cause event, prices strings. No separate calculationValid field or filtering.

## CP329-S05 — Legacy StopAll

Source: `engine/bridge/trading_pipeline.py:596–660`.

Serialize number/source/decision, gate exact event/stopped owner and underlying E, nullable Order fields and own stop triple. Gate not actual stop; donor metadata omitted in legacy. Stop time truthiness guard. Preserve causes and prices.

## CP329-S06 — Display conversions

Source: `engine/bridge/trading_pipeline.py:663–688`.

Bridge timestamp: None->null, strings unchanged, datetime components formatted to seconds without timezone conversion, other type null. Direction title-case string; exact mode A/B map; color None/empty->null else title-case. No Decimal rounding.

## CP329-S07 — Horizon and exact proof

Source: `engine/bridge/trading_pipeline.py:691–739`.

Horizon last visible main timestamp+timeframe; event must be nonnull and strictly earlier (no lower horizon bound). Normalize level, lower bound exact event in chronology second_times or candle timestamps fallback; scan only same-timestamp rows, High>level bearish else Low<level; any hit returns recorded time, otherwise null, no substitute crossing.

## CP329-S08 — Stop view

Source: `engine/bridge/trading_pipeline.py:742–759`.

If stop main time absent/outside horizon both time and event null. Else format main time and independent exact strict proof event; lack of proof does not remove main time.

## CP329-S09 — Projection identity

Source: `engine/bridge/trading_pipeline.py:786–819`.

Behavior parent Order identity requires both First and Break nonnull; normalize int pair. Build fresh final audit identity map, last duplicate wins. Preserve direction and market references; no choice of new Order.

## CP329-S10 — Physical and formation Order

Source: `engine/bridge/trading_pipeline.py:821–871`.

Absent audit or out-of-range First/Break returns null. Read entry and crossed tuple (main,exact); native confirmation proof for physical Order direction default intrabar flag. Display physical First/Break main, exact proof and stop level/time; parent Order uses recorded physical pair only if final audit retained it.

## CP329-S11 — Current Order exact cause

Source: `engine/bridge/trading_pipeline.py:873–926`.

Require proven strict stop and behavior source_time. Match parent-stop exact type,source time,event and family (None accepts None/empty). Reset-leg accepts matching post type or generic E/StopAll matching prefix, exact post source and stop; no family gate there. Dedup by physical pair; exactly one match projects, zero/conflict null. No positional or formation Order inference.

## CP329-S12 — Nested OrderAudit

Source: `engine/bridge/trading_pipeline.py:928–985`.

Require valid physical projection else RuntimeError. Parent-stop fields formatted and family title-case; reset-leg all fields convert datetime only; unknown cause kinds omitted. Physical First/Break indices and source box times/prices, stop source and main/exact proof displayed.

## CP329-S13 — Authoritative stop adapters

Source: `engine/bridge/trading_pipeline.py:988–1042`.

Parent stop uses supplied detector.parent_stop and bounds returned index; catches AttributeError/TypeError/ValueError only around call. A uses existing S detector first_a_stop(price,_a_confirmation_time), catches also IndexError. No new detector or substitute search; helper itself may execute native stop lookup. Format stop with proof and price string.

## CP329-S14 — Blue/Reaction formation proof

Source: `engine/bridge/trading_pipeline.py:1045–1108`.

Non-scale Blue source time and absent event; scale requires 1-based Reaction ordinal and bounded Break; proof false intrabar flag. Reaction uses raw First/Break and native candle tag plus public box geometry; default true proof uses raw candidate, never public clipped level.

## CP329-S15 — Reset and standalone Blue view

Source: `engine/bridge/trading_pipeline.py:1111–1167`.

Reset occurrence recorded display/second strings, previous First main only if bounded, broken level string; no substitute proof. Blue mapped Scale/Reset, source line/extreme string, formation proof; standalone stop main/exact always null (not retained), stop price sourceExtreme. BrokenLevel only reset.

## CP329-S16 — Full Blue ordinal join

Source: `engine/bridge/trading_pipeline.py:1170–1179`.

Stable sort full lines by int Reaction number,source time,string kind; enumerate from1. Join not visible list index; includes full invalid/internal lines as supplied.

## CP329-S17 — A nested projection

Source: `engine/bridge/trading_pipeline.py:1182–1269`.

Find full Blue by each ordinal, absent yields null formation. Retained A exact Blue stop proof via each recorded stop level/time/event, not recomputed. A stop from authoritative S helper; strict proof for current Order. Route ordinary/double-stop Type-1/2, parent null, optional 1-based Reaction proof false flag; source and prices retained.

## CP329-S18 — S nested projection

Source: `engine/bridge/trading_pipeline.py:1272–1325`.

Read own stop from E parent service, prove event. Blue formation maps simple/advanced/type3/type4 to Type1–4, other colors null. Parent A formed source/price and recorded stop proof; formation Order via final physical pair. Current Order from exact S source/color/stop cause, no replacement of source.

## CP329-S19 — E parent identity join

Source: `engine/bridge/trading_pipeline.py:1328–1377`.

Source pair int index/time required. Exact stored parent type S/E/StopAll selects corresponding map to get color/number; missing parent keeps stored type/source/price/stop metadata but unavailable color/number null. No temporal-nearest join.

## CP329-S20 — E nested projection

Source: `engine/bridge/trading_pipeline.py:1380–1424`.

Own stop via E service and strict proof; E family/number, stored source; parent exact identity and recorded formation Order. Current Order exact E<number>/family/source/stop cause; no native ledger change.

## CP329-S21 — StopAll nested projection

Source: `engine/bridge/trading_pipeline.py:1427–1493`.

Formation gate type maps sequence-group/stopall/opposite-S to Type1/2/3. Parent represents donor type/color/number/source/price and independent donor actual stop fields, NOT stopped-group gate; null if unavailable. Formation Order final pair; current Order exact StopAll<number>/empty family/own strict stop. Own stop separate.

## CP329-S22 — OrderAudit ordering

Source: `engine/bridge/trading_pipeline.py:1496–1503`.

Sort key First and Break main epochs from actual detector candles; no rank by owner cause.

## CP329-S23 — Shared additive projection

Source: `engine/bridge/trading_pipeline.py:1506–1608`.

Use exact selected arrays shared with legacy. Physical Order direction E detector or opposite fallback. Full Blue ordinal map; S parent map from captured full S, E/StopAll maps full then selected (last wins), skip absent pairs. Reactions raw from native results. Build fresh arrays in selected order; nested out-of-range historical parents not republished as independent rows.

## CP329-S24 — Bridge consistency assertions

Source: `engine/bridge/trading_pipeline.py:1611–1676`.

Collect physical audit pair set. Every public S/E/StopAll with both Order indexes must exist; missing raises. Parent-stop key exact type/family/event/source time maps one identity; same key/same identity allowed, different identity raises. No repair, re-ranking or creation; assertion not an independent completeness proof.

## CP329-S25 — Legacy accepted audit

Source: `engine/bridge/trading_pipeline.py:1679–1729`.

Serialize prepared identities only; cause type parent-stop epoch fields, reset-leg datetimes converted, other omitted. Truthy behavior_public_number overrides native ordinal. Preserve physical geometry and source/stop hit fields, nullable crossing; sort First/Break epoch, stable tie.

## CP329-S26 — Absolute index projection

Source: `engine/bridge/trading_pipeline.py:1860–1871`.

Recursively copy lists/dicts even offset0. Offset only exact int nonnegative keys index or suffix Index (not bool); physicalOrderIdentity/resetReactionIdentity list/tuple parts independently offset exact nonnegative ints, output list. Other values recurse or stay unchanged; IDs/times not generally rewritten.

## CP329-S27 — Trend transition serialization

Source: `engine/bridge/trading_pipeline.py:1874–1894`.

Source actual boundary candle, target direction, previous opposite label, absolute source and stopped Primary3 source indexes, exact event and Decimal level string. ID direction+trend+source epoch. Icon actual +49 main candle (50th inclusive) with High for bullish/Low bearish else null.

## CP329-S28 — Additive shared selection

Source: `engine/bridge/trading_pipeline.py:3176–3251`.

One selected Reaction/reset pair list feeds legacy serialization and nested bridge. Blue flag plus inclusive source range, A flag, S/E/StopAll final visibility lists, audit sorted by physical time if nonnull detector. Build legacy arrays then bridgeOutput from SAME lists. Prior legacy-only branch CP323-S32 retained.

## CP329-S29 — Primary Order serialization

Source: `engine/bridge/trading_pipeline.py:3254–3280`.

Separate conceptual owner from physical direction. Types fixed Order_A then Order_B if causes present. Audit causes map datetime to epoch and Decimal to string (top-level values); source times from market candles, exact confirmation/stop fields and nullable box levels. No new filtering.

## CP329-S30 — Primary point identity/horizon

Source: `engine/bridge/trading_pipeline.py:3283–3326`.

Resolve physical final primary through selected end, native secondary points otherwise. Stable ID from identity_source or point's original role/number/trigger/decision absolute indexes, non-first cycle suffix, cycle ID offset for four-part cycle syntax. Display winner number/source/price; local numeric indexes until absolute projection. Relabel audit causes via final primary. Select source inclusive and decision<=end.

## CP329-S31 — MBL publication

Source: `engine/bridge/trading_pipeline.py:3327–3358`.

Visible cycles trigger<=end. Public leg from formed_matching_legs with primary confirmation at horizon; no additional source-start clip. ID reference/second absolute indexes; cap actual source+400 candle or extrapolate last+TF, not calculation stop. Stop fields hidden if stop index>end. Preserve trigger/confirmation exact and main time.

## CP329-S32 — Primary cycle and post-secondary output

Source: `engine/bridge/trading_pipeline.py:3359–3402`.

Final primary rows vs logical secondary rows; cycleIds dedup encounter order for same physical source and confirmed decision. Cycle rows through activation horizon, high/low count rules as source; primary IDs joined by source. Post-secondary3 orders per visible cycle with stop<=end, no global dedup here. Status last visible cycle else qualified before exclusive horizon waiting break else waiting matching; role-specific postPH3/postPL3 key.

## CP329-S33 — Response envelope

Source: `engine/bridge/trading_pipeline.py:3633–3679`.

Publish engine versions, flag rules (E present+S enabled; StopAll explicit lifecycle+E+S), selected actual bucket epochs and requested timeframe; direction outputs for state.directions. No business rule substitution.

## CP329-S34 — Final reversal and T/F horizon

Source: `engine/bridge/trading_pipeline.py:3680–3710`.

Replace groups only if transition index<=visible end; activeDirection max(calculationStartIndex default -1,direction lexical tie). Repair horizon last visible main+TF-1 second inclusive; closed_through min(epoch(through)+1,last lower epoch+raw_timeframe). StopAll closure decision main epoch+TF<=closed_through. Annotate each segment independently (not aggregate concatenated arrays anew). Timing only rounded 2 decimals.

## CP329-S35 — TF01–02

Source: `engine/pipeline/true_false.py:18–30`.

Capture inclusive through upper bound once; closure left lower bound converted start restricted to right; policy strict low/high; Decimal(level), first hit epoch or null. No main fallback.

## CP329-S36 — TF03/08

Source: `engine/pipeline/true_false.py:33–55`.

Rank S (priority,0), E (priority,number). Active repeat counts separate from reference frontier. Search largest smaller rank descending, lower bound transformed price then latest preceding strictly lower reference; equality excluded.

## CP329-S37 — TF04/05 start and verdict

Source: `engine/pipeline/true_false.py:58–100`.

Reset references/started and zero verdict/base counts on non-S/E, retaining repair_count/latest. S starts Basic interval, E before S skipped. Direction low transforms Decimal by exact sign copy. Engulf lower rank base_count>=2 and display_restart lower verdict_count>=2 independent. S/engulf T, otherwise invert largest smaller strictly crossed reference, absent uses odd F/even T. Repair callback only when key missing, not null.

## CP329-S38 — TF04 repeat/repair recurrence

Source: `engine/pipeline/true_false.py:101–128`.

Assign verdict, pop reference frontier while >= transformed price, append. Evict smaller repeat ranks and repair only latest F with repair_count1, do not delete references. Same-rank same verdict accumulates repair_count; verdict_count only when no display_restart, mark prior/current repeated at>=2. Same F removes prior repair>=current source and attempts current repair. base_count increments whenever prior rank exists regardless verdict. No final sweep.

## CP329-S39 — TF06 StopAll recurrence

Source: `engine/pipeline/true_false.py:131–159`.

New series on first/nonincreasing number; track previous end/largest prior, restart group parity, clear prefix. Otherwise pending restart sets verdict start current. Assign parity T even relative start. Prefix rows number<=largest prior; exact boundary equal previous end or largest and closure callback absent/true marks entire prefix repeated and group parity, sets next restart. No repair.

## CP329-S40 — TF07 final annotation

Source: `engine/pipeline/true_false.py:162–188`.

Clear all three annotation keys on every visited primary/StopAll/E/S row. First row by sourceTime in traversal primary directional then StopAll,E,S, exclude exactly False validity. Sort selected; verdict null initially; primary flushes StopAll buffer, numbers1/2/3 T/F/F; Basic on entire event stream then trailing StopAll. Nonwinning rows no annotation, A/Blue/secondary not visited; mutates final dicts only.

## Qualifications

- Authoritative stop adapters call existing detector methods, which may execute native lookup; no assertion of zero search computation merely because projection is read-only.
- Legacy and additive selection share object lists on active additive path; no runtime byte-equivalence claim.
- Only exact recorded lower timestamp can prove event; absence leaves null without alternate event selection.
- T/F operates on finalized dictionaries and can annotate earlier selected rows; no feedback into native calculation.

## Remaining

CP330 / W2 Live/market aggregation, cache and input/entry integration: review source only (no RAW payload access), actual native dispatch versus optional protocols, cache invalidation and rollback, market segment/index windows and timestamp/Decimal conversion; then W2 closure and W3/W4.
