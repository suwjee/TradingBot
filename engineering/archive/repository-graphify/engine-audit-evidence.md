Read-only audit of the current working tree. Findings below are source-verified unless explicitly labeled as a risk. No engine regression or independent historical Bearish validation was performed; one package-import failure was reproduced with bytecode writing disabled.

Current versions:

| File under `engine/` | Constant | Value |
|---|---|---|
| `bridge/trading_pipeline.py` | `TRADING_PIPELINE_VERSION` | `1.2.2` |
| `pipeline/reaction_engine.py` | `REACTION_ENGINE_VERSION` | `9.5.2` |
| `pipeline/blue_line_detector.py` | `BLUE_LINE_VERSION` | `2.3.0` |
| `pipeline/a_zone_detector.py` | `A_ZONE_VERSION` | `1.6.3` |
| `pipeline/s_zone_detector.py` | `S_ZONE_VERSION` | `4.13.1` |
| `pipeline/e_zone_detector.py` | `E_ZONE_VERSION` | `6.6.2` |
| `pipeline/lifecycle_engine.py` | `STOP_ALL_VERSION` | `1.10.1` |
| `pipeline/direction_policy.py` | `DIRECTION_POLICY_VERSION` | `1.0.0` |
| `pipeline/core_utils.py` | `CORE_UTILS_VERSION` | `1.0.0` |

A additionally declares `A_ZONE_LAST_MODIFIED_DATE = "2026-09-17"`.

1. Entry points and contracts

`engine/bridge/trading_pipeline.py:parse_arguments` requires:

- Engine paths: `--reaction-engine/--engine`, `--blue-line-engine/--blue-engine`, `--a-zone-engine/--a-engine`, `--s-zone-engine/--s-engine`.
- Data and range: `--data`, integer `--timeframe`, integer `--from-time`, integer `--to-time`.
- `--direction bullish|bearish|both`.
- Optional `--e-zone-engine/--e-engine` and `--lifecycle-engine/--stopall-engine`.
- `--blue-lines`, `--a-zones`, `--s-zones`, each `enabled|disabled`, default enabled.

Only positive timeframe is explicitly validated beyond argparse. Lifecycle is loaded from its default pipeline location even when its CLI path is absent, but public StopAll computation requires an explicitly supplied lifecycle path, an E engine, and enabled S.

`prepare_market_context` reads the entire JSON file with `orjson`, removes a UTF-8 BOM, and expects a row array containing `time/open/high/low/close`. `build_candle_buckets` assumes chronological input. It merges consecutive rows with the same integer timestamp into lower candles, and aggregates main candles into epoch-aligned `timestamp // timeframe * timeframe` buckets. Open comes from the first row, Close from the last, High/Low from extrema. It performs no sorting, global deduplication, missing-candle filling, OHLC-integrity validation, or cadence validation.

The entire physical RAW is calculation context, including observations after `to-time`. Requested endpoints select visible main buckets. Reaction visibility uses First index; Reset uses Reset index; Blue/A/S/E/StopAll use source index; OrderAudit uses Order First index. References and decision times can therefore lie outside the visible range. Source indexes and ordinals remain full-file identities.

`main` emits compact JSON to stdout. Progress is stderr `QG_PROGRESS:{"status","label","durationMs"?}`. Successful exit is 0; runtime exceptions yield `{"error": ...}` and exit 1. Argparse failures use normal argparse stderr/exit 2. Imports before the guarded `main`, including missing `orjson`, can fail outside this JSON error contract. `timed` emits “completed” in `finally`, even for a failed stage.

Caller: `apps/chart/vite.config.js:runDetector` launches a fresh Python process using `TRADINGBOT_PYTHON || "python"`, all six explicit engine paths, and legacy flag aliases. `/api/reactions` accepts POST `{id,timeframe,from,to,direction,blueLines,requestId?}`; it accepts only one direction, always enables A/S, and always supplies E/lifecycle. Browser Blue visibility can be disabled while Blue remains a calculation dependency. The endpoint returns cached or new bridge JSON, adds cache/source/timing headers, and converts failures to HTTP 400. SSE progress is `/api/reactions/progress`.

2. Actual orchestration

`prepare_pipeline_state` computes both directional Reaction streams whenever any behavior module is needed, even for a single-direction response. It classifies internal Reaction geometry with `build_behavior_reaction_views`.

