const step = (en, fa, code, source) => ({ en, fa, code, source });

const type = ({ id, en, fa, entry, reject, output, steps, source }) => ({
  id,
  names: { en, fa },
  entry: { en: entry.en, fa: entry.fa },
  reject: { en: reject.en, fa: reject.fa },
  output,
  steps,
  source,
});

const reactionSource = "engine/pipeline/reaction_engine.py";
const blueSource = "engine/pipeline/blue_line_detector.py";
const aSource = "engine/pipeline/a_zone_detector.py";
const sSource = "engine/pipeline/s_zone_detector.py";
const eSource = "engine/pipeline/e_zone_detector.py";
const stopAllSource = "engine/pipeline/lifecycle_engine.py";
const bridgeSource = "engine/bridge/trading_pipeline.py";

export const ENGINE_CONTRACTS = Object.freeze({
  reaction: {
    contract: [
      step("Classify every candle with Decimal OHLC; a doji is GREEN.", "قیمت‌های OHLC هر کندل را با Decimal بخوان و دوجی را سبز حساب کن.", "tag = GREEN if close >= open else RED", `${reactionSource}:classify_candle_color`),
      step("Mode A finds the first valid direction change without requiring an earlier Reaction.", "در Mode A اولین تغییر جهت معتبر را بدون نیاز به ری‌اکشن قبلی پیدا کن.", "candidate = detector._first_initial(direction)", `${reactionSource}:_first_initial`),
      step("Build First, BoxTop, BoxBottom and their source candles before looking for confirmation.", "قبل از جست‌وجوی تأیید، First و BoxTop و BoxBottom را همراه کندل منبع هرکدام بساز.", "candidate = Candidate(first, box_top, box_bottom, sources)", `${reactionSource}:Candidate`),
      step("Freeze the candidate break level; update only the candidate extreme while it remains alive.", "سطح شکست کاندید را ثابت نگه دار و تا وقتی کاندید زنده است فقط extreme آن را به‌روزرسانی کن.", "candidate.box_bottom = min(candidate.box_bottom, candle.low)", `${reactionSource}:BullishDetector.detect`),
      step("Confirm only on a strict upper crossing. Equality never confirms a bullish Reaction.", "ری‌اکشن را فقط با عبور قطعی تأیید کن؛ برابری هیچ‌وقت تأیید نیست.", "confirmed = high > box_top", `${reactionSource}:breakout_analysis`),
      step("When invalidation and confirmation share a main candle, lower-second chronology decides which occurred first.", "اگر ابطال و تأیید داخل یک کندل اصلی باشند، ترتیب کندل‌های ثانیه‌ای مشخص می‌کند کدام زودتر رخ داده است.", "winner = first_exact_event(invalidation, confirmation)", `${reactionSource}:breakout_analysis`),
      step("Publish exact First/Break geometry and preserve anchor or leg-boundary provenance.", "هندسه دقیق First و Break را منتشر کن و منبع anchor یا مرز لگ را نگه دار.", "append_reaction(direction, candidate)", `${reactionSource}:_append_reaction`),
    ],
    types: [
      type({
        id: "mode_a", en: "Mode A · initial Reaction", fa: "Mode A · ری‌اکشن آغازین",
        entry: { en: "A new selected-range leg or post-Reset leg is open; an eligible FirstRed follows GREEN context.", fa: "یک لگ تازه در ابتدای بازه یا بعد از Reset باز است و FirstRed واجدشرایط بعد از زمینهٔ GREEN دیده می‌شود." },
        reject: { en: "The owner floor is crossed before the strict break, or lower-second chronology gives invalidation priority.", fa: "پیش از شکست قطعی، کف مالک شکسته شود یا ترتیب ثانیه‌ای ابطال را زودتر از تأیید نشان دهد." },
        output: ["reactions.firstIndex", "reactions.firstTime", "reactions.boxTop", "reactions.boxBottom", "reactions.breakIndex", "reactions.breakTime", "internal exact Break event", "reactions.mode=A"],
        steps: [
          "find the first opposite-color candle after the reference color",
          "build the preceding same-color run and initial box",
          "track the candidate extreme without moving the frozen break level",
          "resolve same-candle races using lower seconds",
          "emit the confirmed Reaction and optional same-candle Reset",
        ],
        source: `${reactionSource}:_first_initial,BullishDetector.detect`,
      }),
      type({
        id: "mode_b", en: "Mode B · continuing Reaction", fa: "Mode B · ری‌اکشن ادامه‌دار",
        entry: { en: "A Reaction is confirmed without Reset; the running bullish peak and the next RED candle open a normal candidate.", fa: "یک Reaction بدون Reset تأیید شده و سقف جاری صعودی همراه کندل RED بعدی کاندید عادی را باز می‌کند." },
        reject: { en: "The previous Reaction resets before this candidate confirms, or no strict High above the frozen BoxTop occurs in range.", fa: "Reaction قبلی پیش از تأیید این کاندید Reset می‌شود یا در بازه هیچ High بالاتر از BoxTop ثابت رخ نمی‌دهد." },
        output: ["internal Reaction ordinal", "reactions.mode=B", "reactions.firstIndex", "reactions.boxTop", "reactions.boxBottom", "reactions.breakIndex", "reactions.breakTime"],
        steps: [
          "track the running directional extreme and its source",
          "open the next candidate on the required color transition",
          "freeze BoxTop/BoxBottom according to direction",
          "confirm on a strict break and preserve exact provenance",
          "inspect a valid confirmation remainder when the next candidate may begin in the same main candle",
        ],
        source: `${reactionSource}:UnifiedReactionDetector.detect,_candidate_from_confirmation_remainder`,
      }),
      type({
        id: "direct_after_reset", en: "Direct recovery after Reset", fa: "بازیابی مستقیم بعد از ریست",
        entry: { en: "A confirmed Reaction has reset and a new valid First appears after that exact reset.", fa: "یک ری‌اکشن تأییدشده ریست شده و بعد از زمان دقیق ریست، First معتبر تازه‌ای دیده می‌شود." },
        reject: { en: "The local leg boundary breaks first, or the candidate starts inside a blocked invalidated interval.", fa: "مرز محلی لگ زودتر بشکند یا کاندید داخل بازه مسدودِ کاندید باطل‌شده شروع شود." },
        output: ["reactions.*", "resets.fromFirstIndex", "resets.secondTime"],
        steps: [
          "clear ordinary candidate state at Reset",
          "scan the post-reset color run and local floor",
          "build a direct candidate with its owner boundary",
          "use lower-second order for boundary-versus-break races",
          "publish the recovered Reaction without nesting inside blocked_through",
        ],
        source: `${reactionSource}:_first_direct_same_direction_after_reset,_scan_direct_candidate`,
      }),
    ],
  },

  reset: {
    contract: [
      step("A Reset belongs to a confirmed Reaction and preserves that owner's First identity.", "هر ریست متعلق به یک ری‌اکشن تأییدشده است و شناسه First همان مالک را نگه می‌دارد.", "reset.from_first_idx = owner.first_idx", `${reactionSource}:_append_reset`),
      step("Use a strict lower crossing of the confirmed bullish BoxBottom; equality is not a Reset.", "ریست فقط با عبور قطعی از مرز مخالف باکس رخ می‌دهد؛ برابری ریست نیست.", "reset = low < box_bottom", `${reactionSource}:confirmed_reset_before_breakout`),
      step("For a same-candle Reset, store the first lower-second crossing in secondTime. For a later Reset, lower seconds only resolve a competing Mode-B break; the public secondTime is null and time/index name the main candle.", "برای Reset داخل کندل تأیید، اولین عبور lower را در secondTime ذخیره کن. در Reset کندل بعدی، lower فقط رقابت با شکست Mode B را حل می‌کند؛ secondTime عمومی null است و time/index همان کندل اصلی را نشان می‌دهند.", "second_time = exact_cross if same_break_candle else None", `${reactionSource}:post_breakout_reset,confirmed_reset_before_breakout,_append_reset`),
      step("Preserve the exact broken level instead of recomputing it in the browser.", "سطح دقیق شکسته‌شده را نگه دار و آن را در مرورگر دوباره محاسبه نکن.", "broken_level = confirmed_boundary", `${bridgeSource}:serialize`),
      step("Clear ordinary candidate state and open direct recovery after the Reset gate: exact secondTime for a same-candle Reset, otherwise the later Reset main candle.", "state کاندید عادی را پاک کن و بازیابی مستقیم را پس از gate ریست باز کن: برای Reset همان کندل از secondTime دقیق و برای Reset بعدی از کندل اصلی ریست استفاده می‌شود.", "state.clear(); resume_after(reset.second_time or reset.time)", `${reactionSource}:UnifiedReactionDetector.detect`),
    ],
    types: [
      type({
        id: "same_candle", en: "Same-candle Reset", fa: "ریست داخل همان کندل تأیید",
        entry: { en: "A strict box break confirms the Reaction, then a later lower second crosses the opposite confirmed boundary inside the same main candle.", fa: "شکست قطعی باکس ری‌اکشن را تأیید کند و بعدتر در همان کندل اصلی، یک کندل ثانیه‌ای از مرز تأییدشدهٔ مقابل عبور کند." },
        reject: { en: "The reset crossing occurs before confirmation or only equals the boundary.", fa: "عبور ریست قبل از تأیید رخ دهد یا فقط با مرز برابر باشد." },
        output: ["resets.index", "resets.time", "resets.secondTime", "resets.brokenLevel", "resets.fromFirstIndex"],
        steps: ["resolve confirmation time", "freeze the confirmed opposite boundary", "scan only later lower seconds", "emit the first strict reset crossing"],
        source: `${reactionSource}:post_breakout_reset`,
      }),
      type({
        id: "later_reset", en: "Later confirmed-Reaction Reset", fa: "ریست بعدیِ ری‌اکشن تأییدشده",
        entry: { en: "After confirmation, a later price event strictly crosses the last confirmed opposite box boundary.", fa: "بعد از تأیید، قیمت در رویدادی بعدی به‌صورت قطعی از مرز مخالف آخرین باکس تأییدشده عبور کند." },
        reject: { en: "Equality, an earlier unrelated candidate, or a crossing outside the active owner does not reset it.", fa: "برابری، کاندید نامرتبط قبلی یا عبور خارج از مالک فعال باعث ریست نمی‌شود." },
        output: ["resets.*", "reaction owner provenance"],
        steps: ["keep the last confirmed owner active", "find the first later main candle whose Low is strictly below BoxBottom", "use lower seconds only to settle a competing Mode-B break in that candle", "attach owner First and broken level with secondTime=null", "clear candidate state and start direct recovery"],
        source: `${reactionSource}:confirmed_reset_before_breakout,_append_reset`,
      }),
    ],
  },

  blue_line: {
    contract: [
      step("Consume authoritative Reactions and Resets in formation order using Decimal('0.618').", "ری‌اکشن‌ها و ریست‌های معتبر را به ترتیب تشکیل و با Decimal('0.618') مصرف کن.", "FIBONACCI_RATIO = Decimal('0.618')", `${blueSource}:FIBONACCI_RATIO`),
      step("Choose the Mode A anchor/leg boundary or the previous Reaction boundary as the Fibonacci reference.", "برای مرجع فیبوناچی در Mode A از anchor یا مرز لگ و در حالت عادی از مرز ری‌اکشن قبلی استفاده کن.", "fib = fibonacci_level(direction, reaction, reference)", `${blueSource}:fibonacci_level`),
      step("Count strict penetrations with a pending extreme. A more directional extreme replaces the pending one, and any same or later confirmation-color main candle confirms it; bullish confirmation is GREEN, including doji.", "نفوذهای strict را با extreme معلق بشمار. extreme جهت‌دارتر جای قبلی را می‌گیرد و هر کندل main هم‌رنگِ تأیید در همان لحظه یا بعدتر آن را تأیید می‌کند؛ در مسیر صعودی GREEN شامل دوجی هم هست.", "strikes = count_scale_strikes(...); confirming_color = 'GREEN'", `${blueSource}:count_scale_strikes`),
      step("If a pending strike remains at Reaction end, inspect lower-second data from its source through the Break candle; only a penetration before or at the strict Break confirms it, and the decisive second maps back to its main candle.", "اگر در پایان Reaction هنوز strike معلق باشد، lower-second را از source آن تا کندل Break بررسی کن؛ فقط نفوذی که پیش از یا هم‌زمان با Break strict رخ دهد تأیید است و second تعیین‌کننده به main candle خودش map می‌شود.", "strike = _intrabar_pending_confirmation(..., start_time=pending.source_time, break_time=break_time)", `${blueSource}:_intrabar_pending_confirmation`),
      step("A scale exists only when the current confirmed strike count is greater than the previous count.", "Scale فقط وقتی ساخته می‌شود که تعداد strike تأییدشدهٔ فعلی از قبلی بیشتر باشد.", "is_scale = previous_count is not None and strike_count > previous_count", `${blueSource}:detect_blue_lines`),
      step("Enforce the stateful one-healthy-Reaction spacing lock between published Blue lines.", "بین دو خط آبی منتشرشده، قفل stateful عبور یک ری‌اکشن سالم کامل را رعایت کن.", "spacing_open = not has_blue_line or healthy_reactions_since_blue >= 1", `${blueSource}:detect_blue_lines`),
      step("Compute scale price at one third and Reset price at one fifth of the decisive candle range.", "قیمت Scale را در یک‌سوم و قیمت Reset را در یک‌پنجم بازه کندل تصمیم‌گیر حساب کن.", "scale = low + (high-low)/3; reset = low + (high-low)/5", `${blueSource}:detect_blue_lines`),
      step("Keep invalid Reset Blue provenance internal. Only calculation-valid lines enter ordinary A pairing or public serialization; the protected special A path may inspect one internal invalid line.", "منبع Reset Blue نامعتبر را داخلی نگه دار. فقط خط‌های calculation-valid وارد جفت‌سازی عادی A یا خروجی عمومی می‌شوند؛ مسیر محافظت‌شدهٔ A خاص می‌تواند یک خط نامعتبر داخلی را بررسی کند.", "ordinary_a/public = valid_lines; special_a may inspect invalid_reset", `${aSource}:_build_blue_states,_double_stop_a_candidates;${bridgeSource}:serialize_blue_lines`),
      step("A bullish Blue stops on the first lower-second Low strictly below its source extreme.", "خط آبی با اولین عبور قطعی در دادهٔ ثانیه‌ای از extreme منبع خودش متوقف می‌شود.", "stop = first(low < source_extreme)", `${aSource}:_build_blue_states`),
    ],
    types: [
      type({ id: "scale", en: "Scale Blue", fa: "خط آبی Scale", entry: { en: "The Reaction's confirmed strike count strictly increases and spacing permits publication.", fa: "تعداد strike تأییدشدهٔ ری‌اکشن بیشتر شده و قفل فاصله اجازه انتشار می‌دهد." }, reject: { en: "No prior count, no strict increase, or the spacing lock is still active.", fa: "تعداد قبلی وجود ندارد، افزایش قطعی رخ نداده یا قفل فاصله هنوز فعال است." }, output: ["blueLines.kind=scale", "blueLines.fibonacciLevel", "blueLines.previousStrikeCount", "blueLines.strikeCount", "blueLines.sourceExtreme", "blueLines.linePrice"], steps: ["calculate the 0.618 level", "collect and confirm strict strikes", "compare with previous count", "apply spacing", "emit at one-third price; ADetector later computes the private BlueState stop"], source: `${blueSource}:count_scale_strikes,detect_blue_lines;${aSource}:_build_blue_states` }),
      type({ id: "reset", en: "Reset Blue", fa: "خط آبی Reset", entry: { en: "An accepted Reset group supplies a strict broken level and spacing permits publication.", fa: "یک گروه Reset پذیرفته‌شده سطح شکسته‌شدهٔ قطعی دارد و قفل فاصله اجازه انتشار می‌دهد." }, reject: { en: "Spacing blocks it, or the same-index prior Blue stop makes the internal Reset Blue calculation invalid.", fa: "قفل فاصله آن را ببندد یا stop خط قبلی روی همان index باعث شود Reset Blue داخلی نامعتبر شود." }, output: ["blueLines.kind=reset", "blueLines.brokenLevel", "blueLines.sourceExtreme", "blueLines.linePrice", "public row only when calculation_valid"], steps: ["group Resets by fromFirstIndex", "select the accepted boundary", "form on the exact strict broken-level crossing", "price at one fifth of the Reset candle", "validate same-index stop conflict", "retain invalid geometry internally but publish only calculation-valid rows"], source: `${blueSource}:detect_blue_lines;${bridgeSource}:serialize_blue_lines` }),
      type({ id: "internal_invalid_reset", en: "Internal invalid Reset Blue", fa: "Reset Blue نامعتبرِ داخلی", entry: { en: "A Reset Blue is geometrically formed but fails calculation validity and is retained only for special A provenance.", fa: "Reset Blue از نظر هندسی ساخته می‌شود اما اعتبار محاسباتی را نمی‌گیرد و فقط برای منبع داخلی A خاص نگه داشته می‌شود." }, reject: { en: "It is never serialized as a public Blue line and cannot enter ordinary A pairing.", fa: "هیچ‌وقت به‌عنوان خط آبی عمومی serialize نمی‌شود و وارد pairing عادی A هم نمی‌شود." }, output: ["internal BlueLine.calculation_valid=false", "possible aZones special source"], steps: ["form Reset geometry", "detect the prior-Blue same-index stop conflict", "mark invalid", "offer only to special double-stop A", "omit from blueLines payload"], source: `${blueSource}:detect_blue_lines;${aSource}:_double_stop_a_candidates` }),
    ],
  },

  a: {
    contract: [
      step("Sort calculation-valid Blue states by exact formation and pair adjacent eligible lines.", "خط‌های آبی calculation-valid را با زمان دقیق تشکیل مرتب کن و جفت‌های مجاور واجد شرایط را بساز.", "states = sorted(valid_blue_states, key=formation_time)", `${aSource}:_build_blue_states`),
      step("Resolve each Blue's first strict stop from lower-second data.", "اولین استاپ قطعی هر خط آبی را از دادهٔ ثانیه‌ای مشخص کن.", "state.stop_event_time = first_strict_cross(source_extreme)", `${aSource}:_build_blue_states`),
      step("Choose one of the three ordinary trigger paths from the pair's exact lifecycle.", "با توجه به چرخه دقیق جفت، یکی از سه مسیر trigger عادی را انتخاب کن.", "trigger = self._pair_trigger(previous, current)", `${aSource}:_pair_trigger`),
      step("Expire an unresolved pair when the next eligible Blue formation arrives.", "اگر جفت تا زمان تشکیل خط آبی واجد شرایط بعدی حل نشد، آن را منقضی کن.", "deadline = next_blue.formation_time", `${aSource}:detect`),
      step("Require the first qualifying same-direction Reaction at or after the trigger and after required stops.", "اولین ری‌اکشن هم‌جهت واجد شرایط را در یا بعد از trigger و پس از استاپ‌های لازم بگیر.", "reaction = self._first_reaction_after(trigger, stops)", `${aSource}:_first_reaction_after`),
      step("Select A price from the inclusive trigger-to-Reaction-break range; preserve the earlier extreme on ties.", "قیمت A را از بازهٔ شامل trigger تا Break ری‌اکشن انتخاب کن و در تساوی extreme زودتر را نگه دار.", "source = self._a_source(trigger_index, reaction.break_idx)", `${aSource}:_a_source`),
      step("Keep equal extrema on the earlier source in _range_extreme and _candidate_source. For coexisting bullish Blue stops, sort by (stop_event_time, -stop_level); an exact-time tie takes the second stop as trigger and the first stop's extreme as continuation level.", "در _range_extreme و _candidate_source، extreme برابر را به source زودتر بده. برای stopهای هم‌زمان Blue صعودی، بر اساس (stop_event_time, -stop_level) مرتب کن؛ در tie دقیق، trigger از stop دوم و continuation level از extreme stop اول می‌آید.", "first, second = sorted(states, key=(stop_event_time, -stop_level)); trigger = second.stop_event_time; level = first.stop_event_extreme", `${aSource}:_range_extreme,_candidate_source,_pair_trigger`),
      step("Allow the protected special double-stop route to consume one valid and one internal invalid Blue.", "مسیر محافظت‌شدهٔ special double-stop می‌تواند یک Blue معتبر و یک Blue نامعتبر داخلی را مصرف کند.", "special = self._double_stop_a_candidates()", `${aSource}:_double_stop_a_candidates`),
      step("Publish each consumed Blue pair once and attach exact trigger, Reaction, source, and later A-stop provenance.", "هر جفت Blue مصرف‌شده را فقط یک‌بار منتشر کن و منبع دقیق trigger، ری‌اکشن، قیمت و استاپ بعدی A را نگه دار.", "emit(AZone(...))", `${aSource}:detect`),
    ],
    types: [
      type({ id: "inherited_reaction_stop", en: "Ordinary A · inherited Reaction stop", fa: "A عادی · استاپ به‌ارث‌رسیده از ری‌اکشن", entry: { en: "A same-direction Reaction begins after the previous Blue formation and confirms before the current Blue formation.", fa: "یک ری‌اکشن هم‌جهت بعد از تشکیل Blue قبلی شروع و پیش از تشکیل Blue فعلی تأیید می‌شود." }, reject: { en: "No strict continuation-level cross occurs after current formation before the pair deadline.", fa: "بعد از تشکیل خط فعلی و پیش از deadline جفت، continuation level به‌صورت قطعی شکسته نشود." }, output: ["aZones.continuationLevel", "aZones.triggerEventTime", "aZones.reactionNumber", "aZones.sourceIndex", "aZones.price"], steps: ["freeze the continuation extreme from previous formation through Reaction break", "start after current Blue formation", "find the first strict continuation cross", "find confirming Reaction", "emit A and consume the pair"], source: `${aSource}:_inherited_stop,_pair_trigger` }),
      type({ id: "previous_blue_stopped", en: "Ordinary A · previous Blue stopped first", fa: "A عادی · استاپ زودترِ Blue قبلی", entry: { en: "The previous Blue stops before the current Blue forms.", fa: "Blue قبلی قبل از تشکیل Blue فعلی متوقف می‌شود." }, reject: { en: "Neither the current formation remainder nor a later current-Blue stop produces the required strict lower continuation.", fa: "نه ادامه همان کندل تشکیل و نه استاپ بعدی Blue فعلی، شکست قطعی ادامه را نسازد." }, output: ["aZones.blue1StopTime", "aZones.blue2StopTime", "aZones.continuationSourceTime", "aZones.triggerEventTime", "aZones.*"], steps: ["freeze the extreme from previous exact stop to before current source", "scan the current formation remainder", "if needed wait for current Blue stop", "require a strict new extreme", "confirm with Reaction and emit"], source: `${aSource}:_pair_trigger` }),
      type({ id: "coexisting_blue_stops", en: "Ordinary A · coexisting Blue stops", fa: "A عادی · استاپ دو Blue هم‌زمانِ فعال", entry: { en: "Both Blue lines coexist; exact chronology identifies the first and second stop.", fa: "هر دو Blue هم‌زمان فعال‌اند و ترتیب دقیق، استاپ اول و دوم را مشخص می‌کند." }, reject: { en: "After the second stop, price never strictly crosses the first-stop extreme before expiry.", fa: "پس از استاپ دوم، قیمت تا پیش از انقضا از extreme استاپ اول به‌صورت قطعی عبور نکند." }, output: ["aZones.blue1StopTime", "aZones.blue2StopTime", "aZones.continuationLevel", "aZones.triggerEventTime", "aZones.*"], steps: ["order stops by exact event", "freeze the first-stop extreme", "wait through the second stop", "allow an immediate trigger if both share the exact event", "confirm with Reaction and emit"], source: `${aSource}:_pair_trigger` }),
      type({ id: "special_double_stop", en: "Special A · double stop", fa: "A خاص · double-stop", entry: { en: "A valid Blue and an internal invalid intermediate Blue form a strict source/formation cross and a later valid Reaction confirms it.", fa: "یک Blue معتبر و یک Blue میانی نامعتبر، عبور قطعی منبع/تشکیل می‌سازند و ری‌اکشن معتبر بعدی آن را تأیید می‌کند." }, reject: { en: "An ordinary A already consumed the Reaction, the lifecycle was already consumed, or duplicate guards match.", fa: "یک A عادی همان ری‌اکشن را مصرف کرده باشد، چرخه قبلاً مصرف شده باشد یا نگهبان‌های تکرار فعال شوند." }, output: ["aZones.*", "consumed valid Blue pair", "no public invalid blueLines object"], steps: ["locate the prior valid Blue", "evaluate the invalid intermediate Blue source cross", "resolve its exact double-stop trigger", "find the first confirming Reaction", "deduplicate against ordinary A", "emit A and consume both Blue inputs"], source: `${aSource}:_double_stop_a_candidates,detect` }),
    ],
  },

  s_red: {
    contract: [],
    types: [],
  },
  s_blue: {
    contract: [],
    types: [],
  },
  e_blue: {
    contract: [],
    types: [],
  },
  e_red: {
    contract: [],
    types: [],
  },
  order_audit: {
    contract: [],
    types: [],
  },
  stop_all: {
    contract: [],
    types: [],
  },
});

