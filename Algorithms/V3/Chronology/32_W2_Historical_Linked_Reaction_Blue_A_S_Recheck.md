# CP347 — historical matrix-linked Reaction, Blue, A, S and core review

22 exact IDs directly reviewed; cumulative 66/131 historical linked records. W2 NOT_ACCEPTED.

### CP323-P10 · engine/pipeline/reaction_engine.py:2792–2864

Validate direction and >=2 committed main, copy lists, positive timeframe and contiguous positional extension with strictly increasing times; main gaps integral timeframe multiples, lower within new main range. Detector construction precedes try; retained cursor scan and index release finally. Snapshot clones Reaction candidates but only shallow Reset list.

Handoff: Standalone optional continuation; no active worker equivalence. Cleanup not guaranteed on detector construction failure.

### CP323-P11 · engine/pipeline/reaction_engine.py:2866–2905

Both empty snapshot; otherwise validate against last committed rows and concatenate. No checkpoint replays initial cursor and counts batch main length; checkpoint seeds retained prefixes, clones previous/candidate and scans from next index. Release new sequence indexes in finally; commit only after successful scan/cleanup, then snapshot; preview leaves owned state unchanged.

Handoff: Snapshot failure after commit not rollback; retained prefixes may share original records. No runtime execution.

### CP323-P15 · engine/pipeline/blue_line_detector.py:447–514

Validate direction, initialize checkpoint and calculate tail. Update bounds first_changed by existing checkpoint count/new reaction count; optional dirty main rewinds to first earlier break at/after dirty or affected Reset owner. Retain shallow checkpoint/line prefixes, replay nonempty suffix, publish only after success, shallow result.

Handoff: Removed Reset owners must be supplied by upstream frontier; no local universal dirty range or timeframe check.

### CP323-P18 · engine/pipeline/a_zone_detector.py:502–531

Binary path only nonnegative start, ordered confirmations, exact naive trigger, and if optional not_before, ordered Firsts and exact naive bound. Max of start and lower bounds; return 1-based original reaction. Else list-order inclusive comparisons, native negative indexing not normalized.

Handoff: A confirmation is caller's false-intrabar chronology value, including possible open fallback; ordering guards not proof of exact event.

### CP323-P21 · engine/pipeline/a_zone_detector.py:839–897

Native wrapper constructs detector then detect; live history has separate dicts. Fresh history and previous reference initialized before base constructor (virtual confirmation calls). Compare zipped First/Break/confirmation triples and lengths; changed time minimum Break in both differing suffixes. Settled strictly before nonnull dirty.

Handoff: No full Reaction structural comparison; cache reuse requires relevant upstream frontier.

### CP323-P22 · engine/pipeline/a_zone_detector.py:898–960

Settled reaction window end<=changed Break boundary. Confirmation cache key Break index/str level; previous hit only when Break main settled. Reset key source/str broken level uses previous if main settled. Crossing key str level,start,end retains null plus lower presence; old bounded end<=dirty or settled hit with same lower availability permits reuse. Earlier unchanged lower rows prevent fallback even when suffix empty; otherwise scan from dirty only in stated cases. Extrema prefer settled previous, else current, else native.

Handoff: String representations not Decimal numeric equality; lower availability controls fallback, not an unrestricted miss cache.

### CP323-P23 · engine/pipeline/a_zone_detector.py:962–1036

Match key trigger/not_before; current, then old nonnull ordinal within common prefix, or old null with same inputs; else search from common prefix if old key exists. Return current Reaction. Blue key includes formation/stop/event/levels/kind/internal, not ordinal. Inherited stop reuse settled reaction window; pair trigger requires expiry and all relevant nonnull events settled; source key trigger index/confirmation both settled; zone identity key preserves Decimal as_tuple.

Handoff: Reuse bounded by exact keys and dirty input contract; no stale old Reaction object on match.

### CP323-P24 · engine/pipeline/a_zone_detector.py:1042–1069

Wrapper result shallow list. Validate timeframe and dirty <= min old/new main counts; dirty minimum available old/new timestamp, else new last+TF (or None). Construct live detector, detect, clear previous history reference, publish detector/result, snapshot.

Handoff: Failure before assignment retains wrapper references, not generalized rollback of external owner objects.

### CP323-S08 · engine/pipeline/reaction_engine.py:1371–1408

Span identity integer First/Break; published box bounds, native confirmation and First main. Outer First strictly earlier, confirmation/box inclusive. Inner path available lower rows inclusive via left/right bisect, nonempty required; extremes index and containment inclusive.

Handoff: No completeness/gap proof beyond actual available rows; published and native geometry distinct.

### CP323-S09 · engine/pipeline/reaction_engine.py:1409–1478

Build both direction spans; optimize only exact naive times globally, otherwise scan all. Lazy inner extrema once eligible, empty breaks owner loop, first valid owner marks identity. Mutate original Candidate metadata by zipped ordinal, identity number map, blocked First timestamps; preserve full result lists.

Handoff: No removal of internal Reactions; no explicit rollback on metadata failure.

### CP323-S19 · engine/pipeline/blue_line_detector.py:517–590

Public filter calculation-valid truthy and not internal. Mark original lines via owner ordinal or strict same Reaction interior for semantic/rendered prices; owner short-circuit, ordinal range guard. Lazy index only once if all nonmissing windows exact naive; fallback full scan. Time First<source<=confirmation and both prices strictly interior; no separate healthy flag. Set true never clear.

