# Phase 01 — Baseline discrepancies and open questions

| ID | Observation | Resolution or disposition |
|---|---|---|
| P1-C01 | Uploaded AGENTS.md (24,494 bytes; Git blob ec54866976859d1f30941943ac4331c4e70128f6; SHA-256 17b399237762e9db870f9b0eafd29b2db4ae3578251fba0202bbe3b58a049dfa) differs from root main AGENTS.md and main portable companion. | RESOLVED for authority: current main governs. Upload is supporting material only. |
| P1-C02 | Uploaded Operating Protocol (65,003 bytes; Git blob 1e58eff58a362c185bcd74f0d78a7320e86abadf; SHA-256 721dc1740011ba7fc2331c979b6e41da93f58bbc30f57b4185f51034f45a244e) differs from current main GPT_bot protocol (91,035 bytes). | RESOLVED for authority: use current main protocol as subordinate guidance. |
| P1-C03 | Golden correctness anchor is commit 01d54ecf0149ebd15de92798be18810b6e2eb791 rather than latest main. | RESOLVED for extraction: use current main; independently verified 16/16 production/package Git blobs equal across commits. Preserve immutable Golden as regression evidence. |
| P1-C04 | Some historical optimization and V9 tooling deliverables are newer-looking or use a different version name. V9 audit explicitly says no new production source version and incomplete tooling. | RESOLVED for authority: no candidate, archive or version label can supersede latest main. |
| P1-C05 | The historical Golden verifier has reported limitations (trailing newline rejection, extra timing sibling not rejected) in current main V9 tooling audit. | OPEN for future verification: independently reproduce and correct test-only comparator before full differential verification; no production modification. |
| P1-C06 | Canonical Intelligence/Vault not directly available through exposed connectors. | DISCLOSED LIMITATION: main is unambiguous for actual implementation per user; intended-semantic comparison remains open when additional canonical evidence is needed. Do not assert absence of semantic conflicts. |
| P1-C07 | Two XAU RAW datasets overlap for 10,185 exact timestamps; zero numeric and Decimal string discrepancies in checked overlap. All datasets have chronology gaps. | RESOLVED for input identity: keep original files separate, preserve gaps; no synthetic insertion or concatenation. |
| P1-C08 | Older curated 5-minute RAW was explicitly excluded from active Golden suite in current main Golden README. | RESOLVED: do not reintroduce it or interpolate it; seven 5-second inputs verified. |
| P1-C09 | Current exact-source reference snapshots and the directly fetched production contents match. The prose and full algorithm branch remain only partially verified. | OPEN semantic audit for phases 2–11. No byte discrepancy observed in the tested scope; no conclusion about all trading rules. |
| P1-C10 | MBL nomenclature needed confirmation. Main primary reference explicitly expands it as Matching Behavior Legs. | RESOLVED terminology for this baseline. |

No runtime defect was corrected, no reference was rewritten, and no intended rule was inferred. Phase 01 resolves source selection, not all semantic disagreements.
