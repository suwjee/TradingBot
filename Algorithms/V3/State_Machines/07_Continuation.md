# Continuation, cache lifecycle and transactional Live — state and lifecycle contract (V3)

Source-derived extended-state models complement [Live](../18_Live_Bridge.md), [RAW](../21_RAW_Aggregation_Contract.md), [indexes](../20_Indexes_And_Caching.md), and [transport](../23_Live_Transport_Contract.md). Labels are analytical unless explicitly native; tables are ordered within each decision stage, not an instruction to persist new fields. Use exact time and Decimal representation, stable ordering, and source-specific guards. Procedure IDs refer to the [V3 registry](../README.md). No runtime results or general mutation-safety guarantee are asserted.

## LX — Active worker normalized-input transaction

The active worker retains normalized market buckets, view/index suffixes and exact byte lineage; it prepares active trading stages afresh and may reuse settled independently calculated closed-regime prefixes. Optional continuations below are separate services, not the active worker's persisted trading state. Registers last_raw_time, prices keyed by (type,value), lower/main arrays (alias at TF1), dirty boundaries and view objects. Last bucket is provisional; settled counts are exclusive.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| LX01 | INIT | E absent or S disabled; timeframe not exact positive int | Reject construction | ERROR | L01,TB12 |
| LX02 | INIT | Valid request | Copy args, store engines, initialize empty buckets/views | READY | L01,TB12,TB19 |
| LX03 | READY | Append rows | Validate integer-positive nondecreasing raw time (equal allowed); if unseeded and empty reject; copy args.to_time=last raw time; emit start outside protected block | STAGE or ERROR | L02 |
| LX04 | STAGE | No rows | Yield unchanged dirty lengths and settled counts, no suffix mutation | REPLAY | TB14,TB17 |
| LX05 | STAGE | New rows | Determine dirty lower if first time=last raw time; dirty main if same timeframe bucket; copy mutable tails, TF1 shared main; normalize/aggregate using prior price cache then local new keys | PREPARE | TB09,TB14,TB15,TB16 |
| LX06 | PREPARE | Aggregation/validation succeeded | Snapshot previous suffixes and last time; add new prices, replace suffixes, set last time, yield delta | REPLAY | TB14 |
| LX07 | REPLAY | Views present | Rebuild candle suffix at dirty positions; if index missing or new length>capacity construct fresh index with crossing retention enabled, else refresh suffix; TF1 shares lower objects | CALCULATE | TB18,TB20,TB21 |
| LX08 | CALCULATE | Full live replay | Clear run caches on entry/exit; prepare market/state without optional live-stage object, build response with optional closed-prefix resolver, report completed stage; final report inside transaction | COMMIT | L02,L03,TB98,TB100,TB101 |
| LX09 | STAGE or PREPARE or REPLAY or CALCULATE | BaseException in protected body/context | If transaction had mutated suffixes restore snapshots, last time, delete added keys; discard retained views; propagate; validation before mutation has no suffix rollback | ERROR | L02,TB14 |
| LX10 | COMMIT | Successful exit | Return payload; next append reuses retained normalized history, not prior trading result | READY | L02 |

Progress callback may fail and is inside or outside protection according to its actual location. Stage count increments before emission, total directions+4; no guarantee of successful external progress delivery. This is input-state transactional behavior, not a blanket rollback for arbitrary callbacks.

## LT — Byte lineage and worker transport

