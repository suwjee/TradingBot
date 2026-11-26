# Phase 04 — Function-level semantic extraction, checkpoint 01

**Status: IN PROGRESS.** Source-only scope. Main baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm head: `627ba700b0107b1f7de2a13c0a4dc5c8b4ff3b3e`. Main was re-resolved at entry and matched the Phase 03 handoff. No production changes, RAW reads, executable reconstruction, engine execution or runtime tests.

## Coverage ledger

The denominator is the Phase 02 FunctionDef inventory (nested declarations included; generated dataclass methods, lambdas and comprehensions are not separate FunctionDef entries). This checkpoint describes 32 named function declarations in four modules plus three package surfaces containing zero functions. It is a first semantic pass, not final bidirectional closure. Source locations below are immutable audit anchors; the algorithms themselves need no source to execute conceptually.

| Module (under engine/) | Declared functions | Described |
|---|---:|---:|
| __init__.py | 0 | 0 |
| bridge/__init__.py | 0 | 0 |
| bridge/live_pipeline.py | 13 | 13 |
| bridge/trading_pipeline.py | 102 | 0 |
| pipeline/PL_PH_detector.py | 46 | 0 |
| pipeline/__init__.py | 0 | 0 |
| pipeline/a_zone_detector.py | 39 | 0 |
| pipeline/blue_line_detector.py | 18 | 0 |
| pipeline/core_utils.py | 6 | 6 |
| pipeline/direction_policy.py | 6 | 6 |
| pipeline/e_zone_detector.py | 54 | 0 |
| pipeline/lifecycle_engine.py | 46 | 0 |
| pipeline/order_audit_engine.py | 82 | 0 |
| pipeline/reaction_engine.py | 107 | 0 |
| pipeline/s_zone_detector.py | 50 | 0 |
| pipeline/true_false.py | 7 | 7 |
| Total | 576 | 32 |

Each named declaration is keyed by its module, source start line, and owner. For full closure require inputs/defaults, state reads/writes, evaluation order, formulas, return/yield, exception paths, dependencies and direction-sensitive versus invariant rules; reconcile each with Phase 02 call, control, effect and exit IDs. No implied proof of arbitrary input dispatch. Generated record interfaces belong to [Phase 03](../Phase_03/Closure_02.md).

## F04-C — Core utilities

Source: engine/pipeline/core_utils.py; blob `38a1053510c5fb114e1b4290de00a2d3b27fc373`; version 1.1.0. No direction-specific behavior. Unless stated, operations do not intercept conversion/comparison/attribute errors; native evaluation and exception propagation are part of the contract.

### C01 — ChronologicalContainmentIndex constructor (20–34)

Input: ordered iterable of triples (start datetime, end datetime, payload of arbitrary type). Create an empty ledger of runs, and three empty working arrays. In caller iteration order, when the working run is nonempty, split BEFORE the current triple if its start is strictly less than the last start OR its end is strictly less than the last end. Store the three previous arrays as a run and start fresh arrays. Append current start, end and original payload reference to corresponding arrays. At exhaustion store final run only if nonempty. Equal boundaries do not split. No sorting, deduplication, interval validity validation or payload copy. Empty input gives zero runs. State owned by the index. Iterable/unpacking/comparison failures propagate; construction does not return a separate result.

### C02 — ChronologicalContainmentIndex.enclosing (36–41)

Input: query start S, end E. Lazy iterator: for each stored run in original order, calculate stop = first index whose start >= S (or run length), then first = first index in ends[0:stop] whose end >= E (or stop). Yield original payloads at positions first through stop exclusive, in ascending order. Equivalent predicate on valid sorted runs: stored start < S AND stored end >= E. Strict left, inclusive right; equal start excluded; equal end included. Does not reorder, mutate, copy or deduplicate payloads. No match yields nothing. Search/comparison failures occur during iteration, not necessarily at iterator creation.

### C03 — ordered_naive_datetimes (44–48)

Input sequence. First require ALL values to have exact datetime type (subclasses excluded) and null tzinfo, with short-circuit evaluation. Only if true, require every consecutive pair in original order to satisfy earlier <= later. Empty and singleton eligible sequences pass when element check passes. Equal times allowed; no sorting. Return Boolean. Index/comparison/type-protocol errors propagate. Both generator scopes are included in this description.

### C04 — as_decimal (51–53)

