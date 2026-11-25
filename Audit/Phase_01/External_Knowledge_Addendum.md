# Phase 01 — External knowledge authority addendum

Discovery date: 2026-11-26. The owner supplied both repositories after the original Phase 01 checkpoint. This append-only review supersedes the earlier access limitation only for direct repository reading, not for live MCP invocation or semantic certification.

## Pinned sources

| Repository | Branch | Commit | Commit date (UTC) | Tracked blobs |
|---|---|---|---|---:|
| [TradingBot](https://github.com/suwjee/TradingBot/tree/466eb875070f02cd0dbfb105033422bbe2fd8c70) | main | 466eb875070f02cd0dbfb105033422bbe2fd8c70 | 2026-11-23 | 1414 |
| [TradingBot-Knowledge](https://github.com/suwjee/TradingBot-Knowledge/tree/698b054ae4f2800b22925961df998ae849a21d18) | main | 698b054ae4f2800b22925961df998ae849a21d18 | 2026-10-28 | 204 |
| [TradingBot-Intelligence-Plugin](https://github.com/suwjee/TradingBot-Intelligence-Plugin/tree/f87341bccf6763fca588de7715a00a8511b076d9) | main | f87341bccf6763fca588de7715a00a8511b076d9 | 2026-10-28 | 92 |

The owner's explicit main-first rule remains binding. The Vault provides intended semantics and prior review context, never replacement executable behavior. The plugin is a read-only retrieval service (version 0.3.9, eight documented MCP tools), not a trading engine. Direct GitHub access is verified; plugin runtime installation, doctor, actual MCP calls and configured cross-verification have NOT RUN in this environment. Do not imply access to a running MCP server merely because its repository is readable.

## Currentness comparison

The Vault's own sync-status pins production commit c2e7903890dddfaf8526cb9b11dd1c5e490c7410 captured 2026-10-27. Direct recursive tree comparison against the latest main finds 4/16 identical production/package Python blobs, 9/16 different, 3/16 absent as standalone files. Of 13 operational modules, one matches, nine differ and three are absent. The two directional Reference snapshots differ even though their version labels both read 5.4.33. The current PL/PH/T-F companion is absent at the compared Vault path. This is a byte identity and availability finding, not a proof that the trading rules of every changed file differ.

See [External_Source_Comparison.json](External_Source_Comparison.json) for exact Git blob identities. The Vault explicitly excluded PL_PH_detector from standalone capture and primary semantic review; the older embedded payload does not certify current primary logic. Live and T/F standalone sources are absent in the captured Vault tree. The Vault declares RAW and fixture stores EMPTY_BY_DESIGN and market regression NOT RUN.

## Known semantic review gap

The Vault's Source-Reference-Consistency.md records REF-REACTION-SUCCESSOR: tension between post-confirmation chronology wording and whole-confirmation-candle successor geometry. Preserve this as a historical open review item and recheck both current main source and current accepted references in the relevant extraction phase. It is not yet independently established as a current defect. Other historical resolved discrepancy records must be rechecked, not blindly reclassified. The October validation report's 109 discovered plugin tests (108 passed, 1 skipped), structural checks and installed-runtime observations are historical only.

## Retrieval and handoff

Consult Vault authority, version, source manifest, registry, core invariants, pipeline, workflow and mirror contracts; retain each note's status, authority, scope and warnings. Trace Concept to Algorithm to Source to Mirror to Current Version. Compare the actual implementation directly against pinned latest main, recording intended/actual differences without silently changing either. The plugin documents fail-closed external source verification; the observed snapshot drift prevents assuming that cross-verification against latest main would pass. Do not synchronize or edit either external repository as part of this specification task.

Phase 01 remains complete for baseline discovery. Direct external repository access is now verified; full semantic reconciliation and runtime retrieval remain unverified. Phase 02 may proceed using main; subsequent semantic phases must address relevant discrepancies. The main source and external repos remain unchanged. Only English metadata and documentation are published here.
