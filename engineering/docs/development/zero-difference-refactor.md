> Current precedence/location note (2026-09-29): explicit user instruction and root AGENTS govern this document. Trading semantics require Plugin/Vault retrieval before source interpretation. For this structural task, the live working tree is authoritative; package/bootstrap and authority examples below are subordinate. Production Engine paths and exact references remain unchanged. Component tests and state use the current engineering document index.

# TradingBot — Production Zero-Difference Refactor, Performance & Code-Quality Specification

## Purpose

This document is the mandatory engineering specification for any programmer or AI performing refactoring, performance optimization, resource optimization, structural cleanup, or maintainability improvement on the TradingBot production engine.

The objective is to improve implementation quality and execution efficiency while preserving the existing trading behavior exactly.

The governing equation is:

```text
CURRENT STABLE BEHAVIOR == REFACTORED STABLE BEHAVIOR
```

No approximation is allowed for behavior-preserving work.

The priority order is:

1. Correctness and zero behavioral difference.
2. Determinism and chronology integrity.
3. Public/output compatibility.
4. Correct architecture and ownership.
5. Performance.
6. Memory/resource efficiency.
7. Readability and maintainability.
8. Cosmetic cleanup.

If performance, code reduction, elegance, or memory savings conflict with exact behavior, exact behavior wins.

---

# 1. Scope is discovered from the live project, never from a fixed file count

The refactor must begin by recursively inspecting the complete current `engine/` tree and every directly relevant dependency, test, configuration file, RAW dataset, regression fixture, and project instruction.

The current engine structure includes the following areas and every one of them must be inspected:

```text
engine/
├── __init__.py
├── algorithms/
│   ├── TradingBot_Bearish_Algorithm_Reference_*.md
│   └── TradingBot_Bullish_Algorithm_Reference_*.md
├── bridge/
│   ├── __init__.py
│   └── trading_pipeline.py
├── pipeline/
│   ├── __init__.py
│   ├── a_zone_detector.py
│   ├── blue_line_detector.py
│   ├── core_utils.py
│   ├── direction_policy.py
│   ├── e_zone_detector.py
│   ├── lifecycle_engine.py
│   ├── order_audit_engine.py
│   ├── reaction_engine.py
│   └── s_zone_detector.py
└── styles/
    └── reaction-detector.css
```

This tree is an inspection baseline, not a permanent hard-coded module count. If the live tree contains additional production files, tests, support files, schemas, or dependencies, they must also be discovered and inspected.

Do not ignore a file because it was absent from an older document.

Do not assume a historical file list is authoritative.

---

# 2. No hash or file-version authority

This specification must not use file hashes or file-version numbers to decide which code is Current, to prove equivalence, or to define acceptance.

Current Source means the actual active production files present in the current project working tree at the start of the task, resolved using the project instructions and repository context.

Rules:

- Never pin this specification to a hash.
- Never pin this specification to a numeric file version.
- Never reject a current file merely because an older document names a different version.
- Never use a hash match as a substitute for semantic or direct output comparison.
- Never use a version string as a substitute for reading the file.
- If repository metadata exists, it may be inspected as supporting context, but it is not the behavioral authority for this refactor specification.

The actual Source, References, tests, and RAW evidence must be read directly.

---

# 3. Mandatory authority chain

For refactor and optimization work, use this authority order:

```text
Latest explicit user instruction
→ engineering/docs/ai/operating-protocol.md
→ AGENTS.md
→ Current Bullish/Bearish Algorithm References
→ Current Production Source
→ Current tests / regression fixtures
→ Authoritative RAW chronology
→ historical evidence only when needed for comparison
```

Production Source defines what the software currently executes.

Algorithm References define the documented intended trading specification.

RAW defines factual market chronology.

If Source and Reference disagree, report the mismatch explicitly. Do not silently alter Source during a behavior-preserving refactor in order to make it match documentation.

If the mismatch represents a possible algorithm defect, separate that issue from the refactor and obtain explicit behavioral approval before changing it.

---

# 4. Mandatory startup audit

Before editing production code, the programmer/AI must:

1. Read `engineering/docs/ai/operating-protocol.md` completely.
2. Read `AGENTS.md` completely.
3. Recursively inventory the live `engine/` tree.
4. Read all files under `engine/algorithms/` completely.
5. Read every production Python file under `engine/bridge/` and `engine/pipeline/` completely.
6. Inspect package `__init__.py` files and their import/export behavior.
7. Inspect `engine/styles/` so presentation artifacts are not accidentally modified by broad cleanup.
8. Locate and read all tests that exercise the engine, bridge, serialization, lifecycle, OrderAudit, and public output.
9. Locate relevant RAW datasets and regression anchors.
10. Inspect manifests/configuration/launchers that can change runtime behavior.
11. Build an ownership map and dependency graph before refactoring.
12. Identify the normal production entry path and the exact commands used for baseline execution.
13. Identify all runtime-visible outputs, side effects, files, streams, and APIs affected by the engine.

No substantial refactor may begin after reading only the file that appears slow.

---

# 5. Refactor classification

A pure refactor or implementation-only performance optimization may change implementation but must not intentionally change trading behavior.

A pure refactor must preserve all applicable:

- decisions;
- chronology;
- first/last event selection;
- strict/equality boundaries;
- object/domain identity;
- source selection;
- tie-breaking;
- ownership;
- provenance;
- Decimal values and representations;
- lifecycle state;
- StopAll boundaries;
- visibility;
- ordering;
- public API behavior;
- CLI behavior where applicable;
- serialization shape and stable content;
- error semantics that are part of the public contract.