With E supplied and S enabled, `calculate_full_direction_state` executes:

1. Blue → A → S.
2. E initial detection.
3. Filter S eligibility against E; rebuild E if S count changes.
4. Resolve A validity against dominant stopped behaviors; derive invalid S identities and accepted/blocked Order context.
5. Rebuild E for “final audit” unconditionally.
6. Reconcile S against shared accepted Order-stop ledgers; rebuild E once if S changes.
7. Use suppressed S evidence to construct earlier E continuations and replace eligible descendant chains.

Thus normal E detection runs two to four times per requested direction, followed by possible continuation construction.

`finalize_direction_visibility` then:

- Removes A sources occupied by S and applies S-transition filtering.
- Calls `lifecycle_engine.reconcile_stopall_lifecycle`.
- Restores eligible independent S-owned E1 roots.
- Resolves lifecycle visibility and historical A/S parent closure.
- Applies requested source-index windows.
- Removes invalid A/S.
- Marks nonpublic Blue geometry.
- Applies the scoped internal Reset-leg Mode-B prohibition to E/StopAll.
- Merges and serializes accepted OrderAudit identities.

There is **no current E/StopAll fixed-point rerun loop**. `reconcile_stopall_lifecycle` calculates StopAll once from accepted S/E, stores `{source_time: number}` in `detector.sequence_resets`, and returns the existing E list.

Without E or with S disabled, the bridge uses its reduced path; E/StopAll/OrderAudit are empty. Blue and A are still computed as dependencies when downstream enabled stages need them.

3. Shared numerical and chronological semantics

`core_utils.as_decimal` preserves existing Decimal objects and otherwise uses `Decimal(str(value))`. There is no explicit Decimal precision/context configuration. JSON numeric literals first pass through `orjson`’s Python numeric conversion; exact original decimal lexemes are not preserved for ordinary JSON floating-point values. Decimal arithmetic is used after that normalization.

Timezone is `Asia/Tehran`. Epochs become naive Tehran-local datetimes; serialization attaches Tehran again and emits integer epoch seconds. Public prices are strings, timestamps/indexes are integers, absent metadata is null.

Market candle color is always `GREEN` for `Open <= Close`, otherwise `RED`; dojis are GREEN. `mirror_candle` deliberately swaps internal GREEN/RED roles, including doji’s internal role, while reflecting OHLC with exact `copy_negate`.

Most crossing predicates are strict: Bullish Low `<` boundary, Bearish High `>` boundary; Reaction confirmation is Bullish High `>` BoxTop or Bearish Low `<` BoxBottom. Equality does not stop or confirm.

`MarketChronology` owns `[start,end)` lower windows, confirmation/reset caches, main-index mapping and canonical Order stops. Confirmation defaults to Break candle open if no strict lower confirmation is found. A explicitly requests `use_intrabar_start=False`; S/E use intrabar start when available.

`LowerTimeframeIndex` is a shared min/max segment tree supporting first strict crossing and range extrema. Equal extrema retain earliest lower position. Module-level caches retain source sequences by identity for the process lifetime.

4. Reaction behavior and real directional differences

`reaction_engine.py` owns `Candle`, `Candidate`, `ResetEvent`, `DetectionResult`, `BullishDetector`, `BearishDetector`, `UnifiedReactionDetector`, `LowerTimeframeIndex`, `MarketChronology`, and internal-Reaction classification.

`BullishDetector.detect` supplies initial Mode-A/Leg-Start geometry: GREEN context → RED First, a frozen leg floor/anchor, BoxTop from the context/First maximum, evolving BoxBottom, strict High breakout. Once confirmed, Mode-B Normal search uses the running peak and a new RED First. Reset is a strict Low break of the previous confirmed bottom.

`BearishDetector` adapts that reference through lazy reflected candles/indexes. Its market semantics are RED context → GREEN First, frozen ceiling, strict Low breakdown, and High Reset. The production `UnifiedReactionDetector` then owns post-initial Normal and post-Reset behavior explicitly; it is not simply a reflected full-pipeline execution.

`_first_direct_same_direction_after_reset` searches the requested direction; opposite patterns do not unlock ordinary post-Reset discovery. `_build_direct_candidate` requires correct context/First colors and local floor/ceiling alignment, retains the whole Reset-to-First outer boundary, and `_scan_direct_candidate` rejects strict owner invalidation before confirmation. Invalidation wins an unresolved same-lower-candle tie.

