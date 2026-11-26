# Module-specific caches and continuation dependencies — V3.0

These contracts extend the shared [range index](08_Range_Indexes_And_Caches.md). A cache is an optimization over the owning rule, not a new trading rule. Cache keys use native equality unless explicitly string/tuple/identity based. Invalidation follows source; no arbitrary expiry. A previous null may be evidence rather than a missing entry.

## K01 — Reaction and geometry

- Directional A-stop finder closure owns two maps: (gate_index,end_index) -> Candidate or null; (context_start,end_index) -> tuple of detected Reactions. The first key does not contain gate_event even though callable accepts it. First search begins at max(1,gate_index) for a direction-role change; rewind preceding context run; reuse cached detection tuple if an eligible First exists, otherwise detect bounded first. Return stored candidate (no clone at this closure). Do not add time to the key as an unsolicited fix.
- Unified detector bounded geometry after Reset uses (direction,reset_index,limit), with limit=min(requested,detector end) or detector end. Cached non-null geometry returns a replacement record; null is a real hit. Break-index cache maps direction to (list length, break indexes); rebuild when length changes. Directional helper detectors lazy-created.
- Direct Order-gate geometry cache key (direction,gate_index,limit,gate_event_time), after reject gate outside detector start/limit. Cache raw Candidate copy or null; on hit return fresh shallow copy. At capacity 32,768 evict oldest insertion before inserting new result; no LRU. Scope is detector run. Copies preserve candidate mutation isolation, not deep immutable state.
- Live behavior views store per-direction ordered entries and pair sets. Geometry signature includes First, Break, intrabar_start, string top/bottom and their source indexes. Reuse entry at same position only if signature same and Break before first_dirty_main; otherwise recompute span and lower extrema. Preserve old owner pairs only for surviving unchanged endpoints, test changed inner against all outer or unchanged inner against changed outer. Update pair sets/entries after deriving blocked identities and applying marks.

## K02 — Blue

Checkpoint per Reaction boundary includes previous reaction, previous strike count, healthy count since Blue, output line count. Initial checkpoint null/null/0/0. Update requires existing checkpoint and first_changed <= new reaction count; dirty main may move frontier earlier when a prior Reaction Break is dirty or a Reset whose index is dirty belongs to its First. Preserve checkpoints through frontier and lines through checkpoint count; recompute suffix with original state and replace stored arrays. Return a list copy. Marking public/internal is separate from checkpoint formation.

## K03 — A

LiveA creates fresh history maps each detector run, keeps previous history for reuse only during update. Dirty time is earliest available old/new main timestamp at first_dirty_main, or new end boundary when absent. Require same timeframe and valid frontier in both sequences. Compare Reaction input triples (First time,Break time,confirmation) to determine common prefix, same sequence and earliest changed Break time. Settled event is strictly before dirty; settled reaction window additionally ends at or before earliest changed reaction time, if any.

| Cache | Key | Reuse / invalidation |
|---|---|---|
| confirmations | Break index, string directional confirmation level | current hit; prior only settled Break candle |
| reset formations | source index, string broken level | prior only settled source |
| crossings | string level,start,end | current hit; prior if bounded end<=dirty or hit<dirty with same lower-presence flag; otherwise resume as source allows |
| extremes | start,end | previous if end settled; otherwise current hit or compute |
| matches | trigger event, not_before | current hit; previous non-null within common Reaction prefix; previous null only if sequence unchanged; else resume at common prefix when previously queried |
| inherited stops | previous Blue key,current Blue key | prior only settled reaction window of current formation |
| triggers | both Blue keys, expires_at | prior only expiry non-null, current formation window settled and relevant expiry/formation/stop events settled |
| sources | trigger index, reaction confirmation | prior only both events settled |
| zones | ordered field name/value pairs, Decimal as_tuple representation | previous matching record; store current |