Registers exact prefix hash state, prefix end before last closing bracket, ending bytes, whole digest, catchup rows from selected slice end, original last time. Worker reads binary framed update requests. Distinguish full hash mismatch (retry) from invalid previous lineage (reapply).

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| LT01 | INIT | Selected/original input | Decode Decimal floats, require nonempty list; match selected slice by original time or object identity; catchup=remaining original, last_time=original last, remember prefix and ending bytes | SEED or EXIT | L04,L05,L06,L07,L13 |
| LT02 | SEED | Valid lineage and pipeline | Append selected, emit seed ready=true and payload | READ | L01,L02,L11,L13 |
| LT03 | READ | EOF | Exit0 | EXIT | L13 |
| LT04 | READ | Nonempty header | Require newline within read limit 256, valid JSON, bytes exact positive int, sha256 string length64; read exact bytes, progress sink only on exact true | VERIFY or EXIT | L12,L13 |
| LT05 | VERIFY | Base digest supplied; mismatch with saved digest or absent leading comma or computed full digest mismatch | Emit RAW_DELTA_MISMATCH; continue without updating lineage or pipeline | READ | L08,L13 |
| LT06 | VERIFY | Base digest supplied and verified | Decode nonempty appended JSON array; hold prospective prefix digest | EXTEND | L04,L08 |
| LT07 | VERIFY | Full bytes, provided digest mismatch | Emit RAW_RETRY; continue, no update | READ | L13 |
| LT08 | VERIFY | Full bytes verified | Require existing prefix length/hash unchanged; suffix after left-strip comma => decode, closing bracket with whitespace => empty, else RAW_CHANGED | EXTEND or EXIT | L09 |
| LT09 | EXTEND | New time <= previous original/new predecessor | RAW_CHANGED, no successful update | EXIT | L10 |
| LT10 | EXTEND | All new times strictly extend | Append catchup+new rows via LX transaction; on success clear catchup/update last time | LINEAGE_COMMIT | L10 |
| LT11 | LINEAGE_COMMIT | Delta | Advance prefix end, replace hash state/digest, retain ending | RESPOND | L08 |
| LT12 | LINEAGE_COMMIT | Full with rows or changed ending only | Recompute full prefix/ending/digest if rows; else update ending/digest if changed | RESPOND | L09 |
| LT13 | RESPOND | Successful context exit | Emit update payload, release local update/raw, read next | READ | L11,L13 |
| LT14 | INIT or READ or VERIFY or EXTEND | LiveRawChanged | Emit RAW_CHANGED with source message, exit1 | EXIT | L13 |
| LT15 | INIT or READ or VERIFY or EXTEND or RESPOND | Other ordinary exception | Diagnostic stderr and LIVE_ENGINE_FAILED, exit1; native BaseException not caught by main | EXIT | L13 |

No exact byte checkpoint advances before pipeline success. Full file verification does not normalize old prices to compare lineage. A valid full file with no new rows can still append catchup. Equal raw time accepted by bucket layer but rejected by lineage new-row gate.

## IX — Retained range indexes and crossing cache

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| IX01 | INIT | Market sequence | Power-of-two capacity, min/max arrays, earliest source positions; optional FIFO crossing cache; identity scoped global association | READY | RE31,RE32,RE33,RE45 |
| IX02 | READY | Refresh suffix invalid 0<=first<=old length<=new length<=capacity | ValueError | ERROR | RE34 |
| IX03 | READY | first==new length | No mutation | READY | RE34 |
| IX04 | READY | Valid changed suffix | Clear crossing history iff first<old length−1; replace times/leaves and update ancestor nodes | READY | RE34 |
| IX05 | READY | Strict crossing query with cache absent | Clamp [left,right); empty returns null; earliest qualifying position by segment pruning | READY | RE40,RE43,RE44 |
| IX06 | READY | Cached settled crossing | Return hit only if <right; else null | READY | RE41 |
| IX07 | READY | Cached scanned frontier>=right | Null; no new scan | READY | RE41 |
| IX08 | READY | Cache miss/unsettled suffix | Search from examined frontier; record hit only if before last row, else remember searched settled extent up to min(right,length−1); FIFO bound | READY | RE41,RE42 |
| IX09 | READY | Prepared index supplied | Require identical candle sequence object, associate or raise; reuse only exact identity | READY or ERROR | RE45 |
| IX10 | READY | Calculation scope exits or segment released | Clear run caches or remove specific sequence associations | RETURN | RE51,RE52,TB98 |

No unconditional re-use after arbitrary input mutation; no sorting or precision normalization added by refresh. Range extrema use earliest tie; S last-equal source selection remains a different owner rule.

## RC — Optional committed Reaction continuation