If any of these intentionally changes, stop calling the work a pure refactor. Treat it as a behavioral/API change and follow the project’s behavioral-change workflow instead.

---

# 6. Absolute zero-difference contract

For a behavior-preserving refactor:

```text
Old stable result == New stable result
```

This applies to every affected stage, not only the final JSON.

The following must be compared when applicable:

```text
RAW normalization
Reaction
Reset
Internal Reaction
Blue
A
S
E
Lifecycle
StopAll
Order
OrderAudit
Visibility / final reconciliation
Final direction payload
Bridge/public projection
Serialized public output
```

The comparison must include:

- exact count;
- exact ordering;
- exact object fields;
- exact identities;
- exact timestamps/indexes;
- exact Decimal values/strings;
- exact nullability;
- exact provenance;
- exact parent/child relationships;
- exact accepted/rejected state;
- exact final serialization key/list/object ordering when contractually stable.

Only explicitly non-deterministic benchmark/telemetry measurements may be excluded from stable-output equality.

Do not create new exclusions merely because they are inconvenient to match.

---

# 7. Fix to the old dependency-chain rule

In a pure refactor, no candle behavior is supposed to change.

Therefore a rule such as “if one candle changes, downstream changes may be legitimate” does not apply to zero-difference refactoring.

If the first stable behavioral difference appears anywhere in the calculation chain, the optimization/refactor is unverified and must be investigated.

Downstream differences are not acceptable simply because they are causally downstream from an earlier difference.

For pure refactor work:

```text
FIRST DIFF = REFRACTOR DEFECT UNTIL PROVEN OTHERWISE
```

If the difference is actually caused by an intentionally approved behavioral change, the task must be reclassified and verified under the behavioral-change protocol.

---

# 8. Behavioral baseline must exist before optimization

Before the first production edit, create a reproducible baseline using the unmodified Current Source.

The baseline must record, for each selected scenario:

- exact input dataset;
- full calculation scope;
- visible/output scope separately;
- direction;
- analysis timeframe;
- lower timeframe;
- configuration and flags;
- command/entry point;
- stage outputs;
- final stable serialized output;
- runtime;
- per-stage runtime where available;
- peak resident memory where practical;
- process exit status and relevant errors.

Store baseline outputs as direct artifacts that can be compared after refactoring.

Do not rely only on counts.

Do not rely only on summaries.

Do not rely only on a checksum/hash.

If a baseline run does not finish successfully, report it as incomplete and do not claim full zero-difference verification for that scenario.

---

# 9. Full RAW is calculation authority

Do not optimize by clipping required historical state.

Rules:

- Full historical context required by the algorithm must remain available.
- Visible-range filtering must not become calculation-range filtering.
- Do not remove earlier events because they are outside the final chart range if they can affect later state.
- Do not replace fine chronology with aggregated OHLC for speed.
- Do not mutate RAW.
- Do not reorder RAW.
- Do not fabricate missing events.

When event ordering matters, use the finest authoritative RAW available:

```text
1s RAW > 5s RAW > coarser data
```

A coarser candle must not be used to infer exact intrabar chronology when finer RAW is available.

---

# 10. Numerical contract

Price-sensitive logic must preserve the project’s exact Decimal semantics.

Never use binary floating point as a shortcut for:

- prices;
- thresholds;
- extrema;
- equality-sensitive comparisons;
- strict crossings;
- stops;
- derived levels;
- serialized price representations.

Normalize numeric input once where architecture permits and reuse the normalized representation.

Avoid repeated Decimal construction in hot loops when the same normalized value already exists.

Optimization must preserve both the numerical result and the source/winner semantics associated with that result.

Returning the same extreme price from a different source candle is not necessarily equivalent.

---

# 11. Candle-color and strict-boundary invariants

Project-wide candle color must remain:

```text
GREEN: close >= open
RED:   close < open
```

Therefore Doji remains GREEN.

For every rule defined as strict, equality remains non-triggering.

Never silently change:

```text
<  to <=
>  to >=
```

Do not “simplify” boundary code without proving identical inclusive/exclusive semantics.

---

# 12. Directional mirror safety

For rules documented as directional mirrors, preserve the exact directional transformation and the identical invariant semantics.

Typical directional primitives include:

```text
Low ↔ High
minimum ↔ maximum
< ↔ >
FirstRed ↔ FirstGreen
Bullish ↔ Bearish
```

Direction-invariant semantics such as identity, chronology policy, lifecycle ownership, stable ordering, serialization structure, Doji semantics, and provenance must not be arbitrarily inverted.

Important refactor rule:

Do not use a refactor as an excuse to “correct” an existing intentional or currently executed directional asymmetry. If Source and documentation disagree, report it separately and preserve Current Source behavior until a behavioral decision is explicitly approved.

Both directions must be runtime-verified whenever changed code can affect directional behavior.

---

# 13. Canonical code ownership

Every rule must remain in its owning component.

The current ownership model is:

### `reaction_engine.py`
Owns Reaction, Reset, Internal-Reaction behavior, reaction chronology, reaction-specific candidate/state processing, and lower-timeframe structures that are intrinsic to Reaction behavior.

### `blue_line_detector.py`
Owns Blue detection, Blue-specific strike/stop/validity behavior, and Blue-specific public/internal state.

### `a_zone_detector.py`
Owns A formation, Blue-to-A relationships, A boundaries, A ownership, inherited A state, and A-specific stop behavior.

### `s_zone_detector.py`
Owns S formation, S candidate competition, S-specific Order-linked decision logic, S source selection, S color/type/formation state, and S-local reconciliation.

It must not become the global authoritative OrderAudit ledger when `order_audit_engine.py` owns that responsibility.

