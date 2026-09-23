# TradingBot — Master Prompt for Complete Standalone Bullish & Bearish Algorithm References

## PRIMARY MISSION

Create and maintain two complete, production-grade, standalone algorithm specification files for TradingBot:

```text
TradingBot_Bullish_Algorithm_Reference_<VERSION>_Comprehensive_Standalone.md
TradingBot_Bearish_Algorithm_Reference_<VERSION>_Comprehensive_Standalone.md
```

These documents must be sufficient to completely reconstruct the current production TradingBot implementation even if all original `.py` source files are permanently unavailable.

The final Algorithm Reference files must be written entirely in **English**.

The references must not depend on external production source files for implementation, interpretation, reconstruction, debugging, or verification.

The final principle is:

```text
THE ALGORITHM REFERENCE ITSELF MUST CONTAIN
EVERYTHING REQUIRED TO REBUILD THE ENGINE.
```

---

# 1. Core Requirement

Each Algorithm Reference must simultaneously satisfy two requirements:

## Requirement A — Exact Synchronization With Current Production Source

The Reference must describe the behavior of the latest authoritative production source exactly.

No legacy behavior, archived implementation, historical assumption, or superseded rule may silently become authoritative again.

## Requirement B — Full Standalone Reconstructability

The Reference must be independently sufficient.

If the production source directory is completely deleted, an experienced engineer must be able to reconstruct the engine from the Reference alone.

