# Chart/server calculation boundary audit — 2026-10-05

**Result: no additional confirmed calculation-correctness defect was demonstrated in the reviewed transport/cache boundary.** The accepted selected-range path preserves sparse RAW chronology, so it can supply the valid input that reproduces Reaction finding **RX-02**. That finding remains owned by the Reaction detector; filtering does not manufacture or fill missing market rows.

Read-only forensic scope: HTTP request construction/validation, complete-source versus selected-range authority, Python child invocation, source/content identity, durable result selection and execution coordination. No production source edit, RAW edit, frontend change, server startup, browser operation or named-pipe startup was performed. Diagnostics write only inside `boundary-audit/`.

## Authority and classification

Both active V5.4.24 references, line 47, expressly authorize this distinction: complete chart supplies the original RAW file; selected range supplies only inclusive chart buckets and begins with empty state; CLI bounds filter presentation after calculating its entire supplied stream. The corresponding ownership statement is at line 49, and global chronology/calculation invariants are at lines 56 and 60. Both references were completely covered during the Reaction sub-audit; their mirrored identical text was verified separately.

Current Source is executable authority. Existing tests and historical result files are evidence, not definitions of trading truth. Parent-coordinated bridge, numeric-input and complete-engine audits own price normalization and finalized serialization; this report does not duplicate the root numeric JSON precision investigation.

The parent's final byte review records **strict Reference Source byte synchronization FAIL; semantic alignment of the twelve existing embeds PASS**. Eleven nonempty embeds use CRLF while current live/package Source uses LF; the empty root `__init__.py` alone is byte-exact. All twelve existing embeds match after newline normalization and have equal Python ASTs. The thirteenth embed, `bridge/__init__.py`, has no current live/package file. These results are recorded in `../reference-byte-analysis.json` and `../check_reference_bytes.py`. Package versus live Source remains byte-equal for all twelve existing files. The prose/reference coverage statement above is not a claim of strict embedded Source byte equality.

No additional boundary finding is classified Confirmed, High-confidence, Suspected or Specification conflict. A reviewed limitation or unexecuted surface is not treated as a defect. Root adjudication and independent refutation of RX-02 remain separate from this boundary result.

Unavailable project authority: current filesystem searches found no repository-root `AGENTS.md`, `README.md`, `apps/chart/README.md`, `apps/chart/server/README.md`, or `TradingBot_AI_Operating_Protocol.md`. The user supplied AGENTS instructions directly, and the active Source/Algorithm References are available. Missing owner documents were recorded rather than reconstructed from archives or memory.

## Request and input contract

| Boundary | Exact current Source | Observed contract and implication |
|---|---|---|
| RAW authority | `raw-resource-store.js:14-23,92-113,162-213` | Store validates exact five-field candle schema, positive safe timestamps, strictly increasing chronology, finite OHLC and consistent high/low. It preserves original row values after validation. Inventory hashes original serialized file bytes. `read()` parses and validates the current original file. |
| Selection identity | `vite.config.js:580-597` | Source id must exist in inventory; supplied chart id must match. Current RAW SHA-256 must equal inventory metadata before a calculation/cache selection proceeds. |
| Request timeframe/range | `vite.config.js:583-590` | Analysis and chart timeframe validation accepts positive `Number.isInteger` second values, without a fixed preset list. Range endpoints must be safe ordered epoch seconds, aligned to chart buckets and inside source bucket bounds. The range helper additionally requires a safe integer chart timeframe. No claim is made that extreme integers beyond normal epoch/date capacity are a supported market configuration. |
| Direction/enable flags | `vite.config.js:591-592,601-603,626`; bridge `1597-1670,2875-2898` | HTTP direction is exactly `bullish` or `bearish`; CLI also supports `both`. HTTP requires a boolean public Blue setting. A and S are always passed `enabled`; E and lifecycle modules are supplied at spawn and their enabled state follows S/module availability. Bridge Output is always requested by this route. There is no independent HTTP E/StopAll toggle. |
| Complete source | `vite.config.js:586-600,636-637` | Input scope is complete when requested chart bucket endpoints equal first/last source buckets. It sends the original RAW path to Python, with `fromTime` equal to requested first bucket and `toTime` equal to the actual last RAW timestamp. Rows are not rewritten or re-serialized through JavaScript on this path. |
| Selected range | `indicator-range-input.js:4-55`; `vite.config.js:638-655` | Binary bounds select every RAW row whose chart bucket falls inclusively between from and to. Requested endpoint buckets must contain rows; missing interior buckets are allowed and preserved. The source is restricted before Python sees it, as the Reference specifies. |
| Last inclusive bucket | `indicator-range-input.js:117-127` | End bound sent to Python is the actual last selected RAW row, rather than the start of the last chart bucket. Thus a final 60-second chart bucket can retain all its finer 5-second rows. Complete input reuses original array/path; selected input uses a unique in-memory Windows pipe. |
| Child process/output | `vite.config.js:239-272` | All maintained module paths are explicitly supplied to `trading_pipeline.py`. Python uses the configured executable, hidden Windows process and bytecode suppression. Successful stdout is returned verbatim; progress lines are taken from stderr, and nonzero exit becomes a request failure. Signal abort requests child termination. Actual server/child lifecycle was not exercised by this sub-audit. |

