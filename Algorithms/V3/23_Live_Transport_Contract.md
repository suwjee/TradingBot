# Live transport — exact append lineage and private pipe (V3)

**Conventions:** B = bullish, R = bearish. Preserve Decimal representation, evaluation order, native failures, exact versus main-candle time, original array order and nulls. Record interfaces: [Declared schemas](../../Contracts/Declared_Record_Schemas.md). Operation IDs designate semantic procedures, not required implementation symbols. This contract does not claim runtime equivalence.


## LT-M01 — Seed and lineage state

Decode selected RAW bytes with Decimal parse_float; require nonempty list, otherwise RAW_CHANGED. Read original path from TRADINGBOT_LIVE_RAW_SOURCE; if path equals selected reuse bytes/list, otherwise decode separately. Binary lower_bound original by selected first time, end=start+selected length; if selected not same object, selected list must equal original slice. Store catchup=original[end:], last time=original last time. Retain exact prefix before last closing bracket, suffix from bracket, SHA-256 prefix state and full digest. No normalization before byte hash. Release local large arrays when no longer needed. Load engines and seed pipeline with selected rows; emit seed ready=true,payload. Original catchup appended with first later update, even empty new rows.

## LT-M02 — Message framing and acceptance

Read binary header up to 256 bytes per iteration; EOF normal exit. Require newline, parse JSON. bytes exact positive int; sha256 string length64 (no hex validation); optional baseSha256, progress exact Boolean true. Read exactly bytes length; partial -> error. Delta when base provided: require base matches checkpoint and leading comma, clone prefix hash, add delta bytes, compute expected full hash with unchanged suffix; mismatch -> recoverable RAW_DELTA_MISMATCH, continue, no pipeline call. Decode new array by enclosing delta after comma. Full file without base: check supplied whole hash; mismatch -> RAW_RETRY, continue. Require file length>old prefix end and old prefix hash exact; tail left-strip, leading comma means parse appended JSON array, exactly closing bracket with whitespace means no new rows, else RAW_CHANGED. Validate new row times strictly greater than original last/new predecessor, without conversion at lineage layer; catchup then new rows passed to active LivePipelineContinuation. Only after successful append clear catchup, advance last time and hash checkpoint. Delta increments prefix end and retains suffix; full append with new rows recomputes prefix/suffix; no new rows may update changed suffix hash only.

## LT-M03 — Worker outputs and failures

Progress sink conditional and context-restored. Forward event only if status started or completedStages present; compact JSON line flush. Success update payload and release local update/raw. Error categories:

| Condition | Action |
|---|---|
| Delta base/leading comma/hash mismatch | error RAW_DELTA_MISMATCH; continue reading |
| Full incoming bytes digest mismatch | error RAW_RETRY; continue reading |
| Existing prefix revised, nonappend tail, selected precision mismatch, nonextending raw time, empty decoded array | error RAW_CHANGED with source message; exit1 |
| Ordinary unhandled exception | diagnostic stderr; error LIVE_ENGINE_FAILED with Apply-again message; exit1 |
| EOF | exit0 |

Invalid header, incomplete read and ordinary decode errors fall into generic ordinary exception handler unless explicitly classified. Native BaseException not caught by main. Progress/IO failures not universally recoverable. Transaction rollback of normalized input and view discard belongs to [Live Bridge](18_Live_Bridge.md), not byte lineage; checkpoint advances only after pipeline success. Transport validation is stricter than aggregation's equal-timestamp allowance. No scheduling assumptions.

## Detailed transport procedures

### L04 — _decode_raw

Decode data with native JSON parser using Decimal for floating numeric tokens and native default handling for other tokens. Require nonempty list; otherwise LiveRawChanged with message requesting Apply again. JSON parsing/encoding/conversion errors propagate as native exceptions. No validation of individual rows or sorting. Return decoded list.

### L05 — LiveRawSource constructor

Inputs selected list, original bytes data, original decoded list. Binary lower bound in original keyed by item.time for selected[0].time (key applied to elements, not target). Compute end=start+len(selected). If selected is not identical object to original AND selected != original[start:end], raise LiveRawChanged for precision/range mismatch. Store catchup slice original[end:], last_time=original[-1].time; invoke L06. Does not independently check sorting or empty lists (indexing failures propagate). Catchup slice contains original row references.

### L06 — LiveRawSource._remember_prefix

