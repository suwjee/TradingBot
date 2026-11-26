# E, cross-stage lifecycle and StopAll — state and lifecycle contract (V3)

Source-derived extended state machines complement [E](../09_E_Zone.md), [Lifecycle](../10_Lifecycle.md), [StopAll](../11_StopAll.md). Labels are analytical unless identified as native. Evaluate guards in local table order; each machine has its own registers and traversal. A transition may be a substep of another; it is not a separate production event or a new field. B/R denote bullish/bearish; strict trend outward predicate Low < level / High > level respectively, and physical Order uses its own direction. Preserve exact Decimal representation, time and source identity. Null means no evidence unless a stated fallback exists. Procedure IDs are defined in the [V3 registry](../README.md); errors propagate except explicit recoverable branches.

## ER — One stopped-parent E race

Registers parent type/object, parent stop, candidate routes, accepted E source times, physical ledger, prospective source. Parent stop is first strict lower crossing from exact parent decision (bounded range), no lower-to-main fallback. Frozen E source is the directional extreme over complete main candles containing stop through max(parent stop,Order stop), earliest equal source.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| ER01 | INIT | Parent has no strict stop | No child | RETURN | E18,E19,E26 |
| ER02 | INIT | Stopped parent S or E | Query unconsumed S (S only), evaluate gate-owned initial even though result unused, then carried BEFORE registration; register parent audit; acquire post-stop iterable before direct candidates; no local rollback | MERGE | E30,OA40,OA44,OA48,OA52,OA55 |
| ER03 | MERGE | S with falsy carried collection | Continuous deadline earliest inherited stop else range end; direct bounded continuation enabled; E instead allows trend-leg continuation | MERGE | E30,OA23 |
| ER04 | MERGE | All routes available | Sort crossed direct/inherited/carried eagerly; lazy sort consecutive accepted equal-stop groups; merge by exact stop,negative First; equal keys preserve direct/inherited/carried/accepted route order | RACE | E30,E31 |
| ER05 | RACE | Candidate's only creating cause is disowned S under accepted/prospective source test | Skip candidate, evaluate next | RACE | E28,E30,OA60 |
| ER06 | RACE | First remaining physical Order | Freeze source, decision=max(parent stop,Order stop), native Order and parent provenance; use optional cache builder | RETURN | E30,E32,E06 |
| ER07 | RACE | Exhausted | Null | RETURN | E30 |

Gate-owned initial query is evaluated in ER02 even though the resulting local is not in the final four-route merge. Do not introduce a fifth merge route merely because a helper was called.

## EC — Provisional recursive discovery

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| EC01 | INIT | All supplied S | Pre-register each stopped S's permitted parent-stop cause before any chain discovery | ROOT | E42 |
| EC02 | ROOT | Next stopped S | Family=S color, number=1,parent=S, empty chain source set and chain; start owned source set from accepted identities | RACE | E42 |
| EC03 | RACE | No child or child source index already in current chain | End current chain; retain existing candidates | ROOT | E42 |
| EC04 | RACE | New child | Append provisional record and mark source in chain and owned sets; parent=child E | STOP | E42 |
| EC05 | STOP | No strict child stop | End chain | ROOT | E42 |
| EC06 | STOP | Child strictly stopped | Advance exact stop, number+1, run same race | RACE | E26,E42 |
| EC07 | ROOT | All chains found, invalid S roots and opposite-family native E continuation occupy same root physical source | Drop entire affected provisional chains | RETURN | E42 |
| EC08 | ROOT | All chains found, no such root conflict | Return candidates | RETURN | E42 |

There is no fixed recursion-count cap in EC. Candidate source deduplication per chain is explicit; it is not a claim of arbitrary input termination.

## EQ — Accepted E source reconciliation and numbering

