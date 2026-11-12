---
title: Exact comparison result
document_role: evidence
lifecycle: generated
owner: engine-zero-difference-audit
created_at: 2026-11-02T12:27:57+03:30
last_modified_at: 2026-11-02T12:31:27+03:30
---

# Exact comparison result

**PASS:0 stable differences** for the optimization versus the immutable post-repair baseline:22 scenarios, 104 actual cold AFTER runs, 104 exact serialized-byte comparisons and 447 native hook snapshots.

Every recursive ordered/typed comparison traverses actual retained content; a final digest is supporting integrity evidence only. Complete actual stdout/stderr and compressed stable payloads remain in before/, repaired-before/ and after/. The only excluded output telemetry is the root timings value. The additional lexical scanner replaces only that value with null in original stdout bytes, preserving every other byte: numeric spelling, string escapes, whitespace/newline, field presence, object-key order and array order. Missing required cases/repeats, invalid input/command/baseline context or tampered outputs cannot PASS that gate. See discovery/lexical-repaired-before-vs-after.json and collection-policy.json.

Native graph comparison captures Decimal/datetime and container types, ordered fields/collections and shared object aliases. Hooks include complete input seconds/candles and selected market bounds, full-direction E/Blue/A/S and invalid/internal evidence, accepted and S OrderAudit, eligible A, prepared pipeline state, direction-range/visibility and primary results when reached. Every reached hook index/name and decompressed graph byte matches; dynamic stage/key inventories are recorded in discovery/final-comparison-summary.json. Sets are compared as typed canonical membership, preserving aliases. This is selective authoritative semantic state, not every private derived cache. Cache/native identity/fresh-list and malformed-row behavior are additionally pinned by focused tests and owner proof.

**Original versus final boundary:** the original22scenario/44run exact determinism gate remains FAIL in2 repeat cases, solely aggregate multi-regime bridgeOutput mapping-key order. The user delegated a separately shown dict.fromkeys preparatory repair. discovery/preparatory-repair-comparison.json reports22PASS and0 unexpected calculation/type/value/Decimal/array differences. Transitivity with the exact post-repair comparison preserves that content in the final output; original raw serialization bytes are not claimed identical where the disclosed key order changed. Neither baseline nor expectations were rewritten to accept an optimization difference.

Strict/equal boundaries, both directions, parent/B earliest/all selection, native Order identity, residual sort insertion ties, Decimal string precision, partial/malformed native rows and cache freshness are exercised by current tests. CLI supplemental switch/error cases compare exact public stdout/exit code; stderr progress is retained. Arbitrary injected custom magic methods and byte-identical traceback-frame text are outside the native ledger/input contract and are not claimed equivalent. See reviews/independent-candidate-review.md.