const sContract = [
  step("Consume final eligible A zones, trend Reactions, opposite Reactions/Resets, and exact lower candles.", "Aهای نهایی واجد شرایط، ری‌اکشن‌های هم‌جهت، ری‌اکشن/ریست مخالف و کندل‌های ثانیه‌ای را مصرف کن.", "detector = SDetector(direction, reactions, opposite_reactions, blue_lines, a_zones, ...)", `${sSource}:SDetector.__init__`),
  step("Open an a_ownership_window immediately after the A's first strict stop, even before S decides. Keep its end open while S is pending; later A source events inside it are ineligible. Close it at the successful S source plus one timeframe.", "a_ownership_window را بلافاصله بعد از اولین stop strict A باز کن، حتی پیش از تصمیم S. تا وقتی S معلق است پایان پنجره باز می‌ماند و source event مربوط به Aهای بعدی داخل آن واجد شرایط نیست؛ پس از S موفق در source آن به‌اندازه یک timeframe بسته می‌شود.", "a_ownership_windows.append((a_stop_event_time, None)); close_at = s_source_time + timeframe", `${sSource}:detect`),
  step("For bullish ownership, an invalid leg head with an actual pending S keeps its internal window until the head's exact strict stop. Opposite-Reaction Firsts opened during that interval cannot own the resumed outer Order/E space; selection resumes after the stop. A head without pending S does not block unrelated Orders.", "در ownership صعودی، leg head نامعتبرِ دارای S معلق پنجره داخلی خود را تا stop strict دقیق head حفظ می‌کند. Firstهای Reaction مخالف که در این فاصله باز شوند مالک فضای بیرونی Order/E پس از resume نیستند؛ انتخاب بعد از stop ادامه پیدا می‌کند. head بدون S معلق Orderهای نامرتبط را مسدود نمی‌کند.", "blocked_order_first_times.update(blocked_orders_while_invalid_leg_heads_are_live(...))", `${bridgeSource}:blocked_orders_while_invalid_leg_heads_are_live`),
  step("Select pre-order, nested advanced, simple, or post-order fallback candidate geometry without mixing their tie rules.", "هندسه کاندید pre-order، advanced تو‌در‌تو، simple یا fallback بعد از Order را با tie rule مخصوص خودش انتخاب کن.", "candidate = pre_order or advanced or simple or fallback", `${sSource}:_candidate_before_order,_nested_trend_reaction,_simple_candidate,_candidate_after_order`),
  step("Treat the opposite Reaction as Order and derive its stop from Mode A leg geometry or the previous Mode B box boundary.", "ری‌اکشن مخالف را Order بگیر و استاپ آن را از هندسه لگ Mode A یا مرز باکس قبلی Mode B بساز.", "order_stop = self._order_stop(order)", `${sSource}:_order_stop`),
  step("Resolve candidate-cross versus Order-stop using exact lower-second chronology; a same-finest-candle tie emits no S.", "رقابت عبور کاندید و استاپ Order را با ترتیب دقیق ثانیه‌ای حل کن؛ تساوی روی یک کندل ریز هیچ Sای نمی‌سازد.", "decision = self._decision(candidate, order_stop)", `${sSource}:_decision`),
  step("Emit red when Order stops first; emit blue only when the candidate crosses first with accepted evidence.", "اگر Order زودتر متوقف شد S قرمز بساز؛ اگر کاندید زودتر شکست فقط با evidence معتبر S آبی بساز.", "color = 'red' if order_stop_first else 'blue'", `${sSource}:detect`),
  step("Preserve A, Order, Reset, source, price, formation type, and exact decision provenance in one S object.", "منبع کامل A، Order، Reset، قیمت، نوع تشکیل و زمان دقیق تصمیم را داخل یک آبجکت S نگه دار.", "emit(SZone(...))", `${sSource}:SZone`),
];