Direct Order geometry differs from ordinary Reaction discovery: `_earliest_confirmed_geometry` allows overlapping candidates and selects the first main-candle confirmation, then earliest First for a tie. `first_order_reaction_after_gate` races outer-boundary restart against gate continuation; outer invalidation is checked first on a same-event tie.

`_append_reaction` stores the opposite edge from complete First..Break main candles. `published_reaction_candidate` clones display geometry and, when the Break candle owns that edge, truncates it at the first exact strict confirmation. Display geometry can therefore differ from calculation geometry.

Verified asymmetry: in `UnifiedReactionDetector.detect`, Bullish initial/post-Reset same-Break Reset uses `analysis.extreme`; Bearish uses the stored `box_top` in those branches. The ordinary Bearish branch refines before obtaining its Reset level. Both directions’ `_candidate_from_confirmation_remainder` reject reuse if the remainder crosses `analysis.extreme`. These are actual source paths; universal mirror correctness cannot be inferred.

5. Blue, A and S rules

`blue_line_detector.py:detect_blue_lines/count_scale_strikes`:

- Fibonacci ratio is exactly Decimal `0.618`.
- Bullish level: `top - .618*(top-reference)`; Bearish: `bottom + .618*(reference-bottom)`.
- Mode A uses its anchor/leg boundary and resets previous strike count; Mode B references the previous Reaction’s opposite box edge.
- New directional extremes create pending strikes; GREEN confirms Bullish strikes, RED confirms Bearish strikes. Pending final strikes may use lower chronology through the Break candle.
- A scale Blue requires a strictly larger count than the preceding Reaction and at least one intervening healthy Reaction after an earlier Blue.
- Scale drawing price is Low + range/3 Bullish, High − range/3 Bearish; Reset drawing price uses range/5.
- Draw span is source time ± one main timeframe.
- Same-index double-stop Reset Blues can be `calculation_valid=False`, but remain special A evidence.
- `mark_internal_blue_lines` uses owning internal Reaction or both semantic `source_extreme` and rendered `line_price` strictly inside a healthy Reaction. `public_blue_lines` removes invalid/internal lines.

`a_zone_detector.py:AZoneDetector`:

- Builds chronologically formed Blue states, uses source extreme as stop level.
- Scale stop scanning starts at exact Reaction confirmation; Reset Blue stop scanning starts after its full source candle.
- Adjacent Blue pairs expire at the next Blue formation.
- `_pair_trigger` handles inherited stop geometry, prior-stop-before-current-formation, and simultaneous stops.
- `_inherited_stop` can freeze the full stop-candle → aligned Break-candle directional extreme.
- `_a_source` freezes the directional extreme from trigger candle open through exact confirming Reaction event inclusive; later Break-candle prices do not move A.
- `_double_stop_a_candidates` handles invalid Reset Blue evidence. `_filter_special_a` resolves conflicts and consumed Blue pairs.
- Earliest extrema normally own equality. Same-event Blue stop ordering uses directional stop-level ordering. Ordinary cycles can reuse adjacent Blue provenance after A’s first strict stop under explicit conditions.

` s_zone_detector.py:SZoneDetector`:

- Audits stopped A independently before S decisions.
- `_first_order_after` chooses a canonical opposite Reaction with First at/after the A-stop containing main candle and confirmation strictly after A stop; rank is confirmation, First index, Break index.
- Simple pre-Order uses A-stop remainder through Order First; equality with Order First remains “after.”
- Advanced requires nested same-direction Reaction inside the opposite Order; it prevents Simple pre-Order chronology from stealing established nested ownership.
- Simple post-Order source spans Order Break through aligned Reaction Break inclusively.
- `_candidate_source_last` assigns equal extrema to the latest candle for Simple Blue and Type3 Reset-leg geometry; ordinary `_candidate_source` keeps earliest.
- `_decision`: Order stop first → Red; qualified candidate cross first → Blue. A same-finest-candle dual crossing yields no decision. Qualified Blue needs aligned Reset Blue or ordinary trend confirmation; the pre-Order branch may fall back to post-Order discovery.
- Type3 is Order-free Blue: active pre-A-stop opposite Reaction, subsequent opposite Reset, strict Break-to-Reset boundary cross, aligned trend confirmation, and completion before the next Order confirmation deadline.
- `_a_owned_by_s` implements handoff ownership plus fresh-trigger and fresh Reset/Reset pair exceptions.
- `reconcile_shared_order_stops` can change an existing S to Red using a later accepted physical Order that stops earlier than its old decision. S source stays frozen. An accepted S-parent-stop Order imposes the terminal shared-Order lifecycle boundary.

