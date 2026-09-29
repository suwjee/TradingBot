> HISTORICAL SNAPSHOT. Versions, paths, commands, and verification results below describe the recorded run; use the current README and operations documentation for today's layout.

# Bridge Output Projection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the approved, opt-in Bridge YAML projection to the existing Calculation Report while preserving all trading calculations, legacy payload collections, and UI behavior.

**Architecture:** `trading_pipeline.py` will create new dictionaries only after final lifecycle/visibility closure, alongside—not in place of—the current direction collections. Immutable provenance is added only at already accepted A and StopAll construction points when the final objects otherwise cannot identify a presentation fact. The existing report renderer will select the parallel projection when available and otherwise retain its legacy row adapter and unchanged UI.

**Tech Stack:** Python 3.12+ dataclasses/Decimal/unittest/PyYAML; native ESM and Node test runner; existing Vite local middleware.

**Spec:** `docs/development/specs/Bridge_Output_Projection.md`; complete field schema from attachment `0291ca05-7e4e-4c04-88dc-bfdd331e04e0/Pasted text.txt`; final constraints from attachment `ac4566ed-1834-4664-b828-5746a28016d1/Pasted text.txt`.

## Global Constraints

- Preserve the exact current calculation path, accepted behavior state, Decimal strings, strict crossings, RAW chronology, order ranking, lifecycle priority, visibility, public legacy arrays, and UI behavior.
- The implementation baseline is Bridge `1.4.1`, Reaction `9.8.0`, Blue `2.3.0`, A `1.6.4`, S `4.20.0`, E `6.13.0`, and lifecycle `1.15.2`, with the hashes in the design specification.
- The named repository copies of `TradingBot_Bridge_Output_Complete_Implementation_Spec.md` and `TradingBot_AI_Operating_Protocol.md` are absent. Use the two supplied attachments as the approved schema; never infer a missing key, field order, or relationship.
- `--bridge-output` is opt-in. Omitting it must leave the JSON direction collections byte-equivalent; enabling it may add only `bridgeOutput`.
- Construct every `bridgeOutput[group]` from the exact final selected object sequence supplied to the matching legacy serializer. Array positions never identify Orders or parent behavior.
- Join physical Orders solely by `(firstIndex, breakIndex)` in the final accepted audit context. A `currentOrder` requires an exact accepted creator match and is otherwise `null`.
- `StopAll.parent.behavior` is its actual donor, never its stopped group. A donor stop is `null` unless an independent physical stop of the exact donor is proven.
- Do not stage, commit, reset, clean, stash, rename, or modify pre-existing user-owned paths. The working tree is intentionally dirty.

## Review Focus

- An omitted `--bridge-output` flag must yield the exact prior direction payload; Task 2 hashes a controlled legacy payload before and after the projection branch.
- A parent-stop label that conflicts on source, family, number, stop event, direction, or lifecycle scope must not claim `currentOrder`; Task 3 asserts `null` and keeps merged reset-leg evidence.
- An S Red donor promoted to StopAll must not acquire `stoppedAt` from `gateEventTime`; Task 1 exercises the immutable donor metadata and null stop rule.
- Hidden/internal or rescued historical items must never shift parallel display associations; Task 3 checks source sentinels, lengths, and order in Bullish and Bearish sequences.
- A historical cached report without `bridgeOutput` must still render exactly through `manualInfoObject`; Task 4 checks both projection selection and fallback, including parsed YAML.

---

## File Structure

| File | Responsibility |
| --- | --- |
| `engine/pipeline/a_zone_detector.py` | Optional keyword-only A formation and effective Blue-stop presentation provenance, written only after an A has already been accepted. |
| `engine/pipeline/lifecycle_engine.py` | Optional keyword-only StopAll donor presentation provenance, copied from the already selected E or S source. |
| `engine/bridge/trading_pipeline.py` | CLI opt-in, finalized sequence selection, pure projection builders, exact audit joins, and additive `bridgeOutput` serialization. |
| `engine/bridge/test_trading_pipeline.py` | Python unit and regression tests for opt-in behavior, provenance, Order ownership, alignment, immutability, and legacy equality. |
| `apps/chart/vite.config.js` | Pass `--bridge-output` only to new calculation processes; continue using the existing bridge-source fingerprint and cache storage. |
| `apps/chart/src/features/manual-review/render.js` | Read the parallel projection for an existing record, with the current legacy adapter as fallback; no markup, formatter, or interaction change. |
| `tests/chart/unit/manual-review.test.mjs` | Node tests for parallel projection selection, fallback, unchanged disclosure markup, and PyYAML parsing of formatted YAML. |