Input raw bytes. Set _end to last occurrence index of closing square bracket (native not-found value -1, no independent rejection here). Construct SHA-256 state over memory view slice before _end; retain byte suffix from _end inclusive as _ending; set _raw_sha256 to L07 digest of prefix plus suffix. Mutates four state fields in that order. No separate return.

### L07 — LiveRawSource._file_digest

Copy supplied hash state, update copy with ending bytes, return hex digest. Original hash state untouched. No exception handling.

### L08 — LiveRawSource.append_delta

Inputs delta bytes, base_sha256, expected raw_sha256, pipeline. If base differs from retained raw digest OR delta lacks leading comma, raise LiveRawDeltaMismatch (no custom message). Clone prefix hash and feed all delta bytes. Compare digest with old ending via L07; mismatch raises same exception before pipeline call. Decode new rows by constructing JSON array from delta excluding first comma, enclosing with brackets (L04 requires nonempty). Call L10; only after success increase _end by delta byte length, replace prefix state and raw digest. Ending stays unchanged. Return pipeline result. No explicit rollback of side effects inside pipeline; metadata updates happen after success.

### L09 — LiveRawSource.append

Inputs full bytes and pipeline. Reject if byte length <= _end OR SHA-256 over prefix before _end differs from stored prefix, using LiveRawChanged. Left-strip suffix from _end. If comma prefix, decode JSON by replacing first comma with opening bracket and retaining remainder (L04). Else if right-stripped suffix is exactly closing bracket, new_rows empty. Else reject as non-append. Call L10 even when new_rows empty. After success, nonempty rows trigger L06 on new full bytes; otherwise if exact ending bytes changed replace ending and recompute raw digest via L07. Return result. No deduplication or fallback to parsing revised history.

### L10 — LiveRawSource._append_rows

Inputs new_rows and pipeline. Starting from retained last_time, each new row's time must be STRICTLY greater than previous (comparison as supplied, no conversion here). Failure raises LiveRawChanged before downstream append. Call pipeline.append with concatenation of retained catchup and new_rows, then clear catchup and assign last_time to final previous. Empty new rows still pass catchup (possibly empty). Return downstream result. Metadata not advanced if downstream fails; previous is local.

### L11 — _send_worker_message

Input kind and arbitrary named fields. Construct mapping with type=kind followed by fields (a type field can overwrite initial type); JSON encode using compact comma/colon separators, native defaults otherwise; print one line with flush enabled. Output side effect only; JSON or IO errors propagate.

### L12 — _report_worker_progress

Input event mapping. Forward via L11 with kind progress and event payload if event.status equals started OR completedStages key exists. Status access occurs first (missing status raises). Otherwise no output. No explicit return.

### L13 — main

Entry parses arguments, reads required environment variable TRADINGBOT_LIVE_RAW_SOURCE as path, reads selected bytes and decodes. If selected path equals original path reuse selected bytes and decoded object; otherwise read and decode original independently. Create lineage L05, release local large input references, create continuation L01 using load_engines(args, empty mapping); send seed ready=true and payload from appending selected. Release selected reference.
Repeatedly read header from binary stdin with size limit 256. Empty header (EOF) ends successfully. Nonempty must end with newline; parse JSON, read bytes, sha256, baseSha256. Validate size exact int and >0, digest string length 64 (no hex-character check). Read exactly size bytes or raise ValueError. Set progress sink to L12 only if progress is exact Boolean true; otherwise no-op lambda. Within progress context:
- If base digest not null, invoke L08. Catch LiveRawDeltaMismatch locally: send error code RAW_DELTA_MISMATCH with checkpoint-continuity message, continue next request.
- Else if hash of raw bytes does not equal digest, send error code RAW_RETRY with retry message, continue.
- Otherwise invoke L09.
After successful progress context, send update with payload, release updated/raw locals. Outer LiveRawChanged handler sends error code RAW_CHANGED with exception text and returns 1. Outer ordinary Exception handler prints error to stderr (flushed), sends LIVE_ENGINE_FAILED generic Apply-again message, returns 1. Otherwise return 0. BaseException outside the ordinary exception family is not caught by main. Module entry invokes native process exit with returned code only when run as main. Progress context/IO/callback failures may propagate from handlers; no blanket guarantee of response on broken pipe.
Both lambda scopes covered conceptually: time-key function in L05, no-op progress sink here. No speculative transport scheduling behavior.
