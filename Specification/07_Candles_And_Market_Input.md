# Candle, market input and bucket contracts (V3.0)

## C01 — Input record and normalized bucket

| Field | Input / normalized value |
|---|---|
| time | integer-convertible input; normalized integer epoch seconds |
| open | normalized Decimal, first row in consecutive bucket |
| high | normalized Decimal, maximum over consecutive bucket |
| low | normalized Decimal, minimum over consecutive bucket |
| close | normalized Decimal, last row in consecutive bucket |

Read required fields by key; absent fields propagate errors. Extra input keys are not carried into the bucket. No global OHLC range validation, sorting, gap filling or synthetic lower observations occurs in this primitive. The batch bridge rejects empty rows. Live decode requires nonempty list. The source calls this collection RAW; this document specifies the logic without reading market datasets.

## C02 — Aggregation procedure

Given rows in caller order, timeframe, normalization callable, optional lower and main tail records and lower_only flag:

~~~text
Initialize each output list with its supplied tail if present, else empty.
For each row in caller order:
    Convert time to integer.
    Normalize open, high, low, close, in that order.
    Merge into lower output by exact timestamp:
        If current record absent or time differs, append a new record.
        Otherwise retain open, select max(previous high, high),
        select min(previous low, low), replace close.
    If lower_only, continue to the next row.
    Compute main timestamp = time for timeframe 1,
        otherwise floor(time / timeframe) * timeframe.
    Merge into main output using the same rules.
Return both lists, preserving input encounter order.
~~~

Equality retains earlier extrema, including their Decimal representation. Adjacent equal lower timestamps collapse; equal timestamps separated by a different timestamp are not globally regrouped. With no tails and no rows both lists are empty. lower_only skips main merging, so a supplied main tail (if any) remains; normal batch use supplies none. At one-second timeframe, the production batch caller passes lower_only and uses lower records as main records instead of building two copies.

## C03 — Candle model

Immutable slotted record; constructor has no defaults and no independent data validation.

| Field | Type | Meaning |
|---|---|---|
| index | integer | sequence ordinal assigned by enumeration, optional start offset |
| timestamp | naive datetime | converted local timestamp |
| display_time | string | formatted local timestamp to seconds |
| tag | string | native GREEN or RED for normal construction |
| open, high, low, close | Decimal each | already normalized OHLC, not re-normalized by constructor |

Color = GREEN when open <= close; otherwise RED. Equal open/close (Doji) is GREEN in both market directions. No dependence on prior candle, high/low, or selected direction. Display format is four-digit year, two-digit month/day/hour/minute/second with separators YYYY-MM-DD HH:MM:SS.

Internal reflection produces a new candle with unchanged index/timestamp/display_time; open and close copy-negated, reflected high = copy-negated original low, reflected low = copy-negated original high. Swap GREEN/RED tag; other tags remain unchanged. This is an internal coordinate adapter, not native color re-evaluation. Preserve Doji's native GREEN output even if its reflected role is RED.

## C04 — MarketContext and BucketAppend

MarketContext carries seconds, candles, lower_index, chronology, inclusive start_index/end_index, index_offset=0 and initial_bullish_trend=false, initial_bearish_trend=false. Seconds and candles can reference the same list at timeframe 1. Do not clone by default or assume independence. Segments have their own list slices and local index coordinate system; indexed zero-origin slices may preserve existing candle record identity. Nonzero starts (or absence of indexed support) reindex the relevant records, and indexed mode supplies prepared parent windows. See T05/I06 for exact guards. See [time contract](03_Chronology_And_Time_Model.md).

BucketAppend carries first_dirty_second, first_dirty_main, settled_seconds, settled_main; all integer positional boundaries. Settled count is max(0, length-1), excluding the final mutable bucket even if a chronological gap exists. Dirty index identifies the suffix to rebuild.

## C05 — Live normalization transaction

LiveMarketBuckets requires exact integer timeframe >=1. Owns lower/main bucket lists, last_raw_time initially null and a persistent price cache. At timeframe 1 both bucket fields are aliases of the same list. For an empty append yield the current dirty/settled boundary without mutating data. Otherwise derive first input time and aligned bucket. If the last lower time equals first input time, reopen a copy of the old lower tail. If main is separate and last main bucket matches first aligned bucket, reopen a copy of main tail. Shared main uses lower dirty index.

Checked row iterator requires time converted to int to equal original time numerically, be >0, and not decrease versus last time. It does not demand exact integer type of every time value. Normalize with persistent existing cache plus separately staged new values. Aggregate before mutating owned suffixes. Save old suffixes and last time, commit new keys and suffix replacements, assign last time, then yield delta. A BaseException thrown during the yielded transaction restores old suffixes and time, deletes new cache keys and rethrows. This is not a general promise of rollback for every failure before entering the try/yield block.

The live worker also checks chronology and rebuilds market views on a BaseException after failed replay. The separate transport lineage requires new timestamps strictly later than prior raw time; do not collapse this stricter gate into bucket nondecrease.

## C06 — Candle view construction and refresh

Construct candles in original bucket order with configurable start ordinal. Call local time conversion, display formatting, native color classification and configured Candle constructor; pass normalized prices unchanged. Live views replace the dirty suffix of the existing list; rebuild a range index if absent or current length exceeds capacity, otherwise refresh suffix in place. When timeframe=1 main views and main index alias lower views/index.

Source provenance is in the [phase evidence](../Audit/Phase_03/README.md). No execution or RAW tests.