const simpleSType = (color) => type({
  id: `simple_${color}`, en: `Simple S · ${color}`, fa: `S ساده · ${color === "red" ? "قرمز" : "آبی"}`,
  entry: color === "red"
    ? { en: "No valid nested advanced Reaction wins and the opposite Order strictly stops before the simple candidate crosses.", fa: "ری‌اکشن advanced تو‌در‌توی معتبری برنده نشود و Order مخالف قبل از عبور کاندید ساده به‌صورت قطعی متوقف شود." }
    : { en: "The simple candidate strictly crosses before Order stop and accepted Reset-Blue or ordinary-Reaction evidence exists.", fa: "کاندید ساده قبل از استاپ Order قطعی بشکند و evidence معتبر Reset Blue یا ری‌اکشن عادی وجود داشته باشد." },
  reject: color === "red"
    ? { en: "Candidate crossing wins, or both events occur on the same finest candle.", fa: "عبور کاندید زودتر رخ دهد یا هر دو رویداد روی یک کندل ریز باشند." }
    : { en: "Order stop wins, events tie, or the early candidate has no accepted evidence.", fa: "استاپ Order زودتر رخ دهد، دو رویداد مساوی باشند یا کاندید زودهنگام evidence معتبر نداشته باشد." },
  output: ["sZones.color", "sZones.formationType=simple", "sZones.a*", "sZones.order*", "sZones.source*", "sZones.decisionEventTime"],
  steps: ["find exact A stop", "select pre-order or post-order simple candidate", "build opposite Order and stop level", "run the exact event race", `emit ${color} simple S with full provenance`],
  source: `${sSource}:_simple_candidate,_candidate_after_order,_decision,detect`,
});

