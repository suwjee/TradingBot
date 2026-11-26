# Physical Orders, Order_A, Order_B and ledger — state and lifecycle contract (V3)

Source-derived extended state machines complement [Order A](../06_Order_A.md), [Order B](../07_Order_B.md), [Order audit](../08_Order_Audit.md). Labels are analytical unless identified as native. Evaluate guards in local table order; each machine has its own registers and traversal. A transition may be a substep of another; it is not a separate production event or a new field. B/R denote bullish/bearish; strict trend outward predicate Low < level / High > level respectively, and physical Order uses its own direction. Preserve exact Decimal representation, time and source identity. Null means no evidence unless a stated fallback exists. Procedure IDs are defined in the [V3 registry](../README.md); errors propagate except explicit recoverable branches.

## OAS — First physical Order after an A stop

The S-stage provisional ledger and E-stage accepted ledger are distinct. Identity=(integer First,integer Break) within the physical direction of the owning group's opposite Order. Mode A/B is Reaction geometry; Order_A/B is creation cause. Initial native candidate selection traverses confirmation-sorted canonical stream, while comparison against independently confirmed geometry ranks First before confirmation.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| OAS01 | INIT | Exact A stop, containing gate main | Find native canonical opposite match with First>=gate and confirmation>stop; cache result by stop | NATIVE | OA75,OA77 |
| OAS02 | NATIVE | No independent callback or incomplete result, First<gate, confirmation<=stop | Keep native (may be null) | SELECTED | OA76 |
| OAS03 | NATIVE | Complete independent result passes exact gates | Match native by physical identity if present; else number=0, no synthetic canonical Reaction | COMPARE | OA76 |
| OAS04 | COMPARE | Native absent or independent (First,confirmation) strictly earlier | Freeze independent; otherwise retain native (tie native) | SELECTED | OA76 |
| OAS05 | SELECTED | Match absent | No provisional Order_A | RETURN | OA79 |
| OAS06 | SELECTED | Physical match exists | Derive canonical stop and crossing; enter provisional physical ledger, append distinct A-source/stop cause | RECORDED | OA78,OA79,OA80,OA82,RE62 |
| OAS07 | RECORDED | Final A acceptance supplied | Remove rejected A provenance; preserve other valid cause pairs and independent causes | FILTERED | OA72,OA73,LC25 |

## OAP — S/E/primary direct parent-stop path

Input parent source, exact stop, native direction, optional deadline and flags. Invalid S/accepted E-owned S cannot create parent-stop; sequence reset between parent source and stop blocks. The direct search may use canonical gate-relative geometry and native opposite stream, with explicit selection conditions. Parent-stop is not a consumption route.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| OAP01 | INIT | Parent S invalid or E-owned source, or sequence reset between parent source and stop | No parent-stop registration | RETURN | OA25,OA40 |
| OAP02 | INIT | Parent eligible | Query direct geometry; map gate to main and resolve eligible native opposite First; canonical identity required except OAS independent A path | DIRECT | OA16,OA19,OA20 |
| OAP03 | DIRECT | After initial optional confirmation filter, native First blocked AND equal gate | Skip; E exception requires exact allowed (stop,gate time) and confirmation>stop; no confirmation-after recheck after blocked skips | DIRECT | OA20,LC25 |
| OAP04 | DIRECT | Optional confirmation_after (evaluated before native blocked-First loop) | Discard geometry and skip initial native rows whose confirmations <= supplied boundary | DIRECT | OA20 |
| OAP05 | DIRECT | Canonical restart geometry and continuous deadline supplied, equals range end or < geometry confirmation | Prefer restart geometry; still compute native stop/cross if native exists before final selection | CANDIDATES | OA20 |
| OAP06 | DIRECT | Otherwise geometry exists AND native crossing absent AND (native absent OR geometric First strictly earlier) | Select geometry | CANDIDATES | OA20 |
| OAP07 | DIRECT | Otherwise native exists | Select native; if none then no direct match | CANDIDATES | OA20 |
| OAP08 | CANDIDATES | E trend-leg continuation enabled | Consider noninternal trend First>parent stop and opposite First after trend confirmation using owner eligibility | CANDIDATES | OA17,OA18,OA23 |
| OAP09 | CANDIDATES | Direct and independent reset-leg candidates | Merge by physical identity; enforce at most one parent-stop owner by (confirmation,First,Break), retain independent reset-leg causes | BOUNDED | OA21,OA22,OA23 |
| OAP10 | BOUNDED | Candidate crossings known or absent | Earliest retained crossing or range_end only if none sets deadline, clipped by supplied continuous deadline; keep confirmation<=deadline; stable sort by exact crossing (range_end if null), First | RETURN | OA23 |
| OAP11 | RETURN | Register parent-stop | Append direct only if no existing physical identity (including B-only); no repeated bound/single-owner gate; register parent-stop-labelled matches, new row then index, preserve existing geometry and add unique exact cause | RECORDED | OA40 |
| OAP12 | RECORDED | New row or earlier existing creation | Index new rows, invalidate carried only; defer native append only under exact prior index/ledger/size conditions, validate next query; no post-stop flush here; later/equal cause alone leaves carried | RECORDED | OA26,OA28,OA40 |