The rebuilt implementation must preserve:

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
Visibility
Chronology
Ownership
Provenance
Serialization
```

and all associated fields and ordering semantics.

---

# 2. The Algorithm Reference Must Contain Actual Required Source Code

This requirement is mandatory.

The Reference must not merely explain what the source code does.

It must also contain the complete code required to reconstruct the production implementation.

For every production component required by the algorithm, the Reference must contain the exact relevant implementation code.

The Reference must therefore include the complete production implementation snapshot for the current algorithm version.

The current production architecture consists of these nine source modules:

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

The complete required implementation of these modules must be embedded directly inside each standalone Algorithm Reference.

The user must not need access to the original files.

Forbidden documentation pattern:

```text
See reaction_engine.py for implementation.
```

Required pattern:

```text
The complete implementation is explained here
AND
the exact required implementation code is embedded here.
```

---

# 3. No External Source Dependency

The Reference must never require the reader to access:

```text
the original Source directory
Git history
another Algorithm Reference
archived source
external helper files
conversation history
developer memory
```

Everything required for reconstruction must exist inside the Reference itself.

The Bullish Reference must be independently usable.

The Bearish Reference must be independently usable.

Neither file may depend on the other.

---

# 4. Output Language

The complete final contents of both Algorithm Reference files must be written in English.

This includes:

```text
Titles
Explanations
Algorithm rules
Comments
Tables
Examples
Pseudocode
Change history
Architecture notes
Validation notes
Reconstruction instructions
Source manifests
Performance notes
```

Embedded production Python code may naturally use the identifiers and comments used by the production implementation, but all newly written explanatory text must be English.

Do not produce Persian prose inside the Algorithm Reference.

---

# 5. Current Production Source Is Authoritative

Always begin from the latest production source currently present in the project.

The current source must be fully read and understood.

Do not determine synchronization only from:

```text
hashes
version numbers
filenames
timestamps
previous Reference documents
```

Hashes may be included as metadata, but they are never a substitute for semantic inspection.

Required process:

```text
Read Source
→ Understand Source
→ Trace execution
→ Extract algorithm
→ Compare Reference
→ Update Reference
```

---

# 6. Every Production File Must Be Read Completely

Do not inspect only the recently modified functions.

Read all nine production modules completely.

No function, class, helper, constant, dataclass, branch, exception path, serialization function, or ownership helper may be skipped.

This includes implementation-only helpers because they may affect:

```text
ordering
boundaries
tie-breaking
identity
state
caching scope
serialization
```

---

# 7. Reference Must Be More Than a Source Dump

Embedding source code alone is not sufficient.

The Reference must contain both:

```text
Complete semantic explanation
+
Complete implementation snapshot
```

A reader must be able to understand the algorithm without reverse-engineering Python code.

The embedded code exists as the final implementation contract and disambiguation mechanism.

---

# 8. Mandatory Three-Layer Structure

Each Reference must contain three layers.

## Layer 1 — Semantic Algorithm Specification

Describe the trading algorithm independently of Python implementation.

Explain exactly:

```text
what forms
when it forms
why it forms
what invalidates it
what confirms it
what stops it
what owns it
what replaces it
what becomes visible
```

## Layer 2 — Reconstruction / Function-Level Specification

Describe the exact implementation contract.

Include:

```text
function responsibilities
inputs
outputs
state transitions
search ranges
boundaries
tie rules
sorting
identity
ownership
error conditions
serialization mapping
```

## Layer 3 — Embedded Production Implementation

Include the complete implementation code needed to rebuild the production engine.

---

# 9. Reconstruction Guarantee

The document must explicitly state:

> This document is sufficient to reconstruct the production TradingBot engine without access to the original source repository.

A valid reconstruction must reproduce exactly:

```text
sourceIndex
sourceTime
decisionIndex
decisionTime
decisionEventTime
stopIndex
stopTime
stopEventTime
price
stopLevel
BoxTop
BoxBottom
Breakout
Reaction Number
E Number
Red/Blue family
FormationType
Order mode
Order cause
Order parent
owner
parent
provenance
lifecycle ownership
event ordering
output ordering
serialization ordering
JSON keys
null/non-null values
Decimal representation
```

---

# 10. Bullish and Bearish Must Both Be Fully Standalone

Do not make Bearish simply say:

```text
Apply the Bullish rules in reverse.
```

That is insufficient.

The Bearish Reference must explicitly describe the complete Bearish algorithm.

The Bullish Reference must explicitly describe the complete Bullish algorithm.

The mirror contract may be explained, but each direction must be independently reconstructable.

---

# 11. Canonical Directional Mirror

Directional geometry must satisfy the exact mirror contract.

```text
Bullish          Bearish
--------------------------------
Low              High
High             Low
Minimum          Maximum
Maximum          Minimum
<                >
>                <
First Red        First Green
BoxBottom        BoxTop
BoxTop           BoxBottom
Bullish          Bearish
Bearish Order    Bullish Order
```

Do not mechanically mirror concepts that are direction-invariant.

---

# 12. Mandatory Direction-Invariant Section

Each Reference must contain an explicit section titled:

```text
Direction-Invariant Rules
```

It must explain all rules that are identical in Bullish and Bearish.

The most important invariant is candle color:

```text
GREEN if close >= open
RED if close < open
```

Therefore:

```text
Doji:
close == open
→ GREEN
```

**A Doji is always GREEN.**

This rule must never be directionally mirrored.

---

# 13. Other Mandatory Direction-Invariant Rules

The following concepts must remain unchanged between Bullish and Bearish unless the current production source explicitly changes them:

```text
Doji = GREEN
Red / Blue family names
E numbering
Behavior taxonomy
Lifecycle priority
StopAll semantics
Stage order
Physical Order identity
Order provenance model
Internal/Public distinction
Serialization schema
Serialization ordering
null/non-null semantics
Decimal exactness
Full RAW authority
Lower-timeframe chronology authority
Stable chronology
StopAll hard boundary
Blue repeat grouping
```

---

# 14. Strict Crossing

Directional strict crossing must be explicitly documented.

Bullish:

```text
Low < Level
```

Bearish:

```text
High > Level
```

Equality is never a crossing:

```text
Low == Level
→ no crossing