If value is an instance of Decimal (including subclass), return the same object. Otherwise obtain the native string representation and construct Decimal from that string, under applicable native Decimal conversion behavior. No rounding policy, quantization or binary-float conversion is added; already-float inputs retain the native string's representation, not the original lost precision. Conversion failures propagate. No explicit mutation.

### C05 — order_identity (59–61)

Inputs first index and break index as arbitrary convertible objects. Convert first to integer, then break to integer; return ordered two-element tuple. Native integer conversion (including truncation of convertible non-integral numeric values) applies, not an explicit index validator. Errors propagate in evaluation order. No chronology/order validity check, direction, numbering or provenance field is included.

### C06 — reaction_identity (64–66)

Input reaction-like object. Read first_idx and convert to integer, then read break_idx and convert to integer; return ordered pair. Missing attribute or conversion errors propagate. No call to C05 is required, no validation or mutation. Same physical identity convention as C05.

## F04-D — Direction primitives

Source: engine/pipeline/direction_policy.py; blob `f7d047abde0eb884905f86c1d2beeaaec3f6e07a`; version 1.0.0. DirectionPolicy is a frozen slotted record with five required fields: direction, extreme_attr, opposite_extreme_attr, first_reaction_tag, context_tag. Standard singleton configurations:

| Field | Bullish | Bearish |
|---|---|---|
| direction | bullish | bearish |
| extreme_attr | low | high |
| opposite_extreme_attr | high | low |
| first_reaction_tag | RED | GREEN |
| context_tag | GREEN | RED |

These labels do not redefine global Doji classification. Native dataclass construction does not validate literal annotations. D01–D05 branch on exact equality with bullish; all other stored directions follow the else arm. D06 validates selection independently. No state mutations or swallowed exceptions.

| ID / source start / function | Inputs | Exact semantic result |
|---|---|---|
| D01 / 29 / opposite_direction (property) | record | bearish if direction is bullish; otherwise bullish |
| D02 / 32 / strict_cross | value, level | bullish: value < level; else value > level; equality false for ordinary finite Decimals |
| D03 / 35 / better_extreme | value, current | bullish: value < current; else value > current; equality does not improve |
| D04 / 38 / choose_extreme | left, right | bullish: native min(left,right); else native max(left,right); on equal ordinary values preserve first object |
| D05 / 41 / confirmation_cross | already selected confirmation-side value, level | bullish: value > level; else value < level; equality false for ordinary finite Decimals |
| D06 / 49 / policy_for | direction string | exact bullish returns shared bullish record; exact bearish returns shared bearish record; otherwise ValueError with the two permitted values |

Comparison failures and Decimal exceptional values follow native comparison/context semantics, not a fabricated finite-value filter.

## F04-TF — Final True/False annotations

Source: engine/pipeline/true_false.py; blob `d569d16bc493b9eb5da75ed5594c168751856b6f`. Constants: verdict field trueFalse, repair field trueFalseRepairTime, repeated field trueFalseRepeated. This is final published-row annotation, not formation. BasicRepeat is mutable slotted record (latest row reference, repair_count, verdict_count); no defaults. All row edits are in-place; no implicit rollback on error. Ordinary missing keys, unsupported comparisons, callback/conversion errors propagate. Direction only affects primary collection and repair crossing; repetition logic is invariant.

### TF01 — repair_crossing_lookup (17–30)

Inputs lower index, epoch-to-time and time-to-epoch converters, keyword-only through. Compute right = upper bound of through in lower_index.times, i.e. first position strictly after through; return closure TF02 capturing that right and supplied objects. No scan at construction. Captured index and converters are references, not copies.

### TF02 — repair_crossing_lookup.find (21–28)

Inputs direction, integer start, string level. Compute left = lower bound of converted start in index times, search limited to [0,right). Resolve policy (invalid direction raises). Select first_less if policy extreme field is low, first_greater otherwise. Convert level directly to Decimal. Call chosen search on [left,right) with threshold. If no position return null; otherwise convert index time at result position to epoch and return. Includes start and through, strict crossing according to lower index contract; equality not enough. Do not manufacture intrabar order. Exact index search implementation and converter binding are downstream open items.

### TF03 — _basic_rank (39–42)

Inputs key and row. If key is sZones, return pair (sequence priority for s and row.color, 0); otherwise (sequence priority for e and row.family, row.number). Priority dependency verified from lifecycle_engine.py:28–37: lowercase native string conversions of kind/family; map s/blue=1, e/blue=2, s/red=3, e/red=4; unknown key raises KeyError. Rank comparisons are lexicographic, not price-based. No row mutation. This dependency description is not counted as lifecycle module coverage.