Blue key includes formation index/time, stop index/time/event, string stop level/extreme, line kind, Boolean internal flag. Crossing value also stores whether lower rows existed: unchanged lower prefix suppresses main fallback even if no lower suffix remains; if prior no-lower and new no-lower, may resume at dirty. No generic cache-hit implies no-revalidation. After successful detect drop prior history references, retain current detector/result; result property copies list.

## K04 — S

Immutable run lookup indexes: reset Blue first valid reset per reaction number, trend confirmation/index arrays preserving native order only when guards (ordered naive datetimes, valid bounds/nondecreasing First) hold; otherwise fallback. Also sorted trend tuples, opposite First-to-confirmation map, sorted reset events, owner reset times and public valid noninternal Blue formations. Do not reorder original candidate traversal just for binary search.

Live S scope = (direction,timeframe,start_index,range_start). Dependencies set contains trend/opposite Reaction Break time, side, enumerated number, Reaction signature; opposite Reset event/First; reset Blue event/number; public Blue event. Signature = First, Break, mode, intrabar_start, top source index/string top, bottom source index/string bottom, anchor index/string anchor. On same scope reduce dirty frontier to earliest symmetric-difference dependency; otherwise no prior decisions. Candidate key = (A ordinal, source index, source time, string price, stop tuple, optional Order tuple of ordinal, reaction signature, confirmation). Reuse only prior settled-through < dirty; null candidate not retained. Type3/4 settle through decision. Other types require Order match and lower row at/after max(confirmation,range_start) no later than decision; absent row means no settled cache. Extend through Order Break main and aligned trend Break/confirmation when available. Replace dependencies/decisions after successful detector run.

## K05 — E

Detector can share chronology's main extreme map keyed by direction, storing normalized directional values, candle codes and sparse table (earliest tie). Or use exact prepared main range index when its candle sequence is identical and live continuation absent; one-second fallback can select lower index. Sparse table combines power-of-two spans with earlier position on tie; inclusive query uses two overlapping maximal spans. Sequence reset setter copies map, sorts reset times and clears order candidates, carried orders, post-stop orders, direct parent-stop caches if allocated.

Live E advance requires nonempty chronology and valid dirty index. Market scope (first main time,timeframe); dirty = dirty main timestamp or final time+timeframe. Move old maps into prior only when scope equal; clear current maps and main index. Require detector chronology identity and established dirty before querying.
- Stop key (less,start,level), progress (scanned_until,event). Prior null/dirty-or-later event restarts at min(scanned_until,dirty) with null; found event reused only before current range end. Resume from max(start,scanned_until), reject start>=end. Store found or scanned end.
- Extreme key (direction,start_index,end_index); current or prior if end candle strictly before dirty; else new main index and inclusive range.
- Zone key includes direction,family,number,parent kind/source index/time/string price, stop event, Order number/First/Break/mode/top and bottom source indexes/string prices, confirmation/string level/stop index/time/crossed tuple/causes/cause time, source index/time/string price. Prior reuse only max(parent stop, Order stop event, confirmation)<dirty, after selecting current ledger Order.
- Reconciliation exact key = candidate object IDs in sequence, grouped candidate evidence, parent evidence, frozenset sequence resets and validity sets (invalid S root identities, lifecycle starts). Evidence includes repr candidate, ledger presence/initial identity/reset-leg causes/cause set, gate blocking, priority and parent/source dependency; parent tuples include source time,A source time,decision,color. Scope = (direction,live_scope). Exact hit restores candidates/accepted identities/lifecycle starts and numbered copies. Otherwise when previous validity same, frontier begins at dirty main position and rewinds for changed candidate/dependent parent groups, changed parent inputs and reset events. Use checkpoint prefix; _ReopenedERace restarts full before native provenance mutation. Do not retain reconciliation if source reports reopened race.

## K06 — Order Audit and Order_B

