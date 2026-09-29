# TradingBot — High-Performance Zero-Difference Refactor Specification

## HPZR2 — Production Refactor / Exact Behavioral Preservation

---

# 1. OBJECTIVE

The objective of this project is to perform a production-grade Refactor and Optimization of the TradingBot while preserving **100% of the existing behavior, calculations, and outputs**.

The fundamental rule is:

> **Old Output == New Output**

Not approximately equal.
Not equal within tolerance.
**Exactly equal.**

Optimization is permitted only when the final output and all required observable/intermediate behavior remain exactly identical.

Priority order:

1. **ZERO DIFFERENCE**
2. **PERFORMANCE**
3. **MEMORY**
4. **CODE STRUCTURE**
5. **COSMETIC**

If an optimization introduces even one valid behavioral difference, that optimization is rejected.

---

# 2. SOURCE AUTHORITY

The only authoritative implementation source is:

> **Current Production Source**

Exactly these 9 production modules are allowed:

```text
reaction_engine.py
blue_line_detector.py
a_zone_detector.py
s_zone_detector.py
e_zone_detector.py
lifecycle_engine.py
trading_pipeline.py
direction_policy.py
core_utils.py
```

Rules:

* Do not reintroduce old or archived Source code.
* Historical Source may only be used for comparison or regression analysis.
* Do not create new Production files.
* Do not create new helper/model/order_engine/performance_utils/cache/common/constants/lifecycle_utils modules.
* Logic must remain inside its correct owner module.
* Do not independently reimplement the same behavior in multiple modules.

---

# 3. HPZR2 DOCUMENTATION STATUS

Version:

```text
5.4.5-HPZR2
```

HPZR2 is:

```text
Documentation / Reconstruction Synchronization
```

Therefore:

```text
Production Source Changes: NONE
Algorithm Changes: NONE
Calculation Changes: NONE
Behavioral Changes: NONE
Serialization Changes: NONE
```

HPZR2 must document and reconstruct the state of the existing Production Source.

It must not introduce new behavioral rules.

---

# 4. ZERO-DIFFERENCE CONTRACT

The Refactor must preserve all of the following exactly.

## Reaction

* Count
* Ordering
* FirstIndex
* BreakIndex
* FirstTime
* BreakTime
* Prices
* Levels
* Box geometry
* Direction
* Mode
* Breakout
* Source
* Serialization

## Reset

All fields, ordering, and identity.

## Blue

All fields, chronology, source, stop, type, kind, price, and serialization.

## A

All A Zones, source, stop, price, Blue references, ownership, and serialization.

## S

All S Zones, color, formation type, A linkage, Order linkage, decision, source, stop, and serialization.

## E

All E objects, family, number, parent, source, color, continuation, StopAll interactions, and serialization.

## StopAll

All StopAll objects, source, gate, lineage, cycle boundary, and serialization.

## Order / OrderAudit

* Physical identity
* FirstIndex
* BreakIndex
* Mode
* Source
* Confirmation
* Stop
* Box
* Reaction
* Provenance
* Audit ordering
* Ownership

---

# 5. EXACT SERIALIZATION

The new output must also be exactly equal at the JSON serialization level.

Comparison must include:

* Key ordering
* List ordering
* Object ordering
* Decimal representation
* Timestamps
* Indexes
* Null values
* Nested objects
* Direction payloads

The only values that may be excluded from exact equality are explicitly designated:

```text
runtime timing telemetry
```

because execution timing is inherently nondeterministic.

Production output itself must remain unchanged.

---

# 6. FULL RAW AUTHORITY

The complete physical RAW dataset is the authoritative calculation source.

Do not optimize by:

* Truncating RAW.
* Selecting only apparently relevant candles before calculation.
* Removing historical data prematurely.
* Changing chronology.
* Removing lower-timeframe data.

All calculations must operate from:

> **Full Physical RAW**

Final filtering must happen at the end, not by prematurely removing data that may affect downstream calculations.