### Task 1: Passive A and StopAll presentation provenance

**Files:**
- Modify: `engine/pipeline/a_zone_detector.py: AZone, _double_stop_a_candidates, _detect_ordinary_a`
- Modify: `engine/pipeline/lifecycle_engine.py: StopAll, _stopall_from_e, _stopall_from_s`
- Test: `engine/bridge/test_trading_pipeline.py`

**Interfaces:**
- Produces: `AZone.formation_route`, `AZone.blue_1_stop_event_time`, and `AZone.blue_2_stop_event_time` as keyword-only optional immutable fields.
- Produces: `StopAll.donor_behavior_type`, `donor_source_index`, `donor_source_time`, `donor_family`, `donor_number`, `donor_stop_time`, and `donor_stop_event_time` as keyword-only optional immutable fields.
- Consumes: only objects already selected by `_detect_ordinary_a`, `_double_stop_a_candidates`, `_stopall_from_e`, and `_stopall_from_s`.

- [ ] **Step 1: Write failing provenance tests**

Add tests that construct `AZone` and `StopAll` with the proposed keyword-only fields and assert exact retention through `dataclasses.replace`:

```python
from dataclasses import fields, replace
from datetime import datetime
from decimal import Decimal

def test_presentation_provenance_is_immutable_and_keyword_only(self):
    event = datetime(2026, 8, 25, 10, 0, 5)
    a_values = {item.name: None for item in fields(AZone)}
    a_values.pop("formation_route", None)
    a_values.pop("blue_1_stop_event_time", None)
    a_values.pop("blue_2_stop_event_time", None)
    a_values.update(direction="bullish", source_index=17, price=Decimal("0.10"))
    zone = AZone(**a_values, formation_route="ordinary", blue_1_stop_event_time=event)
    self.assertEqual(replace(zone, price=zone.price).formation_route, "ordinary")

    stopall_values = {item.name: None for item in fields(StopAll)}
    for key in ("donor_behavior_type", "donor_source_index", "donor_source_time", "donor_family", "donor_number", "donor_stop_time", "donor_stop_event_time"):
        stopall_values.pop(key, None)
    stopall_values.update(direction="bullish", number=1, source_index=17, price=Decimal("0.10"))
    stopall = StopAll(**stopall_values, donor_behavior_type="S", donor_source_time=event, donor_stop_event_time=None)
    self.assertIsNone(replace(stopall, number=2).donor_stop_event_time)
```

