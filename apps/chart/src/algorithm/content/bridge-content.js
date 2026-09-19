const normalizeBridgeStep = (item) => {
  let { en, fa, code } = item;
  if (code === "valid = not strict_boundary_break; while lifecycle_changed: reconcile()") {
    en = "Strict boundary breaks normally invalidate a candidate, but an interior-leg A exception may retain a qualifying crossing; equality remains valid. Recompute affected E/StopAll state by reset map and reject repeated maps.";
    code = "valid = not strict_boundary_break or qualifying_interior_leg_a_exception; reset_map = {source_time: number}; repeated_map => ValueError";
  }
  if (en.includes("disabled upstream switch prevents")) {
    en = "A disabled switch suppresses only its requested public collection; dependencies still calculate when a downstream enabled module needs them. Disabling S also disables E/StopAll.";
  }
  if (en.includes("Close presentation lineage")) {
    en = "Close presentation lineage, remove invalid or shadowed A/S/E labels, preserve required historical parents, then serialize the eight bullish collections plus envelope and timings.";
  }
  return { ...item, en, fa, code };
};

const step = (en, fa, code, source) => Object.freeze(normalizeBridgeStep({ en, fa, code, source }));

const normalizeBridgeBranch = (item) => {
  const next = { ...item, entry: { ...item.entry }, reject: { ...item.reject } };
  if (next.id === "module_orchestration") {
    next.reject.en = "A disabled switch suppresses only its requested public collection; dependencies still calculate when a downstream enabled module needs them. Disabling S also disables E/StopAll.";
  }
  return next;
};

const branch = (input) => {
  const { id, en, fa, entry, reject, output, steps, source } = normalizeBridgeBranch(input);
  return Object.freeze({
    id,
    names: Object.freeze({ en, fa }),
    entry: Object.freeze(entry),
    reject: Object.freeze(reject),
    output: Object.freeze(output),
    steps: Object.freeze(steps.map((item) => Object.freeze(item))),
    source,
  });
};

const source = "engine/bridge/trading_pipeline.py";