## OB — Reset-leg state machine

Registers accepted dominant stop records, distinct accepted anchor records, sorted Reset events and trend/opposite canonical lists, frozen boundary/source, exact crossing, selected physical Order. Post-stop eligibility and geometric anchor are independently selected, not interchangeable.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| OB01 | INIT | Direction invalid | ValueError | ERROR | OA06 |
| OB02 | INIT | No accepted stops or anchors | Empty output | RETURN | OA06 |
| OB03 | INIT | Accepted lifetimes | Dominant at exact stop among active lifetimes; same-main best rank and event ordering; prepare anchors and eligible Reset events | RESET | OA02,OA03,OA06,OA11 |
| OB04 | RESET | No same-First canonical trend owner confirmed strictly before Reset | Skip Reset | RESET | OA06 |
| OB05 | RESET | Owner exists | Select last matching owner; latest dominant stop and latest anchor strictly before First main; missing either or anchor index>First rejects | BOUNDARY or RESET | OA06 |
| OB06 | BOUNDARY | Anchor..First inclusive | Strict directional min/max with earliest equal source; require strict extension beyond anchor and source<First | CROSS or RESET | OA04,OA06 |
| OB07 | CROSS | Actual exact Reset; default searches strictly later lower rows for outward boundary crossing; supplied truthy callback supplies crossing without independent strict/time verification | If null, skip; else retain returned exact event and clamped containing main | EXPIRY or RESET | OA03,OA05,OA06 |
| OB08 | EXPIRY | Next accepted A formation strictly after owner First, its main <= crossing main | Expire setup | RESET | OA06 |
| OB09 | EXPIRY | No expiring A | Choose first canonical opposite sorted by confirmation,First,Break,ordinal with First>=cross main and confirmation>cross exact | PHYSICAL or RESET | OA06 |
| OB10 | PHYSICAL | Candidate exists | Freeze complete stop/anchor/reset/boundary/crossing/Order evidence as reset-leg | RESET | OA06 |
| OB11 | RESET | End of input | Return discovered leg list | RETURN | OA06 |
| OB12 | RETURN | Register accepted legs | Nonempty input invalidates carried; create physical row only if absent, publish then index; add full-dict-distinct B cause, stable sort by post-stop,Reset,strictBreak,identity; invalidate carried on unique addition | RECORDED | OA30 |
| OB13 | RECORDED | Feedback requires comparison | Compare semantic leg signature, not just physical identity or count | RECORDED | OA12,TB74 |

Explicit second_time may be parsed through chronology. Without it OA03 requires lower proof of a strict reset in its main; no coarse main fallback for Order_B. First may equal the strict-break main while confirmation must be strictly after crossing. Stop and anchor discovery considers accepted A/S/E/StopAll with exact dominance rules; an invalid A cannot open a new accepted reset-leg.

## OLR — Physical ledger availability and use