Add one test for each constructor path asserting `_stopall_from_e()` retains donor type `E` and its exact source identity, while `_stopall_from_s()` retains donor type `S` with both donor stop fields `None` unless a separately passed proven stop exists.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python engine/bridge/test_trading_pipeline.py`

Expected: FAIL because the proposed keyword-only provenance parameters do not exist.

- [ ] **Step 3: Add only passive immutable fields and populate accepted paths**

Import `field` from `dataclasses`. Add the fields with `field(default=None, kw_only=True)` so existing positional constructors remain compatible. Set `formation_route="double-stop"` only in `_double_stop_a_candidates()` and `formation_route="ordinary"` only in `_detect_ordinary_a()` after the existing accepted candidate is assembled. Copy an exact Blue stop event only when the chosen branch already uses that exact `BlueState.stop_event_time`; otherwise pass `None`.

In the StopAll constructors, copy identity fields from the already selected `item`. `_stopall_from_e()` sets donor type `E`; `_stopall_from_s()` sets donor type `S`. Set donor stop fields only from an existing, exact donor strict-stop field. Never use `gate_event_time`, `stopped_behavior_*`, an E decision, or a group event as a donor stop substitute.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `python engine/bridge/test_trading_pipeline.py`

Expected: PASS, including the new provenance tests; no assertion may inspect or change a detector decision.

- [ ] **Step 5: Check modified engine syntax**

Run: `python -c "import ast, pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['engine/pipeline/a_zone_detector.py','engine/pipeline/lifecycle_engine.py']]"`

Expected: exit code 0.

### Task 2: Opt-in finalized Bridge projection shell

**Files:**
- Modify: `engine/bridge/trading_pipeline.py: parse_arguments, serialize_direction_payload, build_direction_output`
- Test: `engine/bridge/test_trading_pipeline.py`

**Interfaces:**
- Produces: `args.bridge_output: bool` from `--bridge-output`.
- Produces: `project_direction_bridge_output(direction, market, state, visibility, selected) -> dict[str, list[dict]]`.
- Consumes: exact already selected sequences named `reactions`, `resets`, `blue_lines`, `a_zones`, `s_zones`, `e_zones`, `stopalls`, and `prepared_order_audit`.

- [ ] **Step 1: Write failing opt-in and alignment tests**

Add a test that parses a valid bridge command once without the flag and once with the flag, then asserts `False` and `True` respectively. Add a pure projection fixture with a unique `source_index` sentinel in each group and assert:

```python
self.assertEqual(list(projected), ["reactions", "resets", "blueLines", "aZones", "sZones", "eZones", "stopAlls", "orderAudit"])
self.assertEqual(len(projected["sZones"]), len(selected.s_zones))
self.assertEqual(projected["sZones"][0]["_test_source_index"], selected.s_zones[0].source_index)
```

The production projector must not emit `_test_source_index`; the fixture-only projector spy receives it through a test callback or an asserted returned source-object list.

Add a legacy regression test that deep-copies a direction payload built without the flag, builds the opt-in result from the same fixture, removes only `bridgeOutput`, and uses `self.assertEqual` to compare all legacy values, types, `None`s, ordering, and collection keys.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python engine/bridge/test_trading_pipeline.py`

Expected: FAIL because the parser has no `bridge_output` attribute and no projection builder exists.

- [ ] **Step 3: Implement the opt-in shell and single-source sequence selection**

Add `parser.add_argument("--bridge-output", action="store_true")`. In `serialize_direction_payload`, select each final object sequence exactly once before serializing it. Pass that exact sequence to both its legacy serializer and the projection builder. Preserve existing serializer values and order by feeding the same sequence they previously received; for `orderAudit`, sort the prepared records once with the existing `(firstTime, breakTime)` order before both consumers.

Return the current direction dictionary unchanged when the flag is false. When true, assign only `payload["bridgeOutput"] = project_direction_bridge_output(direction, market, state, visibility, selected)` after every legacy key has been built. Keep projection code in `trading_pipeline.py`, so its existing Vite source fingerprint invalidates stale payloads without adding a runtime dependency.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `python engine/bridge/test_trading_pipeline.py`

Expected: PASS; the no-flag payload must contain no `bridgeOutput`, and the enabled payload must differ only by that mapping.

- [ ] **Step 5: Check bridge syntax**

Run: `python -m py_compile engine/bridge/trading_pipeline.py`

Expected: exit code 0.

### Task 3: Exact schema, physical Order, parent, and currentOrder projectors

**Files:**
- Modify: `engine/bridge/trading_pipeline.py: project_direction_bridge_output and its pure helper functions`
- Test: `engine/bridge/test_trading_pipeline.py`

**Interfaces:**
- Produces: ordered pure builders `project_reaction`, `project_reset`, `project_blue`, `project_a`, `project_s`, `project_e`, `project_stopall`, `project_order_audit`, and `project_physical_order`.
- Produces: `resolve_current_order(behavior, behavior_identity, audit_by_identity) -> dict | None`.
- Consumes: final prepared audit records indexed only by `(firstIndex, breakIndex)`, final source objects, chronology, and the passive provenance from Task 1.

- [ ] **Step 1: Write failing schema and ownership tests**

Build `SimpleNamespace` fixtures for one object per schema family and assert insertion-order keys exactly match the approved field order. Test a Reset Blue includes `brokenLevel` while a Scale Blue omits it; S Red has `formation is None`; S Blue `simple`, `advanced`, `type3`, and `type4` map to Types 1–4; Type-3/Type-4 `parent.order is None`; and StopAll gate labels map to Types 1–3.

Add exact ownership fixtures:

