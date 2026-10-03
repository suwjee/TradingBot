# Graph Health — 2026-09-23

- Graphify 0.9.63 / graphifyy 0.9.42; source commit `822c5ce1c1e7f464d2e08085fd6d991ee1d5d8ed`.
- Final graph: 2,691 nodes, 4,526 directed links, 147 communities.
- Normalized extraction integrity: missing=0, dangling=0, self-loops=0, duplicate endpoint pairs=0.
- Serialized graph integrity: missing=0, dangling=0, self-loops=0.
- Raw AST pass had 164 unresolved import/reference endpoints and 247 parallel endpoint-edge collapses; direct imports were resolved to path/external-module nodes and edge variants were preserved in `edge_evidence`.
- Unclassified configuration/style/batch paths are path-only nodes. `tokens.css` redacted scan flags: {'private_key_marker': False, 'jwt_like_value': False, 'credential_assignment': False, 'long_high_entropy_literals': 0}; 177 CSS custom-property names indexed, all values omitted.
- RAW/runtime paths are directory-scope markers only. No candles, drawings, caches, credentials, or session contents were read/copied.
- Previous Graphify outputs were excluded from input. No filesystem walk errors. No semantic LLM call was made; the source-located inline layer contains 10 concepts and 2 hyperedges, all explicitly grounded and value-safe.

## Raw extractor diagnostic

```text
[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 2448
unverified_code_nodes: 0
raw_edges: 4543
valid_candidate_edges: 4379
missing_endpoint_edges: 0
dangling_endpoint_edges: 164
self_loop_edges: 0
exact_duplicate_edges: 116
directed_unique_endpoint_pairs: 4132
directed_same_endpoint_collapsed_edges: 247
undirected_unique_endpoint_pairs: 4131
undirected_same_endpoint_collapsed_edges: 248
same_endpoint_group_count: 169
relation_variant_groups: 54
source_file_variant_groups: 0
source_location_variant_groups: 22
context_variant_groups: 49
post_build_graph_type: DiGraph
post_build_edges: 4143
producer_suppression_sites: 11
producer_suppression_examples:
  - L1144 seen_ids arity=unknown
  - L1410 seen_ids arity=unknown
  - L1412 seen_doc_refs arity=unknown
  - L1772 seen_ids arity=unknown
  - L2262 seen_keys arity=unknown
  - L2431 seen_keys arity=unknown
  - L3837 seen_ids arity=unknown
  - L3945 seen_ids arity=unknown
examples:
  - engine_pipeline_a_zone_detector_azonedetector_pair_trigger -> engine_pipeline_a_zone_detector_py_datetime edges=6 relations=['references'] locations=['L305'] contexts=['generic_arg', 'parameter_type']
  - engine_pipeline_e_zone_detector_ezonedetector_cross_order -> engine_pipeline_e_zone_detector_py_datetime edges=6 relations=['references'] locations=['L1381', 'L1401'] contexts=['generic_arg', 'parameter_type']
  - engine_pipeline_s_zone_detector_szonedetector_first_a_stop -> engine_pipeline_s_zone_detector_py_datetime edges=6 relations=['references'] locations=['L231', 'L267'] contexts=['generic_arg', 'parameter_type']
  - engine_pipeline_s_zone_detector_szonedetector_first_type3 -> engine_pipeline_s_zone_detector_py_datetime edges=6 relations=['references'] locations=['L482'] contexts=['generic_arg', 'parameter_type']
  - engine_pipeline_s_zone_detector_szonedetector_first_type4 -> engine_pipeline_s_zone_detector_py_datetime edges=6 relations=['references'] locations=['L543'] contexts=['generic_arg', 'parameter_type']
note: normal graph.json is post-build; raw producer loss must be measured earlier.
```

## Normalized extraction diagnostic

```text
[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 2691
unverified_code_nodes: 0
raw_edges: 4526
valid_candidate_edges: 4526
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
self_loop_edges: 0
exact_duplicate_edges: 0
directed_unique_endpoint_pairs: 4526
directed_same_endpoint_collapsed_edges: 0
undirected_unique_endpoint_pairs: 4525
undirected_same_endpoint_collapsed_edges: 1
same_endpoint_group_count: 0
relation_variant_groups: 0
source_file_variant_groups: 0
source_location_variant_groups: 0
context_variant_groups: 0
post_build_graph_type: DiGraph
post_build_edges: 4526
producer_suppression_sites: 11
producer_suppression_examples:
  - L1144 seen_ids arity=unknown
  - L1410 seen_ids arity=unknown
  - L1412 seen_doc_refs arity=unknown
  - L1772 seen_ids arity=unknown
  - L2262 seen_keys arity=unknown
  - L2431 seen_keys arity=unknown
  - L3837 seen_ids arity=unknown
  - L3945 seen_ids arity=unknown
note: normal graph.json is post-build; raw producer loss must be measured earlier.
```
