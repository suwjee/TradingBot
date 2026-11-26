# S Zone — state and lifecycle contract (V3)

Scope: source-only semantic model, complementing [S](../05_S_Zone.md), [Order A](../06_Order_A.md) and [Order audit](../08_Order_Audit.md). State labels are analytical unless explicitly named as native. An evaluation row is an ordered guarded transition of the indicated machine, not a new persisted engine field. Guards are evaluated in table order within a decision stage; separate machines can run independently. HORIZON means end of supplied calculation context, not the requested visible range. B = bullish; R = bearish. X is Low for B and High for R; outward means X < level for B and X > level for R; confirmation uses High > top for B and Low < bottom for R. Ordinary equal finite prices do not strictly cross. Use exact Decimal semantics and owner-specific time windows; no fabricated intrarow order. Procedure IDs refer to the [V3 registry](../README.md). A dash in the effect means no new accepted record. Exceptions propagate unless a guard specifies another result.

## SOW — A ownership and S discovery

Registers ordered A list, provisional physical audit, output, cycle_start, ownership windows (start exact, optional end). Initial clear windows and audit, audit all stopped A BEFORE eligibility sweep; each physical A stop's first Order selection is immutable for that lookup. Output sorted source/decision.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| SOW01 | INIT | Detector constructed | Initialize dependencies; clear windows/audit, provisionally audit every stopped A | NEXT_A | S01,S42,OA75,OA79 |
| SOW02 | NEXT_A | First matching ownership window contains source event (start inclusive,end exclusive/open), no escape | Skip A; no duplicate accepted S branch | NEXT_A | S25,S26,S27,S42 |
| SOW03 | NEXT_A | Source earlier than cycle_start, or equal with output already present | Skip A | NEXT_A | S42 |
| SOW04 | NEXT_A | No strict A stop from S07 returned confirmation (including native RE61 fallback) | Skip A | NEXT_A | S07,S10,S42 |
| SOW05 | NEXT_A | A stop exists | Resolve first physical Order after stop before next-A gate; if stop>=next A confirmation skip | NEXT_A or WINDOW | S42,OA76 |
| SOW06 | WINDOW | Valid stop before next A confirmation | Open (stop,null), resolve S route; missing S leaves window open | NEXT_A or ACCEPT | S40,S42 |
| SOW07 | ACCEPT | Resolved S | Append, cycle_start=S source main; close latest window at max(stop, decision+1 microsecond) | NEXT_A | S42 |
| SOW08 | NEXT_A | Exhausted | Return sorted S; eligible A is separate filter over ownership windows | RETURN | S28,S42 |

Escape from ownership: A trigger strictly later than window start, or exact closed-window reset-reset condition (S26/S27); use first matching window. A source exact event is first lower row matching price in its source main, with main fallback. A stop fallback allowed only when lower interval empty. A candidate may be audited but subsequently invalid/disowned.

## SRT — Independent Type3 and Type4 versus Order-backed route

Deadline = first physical Order confirmation else range end. Type3 and Type4 independently evaluated before Order-backed race.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| SRT01 | INIT | Valid stopped A | Compute deadline; evaluate both order-free routes | ARBITRATE | S40 |
| SRT02 | TYPE3_SCAN | Opposite Reset strictly after A stop and before deadline; owner confirmation<=A stop; first owner Reset not <=A stop | Freeze last-equal directional extreme owner Break..Reset main; first strict crossing from Reset to exclusive deadline, require aligned trend confirmation in (A stop,cross]; no later recross search if first hit unqualified | TYPE3_READY or TYPE3_SCAN | S18,S19,S20 |
| SRT03 | TYPE4_SCAN | Trend confirmation in (A stop,deadline), Break main not before A stop main | Freeze last-equal extreme A-stop main..Break; search first strict cross from max(confirmation,candidate event,A stop) to exclusive min(next filtered aligned confirmation,deadline), require public Blue formation from source main through crossing; skip candidate without later recross search if unqualified | TYPE4_READY or TYPE4_SCAN | S21,S22 |
| SRT04 | ARBITRATE | Type3 exists and Type4 absent or Type3 decision<=Type4 | Emit Blue type3 with reset provenance and no Order | RETURN | S38,S40 |
| SRT05 | ARBITRATE | Type4 exists and Type3 absent or Type4 strictly earlier | Emit Blue type4, no Order provenance | RETURN | S23,S40 |
| SRT06 | ARBITRATE | Neither order-free route, Order exists | Resolve Order-backed geometry | ORDER_RACE | S12,S40 |
| SRT07 | ARBITRATE | Neither and no Order | Null | RETURN | S40 |

