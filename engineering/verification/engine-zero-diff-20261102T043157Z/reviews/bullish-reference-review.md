# Current Bullish Reference non-embedded review

Generated read-only inspection evidence, not a new trading specification. Created: 2026-11-02T08:06:25+03:30. Last modified: 2026-11-02T08:10:07+03:30.

## Input identity and reading scope

File: `engine/algorithms/TradingBot_Bullish_Algorithm_Reference_V5.4.33_Source_Synchronized.md`.

Observed identity: 16,049 lines, 829,064 bytes, SHA-256 `50b2484f695313c26257ffc671205910bf8c792b98de069ca5dacf10890074f3`. The maintained header identifies the active source-synchronized local extension, unreleased; it was modified at 2026-11-02T07:13:10+03:30. Version identifiers and hashes here describe this observed file, not permanent semantic authority.

Every non-embedded prose/schema/history/symbol/verification line was read. Actual reads: 1-180 with the output-truncated gap explicitly reread at 85-100; 181-280; 281-400; 401-520; 521-640; 641-770; 771-875; 876-954; 955-1011; 1012-1128; 1129-1245; 1246-1354; 15966-16049. A separate filtered read covered all Section 16 wrappers/manifest metadata while skipping only source-body rows. No truncated result was accepted as a complete read without recovering its missing range.

Section 16 embedded bodies were not read as a second copy of the Source. The parent must map their exact bytes to the team's genuinely complete live-Source read ledgers using an independent byte verifier. Source-body exclusions (inclusive document lines):

| Source | Excluded embedded body lines |
| --- | --- |
| `__init__.py` | Empty body (opening 1354, closing 1355). |
| `bridge/__init__.py` | 1366-1366 |
| `bridge/trading_pipeline.py` | 1378-4810 |
| `pipeline/__init__.py` | 4822-4849 |
| `pipeline/a_zone_detector.py` | 4861-5664 |
| `pipeline/blue_line_detector.py` | 5676-6156 |
| `pipeline/core_utils.py` | 6168-6193 |
| `pipeline/direction_policy.py` | 6205-6274 |
| `pipeline/e_zone_detector.py` | 6286-7546 |
| `pipeline/lifecycle_engine.py` | 7558-9086 |
| `pipeline/order_audit_engine.py` | 9098-11319 |
| `pipeline/PL_PH_detector.py` | 11331-11996 |
| `pipeline/reaction_engine.py` | 12008-14508 |
| `pipeline/s_zone_detector.py` | 14520-15964 |

All headings, hashes, byte/LF counts, source markers and fences around those exclusions were read (filtered Section 16 read 1343-15967). The exact inclusion ranges are also recorded in `reaction-read-ledger.json`. Schema/symbol index lines 770-1010 were read fully despite long physical lines; they are descriptive navigation/integrity evidence, not semantic authority (772-774).

## Governing contracts relevant to the refactor

