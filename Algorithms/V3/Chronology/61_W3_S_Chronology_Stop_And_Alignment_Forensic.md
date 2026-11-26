# CP376 — S chronology, stop and alignment

Pinned source: `53460e68538ac790ab969084c1c7101e5ca833d7`; B04-02 178–402. 733 category rows, 167 W1, 566 additional, 10 supplements; previous 553 rows revalidated without overlap.

### W3 CP376 — chronology, stop, source and Reaction alignment (S02–S19)

- **S02 (178–180)**: Delegate main index to chronology without clamp argument; native default rejects events before first main candle and maps by right bound minus one.
- **S03 (181–185)**: Delegate lower window with explicit start/end; provider half-open bounds and native slices; no extra validation.
- **S04 (186–190)**: Call provider reaction_confirmation(direction,reaction) with default intrabar enabled. Provider invalid intrabar start resets to Break open; first strict lower confirmation or Break-open fallback, including cached value.
- **S05 (191–197)**: Public API returns virtual S04 result unchanged; no independent timestamp or crossing validation.
- **S06 (198–200)**: Provider Reset time precedence cached nonnull, truthy second_time parse, truthy display_time parse, else timestamp; no new local normalization.
- **S07 (201–208)**: Convert reaction_number to int, reject below 1 or above trend count, then positional one-based trend Reaction lookup and S04 using S direction. Ordinal not independent physical identity.
- **S08 (209–213)**: Select policy extreme attribute and normalize via as_decimal; existing Decimal preserved, otherwise Decimal(str(value)).
- **S09 (214–216)**: Delegate strict directional crossing; bullish low < level, bearish high > level; equality excluded.
- **S10 (217–222)**: Clamp lower start using max(start,range_start); bisect left at clamped start and exclusive range_end; actual lower availability controls branch.
- **S10 (223–234)**: If nonempty indexed interval and index nonnull, use first_less bullish or first_greater otherwise. Indexed miss returns None directly, not main fallback; hit uses lower_times[position] and provider main position for candle timestamp.
- **S10 (235–240)**: Otherwise slice lower rows and traverse in existing order, returning first strict directional hit using row timestamp and mapped main position. Index and linear timestamp origins differ.
- **S10 (241–251)**: Nonempty linear miss returns None. Only empty slice scans main from max(selected start_index,bisect_left(candle_times,original start)) through end_index inclusive. No containing predecessor; return actual native candle.index int and same timestamp twice; exhaustion None.
- **S11 (253–259)**: Public first_a_stop forwards level,start unchanged through virtual S10.
- **S12 (260–278)**: Forward exactly supplied zone/ordinal/price/stop tuple and first physical Order match to S39. Wrapper does not select or substitute later Order; initial cause comment is not complete accepted-ledger proof.
- **S13 (279–293)**: Reject reversed range before seed; positional start access and inclusive subsequent slice without clipping to selected analysis range; strict policy improvement preserves first equal. Return actual source object's integer index and timestamp.
- **S14 (294–313)**: Separate reversed-range error; positional seed and inclusive slice; replace on <= bullish or >= otherwise, so last equal owns. Preserve source object's index/time and Decimal selected value.
- **S15 (314–324)**: Optimized path requires nonnull ordered confirmation list, exact datetime query type and naive tzinfo. bisect_right excludes equality; return one-based original position and cached timestamp or None without fallback.
- **S15 (325–333)**: Otherwise enumerate original trend order, recompute virtual S04 for each and choose first strict confirmation > query. No sorting or unconditional exact crossing proof.
- **S16 (334–345)**: Read integer Order First then Break, First candle timestamp, Decimal top then bottom; default all trend positions, narrow via two right bounds only if ordered First list exists. Upper bound inclusive Order Break.
- **S16 (346–357)**: Original positions traversed. Read candidate First, Break, First timestamp. Ordered short-circuit rejects First time <= Order First, First index <= Order First, Break > Order Break, or First time >= Order confirmation.
- **S16 (358–367)**: Compute confirmation after preliminary guards; compute containment eagerly even if confirmation too late, top <= Order top then bottom >= Order bottom if top passes. Final confirmation <= Order confirmation and containment; first qualifying original ordinal; None otherwise.
- **S17 (369–377)**: Call S14 with integer Order Break then aligned Reaction Break; inclusive last-equal geometry, no lower-event clipping.
- **S18 (378–393)**: Lookup integer Reset from_first_idx in mixin owner map, missing returns None. Use selected owner's Break position and main index of provider Reset time; reversed interval None; otherwise S14 inclusive last-equal whole main geometry. First-key map is not full physical identity.
- **S19 (394–402)**: bisect_right on sorted trend confirmation times at A-stop; guard position within length then <= crossing. Interval (A-stop,crossing]; only Boolean existence, no candidate source/geometry proof.

The local return values do not prove physical ownership, crossing-cache freshness, or arbitrary external callback equivalence. W3 cross-owner acceptance remains independent.
