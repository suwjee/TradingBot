const normalizePhase = (item) => {
  let { en, fa, code } = item;
  if (code.includes("first_red.low >= (anchor.low or leg_floor)")) {
    en = "Mode A accepts FirstRed with an optional RED anchor; without an anchor it requires FirstRed.Low >= previous GREEN Low OR FirstRed.Low >= the leg floor. Equality is eligible.";
    code = "eligible = first_red.low >= anchor.low if anchor else first_red.low >= previous_green.low or first_red.low >= leg_floor";
  }
  if (code.includes("box_bottom = min(low[top_source+1:current])")) {
    en = "Mode B starts BoxBottom at top_source+1 only when that source is before FirstRed; otherwise the inclusive start is the FirstRed candle itself.";
    code = "bottom_start = top_source + 1 if top_source < current.index else current.index; box_bottom = min(low[bottom_start:current])";
  }
  if (code.includes("winner = first_exact_event(low < boundary, high > box_top)")) {
    en = "When invalidation and confirmation share one finest candle, Low is checked before High, so the strict invalidation/Reset event wins that tie.";
    code = "winner = low_event if low_event < high_event else high_event";
  }
  if (code.includes("append_reaction(); reset = first_later_second")) {
    en = "After confirmation, scan the remaining seconds for a same-candle Reset; public direct recovery starts at reset.index + 1, while secondTime is provenance.";
    code = "append_reaction(); reset = post_breakout_reset(); recovery_start = reset.index + 1";
  }
  if (code.includes("recovery_start = reset.secondTime or reset.time")) {
    en = "Reset clears candidate state, stores brokenLevel/fromFirstIndex, and direct recovery scans main candles strictly after the Reset index; secondTime does not move that public boundary.";
    code = "state.clear(); recovery_start = reset.index + 1; secondTime = reset.secondTime";
  }
  if (en.includes("starts at the strict Reset event") && code.includes("calculation_valid")) {
    en = "Reset Blue is grouped by owner First. Its public row uses the Reset main candle as source_time; the row start/end are the source candle boundary, while exact lower-second time remains internal provenance.";
    code = "source_time = reset.time; start_time = source_time - timeframe; end_time = source_time + timeframe; calculation_valid = ...";
  }
  if (code === "reaction = first_after(trigger_event, max(stop1, stop2))") {
    en = "Confirmation has two inclusive gates: the Reaction main candle is not before the trigger event, and its first eligible main time is not before the effective stop floor.";
    code = "trigger_ok = reaction.confirmation_event >= trigger_event; reaction_ok = reaction.first_time >= max(stop1, stop2)";
  }
  if (en.includes("_candidate_source")) {
    en = en.replace("_candidate_source", "_a_source");
    fa = fa.replaceAll("_candidate_source", "_a_source");
  }
  if (code === "winner = min(eligible, key=(stop_event, -first_index))") {
    en = "Within the direct order_candidates pool, equal stop events keep the older First. The final direct/inherited/carried race uses newer First only for an equal stop event.";
    code = "direct = first_order(order_candidates, key=(stop_event, first_index)); winner = min(final_representatives, key=(stop_event, -first_index))";
  }
  if (code === "family = 'red' when red parent/order dominates") {
    en = "Chronological ownership selects the earliest decision; red-family priority applies only when candidates stop in the same main candle, so a nested blue E may remain.";
    code = "owner = earliest_decision; same_candle_tie = StopAll > E_red > S_red > E_blue > S_blue > A";
  }
  if (code === "decision = order_cross first; tie => None") {
    en = "Same-finest-candle candidate and Order crossings reject S. An unqualified candidate cross in ordinary post-Order scanning keeps searching; a later qualifying Order stop may still emit red.";
    code = "decision = reject_same_candle_tie; ordinary_unqualified_candidate = keep_scanning; pre_order_unqualified = fallback";
  }
  if (code === "type3 = reset_leg_cross + trend_reaction_before_cross") {
    en = "Type 3 evaluates every eligible Reset in [A-stop, next Order confirmation), chooses the earliest strict boundary crossing, and requires owner confirmation at or before A-stop.";
    code = "candidates = [reset for reset in eligible_resets if a_stop <= decision < deadline]; type3 = min(candidates, key=decision_time)";
  }
  if (en.includes("discard causes without an accepted public parent")) {
    en = "Collect stopped-A causes and accepted E ledger causes; keep causes with accepted calculation provenance even when a public output switch hides an upstream row.";
  }
  if (code === "while resets_changed: rerun_E_with_sequence_resets()") {
    en = "Recompute S visibility from the current E state, rerun E/StopAll, compare only {source_time:number}; a repeated map raises the non-convergence error and emits no partial result.";
    code = "reset_map = {source_time: number}; if reset_map == previous_map: return; if reset_map in seen: raise ValueError('E/StopAll lifecycle reconciliation did not converge')";
  }
  if (code === "gate = count >= 2 and previous_stop <= current_e.decision") {
    code = "gate = count >= 2 and previous_stop <= current_e.decision; gate_type = 'stopall-stop'";
  }
  return { ...item, en, fa, code };
};

