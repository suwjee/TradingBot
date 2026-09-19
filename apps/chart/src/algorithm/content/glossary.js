const normalizeGlossaryEntry = (term, code, en, fa) => {
  if (term === "Mode B") {
    en = "A continuing Reaction after an unreset confirmed owner. BoxTop uses the running peak and BoxBottom begins at top_source + 1 only when that source precedes FirstRed; otherwise it starts inclusively at FirstRed.";
    fa = "Reaction ادامه‌دار پس از مالک تأییدشده و بدون Reset است. BoxTop از running peak می‌آید و BoxBottom فقط وقتی از top_source + 1 شروع می‌شود که منبع قبل از FirstRed باشد؛ در غیر این صورت شروع آن روی FirstRed inclusive است.";
  }
  if (term === "BlueState") {
    en = "A private A-module record for a calculation-valid Blue: blue/reaction/formation/source indices and times, main-candle end, first strict stop event/time/extreme, and ordinal. Deadline is derived locally from the next state; it is not a BlueState field or Bridge collection.";
    fa = "رکورد داخلی ماژول A برای Blue معتبر محاسباتی شامل index/timeهای Blue، Reaction، formation و source، پایان کندل اصلی، اولین stop strict و ordinal است. deadline از state بعدی به‌صورت محلی به‌دست می‌آید و fieldِ BlueState یا collectionِ Bridge نیست.";
  }
  if (term === "First exact event") {
    en = "When events share a main candle, the maintained module rule decides chronology: Reaction invalidation/Reset checks the strict Low event before strict High confirmation; S rejects same-finest-candle candidate/Order ties. Coexisting bullish Blue stops use higher stop level first at an exact event, then the second stop triggers and the first supplies continuation level.";
    fa = "وقتی رویدادها در یک کندل اصلی مشترک‌اند، قانون همان ماژول ترتیب را تعیین می‌کند: در Reaction ابتدا Low strict برای invalidation/Reset و سپس High strict برای confirmation بررسی می‌شود؛ S در tie یک finest candle خروجی نمی‌دهد. در stop دقیق هم‌زمان Blue صعودی، stop level بالاتر اول است، stop دوم trigger و stop اول continuation level را می‌دهد.";
  }
  if (term === "Direct Order") {
    en = "The published complete opposite Reaction geometry after the parent gate; bounded direct geometry is a fallback only when the published candidate has no strict stop.";
    fa = "هندسه کامل Reaction مخالف پس از gate والد؛ هندسه مستقیمِ bounded فقط وقتی fallback است که candidate منتشرشده stop strict نداشته باشد.";
  }
  if (term === "Fixed point") {
    en = "Repeat Bridge E/StopAll reconciliation while recomputing S visibility from current E, comparing only {source_time:number}; equality returns the result, while a repeated map raises ValueError('E/StopAll lifecycle reconciliation did not converge').";
    fa = "reconciliation مربوط به E/StopAll را با بازسازی visibilityِ S از E فعلی تکرار کن و فقط {source_time:number} را مقایسه کن؛ برابری خروجی را برمی‌گرداند و map تکراری ValueError می‌دهد.";
  }
  return { en, fa };
};

const entry = (term, code, en, fa, usedIn) => {
  ({ en, fa } = normalizeGlossaryEntry(term, code, en, fa));
  return Object.freeze({
  term,
  code: Object.freeze(code),
  en,
  fa,
  usedIn: Object.freeze(usedIn),
  });
};