---

# 7. LOWER-TF CHRONOLOGY

When calculating a higher timeframe such as 30s, the original lower-timeframe chronology must be preserved exactly.

For example, when:

```text
Main timeframe = 30s
RAW timeframe  = 5s
```

the physical 5s candle order is authoritative for intra-candle calculations.

Do not reconstruct lower-TF chronology merely from aggregated OHLC.

---

# 8. DECIMAL CONTRACT

All price-sensitive calculations must preserve exact Decimal semantics.

Conversions such as:

```python
float(...)
```

that can change numerical semantics are prohibited.

Normalization must be lossless.

Required invariant:

```text
Decimal state before == Decimal state after
```

Even when the displayed numeric value is identical, observable representation must not change unnecessarily, especially in serialization.

---

# 9. CANDLE COLOR

Canonical candle-color rule:

```text
GREEN = close >= open
RED   = close < open
```

Therefore:

```text
Doji = GREEN
```

This rule is direction-invariant and must not be mirrored or inverted.

---

# 10. DIRECTION MIRROR

Bullish and Bearish behavior must be exact directional mirrors where the rule is directional.

## Bullish

```text
Directional Extreme = Low
Extreme Selection   = Minimum
Strict Crossing     = Low < Level
First Opposite Tag  = FirstRed
```

## Bearish

```text
Directional Extreme = High
Extreme Selection   = Maximum
Strict Crossing     = High > Level
First Opposite Tag  = FirstGreen
```

Mirror mapping:

```text
Bullish ↔ Bearish
Low ↔ High
Minimum ↔ Maximum
< ↔ >
FirstRed ↔ FirstGreen
```

However, the following must **NOT** be mirrored:

```text
Lifecycle Priority
StopAll Priority
Serialization Rules
Physical Identity
Tie-Breaking Rules
Ordering Rules
Cycle Reset Semantics
Ownership Semantics
```

These are direction-invariant rules.

---

# 11. STRICT CROSSING

Bullish:

```text
Low < Level
```

Bearish:

```text
High > Level
```

Equality is never considered a crossing.

Therefore:

```text
Low == Level  → NO CROSS
High == Level → NO CROSS
```

---

# 12. PHYSICAL ORDER IDENTITY

Physical Order identity is:

```text
(FirstIndex, BreakIndex)
```

This is the canonical physical identity.

Timestamp alone is not an identity.

All implementations must preserve this identity.

Secondary indexes may be used for acceleration, but they are never authoritative.

---

# 13. AUTHORITATIVE VS ACCELERATOR DATA

### Authoritative

Canonical chronological collections and authoritative lifecycle lists.

### Non-authoritative

```text
sets
dicts
indexes
caches
side indexes
lookup maps
```

These structures are acceleration mechanisms only.

They must never alter:

* Chronology
* Ownership
* Ordering
* Duplicate handling
* Authoritative winner selection

---

# 14. CACHE SCOPE

All caches must be:

```text
run-scoped
```

Prohibited:

```text
global mutable trading-state cache
cross-run behavioral cache
dataset-specific cache
timestamp-specific branch
symbol-specific optimization branch
```

Caches must not become persistent trading state after the calculation run.

---

# 15. REACTION OPTIMIZATION

Allowed optimization techniques include:

* Indexed lower-TF range queries
* First-event lookup
* Exact range min/max lookup
* Elimination of repeated history-prefix allocations
* Elimination of repeated containment scans

Only if:

```text
Result_before == Result_after
```

Reaction geometry, chronology, identity, and serialization must remain unchanged.

---

# 16. BLUE OPTIMIZATION

Blue calculation must retain exactly the existing Source semantics.

Allowed:

* Indexing
* Lookup acceleration
* Immutable chronology indexes
* Elimination of repeated scans

Prohibited:

* Changing Blue formation rules
* Changing stop rules
* Changing type
* Changing inheritance
* Changing visibility
* Changing chronology

---

