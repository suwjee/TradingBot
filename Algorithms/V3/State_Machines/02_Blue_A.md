# Blue and A — state and lifecycle contract (V3)

Scope: source-only semantic model, complementing [Blue](../03_Blue_Line.md) and [A](../04_A_Zone.md). State labels are analytical unless explicitly named as native. An evaluation row is an ordered guarded transition of the indicated machine, not a new persisted engine field. Guards are evaluated in table order within a decision stage; separate machines can run independently. HORIZON means end of supplied calculation context, not the requested visible range. B = bullish; R = bearish. X is Low for B and High for R; outward means X < level for B and X > level for R; confirmation uses High > top for B and Low < bottom for R. Ordinary equal finite prices do not strictly cross. Use exact Decimal semantics and owner-specific time windows; no fabricated intrarow order. Procedure IDs refer to the [V3 registry](../README.md). A dash in the effect means no new accepted record. Exceptions propagate unless a guard specifies another result.

## BLS — Strike machine per Reaction

Registers: frozen Fibonacci level, list of confirmed strikes, pending strike/null. Threshold = last confirmed strike extreme else level. Eligible Break extreme only from rows <= RE61 returned confirmation time (including Break-open fallback), not full main. Initial empty strikes, null pending.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| BLS01 | INIT | Reaction and reference supplied | Calculate exact 0.618 level; enumerate main First..Break | EMPTY | BL04,BL06 |
| BLS02 | EMPTY or PENDING | Break has no eligible lower rows | Skip entire main including confirming-color check | EMPTY or PENDING | BL06 |
| BLS03 | EMPTY or PENDING | Directional extreme strictly improves threshold and pending if any | Replace pending with current source/index/price; equality retains old | PENDING | BL06 |
| BLS04 | PENDING | Current main confirming color (GREEN B, RED R), after improvement check | Append pending strike, clear pending | EMPTY | BL06 |
| BLS05 | PENDING | End of main traversal | Scan lower from pending source through exact Break, accumulate strict threshold penetrations; first strict confirmation with eligible set selects most directional earliest tie | RETURN | BL05,BL06 |
| BLS06 | EMPTY | End of traversal | Return level and strikes | RETURN | BL06 |

## BLQ — Sequence and visibility state

Registers previous Reaction, previous_count nullable, output (including internal/invalid), counter of intervening Reactions, checkpoints. New run previous=null,count=null,counter=0.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| BLQ01 | NEXT | Mode A | Anchor if non-null else leg boundary; missing both error; previous_count=null; spacing unchanged | COUNT or ERROR | BL09 |
| BLQ02 | NEXT | Other mode | Previous Reaction edge required; missing predecessor error | COUNT or ERROR | BL09 |
| BLQ03 | COUNT | Prior count nonnull, new count > prior and (no output or counter>=1) | Emit Scale at decisive strike, counter=0 | RESET_SCAN | BL07,BL09 |
| BLQ04 | COUNT | No Scale | Increment counter once iff any Blue already exists | RESET_SCAN | BL09 |
| BLQ05 | RESET_SCAN | Matching Reset and (no Blue or counter>=1) | Emit Reset even if invalid; invalid iff previous line first strict stop occurs on Reset main and Reset extends farther than prior extreme; counter=0 | RESET_SCAN | BL03,BL08,BL09 |
| BLQ06 | RESET_SCAN | Matching Reset but output and counter<1 | Skip | RESET_SCAN | BL09 |
| BLQ07 | RESET_SCAN | All matching Resets handled | Store previous Reaction/count, optional checkpoint of count/counter/output length | NEXT | BL09 |
| BLQ08 | NEXT | Input exhausted | Return calculation evidence, not public filter | RETURN | BL09,BL10 |
| BLQ09 | RETURN | Internal owner or both prices strictly inside same protecting Reaction with First < source <= confirmation | Mark internal; keep calculation flag and ordinal | RETURN | BL15,BL16,BL17,BL18 |
| BLQ10 | RETURN | Public projection | Select calculation_valid and not behavior_internal; invalid Reset remains accessible to A | RETURN | BL14 |

## AP — Ordinary A adjacent-Blue pair machine