Registers heap of source groups (earliest source time, earliest decision,source index), candidate maps, accepted physical source identities/times, active E list, numbered list, sequence_start nullable, regenerated set, indexed child decisions. Reconciliation operates on all candidates, not a first-root greedy reduction.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| EQ01 | INIT | Candidates/checkpoint | Build indexes and pending source groups; restore allowed prefix if replay; active/numbered/sequence state | SOURCE | E07,E43,E44,E45,E46 |
| EQ02 | SOURCE | Next group contains Order whose sole cause is now disowned S and active parent exists | Reopen full ER race; if checkpoint replay raise internal reopen signal, otherwise enqueue regenerated source; no geometry patch | SOURCE or REPLAY | E44,E47,E49,OA60 |
| EQ03 | SOURCE | Invalid Order (disowned, blocked gate-owned, invalid S without independent cause) or inactive parent | Reject candidate | FILTER | E41,E48,E49,OA60,OA61 |
| EQ04 | FILTER | S parent | Require existing S not E-owned, source>sequence_start and A-source>=sequence_start when reset exists; later prior E requires rebuilt-after-E or unused earlier Red S dominating prior Blue E | FILTER | E49 |
| EQ05 | FILTER | E parent | Permit sequence-start parent or active physical parent; preliminary skipped-parent recursion allowed only through invalid Order but not invalid-S-without-cause, seen guards; final winner still needs active/boundary parent | FILTER | E49,E44 |
| EQ06 | FILTER | Lower S competes with active E it strictly stops, owner Red or candidate Blue, owner child decision>=candidate decision | Exclude candidate | FILTER | E44,E50 |
| EQ07 | FILTER | Any remaining candidates not blocked by still-unaccepted later Red S before Blue E parent stop | Restrict to that subset; if subset empty retain original | SELECT | E44 |
| EQ08 | FILTER or SELECT | No eligible candidate | Skip group | SOURCE | E44 |
| EQ09 | SELECT | Candidate set nonempty | Choose highest parent ownership priority (actual active parent family when found), then earliest decision,parent stop; retain first tie | NUMBER | E44,E51 |
| EQ10 | NUMBER | Winner E parent not actually active and not sequence_start | Skip winner (no detach) | SOURCE | E44 |
| EQ11 | NUMBER | Valid winner | Collect active E strictly crossed by winner price AND winner decision>prior decision | NUMBER | E44,E50 |
| EQ12 | NUMBER | Actual parent Red OR any stopped Red | Family Red; number=max stopped Red+1 or 1 | COMMIT | E44 |
| EQ13 | NUMBER | Otherwise parent Blue OR stopped Blue | Family Blue; number=max stopped Blue+1 or 1 | COMMIT | E44 |
| EQ14 | NUMBER | Otherwise | Original family, number1 | COMMIT | E44 |
| EQ15 | COMMIT | Winner accepted | Remove all stopped active identities, append immutable renumbered winner, index accepted source | COMMIT | E44,E45 |
| EQ16 | COMMIT | Winner source is sequence reset | Clear active list, sequence_start=source; else append winner to active | CONTINUE | E44 |
| EQ17 | CONTINUE | Regenerated winner and actual strict stop | Rerace child; enqueue only if child source index>current source | SOURCE | E44,E47 |
| EQ18 | SOURCE | Heap exhausted | Collect lineage stops with seen set; retain native numbered tuple; project E parent label to StopAll at reset source; return | RETURN | E44,E52 |
| EQ19 | REPLAY | Internal reopen signal | Restart full reconciliation rather than retain stale prefix | SOURCE | E07 |

Family promotion is based on stopped active lineage and actual accepted parent, not most recent Red S label. Source-time and decision-time can differ; same-source family priority precedes earliest decision.

## EF — Restoration and final E ownership

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| EF01 | INIT | Consumed S evidence linked to larger stopped E | Reject S sharing owner/accepted E identity; require S stop; E35 allows invalid-S candidate only if independent A identity bypass or valid cause; reset in (parent source,child source] blocks; E34 owner lookup in current result, no separate E35 owner membership gate | COMPARE | E33,E34,E35,LC34 |
| EF02 | COMPARE | Nonempty continuation and no existing direct child, or first supplied continuation decision strictly earlier than earliest direct child's decision | Remove exact ancestry matches (normal acyclic owner retained); no per-descendant decision gate; merge kept then supplied continuation, update accepted identities after conflict resolve | CONFLICT | E36,E37 |
| EF03 | COMPARE | No earlier valid continuation | Preserve current chain | CONFLICT | E36 |
| EF04 | CONFLICT | Multiple E at exact physical source | Higher injected e priority, then higher number only for same family and equal priority; otherwise incumbent; stable sort source,raw index,decision | RESTORE | E38,E39 |
| EF05 | RESTORE | Independent S root still eligible and not occupied by accepted E | Process root heap; rerace if only-disowned cause, respect direct earliest lineage and conflict checks | RESTORE | E40 |
| EF06 | RESTORE | Final accepted E list | Rebuild/ensure physical ledger with accepted S and historical valid causes; no creation from display geometry alone | RETURN | E53,OA62,OA64,OA65 |