const advancedSType = (color) => type({
  id: `advanced_${color}`, en: `Advanced S · ${color}`, fa: `S پیشرفته · ${color === "red" ? "قرمز" : "آبی"}`,
  entry: color === "red"
    ? { en: "A same-direction Reaction is chronologically and geometrically nested inside the opposite Order, then Order stops first.", fa: "یک ری‌اکشن هم‌جهت از نظر زمان و قیمت کاملاً داخل Order مخالف باشد و سپس Order زودتر متوقف شود." }
    : { en: "A nested same-direction Reaction supplies the candidate; it crosses before Order stop with accepted evidence.", fa: "یک ری‌اکشن هم‌جهت تو‌در‌تو کاندید را بسازد و با evidence معتبر قبل از استاپ Order شکسته شود." },
  reject: color === "red"
    ? { en: "Nested geometry is invalid, candidate wins, or the exact events tie.", fa: "هندسه تو‌در‌تو نامعتبر باشد، کاندید برنده شود یا رویدادهای دقیق مساوی باشند." }
    : { en: "Nested geometry is invalid, Order wins, events tie, or evidence is missing.", fa: "هندسه تو‌در‌تو نامعتبر باشد، Order برنده شود، رویدادها مساوی باشند یا evidence وجود نداشته باشد." },
  output: ["sZones.color", "sZones.formationType=advanced", "sZones.a*", "sZones.order*", "sZones.source*", "sZones.decisionEventTime"],
  steps: ["find exact A stop and Order", "locate a nested trend Reaction inside the Order box", "derive the advanced boundary from Order geometry", "resolve candidate-versus-stop chronology", `emit ${color} advanced S with full provenance`],
  source: `${sSource}:_nested_trend_reaction,_candidate_for_trend_reaction,_decision,detect`,
});