// Only aliases used by the explanatory pseudocode belong here. The right-hand
// side names are the maintained Python/Bridge names, not a second vocabulary.
export const GLOSSARY_ENTRIES = Object.freeze([
  entry("Main Candle", ["candles", "self.candles"], "The candle stream at the selected analysis timeframe.", "کندل‌های تایم‌فریم انتخاب‌شده که محاسبه اصلی روی آن‌ها جلو می‌رود.", ["All families"]),
  entry("Lower Candle", ["seconds", "one_second_candles", "self.seconds", "self.lower"], "The finer candle stream used to decide the exact order of strict events inside a main candle.", "کندل ریزتر برای تعیین ترتیب دقیق رویدادهای strict داخل یک کندل اصلی.", ["Reaction", "Reset", "Blue Line", "A", "S", "E", "StopAll"]),
  entry("GREEN candle", ["Candle.tag == 'GREEN'", "open <= close"], "A candle whose Open is less than or equal to Close; doji is GREEN.", "کندلی که Open آن کوچک‌تر یا مساوی Close است؛ دوجی هم GREEN محسوب می‌شود.", ["Reaction", "Blue Line"]),
  entry("RED candle", ["Candle.tag == 'RED'", "open > close"], "A candle whose Open is greater than Close.", "کندلی که Open آن بزرگ‌تر از Close است.", ["Reaction"]),
  entry("Mode A", ["Candidate.mode == 'A'", "Reaction.mode == 'A'"], "The first Reaction of the selected range or a fresh post-Reset leg. Its frozen outer leg boundary can invalidate it before confirmation.", "اولین Reaction در بازه انتخابی یا لگ تازه پس از Reset؛ مرز بیرونی ثابت لگ می‌تواند پیش از تأیید آن را باطل کند.", ["Reaction", "Blue Line", "S Order", "E Order"]),
  entry("Mode B", ["Candidate.mode == 'B'", "Reaction.mode == 'B'"], "A continuing Reaction after an unreset confirmed owner. Its BoxTop comes from the running peak and its BoxBottom begins after that peak source.", "Reaction ادامه‌دار پس از مالک تأییدشده‌ای که Reset نشده؛ BoxTop از سقف جاری و BoxBottom از بعدِ کندل منبع همان سقف آغاز می‌شود.", ["Reaction", "Blue Line", "S Order", "E Order"]),
  entry("First", ["first_idx", "first_time", "FirstIndex", "FirstTime"], "The first required-color candle that owns one Reaction or physical Order geometry.", "اولین کندل با رنگ لازم که مالک هندسه یک Reaction یا Order فیزیکی است.", ["Reaction", "S", "E", "Order Audit"]),
  entry("FirstRed", ["first candle where tag == 'RED'", "first_idx"], "The bullish friendly name for a Reaction First candle; it must satisfy the active Mode-A or Mode-B context.", "نام سادهٔ کندل First در روند صعودی؛ این کندل باید زمینهٔ فعال Mode A یا Mode B را رعایت کند.", ["Reaction"]),
  entry("BoxTop", ["box_top", "box_top_source_idx", "box_top_source_time"], "The frozen upper Reaction boundary and the provenance of the candle that supplied it.", "مرز بالایی ثابت Reaction و منبع کندلی که آن را ساخته است.", ["Reaction", "Order geometry"]),
  entry("BoxBottom", ["box_bottom", "box_bottom_source_idx", "box_bottom_source_time"], "The lower Reaction boundary and its source; in a bullish candidate it may move lower until the exact Break.", "مرز پایینی Reaction و منبع آن؛ در کاندید صعودی تا Break دقیق می‌تواند پایین‌تر به‌روزرسانی شود.", ["Reaction", "Reset", "Order geometry"]),
  entry("Break", ["break_idx", "break_time", "breakout_analysis"], "The first strict confirmation of a Reaction box. The public time is the main candle; lower data supplies exact intrabar chronology.", "اولین تأیید strict باکس Reaction؛ زمان عمومی کندل اصلی است و داده lower ترتیب دقیق داخل کندل را تعیین می‌کند.", ["Reaction", "Order geometry"]),
  entry("Scale Strike", ["ScaleStrike", "count_scale_strikes", "_intrabar_pending_confirmation"], "A new strict Fibonacci penetration. Its pending extreme can be replaced by a more directional value and is confirmed by any same or later required-color candle; bullish GREEN includes doji. A pending strike at Reaction end uses the lower-second Break fallback.", "نفوذ strict تازه در فیبوناچی؛ extreme معلق می‌تواند با مقدار جهت‌دارتر جایگزین و با هر کندل هم‌رنگِ لازم در همان لحظه یا بعدتر تأیید شود؛ GREEN صعودی دوجی را هم شامل می‌شود. strike باقی‌مانده تا پایان Reaction از fallback lower-second در Break استفاده می‌کند.", ["Blue Line Scale"]),
  entry("Scale Blue", ["BlueLine.kind == 'scale'"], "A Blue Line emitted when confirmed strike count strictly grows and the spacing lock is open; its line price is one third of the source candle range.", "Blue Lineای که با افزایش strict تعداد strike و بازبودن قفل فاصله ساخته می‌شود؛ قیمت خط یک‌سوم بازه کندل منبع است.", ["Blue Line"]),
  entry("Reset Blue", ["BlueLine.kind == 'reset'"], "A Blue Line derived from an owned Reaction Reset; its price is one fifth of the Reset candle range and it may remain internal when calculation_valid is false.", "Blue Line ساخته‌شده از Reset متعلق به Reaction؛ قیمت آن یک‌پنجم بازه کندل Reset است و در حالت calculation_valid=false می‌تواند فقط داخلی بماند.", ["Blue Line", "A"]),
  entry("BlueState", ["a_detector.BlueState", "ADetector._build_blue_states"], "A private A-module view of a calculation-valid Blue with exact formation, first strict stop, ordinal, and deadline. It is not a Bridge collection.", "نمای داخلی ماژول A از Blue معتبر همراه زمان تشکیل، اولین stop strict، شماره و deadline؛ این آبجکت collection عمومی Bridge نیست.", ["A"]),
  entry("Continuation level", ["AZone.continuation_level", "continuation_source_index", "continuation_source_time"], "The frozen directional level used by an A trigger path, together with the source that supplied it.", "سطح جهت‌دار ثابتی که یکی از مسیرهای trigger در A استفاده می‌کند، همراه منبع سازندهٔ آن.", ["A"]),
  entry("Order_A", ["order.mode == 'A'", "SZone.order_mode == 'A'", "EZone.order_mode == 'A'"], "An opposite Reaction used as an Order whose stop level comes from the complete Mode-A leg extreme through Break.", "Reaction مخالفی که به‌عنوان Order استفاده می‌شود و سطح stop آن از extreme کامل لگ Mode A تا Break می‌آید.", ["S", "E", "Order Audit"]),
  entry("Order_B", ["order.mode == 'B'", "SZone.order_mode == 'B'", "EZone.order_mode == 'B'"], "An opposite continuing Reaction used as an Order; in the bullish path its stop level normally inherits the previous opposite Reaction BoxTop.", "Reaction ادامه‌دار مخالف که به‌عنوان Order استفاده می‌شود؛ در روند صعودی سطح stop آن معمولاً BoxTop ری‌اکشن مخالف قبلی است.", ["S", "E", "Order Audit"]),
  entry("Type 3", ["SZone.formation_type == 'type3'", "SDetector._first_type3"], "A protected blue S route from an eligible opposite Reset leg before the next Order confirmation. Its serialized Order fields are null.", "مسیر محافظت‌شدهٔ S آبی از لگ Reset مخالف واجدشرایط، پیش از تأیید Order بعدی؛ فیلدهای Order آن در خروجی null هستند.", ["S blue"]),
  entry("Family", ["SZone.color", "EZone.family"], "The blue/red ownership class used by S, E, and StopAll priority. For E, accepted parent ownership can reconcile the provisional value.", "کلاس مالکیت آبی/قرمز برای اولویت S، E و StopAll؛ در E مالکیت والد پذیرفته‌شده می‌تواند مقدار اولیه را اصلاح کند.", ["S", "E", "StopAll"]),
  entry("Parent stop", ["SDetector._first_a_stop", "EDetector._parent_stop", "parent_stop_event_time"], "The first exact strict crossing of the accepted parent's price after its decision; it opens the next lifecycle gate.", "اولین عبور strict دقیق از قیمت والد پذیرفته‌شده پس از تصمیم آن؛ این رویداد gate چرخه بعدی را باز می‌کند.", ["S", "E", "Order Audit"]),
  entry("Sequence reset", ["EDetector.sequence_resets", "reconcile_stopall_lifecycle"], "The map from an accepted StopAll source time to its number; it resets E active sequence state and is iterated to a fixed point.", "نگاشت زمان source هر StopAll پذیرفته‌شده به شماره آن؛ وضعیت دنباله فعال E را ریست می‌کند و تا نقطه ثابت تکرار می‌شود.", ["E", "StopAll", "Bridge"]),
  entry("Shadowed source", ["finalize_visibility", "e_source_indices", "stopall_source_indices"], "An A or S label hidden from presentation because accepted E or StopAll owns the same source index; required historical parents are restored before this filter.", "برچسب A یا S که چون E یا StopAll پذیرفته‌شده مالک همان source index است از نمایش حذف می‌شود؛ والد تاریخی لازم پیش از این فیلتر بازگردانده می‌شود.", ["Bridge"]),
  entry("Owner boundary", ["anchor_value", "leg_boundary_value"], "The frozen Mode-A boundary that owns the candidate and can invalidate it before confirmation.", "مرز ثابت Mode A که مالک کاندید است و می‌تواند پیش از تأیید آن را باطل کند.", ["Reaction Mode A"]),
  entry("Running peak", ["running_peak", "running_peak_src"], "The highest active bullish reference carried into Mode B.", "بالاترین مرجع فعال صعودی که وارد Mode B می‌شود.", ["Reaction Mode B"]),
  entry("Exact event", ["second_time", "trigger_event_time", "decision_event_time", "stop_event_time"], "The lower-candle timestamp used for chronological races; it is more precise than the main-candle time.", "زمان lower-candle برای رقابت زمانی؛ از زمان کندل اصلی دقیق‌تر است.", ["All strict races"]),
  entry("Strict crossing", ["low < level", "high > level", "_strict_stop"], "A boundary is crossed only with < or >. Equality never counts as a break or stop.", "عبور فقط با < یا > انجام می‌شود و برابری break یا stop نیست.", ["All families"]),
  entry("First exact event", ["breakout_analysis", "post_breakout_reset", "SDetector._decision"], "When two events share a main candle, the earlier lower-candle event wins; maintained tie rules are then applied. For coexisting bullish Blue stops at one exact event, higher stop level is first, the second stop supplies the trigger, and the first stop supplies continuation level.", "وقتی دو رویداد در یک کندل اصلی هستند، رویداد lower زودتر برنده است و سپس قانون tie همان ماژول اعمال می‌شود. در stop دقیقاً هم‌زمان Blue صعودی، stop level بالاتر اول است، stop دوم trigger را می‌دهد و stop اول continuation level را می‌سازد.", ["Reaction", "S", "E"]),
  entry("Reaction geometry", ["Candidate", "Reaction", "first_idx", "box_top", "box_bottom", "break_idx"], "The complete First/Box/Break shape reused as a physical Order identity by downstream modules.", "هندسه کامل First/Box/Break که ماژول‌های بعدی آن را به‌عنوان هویت فیزیکی Order استفاده می‌کنند.", ["Reaction", "S", "E", "Order Audit"]),
  entry("Physical Order identity", ["(first_index, reaction.break_idx)", "order_audit[(first_idx, break_idx)]"], "Two causes refer to the same Order when their First and Break indices match.", "دو علت وقتی به یک Order اشاره دارند که FirstIndex و BreakIndex آن‌ها یکسان باشد.", ["E", "Order Audit"]),
  entry("Source extreme", ["source_extreme", "source_index", "source_time"], "The directional extreme that supplies an object's price and later strict stop level.", "اکسترم جهت‌دار که قیمت آبجکت و سطح stop بعدی را می‌سازد.", ["Blue Line", "A", "S", "E", "StopAll"]),
  entry("Decision event", ["decision_event_time"], "The exact moment all gates for S, E, or StopAll have become true.", "لحظه دقیق که همه gateهای لازم برای S، E یا StopAll برقرار شده‌اند.", ["S", "E", "StopAll"]),
  entry("Calculation-valid Blue", ["calculation_valid"], "A Blue state allowed to enter A calculations; an internal invalid Reset Blue may remain only for the protected special A path.", "Blue مجاز برای محاسبه A؛ Reset Blue داخلی نامعتبر فقط برای مسیر ویژه محافظت‌شده A باقی می‌ماند.", ["Blue Line", "A"]),
  entry("Spacing lock", ["has_blue_line", "healthy_reactions_since_blue", "previous_count"], "State that prevents repeated Scale Blue output while still advancing the comparison count.", "وضعیتی که از Scale Blue تکراری جلوگیری می‌کند ولی شمارنده مقایسه را جلو می‌برد.", ["Blue Line Scale"]),
  entry("A ownership window", ["cycle_after_index", "next A confirmation", "a_stop_event_time", "a_ownership_windows"], "Opened immediately after an A strict stop. It remains open while S is pending, excludes later A source events inside the interval, and closes at a successful S source plus one timeframe; without S it remains pending.", "بلافاصله بعد از stop strict A باز می‌شود؛ تا تصمیم S باز می‌ماند، source event مربوط به Aهای بعدی داخل بازه را کنار می‌گذارد و پس از S موفق در source آن به‌اندازه یک timeframe بسته می‌شود؛ بدون S معلق می‌ماند.", ["A", "S"]),
  entry("Candidate crossing", ["SDetector._candidate_event_time", "_candidate_before_order", "_candidate_after_order", "SDetector._decision"], "The strict directional crossing compared with the opposite Order stop to decide S color.", "عبور strict کاندید که با stopِ Order مخالف مقایسه می‌شود تا رنگ S مشخص شود.", ["S red", "S blue"]),
  entry("Reset leg", ["_type3_reset_leg", "_reset_leg_geometry", "reset_time"], "The Break-to-Reset lifecycle used by S Type 3 and E Order_B candidates.", "چرخه Break-to-Reset که S Type 3 و کاندیدهای E Order_B از آن استفاده می‌کنند.", ["S Type 3", "E"]),
  entry("Direct Order", ["first_order_reaction_after_gate", "_first_healthy_direct_geometry"], "The first healthy complete Reaction geometry after the current parent gate.", "اولین هندسه کامل و سالم Reaction بعد از gate والد فعلی.", ["S", "E"]),
  entry("Carried-live Order", ["initial_order_audit", "order_audit"], "A previously accepted physical Order that is still eligible in a later E lifecycle.", "Order فیزیکی قبلاً پذیرفته‌شده که در چرخه بعدی E هنوز معتبر است.", ["E", "Order Audit"]),
  entry("Deadline", ["ADetector.detect: expires_at", "continuous_deadline", "range_end"], "A context-specific exclusive bound: A uses the next Blue formation; S Type 3 uses the next Order confirmation; E only uses continuous_deadline for the inherited-S Order race.", "مرز انحصاری وابسته به زمینه: A از تشکیل Blue بعدی، S Type 3 از تأیید Order بعدی، و E فقط برای رقابت Order به‌ارث‌رسیده از S از continuous_deadline استفاده می‌کند.", ["A", "S", "E"]),
  entry("Dominant ownership", ["split_a_zones_by_dominant_stops", "blocked_order_first_times"], "Bridge reconciliation that first selects the owner whose strict stop is in the latest main candle. Only same-candle ties use StopAll > E red > S red > E blue > S blue > A, followed by sequence and deterministic source keys. A live invalid bullish head with pending S blocks opposite Order Firsts until its exact stop.", "اصلاح Bridge که ابتدا مالک دارای stop strict در جدیدترین main candle را انتخاب می‌کند. فقط tie همان کندل از StopAll > E red > S red > E blue > S blue > A و سپس sequence و کلیدهای قطعی source استفاده می‌کند. leg head صعودی نامعتبرِ دارای S معلق Firstهای Order مخالف را تا stop دقیق مسدود می‌کند.", ["Bridge"]),
  entry("Visibility closure", ["final_a_zones", "final_s_zones", "final_e_zones", "display_a_zones", "display_s_zones"], "The final Bridge pass that hides shadowed rows while retaining parents required by visible children.", "مرحله نهایی Bridge که ردیف‌های پوشانده‌شده را مخفی و والد لازم برای child قابل‌نمایش را حفظ می‌کند.", ["Bridge"]),
  entry("Fixed point", ["reconcile_stopall_lifecycle"], "Repeat E/StopAll reconciliation until the sequence-reset map and public lifecycle no longer change.", "تکرار اصلاح E/StopAll تا نقشه reset شماره‌ها و چرخه عمومی دیگر تغییر نکند.", ["E", "StopAll", "Bridge"]),
  entry("Public collection", ["directions['bullish']", "serialize_direction"], "One of the eight arrays returned by the Bridge after calculation, ownership, and range filters.", "یکی از هشت آرایه خروجی Bridge پس از محاسبه، ownership و فیلتر بازه.", ["Bridge"]),
]);