### TF04 — _basic_verdicts (45–94)

Inputs direction, ordered sequence of (key,row), optional-in-effect first_crossing callback (null permitted). Local maps: repeats keyed by rank and known keyed by source time; initially empty; started=false. Nested TF05 owns repair assignment.

For each event in caller order:
1. Determine is-S. An S permanently starts this pass; skip all preceding non-S events.
2. Compute rank and source time t. Collect keys of existing repeats strictly lower than rank, in map iteration order. Lookup parent verdict using optional parentSourceTime. Engulf is true if any lower rank's verdict_count >= 2.
3. Verdict = T if is-S or engulf; else if known parent is not null then F for parent T, T otherwise; else F for odd number, T for even. Store verdict in row then known[t] (same value; chained assignment evaluates right side once, target order is row then known). Duplicate source times overwrite known entries.
4. Remove each lower repeat. If removed latest verdict is F AND repair_count equals 1, invoke TF05 for that earlier row with current t.
5. If engulf, set verdict_count to zero on all still-retained repeats, leaving repair_count unchanged.
6. Lookup same-rank prior repeat. Start new counters at 1. If prior exists and prior latest verdict equals new verdict, add prior repair_count and verdict_count respectively. If verdict is F, remove prior row repair when its repair time (default -1) is >= t, then invoke TF05 on current row using t.
7. Replace rank's repeat with a new BasicRepeat pointing to current row and updated counters.

No final sweep of repeats; returns no value. This function assumes meaningful ordering from its caller, not internal sorting. Repair callback can mutate shared state or fail; earlier row annotations remain. Lower-rank list and engulf generator are evaluated before removal.

### TF05 — _basic_verdicts.repair (50–54)

Captured direction and first_crossing; inputs row and start. If callback exists AND repair field absent (present null still counts as present), call callback(direction,start,row.price). If non-null crossing returned, write repair field. Otherwise leave untouched. No separate output; callback exceptions propagate.

### TF06 — _stopall_verdicts (97–125)

Inputs ordered StopAll rows, optional confirmation_closed callback. Initialize previous_number=0, previous_series_end=0, largest_prior_end=0, group_start/verdict_start=null, empty repeated-prefix list, restart=false.
For each row with number n:
- New series if group_start null or n <= previous_number. Set previous_series_end to previous_number, update largest_prior_end by max, set both start values to n, clear prefix, restart=false. Otherwise if restart flag, set verdict_start=n and clear flag.
- Set previous_number=n. Assign T if (n-verdict_start) even, F otherwise.
- If n <= largest_prior_end, append original row to prefix. When n equals previous_series_end OR largest_prior_end, and callback absent OR callback(row) truthy, revisit every retained prefix row: repeated=true, verdict T for even (its number-group_start), F otherwise. Set restart=true. Prefix is retained until series reset; a larger matching boundary may overwrite earlier temporary verdicts.

No return value, sorting or repair computation. Confirmation callback not called unless the number boundary matches. Earlier repeated flags are not explicitly removed here (TF07 clears them before collection). Equal and decreasing numbers start new series.

### TF07 — apply_true_false (128–155)

Inputs direction, group mapping, first_crossing default null, keyword-only stopall_confirmation_closed default null. Choose primaryLows for exact bullish, primaryHighs otherwise. Visit collections in priority order: selected primary, stopAlls, eZones, sZones; missing collection acts as empty tuple. For each row, remove the three annotation keys if present, even for invalid/donor rows. If calculationValid is NOT the exact Boolean false, retain the first row per sourceTime (set-if-absent); subsequent same-source rows do not replace it. Sort retained pairs by sourceTime ascending; stable sorting applies, though keys are unique.
Set retained row verdict to null. On a primary row, evaluate accumulated stop rows via TF06 and clear stop buffer; if number is 1,2,3 assign T only to 1 and F to 2/3. Other primary numbers stay null. On stopAlls append to stop buffer; on other collections append to basic buffer. After traversal evaluate TF04 on the entire basic buffer (not reset by primary rows) and then TF06 on remaining stop buffer. No return value, no creation of trading objects. Dictionary identity and row aliases remain observable; a row present in multiple collections can have annotation removed repeatedly during the collection pass. Sorting or callback errors propagate without rollback.

## F04-L — Live bridge transport

