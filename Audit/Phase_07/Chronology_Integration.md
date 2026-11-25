# Phase 07 — cross-owner chronology integration and comparison evidence

**Status: structural validation PASS; source-only semantic closure INCOMPLETE.** Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`.

The [123 reviewed chronology clauses](../../Algorithms/V3/Chronology/README.md) supplement the existing source-derived Phase 05 procedure contracts and Phase 06 state models. The [cross-owner supplement](../../Algorithms/V3/Chronology/07_Cross_Owner_Chronology.md) records 48 additional direct source reviews (CH76–CH123).

## Critical cross-stage precedence

| Boundary | Native temporal policy | Direct clauses |
|---|---|---|
| Reaction gate | Exact lower position decides; restart wins equal position; next First scan starts after owning main | CH06, CH08, CH76 |
| Blue → A | Scale first; exact Break prefix included; A pair expiry is separate from formation; freeze source through confirmation | CH10–CH14, CH80–CH87 |
| A → S | Confirmation and stop are separate; A stop strictly before next A confirmation; Type 3 wins exact Type 3/4 tie | CH15–CH18, CH89–CH94 |
| S / Order | Same lower position rejects S candidate/Order race, but later accepted Order reconciliation selects stop >= source and < old decision | CH17, CH95 |
| Order → E | Route-local selection keys differ from E global stop/descending First; strict Reset interval ends inclusive | CH19–CH28, CH97–CH103 |
| E reconciliation | Source identity and family priority before decision chronology in same-source conflict | CH64–CH66, CH104–CH108 |
| Lifecycle | A dominance uses latest stop-owning main; S dominance latest exact stop; StopAll freezes historical boundary | CH109–CH113 |
| Primary | PH gate allows exact equality, PL does not; global reversal before activation before point commitment on ties | CH34–CH36, CH114–CH116 |
| Bridge / Live | Full physical chronology separate from visible range; independent reversal prefix, dirty frontier, and replay scopes | CH37–CH45, CH117–CH123 |

## Procedure and comparison ledgers

[Procedure crosswalk](Procedure_Chronology_Links.json): all 576 named source declarations link uniquely to the recorded Phase 05 procedure heading and to their Phase 06 transition references where direct. 550 procedures have direct references (1,018 occurrences); 26 are supporting-only per Phase 06. These links compose previously extracted semantics without duplicating implementation bodies.

| Comparison ledger | Rows | Arity match | Chained |
|---|---:|---:|---:|
| [Group 01](Comparison_Operands_01.json) | 365 | 365 | 17 |
| [Group 02](Comparison_Operands_02.json) | 354 | 354 | 4 |
| [Group 03](Comparison_Operands_03.json) | 430 | 430 | 12 |
| [Group 04](Comparison_Operands_04.json) | 1028 | 1028 | 14 |
| Total | 2177 | 2177 | 47 |

The ledger separates strict and inclusive inequalities, equality, identity and membership. Native chained comparisons evaluate shared middle operands once and short-circuit; do not reduce them to unrelated independently evaluated comparisons. Operand roots link to original coordinates and metadata, not copied executable expressions. A matching operand count is not semantic equivalence. Compound operand interpretation and state effects still require the owning procedure.

[Validation](Chronology_Integration_Validation.json) records readback and structural checks. [Decision-site crosswalk](Decision_Site_Crosswalk.md) retains all branch, comparison, arithmetic and call sites. Semantic closure requires contextual disposition of temporal sites beyond source-range overlap and lexical signals. Phase 08 remains blocked.
