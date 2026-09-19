const typeSummary = (code, sources) => Object.freeze({
  code,
  sources: Object.freeze(sources),
});

// These are read-only, code-derived walkthroughs. They deliberately name the
// maintained Python operations and guards without becoming a second runtime.
export const TYPE_MODULE_SUMMARIES = Object.freeze({
  reaction: Object.freeze({
    mode_a: typeSummary(`def detect_mode_a(candles, lower):
    leg_floor = candles[range_start].low
    anchor_red = range_open_red_if_present()
    anchor_red_origin = "leg_open" if anchor_red is not None else None

    for first_red in candles_after_range_start:
        if not (previous_candle.tag == "GREEN" and first_red.tag == "RED"):
            if first_red.tag == "RED":
                anchor_red = first_red
            continue

        # A rejected candidate becomes an invalidation anchor until a later
        # GREEN/RED pair proves that anchor is no longer the active floor.
        if candidate_was_invalidated_by_owner_floor(first_red):
            anchor_red = first_red
            anchor_red_origin = "candidate_invalidation"
        if anchor_red_origin == "candidate_invalidation" and previous_candle.low < anchor_red.low and first_red.low < anchor_red.low:
            anchor_red = None
            anchor_red_origin = None
        # With an anchor, FirstRed may not be lower than Anchor.Low.
        # Without one, FirstRed.Low must keep either the previous GREEN Low or
        # the original leg floor. Equality remains eligible.
        eligible = (
            first_red.low >= anchor_red.low
            if anchor_red is not None
            else first_red.low >= previous_candle.low or first_red.low >= leg_floor
        )
        if not eligible:
            anchor_red = first_red
            continue

        green_high, green_source = highest_in_contiguous_green_run_before(first_red)
        candidate = Candidate(
            first=first_red,
            box_top=max_with_earliest_source(green_high, first_red.high),
            box_bottom=first_red.low,
            owner_floor=anchor_red.low if anchor_red else leg_floor,
            mode="A",
        )
        for candle in candles_after(first_red):
            invalidation = candle.low < candidate.owner_floor
            confirmation = candle.high > candidate.box_top
            if invalidation and confirmation:
                invalidation = lower_second_low_happens_before_high(candle)
            if invalidation:
                break
            candidate.box_bottom = min(candidate.box_bottom, candle.low)
            if confirmation:
                refine_bottom_using_seconds_before_exact_break(candidate, candle)
                return _append_reaction("bullish", candidate)
    return None`, [
      "engine/pipeline/reaction_engine.py:_first_initial",
      "engine/pipeline/reaction_engine.py:BullishDetector.detect",
      "engine/pipeline/reaction_engine.py:green_run_peak_before",
      "engine/pipeline/reaction_engine.py:breakout_analysis",
    ]),
    mode_b: typeSummary(`def detect_mode_b(candles, lower, previous_reaction):
    running_peak, running_source = previous_reaction.break_candle.high, previous_reaction.break_index
    candidate = None

    for candle in later_candles:
        # A strict Low below the previous Reaction.BoxBottom is a Reset.  If
        # this candle also breaks a waiting candidate, lower seconds decide.
        if previous_owner_resets_before_candidate_break(candle, lower):
            return "RESET"

        if candidate is None and candle.tag == "RED":
            top_source = running_source if running_peak >= candle.high else candle.index
            bottom_start = top_source + 1 if top_source < candle.index else candle.index
            candidate = Candidate(
                first=candle,
                box_top=max(running_peak, candle.high),
                box_bottom=minimum_low(bottom_start, candle.index),
                mode="B",
            )

        if candidate is not None:
            candidate.box_bottom = min(candidate.box_bottom, candle.low)
            if candle.high > candidate.box_top:
                refine_bottom_using_seconds_before_exact_break(candidate, candle)
                reaction = _append_reaction("bullish", candidate)
                same_candle_reset = first_later_second_low_below(reaction.box_bottom)
                next_candidate = None if same_candle_reset else candidate_from_whole_red_break_candle(candle)
                return reaction, same_candle_reset, next_candidate

        if candle.high > running_peak:
            running_peak, running_source = candle.high, candle.index
    return None`, [
      "engine/pipeline/reaction_engine.py:UnifiedReactionDetector.detect",
      "engine/pipeline/reaction_engine.py:_candidate_from_confirmation_remainder",
      "engine/pipeline/reaction_engine.py:breakout_analysis",
    ]),
    direct_after_reset: typeSummary(`def recover_after_reset(reset, candles, lower):
    blocked_through = reset.index
    for first_red in candles[reset.index + 1:]:
        if first_red.index <= blocked_through:
            continue
        if not (previous_candle.tag == "GREEN" and first_red.tag == "RED"):
            continue

        local_floor = minimum_low(local_red_and_green_context_before(first_red))
        if first_red.low < local_floor:
            continue
        owner_floor = minimum_low(reset.index, first_red.index - 1)
        candidate = Candidate(
            first=first_red,
            box_top=max_high(contiguous_green_run_before(first_red), first_red.high),
            box_bottom=first_red.low,
            owner_floor=owner_floor,
            mode="A",
        )
        confirmed, invalidated_at = _scan_direct_candidate(candidate, lower)
        if confirmed is not None:
            return _append_reaction("bullish", confirmed)
        if invalidated_at is not None:
            blocked_through = invalidated_at
    return None`, [
      "engine/pipeline/reaction_engine.py:_first_direct_same_direction_after_reset",
      "engine/pipeline/reaction_engine.py:_scan_direct_candidate",
      "engine/pipeline/reaction_engine.py:_candidate_from_confirmation_remainder",
    ]),
  }),

  reset: Object.freeze({
    same_candle: typeSummary(`def same_candle_reset(reaction, break_candle, lower):
    confirmation = breakout_analysis(reaction, break_candle)
    if confirmation is None:
        return None
    reset_second = post_breakout_reset(
        confirmation,
        confirmed_bottom=reaction.box_bottom,
        same_main_candle=break_candle,
    )
    return _append_reset(
        owner=reaction.first_idx,
        index=break_candle.index,
        second_time=reset_second.display_time,
        broken_level=reaction.box_bottom,
    ) if reset_second is not None else None`, [
      "engine/pipeline/reaction_engine.py:post_breakout_reset",
      "engine/pipeline/reaction_engine.py:_append_reset",
      "engine/pipeline/reaction_engine.py:breakout_analysis",
    ]),
    later_reset: typeSummary(`def later_reset(reaction, waiting_mode_b_candidate, candles, lower):
    for candle in candles_after(reaction.break_index):
        if candle.low >= reaction.box_bottom:
            continue
        if waiting_mode_b_candidate is not None and candle.high > waiting_mode_b_candidate.box_top:
            reset_wins = confirmed_reset_before_breakout(
                waiting_mode_b_candidate, candle, reaction.box_bottom,
            )
            if not reset_wins:
                return "MODE_B_CONFIRMS_FIRST"
        return _append_reset(
            owner=reaction.first_idx,
            index=candle.index,
            second_time=None,          # exact seconds decide the race only
            broken_level=reaction.box_bottom,
        )
    return None`, [
      "engine/pipeline/reaction_engine.py:confirmed_reset_before_breakout",
      "engine/pipeline/reaction_engine.py:_append_reset",
      "engine/pipeline/reaction_engine.py:UnifiedReactionDetector.detect",
    ]),
  }),

  blue_line: Object.freeze({
    scale: typeSummary(`def scale_blue(reaction, previous_count, state):
    if reaction.mode == "A":
        reference = reaction.anchor_value or reaction.leg_boundary_value
        previous_count = None
    else:
        reference = previous_reaction_floor(reaction)
    fibonacci = fibonacci_level("bullish", reaction, reference)  # uses FIBONACCI_RATIO=Decimal("0.618")
     # count_scale_strikes keeps one pending strict extreme, replaces it only
     # with a more directional value, and confirms it on any same or later
     # GREEN main candle (doji is GREEN). If it survives to Break, lower-second
     # fallback confirms only a penetration before or at the exact Break.
     strikes = count_scale_strikes(reaction, fibonacci, main, one_second)
    if previous_count is None or len(strikes) <= previous_count:
        return None
    if state.has_blue_line and state.healthy_reactions_since_blue < 1:
        return None
    decisive = strikes[-1]
    source = main[decisive.source_index]
    line_price = source.low + (source.high - source.low) / Decimal(3)
    return BlueLine(kind="scale", strike_count=len(strikes), line_price=line_price)
    # The public Blue row has no stop fields; ADetector computes a private
    # BlueState stop later when it evaluates A.`, [
      "engine/pipeline/blue_line_detector.py:fibonacci_level",
      "engine/pipeline/blue_line_detector.py:count_scale_strikes",
      "engine/pipeline/blue_line_detector.py:_intrabar_pending_confirmation",
      "engine/pipeline/blue_line_detector.py:detect_blue_lines",
    ]),
    reset: typeSummary(`def reset_blue(reset, reaction_number, state, candles):
    if state.has_blue_line and state.healthy_reactions_since_blue < 1:
        return None
    source = candles[reset.index]
    line_price = source.low + (source.high - source.low) / Decimal(5)
    valid = not _stops_on_index(
        "bullish", state.last_line, candles,
        state.last_line.source_index + 1, reset.index,
    ) or source.low >= state.last_line.source_extreme
    return BlueLine(
        kind="reset", reaction_number=reaction_number,
        broken_level=reset.broken_level, calculation_valid=valid,
        line_price=line_price,
    )
    # detect_blue_lines keeps invalid internal rows; serialize_blue_lines
    # publishes only calculation_valid=True.`, [
      "engine/pipeline/blue_line_detector.py:detect_blue_lines",
      "engine/pipeline/blue_line_detector.py:_stops_on_index",
    ]),
    internal_invalid_reset: typeSummary(`def internal_invalid_reset(reset, prior_line):
    line = build_reset_blue(reset, line_price_rule="one fifth")
    same_index_stop = _stops_on_index(
        "bullish", prior_line, candles,
        prior_line.source_index + 1, reset.index,
    )
    line.calculation_valid = not (
        same_index_stop and line.source_extreme < prior_line.source_extreme
    )
    if not line.calculation_valid:
        retain_for = "A._double_stop_a_candidates"
        return line, retain_for
    return line, "public blueLines"`, [
      "engine/pipeline/blue_line_detector.py:detect_blue_lines",
      "engine/pipeline/a_zone_detector.py:_double_stop_a_candidates",
    ]),
  }),

  a: Object.freeze({
    inherited_reaction_stop: typeSummary(`def a_from_inherited_reaction_stop(previous, current, expires_at, reactions):
    inherited = _inherited_stop(previous, current)
    if inherited is None:
        return None
    level, source_index, source_time, _ = inherited
    trigger = first_crossing(level, current.formation_time, expires_at)
    if trigger is None:
        return None
    effective_not_before = max(previous.effective_stop_time, current.effective_stop_time)
    reaction = _first_reaction_after(trigger.event_time,
        not_before=effective_not_before)
    if reaction is None:
        return None
    return _make_a(previous, current, level, source_index, trigger, reaction)`, [
      "engine/pipeline/a_zone_detector.py:_inherited_stop",
      "engine/pipeline/a_zone_detector.py:_pair_trigger",
      "engine/pipeline/a_zone_detector.py:_first_reaction_after",
    ]),
    previous_blue_stopped: typeSummary(`def a_after_previous_blue_stop(previous, current, expires_at):
    if previous.stop_event_time is None or previous.stop_time is None:
        return None
    level, source_index, source_time = _range_extreme(
        previous.stop_event_time,
        current.source_time - microsecond,
    )
    formation_end = min(current.main_candle_end, expires_at) if expires_at else current.main_candle_end
    trigger = first_crossing(level, current.formation_time, formation_end)
    if trigger is None:
        if current.stop_event_time is None or event_after(current.stop_event_time, expires_at):
            return None
        trigger = first_crossing(level, current.stop_event_time, expires_at)
    if trigger is None:
        return None
    return _pair_and_confirm(previous, current, level, source_index, trigger)`, [
      "engine/pipeline/a_zone_detector.py:_pair_trigger",
      "engine/pipeline/a_zone_detector.py:_range_extreme",
      "engine/pipeline/a_zone_detector.py:_first_crossing",
    ]),
    coexisting_blue_stops: typeSummary(`def a_from_coexisting_stops(previous, current, expires_at):
    if previous.stop_event_time is None or current.stop_event_time is None:
        return None
     # Bullish ordering is (stop_event_time, -stop_level): at an exact event
     # the higher stop level is first. The equal-time trigger comes from the
     # second stop, while continuation level/source come from the first.
     first, second = sorted(
         (previous, current),
         key=lambda item: (item.stop_event_time, -item.stop_level),
     )
    level = first.stop_event_extreme
    trigger = second.stop_event_time if first.stop_event_time == second.stop_event_time else first_crossing(
        level, second.stop_event_time, expires_at
    )
    if trigger is None:
        return None
    return _pair_and_confirm(previous, current, level,
        first.stop_index, trigger)`, [
      "engine/pipeline/a_zone_detector.py:_pair_trigger",
      "engine/pipeline/a_zone_detector.py:_first_crossing",
      "engine/pipeline/a_zone_detector.py:_range_extreme",
      "engine/pipeline/a_zone_detector.py:_a_source",
    ]),
    special_double_stop: typeSummary(`def special_double_stop(previous_valid, invalid_reset):
    crossing = first_crossing(
        previous_valid.source_extreme,
        invalid_reset.source_time,
        invalid_reset.source_time + timeframe,
    )
    if crossing is None or crossing.main_index != invalid_reset.source_index:
        return None
    reaction = _first_reaction_after(crossing.event_time,
        not_before=invalid_reset.source_time)
    if reaction is None:
        return None
    source = _a_source(crossing.main_index, reaction)
    return _make_special_a(previous_valid, invalid_reset, crossing, reaction, source)
    # detect() removes duplicate ordinary A and already-owned lifecycles.`, [
      "engine/pipeline/a_zone_detector.py:_double_stop_a_candidates",
      "engine/pipeline/a_zone_detector.py:_a_source",
      "engine/pipeline/a_zone_detector.py:detect",
    ]),
  }),

  s_red: Object.freeze({
    simple_red: typeSummary(`def simple_red(a_zone):
     a_stop = _first_a_stop(a_zone.price, a_zone.confirmation_event)
     # S ownership opens immediately after A-stop. A pending S keeps the end
     # open; a bullish invalid head blocks opposite Order Firsts until its
     # exact stop, while a head without pending S blocks nothing unrelated.
    if a_stop is None or next_a_confirms_at_or_before(a_stop):
        return None
    order = _first_order_after(a_stop.event_time)
    if order is None:
        return None
    order_stop = _order_stop(order)  # Mode A leg extreme or prior Mode B box

    pre = _candidate_before_order(a_stop, order) if _candidate_timing(...) == "before" else None
    if pre is not None:
        result = _decision(pre, order_stop, fallback_on_unqualified_cross=True)
        if result is not None and result.color == "red":
            return emit_s("red", "simple", source=pre, decision=result)
        if result is None or result.color != "fallback":
            return None

    if _nested_trend_reaction(order) is not None:
        return None  # advanced owns this branch
    aligned = _first_trend_reaction_after_order(order.confirmation)
    if aligned is None:
        return None
    blue_candidate = _simple_candidate(order.break, aligned.break)  # last extreme tie
    red_source = pre or _candidate_after_order(order.confirmation, aligned)
    result = _decision(blue_candidate, order_stop, candidate_start=aligned.confirmation)
    if result is None or result.color != "red":
        return None
    return emit_s("red", "simple", source=red_source, decision=result)`, [
      "engine/pipeline/s_zone_detector.py:_simple_candidate",
      "engine/pipeline/s_zone_detector.py:_candidate_after_order",
      "engine/pipeline/s_zone_detector.py:_decision",
    ]),
    advanced_red: typeSummary(`def advanced_red(a_zone, order):
    nested = _nested_trend_reaction(order, order.confirmation_time)
    if nested is None:
        return None
    candidate = opposite_order_box_boundary_source(order)
    decision = _decision(
        candidate.price, _order_stop(order), order.confirmation_time,
        nested.number, a_zone.a_stop_event_time,
        candidate_start=nested.confirmation_time,
    )
    if decision is None or decision.color != "red":
        return None
    return emit_s(color="red", formation_type="advanced",
        nested_reaction=nested.number, order=order, decision=decision)`, [
      "engine/pipeline/s_zone_detector.py:_nested_trend_reaction",
      "engine/pipeline/s_zone_detector.py:_decision",
      "engine/pipeline/s_zone_detector.py:detect",
    ]),
  }),

  s_blue: Object.freeze({
    simple_blue: typeSummary(`def simple_blue(a_zone, order):
     a_stop = _first_a_stop(a_zone.price, a_zone.confirmation_event)
     # Keep the a_ownership_window open while this S is pending. The bridge
     # separately blocks opposite Order Firsts owned by a live invalid head.
    if a_stop is None or order is None or next_a_confirms_at_or_before(a_stop):
        return None
    order_stop = _order_stop(order)

    pre = _candidate_before_order(a_stop, order) if _candidate_timing(...) == "before" else None
    if pre is not None:
        decision = _decision(pre, order_stop, fallback_on_unqualified_cross=True)
        if decision is not None and decision.color == "blue":
            return emit_s("blue", "simple", source=pre, decision=decision)
        if decision is None or decision.color != "fallback":
            return None

    if _nested_trend_reaction(order) is not None:
        return None  # advanced owns this branch
    aligned = _first_trend_reaction_after_order(order.confirmation)
    if aligned is None:
        return None
    candidate = _simple_candidate(order.break, aligned.break)  # last extreme tie
    decision = _decision(candidate.price, order_stop,
        order.confirmation_time, trend_reaction_number=aligned.number,
        behavior_start=a_stop.event_time, candidate_start=aligned.confirmation_time)
    if decision is None or decision.color != "blue":
        return None
    return emit_s(color="blue", formation_type="simple", order=order, decision=decision)`, [
      "engine/pipeline/s_zone_detector.py:_simple_candidate",
      "engine/pipeline/s_zone_detector.py:_decision",
      "engine/pipeline/s_zone_detector.py:_candidate_cross_has_blue",
    ]),
    advanced_blue: typeSummary(`def advanced_blue(a_zone, order):
    nested = _nested_trend_reaction(order, order.confirmation_time)
    if nested is None:
        return None
    candidate = opposite_order_box_boundary_source(order)
    decision = _decision(
        candidate.price, _order_stop(order), order.confirmation_time,
        trend_reaction_number=nested.number,
        behavior_start=a_zone.a_stop_event_time,
        candidate_start=nested.confirmation_time,
    )
    if decision is None or decision.color != "blue":
        return None
    return emit_s(color="blue", formation_type="advanced",
        nested_reaction=nested.number, order=order, decision=decision)`, [
      "engine/pipeline/s_zone_detector.py:_nested_trend_reaction",
      "engine/pipeline/s_zone_detector.py:_decision",
      "engine/pipeline/s_zone_detector.py:detect",
    ]),
    type3: typeSummary(`def build_type3(a_zone, deadline):
    candidates = []
    for reset in opposite_resets:
        owner = eligible_owner_confirmed_at_or_before_a_stop(reset, a_zone)
        if owner is None or reset.time <= a_zone.a_stop_event_time or reset.time >= deadline:
            continue
        source_index, source_time, boundary = _type3_reset_leg(reset)
        crossing = first_strict_cross(
            reset.time, boundary, start_inclusive=True, before=deadline,
        )
        if crossing is None or not _type3_has_trend_reaction(a_zone.a_stop_event_time, crossing):
            continue
        candidates.append((crossing.decision_event_time, reset, owner, source_index, source_time, crossing))
    if not candidates:
        return None
    _, reset, owner, source_index, source_time, crossing = min(candidates, key=lambda item: item[0])
    return emit_s(color="blue", formation_type="type3",
        order=None, reset_reaction=owner.number, decision=crossing)`, [
      "engine/pipeline/s_zone_detector.py:_first_type3",
      "engine/pipeline/s_zone_detector.py:_type3_reset_leg",
      "engine/pipeline/s_zone_detector.py:_type3_has_trend_reaction",
    ]),
  }),

  e_blue: Object.freeze({
    direct_order_a_blue: typeSummary(`def blue_e_from_direct_order(parent_type, parent):
    parent_stop = _parent_stop(parent_type, parent)
    if parent_stop is None:
        return None

    published = first_published_opposite_reaction_at_or_after(parent_stop.event_time)
    canonical = published if strict_stop(published) is not None else bounded_geometry_fallback(
        _first_healthy_direct_geometry(parent_stop.event_time),
    )
    pool = order_candidates(parent_stop.event_time, continuous_deadline_for_s(parent))
    direct = first_stopped_order(pool, preferred=canonical)  # older First wins equal direct stop events
    winner = min(
        stopped(direct, unconsumed_blue_s_order(parent), carried_order(parent)),
        key=(order_stop_event, -first_index),
    )
    if direct is None or winner is None:
        return None
    return _zone("blue", parent_type, parent, parent_stop.event_time)`, [
      "engine/pipeline/e_zone_detector.py:_first_healthy_direct_geometry",
      "engine/pipeline/e_zone_detector.py:order_candidates",
      "engine/pipeline/e_zone_detector.py:_zone",
    ]),
    reset_leg_order_b_blue: typeSummary(`def blue_e_from_reset_leg_order_b(parent_type, parent):
    parent_stop = _parent_stop(parent_type, parent)
    if parent_stop is None:
        return None
    for reset in opposite_resets_after(parent_stop.event_time):
        leg_start, boundary = _reset_leg_geometry(reset, reset.time)
        crossing = _strict_trigger_cross(reset.time, boundary)
        if crossing is None or not _reset_leg_has_simple_trend_reaction(leg_start, crossing):
            continue
        order_b = _first_order_b_geometry(reset.time, crossing, next_owner_reset)
        pool = order_candidates(parent_stop.event_time)
        winner = first_stopped_order(pool)  # older First wins inside direct pool
        if order_b is not None and identity(winner) == identity(order_b):
            return _zone("blue", parent_type, parent, parent_stop.event_time)
    return None`, [
      "engine/pipeline/e_zone_detector.py:_reset_leg_geometry",
      "engine/pipeline/e_zone_detector.py:_strict_trigger_cross",
      "engine/pipeline/e_zone_detector.py:_first_order_b_geometry",
      "engine/pipeline/e_zone_detector.py:_zone",
    ]),
    carried_live_blue: typeSummary(`def blue_e_from_carried_live_order(parent_type, parent):
    parent_stop = _parent_stop(parent_type, parent)
    if parent_stop is None:
        return None
    carried = _carried_order_for_parent(parent, parent_stop.event_time)
    inherited = _unconsumed_s_order(parent, parent_stop.event_time) if parent_type == "S" else None
    pool = [direct_order_after(parent_stop), inherited, carried]
    winner = min(stopped(pool), key=(order_stop_event, negative_first_index))
    if winner not in (carried, inherited):
        return None
    return _zone("blue", parent_type, parent, parent_stop.event_time)`, [
      "engine/pipeline/e_zone_detector.py:_carried_order_for_parent",
      "engine/pipeline/e_zone_detector.py:_unconsumed_s_order",
      "engine/pipeline/e_zone_detector.py:_zone",
    ]),
    recursive_blue: typeSummary(`def recursive_blue(s_parent):
    parent_type, parent, number = "S", s_parent, 1
    while (parent_stop := _parent_stop(parent_type, parent)) is not None:
        child = _zone("blue", number, parent_type, parent, parent_stop.event_time)
        if child is None or repeats_source_in_chain(child):
            break
        provisional.append(child)
        parent_type, parent, number = "E", child, number + 1

     # Latest main candle containing a strict stop owns the transition. Only
     # same-candle stops use StopAll > E red > S red > E blue > S blue > A,
     # then sequence number and deterministic source keys.
     accepted = chronological_active_state_reconciliation(provisional)
    accepted = apply_family_dominance_and_sequence_resets(accepted)
    keep_stopped_history_and_required_lineage(accepted)
    rebuild_order_audit_from_accepted_parents()
    return accepted`, [
      "engine/pipeline/e_zone_detector.py:detect",
      "engine/pipeline/e_zone_detector.py:_zone",
      "engine/pipeline/e_zone_detector.py:_order_cause_evidence",
    ]),
  }),

  e_red: Object.freeze({
    direct_order_a_red: typeSummary(`def red_e_from_direct_order(parent_type, parent):
    parent_stop = _parent_stop(parent_type, parent)
    if parent_stop is None:
        return None
    published = first_published_opposite_reaction_at_or_after(parent_stop.event_time)
    canonical = published if strict_stop(published) is not None else bounded_geometry_fallback(
        _first_healthy_direct_geometry(parent_stop.event_time),
    )
    pool = order_candidates(parent_stop.event_time, continuous_deadline_for_s(parent))
    direct = first_stopped_order(pool, preferred=canonical)  # older First wins equal direct stop events
    winner = min(
        stopped(direct, unconsumed_blue_s_order(parent), carried_order(parent)),
        key=(order_stop_event, -first_index),
    )
    if direct is None or winner is None:
        return None
    return _zone("red", parent_type, parent, parent_stop.event_time)`, [
      "engine/pipeline/e_zone_detector.py:_first_healthy_direct_geometry",
      "engine/pipeline/e_zone_detector.py:order_candidates",
      "engine/pipeline/e_zone_detector.py:_zone",
    ]),
    reset_leg_order_b_red: typeSummary(`def red_e_from_reset_leg_order_b(parent_type, parent):
    parent_stop = _parent_stop(parent_type, parent)
    if parent_stop is None:
        return None
    for reset in opposite_resets_after(parent_stop.event_time):
        leg_start, boundary = _reset_leg_geometry(reset, reset.time)
        crossing = _strict_trigger_cross(reset.time, boundary)
        if crossing is None or not _reset_leg_has_simple_trend_reaction(leg_start, crossing):
            continue
        order_b = _first_order_b_geometry(reset.time, crossing, next_owner_reset)
        pool = order_candidates(parent_stop.event_time)
        winner = first_stopped_order(pool)  # older First wins inside direct pool
        if order_b is not None and identity(winner) == identity(order_b):
            return _zone("red", parent_type, parent, parent_stop.event_time)
    return None`, [
      "engine/pipeline/e_zone_detector.py:_reset_leg_geometry",
      "engine/pipeline/e_zone_detector.py:_strict_trigger_cross",
      "engine/pipeline/e_zone_detector.py:_first_order_b_geometry",
      "engine/pipeline/e_zone_detector.py:order_candidates",
      "engine/pipeline/e_zone_detector.py:_zone",
    ]),
    carried_live_red: typeSummary(`def red_e_from_carried_live_order(parent_type, parent):
    parent_stop = _parent_stop(parent_type, parent)
    if parent_stop is None:
        return None
    carried = _carried_order_for_parent(parent, parent_stop.event_time)
    inherited = _unconsumed_s_order(parent, parent_stop.event_time) if parent_type == "S" else None
    pool = [direct_order_after(parent_stop), inherited, carried]
    winner = min(stopped(pool), key=(order_stop_event, negative_first_index))
    if winner not in (carried, inherited):
        return None
    return _zone("red", parent_type, parent, parent_stop.event_time)`, [
      "engine/pipeline/e_zone_detector.py:_carried_order_for_parent",
      "engine/pipeline/e_zone_detector.py:_unconsumed_s_order",
      "engine/pipeline/e_zone_detector.py:_zone",
    ]),
    recursive_red: typeSummary(`def recursive_red(s_parent):
    parent_type, parent, number = "S", s_parent, 1
    while (parent_stop := _parent_stop(parent_type, parent)) is not None:
        child = _zone("red", number, parent_type, parent, parent_stop.event_time)
        if child is None or repeats_source_in_chain(child):
            break
        provisional.append(child)
        parent_type, parent, number = "E", child, number + 1

     # Latest main candle containing a strict stop owns the transition. Only
     # same-candle stops use StopAll > E red > S red > E blue > S blue > A,
     # then sequence number and deterministic source keys.
     accepted = chronological_active_state_reconciliation(provisional)
    accepted = keep_red_over_blue_and_apply_sequence_resets(accepted)
    keep_stopped_history_and_required_lineage(accepted)
    rebuild_order_audit_from_accepted_parents()
    return accepted`, [
      "engine/pipeline/e_zone_detector.py:detect",
      "engine/pipeline/e_zone_detector.py:_zone",
      "engine/pipeline/e_zone_detector.py:_order_cause_evidence",
    ]),
  }),

  order_audit: Object.freeze({
    parent_stop: typeSummary(`def audit_parent_stop(parent_type, parent):
    gate = a_confirmation(parent) if parent_type == "A" else parent.decision_event_time
    stop = first_strict_parent_cross(from_event=gate, level=parent.price)
    if stop is None:
        return None
    order = first_healthy_opposite_order_after(stop.event_time)
    if order is None:
        return None
    return register_order_audit(
        identity=(order.first_idx, order.break_idx),
        cause=("parent-stop", parent_type, parent.source_time, stop.event_time),
    )`, [
      "engine/pipeline/s_zone_detector.py:_audit_stopped_a",
      "engine/pipeline/e_zone_detector.py:_first_healthy_direct_geometry",
      "engine/pipeline/e_zone_detector.py:_register_order_audit",
    ]),
    reset_leg: typeSummary(`def audit_reset_leg(parent_stop):
    evidence = _reset_leg_evidence_after(parent_stop.event_time)
    if evidence is None:
        return None
    reset_time, crossing = evidence
    order = _first_order_b_geometry(reset_time, crossing, range_end)
    if order is None:
        return None
    return register_order_audit(
        identity=(order.first_idx, order.break_idx),
        cause="reset-leg", reset_time=reset_time, reset_break=crossing,
    )`, [
      "engine/pipeline/e_zone_detector.py:_reset_leg_evidence",
      "engine/pipeline/e_zone_detector.py:_first_order_b_geometry",
      "engine/pipeline/e_zone_detector.py:_register_order_audit",
    ]),
    merged_identity: typeSummary(`def merge_order_audit(entries):
    by_identity = {}
    for entry in entries:
        if not accepted_calculation_provenance(entry.cause):
            continue
        identity = (entry.order.first_idx, entry.order.break_idx)
        record = by_identity.setdefault(identity, copy_physical_order_geometry(entry.order))
        record.causes = deduplicate_causes(record.causes + entry.causes)
    return serialize_order_audit(sort_by_first_then_break(by_identity.values()))`, [
      "engine/pipeline/e_zone_detector.py:_register_order_audit",
      "engine/pipeline/e_zone_detector.py:_enrich_order_audit_reset_causes",
      "engine/bridge/trading_pipeline.py:serialize_order_audit",
    ]),
  }),

  stop_all: Object.freeze({
    stopall_1: typeSummary(`def stopall_1(s_key, s_count, e_key, e_count, current_e):
    qualifies_e = e_key is not None and e_count >= 2
    qualifies_s = e_key is None and s_key is not None and s_count >= 2
    if not (qualifies_e or qualifies_s):
        return None
    parent = latest_matching_parent(
        e_key if qualifies_e else s_key,
        before=current_e.source_time,
    )
    gate = _strict_stop(parent.decision_event_time, parent.price)
    if gate is None or gate.event_time > current_e.decision_event_time:
        return None
    return _stopall_from_e(
        current_e, number=1, gate_type="stopall-stop",
        gate_event=gate.event_time,
        stopped_behavior=e_key if qualifies_e else s_key,
        stopped_count=e_count if qualifies_e else s_count,
    )`, [
      "engine/pipeline/lifecycle_engine.py:detect",
      "engine/pipeline/lifecycle_engine.py:_strict_stop",
      "engine/pipeline/lifecycle_engine.py:_stopall_from_e",
    ]),
    continuation: typeSummary(`def stopall_continuation(active_stopalls, current_e):
    stopped = [
        item for item in active_stopalls
        if (stop := _strict_stop(item.decision_event_time, item.price)) is not None
        and stop.event_time <= current_e.decision_event_time
    ]
    if not stopped:
        return None
    highest = max(item.number for item in stopped)
    next_stopall = _stopall_from_e(
        current_e, number=highest + 1,
        gate_type="stopall-stop",
        stopped_behavior=f"StopAll{highest}",
        gate_event=min(stop.event_time for stop in stopped),
        stopped_count=len(stopped),
    )
    return remove_stopped_and_append(active_stopalls, next_stopall)`, [
      "engine/pipeline/lifecycle_engine.py:detect",
      "engine/pipeline/lifecycle_engine.py:_strict_stop",
      "engine/pipeline/lifecycle_engine.py:_stopall_from_e",
    ]),
  }),
});
