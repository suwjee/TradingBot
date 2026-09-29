# Bridge Output Projection Design

**Status:** Revised for final review  
**Date:** 2026-09-23  
**Scope:** The YAML values shown only inside the Calculation Report / Manual Test `Bridge output` disclosure.

## Authority and Baseline

The implementation authority is the current working-tree source. The detailed
field schema is the complete Bridge Output specification supplied with this
task in attachment `0291ca05-7e4e-4c04-88dc-bfdd331e04e0/Pasted text.txt`,
together with the final requirements in attachment
`ac4566ed-1834-4664-b828-5746a28016d1/Pasted text.txt`. The repository does
not currently contain the separately named
`TradingBot_Bridge_Output_Complete_Implementation_Spec.md` or
`TradingBot_AI_Operating_Protocol.md`; that absence must be reported in the
implementation record and does not authorize replacement rules.

Before production-code implementation begins, the engineer must have the exact
approved YAML schema from that complete specification available for direct
field-by-field comparison. A missing repository copy, inaccessible attachment,
or ambiguous field must stop that field's implementation; it never authorizes
guessing a key, nesting, field order, optional object, or output contract. The
fallback for an unproven value in an otherwise specified field is `null`, not a
new derivation.

Before editing, the relevant production files were recorded as follows. These
versions and SHA-256 hashes are the required comparison baseline; the current
source controls behavior when a maintained reference has older version text.

| Source | Version | SHA-256 |
| --- | --- | --- |
| `engine/bridge/trading_pipeline.py` | `1.4.1` | `98F54CF3BE6DDACD4E6B523B604BE5A00635DCF8B464BC7D03772BBCCCDED62E` |
| `engine/pipeline/reaction_engine.py` | `9.8.0` | `BEA0D5A5E95EE15AD54D024F6C01B8C777BA2ABCC3C8E671118F1AE2DF28F2A6` |
| `engine/pipeline/blue_line_detector.py` | `2.3.0` | `6FA01D94BC98060B62BC7E68DB0EC24A0B0159727D44043AFFEE7130A9C11448` |
| `engine/pipeline/a_zone_detector.py` | `1.6.4` | `F5658AEF5105DCFAD916D3EA6F792877737C2568D67CF27C7B63C2638C5343FD` |
| `engine/pipeline/s_zone_detector.py` | `4.20.0` | `7714025B3F43087B09844DF6FEEEF4EEF0EC72EEB841115293DF4C126FD202EE` |
| `engine/pipeline/e_zone_detector.py` | `6.13.0` | `6E32B947AA1B4E1E6B986F26EE9A464542F320DC6A207ECE1E8FCE54407D0369` |
| `engine/pipeline/lifecycle_engine.py` | `1.15.2` | `84BED2E674F855A4D2DC52960840EDDC6D8F058FF247B893A319EECDC36E152D` |

The maintained Bullish and Bearish references remain required reading before
an engine-adjacent provenance addition. Any discrepancy with this baseline,
the final requirements, or those references is a reportable blocker for that
field; it is never resolved through a trading-rule change.

## Goal

Make the existing collapsed `Bridge output` disclosure render the approved
Reaction, Reset, Blue Line, A, S, E, StopAll, and Order Audit YAML schema
without changing any trading calculation, lifecycle decision, public legacy
collection, visual styling, DOM layout, controls, or report interaction.

## Existing Data Flow

`engine/bridge/trading_pipeline.py` calculates and finalizes trading state,
then serializes the legacy direction collections. `apps/chart/src/features/
manual-review/render.js` currently derives a display-only object from those
legacy rows before formatting it as YAML. That derivation lacks several
source-backed parent, Order, exact-event, and lifecycle provenance fields.

## Design

### Additive, opt-in Bridge view

Add an opt-in `--bridge-output` bridge argument. When enabled, each direction
gets an additive `bridgeOutput` mapping whose keys are the existing collection
names (`reactions`, `resets`, `blueLines`, `aZones`, `sZones`, `eZones`,
`stopAlls`, and `orderAudit`). The mapping contains JSON-like values in the
approved field order. It is not a replacement for any legacy collection.

