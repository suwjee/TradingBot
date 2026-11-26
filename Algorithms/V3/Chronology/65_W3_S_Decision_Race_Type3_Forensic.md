# CP380 — S decision race and Type3 construction

Pinned source: `53460e68538ac790ab969084c1c7101e5ca833d7`; B04-06 870–1053. 419 category rows, 98 W1, 321 additional, 7 supplements; 2468 prior rows revalidated without overlap.

### W3 CP380 — S decision race and Type3 construction (S37–S38)

- **S37 (870–879)**: Decision receives independent candidate and Order stop levels, timing, ordinal, behavior start, optional candidate start and fallback flag.
- **S37 (880–889)**: Clamp lower start to range_start and exclude range_end via left bounds. Nonempty interval queries Order stop first, directly on lower index; exact bearish Order uses first_greater otherwise first_less. No null-index guard.
- **S37 (891–895)**: Candidate gate max(scan_start,candidate_start or scan_start) uses truthiness. Fallback mode sets gate and family fallback, defers qualification until after race.
- **S37 (896–911)**: Normal mode gets Reset Blue time only for valid ordinal and first sorted trend confirmation strictly after behavior_start. Keep nonnull qualifiers, not necessarily observed events.
- **S37 (912–926)**: No qualifiers means candidate_position None without query. Else earliest qualifier then max candidate gate; restricted lower bound and strict directional first index search, family blue.
- **S37 (927–934)**: Fallback mode performs first strict candidate query from qualified_start restricted to lower interval.
- **S37 (935–946)**: Both absent or same nonnull position returns None before fallback qualification. Equal timestamps at distinct positions are not same-position tie. Earlier Order position or absent candidate yields red mapped main position/time and event.
- **S37 (947–960)**: Assert surviving candidate nonnull; obtain lower timestamp. Fallback flag permits upgrade to blue via S34 then S35 short circuit, otherwise fallback family. Map main after qualification, return separate exact event.
- **S37 (962–972)**: Only empty lower interval enters main fallback. Start max(selected start, bisect_right(main times, original start)-1); inclusive selected end. Candidate strict predicate precedes optional gate event>=candidate_start. Order predicate evaluated independently.
- **S37 (973–978)**: Both main predicates true returns None before qualifier. Otherwise Order wins red with native Candle.index int and timestamp in both time slots.
- **S37 (979–988)**: Qualified candidate checks Reset Blue then ordinary confirmation after ambiguity/Order gates. Return blue on either, native Candle.index and main timestamp twice.
- **S37 (989–995)**: Unqualified candidate returns fallback only when flag; otherwise continue next main row, exhaustion None. Unlike normal lower qualifier gating, main ambiguity may be found before candidate qualified.
- **S38 (996–1015)**: Unpack caller A-stop and Type3 tuple; retain Reset owner ordinal/time; no recalculation.
- **S38 (1016–1026)**: Construct frozen slotted blue/type3 SZone with parent ordinal, native int parent index, parent source time, caller price and stop triple.
- **S38 (1027–1043)**: All Order provenance explicitly None, no physical Order creation.
- **S38 (1044–1053)**: Retain Reset ordinal/time and candidate/decision provenance unchanged, no extra price normalization or accepted lifecycle decision.

The native lower and main races have distinct admission and tie rules. This documents local source behavior, not runtime equivalence or accepted-ledger closure.
