# CP359 — W3 B02 live behavior and directional A-stop finder

Pinned main c99b4c957e932d9ee70c492ca03ce80711447fc1; reaction_engine.py blob 9adffb832ffa231ba0cb01de507a30fbe62be0b0, lines 1481–1616. Separate same-assistant source-first pass, not independently staffed or blind.

RE69 initializes empty direction lists and match sets, then updates dirty zero; constructor ignores result, not side effects. RE70 validates inclusive dirty range with chained short circuit, reuses only same ordinal and equal geometry before dirty, otherwise computes span/path and marks changed only on full entry inequality. Geometry uses string price representations; remaining fields use native equality. Rebuild does not imply changed. Retain surviving unchanged pairs, recompute changed inner vs all outer and unchanged inner vs changed outer, retain all passing ordinal pairs; blocked identity is physical First/Break, not pair positions. Removal of one owner need not release another. Apply metadata to native records before map assignment; partial writes and chronology side effects are not rolled back.

RE71 validates exact direction and captures sources in two closure caches. RE72 ignores gate_event; membership hit includes cached null, scans adjacent tags in order, extends context backward, selects first tuple reaction with integer First>=gate, invokes bounded Unified only if no cached selection. Detection tuple replacement precedes reselection; failure there can leave partial cache changes. Candidate returned by reference; no exact-time acceptance or canonical Order creation. Bridge fallback and reusable-context paths differ; Order Audit performs separate time and identity admission, with canonical remap qualification.

495 category rows (111 W1, 384 additional), 24 source contract groups, 7 historical supplemental records. Four synthetic filter IDs joined using exact historical crosswalk. Zero prior local overlap or coordinate errors. CP359-F01 resolved scoped documentation precision; historical B02-07-F01–F03 retained. Prior five findings stay open. No RAW payload, runtime, ZIP, production/main change. W3 INCOMPLETE; W4 NOT RUN; Phase08 BLOCKED.

Evidence: [local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP359_W3_Live_Behavior_A_Stop_Local_Forensic_Register.json), [consumer boundaries](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP359_W3_Live_Behavior_A_Stop_Consumer_Boundaries.json), [completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP359_Completion.json).

Next source begins 1617, Unified Reaction ownership. Full cross-owner review pending.
