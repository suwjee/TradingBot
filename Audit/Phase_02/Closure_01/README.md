# Phase 02 — Static closure supplement 01

**Status: PARTIAL.** This pass adds candidate evidence, not runtime dispatch proof. Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70` (latest main at phase start); prior algorithm checkpoint `d31aff0a57f97822a0ab3f8693d6c5c944a34ba1`. Historical reports are unchanged.

## Verified scope

- 16/16 current production Python source blob identities and sizes match prior Phase 02; all 16 pinned source files fetched.
- 28/28 historical report blob identities and sizes match the manifest.
- All 5120 call inventory entries counted; 1528 individual review rows with stable IDs (1164 formerly unresolved, 364 imported/dynamic).
- 12/12 aggregate integrity checks passed.

| Triage category | All reviewed | Formerly unresolved |
|---|---:|---:|
| IMPORTED_CANDIDATE | 364 | 0 |
| INTERNAL_NAME_ONLY | 288 | 288 |
| INTERNAL_TYPE_EVIDENCE | 73 | 73 |
| STANDARD_NAME_ONLY | 308 | 308 |
| STANDARD_TYPE_EVIDENCE | 255 | 255 |
| UNCLASSIFIED_DYNAMIC | 240 | 240 |

Each row identifies the pinned call and enclosing scope, prior resolution, candidate target IDs, receiver type evidence (parameter annotation, direct syntactic receiver, conservative reaching-write annotation/constructor, list/map expression, enclosing class or declared immediate base), standard-method candidate names, import binding and existing effect flags. A matching class/member name is not an established call edge. The analysis uses a limited source-line heuristic and the prior AST inventory; it is not a type checker. Source bodies are not included.

## State and path evidence

896 call sites match the reflective/import/dynamic name screen, including already-classified calls. This is a name screen, not proof of reflection or mutation at runtime. Conservative dataflow: 12743 read sites; 7139 retain ENTRY_UNKNOWN; 5604 retain PARAMETER; 1381 have multiple candidate write nodes. Unknown effects remain attached to the original scope and call ID. See the group reports for the per-site evidence.

## Deliverables

- [Aggregate summary and integrity checks](Summary.json)
- [Group 01 — package, bridges and primary structures](Group_01.json)
- [Group 02 — A, Blue, core, direction and E](Group_02.json)
- [Group 03 — lifecycle, order audit, reaction, S and T/F](Group_03.json)
- [Original Phase 02 checkpoint](../Phase_02_Completion_Report.md)

## Remaining acceptance gates

| Gate | Status |
|---|---|
| Exact runtime dispatch, dynamic receiver ownership, actual binding | NOT RUN |
| Exact heap alias and interprocedural state/side-effect analysis | INCOMPLETE |
| Exception and semantic branch feasibility / dead-code proof | NOT ESTABLISHED |
| Runtime branch coverage, full RAW, differential reconstruction and regression | NOT RUN |

The authoritative source was accessed through pinned GitHub blobs because engine.zip was unavailable in this runtime. No application modules were executed, no RAW was modified, no production code or algorithm rules were changed. These records are Phase 03 inputs, not a claim that Phase 02 has reached full semantic closure.