ENGINE_CONTRACTS.s_red.contract = sContract;
ENGINE_CONTRACTS.s_red.types = [simpleSType("red"), advancedSType("red")];
ENGINE_CONTRACTS.s_blue.contract = sContract;
ENGINE_CONTRACTS.s_blue.types = [
  simpleSType("blue"),
  advancedSType("blue"),
  type({
    id: "type3", en: "Type 3 S · blue", fa: "S نوع ۳ · آبی",
    entry: { en: "After A-stop and before the first later opposite Order confirmation, an eligible opposite Reset leg is strictly crossed with a confirming trend Reaction.", fa: "بعد از استاپ A و پیش از تأیید اولین Order مخالف بعدی، مرز لگ یک ریست مخالف واجد شرایط به‌صورت قطعی شکسته شود و ری‌اکشن هم‌جهت تأییدکننده وجود داشته باشد." },
    reject: { en: "The opposite owner was not healthy at A-stop, the leg does not cross before deadline, or no trend Reaction confirms by the cross.", fa: "مالک مخالف هنگام استاپ A سالم نباشد، لگ پیش از deadline شکسته نشود یا تا زمان عبور ری‌اکشن هم‌جهت تأیید نشود." },
    output: ["sZones.color=blue", "sZones.formationType=type3", "sZones.resetReactionNumber", "sZones.resetTime", "sZones.source*", "order fields=null"],
    steps: ["find opposite owners confirmed before A-stop and not reset by it", "build each owner-Break through Reset leg", "take the directional extreme with the documented tie rule", "find the first strict post-Reset cross before deadline", "require a trend Reaction from A-stop through cross", "emit earliest Type 3 without invented Order geometry"],
    source: `${sSource}:_type3_reset_leg,_first_type3,detect`,
  }),
];

const eContract = [
  step("Start from every accepted S and recursively from each accepted E parent.", "از هر S پذیرفته‌شده شروع کن و بعد از هر E پذیرفته‌شده مسیر را به‌صورت بازگشتی ادامه بده.", "for parent in accepted_s_and_e: build_child(parent)", `${eSource}:detect`),
  step("Find the parent's first strict stop from its exact decision event using lower-second data.", "اولین استاپ قطعی والد را از زمان دقیق تصمیمش و با دادهٔ ثانیه‌ای پیدا کن.", "parent_stop = self._parent_stop(parent_type, parent)", `${eSource}:_parent_stop`),
  step("Build direct parent-stop Order_A and Reset-leg Order_B candidates, then merge equal physical identities.", "کاندیدهای Order_A مستقیم و Order_B حاصل از reset-leg را بساز و identityهای فیزیکی برابر را ادغام کن.", "candidates = self.order_candidates(...)", `${eSource}:order_candidates`),
  step("Compute strict Order stops. Candidate confirmation is bounded by the earliest known Order stop and, only for an S inheritance race, by the inherited Order's continuous deadline.", "استاپ قطعی Orderها را حساب کن. تأیید کاندید با زودترین استاپ شناخته‌شده محدود می‌شود و فقط در رقابت inheritance از S، deadline پیوستهٔ Order به‌ارث‌رسیده هم اعمال می‌شود.", "match = self._first_order(parent_stop, continuous_deadline_for_s_only)", `${eSource}:order_candidates,_first_order`),
  step("At an equal stop event prefer the newer Order First, while preserving all merged causes.", "اگر زمان استاپ برابر بود، First جدیدتر Order را ترجیح بده و همه causeهای ادغام‌شده را نگه دار.", "winner = min(matches, key=(stop_event, -first_index))", `${eSource}:_zone`),
  step("Choose the directional extreme from parent-stop main candle through Order-stop main candle, inclusive.", "extreme جهت روند را از کندل اصلی استاپ والد تا کندل اصلی استاپ Order، به‌صورت شامل، انتخاب کن.", "source = self._extreme_between(parent_stop, order_stop)", `${eSource}:_extreme_between`),
  step("Inherit family, calculate recursive number with active-state dominance, and retain stopped history.", "family را به ارث ببر، شماره بازگشتی را با dominance وضعیت فعال بساز و سابقه متوقف‌شده را نگه دار.", "zone = replace(zone, family=family, number=number)", `${eSource}:detect`),
  step("Rebuild the accepted Order ledger after ownership and repeat E/StopAll until sequence resets reach a fixed point.", "بعد از حل مالکیت، ledger سفارش‌های پذیرفته‌شده را دوباره بساز و E/StopAll را تا رسیدن resetهای دنباله به نقطه ثابت تکرار کن.", "reconcile_stopall_lifecycle(...) ", `${bridgeSource}:reconcile_stopall_lifecycle`),
];

const eTypes = (family) => [
  type({ id: `direct_order_a_${family}`, en: `E ${family} · direct Order_A`, fa: `E ${family === "red" ? "قرمز" : "آبی"} · Order_A مستقیم`, entry: { en: "The accepted parent strictly stops and the directional Reaction API returns a healthy direct opposite Order whose First begins at or after that exact gate.", fa: "والد پذیرفته‌شده به‌صورت قطعی متوقف شود و API هندسه جهت، یک Order مخالف سالم برگرداند که First آن در یا بعد از همان gate دقیق آغاز شده باشد." }, reject: { en: "Order First opened before the exact parent stop, an already gate-owned Order has priority, or another eligible Order stops first.", fa: "First سفارش پیش از استاپ دقیق والد باز شده باشد، Order متعلق به gate اولویت داشته باشد یا Order واجدشرایط دیگری زودتر متوقف شود." }, output: ["eZones.family", "eZones.number", "eZones.parent*", "eZones.orderCauses includes parent-stop", "eZones.order*", "eZones.source*", "eZones.decisionEventTime"], steps: ["strict-stop the parent", "request direct geometry after the exact gate", "resolve prior-owner Reset and same-gate ownership", "merge it into the complete Order pool", "rank stopped Orders by stop event then newer First", "choose the inclusive source extreme", "emit the accepted E and rebuild audit"], source: `${eSource}:_first_healthy_direct_geometry,order_candidates,_zone` }),
  type({ id: `reset_leg_order_b_${family}`, en: `E ${family} · Reset-leg Order_B`, fa: `E ${family === "red" ? "قرمز" : "آبی"} · Order_B از لگ ریست`, entry: { en: "An eligible opposite owner/reset leg forms, its directional boundary crosses after Reset, and a valid opposite Order_B geometry confirms within the resulting lifecycle.", fa: "یک لگ owner/reset مخالف واجد شرایط ساخته شود، مرز جهت‌دارش بعد از ریست بشکند و هندسه معتبر Order_B مخالف در همان چرخه تأیید شود." }, reject: { en: "The leg has no strict cross, simple trend evidence is absent, owner/Reset rules reject its geometry, or an earlier eligible Order stop closes the decision window.", fa: "لگ عبور قطعی نداشته باشد، evidence سادهٔ روند وجود نداشته باشد، قواعد owner/Reset هندسه را رد کنند یا استاپ زودترِ یک Order واجدشرایط پنجره تصمیم را ببندد." }, output: ["eZones.family", "eZones.number", "eZones.orderCauses includes reset-leg", "eZones.orderResetLegResetTime", "eZones.orderResetLegBreakTime", "eZones.order*", "eZones.*"], steps: ["build owner Break-to-Reset leg", "find the directional leg extreme", "require its first strict post-Reset crossing", "verify simple trend-Reaction evidence", "request the first valid opposite Order_B geometry", "merge equal First/Break identity and causes", "rank it inside the complete Order pool and emit only if it wins"], source: `${eSource}:_reset_leg_geometry,_first_order_b_geometry,order_candidates,_zone` }),
  type({ id: `carried_live_${family}`, en: `E ${family} · carried live Order`, fa: `E ${family === "red" ? "قرمز" : "آبی"} · سفارش زندهٔ منتقل‌شده`, entry: { en: "An accepted ledger Order formed within the parent's lifecycle and its strict stop is at or after the new parent stop; Blue S may also pass its own unconsumed Order.", fa: "یک Order پذیرفته‌شده در طول چرخه والد تشکیل شده و استاپ قطعی آن در یا بعد از استاپ والد جدید است؛ S آبی همچنین می‌تواند Order مصرف‌نشدهٔ خودش را منتقل کند." }, reject: { en: "It formed outside the eligible parent lifecycle, confirmed after the parent stop, stopped before the parent, or loses the common stop-time/newer-First race.", fa: "بیرون چرخه واجدشرایط والد تشکیل شده، بعد از استاپ والد تأیید شده، پیش از والد متوقف شده یا رقابت مشترک زمان استاپ/First جدیدتر را ببازد." }, output: ["eZones.orderCauses includes carried-live", "same order First/Break identity", "new eZones parent/source/decision"], steps: ["read accepted E and stopped-A Order ledgers", "include the Blue S unconsumed Order when applicable", "prove confirmation and strict-stop chronology across the parent", "keep the original First/Break geometry", "rank it together with direct and reset-leg choices", "emit E without inventing new Order geometry"], source: `${eSource}:_carried_order_for_parent,_unconsumed_s_order,_zone` }),
  type({ id: `recursive_${family}`, en: `E ${family} · recursive continuation`, fa: `E ${family === "red" ? "قرمز" : "آبی"} · ادامه بازگشتی`, entry: { en: "An accepted E strictly stops and another accepted Order wins for the resulting parent lifecycle.", fa: "یک E پذیرفته‌شده به‌صورت قطعی متوقف شود و یک Order معتبر دیگر در چرخه والد جدید برنده شود." }, reject: { en: "No strict parent stop, no eligible Order, dominance rejects the branch, or a StopAll boundary resets the sequence.", fa: "استاپ قطعی والد یا Order واجد شرایط وجود نداشته باشد، dominance شاخه را رد کند یا مرز StopAll دنباله را ریست کند." }, output: ["eZones.parentType=E or StopAll", "eZones.family", "eZones.number=N", "historical stopped E", "new active E"], steps: ["strict-stop current E", "build and rank the next Order pool", "create child geometry", "inherit dominant family", "increment the active stopped-family number", "apply StopAll sequence reset", "continue until no child is valid"], source: `${eSource}:detect` }),
];

