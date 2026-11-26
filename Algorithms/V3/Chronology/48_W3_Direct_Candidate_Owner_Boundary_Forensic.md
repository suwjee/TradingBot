# CP363 — W3 direct candidate and owner-boundary forensic review

Pinned source: `c99b4c957e932d9ee70c492ca03ce80711447fc1`, reaction_engine.py lines 2291–2433, RE92–96, historical B02-12. Separate source-first pass, not independent human attestation.

- First lookup precedes bounds and tag rejection. The two backward runs are contiguous and Reset-bounded. Local extrema reject strictly, outer leg extrema are independently frozen. Initial opposite edge uses positional First; confirmation edge and anchor use stored identity.
- Direct scan saves confirmation before RE94, then invalidation precedes mutation; exact B/R update guards are separate. Direct Break is positional, unlike concurrent stored identity. Refine return ignored; failures do not imply rollback.
- Missing boundary short-circuits false. Both main predicates calculated before decisions; full main lower window on both strict predicates, outward before confirmation each row. Empty/unresolved lower defaults invalidation. Equal timestamp across distinct rows is not a same-row tie.
- Result aliases direction lists; public detect forwards optional stop gate with retention false. Permissive and concurrent callers remain distinct.

415 canonical rows (94 W1, 321 additional), 25 contracts, six historical supplements; zero coordinate errors or prior overlap. CP363-F01 resolved scoped documentation; historical B02-12-F01 preserved. Cross-owner findings remain open. No RAW payload, runtime, ZIP or production change.

Evidence: [local register](../../Audit/Phase_07/Rebaseline_v2_8_7/CP363_W3_Direct_Candidate_Owner_Boundary_Local_Forensic_Register.json), [consumer boundaries](../../Audit/Phase_07/Rebaseline_v2_8_7/CP363_W3_Direct_Candidate_Owner_Boundary_Consumer_Boundaries.json). Next: 2434–2908.