# 17. A OPTIMIZATION

A detection must preserve existing Source semantics.

In particular:

* Blue pairing
* Source
* Stop
* Ownership
* Boundaries
* Lifecycle interaction

must remain unchanged.

A objects must not be prematurely removed merely because they appear unnecessary if downstream calculations still require them.

---

# 18. S OPTIMIZATION

S is one of the most sensitive calculation stages.

Allowed optimization techniques:

```text
Immutable Reaction/Reset/Blue indexes
Cached A-stop → eligible Order searches
Exact lower-TF crossing indexes
```

The following must remain exactly unchanged:

* Chronology
* Order selection
* Candidate selection
* Source selection
* A ownership
* StopAll interaction

---

# 19. S-AFTER-A RULE

S after A must be determined by the actual lifecycle state.

The implementation must NOT use an oversimplified rule such as:

```text
A stopped → next S = StopAll
```

After an A stops, the next S may be a normal S.

Canonical examples:

```text
A 2026-08-26 10:55:30
→ S Red 11:04:00
```

must be:

```text
S Red
```

not:

```text
StopAll1
```

Also:

```text
A 2026-08-26 22:41:30
→ S Red 23:00:00
```

and:

```text
A 2026-08-28 08:31:30
→ S Red 08:57:00
```

---

# 20. ORDER_B

Order_B is an independent formation cause.

This:

```text
Reaction.mode == B
```

must not by itself be interpreted as an Order_B.

Order_B starts from a Reset of the same trend direction.

Primary extreme:

```text
Breakout main candle
through
Reset main candle
inclusive
```

Then evaluate:

* Exact lower-TF strict break
* Raw opposite-direction Reaction geometry
* Mirrored other edge
* First canonical opposite Reaction after the gate

---

# 21. ORDER OWNERSHIP

If multiple Order candidates map to the same physical Order:

```text
Physical Identity = (FirstIndex, BreakIndex)
```

there is only one physical Order.

For Order_B:

> The latest valid reset-leg cause for the same physical Order is authoritative.

Duplicate Order_B origins must not create multiple physical Orders.

---

# 22. PARENT-STOP ORDER OWNERSHIP

If one parent-stop provenance can produce multiple Orders:

The earliest Order according to:

```text
(confirmationTime, FirstIndex, BreakIndex)
```

owns the parent-stop provenance.

Later physical Orders are removed unless they are independently valid through another cause, such as a reset-leg cause.

---

# 23. ORDER AUDIT

OrderAudit is authoritative.

It must not be replaced by cache/index structures.

Indexes are lookup accelerators only.

OrderAudit must preserve the required:

* Candidates
* Physical identity
* Cause
* Provenance
* Confirmation
* Ownership
* Final authoritative cause

---

# 24. LIFECYCLE PRIORITY

Lifecycle priority is invariant:

```text
StopAll
>
E Red
>
S Red
>
E Blue
>
S Blue
>
A
```

This priority is identical for Bullish and Bearish.

---

# 25. E FAMILY / NUMBER

E family follows the accepted stopped parent.

Rules:

* If the stopped parent remains active, the child remains in the same family.
* An unbroken Red S can supersede a Blue E.
* S cannot supersede an active Red E.
* Red priority is higher than Blue.
* New same-family number:

```text
max(stopped same-family number) + 1
```

* If no family exists:

```text
new family/root = 1
```

* StopAll clears active E continuation.
* StopAll may retype the child parent as StopAll for lineage semantics.

---

# 26. SAME-SOURCE E COLLISION

If multiple E candidates have the same:

```text
(sourceIndex, sourceTime)
```

only one E may be accepted.

Priority:

```text
Red > Blue
```

Within the same family:

```text
Higher number > Lower number
```

For an exact tie:

```text
First accepted provenance
```

is preserved.

---

# 27. INVALID A / INVALID S

If an S was formed but its parent A later becomes calculation-invalid:

The S must not be globally deleted before E processing.

It must remain available as:

