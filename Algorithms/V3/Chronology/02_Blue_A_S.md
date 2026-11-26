# Blue, A and S

Source-only Phase 07 checkpoint. These clauses describe pinned main, not proposed algorithm changes.

## CH09

Main stop query scans max(0,start) through end inclusive; returns whether first strict penetration belongs to end index.

[Source engine/pipeline/blue_line_detector.py:62–75](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/blue_line_detector.py#L62-L75)

## CH10

Pending scale scans lower rows through Break end exclusive, stops after confirmation time (equality included). Add penetration before checking same-row breakout; first breakout with eligible evidence selects accumulated directional extreme, earliest on equal price.

[Source engine/pipeline/blue_line_detector.py:87–142](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/blue_line_detector.py#L87-L142)

## CH11

A strict crossing window [start,end) or physical lower end. Nonempty lower window with no hit returns null. Empty lower window alone falls back to main starts selected by lower bounds.

[Source engine/pipeline/a_zone_detector.py:129–169](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L129-L169)

## CH12

A extreme range includes exact endpoints (end + one microsecond), rejects reversed bounds. Earliest equal extreme; absent lower rows uses complete owning main candles of both endpoints.

[Source engine/pipeline/a_zone_detector.py:171–214](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L171-L214)

## CH13

Scale Blue formation/stop scan use A's native confirmation with intrabar start disabled: search begins at Break open, returns the first strict lower hit or Break-open fallback if absent. Reset Blue forms at first strict lower Reset crossing or source open fallback; stop scan starts at source open + timeframe.

[Source engine/pipeline/a_zone_detector.py:216–243](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L216-L243)

## CH14

A selects first list position with confirmation >= trigger and optional First time >= not-before, using binary search only under ordered conditions.

[Source engine/pipeline/a_zone_detector.py:497–531](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L497-L531)

## CH15

S A-stop scan [max(start,range start),range end). Nonempty lower no-hit returns null. Empty lower window uses main starts >= original start within stage indices, duplicating main time as event.

[Source engine/pipeline/s_zone_detector.py:217–251](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L217-L251)

## CH16

Candidate event is first exact lower extreme equal to level in [max(source open,not-before),source open+timeframe). No equality hit returns max(source open,not-before), not proof of physical event.

[Source engine/pipeline/s_zone_detector.py:785–798](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L785-L798)

## CH17

S Order stop independent of candidate qualification. Candidate gate max(scan start,candidate start); nonfallback uses earliest available Reset Blue or strictly post-behavior ordinary trend confirmation, then max with gate. Compare lower positions, same-position joint hits reject. Earlier Order red, earlier candidate blue or fallback according to qualification.

[Source engine/pipeline/s_zone_detector.py:870–960](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L870-L960)

## CH18

No lower rows: S race starts at owning main candle and scans through stage end. Same main row with both hits rejects; otherwise Order red, qualified candidate blue, permitted unqualified fallback.

[Source engine/pipeline/s_zone_detector.py:962–993](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L962-L993)
