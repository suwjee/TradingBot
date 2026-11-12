---
title: Bullish Setup Annotation Verification
document_role: evidence
lifecycle: historical
owner: engine-and-chart
created_at: 2026-11-03T00:33:50+03:30
last_modified_at: 2026-11-03T00:51:54+03:30
---

# Bullish setup annotations

The approved bullish teaching is implemented as a calculation-owned stage after accepted native behaviors/primary structures. It publishes schematic entry, stop and 4R target levels, scoped T/F assessments and reference-break provenance. The Chart renders editable indicator-owned schematics and status labels. Manual Long/Short drawings remain separate. No trade execution, simulation, sizing, PnL, target-hit or position-management ledger was added.

The final clarification is authoritative: the sole direct entry without waiting for another behavior is the first StopAll-1 behavior -> F -> its confirmed StopAll-2. All other eligible StopAll and PL entries use the first qualifying S/E confirmation candle Close. The first T family has entry priority. Repeated-prefix exclusion, causal overlapping native chains, parity failure, larger movements and fixed PL-to-StopAll-1 reference highs are calculated in Engine, not the browser.

## Verification

| Check | Result | Evidence |
| --- | --- | --- |
| Initial Engine baseline | PASS, 330 tests | [Baseline log](../../../apps/chart/state/tmp/bullish-setups-engine-baseline.log) |
| Final Engine unit/contract suite | PASS, 365 tests | [Final Engine log](../../../apps/chart/state/tmp/bullish-setups/engine-final.log) |
| Initial Chart baseline | PASS, 270 tests | [Baseline Chart log](../../../apps/chart/state/tmp/bullish-setups/chart-before.log) |
| Final Chart unit/contract suite | PASS, 275 tests | [Final Chart log](../../../apps/chart/state/tmp/bullish-setups/chart-final.log) |
| Production build | PASS | [Build log](../../../apps/chart/state/tmp/bullish-setups/build-final.log) |
| Final native RAW replay | PASS | [Runtime/hash evidence](../../../apps/chart/state/tmp/bullish-setups/final-runtime.json) |
| User acceptance anchors and exact reference High | PASS | [RAW verification](../../../apps/chart/state/tmp/bullish-setups/raw-verification.json) |
| Native upstream and bearish compatibility | PASS | Every pre-existing field/array under directions equals the pre-change baseline after removing only the six new annotation fields, including independent regime segments |
| Browser interaction | PASS, 7 check groups | [Browser QA](../../../apps/chart/state/tmp/bullish-setups/browser-qa.json) |
| Repeated setup calculation on real native inputs | PASS, two contexts | [Determinism evidence](../../../apps/chart/state/tmp/bullish-setups/stage-determinism.json); identical results on both executions of each accepted native context |
| Documentation governance and verifier tests | PASS, zero diagnostics and 31 tests | [Changed-files check](../../../apps/chart/state/tmp/bullish-setups/anti-drift.json), [verifier tests](../../../apps/chart/state/tmp/bullish-setups/anti-drift-unit.log) |
| Source-aware cache invalidation | PASS | [Real HTTP fingerprint comparison](../../../apps/chart/state/tmp/bullish-setups/source-fingerprint.json) |
| Accepted Reference exact Source coverage | PASS | Current dynamic discovery and compile/hash comparison: both References contain all 15 current production Python files |
| Syntax, whitespace and local links | PASS | Python AST, JavaScript node --check, git diff --check, report-link validation |
| Pre-existing unrelated work | PASS | [Original-byte guard](../../../apps/chart/state/tmp/bullish-setups/user-work-guard.json): nine pre-existing files outside this task's changes remain identical |
| Generic premium static audit | FAIL on 81 pre-existing findings; 0 new | [Baseline comparison](../../../apps/chart/state/tmp/bullish-setups/ui-static-comparison.json); native-select metadata, dynamic-button detection and existing scrollbar rules were not broadened into an unrelated redesign |

The final suites add 35 Engine cases and 5 Chart cases to the current baseline. Targeted cases cover strict/equality boundaries, native stop-row inclusion, same-event successor ordering, first behavior confirmation versus source time, first-T fallback, ignored-prefix independence and full prior extent, direct-2-only entry, larger PL priority, coincident PL roles, historical-role stability, joined native chains and S-donor resets, immutable inputs, Decimal 4R geometry, horizon clipping and absolute regime/cycle identity. New failures and review counterexamples were watched fail before their corrections passed.

Independent read-only review identified four important issues: inherited F not recording its later stop, an unsupported retrospective-source eligibility gate, local setup cycle IDs after regime offsets, and S-donor ancestry resets. Each was reproduced and fixed with a regression test. Final role-tie, waiting-phase exit, owning-regime isolation and browser overlap/visibility checks were added during self-review. Secondary directional dependency contexts do not publish bullish trend schematics. The browser regression also verifies selected automatic-position handles win over overlapping indicator bodies.

## RAW scope and concrete results

The originally named October-only file was not present. The available authoritative 5s source was `apps/chart/state/data/RAW/FXCM/USOIL/RAW FXCM_USOIL 5S FROM 2026-10-01 22-00-00 TO 2026-11-02 17-33-15.json` (319188 rows). It covers the user's examples. The supported bridge processed the complete supplied source using 30s calculations, initial bearish direction and presentation end 2026-10-31 00:14:55, including the native fresh bullish regime from 2026-10-07 16:57:30. RAW bytes were unchanged throughout the final replay: `c1d39cb0bc37e4d14ddec22b24906331461e438413b7ec9fe268d4203c2f2430`.

