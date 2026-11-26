# CP344 — W2 Live Pipeline queue reconciliation

Source-only scoped review, W2 not accepted.

## CP323-S42 — 22–70

Constructor checks E non-null and S enabled before exact-type positive integer timeframe; shallow-copies args, retains engines, creates buckets and views. append converts row time to int, requires numeric equality and positive value, compares nondecreasing against last raw time, allows equal. Empty initial history errors. Copies args and updates to_time; direction_count 2 if primary present OR both, otherwise 1. Captured progress counter increments before emit; initial progress is outside try. Within stage_append context passes retained views, delta and report_stage to calculate_live_from_buckets, emits validation-ready before context exit. Any BaseException within protected block replaces views and reraises; returns payload only after normal exit.

Bucket owner TB14 rollback applies to staged suffix/key/time changes after publication, not arbitrary pre-yield commit or external callback effects. Initial progress and prevalidation outside protection. Closed-prefix cache discarded with views on error; active runner supplies no live trading-stage continuation. L10/L11 strict lineage time check is separate from L02 nondecreasing numeric gate. Direction count not proof of actual engine count.

W1/B10 overlap: 45 canonical row references.

## CP330-S24 — 73–85

Two distinct ValueError subclasses carry changed-lineage versus failed byte-continuity meaning. _decode_raw invokes native json.loads(data,parse_float=Decimal) before list/nonempty check; empty or non-list raises LiveRawChanged with exact message. Native parser errors propagate; no row validation, sorting, integer-time coercion, or price normalization performed here.

Main worker distinguishes delta mismatch retry from changed lineage exit; native JSON failures reach generic Exception handler. Decimal parsing is not byte-lexeme identity; lineage hash preserves original byte prefix separately and advances only after successful pipeline append. Batch loader BOM handling and bucket normalization are distinct; no synthetic RAW execution.

W1/B10 overlap: 7 canonical row references.

## Gate
All 185 queued transition IDs and all 9 supplemental accessors now reviewed. The historical matrix and cross-owner closure remain independently subject to CP331-F05 and CP333-R01/R02.

CP345 / W2 independent semantic closure assessment: reconcile CP331-F05 / CP333-R01/R02, distinguish all 185 directly reviewed queue records from the 131 historically intersecting transitions; verify actual handoffs, active/historical specification consistency, conditional consumers, owner ledger and failure/replay. Do not equate exact ID union with semantic acceptance. W3/W4 remain NOT RUN.
