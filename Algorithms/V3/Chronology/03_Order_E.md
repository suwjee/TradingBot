# Order and E

Source-only Phase 07 checkpoint. These clauses describe pinned main, not proposed algorithm changes.

## CH19

Order_B trusts precise Reset second_time through Reset resolver; otherwise requires strict crossing in Reset main [open,open+timeframe). Missing crossing returns null, no open fallback.

[Source engine/pipeline/order_audit_engine.py:139–167](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L139-L167)

## CH20

Order_B boundary includes both main endpoints; earliest equal extreme. Default strict crossing begins at upper bound of Reset timestamp (see 232–238).

[Source engine/pipeline/order_audit_engine.py:170–195](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L170-L195)

## CH21

Order_B sorts Reaction by confirmation, First, Break, ordinal/number; Reset by event time, from-First, ordinal. Reset exact event must exist.

[Source engine/pipeline/order_audit_engine.py:232–272](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L232-L272)

## CH22

Order_B latest post-stop and anchor strictly before Reset Reaction First main time; strict anchor extension and boundary source precedes First. Opposite First may equal strict-cross main; confirmation > exact crossing. Next A after First expires leg if A main index <= crossing main.

[Source engine/pipeline/order_audit_engine.py:300–354](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L300-L354)

## CH23

Stopped-A Order_A selection (SOrderAuditMixin): native confirmation strictly after the A stop and First >= gate main. Independent geometry also requires First >= gate main and initial confirmation strictly after the A stop; a canonical identity remap recomputes confirmation without reapplying that local strict threshold. Independent geometry may map to canonical identity or retain number zero; it wins only if (First,confirmation) is lexicographically earlier. This clause does not impose a universal strict post-parent-stop confirmation gate on the S/E direct Order_A route: `_compute_direct_parent_stop_order` begins at the containing main First and applies `confirmation_after` only when supplied (the later blocked-First skip does not reapply the initial threshold). `order_candidates` ordinarily calls it without that optional threshold. Order_B's strictly later confirmation is relative to its exact boundary break, not a generic parent stop.

[Historical source engine/pipeline/order_audit_engine.py:2546–2620](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L2546-L2620)

## CH24

E first strict crossing is in half-open lower positions, indexed or linear; no main fallback in this primitive. Indexed return (including missing hit) is final; the linear path does not locally clamp positions. No fallback between routes.

[Source engine/pipeline/e_zone_detector.py:420–435](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L420-L435)

## CH25

E parent-stop scans [max(source time,range start),range end). Parent and opposite Order have separate directional stop policies; optional continuation retains exact event and main owner. Live E Order crossing caches raw (start,level) membership including null, clamps search start separately, and reads main time from times[index]; nonlive inherited Order crossing uses candle.timestamp. W2 must reconcile owner time representations.

[Source engine/pipeline/e_zone_detector.py:507–557](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L507-L557)

## CH26

E extreme uses full main candles containing parent and Order stops, both included and clamped to stage bounds. Lower events determine chronology without truncating boundary OHLC. The local boundary expressions are asymmetric: max(stage_start,mapped_start) and min(stage_end,mapped_end), then promote end to start when reversed, with no second stage clamp.

[Source engine/pipeline/e_zone_detector.py:581–606](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L581-L606)

## CH27

E four merged consumption routes: direct, inherited, carried, post-stop accepted; gate-owned lookup is not fifth stream. Earliest exact Order stop, then latest First. Reorder equal-stop accepted groups; reject disowned-S-only causes using prospective source. S with no carried route uses earliest inherited stop or range end as deadline. The unused gate query executes; carried truthiness gates deadline. Three crossed routes are sorted eagerly, accepted equal-stop groups lazily, with exact merge-key ties in direct/inherited/carried/accepted order. Explicit empty owned set stays empty. Prospective source precedes ownership rejection, no local rollback.

[Source engine/pipeline/e_zone_detector.py:608–675](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L608-L675)

## CH28

E decision event is max(parent stop,Order stop). Source, decision, confirmation and stop remain separate. EZone does not store a separate exact Order-crossing field; preserve supplied match stop/source fields and prospective source price, and derive First/Break/box-source main times from detector.times.

[Source engine/pipeline/e_zone_detector.py:677–730](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L677-L730)

### CP332 current-baseline clarification

The CH23 wording above is narrowed to the actual stopped-A route. See [current direct parent-stop selection](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L829-L918), [candidate dispatch](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L982-L1068), and [stopped-A selection](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/order_audit_engine.py#L2546-L2620). The previous wording is retained in the CP332 correction record; no production rule was changed.