export const BRIDGE_FAMILY_CONTRACT = Object.freeze({
  contract: Object.freeze([
    step(
      "Validate the request before reading data. timeframe must be at least one second and every engine path, range boundary, switch, and direction comes from the request.",
      "اول خود درخواست را چک کن. timeframe باید حداقل یک ثانیه باشد و مسیر موتورها، بازه، سوییچ‌ها و direction هم مستقیم از درخواست می‌آیند.",
      "validate(args); require(args.timeframe >= 1)",
      `${source}:main`,
    ),
    step(
      "Turn the selected interval into an independent virtual file before aggregation. Rows before from_time and rows at or after to_time + timeframe are excluded.",
      "قبل از ساخت کندل‌ها، بازه انتخابی مثل یک فایل مستقل جدا می‌شود؛ داده قبل از from_time و از to_time + timeframe به بعد اصلاً وارد محاسبه نمی‌شود.",
      "rows = isolate_raw_range(source_rows, from_time, to_time + timeframe)",
      `${source}:isolate_raw_range,main`,
    ),
    step(
      "Normalize the isolated rows once, build lower and main candle views, and give every module the same zero-based range 0..len(candles)-1.",
      "داده جداشده را یک‌بار نرمال کن، نمای lower و main را از همان داده بساز و همان بازه 0 تا آخرین کندل را به همه ماژول‌ها بده.",
      "seconds, candles = build_candle_views(rows); start_index, end_index = 0, len(candles) - 1",
      `${source}:build_candle_buckets,build_candle_objects,main`,
    ),
    step(
      "Run the bullish dependency chain in order: Reaction, Blue Line, A, S, preliminary E, ownership reconciliation, final E audit, then StopAll reconciliation.",
      "زنجیره صعودی دقیقاً با این ترتیب جلو می‌رود: Reaction، بعد Blue Line، بعد A، بعد S، بعد E اولیه، اصلاح ownership، E نهایی و در آخر StopAll.",
      "Reaction -> BlueLine -> A -> S -> E(initial) -> ownership -> E(final) -> StopAll",
      `${source}:main,reconcile_stopall_lifecycle`,
    ),
    step(
      "S and E may request opposite Order geometry as an internal input required by the bullish result. Only the requested bullish result is documented and returned by this page.",
      "S و E برای ساخت خروجی صعودی ممکن است هندسه Order مخالف را به‌عنوان ورودی داخلی بخواهند. این صفحه فقط نتیجه و روند صعودی درخواستی را توضیح می‌دهد.",
      "supporting_order_geometry = internal_dependency; published_direction = 'bullish'",
      `${source}:main`,
    ),
    step(
      "Resolve dominant stopped ownership before publication. Strict boundary breaks invalidate a candidate; equality stays valid. Re-run affected E and StopAll passes until the lifecycle no longer changes.",
      "قبل از خروجی، مالکیت رفتارهای متوقف‌شده را حل کن. عبور strict کاندید را نامعتبر می‌کند ولی برابری معتبر می‌ماند. اگر S/E/StopAll تغییر کرد، پاس‌های وابسته را دوباره اجرا کن تا نتیجه ثابت شود.",
      "valid = not strict_boundary_break; while lifecycle_changed: reconcile()",
      `${source}:split_a_zones_by_dominant_stops,reconcile_stopall_lifecycle`,
    ),
    step(
      "For bullish leg ownership, the owner is the module whose strict stop belongs to the latest main candle. Only stops in that same candle are resolved by StopAll > E red > S red > E blue > S blue > A, then sequence number and deterministic source keys.",
      "در ownership لگ صعودی، مالک ماژولی است که stop strict آن در جدیدترین main candle رخ داده است. فقط stopهای همان کندل با اولویت StopAll > E red > S red > E blue > S blue > A و سپس شماره دنباله و کلیدهای قطعی source حل می‌شوند.",
      "owner = max(stopped, key=(stop_main_index, module_priority, number, source_time, source_index))",
      `${source}:split_a_zones_by_dominant_stops`,
    ),
    step(
      "An invalid bullish leg head with a real pending S keeps its internal ownership window through the head's exact strict stop. Opposite-Reaction Firsts opened during that window cannot own the resumed outer Order/E space; after the stop, selection resumes. A head without pending S does not block unrelated Orders.",
      "leg head صعودی نامعتبرِ دارای S معلق، پنجره ownership داخلی خود را تا stop strict دقیق head حفظ می‌کند. Firstهای Reaction مخالف در این پنجره مالک فضای بیرونی Order/E پس از resume نیستند؛ بعد از stop انتخاب ادامه می‌یابد. head بدون S معلق Orderهای نامرتبط را مسدود نمی‌کند.",
      "blocked_order_first_times = blocked_orders_while_invalid_leg_heads_are_live(...) ",
      `${source}:blocked_orders_while_invalid_leg_heads_are_live`,
    ),
    step(
      "Close presentation lineage, remove invalid or shadowed A/S/E labels, preserve required historical parents, then serialize exactly eight bullish collections plus the payload envelope and timings.",
      "در پایان زنجیره نمایش را ببند؛ A/S/E نامعتبر یا پوشانده‌شده را حذف کن، والد تاریخی لازم را نگه دار و هشت collection صعودی را همراه envelope و timings serialize کن.",
      "payload['directions']['bullish'] = serialize_direction()",
      `${source}:serialize_direction,main`,
    ),
  ]),
  types: Object.freeze([
    branch({
      id: "range_isolation",
      en: "Range isolation & candles",
      fa: "جداسازی بازه و ساخت کندل‌ها",
      entry: {
        en: "A valid request supplies a source file, timeframe, from_time, to_time, and bullish direction.",
        fa: "درخواست معتبر باید فایل منبع، timeframe، from_time، to_time و direction صعودی داشته باشد.",
      },
      reject: {
        en: "timeframe is below one second, the isolated range is empty, or candle normalization cannot build the required views.",
        fa: "timeframe کمتر از یک ثانیه باشد، بازه جداشده خالی باشد یا نتوان نمای کندل لازم را ساخت.",
      },
      output: ["isolated rows", "Lower Candle[]", "Main Candle[]", "start_index=0", "end_index=len(candles)-1"],
      steps: [
        step("Validate CLI/request arguments.", "ورودی‌های درخواست را چک کن.", "validate(args)", `${source}:main`),
        step("Read and parse the source JSON once.", "JSON منبع را فقط یک‌بار بخوان و parse کن.", "source_rows = orjson.loads(source_text)", `${source}:main`),
        step("Cut the raw rows before any aggregation.", "قبل از هر aggregation، raw rowها را به بازه انتخابی محدود کن.", "rows = isolate_raw_range(...) ", `${source}:isolate_raw_range`),
        step("Build lower and timeframe buckets from the same rows.", "bucketهای lower و timeframe را از همان rowها بساز.", "second_buckets, timeframe_buckets = build_candle_buckets(...) ", `${source}:build_candle_buckets`),
        step("Build candle objects and use the whole isolated index range.", "آبجکت کندل را بساز و کل indexهای همین بازه مستقل را استفاده کن.", "start_index, end_index = 0, len(candles) - 1", `${source}:build_candle_objects`),
      ],
      source: `${source}:main,isolate_raw_range,build_candle_buckets,build_candle_objects`,
    }),
    branch({
      id: "module_orchestration",
      en: "Bullish module orchestration",
      fa: "اجرای زنجیره ماژول‌های صعودی",
      entry: {
        en: "The isolated candle views and enabled module switches are ready.",
        fa: "نمای کندل‌های جداشده و سوییچ ماژول‌های فعال آماده باشد.",
      },
      reject: {
        en: "A disabled upstream switch prevents its dependent collection from being calculated or published.",
        fa: "اگر سوییچ upstream خاموش باشد، collection وابسته به آن محاسبه یا منتشر نمی‌شود.",
      },
      output: ["ReactionResult", "BlueLine[]", "AZone[]", "SZone[]", "EZone[]", "StopAll[]", "Order audit ledger"],
      steps: [
        step("Run UnifiedReactionDetector for the isolated range.", "UnifiedReactionDetector را روی همین بازه اجرا کن.", "result = UnifiedReactionDetector(...).detect()", `${source}:main`),
        step("Build Blue Line and A from the same Reaction objects.", "Blue Line و A را از همان آبجکت‌های Reaction بساز.", "lines = detect_blue_lines(...); a_zones = detect_a_zones(...) ", `${source}:main`),
        step("Build S with exact lower-candle Order races.", "S را با رقابت زمانی دقیق Order روی lower candleها بساز.", "s_zones = SDetector(...).detect()", `${source}:main`),
        step("Build preliminary E and re-run it when accepted S changes.", "E اولیه را بساز و اگر Sهای پذیرفته‌شده تغییر کردند دوباره اجرا کن.", "preliminary_e = EDetector(...).detect()", `${source}:main`),
        step("Run the final E audit and StopAll lifecycle pass.", "E نهایی و بعد چرخه StopAll را اجرا کن.", "e_zones, stopalls = reconcile_stopall_lifecycle(...) ", `${source}:reconcile_stopall_lifecycle`),
      ],
      source: `${source}:main,reconcile_stopall_lifecycle`,
    }),
    branch({
      id: "ownership_reconciliation",
      en: "Ownership & visibility reconciliation",
      fa: "حل ownership و فیلتر نمایش",
      entry: {
        en: "Preliminary A, S, E, StopAll, and exact stop events exist for the bullish range.",
        fa: "A، S، E، StopAll اولیه و زمان دقیق stopها برای بازه صعودی آماده باشد.",
      },
      reject: {
        en: "An object loses ownership to a later dominant strict stop, is invalidated by provenance, or is shadowed at the same source by E/StopAll.",
        fa: "آبجکت با stop strict و قوی‌ترِ بعدی ownership را ببازد، provenance آن نامعتبر شود یا در همان source زیر E/StopAll قرار بگیرد.",
      },
      output: ["display_a_zones", "display_s_zones", "final_e_zones", "stopalls", "accepted Order audit lineage"],
      steps: [
        step("Split A by dominant stop ownership. Choose the latest stop-containing main candle first, then resolve only same-candle ties by module priority and sequence.", "Aها را با ownership استاپ غالب جدا کن؛ ابتدا جدیدترین main candle دارای stop را انتخاب کن و فقط tieهای همان کندل را با priority ماژول و sequence حل کن.", "calculation_a, invalid_a = split_a_zones_by_dominant_stops(...) ", `${source}:split_a_zones_by_dominant_stops`),
        step("Block Orders that belong to invalid live leg heads.", "Orderهای متعلق به leg head نامعتبر و هنوز زنده را ببند.", "blocked_order_first_times.update(...) ", `${source}:blocked_orders_while_invalid_leg_heads_are_live`),
        step("Rebuild final E using only accepted upstream ownership.", "E نهایی را فقط با ownership پذیرفته‌شده upstream دوباره بساز.", "preliminary_e = EDetector(...).detect()", `${source}:main`),
        step("Keep historical parents referenced by final children.", "والدهای تاریخی که child نهایی به آن‌ها اشاره دارد نگه دار.", "final_* = lineage_closure(final_*)", `${source}:main`),
        step("Remove same-source A/S when E or StopAll owns that source.", "اگر E یا StopAll مالک همان source است، A/S هم‌منبع را از نمایش بردار.", "display = remove_shadowed_sources(...) ", `${source}:main`),
      ],
      source: `${source}:split_a_zones_by_dominant_stops,blocked_orders_while_invalid_leg_heads_are_live,main`,
    }),
    branch({
      id: "serialization",
      en: "Bullish payload serialization",
      fa: "ساخت payload صعودی",
      entry: {
        en: "The final visible collections and accepted Order ledger are stable.",
        fa: "collectionهای نهایی قابل‌نمایش و دفتر Orderهای پذیرفته‌شده ثابت شده باشند.",
      },
      reject: {
        en: "Invalid internal Blue lines, rejected A/S identities, out-of-range sources, and unsupported hidden candidates are not serialized as public rows.",
        fa: "Blue داخلی نامعتبر، شناسه A/S ردشده، source بیرون بازه و کاندید مخفی بدون پشتیبانی وارد ردیف عمومی نمی‌شوند.",
      },
      output: ["payload envelope", "directions.bullish", "eight serialized collections", "timings.phasesMs", "timings.bridgeTotalMs"],
      steps: [
        step("Create the version, feature-switch, timeframe, and actual-range envelope.", "envelope شامل versionها، سوییچ‌ها، timeframe و بازه واقعی را بساز.", "payload = {engine, versions, enabled_flags, timeframe, actualFrom, actualTo}", `${source}:main`),
        step("Serialize each accepted collection with Decimal values as strings and datetimes as epochs.", "هر collection پذیرفته‌شده را با Decimal به شکل string و datetime به شکل epoch serialize کن.", "serialize_* (accepted_items)", `${source}:serialize,serialize_blue_lines,serialize_a_zones,serialize_s_zones,serialize_e_zones,serialize_stopalls`),
        step("Merge Order audit rows by physical First/Break identity and combine causes.", "ردیف‌های Order Audit را با شناسه فیزیکی First/Break یکی کن و causeها را ادغام کن.", "orderAudit = serialize_order_audit(...) ", `${source}:serialize_order_audit`),
        step("Attach exactly eight collections under directions.bullish.", "دقیقاً هشت collection را زیر directions.bullish بگذار.", "payload['directions']['bullish'] = serialize_direction()", `${source}:main`),
        step("Add phase and total timings, compact-encode JSON, and print one response.", "زمان هر فاز و زمان کل را اضافه کن، JSON را فشرده encode کن و یک پاسخ چاپ کن.", "print(json.dumps(payload, separators=(',', ':'))) ", `${source}:main`),
      ],
      source: `${source}:serialize,serialize_blue_lines,serialize_a_zones,serialize_s_zones,serialize_e_zones,serialize_stopalls,serialize_order_audit,main`,
    }),
  ]),
});