const guide = (title, fa, phases, checks, output) => Object.freeze({
  title,
  fa,
  phases: Object.freeze(phases.map((item) => Object.freeze(normalizePhase(item)))),
  checks: Object.freeze(checks),
  output: Object.freeze(output),
});

// This is intentionally a compact, non-executable guide.  Each line names the
// maintained Python/Bridge operation that owns the calculation; it is not a
// second implementation of the trading rules.
export const CALCULATION_GUIDES = Object.freeze({
  reaction: guide(
    "Reaction calculation cheat sheet",
    "راهنمای محاسبه Reaction",
    [
      { en: "Bridge validates the selected range, builds contiguous main and lower-timeframe candles, and converts OHLC to Decimal; Open <= Close is GREEN (including doji).", fa: "Bridge بازهٔ انتخابی را اعتبارسنجی می‌کند، کندل‌های اصلی و lower را می‌سازد و OHLC را Decimal می‌کند؛ Open <= Close سبز است و دوجی هم سبز محسوب می‌شود.", code: "candles = normalize_and_slice(raw, from_time, to_time + timeframe)" },
      { en: "Mode A opens at the selected-range start and after each Reset. It keeps a leg floor and optional RED anchor, then accepts FirstRed after GREEN only when its Low preserves the applicable floor.", fa: "Mode A در ابتدای بازه و بعد از هر Reset باز می‌شود؛ کف لگ و RED anchor اختیاری را نگه می‌دارد و FirstRed بعد از GREEN را فقط وقتی می‌پذیرد که Low آن کف مالک را حفظ کند.", code: "mode = 'A'; eligible = first_red.low >= (anchor.low or leg_floor)" },
      { en: "Mode A BoxTop is the greater of the preceding GREEN run high and FirstRed.High; BoxBottom starts at FirstRed.Low. The leg boundary/anchor stays frozen for invalidation.", fa: "در Mode A، BoxTop بزرگ‌ترِ سقف run سبز قبلی و Highِ FirstRed است؛ BoxBottom از Lowِ FirstRed شروع می‌شود و boundary لگ برای ابطال ثابت می‌ماند.", code: "box_top = max(green_run_high, first_red.high); box_bottom = first_red.low" },
      { en: "Mode B starts after a confirmed Reaction that has not reset. A RED candle opens a candidate with BoxTop=max(running_peak, RED.High) and BoxBottom equal to the minimum Low after the chosen BoxTop source through that candle.", fa: "Mode B بعد از Reaction تأییدشده‌ای فعال می‌شود که Reset نشده باشد؛ کندل RED کاندیدی با BoxTop=max(running_peak, RED.High) و کمترین Low بعد از منبع انتخاب‌شدهٔ BoxTop تا همان کندل می‌سازد.", code: "box_top = max(running_peak, red.high); box_bottom = min(low[top_source+1:current])" },
      { en: "While waiting, lower lows may move BoxBottom but never move the frozen break level. A strict High > BoxTop confirms; equality does not.", fa: "در انتظار تأیید، Low پایین‌تر فقط BoxBottom را جابه‌جا می‌کند و سطح شکست ثابت می‌ماند؛ تأیید فقط با High > BoxTop است و برابری کافی نیست.", code: "confirmed = lower_or_main.high > candidate.box_top" },
      { en: "If invalidation and confirmation occur in one main candle, the first lower-second event wins. A strict low below the Mode-A owner boundary invalidates before confirmation.", fa: "اگر ابطال و تأیید در یک کندل اصلی باشند، اولین رویداد lower-second برنده است؛ Low پایین‌تر از boundary مالک در Mode A پیش از تأیید کاندید را باطل می‌کند.", code: "winner = first_exact_event(low < boundary, high > box_top)" },
      { en: "After confirmation, the engine records exact Break provenance, scans the remaining seconds for a same-candle Reset, then resumes Mode B or clears state and starts direct recovery after Reset.", fa: "بعد از تأیید، provenance دقیق Break ثبت می‌شود، ثانیه‌های باقی‌مانده برای Reset همان کندل بررسی می‌شوند و سپس Mode B ادامه می‌یابد یا بعد از Reset بازیابی مستقیم آغاز می‌شود.", code: "append_reaction(); reset = first_later_second(low < confirmed_bottom)" },
      { en: "The Bridge serializes First/BoxTop/BoxBottom/Break/mode and Reset ownership; JavaScript only renders these returned objects.", fa: "Bridge فیلدهای First/BoxTop/BoxBottom/Break/mode و مالکیت Reset را serialize می‌کند و JavaScript فقط آبجکت برگشتی را رسم می‌کند.", code: "payload.reactions = serialize(result.reactions); payload.resets = serialize(result.resets)" },
    ],
    ["Decimal OHLC", "strict < / > comparisons", "lower-second chronology", "frozen Mode-A owner boundary", "selected-range isolation"],
    ["reactions[]", "resets[]", "mode=A or B", "breakTime on the main candle", "internal exact Break event", "fromFirstIndex ownership"],
  ),
  reset: guide(
    "Reaction Reset calculation cheat sheet",
    "راهنمای محاسبه Resetِ Reaction",
    [
      { en: "For the bullish path, use only a confirmed Reaction owner and its confirmed BoxBottom.", fa: "در مسیر صعودی فقط Reaction تأییدشده و BoxBottom همان مالک استفاده می‌شود.", code: "level = owner.box_bottom" },
      { en: "A same-candle Reset scans lower candles strictly after the exact Break and stores secondTime. A later Reset uses lower chronology only for a race, then stores the owning main candle with secondTime=null.", fa: "Reset همان کندل lowerها را دقیقاً بعد از Break اسکن و secondTime را ذخیره می‌کند؛ Reset دیرتر فقط برای حل race از ترتیب lower استفاده می‌کند و با secondTime=null روی کندل اصلی مالک ذخیره می‌شود.", code: "same_candle.secondTime = exact_cross; later.secondTime = None" },
      { en: "For a same-main-candle race, scan only seconds after confirmation. Preserve the main index plus exact secondTime.", fa: "در race داخل یک کندل اصلی، فقط ثانیه‌های بعد از تأیید بررسی می‌شوند و index اصلی همراه secondTime دقیق حفظ می‌شود.", code: "secondTime = first_strict_cross_after(confirmation_time)" },
      { en: "Reset clears ordinary candidate state, stores brokenLevel and fromFirstIndex, and opens direct recovery after its exact gate when present or its main-candle time otherwise.", fa: "Reset وضعیت کاندید عادی را پاک می‌کند، brokenLevel و fromFirstIndex را نگه می‌دارد و بازیابی مستقیم را از gate دقیق، و در نبود آن از زمان کندل اصلی، باز می‌کند.", code: "state.clear(); recovery_start = reset.secondTime or reset.time" },
      { en: "Bridge returns the reset row; no browser-side Reset or Reaction is recomputed.", fa: "Bridge ردیف Reset را برمی‌گرداند و مرورگر Reset یا Reaction را دوباره محاسبه نمی‌کند.", code: "payload.resets = serialize_resets(resets)" },
    ],
    ["strict opposite-boundary cross", "owner lifecycle still active", "exact lower-second time", "no future candle outside selected range"],
    ["index", "time", "secondTime", "brokenLevel", "fromFirstIndex"],
  ),
  blue_line: guide(
    "Blue Line calculation cheat sheet",
    "راهنمای محاسبه Blue Line",
    [
      { en: "Process Reactions in formation order. Mode-A reference is anchor_value, falling back to leg_boundary_value; Mode-B reference is the previous Reaction opposite boundary.", fa: "Reactionها به ترتیب تشکیل مصرف می‌شوند؛ مرجع Mode A همان anchor_value و در نبود آن leg_boundary_value است و Mode B از مرز مخالف Reaction قبلی استفاده می‌کند.", code: "reference = reaction.anchor_value or reaction.leg_boundary_value" },
      { en: "Calculate the bullish Fibonacci level with Decimal('0.618'): top - 0.618*(top-reference).", fa: "سطح Fibonacci صعودی با Decimal('0.618') از فرمول top - 0.618*(top-reference) حساب می‌شود.", code: "fib = top - Decimal('0.618') * (top - reference)" },
      { en: "A bullish strike needs a strict new Low below the previous comparison level. The pending extreme may be replaced by a lower Low, and any same or later GREEN main candle confirms it; doji is GREEN.", fa: "Strike صعودی به Low جدیدِ strict زیر comparison قبلی نیاز دارد. extreme معلق با Low پایین‌تر جایگزین می‌شود و هر کندل main سبز در همان لحظه یا بعدتر آن را تأیید می‌کند؛ دوجی هم GREEN است.", code: "pending = lower_strict_extreme; confirmed_by = any_GREEN_at_or_after_pending" },
      { en: "If the pending strike survives to the Reaction Break, inspect lower-second data from the pending source through the Break candle. A strict penetration before or at Break confirms it and maps the decisive second to its main candle.", fa: "اگر strike معلق تا Break Reaction باقی بماند، lower-second را از source آن تا کندل Break بررسی کن. نفوذ strict پیش از یا هم‌زمان با Break آن را تأیید می‌کند و second تعیین‌کننده به main candle خودش map می‌شود.", code: "confirmed_by = _intrabar_pending_confirmation(start=pending.source_time, break=break_time)" },
      { en: "Emit Scale only when current strikeCount > previousStrikeCount and the stateful spacing lock is open. Suppressed scales still update the reference count.", fa: "Scale فقط وقتی منتشر می‌شود که strikeCount فعلی از قبلی بیشتر و spacing lock باز باشد؛ Scale سرکوب‌شده همچنان count مرجع را به‌روزرسانی می‌کند.", code: "emit_scale = previous_count is not None and count > previous_count and spacing_open" },
      { en: "Scale linePrice is one third of the decisive candle range from the directional floor/ceiling; Reset linePrice is one fifth of its Reset candle range.", fa: "linePrice در Scale یک‌سوم بازهٔ کندل decisive از سمت جهت روند و در Reset یک‌پنجم بازهٔ کندل Reset است.", code: "bull_scale = low + (high-low)/3; bull_reset = low + (high-low)/5" },
      { en: "Reset Blue is grouped by owner First and starts at the strict Reset event. A same-index prior-Blue stop plus a lower new source extreme marks the internal line calculation_valid=False.", fa: "Reset Blue با First مالک گروه‌بندی می‌شود و از رویداد strict Reset شروع می‌شود. اگر Blue قبلی روی همان index stop شود و sourceExtreme جدید پایین‌تر باشد، خط داخلی calculation_valid=False می‌گیرد.", code: "calculation_valid = not(prior_stop_on_reset_index and source.low < prior.source_extreme)" },
      { en: "Blue output itself has no stop fields. ADetector later builds private BlueState rows and finds each valid Blue's first strict stop; an invalid Reset Blue remains only for the protected special-A path.", fa: "خروجی Blue خودش فیلد stop ندارد. ADetector بعداً BlueStateهای داخلی را می‌سازد و اولین stop strict هر Blue معتبر را پیدا می‌کند؛ Reset Blue نامعتبر فقط برای مسیر محافظت‌شدهٔ A خاص می‌ماند.", code: "blue_states = ADetector._build_blue_states(public_blue_lines)" },
    ],
    ["Reaction order", "Decimal 0.618", "strict strike", "spacing lock", "calculationValid", "source extreme stop"],
    ["kind=scale/reset", "fibonacciLevel", "strike counts", "linePrice", "source geometry", "private downstream BlueState stop (not serialized in blueLines)"],
  ),
  a: guide(
    "A calculation cheat sheet",
    "راهنمای محاسبه A",
    [
      { en: "Build BlueState only from calculation-valid Blue lines; formation time is Reaction confirmation for Scale and exact Reset crossing for Reset Blue.", fa: "BlueState فقط از Blueهای معتبر ساخته می‌شود؛ زمان تشکیل Scale زمان تأیید Reaction و زمان تشکیل Reset Blue عبور دقیق Reset است.", code: "states = build_blue_states(valid_blue_lines)" },
      { en: "Resolve each Blue's first strict source-extreme stop from lower candles; pair adjacent states once per lifecycle.", fa: "اولین stop strict از extreme منبع هر Blue پیدا می‌شود و stateهای مجاور هر lifecycle فقط یک‌بار جفت می‌شوند.", code: "stop = first(lower.low < source_extreme); pair(previous, current)" },
      { en: "Try the three ordinary triggers: inherited Reaction stop, previous Blue stopped first, or coexisting Blue stops. The next Blue formation is the expiry deadline.", fa: "سه trigger عادی بررسی می‌شوند: stop به‌ارث‌رسیده از Reaction، توقف Blue قبلی، یا توقف هم‌زمان دو Blue؛ تشکیل Blue بعدی deadline است.", code: "trigger = inherited or previous_stop or coexisting_stops" },
      { en: "Find the first qualifying same-direction Reaction after the trigger and after both required stops; no confirmation means no A.", fa: "اولین Reaction هم‌جهتِ واجد شرایط بعد از trigger و بعد از هر دو stop لازم انتخاب می‌شود؛ بدون آن A ساخته نمی‌شود.", code: "reaction = first_after(trigger_event, max(stop1, stop2))" },
      { en: "A price/source is the directional extreme over the inclusive trigger-index through Reaction-break range; _range_extreme and _candidate_source replace only a strictly better value, so equal extrema keep the earlier source.", fa: "قیمت و sourceِ A extreme جهت‌دار در بازهٔ inclusive از trigger تا Break Reaction است؛ _range_extreme و _candidate_source فقط مقدار strict بهتر را جایگزین می‌کنند و extreme برابر source زودتر را نگه می‌دارد.", code: "source = first_strict_extreme(candles[trigger_index:reaction.break_idx+1])" },
      { en: "For coexisting bullish Blue stops, sort by (stop_event_time, -stop_level), so a higher stop level wins an exact-time tie. The trigger then uses the second stop event while continuation level/source come from the first stop.", fa: "برای stopهای هم‌زمان Blue صعودی، بر اساس (stop_event_time, -stop_level) مرتب کن تا در زمان برابر stop level بالاتر برنده باشد. سپس trigger از رویداد stop دوم و continuation level/source از stop اول می‌آید.", code: "first, second = sorted(stops, key=(stop_event_time, -stop_level)); trigger=second.stop_event_time; level=first.stop_event_extreme" },
      { en: "The protected double-stop path may consume one public and one internal invalid Blue when the invalid line strictly crosses the prior source on its own formation candle.", fa: "مسیر double-stop محافظت‌شده می‌تواند یک Blue عمومی و یک Blue داخلی نامعتبر را مصرف کند، اگر خط نامعتبر در کندل تشکیل خودش از source قبلی strict عبور کند.", code: "special = valid_blue + internal_invalid_blue with same-index strict cross" },
      { en: "Bridge removes rejected A identities before publication. Every public aZones row is accepted and therefore serializes calculationValid=true.", fa: "Bridge شناسه‌های A ردشده را قبل از خروجی حذف می‌کند. پس هر ردیف عمومی aZones پذیرفته‌شده است و calculationValid=true دارد.", code: "payload.aZones = serialize_a_zones(display_a_zones_without_invalid_identities)" },
    ],
    ["valid Blue only", "first strict Blue stops", "pair deadline", "Reaction after both stops", "inclusive source range", "double-stop guards"],
    ["aZones", "triggerEventTime", "continuationLevel", "reaction provenance", "calculationValid"],
  ),
  s_red: guide(
    "S red calculation cheat sheet",
    "راهنمای محاسبه S قرمز",
    [
      { en: "Start from an eligible A outside stopped-parent ownership and locate its first strict A stop. Open the a_ownership_window immediately, even before S decides.", fa: "از A واجد شرایط خارج از ownership والد متوقف‌شده شروع کن و اولین stop strict آن را پیدا کن؛ a_ownership_window را همان لحظه، حتی پیش از تصمیم S، باز کن.", code: "a_stop = first(low < A.price); window = (a_stop_event_time, None)" },
      { en: "Keep the window open while S is pending, so later A source events inside it cannot own S. A successful S closes it at source_time + timeframe; no S leaves pending ownership open.", fa: "تا وقتی S معلق است پنجره را باز نگه دار تا source event مربوط به Aهای بعدی داخل آن مالک S نشود. S موفق پنجره را در source_time + timeframe می‌بندد و نبود S مالکیت معلق را باز نگه می‌دارد.", code: "close_at = s_source_time + timeframe if S else None" },
      { en: "Treat the first healthy opposite Reaction after A-stop as the Order input. Its stop is the Mode-A leg-head High or the previous opposite Reaction BoxTop for Mode B.", fa: "اولین Reaction مخالف سالم بعد از A-stop ورودی Order است. stop آن در Mode A از High سر لگ و در Mode B از BoxTop واکنش مخالف قبلی می‌آید.", code: "order_stop = mode_a_leg_head_high or previous_opposite_reaction.box_top" },
      { en: "Choose pre-order, nested advanced, simple, or post-order fallback candidate geometry with its own tie rule.", fa: "هندسهٔ candidate از مسیر pre-order، nested advanced، simple یا fallback بعد از Order انتخاب می‌شود و هر مسیر tie rule خودش را دارد.", code: "candidate = pre_order or advanced or simple or after_order" },
      { en: "Scan exact lower-second events: candidate Low < candidate price versus Order High > order stop. Same finest-candle tie emits no S; Order first emits red.", fa: "رویدادهای lower-second را مقایسه کن: Low کاندید زیر قیمت در برابر High Order بالای stop؛ tie در یک finest candle هیچ S نمی‌سازد و Order زودتر قرمز است.", code: "decision = order_cross first; tie => None" },
      { en: "Store S source/decision provenance. Independently, the stopped-A audit has already recorded the physical Order and every accepted A parent-stop cause.", fa: "منبع و زمان تصمیم S را ذخیره کن. مستقل از نتیجه S، ممیزی A متوقف‌شده از قبل Order فیزیکی و همه علت‌های parent-stop مربوط به A پذیرفته‌شده را ثبت کرده است.", code: "emit(red_s); audit[(First, Break)].a_causes += (A.source, A.stop_event)" },
      { en: "If an invalid bullish leg head has a pending S, keep its internal ownership until the exact head stop and block opposite-Reaction Firsts from the outer Order/E space; a head without pending S does not block unrelated Orders.", fa: "اگر leg head صعودی نامعتبر S معلق داشته باشد، ownership داخلی را تا stop دقیق head نگه دار و Firstهای Reaction مخالف را از فضای بیرونی Order/E مسدود کن؛ head بدون S معلق Orderهای نامرتبط را مسدود نمی‌کند.", code: "blocked_firsts = blocked_orders_while_invalid_leg_heads_are_live(...)" },
    ],
    ["A ownership window", "opposite Order", "candidate path", "strict lower chronology", "same-candle tie rejection"],
    ["sZones.color=red", "order geometry", "decisionEventTime", "parent A provenance", "order audit cause"],
  ),
  s_blue: guide(
    "S blue / Type 3 calculation cheat sheet",
    "راهنمای محاسبه S آبی و Type 3",
    [
      { en: "Use the same A-stop and opposite-Order setup as S red, opening a_ownership_window immediately and keeping it open while S is pending. Then compare candidate-cross and Order-stop in lower-second chronology.", fa: "همان setup مربوط به A-stop و Order مخالف S قرمز را بردار، a_ownership_window را بلافاصله باز و تا تصمیم S معلق باز نگه دار؛ سپس candidate-cross و Order-stop را با ترتیب lower-second مقایسه کن.", code: "window = (a_stop_event_time, None); candidate_cross = low < candidate_price; order_stop = high > order_stop_level" },
      { en: "Candidate-first can emit blue only when aligned Reset Blue formation or an ordinary same-direction Reaction is evidence by the crossing event.", fa: "اگر candidate زودتر عبور کند، S آبی فقط وقتی مجاز است که Reset Blue هم‌راستا یا Reaction عادی هم‌جهت تا زمان عبور evidence باشد.", code: "blue = candidate_first and (reset_blue <= cross or reaction <= cross)" },
      { en: "Type 3 is checked before the first later opposite Order confirmation: owner Reset leg Break-to-Reset geometry, strict post-Reset boundary cross, and a trend Reaction by that cross.", fa: "Type 3 پیش از تأیید اولین Order مخالف بعدی بررسی می‌شود: هندسهٔ Break-to-Reset مالک، عبور strict بعد از Reset و Reaction روند تا زمان عبور لازم است.", code: "type3 = reset_leg_cross + trend_reaction_before_cross" },
      { en: "Type 3 emits blue with reset provenance and null Order fields; it does not invent an Order box or stop.", fa: "Type 3 با رنگ آبی و provenance Reset منتشر می‌شود و فیلدهای Order را null نگه می‌دارد؛ Order خیالی ساخته نمی‌شود.", code: "emit(formationType='type3', color='blue', order=None)" },
      { en: "Bridge keeps exact source, candidate/decision time, formationType and nullable Order fields.", fa: "Bridge source، زمان candidate/decision، formationType و فیلدهای nullableِ Order را دقیق نگه می‌دارد.", code: "payload.sZones = serialize_s_zones(accepted_s)" },
      { en: "For a bullish invalid leg head with a real pending S, opposite-Reaction Firsts opened before the head's strict stop are blocked from outer Order/E ownership; selection resumes after that stop.", fa: "در leg head صعودی نامعتبرِ دارای S واقعی معلق، Firstهای Reaction مخالف پیش از stop strict head از ownership بیرونی Order/E مسدود می‌شوند و انتخاب بعد از stop ادامه پیدا می‌کند.", code: "blocked_order_first_times.update(blocked_orders_while_invalid_leg_heads_are_live(...))" },
    ],
    ["A-stop gate", "strict candidate/order race", "evidence by crossing", "Type-3 deadline", "nullable Order contract"],
    ["sZones.color=blue", "formationType=simple/advanced/type3", "evidence", "decisionEventTime", "reset provenance"],
  ),
  e_blue: guide(
    "E blue calculation cheat sheet",
    "راهنمای محاسبه E آبی",
    [
      { en: "Start from an accepted blue S, then recursively from each accepted blue E child after its strict parent stop.", fa: "از S آبی پذیرفته‌شده شروع کن و بعد از stop strict هر E آبی، child بعدی را به‌صورت بازگشتی بساز.", code: "parent_stop = first(low < parent.price); parent_type in {'S','E'}" },
      { en: "Merge identical direct Order_A and Reset-leg Order_B First/Break geometry, then let that result compete with the Blue-S inherited Order and carried-live accepted Orders.", fa: "هندسه‌های همسان First/Break مربوط به Order_A مستقیم و Order_B حاصل از reset-leg را ادغام کن؛ سپس نتیجه را با Order به‌ارث‌رسیده از S آبی و Orderهای پذیرفته‌شدهٔ carried-live وارد رقابت کن.", code: "orders = compete(merge_by_identity(direct_A, reset_leg_B), inherited_s, carried_live)" },
      { en: "Limit candidates by the earliest known Order stop and any inherited-S continuous deadline, then choose the earliest completed Order; equal stop events prefer the newer First.", fa: "کاندیدها را با اولین stop شناخته‌شدهٔ Order و deadline پیوستهٔ S ارث‌رسیده محدود کن، سپس زودترین Order کامل را بردار؛ در stop برابر First جدیدتر اولویت دارد.", code: "winner = min(eligible, key=(stop_event, -first_index))" },
      { en: "E source is the inclusive directional extreme from parent stop through Order stop; decision event is max(parent_stop, order_stop).", fa: "sourceِ E extreme جهت‌دارِ inclusive از stop والد تا stop Order است و decision event برابر max این دو رویداد است.", code: "source = extreme(parent_stop, order_stop); decision=max(...)" },
      { en: "Inherit blue family, assign the active sequence number, retain stopped history, and register the accepted Order causes.", fa: "خانوادهٔ آبی، شمارهٔ sequence فعال، سابقهٔ stop‌شده و علت‌های Order پذیرفته‌شده حفظ می‌شوند.", code: "zone = E(family='blue', number=next_blue, causes=...)" },
      { en: "The Bridge/E reconciliation may rerun E after StopAll sequence resets until the reset map reaches a fixed point.", fa: "Bridge ممکن است پس از resetهای StopAll، E را تا رسیدن reset map به fixed point دوباره اجرا کند.", code: "while resets_changed: rerun_E_with_sequence_resets()" },
    ],
    ["accepted parent", "strict parent stop", "Order pool", "deadline", "identity merge", "fixed-point reset map"],
    ["eZones.family=blue", "number", "parent lineage", "Order causes", "source/decision", "orderAudit"],
  ),
  e_red: guide(
    "E red calculation cheat sheet",
    "راهنمای محاسبه E قرمز",
    [
      { en: "Use the same E lifecycle as blue, but red-family dominance is preserved whenever a red and blue candidate compete.", fa: "چرخهٔ E مانند آبی است، اما هر زمان Red و Blue رقابت کنند، dominance خانوادهٔ قرمز حفظ می‌شود.", code: "family = 'red' when red parent/order dominates" },
      { en: "Direct, Reset-leg and carried-live Order candidates are filtered by the parent gate, owner blocks, earliest known Order stop, and the inherited-S continuous deadline only when applicable.", fa: "Orderهای مستقیم، reset-leg و carried-live با gate والد، owner block، زودترین استاپ شناخته‌شده Order و فقط در صورت کاربرد با continuous deadline ارث‌رسیده از S فیلتر می‌شوند.", code: "eligible = candidates_confirmed_by(min(first_order_stop, inherited_s_deadline))" },
      { en: "Select the earliest completed Order, compute inclusive parent-stop-to-order-stop extreme, and preserve all physical causes.", fa: "زودترین Order کامل انتخاب، extreme از stop والد تا stop Order به‌صورت inclusive محاسبه و همهٔ causeهای فیزیکی حفظ می‌شوند.", code: "decision=max(parent_stop, order_stop); source=extreme_between(...)" },
      { en: "Recursive E numbering increments the active red family; StopAll boundaries restart the sequence at the recorded source time.", fa: "شماره‌گذاری بازگشتی خانوادهٔ قرمز افزایش می‌یابد و مرز StopAll در source time ثبت‌شده sequence را restart می‌کند.", code: "number = max(stopped_red_numbers, default=0) + 1" },
      { en: "Serialize E plus the accepted Order ledger; no browser-side family or number is inferred.", fa: "E و ledger سفارش پذیرفته‌شده serialize می‌شوند و مرورگر family یا number را حدس نمی‌زند.", code: "payload.eZones = serialize_e_zones(e_zones)" },
    ],
    ["red dominance", "owner/gate eligibility", "strict order stop", "inclusive extreme", "sequence reset"],
    ["eZones.family=red", "recursive number", "parentType", "Order causes", "orderAudit linkage"],
  ),
  order_audit: guide(
    "Order Audit calculation cheat sheet",
    "راهنمای محاسبه Order Audit",
    [
      { en: "Collect stopped-A causes from S and accepted E ledger causes from E; discard causes without an accepted public parent.", fa: "علت‌های A متوقف‌شده را از S و علت‌های ledgerِ E پذیرفته‌شده را از E جمع کن؛ هر علتی که والد عمومی پذیرفته‌شده ندارد کنار بگذار.", code: "combined = accepted_s_causes + accepted_e_causes" },
      { en: "Physical identity is (FirstIndex, BreakIndex). Equal identities share one complete Reaction geometry.", fa: "identity فیزیکی برابر (FirstIndex, BreakIndex) است و identityهای برابر یک هندسهٔ کامل Reaction مشترک دارند.", code: "identity = (reaction.first_idx, reaction.break_idx)" },
      { en: "Merge and deduplicate the two serialized cause shapes: parent-stop and reset-leg. carried-live stays on E lineage and does not create a third Order Audit cause or a second box.", fa: "دو شکل cause قابل‌serialize یعنی parent-stop و reset-leg را ادغام و deduplicate کن. carried-live در lineage خود E می‌ماند و cause سوم Order Audit یا box دوم نمی‌سازد.", code: "entry.causes = unique(parent_stop_causes + reset_leg_causes)" },
      { en: "Inside the bullish pipeline, compute the opposite Order stop with strict High > stopLevel and preserve its exact source/event.", fa: "داخل مسیر صعودی، stop مربوط به Order مخالف با شرط strictِ High > stopLevel حساب می‌شود و source/event دقیقش می‌ماند.", code: "stop = first(lower.high > order.stop_level)" },
      { en: "Serialize only First-in-range records sorted by First then Break; audit-only boxes do not invent stop lines.", fa: "فقط رکوردهایی که First آن‌ها داخل بازه است و بر اساس First سپس Break مرتب شده‌اند serialize می‌شوند؛ audit-only خط stop خیالی ندارد.", code: "rows = sorted(in_range(records), key=(first_index, break_index))" },
    ],
    ["accepted parents", "First/Break identity", "cause deduplication", "strict Order stop", "range filter"],
    ["orderAudit[]", "reactionMode", "full box geometry", "stop level/source/hit", "causes[]"],
  ),
  stop_all: guide(
    "StopAll calculation cheat sheet",
    "راهنمای محاسبه StopAll",
    [
      { en: "Consume only visible accepted S and accepted E; StopAll never discovers new Reaction or Order geometry.", fa: "StopAll فقط Sهای visible و Eهای پذیرفته‌شده را مصرف می‌کند و Reaction یا Order جدید کشف نمی‌کند.", code: "detector = StopAllDetector(s_zones, e_zones, candles, lower)" },
      { en: "Process E by source chronology and integrate earlier S only. Group priority is S blue < E blue < S red < E red; red E dominates blue E.", fa: "Eها بر اساس source chronology پردازش و فقط Sهای زودتر وارد می‌شوند؛ priority گروهی S blue < E blue < S red < E red است و E قرمز بر آبی غالب است.", code: "priority = {('s','blue'):1, ('e','blue'):2, ('s','red'):3, ('e','red'):4}" },
      { en: "For bullish leg ownership, the latest main candle containing a strict stop owns the transition. Only stops in that same candle use StopAll > E red > S red > E blue > S blue > A, then sequence number and deterministic source keys.", fa: "در ownership لگ صعودی، جدیدترین main candle دارای stop strict مالک transition است. فقط stopهای همان کندل با StopAll > E red > S red > E blue > S blue > A و سپس شماره دنباله و کلیدهای قطعی source حل می‌شوند.", code: "owner = max(stops, key=(stop_main_index, module_priority, number, source_time, source_index))" },
      { en: "Before ordinary group integration, continue any active StopAll that has strictly stopped by the current E decision; number=max(stopped)+1.", fa: "پیش از منطق عادی، StopAll فعالِ متوقف‌شده تا decision E فعلی بررسی و شمارهٔ بعدی max(stopped)+1 می‌شود.", code: "if active_stopall_stop <= e.decision: number=max(stopped)+1" },
      { en: "For StopAll 1, require at least two matching active members and a strict stop of the previous matching member no later than current E decision.", fa: "برای StopAll 1 حداقل دو عضو هم‌گروه و stop strict عضو قبلی تا حداکثر decision E فعلی لازم است.", code: "gate = count >= 2 and previous_stop <= current_e.decision" },
      { en: "Convert the decisive E into StopAll while copying source, decision, winning Order, lineage and gate metadata; reset group state.", fa: "E تصمیم‌گیرنده به StopAll تبدیل می‌شود و source، decision، Order برنده، lineage و gate metadata را کپی می‌کند؛ سپس group reset می‌شود.", code: "stopall = copy_e_with_gate(e, gate_type, stopped_behavior)" },
      { en: "Attach the later strict StopAll stop and feed source-time/number resets back into E until the Bridge fixed point is identical.", fa: "stop strict بعدی StopAll ثبت و resetهای source-time/number دوباره به E داده می‌شوند تا fixed point یکسان شود.", code: "stopall.stop = first(lower.low < stopall.price); reconcile_until_stable()" },
    ],
    ["accepted S/E only", "chronological source", "sequence priority", "two-member gate", "strict stop", "E feedback fixed point"],
    ["stopAlls[]", "number", "gateType", "stoppedBehavior", "underlying E/order lineage", "stopEventTime"],
  ),
});
