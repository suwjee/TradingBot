# CP379 — S candidate timing and Blue qualification

Pinned source: `53460e68538ac790ab969084c1c7101e5ca833d7`; B04-05 696–869. 436 category rows, 116 W1, 320 additional, 9 supplements; 2032 prior rows revalidated without overlap.

### W3 CP379 — candidate timing, source and Blue qualification (S29–S36)

- **S29 (696–710)**: Timing receives optional A-stop event; comment describes Advanced protection, operative price and event gates below.
- **S29 (711–721)**: Read stop main trend extreme, then normalized opposite Order box bottom bullish or top bearish. Legacy after when bottom<=low bullish or top>=high otherwise, equality after.
- **S29 (722–729)**: Legacy before returns immediately before nested query. Legacy after plus nonnull nested S16 keeps after, without simple candidate chronology.
- **S29 (730–739)**: Null stop event defaults to A-stop main open; S30 candidate, S31 returned event, then Order First main open. Strict event<First open yields before; equality after. S31 fallback not observed event.
- **S30 (741–750)**: Default only null stop event to stop main open, then integer Order First.
- **S30 (751–757)**: Eager S13 whole main inclusive candidate before lower query; reversed range fails even if lower could supply geometry. Query supplied stop event to nominal stop main end; no clamp to stop main open. Empty returns initial whole-main candidate.
- **S30 (758–769)**: Nonempty remainder seed first lower row then strict bullish low/bearish high improvement, retaining first equal. Lower source reference updated but not returned as exact event.
- **S30 (770–783)**: Later S13 range only when First>stop index; later strict improvement wins, equality or absence retains stop main positional index/time and remainder price. Distinguish native Candle.index of later candidate.
- **S31 (785–798)**: Read source main open; lower window [max(open,not_before),open+TF); return first equal normalized extreme timestamp; else max(open,not_before), even beyond nominal end. Price argument not independently normalized here.
- **S32 (800–806)**: Public fallback argument forwards as lower gate not independent replacement; virtual S31 result unchanged.
- **S33 (807–810)**: Explicit nonnull formation_time returned unchanged before source/ordinal reads, no local time validation.
- **S33 (811–819)**: Otherwise int source index and actual candle timestamp, exact string kind !=reset covers any other kind. Valid integer ordinal uses S04 provider default; invalid ordinal returns source open.
- **S33 (820–835)**: Reset broken_level None returns source; otherwise whole source main lower half-open scan. Select directional Low/High then normalize; broken_level normalized within chosen strict comparison per row, not if empty. First strict hit timestamp else source-open fallback.
- **S34 (837–852)**: Check ordinal bounds before map lookup; no native int conversion here. First calculation-valid Reset entry (may internal) from S01, not necessarily earliest. Nonnull time<=cross event; no source-main or behavior-start lower bound.
- **S35 (854–863)**: Upper bound sorted trend confirmation times at behavior start, then within length and <=event, interval (start,event]. Includes provider fallback times and no independent observed confirmation proof.
- **S36 (865–869)**: Read normalized trend extreme then delegate strict policy crossing; no rounding/equality relaxation.

Local returned-time provenance does not prove a physical event or cross-owner acceptance. No Runtime claim.