export const BRIDGE_MODULE_SUMMARY = Object.freeze({
  code: `def build_bullish_payload(args):
    validate(args)
    source_rows = orjson.loads(read(args.data))
    rows = isolate_raw_range(source_rows, args.from_time, args.to_time + args.timeframe)
    require(rows)

    second_buckets, timeframe_buckets = build_candle_buckets(rows, args.timeframe)
    seconds = build_candle_objects(second_buckets)
    candles = seconds if args.timeframe == 1 else build_candle_objects(timeframe_buckets)
    start_index, end_index = 0, len(candles) - 1

    requested = ("bullish",)
    reaction_directions = ("bullish", "opposite Order direction") if S_enabled else requested
    reactions = {
        direction: UnifiedReactionDetector(candles, seconds, 0, end_index, direction).detect()
        for direction in reaction_directions
    }

    if S_enabled and E_engine_exists:
        # Opposite reactions are calculation-only Order geometry for bullish S/E.
        blue = detect_blue_lines("bullish", reactions["bullish"], candles, seconds, ...)
        all_a = detect_a_zones("bullish", reactions["bullish"], blue, candles, seconds, ...)
        s_detector = SDetector(
            "bullish", reactions["bullish"], reactions["opposite Order direction"], blue, all_a,
            initial_order_geometry=directional_a_stop_order_finder(...),
        )
        all_s_candidates = s_detector.detect()

        e_detector = EDetector(
            "bullish", ..., all_s_candidates,
            initial_order_audit=s_detector.order_audit,
        )
        preliminary_e = e_detector.detect()
        accepted_s = remove_s_reset_by_preliminary_e(all_s_candidates, preliminary_e)
        if accepted_s_changed:
            preliminary_e = rerun_e(accepted_s, blocked_order_first_times=removed_s_sources)

        visible_a = visible_a_after_s_ownership_and_stops(
            s_detector.eligible_a_zones, accepted_s,
        )
        accepted_a, invalid_a = split_a_zones_by_dominant_stops(
            visible_a, all_s_candidates, preliminary_e, stopalls=[],
        )
        invalid_s = s_whose_parent_a_is_invalid(all_s_candidates, invalid_a)
        accepted_a_sources = _a_zones_for_module_engines(
            s_detector.eligible_a_zones, accepted_s, preliminary_e, "bullish",
        )
        accepted_audit = keep_s_order_causes_from_accepted_a(
            s_detector.order_audit, accepted_a_sources,
        )
        blocked_firsts = orders_owned_while_invalid_leg_heads_are_live(invalid_a)

        e_detector = rebuild_e_detector(
            accepted_s,
            initial_order_audit=accepted_audit,
            blocked_order_first_times=blocked_firsts,
        )
        e_zones = e_detector.detect()                 # final audit pass; full S is still input
        accepted_s_for_display = accepted_s - invalid_s
        if StopAll_engine_exists:
            e_zones, stopalls = reconcile_stopall_lifecycle(
                e_detector, accepted_s, e_zones,
            )                                        # fixed point
        else:
            stopalls = []

        display_e = remove_sources_owned_by_stopall(e_zones, stopalls)
        display_s = visible_s_after_module_resets(all_s_candidates, display_e + stopalls)
        display_s += historical_s_parents_referenced_by(display_e)
        display_a = visible_a_after_module_boundaries(visible_a, display_s, display_e + stopalls)
        display_a += historical_a_parents_referenced_by(display_s)
        display_a, display_s = remove_same_sources_owned_by(display_e, stopalls)
        display_a -= invalid_a
        display_s = display_s & accepted_s_for_display
        display_a, display_s, display_e, stopalls = filter_source_index_to_isolated_range(...)
    else:
        # When downstream switches/engines are absent, calculate only the
        # dependencies requested by Blue/A/S and keep E/StopAll empty.
        blue = detect_blue_lines(...) if (Blue_enabled or A_enabled or S_enabled) else []
        all_a = detect_a_zones(...) if (A_enabled or S_enabled) else []
        display_s = SDetector(...).detect() if S_enabled else []
        display_a = visible_a_after_s_ownership_and_stops(all_a, display_s)
        display_e, stopalls = [], []

    payload = build_payload_envelope(args, candles)
    payload["directions"]["bullish"] = serialize_direction(
        reactions["bullish"],
        public_calculation_valid_blue_if_enabled(blue),
        display_a_if_enabled, display_s, display_e, stopalls,
        serialize_order_audit(
            e_detector, s_detector,
            accepted_a_sources={a.source_time for a in display_a},
        ) if e_detector is not None else [],
    )
    payload["timings"] = measured_phases_and_total()
    return payload`,
  sources: Object.freeze([
    `${source}:main`,
    `${source}:split_a_zones_by_dominant_stops`,
    `${source}:reconcile_stopall_lifecycle`,
    `${source}:serialize_direction`,
  ]),
});

