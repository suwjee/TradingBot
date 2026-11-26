# W3 B03-07 — A source freeze and ordinary pair (CP372)

Pinned [source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/pipeline/a_zone_detector.py#L592-L733), blob 431934d2fb597238d5281a769c29fdb51747868b.

- G1 / A17 L592–605: Input trigger index and Reaction; intended exact freeze is conditional on lower coverage.
- G2 / A17 L606–609: Read trigger main timestamp by position before virtual A14; returned confirmation may be Break-open fallback; reversed range returns null before A08.
- G3 / A17 L610–612: A08 inclusive extrema, reorder price/index/time to index/time/price; empty lower coarse containing-main fallback may contain later prices.
- G4 / A18 L613–619: Fresh local output, cycle=-1, reuse=null, offset=0; no supplied state-list validation.
- G5 / A18 L620–626: Adjacent valid-state pair; bridge iff nonnull retained ordinal equals previous ordinal, not physical identity.
- G6 / A18 L627–638: Current consumed condition first, otherwise previous consumed and not bridge. Clear reuse only on skipped bridge pair; advance one.
- G7 / A18 L639–647: Expiry from next-next valid state formation, not full Blue ordinal. Null virtual trigger advances without clearing reuse.
- G8 / A18 L648–658: Unpack eight trigger fields including effective stop main times distinct from actual state.
- G9 / A18 L659–665: A15 exact trigger and max effective stop mains inclusive First gate; null match breaks whole loop. Original Reaction retained.
- G10 / A18 L666–671: Null A17 advances without clearing reuse; success unpacks source then converts Break index.
- G11 / A18 L672–682: Virtual A21 before append; retain original line source times, full ordinals, effective stop mains and actual state stop levels.
- G12 / A18 L683–699: Frozen continuation, trigger, matched ordinal; fresh First positional read, Break timestamp using converted Break; source tuple; required reads may fail before append.
- G13 / A18 L700–712: Route ordinary; copy exact stop only on actual/effective main equality, not causal proof. Append before cycle update.
- G14 / A18 L713–716: Set frontier to matched Break, recompute virtual A14 and A07 strict stop from returned confirmation unbounded. Failure after local append propagates; no partial list returned.
- G15 / A18 L717–725: Reuse iff stop nonnull, next-next state exists and formation>=exact stop; equality allowed. Retain current ordinal then advance one.
- G16 / A18 L726–733: Else clear reuse and skip while offset in bounds and formation<=new Break. No unconditional increment; if previous formation>Break, offset may remain unchanged. Native invariant conditional, arbitrary state termination not proven. Return detection-order list.

297 canonical rows, 72 W1, 225 additional, six historical supplements. Prior attempt ended at tool-call limit; parent has no CP372 files. Reconstructed source-derived evidence. CP372-F01 documentation resolved. CP372-F02 OPEN: No unconditional increment at 726–731. Under coherent ordered main chronology, valid formation mapping, actual stops not earlier than their formations, crossing at/after start, aligned Reaction confirmation within its own Break main and unchanged caches, each successful route has trigger at/after previous formation: inherited/early formation route starts current formation (later than previous under inheritance; early guard plus actual previous stop), early actual-stop starts current stop; remaining route uses later actual stop or crossing from it. Then matched confirmation>=trigger implies Break position>=previous formation. This is a sufficient conditional argument, not proof of all native creator/consumer, duplicate time, gap/position, fallback or live cache invariants. Retain OPEN, not proven runtime defect.

[Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP372_W3_A_Source_Ordinary_Pair_Local_Forensic_Register.json) · [Consumer boundaries](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP372_W3_A_Source_Ordinary_Pair_Consumer_Boundaries.json) · [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP372_Completion.json).