Registers full sorted Blue ordinals (including invalid), filtered valid states with formation and stop, current pair offset, cycle_after_index=-1, nullable bridge_reuse_ordinal, output. Pair expiry = following valid state's formation or null. Formation gate (Scale A14 confirmation with intrabar disabled and possible Break-open fallback, Reset first strict lower cross else source main) and stop gate are separate; Reset stop starts at next main boundary.

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| AP01 | INIT | Inputs | Sort and number, build valid states, calculate strict stop and source provenance | PAIR | A01,A07,A09,A10,A11 |
| AP02 | PAIR | No adjacent pair left | Return ordinary output | RETURN | A18 |
| AP03 | PAIR | Current formation index <= cycle_after, or previous <= cycle_after without bridge exception | Clear bridge if used, advance pair | PAIR | A18 |
| AP04 | PAIR | Previous stop exact/main absent or exact stop > expiry | Reject pair; advance | PAIR | A13,A18 |
| AP05 | PAIR | Inherited stop available | Search strict crossing of inherited level from current formation to exclusive expiry; if absent reject (no fallback to other routes) | MATCH or PAIR | A13,A16 |
| AP06 | PAIR | No inheritance, previous stop < current formation | Freeze extreme previous exact stop..current source open-1 microsecond; first cross in current formation remainder to min(end,expiry), if found use effective current stop main | MATCH | A08,A13 |
| AP07 | PAIR | AP06 no formation crossing | Require current actual stop <= expiry; strict cross from current exact stop to expiry; missing gate/cross rejects | MATCH or PAIR | A13 |
| AP08 | PAIR | No inheritance, previous stop >= current formation | Require current actual stop <= expiry; order stops by exact time then higher level B/lower R; first exact stop row extreme freezes continuation | TWO_STOPS or PAIR | A13 |
| AP09 | TWO_STOPS | Exact stop times equal | Trigger directly at second stop, no additional strict cross required | MATCH | A13 |
| AP10 | TWO_STOPS | Exact stop times differ | Strict cross from second exact stop to exclusive expiry, or reject | MATCH or PAIR | A13 |
| AP11 | MATCH | No aligned Reaction with confirmation>=trigger and First>=both effective stop mains | Break entire ordinary loop (not merely skip pair) | RETURN | A15,A18 |
| AP12 | MATCH | Aligned Reaction exists but source window invalid | Advance pair | PAIR | A17,A18 |
| AP13 | MATCH | Valid aligned source | Freeze price/source using A08 from trigger main open through A14 returned confirmation inclusive (including native time and empty-lower main fallback); emit A and provenance; cycle_after=Break | ADVANCE | A17,A18,A21 |
| AP14 | ADVANCE | First strict A stop from confirmation exists and next Blue formation >= that stop event | Allow current ordinal bridge reuse; advance one | PAIR | A07,A18 |
| AP15 | ADVANCE | Otherwise | Clear reuse, skip all states through cycle_after | PAIR | A18 |

Stop/cross helper: lower interval nonempty means no main fallback on miss. Empty lower interval permits established main search. Pair expiry is exclusive for crossing queries, but stop guard rejects only >expiry; simultaneous AP09 can trigger at equality. Inheritance requires previous formation before current; chained route requires earlier actual stop and noninternal lines, otherwise previous line must not be Scale. Its aligned Reaction First strictly after start, Break strictly before current formation; chained includes full Break, other route ends at Break open. These conditions are gates, not state fields.

## AD — Invalid Reset Blue (special double-stop) and ordinary collision resolution

| ID | From | Guard / input | Mutation / emitted evidence | To | Procedures |
|---|---|---|---|---|---|
| AD01 | INIT | Full sorted Blue sequence | Previous valid=null, special empty | SCAN | A12 |
| AD02 | SCAN | Valid line | Retain as previous valid | SCAN | A12 |
| AD03 | SCAN | Invalid line and previous valid absent or strict crossing not on invalid source main | Skip invalid; retain previous | SCAN | A12 |
| AD04 | SCAN | Invalid line with previous valid stop on invalid main | Align first Reaction with confirmation >= exact trigger and First main time >= invalid source time; valid source required | FORM or SCAN | A12,A15,A17 |
| AD05 | FORM | Successful geometry | Emit double-stop A, both effective stop mains invalid main, continuation prior source, no exact Blue stop fields; consume previous | SCAN | A12 |
| AD06 | SCAN | Horizon | Filter special by ordinary Reaction ordinal collision | RESOLVE | A19,A20 |
| AD07 | RESOLVE | Latest strictly earlier-source ordinary A has A22 first stop from next source main open, before special First and >= special Blue1 source | Reject special; later recross is not first stop | RESOLVE | A19,A22 |
| AD08 | RESOLVE | Remaining special overlaps Blue ordinal with strictly later-trigger ordinary | Remove ordinary; equal trigger does not remove | RESOLVE | A19 |
| AD09 | RESOLVE | Finished | Combine surviving ordinary and special, stable sort by source_time,trigger_event_time | RETURN | A20 |

A object emitted by AP/AD is detected, not automatically accepted by lifecycle. A acceptance and S ownership are separately modeled; no stage may infer eligibility merely from a public label.