## LC — Cross-stage acceptance, invalidity and visibility (not a single Boolean)

State dimensions: detected native geometry, calculation eligibility, consumed physical owner, provisional causes, accepted cause, source collision, display eligibility. Source identity and actual stop event are independent. A hidden record can be historically required; invalid/disowned cause must not gain new creation rights. Sequence priority S Blue=1,E Blue=2,S Red=3,E Red=4. Module priority A/other=0, S/E same rank, StopAll=5. Priority depends on record shape in module ranking; not a universal sorting key for every race.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| LCX01 | INIT | S ownership windows and A/S/E candidates | Separate S-eligible A from raw A; derive stopped module records via explicit stop or finder | A_SWEEP | S26,S28,LC29,LC32 |
| LCX02 | A_SWEEP | New A by source,index | Add ready stopped owners whose stop main<=A source index; exclude owner source>=A source, stop main later, consumed owner, prior A whose new trigger>owner stop | A_SWEEP | LC32 |
| LCX03 | A_SWEEP | No eligible stopped owner, or A price not strictly beyond selected owner | Valid A (equality valid); no consumption | A_SWEEP | LC30,LC32 |
| LCX04 | A_SWEEP | Eligible owners | Dominance newest stop main, then module rank,number,source,index,earlier original ordinal; duplicate identity last stop for dominance, first stop for interior | A_BOUNDARY | LC27,LC28,LC32 |
| LCX05 | A_BOUNDARY | Strict extension, non-A owner, interior trend evidence (extreme stop main..A First main, source before A source and strictly beyond A price; aligned Reaction First>=head and <=A First, Break<A source and confirmation<A source time) | Keep A, consume eligible owners at <= dominant priority | A_SWEEP | LC32 |
| LCX06 | A_BOUNDARY | Strict extension, no interior, winner S | Invalid A and stage-invalid identity; do NOT consume S | A_SWEEP | LC32 |
| LCX07 | A_BOUNDARY | Strict extension, no interior, winner not S | Invalid A, consume eligible owners at <= dominant priority | A_SWEEP | LC32 |
| LCX08 | A_SWEEP | End | Determine accepted A and invalid S/stage-invalid S derived from A; filter initial A causes; block opposite First in invalid-A live leg | ORDER_CONTEXT | LC25,LC33,TB73 |
| LCX09 | ORDER_CONTEXT | Exact simultaneous accepted E stop and invalid A stop, eligible blocked gate First not inherited and strictly post-stop confirmation | Record narrow E exception; do not globally unblock First | E_REBUILD | LC25 |
| LCX10 | ORDER_CONTEXT | Otherwise | Retain blocked/inherited set excluding accepted initial First; no exception | E_REBUILD | LC25 |
| LCX11 | E_REBUILD | S input evaluation relative to strictly prior E/accepted S | Reject lower/equal priority S if A source predates prior source or A/S price strictly extends prior; otherwise retain | E_REBUILD | LC35,LC36 |
| LCX12 | E_REBUILD | Consumed S candidate after larger E strict stop, earlier E source, stop before A source, E priority higher, strict source Close beyond stopped-main Close | Preserve earliest evidence per owner, choose latest qualifying or eligible older higher owner per LC34 | E_REBUILD | LC34 |
| LCX13 | E_REBUILD | Reconciled S changes | Rebuild E and accepted ledger; remove stage-invalid S at stage-specific gate; retain other geometry only as permitted evidence | FINAL | S43,TB73,OA62 |
| LCX14 | FINAL | Initial A visibility relative to S | Suppress A on S source or S decision-containing main | FINAL | LC26 |
| LCX15 | FINAL | StopAll and E share source | Remove E from visible E; use StopAll donor geometry and history | FINAL | LC40,LC45 |
| LCX16 | FINAL | S after stopped external modules/prior accepted S | Respect latest prior external cutoff and exact source event; lower-priority S source Close beyond external stop-main Close suppresses without consumption; otherwise choose latest exact stop then rank, apply strict boundary and consume no-higher owners or retain higher S | FINAL | LC38,LC39 |
| LCX17 | FINAL | Accepted E references historical S | Restore required S by source time, then apply occupied-source and invalid-S filtering | FINAL | LC45 |
| LCX18 | FINAL | A provenance starts before dominant prior module stop boundary | Suppress A; restore historical A referenced by S; remove A on E/StopAll occupied source | FINAL | LC41,LC45 |
| LCX19 | FINAL | Internal behavior output helper | Copy A/S/E/StopAll lists, no additional removal in current implementation | FINAL | LC44 |
| LCX20 | FINAL | Final public range and invalidity gates | Clip source range inclusive, filter invalid A/S; primary can replace public StopAll source; do not delete independently valid physical causes | RETURN | TB77,P10,OA71 |

