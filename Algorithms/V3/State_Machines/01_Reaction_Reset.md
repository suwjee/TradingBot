# Reaction and Reset — state and lifecycle contract (V3)

Scope: source-only semantic model, complementing [Reaction](../01_Reaction_Engine.md), [Reset](../02_Reset_Algorithm.md) and [chronology](../20_Indexes_And_Caching.md). State labels are analytical unless explicitly named as native. An evaluation row is an ordered guarded transition of the indicated machine, not a new persisted engine field. Guards are evaluated in table order within a decision stage; separate machines can run independently. HORIZON means end of supplied calculation context, not the requested visible range. B = bullish; R = bearish. X is Low for B and High for R; outward means X < level for B and X > level for R; confirmation uses High > top for B and Low < bottom for R. Ordinary equal finite prices do not strictly cross. Use exact Decimal semantics and owner-specific time windows; no fabricated intrarow order. Procedure IDs refer to the [V3 registry](../README.md). A dash in the effect means no new accepted record. Exceptions propagate unless a guard specifies another result.

## RXI — Standalone leg detector (native mode A/B and SCANNING/WAITING)

Extended state: mode, state, candidate, last_confirmed_bottom/first, running_peak/source, leg_open_low, leg_just_started, anchor and origin, reset_context, index, output arrays. Start mode A, SCANNING, empty lists and null geometry, new-leg true. Retained initial cursor restores only its recorded fields. This table uses the bullish reference coordinates; bearish mirrors prices and roles, not the native market color.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| RXI01 | INIT | Initial cursor absent/present | Initialize fields or restore initial cursor and candidate copy; resume next_index | SCANNING or WAITING | RE15,RE80 |
| RXI02 | SCANNING or WAITING | Last confirmed edge strictly reset; if WAITING, reset race wins | Append Reset with null second_time, clear confirmed owner/candidate/peak, mode A, new-leg true, remember reset candle and RED anchor if eligible; consume candle | SCANNING | RE12,RE15 |
| RXI03 | WAITING | Mode A invalidation before confirmation | Discard candidate, set anchor to current RED or null, origin candidate_invalidation or null; consume candle; no Reset record | SCANNING | RE11,RE15 |
| RXI04 | WAITING | No earlier reset/invalidation, strict lower Low | Update opposite edge/source before evaluating breakout | WAITING | RE15 |
| RXI05 | WAITING | Strict High > frozen top, first_only | Set Break, refine if current main owns bottom and exact analysis exists; append copied confirmed candidate; return | RETURN | RE10,RE15 |
| RXI06 | WAITING | Strict High > top, not first_only | Confirm/refine; append copy; set last confirmed edge/First, running High/index, mode B, clear candidate | BREAK_REMAINDER | RE10,RE15 |
| RXI07 | BREAK_REMAINDER | Strict post-breakout lower reset found | Append exact Reset; clear owner/peak, mode A, new-leg true, remember reset context and anchor | SCANNING | RE13,RE15 |
| RXI08 | BREAK_REMAINDER | No later reset; current main RED | New mode B candidate from current main High/Low; no exact-analysis requirement here | WAITING | RE15 |
| RXI09 | BREAK_REMAINDER | Otherwise | No successor candidate | SCANNING | RE15 |
| RXI10 | SCANNING | Mode A, leg_just_started | Freeze leg_open_low; clear new-leg flag/reset_context; RED after GREEN reset with Low >= reset Low opens candidate (top max GREEN run/current); other RED becomes leg_open anchor; consume main | WAITING or SCANNING | RE09,RE15 |
| RXI11 | SCANNING | Mode A later, previous GREEN and current RED | If invalidation-origin anchor and both Lows below anchor, clear it. Pass if Low >= remaining anchor Low, else Low >= previous Low or leg-open Low. On pass freeze top/source, anchor and leg boundary | WAITING if pass; otherwise SCANNING | RE09,RE15 |
| RXI12 | SCANNING | Mode A, candidate not formed | RED updates scan anchor; DOJI/NEUTRAL label clears anchor; other tags leave it | SCANNING | RE15 |
| RXI13 | SCANNING | Mode B, RED | Choose higher of running peak/current High (running wins equality); min Low from after top source through current, or current alone; create candidate | WAITING | RE07,RE15 |
| RXI14 | SCANNING or WAITING | Mode B scan branch, null running peak or strict higher High | Initialize or update peak/source after possible candidate construction; equal existing peak is retained; advance main cursor. WAITING branch does not execute this scan update | SCANNING or WAITING | RE15 |
| RXI15 | SCANNING or WAITING | Horizon | If retain_initial, store next_index and initial-mode cursor fields; return confirmed lists only | RETURN | RE15 |