### `e_zone_detector.py`
Owns E formation, E family/continuation behavior, E-specific parent/cause discovery, E-specific Order cause discovery where required by the E algorithm, and E-local reconciliation.

It must not absorb unrelated lifecycle or global OrderAudit authority merely for convenience.

### `lifecycle_engine.py`
Owns lifecycle priority, dominance, StopAll state transitions, cycle/reset semantics, lifecycle reconciliation, and lifecycle/visibility rules assigned to that engine.

### `order_audit_engine.py`
Owns authoritative Order/OrderAudit reconciliation, physical Order identity handling, cause/provenance reconciliation, deduplication/ownership rules assigned to OrderAudit, accepted/live Order state, and OrderAudit serialization support owned by that component.

Indexes built for OrderAudit acceleration remain secondary to the authoritative ledger.

### `direction_policy.py`
Owns genuinely shared directional primitives only: directional field/extreme/comparator/policy selection and other behavior explicitly assigned to directional policy.

It must not become a dumping ground for stage-specific business rules.

### `core_utils.py`
Owns behavior-neutral shared primitives such as canonical generic identity/normalization helpers that are truly cross-stage.

It must not own lifecycle, S, E, Order, or other domain policy simply to reduce duplication.

### `trading_pipeline.py`
Owns pipeline orchestration, loading/wiring, market-context preparation, stage sequencing, final projection/serialization orchestration, progress/timing integration, and bridge/public output assembly.

It must not implement hidden duplicate trading algorithms that belong to pipeline stages.

### package `__init__.py` files
Own package/import/export surface only.

Do not add trading behavior through import side effects.

### `engine/algorithms/*.md`
These are specifications/documentation and reconstruction/reference artifacts. They are not alternate runtime engines.

### `engine/styles/reaction-detector.css`
Owns presentation styling only. A refactor of calculation code must not alter visual styling unless presentation work is explicitly part of scope.

---

# 14. No arbitrary relocation of logic

Do not move code merely because another file appears more convenient.

Before moving any function or block, prove:

- the destination is the true owner;
- dependencies improve rather than worsen;
- no circular import is created;
- no state becomes more global;
- no business rule is duplicated;
- testability improves or remains at least equal;
- public/internal interfaces remain stable;
- the move does not hide a stage boundary.

If ownership is unclear, do not move the logic until the ambiguity is resolved.

New production modules are not created as part of a normal zero-difference refactor unless the user explicitly authorizes an architecture change.

---

# 15. Dependency-direction rules

Dependencies must remain understandable and one-directional where architecture permits.

Rules:

- lower-level neutral helpers must not import higher-level lifecycle/business stages;
- serializers must not call back into trading calculation to reconstruct missing state;
- stage engines must not depend on presentation/CSS;
- package initialization must not trigger calculations;
- avoid circular imports;
- avoid hidden import-time mutation;
- avoid monkey-patching production behavior;
- avoid dynamic behavior injection that makes ownership difficult to trace;
- use explicit parameters/interfaces rather than reaching into unrelated module globals.

A refactor that reduces local code while increasing architectural coupling is not an improvement.

---

# 16. Single source of truth

Every business rule should have one authoritative implementation whenever architecture permits.

Do not copy/paste the same rule into multiple modules.

Do not maintain separate Bullish/Bearish implementations when a shared direction primitive can safely express the mirror without obscuring ownership.

Do not centralize two visually similar code blocks if they represent different domain policies.

Before extracting a helper, decide whether the duplication is:

```text
same rule → centralize safely
different owner/policy → keep separate
```

Abstraction is justified by shared semantics, not by similar syntax.

---

# 17. Clean-code standard

Production code must be easy to audit against the algorithm.

Prefer:

- small focused functions;
- one clear responsibility per function;
- descriptive domain names;
- explicit inputs and outputs;
- explicit type hints where useful;
- immutable structures where appropriate;
- narrow interfaces;
- guard clauses when they reduce nesting;
- deterministic sorting keys;
- explicit validation;
- explicit state transitions;
- comments explaining WHY;
- minimal side effects;
- local reasoning without hidden global context.

Avoid:

- giant multi-purpose functions;
- deeply nested control flow when clearer decomposition exists;
- Boolean-flag combinations that create hidden modes;
- vague helper names;
- magic timestamps/prices/indexes;
- magic constants without meaning;
- broad `except` blocks;
- swallowed exceptions;
- silent fallbacks;
- duplicated rules;
- dead code;
- unused helpers/imports;
- commented-out old implementations;
- debug prints;
- temporary bypass flags;
- TODOs representing required production cleanup;
- speculative frameworks or abstractions;
- clever code that is harder to verify than the straightforward equivalent.

Shorter code is not automatically better code.

---

# 18. Naming standard

Use TradingBot domain terminology consistently with Current Source and Algorithm References.

Names must describe semantic meaning, not implementation accidents.

Prefer names such as:

```text
first_crossing
confirmation_time
source_extreme
order_identity
decision_event_time
accepted_order
source_index
stop_event
lifecycle_state
```

Avoid names such as:

```text
x
tmp
data2
thing
fix
special_case
obj2
val
arr
```

Additional rules:

- Boolean names should communicate truth meaning, such as `is_*`, `has_*`, `can_*`, `should_*` where appropriate.
- Collections should normally use plural semantic names.
- Index variables may be short only in tiny obvious local loops; persisted/domain indexes need semantic names.
- Do not rename established public fields or domain concepts during a pure refactor merely for style.
- Do not introduce a new synonym for an existing TradingBot concept.

---

# 19. Function and interface design

Every function should have a stable, explainable contract.

