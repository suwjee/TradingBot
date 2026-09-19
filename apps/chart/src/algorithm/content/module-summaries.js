const summary = (code, sources) => Object.freeze({ code, sources: Object.freeze(sources) });

export const MODULE_SUMMARIES = Object.freeze({
  reaction: summary(`def find_bullish_reactions(main_candles, lower_candles):
    candles = decimal_candles(main_candles)       # Open <= Close is GREEN
    reactions, resets = [], []

    # The selected range begins as a new leg.  The directional detector owns
    # the complete Mode-A scan and returns its first confirmed Reaction.
    current = first_confirmed_mode_a(
        first_red_after_green=True,
        frozen_owner_floor=True,
        strict_break="High > BoxTop",
        exact_race=lower_candles,
    )
    if current is None:
        return reactions, resets
    reactions.append(current)

    next_index = current.break_index + 1
    # Every Mode-A leg starts a fresh Blue strike-count comparison.
    running_peak = current_break_candle.high
    pending_reset = same_candle_reset_after_exact_break(current, lower_candles)

    while next_index <= last_index:
        # A strict Low below the confirmed BoxBottom resets the active owner.
        # If a Mode-B break competes inside the same main candle, lower-candle
        # chronology decides whether Reset or confirmation happened first.
        if pending_reset or previous_owner_resets_before_candidate_break():
            reset = record_owned_reset(previous=current)
            resets.append(reset)
            recovered = first_direct_mode_a_after_reset(
                reset_index=reset.index,
                frozen_leg_floor=True,
                reject_blocked_nested_first=True,
            )
            if recovered is None:
                break
            reactions.append(recovered)
            current = recovered
            next_index = recovered.break_index + 1
            running_peak = recovered_break_candle.high
            pending_reset = same_candle_reset_after_exact_break(recovered, lower_candles)
            mode_b_candidate = None if pending_reset else candidate_from_break_candle(recovered)
            continue

        if mode_b_candidate is None and candle.tag == "RED":
            # BoxTop keeps the running peak.  BoxBottom starts at the lowest
            # main-candle Low after that peak source through FirstRed.
            top_source = running_peak_source if running_peak >= candle.high else candle.index
            bottom_start = top_source + 1 if top_source < candle.index else candle.index
            mode_b_candidate = Candidate(
                first=candle,
                box_top=max(running_peak, candle.high),
                box_bottom=min_low(bottom_start, candle.index),
                mode="B",
            )

        if mode_b_candidate is not None:
            mode_b_candidate.box_bottom = min(mode_b_candidate.box_bottom, candle.low)
            if candle.high > mode_b_candidate.box_top:   # equality is not a break
                refine_box_bottom_until_exact_break(lower_candles)
                reactions.append(mode_b_candidate)
                current = mode_b_candidate
                running_peak = candle.high
                pending_reset = same_candle_reset_after_exact_break(current, lower_candles)
                mode_b_candidate = None if pending_reset else candidate_from_break_candle(current)

        running_peak = max_with_earliest_source(running_peak, candle.high)
        next_index += 1

    return reactions, resets`, [
    "engine/pipeline/reaction_engine.py:UnifiedReactionDetector.detect",
    "engine/pipeline/reaction_engine.py:BullishDetector.detect",
    "engine/pipeline/reaction_engine.py:breakout_analysis",
  ]),

  reset: summary(`def find_reaction_resets(reactions, lower_candles):
    resets = []

    for reaction in confirmed_owner_order(reactions):
        level = reaction.box_bottom
        break_event = exact_strict_high_cross(reaction.box_top)

        # Case 1: confirmation and Reset share one main candle.  Only seconds
        # after the exact Break may reset the newly confirmed Reaction.
        same_candle = first_lower_candle(
            after=break_event,
            before=break_main_candle_end,
            where="Low < BoxBottom",
        )
        if same_candle is not None:
            resets.append(Reset(
                index=reaction.break_index,
                second_time=same_candle.time,
                broken_level=level,
                from_first_index=reaction.first_index,
            ))
            clear_candidate_and_restart_mode_a()
            continue

        # Case 2: a later main candle reaches the boundary.  The engine uses
        # lower seconds to resolve a same-candle race with a waiting Mode-B
        # confirmation, but the public later Reset stores main time and leaves
        # secondTime null.
        later = first_main_candle(where="Low < BoxBottom")
        if later is not None and reset_wins_any_lower_second_race(later):
            resets.append(Reset(
                index=later.index,
                second_time=None,
                broken_level=level,
                from_first_index=reaction.first_index,
            ))
            clear_candidate_and_restart_mode_a()

    return resets`, [
    "engine/pipeline/reaction_engine.py:confirmed_reset_before_breakout",
    "engine/pipeline/reaction_engine.py:post_breakout_reset",
    "engine/pipeline/reaction_engine.py:_append_reset",
  ]),

  blue_line: summary(`def build_bullish_blue_lines(reactions, resets, candles, lower_candles):
    previous_strike_count = None
    has_blue_line = False
    healthy_reactions_since_blue = 0
    all_lines = []
    resets_by_owner = group_resets_by_first_index(resets)

    for reaction in reactions:
        if reaction.mode == "A":
            previous_strike_count = None
        reference = (
            mode_a_anchor(reaction)
            if reaction.mode == "A"
            else previous_reaction_floor(reaction)
        )
        fibonacci = reaction.box_top - Decimal("0.618") * (
            reaction.box_top - reference
        )
         # A pending strike is replaced only by a more directional strict
         # extreme. Any same or later GREEN main candle confirms it (doji is
         # GREEN); a pending strike at Reaction end uses lower-second fallback
         # through the exact Break candle.
         strikes = confirmed_strict_strikes(
            reaction,
            fibonacci,
            candles,
            lower_candles,
        )

        count_increased = (
            previous_strike_count is not None
            and len(strikes) > previous_strike_count
        )
        spacing_open = not has_blue_line or healthy_reactions_since_blue >= 1
        scale_emitted = False
        if count_increased and spacing_open:
            all_lines.append(make_scale_blue(reaction, strikes[-1]))
            has_blue_line = True
            healthy_reactions_since_blue = 0
            scale_emitted = True

        if has_blue_line and not scale_emitted:
            healthy_reactions_since_blue += 1

        for reset in resets_by_owner.get(reaction.first_index, []):
            if has_blue_line and healthy_reactions_since_blue < 1:
                continue
            line = make_one_fifth_reset_blue(reset, candles)
            line.calculation_valid = not prior_blue_stops_on_reset_index(
                previous_line=last_item(all_lines),
                reset_line=line,
                candles=candles,
            )
            all_lines.append(line)
            has_blue_line = True
            healthy_reactions_since_blue = 0

        previous_strike_count = None if reaction.mode == "A" else len(strikes)

    # Blue itself publishes no stop fields.  ADetector later builds private
    # BlueState rows and finds the first strict source-extreme stop for A.
    private_blue_states_for_a = build_blue_states_from_valid_lines(all_lines)
    return {
        "calculation": all_lines,
        "public": [line for line in all_lines if line.calculation_valid],
        "downstream_only": private_blue_states_for_a,
    }`, [
     "engine/pipeline/blue_line_detector.py:count_scale_strikes",
     "engine/pipeline/blue_line_detector.py:_intrabar_pending_confirmation",
    "engine/pipeline/blue_line_detector.py:detect_blue_lines",
    "engine/pipeline/a_zone_detector.py:_build_blue_states",
  ]),

  a: summary(`def build_bullish_a_zones(blue_lines, reactions):
    special = _double_stop_a_candidates()
    states = _build_blue_states()  # skips calculation_valid=False
    output = []
    cycle_after_index = -1
    index = 0

    while index + 1 < len(states):
        previous, current = states[index], states[index + 1]
        if previous.formation_index <= cycle_after_index or current.formation_index <= cycle_after_index:
            index += 1
            continue

        expires_at = states[index + 2].formation_time if index + 2 < len(states) else None
        trigger = _pair_trigger(previous, current, expires_at)
        if trigger is None:
            index += 1
            continue

        match = _first_reaction_after(
            trigger.trigger_event_time,
            not_before=max(trigger.blue_1_stop_time, trigger.blue_2_stop_time),
        )
        if match is None:
            break

         # _range_extreme/_a_source keep the earlier source on equal
         # bullish extrema. Coexisting Blue stops use (stop_event_time,
         # -stop_level): at an exact-time tie the second stop is the trigger
         # and the first stop supplies continuation level/source.
         source = _a_source(trigger.trigger_index, match.reaction)
        if source is not None:
            output.append(AZone(previous, current, trigger, match, source))
            cycle_after_index = match.reaction.break_idx
        index = first_state_formed_after(cycle_after_index)

    special = reject_special_owned_by_ordinary_or_prior_live_a(special, output)
    output = remove_later_ordinary_a_reusing_special_blue_ordinals(output, special)
    return sorted(output + special, key=lambda item: (item.source_time, item.trigger_event_time))`, [
    "engine/pipeline/a_zone_detector.py:_build_blue_states",
     "engine/pipeline/a_zone_detector.py:_pair_trigger",
     "engine/pipeline/a_zone_detector.py:_range_extreme",
    "engine/pipeline/a_zone_detector.py:_double_stop_a_candidates",
    "engine/pipeline/a_zone_detector.py:detect",
  ]),

  s_red: summary(`def build_red_s_zones(a_zones, bullish_reactions, opposite_geometry):
    red_zones, order_audit = [], {}
    ownership_windows = []

    # Audit every stopped A before S filters; Bridge later keeps only causes
    # belonging to accepted public A rows.
    for a_zone in a_zones:
        audit_first_order_created_by_strict_a_stop(a_zone, order_audit)

    for a_zone in a_zones_in_source_order:
        if a_source_is_inside_prior_s_ownership(a_zone, ownership_windows):
            continue
        a_stop = first_lower_event(from_event=a_confirmation(a_zone), where="Low < A.price")
        if a_stop is None or next_a_confirms_at_or_before(a_stop):
            continue
        # Ownership opens immediately and stays pending until an S decides.
        ownership_windows.append((a_stop.event_time, None))

        order = first_healthy_opposite_geometry_after_exact_a_stop(a_stop.event_time)
        if order is None:
            continue
        order_stop_level = (
            full_mode_a_leg_high_through_break(order)
            if order.mode == "A"
            else previous_opposite_reaction.box_top
        )

        timing = "after" if order.box_bottom <= a_stop_main_candle.low else "before"
        pre_order_candidate = candidate_from_exact_a_stop_remainder_through_order_first()
        if timing == "before" and pre_order_candidate is not None:
            decision = race_after_order_confirmation(
                candidate_cross="Low < candidate.price",
                order_stop="High > order_stop_level",
                same_lower_candle="reject",
                unqualified_candidate_cross="fallback",
            )
            if decision == "red":
                red_zones.append(make_s_zone("red", "simple", pre_order_candidate, order))
                ownership_windows[-1] = (a_stop.event_time, s_source_time + timeframe)
                continue
            if decision != "fallback":
                continue

        nested = first_bullish_reaction_wholly_inside_order_before_confirmation()
        if nested is not None:
            candidate = order_box_bottom_source                 # advanced
            formation_type = "advanced"
        else:
            aligned = first_bullish_reaction_confirmed_after_order()
            if aligned is None:
                continue
            candidate = lowest_main_low(order.break_index, aligned.break_index)  # last tie
            formation_type = "simple"

        red_source = pre_order_candidate or candidate_after_order(candidate, order)
        decision = exact_lower_candle_scan(
            red_source, order_stop_level,
            blue_only_when="Reset Blue or ordinary Reaction evidence exists by cross",
            raw_same_lower_candle_cross="reject",
            unqualified_candidate_cross="keep scanning",
        )
        if decision == "red":
            red_zones.append(make_s_zone("red", formation_type, red_source, order))
            ownership_windows[-1] = (a_stop.event_time, s_source_time + timeframe)

    return sorted(red_zones), order_audit`, [
    "engine/pipeline/s_zone_detector.py:_first_a_stop",
    "engine/pipeline/s_zone_detector.py:_decision",
     "engine/pipeline/s_zone_detector.py:_audit_stopped_a",
     "engine/pipeline/s_zone_detector.py:detect",
     "engine/bridge/trading_pipeline.py:blocked_orders_while_invalid_leg_heads_are_live",
  ]),

  s_blue: summary(`def build_blue_s_zones(a_zones, bullish_reactions, opposite_geometry):
    blue_zones, order_audit = [], {}
    ownership_windows = []

    for a_zone in a_zones:
        audit_first_order_created_by_strict_a_stop(a_zone, order_audit)

    for a_zone in a_zones_in_source_order:
        if a_source_is_inside_prior_s_ownership(a_zone, ownership_windows):
            continue
        a_stop = first_lower_event(from_event=a_confirmation(a_zone), where="Low < A.price")
        if a_stop is None or next_a_confirms_at_or_before(a_stop):
            continue
        # A bullish invalid leg head with a real pending S keeps this window
        # private until the head's exact stop. Opposite Order Firsts opened
        # before then are blocked from outer E ownership; no pending S means no
        # such block.
        ownership_windows.append((a_stop.event_time, None))
        next_order = first_healthy_opposite_geometry_after_exact_a_stop(a_stop.event_time)
        type3_deadline = next_order.confirmation if next_order else selected_range_end

         # Type 3 preempts ordinary blue S when any eligible Reset lifecycle
         # decides first inside [a_stop, next Order confirmation).
         # Evaluate every eligible Reset and choose the earliest strict crossing
        # in [a_stop, type3_deadline). The owner confirmation may equal A-stop.
        type3_candidates = all_opposite_reset_candidates_after_a_stop_before(type3_deadline)
        type3 = min(
            (candidate for candidate in type3_candidates
             if candidate.owner_confirmation <= a_stop.event_time
             and a_stop.event_time <= candidate.decision_event_time < type3_deadline),
            key=lambda candidate: candidate.decision_event_time,
            default=None,
        )
        if type3 is not None:
            owner = type3.owner
            reset_leg = directional_extreme(owner.break_index, type3.reset_index, prefer_last_tie=True)
            cross = first_lower_event(after=type3.reset_time, where="Low < reset_leg.price")
            evidence = bullish_reaction_confirmation_between(a_stop.event_time, cross.time)
            if cross and evidence:
                blue_zones.append(make_type3_s(
                    source=reset_leg, decision=cross,
                    order_fields=None, reset_provenance=type3,
                ))
                ownership_windows[-1] = (a_stop.event_time, reset_leg.source_time + timeframe)
                continue

        if next_order is None:
            continue
        order_stop_level = mode_a_leg_high_or_previous_mode_b_box_top(next_order)
        pre = candidate_from_exact_a_stop_remainder_through_order_first()
        if candidate_timing_is_before_order(pre, next_order):
            decision = first_lower_candle_after_order_confirmation_where(
                candidate_cross="Low < pre.price with accepted evidence",
                order_stop="High > order_stop_level",
                unqualified_candidate_cross="fallback",
                same_lower_candle="reject",
            )
            if decision == "blue":
                blue_zones.append(make_s_zone("blue", "simple", pre, next_order))
                ownership_windows[-1] = (a_stop.event_time, pre.source_time + timeframe)
                continue
            if decision != "fallback":
                continue

        nested = first_bullish_reaction_wholly_inside_order_before_confirmation()
        if nested is not None:
            candidate = order_box_bottom_source
            formation_type = "advanced"
            candidate_start = nested.confirmation
        else:
            aligned = first_bullish_reaction_confirmed_after_order()
            if aligned is None:
                continue
            candidate = lowest_main_low(next_order.break_index, aligned.break_index)  # last tie
            formation_type = "simple"
            candidate_start = aligned.confirmation

        decision = first_lower_candle_after_order_confirmation_where(
            candidate_cross="Low < candidate.price with accepted evidence by this event",
            order_stop="High > order_stop_level",
            not_before_candidate=candidate_start,
            raw_same_lower_candle_cross="reject",
            unqualified_candidate_cross="keep scanning",
        )
        if candidate_cross_and_order_stop_share_one_lower_candle(decision):
            continue
        if decision == "blue":
            blue_zones.append(make_s_zone("blue", formation_type, candidate, next_order))
            ownership_windows[-1] = (a_stop.event_time, candidate.source_time + timeframe)

    return sorted(blue_zones, key=(source_time, decision_event_time)), order_audit`, [
    "engine/pipeline/s_zone_detector.py:_candidate_cross_has_blue",
    "engine/pipeline/s_zone_detector.py:_first_type3",
     "engine/pipeline/s_zone_detector.py:_decision",
     "engine/pipeline/s_zone_detector.py:detect",
     "engine/bridge/trading_pipeline.py:blocked_orders_while_invalid_leg_heads_are_live",
  ]),

  e_blue: summary(`def build_blue_e_family(accepted_s, initial_order_audit):
    provisional = []
    discover_orders_for_every_stopped_s_before_recursive_walk()

    for blue_s in accepted_s_where(color="blue"):
        parent_type, parent, next_number = "S", blue_s, 1
        used_sources = set()
        while (parent_stop := first_strict_low_below(parent.price, from_event=parent.decision_event)):
            inherited = unconsumed_blue_s_order(parent, parent_stop) if parent_type == "S" else None
            carried = accepted_order_formed_and_live_inside_parent(parent, parent_stop)
            register_parent_order_eligibility(parent, parent_stop)
            # Direct candidates use order_candidates() and older First wins an
            # equal stop event. The final race across direct/inherited/carried
            # representatives uses newer First only for that equal-time tie.
            direct = canonical_published_or_bounded_fallback(
                published=published_order_candidate(parent_stop),
                bounded=first_healthy_direct_geometry(parent_stop),
            )
            direct_pool = order_candidates(
                parent_stop.event,
                continuous_deadline=inherited.stop_event if inherited and not carried else None,
            )
            direct = first_order(direct_pool, preferred=direct)
            winner = min(
                stopped(direct, inherited, carried),
                key=(order_stop_event, -first_index),
            )
            if winner is None:
                break

            decision = max(parent_stop.event, winner.stop_event)
            source = lowest_main_low(
                parent_stop.main_candle, winner.stop_main_candle,
                include_both_complete_candles=True,
            )
            if source.identity in used_sources:
                break
            child = EZone("blue", next_number, parent_type, parent, winner, source, decision)
            provisional.append(child)
            used_sources.add(source.identity)
            parent_type, parent, next_number = "E", child, next_number + 1

     # A later main candle containing a strict stop owns the transition first.
     # Only same-candle stops use StopAll > E red > S red > E blue > S blue > A,
     # then sequence number and deterministic source keys.
     accepted = reconcile_chronological_active_ownership(provisional)
    accepted = apply_red_over_blue_dominance_and_stopall_sequence_resets(accepted)
    retain_stopped_history_and_required_parent_lineage(accepted)
    rebuild_order_audit_from_accepted_s_e_stopall_parents(accepted)
    return sorted(accepted, key=(source_time, source_index))`, [
    "engine/pipeline/e_zone_detector.py:order_candidates",
    "engine/pipeline/e_zone_detector.py:_carried_order_for_parent",
     "engine/pipeline/e_zone_detector.py:_zone",
     "engine/pipeline/e_zone_detector.py:detect",
     "engine/bridge/trading_pipeline.py:split_a_zones_by_dominant_stops",
  ]),

  e_red: summary(`def build_red_e_family(accepted_s, initial_order_audit):
    provisional = []
    discover_orders_for_every_stopped_s_before_recursive_walk()

    for red_s in accepted_s_where(color="red"):
        parent_type, parent, next_number = "S", red_s, 1
        used_sources = set()
        while (parent_stop := first_strict_low_below(parent.price, from_event=parent.decision_event)):
            inherited = unconsumed_blue_s_order(parent, parent_stop) if parent_type == "S" else None
            carried = accepted_order_formed_and_live_inside_parent(parent, parent_stop)
            register_parent_order_eligibility(parent, parent_stop)
            # Direct candidates use order_candidates() and older First wins an
            # equal stop event. A bounded geometric fallback is allowed only
            # when the published candidate has no strict stop.
            direct = canonical_published_or_bounded_fallback(
                published=published_order_candidate(parent_stop),
                bounded=first_healthy_direct_geometry(parent_stop),
            )
            direct_pool = order_candidates(
                parent_stop.event,
                continuous_deadline=inherited.stop_event if inherited and not carried else None,
            )
            direct = first_order(direct_pool, preferred=direct)
            winner = min(
                stopped(direct, inherited, carried),
                key=(order_stop_event, -first_index),
            )
            if winner is None:
                break

            decision = max(parent_stop.event, winner.stop_event)
            source = lowest_main_low(
                parent_stop.main_candle, winner.stop_main_candle,
                include_both_complete_candles=True,
            )
            if source.identity in used_sources:
                break
            child = EZone("red", next_number, parent_type, parent, winner, source, decision)
            provisional.append(child)
            used_sources.add(source.identity)
            parent_type, parent, next_number = "E", child, next_number + 1

     # A later main candle containing a strict stop owns the transition first.
     # Only same-candle stops use StopAll > E red > S red > E blue > S blue > A,
     # then sequence number and deterministic source keys.
     accepted = reconcile_chronological_active_ownership(provisional)
    accepted = keep_red_over_blue_and_apply_stopall_sequence_resets(accepted)
    retain_stopped_history_and_required_parent_lineage(accepted)
    rebuild_order_audit_from_accepted_s_e_stopall_parents(accepted)
    return sorted(accepted, key=(source_time, source_index))`, [
    "engine/pipeline/e_zone_detector.py:order_candidates",
    "engine/pipeline/e_zone_detector.py:_carried_order_for_parent",
     "engine/pipeline/e_zone_detector.py:_zone",
     "engine/pipeline/e_zone_detector.py:detect",
     "engine/bridge/trading_pipeline.py:split_a_zones_by_dominant_stops",
  ]),

  order_audit: summary(`def build_order_audit(s_audit, accepted_e_orders, accepted_parents, view_range):
    records = {}

    for candidate in chain(s_audit, accepted_e_orders):
        if not accepted_calculation_provenance(candidate.cause):
            continue

        identity = (
            candidate.order.first_index,
            candidate.order.break_index,
        )
        if identity not in records:
            records[identity] = copy_physical_order_geometry(candidate.order)
            records[identity].causes = []

        records[identity].causes = deduplicate_causes(
            records[identity].causes + candidate.causes
        )

    visible = [
        record
        for record in records.values()
        if view_range.contains(record.first_index)
    ]
    return sorted(visible, key=lambda item: (item.first_index, item.break_index))`, [
    "engine/pipeline/s_zone_detector.py:_audit_stopped_a",
    "engine/pipeline/e_zone_detector.py:_register_order_audit",
    "engine/pipeline/e_zone_detector.py:_enrich_order_audit_reset_causes",
    "engine/bridge/trading_pipeline.py:serialize_order_audit",
  ]),

  stop_all: summary(`def build_stop_all_sequence(s_zones, e_zones, lower_candles):
    s_key, s_count = None, 0
    e_key, e_count = None, 0
    active, output = [], []

    for e_item in chronological(e_zones):
        while next_s.source_time < e_item.source_time:
            incoming = _sequence_priority("s", next_s.color)
            current = _active_sequence_priority(s_key, e_key)
            if e_key is None and s_key == next_s.color:
                s_count += 1
            elif incoming > current:
                s_key, s_count = next_s.color, 1
                e_key, e_count = None, 0
            next_s = advance_s()

        stopped_active = [item for item in active if _strict_stop(item) <= e_item.decision_event_time]
        if stopped_active:
            highest = max(item.number for item in stopped_active)
            gate_event = min(item.stop_event_time for item in stopped_active)
            zone = _stopall_from_e(
                e_item, highest + 1, "stopall-stop",
                gate_event=gate_event,
                stopped_behavior=f"StopAll{highest}",
                stopped_count=len(stopped_active),
            )
            output.append(zone)
            active = remove_stopped_and_append(active, stopped_active, zone)
            s_key, s_count, e_key, e_count = None, 0, None, 0
            continue

        qualifies_e = e_key is not None and e_count >= 2
        qualifies_s = e_key is None and s_key is not None and s_count >= 2
        parent = latest_matching_parent(qualifies_e, qualifies_s)
        if parent and _strict_stop(parent) <= e_item.decision_event_time:
            zone = _stopall_from_e(e_item, 1, "stopall-stop", ...)
            output.append(zone)
            active.append(zone)
            s_key, s_count, e_key, e_count = None, 0, None, 0
            continue

         # Group priority is S blue < E blue < S red < E red. This is
         # separate from leg ownership: latest stop-containing main candle
         # wins, then same-candle StopAll > E red > S red > E blue > S blue > A.
         e_key, e_count, s_key, s_count = integrate_e_by_priority(e_item, ...)

    return attach_next_strict_stop(output, lower_candles)


def reconcile_e_and_stop_all(e_detector, visible_s):
    seen_reset_maps = set()
    while True:
        e_zones = e_detector.detect()
        # Recompute S visibility from the current E state before each pass;
        # compare only the public reset map owned by the E detector.
        visible_s = recompute_s_visibility(visible_s, e_zones)
        stop_alls = build_stop_all_sequence(visible_s, e_zones, lower_candles)
        previous_map = dict(e_detector.sequence_resets)
        reset_map = {item.source_time: item.number for item in stop_alls}
        if reset_map == previous_map:
            return e_zones, stop_alls
        if freeze(reset_map) in seen_reset_maps:
            raise ValueError("E/StopAll lifecycle reconciliation did not converge")
        seen_reset_maps.add(freeze(reset_map))
        e_detector.sequence_resets = reset_map`, [
    "engine/pipeline/lifecycle_engine.py:StopAllDetector.detect",
    "engine/pipeline/lifecycle_engine.py:_stopall_from_e",
    "engine/bridge/trading_pipeline.py:reconcile_stopall_lifecycle",
  ]),
});
