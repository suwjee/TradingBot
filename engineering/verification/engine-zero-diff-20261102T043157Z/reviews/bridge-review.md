# Bridge full-read review

document_role: evidence; lifecycle: generated; owner: engine-audit

Reader: parent /root. File `engine/bridge/trading_pipeline.py`, pre-edit SHA256 `6d93dbaf67e4dce02060575b92dda5de6eaf6de0148f6db54056015c072181dc`, 3433 lines. Actual sequential chunks read: 1-400,401-800,801-1200,1201-1700,1701-2200,2201-2700,2701-3100,3101-3433. Final tail 3401-3433 reread after a combined output truncated its last exception-handler lines. Complete source read: YES. Both engine/bridge/__init__.py and empty engine/__init__.py were read entirely. Pipeline markers/helpers covered by reaction reader.

## Ownership and mutation

`parse_arguments -> load_engines -> prepare_market_context -> prepare_pipeline_state -> build_response_payload -> main JSON encode`. Bridge normalizes lossless JSON numbers with `parse_float=Decimal`, constructs lower and main candles, shared LowerTimeframeIndex/MarketChronology and full supplied calculation context. from/to only constrain presentation. No hidden original history is recoverable from a selected input stream.

Both geometric Reaction directions are calculated when any behavior is enabled. Blue/A/initial S are reused between bounded Order_B feedback passes. Full E/S/lifecycle acceptance state is mutable and retained in PipelineState; final visibility may restore independent S-root E, synchronize audit and register accepted Order_B legs. Primary commits mutate the native Order ledger and labels; final opposite-direction visibility is recalculated. Primary3 reversal recomputes an independent historical prefix and fresh suffix, possibly repeatedly; each segment rebases local candle indexes to public absolute indexes. Never reuse state between physically independent segments without proof.

Serializers preserve field names, Decimal `str`, insertion/array order and explicit null values. Optional BridgeProjection joins finalized identity/cause evidence; it invokes owner chronology/stop APIs and validates exact lower events. Its current_order iterates all audit identities and causes per behavior (roughly O(B*O*C)), and physical_order can recompute confirmation/projection for repeated appearances. Indexing those joins is a possible presentation-only optimization, but must retain exact family matching, ambiguity/null behavior and cause ordering.

## Complexity and risk hypotheses (not measured)

- Input parse/aggregation/candle construction O(R), memory O(R+M+unique-price-values). `build_candle_buckets` maintains per-call typed-value Decimal cache: equality/representation behavior must stay exact, including Decimal values with equal numeric value and different exponent. Replacing cache lookups with direct Decimal shortcuts can change current representation.
- Shared time/display caches are module-level and retain state until process exit; production normal CLI is a separate process per calculation. Warm in-process repeated calls may retain state; verify separately.
- Full-direction orchestration repeats dependent E and lifecycle passes; up to eight Order_B passes, plus multiple E rebuilds per pass. Removing a pass without proof risks accepted provenance/ownership divergence.
- Primary regimes rerun prefixes/suffixes and allocate fresh Candle copies, MarketChronology and indexes. They deliberately enforce independent state; simply caching/reusing mutable detector objects is unsafe.
- `serialize_primary_structures` calls `selected(cycle.highs/lows)` for counts, materializing full rows/orders, then discards those rows. A possible allocation reduction requires preserving observable exceptions and resolver side effects; benchmark separately.
- `merge_regime_outputs` iterates sets of array/bridge keys. Potential stable key-order nondeterminism when multiple segments of the same direction are merged must be tested; no fix is authorized merely to make a baseline pass.

## Runtime closure outside Engine

Current `apps/chart/vite.config.js` explicitly fingerprints bridge, all active detector/helper owners including primary, and range-input support. runDetector spawns actual Python bridge with configured module paths and env PYTHONDONTWRITEBYTECODE=1. Full source passes original RAW path; selected range passes in-memory input. Existing module implementation edits are included in cache fingerprint without a new server file. No Chart/Vite code change is justified by the current optimization scope. Python supported startup checks orjson/tzdata and >=3.12; normal benchmark runner is stale for arbitrary real timestamp ranges, so this audit uses the supported bridge CLI with discovered input bounds.
