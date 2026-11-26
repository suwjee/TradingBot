# CP355 — W3 Reaction breakout and race forensic review

Pinned main `c99b4c957e932d9ee70c492ca03ce80711447fc1`; Reaction source blob `9adffb832ffa231ba0cb01de507a30fbe62be0b0`, lines 235–327. Separate same-assistant source-first pass, not an independently staffed or blind audit.

PASS_SCOPED for RE09–RE12: 65 W1 rows, 229 additional category rows, 4 historical supplemental items, 31 source contract groups. Exact category/row/node/span joins plus manually derived source-group semantics and row roles; overlapping categories are not distinct rules or runtime paths.

- Green run: immediate predecessor must be at/above stage start and exactly GREEN; contiguous backward walk, then inclusive maximum with owner. No earlier disjoint run or upper-index guard.
- Breakout analysis: derive start index first, truthy intrabar_start overrides timestamp lookup; no local clamp. Strict lower high crossing inside half-open window; min Low through crossing inclusive. Map minimum timestamp to selected main owner, absent hit or owner returns None. No candidate mutation.
- Mode A invalidation: caller owns mode admission. Non-null anchor value precedes leg boundary. Main Low equality is not breach; main High equality is not breakout. Both main strict crosses trigger full nominal main interval lower queries, not intrabar start.
- Confirmed reset: caller owns main reset evidence; null candidate or main High <= top returns true. Otherwise both lower queries run before arbitration, as for invalidation. If both absent true; outward absent/breakout present false; outward present/breakout absent true; both present outward position <= breakout position. Same physical row gives outward priority; duplicate timestamp alone is not tie.
- Bounded Bullish, Bearish and unified consumers inspected: helpers return geometry/Boolean, callers own mutation, emission and continuation. Full state and mirror proof remain open.

CP355-F01 resolved scoped documentation precision in RE10–RE12. CP355-F02 open caller admission/mirror/state ownership. CP351-F03 through CP354-F03 remain open.

## Evidence

- [Local register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP355_W3_Race_Local_Forensic_Register.json)
- [Consumer boundary register](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP355_W3_Race_Consumer_Boundaries.json)
- [Completion](../../../Audit/Phase_07/Rebaseline_v2_8_7/CP355_Completion.json)

W3 INCOMPLETE; W4 NOT RUN. B02 reviewed 1–327 and 886–1369; complement 328–885 and 1370–2908. Continue from 328–689 (post-breakout reset, Bullish scan and mirror records) in complete adaptive partitions. No RAW payload, project runtime, ZIP, production or main change.
