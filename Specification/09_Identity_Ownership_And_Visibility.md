# Identity, provenance, ownership and visibility — V3.0

## P01 — Do not conflate identity domains

| Domain | Key / order | Meaning |
|---|---|---|
| Candle | sequence position or stored index, with owning market/regime | physical observation; not globally unique across independently reindexed regimes |
| Reaction / physical Order | ordered pair of integer First and Break indices | direction and regime are external owner context, not additional pair fields |
| Reaction ordinal | one-based original directional list order | includes internal reactions; not a compact public-only numbering |
| Reset | originating First, reset index and event provenance | cache identity also includes timestamp representations and broken level; see time contract |
| A/S source identity used by lifecycle invalid sets | (source_time, integer source_index) | physical source, within owning direction |
| E physical deduplication | (integer source_index, source_time) | keep one accepted E per source; note tuple order differs from invalid-set key |
| Lifecycle module identity | (runtime class name, family if present else color if present else null, number or null, source_time, source_index or null) | includes logical role; not identical to physical source pair |
| Primary physical point | (source_index, source_time) within primary kind/direction | local cycle roles can coexist before final reconciliation |
| Order_A cause identity | (parentType, parentFamily, eventTime, parentSourceTime) | exact creation event/parent, not just Order geometry |
| E exception key | (exact E parent stop event, physical First time) | limited First veto exception, not general unblocking |
| Public primary ID | direction, origin kind/number/absolute trigger and decision indexes, optional non-first origin cycle ID | preserves original identity when final number is revised |
| T/F annotation owner | sourceTime within one directional group/segment | first valid row encountered in the defined collection priority |

Physical identity converts First/Break separately to integers. Do not use decimal-price equality, Reaction mode, public number, cause type or stop index as a replacement. Mode A/B denotes Reaction geometry; Order_A/B denotes creation cause (parent-stop/reset-leg). One physical Order can carry both causes. A bounded geometry may have number zero without an invented public Reaction number. For segments, keep local and absolute indexes distinct; add offset only to fields the bridge translates.

## P02 — Reaction and Blue ownership

Reaction containment compares an inner candidate against opposite-direction spans. A possible outer owner must begin strictly earlier, confirm at or after inner confirmation, have top >= inner top and bottom <= inner bottom. Use the published geometry and the inner actual lower-path extrema from [First time, confirmation time] inclusive. Empty lower path does not prove containment; both extremes must lie within outer bounds inclusively. The chronological index is a candidate optimization; fallback traverses outer spans. Mark inner identity blocked on first qualifying owner; live pair tracking retains all valid owner pairs so removal of one does not automatically release another. Assign behavior_public_number using original directional ordinal, record public box and confirmation/First time, and mark behavior_internal by blocked physical identity. Full result remains available downstream.

Blue internal marking is true if its one-based owner Reaction is internal, or if there exists a Reaction whose First < Blue source time <= confirmation and both semantic source extreme and rendered line price lie strictly inside its box. Missing source time/price/box-time evidence follows the explicit null gates. Marking sets behavior_internal true (including native low-level mutation of a frozen Blue record); it does not clear an existing true flag. Public Blue requires truthy calculation_valid (default true) and not truthy behavior_internal (default false). Do not replace semantic extreme with drawing price. A formation's acceptance/visibility is independent of whether the upstream structure is drawn.

## P03 — Order ledger and cause ownership

Accepted ledger owned by detector is keyed by physical First/Break. Newly accepted identity adds a sorted confirmation-index record (confirmation, First, Break). A new cause on same physical geometry updates cause evidence rather than manufacturing a second identity. Reset-leg cause records include post-stop owner, anchor behavior, Reset geometry and exact confirmation/strict-break provenance, physical identity and confirmation. Deduplicate exact cause dictionaries and sort reset-leg causes by post stop time, reset time, strict break time, physical pair. A stopped-A cause can be filtered by accepted A source time. For merged publication, retain rows inside First-index visibility or explicitly required by displayed S/E/StopAll; keep first entry for physical identity and append distinct supplied causes. A missing stop_cross key triggers a lookup; an explicitly null stop_cross is already a recorded no-cross value. For each parent-stop cause key select earliest (confirmation, First, Break); exact rank tie retains first encountered owner. Remove that cause from other physical rows and omit rows with no accepted causes. Never replace original stop geometry solely to rename primary labels.