## SOR — Order-backed candidate and race

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| SOR01 | ORDER_RACE | Opposite physical Order confirmed | Canonical Order stop; derive candidate timing from Order boundary vs A-stop main extreme; consider nested trend and S31 returned pre-order event time (including native fallback) | BEFORE or AFTER | S12,S29,OA80 |
| SOR02 | BEFORE | Pre-order source | Clip A-stop main lower interval from exact stop; compare full subsequent mains through Order First; stop-main wins tie; empty lower uses full stop main | PRE_RACE | S30 |
| SOR03 | PRE_RACE | Both eligible crossings at the same lower position (or same main in fallback), neither hit, or no decision | Null | RETURN | S37,S39 |
| SOR04 | PRE_RACE | Candidate wins but unqualified fallback | Discard preliminary candidate, use aligned after geometry | AFTER | S37,S39 |
| SOR05 | PRE_RACE | Order wins or qualified Blue | Retain pre-order source; build zone and decision | RETURN | S39 |
| SOR06 | AFTER | Nested trend First strictly later than Order First and before confirmation, Break<=Order Break, exact confirmation<=Order confirmation, inclusive contained box | Advanced candidate using Order outward edge's source; gate nested confirmation | RACE | S16,S24 |
| SOR07 | AFTER | No eligible nested trend; first trend confirmation strictly after Order | Simple candidate, last-equal extreme Order Break..trend Break | RACE | S15,S17,S24 |
| SOR08 | AFTER | No aligned candidate | Null: when no nested match and no subsequent trend match, S39 returns immediately | RETURN | S24,S39 |
| SOR09 | RACE or PRE_RACE | Nonempty lower window | Order strict predicate from scan_start; candidate gate=max(scan_start,candidate_start); qualified route adds earliest of matching Reset Blue/next trend confirmation; fallback route searches without qualifier | LOWER_DECIDE | S37 |
| SOR10 | LOWER_DECIDE | Neither hit or same exact lower position | Null (same-position ambiguous) | RETURN | S37 |
| SOR11 | LOWER_DECIDE | Order crossing strictly earlier or only Order | Red; source remains pre-order when selected, otherwise earliest equal extreme Order Break..decision main | RETURN | S37,S39 |
| SOR12 | LOWER_DECIDE | Candidate earlier or only candidate | Blue if qualified, otherwise fallback only in preliminary route; preserve candidate source | RETURN | S37,S39 |
| SOR13 | RACE or PRE_RACE | Lower window empty | Scan containing main onward; both predicates true => null before candidate qualification; Order wins Red; candidate Blue only qualified, else fallback when enabled; exhausted null | RETURN | S37 |

Do not convert a lower-window miss into a main-only scan. Distinguish equal time from equal lower position; the actual race compares positions. Source price and exact decision need not share a main. No Order-free route creates a synthetic Order identity.

## SR — Accepted shared-Order reconciliation

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| SR01 | INIT | S list and accepted ledger | Dedup physical First/Break, retain available crossing; require confirmation<stop; sort stop,confirmation,First,Break | NEXT | S43 |
| SR02 | NEXT | Earliest accepted physical stop >= frozen S source main and < existing decision | Replace S color with Red and Order/decision provenance, retain source,price,A and formation type; clear reset provenance | NEXT | S43 |
| SR03 | NEXT | No earlier eligible shared stop | Preserve S | NEXT | S43 |
| SR04 | NEXT | End | Return reconciled records; stage re-evaluates accepted roots and E when changed | RETURN | S43,TB73 |

Live decision reuse and invalidation require settled exact evidence and dependency frontier. See [continuation](07_Continuation.md). S stage does not own downstream final visibility.
