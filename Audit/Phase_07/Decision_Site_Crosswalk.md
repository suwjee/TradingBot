# Phase 07 — exact AST-site crosswalk (checkpoint 04)

Status: **STRUCTURAL CROSSWALK VERIFIED; SEMANTIC CLOSURE INCOMPLETE**.

Baseline: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. The original Phase 02 full AST inventory blobs were fetched by immutable blob SHA, including large inventories that were empty when read through the regular file endpoint. All 16 production source files were fetched at pinned main and checked against Phase 04 source identities. Every original branch/control site, comparison, arithmetic and call row is retained with its original AST location and nearest named procedure where available. Filter IDs resolve to AST nodes rather than being misinterpreted as source line numbers.

| Group | Branch/control sites | Comparison rows | Arithmetic rows | Call sites |
|---|---:|---:|---:|---:|
| [01](Decision_Site_Crosswalk_01.json) | 602 | 365 | 176 | 1326 |
| [02](Decision_Site_Crosswalk_02.json) | 501 | 354 | 175 | 791 |
| [03](Decision_Site_Crosswalk_03.json) | 640 | 430 | 211 | 1075 |
| [04](Decision_Site_Crosswalk_04.json) | 1390 | 1028 | 512 | 1928 |
| Total | 3133 | 2177 | 1074 | 5120 |

The totals are category counts, not mutually exclusive AST nodes. There are 1707 branch/control rows with lexical signals and 1426 without direct signals. 828 rows have at least one reviewed rule-range link and 3126 have a nearest named-procedure link. These are conservative search/traceability signals, not reviewed guard semantics or proof that untagged nodes cannot affect chronology. Focus spans for control constructs are approximations; AST coordinates are authoritative. See [validation](Decision_Site_Validation.json).

The earlier lexical source index remains unchanged. The new crosswalk fixes the missing direct AST-location join and adds auditable owner/range references, without reproducing source bodies. No claim of independent semantic certification; Phase 08 remains blocked until the remaining owner semantics and cross-stage interactions are verified.
