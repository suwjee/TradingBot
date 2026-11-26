# Reset — confirmed geometry invalidation and restart (V3)


**Contract conventions.** B = bullish, R = bearish. Directional extreme X is Low for B and High for R; a strict improvement or stop is X < level for B and X > level for R. Confirmation uses High > top for B and Low < bottom for R. Main position/time, exact lower event, physical identity and ordinal are different fields. Preserve Decimal representation, original arithmetic order, stable traversal, and native failures unless an explicit fallback is specified. Use [declared record interfaces](../../Contracts/Declared_Record_Schemas.md) and [index/chronology services](20_Indexes_And_Caching.md). Procedure labels below name semantic operations, not required implementation symbols.


## RS-M01 — Inputs and ownership

Reset belongs to the [Reaction module](01_Reaction_Engine.md), not Blue or lifecycle. A Reset record contains main index/time, nullable exact second display time, broken confirmed opposite edge and the owning confirmed Reaction First. Do not substitute an unrelated extreme or an Order stop. Candidate invalidation before confirmation is not itself a confirmed Reaction Reset.

## RS-M02 — Race and record rules

| Situation | Decision |
|---|---|
| No confirmed owner and mode A boundary strictly breached before or on confirmation row | Discard initial candidate; reset anchor/search, no confirmed Reset record |
| Confirmed owner strict outward breach, no competing confirmation | Reset |
| Both main OHLC predicates true | Search lower rows for outward and confirmation; if outward exists and precedes/ties confirmation, Reset; if only confirmation is proven, confirmation wins; if neither is proven, Reset wins in the reference race |
| Confirmed candidate exact analysis exists | Search from confirmation + 1 microsecond to Break main end exclusive for strict opposite-edge break |
| Later same-Break breach found | Record exact second, disqualify same-Break mode B reuse; next scan resumes structural Reset |
| No later breach | May seed next mode B from entire Break lower interval subject to correct First color and exact analysis |

In bullish coordinates strict reset is Low < confirmed BoxBottom; in bearish coordinates High > confirmed BoxTop. A confirmed lower-timeframe Reset and a main-candle Reset are represented differently: the former records exact second, the latter may have null second_time. Chronology chooses truthy second display string first, else main display string, else timestamp attribute; the fallback is a representation, not a proof of a crossing. Scale/Reset Blue, Type3 S and Order_B each apply their own formation/search gate; they do not alter this record.

## RS-M03 — Restart algorithm

At Reset, preserve owner First and broken level; clear active candidate and prior continuation state. In the standalone initial scanner switch to Mode A, clear peak and leg floor, mark first leg candle and remember reset context; a reset candle with First color can be anchor. In Unified, use Reset index (pending same-Break Reset when set) and avoid duplicate record for same previous First. Search First strictly after Reset using color/context transition; build local floor/ceiling and frozen outer extreme over the inclusive Reset..First−1 region. Reject First if it strictly violates its local gate. Scan later candles in order. When main simultaneously breaches outer boundary and confirms, lower outward check precedes confirmation, with absent proof invalidating. On invalidation block all potential First positions through invalidating main. If no confirmation and no invalidation by horizon, mark pending for continuation and permit later First candidates in bounded structural search. First healthy completion in First traversal order becomes Mode A; clear cross-direction gate flags; canonicalize and continue. A bounded geometry-only search can find completed geometry without invalidation check, but cannot by itself create an accepted Order.

## RS-M04 — Distinct downstream semantics

Blue Reset uses exact formation if provable, otherwise source main time, and starts ordinary Blue stop scan after source main end. Order_B requires actual exact Reset if no explicit second, then searches strictly later lower rows; no coarse Reset fallback for that proof. S Type3 uses stored reset chronology and its own prior-owner confirmation gate. See [Blue](03_Blue_Line.md), [S](05_S_Zone.md) and [Order B](07_Order_B.md). The source-level operation definitions are RE11–RE13, RE27–RE28, RE77, RE83–RE86 and RE93–RE98 in Reaction, and RE58–RE60 in Index/Chronology. No new exception or trend-switch semantics are added.