The Vite calculation caller enables this argument for new calculation reports.
The changed bridge source remains part of the existing calculation fingerprint,
so an old cached payload without `bridgeOutput` is not treated as the new
output. A direct bridge invocation that omits the argument has byte-equivalent
legacy direction collections.

The cache fingerprint already includes `trading_pipeline.py`; the Vite caller
must pass `--bridge-output` only for newly produced calculation reports. It
must neither rewrite historical cache files nor change user runtime data.

Each projected collection is constructed from the same finalized, selected
sequence that the matching legacy serializer receives. Therefore, for every
group and every valid index, `bridgeOutput[group][index]` describes exactly
`groups[group][index]` after all visibility, historical rescue, internal-object,
range, and ordering rules have run. Array position is only this guaranteed
display association; it is never evidence of a physical Order identity or a
parent-behavior relationship.

### Read-only projection boundary

Build the projection only after `finalize_direction_visibility()` returns.
The projector reads final selected objects, full chronology, final Order Audit,
and retained authoritative detector provenance. It returns newly allocated
plain dictionaries and lists; it does not mutate dataclasses, audit entries,
candidate lists, filters, chronology, cache state, or serializers.

The projector joins physical Orders exclusively with `(firstIndex, breakIndex)`
and final accepted audit entries. It resolves `currentOrder` only when the
final accepted Order Audit contains an exact, verifiable association between
that physical Order and the authentic stopped behavior. A generic
`parent-stop` cause is insufficient unless its complete owner identity,
behavior source, family/number where applicable, and exact stop event match
unambiguously. `reset-leg` provenance and every valid multiple-cause
association stay attached to the physical Order; they are not converted into
or used to guess behavior ownership. An unproven or ambiguous association is
`null` and is recorded as missing provenance in a diagnostic or regression
test. The projector does not scan RAW with new eligibility rules, choose the
nearest time, use display order, construct a provisional Order, or use a
fixture-specific exception.

The physical-Order view is a single canonical, read-only formatter shared by
`parent.order`, `currentOrder`, and `orderAudit`. It preserves the physical
identity, First/Break candles, frozen box geometry, confirmation, stop level
and source, stop-hit chronology, and every final accepted cause. It never
deduplicates by timestamp, price, reaction number, label, or display index.
Native Reaction mode and Order_A/Order_B provenance remain distinct concepts.

`parent.order` is the physical Order used to form or decide a behavior;
`currentOrder` is an Order created by that behavior's own authentic strict
stop. A present `parent.order` therefore neither implies nor supplies a
`currentOrder`. `accepted-live` and `carried-live` explain reuse and do not
transfer the original creator. A public-audit absence may be resolved only by
an already validated, full-scope final accepted ledger containing the exact
identity and exact creator relationship; otherwise the nested `currentOrder`
is `null` and no new public audit row is introduced.

### Immutable provenance additions, only where necessary

The existing objects already expose most presentation facts. The implementation
may add optional immutable metadata only where the source cannot otherwise
identify a requested fact unambiguously:

- `AZone` formation route (`ordinary` or `double-stop`) and branch-owned exact
  effective Blue-stop evidence.
- StopAll donor identity needed to distinguish the real source behavior from
  its stopped group.

Those values are written at an already accepted construction point and merely
carried through existing `replace`/filter behavior. They must not be read by a
detector decision, alter an order ledger, modify a price, change a time window,
or affect visibility. Any unavailable exact event remains `null`.

`StopAll.parent.behavior` is projected from that retained donor identity: the
actual S or E behavior that produced the accepted StopAll. It must never be
derived automatically from `stoppedBehaviorType`, `stoppedBehaviorKey`, or the
stopped behavior group. If the existing accepted StopAll source cannot identify
the donor unambiguously, optional immutable presentation metadata is captured
at `_stopall_from_e()` or `_stopall_from_s()` and carried forward unchanged.
This metadata cannot alter a StopAll gate, formation decision, lifecycle state,
priority, boundary, visibility, or behavior ownership.

`parent.behavior.stoppedAt` is populated only by a proven physical strict stop
of that exact donor behavior in the relevant accepted relationship. In the S
Red → StopAll promotion path, `gateEventTime`, stopped-group evidence, and an
E decision are not evidence that the donor S stopped; the field is therefore
`null` unless an independent authoritative S stop is present. The same rule
applies to every StopAll donor: a convenient lifecycle gate is never
substituted for a physical donor stop.