```text
Geometry Evidence
OrderAudit Evidence
Continuation Evidence
```

unless an explicit rule suppresses it.

If an invalid S would create a competing cross-family E1 root:

the cross-family root is suppressed.

However, same-family continuation/evidence must remain available.

---

# 28. BLUE STOPALL GATE

Blue repeat counting must be based on:

> **Exact accepted Blue behavior key**

It must not merely count changes in the lifecycle dominant key.

Examples that may arm the gate:

```text
S Blue × 2
E1 Blue × 2
E5 Blue × 2
```

Repeated:

```text
E1 Blue
E1 Blue
```

must increment the count even while E1 Blue remains dominant.

However:

```text
E1 Blue
E2 Blue
E3 Blue
```

are different exact Blue behavior keys.

They must not be counted as three occurrences of one key.

Therefore:

```text
E3 Blue
```

alone is not sufficient.

---

# 29. STOPALL CREATION

When an accepted S Red is encountered:

First evaluate the Blue-repeat gate.

If an exact Blue behavior key has:

```text
count >= 2
```

that S Red becomes:

```text
StopAll
```

If multiple Blue groups qualify, metadata selection must remain deterministic.

---

# 30. STOPALL HARD RESET

Every StopAll creates a hard cycle boundary.

After StopAll:

```text
Active S state       = reset
Active E exact-key state = reset
Blue repeat counters = 0
Cycle measurement    = restart
```

A new lifecycle cycle starts after the StopAll.

---

# 31. E STOP / RECURSION

Before every E decision:

1. Previous S events must be ingested.
2. StopAll objects must be evaluated.
3. If StopAll is stopped:

   * the next StopAll may be generated from the current E.
4. If StopAll is not generated:

   * same-key E/S sequence-group stop must be preserved.
5. Active E key/count must be updated.

Accepted StopAll resets the active cycle state.

E can be recursive:

```text
S → E1
E1 → E2
E2 → E3
...
```

subject to family, number, and ownership rules.

---

# 32. STOPALL / E3 SPECIAL CASE

A single:

```text
E3 Blue
```

is simply one E3 Blue occurrence.

The existence of:

```text
E1 Blue
E2 Blue
```

before it does not turn them into three occurrences of the same exact key.

For an E3-based StopAll, E3 Blue must form again according to the applicable rule and then stop.

---

# 33. BEARISH SPECIAL RULES

Bearish:

```text
Directional Extreme = High
Extreme = Maximum
Strict Stop/Break = High > Level
```

Bullish:

```text
Directional Extreme = Low
Extreme = Minimum
Strict Stop/Break = Low < Level
```

Lifecycle semantics remain shared.

---

# 34. BEARISH TYPE-4 S BLUE

Bearish Type-4 S Blue is active only when:

```text
A stopped
AND
Order does not yet exist
```

If an Order forms, the S leaves Type-4 status.

Candidate S:

```text
Highest High
```

from:

```text
Stop-A candle
through
the breakout candle of the latest bearish Reaction
```

Canonical corrected bearish Reaction:

```text
2026-08-28 06:31:30
```

not:

```text
06:25:00
```

---

# 35. FINAL VISIBILITY

After lifecycle reconciliation:

1. Initial A must not expose source indexes occupied by final S.
2. StopAll is determined from lifecycle-visible S/E.
3. Independent accepted S E1 roots must be restored without rewriting the dominant StopAll sequence.
4. StopAll at the same source suppresses E.
5. Final E/StopAll at the same source suppresses A/S labels.
6. Lineage must remain intact.
7. Historical E rescue is presentation-only.
8. Rescue must not feed back into lifecycle or StopAll.
9. Calculation-invalid S must be removed from final S output.
10. Stage-invalid S descendants of A must be removed.
11. Public Blue output must include only:

```text
calculation_valid == true
AND
behavior_internal == false
```

---

# 36. INTERNAL REACTION

Internal-Reaction filtering must only hide:

