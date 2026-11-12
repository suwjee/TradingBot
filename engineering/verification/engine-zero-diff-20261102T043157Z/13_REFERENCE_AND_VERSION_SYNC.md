---
title: Reference and version synchronization
document_role: evidence
lifecycle: generated
owner: engine-zero-difference-audit
created_at: 2026-11-02T12:27:57+03:30
last_modified_at: 2026-11-02T12:31:27+03:30
---

# Reference and version synchronization

Both accepted local Bullish/Bearish V5.4.33 Source_Synchronized documents retain their accepted identities and existing created_at/history. Exact current changed Source bodies, SHA-256, byte/LF counts, Source manifest/version rows and AST symbol indexes are regenerated; a truthful unreleased implementation audit note distinguishes the preparatory repair and optimization. Existing trading teaching text and pre-existing semantic discrepancies are preserved.

Source modules changed: `engine/bridge/trading_pipeline.py`, `engine/pipeline/order_audit_engine.py`. Bridge public API1.13.0 remains unchanged; its existing implementation1.16.0 ->1.16.1. OrderAudit internal Source version1.8.1 ->1.8.2; no public serialized version field changes. Exact final hashes are in discovery/source-manifest-final.json, source patches in source-diffs/. No unrelated module metadata changes.

The maintained verify_order_references.py verifier recovered every dynamically discovered production file from **both** References, verified exact bytes/hash/LF and compiled recovered modules: PASS; full log discovery/final-references.log. Anti-Drift unit/full and final Engine tests were rerun after synchronization: PASS. This establishes exact local reconstruction, not trading-semantic consistency. Canonical Vault/Plugin intended semantics and exclusions are unchanged; no clean-source Vault capture/synchronization or new primary material was requested/performed. The older Vault executable pins remain explicitly stale relative to current local Source.