For changed functions, confirm:

- responsibility;
- inputs;
- assumptions;
- output meaning;
- mutation/side effects;
- ownership;
- chronology expectations;
- error behavior;
- complexity on full RAW.

Prefer pure or near-pure calculation helpers when practical.

Do not let a generic utility secretly mutate lifecycle or trading state.

Do not pass large state objects merely to access one field when a narrower interface improves clarity without causing excessive churn.

Do not fragment one coherent rule into so many tiny helpers that the algorithm becomes impossible to follow.

The correct granularity is the smallest structure that remains semantically clear and auditable.

---

# 20. Comments and docstrings

Comments/docstrings should document non-obvious engineering or algorithm constraints, including:

- WHY a boundary is inclusive/exclusive;
- WHY a strict comparator is required;
- WHY a source/tie winner is selected;
- WHY an index/cache is behavior-safe;
- WHY a lifecycle state must survive presentation filtering;
- WHY an apparently simpler implementation would be wrong;
- ownership and mutation contracts;
- complexity assumptions where material.

Do not add comments that simply paraphrase the next line.

Do not preserve obsolete comments after changing structure.

Do not document one historical timestamp as if it were a general rule.

---

# 21. Complexity review is mandatory before optimization

Analyze complexity across the call chain, not only inside the function being edited.

For every hot or RAW-driven path, classify the expected time behavior approximately:

```text
O(n)
O(n log n)
O(n * k) for small bounded k
O(n²) or worse
```

Potentially unbounded `O(n²)` work over full history is a performance risk and must be justified or redesigned if an exact semantics-preserving alternative exists.

Look specifically for:

- loop-inside-loop over history;
- helper calls inside loops that themselves scan history;
- repeated `sort()`;
- repeated list membership on large lists;
- repeated `min()`/`max()` over overlapping ranges;
- repeated timestamp-to-index linear lookup;
- repeated duplicate detection by full scan;
- repeated serialization/parsing;
- repeated reconstruction of the same candidate collection.

Do not hide expensive work inside comprehensions, generators, properties, or helpers.

---

# 22. Performance optimization order

Optimize in this order:

1. Eliminate unnecessary work.
2. Fix algorithmic complexity.
3. Reuse already normalized/derived data.
4. Add safe indexes/range lookup structures.
5. Reduce repeated allocation/object churn.
6. Optimize hot-path implementation details.
7. Consider concurrency only after sequential inefficiency is addressed.

Do not start with micro-optimization while a repeated full-history scan remains.

---

# 23. RAW and chronology performance-by-design

Within one run, reuse authoritative normalized data whenever architecture permits.

Prefer:

- one-time RAW parsing;
- one-time timestamp normalization;
- one-time Decimal normalization;
- monotonic timestamp arrays;
- timestamp-to-canonical-index maps;
- canonical identity maps;
- sorted event arrays;
- bounded range indexes;
- `bisect`/binary-search boundaries;
- monotonic cursors for sequential scans;
- incremental state only when it exactly matches algorithm semantics.

Avoid:

- rereading the same RAW file for each stage;
- rebuilding identical timestamp arrays in multiple stages;
- reparsing datetime values in hot loops;
- reconverting normalized Decimal values;
- repeatedly recalculating immutable candle properties;
- copying huge slices merely to run min/max/search;
- converting full authoritative collections to alternate forms without a proven need.

---

# 24. Range-query safety

Range-query acceleration must preserve more than the extreme numeric value.

For each optimized query, preserve exactly:

- range start/end;
- inclusive/exclusive boundaries;
- direction;
- strict/equality semantics;
- first/last tie winner;
- source candle/index/time;
- Decimal semantics;
- chronology.

If an index returns the same minimum/maximum price from a different source event than Current Source, the optimization may be wrong even if the displayed price matches.

---

# 25. Cache and memoization safety

Caches are accelerators, never authority.

Default rule:

```text
cache scope = current calculation run
```

Before adding any cache, prove:

- the cached computation is deterministic;
- every behavior-affecting input is represented;
- direction is represented when relevant;
- run/dataset context cannot collide;
- lifecycle mutation cannot make the entry stale, or invalidation is exact;
- later reconciliation cannot change the authoritative result, or invalidation is exact;
- memory is bounded;
- reset boundaries are correct;
- the cache cannot leak state into the next run.

Do not cache partially finalized lifecycle decisions without a formally correct invalidation model.

At StopAll or another hard lifecycle boundary, all derived per-cycle cache/index/counter state owned by that cycle must reset consistently.

A fast stale cache is a correctness defect.

---

# 26. Authoritative collections vs acceleration structures

Canonical chronological/state collections remain authoritative unless the Current architecture explicitly defines otherwise.

The following are normally secondary acceleration structures:

```text
sets
dicts
lookup maps
side indexes
binary-search arrays
range indexes
memoization caches
```

They must not silently redefine:

- chronology;
- ownership;
- duplicate policy;
- ordering;
- winner selection;
- identity;
- lifecycle truth.

Do not iterate an unordered accelerator as if its iteration order were the canonical event order.

---

# 27. Memory and allocation efficiency

Memory optimization is part of performance engineering, but must preserve behavior.

In high-volume paths:

- avoid duplicate full-history collections containing the same logical data;
- avoid large temporary slices when index bounds suffice;
- avoid cloning/replacing domain objects repeatedly without semantic need;
- avoid unnecessary deep copies;
- avoid materializing generators/iterators into full lists without need;
- bound caches;
- release stage-local large temporaries when no downstream stage needs them;
- reuse immutable normalized values;
- avoid retaining references that prevent large obsolete structures from being collected;
- prefer compact keys/structures only when clarity and identity semantics remain intact.

