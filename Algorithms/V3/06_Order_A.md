# Order_A — Physical parent-stop creation (V3)

**Conventions:** B = bullish, R = bearish. Parent directional extreme is Low for B and High for R; strict parent stop/improvement means lower for B and higher for R. An opposite Order has its own direction and strict predicate, not the parent predicate. Use Decimal normalization and native arithmetic order; preserve source/main versus exact-event times, physical identity, original order, and nulls. Use [record interfaces](../../Contracts/Declared_Record_Schemas.md) and [chronology/index services](20_Indexes_And_Caching.md). Procedure labels name semantic operations, not required implementation symbols.


## OA-M01 — Identity and parent eligibility

Order_A is a creation cause, not mode A. Physical Order = opposite-direction Reaction geometry keyed by (integer First, integer Break) inside the owner direction ledger. Canonical stop: mode A includes anchor/First−1 and extends backward through required context color, then selects directional extreme for Order over inclusive interval through Break; mode B uses preceding canonical opposite Reaction edge/source and requires ordinal >1. Actual stop uses Order direction, strict and lower chronological [max(confirmation,range start),range end). No coarse main fallback for ordinary Order stop. See [Reaction](01_Reaction_Engine.md), [ledger](08_Order_Audit.md).

## OA-M02 — First physical Order after stopped A (S-side)

Build opposite matches sorted by (confirmation,First,Break,ordinal). Choose first with confirmation > exact A stop and First >= its containing main. Independent geometry callback may supply another complete physical result, but requires Break, First >= gate and confirmation > stop. Map to canonical if exact physical identity matches opposite First map; otherwise number zero and preserve real geometry. Compare independent vs native by (First,confirmation); strict earlier wins, ties native. Freeze this selection per A stop; audit records selected identity, stop geometry, selected A source/stop, all unique A causes. Multiple A causes may join physical identity. Source visibility is not synonymous with accepted A; lifecycle later filters by accepted A provenance, retaining historical accepted sources outside view.

## OA-M03 — Parent stop after S/E

Geometry service returns earliest complete gate geometry; blocked First at gate moves to next main, intervening previous opposite-owner Reset can restart search. Require exact canonical identity; no arbitrary Order-only exception here. The independent native candidate begins at First lower-bound of gate main, optionally skip confirmations <= specified gate for primary. Invalid-A First veto applies only at gate main; accepted E exception is exact (parent stop,gate main) and confirmation > stop, never global. Compare independent and geometric:
- prefer restart geometry if continuous deadline supplied and equals range end or precedes geometric confirmation;
- otherwise use geometric if independent crossing absent and its First strictly earlier or independent absent;
- otherwise independent if present.
No unconditional retry. Optional E trend-leg route requires non-internal trend whose First > parent stop, then continued canonical geometry with opposite First > its exact confirmation.

Merge candidates by physical identity; direct route parent-stop cause, eligible Order_B reset-leg independent. Exactly one parent-stop owner selected earliest confirmation, then First, then Break; remove other parent-stop label, keep reset-leg if present. Earliest actual candidate crossing or range end sets deadline (clamp to supplied continuous deadline); keep confirmation <= deadline and sort by crossing then First. Creation audit includes direct parent candidate even if not consumed by the current E race. Invalid/disowned S or intervening sequence reset cannot introduce parent-stop cause. Reuse and final accepted reconciliation are [ledger semantics](08_Order_Audit.md), not new Order_A.

## Detailed parent-stop procedures

### OA14 — _order_stop
Ignore context_start. If number valid 1-based and exact object is canonical opposite at number-1, cache by number. Otherwise no cache. Both routes chronology.canonical_order_stop(order_direction,number,reaction,opposite_reactions,start_index). Return normalized level/source index/time from chronology, no synthetic contextual stop.

### OA15 — order_stop
Public OA14 wrapper.

### OA16 — _first_healthy_direct_geometry
No finder => null. Start containing main index and exact event; while index<=end call finder(order_direction,index,end,event). Null => null. If candidate First is blocked and equals original gate main time, advance to candidate First index+1, search_event=First. Otherwise get exact confirmation; prior owner via upper_bound(opposite confirmations,search_event)-1. First prior reset in stored order with search_event<reset<=confirmation restarts at reset main/exact time. Else require candidate identity canonical, otherwise null; return canonical number/object/confirmation. allow_bounded_continue is accepted but not used in function body; restarted assigned but not read. No extra mode gate.

### OA17 — _trend_leg_direct_order
No finder null. Trend confirmation strictly > start via upper bound; skip trend First<=start. Per sorted trend position cache OA18 result (including null), return first canonical number/object/confirmation or null.

### OA18 — _trend_leg_order_position
Reject internal trend. Finder opposite from trend Break through end at exact trend confirmation. Require candidate and gate decision continue; invoke confirmation callback; candidate First>trend confirmation required. Return canonical physical position or null.