High == Level
→ no crossing
```

Strictness itself is direction-invariant.

---

# 15. Exact Decimal Contract

All algorithmic price decisions must preserve exact Decimal semantics.

Never redesign the algorithm using binary float comparison.

Forbidden for algorithmic decisions:

```python
float(price)
round(price)
Decimal(float_value)
```

Authoritative normalization should follow the production behavior, typically:

```python
Decimal(str(value))
```

or the exact authoritative production helper.

---

# 16. Candle Color Contract

The exact rule must appear prominently in both Reference files:

```python
GREEN if close >= open else RED
```

Do not use:

```text
Bullish candle vs Bearish candle
```

as a substitute for the actual color rule.

Doji must remain GREEN under all market directions.

---

# 17. Full Physical RAW Authority

The Reference must explain that algorithmic calculation operates on Full Physical RAW.

Presentation range and calculation range are different concepts.

Correct model:

```text
Full RAW
→ Normalize
→ Full Calculation
→ Full Lifecycle
→ Final Output Filtering
```

Do not silently truncate historical state because a request starts later.

---

# 18. Lower-Timeframe Authority

Exact event chronology must use the original lower-timeframe data when required.

This includes:

```text
Reaction confirmation
Breakout
Reset
Blue stop
A trigger
A stop
Order confirmation
Order stop
S decision
E decision
StopAll
```

Main timeframe OHLC may not replace lower-TF chronology where production currently depends on exact event ordering.

---

# 19. Main Candle and Lower-TF Relationship

Document exactly how a lower-TF event maps to:

```text
physical main index
main candle timestamp
event timestamp
```

These are not interchangeable.

Distinguish fields such as:

```text
sourceTime
decisionTime
decisionEventTime
stopTime
stopEventTime
```

---

# 20. Range Boundaries

Every range scan must define whether its boundaries are:

```text
inclusive
exclusive
```

Document equivalent behavior for operations implemented with:

```python
bisect_left
bisect_right
```

Do not use vague phrases such as:

```text
between A and B
```

when exact inclusion changes output.

---

# 21. Tie Semantics

Document all tie rules.

Examples include:

```text
first equal extreme wins
last equal extreme wins
same lower-TF timestamp precedence
stable sort precedence
first physical identity match
latest Reset-leg origin
```

Any tie capable of changing one field must be explicitly specified.

---

# 22. Behavior Definition

Only these objects are Behaviors:

```text
A
S
E
StopAll
```

The following are not Behaviors:

```text
Reaction
Reset
Blue
Order
OrderAudit
```

This terminology must remain consistent throughout the document.

---

# 23. Authoritative Pipeline Order

The full stage order must be documented exactly.

At minimum:

```text
RAW Normalization
→ Reaction / Reset
→ Internal Reaction Ownership
→ Blue
→ A
→ S
→ E
→ E Reconciliation
→ Lifecycle
→ StopAll
→ Visibility
→ OrderAudit
→ Serialization
```

If the production pipeline contains additional reconciliation passes, document them.

---

# 24. Reaction Specification

Reaction reconstruction must include:

```text
Mode A
Mode B
First reaction candle
FirstRed / FirstGreen
Anchor
Leg boundary
BoxTop
BoxBottom
Box ownership
Breakout
Exact lower-TF confirmation
Same-Break Reset
Post-breakout Reset
Candidate invalidation
Intrabar extreme
Cross-direction geometry
Internal Reaction classification
Public geometry
```

Do not omit exact event ordering.

---

# 25. Reset Specification

Document:

```text
Reset trigger
broken level
owner Reaction
main index
lower-TF reset timestamp
same-Break Reset
post-breakout Reset
state reset effects
new leg initialization
```

---

# 26. Blue Specification

Document all Blue variants and states:

```text
Scale Blue
Reset Blue
Fibonacci level
Scale strikes
Pending strike
Intrabar confirmation
Source candle
Source extreme
Line price
Calculation validity
Behavior internal state
Public visibility
Stop
Stop event
Stop level
Stop transfer
Inherited stop
```

---

# 27. A Specification

Document all A logic including:

```text
Blue pair
Blue ordinals
first stop
second stop
double-stop
inherited stop
continuation extreme
trigger
Reaction confirmation
A candidate
A accepted
A source
A price
A strict stop
A ownership window
```

---

# 28. S Specification

Every existing S formation route must be independently documented.

Examples include:

```text
S Red
S Blue Simple
S Blue Advanced
S Blue Type-3
S Blue Type-4
```

For every route specify:

```text
parent
candidate source
candidate level
entry condition
required evidence
Order relationship
Blue relationship
stop
decision
decision event
family
price
invalidation
lifecycle interaction
```

---

# 29. Order Specification

Document physical Order independently from the reason it exists.

Physical Order identity is:

```text
(FirstIndex, BreakIndex)
```

Do not use:

```text
parent
cause
stop
confirmation timestamp
```

as the physical identity.

---

# 30. Multiple Order Causes

One physical Order may have multiple causes.

Possible provenance must be documented independently from identity.

Examples:

```text
parent-stop
reset-leg
carried-live
accepted-live
stopped-A
```

Creation provenance and use provenance must not be conflated.

---

# 31. Order_A

Document exactly how Order_A geometry is discovered, validated, accepted, stopped, and attached to downstream behavior.

Include all authoritative box and stop fields.

---

# 32. Canonical Order_B

Order_B must be documented as an independent formation mechanism.

Do not equate Order_B with native Reaction Mode-B.

Document:

```text
same-direction Reset
Reset owner
primary trigger extreme
strict break
closed geometry evidence range
opposite extreme
canonical opposite Reaction
physical Order assignment
Reset-leg provenance
latest valid Reset-leg cause
```

---

# 33. Mode-B Stopped-A Refresh

Document exactly:

```text
initial provisional Order
native Mode-B chain
replacement deadline
decision event
termination by Mode-A
non-retroactive replacement
OrderAudit reassignment
```

---

# 34. Shared Accepted Order Stop

Document that an accepted physical Order may be used to decide another eligible open S/E candidate if its exact stop chronology satisfies the current production rule.

Creating parent and consuming candidate do not necessarily need to be identical.

---

# 35. E Specification Must Be Extremely Detailed

E must not be summarized.

Document all E paths:

```text
S parent
E parent
parent stop
parent-stop Order
Reset-leg Order
carried-live
accepted-live
accepted Order ledger
recursive E creation
E source
E candidate
E decision
E family
E number
E stop
E reconciliation
owner finality
historical rescue
suppressed intermediate E
sequence reset
cross-stage priority
```

---

# 36. E Numbering

Explain exactly:

```text
when E1 forms
when E2 forms
when the number increments
when family changes
when numbering resets
how StopAll affects E state
```

E numbering does not mirror between directions.

---

# 37. Lifecycle Priority

The authoritative priority must be documented exactly:

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

This priority is direction-invariant.

---

# 38. StopAll

Document StopAll as a hard lifecycle boundary.

After StopAll:

```text
previous ownership expires
previous descendants cannot leak
cycle state restarts
Blue repeat counters reset
previous lifecycle state cannot own new behaviors
```

---

# 39. Blue-Repeat StopAll

Document exact grouping rules.

All accepted S Blue occurrences belong to:

```text
S Blue
```

Each numbered E Blue is a separate exact group:

```text
E1 Blue
E2 Blue
E3 Blue
...
```

Example:

```text
E1 Blue + E1 Blue
→ same group, count = 2
```

but:

```text
E1 Blue + E2 Blue
→ different groups
```

Document exact arming and reset behavior from current production source.

---

# 40. Internal Reaction and Internal Blue

Internal/public state must not be confused with calculation validity.

Document separately:

```text
calculation-visible
lifecycle-visible
presentation-visible
```

Do not apply blanket filtering unless production explicitly does so in that branch.

---

# 41. Visibility

Explain:

```text
accepted calculation state
dominant lifecycle state
suppressed state
historical-only state
public state
serialized state
```

A hidden object may still provide valid calculation evidence.

---

# 42. OrderAudit

OrderAudit must be reconstructable from the Reference.

Document:

```text
physical identity
Reaction number
confirmation
stop geometry
causes
A causes
parent-stop cause
Reset-leg cause
accepted-live/carried-live use
consumed provenance
bridge consistency
serialization
```

---

# 43. Dataclass Schemas

For every algorithmically relevant dataclass include:

```text
class name
field names
field order
types
optional types
semantic meaning
creation stage
serialization mapping
```

Do not omit private-but-required intermediate schemas if their structure affects reconstruction.

---

# 44. Function-Level Reconstruction Contract

For every algorithmically important class/function/method document:

```text
purpose
arguments
return value
state read
state modified
search interval
directional mapping
boundary semantics
tie semantics
failure conditions
callers
downstream consumers
```

---

# 45. Performance Helpers Must Also Be Included

Performance helpers that do not change Algorithm behavior must still exist in the embedded implementation if production requires them.

Examples:

```text
binary-search indexes
precomputed chronology
per-run caches
identity maps
range min/max indexes
secondary lookup sets
```

They must be clearly labeled as:

```text
Performance Implementation Detail
```

not Algorithm rules.

---

# 46. No Missing Helper Code

Do not omit helper functions merely because they seem trivial.

If production code requires a helper to compile or behave correctly, that helper must be present in the Reference.

The standalone file must contain enough code to recreate a working implementation.

---

# 47. Embedded Code Must Be Complete

At the end of each Reference include a section such as:

```text
Exact Production Implementation Snapshot
```

For every production module include:

```text
Filename
Version
Last Modified
Role
Complete Python source
```

Do not use:

```text
...
code omitted
unchanged code
same as previous version
refer to repository
```

No production implementation may be truncated.

---

# 48. Embedded Code Must Be Usable

The embedded code must preserve:

```text
imports
constants
dataclasses
functions
classes
methods
type aliases
version constants
comments needed for non-obvious invariants
```

An engineer must be able to extract each code block and reconstruct the production source files.

---

# 49. No Dependency on Original Source After Generation

After the Reference is generated, perform this conceptual test:

```text
Delete the original Source directory.
```

Then ask:

```text
Can all required .py production files be recreated
from this Reference alone?
```

If not, the Reference is invalid.

---

# 50. Source Manifest

Include a complete production manifest:

```text
Filename
Source version
Last modified
Role
```

Do not allow stale manifest entries.

---

# 51. Source Symbol Index

Maintain a complete index of:

```text
classes
dataclasses
functions
methods
important constants
```

If source line numbers are included, regenerate them after every source change.

Never preserve stale line numbers from an earlier release.

---

# 52. Do Not Use Hashes as the Main Audit

Hashes may be stored as integrity metadata.

However, synchronization validation must be based on actual reading and semantic comparison.

Required:

```text
read code
compare code
understand code
compare behavior
```

Not merely:

```text
hash A == hash B
```

---

# 53. Reference Update Procedure

After every production source change:

```text
Freeze latest Source
→ Read all 9 files
→ Identify changed implementation
→ Determine whether behavior changed
→ Update Bullish semantic specification
→ Update Bearish semantic specification
→ Update invariant rules
→ Update function contracts
→ Update schemas
→ Update performance/architecture notes
→ Update version manifest
→ Regenerate symbol index
→ Replace embedded production source snapshot
→ Re-audit entire Reference
→ Re-run mirror validation
→ Re-run behavioral regression
```

---

# 54. Algorithm Change vs Implementation Change

Explicitly distinguish:

```text
Algorithm Change
```

from:

```text
Behavior-Preserving Refactor
```

If an optimization changes only implementation:

```text
Algorithm Changes: NONE
Behavioral Changes: NONE
```

must be recorded.

---

# 55. Change History

Every revision must document:

```text
what changed
why it changed
affected Source files
affected algorithm stages
Bullish impact
Bearish impact
serialization impact
whether old wording was superseded
```

---

# 56. Superseded Rules

Historical rules may remain for traceability only if clearly marked:

```text
SUPERSEDED
```

The current authoritative rule must never be ambiguous.

---

# 57. Validation Examples

Regression timestamps and symbols may be included as examples.

However, every fixture-specific example must explicitly state:

```text
Validation evidence only.
Never hardcode this symbol, timestamp, filename, or dataset.
```

Examples must not replace the general rule.

---

# 58. No Dataset-Specific Algorithm

Never introduce production logic based on:

```text
XAUUSD
USOIL
specific timestamp
specific file
specific RAW fixture
```

unless such behavior is genuinely part of the formal algorithm—which normally it must not be.

---

# 59. Serialization Contract

Document exact JSON serialization for every public entity.

Include:

```text
JSON key
source field
type
Decimal conversion
datetime conversion
null handling
ordering
range filtering
```

---

# 60. Stable Output Ordering

Ordering is algorithmically significant.

Do not assume sets or dictionaries may replace ordered lists unless the source explicitly guarantees equivalent ordering.

If a secondary set/index exists only for lookup, document that the ordered structure remains authoritative.

---

# 61. Datetime Contract

Document:

```text
timezone
epoch conversion
datetime construction
main timeframe alignment
full datetime comparison
lower-TF event time
```

Never reduce full datetime comparisons to time-of-day.

---

# 62. Exceptions and Hard Invariants

Document all hard errors that production intentionally raises.

Examples:

```text
invalid direction
missing Reaction
invalid range
missing owner
bridge inconsistency
impossible chronology
```

A reconstructed implementation must preserve these invariant protections where behaviorally relevant.

---

# 63. Mirror Audit After Every Release

For every directional branch inspect all mappings involving:

```text
Low / High
min / max
< / >
BoxBottom / BoxTop
FirstRed / FirstGreen
Bullish / Bearish
directional extreme
opposite directional extreme
```

Then separately verify invariants were not accidentally mirrored.

Especially:

```text
Doji = GREEN
Red/Blue family
E numbering
Lifecycle priority
StopAll
Order identity
Stage order
Serialization
```

---

# 64. Reflected-Market Validation

As an additional mirror test, for suitable RAW data define:

```text
open'  = -open
high'  = -low
low'   = -high
close' = -close
```

Then validate conceptually and behaviorally:

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

after applying the proper field mirror mapping.

This is a validation tool, not a replacement for source review.

---

# 65. Doji Exception for Mathematical Reflection

Because:

```text
Doji = GREEN
```

is direction-invariant, perfect RED/GREEN mathematical reflection is not expected for Doji candles.

Do not incorrectly "fix" this invariant to satisfy a synthetic symmetry test.

Production behavior wins.

---

# 66. Reference-to-Source Audit

Before release, verify all of the following manually and semantically:

```text
Every current Source behavior is documented.
Every current documented behavior exists in Source.
Every production function required for reconstruction exists in embedded code.
Every schema matches production.
Every directional rule matches production.
Every invariant matches production.
Every serialized field matches production.
Every stage is documented.
Every symbol index is current.
No source block is truncated.
```

---

# 67. Standalone Compilation Goal

The embedded code should be organized so that an engineer can extract the module sections into:

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

and reconstruct the production implementation without retrieving external algorithm code.

---

# 68. No Hidden Required Code

If production depends on code, it must exist inside the Reference.

Do not silently depend on:

```text
a missing helper
an omitted constant
an unavailable class
an external algorithm module
a previous Reference version
```

Only standard/runtime dependencies that are explicitly documented may remain external.

---

# 69. Third-Party and Standard Library Dependencies

List all non-project dependencies required to execute the reconstructed source.

Examples:

```text
Python version assumptions
orjson
zoneinfo
decimal
dataclasses
bisect
```

Clearly distinguish:

```text
project algorithm source
```

from:

```text
standard library / third-party dependency
```

The Reference must contain all project-owned algorithm code, but does not need to embed the Python standard library or third-party package source.

---

# 70. Architecture Reconstruction

Explain the intended module relationship:

```text
reaction_engine
    ↓