Do not sacrifice readability for microscopic memory savings in cold code.

Do not use float to reduce Decimal cost or memory.

---

# 28. CPU hot-path discipline

Treat code executed once per candle, candidate, Reaction, Order, S/E event, or lifecycle transition as potentially hot.

Inside hot paths, avoid:

- file I/O;
- repeated JSON serialization;
- per-item debug logging;
- repeated sorting;
- repeated direction normalization;
- repeated full-history helper scans;
- repeated string formatting;
- unnecessary exceptions for normal control flow;
- repeated dynamic attribute discovery when a direct stable access exists;
- unnecessary temporary collections.

Hoist loop-invariant work outside the loop when semantics permit.

Do not apply obscure micro-optimizations unless profiling shows they matter.

---

# 29. I/O discipline

Calculation stages should operate on prepared in-memory authoritative state, not repeatedly hit disk.

Rules:

- read input once where architecture permits;
- do not write temporary per-event files in production calculation;
- do not serialize/deserialize between internal stages merely for convenience;
- keep benchmark output writing outside timed calculation sections unless production behavior includes that I/O;
- keep diagnostic/profiling I/O out of benchmark runs.

---

# 30. Concurrency and parallelism

Do not add threading, multiprocessing, async execution, or parallel stage evaluation merely to improve a benchmark number.

Parallelism is allowed only when all are proven:

- stage dependencies allow it;
- deterministic chronology is preserved;
- shared mutable state is eliminated or correctly synchronized;
- output ordering is stable;
- cache ownership is clear;
- lifecycle sequencing is not violated;
- process/thread overhead is justified by measured benefit;
- exact regression remains zero-difference.

Never parallelize inherently sequential lifecycle logic whose order is part of the algorithm.

First remove avoidable sequential inefficiency.

---

# 31. Determinism contract

Identical Source, RAW, configuration, timeframe, direction, and request parameters must produce identical stable outputs.

Do not introduce hidden dependency on:

- wall-clock time;
- randomness;
- unordered set/dict iteration for authoritative selection;
- previous runs;
- mutable module-global trading state;
- thread scheduling;
- unrelated files/environment state;
- benchmark instrumentation.

All tie-breaking must be explicit and stable.

Run repeated determinism checks after refactoring.

---

# 32. Error handling

Fail clearly on broken internal invariants.

Do not silently invent substitute:

- chronology;
- parentage;
- identity;
- provenance;
- geometry;
- Order cause;
- lifecycle state.

Use explicit validation for impossible/invalid conditions where appropriate.

Avoid broad exception swallowing.

Do not convert a real defect into an empty/default result merely to keep the pipeline running.

Public error behavior that is part of the existing contract must remain stable in a pure refactor.

---

# 33. Serialization is a projection, not a second algorithm

Serializers must project finalized authoritative state.

Do not:

- recalculate trading logic inside serialization;
- repair upstream state by filtering it away;
- silently reorder contractually ordered collections;
- change null/default behavior;
- change field meaning;
- change Decimal/timestamp representation;
- rename/remove/add public fields during pure refactor;
- expose internal acceleration structures.

If significant trading logic is needed in a serializer, re-check ownership upstream.

---

# 34. Bridge and public projection safety

`trading_pipeline.py` and bridge/public projection are part of the observable contract.

When refactoring pipeline/serialization code, preserve:

- stage execution order;
- required shared context;
- direction behavior;
- display-range vs calculation-range separation;
- progress semantics if public;
- final visibility;
- public payload shape;
- stable object/list ordering;
- optional bridge projection behavior;
- CLI/request parameter meaning;
- exit/error behavior where contractually visible.

Do not move business logic into the bridge simply because all stages pass through it.

---

# 35. Package initializer safety

Inspect all `__init__.py` files during the refactor.

Preserve/import only intended package surface.

Avoid:

- import-time trading calculations;
- circular imports;
- expensive hidden initialization;
- global mutable state creation;
- side effects that change test order or repeated-run behavior.

A package-surface cleanup must not break the production loader/bridge path.

---

# 36. Presentation/CSS isolation

`engine/styles/reaction-detector.css` must be inspected as part of the engine tree but must remain presentation-only.

Unless UI work is explicitly requested:

- do not alter CSS during algorithm refactor;
- do not use CSS/presentation changes to hide calculation differences;
- do not let presentation state influence calculation truth.

If presentation is intentionally changed in a separate scope, verify it independently from trading-equivalence tests.

---

# 37. No dataset-specific or fixture-specific production logic

Never add a production branch tied only to:

- symbol;
- exact timestamp;
- exact price;
- RAW filename;
- fixture name;
- test name;
- one array index;
- expected JSON;
- one historical example.

An optimization or correction must express a general engineering/algorithm rule valid for every equivalent state.

Historical examples are regression evidence, not production conditions.

---

# 38. No temporary production hacks

Do not leave in production:

- debug branches;
- benchmark-only branches;
- temporary logging;
- disabled validations;
- bypass switches;
- expected-value injections;
- commented-out old code;
- “remove later” shortcuts;
- profiler hooks enabled by default;
- fixture-dependent cache seeding.

All temporary instrumentation must be removed or strictly isolated from normal production behavior before completion.

---

# 39. Profiling before optimization

Do not guess where the system is slow when profiling is practical.

Before substantial performance edits:

1. Run the baseline.
2. Measure end-to-end runtime.
3. Measure stage runtime where available.
4. Use a profiler appropriate to the environment to identify hot call paths.
5. Inspect algorithmic complexity of those call paths.
6. Inspect repeated scans/sorts/conversions/allocations.
7. Inspect peak memory separately when memory is material.
8. Identify the top measured bottlenecks.
9. Optimize highest-impact safe bottlenecks first.

