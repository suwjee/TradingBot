---
title: Non-Engine Runtime and Resource Audit
document_role: verification
lifecycle: snapshot
captured_on: 2026-11-20
---

# Non-Engine Runtime and Resource Audit

Baseline `00d34492a6b13831cf76a120887985db9566b470`, TradingBot v2.8.2. Measurements were taken on Windows using Node 26.11.1 and Chrome 157 on the same workstation.

## Audit coverage

The final structural inventory found 1,334 tracked paths outside `engine/` totaling 966,267,417 bytes. It checked eight ZIP central directories, 140 gzip headers and 14 media signatures without extracting archive members. The initial audit recorded five empty historical diagnostic JSON files, which remain evidence of incomplete runs. Its archive CRC and Python AST checks did not distinguish historical copies of Engine Source. The final verification did not repeat those checks or use them as evidence of the Engine scope gate.

The source review covered Chart and Manual Review, alerts and drawing flows, Vite routes, RAW storage and lineage, FARAZ acquisition, startup, release tooling, CI, and maintained documentation. The archive review covered classification and structural integrity. The scan counted 23,158 untracked or generated files by metadata. It skipped the Git database and did not read personal state, acquired RAW or credential values during inventory. The existing Engine ran as an application dependency in isolated integration tests. The audit and the working-tree diff exclude its directory.

| Entry point | Runtime owner and state boundary | Verification |
| --- | --- | --- |
| `scripts/launch.bat` → `scripts/start.ps1` | Windows launcher, Node and Python discovery, npm lockfile, Vite CLI | Launcher syntax and direct invocation arguments |
| `apps/chart/index.html` → `apps/chart/src/main.js` | Chart, drawing and workspace state, timeframe, Tehran time, deferred Algorithm, Alerts and exporter navigation | Chart unit suite and isolated Chrome |
| `/api/candle-files` → `raw-resource-store.js` and `candle-file-response.js` | RAW inventory, digest/sidecar, Append, Cut, transfer, download and response identity | RAW, request and transfer tests |
| `/api/reactions` → `calculation-coordinator.js` and `live-engine-sessions.js` | Fresh application requests, RAW validation, session isolation, SSE, cancellation and worker recovery | Coordinator and session unit tests, Chrome Apply, integration tests |
| `/api/faraz` → `faraz-candle-api.js` | Session-endpoint access, request pacing, retry, cancellation, coverage decision and publication | Mock history/auth and temporary local state |
| `/info/<id>` → `review.html` and Manual Review entry | Serialized report rendering and saved review state | Unit, API report parity and Chrome popup |
| `scripts/git/git.bat` and CI | Runtime policy for production, engineering policy for main, local-state exclusions | Path-policy verification and isolated release fixtures |

## Applied changes

- Load and mount the Algorithm workspace on first navigation or a deep link. Keep its navigation state after first use. A pending load yields to a newer selection or an explicit departure.
- Use one forward pass to normalize and validate chart input. Copy the display history once when extending its last bucket. Merge already chronological RAW in one ordered pass with existing-row precedence, and look up candle times by binary search. Reuse the activity-log date formatter.
- Run Apply, routine Live replays and Live recovery under the same calculation limit. Default to one active calculation per Vite server. Recovery that already owns a slot continues inline. A disconnected Apply releases queued work or cancels owned active work and terminates its progress channel. Subsequent calculations remain fresh. Manual Review retains serialized snapshots for its separate review contract.
- Resolve the exact listed RAW directly for Apply. Check byte identity when work is admitted and again before returning a result. Parse verified selected-range input bytes without repeating the read. Stream candle files from the same descriptor used for headers and close the stream on disconnect. Include file identity and high-resolution change times in the candle response validator.
- Keep FARAZ cancellation and the watchdog active until the response body finishes. Stop sibling requests when a packet fails terminally. Reuse the verified ordered export instead of sorting it again, and use the same staged RAW buffer for integrity verification and hashing.
- Close a FARAZ download stream when its client disconnects. Release the packet plan when the acquisition ends and discard unpublished rows when an export waiting for a coverage decision is cancelled. Count recovery overlaps by advancing through the ordered gaps, preserving the public interval records.
- Start the installed Vite CLI directly from the Windows launcher. Batch Python package discovery and skip repeated npm directory checks on a warm installation. Preserve the native config loader and its existing watcher settings.
- Resolve the watcher, RAW inventory, and chart update contract test paths relative to their test modules so both runner working directories exercise the same files.

## Resource measurements

