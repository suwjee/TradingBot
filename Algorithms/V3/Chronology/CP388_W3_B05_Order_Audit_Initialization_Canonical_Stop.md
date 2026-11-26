# CP388 — Order Audit initialization and canonical stop

Pinned source: `6ddb93ba097ef137af2405ef15356b6f6bcf97de`, lines 554–688. Independent local source scope only.

## OA13-A (554–569)

Initialize new empty cross-order and canonical-stop dictionaries, not clear old aliases. Number-only canonical cache presumes same run, exact canonical object and unchanged geometry/chronology. Annotation does not enforce shape.

## OA13-B (570–587)

Initial record cache, First-time list, confirmation-time list and by-First index start None; confirmation records start empty tuple. No materialization or publication of initial A records occurs here.

## OA13-C (588–600)

Fresh candidate, carried, post-stop and direct-parent-stop dictionaries. Distinct key shapes and null result annotations; no data validation, invalidation of external aliases, or eager calculations.

## OA13-D (601–611)

New authoritative order_audit keyed by physical pair; empty separate confirmation index, sorted audit None, pending list empty. No Order creation or initial A import. Derived indexes do not own ledger provenance.

## OA13-E (612–624)

Four separate ordered callback traversals: trend First, trend confirmations with direction, opposite First, opposite confirmation via owner callback. No local sort, bounds check or immutable snapshot of objects. Alignment depends on stable sequences and callbacks.

## OA13-F (625–634)

Zip trend confirmation, First and reaction with shortest-input semantics, stable sorted by confirmation alone. Equal confirmation order preserved. Extract aligned confirmation times; fresh empty trend-leg position cache. Opposite confirmation order not sorted here.

## OA13-G (635–643)

Group opposite Reset events by int from-First key, append delegated Reset times in supplied order including duplicates. Opposite-by-First dict comprehension last duplicate First wins; no local validation.

## OA13-H (644–652)

Separate physical reaction identity position map uses enumerate then setdefault; first occurrence of int First/Break pair wins. Not same policy as opposite-by-First. Identity helper normalizes only indexes. Sequential initialization can fail after partial writes, no local rollback.

## OA14-A (653–663)

Discard context_start. Inclusive ordinal range short-circuits before number-1 indexing; only exact object identity of canonical opposite Reaction admits cache lookup by number. Cached non-None returned directly; None treated as miss. Native invalid type/index failures not caught.

## OA14-B (664–672)

Canonical cache miss delegates chronology.canonical_order_stop with order_direction, number, same reaction object, opposite list and start_index. Store result unchanged only after successful return; no Decimal conversion or manufactured context stop.

## OA14-C (673–680)

Noncanonical path delegates same method with same argument shapes, bypasses all canonical cache reads and writes. Caller must ensure admissible number/geometry; no local validation of delegated return.

## OA15-A (681–688)

Public order_stop forwards reaction_number and reaction to private _order_stop, no explicit context. Return result directly without copying, extra calculation or validation.

## Consumer boundaries

E constructor lines 346–365,389,413–414,559–566 establish shallow copied streams and delegated chronology. Core utils lines 64–66 normalize physical pair indexes. Neither boundary establishes run immutability, complete creator/consumer identity or cache validity.

## Evidence

440 category rows (51 W1, 389 additional), 8 historical supplements, prior 1609 rows revalidated without overlap or identity errors. Local source review only; run immutability, chronology/index alignment, callback stability, cache lifetime, failure rollback and ledger creator/consumer acceptance remain independent. Constructor lists are shallow; no runtime immutability or exception-path equivalence established. No RAW payload, runtime, ZIP or production changes.
