# Phase 07 source inventory

Pinned main: `466eb875070f02cd0dbfb105033422bbe2fd8c70`. All sixteen production source files were fetched directly; blob identities matched Phase 04.

| Group | Modules | Procedures | Candidate lines | Comparisons | Arithmetic | Scopes |
|---|---:|---:|---:|---:|---:|---:|
| [01](Source_Index_01.json) | 4 | 115 | 1085 | 365 | 176 | 270 |
| [02](Source_Index_02.json) | 4 | 103 | 923 | 354 | 175 | 192 |
| [03](Source_Index_03.json) | 4 | 112 | 1182 | 430 | 211 | 270 |
| [04](Source_Index_04.json) | 4 | 246 | 2785 | 1028 | 512 | 436 |
| Total | 16 | 576 | 5975 | 2177 | 1074 | 1168 |

Every named declaration is retained. 495 contain at least one lexical candidate. Each candidate line stores categories and overlapping reviewed rule IDs; named procedures also link intersecting reviewed ranges. Unmatched procedures are not declared chronology-independent. Lexical labels include positional, time, selection, ordering, window, continuation and visibility vocabulary and may overinclude or miss implicit temporal dependencies. Operator rows retain prior AST node identifiers (not source line numbers) and scope indices. Do not conflate lexical hits, AST comparison count or range overlap with semantic coverage. See [validation](Validation.json) and [checkpoint](README.md).
