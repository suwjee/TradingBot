# Additional owner-specific chronology boundaries

**Reviewed selected source ranges — not full semantic closure.** Baseline `466eb875070f02cd0dbfb105033422bbe2fd8c70`. **Current-baseline precedence:** see [CP350 current semantic qualifications](35_W2_Semantic_Closure_Reconciliation.md) together with CP292 current anchor transfer and CP334–349 direct rechecks. Historical wording below is retained as historical evidence; current qualifications control where they differ.

## CH46 — Breakout analysis

Start at top-source + 1 when that source predates First, otherwise top-source; an intrabar start overrides. Lower search is [start, Break end). First strict high above top owns confirmation; minimum low includes its crossing row. Missing crossing or unmappable source returns null.

[Source engine/pipeline/reaction_engine.py:250–270](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L250-L270). Overlapping named procedures: RE10. Overlap is not whole-procedure certification.

## CH47 — Standalone invalidation and Reset race

Mode A chooses anchor value, otherwise leg boundary. No boundary or no strict low penetration rejects invalidation. Penetration without main confirmation accepts invalidation. When both are possible, compare first lower positions in the same main interval: invalidation wins equality; absent invalidation wins only when breakout is also absent. Confirmed Reset race follows the same lower-position tie and missing-hit handling, with null candidate or absent main breakout allowing Reset.

[Source engine/pipeline/reaction_engine.py:272–326](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L272-L326). Overlapping named procedures: RE11, RE12. Overlap is not whole-procedure certification.

## CH48 — Post-breakout Reset

Search strictly after confirmation (event + one microsecond) through Break open + timeframe, exclusive. Missing analysis returns null.

[Source engine/pipeline/reaction_engine.py:328–341](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L328-L341). Overlapping named procedures: RE13. Overlap is not whole-procedure certification.

## CH49 — Unified refinement and Break reuse

Refine the opposite edge only if Break owns that edge. Reuse the Break as the next First only with required color and exact analysis; strict opposite-edge crossing in its later remainder disqualifies reuse. Reused geometry uses the full candle lower interval, earliest timestamp on extreme ties, and main open as intrabar start.

[Source engine/pipeline/reaction_engine.py:1781–1851](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L1781-L1851). Overlapping named procedures: RE78, RE79. Overlap is not whole-procedure certification.

## CH50 — Direct post-Reset search

Scan First indices from Reset + 1 through the inclusive end. Skip indices through the blocked frontier and require the color transition. Return the first completed candidate in First order with the earlier-pending flag; invalidation advances the blocked frontier through its index. No completion returns null and pending true.

[Source engine/pipeline/reaction_engine.py:1960–1991](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L1960-L1991). Overlapping named procedures: RE84. Overlap is not whole-procedure certification.

## CH51 — Geometry-only post-Reset search

This path ignores lifecycle invalidation. First indices ascend, followed by candidate scan from First + 1 through the inclusive limit. Return first strict geometrical completion after refinement. Cache lookup includes direction, Reset and limit; cached Break index list is tied to append-only stream length.

[Source engine/pipeline/reaction_engine.py:1993–2066](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L1993-L2066). Overlapping named procedures: RE85, RE86, RE87. Overlap is not whole-procedure certification.

## CH52 — Initial Unified continuation

Commit initial Reaction and advance to Break + 1. Optional stop-after-First threshold includes equality. Post-confirmation Reset uses the exact analyzed edge, not the expanded public box, with main fallback when analysis is missing. Record exact pending Break Reset, or reuse candidate through the shared rule.

[Source engine/pipeline/reaction_engine.py:2434–2515](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L2434-L2515). Overlapping named procedures: RE97. Overlap is not whole-procedure certification.

## CH53 — Unified Reset race

Pending Reset or strict confirmed-edge penetration initiates Reset; competing candidate confirmation is resolved by lower-position race. Winning Reset uses pending Reset index or current main index. Optional cursor captures pre-Reset state and last Reset from-First prevents duplicate publication.