Do not run heavy tracing/profiling instrumentation inside the final benchmark run if it materially changes timing.

Profiling evidence guides optimization; regression evidence proves correctness.

---

# 40. Benchmark methodology

Performance claims must be reproducible and comparable.

For baseline and refactored runs, keep identical:

- machine/environment;
- Python/runtime mode;
- Source entry path;
- RAW dataset;
- calculation start/history;
- direction;
- timeframe;
- configuration/flags;
- output mode;
- logging/debug state;
- process priority/power mode where controllable.

Measure at minimum:

- wall-clock time;
- CPU time where practical;
- per-stage wall time where practical;
- peak resident memory;
- output counts;
- exact stable output equality.

Benchmark guidance:

- use a fresh process for independent runs when process state/caches can affect results;
- separate correctness runs from profiler-heavy runs;
- use warm-up only when measuring steady-state behavior and document that choice;
- if startup/import cost is production-relevant, measure cold-start separately;
- use multiple measured repetitions for representative workloads when practical;
- compare median rather than only one best run;
- report run-to-run spread when it is material;
- alternate baseline/refactored runs when practical to reduce thermal/load bias;
- do not run unrelated heavy tasks simultaneously;
- do not claim improvement from incomparable runs.

For extremely heavy full-RAW runs, a smaller number of repetitions may be used, but limitations must be stated and no exaggerated performance claim may be made.

---

# 41. Performance acceptance

A performance optimization is accepted only if:

1. all mandatory zero-difference checks pass;
2. the targeted bottleneck shows a real/repeatable improvement or a clearly demonstrated complexity/resource improvement;
3. no unrelated stage suffers an unexplained material regression;
4. peak memory does not increase without a justified tradeoff;
5. code readability/ownership does not materially degrade;
6. the optimization remains general rather than dataset-specific.

Do not require an arbitrary percentage improvement.

Do not claim “faster” when measurement noise is comparable to the observed difference.

If performance does not improve meaningfully, retain the simpler implementation unless the structural change has another concrete engineering benefit.

---

# 42. Memory acceptance

For changes that add indexes/caches/collections, compare peak memory before and after.

A memory increase is acceptable only when:

- it produces a measured meaningful performance gain or reduces correctness risk;
- the added memory is bounded;
- the lifetime is controlled;
- no cross-run leak exists;
- large temporary structures are released;
- the tradeoff is reported.

A cache that makes runtime faster while causing uncontrolled memory growth is rejected.

---

# 43. Refactor sequencing

Use small, auditable steps.

Recommended sequence:

```text
Inspect complete project
→ establish behavioral baseline
→ profile / complexity review
→ build ownership/dependency map
→ define exact bottleneck and invariants
→ design semantics-preserving change
→ implement smallest coherent step
→ run targeted exact comparison
→ continue to next step
→ perform maintainability cleanup only within affected path
→ run full exact regression
→ run benchmark/memory comparison
→ inspect final diff
→ synchronize documentation/references when required
```

Do not perform a massive rewrite and attempt to understand differences only at the end.

After each meaningful structural step, compare behavior while the diff is still small enough to diagnose.

---

# 44. Refactor design review before coding

Before editing, answer these questions explicitly or mentally:

1. What exact component owns the code?
2. What behavior must remain unchanged?
3. What input size does the path see on full RAW?
4. What is the current call-chain complexity?
5. What is the proposed complexity?
6. Which scans/sorts/lookups repeat?
7. Which immutable values can be computed once?
8. Which lookup/range index is safe?
9. What tie/source semantics must it preserve?
10. Which state mutates later?
11. What invalidates caches/indexes?
12. What resets at lifecycle boundaries?
13. What must remain Decimal?
14. Which lower-TF chronology is required?
15. What mirror impact exists?
16. What identity/provenance must remain exact?
17. What additional memory is retained?
18. Which tests prove exact equivalence?
19. Is the resulting code easier or harder to audit?
20. Is there a simpler semantics-preserving design?

If the design cannot answer these safely, do not implement it yet.

---

# 45. Maintainability gate

Before final regression, review every changed path for:

- correct owner;
- focused functions;
- domain-correct naming;
- explicit boundaries;
- no duplicated rule;
- no unexplained magic constants;
- no unnecessary nesting;
- no hidden mutation;
- no broad exception swallowing;
- no stale comments;
- no dead code;
- no unused imports/helpers;
- no temporary branches;
- no avoidable repeated scans;
- no avoidable repeated sort/parsing/conversion;
- no unsafe cache;
- no unbounded memory growth;
- no direction drift;
- no serializer-side business logic;
- no new circular dependencies;
- no technical debt knowingly introduced by the current refactor.

Pre-existing unrelated debt should be reported separately rather than triggering uncontrolled project-wide cleanup.

---

# 46. Mandatory regression hierarchy

Run the strongest applicable verification in this order:

1. Syntax/compile checks for every changed Python file.
2. Import/runtime initialization through the real production path.
3. Focused unit/invariant tests.
4. Exact targeted stage comparison.
5. Equality/boundary tests.
6. Upstream zero-difference comparison.
7. Downstream zero-difference comparison.
8. Order/OrderAudit integrity comparison when applicable.
9. Serialization/public-contract comparison.
10. Repeated determinism comparison.
11. Bullish runtime verification.
12. Bearish runtime verification.
13. Mirror/reflected-market verification where applicable.
14. Historical regression anchors.
15. Representative continuous RAW runs.
16. Full production-style RAW runs for high-risk/historical-state/cache/lifecycle changes.
17. Performance and peak-memory comparison.