| Measurement | Baseline | Candidate |
| --- | ---: | ---: |
| Chart startup JavaScript, uncompressed | 833,761 B | 522,322 B |
| Chart startup CSS, uncompressed | 186,655 B | 146,385 B |
| Chart startup JavaScript heap after GC, median | 5.04 MiB | 2.99 MiB |
| Chrome DOM nodes before opening Algorithm | 73,583 | 5,256 |
| Extend and roll over a 1 million-row chart bucket | 4.983 ms and 15.260 MiB | 1.442 ms and 7.631 MiB |
| Merge 150 arrivals into 1 million rows | 152.749 ms and 57.264 MiB | 4.088 ms and 7.631 MiB |
| Merge 100,000 arrivals into 1 million rows | 271.434 ms and 101.092 MiB | 10.459 ms and 8.393 MiB |
| Warm lookup of one RAW item in a 60-file inventory | 3.022 ms | 0.148 ms |
| Idle launcher Node processes | 3 processes and 238.15 MiB private | 1 process and 155.15 MiB private |
| FARAZ coverage summaries for 200 original gaps | 0.265 ms | 0.010 ms |
| FARAZ coverage summaries for 10,000 original gaps | 163.037 ms | 0.384 ms |

Chart values are three alternating Chrome runs of the built assets with an identical synthetic 650-candle HTTP fixture and fresh browser contexts. The sample also recorded lower Chrome ScriptDuration. Browser scheduling varied during the run. Node timings are medians of seven alternating synthetic runs. Heap deltas are immediate allocations, not resident or retained memory. The isolated launcher comparison disabled polling in both paths and sampled private process memory after the same Vite endpoint became ready. It excludes browser, PowerShell and Engine memory.

The FARAZ overlap timings are wall-clock medians of nine alternating post-warm-up samples. Each input contained fully recovered gaps and gaps split into two remaining intervals. Complete result records matched before timing. The sub-millisecond samples were below reliable Windows process CPU timer resolution. This benchmark excludes FARAZ HTTP, RAW publication and verification.

The first Algorithm visit still builds the complete reference for search, navigation and export. Manual Review retains its sixteen-report count limit. The VMware-compatible watcher default remains in place. These measurements cover specific resource costs and do not establish a machine-wide CPU or RAM ceiling. External FARAZ behavior was exercised through fixtures.

## Cleanup

| Removed ignored artifacts | Directories | Files | Logical bytes |
| --- | ---: | ---: | ---: |
| pytest, Ruff and non-Engine verifier bytecode caches | 3 | 15 | 225,189 |
| Vite build at `apps/chart/dist` | 1 | 5 | 1,023,023 |
| Synthetic browser/catalog outputs and the final synthetic review | 7 | 133 | 1,969,904 |
| Local launcher benchmark logs | 2 | 4 | 257 |
| Total | 13 | 157 | 3,218,373 |

The dry inventory recorded exact targets, ownership, recovery commands or scripts, and logical size before deletion. The PowerShell deletion required ignored, untracked, non-reparse paths and checked for active producers. The protected metadata comparison covered 14 RAW/sidecar files, seven files in the mixed cache, one secret-state file, and 49 Chart test files. Dependencies, baseline assets, reports, screenshots, historical evidence, and temporary directories with unclear provenance remain available. There were no tracked deletions or moves. The measurement is the sum of file lengths rather than a volume-allocation delta.

## Verification

- PASS 374 Chart unit tests and two Vite/Live integration tests. The integration fixtures cover recovery, RAW append parity against fresh Apply, and review snapshot payload parity.
- PASS production Vite build. Vite still warns that the initial JavaScript chunk exceeds 500 kB uncompressed.
- PASS isolated Chrome startup, deep-link navigation, Persian language selection, delayed import cancellation and startup navigation ordering. After cleanup, Chrome opened synthetic RAW, visited Alerts, switched to a 60-second chart with 55 displayed candles, made two Apply calls with distinct IDs and the bypass header, and rendered the second report in a Manual Review popup. Chrome reported no JavaScript exceptions and one 404 resource warning.
- PASS Windows PowerShell launcher argument and working-directory checks, plus the batched dependency probe with one intentionally absent module.
- PASS 31 repository verifier unit tests, 17 Git Manager fixture checks, the release dependency fixture, and the actual policy classification of 26 deliverable paths. Main includes all 26 and production includes the 11 runtime paths. Existing rules exclude all 13 removed local roots.
- PASS Git checked for staged and unstaged differences under `engine/` by path status. The live Engine was exercised only as an application dependency. Direct Engine inspection and verification were outside scope.
- NOT RUN full launcher, full repository anti-drift and the live-checkout release dry run because they directly inspect Engine Source. External FARAZ, VMware and an end-to-end before/after Live performance comparison were not run.

Machine-local measurements and reproduction scripts are under `apps/chart/state/tmp/non-engine-audit-20261120/`. The JSON files include the inventory, final browser results, launcher process roles, RAW lookup, Node timings, and the cleanup ledgers. The browser and build measurements were refreshed during final verification.