[Source engine/pipeline/reaction_engine.py:2517–2575](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/reaction_engine.py#L2517-L2575). Overlapping named procedures: RE98. Overlap is not whole-procedure certification.

## CH54 — Double-stop candidate

An invalid Blue pairs with the last calculation-valid Blue. First crossing of prior source level is sought from invalid Blue formation time to its source candle end exclusive; crossing must belong to that same main candle. Reaction confirmation is at or after trigger, First no earlier than formation. Successful formation consumes the previous pointer.

[Source engine/pipeline/a_zone_detector.py:274–335](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L274-L335). Overlapping named procedures: A12. Overlap is not whole-procedure certification.

## CH55 — Pair expiry

Missing prior stop returns null. A stop strictly after expires_at is rejected; equality is allowed.

[Source engine/pipeline/a_zone_detector.py:337–364](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L337-L364). Overlapping named procedures: A13. Overlap is not whole-procedure certification.

## CH56 — Inherited continuation level

Previous formation must precede current formation. Chained case needs previous exact stop strictly before current formation and both lines not behavior-internal. Nonchained previous Scale is excluded. Start at previous stop main time for chained, otherwise prior formation. First strictly later than start; Break strictly before current formation. Chained range includes whole Break candle; nonchained ends at Break open, inclusive under range helper.

[Source engine/pipeline/a_zone_detector.py:533–590](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L533-L590). Overlapping named procedures: A16. Overlap is not whole-procedure certification.

## CH57 — First A stop ownership

Start at next main candle after source, end exclusive. If first strict stop precedes not_before it is not owned by this lifecycle; a later recross cannot substitute. Equality to not_before is valid.

[Source engine/pipeline/a_zone_detector.py:813–836](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L813-L836). Overlapping named procedures: A22. Overlap is not whole-procedure certification.

## CH58 — A dirty frontier and crossing cache

Settled event is strictly before dirty; settled Reaction window additionally ends no later than changed Reaction time. Prior confirmation or Reset formation reused only with settled main time. Prior crossing reused when bounded end <= dirty or old hit < dirty and lower-presence unchanged. Unchanged lower evidence suppresses main fallback even if no suffix lower rows remain. Otherwise resume according to prior lower presence and dirty.

[Source engine/pipeline/a_zone_detector.py:890–949](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/a_zone_detector.py#L890-L949). Overlapping named procedures: A25, A26, A27, A28, A29. Overlap is not whole-procedure certification.

## CH59 — Type-3 candidate race

Reset timestamps strictly after A stop and before deadline. Owner confirmation <= A stop; any first owner Reset <= A stop excludes. Boundary crossing starts at Reset timestamp inclusive, deadline exclusive, requires trend qualifier. Earliest exact crossing wins; equal timestamp retains earlier iteration winner.

[Source engine/pipeline/s_zone_detector.py:403–450](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L403-L450). Overlapping named procedures: S20. Overlap is not whole-procedure certification.

## CH60 — Type-4 candidate replacement

Trend confirmation strictly after A stop and before deadline; Break index >= A stop index. Rebuild candidate from A-stop main through Break main using candidate_source_last. Search starts max(confirmation,candidate event,A stop), ends min(deadline,next confirmation) exclusive. First crossing requires public valid Blue between candidate-source main and crossing inclusive; otherwise discard and next aligned Reaction rebuilds.

[Source engine/pipeline/s_zone_detector.py:453–532](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L453-L532). Overlapping named procedures: S21, S22. Overlap is not whole-procedure certification.

## CH61 — Pre-Order candidate partial first main

Initial candidate uses A-stop main through Order First inclusive. If lower remainder [exact A stop, stop main end) exists, restrict first main to that remainder and compare later whole main candles through First. Later candidate wins only strict improvement; tie retains A-stop remainder. Empty lower remainder retains original main candidate; missing A stop event defaults to main open.

[Source engine/pipeline/s_zone_detector.py:741–783](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L741-L783). Overlapping named procedures: S30. Overlap is not whole-procedure certification.

## CH62 — Qualification time

Aligned Reset Blue formation <= candidate crossing; ordinary trend confirmation must be strictly after behavior start and <= crossing.

[Source engine/pipeline/s_zone_detector.py:837–862](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/s_zone_detector.py#L837-L862). Overlapping named procedures: S34, S35. Overlap is not whole-procedure certification.

## CH63 — E continuation and cache frontier

Validate nonempty chronology and dirty main index in [0,length]. Dirty is changed main open or last main + timeframe. Retain previous caches only if first time and timeframe unchanged. Prior stop event at or after dirty or absent rewinds scanned frontier to min(previous scan,dirty); retained stop must be strictly before range end. Search resumes at max(start,scanned frontier). Extreme cache reused only when end main is strictly before dirty; new query includes end main.

[Source engine/pipeline/e_zone_detector.py:128–193](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L128-L193). Overlapping named procedures: E02, E03, E04, E05. Overlap is not whole-procedure certification.

## CH64 — E source heap and accepted order

Group candidates by source index. Heap key is minimum source time, minimum decision time and source index; only groups at or beyond frontier enter initial heap. Restore accepted prefix and active state from checkpoint. First accepted object at each equal source timestamp wins, including regenerated sources inserted out of order.

[Source engine/pipeline/e_zone_detector.py:1132–1189](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1132-L1189). Overlapping named procedures: E44, E45. Overlap is not whole-procedure certification.

## CH65 — E parent and child chronology

Index latest child decision per parent. Enqueue unique regenerated candidates. Reject missing or disowned S; after sequence reset, S source must be strictly later and A source no earlier. Prior E is strictly earlier source time. Rebuilt S source strictly after prior E and A source no earlier; exception preserves unconsumed red S predating blue E.

[Source engine/pipeline/e_zone_detector.py:1191–1262](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1191-L1262). Overlapping named procedures: E44, E46, E47, E48, E49. Overlap is not whole-procedure certification.

## CH66 — E reopened race and dominance

Stop an E only with strictly later decision and strict directional price penetration. Reopen disowned-S-only Order when parent active; checkpoint path raises rewind, otherwise regenerate. Lower-priority S that stops active owner is blocked when owner is red or candidate blue and known child decision >= candidate decision.

[Source engine/pipeline/e_zone_detector.py:1287–1345](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/e_zone_detector.py#L1287-L1345). Overlapping named procedures: E44, E50. Overlap is not whole-procedure certification.

## CH67 — S donor precedence

Accepted red S directly reverses armed Blue when owner decision strictly precedes S decision; no prior price stop or Mode B required. Otherwise use frozen pending stop or armed stop strictly before S source. Red Mode B with completed Blue qualifies StopAll; retain pending completion otherwise.

[Source engine/pipeline/lifecycle_engine.py:422–474](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L422-L474). Overlapping named procedures: LC15, LC18. Overlap is not whole-procedure certification.

## CH68 — E donor precedence

Active StopAll with strict stop <= E decision qualifies. Multiple stopped active owners contribute highest number and earliest exact stop gate; remove stopped group and append new object. Otherwise pending or qualifying armed stop before E source with donor exception produces StopAll1; else accept E. Optional checkpoint follows each ordered event.

[Source engine/pipeline/lifecycle_engine.py:475–523](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L475-L523). Overlapping named procedures: LC15, LC19. Overlap is not whole-procedure certification.

## CH69 — StopAll replay frontier

Dirty index in [0,length]; cap dirty by prior covered horizon (last lower timestamp + one microsecond). Unchanged event prefix requires identical kind and repr, and max(source,decision) < dirty. Restore checkpoint prefix. Prior resolved stop strictly before dirty remains; otherwise re-resolve after dirty. Update observed covered horizon.

[Source engine/pipeline/lifecycle_engine.py:550–590](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L550-L590). Overlapping named procedures: LC23. Overlap is not whole-procedure certification.

## CH70 — Native Order stop

Start at max(requested start,range start) inclusive, end exclusive; no crossing caches null. Store exact lower stop separately from owning main time.

[Source engine/pipeline/order_audit_engine.py:1459–1484](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L1459-L1484). Overlapping named procedures: OA42, OA43. Overlap is not whole-procedure certification.

## CH71 — Gate-owned initial Order

First main equals parent-stop owning main. Confirmation and crossing must both be >= parent stop. Select earliest exact stop then Reaction First time. Separate route from E global race.

[Source engine/pipeline/order_audit_engine.py:1612–1632](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L1612-L1632). Overlapping named procedures: OA48. Overlap is not whole-procedure certification.

## CH72 — Carried creation windows

Ledger creation event strictly within (lifecycle decision,parent stop), confirmation <= parent stop, crossed >= parent stop. Indexed path deduplicates ordinals in insertion order. Initial A records instead use closed First main window [lifecycle decision,parent stop], same confirmation/stop bounds. Sort exact stop then descending First; absent lifecycle start returns empty.

[Source engine/pipeline/order_audit_engine.py:1722–1795](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L1722-L1795). Overlapping named procedures: OA52. Overlap is not whole-procedure certification.

## CH73 — Accepted-live initial view

Order stream key exact stop, confirmation, negative First. Initial view accepts stop strictly after confirmation; native geometry must have required types and consistent identity times, otherwise fall back to full authoritative scan. This clause covers initial view, not entire accepted stream.

[Source engine/pipeline/order_audit_engine.py:1879–1934](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/order_audit_engine.py#L1879-L1934). Overlapping named procedures: OA55, OA56, OA57. Overlap is not whole-procedure certification.

## CH74 — MBL activation and refresh

MBL stop is strict crossing strictly later than trigger. Activation takes complete main extreme from second behavior through gate inclusive and finds MBL stop from exact gate event. Refresh preserves existing record if resolved stop identity unchanged.

[Source engine/pipeline/PL_PH_detector.py:490–515](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L490-L515). Overlapping named procedures: P20, P21. Overlap is not whole-procedure certification.

## CH75 — Primary continuation dirty rewind

Require original timeframe and datetime dirty event. Rewind dirty frontier to owning main open if dirty lies inside that candle in old or new chronology; whole decision or trigger main participates in source price. Run new frontier with fresh Orders.

[Source engine/pipeline/PL_PH_detector.py:816–839](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L816-L839). Overlapping named procedures: P46. Overlap is not whole-procedure certification.