```text
forbidden internal native-Mode-B E/StopAll Orders
```

whose surviving cause is solely Reset-leg.

It must not remove:

```text
A
S
other E
StopAll
```

merely because their source point lies inside a healthy Reaction.

---

# 37. PERFORMANCE OPTIMIZATION STRATEGY

HPZR2 optimization should focus on:

## Reaction

* Indexed range lookup
* First-event lookup
* Avoid repeated containment scans
* Avoid repeated history-prefix allocations

## S

* Immutable Reaction/Reset/Blue chronology indexes
* Cached A-stop → eligible Order searches
* Exact lower-TF range indexes

## E

* Per-run canonical Order-stop cache
* Immutable initial-Order indexes
* Physical identity indexes
* Confirmation-time side index
* Avoid repeated OrderAudit/history scans
* Materialize duplicate Order_B causes only once

---

# 38. MEMORY RULE

Memory optimization must never change behavior.

Allowed:

* Temporary indexes
* Run-scoped caches
* Immutable lookup structures

However:

```text
Authoritative chronological data
```

must not be removed if downstream calculations depend on it.

---

# 39. NO DATASET-SPECIFIC OPTIMIZATION

The following are prohibited:

```python
if symbol == "...":
```

or:

```python
if timestamp == "...":
```

or:

```python
if dataset == "...":
```

or any other branch added solely to make one specific RAW dataset pass.

Optimizations must be general and reusable.

---

# 40. NO FALSE PASS

If the baseline does not complete on a full RAW dataset:

do not fabricate or infer a baseline result.

Report explicitly:

```text
Baseline incomplete
```

and do not claim full Zero-Difference validation for that dataset.

HPZR1 precedent:

For the largest RAW dataset containing 309,906 rows, the optimized implementation completed, while the baseline exceeded the 240-second limit before completing E. Therefore a complete baseline Zero-Difference claim was not made for that dataset.

---

# 41. BENCHMARK PROTOCOL

Before and after the Refactor, execute the exact same:

* RAW dataset
* Direction
* Timeframe
* Environment
* Command
* Output schema

Measure:

```text
Wall time
Peak RSS
Stage timing
Output count
Output hash
Final serialized payload
```

---

# 42. EXACT REGRESSION COMPARISON

Every stage must be compared:

```text
Reaction
Reset
Blue
A
S
E
StopAll
OrderAudit
Final Serialized Direction Payload
```

Comparison must include:

```text
Count
Exact object equality
Exact list equality
Exact JSON equality
Hash equality
```

No tolerance is allowed.

---

# 43. REQUIRED MIRROR TEST

Bullish and Bearish must be tested against synthetic reflected markets.

Mapping:

```text
Bullish(original)
↔
Bearish(reflected)
```

and:

```text
Bearish(original)
↔
Bullish(reflected)
```

Field-by-field comparison is required.

For mathematical reflection tests, datasets without Doji may be used because:

```text
Doji = GREEN
```

is an actual production invariant and must not be modified merely to obtain mathematical symmetry.

---

# 44. DEPENDENCY CHAIN RULE

If one candle's behavior changes:

all later behaviors that depend on that candle may also legitimately change.

Do not artificially force downstream behavior to remain unchanged merely to make a regression look cleaner.

Only behavior before the first edited point in a protected range must remain unchanged, unless explicitly specified otherwise.

---

# 45. VERSIONING REQUIREMENT

Every modified Source file must contain:

* New version number
* Modification date
* Modification time
* Change note

Example:

```text
Version: 9.x.x
Last Modified: YYYY-MM-DD HH:MM:SS +03:30
Change: HPZR2 ...
```

Versioning must never be omitted.

---

# 46. SOURCE STRUCTURE

Refactoring must remain inside the existing 9 Production modules.

No new Production module may be created.

Owner boundaries:

