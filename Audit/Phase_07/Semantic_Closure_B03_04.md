# Phase 07 — Checkpoint 32 / W1 B03-04

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; entry algorithm `501c025e5d525568fc026e62994f2a7e8c76af57`. **Local review PASS; B03 INCOMPLETE; Phase 08 BLOCKED.** A01–A08, lines 1–215; 131 original rows, 9 supplemental items, 2 resolved local documentation omissions/clarifications. A cumulative 131/708; B03 568/1145.

[Individual evidence](Semantic_Closure_B03_04.json) preserves original category IDs, spans, local meanings and historical navigation. Compared with [A contract](../../Algorithms/V3/04_A_Zone.md), [Blue/A state model](../../Algorithms/V3/State_Machines/02_Blue_A.md) and [shared chronology](../../Algorithms/V3/20_Indexes_And_Caching.md). Historical references retained; active edits preserve stable identifiers and line counts.

## Verified local behavior

Verified stable full Blue sort and retained native Reaction order; three separate ordered-time guards and virtual confirmation dispatch. A07 indexed/linear lower crossing miss never falls back to main when lower rows exist. A08 inclusive lower extrema and containing-main fallback differ from A07 main-open fallback. Lower path returns mapped position, main fallback returns native candle.index; these require caller alignment, not assumed identity.

## Findings

- B03-04-F01: Distinguish returned confirmation time from proof of an exact lower hit.
- B03-04-F02: Resolve ambiguous position field and preserve distinct lower-source time access.

## Open dependencies

- W2 verify index/time/sequence alignment and caller-valid ranges; no claim arbitrary source mutation safe.
- W3 separate forensic review pending.

No RAW read, runtime execution, production change or main modification.