ENGINE_CONTRACTS.e_blue.contract = eContract;
ENGINE_CONTRACTS.e_blue.types = eTypes("blue");
ENGINE_CONTRACTS.e_red.contract = eContract;
ENGINE_CONTRACTS.e_red.types = eTypes("red");

ENGINE_CONTRACTS.order_audit.contract = [
  step("Merge S parent-A audit and the accepted E ledger into one physical Order registry.", "ممیزی Order والد A در S و ledger پذیرفته‌شده E را در یک رجیستری سفارش فیزیکی ادغام کن.", "audit = merge(s_order_audit, e_accepted_ledger)", `${bridgeSource}:serialize_order_audit`),
  step("Use (FirstIndex, BreakIndex) as physical identity and deduplicate equal geometry.", "زوج (FirstIndex, BreakIndex) را identity فیزیکی بگیر و هندسه برابر را تکراری نکن.", "identity = (order.first_idx, order.break_idx)", `${eSource}:_register_order_audit`),
  step("Merge every accepted parent-stop and reset-leg cause without adding a second physical Order row. carried-live remains E lineage metadata and is not serialized as a third Order Audit cause shape.", "همه causeهای معتبر parent-stop و reset-leg را بدون ساخت ردیف فیزیکی دوم برای Order ادغام کن. carried-live فقط metadata زنجیرهٔ E می‌ماند و به‌عنوان شکل سوم cause در Order Audit serialize نمی‌شود.", "audit.causes = deduplicate(parent_stop_causes + reset_leg_causes)", `${eSource}:_register_order_audit,_enrich_order_audit_reset_causes;${bridgeSource}:serialize_order_audit`),
  step("Preserve complete Reaction geometry, mode/number, stop level/source, strict stop result, and exact event.", "هندسه کامل ری‌اکشن، mode/number، سطح و منبع استاپ، نتیجه عبور قطعی و زمان دقیق را نگه دار.", "audit(order_geometry, stop_geometry, causes)", `${bridgeSource}:serialize_order_audit`),
  step("After ownership, retain only causes backed by accepted public parents and rebuild the final ledger.", "بعد از حل مالکیت، فقط causeهایی را نگه دار که والد عمومی پذیرفته‌شده دارند و ledger نهایی را دوباره بساز.", "entry = _accepted_audit_entry(entry, accepted_sources)", `${bridgeSource}:_accepted_audit_entry`),
  step("Serialize only Orders whose First lies inside the presentation range, ordered by First then Break.", "فقط Orderهایی را serialize کن که First آن‌ها داخل بازه نمایش است و خروجی را با First و بعد Break مرتب کن.", "rows = sorted(in_range(rows), key=(first_index, break_index))", `${bridgeSource}:serialize_order_audit`),
];
ENGINE_CONTRACTS.order_audit.types = [
  type({ id: "parent_stop", en: "Order_A · parent-stop", fa: "Order_A · استاپ والد", entry: { en: "A final accepted A, S, E, or StopAll strictly stops and direct opposite Reaction geometry is accepted after its exact gate.", fa: "یک A یا S یا E یا StopAll نهایی و پذیرفته‌شده به‌صورت قطعی متوقف شود و هندسه مستقیم ری‌اکشن مخالف بعد از gate دقیق آن پذیرفته شود." }, reject: { en: "The parent is internal/rejected, geometry opens before the gate, or no accepted downstream owner retains the cause.", fa: "والد داخلی یا ردشده باشد، هندسه قبل از gate باز شود یا هیچ مالک پایین‌دستی پذیرفته‌شده‌ای cause را نگه ندارد." }, output: ["orderAudit physical geometry", "cause.type=parent-stop", "cause.parentType", "cause.parentFamily", "cause.parentSourceTime", "cause.stopEventTime"], steps: ["strict-stop accepted parent", "ask directional API for direct geometry", "build complete stop lifecycle", "register by First/Break", "attach parent provenance", "retain after accepted-parent filtering"], source: `${eSource}:_first_healthy_direct_geometry,_register_order_audit;${bridgeSource}:_accepted_audit_entry` }),
  type({ id: "reset_leg", en: "Order_B · reset-leg", fa: "Order_B · لگ ریست", entry: { en: "An accepted opposite Reset leg crosses its boundary and yields valid post-gate opposite geometry.", fa: "مرز لگ یک ریست مخالف پذیرفته‌شده شکسته شود و هندسه معتبر مخالف بعد از gate ساخته شود." }, reject: { en: "Reset ownership, leg evidence, gate chronology, or final accepted-parent filtering fails.", fa: "مالکیت ریست، evidence لگ، ترتیب gate یا فیلتر نهایی والد پذیرفته‌شده رد شود." }, output: ["orderAudit physical geometry", "cause.type=reset-leg", "cause.resetTime", "cause.boundaryBreakTime", "reactionNumber may be 0"], steps: ["form the owner Break-to-Reset leg", "cross its strict boundary", "build post-gate geometry", "register physical identity", "attach reset provenance", "merge with equal parent-stop geometry if needed"], source: `${eSource}:_first_order_b_geometry,_register_order_audit` }),
  type({ id: "merged_identity", en: "Merged multi-cause Order", fa: "Order مشترک با چند علت", entry: { en: "Two or more accepted causes resolve to the same physical First/Break identity.", fa: "دو یا چند علت پذیرفته‌شده به یک identity فیزیکی First/Break برسند." }, reject: { en: "Geometry differs, or a cause has no accepted parent after final ownership.", fa: "هندسه متفاوت باشد یا بعد از مالکیت نهایی، cause والد پذیرفته‌شده نداشته باشد." }, output: ["one orderAudit row", "deduplicated causes[]", "one physical box", "stop line only when owned by S/E/StopAll"], steps: ["key by First/Break", "merge cause arrays", "deduplicate identical cause records", "preserve canonical geometry", "serialize once", "avoid duplicate chart boxes"], source: `${eSource}:_register_order_audit;${bridgeSource}:serialize_order_audit` }),
];