A tiny fixture alone is never sufficient evidence for a change that affects long-lived state, caching, chronology, lifecycle, or full-history searches.

---

# 47. RAW dataset selection for regression

Discover RAW datasets from the current project rather than hard-coding one filename into production or this specification.

For verification, select datasets that collectively exercise:

- finest available chronology;
- long continuous history;
- multiple symbols/instruments when available;
- both directions;
- high event density;
- equality/strict-boundary cases;
- lifecycle/StopAll continuation;
- Order/OrderAudit reconciliation;
- large-history performance.

When overlapping datasets exist, use the finest chronology and sufficient earlier history needed to reconstruct state.

Calculation scope may be wider than presentation scope.

---

# 48. Exact comparison method

For each baseline/refactored scenario, compare direct stable data structures and serialized artifacts.

The comparison tool must report the first difference with a precise path, such as:

```text
stage
collection index
object identity
field name
old value
new value
```

Prefer first-difference diagnostics over dumping enormous files.

For ordered collections, compare order directly.

For Decimal values, compare exact semantic/string form required by the production contract.

For JSON, compare the actual stable serialized output directly when byte/order stability is part of the contract.

Do not treat a summary/hash/count match as proof of full equality.

---

# 49. Determinism test

Run identical calculations repeatedly after refactoring.

PASS requires exact stable equality across repeated runs.

If repeated runs differ, investigate:

- unordered iteration;
- stale mutable global state;
- cache leakage;
- wall-clock values entering output;
- concurrency ordering;
- reused mutable objects;
- process/environment dependence.

Do not benchmark a nondeterministic implementation as release-ready.

---

# 50. Order and OrderAudit verification

Whenever changed code can influence Order, S, E, Lifecycle, StopAll, provenance, or OrderAudit, compare exact:

- physical Order identity;
- First/Break identity and chronology;
- confirmation;
- source;
- level/stop;
- stop event/time;
- parent;
- cause;
- provenance;
- deduplication;
- accepted/live/carried state;
- ownership;
- stable audit ordering;
- serialized OrderAudit output.

Do not replace the authoritative OrderAudit ledger with a cache or side index.

`order_audit_engine.py` must be explicitly included in refactor, dependency, benchmark, and regression review whenever Order state can be affected.

---

# 51. Algorithm Reference handling

The refactor specification must not duplicate detailed mutable trading rules that already live in Current Source/References.

Therefore:

- read Current Bullish and Bearish References completely before editing;
- preserve all active algorithm semantics during pure refactor;
- do not convert historical examples into production branches;
- do not copy old timestamp-specific examples into this refactor specification;
- if a Reference embeds Source, synchronize embedded implementation according to the project documentation workflow after approved Source changes;
- implementation-only refactor must not invent a new trading rule in Reference prose;
- Source/Reference mismatches discovered during refactor must be reported separately.

This separation keeps the refactor specification stable while trading rules evolve.

---

# 52. Diff hygiene

Before completion inspect the complete diff, not only the intended hunks.

Reject unintended:

- unrelated formatting churn;
- mass renames unrelated to the bottleneck;
- changed imports with no reason;
- accidental schema/public-output changes;
- one-direction-only edits;
- debug code;
- disabled validations;
- dead code;
- stale comments;
- float introduction;
- fixture-specific conditions;
- broad architecture changes hidden inside performance work.

Only intentional, explainable changes may remain.

---

# 53. Rollback safety

A substantial refactor must remain reversible until fully verified.

Before broad structural edits:

- preserve the unmodified baseline Source state using the project’s normal repository workflow;
- keep changes reviewable;
- avoid mixing unrelated fixes/refactors;
- make it possible to revert a failed optimization without reconstructing old logic manually.

If one optimization fails zero-difference verification, revert or isolate that optimization rather than weakening the acceptance criteria.

---

# 54. No “performance by deletion” of evidence

Never improve speed/memory by deleting intermediate or historical state that downstream calculations may need.

Internal state may be invisible publicly and still be algorithmically required.

Presentation filtering must not destroy calculation evidence.

A data structure may be released only when its lifetime is proven complete and no later stage, reconciliation, audit, visibility, or serialization step can reference it.

---

# 55. No optimization by changed semantics

The following are rejected unless separately approved as behavioral changes:

- approximated numeric calculations;
- coarse chronology replacing fine RAW;
- altered tie-breaking;
- different source-event selection;
- relaxed strict comparisons;
- early pruning that removes downstream-required state;
- altered order of reconciliation;
- skipping “rare” branches;
- reusing stale cached state;
- replacing authoritative objects with lossy summaries;
- changing output ordering;
- changing defaults;
- changing error fallback behavior to avoid work.

Fast wrong output is a failure.

---

# 56. Testing and benchmark code must not contaminate production ownership

Benchmark/profiling/regression helpers should live in the existing testing/tooling locations defined by the project, not inside trading-stage business logic.

Do not add production branches such as:

```text
if benchmark_mode:
    use_different_algorithm()
```

Instrumentation may measure production code but must not change the production algorithm.

---

# 57. Resource reporting

The final report must describe performance and resource effects with direct measured values.

Report, for each meaningful benchmark scenario:

```text
Baseline wall time
Refactored wall time
Absolute time saved
Relative improvement
Baseline peak RSS
Refactored peak RSS
Memory delta
Relevant stage timings
Number of measured runs
Representative/median result
Stable-output comparison result
```

Do not report only the best run.

Do not hide regressions in a faster total if a stage became pathologically worse.

