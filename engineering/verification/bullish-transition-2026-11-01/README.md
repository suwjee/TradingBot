---
title: PH3 bearish-to-bullish transition verification
document_role: evidence
lifecycle: historical
owner: engine-verification
created_at: 2026-11-01T16:18:21+03:30
last_modified_at: 2026-11-01T16:24:27+03:30
---

# PH3 trend transition

The approved change stops the bearish regime on the first strict stop of a confirmed PH3, retains its historical objects, and starts independent bullish calculation at the complete crossing candle. The first new bullish Reaction has a narrow bootstrap exception; subsequent Reset and native downstream rules remain active.

PL circle default radius is 4px. MBL display ends at the earlier strict crossing or 400 actual calculation candles. The green dashed transition line and 20px upward icon are rendered from finalized Engine metadata. The icon targets actual candle 50 (start=1) with its bottom 100px above that candle's High.

The implementation is in the existing Engine owners and existing Chart rendering files. Vite's current content fingerprint already covers every changed production Engine file, so no cache-owner change was needed. No bullish primary mirror was added.

## Verification

| Check | Result | Evidence / scope |
| --- | --- | --- |
| Engine unit suite | PASS | 210 tests; baseline 193 |
| Chart unit suite | PASS | 255 tests; baseline 250 |
| Documentation verifier unit suite | PASS | 31 tests |
| Production Chart build | PASS | Vite reports a greater-than-500KB chunk warning |
| Exact accepted Reference reconstruction | PASS | Both references dynamically match all discovered production Python owners |
| Repository anti-drift | PASS | Full mode: zero errors, warnings or information diagnostics |
| Full October USOIL 5s RAW at 30s | PASS | Before/after CLI, both directions |
| Actual local HTTP calculation | PASS | Complete RAW request, bearish initial direction, HTTP 200/cache miss; direction payloads exactly match CLI |
| Independent old-engine historical prefix | PASS | All eleven calculation/primary arrays match; only approved MBL cap and stopped-cycle status differ |
| Physically isolated fresh suffix | PASS | No earlier RAW row supplied; every output field matches the integrated bullish output after absolute-index projection |
| Existing request compatibility | PASS | One-day USOIL input: bullish-only and disabled-primary direction payloads exactly match the prior Engine |
| Browser rendering | PASS | Chrome/Playwright, 1700x1050 and 1100x820, no page errors |
| Fixed-pixel placement | PASS | 20x20px icon; exactly 100px from target High to bottom |
| Broader independent market correctness | NOT RUN | No claim beyond the supplied USOIL case and the stated bounded compatibility input |
| Knowledge Vault capture | NOT RUN | Maintained capture skips uncommitted/dirty paths; read-only check reports needs_review |
| Commit / push / release | NOT RUN | Not requested |

Browser plugin was unavailable; regular Playwright was used. The real Chart rendered the freshly calculated complete RAW payload through a test-only in-browser export; no debug hook was added to production. A separate actual HTTP calculation validated transport, source fingerprint and Engine execution.

## Exact USOIL acceptance

- PH1: 2026-10-07 00:13:30, 90.034.
- PH2: 2026-10-07 03:55:30, 90.289.
- PH3: 2026-10-07 04:47:00, 90.573.
- Strict stop / new bullish context: 2026-10-07 16:57:30 Asia/Tehran.
- FirstRed and BoxTop source: 16:57:30; BoxTop 90.622.
- BoxBottom source: 16:59:30; BoxBottom 90.364.
- Break: 17:00:30.
- Icon target: 17:22:00, absolute calculation index 10403, High 90.549.
- No PH4 or later bearish cycle is exposed after the global transition.

The full-month comparable CLI runs took 90.04s before and 107.90s after. The new execution includes independently recomputed historical prefix and fresh bullish suffix. This is a behavior change, not a zero-difference optimization.

## Independent review

The reviewer found three Important regressions. All were reproduced with failing tests and corrected:

1. A future transition must not replace an earlier presentation window. The related pre-transition status is also covered.
2. Explicit bullish PH circle-radius customization must survive layout and drawing.
3. Historical paint, hit regions and selection must share the same boundary.

No reviewer finding remains deferred.

## Ownership and preservation

Implementation was isolated in a managed worktree. Transfer to the original live checkout completed with original-HEAD byte checks for changed tracked files and refuses collisions for new files. Existing dirty engineering documents, GPT material, archives and engine.zip are outside this task.

Both accepted Algorithm References contain the approved rule delta, updated source manifests, regenerated changed-owner AST indexes and exact Source. Previously accepted later October-cycle / PH4+ examples are marked historical under the new global transition.

The standalone Knowledge Vault intentionally excludes standalone PH/PL/MBL concepts. Its maintained source-capture workflow accepts only clean committed files; this task does not bypass that workflow or commit user work. Vault capture/review remains pending a later authorized commit. The unrelated pre-existing Vault Gemini output is preserved.

## Artifacts

- [Desktop chart](chart-desktop.png)
- [Laptop chart](chart-laptop.png)
- [Implementation plan](plan.md)
- [Reference synchronization helper](sync_references.py)
- [Bounded compatibility evidence](compatibility.json)
- [Input isolation evidence](isolation.json)
- [Browser geometry evidence](browser-qa.json)

Full runtime outputs and derived immutable-input test copies remain in the Chart-owned ignored task directory, rather than being copied into a release package. Graphify was not run.


## Live checkout completion

The original X:/My-Projects/TradingBot checkout now contains the verified changes. All 13 pre-existing dirty/untracked files and the authoritative RAW are byte-unchanged. Engine 210, Chart 255, exact reference reconstruction and full anti-drift passed again in that checkout. The existing Chart service on port 5173 was restarted with its maintained dev-server entry point after verifying no active child work. Its renderer is current and a bounded real HTTP request from October 1 through October 7 17:23 returned 200 with the expected complete transition/initial-Reaction acceptance anchors. See [live runtime evidence](live-runtime.json). Refresh the browser and Apply the indicator to calculate the desired current range.