```text
reaction_engine.py
    Reaction / Reset

blue_line_detector.py
    Blue

a_zone_detector.py
    A

s_zone_detector.py
    S / Order-related S calculation

e_zone_detector.py
    E / StopAll / OrderAudit lifecycle integration

lifecycle_engine.py
    Lifecycle ownership / priority

trading_pipeline.py
    Pipeline orchestration

direction_policy.py
    Directional mirror policy

core_utils.py
    Behavior-neutral primitives
```

---

# 47. DIRECT SOURCE SYNCHRONIZATION

If the Reference contains embedded Source:

1. Locate:

```text
SOURCE_FILE_BEGIN:<name>
```

2. Extract the complete Python code fence.
3. Save it unchanged as UTF-8.
4. Recover all 9 modules.
5. Compile them.
6. Provide required runtime dependencies such as `orjson`.

Embedded Source must never contain:

```text
... code omitted
unchanged from previous version
external source pointer
```

or equivalent placeholders.

---

# 48. REQUIRED VERIFICATION

After Refactor:

```text
All production files read completely: PASS

Bullish semantic audit: PASS
Bearish semantic audit: PASS
Mirror audit: PASS

Doji invariant: PASS
Strict crossing: PASS
Decimal contract: PASS
Lower-TF chronology: PASS
Full RAW authority: PASS

Reaction: PASS
Reset: PASS
Blue: PASS
A: PASS
S: PASS
E: PASS
StopAll: PASS
Order: PASS
OrderAudit: PASS

Dataclass schemas: PASS
Serialization: PASS
Symbol indexes: PASS

No omitted production code: PASS
No external production dependency: PASS

Standalone reconstruction: PASS
```

These PASS statuses must be based on actual tests, not inspection alone.

---

# 49. REQUIRED FINAL REPORT

The final report must include:

## Changed Files

```text
File
Old Version
New Version
Change
```

## New Production Files

Expected:

```text
0
```

unless the user explicitly authorizes new files.

## Behavioral Changes

For a pure refactor:

```text
NONE
```

## Algorithm Changes

For a pure refactor:

```text
NONE
```

## Calculation Changes

```text
NONE
```

## Serialization Changes

```text
NONE
```

## Performance

Report:

```text
Baseline
Optimized
Speedup
Percentage Reduction
```

## Memory

Report:

```text
Baseline RSS
Optimized RSS
Difference
```

## Regression

For every RAW dataset:

```text
Bullish
Bearish
Reaction
Reset
Blue
A
S
E
StopAll
OrderAudit
Final JSON
```

---

# 50. ACCEPTANCE CRITERIA

The Refactor is accepted only when:

```text
Old Output == New Output
```

for every regression dataset for which a complete baseline execution exists.

Additionally:

```text
No behavioral change
No algorithm change
No calculation change
No serialization change
```

must be demonstrated.

Performance improvement must be measurable.

Memory must not increase unnecessarily.

No dataset-specific hacks may exist.

---

# 51. ABSOLUTE RULE

At every stage:

> **ZERO DIFFERENCE ALWAYS WINS.**

If there is a conflict between:

```text
Performance
```

and:

```text
Behavioral Equivalence
```

then:

```text
Behavioral Equivalence wins.
```

If an optimization causes even one difference in:

```text
Reaction
Reset
Blue
A
S
E
StopAll
Order
OrderAudit
Lifecycle
Serialization
```

that optimization must be rejected or rolled back.

---

# 52. FINAL PRINCIPLE

HPZR2 must not change the TradingBot's trading logic.

HPZR2 must preserve:

```text
Same Behavior
+
Same Calculation
+
Same Output
+
Same Serialization
+
Same Lifecycle
+
Same Bullish/Bearish Mirror
```

while improving implementation efficiency where safely possible.

The final target is:

```text
SAME BEHAVIOR
SAME CALCULATION
SAME OUTPUT
SAME SERIALIZATION
LESS TIME
LESS UNNECESSARY WORK
NO REGRESSION
```

And above all:

```text
OLD OUTPUT == NEW OUTPUT
```
