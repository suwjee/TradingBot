# LB — Live transport and lineage

## Seed
RAW is nonempty JSON array parsed with Decimal. Read selected CLI path and original from TRADINGBOT_LIVE_RAW_SOURCE. If same path reuse array. Find first selected time by lower_bound in original; end=start+len(selected). If selected is not original and differs from slice: RAW_CHANGED. catchup=original[end:], last_time=original[-1].time. Hash exact bytes before last closing bracket; ending includes closing bracket and remainder. Full SHA256=hash(prefix+ending). Seed append(selected), send type=seed,ready=true,payload.

## Full append
Reject RAW_CHANGED if length <= old_end or hash(data[:old_end]) differs from prior prefix. Strip leading whitespace of tail; if comma, parse "["+tail without comma; if trimmed tail equals "]", new_rows=[]; otherwise reject. Require each new time strictly > last_time. Invoke pipeline.append(catchup+new_rows); only after success clear catchup and advance last_time. With new rows recompute prefix, ending and hash; if only ending changed update ending/full hash.

## Delta
Require baseSha256=old full hash and first byte comma. Clone prefix hash and add delta; hash(prefix+delta+old ending) must equal new sha256 else RAW_DELTA_MISMATCH without state change. Parse "["+delta without comma+"]". Apply same strict append; after success end+=len(delta), commit new prefix/hash, ending unchanged.

## Pipeline continuation
Require E engine present and S enabled, timeframe exact integer >=1. Copy args; create buckets/views. Each row's int(time) must equal original and >0, not less than previous. Equality allowed here unlike lineage. Empty initial time rejects. Copy args, to_time=previous. direction_count=2 if primary present or direction both else 1. totalStages=direction_count+4. Emit started; stage_append transaction; calculate from buckets/views/delta with reporting; on success report ready. On BaseException rollback input, replace views, rethrow. Public trading stages replay.

## Worker
Read binary header with readline(256); require newline; JSON bytes exact int >0, sha256 string len=64, optional baseSha256; progress enabled only exact true. Read exact byte count. If base digest present run delta; mismatch error RAW_DELTA_MISMATCH and continue. Else hash mismatch RAW_RETRY and continue; otherwise full append. On success send update payload. Report only started or completedStages progress. RAW_CHANGED -> error and exit 1; other exceptions -> stderr, LIVE_ENGINE_FAILED and exit 1; EOF exit 0. Compact JSON messages, flush.

Source reviewed; full bucket/view transaction and worker integration not independently verified.