export const BRIDGE_TYPE_MODULE_SUMMARIES = Object.freeze({
  range_isolation: Object.freeze({
    code: `def range_isolation(source_rows, from_time, to_time, timeframe):
    require(timeframe >= 1)
    range_end_exclusive = to_time + timeframe
    rows = isolate_raw_range(source_rows, from_time, range_end_exclusive)
    require(rows)
    second_buckets, timeframe_buckets = build_candle_buckets(rows, timeframe)
    seconds = build_candle_objects(second_buckets)
    candles = seconds if timeframe == 1 else build_candle_objects(timeframe_buckets)
    return candles, seconds, 0, len(candles) - 1`,
    sources: Object.freeze([`${source}:isolate_raw_range`, `${source}:build_candle_buckets`, `${source}:build_candle_objects`, `${source}:main`]),
  }),
  module_orchestration: Object.freeze({
    code: `def module_orchestration(candles, seconds, switches):
    directions = ("bullish", "opposite Order direction") if switches.S else ("bullish",)
    reaction = {d: UnifiedReactionDetector(..., d).detect() for d in directions}
    if not (switches.blue or switches.A or switches.S):
        return reaction

    blue = detect_blue_lines("bullish", reaction["bullish"], ..., reaction["bullish"].resets)
    if not (switches.A or switches.S):
        return reaction, blue
    a_zones = detect_a_zones("bullish", reaction["bullish"], blue, ...)
    if not switches.S:
        return reaction, blue, a_zones

    s_detector = SDetector(
        "bullish", reaction["bullish"], reaction["opposite Order direction"], blue, a_zones,
        initial_order_geometry=directional_a_stop_order_finder(...),
    )
    s_candidates = s_detector.detect()
    if not switches.E:
        return reaction, blue, a_zones, s_candidates

    preliminary_e = EDetector(
        "bullish", ..., s_candidates,
        initial_order_audit=s_detector.order_audit,
    ).detect()
    accepted_s = reconcile_s_with_preliminary_e(s_candidates, preliminary_e)
    return reaction, blue, a_zones, s_candidates, accepted_s, preliminary_e`,
    sources: Object.freeze([`${source}:main`, `${source}:reconcile_stopall_lifecycle`]),
  }),
  ownership_reconciliation: Object.freeze({
    code: `def ownership_reconciliation(a_zones, s_zones, e_zones, stopalls):
    # Latest main candle containing a strict stop owns the transition. Only
    # same-candle stops use StopAll > E red > S red > E blue > S blue > A,
    # followed by sequence number and deterministic source keys.
    accepted_a, invalid_a = split_a_zones_by_dominant_stops(...)
    invalid_s = s_owned_by(invalid_a)
    accepted_a_sources = _a_zones_for_module_engines(a_zones, s_zones, e_zones, "bullish")
    accepted_audit = filter_stopped_a_causes_by(accepted_a_sources)
    # A live invalid bullish head with pending S blocks opposite Order Firsts
    # until its exact strict stop; without pending S there is no block.
    blocked_firsts = blocked_orders_while_invalid_leg_heads_are_live(invalid_a)
    e_zones = rerun_final_e_with(
        accepted_s=s_zones,
        accepted_audit=accepted_audit,
        blocked_order_first_times=blocked_firsts,
    )
    e_zones, stopalls = reconcile_stopall_lifecycle(...)
    final_e = remove_sources_owned_by_stopall(e_zones, stopalls)
    final_s = visible_s_after_module_resets(s_zones, final_e + stopalls)
    final_s += referenced_historical_s(final_e)
    final_a = visible_a_after_module_boundaries(a_zones, final_s, final_e + stopalls)
    final_a += referenced_historical_a(final_s)
    final_a, final_s = remove_sources_owned_by(final_e, stopalls)
    final_a -= invalid_a
    final_s = final_s - invalid_s
    return final_a, final_s, final_e, stopalls`,
    sources: Object.freeze([`${source}:split_a_zones_by_dominant_stops`, `${source}:reconcile_stopall_lifecycle`, `${source}:main`]),
  }),
  serialization: Object.freeze({
    code: `def serialization(result, blue, a_zones, s_zones, e_zones, stopalls):
    direction_payload = {
        "reactions": serialize(result)[0],
        "resets": serialize(result)[1],
        "blueLines": serialize_blue_lines(blue),
        "aZones": serialize_a_zones(a_zones),
        "sZones": serialize_s_zones(s_zones),
        "eZones": serialize_e_zones(e_zones),
        "stopAlls": serialize_stopalls(stopalls),
        "orderAudit": serialize_order_audit(...),
    }
    return payload_envelope(direction_payload, timings)`,
    sources: Object.freeze([`${source}:serialize_direction`, `${source}:serialize_order_audit`, `${source}:main`]),
  }),
});

