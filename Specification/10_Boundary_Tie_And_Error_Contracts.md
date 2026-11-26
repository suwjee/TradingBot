# Boundary, tie, null and failure contracts — V3.0

## B01 — Shared native semantics

Do not substitute global inclusive comparisons for strict ones. Strict cross and better extreme return false on equality. The original numeric representation can matter when equal prices select a different source. An exact lower observation can prove both sides crossed without proving intrarow order; use the owning race rule, never invent tick chronology. Preserve left-to-right short-circuit evaluation, first matching element, insertion order of ordered mappings, stable sort, native min/max first-on-tie and explicit tie keys. Set membership is not a stable order guarantee.

## B02 — Tie and boundary matrix

| Source path / operation | Equality / order |
|---|---|
| OHLC merge | earlier high/low retained, latest close, first open |
| Range tree / E sparse main extreme | earliest equal positional source |
| DetectorBase min/max | strict improvement only; inclusive main range; indexed path same earliest tie |
| A first crossing | lower [start,end); if lower rows exist but no strict crossing, null, no main fallback |
| A range extreme | includes end via +1 microsecond; lower index or lower scan; main fallback includes containing start/end; earliest equal |
| S ordinary candidate source | inclusive main range, strict improvement, earliest equal |
| S last candidate source | inclusive main range, <= for bullish / >= for bearish, latest equal |
| S candidate after Order confirmation partial candle | qualifying better-or-equal lower remainder can replace prior candidate |
| S candidate vs Order-stop race | exact same lower position returns null; earlier Order -> red; earlier qualified candidate -> selected family; no-lower fallback both crosses on same main -> null |
| S pre/post-Order geometry | equal boundary remains after-Order; nested geometry owns Advanced; exact earlier event may change Simple route |
| Blue confirmation / decisive strike | eligible lower rows no later than confirmation; strict penetration and strict confirmation; min/max first equal |
| Reaction behavior containment | outer First strictly earlier; outer confirmation at least inner; price limits inclusive; lower path end inclusive |
| E parent/source geometry | complete main candles containing parent stop and order stop included, lower stop chronology not a truncation of source OHLC |
| E consumption of physical Orders | earliest exact stop then later First (negative First index); across direct, inherited, carried, post-stop routes; disowned-source filter may skip earlier choice |
| Accepted post-stop Order stream | stop time, confirmation, negative First; E consumption deliberately reorders same-stop group by its own key |
| Lifecycle sequence hard reset | interval (start,end], reset exactly at start excluded, at end included |
| Parent-stop cause publication | earliest confirmation, then First, then Break; exact tie first |
| Primary strict crossing | starts strictly after event via upper bound; same-time up/down -> ambiguous/wait, no invented winner |
| Primary extreme | inclusive main indexes; native min/max first equal |
| Primary physical reconciliation | highest local number then role order; strictly more extreme price can continue numbering |
| Primary Order candidate | earliest stop event, later First, earlier Break among eligible candidates |
| T/F final owner | first valid same-source in collection priority, not max number |

The matrix is a foundational navigation contract, not an assertion that every branch of Reaction/Reset, S families or E lifecycle uses a single tie rule. The exact branch-level race conditions will be derived in function/module/event phases.

## B03 — Missing, null, false, empty and zero

A nullable declared field can still be required at record construction. A field default null does not establish a global null-handling rule. Native annotations are not runtime validators. Preserve key presence separately from key value: e.g. Order stop_cross missing invokes a lookup, null is cached no-cross; a stored null direct-parent or crossing result counts as a cache hit. Optional supplied callables may be selected using non-null or truthiness guards; these are not interchangeable. Preserve the caller's actual guard. A valid index 0 must not be lost through a truthiness default. A physical bounded Order number zero and no public Reaction are distinct from missing number. An explicit false calculationValid is the T/F exclusion condition, while public Blue uses Boolean conversion/defaults. Empty input and no-result paths are not universally errors.

## B04 — Error / fallback matrix

| Primitive / boundary | Exact outcome at this level |
|---|---|
| Direction policy factory | reject any value other than bullish/bearish with ValueError |
| CLI | parser validates choices/required/type; timeframe or raw timeframe <1 raises ValueError |
| Live timeframe | require exact int and >=1; reject otherwise |
| Batch market rows | reject empty; no general sort or full OHLC validation |
| Live decode | nonempty list required; JSON parse error propagates |
| Live time validation | positive int-convertible equal value, nondecreasing; transport lineage extension strictly increasing relative to prior raw |
| Display datetime parsing | invalid format raises; Reset prefers nonempty second then display then timestamp |
| Main index | before first raises unless clamp; clamp returns 0; no separate post-last rejection |
| DetectorBase timeframe | derived nonpositive raises |
| Range-index extreme | invalid/empty range raises ValueError |
| Range-index crossing | bounds clamped; empty/no crossing returns null |
| Prepared index | source sequence identity mismatch raises |
| Suffix refresh | invalid monotonic/capacity bound raises |
| Reaction confirmation | no qualifying lower crossing returns Break candle start, not evidence of crossing |
| A crossing | only empty lower window enables main fallback; no lower crossing with existing rows returns null |
| A extreme | end<start raises; empty lower window uses containing main extremes |
| S source extreme | reversed index bounds raise ValueError; exact race tie null |
| Blue missing main candle | converts missing-key error to ValueError, chained; missing Leg-Start boundary or preceding reaction also raises |
| Canonical Mode-B Order stop | reaction_number<=1 raises; prior healthy geometry required |
| E sequence priority callback | constructor rejects null resolver |
| E main sparse range | length<=0 returns left position in helper, not a universal valid range |
| Order optimized stream / carried index | guarded native validation; fallback on incompatible row/geometry; local Decimal context isolates flags/traps |
| Live bucket transaction | restore old suffixes, timestamp, newly added cache keys for BaseException thrown through yielded transaction; rethrow |
| Live worker | discard views after failed replay; lineage metadata commits after successful append |
| Feedback | repeated Order_B identity or eight passes without convergence raises RuntimeError |
| Primary continuation | timeframe mismatch ValueError; changed event not datetime TypeError |
| Reversal regime | invalid segment boundaries or unsupported independent Primary3 evidence raises |

### B05 — Additional v2.8.7 boundaries

| Primitive | Exact guard / result |
|---|---|
| MarketIndexWindow crossing | clamp local bounds; empty returns null; base position translated only when non-null |
| MarketIndexWindow extreme | require 0 <= left < right <= window length; otherwise ValueError |
| Closed prefix reuse | absolute exclusive end <= first_dirty_main, matching complete key, and non-null saved result; otherwise calculate |
| Closed prefix transaction | publish current used map only on normal exit; exception through yield retains prior map |
| Live buckets with live_views | bucket_delta must not be null (assertion); no such assertion in no-view route |
| StopAll donor choice | retain accepted E on occupied physical pair; independent root is additional donor only at absent pair |
| Basic reference crossing | strict comparison price below current in normalized space; equal history tail removed when inserting newer pair |
| Repair crossing | first lower position in inclusive horizon, from lower_bound(start), using strict native directional predicate |

Source: trading_pipeline.py:1756–1857, 2596–2640, 3737–3753; true_false.py:18–29, 47–128.

Do not infer an exception is reachable merely from a conservative CFG edge. Do not suppress native parse, conversion, key, arithmetic, callback or comparison errors where source does not catch them. Detailed exception types, exact messages, branches and cleanup obligations remain attached to every owning function in the Phase 04 inventory. No runtime tests.
