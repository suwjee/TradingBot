# CP345 — Historical-linked Live, response and T/F semantic recheck

Scoped source-only review: 19/131 linked records; 185/185 queue records preserved; W2 not accepted.

## CP323-P29 — TB runner / LV-M04

Retained views only select staged closed_regimes callback when views nonnull and bucket_delta asserted. Common runner creates calculation scope, prepares market, optionally reports ready, calls prepare_pipeline_state without live=, builds response with closed resolver. CLI separately loads engines and prepares market/state without live stages.

Callback availability is not active incremental trading dispatch; independent cache and view/bucket owners distinct; scope cleanup may fail and propagate.

Matrix: CP333-M08, CP333-M32, CP333-X03, CP333-X04. Source: engine/bridge/trading_pipeline.py:3740–3786.

## CP329-S33 — Response envelope / TF-M01

E-enabled requires E nonnull and S enabled; StopAll also requires explicit lifecycle path. eVersion uses truthiness, not same exact guard. Output actualFrom/To selected main times; versions and flags separate. Each state direction calls build_direction_output; no native reformation in envelope.

Version field availability does not prove enabled stage. Direction outputs are inputs to later reversal replacement and annotations.

Matrix: CP333-X01. Source: engine/bridge/trading_pipeline.py:3633–3679.

## CP329-S34 — CH45 / TF-M02

Transition <= end triggers replacement using state.live_stages and closed resolver; choose max tuple of segment start(default -1) and direction with lexical tie. If calculationSegments present (including empty), iterate it, otherwise group singleton. Repair through=end main+TF−1s; closed=min(epoch(through)+1,epoch(last lower)+raw_timeframe default 1). Confirmation closure exact <=. Round only telemetry values.

No T/F aggregation across segments, no lower bound for repair beyond start supplied. StopAll closure distinct from native strict stop and display horizon.

Matrix: CP333-M33, CP333-X01, CP333-X02. Source: engine/bridge/trading_pipeline.py:3680–3710.

## CP329-S35 — TF01–02 / CH41

Fixed right bisect_right through, left bisect_left converted start with hi=right, policy resolves exact bullish/bearish, bound strict lower index search and Decimal(level), position zero valid, return epoch or null.

Native first_less excludes >=level, first_greater excludes <=level; clamp bounds and retained settled history as applicable. Native Bridge converters Tehran-naive/epoch caches, not generic timezone inference. No fallback or runtime dispatch proof.

Matrix: CP333-M04, CP333-X02. Source: engine/pipeline/true_false.py:18–30.

## CP329-S36 — TF03/08

Rank tuple S priority/color then zero; non-S key treated E priority/family and number. Descending ranks strictly smaller than current, bisect_left on increasing transformed price, return preceding verdict if nonzero position; equality excluded.

Price reference frontier and repeat map independent; lifecycle priority owner and direction policy are separate from physical formation.

Matrix: CP333-M04, CP333-X02. Source: engine/pipeline/true_false.py:33–55.

## CP329-S37 — TF04/05 / CH42

Fresh repeat and reference maps. Repair only if callback nonnull AND key absent, store nonnull result. Boundary clears references, sets started false, resets verdict/base counters but preserves repair count/latest. S starts, E skipped before S. Normalize low direction via Decimal.copy_negate; lower-rank base>=2 yields engulf, verdict>=2 independently display_restart. S/engulf T else invert crossed reference, absent odd F/even T.

Source time orders selected published rows, not exact decision chronology. Callback failures propagate; no rollback of previously modified rows.

Matrix: CP333-M04, CP333-X02. Source: engine/pipeline/true_false.py:58–100.

## CP329-S38 — TF04

Write verdict, discard frontier tail >=price then append. Pop lower repeats, repair singleton F from current source time; keep their price references. Same-rank equal verdict adds repair count and unless display_restart adds display count, marks prior/current at >=2. Same F removes earlier repair if >=current source, then repairs current. Base count increments for any existing rank.

Three counts distinct; no final sweep or native geometry mutation; prior repeated flags survive recurrence.

Matrix: CP333-X02. Source: engine/pipeline/true_false.py:101–128.

## CP329-S39 — TF06 / CH43

New series when group_start None or number<=previous; prior end and max tracked; clear prefix; else pending restart sets verdict origin. T for even offset. Prefix accumulates if number<=max; callback evaluated only on immediate/largest prior boundary. Absent or truthy qualifies retrospective prefix parity/repeated and sets restart.

Closed-horizon callback is Bridge-owned. No native StopAll change; callback exceptions may leave partial annotations.

Matrix: CP333-X02. Source: engine/pipeline/true_false.py:131–159.

## CP329-S40 — TF07 / CH44

Directional primary then StopAll/E/S, remove three annotation keys even invalid/donor rows, only exact False excluded, first sourceTime wins. Sort, null default, primary flushes StopAll and labels 1 T 2/3 F; Basic sees full stream including reset boundaries, then trailing StopAll.

A/Blue/secondary not visited; aliasing remains observable, no rollback. Selection by published sourceTime not physical ledger identity.

Matrix: CP333-X01. Source: engine/pipeline/true_false.py:162–188.

## CP330-S23 — CLI result boundary

