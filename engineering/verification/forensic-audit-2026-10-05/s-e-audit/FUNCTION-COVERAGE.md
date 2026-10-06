# S/E complete source symbol reading coverage

Every definition below belongs to a source file read completely. Reading status does not assert universal behavioral verification.

## s_zone_detector.py

| Definition | Kind | Exact source lines | Study |
|---|---|---:|---|
| `SZone` | ClassDef | 28-63 | READ_FULL |
| `SZoneDetector` | ClassDef | 66-1418 | READ_FULL |
| `__init__` | FunctionDef | 67-192 | READ_FULL |
| `_main_index` | FunctionDef | 194-195 | READ_FULL |
| `_lower_window` | FunctionDef | 197-200 | READ_FULL |
| `_reaction_confirmation_time` | FunctionDef | 202-205 | READ_FULL |
| `reaction_confirmation_time` | FunctionDef | 207-211 | READ_FULL |
| `_reset_time` | FunctionDef | 214-215 | READ_FULL |
| `_a_confirmation_time` | FunctionDef | 217-223 | READ_FULL |
| `_trend_extreme` | FunctionDef | 225-228 | READ_FULL |
| `_a_stopped` | FunctionDef | 230-231 | READ_FULL |
| `_first_a_stop` | FunctionDef | 233-267 | READ_FULL |
| `first_a_stop` | FunctionDef | 269-273 | READ_FULL |
| `_resolved_order_backed_zone` | FunctionDef | 276-292 | READ_FULL |
| `_candidate_source` | FunctionDef | 295-308 | READ_FULL |
| `_candidate_source_last` | FunctionDef | 310-328 | READ_FULL |
| `_first_trend_reaction_after_order` | FunctionDef | 330-339 | READ_FULL |
| `_nested_trend_reaction` | FunctionDef | 342-370 | READ_FULL |
| `_simple_candidate` | FunctionDef | 372-379 | READ_FULL |
| `_type3_reset_leg` | FunctionDef | 381-395 | READ_FULL |
| `_type3_has_trend_reaction` | FunctionDef | 397-404 | READ_FULL |
| `_first_type3` | FunctionDef | 406-453 | READ_FULL |
| `_type4_has_blue` | FunctionDef | 456-465 | READ_FULL |
| `_first_type4` | FunctionDef | 467-535 | READ_FULL |
| `_build_type4_zone` | FunctionDef | 537-587 | READ_FULL |
| `_candidate_after_order` | FunctionDef | 590-629 | READ_FULL |
| `_a_source_event_time` | FunctionDef | 631-638 | READ_FULL |
| `_a_owned_by_s` | FunctionDef | 640-679 | READ_FULL |
| `_a_pair_is_reset_reset` | FunctionDef | 681-692 | READ_FULL |
| `eligible_a_zones` | FunctionDef | 695-697 | READ_FULL |
| `_candidate_timing` | FunctionDef | 699-742 | READ_FULL |
| `_candidate_before_order` | FunctionDef | 744-786 | READ_FULL |
| `_candidate_event_time` | FunctionDef | 788-801 | READ_FULL |
| `candidate_event_time` | FunctionDef | 803-807 | READ_FULL |
| `_blue_formation_time` | FunctionDef | 810-838 | READ_FULL |
| `_candidate_cross_has_blue` | FunctionDef | 840-855 | READ_FULL |
| `_has_ordinary_trend_reaction` | FunctionDef | 857-865 | READ_FULL |
| `_candidate_crossed` | FunctionDef | 868-870 | READ_FULL |
| `_decision` | FunctionDef | 873-996 | READ_FULL |
| `_build_type3_zone` | FunctionDef | 999-1055 | READ_FULL |
| `_build_order_backed_zone` | FunctionDef | 1057-1226 | READ_FULL |
| `detect` | FunctionDef | 1228-1302 | READ_FULL |
| `reconcile_shared_order_stops` | FunctionDef | 1305-1418 | READ_FULL |
| `detect_s_zones` | FunctionDef | 1421-1444 | READ_FULL |

## e_zone_detector.py

| Definition | Kind | Exact source lines | Study |
|---|---|---:|---|
| `EZone` | ClassDef | 31-66 | READ_FULL |
| `EZoneDetector` | ClassDef | 69-1108 | READ_FULL |
| `__init__` | FunctionDef | 70-223 | READ_FULL |
| `sequence_resets` | FunctionDef | 226-227 | READ_FULL |
| `sequence_resets` | FunctionDef | 230-242 | READ_FULL |
| `_reset_time` | FunctionDef | 244-245 | READ_FULL |
| `_main_index` | FunctionDef | 247-248 | READ_FULL |
| `_first_cross_position` | FunctionDef | 251-266 | READ_FULL |
| `_stop_value` | FunctionDef | 268-269 | READ_FULL |
| `_build_extreme_sparse` | FunctionDef | 271-298 | READ_FULL |
| `_extreme_position` | FunctionDef | 300-317 | READ_FULL |
| `_first_parent_stop` | FunctionDef | 320-331 | READ_FULL |
| `_confirmation_for` | FunctionDef | 333-334 | READ_FULL |
| `_confirmation` | FunctionDef | 336-337 | READ_FULL |
| `_reaction_first_time` | FunctionDef | 339-340 | READ_FULL |
| `_parent_stop` | FunctionDef | 343-349 | READ_FULL |
| `parent_stop` | FunctionDef | 351-355 | READ_FULL |
| `_extreme_between` | FunctionDef | 358-372 | READ_FULL |
| `_zone` | FunctionDef | 374-475 | READ_FULL |
| `set_consumed_s_evidence` | FunctionDef | 477-487 | READ_FULL |
| `_apply_consumed_s_evidence` | FunctionDef | 489-505 | READ_FULL |
| `continuation_chain_from_s` | FunctionDef | 507-555 | READ_FULL |
| `replace_with_earlier_continuation` | FunctionDef | 557-598 | READ_FULL |
| `descends_from_owner` | FunctionDef | 566-580 | READ_FULL |
| `resolve_same_source_conflicts` | FunctionDef | 600-642 | READ_FULL |
| `outranks` | FunctionDef | 618-625 | READ_FULL |
| `restore_independent_s_roots` | FunctionDef | 644-703 | READ_FULL |
| `_invalid_s_without_order_cause` | FunctionDef | 705-727 | READ_FULL |
| `_discover_candidate_chains` | FunctionDef | 729-819 | READ_FULL |
| `_reconcile_candidate_chains` | FunctionDef | 821-1095 | READ_FULL |
| `valid_order` | FunctionDef | 852-856 | READ_FULL |
| `parent_active` | FunctionDef | 858-929 | READ_FULL |
| `stopped_by` | FunctionDef | 931-936 | READ_FULL |
| `ownership_priority` | FunctionDef | 987-992 | READ_FULL |
| `collect_lineage` | FunctionDef | 1073-1085 | READ_FULL |
| `detect` | FunctionDef | 1098-1108 | READ_FULL |
| `detect_e_zones` | FunctionDef | 1111-1140 | READ_FULL |
