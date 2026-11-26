# CP343 — W2 Bridge orchestration and Primary projection queue reconciliation

Pinned source `c99b4c957e932d9ee70c492ca03ce80711447fc1`, blob `e1e65ba960c5f726f9a05e2ab89e4457b65e5735`. W2 NOT_ACCEPTED. Nine direct records; Bridge queue 45/45 across CP341–343.

## CP323-P27 — TB76 Blue/A dependency and selection

Blue required if any Blue/A/S exactly enabled, A required if A/S enabled. Reusable context selects full stored records by inclusive int source index; native fallback calls full-result Blue then A with current Blue list and full chronology, no explicit source clipping in these branches. Disabled requirements yield empty. Opposite direction and local range read before flags.

Handoff: If S enabled later, eligible A overrides earlier selected A, candidate/accepted S distinct under reusable context. No claim that range-clipped A enters final S calculation; visible clipping and native full context are separate.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L2837-L2895). B09 overlap occurrences: 32.

## CP323-S32 — TB79 legacy path

Direction result read; falsy bridge_output incl missing selects direct legacy. Timed Reaction serialization calls published candidate transform on selected raw pairs; direct Blue flag and visible bounds, A flag independent, S/E/StopAll passed through from visibility. Audit gated by map membership, not retrieved value non-null; legacy malformed detector key with None differs from additive branch.

Handoff: No additive projection callback when disabled. Same valid-state selection contract is not arbitrary malformed-state equivalence; no empirical byte equality asserted.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3113-L3175). B09 overlap occurrences: 23.

## CP329-S26 — TB64

Recursively copy list/dict even offset zero; exact int nonnegative value under index or suffix Index adds offset (bool/int subclasses excluded). Otherwise exact physicalOrderIdentity/resetReactionIdentity list/tuple converted to list; eligible components offset independently, others unchanged without recursive special-route traversal. Other ordinary tuple/scalar unchanged.

Handoff: IDs/epoch/Decimal strings not generally rewritten. This projection does not mutate calculation-local records; upstream already-absolute identity strings separate.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1860-L1871). B09 overlap occurrences: 29.

## CP329-S27 — TB65

Source from transition.index main array; icon actual source+49 main candle if upper bound valid (no lower guard), not extrapolated or clipped to visible end. Direction absent defaults bullish, exact bullish selects previous bearish/ph fields/icon High, others previous bullish/pl/icon Low. Absolute source/icon and stopped-point source index add offset; ID direction:trend:source epoch and level native string.

Handoff: Exact event time distinct from source main, transition.high retains neutral stopped point even on bullish reversal. Caller owns valid transition index and role, no extra confirmation or selection.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L1874-L1894). B09 overlap occurrences: 26.

## CP329-S28 — TB80–81

Construct transform once, select raw/public Reaction pairs and resets once, pass selection to legacy serialize bypassing repeat transform. Blue selected by display flag and inclusive source; A flag independent; S/E/StopAll references from visibility. Get audit detector, nonnull gate sort prepared rows by main First/Break. Build legacy arrays then bridgeOutput from same object selections; legacy audit sorts output again, stable ties. Preselected Blue passed without bounds.

Handoff: Additive view may call existing owner stop services, not new detectors/trading selection. No cross-route identity replacement. Legacy-only map membership differs on malformed state.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3176-L3251). B09 overlap occurrences: 28.

## CP329-S29 — TB82–83

Order ownerDirection independent of physical direction. types fixed parent-stop=>Order_A then reset-leg=>Order_B by membership, no unknown type or duplicate type; causes list preserves order/duplicates. auditCauses maps each top-level datetime to epoch, Decimal to str, other incl nested unchanged. Direct native First/Break/stop source/hit indexes fetch main timestamps; exact event fields independently epoch; box values explicit nonnull guards.

Handoff: Read immutable snapshot/copies relabeled by native owner; serializer doesn't revalidate stop, price or horizon, and does not recursively normalize audit metadata.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3254-L3280). B09 overlap occurrences: 28.

## CP329-S30 — TB84–86

Import native resolution/relabel/leg services; direction default absent bearish; exact bullish final lows else highs through market.end_index. Falsy cycles fallback singleton; first cycle ID. cycle_identity truthy value/offset, exact four parts token cycle then int-offset donor indices. Point relabel against final primary, origin truthy identity_source or actual point; ID origin kind/number/absolute trigger/decision, suffix nonnull different origin cycle. Actual row uses winner geometry/number and local indices, row cycle independent, owner bearish PH else bullish. Selection source inclusive then decision<=end.

Handoff: Physical role reconciliation native P06 and label P08 separate from display. No new mutation of native point or ledger; invalid cycle strings can propagate conversion error.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3283-L3326). B09 overlap occurrences: 52.

## CP329-S31 — TB84 / MB-M03

Visible cycles MBL nonnull and trigger<=end. Formed leg generator separately requires primary confirmation within end (earliest exact decision), not additional visible-source clip. ID reference/second absolute, row local; cap source+400 actual full main candle else extrapolate last+TF*(source+401-count). No cap by visible end here; reversal may clip later. Optional stop fields each gate nonnull stop index<=end (equality/zero allowed); actual stop event assumed valid when index present.

Handoff: Calculation MBL activation/own strict stop and display cap distinct; activated unconfirmed cycle can still be visible for status but not formed MBL output.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3327-L3358). B09 overlap occurrences: 49.

## CP329-S32 — TB84 cycle/post-secondary

Highs native if bullish else final, lows final if bullish else native. Main lookup local index/serialized source epoch last-wins; cycleIds original main points matching source/index and decision<=end with nonnull cycle IDs, stable dedup. Visible cycle with id: highCount always invokes selected projection; lowCount bullish invokes selected cycle lows, bearish counts emitted lows with cycleId. main-side IDs join existing by_source, decision horizon and dedup. Post-orders traverse cycles/list in order, skip stop_index>end, relabel and owner opposite, optional cycleId; no global dedup. Status last visible cycle else qualified exact time<horizon waiting break, equality/later/null waiting matching. Return role-specific postPH3/postPL3 key.

Handoff: Asymmetric count evaluation preserved; no implicit mirror correction. Distinguish native global post_orders dedup from per-cycle serialization; epoch pair is display key, not native exact datetime identity.

[Pinned source](https://github.com/suwjee/TradingBot/blob/c99b4c957e932d9ee70c492ca03ce80711447fc1/engine/bridge/trading_pipeline.py#L3359-L3402). B09 overlap occurrences: 69.

## Findings

- CP343-F01: Detailed TB76, TB64–65, TB79–86 and MB-M03 already distinguish native eligibility, current horizon, exact identity and display projection. Preserve asymmetric cycle counts and per-cycle post-secondary output.
- CP343-F02: 45/45 Bridge queue IDs reviewed; historical matrix intersections and other explicit or implicit handoffs still require closure-level semantic reconciliation. No runtime equivalence or W2 acceptance.

CP344 / W2 Live Pipeline queue semantic reconciliation: CP323-S42 (22–70) and CP330-S24 (73–85) against pinned live_pipeline.py, W1/B10 and active Live Bridge/Transport/RAW contracts, conditional callbacks and rollback. Then independent CP331-F05 / CP333-R01/R02 semantic closure assessment; W2 not accepted.
