---
title: Bullish primary mirror and alternating-regime verification
document_role: evidence
lifecycle: historical
owner: engine-and-chart
created_at: 2026-11-01T19:22:42+03:30
last_modified_at: 2026-11-01T19:28:22+03:30
---

# Approved bullish primary mirror

The bullish PL/PH/MBL mirror and PL3-to-bearish transition are implemented. User clarification retains 28x28 CSS icons and changes both clearances to500px: bullish icon bottom above candle High, bearish icon top below candle Low. Targets remain the actual50th candle counting start1. Bullish PL uses pink upward double chevrons below Low; PH uses a green4px-radius circle above High. Existing explicit appearance settings remain supported.

Primary calculation reuses the approved state machine through price reflection with original RAW indexes; native Order identity, causes, behavioral families and market Doji color are retained. Native confirmed PL ownership and parent-stop Orders mirror PH. Every reversal starts independent input at the complete crossing main candle; only the first Reaction uses the new-regime bootstrap. Historical segments retain their own right-end bounds; Chart never detects trading events.

## Current verification

| Check | Status | Scope |
|---|---|---|
| Engine unit tests | PASS | 242 current tests, including bullish primary/native PL, bearish bootstrap, chronology, reset and repeated contexts |
| Documentation verification tests | PASS |31 current anti-drift tests;273 combined with Engine |
| Chart suite | PASS |260 current tests, including marker geometry/colors, shape opacity, aggregate offsets and report metadata exclusion |
| Production build | PASS | Existing large-chunk warning remains |
| Exact References | PASS | Both reconstruct all14 dynamically discovered current Python owners |
| Full anti-drift | PASS | Zero diagnostics |
| Full supplied RAW CLI | PASS |309266 USOIL5s rows,57840 main30s candles, both initial-direction request |
| Actual complete-source HTTP | PASS |HTTP200, cache miss; finalized direction results exactly equal CLI |
| Independent fresh regime inputs | PASS |207697 bullish RAW rows and47375 subsequent bearish RAW rows, physically separate derived files; every compared output field equal |
| Protected bearish history | PASS | All16 original pre-first-reversal fields exactly equal the pre-task Engine output |
| Independent RAW chronology checks | PASS |23 PH/PL extrema and native Order stops,7 MBL extrema,2 primary3 stops and actual-candle50 targets |
| Disabled-primary compatibility | PASS | Old/new both-direction outputs identical on3000 authoritative input rows |
| Browser | PASS | Actual Chrome/Playwright Chart, desktop and laptop;28px size/500px clearance, pink PL/green PH, hide/restore, no page errors |
| Independent code review | PASS | Engine review+242 tests; Chart review+54 focused tests and actual drawIndicator VM clipping/hiding |
| Broader independent market validation | NOT RUN | No claim of all-symbol/all-timeframe correctness |

The independent Chart review found two regressions: segment metadata appeared as Manual Review records, and explicit circle opacity followed point kind. Both were reproduced with failing tests and fixed. Color follows PH/PL; opacity remains a shape setting. Manual Review excludes segment containers and retains finalized aggregate records.

Browser plugin was unavailable, so regular Playwright with installed Chrome was used. Browser-only exports were injected in the test response; no production debug hook was added. A fixed500px clearance can place an icon outside a short plot; pixel anchors remain exact and price-scale behavior is unchanged.

## Bounded market observations

The original bearish PH1/2/3 sources remain October7 at00:13:30,03:55:30,04:47:00; PH3 price90.573. Bullish start remains16:57:30, with FirstRed/BoxTop16:57:30, BoxBottom16:59:30 and Break17:00:30.

The new bullish regime ends when PL3 price99.822 first stops on October27 at20:01:20, inside the20:01:00 main candle (Tehran). Bearish calculation starts with that complete main candle. Its50th actual candle is20:25:30, Low99.978. This is bounded verification evidence, never a production special case.

Diagnostic full-CLI wall times were212.74s before and181.19s after; complete-source HTTP took152.90s. These are comparable-input observations with ordinary cache/load variation, not a controlled optimization or global performance claim.

## Preservation and delivery

Implementation began from preserved dirty worktree bytes. Live files are guarded against task-start originals. Two live architecture documents contained prior user authority refinements; those were three-way merged with the task's single new paragraph, preserving all prior nonblank content except the intentionally updated modification timestamp. The merge evidence records the original hashes. Authoritative RAW is read-only; derived verification inputs stay in ignored task scratch.

No staging, commit, push, release or Graphify execution occurred. Accepted References and maintained owner paragraphs are synchronized. The scoped Knowledge Vault still excludes standalone PH/PL/MBL concepts; its maintained capture workflow requires a later authorized clean committed source and is pending. The existing REF-REACTION-SUCCESSOR narrative ambiguity was not changed by this feature.

## Evidence

[Plan](plan.md) | [RAW checks](raw-acceptance.json) | [Independent inputs](isolation.json) | [Compatibility](compatibility.json) | [Browser measurements](browser-qa.json) | [Preserved live documents](merge-preservation.json)

[Bearish start](bearish-start-desktop.png) | [Laptop](bearish-start-laptop.png) | [Bullish PL](bullish-pl.png) | [Bullish PH](bullish-ph.png) | [Red icon](bearish-icon-detail.png) | [Green icon](bullish-icon-detail.png)

## Completed live delivery

Initial guarded transfer completed for32 task files, followed by two final evidence summaries, preserving30 other initially dirty/untracked live files byte-for-byte. The two edited architecture documents retain the user's prior authority refinements. Live Engine242+documentation31 tests, Chart260 tests, build, exact References and full anti-drift all PASS. Port5173 was restarted through the maintained hidden dev-server entry point after confirming no active calculation child. Served renderer is28px/500px. A fresh bounded bullish HTTP request returned200/cachemiss with primaryVersion1.4.0. All production Engine bytes equal the verified worktree. The live Source fingerprint was independently recomputed; its difference from the worktree comes only from the unchanged transport helper's LF/CRLF byte style.

[Delivery checks](delivery.json) | [Live acceptance](live-acceptance.json)