The result contains 22 bullish schematic entries and 89 setup assessments (some assessments refer to native objects subsequently owned by primary structures, so Chart status labels are matched only to current public objects). Final setup classifications are separate from native calculation-validity flags.

| Anchor | Anchor source, Tehran | Entry candle, Tehran | Entry Close | Stop Low |
| --- | --- | --- | --- | --- |
| StopAll-1 | 2026-10-14 08:03:00 | 2026-10-14 08:59:30 | 94.637 | 94.552 |
| StopAll-2 | 2026-10-14 09:01:00 | 2026-10-14 09:19:30 | 94.658 | 94.457 |
| StopAll-4 | 2026-10-14 11:42:00 | 2026-10-14 12:09:30 | 94.289 | 94.007 |
| PL-1 | 2026-10-15 05:28:30 | 2026-10-15 06:33:30 | 93.739 | 93.56400000000001 |
| StopAll-4 | 2026-10-16 01:44:00 | 2026-10-16 03:00:30 | 97.524 | 97.372 |
| StopAll-7 | 2026-10-16 05:54:30 | 2026-10-16 06:40:00 | 97.353 | 97.092 |

The frozen reference High is 95.388, owned by 2026-10-14 05:12:30, exactly as taught. The S Blue with source 2026-10-15 06:22:30 is confirmed at 06:33:30. The entry uses that confirmation candle Close 93.739; its explicit close-event time is 06:34:00. Source label time, confirmation event and Close are deliberately distinct.

All 22 setup levels satisfy positive risk and exact Decimal target-minus-entry = 4*(entry-minus-stop); the initial width is 50 chart intervals. Cycle IDs join the projected absolute primary cycles. No market timestamp, symbol or expected price is hard-coded into production detection.

## Browser and presentation

Browser plugin was not available, so the installed playwright-core and headless local Chrome exercised the actual app against the refreshed local server. Requests to candle/drawing/calculation endpoints were isolated in-memory fixtures; the calculation response was the actual verified Engine output clipped only for presentation. No personal Chrome window was controlled and no workstation RAW or drawings were changed by browser QA.

The real Apply flow renders automatic boxes and F labels. Tested interactions include independent target/stop dragging; both horizontal handles; numeric fields; undo/redo; lock; hide and undo; explicit override restoration; pan/zoom; a 640px viewport; indicator disablement; and independent manual drawing creation. R:R text is 10px. Colored fills remain 10%. Fresh calculations retain the existing fresh-presentation contract. No browser runtime/console errors or acquisition/trade requests occurred.

[Initial Engine schematics](../../../apps/chart/state/tmp/bullish-setups/setups-initial.png) · [Edited desktop](../../../apps/chart/state/tmp/bullish-setups/setups-desktop.png) · [Narrow viewport](../../../apps/chart/state/tmp/bullish-setups/setups-narrow.png)

Both existing Vite servers were identified by exact project command lines and checked for active calculation/service children before being restarted hidden with their original ports/host/native loader. [Runtime checks](../../../apps/chart/state/tmp/bullish-setups/runtime-servers.json) confirm 5173/5174 serve current annotation code and the same current source fingerprint. Reload the chart with Ctrl+F5 and apply the calculation again.

## Performance and limitations

The setup stage's first executions accumulated 45.345ms across the two real native contexts. The verification wrapper deliberately repeated each stage and asserted identical results; the production stage has no repeat wrapper. Complete pipeline wall times varied materially across runs (approximately164-373s); the final replay took 178.007s. These shared-workstation measurements do not establish a controlled whole-pipeline speedup or slowdown. The stage reuses immutable strict-cross indexes, builds one main-price index per evaluated regime, and avoids per-frame rebuilds and per-pointer-move persistence in Chart.

The production build emits the existing >500kB minified-chunk class of warning (current JS 790.59kB); no warning threshold was changed. Static audit findings above remain pre-existing. Functional unit/RAW/browser results do not prove universal market correctness or absence of all defects.

The Knowledge Plugin/Vault was consulted for authority/context. Live Source, both accepted local References, maintained architecture/UX/testing documentation and the user's teaching notes are the deliverables of this task. External Vault/Plugin snapshots were not rebuilt; excluded primary-structure material was not ingested. No staging, commit, push, tag, release or deployment was performed.

## Reproduction

Use the supported current runners from the repository root. Pytest was installed into task-local ignored storage rather than changing the global Python environment:

```powershell
$env:PYTHONPATH = (Resolve-Path 'apps/chart/state/tmp/bullish-setups-test-deps').Path
python -m pytest engine/tests/unit -q
python engine/tests/verification/verify_order_references.py
python engineering/verification/bullish-setups-20261102/verify_setup_raw.py --make-browser-fixture
node engineering/verification/bullish-setups-20261102/browser-qa.mjs
```

Run npm test and npm run build from apps/chart. Browser QA defaults to the task server 5180; SETUP_QA_URL can point at the refreshed 5173 server. The exact successful full-RAW command is retained in apps/chart/state/tmp/bullish-setups/baseline-command.json. Runtime payloads/logs/screenshots reside in ignored project-local state, while verification helpers and this curated report are reviewable repository artifacts.
