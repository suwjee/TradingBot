# CP333 — W2 historical dependency matrix

Pinned production baseline: `c99b4c957e932d9ee70c492ca03ce80711447fc1`. This bounded reconciliation does not accept W2 or resolve F05. Existing 316 transition records, 20 direct chronology accessors and 125 CP332 selected sites remain independent inventories.

## Historical dependency reconciliation

### CP333-M01 — CP321-D01

Package and configured loader are source-established; imported runtime objects/environment remain conditional. No synthetic transition counted for empty package.

Source: `engine/__init__.py:1–1`; `engine/bridge/__init__.py:1–1`; `engine/pipeline/__init__.py:1–26`; `engine/bridge/trading_pipeline.py:25–40`; `engine/bridge/trading_pipeline.py:87–98`; `engine/bridge/trading_pipeline.py:1974–2009`.

Active specifications: [16_W2_Live_Market_Entry_Transport_Reconciliation.md](16_W2_Live_Market_Entry_Transport_Reconciliation.md)

### CP333-M02 — CP321-D02

Strict-start/inclusive-end query does not prove price containment; caller Reaction/Blue predicates and fallback determine eligibility.

Source: `engine/pipeline/core_utils.py:18–45`; `engine/pipeline/reaction_engine.py:1371–1478`; `engine/pipeline/blue_line_detector.py:526–590`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M03 — CP321-D03

Decimal conversion preserves Decimal input; a physical pair neither proves event order nor creation ownership. Typed cache may distinguish equal values of different types.

Source: `engine/pipeline/core_utils.py:48–62`; `engine/bridge/trading_pipeline.py:271–271`; `engine/bridge/trading_pipeline.py:721–735`; `engine/bridge/trading_pipeline.py:786–791`; `engine/bridge/trading_pipeline.py:814–819`; `engine/bridge/trading_pipeline.py:1611–1676`; `engine/bridge/trading_pipeline.py:3075–3075`; `engine/bridge/trading_pipeline.py:3452–3452`.