Registers committed candle/lower copies, confirmed result, optional initial cursor, optional normal checkpoint, processed_main_candles. Initial seed requires >=2 main candles; valid direction and timeframe; each main position contiguous and increasing by positive integer multiple of TF, lower contiguous index/strict time; lower extension inside new main interval [first, last+TF).

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| RC01 | INIT | Seed invalid | LiveReactionUnavailable or policy error | ERROR | RE99,RE104 |
| RC02 | INIT | Seed valid | New detector, retain initial/normal cursors, release temporary indexes finally; save result/checkpoint, processed=0 | COMMITTED | RE99,RE102,RE103 |
| RC03 | COMMITTED | Both extension arrays empty | Snapshot, no advancement | COMMITTED | RE100,RE107 |
| RC04 | COMMITTED | Extension invalid (one empty, grid/index/time/range invalid) | Reject without committing | ERROR | RE104,RE107 |
| RC05 | COMMITTED | Valid extension and checkpoint null | New copied combined lists; resume initial cursor; processed=extension main count | PROSPECT | RE107 |
| RC06 | COMMITTED | Valid extension and checkpoint present | Restore accepted Reaction/Reset prefix counts, clone previous/current candidate cursor; replay from checkpoint, processed=len(next_main)−cursor.next_index | PROSPECT | RE107 |
| RC07 | PROSPECT | Earliest post-Reset owner unresolved | Keep earliest pre-reset checkpoint rather than later complete owner; allows displacement on later data | PROSPECT | RE84,RE98 |
| RC08 | PROSPECT | Replay completes | Release temporary indexes in finally; if preview return cloned result without storing anything | COMMITTED | RE101,RE106,RE107 |
| RC09 | PROSPECT | Advance succeeds | Replace committed lists/result/cursors, increment processed count, return snapshot | COMMITTED | RE105,RE107 |
| RC10 | PROSPECT | Exception in replay | Release indexes, no commit of new local arrays/result | ERROR | RE107 |

Standalone continuation's committed grid is not equivalent to active worker's provisional-tail append service. Preview has no stored cursor advancement.

## CV — Optional geometry/Blue/A/S continuation and dependency invalidation

Each row describes a separate service; its own previous state is retained only at documented boundary, not a common cross-stage checkpoint.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| CV01 | RX_VIEW | Dirty main valid | For each native position reuse prior entry only equal geometry signature and Break<dirty; otherwise recompute span/path and changed set | RX_VIEW | RE69,RE70 |
| CV02 | RX_VIEW | Updated inner/outer entries | Retain matched pairs with surviving unchanged positions; changed inner checks all outer, unchanged inner changed outer; rebuild blocked identities and mutate metadata on original full reaction objects; commit maps after metadata application | RX_VIEW | RE70 |
| CV03 | BLUE | first_changed valid existing checkpoint <= reaction count | Rewind earlier if previous reaction Break>=dirty main or First owns Reset index>=dirty; retain output through checkpoint line_count | BLUE | BL11,BL13 |
| CV04 | BLUE | Recompute suffix | Replay previous count/spacing/checkpoints; commit new lists, shallow result | BLUE | BL09,BL12,BL13 |
| CV05 | A | Same timeframe, dirty within min old/new size | Dirty instant=min old/new time at dirty else new end; build fresh detector/current history and longest equal First/Break/confirmation prefix | A | A24,A39 |
| CV06 | A | Query history | Settled event/range strict before dirty or bounded end<=dirty under specific keys; inherited/match reuse bounded by changed Reaction frontier; retain null evidence only when corresponding conditions hold | A | A25,A26,A27,A28,A30,A31,A33,A34,A35,A36 |
| CV07 | A | Crossing query old key with start<dirty | Reuse if end<=dirty or hit<dirty and old/new lower presence agrees. Otherwise resume dirty when unchanged lower prefix proves no hit, suppress fallback on exhausted suffix; old/new both without lower may resume dirty | A | A29 |
| CV08 | A | New detect successful | Clear previous-history pointer, replace detector/result; no shared transaction guarantee for external state | A | A37,A39 |
| CV09 | S | Scope unchanged (direction,TF,start index,range start) | Dirty=min market dirty, earliest symmetric-difference dependency (trend/opposite Break geometry, Reset, Reset Blue, public Blue); otherwise discard previous decisions | S | S44,S45,S46,S48 |
| CV10 | S | Resolve candidate matching key, cached settled_through<dirty | Reuse non-null S decision; still run A ownership/audit pass | S | S48,S49 |
| CV11 | S | Cache miss | Recompute, retain only non-null decision with settled_through: Type3/4 own decision; Order-backed requires a lower row at/after clamped confirmation no later than decision (not independent crossing proof), includes Order Break and first later aligned trend Break/returned confirmation | S | S47,S49 |
| CV12 | S | Detection successful | Replace scope,dependencies,decision map | S | S48 |