export const BRIDGE_CALCULATION_GUIDE = Object.freeze({
  title: "Bridge orchestration & output",
  fa: "ترتیب اجرای Bridge و ساخت خروجی",
  phases: Object.freeze([
    Object.freeze({ en: "Validate arguments and isolate raw rows before aggregation.", fa: "ورودی‌ها را چک کن و raw rowها را قبل از aggregation جدا کن.", code: "rows = isolate_raw_range(source_rows, from_time, to_time + timeframe)" }),
    Object.freeze({ en: "Build lower and main candle objects once from the isolated rows.", fa: "آبجکت‌های lower و main را یک‌بار از همان rowهای جداشده بساز.", code: "seconds, candles = build_candle_views(rows, timeframe)" }),
    Object.freeze({ en: "Run the bullish module chain in dependency order.", fa: "زنجیره ماژول‌های صعودی را به ترتیب وابستگی اجرا کن.", code: "Reaction -> BlueLine -> A -> S -> E -> StopAll" }),
    Object.freeze({ en: "Reconcile invalid ownership and repeat affected lifecycle passes until stable. Bullish ownership starts with the latest stop-containing main candle, then uses StopAll > E red > S red > E blue > S blue > A only for same-candle ties; compare the reset map and raise on a repeated map.", fa: "ownership نامعتبر را حل کن و پاس‌های وابسته را تا ثابت‌شدن نتیجه تکرار کن. در مسیر صعودی ابتدا جدیدترین main candle دارای stop انتخاب می‌شود و فقط tie همان کندل از StopAll > E red > S red > E blue > S blue > A استفاده می‌کند.", code: "owner = latest_stop_main_candle; reset_map = {source_time: number}; repeated_map => ValueError" }),
    Object.freeze({ en: "Keep a bullish invalid leg head with a real pending S as an internal owner through its exact strict stop; block opposite Order Firsts during that interval and resume after the stop. No pending S means no unrelated-order block.", fa: "leg head صعودی نامعتبرِ دارای S واقعی معلق را تا stop strict دقیق به‌عنوان مالک داخلی نگه دار؛ Firstهای Order مخالف را در این فاصله ببند و بعد از stop ادامه بده. بدون S معلق، Order نامرتبط مسدود نمی‌شود.", code: "blocked_order_first_times = blocked_orders_while_invalid_leg_heads_are_live(...)" }),
    Object.freeze({ en: "Close visible lineage and remove shadowed sources.", fa: "زنجیره قابل‌نمایش را کامل کن و sourceهای پوشانده‌شده را حذف کن.", code: "display_e, display_s, display_a = finalize_visibility()" }),
    Object.freeze({ en: "Serialize the eight collections, payload envelope, and timings.", fa: "هشت collection، envelope و timings را serialize کن.", code: "payload['directions']['bullish'] = serialize_direction()" }),
  ]),
  checks: Object.freeze(["timeframe >= 1", "selected range is not empty", "strict crossing keeps equality valid", "latest stop-containing main candle owns bullish transition", "same-candle priority and sequence tie-break", "pending invalid-head Order block", "accepted ownership only", "source index inside isolated range", "eight direction collections"]),
  output: Object.freeze(["17 payload envelope fields", "8 directions.bullish collections", "183 collection fields", "2 timing fields", "7 Order cause fields"]),
});