Source: engine/bridge/live_pipeline.py; blob `e1f1e7d3414a75ed073b67ff2ded3a5a481f6182`; version 1.3.0. Dependencies imported from trading_pipeline (bucket/view state, calculation, progress, argument parsing, engine loading); exact internals remain open. Two custom exception classes subclass ValueError without additional fields: LiveRawChanged and LiveRawDeltaMismatch. Transport is direction-neutral except progress-stage count. Byte hashes are SHA-256, not price arithmetic. Do not normalize RAW in this documentation.

### L01 — LivePipelineContinuation constructor (25–33)

Inputs args and engines. If engines.e_zone is null OR args.s_zones not enabled, raise ValueError (complete behavior pipeline required). Next require exact integer timeframe >=1 (Boolean and subclass excluded), otherwise ValueError. Shallow-copy args, retain engines reference, construct fresh LiveMarketBuckets using original args.timeframe, then fresh LiveMarketViews. No explicit result. Initialization failures propagate.

### L02 — LivePipelineContinuation.append (35–70)

Input rows list of mappings. Start previous_time at bucket last_raw_time. In caller order, convert row.time to integer; reject if converted value differs numerically from original or is <=0; reject if earlier than previous_time when previous exists. Equality with previous is permitted here (different from L10). Update local previous_time. If still null, raise ValueError for no timeframe candles. Shallow-copy retained args; set copy.to_time=previous_time. Direction count=2 if primary engine non-null OR direction is both, else 1. Local stage count=0. Establish L03 callback. Emit started event for Build live market chronology, liveProgress=true, before protected block. In protected block open bucket stage_append transaction with rows; obtain delta; call calculation with copied args, retained engines, buckets, live_views=current view object, bucket_delta=delta and report_stage callback. Report Calculated result ready for validation within transaction. On any BaseException from protected block (including context exit), replace current views with fresh LiveMarketViews then re-raise; transaction rollback semantics delegated to bucket owner. Return payload after successful context exit. Pre-validation and initial progress exceptions are outside that catch. State of external callbacks is not rolled back by this wrapper.

### L03 — LivePipelineContinuation.append.report_stage (52–55)

Input label. Increment captured completed_stages before emitting completed progress: liveProgress=true, completedStages=current count, totalStages=direction_count+4. Captures direction_count and mutable local counter. No explicit result; emit failure propagates after counter increment.

### L04 — _decode_raw (81–85)

Decode data with native JSON parser using Decimal for floating numeric tokens and native default handling for other tokens. Require nonempty list; otherwise LiveRawChanged with message requesting Apply again. JSON parsing/encoding/conversion errors propagate as native exceptions. No validation of individual rows or sorting. Return decoded list.

### L05 — LiveRawSource constructor (91–98)

Inputs selected list, original bytes data, original decoded list. Binary lower bound in original keyed by item.time for selected[0].time (key applied to elements, not target). Compute end=start+len(selected). If selected is not identical object to original AND selected != original[start:end], raise LiveRawChanged for precision/range mismatch. Store catchup slice original[end:], last_time=original[-1].time; invoke L06. Does not independently check sorting or empty lists (indexing failures propagate). Catchup slice contains original row references.

### L06 — LiveRawSource._remember_prefix (100–106)

Input raw bytes. Set _end to last occurrence index of closing square bracket (native not-found value -1, no independent rejection here). Construct SHA-256 state over memory view slice before _end; retain byte suffix from _end inclusive as _ending; set _raw_sha256 to L07 digest of prefix plus suffix. Mutates four state fields in that order. No separate return.

### L07 — LiveRawSource._file_digest (109–112; static)

Copy supplied hash state, update copy with ending bytes, return hex digest. Original hash state untouched. No exception handling.

### L08 — LiveRawSource.append_delta (114–127)

Inputs delta bytes, base_sha256, expected raw_sha256, pipeline. If base differs from retained raw digest OR delta lacks leading comma, raise LiveRawDeltaMismatch (no custom message). Clone prefix hash and feed all delta bytes. Compare digest with old ending via L07; mismatch raises same exception before pipeline call. Decode new rows by constructing JSON array from delta excluding first comma, enclosing with brackets (L04 requires nonempty). Call L10; only after success increase _end by delta byte length, replace prefix state and raw digest. Ending stays unchanged. Return pipeline result. No explicit rollback of side effects inside pipeline; metadata updates happen after success.

### L09 — LiveRawSource.append (129–145)