### OA19 — _direct_parent_stop_order
Cache by start,deadline,bounded flag,E flag,confirmation_after including null results; delegate OA20 on miss.

### OA20 — _compute_direct_parent_stop_order
Gate main time from start. Geometric OA16; reject if confirmation_after given and confirmation<=it. Independent starts lower_bound(opposite First times,gate time), skip confirmation<=confirmation_after when specified; skip blocked First only when equal gate, unless E parent, pair (start,gate time) excepted and confirmation>start. Independent candidate if position valid. Prefer geometric when deadline exists, gate decision restart and deadline equals range_end or deadline<geometric confirmation. Else compute independent stop crossing if independent. Select geometric if not preferred already, independent crossing absent and independent absent or geometric First strictly earlier; otherwise independent if exists. Return min selected pool by First time,confirmation or null. No independent geometric fallback outside these clauses.

### OA21 — _merge_order_candidate
Resolve canonical stop and crossing; construct OrderMatch cause parent-stop and supplied cause time. Per physical identity insert if absent or rank (confirmation,First,Break) strictly earlier. Return stored winner.

### OA22 — _enforce_single_parent_stop_owner
If >1 parent-stop match, choose min confirmation,First,Break. For others with parent-stop strip that label; keep remaining causes with parent cause time null or delete identity. Mutates passed dict.

### OA23 — order_candidates
Cache key start,deadline,bounded/trend/E flags; return list copy on hit. Add OA19 and optionally OA17 via OA21. For each B leg whose physical First time>start, merge reset-leg label into same identity (ordered unique) or create match from leg confirmation and stop/cross. OA22. Deadline earliest non-null stop crossing among candidates or range_end; min continuous deadline when supplied. Keep confirmation<=deadline. Sort by crossing exact time (range_end for null), reaction First time; cache tuple, return list.

### OA24 — _first_order
OA23 with flags, filter crossed not null, return first or null.

### OA40 — _register_order_audit
Skip S whose identity invalid or accepted E occupies it. Skip known sequence reset in (source,parent_stop]. OA23 with S bounded/E trend flags; also OA19 and append direct match if absent from candidates, even if no stop before decision. Register only matches with parent-stop cause. New physical row preserves geometry, adds index. Label parent type, E+number if present, override StopAll+sequence number at reset source and empty family; otherwise family from color/family. Add unique parent-stop cause with event/source. Determine earlier existing creation from minimum prior parent-stop event; exception => conservative earlier true. Invalidate carried if new row or earlier existing creation. When only appended rows and prior validated creation index refers to same exact dict and size agrees, retain pending index extension for next query. Later/equal additional cause does not change carried eligibility. No post-stop invalidation for cause-only additions.

### OA41 — visual_order_lifecycle
Static method with explicit self argument. Start lower bound opposite First times; first candidate First>=start and confirmation>=start, compute stop/cross, return singleton eight-field tuple with final false; else empty.

### OA42 — _cross_order
Cache (start,level) including null. Search strict crossing over lower [max(start,range_start),range_end), less unless order_direction bearish. Null absent; otherwise (main index, main timestamp, exact lower event). Cache result.

### OA43 — cross_order
Public OA42 wrapper.

### OA75 — SOrderAuditMixin._initialize_stopped_a_order_lookup
Opposite First map int->(1-based number,reaction), last duplicate wins. Sort native matches (confirmation,First,Break,number,reaction), confirmation times list; empty first-canonical cache.

### OA76 — _first_order_after
Native OA77. If no initial geometry callback return native. Else call with gate main index,exact A stop,end. Null/incomplete physical, First<gate or confirmation<=stop => native. If physical identity matches mapped same First, use canonical number/object and recompute confirmation; else number0. Return independent if native absent or (First index,confirmation) strictly earlier than native; otherwise native. No public Reaction invented for order-only geometry.

### OA77 — _first_canonical_order_after
Cache by exact A stop incl null; upper_bound confirmation stop; first sorted match whose First index>=gate main. Return number,reaction,confirmation or null.

### OA78 — _record_a_order_audit
Compute stop via OA80, physical identity. If absent create row with reaction number/object/confirmation, stop geometry, A source/stop and empty a_causes. Append unique (A source,stop). Existing geometry and first selected cause preserved.

### OA79 — _audit_stopped_a
Normalize A price; first A stop after its confirmation; absent => return. OA76 at exact event; if match OA78.

### OA80 — SOrderAuditMixin._order_stop
Delegate chronology.canonical_order_stop with order_direction,number,reaction,opposite list,start_index. No local cache.

### OA81 — _order_stop_crossed
Bearish Order normalized High>level; otherwise normalized Low<level.

### OA82 — _shared_order_stop_cross
Lower range [max(confirmation,range_start),range_end). If nonempty and lower index exists, first_greater bearish/first_less otherwise, return null if none; else scan slice OA81. Return main index/timestamp/exact lower event at first crossing or null.