## P04 — Lifecycle priorities

Sequence priority for lowercased (kind,family): S blue=1, E blue=2, S red=3, E red=4. Unsupported tuple raises lookup error. Module priority checks attributes in order: stopped_behavior_type -> 5; family -> 4 for red else 2; a_source_time -> 3 for red color else 1; otherwise 0. These are distinct functions; the latter recognizes shape, not a general enum validator. No direction-dependent priority flip.

Dominant occurrence tracks kind, family, number, count and latest. Initial occurrence creates count 1. Exact same kind/family/number increments count and replaces latest. Higher priority or qualifying same-priority E dominance replaces owner; otherwise retain. Armed at count>=2. Lifecycle selection can use latest stopped main candle before applying priority, number, source time/index; do not globally sort solely by family. E same-source winner compares family priority then number within family, preserving current winner on exact tie; sort output by source time, source index, decision time.

StopAll removes competing E at same source index for final visibility; final S is selected after module reset boundaries and historical S parents referenced by retained E can be restored. Final A is selected after module boundaries, with historical A parents referenced by retained S restored from eligible lineage input. Sort restored S/A by source time/index. Occupied E/StopAll source indexes remove A/S; invalid S physical pairs remove S. The legacy filter_internal_behavior_outputs returns list copies without obsolete secondary-order suppression. The bridge prepares required physical Order identities for all displayed S/E/StopAll. Display lineage is not a rewrite of earlier calculated state.

## P05 — Primary identity versus role

Only points with decision_index <= requested horizon participate in physical reconciliation. Group by source pair. Sort groups by minimum decision_event_time, source_time, source_index. Within group role order = (decision_event_time, cycle's enumeration position or length, cycle_id or empty, trigger_index, number). Identity origin is minimum role order. Final winner is highest local number, then minimum role order; if price is strictly more extreme than preceding resolved point, final number is max(local winner number, previous final number+1). Copy winner with final number and identity_source = origin.identity_source if present/truthy else origin. Internal cycle states and orders remain independent. MBL becomes publicly formed only when corresponding primary point is confirmed within horizon, not just when activated.

Public ID constructed from direction, origin kind, origin number, trigger_index+offset, decision_index+offset separated by colons; append adjusted origin cycle ID if non-null and not first cycle ID. Cycle ID of form direction:cycle:reference:second adjusts both indexes when nonzero offset. Point's current number and source remain its current resolved values. Primary order labels are reconciled by source time; relabel qualifying PH/PL cause labels without changing provenance, deduplicate resulting cause dictionaries.

## P06 — Final verdict and output

T/F first removes old verdict/repair/repeated keys from all visited row dictionaries. Collection ownership priority is primaryLows (bullish) or primaryHighs (otherwise), StopAlls, E zones, S zones. Ignore rows with calculationValid exactly false; first row per sourceTime wins. Sort by sourceTime. Assign neutral verdict before category rules. Primary boundaries flush StopAll segment evaluation; primary numbers 1/2/3 get T/F/F. This is a final annotation layer, not formation logic.

Multiple regimes in one direction preserve segment order: copy last segment's scalar envelope, concatenate list fields in original segment order, combine Bridge Output list fields in encounter order, remove aggregate calculationEndTime, keep calculationSegments. Do not reconstruct geometry from concatenated arrays.

## Scope

These are shared identity and visibility contracts. Each exact formation, lifecycle state transition, event priority, and output field condition still needs its owning algorithm specification. See [record schemas](../Contracts/Declared_Record_Schemas.md), [boundary matrix](10_Boundary_Tie_And_Error_Contracts.md) and [audit](../Audit/Phase_03/Closure_02.md). No runtime verification.
