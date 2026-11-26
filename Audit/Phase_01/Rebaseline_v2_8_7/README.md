# Phase 01 — v2.8.7 delta rebaseline (CP286)

**PASS for source discovery and baseline freeze only.** Current main `c99b4c957e932d9ee70c492ca03ce80711447fc1`, previous `466eb875070f02cd0dbfb105033422bbe2fd8c70`; root tree `9e1ede6672cd5daf2bf099361c17b4a723fd21cc`; Engine tree `bd35650cbb317b30d2855f7b31f24de5fcfae955`.

Main is sole executable authority per user. Root AGENTS and portable governance identities unchanged; latest README, architecture, release and Chart/RAW boundary changes discovered. Previous manifest and completion are immutable. All 27 changed paths retrieved and compared; 9 Engine blobs freshly hashed, 55 carried forward only by identical blob/size. Three references each contain 16 matching exact embedded source blocks. 587 lexical functions, 87 classes and 17,204 LF-counted source lines (not AST totals). 44 Engine tests/tools, 301 lexical test definitions. 14/16 production blobs match historical Golden; two differ; do not treat stored outputs as a current oracle. Four canonical RAW paths inventoried by Git tree metadata only; eight future mandatory independent runs. No RAW payload or runtime execution.

## Evidence

- [Source manifest](Source_Manifest.json)
- [Production/reference integrity](Production_and_Reference_Integrity.json)
- [Repository discovery](Repository_Discovery.json)
- [Test inventory](Test_Inventory.json)
- [Change impact and ZIP reconciliation](Change_Impact.json)
- [RAW metadata](RAW_Metadata.json)
- [Completion evidence](Completion.json)
- [Conflicts](Conflicts_Register.md)

## Acceptance

| Check | Status |
|---|---|
| Authoritative main resolved and pinned | PASS |
| Complete prior/current root tree and Engine inventory | PASS |
| 64 Engine identities/lengths and digest provenance (9 fresh,55 identical prior) | PASS |
| 16 production/package identities and lexical metadata | PASS |
| 48 embedded source block comparisons | PASS |
| Governing root and portable docs reviewed; identity unchanged | PASS |
| 27 changed files inventoried; content retrieved | PASS |
| 44 Engine tests/tools and 301 lexical test definitions; external runners discovered | PASS |
| ZIP CRC and 18 SHA256 entries, all 12 source copies compared | PASS |
| Canonical four RAW tree paths and policy recorded | PASS (metadata only) |
| Historical Golden authority difference recorded (14/16 unchanged) | PASS (classification only) |
| Runtime, RAW integrity and full semantic certification | NOT APPLICABLE TO SOURCE-ONLY DISCOVERY |

## Handoff

RB02 / CP287 — regenerate Phase 02 AST/static inventories for pinned engine/pipeline/true_false.py and engine/bridge/trading_pipeline.py; refresh dependencies, source-to-site mappings and metadata; do not start W2 before W1 rebaseline closure.
