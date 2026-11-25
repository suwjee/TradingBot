# Dependency graph — current main

Static import edges (including imports inside guarded branches):

```mermaid
flowchart TD
  live_pipeline --> trading_pipeline
  trading_pipeline --> PL_PH_detector
  trading_pipeline --> core_utils
  trading_pipeline --> order_audit_engine
  trading_pipeline --> true_false
  PL_PH_detector --> core_utils
  PL_PH_detector --> lifecycle_engine
  PL_PH_detector --> order_audit_engine
  pipeline_init --> blue_line_detector
  a_zone_detector --> core_utils
  a_zone_detector --> direction_policy
  blue_line_detector --> core_utils
  blue_line_detector --> direction_policy
  e_zone_detector --> core_utils
  e_zone_detector --> direction_policy
  e_zone_detector --> order_audit_engine
  e_zone_detector --> reaction_engine
  lifecycle_engine --> core_utils
  lifecycle_engine --> direction_policy
  lifecycle_engine --> order_audit_engine
  order_audit_engine --> core_utils
  order_audit_engine --> e_zone_detector
  reaction_engine --> core_utils
  reaction_engine --> direction_policy
  s_zone_detector --> core_utils
  s_zone_detector --> direction_policy
  s_zone_detector --> order_audit_engine
  true_false --> direction_policy
  true_false --> lifecycle_engine
```

The apparent E Zone / OrderAudit cycle is a **syntactic dependency**, not a demonstrated runtime import cycle: OrderAudit's reference to EZone is guarded by TYPE_CHECKING at lines 17–18; E imports OrderAudit at module initialization. Treat type-only edges separately from runtime dependencies. Core Utilities and Direction Policy are shared primitives. Primary imports Lifecycle and OrderAudit. T/F imports Lifecycle and Direction Policy.

## Dynamic closure

Trading Bridge `load_module` (87–94) uses path-based loading and registration; `load_engine` (97–98) selects Reaction; `load_engines` (1892–1927) binds Reaction, Blue, A, S, optional E, Lifecycle with a default path, and optional Primary. These path-driven edges are not ordinary import statements. Native `main` (3717–3748) uses this bundle and shared market/state/response functions. Live Pipeline imports the shared bridge, constructs a continuation and invokes `calculate_live_from_buckets`; the latter replays stages through `_run_live_calculation` (3706–3714). Static import edges must not be mistaken for pipeline execution order. The 23 external import roots listed in the summary are Python standard-library references (including future imports); dynamic engine configuration and environment dependencies still require the runtime contract. Project startup documents require Python 3.12+; analysis here is Python 3.13.5. Chart/Vite/FARAZ are outside the 16-file production Python extraction scope and remain boundary dependencies (Phase 01 Repository_Discovery). No full downstream JavaScript call graph claimed.