Ledger has independent dimensions: confirmation (native physical geometry), strict crossing nullable, creation cause set (parent-stop and reset-leg), and accepted/suppressed display selection. A consumption request is not itself a mutation of creation cause. Lifetime availability is evaluated relative to requested parent and decision gate.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| OLR01 | INIT | Initialize detector ledger | Fresh authoritative empty ledger, separate empty confirmation index, pending and cache structures; stable trend confirmation-only ordering; opposite stream order retained; last First-key and first physical-identity duplicate wins; initial A records remain lazy | AVAILABLE | OA13,OA45 |
| OLR02 | AVAILABLE | Physical Order's canonical stop requested | Mode A scan anchor or First−1 backwards through context and then inclusive through Break; Mode B preceding canonical ordinal edge, ordinal<=1 errors | AVAILABLE or ERROR | RE62,OA14,OA80 |
| OLR03 | AVAILABLE | Strict Order crossing requested | Native (start,level) cache incl null; strict lower [max(confirmation,range start),range end), indexed miss no retry; clamp main, candle.timestamp and exact event; no fabricated main crossing | AVAILABLE | OA42,OA82 |
| OLR04 | AVAILABLE | Unconsumed S Blue recorded evidence | str(color)==blue, confirmation/level non-null, crossing>=new parent stop; copy recorded geometry into carried-live match, no creation cause | USE_CANDIDATE | OA44 |
| OLR05 | AVAILABLE | Gate-owned initial A match | Lazy initial records and by-First index; exact First main=gate bucket, confirmation>=parent stop and crossing non-null>=parent stop; select min crossing then First, first tie | USE_CANDIDATE | OA48 |
| OLR06 | AVAILABLE | Carried accepted ledger entry | Earliest parent-stop creation or any reset-leg confirmation strictly within (lifecycle start,parent stop), confirmation<=parent stop, crossing>=parent stop | USE_CANDIDATE | OA49,OA52 |
| OLR07 | AVAILABLE | Carried initial A entry | Initial First in allowed inclusive lifecycle/stop window plus original confirmation/crossing gates | USE_CANDIDATE | OA45,OA52 |
| OLR08 | AVAILABLE | Accepted post-stop request | Confirmation>parent stop and crossing>both; no sequence reset in (parent stop,crossing]; dedup identities | USE_CANDIDATE | OA25,OA53,OA55 |
| OLR09 | USE_CANDIDATE | Native optimized index preconditions hold | Use validated time/Decimal/crossing shape and sorted merge; preserve legacy ties | AVAILABLE | OA50,OA51,OA55,OA56,OA57,OA58,OA59 |
| OLR10 | USE_CANDIDATE | Native optimization prerequisites fail | Legacy scan/sort with same eligibility; no new acceptance from invalid cache data | AVAILABLE | OA50,OA53,OA55 |

## OLC — Acceptance, revocation and final projection

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| OLC01 | PROVISIONAL | A eligibility resolved | Filter initial A source/stop provenance against accepted A; retain independent valid causes | ACCEPTANCE | OA72,OA73,LC25 |
| OLC02 | ACCEPTANCE | E or S source ownership changes | Reject S parent-stop cause if invalid or E-owned; Order usable only if at least one valid independent cause where required | ACCEPTANCE | OA60,OA62,OA63 |
| OLC03 | ACCEPTANCE | Rebuild from accepted S/E plus historical evidence and reset legs | Merge physical identities; retain valid historical provenance even unused; recover geometry only with valid cause; rebuild index/cache | ACCEPTED | OA62,OA64,OA65 |
| OLC04 | ACCEPTED | Primary point committed in matching owner direction | Derive strict stop in (decision,range_end); request direct with confirmation_after=stop (OA20 sequential-skip caveat, no final local recheck); reparent before optional registration | ACCEPTED | OA32,OA33,OA34,OA36 |
| OLC05 | ACCEPTED | StopAll parent-stop tuple same source time, non-null equal stop strictly after primary decision | Transfer matching cause only on direct identity (null revokes matches); B post-stop exact source pair and stop gate; independent anchor exact pair and truthy Reset identity, First main>=decision, no stop/direct gate | ACCEPTED | OA31,OA36 |
| OLC06 | ACCEPTED | Replacement parent set and B cause collection both empty | Defer deletion of any causeless identity, filter all matching confirmation tuples in place; invalidate post-stop only on revocation, carried on changes or revocation | ACCEPTED | OA31 |
| OLC07 | ACCEPTED | Final primary labels supplied | Last source wins; parent prefix-specific relabel, B OA01 matches PH/PL prefixes against same map; equality dedup; invalidate carried only on change, retain geometry/index | ACCEPTED | OA01,OA37,OA38,OA39 |
| OLC08 | ACCEPTED | Prepare audit for view | Merge accepted S/A and E rows, preserve first physical geometry; keep visible First or identity required by visible behavior | PREPARED | OA67,OA68,OA69,OA71 |
| OLC09 | PREPARED | Parent-stop cause on multiple physical identities | Earliest confirmation,First,Break owns cause; remove only lost cause; drop identity iff no remaining causes | PREPARED | OA66,OA70 |
| OLC10 | PREPARED | Bridge validation | Each displayed S/E/StopAll with physical pair must refer to retained audit; one exact parent-stop cause may not name multiple identities | RETURN or ERROR | TB61 |

An Order can be confirmed but not yet strictly stopped; the audit may retain it. E/primary use routes requiring a crossed Order cannot consume an unstopped entry. Do not represent carried-live or accepted-live as independent creation causes. See [E and lifecycle](05_E_Lifecycle_StopAll.md) for reopening races and accepted-owner transitions.