One relevant sparse example is recorded in `probe-evidence.json`: selected 30-second chart buckets `[60,120]` retain the missing bucket `90`. The Reaction detector later infers 60 seconds from its first two occupied main candles despite a requested 30-second analysis timeframe. The boundary neither rejects this valid gap nor fills it; RX-02 therefore has an accepted production transport trigger. The independent source-level Reaction repro contains realistic timestamps and both directions.

The selected path's named-pipe serialization preserves Decimal-compatible price **strings** exactly in the pure filter probes. Numeric JSON parsing and float representation are part of the root precision investigation. A successful range test cannot establish exact trading arithmetic for every numeric input representation.

## Cache, source fingerprint and state contract

| Requirement | Exact current Source | Assessment |
|---|---|---|
| Trading source content identity | `vite.config.js:27-40,51-62` | SHA-256 covers the full bytes of ten trading Python modules plus `indicator-range-input.js`, prefixed with each basename. Same-length edits or preserved mtimes still change this fingerprint. The exact current function was independently executed with scratch files to demonstrate content invalidation. Package wrappers are not trading execution sources here. |
| Semantic request identity | `vite.config.js:603-607` | Cache identity includes format/version marker, source fingerprint, chart/file identity, source mtime, analysis/chart timeframes, from/to, direction, public Blue setting, Bridge Output and complete/selected scope. Execution identity additionally contains RAW SHA-256. Request-id/progress identity does not decide trading identity. |
| RAW content validation | `raw-input-identity.js:4-31`; `vite.config.js:594-597,620,660,668` | Stat identity is checked before/after streaming the file hash. Current hash/stat must match selected identity immediately before work and after execution or cache read. Same-size content mutations are rejected; captured SHA changes independently of time metadata. Source SHA is rechecked before persistence and cache-hit publication at `657-660,669-671`. |
| Durable content stamp | `calculation-cache.js:4-37` | Result sidecar must equal current RAW hash to read a cache hit. Missing/unmatched stamp is a miss. A changed RAW hash selects an alternate result path when an existing stamped report belongs to older bytes. The exact serialized result text is persisted; cache does not recompute trading objects. |
| Write sequence | `calculation-cache.js:28-37` | Old hash stamp is removed before result write, then the new stamp is published after synchronous result write. A partial write without its stamp cannot be read as a valid hit by these functions. This was assessed for the current single Node process and coordinator; no unobserved multi-process race is asserted. |
| Work coordination | `calculation-coordinator.js:1-102`; `vite.config.js:73-75,619-666` | Default concurrency is one; configured values are 1-8. Identical execution keys return the same promise. Different jobs are FIFO with bounded active count. Recent 120 progress events replay to a joiner; subscriber failure does not alter execution. Shutdown rejects queued jobs and aborts active signals. |
| Historical report distinction | `vite.config.js:329-355,674-687` | `/api/info` reads a saved calculation snapshot and its request metadata; `/api/reactions` obtains/revalidates current input/source identity. Historical report browsing is not a recalculation or current trading authority. Absence of a fresh-source check in the historical route is therefore not established as a stale trading-cache bug. |

No stale cache, lost range row, fabricated row, order-changing queue or reused wrong-input result was demonstrated. This does not certify finalized Engine trading correctness: the same correctly identified input can still reproduce an upstream detector defect.