## EV — Optional E and Order_B retained services

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| EV01 | E | Advance valid nonempty chronology/dirty index | Scope first main time,TF; rotate current maps to previous iff same scope; reset current maps/index; set dirty and exact chronology identity | E | E01,E02,E03 |
| EV02 | E | Parent stop query | Key less,start,level. Prior hit>=dirty or null rewinds scanned_until to min(old,dirty); retained hit only if <range_end; otherwise search from max(start,scanned_until), save hit or horizon | E | E04 |
| EV03 | E | Extreme/zone query | Reuse old extreme only when end main time<dirty; zone cache uses full geometry key and settled conditions; else recalc | E | E05,E06 |
| EV04 | E | Reconciliation exact evidence key hit | Restore numbered list, candidate list, accepted identities and lifecycle starts | E | E07 |
| EV05 | E | Previous scoped evidence valid but changed groups/parents/resets | Rewind frontier to dirty main and every changed source/parent dependency/reset; restore earlier steps and boundary checkpoint | E | E07 |
| EV06 | E | Replay raises internal reopened race | Clear steps, recompute full reconciliation; only save evidence if no reopened race | E | E07 |
| EV07 | E | Sequence reset map replaced | Copy map/sorted times; clear order_candidates, carried, post-stop and direct-parent caches if present | E | E10 |
| EV08 | ORDER_B | Dirty valid | Set dirty lower/old limit from previous last lower; fresh boundary/cross maps | ORDER_B | OA07,OA08 |
| EV09 | ORDER_B | Boundary key first,last, last<dirty main | Reuse old boundary if present; else recompute; store | ORDER_B | OA09 |
| EV10 | ORDER_B | Crossing key Reset time,level | Reuse old nonnull hit only before dirty and <=current last lower; else strict search after Reset, resume min(old_limit,dirty_lower) if old key existed | ORDER_B | OA10 |
| EV11 | ORDER_B | Discovery successful | Commit maps and last_lower_time | ORDER_B | OA08 |

## LV — Optional StopAll and Primary replay

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| LV01 | STOPALL | Valid dirty main | Rewind dirty to previous covered_until (last lower+1 microsecond) if earlier; find prefix equal event kind/repr and max(source,decision)<dirty | STOPALL | LC21,LC23 |
| LV02 | STOPALL | Prefix determined | Restore checkpoint and output prefix, replay remaining events; old own-stop hit retained only before dirty, else rescan from max(decision,dirty); new outputs resolve normally | STOPALL | LC15,LC20,LC23 |
| LV03 | STOPALL | Success | Commit checkpoint/event keys/output/result/covered_until, return shallow copy | STOPALL | LC22,LC23 |
| LV04 | PRIMARY | Same TF and exact datetime changed event | Rewind dirty to containing main open in old/new grids when within nominal interval; new run uses old state | PRIMARY | P44,P46 |
| LV05 | PRIMARY | Activation schedule changed | Rewind frontier to first changed activation across old/new schedules; retain steps strictly before frontier | PRIMARY | P17,P18 |
| LV06 | PRIMARY | Retained steps replay | Restore checkpoints, replay primary callbacks in original order, refresh MBL stop; retain crossing hits only before dirty, else resume after gate and dirty | PRIMARY | P16,P19,P20 |
| LV07 | PRIMARY | Recompute successful | Drop previous-run link, commit new run/result/times; callbacks may mutate external ledger, no universal rollback | PRIMARY | P46 |

These are source-supported optional continuation boundaries. They must not be combined into a claim that active worker performs incremental trading-stage execution.

## v2.8.7 closed-prefix cache lifecycle

LiveMarketViews owns a fresh closed-regime cache. The staged resolver reads the previous published mapping only for exact range keys whose absolute exclusive end is no later than first_dirty_main; missing/ineligible results are calculated. Store used results in a fresh mapping, publish only on normal cache-stage completion. On outer protected append failure discard views and their cache. MarketIndexWindow clamps crossing searches, but validates range-extreme queries without clamping; both translate results back to the local segment position. See TB103–104 for precise key order, bounds and errors. [Source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1756-L1857).
