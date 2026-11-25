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

Order_A post-stop: First >= gate main, confirmation strictly later. Native search uses upper bound of stop on confirmations. Independent geometry may map to canonical identity or number zero; wins only if (First,confirmation) lexicographically earlier.

[Source engine/pipeline/order_audit_engine.py:2546–2620](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L2546-L2620)

## CH24

E first strict crossing is in half-open lower positions, indexed or linear; no main fallback in this primitive.

[Source engine/pipeline/e_zone_detector.py:420–435](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L420-L435)

## CH25

E parent-stop scans [max(source time,range start),range end). Parent and opposite Order have separate directional stop policies; optional continuation retains exact event and main owner.

[Source engine/pipeline/e_zone_detector.py:507–557](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L507-L557)

## CH26

E extreme uses full main candles containing parent and Order stops, both included and clamped to stage bounds. Lower events determine chronology without truncating boundary OHLC.

[Source engine/pipeline/e_zone_detector.py:581–606](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L581-L606)

## CH27

E four merged consumption routes: direct, inherited, carried, post-stop accepted; gate-owned lookup is not fifth stream. Earliest exact Order stop, then latest First. Reorder equal-stop accepted groups; reject disowned-S-only causes using prospective source. S with no carried route uses earliest inherited stop or range end as deadline.

[Source engine/pipeline/e_zone_detector.py:608–675](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L608-L675)

## CH28

E decision event is max(parent stop,Order stop). Source, decision, confirmation and stop remain separate.

[Source engine/pipeline/e_zone_detector.py:677–730](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L677-L730)