```python
creator = cause("parent-stop", parentType="E2", parentFamily="red", parentSourceTime=e.source_time, eventTime=e_stop)
wrong_source = cause("parent-stop", parentType="E2", parentFamily="red", parentSourceTime=other_time, eventTime=e_stop)
merged = prepared_order(identity=(17, 23), causes=[creator, reset_leg])

self.assertEqual(resolve_current_order(e, e_identity, {identity: merged})["firstCandle"]["index"], 17)
self.assertIsNone(resolve_current_order(e, e_identity, {identity: prepared_order((17, 23), [wrong_source, reset_leg])}))
```

Assert an accepted-live/carried-live-only cause, a display-order match, and a nearest-timestamp match all return `None`. Assert the merged `reset-leg` cause is preserved in projected Order Audit. Add StopAll tests proving donor identity comes from `donor_*` fields and a promoted S donor has `parent.behavior.stoppedAt == {"time": None, "eventTime": None}` or the exact approved nullable representation, never the gate event.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python engine/bridge/test_trading_pipeline.py`

Expected: FAIL because the schema builders and exact identity resolver do not exist.

- [ ] **Step 3: Implement pure read-only builders**

Implement an `audit_by_identity` dictionary from final `prepared_order_audit`, keyed exclusively by the Order reaction's First/Break indexes. `project_physical_order` formats one audit record without mutation. It preserves exact Decimal `str` values, Times rendered through the existing Tehran formatter, stop values and pending stop `None`s, plus every accepted cause.

Implement `resolve_current_order` to match all recorded creator evidence: direction, behavior type, applicable family/number, original behavior source identity, exact strict-stop event, lifecycle scope, and the final accepted parent-stop cause. Return `None` for a missing, conflicting, reset-leg-only, accepted-live-only, carried-live-only, provisional, or out-of-range identity not present in the final prepared audit. Do not call detector decision code, inspect neighboring rows, or recalculate a stop.

Project parent behavior from stored original lineage. For E, resolve its actual S/E/StopAll parent from final accepted source identity; never choose a latest visible row. For StopAll, use only Task 1 donor metadata. Fill donor `stoppedAt` only from the exact donor stop metadata and leave it `null` for an S Red promotion with no physical donor stop. Use the attached complete schema verbatim for every field name, nesting, optional section, and object-key order. Return `null` for any unproven event or provenance field.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `python engine/bridge/test_trading_pipeline.py`

Expected: PASS for schema order, field nullability, exact Order identity, multiple causes, ambiguous ownership, donor-versus-group identity, and array source correspondence in both directions.

- [ ] **Step 5: Run projection immutability regression**

Run: `python engine/bridge/test_trading_pipeline.py`

Expected: PASS for a test that snapshots `repr`/deep copies of source objects, audit causes, and selected sequences before two projector calls, then proves the snapshots and both projections are identical afterward.

### Task 4: Enable new reports and consume the projection without UI changes

**Files:**
- Modify: `apps/chart/vite.config.js: runCalculation argument list`
- Modify: `apps/chart/src/features/manual-review/render.js: manualInfoObject`
- Modify: `tests/chart/unit/manual-review.test.mjs`

**Interfaces:**
- Consumes: direction-level `bridgeOutput[group][index]` from Task 2.
- Produces: unchanged event-card markup and YAML formatter output, with projected values preferred only when the corresponding object exists.

- [ ] **Step 1: Write failing renderer and YAML round-trip tests**

Add a report fixture with `directions.bullish.sZones[0]` and matching `directions.bullish.bridgeOutput.sZones[0]`, then assert `buildReviewBody()` stores the projected field in its returned `bridgeData`. Add a second fixture with no `bridgeOutput` and assert the current legacy `manualInfoObject` fields remain present.

Format a representative projected object with `formatInfoYaml`, send the string to the installed Python parser, and assert the parsed result preserves null and string prices:

```js
const parsed = spawnSync("python", ["-c", "import sys,yaml,json; print(json.dumps(yaml.safe_load(sys.stdin.read())))"], { input: yaml, encoding: "utf8" });
assert.equal(parsed.status, 0);
assert.deepEqual(JSON.parse(parsed.stdout), { type: "S", stop: { time: null, price: "0.10" } });
```

Assert the body retains `class="bridge-output"`, lacks an `open` attribute, and retains the existing copy-button labels.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `npm.cmd test -- manual-review.test.mjs`

Expected: FAIL because `manualInfoObject` does not select `groups.bridgeOutput[group][index]`.

- [ ] **Step 3: Make the minimal Vite and renderer changes**

Append `"--bridge-output"` to the Vite `runDetector` argument list used by newly started calculations. In `manualInfoObject`, before legacy field adaptation, read the corresponding non-array plain object at `groups?.bridgeOutput?.[group]?.[index]`; return it unchanged when it exists. Otherwise execute the existing fallback unchanged. Do not alter `yamlLines`, `reviewRuntime`, HTML templates, styles, labels, card events, filters, or cache-file reads.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `npm.cmd test -- manual-review.test.mjs`

Expected: PASS for projected preference, legacy fallback, YAML parse round trip, and unchanged disclosure markup.

- [ ] **Step 5: Run JavaScript syntax checks**

Run: `node --check apps/chart/vite.config.js; node --check apps/chart/src/features/manual-review/render.js`

Expected: both commands exit 0.

### Task 5: End-to-end zero-difference verification

**Files:**
- Modify: `engine/bridge/test_trading_pipeline.py` only if a test fixture is needed to make a required acceptance case deterministic.
- Verify: `engine/bridge/trading_pipeline.py`, `apps/chart/vite.config.js`, `apps/chart/src/features/manual-review/render.js`, and all Task 1–4 tests.

**Interfaces:**
- Consumes: all completed production and test interfaces.
- Produces: recorded command output and a baseline comparison report; no runtime/cache rewrite.

- [ ] **Step 1: Create a failing direct-bridge comparison test**

Add a test helper that executes the same complete, non-sensitive regression RAW input twice in a temporary directory: once without `--bridge-output` and once with it. Remove only `directions.*.bridgeOutput` from the enabled parsed object, normalize the observational `timings`, and assert byte-for-byte serialized equality of every remaining payload field. Assert the enabled object has all eight bridge-output collection keys and no legacy collection key changes.

- [ ] **Step 2: Run the comparison test and verify RED**

Run: `python engine/bridge/test_trading_pipeline.py`

Expected: FAIL until the projection is wired through the actual CLI and contains the required collections.

- [ ] **Step 3: Complete only missing presentation wiring**

Correct projection wiring, test fixtures, or presentation-only provenance exposure revealed by the failure. If satisfying a field would require a detector predicate, calculation range, chronology, Order ranking, lifecycle, visibility, or legacy serializer change, leave that field `null`, record the provenance gap in the test, and do not change trading code.

- [ ] **Step 4: Run the complete verification set**

Run:

```powershell
python engine/bridge/test_trading_pipeline.py
npm.cmd test
npm.cmd run build
node --check apps/chart/vite.config.js
node --check apps/chart/src/features/manual-review/render.js
```

Expected: every command exits 0. Report any environmental failure verbatim rather than calling the task complete.

- [ ] **Step 5: Record final baseline evidence without touching runtime data**

Run the Bridge against the approved full RAW regression fixture only through a temporary output path or in-memory process capture. Record module hashes, enabled/disabled legacy comparison hashes, bridge-output schema findings, unsupported `null` provenance, and any source/reference divergence in the implementation report. Do not write to `runtime/cache`, replace a persisted calculation, or hardcode any observed timestamp, symbol, price, or fixture identity.

## Plan Self-Review

- Spec coverage: Tasks 1–3 implement passive provenance, additive projection, exact ownership, StopAll donor semantics, alignment, schema ordering, nulls, and Order causes. Task 4 limits the frontend to existing YAML values. Task 5 validates zero difference and the full suite.
- Placeholder scan: no implementation step relies on a future or unspecified action; unavailable schema facts are explicitly `null` and recorded.
- Type consistency: Task 1 produces the only optional provenance consumed by Task 3. Task 2 produces the exact selected sequences and `bridgeOutput` map consumed by Task 3 and Task 4. Task 4 consumes only the direction/group/index association produced by Task 2.
- Review focus coverage: the five listed failure modes are tested by Tasks 1–4, with Task 5 as the end-to-end regression gate.