- Source inventory is dynamically discovered; the manifest and exact-source snapshot must be synchronized with the same current production closure (110-145, 1343-1345). The current Section 1 includes live root/package markers and current primary module. Older package-specific omissions below remain historical.
- Complete supplied input is calculated before CLI presentation bounds. The selected-range HTTP stream has its own explicit input boundary, so no history outside that supplied stream is available (139-145). Ownership remains Reaction, Blue, A, S, E, OrderAudit, lifecycle, primary and Bridge as specified; serializers and Chart cannot repair a changed upstream algorithm.
- Decimal lexemes, strict equality exclusions, market GREEN doji, physical `(FirstIndex,BreakIndex)`, exact chronology, stable ordering and provenance remain invariant (147-156). Earliest equal source is normal, with explicit last-on-equality exceptions for S Type-3/4. Copying a price without its owner/event is insufficient.
- Reaction confirmations and public opposite box edges stop at the exact authoritative lower row. Reset/invalidation chronology and bounded post-Reset structural acceptance remain separate from geometry-only evidence (158-194). Complete post-A-stop physical Order_A is an explicit noncanonical-public-Reaction exception; its real physical identity is retained and reaction number is zero (188-190, 258-264, 309-329).
- Blue strikes and pending intrabar confirmation use the exact confirmation prefix, including its row; calculation-invalid double-stop Blue remains A evidence, while public Blue is valid and noninternal (196-214). A's source freezes from trigger main open through exact confirming Reaction; lower-TF/source ties and first-stop ownership must survive an index replacement (216-236).
- S Type-3/4, pre/post-Order Simple and Advanced routes retain distinct full-candle/intrabar boundaries, last-equality owners and race ties. Same lower-row Order-stop/candidate race yields no S decision (238-279). Shared physical accepted Order stop deduplication uses exact identity and chronology.
- E compares the complete eligible physical candidate set before selecting earliest strict Order stop, then larger First on a same-stop tie. E source uses complete boundary main candles, not a truncated intrabar range. Accepted E source ownership disowns provisional same-source S creation but preserves independent valid causes (281-329).
- Order_A parent-stop and Order_B reset-leg causes are creation; carried/live accepted routes are use. Accepted A validity and native physical/cause preservation survive rebuilding. Order_B's main calculation candle owns the gate/accepted-A expiry while exact RAW proves required within-candle chronology (331-381).
- Lifecycle preserves one exact dominant S/E owner, count>=2 arming, complete priority and accepted decision chronology, including direct-child/own-source-candle E donor exceptions and direct accepted S Red donor. A is not in S/E dominance. StopAll resets active state but retains historical calculation/provenance (383-421).
- Public legacy schemas, Decimal strings, Tehran local epoch contract, source ordering, pre-window required Orders and optional read-only Bridge projection remain stable (423-446). Full field lists 429-438 and complete dataclass/AST index 770-1010 were read.
- Primary extension retains independent cycles with globally chronological native audit updates, immutable per-cycle MBL, earliest source ties, final physical numbering/identity and qualified historical references. PH/PL parent commits may alter native audit causes only under the existing current rules. No refactor may substitute one global cycle, lose native identity, or clip required history (448-616).
- Current automatic bidirectional primary calculation and repeated fresh directional regimes are explicitly approved. Final PH3/PL3 strict stop ends the stopped regime; an independently supported fresh prefix/suffix owns the new calculation with no prior detector/order state. Only first Reaction uses new-regime bootstrap. No PH4/PL4 is invented. The existing cancellation and opposing-event ambiguity handling remains unchanged (559-599, 691-766).
- Current presentation markers are 28x28 CSS pixels, actual candle50 counting the boundary as one, 100px clearance; MBL cap is 400 actual candles and label 9px. Auto/Manual controls remain outside approved change (617-640, 760-766). These are current presentation contracts and not optimization parameters.

## Conflicts, historical boundaries and limitations

1. **Disclosed live ambiguity, preserve executable behavior:** Section 4.4 lines 176-178 allows the complete confirmation candle as next First while saying post-event chronology controls the new boundary. Current Source `_candidate_from_confirmation_remainder` (Reaction 1574-1604) first rejects strict post-confirmation Reset and then unconditionally sets whole-confirmation mode, constructing the new boundary from the whole candle. The parent confirms current Plugin retrieval labels this `REF-REACTION-SUCCESSOR`; Section 14.0m 1127 explicitly retains it. This review does not resolve the semantic interpretation or authorize a fix.
2. **Generic summary wording versus explicit exception:** direction-invariant matrix 1086 and stage-summary Order_A row 1104 state generic canonical-membership wording, while normative detailed Sections 7.4/9.1 explicitly admit complete post-A-stop geometry-only Order_A with reaction number zero. Treat the detailed explicit approved exception as an existing disclosed scope qualification; do not remove those native Orders as a cleanup. Any editorial reconciliation belongs to an authorized Reference workflow, not this read-only report.
3. **Historical numbers/layout/commands are evidence only:** Section 13.9 1110-1117 retains old twelve-file/no-root-marker package claims despite its current manifest now including root marker and primary module. The section is explicitly historical. Likewise 1225-1341 and 15968-16049 preserve older versions, omitted package files and commands; they cannot redefine current inventory or be rerun blindly as today's supported commands.
4. **Historical marker caps/examples remain historical:** USOIL examples at 652-687 mention an old 100-candle cap and PH4+ future cycles. The surrounding headings and explicit current 400-candle/PH3 reversal rules supersede those old acceptance expectations. Do not create timestamp/RAW-specific production branches from any bounded example.
5. **Current status is not historical PASS:** Section 14.0m 1121-1127 points to the dated prior task record, distinguishes structural reconstruction from trading correctness, states bounded Plugin knowledge and pending clean-Source Vault capture, and excludes standalone PH/PL/MBL Vault synchronization. Earlier Section 14.0p and release/annex PASS counts remain historical. No tests, RAW replay, browser verification or performance measurements were run by this reviewer.

## Gate result

Non-embedded Bullish Reference reading: COMPLETE for the observed hash. Embedded duplicate Source second read: NOT CLAIMED; exact byte identity plus mapped full-read team ledgers is required. Current Reference/source fidelity execution: NOT RUN by this reviewer. Behavioral corrections and Reference changes: NONE. Baseline/equivalence/performance acceptance remains the parent's later gate.