6. E, Order and StopAll lifecycle

`e_zone_detector.py:EZoneDetector` separates native chain discovery, reconciliation and accepted audit rebuilding.

Order creation paths are direct `parent-stop`, `reset-leg`, and `carried-live`. Physical identity is `(FirstIndex,BreakIndex)` and causes merge.

Mode-A Order stop is the complete anchor/context-through-Break directional outer extreme; Mode B inherits the previous healthy opposite Reaction edge (`MarketChronology.canonical_order_stop`).

Reset-leg Order_B requires actual opposite Reset context, inclusive Break-to-Reset boundary, strict boundary crossing, noninternal aligned trend evidence, first structurally owned opposite geometry, and an exact published opposite-Reaction identity. A trend Reset cannot release an opposite owner. Deadlines use the next nonnested outer Reset and current decision/stop bounds.

There are narrow direct Order_A exceptions for bounded `"continue"` geometry: S→E, and E after a newly confirmed noninternal trend leg. Noncanonical accepted geometry uses Reaction number 0. This does not relax Reset-leg canonicality.

`_zone` chooses one representative per direct/inherited/carried path, then earliest Order stop; ties favor later Order First. E source uses the complete main candles containing parent stop through Order stop, keeping earliest equal extrema. E chains terminate on no next Order/stop or repeated source index; no fixed numeric recursion depth is configured.

Reconciliation prioritizes accepted parent ownership and chronological lifecycle. Same physical E source keeps Red over Blue, then higher number within a family; exact rank ties retain existing provenance. Invalid S cannot open a competing cross-family root where that S source already has a native E continuation. `restore_independent_s_roots` restores eligible direct E1 roots after dominant StopAll arbitration, excluding S sources already owned by E.

`lifecycle_engine.py` priority is invariant across market direction:

`StopAll > E Red > S Red > E Blue > S Blue`.

A/S discovery remains possible within larger behaviors, but exact stopped-owner chronology and provenance determine subsequent eligibility. Historical parents may be restored for visible lineage; final same-source E/StopAll suppresses A/S labels. Internal geometry is not generally discarded: the public prohibition specifically targets internal Reset-leg Mode-B E/StopAll ownership. Audit merges causes first and rejects all-reset-leg internal Mode-B entries.

`StopAllDetector.detect` groups repeated dominant S color or repeated E `(family,number)`. At least two group members, strict group stop, and a qualifying subsequent E decision create StopAll1. A strict stop of existing active StopAll followed by a qualifying E produces highest stopped number + 1. Lower-priority distinct-source events remain output but do not split the dominant group. StopAll inherits the decisive E geometry/Order, and final public E is removed at that StopAll source.

7. Public serialization

`trading_pipeline.py:serialize*` is authoritative.

Envelope fields: `engine`, `version`, `pipelineVersion`, `blueLineVersion`, `aVersion`, `sVersion`, `eVersion`, `stopAllVersion`, enable booleans, `timeframe`, `actualFrom`, `actualTo`, `directions`, and `timings.{phasesMs,bridgeTotalMs}`.

Each direction always contains `reactions`, `resets`, `blueLines`, `aZones`, `sZones`, `eZones`, `stopAlls`, `orderAudit`.

- Reaction: First/Break indexes and times; BoxTop/Bottom prices and source indexes/times; `mode`.
- Reset: `index,time,secondTime,brokenLevel,fromFirstIndex`.
- Blue: direction/kind, Reaction number, previous/current strike count, Fibonacci level, source index/time/extreme, broken level, line price/start/end.
- A: direction, both Blue ordinals/source/stop times and stop levels, continuation level/source, trigger index/time/event, Reaction number/First/Break time, source index/time/price, `calculationValid:true`.
- S: direction/color/formationType, A identity/price/stop chronology, complete Order direction/number/mode/First/Break/confirmation/box/stop provenance, Reset Reaction/time, source/price and decision chronology, `calculationValid:true`. Type3 Order fields are null.
- E: direction/family/number, parent identity/price/stop chronology, complete Order geometry/stop provenance plus cause fields, source/price and decision chronology.
- StopAll: direction/number/source/price/decision, gate type/event, stopped behavior type/key/count, underlying E family/number, complete Order provenance, nullable own stop fields.
- OrderAudit: Order direction/Reaction number/mode/geometry, stop level/source/hit indexes and times, and merged causes. Parent-stop causes carry parent type/family/event/source; Reset-leg causes carry Reset and boundary-break times.