`rawStore.list()` can hydrate/update metadata sidecars while building inventory (`raw-resource-store.js:191`). This audit read the code without invoking inventory against protected RAW. Cache and RAW-identity probes instead used new scratch files in the audit output directory.

## Complete read and function coverage

`coverage.json` records exact SHA-256, bytes, complete line coverage and AST start/end positions for **200 production function nodes across 11 completely read files, 1,865 Source lines**, including anonymous callbacks. Reading coverage is distinct from dynamic verification of each callable. The required first five files cover 1,025 lines; all named functions and closures in those files were read.

| Production file | READ_FULL lines | AST function nodes |
|---|---:|---:|
| `apps/chart/vite.config.js` | 1-727 | 66 |
| `apps/chart/server/indicator-range-input.js` | 1-128 | 16 |
| `apps/chart/server/calculation-cache.js` | 1-37 | 4 |
| `apps/chart/server/raw-input-identity.js` | 1-31 | 4 |
| `apps/chart/server/calculation-coordinator.js` | 1-102 | 13 |
| `apps/chart/server/raw-resource-store.js` | 1-304 | 36 |
| `apps/chart/server/local-state-paths.js` | 1-32 | 2 |
| `apps/chart/server/request-body.js` | 1-64 | 12 |
| `apps/chart/server/progress-channels.js` | 1-66 | 9 |
| `apps/chart/src/features/raw-file-contract.js` | 1-54 | 8 |
| `apps/chart/src/features/candle-update.js` | 1-320 | 30 |

Full test reads: `apps/chart/tests/unit/indicator-range-input.test.mjs` 1-273, `calculation-cache.test.mjs` 1-34, `raw-input-identity.test.mjs` 1-41, `calculation-coordinator.test.mjs` 1-125. `apps/chart/package.json` was read in full. Relevant bridge CLI settings at `1597-1670` and response-enable derivation at `2865-2904` were reviewed; root owns its complete Source audit.

Other Vite route imports (Faraz ingestion, chart transfer/migration, candle-file response) are inventoried by their current import/call sites. Their full correctness is outside this calculation-transport subtask. All code inside the full Vite config, including auxiliary route handlers, was read; unsupported broader claims are not inferred from that reading.

Current file digests are recorded, but these chart files were not in the root's initial Engine/RAW protected-hash scope. Therefore the coverage artifact explicitly says `NOT IN ROOT PRE-AUDIT HASH SCOPE` rather than claiming an unavailable before/after digest proof. All mutation commands issued by this sub-audit target its own output/scratch directory.

## Reproducible verification and limits

From the repository root:

```powershell
node engineering/verification/forensic-audit-2026-10-05/boundary-audit/probes.mjs
node engineering/verification/forensic-audit-2026-10-05/boundary-audit/coverage.mjs
```

| Evidence | Result | Practical scope |
|---|---|---|
| `probe-evidence.json`, seed 530105 | PASS | 500 valid sparse chronological inputs, 2,500 range differential assertions, original full-array identity, rejected unavailable/misaligned endpoints, string price preservation, final full-source bound through last RAW row. |
| Coordinator diagnostics | PASS | Ten distinct jobs, one shared duplicate promise, FIFO start order, active cap two, 120-event replay, isolated throwing observer, queued rejection and active abort signal. Uses in-memory jobs rather than detector processes. |
| Cache/identity/fingerprint diagnostics | PASS | Exact payload text, missing/mismatched hash miss, retained old snapshot, same-size RAW content change rejected, exact current fingerprint function detects same-size edits. Scratch mtime restoration differed by 0.04931640625 ms on this filesystem; the artifact records that limitation rather than claiming exact metadata equality. |
| Root chart unit execution, `../chart-unit-tests.log` | PASS 78/78 | Existing unit suite result was inspected. It was not rerun by this sub-audit. It includes transport tests and is supporting execution evidence. |
| Live HTTP/server/browser execution | NOT RUN | Parent explicitly scoped this subtask to source review and isolated diagnostics without server/network startup. No endpoint behavior claim depends on a live request from this agent. |

No source fix, RAW repair, deployed cache change or full-engine behavioral counterfactual is part of this report. The next actionable review is to assess RX-02 alongside the Reaction report; the boundary supplies the documented sparse input unchanged.
