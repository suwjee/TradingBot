# CP350 — W2 current-baseline semantic closure reconciliation

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`. The source-only review register supersedes ambiguous historical summaries only where explicitly qualified below. Original CP321–349 artifacts and CH historical anchors remain unchanged; CP292 current-anchor transfer remains authoritative for coordinates. No production modification, RAW payload, runtime equivalence, or W3 forensic acceptance.

## Explicit current-baseline qualifications

### CH13

Break-open confirmation means false use_intrabar_start, not that confirmation necessarily equals Break open. First strict lower crossing in the full Break window wins; missing crossing returns Break open. Reset Blue and actual stop are independent.

Reviewed transitions: CP323-S20, CP323-S21. Source: engine/pipeline/reaction_engine.py:1257–1302; engine/pipeline/a_zone_detector.py:157–169. Historical document: Algorithms/V3/Chronology/02_Blue_A_S.md.

### CH25

Public E parent stop begins at parent's exact decision. Native and live main times agree under the same coherent candle chronology; live retains detector.times[index], inherited native reads the owning candle timestamp. Do not equate different or externally mutated sequences.

Reviewed transitions: CP326-S12, CP326-S13. Source: engine/pipeline/e_zone_detector.py:478–578; engine/pipeline/order_audit_engine.py:1459–1484. Historical document: Algorithms/V3/Chronology/03_Order_E.md.

### CH39

Positive integral numeric equality is checked after int conversion; not an exact Python int-type requirement for rows. Nondecreasing accepts equality. Inner rollback try follows publication of new keys/suffix/time; earlier assignments outside, outer protected block discards views; original lineage has separate strictly increasing rule.

Reviewed transitions: CP330-S06, CP330-S07, CP330-S08, CP323-S42, CP330-S28. Source: engine/bridge/trading_pipeline.py:229–303; engine/bridge/live_pipeline.py:35–70; engine/bridge/live_pipeline.py:148–156. Historical document: Algorithms/V3/Chronology/05_Projection_Live_TF.md.

### CH69

An old nonnull exact hit can be reused when effective dirty is null or hit<dirty; prefix equality needs max(source,decision)<dirty only if dirty nonnull. Covered horizon caps dirty when available.

Reviewed transitions: CP327-S16, CP327-S17. Source: engine/pipeline/lifecycle_engine.py:550–590. Historical document: Algorithms/V3/Chronology/06_Additional_Owner_Boundaries.md.

### CH86

A fallback extreme is entire mapped start..end main range inclusive, not lower-proven; start=max(0,upper_bound(start)-1), end=min(last,max(start,upper_bound(end)-1)); an owning boundary is not independently validated by a lower hit. Native A confirmation starts at Break open (flag false), later strict hit or fallback.

Reviewed transitions: CP323-S21, CP323-S20. Source: engine/pipeline/a_zone_detector.py:171–214. Historical document: Algorithms/V3/Chronology/07_Cross_Owner_Chronology.md.

### CH96

S continuation Type3/4 directly use decision time; Order-backed guard requires a lower row at/after clamped Order confirmation and no later than decision, not a strict crossing proof. Reuse additionally requires key/dependencies and frontier<dirty.

Reviewed transitions: CP324-S21, CP324-S22. Source: engine/pipeline/s_zone_detector.py:1469–1525. Historical document: Algorithms/V3/Chronology/07_Cross_Owner_Chronology.md.

### CH99

Direct parent stop confirmation_after is optional. Native threshold loop precedes same-gate blocked-First skipping and threshold is not reapplied afterward. E exact exception checks > start; geometry callback conditions and preference separate.

Reviewed transitions: CP325-S16. Source: engine/pipeline/order_audit_engine.py:829–918. Historical document: Algorithms/V3/Chronology/07_Cross_Owner_Chronology.md.

### CH101

Eager accepted-live initial records bisect confirmation > parent_stop, audit index bisects tuple with 2**63-1 sentinel; add_match itself checks crossed>parent_stop and crossed>match confirmation, reset gate, physical dedup. No independent blanket confirmation recheck of each audit entry; optimized native route must be described separately.

Reviewed transitions: CP325-S33, CP325-S34, CP325-S35. Source: engine/pipeline/order_audit_engine.py:1798–1878. Historical document: Algorithms/V3/Chronology/07_Cross_Owner_Chronology.md.

### CH113

LC40 calculates once per invocation; TB74 calls it once per enabled feedback pass (up to 8). Final visibility uses converged objects without extra StopAll detection.

Reviewed transitions: CP327-S30, CP323-S28. Source: engine/pipeline/lifecycle_engine.py:1377–1409; engine/bridge/trading_pipeline.py:2569–2645. Historical document: Algorithms/V3/Chronology/07_Cross_Owner_Chronology.md.

### CH115

PH commitment clears pending proposals only when commit_high is non-null, after callback; reflected adapter always exposes a method, but external owner mutation depends on supplied callback. PL commitment does not clear others.

Reviewed transitions: CP328-S11, CP328-S25. Source: engine/pipeline/PL_PH_detector.py:380–402; engine/pipeline/PL_PH_detector.py:770–801. Historical document: Algorithms/V3/Chronology/07_Cross_Owner_Chronology.md.

### CH119

Bridge passes frozenset of accepted A physical identities, not global accepted-only creation permission. Inside continuation, invalid-S-only/no other creation cause can survive only with independent accepted A identity; ordinary other valid causes remain eligible. Match current E owner by exact source index/time, then rebuild ledger from actual resulting state and supplemental evidence.

Reviewed transitions: CP323-S28, CP326-S18. Source: engine/bridge/trading_pipeline.py:2507–2555; engine/pipeline/e_zone_detector.py:770–823. Historical document: Algorithms/V3/Chronology/07_Cross_Owner_Chronology.md.

### CH120

Equality of sorted 17-field signature including multiplicity terminates, repeated unequal signature or 8-pass exhaustion raises. Not full dataclass equality. CP292 C07 current-source supplement takes precedence.

Reviewed transitions: CP325-S12, CP323-S28. Source: engine/pipeline/order_audit_engine.py:531–550; engine/bridge/trading_pipeline.py:2569–2645. Historical document: Algorithms/V3/Chronology/07_Cross_Owner_Chronology.md.

### C01 / C04 / C05

Projection proof checks returned timestamp, even native fallback can verify; C04/05 transaction wording is limited by actual try boundaries (CH37/39/40 and CP342/345). No substitute event, external callback rollback or early assignment rollback guarantee.

Reviewed transitions: CP329-S07, CP329-S10, CP330-S06, CP323-S42. Source: engine/bridge/trading_pipeline.py:690–783; engine/bridge/trading_pipeline.py:229–303; engine/bridge/live_pipeline.py:35–70. Historical document: Algorithms/V3/Chronology/08_Current_Chronology_Rebaseline.md.

## Additional source boundaries

- engine/pipeline/reaction_engine.py:175–183: Cache key id(candles) plus identity check; timestamp list shared by reference, fresh list on miss, registry retains object reference; native immutable-source premise and scope clearing CP332-P12 / RE45–47 / TB97–101.
- engine/pipeline/reaction_engine.py:342–345: detect delegates to own _scan(first_only=first_only) unchanged; no additional cross-owner semantics.
- engine/bridge/trading_pipeline.py:365–373: When either bound absent select without int(index); only both present apply inclusive int index range, selected lists used by legacy and Bridge output. No calculation filter.

## Closure evidence and limitations

316 source review records, 20 chronology accessors, 14 provider contracts, 50 consumer groups, 125 selected sites and 37 historical contracts are registered with exact source and evidence. 75 additional non-matrix call forms carry explicit source/owner/consumer semantic dispositions; the 161-form discovery is lexical assistance, not proof of dynamic execution. CP292 124 source-anchor rows cover CH01–CH123 and current document heading registry fixes eight shorthand or mistaken references. The declared native source and conditional interface scope excludes arbitrary user-provided callback implementations or runtime dispatch. W3 is independent.


## Independent W2 closure disposition

PASS_SCOPED_W2_ACCEPTANCE at CP350. CP331-F05 and CP333-R01/R02 resolved within pinned native source and identified conditional interfaces; R03 reassessment complete. All 37 contracts have 138 anchor dispositions, including five direct nontransition source checks; four provider-only groups directly rechecked. This is not a runtime equivalence or W3 forensic acceptance. W3 and W4 remain NOT RUN. See `CP350_W2_Independent_Semantic_Closure_Gate.json`.