Handoff: Caller supplies all candidate reactions; invalid evidence not erased before A; partial mutation may survive failure.

### CP323-S20 · engine/pipeline/a_zone_detector.py:26–128

Direction exact validation, copy native Reactions, stable Blue sort int ordinal/source time/str kind, chronology refs. First and Break main arrays and native A confirmation precomputed, independent ordered-naive flags. BlueState and AZone field contracts separate exact/main events; optional presentation fields not acceptance keys.

Handoff: A owns pairing and uses full Blue ordering including invalid/internal; policy/chronology primitives delegated.

### CP323-S24 · engine/pipeline/a_zone_detector.py:731–836

Drop special if ordinary same nonnull Reaction ordinal. Latest ordinary strictly earlier source (first equal max), discard if its first strict stop from next source main until special First is at/after special Blue1 source. Remaining special consumes later-trigger ordinary intersecting integer Blue pair; equal trigger not consumed. Stable source/trigger final sort.

Handoff: No re-cross or older-owner fallback; stop query and visibility distinct.

### CP323-S34 · engine/pipeline/s_zone_detector.py:80–176

Copy inputs, sort A by Break main/source int; validate inclusive range, derive half-open end. Initialize physical audit/windows and stopped-A lookup. First valid Reset Blue formation per ordinal, including internal. Trend chronological sorted tuples distinct from original order; optional ordered-naive confirmations and valid monotonic First indexes. Opposite confirmation keyed First last wins; exact Reset sort/owner map; public Blue excludes invalid/internal.

Handoff: Native default confirmation may fallback. Do not equate original ordinal with sorted confirmation rank or collapse physical pair by First.

### CP323-S35 · engine/pipeline/s_zone_detector.py:201–251

A ordinal range checked; price via as_decimal/policy. Strict stop from max(start,range_start), lower half-open to range end; indexed nonempty miss null, unindexed nonempty scan miss null; only empty lower scan main from lower_bound(original start) bounded stage. Main fallback duplicates timestamp.

Handoff: Exact lower evidence not guaranteed by main fallback; different start callers preserved.

### CP323-S38 · engine/pipeline/s_zone_detector.py:1248–1304

Clear windows/audit then audit every A before eligibility. Skip owned/cycle older or equal after output; next A confirmation bound strict stop<next. Compute first Order match before next bound rejection. Open ownership before candidate resolution; null leaves open. Success closes at max(A stop,decision+microsecond), advances cycle source; stable final sort.

Handoff: Initial audit includes later ineligible candidates; accepted A filtering downstream. Wrapper may mutate before exceptions.

### CP324-S02 · engine/pipeline/s_zone_detector.py:253–276

Resolved first Order-backed zone delegates builder with original first physical Order and A stop unchanged.

Handoff: Later canonical Reaction does not replace creation provenance; source decision may use shared accepted Order only in separate reconciliation.

### CP324-S19 · engine/pipeline/s_zone_detector.py:1307–1421

Dedup physical First/Break, prefer nonnull stop_cross over null even if malformed. Require datetime confirmation; supplied tuple len>=3 with datetime element 2 accepted as shape, else compute strict cross; require confirmation<cross. Sort exact event/confirmation/First/Break. Earliest cross>=S source (inclusive), <current decision. Replace Red Order/decision fields, clear Reset; preserve source/A/formation.

Handoff: No local price proof of shape-valid supplied cross; no confirmation relative to S source required; no creation cause change.

### CP324-S20 · engine/pipeline/s_zone_detector.py:1424–1466

Dependency key includes raw geometry and string price/anchor, intrabar optional; set of trend/opposite Break time/side/zero ordinal/key plus exact reset owner, reset-Blue ordinal, public Blue time. Scope and stored decisions fresh.

Handoff: Dependency set dedups; caller supplies current authoritative detector and dirty market.

### CP324-S21 · engine/pipeline/s_zone_detector.py:1468–1490

Type3/4 frontier decision directly. Other types assert Order; lower_bound(max(Order confirmation,range start)) needs a row not later than decision; otherwise null. Max decision/Order Break, aligned trend Break and confirmation if present.

Handoff: Presence guard not crossing proof or range_end check; prevents simple main-only fallback caching where absent lower evidence.

### CP324-S22 · engine/pipeline/s_zone_detector.py:1492–1525

Validate dirty index inclusive count, scope direction/timeframe/start/range start; dirty timestamp or range end. Same scope min dirty with symmetric dependency difference event; other scope no prior. Key A ordinal/source index/time/str price/stop/optional Order number+geometry+confirmation. Reuse prior only frontier<dirty; otherwise resolve, cache nonnull with settled frontier. Publish scope/deps/decisions after detector success.

Handoff: No null decision caching/current-map hit; wrapper commit distinct from detector mutation. Conditional continuation only.

### CP325-S45 · engine/pipeline/core_utils.py:51–66

as_decimal returns existing Decimal unchanged (isinstance), otherwise Decimal(str(value)). Canonical Order identity and Reaction identity use int First/Break only.

Handoff: No rounding or lexical preservation promise for arbitrary non-Decimal input; no direction/parent key, bounds or identity validation.

Qualified RX-M04, S-M05 and CH03. All earlier evidence preserved. No production, runtime or RAW change. F05/R01/R02 remain open.