Private fields such as `behavior_internal`, anchors, `order_gate_decision` and native invalid state are not generally public.

8. Confirmed defects and risks

- **Reproduced package import failure:** `engine/pipeline/__init__.py` imports/export `run_blue_line`, absent from `blue_line_detector.py`. Even after adding the flat pipeline import path, `import engine.pipeline` raises `ImportError`. Production dynamic loading bypasses this package entry point.
- **Cache coverage gap:** `apps/chart/vite.config.js:calculationSources` fingerprints bridge plus six main engines but omits `direction_policy.py` and `core_utils.py`. Changes to those calculation dependencies can reuse stale cache.
- **Sparse-data risk:** `reaction_engine.DetectorBase.__init__` infers timeframe from the first two main timestamps; `MarketChronology` uses the requested timeframe. Missing early buckets can make Reaction windows differ from downstream windows. One main candle defaults Reaction’s interval to one second regardless of requested timeframe.
- **Mapping inconsistency:** `lifecycle_engine.visible_a_zones_after_s_stops` uses `bisect_left(times, decision_event_time)`, which maps intrabar events to the next candle, despite its containing-stop-candle description. It also uses S decision rather than a separately calculated S strict stop. This needs a focused fixture to establish intended behavior.
- **StopAll reset-map propagation risk:** `reconcile_stopall_lifecycle` changes `sequence_resets` after E detection but does not update `_sequence_reset_times` or rebuild accepted audit. Comments promise downstream audit semantics; the implementation does not fully refresh that derived state.
- **Unequal internal filtering:** public E/StopAll filtering rejects an internal Mode-B with Reset-leg provenance even if another cause exists; OrderAudit rejects only when all merged causes are Reset-leg. Mixed-cause cases can differ between ledger and public behavior.
- **No universal missing-data rejection:** A/S sometimes fall back to main candles only when the lower window is completely empty; partially missing lower data is trusted. E/StopAll mostly return no event when lower chronology cannot establish a crossing. Confirmation falls back to Break open. These paths do not constitute evidence of complete chronology.
- **No fixed bar lookback:** searches generally run to actual lifecycle boundaries or full RAW end. A short display range does not reduce calculation work.

9. Performance and documentation

Static hotspots are full-file bytes/JSON/bucket/Candle allocation; both Reaction directions; nested post-Reset/direct-geometry scans; cross-direction internal-Reaction containment; repeated A/S/E scans; two-to-four E detector passes; recursive candidate chains and lineage reconciliation. Segment indexes, reflected-view caching and confirmation caches mitigate repeated work. No fresh timings were measured.

`UnifiedReactionDetector._geometry_after_reset_cache` is checked but its current helper never populates it; several E caches use `.get(...) is not None`, so cached misses are recomputed. Module-level source-retaining caches are appropriate to fresh subprocess execution but would accumulate in a long-lived embedding.

The root references `engine/TradingBot_{Bullish,Bearish}_Algorithm_Reference.md` contain recent amendments covering full-RAW context and single-pass StopAll, but still retain contradictory older fixed-point/range-isolation sections. Their latest version list says A `1.6.2`, while current source is `1.6.3`.

`engine/algorithms/TradingBot_{Bullish,Bearish}_Algorithm_Reference_V4.0.1.md` freezes substantially older versions: Reaction `9.4.4`, Blue `2.2.1`, A `1.4.2`, S `4.5.1`, E `6.3.1`, lifecycle `1.3.1`, unversioned bridge. It describes removed helpers (`isolate_raw_range`, `build_native_raw_candles`), isolated-range indexes, preserved duplicate RAW rows, and “Doji GREEN in every adapter.” These differ from current whole-file calculation, consecutive-timestamp aggregation and internal role-swapping. Those documents are historical snapshots, not an accurate standalone specification of today’s runtime.

The working tree has deleted legacy engine filenames and untracked replacement engine files. The audit covers the current files, not the committed historical implementation.