Inputs full bytes and pipeline. Reject if byte length <= _end OR SHA-256 over prefix before _end differs from stored prefix, using LiveRawChanged. Left-strip suffix from _end. If comma prefix, decode JSON by replacing first comma with opening bracket and retaining remainder (L04). Else if right-stripped suffix is exactly closing bracket, new_rows empty. Else reject as non-append. Call L10 even when new_rows empty. After success, nonempty rows trigger L06 on new full bytes; otherwise if exact ending bytes changed replace ending and recompute raw digest via L07. Return result. No deduplication or fallback to parsing revised history.

### L10 — LiveRawSource._append_rows (147–157)

Inputs new_rows and pipeline. Starting from retained last_time, each new row's time must be STRICTLY greater than previous (comparison as supplied, no conversion here). Failure raises LiveRawChanged before downstream append. Call pipeline.append with concatenation of retained catchup and new_rows, then clear catchup and assign last_time to final previous. Empty new rows still pass catchup (possibly empty). Return downstream result. Metadata not advanced if downstream fails; previous is local.

### L11 — _send_worker_message (159–160)

Input kind and arbitrary named fields. Construct mapping with type=kind followed by fields (a type field can overwrite initial type); JSON encode using compact comma/colon separators, native defaults otherwise; print one line with flush enabled. Output side effect only; JSON or IO errors propagate.

### L12 — _report_worker_progress (163–165)

Input event mapping. Forward via L11 with kind progress and event payload if event.status equals started OR completedStages key exists. Status access occurs first (missing status raises). Otherwise no output. No explicit return.

### L13 — main (168–221)

Entry parses arguments, reads required environment variable TRADINGBOT_LIVE_RAW_SOURCE as path, reads selected bytes and decodes. If selected path equals original path reuse selected bytes and decoded object; otherwise read and decode original independently. Create lineage L05, release local large input references, create continuation L01 using load_engines(args, empty mapping); send seed ready=true and payload from appending selected. Release selected reference.
Repeatedly read header from binary stdin with size limit 256. Empty header (EOF) ends successfully. Nonempty must end with newline; parse JSON, read bytes, sha256, baseSha256. Validate size exact int and >0, digest string length 64 (no hex-character check). Read exactly size bytes or raise ValueError. Set progress sink to L12 only if progress is exact Boolean true; otherwise no-op lambda. Within progress context:
- If base digest not null, invoke L08. Catch LiveRawDeltaMismatch locally: send error code RAW_DELTA_MISMATCH with checkpoint-continuity message, continue next request.
- Else if hash of raw bytes does not equal digest, send error code RAW_RETRY with retry message, continue.
- Otherwise invoke L09.
After successful progress context, send update with payload, release updated/raw locals. Outer LiveRawChanged handler sends error code RAW_CHANGED with exception text and returns 1. Outer ordinary Exception handler prints error to stderr (flushed), sends LIVE_ENGINE_FAILED generic Apply-again message, returns 1. Otherwise return 0. BaseException outside the ordinary exception family is not caught by main. Module entry invokes native process exit with returned code only when run as main. Progress context/IO/callback failures may propagate from handlers; no blanket guarantee of response on broken pipe.
Both lambda scopes covered conceptually: time-key function in L05, no-op progress sink here. No speculative transport scheduling behavior.

## Package initialization surfaces

- engine/__init__.py, blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`: empty.
- engine/bridge/__init__.py, blob `7cce7308316bd9e00f1a3687a6a84e0f1adb22d4`: docstring only.
- engine/pipeline/__init__.py, blob `656ba15cfbd7edab34a66cd5bc907171940af38c`: resolve its own directory to string; if exact string absent in sys.path insert at index zero; then import and expose BlueLine, ScaleStrike, count_scale_strikes, detect_blue_lines, fibonacci_level from package-relative blue_line_detector, in that order in __all__. If already present do not move it. Import errors propagate. Module initialization has a search-path side effect; no named function declarations.

## Review and next checkpoint

Source content was independently retrieved from pinned main for all seven listed surfaces and the sequence-priority dependency span. The four completed module descriptions enumerate all 32 named declarations against the Phase 02 scope evidence. The other 544 named declarations are NOT YET EXTRACTED by this phase. The class/module metadata above does not certify all 85 classes. Cross-module callback resolution, native library protocol assumptions, exact error strings where summarized, dataflow/branch/call/effect/exit ID crosswalk, and independent final completeness review remain open. Static source interpretation only; runtime gates are out of scope. Next: Blue Line, A/S and remaining owning engines/bridges, preserving source order and explicit dependencies. Do not declare Phase 04 complete until all named declarations and their behavior-affecting anonymous/module scopes are reconciled.
