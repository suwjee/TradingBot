# PH3 Trend Reversal Implementation Plan

> Execute inline with superpowers:executing-plans; finish with an independent review. User authorized implementation on 2026-11-01. Do not stage, commit, publish, or run Graphify.

**Goal:** Stop bearish calculation at the first strict stop of a confirmed PH3, start isolated bullish calculation at that main candle, and render the requested transition markers.

**Architecture:** Primary calculation owns the globally earliest transition. The existing bridge orchestrates independent prefix/suffix market contexts; the Reaction engine has an explicit first-Reaction bootstrap limited to the new bullish context. Chart renders finalized event metadata, including the actual 50th candle, without detecting trading events.

**Tech stack:** Python Decimal/MarketChronology, existing JavaScript Canvas chart, pytest and Node's test runner.

**Spec:** Current user teaching and clarifications in this chat; the accepted References will receive the approved delta and exact updated Source.

## Constraints

- Preserve original dirty/untracked user files; implement in the managed worktree and transfer only verified task files with original-byte checks.
- PH3 strict stop uses exact supplied lower chronology; equality does not reverse. Any cycle may trigger the global transition.
- Preserve the three approved USOIL PHs and their identity/provenance; PH4 must not be committed.
- New bullish input includes the complete crossing main candle and excludes all earlier candles/state. Only the first bullish Reaction bypasses the previous-leg/Reset context; later Reset and downstream stages remain normal.
- Bearish objects become historical at transition; no post-transition bearish calculation results may leak into output.
- MBL ends at the earlier strict stop or the 400-candle cap, including the latest leg. PL circle default radius is 4px; preserve explicit user appearance customization and bullish PH appearance.
- Transition line: green, dashed, full plot height. Icon: green upward zigzag, 20x20 CSS px, centered on actual candle number 50 (start=1), bottom edge 100px above that candle's High.
- Do not expand the standalone Vault's explicitly excluded PH/PL/MBL concept scope. Synchronize accepted References; disclose any unavailable Vault synchronization.

## Review focus

- Multiple cycles, coincident confirmations, strict equality and intrabar ordering.
- Presentation windows before/after reversal and missing/session-gap candles.
- Bullish-only requests and disabled primary detection retain existing behavior.
- Complete isolation of new state, normal post-first Reset, and absolute public source indexes.
- Stable historical IDs, session-aware 400-candle caps, fixed screen-pixel geometry, and absent 50th candle.

## Tasks

### 1. Primary transition and initial bullish Reaction

Files: `engine/pipeline/PL_PH_detector.py`, `engine/pipeline/reaction_engine.py`, focused Engine unit tests.

- [x] Add failing behavioral tests for first PH3 strict stop, equality, multiple cycles and suppression of PH4 callbacks.
- [x] Add failing tests for isolated initial FirstRed, evolving bottom and subsequent normal Reset.
- [x] Implement a finalized transition record and a narrowly enabled bullish bootstrap; run focused tests and the complete Engine unit suite.

### 2. Independent trend contexts and output

Files: `engine/bridge/trading_pipeline.py`, Engine integration/unit tests.

- [x] Add tests for independent market segments, preservation of public indexes, suffix isolation, presentation horizons, and 400-candle caps.
- [x] Orchestrate prefix/suffix with fresh detectors, publish transition event/50th actual candle metadata, and stop exposing bearish continuation.
- [x] Preserve unaffected request paths and run full USOIL replay; compare old valid anchors and independent fresh-suffix output.

### 3. Chart rendering

Files: `apps/chart/src/chart/primary-structure.js`, `apps/chart/src/main.js`, `apps/chart/tests/unit/primary-structure.test.mjs`.

- [x] Add failing rendering/geometry tests for radius, cap, transition line/icon, absent target and pixel spacing.
- [x] Render the finalized metadata with Canvas vector geometry and stable object identities. Keep existing settings controls.
- [x] Run Chart unit suite, production build and browser visual verification.

### 4. Synchronization and delivery

Files: both current accepted Algorithm References, task verification report.

- [x] Synchronize the approved prose, source blocks and integrity metadata; verify extraction against live bytes.
- [x] Independently review the patch, fix material issues with regression tests, and run required checks.
- [x] Transfer verified task files to the original live checkout only if their original bytes are unchanged; preserve all user edits and verify final diff/runtime paths.

## Baseline and ledger

- PASS: Engine unit baseline, 193 tests; Chart unit baseline, 250 tests.
- PASS: full October USOIL RAW, 30s, both directions, existing bridge; 90.04 seconds. Stored under ignored task runtime evidence.
- Ruling: use the managed worktree for implementation, then apply only task changes to the live checkout, because the user requested changes to their current running project. No Git merge/commit is needed.
- Ruling: preserve appearance overrides and use 4px as the PL default; do not remove the existing radius control or change bullish PH's 12px default.

- Ruling: the maintained Engineering UI/UX Reference already owns the existing design context; avoid a duplicate root DESIGN.md. Keep the approved feature contract in both accepted Algorithm References.
- Final review: three Important findings fixed with witnessed failing tests: presentation-horizon gating, explicit PH radius overrides, and historical paint/hit/selection boundary parity. The related pre-transition status was also pinned and corrected.
- PASS: independent old-engine prefix matches all eleven calculation/primary arrays; only the approved MBL cap and cycle statuses differ. Independent fresh suffix matches every output field after absolute-index projection.
- PASS: full RAW actual HTTP calculation, 200/cache miss; CLI/HTTP direction outputs match exactly. Browser rendering verified on desktop and laptop, with 20px icon and exact 100px bottom clearance.

- PASS: live checkout Engine suite 210, Chart suite 255, reference extraction and full anti-drift; 13 original dirty/untracked files and authoritative RAW byte-unchanged.
- PASS: existing Chart service restarted with maintained dev-server entry point after confirming no active child work; current renderer and a bounded current-source HTTP acceptance request verified on port 5173.