Active specifications: [11_W2_Order_Ledger_Reconciliation.md](11_W2_Order_Ledger_Reconciliation.md); [16_W2_Live_Market_Entry_Transport_Reconciliation.md](16_W2_Live_Market_Entry_Transport_Reconciliation.md); [15_W2_Projection_Serialization_TF_Reconciliation.md](15_W2_Projection_Serialization_TF_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [14_W2_Primary_Reversal_Reconciliation.md](14_W2_Primary_Reversal_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M04 — CP321-D04

Direction-policy selection differs from reflected structural role. T/F normalization uses the sign copy, not a change of physical index.

Source: `engine/pipeline/direction_policy.py:19–68`; `engine/pipeline/true_false.py:18–28`; `engine/pipeline/true_false.py:58–90`; `engine/pipeline/true_false.py:41–90`.

Active specifications: [15_W2_Projection_Serialization_TF_Reconciliation.md](15_W2_Projection_Serialization_TF_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M05 — CP321-D05

Prepared sequence identity is object identity; windows translate/clamp search and validate extrema bounds, not arbitrary equality-based cache reuse.

Source: `engine/pipeline/reaction_engine.py:1077–1092`; `engine/bridge/trading_pipeline.py:1788–1857`; `engine/bridge/trading_pipeline.py:2055–2078`.

Active specifications: [16_W2_Live_Market_Entry_Transport_Reconciliation.md](16_W2_Live_Market_Entry_Transport_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M06 — CP321-D06

Native confirmation open fallback is distinct from exact timestamp proof. Duplicate lower timestamps can prove a fallback timestamp only if a strict crossing is present; no replacement event search.

Source: `engine/pipeline/reaction_engine.py:959–1074`; `engine/pipeline/reaction_engine.py:1153–1299`; `engine/bridge/trading_pipeline.py:702–783`; `engine/pipeline/reaction_engine.py:1300–1302`.

Active specifications: [15_W2_Projection_Serialization_TF_Reconciliation.md](15_W2_Projection_Serialization_TF_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M07 — CP321-D07

Observed nonempty lower path is not a gap-free proof; indexed and linear containment use separate eligibility conditions; original geometry objects retain owner annotations.

Source: `engine/pipeline/reaction_engine.py:1370–1480`; `engine/bridge/trading_pipeline.py:2648–2739`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M08 — CP321-D08

Committed Reaction continuation and preview are conditional services; active live worker calls prepare_pipeline_state without passing optional live stages.

Source: `engine/pipeline/reaction_engine.py:2784–2907`; `engine/bridge/trading_pipeline.py:2648–2802`; `engine/bridge/trading_pipeline.py:3738–3753`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M09 — CP321-D09

Blue ordinal/frozen first pass retained even across feedback; owner-local dirty rewind cannot be treated as proof of composed incremental equivalence.

Source: `engine/pipeline/blue_line_detector.py:447–516`; `engine/bridge/trading_pipeline.py:2211–2266`; `engine/bridge/trading_pipeline.py:2272–2279`; `engine/bridge/trading_pipeline.py:2569–2645`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md)

### CP333-M10 — CP321-D10

Full Blue ordinal map precedes public filtering; same interior requires both semantic and rendered prices; no promotion from visibility.

Source: `engine/pipeline/blue_line_detector.py:517–590`; `engine/bridge/trading_pipeline.py:3020–3110`; `engine/bridge/trading_pipeline.py:1170–1179`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [15_W2_Projection_Serialization_TF_Reconciliation.md](15_W2_Projection_Serialization_TF_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M11 — CP321-D11

A false flag starts scanning at Break open, not necessarily event at open; bisection requires ordered eligible datetimes, otherwise original sequence fallback.

Source: `engine/pipeline/a_zone_detector.py:69–109`; `engine/pipeline/a_zone_detector.py:497–531`; `engine/bridge/trading_pipeline.py:1182–1269`; `engine/bridge/trading_pipeline.py:2211–2266`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [15_W2_Projection_Serialization_TF_Reconciliation.md](15_W2_Projection_Serialization_TF_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M12 — CP321-D12

First-stop cycle excludes recross as a new first stop; dirty reuse is local; S eligibility/lifecycle invalidation differs from display suppression.

Source: `engine/pipeline/a_zone_detector.py:798–837`; `engine/pipeline/a_zone_detector.py:868–1070`; `engine/bridge/trading_pipeline.py:2270–2406`; `engine/bridge/trading_pipeline.py:2897–2922`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M13 — CP321-D13

S uses full native lists, shared chronology and initial geometry service; A sorting and native reaction ordering differ from display order.

Source: `engine/pipeline/s_zone_detector.py:67–164`; `engine/bridge/trading_pipeline.py:2211–2266`; `engine/bridge/trading_pipeline.py:2648–2802`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M14 — CP321-D14

S uses default confirmation flag distinct from A false flag. Main fallback only empty lower rows; equal next confirmation blocks ownership.

Source: `engine/pipeline/s_zone_detector.py:186–257`; `engine/pipeline/s_zone_detector.py:1248–1300`; `engine/bridge/trading_pipeline.py:1182–1269`; `engine/bridge/trading_pipeline.py:2270–2406`; `engine/pipeline/order_audit_engine.py:2546–2600`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [10_W2_S_Decision_Reconciliation.md](10_W2_S_Decision_Reconciliation.md); [15_W2_Projection_Serialization_TF_Reconciliation.md](15_W2_Projection_Serialization_TF_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M15 — CP321-D15

Exact shared stop must be after confirmation; source_time equality is accepted, decision equality rejected. Revisions preserve physical geometry and creation causes.

Source: `engine/pipeline/s_zone_detector.py:1301–1423`; `engine/bridge/trading_pipeline.py:2153–2210`; `engine/bridge/trading_pipeline.py:2569–2645`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [10_W2_S_Decision_Reconciliation.md](10_W2_S_Decision_Reconciliation.md)

### CP333-M16 — CP321-D16

Recomputed dependency symmetric difference can move dirty frontier earlier; retained through<dirty; ownership pass still runs.

Source: `engine/pipeline/s_zone_detector.py:1433–1527`; `engine/bridge/trading_pipeline.py:2211–2266`.

Active specifications: [10_W2_S_Decision_Reconciliation.md](10_W2_S_Decision_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md)

### CP333-M17 — CP321-D17

Dominant post-stop owner and later anchor are distinct; endpoints and exact reset crossing rules are not inferred from main geometry.

Source: `engine/pipeline/order_audit_engine.py:77–169`; `engine/pipeline/order_audit_engine.py:442–529`; `engine/bridge/trading_pipeline.py:2569–2645`.

Active specifications: [11_W2_Order_Ledger_Reconciliation.md](11_W2_Order_Ledger_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M18 — CP321-D18

Feedback identity omits some fields (including post_stop.behavior_source_time); sorted tuple equality is implemented convergence criterion, not full object equality. Eight passes maximum; repeated new identity fails; restoration reindexes preserved entries.

Source: `engine/pipeline/order_audit_engine.py:530–552`; `engine/pipeline/order_audit_engine.py:1135–1200`; `engine/bridge/trading_pipeline.py:2569–2645`; `engine/pipeline/order_audit_engine.py:2249–2288`.

Active specifications: [11_W2_Order_Ledger_Reconciliation.md](11_W2_Order_Ledger_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md)

### CP333-M19 — CP321-D19

Accepted A filter is provenance filter; restoration separately drops invalid S-only causes, preserves surviving canonical identities, reindexes and invalidates caches. Required identity bypasses range, not cause eligibility; absent stop_cross differs from explicit null.

Source: `engine/pipeline/order_audit_engine.py:2249–2290`; `engine/pipeline/order_audit_engine.py:2361–2505`; `engine/bridge/trading_pipeline.py:2408–2566`; `engine/bridge/trading_pipeline.py:3050–3109`; `engine/bridge/trading_pipeline.py:1611–1676`.

Active specifications: [11_W2_Order_Ledger_Reconciliation.md](11_W2_Order_Ledger_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [15_W2_Projection_Serialization_TF_Reconciliation.md](15_W2_Projection_Serialization_TF_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M20 — CP321-D20

Independent stopped-A initial confirmation > stop; canonical remap recomputes without rechecking. S/E direct parent-stop uses main gate and optional confirmation_after; distinct route (CP332 correction).

Source: `engine/pipeline/order_audit_engine.py:2520–2600`; `engine/bridge/trading_pipeline.py:2648–2739`; `engine/bridge/trading_pipeline.py:2153–2210`; `engine/pipeline/order_audit_engine.py:829–918`; `engine/pipeline/order_audit_engine.py:982–1068`.

Active specifications: [10_W2_S_Decision_Reconciliation.md](10_W2_S_Decision_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [11_W2_Order_Ledger_Reconciliation.md](11_W2_Order_Ledger_Reconciliation.md); [03_Order_E.md](03_Order_E.md)

### CP333-M21 — CP321-D21

Exact main index identity and available bound method required for shared extrema; non-live else sparse; one-second lower fallback; direct finder optional.

Source: `engine/pipeline/e_zone_detector.py:312–393`; `engine/bridge/trading_pipeline.py:2153–2210`; `engine/bridge/trading_pipeline.py:1826–1857`; `engine/bridge/trading_pipeline.py:2055–2078`.

Active specifications: [12_W2_E_Reconciliation.md](12_W2_E_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [16_W2_Live_Market_Entry_Transport_Reconciliation.md](16_W2_Live_Market_Entry_Transport_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M22 — CP321-D22

Strict parent/order lower stops separate from source extreme across full main endpoint candles. Retention uses settled event bounds, not blanket source-time proof.

Source: `engine/pipeline/e_zone_detector.py:153–219`; `engine/pipeline/e_zone_detector.py:458–579`; `engine/bridge/trading_pipeline.py:988–1006`; `engine/bridge/trading_pipeline.py:2408–2566`.

Active specifications: [12_W2_E_Reconciliation.md](12_W2_E_Reconciliation.md); [15_W2_Projection_Serialization_TF_Reconciliation.md](15_W2_Projection_Serialization_TF_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M23 — CP321-D23

Same-parent root replaces earliest incumbent without testing earlier new decision; physical ownership prevents disowned parent reuse; restoration followed by ledger ensure.

Source: `engine/pipeline/e_zone_detector.py:915–1006`; `engine/bridge/trading_pipeline.py:2569–2645`.

Active specifications: [12_W2_E_Reconciliation.md](12_W2_E_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md)

### CP333-M24 — CP321-D24

Reconciliation source-index grouping, family priority and event order remain distinct; native hard reset and accepted-ledger rebuilding occur before downstream projection.

Source: `engine/pipeline/e_zone_detector.py:1132–1203`; `engine/pipeline/e_zone_detector.py:1372–1456`; `engine/pipeline/e_zone_detector.py:1495–1507`; `engine/bridge/trading_pipeline.py:2211–2566`.

Active specifications: [12_W2_E_Reconciliation.md](12_W2_E_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M25 — CP321-D25

Donor is E, not A-zone. Owner strict stop before boundary, or E donor source-bucket/parent provenance exception; one pass freezes StopAll then assigns E reset map, no retroactive rebuild.

Source: `engine/pipeline/lifecycle_engine.py:121–142`; `engine/pipeline/lifecycle_engine.py:356–420`; `engine/pipeline/lifecycle_engine.py:1377–1411`; `engine/bridge/trading_pipeline.py:2569–2645`; `engine/pipeline/e_zone_detector.py:395–412`.

Active specifications: [13_W2_Lifecycle_StopAll_Reconciliation.md](13_W2_Lifecycle_StopAll_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [12_W2_E_Reconciliation.md](12_W2_E_Reconciliation.md)

### CP333-M26 — CP321-D26

Optional StopAll finder retains earlier proven stops only under dirty-frontier/changed-event guards; active public dispatch does not establish that optional service is used.

Source: `engine/pipeline/lifecycle_engine.py:534–592`; `engine/bridge/trading_pipeline.py:2606–2611`.

Active specifications: [13_W2_Lifecycle_StopAll_Reconciliation.md](13_W2_Lifecycle_StopAll_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md)

### CP333-M27 — CP321-D27

Accepted A removes provisional First blocks; E exception exact stop plus First and confirmation relation; module priority and explicit stop/tuple-last callback rules distinct.

Source: `engine/pipeline/lifecycle_engine.py:606–694`; `engine/pipeline/lifecycle_engine.py:712–765`; `engine/bridge/trading_pipeline.py:2408–2445`.

Active specifications: [11_W2_Order_Ledger_Reconciliation.md](11_W2_Order_Ledger_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M28 — CP321-D28

Latest stopped main vs exact event ranks must not be conflated. Consumed suppressed S uses strict Close-boundary evidence and earlier candidate order; physical accepted-A ownership retained.

Source: `engine/pipeline/lifecycle_engine.py:766–972`; `engine/pipeline/lifecycle_engine.py:996–1137`; `engine/bridge/trading_pipeline.py:2270–2406`; `engine/bridge/trading_pipeline.py:2491–2540`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [13_W2_Lifecycle_StopAll_Reconciliation.md](13_W2_Lifecycle_StopAll_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M29 — CP321-D29

Internal behavior filter currently copies arrays; visibility restores referenced lineage and clips later; accepted calculation causes kept separately for audit, not promoted by visibility.

Source: `engine/pipeline/lifecycle_engine.py:1496–1603`; `engine/bridge/trading_pipeline.py:2939–3110`; `engine/pipeline/order_audit_engine.py:2361–2505`.

Active specifications: [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [11_W2_Order_Ledger_Reconciliation.md](11_W2_Order_Ledger_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M30 — CP321-D30

Physical primary identity source differs from role winner; confirmed point needed for MBL and public StopAll removal through horizon; seed source order differs from exact activation time.

Source: `engine/pipeline/PL_PH_detector.py:73–239`; `engine/pipeline/PL_PH_detector.py:248–349`; `engine/bridge/trading_pipeline.py:3405–3460`.

Active specifications: [14_W2_Primary_Reversal_Reconciliation.md](14_W2_Primary_Reversal_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M31 — CP321-D31

Primary gate inclusive vs secondary strict/canonical; stop strictly after max confirmation/event. Global transition wins tie, activation precedes point ties; confirmed primary callback alone mutates native ledger and invalidates proposals; no PL4.

Source: `engine/pipeline/PL_PH_detector.py:350–385`; `engine/pipeline/PL_PH_detector.py:583–622`; `engine/pipeline/PL_PH_detector.py:624–682`; `engine/bridge/trading_pipeline.py:3405–3460`; `engine/pipeline/PL_PH_detector.py:386–433`.

Active specifications: [14_W2_Primary_Reversal_Reconciliation.md](14_W2_Primary_Reversal_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md)

### CP333-M32 — CP321-D32

Mirror price sign and role swap retain time/index and family. Dirty rewind to containing main candle; independent reversal prefix is proved, cache optional; released segment indexes and output offsets are distinct.

Source: `engine/pipeline/PL_PH_detector.py:683–742`; `engine/pipeline/PL_PH_detector.py:770–839`; `engine/bridge/trading_pipeline.py:3405–3460`; `engine/bridge/trading_pipeline.py:3502–3632`; `engine/bridge/trading_pipeline.py:3738–3767`.

Active specifications: [14_W2_Primary_Reversal_Reconciliation.md](14_W2_Primary_Reversal_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

### CP333-M33 — CP321-D33

Confirmed number3 reversal strict crossing tie uses source index/cycle ID. Visible end controls final labels/StopAll ownership; required audit identities retained. Primary dispatch chosen direction and configured owners only.

Source: `engine/pipeline/PL_PH_detector.py:73–146`; `engine/pipeline/PL_PH_detector.py:147–209`; `engine/bridge/trading_pipeline.py:3405–3501`; `engine/bridge/trading_pipeline.py:3680–3690`.

Active specifications: [14_W2_Primary_Reversal_Reconciliation.md](14_W2_Primary_Reversal_Reconciliation.md); [09_W2_Reaction_Blue_A_Reconciliation.md](09_W2_Reaction_Blue_A_Reconciliation.md); [15_W2_Projection_Serialization_TF_Reconciliation.md](15_W2_Projection_Serialization_TF_Reconciliation.md); [17_W2_Provider_Consumer_Supplement.md](17_W2_Provider_Consumer_Supplement.md)

## Additional bounded handoffs

### CP333-X01 — Serialized output to T/F per segment

Reversal output replaces direction groups only if transition index<=market.end_index. Apply T/F to each calculationSegments entry or group itself, not both. Final sourceTime winner priority directional primary, StopAll, E, S using first valid occurrence. Clears previous verdict metadata even for invalid candidates; no native geometry mutation.

Source: `engine/bridge/trading_pipeline.py:3644–3703`; `engine/pipeline/true_false.py:162–188`.

### CP333-X02 — T/F repair and open confirmation cutoff

Repair through selected main open + timeframe -1 second; inclusive lower search end, inclusive start; strict own-direction crossing with Decimal level. StopAll closure uses decisionTime + timeframe <= min(epoch(through)+1,last lower timestamp epoch+raw_timeframe). Repeated prefix relabel only on closure callback or absent callback; distinct Basic repeat/verdict/base counters.

Source: `engine/bridge/trading_pipeline.py:3691–3703`; `engine/pipeline/true_false.py:18–30`; `engine/pipeline/true_false.py:41–90`; `engine/pipeline/true_false.py:110–159`.

### CP333-X03 — Live lineage to active replay

Selected precision must match original slice; catch-up then strictly increasing appended times. Prefix hash/delta proof checked before pipeline append; lineage updates after success. Delta mismatch or raw digest mismatch emits retry errors without advancing; RAW change terminates. Active worker replays all trading stages without optional live= argument, using conditional retained market views and staged closed-regime cache.

Source: `engine/bridge/live_pipeline.py:92–156`; `engine/bridge/live_pipeline.py:168–226`; `engine/bridge/trading_pipeline.py:3738–3767`.

### CP333-X04 — Live scope and public output boundary

Public main loads engines and executes market context + pipeline + response in calculation scope, encodes only after leaving it; worker emits separate progress and seed/update messages. No implicit live continuation argument in either active pipeline call; protocol availability is not evidence of active use. Exceptions produce error payload and nonzero status.

Source: `engine/bridge/trading_pipeline.py:3738–3767`; `engine/bridge/trading_pipeline.py:3770–3810`; `engine/bridge/live_pipeline.py:159–226`.

## Acceptance boundary

33/33 prior dependency contracts have dispositions; 4 additional handoff contracts rechecked. The matrix overlaps 131/316 prior transition IDs and 11/20 accessor IDs. These are traceability intersections, not a semantic acceptance count. 185 transition IDs not intersected by this matrix are explicitly queued; they have prior bounded review evidence and are not presumed defects. Uncovered line intervals are candidates for review, not proven gaps. The remaining cross-owner source/specification reconciliation and conditional dispatch review must precede W2 acceptance. No runtime, RAW payload, ZIP or production changes.

[Matrix and remaining review queue](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP333_W2_Dependency_Matrix.json).
