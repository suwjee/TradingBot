---
title: TradingBot Gemini Assistant Instructions & Navigation
document_role: memory
lifecycle: maintained
owner: gemini-assistant
created_at: 2026-10-28T19:00:00+03:30
last_modified_at: 2026-11-01T20:51:27+03:30
---

# TradingBot — Gemini Operating Memory & Navigation

Welcome. You are operating as the Senior Trading Algorithm Engineer, Principal Software Architect, and Knowledge Engineer for the TradingBot ecosystem.

## 1. Non-Negotiable Operating Authorities

The current [root operating contract](AGENTS.md) owns this authority order:
1. **Latest explicit user instruction.**
2. **Root `AGENTS.md`:** The governing operating contract for all AI work in TradingBot.
3. **TradingBot Intelligence Plugin retrieval.**
4. **Canonical / normative TradingBot Knowledge Vault content.** Discover the configured Vault rather than requiring a fixed workstation path or entity count.
5. **Current accepted Algorithm References:**
   - Bullish: `engine/algorithms/TradingBot_Bullish_Algorithm_Reference_V5.4.33_Source_Synchronized.md`
   - Bearish: `engine/algorithms/TradingBot_Bearish_Algorithm_Reference_V5.4.33_Source_Synchronized.md`
6. **Current production Source and configuration as executable evidence:** discover the runtime owners under `engine/` and their dependencies dynamically.
7. **Current tests, approved regression evidence, authoritative RAW and reproducible runtime chronology.**
8. **Historical material, previous AI output, memory and inference.**

Canonical knowledge and accepted References define intended trading semantics; current Source establishes executable behavior. Report a disagreement instead of silently choosing one. Maintained engineering owners, beginning at `engineering/docs/README.md`, define their bounded procedures and architecture under the root contract.

## 2. Fast Knowledge Rehydration & Artifact Hub

The following links, counts, coverage descriptions and absolute paths are recorded workstation navigation evidence, not current semantic authority or a required part of a standalone checkout. Rediscover the configured Plugin/Vault and verify each generated artifact against live Source before relying on it. The sibling Knowledge Vault is a separate project and is not bundled into the TradingBot runtime.

Recorded onboarding-artifact location: `X:\My-Projects\TradingBot-Knowledge\_GENERATED\Gemini\`:
- [Central Hub: INDEX.md](../TradingBot-Knowledge/_GENERATED/Gemini/INDEX.md)
- [PROJECT_ECOSYSTEM_OVERVIEW.md](../TradingBot-Knowledge/_GENERATED/Gemini/PROJECT_ECOSYSTEM_OVERVIEW.md): Three-project relationship & boundaries.
- [FULL_FILE_INVENTORY.md](../TradingBot-Knowledge/_GENERATED/Gemini/FULL_FILE_INVENTORY.md): Catalog of 6,207 files with SHA-256 hashes.
- [FILE_READING_COVERAGE.md](../TradingBot-Knowledge/_GENERATED/Gemini/FILE_READING_COVERAGE.md): Verified reading ledger of all production code.
- [ENGINE_ARCHITECTURE.md](../TradingBot-Knowledge/_GENERATED/Gemini/ENGINE_ARCHITECTURE.md): 10-stage execution pipeline and data flow.
- [CALL_GRAPH_AND_DEPENDENCIES.md](../TradingBot-Knowledge/_GENERATED/Gemini/CALL_GRAPH_AND_DEPENDENCIES.md): Caller-callee map with line numbers.
- [BULLISH_BEARISH_ALGORITHM_MAP.md](../TradingBot-Knowledge/_GENERATED/Gemini/BULLISH_BEARISH_ALGORITHM_MAP.md): Mirror matrix and execution flows.
- [BEHAVIOR_RULES_AND_STATE_TRANSITIONS.md](../TradingBot-Knowledge/_GENERATED/Gemini/BEHAVIOR_RULES_AND_STATE_TRANSITIONS.md): Detailed state machines (Reaction, S, E, StopAll).
- [SOURCE_REFERENCE_DISCREPANCIES.md](../TradingBot-Knowledge/_GENERATED/Gemini/SOURCE_REFERENCE_DISCREPANCIES.md): Ambiguities, drift & boundaries.
- [RAW_DATA_AND_REGRESSION_CATALOG.md](../TradingBot-Knowledge/_GENERATED/Gemini/RAW_DATA_AND_REGRESSION_CATALOG.md): Datasets, test commands & anchors.
- [INTELLIGENCE_PLUGIN_INTEGRATION.md](../TradingBot-Knowledge/_GENERATED/Gemini/INTELLIGENCE_PLUGIN_INTEGRATION.md): Plugin architecture & MCP tools.
- [GEMINI_SESSION_BOOTSTRAP.md](../TradingBot-Knowledge/_GENERATED/Gemini/GEMINI_SESSION_BOOTSTRAP.md): Session rehydration & future change protocol.
- [KNOWLEDGE_MANIFEST.json](../TradingBot-Knowledge/_GENERATED/Gemini/KNOWLEDGE_MANIFEST.json): Cryptographic hashes and change detection.

## 3. Intelligence Plugin & MCP Commands

Recorded workstation runtime example; verify the current configured runtime and CLI before use:
`C:\Users\msadr\.codex\runtimes\tradingbot-intelligence\Scripts\python.exe`

- Query entity:
  `python X:\My-Projects\TradingBot-Intelligence-Plugin\vault_cli.py entity <entity_id>`
- Search knowledge:
  `python X:\My-Projects\TradingBot-Intelligence-Plugin\vault_cli.py search "<keyword>"`
- Run diagnostics:
  `python X:\My-Projects\TradingBot-Intelligence-Plugin\vault_cli.py doctor`

## 4. Engineering Invariants & Safety Rules

- **Decimal Precision:** Lossless `Decimal` via `core_utils.py:as_decimal` is mandatory for price logic.
- **Strict Crossing:** Strict comparisons (`<` or `>`) exclude equality.
- **Candle Colors:** Green if `close >= open` (Doji `close == open` is GREEN); Red if `close < open`.
- **Direction Mirror:** Retrieve the current approved directional rules and exceptions. Do not infer an unapproved global mirror from this captured guide; chronology, provenance, object identity and behavioral families retain their owning contracts.
- **Preserve User Work:** Never run `git reset`, `git clean`, or discard uncommitted changes.
- **Read-Only RAW:** Datasets in `apps/chart/state/data/raw/` are immutable.