Mode A invalidation and confirmed reset race are not the same event. Invalidation rejects an unresolved candidate; confirmed reset records a previously accepted owner. Both helpers test lower outward before confirmation when both predicates occur; see exact distinctions in RE11/RE12. The standalone Break reuse RXI08 is **not** Unified's full-lower-window reuse.

## RXU — Unified directional detector

State: previous confirmed candidate, optional current candidate, next main, running opposite extreme/source, pending Reset index, canonical lists, optional earliest open checkpoint. Initialization selects ordinary initial or isolated-regime trend bootstrap; no initial result returns empty. In isolated bootstrap, first correct-color main may occur at boundary; frozen confirmation edge chosen from running extreme until First, outward edge evolves thereafter, no prior-boundary invalidation. Main iteration starts after Break.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| RXU01 | INIT | Ordinary or isolated initial search incomplete | Return empty lists; optional initial cursor retained | RETURN | RE80,RE82,RE97 |
| RXU02 | INIT | Initial complete | Canonical append (adjacent opposite anchor gate, recompute outward edge First..Break, exact refinement if Break owns it); optional early return by First threshold | REMAINDER or RETURN | RE76,RE97 |
| RXU03 | REMAINDER | Exact post-confirmation reset in same main | Record Reset once using analyzed outward level; pending Reset=Break; candidate=null | NORMAL | RE77,RE97,RE98 |
| RXU04 | REMAINDER | No post-reset, correct tag, exact analysis, no strict later outward break, nonempty entire Break lower interval | Seed B from full lower main interval, earliest equal edges, both source indexes Break, intrabar start main open | NORMAL | RE79,RE97,RE98 |
| RXU05 | REMAINDER | No post-reset, successor gate fails | Candidate null | NORMAL | RE79,RE97,RE98 |
| RXU06 | NORMAL | Pending reset or previous edge strictly crossed, and competing candidate confirms | Apply confirmed-reset race; if confirmation wins, continue candidate path; pending index is not a fabricated independent event order | NORMAL or RESTART | RE12,RE27,RE98 |
| RXU07 | NORMAL | Reset wins, including pending index | Capture pre-reset checkpoint when requested and earliest absent; resolve reset index, clear pending; append only if last Reset not same owner First | RESTART | RE77,RE98 |
| RXU08 | RESTART | Structural search no complete healthy result | Break loop; retain earliest-open checkpoint if applicable | RETURN | RE83,RE84,RE98 |
| RXU09 | RESTART | Healthy structural candidate | Set mode A, clear cross-direction origin/chain flags; append canonical; update previous, cursor=Break+1, running opposite extreme/source | REMAINDER or RETURN | RE76,RE83,RE98 |
| RXU10 | NORMAL | No reset, candidate exists | Strict outward improvement updates edge and source | NORMAL | RE98 |
| RXU11 | NORMAL | Candidate strict confirmation | Set Break, refine exact prefix, evaluate later reset, append canonical; optional early return before recording post-reset; otherwise previous copy, running edge=current | REMAINDER or RETURN | RE78,RE98 |
| RXU12 | NORMAL | No candidate; correct First tag | Freeze confirmation edge from current/running (running wins equality), opposite extreme from edge source+1 through First or First alone | NORMAL | RE07,RE08,RE98 |
| RXU13 | NORMAL | Main traversal continues | Update running opposite extreme on strict improvement; advance index | NORMAL | RE98 |
| RXU14 | NORMAL | Horizon | Return lists; retain earliest unresolved reset-search checkpoint else current normal cursor and counts | RETURN | RE95,RE98 |