| Detector cache | Key / value | Ownership or invalidation |
|---|---|---|
| canonical order stop | one-based reaction number -> level/source index/time | only exact object at canonical opposite list position; noncanonical uncached |
| cross order | (start,level) -> hit tuple/null | run scope; bounds [max(start,range_start),range_end) |
| direct parent | (start,deadline,bounded continue,e_parent,confirmation_after) -> match/null | sequence reset invalidation |
| order candidates | (start,deadline,bounded continue,trend-leg continue,e_parent) -> tuple | return list copy on hit; sequence reset invalidation |
| carried orders | (lifecycle_start,parent_stop) -> tuple | requires decision time; cause changes clear map and creation index/append state; sequence reset also clears map |
| post-stop accepted | (parent_stop,confirmation-index length) -> list | cause-only changes do not clear; ledger reset/removal invalidates; new physical identity changes length |
| initial Order records | materialized tuple, sorted first/confirmation indexes and first-time groups | immutable initial ledger per detector |
| trend-leg order positions | trend position -> canonical position or null | detector scope |
| S first canonical Order | A stop event -> match/null | scan after strict confirmation, First>=gate main index |

Authoritative accepted ledger is separate from secondary confirmation index. Inserting new identity sorts by confirmation/First/Break; optimized sorted audit can add pending records, otherwise mark rebuild. Clear ledger and index together, invalidate carried and post-stop caches; cause-only changes invalidate carried results. Native optimized stream checks types, timezone identity, valid geometry under local Decimal context; any guarded incompatibility triggers eager fallback, not removal of valid candidates. Audit tiers keyed by bit_length of run length, merge equal tiers with stable sorted order; published runs remain immutable for existing iterators. Sequence reset time acts as hard query gate. Exact query keys are not all representation-sensitive (Decimal equality is intentional).

Live Order_B boundary key (first,last); reuse old if last<first_dirty_main. Crossing key (reset_time,level); retain old non-null hit only before dirty and no later than last lower row. Otherwise scan strictly after Reset and resume from min(old lower coverage,dirty lower position) when previous key exists. Replace current maps and last lower time after result. Boundary attribute is fixed by direction.

## K07 — StopAll and Primary

StopAll continuation holds checkpoint sequence, event keys (kind,repr immutable S/E), unresolved output, resolved results, covered-until. Dirty = changed main time or null, reduced to prior covered-until when earlier. Preserve event prefix only while exact keys match and max(source,decision) strictly before dirty (if dirty exists). Resume from corresponding checkpoint/output count. For retained output reuse old resolved stop if non-null and strictly before dirty or no dirty; otherwise resolve after dirty. Newly produced output resolves normally. Replace checkpoint, keys, output/results and observed coverage; return copy.

Primary run holds activation schedule, steps, crossing map and projected points. Retained step frontier begins at dirty event and rewinds for first differing old/new schedule; keep strictly earlier steps. Crossing key (event,string level,above); current hit first, old hit only <dirty, otherwise bisect strictly after event and resume at dirty if previous key present. Live Primary requires original timeframe and exact datetime changed event; rewind to containing main start in old/new time arrays when event before main end. Run against new inputs/Order resolver, then release previous pointer after success. Reflected Primary point projection caches by object identity, checks prior original object is same, otherwise constructs reflected point (including identity_source recursively) and stores original/projected pair; not keyed by final number.

## K08 — Live and Bridge scope

Live normalization and view transaction is [C05–C06](07_Candles_And_Market_Input.md); conversion and chronology caches are [T01/T04](03_Chronology_And_Time_Model.md). Each active calculation scope clears time caches and optional reaction market caches before and in finally. Independent regime uses fresh reindexed candles and releases indexes. Transport hash/prefix metadata only advances after successful downstream calculation; no data access in this specification. Do not imply all continuation classes are necessarily used by every current bridge route.

## Boundaries

This catalog covers shared/high-risk cache and continuation contracts identified from current source. The audit includes a lexical identifier screen for navigation, not a proof of exhaustive cache key/attribute coverage. Exact constructor state, every cache mutation, callback dispatch and exceptional path remains function-level work; do not promote these summaries to full per-function semantics.
