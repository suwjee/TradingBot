# CP374 — W3 Live A History and B03 local exact union

Pinned main: `c99b4c957e932d9ee70c492ca03ce80711447fc1`. Source: `engine/pipeline/a_zone_detector.py`, blob `431934d2fb597238d5281a769c29fdb51747868b`, lines 848–1070, A24–A39. Source-only independent review, no RAW or Runtime.

- **G1 / declaration / 848–851:** Two aliases describe event triple and heterogeneous key type; they do not allocate trading events or normalize values.
- **G2 / declaration / 852–862:** Mutable slotted history with nine independent dictionary factories: confirmations, reset formations, crossings (hit/availability pair), extremes, matches (ordinal/null), inherited stops, triggers, sources (nullable), and zones. Per-instance allocation, not shared class dictionary.
- **G3 / declaration / 863–867:** Live detector extends ordinary detector; class declaration and descriptive text do not themselves replay an event.
- **G4 / A24 / 868–869:** Construction receives the caller-owned ordered inputs and allocates a fresh current history before inherited initialization.
- **G5 / A24 / 870–872:** Prior nonnull detector supplies the prior history by reference, otherwise allocate a separate empty history; set dirty before base initialization. Base A01 constructs confirmation times via virtual A27 after setting direction, reactions and candle times, before prefix attributes exist.
- **G6 / A24 / 873–875:** Create a new list of First-main, Break-main, confirmation timestamp triples in reaction input order; zip truncates to shortest input, no sorting, no full geometry or physical identity comparison.
- **G7 / A24 / 876–878:** Old inputs reference prior triple list if prior exists, otherwise empty list. Initialize same flag by length equality and common-prefix count to zero.
- **G8 / A24 / 879–883:** Compare old/new zipped triples in native order; first unequal tuple sets same false and breaks, equal pairs increment prefix only. Length change alone leaves same false even if shared prefix equal.
- **G9 / A24 / 884–889:** Traverse old and new suffixes after common prefix; take min of element 1 (Break main timestamp), default null for empty suffixes. Changed First/confirmation with same Break still uses Break; no changed-geometry proof from equal triples.
- **G10 / A25 / 890–892:** Dirty null short-circuits false; nonnull event strictly earlier than dirty is settled. Equality not settled; timestamp comparison failures propagate.
- **G11 / A26 / 893–897:** Evaluate A25 first; require changed Break absent or end at/before it. Changed Break equality allowed only when end strictly precedes dirty.
- **G12 / A27 / 898–902:** Read integer Break index, direction-specific confirmation-side raw box level (top bullish, bottom bearish), key index and native string spelling; select current confirmation dictionary. Constructor dispatch requires no prefix state.
- **G13 / A27 / 903–908:** Current membership first (including returned fallback); only on miss evaluate indexed main-open settlement and prior membership. Reuse prior value or invoke base A14 (provider with intrabar start disabled); write selected confirmation and return current indexed value. Guard is main open, not hit event.
- **G14 / A28 / 909–911:** Reset formation key combines supplied source index and native string of broken level.
- **G15 / A28 / 912–917:** Prior reuse only when source main open is strictly settled and key exists; otherwise base A10. Always store selected result in current dictionary; no current lookup shortcut. No exact event-time revalidation.
- **G16 / A29 / 918–920:** First crossing key uses string level and original start/end; preserves null unbounded end and does not replace key when resuming.
- **G17 / A29 / 921–925:** Current membership wins, returning cached hit element including null before provider access. On miss obtain current full-window lower bounds and calculate availability as left strictly less than right.
- **G18 / A29 / 926–930:** Read old crossing pair or absent sentinel, retain dirty and original scan start. Prior consideration requires nonnull pair, nonnull dirty and original start strictly before dirty; unpack old hit and old availability only inside gate.
- **G19 / A29 / 931–936:** Return whole old pair if bounded end <= dirty, irrespective of changed availability, OR old hit nonnull with hit timestamp strictly before dirty and matching old/current lower availability. Short-circuit order matters; bounded null hit retained.
- **G20 / A29 / 937–943:** Compute dirty lower position using left insertion index, clamp by right. Old lower availability plus strictly nonempty unchanged lower prefix suppresses main fallback; exhausted suffix stores (null,true) and returns immediately.
- **G21 / A29 / 944–946:** If unchanged lower prefix survives with suffix remaining, resume from dirty. Otherwise resume dirty only if old and current both lack lower rows; when neither branch applies keep original start.
- **G22 / A29 / 947–950:** Invoke inherited first-crossing with selected scan start and original end; write under original full query key with current FULL-window availability, not suffix availability. Preserve native strict direction and fallback; no arbitrary-edit equivalence proof.
- **G23 / A30 / 951–952:** Extreme key uses exact start/end timestamps without normalization.
- **G24 / A30 / 953–960:** Prior settled-end plus membership takes priority over current cache; otherwise current hit returns directly; otherwise base A08. Store prior/base result in current. Not the A27/A29 lookup order.
- **G25 / A31 / 961–964:** Reaction match key includes exact trigger and optional not_before. Read prior ordinal/null before checking current dictionary, so a failed prior lookup can precede current hit.
- **G26 / A31 / 965–970:** Current key wins even if null; else reuse positive native prior ordinal at/before common-prefix count; else retain prior null only for actual old membership and same timestamp triples. No previous object retained as result.
- **G27 / A31 / 971–977:** Base A15 rescan begins at common prefix when prior key exists (including null), else zero. Native A15 inclusive confirmation/First gates, ordered-search eligibility and linear fallback remain owner rules. Keep returned ordinal or null.
- **G28 / A31 / 978–980:** Write match ordinal/null; nonnull returns pair with CURRENT reactions[ordinal-1], not the previous object. No new bounds or physical identity test.
- **G29 / A32 / 981–988:** Static Blue key contains formation index/time, stop index/time/event time, native string stop level and event extreme (null string included), original kind and bool internal default false. No ordinal, drawing field, calculation-valid flag, or line object identity in key; key hashability remains native.
- **G30 / A33 / 989–991:** Evaluate previous then current Blue key to form inherited-stop key; local key construction may raise before guard.
- **G31 / A33 / 992–998:** Reuse prior inherited stop including null if current formation passes settled reaction window and key exists; else base A16 (which can virtually dispatch A30). Always write current; no current lookup shortcut.
- **G32 / A34 / 999–1000:** Pair trigger key evaluates both Blue keys and expiry, including null expiry.
- **G33 / A34 / 1001–1007:** Require nonnull expiry, current formation settled reaction window, then all nonnull expiry/previous formation/previous stop event/current stop event strictly settled; generator filters null events and all short-circuits. Finally require prior key membership. Does not separately reject null stop event in this reuse guard.
- **G34 / A34 / 1008–1013:** Reuse prior trigger including null or invoke base A13 (native virtual A33/A29/A30). Store current result and return; no current-first shortcut, no unconditional expiry-null reuse.
- **G35 / A35 / 1014–1016:** Compute confirmation via virtual A27 before looking up source; source key is trigger index and returned confirmation, not entire Reaction identity.
- **G36 / A35 / 1017–1025:** Require confirmation settled, indexed trigger main-open settled and prior source key; nullable source can be reused. Otherwise call A17, which queries confirmation again and may virtually use A30. Write current result; no current source membership lookup.
- **G37 / A36 / 1026–1031:** Zone key uses keyword insertion order and replaces Decimal instances with native as_tuple sign/digits/exponent; other values retained without sorting/coercion. Representation distinctions including signed zero and exponent survive, unlike numeric equality.
- **G38 / A36 / 1032–1036:** Look up only prior zones. Null/missing allocates via A21; assign selected same-object or new record to current key then return. Current key is not consulted on repeated calls; key hash/type/construction/assignment errors propagate.
- **G39 / declaration / 1037–1041:** Separate continuation wrapper class describes replay from first mutable main with revised upstream inputs; no cache or publication occurs at class declaration.
- **G40 / A37 / 1042–1047:** Store direction; construct fresh live detector with null previous and dirty; detect before assigning result then detector on the new wrapper. Constructor failures do not produce a successfully constructed wrapper.
- **G41 / A38 / 1048–1051:** Result property returns new list of retained records, not deep copies; physical zone references retained. Copy allocation failure propagates.
- **G42 / A39 / 1052–1055:** Capture old detector; validate exact timeframe equality first; mismatch raises before dirty-index gate or new detector construction.
- **G43 / A39 / 1056–1057:** Inclusive dirty-index admission from zero to min(old candle count,new candle count). No exact-int validator; native comparisons and subsequent indexing govern failure.
- **G44 / A39 / 1058–1062:** Minimum available old/new main open at dirty position; each time array tested independently. Default is new last timestamp plus timeframe or null for empty new times; default evaluated eagerly before min consumes candidates. No implicit index clamp or normalization.
- **G45 / A39 / 1063–1066:** Construct candidate detector with retained direction, revised inputs, old detector and computed dirty time; perform detection before replacing wrapper fields. No explicit catch; external provider/input aliases are not transactional.
- **G46 / A39 / 1067–1068:** Replace candidate prior-history reference with fresh history before tuple assignment publishes candidate detector and result to wrapper. Prior/current history release is reference replacement, not a deep rollback of shared external state.
- **G47 / A39 / 1069–1070:** Return result property (fresh shallow list) after wrapper publication. Post-publication copy failure does not roll back; a pre-publication detection failure retains old wrapper fields but does not guarantee external alias rollback.

## Reconciliation

959 canonical records (198 W1, 761 additional), 16 historical supplements. Prior CP369–373 exact direct row join: 2,211 unique records; 0 identity/operation/span/W1 link errors after resolving comprehension filter IDs. Canonical complement exactly 959 in 848–1070. A exact union 3,170/3,170 (708 W1, 2,462 additional), 53 historical supplements. Blue CP368 1,524/1,524, 24 supplements. B03 4,694/4,694 local, 77 supplements. Cross-owner remains independent; no whole W3 acceptance.

## Open obligations

CP351-F03, CP352-F03, CP353-F03, CP354-F03, CP355-F02 and CP372-F02 remain OPEN. CP372-F02 concerns conditional native A18 progress with chronology and cache freshness, not a demonstrated runtime defect. Preserve CP350 registers, prior W1/W2 scope, and all historical evidence. See local forensic register and consumer boundaries.