export const REACTION_GEOMETRY_REFERENCE = Object.freeze({
  title: "Reaction geometry used by downstream Orders",
  titleFa: "هندسه Reaction که Orderهای پایین‌دست استفاده می‌کنند",
  summary: "Reaction geometry is calculated by the maintained Reaction detector. Bridge passes those same objects into S and E; it does not rebuild their prices or boundaries.",
  summaryFa: "هندسه Reaction توسط موتور اصلی Reaction محاسبه می‌شود. Bridge همان آبجکت‌ها را به S و E می‌دهد و قیمت یا مرز آن‌ها را دوباره نمی‌سازد.",
  code: `def provide_reaction_geometry(selected_range):
    candles, lower = build_shared_candle_views(selected_range)

    bullish_result = UnifiedReactionDetector(
        candles, lower, direction="bullish",
    ).detect()

    # Internal opposite Order geometry is a dependency of bullish S/E.
    geometry_detector = UnifiedReactionDetector(candles, lower, direction=order_direction)

    direct_order = geometry_detector.first_order_reaction_after_gate(
        start_index, end_index, exact_gate_event,
    )
    reset_order = geometry_detector.first_simple_geometry_after_gate(
        reset_index, gate_index, end_index,
    )

    # First/BoxTop/BoxBottom/Break values remain detector-owned.
    return reuse_original_reaction_objects(direct_order, reset_order)`,
  phases: Object.freeze([
    Object.freeze({ en: "Build main and lower candle views once from the isolated range.", fa: "نمای main و lower را یک‌بار از بازه جداشده بساز.", code: "candles, lower = build_candle_views(isolated_rows)" }),
    Object.freeze({ en: "Run the maintained Reaction detector; its Candidate/Reaction objects own First, BoxTop, BoxBottom, and Break.", fa: "موتور اصلی Reaction را اجرا کن؛ آبجکت‌های Candidate/Reaction مالک First، BoxTop، BoxBottom و Break هستند.", code: "reaction_objects = UnifiedReactionDetector(...).detect()" }),
    Object.freeze({ en: "For bullish S/E only, request the required opposite Order geometry through detector helper methods.", fa: "فقط برای S/E صعودی، هندسه Order مخالف لازم را از helperهای خود detector درخواست کن.", code: "order_geometry = detector.first_order_reaction_after_gate(...)" }),
    Object.freeze({ en: "Respect the gate, Reset ownership, continuous deadline, and earliest strict confirmation selected by those helpers.", fa: "gate، مالکیت Reset، deadline پیوسته و اولین تأیید strict انتخاب‌شده توسط همان helperها را رعایت کن.", code: "accepted = geometry_inside_owner_window_and_deadline" }),
    Object.freeze({ en: "Pass the original geometry object into S/E and merge repeated causes by (FirstIndex, BreakIndex).", fa: "همان آبجکت هندسه را وارد S/E کن و علت‌های تکراری را با (FirstIndex, BreakIndex) ادغام کن.", code: "identity = (geometry.first_idx, geometry.break_idx)" }),
  ]),
  checks: Object.freeze(["isolated range", "shared candle objects", "exact gate event", "Reset ownership", "continuous deadline", "First/Break identity"]),
  outputs: Object.freeze(["original Reaction geometry", "direct Order_A candidate", "Reset-leg Order_B candidate", "physical Order identity"]),
  sources: Object.freeze([
    "engine/pipeline/reaction_engine.py:first_order_reaction_after_gate",
    "engine/pipeline/reaction_engine.py:first_simple_geometry_after_gate",
    "engine/pipeline/reaction_engine.py:_earliest_confirmed_geometry",
    "engine/bridge/trading_pipeline.py:main",
  ]),
});