ENGINE_CONTRACTS.stop_all.contract = [
  step("Consume visible accepted S and accepted E only; never discover new Reaction or Order geometry.", "فقط Sهای نمایشی پذیرفته‌شده و Eهای پذیرفته‌شده را مصرف کن و هیچ Reaction یا Order تازه‌ای نساز.", "detector = StopAllDetector(direction, visible_s, accepted_e, ...)", `${stopAllSource}:StopAllDetector.__init__`),
  step("Process E by source chronology and integrate only S with an earlier source time.", "Eها را به ترتیب زمان منبع پردازش کن و فقط Sهایی را قبل از هر E وارد کن که زمان منبعشان زودتر است.", "eligible_s = [s for s in s_zones if s.source_time < current_e.source_time]", `${stopAllSource}:detect`),
  step("Maintain group priority S-blue < E-blue < S-red < E-red and exact E family/number identity.", "اولویت گروه را به‌ترتیب S آبی، E آبی، S قرمز و E قرمز نگه دار و identity دقیق family/number در E را رعایت کن.", "priority = _SEQUENCE_PRIORITY[(kind, family)]", `${stopAllSource}:_sequence_priority`),
  step("Before integrating the current E, require at least two matching active members and a strict stop of the previous matching member by current decision.", "قبل از واردکردن E فعلی، دست‌کم دو عضو فعال هم‌گروه و استاپ قطعی عضو قبلی تا زمان تصمیم E فعلی لازم است.", "if count >= 2 and previous_stop <= current.decision: emit_stopall_1", `${stopAllSource}:detect`),
  step("Before ordinary group logic, continue from any active StopAll that strictly stopped by the current E decision.", "پیش از منطق عادی گروه، هر StopAll فعال را که تا تصمیم E فعلی قطعی متوقف شده ادامه بده.", "number = max(stopped_active_numbers) + 1", `${stopAllSource}:detect`),
  step("Copy source, decision, winning Order, and underlying E lineage from the decisive E; StopAll has no red/blue color.", "منبع، تصمیم، Order برنده و lineage زیرین E را از E تصمیم‌گیر کپی کن؛ StopAll رنگ قرمز/آبی ندارد.", "stopall = self._stopall_from_e(e, number, gate)", `${stopAllSource}:_stopall_from_e`),
  step("Calculate each StopAll's later strict stop and preserve it for the next continuation.", "استاپ قطعی بعدی هر StopAll را حساب کن و برای ادامه بعدی نگه دار.", "stop = self._strict_stop(stopall.decision_event_time, stopall.price)", `${stopAllSource}:_strict_stop`),
  step("Feed StopAll source boundaries back into E numbering until the bridge reaches an identical fixed point.", "مرزهای منبع StopAll را دوباره به شماره‌گذاری E برگردان تا Bridge به نقطه ثابت کاملاً یکسان برسد.", "resets = {item.source_time: item.number}; rerun_e_until_stable(resets)", `${bridgeSource}:reconcile_stopall_lifecycle`),
];
ENGINE_CONTRACTS.stop_all.types = [
  type({ id: "stopall_1", en: "StopAll 1 · group gate", fa: "StopAll ۱ · دروازه گروه", entry: { en: "An active group has at least two matching members and the previous matching member strictly stops no later than the current E decision.", fa: "گروه فعال دست‌کم دو عضو هم‌گروه دارد و عضو هم‌گروه قبلی حداکثر تا تصمیم E فعلی به‌صورت قطعی متوقف می‌شود." }, reject: { en: "Group count is below two, identity does not match, equality is the only touch, or the stop occurs after current decision.", fa: "تعداد گروه کمتر از دو باشد، identity یکی نباشد، فقط برخورد مساوی رخ دهد یا استاپ بعد از تصمیم فعلی باشد." }, output: ["stopAlls.number=1", "stopAlls.gateType", "stopAlls.stoppedBehavior*", "stopAlls.underlyingE*", "stopAlls.order*", "stopAlls.source*"], steps: ["integrate earlier S events", "read active dominant group", "find previous matching member", "strict-stop it by current E decision", "convert current E into StopAll1", "reset group state", "attach later StopAll stop metadata"], source: `${stopAllSource}:detect,_stopall_from_e` }),
  type({ id: "continuation", en: "StopAll 2+ · continuation", fa: "StopAll ۲ به بعد · ادامه دنباله", entry: { en: "One or more active StopAll objects strictly stop by the current E decision.", fa: "یک یا چند StopAll فعال تا زمان تصمیم E فعلی به‌صورت قطعی متوقف شوند." }, reject: { en: "No active StopAll has a strict stop by current decision.", fa: "هیچ StopAll فعالی تا تصمیم فعلی استاپ قطعی نداشته باشد." }, output: ["stopAlls.number=max(stopped)+1", "stopAlls.gateType=continuation", "new underlying E/order lineage", "stopped previous StopAll history"], steps: ["check active StopAll before normal group logic", "collect those strictly stopped by current decision", "take maximum stopped sequence number", "convert current E to the next StopAll", "remove stopped active entries", "reset group state and keep history"], source: `${stopAllSource}:detect` }),
];

// Keep the rendered contract text synchronized with the maintained Python
// branches. These are presentation corrections only; calculation authority
// remains in the source modules named above.
const patchStep = (family, index, en, code) => {
  const item = ENGINE_CONTRACTS[family].contract[index];
  if (item) {
    item.en = en;
    item.code = code;
  }
};

const patchTypeText = (family, id, values) => {
  const item = ENGINE_CONTRACTS[family].types.find((candidate) => candidate.id === id);
  if (!item) return;
  if (values.entry) item.entry.en = values.entry;
  if (values.reject) item.reject.en = values.reject;
  if (values.entryFa) item.entry.fa = values.entryFa;
  if (values.rejectFa) item.reject.fa = values.rejectFa;
  if (values.steps) item.steps = values.steps;
};

const patchFa = (family, index, fa) => {
  const item = ENGINE_CONTRACTS[family].contract[index];
  if (item) item.fa = fa;
};