RXU02/09/11 canonicalization: adjacent confirmed opposite anchor may replace confirmation edge only with source conditions in RE76 (B anchor Low >= First Low; R anchor High <= First High); then outward edge recomputation. No public clipping of the native accepted lists.

## RXS — Post-Reset structural versus geometry-only search

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| RXS01 | INIT | Reset index, bounded horizon | blocked_through=Reset, earlier_pending=false, First starts Reset+1 | SEEK_FIRST | RE83,RE84 |
| RXS02 | SEEK_FIRST | First <= blocked_through or wrong adjacent tags or direct builder rejects local gate | Advance First, no candidate | SEEK_FIRST | RE84,RE92 |
| RXS03 | SEEK_FIRST | Valid direct First | Freeze owning boundary, candidate and source | SEEK_BREAK | RE92,RE93 |
| RXS04 | SEEK_BREAK | Outward boundary strictly invalidated, including same lower row tie or missing lower proof when both main predicates | Return invalidation main; block subsequent First through it | SEEK_FIRST | RE93,RE94 |
| RXS05 | SEEK_BREAK | No invalidation, strict confirmation | Refine and return healthy candidate plus earlier_pending flag | RETURN | RE84,RE93 |
| RXS06 | SEEK_BREAK | Neither by horizon | earlier_pending=true, next eligible First allowed | SEEK_FIRST | RE84,RE93 |
| RXS07 | SEEK_FIRST | No more First | Return null, still_open=true | RETURN | RE84 |
| RXS08 | INIT | Geometry-only route requested | Independently search completed geometry, without structural acceptance gate; no canonical append | RETURN | RE85,RE86 |

## RXG — Gate-relative independent Order geometry

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| RXG01 | INIT | Gate before start or >= bounded limit | Null | RETURN | RE88 |
| RXG02 | INIT | Cache key hit | Copy candidate or return null | RETURN | RE88,RE89 |
| RXG03 | INIT | No prior confirmed owner at/before gate (same-main exact gate considered) | Search earliest completed geometry from gate+1; tag no-history | SEARCH | RE88,RE90,RE91 |
| RXG04 | INIT | Prior owner exists | Compute outer boundary First..max(First,gate-1), gate confirmation-side level; search lower from gate event/main open to limit main end | RACE | RE88 |
| RXG05 | RACE | Neither strict crossing exists | Cache null | RETURN | RE88,RE89 |
| RXG06 | RACE | Outward exists and <= gate position (or gate absent) | Restart wins, map event to main; start at main+1, invalid map/limit => null | SEARCH or RETURN | RE88 |
| RXG07 | RACE | Gate crossing strictly earlier or only gate | Continue from gate+1 | SEARCH | RE88 |
| RXG08 | SEARCH | Earliest main confirmation of any active healthy candidate | Earliest First among same main completions; tag selected route; reconstruct absent anchor only on continue with earlier Reset; copy into bounded cache | RETURN | RE88,RE91,RE92,RE94 |
| RXG09 | SEARCH | No completed geometry | Cache null | RETURN | RE89,RE91 |

## RXV — Native, internal and public geometry

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| RXV01 | NATIVE | Presentation requested | Clone candidate, compute permitted published box clipping; native record untouched | VIEW | RE30 |
| RXV02 | VIEW | Opposite span starts strictly earlier, end >= inner end, inclusive box containment and available entire inner lower path within outer box | Set behavior_internal, retain native First/Break and numbering | INTERNAL | RE63,RE64,RE65,RE66,RE67,RE68 |
| RXV03 | VIEW | No qualifying protector or missing path | Remain external view | EXTERNAL | RE67,RE68 |
| RXV04 | INTERNAL or EXTERNAL | Live dependency update | Reuse eligible unchanged views or rebuild from changed opposite containment; preserve canonical objects | VIEW | RE69,RE70 |

Cross-check: primary and S Order gate geometry is not a native Reaction append. No transition invents confirmation within a lower row. Batch returns no pending public object; continuation retains it under its own cursor contract.