---

# 58. Verification statuses

Use only:

```text
PASS
FAIL
NOT RUN
INCOMPLETE
NOT APPLICABLE
```

Definitions:

- `PASS`: completed and assertions/comparisons succeeded.
- `FAIL`: completed and required behavior/equality was violated.
- `NOT RUN`: not executed.
- `INCOMPLETE`: started but no valid complete result was produced.
- `NOT APPLICABLE`: demonstrably irrelevant to the current change.

Compilation alone is not regression PASS.

A timeout/partial run is not PASS.

A final output that “looks right” is not PASS.

---

# 59. Zero-difference release gate

Do not declare the refactor verified unless all mandatory applicable checks have completed successfully.

At minimum, release-ready pure refactor requires:

```text
Project/Source inspection                 PASS
Current Source/Reference understanding    PASS
Ownership/dependency review               PASS
Baseline capture                          PASS
Compile/import/runtime integrity          PASS
Targeted exact comparison                 PASS
Upstream exact comparison                 PASS
Downstream exact comparison               PASS
Order/OrderAudit integrity if applicable  PASS
Serialization/public output               PASS
Determinism                               PASS
Bullish runtime verification              PASS
Bearish runtime verification              PASS
Mirror verification where applicable      PASS
Historical regressions                    PASS
Full/representative RAW regressions        PASS
Performance benchmark                     PASS
Peak-memory comparison                    PASS
Maintainability review                    PASS
Final diff review                         PASS
```

If a mandatory item is `FAIL`, `NOT RUN`, or `INCOMPLETE`, final status must be:

```text
ZERO-DIFFERENCE REFACTOR NOT VERIFIED
```

Only when every mandatory applicable item passes may final status be:

```text
ZERO-DIFFERENCE REFACTOR VERIFIED
```

---

# 60. Final report format

The final user-facing report must include:

## Scope inspected

- project instructions read;
- complete engine tree inspected;
- Current References inspected;
- production Source inspected;
- tests/RAW/config used.

## Bottlenecks found

For each bottleneck:

```text
Owning file/component
Hot path
Current complexity/data-access pattern
Evidence from profiling/inspection
Selected optimization
Why semantics are preserved
```

## Changed files

For each changed file:

```text
Path
Reason
Structural/performance change
Behavioral change: NONE for pure refactor
```

Do not identify files by hashes or pinned numeric versions in this specification/reporting workflow.

## Code-quality result

Report:

- ownership quality;
- naming/readability improvements;
- duplication removed;
- dead code removed;
- dependency/coupling changes;
- complexity changes;
- cache/index safety;
- remaining technical debt.

## Performance result

Report baseline/refactored runtime and stage timing using comparable runs.

## Memory result

Report baseline/refactored peak memory and the reason for meaningful changes.

## Regression result

Report every applicable verification category and status.

## Final status

Use only evidence-supported status:

```text
ZERO-DIFFERENCE REFACTOR VERIFIED
```

or

```text
ZERO-DIFFERENCE REFACTOR NOT VERIFIED
```

---

# 61. Definition of Done

The task is complete only when all applicable statements are true:

- the complete current project scope was inspected;
- no file was excluded because an older specification omitted it;
- Current Source was read directly;
- Current Bullish/Bearish References were read directly;
- no hash or pinned file-version assumption was used as authority;
- a baseline existed before production changes;
- bottlenecks were identified by evidence or clear complexity analysis;
- each change remained in the correct owner;
- `order_audit_engine.py` was included whenever OrderAudit/Order state was relevant;
- no business rule was duplicated;
- no new production module was introduced without explicit authorization;
- clean naming/function/interface standards were met;
- dead/debug/temporary code was removed;
- Decimal semantics were preserved;
- strict/equality semantics were preserved;
- Doji semantics were preserved;
- finest available chronology was preserved;
- full required history was preserved;
- deterministic ordering/tie-breaking was preserved;
- caches/indexes were proven safe;
- CPU hot paths were reviewed;
- memory lifetime/peak usage was reviewed;
- serialization remained a projection;
- public output remained exact;
- both directions were verified where applicable;
- repeated determinism passed;
- representative/full RAW regression passed as required;
- performance was measured with comparable methodology;
- peak memory was measured when relevant;
- final diff contained only intentional changes;
- every unperformed/failed test was reported honestly;
- no performance claim exceeded the evidence.

---

# 62. Final engineering principles

```text
Correctness before speed.
Evidence before assumptions.
Current Source before stale documentation.
Full RAW chronology before coarse inference.
Decimal before float.
Exact source identity before approximate extrema.
Ownership before convenience.
Single source of truth before duplication.
Readable code before clever code.
Algorithmic complexity before micro-optimization.
Eliminate work before adding concurrency.
Run-scoped safe acceleration before persistent mutable cache.
Direct stable comparison before summary/hash shortcuts.
Small verified refactor steps before broad rewrites.
Measured performance before performance claims.
Zero difference before release.
```

The target state is:

```text
SAME TRADING BEHAVIOR
SAME CALCULATION SEMANTICS
SAME CHRONOLOGY
SAME IDENTITY / PROVENANCE
SAME PUBLIC OUTPUT
SAME SERIALIZATION
SAME DETERMINISM
CLEANER OWNERSHIP
CLEANER CODE
BETTER READABILITY
LESS DUPLICATION
LOWER UNNECESSARY CPU WORK
LOWER UNNECESSARY MEMORY WORK
MEASURABLY BETTER PERFORMANCE
NO REGRESSION
```

Above all:

```text
CURRENT STABLE BEHAVIOR == REFACTORED STABLE BEHAVIOR
```