blue_line_detector
    ↓
a_zone_detector
    ↓
s_zone_detector
    ↓
e_zone_detector
    ↓
lifecycle_engine
    ↓
trading_pipeline
```

and show where:

```text
direction_policy
core_utils
```

are shared.

Actual dependency details must follow current production source, not this simplified illustration if they differ.

---

# 71. Complete Public API Documentation

Document the externally meaningful entry points required to run TradingBot.

Include:

```text
input format
direction parameter
timeframe parameter
range parameters
normalization behavior
pipeline invocation
output schema
progress/telemetry behavior if production relevant
```

---

# 72. Performance Implementation Notes

When the source contains performance optimizations such as:

```text
bisect
immutable indexes
per-run caches
precomputed Order chronology
range extrema indexes
Order identity maps
```

document why they are safe and which algorithmic invariant they preserve.

Example:

```text
Algorithm Requirement:
Select the first strict crossing after T.

Performance Implementation:
Use a lower-timeframe search index instead of rescanning all rows.

Behavioral Effect:
NONE.
```

---

# 73. Global Mutable State Warning

Document whether any module-level cache exists.

Any cache affecting calculations must have clearly defined lifecycle and contamination protection.

Cross-RAW or Bullish/Bearish hidden mutable state must not be introduced during reconstruction unless production explicitly uses it safely.

---

# 74. Reconstruction Completeness Test

For every major component ask:

```text
Can an engineer implement this without seeing the original source?
```

Specifically test:

```text
Reaction?
Reset?
Blue?
A?
S?
E?
Order?
OrderAudit?
Lifecycle?
StopAll?
Serialization?
```

If any answer is "not exactly," the Reference is incomplete.

---

# 75. Behavioral Completeness Test

A complete Reference must answer:

```text
What happens?
When does it happen?
Which exact event triggers it?
Which price is used?
Which candle owns the price?
Which lower-TF event confirms it?
What invalidates it?
What replaces it?
Who owns it?
What happens after its stop?
What is public?
What is serialized?
What is reset by StopAll?
```

---

# 76. Final Document Quality Standard

The Reference must not merely be readable.

It must be:

```text
Precise
Deterministic
Reconstructable
Auditable
Directionally explicit
Chronologically explicit
Ownership explicit
Schema explicit
Serialization explicit
Implementation complete
```

---

# 77. Mandatory Final Verification Report

Before declaring the Reference finished, report:

```text
All production files read completely: YES/NO

