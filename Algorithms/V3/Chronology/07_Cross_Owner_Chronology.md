# Cross-owner chronology and replay boundaries

Reviewed source-derived clauses; full semantic closure is not asserted. Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`.

## CH76 — Order gate restart versus continue

With prior owner, outer boundary uses owner First through max(First,gate index minus one). Search strict outer and gate-side hits in [exact gate or gate open, final main end). Outer wins equal lower position. Restart begins at mapped hit main index plus one, continue at gate plus one. Reconstruct missing anchor from latest Reset strictly before result First, through First minus one; never overwrite existing anchor.

[Source engine/pipeline/reaction_engine.py:2134–2216](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L2134-L2216). Overlapping procedures: RE88.

## CH77 — Reset restart handoff

Record Reset unless already recorded. Preserve earliest pre-Reset checkpoint when pending First can displace bounded result. No confirmed structural candidate terminates scan. Rejected append advances to Break plus one with pending Reset at Break. Accepted structure resumes at Break plus one; exact post-confirmation Reset prevents same-Break successor.

[Source engine/pipeline/reaction_engine.py:2574–2650](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L2574-L2650). Overlapping procedures: RE98.

## CH78 — Normal confirmation and running extreme

Update opposite edge before strict Break check. On confirmation use exact analysis edge for post-confirmation Reset; append canonical candidate. Stop early only if First >= requested threshold. Otherwise record exact Reset or seed remainder. New mode-B candidate picks running extreme on equality; opposite range begins after earlier extreme source or current main when coincident. Running extreme changes only on strict improvement.

[Source engine/pipeline/reaction_engine.py:2651–2761](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L2651-L2761). Overlapping procedures: RE98.

## CH79 — Committed Reaction continuation

Seed requires at least two main candles. Main index increments one and positive gap is multiple of timeframe; lower index increments one with strictly increasing times, lower batch within [first new main,last new main + duration). Empty append/preview returns snapshot. Resume retained checkpoint or initial cursor. Preview does not advance committed state; append commits result and cursor.

[Source engine/pipeline/reaction_engine.py:2763–2907](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L2763-L2907). Overlapping procedures: RE98, RE99, RE100, RE101, RE102, RE103, RE104, RE105, RE106, RE107.

## CH80 — Scale strikes and exact Break prefix

Traverse First through Break inclusive. Break extreme uses only lower rows <= confirmation within Break interval; absent prefix proves no new strike. Penetration strictly extends last confirmed strike or Fibonacci level and current pending extreme. Confirm pending on qualifying main color; unresolved pending uses intrabar confirmation race.

[Source engine/pipeline/blue_line_detector.py:144–231](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/blue_line_detector.py#L144-L231). Overlapping procedures: BL06.

## CH81 — Reset Blue double-stop validity

Invalidate new Reset Blue only when previous line first strictly stops at this Reset index and Reset main extreme strictly crosses prior sourceExtreme. Start previous stop search at prior source index plus one. Draw range is source time minus/plus timeframe, not formation chronology.

[Source engine/pipeline/blue_line_detector.py:271–314](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/blue_line_detector.py#L271-L314). Overlapping procedures: BL08.

## CH82 — Blue order and spacing

Process supplied Reaction order and Reset rows grouped by from-First in supplied order. Mode A clears prior strike count; mode B requires previous Reaction. Scale evaluated first; emit on strictly greater count with no prior Blue or at least one healthy Reaction since Blue. If no Scale emitted increment spacing before Reset processing. Each Reset emission clears spacing.

[Source engine/pipeline/blue_line_detector.py:325–431](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/blue_line_detector.py#L325-L431). Overlapping procedures: BL09.

## CH83 — Blue rewind

Dirty main can move changed Reaction earlier when earlier Reaction Break >= dirty main or First owns Reset at/after dirty. Retain checkpoint prefix and its line count; replay suffix.

[Source engine/pipeline/blue_line_detector.py:469–495](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/blue_line_detector.py#L469-L495). Overlapping procedures: BL11, BL12, BL13.

## CH84 — Blue internal interval

Internal if owner marked internal or both semantic extreme and rendered price strictly within same protected box, source time > behavior First and <= confirmation. Naive datetime index path conditional; visibility does not alter calculation validity.

[Source engine/pipeline/blue_line_detector.py:531–589](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/blue_line_detector.py#L531-L589). Overlapping procedures: BL15, BL16, BL17, BL18.

## CH85 — Ordinary A pair trigger

Inherited level route searches [current formation,expiry). Without inheritance and prior stop strictly before current formation, choose extreme from prior stop through current source open minus one microsecond. Search current formation through min(main end,expiry) exclusive, then current stop onward if needed. Otherwise require current stop not after expiry; sort two stops by exact time and direction-dependent level. Equal stop time uses second stop directly; unequal requires continuation cross from second stop through expiry exclusive.

[Source engine/pipeline/a_zone_detector.py:365–496](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L365-L496). Overlapping procedures: A13.

## CH86 — A source freeze

Extreme from trigger main open through exact A Reaction confirmation inclusive; reversed interval null. Later Break rows cannot move source.

[Source engine/pipeline/a_zone_detector.py:592–605](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L592-L605). Overlapping procedures: A17.

## CH87 — Adjacent Blue lifecycle

Process adjacent states. Current formation after cycle Break; prior also after unless bridge reuse. Third formation is expiry. First aligned Reaction confirmation >= trigger and First >= max(stop main times). No match breaks. After source selection cycle frontier becomes Break. Reuse current Blue only if A first strict stop exists and next formation >= stop; else skip through Break.

[Source engine/pipeline/a_zone_detector.py:607–724](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L607-L724). Overlapping procedures: A17, A18.

## CH88 — Special versus ordinary A

Reject special if same Reaction already ordinary. Latest ordinary source strictly before special may suppress by first-stop test through special First with not-before Blue1 source. Retained special suppresses shared-ordinal ordinary only for strictly later trigger, not equality.

[Source engine/pipeline/a_zone_detector.py:726–797](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L726-L797). Overlapping procedures: A18, A19.

## CH89 — Post-Order candidate

Main start first open >= exact Order confirmation bounded by stage start and Reaction First. Eligible anchor at/after selected index. Otherwise range through First; if confirmation belongs to earlier main, inspect lower remainder [confirmation,main end). Earlier remainder replaces on improvement or equality.

[Source engine/pipeline/s_zone_detector.py:587–627](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L587-L627). Overlapping procedures: S24.

## CH90 — A ownership windows

Source event first exact matching extreme within source main, else source open. S owns [start,end) or open interval. A trigger strictly after start is independently eligible. Decided interval permits Reset-Reset pair with Blue1 source > start, Blue1 stop < Blue2 source, A source = Blue2 stop main. Open interval does not permit latter exception.

[Source engine/pipeline/s_zone_detector.py:628–695](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L628-L695). Overlapping procedures: S25, S26, S27, S28.

## CH91 — Simple versus Advanced timing

Legacy after includes equality; nested trend preserves Advanced. Otherwise legacy after can become before only if exact candidate event < Order First main time.

[Source engine/pipeline/s_zone_detector.py:696–740](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L696-L740). Overlapping procedures: S29.

## CH92 — Order-backed S handoff

Pre-Order simple opens at source event; race starts at Order confirmation with fallback allowed. No decision null; fallback alone defers to aligned geometry. Nested alignment uses Advanced Order box opposite-edge main and trend confirmation gate; otherwise first post-Order trend required. Red without accepted pre-Order source uses complete main extreme from Order Break through decision index.

[Source engine/pipeline/s_zone_detector.py:1054–1165](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L1054-L1165). Overlapping procedures: S39.

## CH93 — Type 3/4 race

Order confirmation is exclusive no-Order deadline, else range end. Independent Type 3 and 4; earlier exact decision wins, Type 3 on equality. Order-backed route only if neither forms.

[Source engine/pipeline/s_zone_detector.py:1225–1245](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L1225-L1245). Overlapping procedures: S40.

## CH94 — A-to-S scheduling

Audit stopped A first. Skip A owned by S or source before cycle start (equal skipped after output). Stop must strictly precede next A confirmation. Open ownership window at A stop even if no decision. Successful S sets cycle start to S source and closes at max(A stop,decision + one microsecond). Sort source time then decision.

[Source engine/pipeline/s_zone_detector.py:1251–1305](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L1251-L1305). Overlapping procedures: S42.

## CH95 — Shared Order reconciliation

Dedup physical First/Break preferring record with exact crossing. Crossing strictly after confirmation; sort crossing,confirmation,First,Break. Select earliest crossing >= frozen S source main time and < current decision. Change decision to Red and Order provenance, not frozen S source or Order creation.

[Source engine/pipeline/s_zone_detector.py:1307–1426](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L1307-L1426). Overlapping procedures: S43, S44.

## CH96 — S settled boundary

Same scope dirty frontier min(changed main,earliest symmetric-difference dependency event). Type 3/4 settle through decision. Order-backed requires actual lower evidence >= confirmation and <= decision; main fallback not cacheable. Horizon includes Order Break and aligned trend Break/confirmation if present. Reuse only settled horizon < dirty.

[Source engine/pipeline/s_zone_detector.py:1450–1519](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L1450-L1519). Overlapping procedures: S46, S47, S48, S49.

## CH97 — Healthy direct geometry restart

Start parent stop main and exact event. Blocked First equal original gate main advances to candidate First plus one. Latest opposite confirmation <= current search event owns prior Reaction. Reset in (search event,candidate confirmation] restarts at Reset main and exact time. Candidate must be canonical opposite identity.

[Source engine/pipeline/order_audit_engine.py:689–763](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L689-L763). Overlapping procedures: OA16.

## CH98 — Trend-leg direct Order

Trend confirmation > start and First > start. Exclude internal trend. Bounded geometry must be continue, opposite First > trend confirmation, canonical identity required.

[Source engine/pipeline/order_audit_engine.py:764–808](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L764-L808). Overlapping procedures: OA17, OA18.

## CH99 — Direct Order choice

Canonical First lower bound is stop main open; optional confirmation-after excludes equality. Blocked same-gate First veto except exact E-parent exception with confirmation > stop. Prefer geometric restart when deadline equals range end or precedes confirmation. Otherwise geometric only if independent crossing absent and geometric First strictly earlier or independent absent; else independent.

[Source engine/pipeline/order_audit_engine.py:829–920](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L829-L920). Overlapping procedures: OA20.

## CH100 — Order deadline and Reset interval

Merge direct, optional trend continuation, reset-leg First > start. Enforce one exact parent-stop creation owner. Deadline earliest known Order stop or range end, reduced by continuous deadline. Include confirmation <= deadline; sort stop (range end fallback), First time. Reset interval (start,end].

[Source engine/pipeline/order_audit_engine.py:982–1098](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L982-L1098). Overlapping procedures: OA23, OA24, OA25.

## CH101 — Accepted-live eager

Initial and ledger confirmation indexes strictly after parent stop. Require crossing > parent stop and own confirmation; reject Reset in (parent stop,crossing]. Dedup by identity with earlier (stop,confirmation,First); output sorted stop,confirmation,negative First.

[Source engine/pipeline/order_audit_engine.py:1798–1878](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L1798-L1878). Overlapping procedures: OA53, OA54.

## CH102 — Accepted-live lazy

Conflicting or unresolved native geometry falls back to eager query. Immutable sorted runs merge by stop,confirmation,negative First with stable suffix. Start strictly after parent stop; exclude crossing at/after next hard Reset; require confirmation > parent stop; emit first physical identity only.

[Source engine/pipeline/order_audit_engine.py:1950–2018](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L1950-L2018). Overlapping procedures: OA55, OA58, OA59.

## CH103 — Disowned-S and gate filter

No causes, reset-leg cause or initial independent identity excludes S-only disownership. Otherwise all causes S parent-stop with already/prospectively owned source. Parent-stop E blocked if gate-owned initial confirmation < candidate Order First.

[Source engine/pipeline/order_audit_engine.py:2020–2045](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L2020-L2045). Overlapping procedures: OA60, OA61.

## CH104 — E replay frontier

Exact saved evidence restores identities and starts. Compatible prior validity permits dirty-main frontier lowered by changed group, E parent source, changed S parent and changed Reset main. Reopened race clears partial steps and restarts complete reconciliation; not saved settled.

[Source engine/pipeline/e_zone_detector.py:220–310](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L220-L310). Overlapping procedures: E07.

## CH105 — E source conflicts

Physical source index/time key. Higher family priority, then higher number within family wins; exact rank preserves earlier accepted object. Sort source time,index,decision.

[Source engine/pipeline/e_zone_detector.py:871–914](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L871-L914). Overlapping procedures: E38, E39.

## CH106 — Independent S roots

Exclude S parent at dominant E source. Heap roots by source time,index,ordinal; newly restored source may disown later root or only Order creator, latter reruns native race. Replace earliest (decision,source) same-parent result or add distinct root, then resolve source conflicts.

[Source engine/pipeline/e_zone_detector.py:915–1006](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L915-L1006). Overlapping procedures: E40.

## CH107 — Recursive E chains

Register stopped S Orders before chain traversal. Each stopped S starts E1; next E only on parent stop; repeated source index ends chain. Invalid S cannot open competing family root at native E continuation source.

[Source engine/pipeline/e_zone_detector.py:1031–1123](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1031-L1123). Overlapping procedures: E42.

## CH108 — E priority before numbering

Choose descending ownership priority then decision then parent stop; Red can win despite later decision. Remove strictly stopped active owners; family/number follow parent and stopped families. Reset source clears active state; else append current; regenerated parent can enqueue child.

[Source engine/pipeline/e_zone_detector.py:1372–1459](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1372-L1459). Overlapping procedures: E44.

## CH109 — Exact E-parent exception

Remove accepted A First times from veto. Exception requires invalid A pending S parent, exact stop equal accepted E stop, First in stop main, blocked not inherited, A source <= First < exact stop, confirmation > stop. Key exact stop and First; not global.

[Source engine/pipeline/lifecycle_engine.py:606–693](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L606-L693). Overlapping procedures: LC25.

## CH110 — A stop records

Explicit stop event precedes finder; tuple final field. Map to main. Last duplicate stop per identity for dominance, first for interior evidence. A iteration source time,index; readiness by stop main.

[Source engine/pipeline/lifecycle_engine.py:735–844](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L735-L844). Overlapping procedures: LC29, LC30, LC31, LC32.

## CH111 — A dominant stop and interior

Eligible owner source < A source and stop main <= A source index. Prior A trigger > prior stop escapes. Rank latest stop main,priority,number,source time,index,earliest ordinal. Equality remains valid. Interior exception uses full main extreme owner stop through aligned First and Reaction Break < A source, confirmation < A source. Invalid A under S does not consume S; other lower/equal owners consumed.

[Source engine/pipeline/lifecycle_engine.py:845–972](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L845-L972). Overlapping procedures: LC32.

## CH112 — S visibility and reset

Ownership event exact source finder or source time. Prior source strictly earlier; latest external source bounds lifecycle. Prior stop <= ownership event. Lower-priority S after latest stopped external suppressed by strict source-close penetration of stop-close. Otherwise rank latest exact stop then priority,number,source time,index. Higher S priority supersedes S; price equality valid. Strict lower/equal continuation consumes stopped owners.

[Source engine/pipeline/lifecycle_engine.py:1199–1376](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L1199-L1376). Overlapping procedures: LC38, LC39.

## CH113 — StopAll hard boundary

Compute StopAll once from accepted E/S; publish source-time reset map to E without retroactive E rebuild. A provenance filter considers module source and stop <= A source, chooses dominant, rejects when earliest Blue1/Blue2/continuation/Reaction First predates exact stop; no price comparison.

[Source engine/pipeline/lifecycle_engine.py:1377–1457](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L1377-L1457). Overlapping procedures: LC40, LC41.

## CH114 — MBL qualification

StopAll occupies source main; exclude coincident S/E. Sort source time,StopAll/S/E rank,index. Dedup kind/index/time. StopAll >=3 references and resets owner. Armed qualification is max(reference decision,all accumulated accepted confirmations).

[Source engine/pipeline/PL_PH_detector.py:248–283](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L248-L283). Overlapping procedures: P15.

## CH115 — Primary scheduler

Activate first strict crossing after qualification, sort crossing,qualification,reference index,second index. Reversal wins equality against activation and decision. Activation <= decision takes priority, point ties activation order. Skip promoted StopAll source. PH commit callback clears pending proposals; recompute reversal.

[Source engine/pipeline/PL_PH_detector.py:286–397](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L286-L397). Overlapping procedures: P16.

## CH116 — Primary replay

Rewind dirty to earliest differing old/new activation; retain steps strictly before frontier. Strict crossing begins upper bound of trigger; reuse old hit < dirty else scan from max(original start,dirty lower bound).

[Source engine/pipeline/PL_PH_detector.py:431–488](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L431-L488). Overlapping procedures: P17, P18, P19.

## CH117 — Initial causal order

Full-history Blue then A then initial S shared across Order_B passes. Only S-eligible A contributes initial audit. E receives accepted audit and provisional S; re-evaluate when S validity changes.

[Source engine/bridge/trading_pipeline.py:2127–2240](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2127-L2240). Overlapping procedures: TB73.

## CH118 — Invalidity and shared Order feedback

Validate all S-eligible A even if hidden. Track all invalid A and separate S-stage-invalid descendants; only latter removed immediately from calculation. Recompute accepted A ledger and E-stop exceptions, rebuild E. Shared accepted Order can revise S; changed S causes one E rebuild.

[Source engine/bridge/trading_pipeline.py:2240–2395](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2240-L2395). Overlapping procedures: TB73.

## CH119 — Consumed S and ledger refresh

Use non-S-stage-invalid candidates. Continuation replacement restricted to accepted independent A Orders; match current E owner by physical index/time. Rebuild ledger after replacement with supplemental S, then suppress all invalid S.

[Source engine/bridge/trading_pipeline.py:2390–2484](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2390-L2484). Overlapping procedures: TB73.

## CH120 — Order_B feedback

At most eight passes. Optional StopAll receives accepted E plus missing independent physical donors; restore roots and accepted audit before discovery. Equal identity registers discovered legs and returns replaced state with converged E and StopAll; repeated changed identity and exhaustion error. Shared initial geometry retained.

[Source feedback](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L2569-L2645). Overlapping procedures: TB74.

## CH121 — Full history versus selected view

Blue/A view may clip by inclusive source index; S/E and eligible A full calculation. Fallback S detector zero to physical last main. Preserve invalid identities.

[Source engine/bridge/trading_pipeline.py:2738–2837](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/bridge/trading_pipeline.py#L2738-L2837). Overlapping procedures: TB76.

## CH122 — Final lifecycle before visibility

Visibility copies converged E and StopAll; no additional donor restoration, reconciliation or reset-leg rediscovery. Capture projection and Primary groups before source clipping; filter invalid/internal after. Required visible audit identities may retain out-of-range accepted orders.

[Source visibility](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L2939-L3112). Overlapping procedures: TB77.

## CH123 — Reversal regime

Boundary main index strictly between zero and length. Recalculate historical [0,boundary), verify Primary3 source time/price; else fail. New independent regime begins boundary inclusive with target bootstrap and offset. Publish incoming transition, cap closed MBL display. Continue only while next reversal within selected end. Optional closed prefix resolver may reuse settled cache only under exact key and dirty bound; still require matching confirmed Primary3 before publication.

[Source reversal](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3531-L3632). Overlapping procedures: TB91–TB95; [response](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3633-L3710).