## SA — Dominant exact owner and StopAll promotion

Native checkpoint fields owner, pending_stop, active tuple, output count. Owner key=(kind,family,number), latest record and count. Armed iff count>=2. Input sorted source time, kind (E before S on equal source), source index. Owner and active StopAll list are separate registers; pending_stop is frozen historical evidence.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| SA01 | INIT | No owner | owner=null,pending=null,active empty,output empty | EVENT | LC06,LC13,LC14,LC15 |
| SA02 | EVENT | Ordinary acceptance, owner absent | Set incoming count1 | EVENT | LC05,LC17 |
| SA03 | EVENT | Ordinary acceptance, exact key matches | Increment count, latest=incoming | EVENT | LC03,LC05 |
| SA04 | EVENT | Ordinary acceptance, higher sequence priority or same-priority E dominates by family/number | Replace with count1 | EVENT | LC05,LC08 |
| SA05 | EVENT | Ordinary acceptance, other incoming | Retain same owner unchanged | EVENT | LC05 |
| SA06 | EVENT | S Red, current Blue owner armed, owner latest decision<S decision | Emit StopAll1 from S, gate=S exact decision, active singleton, clear owner/pending | EVENT | LC12,LC18 |
| SA07 | EVENT | S otherwise | Find armed stop before source; completed=pending or current valid stop | S_GATE | LC16,LC18 |
| SA08 | S_GATE | Red S, completed Blue owner, Order mode upper B | Emit StopAll1 from S with completed exact stop gate; active singleton; clear owner/pending | EVENT | LC12,LC18 |
| SA09 | S_GATE | No promotion | Freeze completed stop if pending absent; apply ordinary acceptance SA02–05 | EVENT | LC18 |
| SA10 | EVENT | E donor, any active StopAll first strict stop<=E exact decision | Emit number=max stopped+1, gate=min exact stops, type stopall-stop; remove stopped active by object identity, append new; clear owner/pending | EVENT | LC09,LC19 |
| SA11 | EVENT | E donor, no stopped active | Resolve completed=pending or armed stop; ordinary strict stop<donor source OR same donor main with source<=stop<source+TF and donor price strict beyond owner, stop<=decision, OR exact parent type/index/time/price/stop match | E_GATE | LC16,LC19 |
| SA12 | E_GATE | Completed exists | Emit StopAll1, sequence-group-stop; append active; clear owner/pending | EVENT | LC09,LC19 |
| SA13 | E_GATE | None | Ordinary owner acceptance SA02–05 | EVENT | LC19 |
| SA14 | EVENT | After each event | Optional checkpoint owner,pending,active,output length | EVENT | LC15 |
| SA15 | EVENT | Exhausted | Compute each emitted StopAll own first strict stop from decision; nullable fields if none; donor stop/gate remain separate | RETURN | LC07,LC20 |
| SA16 | RETURN | Apply lifecycle | Build source->StopAll number sequence reset map (later duplicate wins); no E recomputation in this helper; suppress same-source E view | RETURN | LC40,E10 |

S Red direct armed-Blue promotion does NOT require price stop or Mode B. Mode B applies only to the subsequent completed-stop route. A completed pending stop does not re-arm a displaced owner. Native StopAll own stop is not the gate event; donor provenance remains separate. Primary ownership is later and conditional. See [Primary](06_Primary_Reversal.md).