const catalogField = (id, type, en, fa, tags) => Object.freeze({
  id,
  type,
  names: Object.freeze({ en, fa }),
  tags: Object.freeze(["bridge", ...tags]),
});

const catalogObject = (id, collection, en, fa, descriptionEn, descriptionFa, fields) => Object.freeze({
  id,
  collection,
  names: Object.freeze({ en, fa }),
  description: Object.freeze({ en: descriptionEn, fa: descriptionFa }),
  tags: Object.freeze(["bridge", id, collection]),
  fields: Object.freeze(fields),
});

export const BRIDGE_ENVELOPE_CATALOG = Object.freeze([
  catalogObject("payload", "payload", "Payload envelope", "پوسته اصلی payload", "Top-level engine versions, switches, range, direction map, and timing data.", "فیلدهای سطح اول برای versionها، سوییچ‌ها، بازه، directionها و زمان اجرا.", [
    catalogField("engine", "string", "Reaction engine identifier", "شناسه موتور Reaction", ["version"]),
    catalogField("version", "string", "Reaction engine version", "version موتور Reaction", ["version", "reaction"]),
    catalogField("blueLineVersion", "string", "Blue Line contract version", "version قرارداد Blue Line", ["version", "blue-line"]),
    catalogField("aVersion", "string", "A engine version", "version موتور A", ["version", "a"]),
    catalogField("sVersion", "string", "S engine version", "version موتور S", ["version", "s"]),
    catalogField("eVersion", "string?", "E engine version", "version موتور E", ["version", "e"]),
    catalogField("stopAllVersion", "string?", "StopAll engine version", "version موتور StopAll", ["version", "stop-all"]),
    catalogField("blueLinesEnabled", "boolean", "Blue Line output switch", "روشن‌بودن خروجی Blue Line", ["setting", "blue-line"]),
    catalogField("aEnabled", "boolean", "A output switch", "روشن‌بودن خروجی A", ["setting", "a"]),
    catalogField("sEnabled", "boolean", "S output switch", "روشن‌بودن خروجی S", ["setting", "s"]),
    catalogField("eEnabled", "boolean", "E calculation/output switch", "روشن‌بودن محاسبه و خروجی E", ["setting", "e"]),
    catalogField("stopAllEnabled", "boolean", "StopAll calculation/output switch", "روشن‌بودن محاسبه و خروجی StopAll", ["setting", "stop-all"]),
    catalogField("timeframe", "integer", "Main timeframe in seconds", "timeframe اصلی برحسب ثانیه", ["time"]),
    catalogField("actualFrom", "epoch", "First isolated main-candle time", "زمان اولین کندل main در بازه جداشده", ["time", "range"]),
    catalogField("actualTo", "epoch", "Last isolated main-candle time", "زمان آخرین کندل main در بازه جداشده", ["time", "range"]),
    catalogField("directions", "object", "Map of requested direction payloads", "map خروجی direction درخواستی", ["output"]),
    catalogField("timings", "object", "Measured phase and total durations", "زمان اندازه‌گیری‌شده فازها و کل Bridge", ["performance"]),
  ]),
  catalogObject("direction_payload", "directions.bullish", "Bullish direction payload", "payload جهت صعودی", "The exact eight public collections under the bullish result.", "همان هشت collection عمومی که زیر خروجی صعودی قرار می‌گیرند.", [
    catalogField("reactions", "array", "Confirmed Reaction rows", "ردیف‌های Reaction تأییدشده", ["reaction"]),
    catalogField("resets", "array", "Accepted Reaction Reset rows", "ردیف‌های Reset پذیرفته‌شده", ["reset"]),
    catalogField("blueLines", "array", "Public calculation-valid Blue Line rows", "ردیف‌های عمومی و معتبر Blue Line", ["blue-line"]),
    catalogField("aZones", "array", "Visible accepted A rows", "ردیف‌های A پذیرفته‌شده و قابل‌نمایش", ["a"]),
    catalogField("sZones", "array", "Visible accepted S rows", "ردیف‌های S پذیرفته‌شده و قابل‌نمایش", ["s"]),
    catalogField("eZones", "array", "Visible accepted E rows", "ردیف‌های E پذیرفته‌شده و قابل‌نمایش", ["e"]),
    catalogField("stopAlls", "array", "Accepted StopAll rows", "ردیف‌های StopAll پذیرفته‌شده", ["stop-all"]),
    catalogField("orderAudit", "array", "Deduplicated physical Order audit rows", "ردیف‌های deduplicate‌شده Order Audit", ["order-audit"]),
  ]),
  catalogObject("timings", "timings", "Timing payload", "زمان اجرای Bridge", "Measured phase durations and whole-bridge runtime in milliseconds.", "زمان هر فاز و زمان کل Bridge برحسب میلی‌ثانیه.", [
    catalogField("phasesMs", "object<string, number>", "Milliseconds grouped by measured phase", "میلی‌ثانیه هر فاز اندازه‌گیری‌شده", ["performance"]),
    catalogField("bridgeTotalMs", "number", "Total bridge runtime in milliseconds", "زمان کل اجرای Bridge به میلی‌ثانیه", ["performance"]),
  ]),
  catalogObject("order_cause", "orderAudit[].causes[]", "Order cause", "علت ساخت Order", "Union shape used inside each Order Audit causes list.", "شکل union که داخل لیست causes هر Order Audit می‌آید.", [
    catalogField("kind", "enum", "Cause kind: parent-stop or reset-leg", "نوع cause: parent-stop یا reset-leg", ["cause"]),
    catalogField("parentType", "enum?", "Parent type for parent-stop", "نوع parent برای parent-stop", ["cause", "parent"]),
    catalogField("parentFamily", "enum?", "Parent family when available", "family والد، اگر وجود داشته باشد", ["cause", "parent"]),
    catalogField("eventTime", "epoch?", "Exact parent-stop event time", "زمان دقیق رویداد parent-stop", ["cause", "time"]),
    catalogField("parentSourceTime", "epoch?", "Parent source time", "زمان source والد", ["cause", "parent", "time"]),
    catalogField("resetTime", "epoch?", "Reset time for reset-leg", "زمان Reset برای reset-leg", ["cause", "reset", "time"]),
    catalogField("boundaryBreakTime", "epoch?", "Reset-leg boundary break time", "زمان شکست boundary در reset-leg", ["cause", "break", "time"]),
  ]),
]);

export const BRIDGE_COPY = Object.freeze({
  summaryFa: "ورودی را به بازه مستقل تبدیل می‌کند، ماژول‌های صعودی را به ترتیب اجرا می‌کند، ownership را با جدیدترین main candle دارای stop و tieهای همان کندل حل می‌کند و خروجی نهایی را serialize می‌کند.",
  stopFa: "Bridge خودش رفتار معاملاتی تازه‌ای نمی‌سازد؛ نتیجه‌های نامعتبر یا بیرون بازه را قبل از serialize حذف می‌کند و فقط ownership نهایی را منتشر می‌کند.",
});
