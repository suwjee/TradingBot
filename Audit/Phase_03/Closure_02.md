# Phase 03 — Foundational contract handoff (checkpoint 02)

Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`; prior algorithm head `aa34054669ef077d779871ad6185b38609c0469c`. User confirms main is frozen until further notice. The branch remains read-only for main, documentation-only for algorithm. Resolve main again at phase entry as a consistency check, not as authorization to change it.

**Status: FOUNDATIONAL CONTRACT HANDOFF COMPLETE; full function-level semantic coverage remains open.** Phase 03 establishes the shared contracts and complete declared record interface inventory, not an exhaustive semantic proof of every module-specific branch or dynamically assigned field. Checkpoint 01 is immutable and retained separately.

## Deliverables and gates

| Foundation gate | Evidence / result |
|---|---|
| Numerical representation, Decimal contexts and shared arithmetic | [N01–N06](../../Specification/02_Numerical_Precision.md); add Scale/Reset drawing formulas; active context is external |
| Direction, candles and time | [direction](../../Specification/06_Direction_Policy.md), [C01–C06](../../Specification/07_Candles_And_Market_Input.md), [T01–T05](../../Specification/03_Chronology_And_Time_Model.md) |
| Shared indexes and core utilities | [I01–I05](../../Specification/08_Range_Indexes_And_Caches.md), [utilities](../../Specification/05_Core_Utilities.md) |
| Identity, provenance and ownership | [P01–P06](../../Specification/09_Identity_Ownership_And_Visibility.md) |
| Boundary, tie, null and failure conventions | [B01–B04](../../Specification/10_Boundary_Tie_And_Error_Contracts.md) |
| Cache contracts and continuation dependencies | [K01–K08](../../Specification/11_Module_Cache_Contracts.md), source-located screen |
| Declared record interface coverage | [catalog](../../Contracts/Declared_Record_Schemas.md), 46 records, 438/438 declared fields |
| Source provenance | [Schema evidence 01](Schema_Evidence_01.json), [02](Schema_Evidence_02.json), [validation](Validation.json), checkpoint 01 |
| Runtime equivalence / RAW / benchmark | OUT OF SCOPE |

## Source mapping for added foundational rules

All locations refer to immutable main. Refer to [checkpoint 01](README.md) for original N/T/C/I mapping.

| Rule | Source anchors |
|---|---|
| P01, P02 | core_utils.py:59–66; reaction_engine.py:1371–1551; blue_line_detector.py:514–590; trading_pipeline.py:3260–3294 |
| P03 | order_audit_engine.py:25–37, 1100–1201, 2290–2443; trading_pipeline.py:3038–3064 |
| P04 | lifecycle_engine.py:28–40, 95–140, 710–740, 1100–1140, 1500–1600; e_zone_detector.py:874–914 |
| P05 | PL_PH_detector.py:128–192; trading_pipeline.py:3260–3294 |
| P06 | true_false.py:130–164; trading_pipeline.py:3469–3497 |
| B01/B02 | direction_policy.py:31–54; reaction_engine.py:203–229, 1371–1406; a_zone_detector.py:131–215; s_zone_detector.py:279–312, 600–626, 687–738, 873–984; blue_line_detector.py:92–142; e_zone_detector.py:580–667; order_audit_engine.py:1088–1097, 1887, 2410–2443; PL_PH_detector.py:224–246, 530–572 |
| B03/B04 | source declarations, prior N/T/C/I mappings; lifecycle_engine.py:736–748; order_audit_engine.py:818–827, 2359–2410; live_pipeline.py:22–86, 114–158; PL_PH_detector.py:800–850 |
| K01 | reaction_engine.py:1488–1615, 1620–1675, 1990–2135 |
| K02 | blue_line_detector.py:325–514 |
| K03 | a_zone_detector.py:852–1095 |
| K04 | s_zone_detector.py:116–180, 1418–1526 |
| K05 | e_zone_detector.py:103–310, 368–425, 440–503, 536–560 |
| K06 | order_audit_engine.py:386–444, 559–694, 810–827, 980–1015, 1069, 1100–1142, 1373, 1458–1476, 1500–1575, 1644–1750, 1800–2011, 2542–2620 |
| K07 | lifecycle_engine.py:535–586; PL_PH_detector.py:321, 449–487, 750–772, 800–850 |
| K08 | trading_pipeline.py:100–138, 213–365, 1755–1777, 3671–3685; live_pipeline.py:22–70, 90–158 |
| Additional Blue formulas | blue_line_detector.py:240–252, 280–290 |

Paths without prefix in this map are under engine/pipeline except trading_pipeline.py and live_pipeline.py (engine/bridge). The exact blob and field line are recorded in schema evidence. These are source provenance only; specification uses no source dependency.

## Record declaration validation

16/16 pinned module blob identities matched Phase 02, 85/85 classes recorded, 46 dataclass records (32 frozen), 438/438 annotated fields. Of these 358 required, 80 defaulted, 117 explicitly nullable by annotation, 14 keyword-only default fields, 17 fresh-container factories. Nullable and defaulted counts overlap. Field presence and default presence checked against prior AST inventory. The cache lexical screen contains 247 line records and is intentionally incomplete as semantic analysis. No new AST compile or runtime tests.

## Handoff limitations

The foundational phase is accepted for its interface/primitive scope, not full semantic coverage of every cache attribute, per-function arithmetic and exception path, dynamic receiver binding, constructor-assigned state, dictionary payload, exact serializer field, or lifecycle/chronology rule. Those remain required in Phases 04–11, with bidirectional source traceability. The 596 earlier name-only candidates remain unresolved at exact binding level. Do not claim algorithm reconstruction without errors until the full source-to-spec audit; even then static coverage cannot prove all-input runtime equivalence. No production or RAW modifications, no execution, no benchmark.