patchStep(
  "reaction",
  5,
  "When invalidation and confirmation share one finest candle, the engine checks the strict Low event before the strict High event; invalidation/Reset therefore wins that tie.",
  "winner = low_event if low_event < high_event else high_event",
);
patchFa("reaction", 5, "اگر invalidation و confirmation در یک finest candle باشند، کد ابتدا Low strict و سپس High strict را بررسی می‌کند؛ بنابراین invalidation/Reset برندهٔ tie است.");
patchStep(
  "reset",
  4,
  "Clear ordinary candidate state and scan direct recovery from the first main candle strictly after reset.index; secondTime remains exact provenance only.",
  "state.clear(); recovery_start = reset.index + 1; secondTime = reset.second_time",
);
patchFa("reset", 4, "state کاندید پاک می‌شود و بازیابی مستقیم از اولین main candle با index بزرگ‌تر از reset.index شروع می‌شود؛ secondTime فقط provenance دقیق است.");
patchStep(
  "s_red",
  6,
  "Emit red only when a qualifying Order stop wins; emit blue only when the candidate wins with accepted evidence. An unqualified ordinary candidate crossing keeps the scan alive.",
  "color = 'red' if qualifying_order_stop_first else ('blue' if candidate_first_with_evidence else keep_scanning)",
);
patchFa("s_red", 6, "قرمز فقط وقتی ساخته می‌شود که Order stop واجدشرایط برنده شود؛ آبی فقط با برنده‌شدن candidate و evidence معتبر ساخته می‌شود. عبور candidate نامعتبر در مسیر عادی اسکن را متوقف نمی‌کند.");
patchStep(
  "a",
  0,
  "Sort Blue states by (reaction_number, source_time, kind), preserving the detector's lifecycle order, then pair adjacent eligible lines.",
  "states = sorted(valid_blue_states, key=(reaction_number, source_time, kind))",
);
patchFa("a", 8, "هر جفت Blue مصرف‌شده با trigger، Reaction و source دقیق منتشر می‌شود؛ provenance مربوط به stopهای بعدی S/A در downstream محاسبه می‌شود و اینجا attach نمی‌شود.");
patchStep(
  "a",
  6,
  "Keep equal directional extrema on the earlier source. For coexisting bullish Blue stops, sort by (stop_event_time, -stop_level); an exact-time tie takes the second stop as trigger and the first stop's extreme as continuation level.",
  "first, second = sorted(states, key=(stop_event_time, -stop_level)); trigger = second.stop_event_time; level = first.stop_event_extreme",
);
patchStep(
  "a",
  7,
  "Allow the protected special double-stop route to consume one valid and one internal invalid Blue.",
  "special = self._double_stop_a_candidates()",
);
patchStep(
  "a",
  8,
  "Publish each consumed Blue pair with exact trigger, Reaction, source, and current A provenance; later S/A stop provenance is computed downstream and is not attached here.",
  "emit(AZone(trigger, reaction, source, blue_stops))",
);
for (const family of ["s_red", "s_blue"]) {
  patchStep(
    family,
    5,
    "Resolve candidate-cross versus Order-stop using exact lower-second chronology; a same-finest-candle tie emits no S. An unqualified post-Order candidate cross keeps scanning, while pre-Order logic may fall back.",
    "decision = reject_same_candle_tie; ordinary_unqualified_candidate = keep_scanning; pre_order_unqualified = fallback",
  );
}
for (const family of ["e_blue", "e_red"]) {
  patchTypeText(family, `direct_order_a_${family.slice(2)}`, {
    entry: "The accepted parent strictly stops and the published directional API supplies the canonical opposite Order; a bounded geometry fallback is allowed only when that published candidate has no strict stop.",
    reject: "The published candidate is incomplete without a bounded fallback, no eligible strict stop exists, or the final direct/inherited/carried race selects another representative.",
    entryFa: "والد پذیرفته‌شده به‌صورت strict متوقف می‌شود و API جهت‌دار Order مخالف canonical را می‌دهد؛ fallback هندسی فقط وقتی مجاز است که candidate منتشرشده stop strict نداشته باشد.",
    rejectFa: "candidate منتشرشده بدون fallback کامل نیست، stop strict واجدشرایط وجود ندارد یا در رقابت نهایی direct/inherited/carried نمایندهٔ دیگری برنده می‌شود.",
    steps: ["strict-stop the parent", "read the published opposite candidate", "use bounded direct geometry only when published stop is absent", "rank direct candidates with older First on equal stop", "race direct/inherited/carried with newer First only on final equal-time tie", "choose inclusive source extreme", "emit accepted E and rebuild audit"],
  });
}
patchTypeText("s_red", "simple_red", {
  reject: "A same-candle tie is rejected; an unqualified ordinary candidate cross keeps scanning, and only a later qualifying Order stop can emit red.",
});
patchTypeText("s_blue", "type3", {
  entry: "Evaluate every eligible opposite Reset after A-stop and before the first later opposite Order confirmation; choose the earliest strict boundary crossing and require owner confirmation at or before A-stop.",
  reject: "No eligible owner, no bounded strict crossing in the lifecycle window, or no trend Reaction by the chosen crossing.",
  steps: ["collect all eligible opposite Resets", "build each Break-to-Reset leg", "bound crossing to [A-stop, next Order confirmation)", "choose earliest decision event", "require owner confirmation <= A-stop and trend evidence", "emit Type 3 with null Order fields"],
});
patchStep(
  "e_blue",
  4,
  "Direct Order candidates use older First on equal stop events; only the final direct/inherited/carried race uses newer First for an equal stop event.",
  "direct = first_order(order_candidates, key=(stop_event, first_index)); winner = min(final_representatives, key=(stop_event, -first_index))",
);
patchStep(
  "order_audit",
  4,
  "After ownership, retain causes backed by accepted calculation provenance and rebuild the final ledger; a public output switch may hide an upstream row without deleting its accepted cause.",
  "entry = _accepted_audit_entry(entry, accepted_calculation_sources)",
);
patchTypeText("order_audit", "parent_stop", {
  reject: "The parent is internal/rejected, geometry opens before the gate, or no accepted calculation provenance retains the cause.",
  rejectFa: "والد داخلی/ردشده است، هندسه پیش از gate باز می‌شود یا هیچ provenance محاسباتی پذیرفته‌شده‌ای cause را نگه نمی‌دارد.",
});
patchTypeText("order_audit", "merged_identity", {
  reject: "Geometry differs, or a cause has no accepted calculation provenance after final ownership.",
  rejectFa: "هندسه متفاوت است یا cause پس از مالکیت نهایی provenance محاسباتی پذیرفته‌شده ندارد.",
});
patchStep(
  "stop_all",
  4,
  "Before ordinary group logic, continue any active StopAll that has strictly stopped by the current E decision; gate_event is the earliest stopped member and number=max(stopped)+1.",
  "stopped = active where strict_stop.event_time <= e.decision; gate_event = min(stop.event_time); number = max(stopped)+1; gate_type = 'stopall-stop'",
);
patchStep(
  "stop_all",
  7,
  "Feed the public {source_time:number} StopAll reset map back into E; recompute S visibility each pass, return on equality, and raise on a repeated map without partial output.",
  "reset_map = {source_time: number}; if reset_map == previous_map: return; if reset_map in seen: raise ValueError('E/StopAll lifecycle reconciliation did not converge')",
);
patchFa("e_blue", 4, "در pool مستقیم، در stop برابر First قدیمی‌تر برنده است؛ فقط در رقابت نهایی direct/inherited/carried برای stop برابر First جدیدتر ترجیح دارد.");
patchFa("order_audit", 4, "پس از مالکیت، causeهای دارای provenance محاسباتی پذیرفته‌شده را نگه دار؛ خاموش‌بودن switch خروجی، cause پذیرفته‌شدهٔ upstream را حذف نمی‌کند.");
patchFa("stop_all", 4, "پیش از منطق عادی، StopAllهای فعالِ دارای stop strict تا تصمیم E را ادامه بده؛ gate_event زودترین stop عضو متوقف‌شده و number برابر max(stopped)+1 است.");
patchFa("stop_all", 7, "نقشهٔ عمومی {source_time:number} را به E برگردان؛ در هر pass دید S را از E فعلی بازسازی کن، در برابری return کن و در map تکراری بدون خروجی ناقص ValueError بده.");
patchTypeText("stop_all", "stopall_1", {
  reject: "Group count is below two, equality is the only touch, or the strict stop occurs after current decision; decisive E family/number identity may differ from the stopped group.",
  rejectFa: "تعداد گروه کمتر از دو است، فقط برابری رخ داده یا stop strict بعد از تصمیم فعلی است؛ family/number مربوط به E تصمیم‌گیرنده می‌تواند با گروه متوقف‌شده متفاوت باشد.",
});
const continuation = ENGINE_CONTRACTS.stop_all.types.find((candidate) => candidate.id === "continuation");
if (continuation) {
  continuation.output = ["stopAlls.number=max(stopped)+1", "stopAlls.gateType=stopall-stop", "stopAlls.gateEventTime=min(stopped stop events)", "stoppedBehavior=StopAll(highest)", "new underlying E/order lineage", "stopped previous StopAll history"];
  continuation.steps = ["check active StopAll before normal group logic", "collect all strictly stopped active members", "take maximum stopped sequence number and earliest gate event", "convert current E to the next StopAll", "remove stopped active entries and append the new one", "reset group state and keep history"];
}
for (const family of Object.values(ENGINE_CONTRACTS)) {
  for (const item of [...family.contract, ...family.types]) {
    for (const key of ["en", "fa", "code", "source"]) {
      if (typeof item[key] === "string") item[key] = item[key].replaceAll("_candidate_source", "_a_source");
    }
  }
}

for (const value of Object.values(ENGINE_CONTRACTS)) {
  Object.freeze(value.contract);
  Object.freeze(value.types);
}