### Manual-review consumption

For an existing report record, `render.js` first uses the parallel
`groups.bridgeOutput[group][index]` projection when present, then retains the
current `manualInfoObject()` implementation as a fallback for historical cache
files. The YAML formatter, disclosure markup, copy button, CSS, labels,
filtering, timelines, and event-card structure remain unchanged.

Parallel arrays are only a display association: the Bridge creates each
projection item beside its corresponding selected legacy item. They are not
used to identify Orders or parent behaviors; those joins happen in Python with
the physical identity described above.

## Approved Presentation Rules

- Times render as `YYYY-MM-DD HH:mm:ss` in `Asia/Tehran`.
- Decimal prices remain their exact serialized strings.
- `null` distinguishes missing/unknown provenance from a pending stop on a
  present Order.
- S Red has `formation: null`; native `formation_type` remains unchanged.
- Reset Blue includes `brokenLevel`; Scale Blue omits it.
- StopAll labels map only at presentation time:
  `sequence-group-stop` → `Type-1`, `stopall-stop` → `Type-2`, and
  `opposite-s-group-stop` → `Type-3`.
- Legacy `reactions`, `resets`, `blueLines`, `aZones`, `sZones`, `eZones`,
  `stopAlls`, and `orderAudit` retain their fields, values, ordering, filtering,
  and serialization.

## Non-goals

- No change to detector predicates, Decimal operations, order eligibility,
  strict crossing rules, event chronology, lifecycle priority, accepted Order
  ranking, internal/public visibility, or direction mirroring.
- No frontend calculation, price comparison, raw-data reconstruction, or
  pseudo-Order creation.
- No UI redesign or visible change outside the YAML values under the existing
  `Bridge output` disclosure.
- No change to current cache/user runtime data.

## Verification

Tests will prove the opt-in boundary, field nesting/order and null behavior,
immutable projection inputs, exact physical-Order association, and fallback
compatibility in the manual-review renderer. A representative bridge run will
hash every legacy direction collection before and after the new output is
enabled, excluding only the additive `bridgeOutput` key. The chart test suite,
bridge tests, JavaScript syntax checks, and production build will run before
completion.

Regression coverage will prove that every parallel projected array remains in
lockstep with its legacy collection for Bullish and Bearish output, including
hidden/internal objects, historical rescued items, out-of-range nested parents,
range filtering, lifecycle filtering, and final ordering. The test fixtures
will assert both equal lengths and one-to-one source-object correspondence;
they will also assert that Order and parent joins still use physical/provenance
identity rather than their presentation indexes.

The implementation plan must also include these mandatory acceptance checks:

- Record source ownership, versions, hashes, reference availability, and the
  exact baseline payload for enabled/disabled component combinations.
- Prove the default command has byte-equivalent legacy output and that enabled
  output differs only by the additive `bridgeOutput` mapping.
- Assert repeated projections do not mutate finalized objects, audit entries,
  detector caches, chronology, filters, or accepted histories.
- Parse the emitted YAML and check field nesting, order, optional sections,
  exact Decimal strings, Tehran time rendering, and `null` distinctions.
- Cover 1s/5s evidence in a 30s view, equality non-crossings, Doji GREEN, and
  independent Bullish/Bearish behavior.
- Cover merged parent-stop/reset-leg causes, shared and carried Orders,
  single-consumption, ambiguous ownership returning `currentOrder: null`,
  out-of-range nested parents/Orders, and pending Order stops.
- Cover ordinary and Double-Stop A, all four S Blue labels plus S Red,
  recursive E and historical rescue, all StopAll gates including StopAll2+,
  donor-versus-stopped-group identity, and an S donor with no physical stop.
- Verify manual-review projection consumption and legacy fallback without any
  change to markup, YAML formatting, copying, controls, filtering, labels,
  CSS, or production report interaction.

## Risk Controls

If a requested value cannot be derived from already accepted state, the output
uses `null` and records the missing provenance in a test or diagnostic. A
mismatch with an illustrative timestamp, a hidden parent, an out-of-range
Order, a tied event, or either direction never authorizes an algorithm change.
