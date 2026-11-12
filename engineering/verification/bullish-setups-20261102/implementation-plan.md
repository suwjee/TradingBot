---
title: Bullish Setup Annotation Implementation Plan
document_role: evidence
lifecycle: historical
owner: engine-and-chart
created_at: 2026-11-02T19:11:46+03:30
last_modified_at: 2026-11-03T00:51:54+03:30
---

# Bullish setup annotations implementation plan

Goal: Apply the user's approved bullish chart-schematic teaching in indicator calculations without trade execution or changing upstream detector results.
Architecture: A new Engine stage consumes accepted native StopAll/S/E/PL chronology. Bridge projects finalized status/setup records. Chart presents these records through its existing independent manual-position geometry. The server includes the new calculation source in content-based cache invalidation.
Authority: Current user teaching and final clarification in this chat, particularly the sole direct StopAll-2 exception and first-T priority. Existing broader detector rules remain unchanged.
Execution: Inline implementation, TDD, independent final review. The user has explicitly authorized implementation and all necessary tests; no further design approval is required. Preserve dirty work from apps/chart/state/tmp/bullish-setups-before-20261102T190205. No commits, pushes, Graphify, or RAW mutations.

## Requirements

- Bullish only; S/E of every accepted color/number can be a behavior. Use confirmation chronology, not retrospective source timestamps. Entry price is that confirmation candle Close.
- Initially StopAll-1 may enter on its first behavior. Sole direct-entry exception: StopAll-1 gave behavior, then became F, and its StopAll-2 is confirmed; enter at that StopAll-2 confirmation Close without a new behavior. Every other eligible StopAll requires its first post-confirmation behavior. SL is the anchor Low; initial target is 4R.
- Stop after behavior means F; stop without behavior means T. Equality does not stop. A successor confirmed before a stop confirms T. F propagates through the same evaluated parity scope immediately to new members and retrospectively to prior members. Behavior alone never makes F.
- Track causal native StopAll chains, not merely global source order: higher-price StopAll-1/2 can overlap an older StopAll-5/6 chain. Native stoppedBehaviorKey and consumption chronology identify ancestry. Do not restart native numbering at the reference high.
- A later movement repeats the prior movement's complete reached StopAll extent, including F members. Ignore this repeated prefix for fresh entry/parity decisions; assess n+1 onward independently. First confirmed T family has entry priority; use the second family only after the first fails. The initial StopAll-1 behavior path can provisionally choose odd; its direct StopAll-2 exception can provisionally choose even.
- H_ref is frozen maximum High from preceding PL confirmation (or original bullish regime start before any PL) through StopAll-1 confirmation, inclusive. Both families F plus strict High > H_ref requires a larger movement. Retain exact strict-stop/break event provenance.
- A larger numbered StopAll examination beyond the repeated prefix or a larger confirmed PL can provide the next level. PL phase takes precedence when it forms before the waiting StopAll entry. Within a PL sequence, advance from PL-1 to PL-2; independent primary cycles keep native identities/numbering. PL entries wait for their first confirmed S/E and use that PL Low.
- Output only annotations/status and provenance: no fill/PnL/quantity/target-hit/closure/concurrency ledger. Keep upstream native objects immutable. Preserve history-before-view, independent regime boundaries and Decimal prices.
- Presentation: green target/red stop, 10% opacity, initial width 50 chart intervals, 10px R:R text, independently editable prices and time span using existing tools. Automatic schematics remain indicator-owned and distinguishable from manual drawings.

## Task 1: Engine calculation stage

Create engine/pipeline/bullish_setup_engine.py and engine/tests/unit/test_bullish_setup_engine.py.
- Write and run failing cases for first behavior entry, direct-2-only, no-behavior T, behavior+stop F, inherited/retroactive F, first-T priority, repeated n-prefix and independent fresh parity, overlapping chains, strict reference break, PL phase/first behavior, larger PL sequence, confirmation vs source time, same-candle event order, no future lookahead, Decimal 4R, nonpositive risk, deterministic input ordering, immutable inputs.
- Implement a chronological event-driven stage using existing immutable price indexes for strict crossings and maximum queries; keep complexity proportional to candles/events rather than repeated history scans.
- Run targeted tests and existing Engine suite.

## Task 2: Bridge, cache and presentation

Modify engine/bridge/trading_pipeline.py to invoke and project the new stage after primary calculation using full accepted history, then clip presentation only. Preserve bearish output and legacy bullish arrays.
Modify apps/chart/vite.config.js so new Engine module edits invalidate calculations.
Create apps/chart/src/chart/setup-annotations.js plus focused Chart contract/render tests; connect main.js rendering and indicator object edits without browser-side trading decisions. Reuse existing drawing-math helpers for editable visual geometry.
- Verify schema/provenance, absolute-index/regime merging, stable independent IDs, original arrays unchanged, custom overrides, hide/lock, editing prices and width, T/F under labels, disabled indicator and historical clipping.

## Task 3: Regression, references and final review

- Baseline: existing Engine suite PASS330; raw baseline apps/chart/state/tmp/bullish-setups/baseline.json covers October plus subsequent primary calculation context from immutable 5s USOIL source. Full pipeline baseline completed163.9s.
- Replay authoritative RAW through new stage; verify the user's October13-16 structural and behavior anchors and reference High independently. User S Blue 2026-10-15 06:22:30 is its source; native confirmation is06:33:30, so entry uses that confirmation candle Close.
- Run complete Engine and Chart suites, production build, exact upstream-output comparison, determinism and bounded horizon/prefix checks. Run real browser interaction with isolated calculation/drawing endpoints and actual Engine-produced annotation payload.
- Synchronize both accepted References and owning maintained architecture/UX documentation, preserving existing user edits and embedded Source fidelity. Query Plugin for authority; do not ingest excluded primary content into the Vault. Record approved new rule scope and explicit synchronization limits.
- Independent code review; fix important findings, rerun affected checks, final diff and original-byte safety review. Report exact PASS/FAIL/NOT RUN/INCOMPLETE and no universal error-free guarantee.

## Review focus

- Coincident native events and delayed source-time labels must not cause entries before confirmation or use future candle state.
- An ignored repeated-prefix F must not contaminate fresh parity, and failure of the prioritized family must not erase an independently valid fallback.
- Native overlapping chains and repeated PL numbers in independent cycles must not be flattened into one global numbering stream.
- New fields must survive clipped historical segments, save/reload, object overrides, and absolute-index conversion without changing native legacy output.
- Static source fingerprinting must include the new module; stale cached results must not masquerade as a new calculation.

## Completion record

Engine stage, Bridge projection, source fingerprinting and indicator presentation are complete. Final current evidence: Engine365 tests, Chart275 tests, exact Source/Reference fidelity, six real-data acceptance anchors, unchanged native outputs and RAW hash, and seven browser check groups. See verification-report.md for limits and reproduction. Four independent-review findings and the coincident-PL/selected-handle/visibility boundaries were fixed with regression tests. All existing out-of-scope dirty files passed their original-byte guard. No commit/publication was performed.
