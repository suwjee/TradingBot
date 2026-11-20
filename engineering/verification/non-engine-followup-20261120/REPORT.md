---
title: FARAZ, Live, and Algorithm Runtime Follow-up
document_role: verification
lifecycle: snapshot
captured_on: 2026-11-20
---

# FARAZ, Live, and Algorithm Runtime Follow-up

The comparison starts with the existing uncommitted [non-Engine runtime audit candidate](../non-engine-runtime-20261120/REPORT.md) on `00d34492a6b13831cf76a120887985db9566b470`. Verification uses Windows, Node 26 and isolated Chrome 157. The Engine was exercised through the application boundary. No Engine Source or archive was opened for this follow-up.

## FARAZ status requests

The browser schedules the next status poll after the current one finishes. It polls at 5 seconds in the foreground exporter or while the login flow is waiting, 15 seconds in a foreground Chart with the exporter closed, and 60 seconds in an inactive tab outside login. The exporter clock stops while its panel or tab is hidden. Focus or visibility restoration can refresh status immediately.

The server shares passive probes for the current session file identity and reuses the result for up to 30 seconds. Explicit checks invalidate older passive state and verify using the requested symbol. Pending passive consumers wait for an explicit check against the same file identity before starting the next shared passive probe. Replacement, deletion and logout cannot restore a stale successful response. Capture and shutdown tests use synthetic storage state.

| Three open Chart tabs in isolated Chrome, 12 seconds | Before | After |
| --- | ---: | ---: |
| Local status GET requests | 9 | 3 |
| Simulated upstream history and profile requests | 18 | 2 |

This browser run used a synthetic session file and mocked upstream response. A separate deterministic HTTP test sent nine passive status requests through the service at three synthetic times and reproduced 18 upstream calls before and two after. Browser scheduling checks also covered focus, visibility, the exporter clock, and slow responses. Real FARAZ and personal session data were not used.

## Live ownership and cancellation

Apply, Live replay and recovery retain the shared calculation limit. Each HTTP client owns its own progress and cancellation. Identical in-flight calculations may share work while preserving the remaining callers. The last disconnect removes queued work before RAW validation or cancels active reads, range transport and worker work. The slot remains owned until its work exits. Queued cancellation preserves the existing Live checkpoint. Live still validates RAW and computes a fresh result for an update.

A deterministic multi-tab fixture blocked one recovery RAW read, queued an abandoned request and left another tab waiting. Closing the first two requests cancelled the admitted read and admitted the surviving tab. It recorded two admitted full recovery reads, one cancelled read and zero admitted reads for the abandoned queued tab. Identical live requests shared one admitted read and the surviving request received its report and progress. These counts describe recovery fixture reads, not all filesystem I/O or live-market throughput.

The cancellation path closes progress for an attached observer. If the GET arrives late, it receives the buffered terminal event and EOF. A repeated GET receives HTTP 204 while the bounded cancellation record remains. The Windows named-pipe fault test also verifies that a failed transport cancels its owned consumer and waits for exit before releasing the calculation slot.

## Algorithm first navigation

The navigation and bilingual/mirrored search retain the complete index. The page mounts the requested article and retains logical navigation, scroll and disclosure state. Full HTML and PDF export build every article on demand.

| Chrome overview with the module preloaded, seven alternating runs | Before | After |
| --- | ---: | ---: |
| Median synchronous first open | 222.9 ms | 105.9 ms |
| Median two-frame display proxy | 231.5 ms | 111.7 ms |
| Article descendant elements | 34,593 | 137 |
| Mounted sections | 14 | 1 |
| Median used heap after explicit GC | 3.95 MiB | 2.41 MiB |
| Median initial search handler | 0.6 ms | 0.6 ms |

A one-off Persian/Bearish full HTML export sample took 56.3 ms before and 290.9 ms after. Export now does its full rendering when requested. All 14 article payloads matched after normalization. PDF verification checked the complete generated document and the print handoff. Native PDF saving was not exercised. Isolated Chrome also verified a mobile deep link, focus and Escape behavior, URL history, search result parity, restored disclosures and clipboard output.

## Verification evidence

- PASS all 392 Chart unit and Windows Vite integration tests with synthetic RAW. The FARAZ-focused suite covered 66 tests and the Live/transport/progress selection covered 54 tests.
- PASS Vite production build. The warning for a startup chunk larger than 500 kB remains.
- PASS isolated Chrome workstation smoke with two distinct fresh Apply IDs and Manual Review rendering. It reported no JavaScript exceptions and one existing resource 404 warning.
- PASS syntax, Git diff and Engine path-status checks. HEAD and the index are unchanged.
- PASS scoped release policy classification of the combined working tree, including the earlier audit. Main includes 34 eligible paths and production includes the 15 runtime paths. The full checkout release dry run remains outside scope because it directly inspects Engine Source.

Machine-local evidence and browser reproduction are in `apps/chart/state/tmp/non-engine-followup-20261120/` and `apps/chart/state/tmp/non-engine-audit-20261120/`. The latter contains `algorithm-first-open.mjs` and `algorithm-first-open-final.json`. The maintained contracts are in [technical architecture](../../docs/architecture/technical-architecture.md) and the [UI/UX reference](../../docs/architecture/ui-ux-reference.md).