Calculation completes before completion progress; compact json.dumps, encoding completed progress, print and return0. Module catches ordinary Exception and emits JSON error then SystemExit(1); SystemExit/BaseException not caught by that handler.

Failure after calculation is not transactional native rollback; CLI not private pipe progress framing.

Matrix: CP333-X04. Source: engine/bridge/trading_pipeline.py:3788–3809.

## CP330-S25 — L05–07 / LT-M01

Bisect original keyed time for selected first; if selected not same object require Python list equality to original slice. Store original remaining rows and original last time; hash original prefix before last closing bracket; suffix retained; digest via hash copy. No independent negative rfind guard.

Decoded equality is not byte-exact selected file equivalence: equal Decimal values with different lexemes/exponents can compare equal. Original byte-prefix lineage checked later. No sorting proof from bisect.

Matrix: CP333-X03. Source: engine/bridge/live_pipeline.py:88–112.

## CP330-S26 — L08 / LT-M02

Reject wrong base or absent leading comma before clone; hash appended bytes plus retained ending and compare target before decode; decode bracketed payload, append rows, then update end/prefix/digest.

LiveRawDeltaMismatch distinct from native parse/downstream exceptions; state assignment only after pipeline success, not general rollback of post-success assignment failures.

Matrix: CP333-X03. Source: engine/bridge/live_pipeline.py:114–127.

## CP330-S27 — L09 / LT-M02

Length must exceed prior end, exact prefix digest; lstrip tail then comma decoded with remaining bracket or rstrip closing bracket gives empty; else changed. Append before remembering prefix; no new rows but suffix changed updates ending and digest.

Full-file caller proves supplied complete hash before this method. Empty new rows can still append catchup. No promise of identity between selected lexemes and original.

Matrix: CP333-X03. Source: engine/bridge/live_pipeline.py:129–145.

## CP330-S28 — L10 / LT-M02

Compare each new row time directly <= previous original last or predecessor; no int conversion. Pipeline gets catchup + new_rows even when both empty; only success clears catchup and advances last.

Stricter than wrapper numeric nondecreasing. Distinguish original lineage last from bucket last (selected seed can end earlier).

Matrix: CP333-X03. Source: engine/bridge/live_pipeline.py:147–156.

## CP330-S29 — L11–12

Compact json print flush with type first then fields (overridable); progress forwards started OR completedStages present, not necessarily every completed event.

No IO/serialization catch locally; callback failure propagates through owning scope.

Matrix: CP333-X04. Source: engine/bridge/live_pipeline.py:159–165.

## CP330-S30 — L13 / LT-M01

Parse args, require env original path, decode selected bytes, same Path equality shares bytes/list else read/decode original separately; lineage constructed before engine bundle/continuation; seed emits result of pipeline.append(selected), then delete selected.

Path equality is not filesystem identity. Original catchup retained for first update; seed selected only.

Matrix: CP333-X03, CP333-X04. Source: engine/bridge/live_pipeline.py:168–183.

## CP330-S31 — L14 / LT-M02

readline(256), EOF ends; missing newline errors, json.loads then get fields; exact int positive bytes (bool excluded), string digest length64 no hex check; read exact body length; only progress is True selects report sink.

Invalid header/body fails generic Exception path, not retry. base digest only tested nonnull at route.

Matrix: CP333-X03, CP333-X04. Source: engine/bridge/live_pipeline.py:184–196.

## CP330-S32 — L15 / LT-M02

Scoped progress context; base nonnull selects delta and catches only LiveRawDeltaMismatch to emit mismatch and continue. Otherwise full SHA mismatch retries; else full append. Success emits update outside context then deletes payload/raw.

Digest failure no pipeline; scope restored on continue/exception by context owner. Emission may fail after accepted lineage/append; no rollback promise.

Matrix: CP333-X03, CP333-X04. Source: engine/bridge/live_pipeline.py:197–212.

## CP330-S33 — L16 / LT-M03

LiveRawChanged handler sends RAW_CHANGED with original message then return1; other Exception logs stderr and sends generic failure then return1; normal EOF return0, module exits main.

BaseException outside these handlers; output failure in handler can escape. No automatic replay after terminal error.

Matrix: CP333-X03, CP333-X04. Source: engine/bridge/live_pipeline.py:213–225.

## Findings
- CP345-F01: Active LV-M01 and CH39/40 summaries overgeneralized exception rollback/view discard. Narrowed to actual try boundaries; detailed TB14/L02 already precise.
- CP345-F02: LT-M01 selected slice decoded equality cannot prove byte-lexeme or Decimal exponent equality; original prefix hash separate.
- CP345-F03: CP331-F05 / CP333-R01/R02 remain open: historical intersections outside this partition and remaining provider/consumer/implicit handoff review not closed.

CP346 / W2 historical matrix-linked Trading Pipeline semantic review: remaining 26 linked Bridge records (CP323-P26/P28, CP323-S26–31/S33, CP328-S28–30, CP329-S07/08/09/13/16/17/24, CP330-S02/08/13/14/16/19); verify owner handoffs, CP322/332 site meanings, active/historical clauses and failure/replay. Then remaining owner partitions and independent F05/R01/R02 closure gate. W3/W4 remain NOT RUN.