Bullish semantic audit: PASS/FAIL
Bearish semantic audit: PASS/FAIL
Mirror audit: PASS/FAIL

Doji invariant verified: PASS/FAIL
Strict crossing verified: PASS/FAIL
Decimal contract verified: PASS/FAIL
Lower-TF chronology verified: PASS/FAIL
Full RAW authority verified: PASS/FAIL

Reaction documented completely: PASS/FAIL
Reset documented completely: PASS/FAIL
Blue documented completely: PASS/FAIL
A documented completely: PASS/FAIL
S documented completely: PASS/FAIL
E documented completely: PASS/FAIL
StopAll documented completely: PASS/FAIL
Order documented completely: PASS/FAIL
OrderAudit documented completely: PASS/FAIL

Dataclass schemas synchronized: PASS/FAIL
Serialization synchronized: PASS/FAIL
Symbol index synchronized: PASS/FAIL

Complete project-owned production code embedded: PASS/FAIL
Any omitted required project code: YES/NO
Any external Source dependency: YES/NO

Standalone reconstruction possible: PASS/FAIL
```

Expected final state:

```text
Complete project-owned production code embedded: PASS
Any omitted required project code: NO
Any external Source dependency: NO
Standalone reconstruction possible: PASS
```

---

# 78. Absolute Final Instruction

Always follow this rule:

> The production Source defines the current behavior, but the Algorithm Reference must independently preserve everything required to understand and rebuild that behavior.

The Algorithm Reference is not merely documentation.

It is simultaneously:

```text
Algorithm Specification
+
Engineering Reconstruction Manual
+
Architecture Specification
+
Data Contract
+
Lifecycle Contract
+
Directional Mirror Contract
+
Serialization Contract
+
Complete Required Production Source Snapshot
```

The final equation is:

```text
CURRENT PRODUCTION SOURCE
+
COMPLETE SEMANTIC UNDERSTANDING
+
COMPLETE BULLISH/BEARISH MIRROR RULES
+
COMPLETE DIRECTION-INVARIANT RULES
+
EXACT CHRONOLOGY
+
EXACT OWNERSHIP
+
EXACT TIE RULES
+
EXACT DATA SCHEMAS
+
EXACT SERIALIZATION
+
FUNCTION-LEVEL RECONSTRUCTION CONTRACT
+
COMPLETE EMBEDDED PROJECT SOURCE CODE
=
TRUE STANDALONE ALGORITHM REFERENCE
```

The final acceptance criterion is:

> If every original TradingBot production `.py` file disappears, the appropriate standalone Algorithm Reference must still contain enough explanation and actual project-owned implementation code to reconstruct the complete production engine with the same algorithm, chronology, ownership, behaviors, and serialized output.

No required algorithm code may exist only outside the Reference.

No behavioral rule may exist only in the reader's assumptions.

No directional invariant may be left implicit.

No production helper required for reconstruction may be omitted.

And under all circumstances:

```text
DOJI IS ALWAYS GREEN.
```
