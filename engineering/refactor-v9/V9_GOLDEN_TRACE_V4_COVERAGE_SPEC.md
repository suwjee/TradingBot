# TradingBot V9 Golden Trace — observer v4 and coverage contract

**Status:** `PARTIAL`, no unconditional `TOOLING VERIFIED` claim.

## Stable event and sidecar contract

- Stream format: compressed UTF-8 JSONL, schema `tradingbot.v9.internal-observer.v4` for test-only observer v4, sequential `event_ordinal` from 1, deterministic JSON serializer and gzip `mtime=0`.
- Record contains `stage`, `method`, `direction` when identifiable, input and result representation with explicit support status, selected pre/post state, optional accepted entity provenance, raw-time fields, candidate rejection reason when observable, and full ordered selected ledger snapshots at authoritative `detect`/`rebuild_accepted_order_audit` boundaries.
- Price-sensitive Decimals are always represented with `{'$decimal': str(value)}`; no float conversion or rounding is done by trace.
- Lossless for supported primitive, sequence, dict and dataclass fields in emitted snapshots. Mapping insertion order and array order are preserved. Set iteration order is retained and explicitly labeled **noncanonical**; no destructive sorting or canonicalization of original event records.
- Large Candle/Candidate collection snapshots are gzip JSONL sidecars with index/digest/size/element count. Selected authoritative boundary snapshots use **fresh** Candidate copies, not first-use-only stale references. Large immutable raw chronology is separately pinned in unmodified SHA-checked chronology sidecars.
- Manifest records gzip SHA256 and uncompressed event JSONL SHA256, row/event counts, stage family counts, deterministic sample index byte offsets, sidecar metadata and unsupported serialization counts. Independent verifier must compare all of them before trusting a trace.

## What is NOT established by the current observer

1. Wrappers select specific method returns, not every mutation site or every branch decision within a method. `event_ordinal` is the order of trace *emission* at method-return points; it is not automatically a complete global chronology of all lower-level decision events.
2. Some `input` payloads or deeply nested custom objects can have `partial_unrepresentable` and must remain coverage gaps. Proving a selected result return is equal does not imply all hidden mutations are equal.
3. OrderAudit cache/index implementation-only call counts may differ Original vs V8.1. The selected-comparison tool excludes precisely named implementation families with explicit disclosure; their semantic state transitions cannot be assumed equal solely because excluded.
4. Source AST audit finds 103 possible mutators outside directly traced wrappers (98 function name/basename keys); short real OIL complete native run observed 81 such keys executed, with 141,332 Original and 140,901 V8.1 calls. The AST may overreport caching/derived helper mutations, so the list requires owner-specific audit and must not be presented as proven 103 behavior mutations.
5. v4 OIL15k strict trace comparison shows 25/4012 sampled events differ by `set` iteration order; diagnostic membership-only view shows those 25 have identical members, but 1,100 intermediate input changes remain unverified. Original event order and data are kept untouched; this is a diagnostic only, not full semantic PASS.
6. All arbitrary Live continuation states and unobserved lifecycle mutations are NOT proven equivalent by any finite selected static snapshot suite.

## Verification and release gate

- Run **both directions in one native calculation** for pinned full RAW extents; assert stable output exactly equals frozen Golden bytes and timing schema matches before interpreting a trace.
- Original and unchanged V8.1 are separate engine source trees. Instrumentation ON/OFF parity is mandatory for both, including repeated Live/error/rollback tests.
- First divergence must identify earliest comparable actual event (stage, direction, raw timestamp, stable parent/entity ID, field, provenance) and report missing/unsupported coverage rather than invent equality.
- Do not certify `TOOLING VERIFIED` without individually verifying state owners, complete mutation-event chronology, source identity, tie handling, candidate rejection coverage, and all specified V9 tests. Until then overall status is `INCOMPLETE`, with `TRACE_COVERAGE_PARTIAL`.