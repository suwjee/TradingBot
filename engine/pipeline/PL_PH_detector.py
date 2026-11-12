"""Directional primary structure state and immutable matching behavior legs.

The bullish path reflects the approved bearish primary state machine.
Native Reaction, Reset,
dominance, physical Order identity and stop geometry remain owned by their
existing engines.
"""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from copy import deepcopy
from dataclasses import dataclass, field, replace
from datetime import datetime
from decimal import Decimal
from typing import Callable, Sequence

from core_utils import as_decimal
from lifecycle_engine import advance_dominant_behavior
from order_audit_engine import relabel_primary_causes

PL_PH_VERSION = "1.4.0"
PL_PH_LAST_MODIFIED = "2026-11-12T01:34:50+03:30"


@dataclass(frozen=True, slots=True)
class StructureOrder:
    direction: str
    reaction_number: int
    first_index: int
    break_index: int
    confirmation_event_time: datetime
    stop_level: Decimal
    stop_source_index: int
    stop_index: int
    stop_event_time: datetime
    causes: tuple[str, ...]
    box_top: Decimal | None = None
    box_bottom: Decimal | None = None
    reaction_mode: str | None = None
    audit_causes: tuple[dict[str, object], ...] = ()


@dataclass(frozen=True, slots=True)
class PrimaryPoint:
    kind: str
    number: int
    source_index: int
    source_time: datetime
    price: Decimal
    trigger_index: int
    trigger_event_time: datetime
    decision_index: int
    decision_event_time: datetime
    order: StructureOrder
    cycle_id: str | None = field(default=None, kw_only=True)
    identity_source: PrimaryPoint | None = field(default=None, kw_only=True)


@dataclass(frozen=True, slots=True)
class MatchingBehaviorLeg:
    source_index: int
    source_time: datetime
    price: Decimal
    reference_stopall_index: int
    second_behavior_index: int
    trigger_index: int
    trigger_event_time: datetime
    stop_index: int | None
    stop_event_time: datetime | None


@dataclass(frozen=True, slots=True)
class TrendTransition:
    """The first strict stop of a confirmed primary3 ends every owner cycle."""
    index: int
    event_time: datetime
    level: Decimal
    high: PrimaryPoint
    target_direction: str = "bullish"

    @property
    def point(self):
        """Neutral stopped-point name; high remains positional compatibility."""
        return self.high


@dataclass(slots=True)
class PrimaryResult:
    highs: list[PrimaryPoint] = field(default_factory=list)
    lows: list[PrimaryPoint] = field(default_factory=list)
    mbl: MatchingBehaviorLeg | None = None
    status: str = "waiting-for-matching-behaviors"
    post_pl3_orders: list[StructureOrder] = field(default_factory=list)
    cycle_id: str | None = None
    cycles: list[PrimaryResult] = field(default_factory=list)
    qualification_event_time: datetime | None = None
    transition: TrendTransition | None = None
    direction: str = "bearish"


def first_bullish_transition(chronology, primary, *, cross=None):
    """Select the earliest exact PH3 stop across all confirmed cycle owners."""
    transitions = []
    for point in resolve_primary_highs(primary, through_index=len(chronology.candles)-1):
        if point.number != 3:
            continue
        crossed = (cross or strict_cross)(chronology, point.decision_event_time, point.price, True)
        if crossed is not None:
            transitions.append(TrendTransition(*crossed, point.price, point))
    return min(transitions, key=lambda item: (
        item.event_time, item.high.source_index, item.high.cycle_id or ""
    ), default=None)


def first_bearish_transition(chronology, primary):
    """Select the earliest confirmed physical PL3 stop across bullish cycles."""
    transitions = []
    for point in resolve_primary_lows(primary, through_index=len(chronology.candles)-1):
        if point.number == 3:
            crossed = strict_cross(chronology, point.decision_event_time, point.price, False)
            if crossed is not None:
                transitions.append(TrendTransition(*crossed, point.price, point, "bearish"))
    return min(transitions, key=lambda item: (
        item.event_time, item.high.source_index, item.high.cycle_id or ""
    ), default=None)


def resolve_primary_highs(primary, *, through_index):
    """Resolve physical PH ownership after independent logical confirmation.

    Each candle has one final number. The greatest coincident local number
    wins; a strictly higher subsequent high continues the preceding final
    number. Logical cycle/reset states and their Order eligibility stay intact.
    Filter confirmations before reconciliation so future roles cannot rename
    an earlier requested horizon.
    """
    return _resolve_primary_points(primary.highs, getattr(primary, "cycles", ()),
                                   through_index, above=True)


def resolve_primary_lows(primary, *, through_index):
    """Reconcile bullish physical PL ownership without resetting local state."""
    return _resolve_primary_points(primary.lows, getattr(primary, "cycles", ()),
                                   through_index, above=False)


def _resolve_primary_points(points, cycles, through_index, *, above):
    physical = {}
    cycle_order = {cycle.cycle_id: index for index, cycle in
                   enumerate(cycles)}
    for point in points:
        if point.decision_index <= through_index:
            physical.setdefault((point.source_index, point.source_time), []).append(point)
    groups = sorted(physical.values(), key=lambda rows: (
        min(point.decision_event_time for point in rows), rows[0].source_time,
        rows[0].source_index,
    ))
    result = []
    for rows in groups:
        def role_order(point):
            return (point.decision_event_time,
            cycle_order.get(point.cycle_id, len(cycle_order)), point.cycle_id or "",
            point.trigger_index, point.number)
        identity = min(rows, key=role_order)
        winner = min(rows, key=lambda point: (-point.number, *role_order(point)))
        number = winner.number
        if result and ((winner.price > result[-1].price) if above
                       else (winner.price < result[-1].price)):
            number = max(number, result[-1].number + 1)
        result.append(replace(winner, number=number,
                              identity_source=identity.identity_source or identity))
    return result


def relabel_primary_order(order, highs):
    """Keep frozen structure Order snapshots aligned with final PH names."""
    labels = {point.source_time: f"{point.kind}{point.number}" for point in highs}
    return replace(order, audit_causes=tuple(relabel_primary_causes(order.audit_causes, labels)))


def formed_matching_legs(primary, *, through_index):
    """A qualified candidate becomes MBL only after its first confirmed PH.

    Keep the frozen candidate internally for cancellation/Order chronology;
    neither activation alone nor a future PH confirms a leg at this horizon.
    """
    for cycle in getattr(primary, "cycles", None) or [primary]:
        if cycle.mbl is None or cycle.mbl.trigger_index > through_index:
            continue
        points = cycle.lows if getattr(primary, "direction", "bearish") == "bullish" else cycle.highs
        confirmation = min((point for point in points
                            if point.decision_index <= through_index),
                           key=lambda point: point.decision_event_time, default=None)
        if confirmation is not None:
            yield cycle, confirmation


def resolve_stopall_ownership(stopalls, primary: PrimaryResult, *, through_index: int):
    """A confirmed PH owns its candle; retain the causal StopAll history.

    A future PH confirmation must not remove the StopAll from an earlier
    requested horizon. The supplied historical collection is never mutated.
    """
    points = primary.lows if getattr(primary, "direction", "bearish") == "bullish" else primary.highs
    promoted = {(point.source_index, point.source_time) for point in points
                if point.decision_index <= through_index}
    return [item for item in stopalls
            if (int(item.source_index), item.source_time) not in promoted]


def order_meets_structure_gate(kind, first_index, confirmation, gate_index, event):
    """PH eligibility follows Order confirmation, including a joint RAW event.

    An accepted PH Order can begin before the structure crossing. PL retains
    its separately specified First-candle and strict confirmation gates.
    """
    if kind == "PH":
        return confirmation >= event
    return first_index >= gate_index and confirmation > event


def strict_cross(chronology, event: datetime, level: Decimal, above: bool):
    """Find the first strictly later selected-RAW crossing, preserving equality."""
    left = bisect_right(chronology.second_times, event)
    return _cross_from(chronology, left, level, above)


def _cross_from(chronology, left, level, above):
    index = chronology.lower_index
    position = (index.first_greater if above else index.first_less)(
        left, len(chronology.seconds), level
    )
    if position is None:
        return None
    instant = chronology.second_times[position]
    return chronology.main_index(instant, clamp=True), instant


def _extreme(chronology, left: int, right: int, high: bool):
    attribute = "high" if high else "low"
    # Python min/max retain the first index on equality, as specified.
    chooser = max if high else min
    source = chooser(range(left, right + 1),
                     key=lambda i: as_decimal(getattr(chronology.candles[i], attribute)))
    return source, as_decimal(getattr(chronology.candles[source], attribute))


def _matching_seeds(s_zones, e_zones, stopalls):
    """Keep qualified legs pending until their first actual strict breakout."""
    occupied = {int(item.source_index) for item in stopalls}
    events = [(item.source_time, 0, "StopAll", item) for item in stopalls]
    events.extend((item.source_time, rank, kind, item)
                  for kind, rank, items in (("S", 1, s_zones), ("E", 2, e_zones))
                  for item in items
                  if int(item.source_index) not in occupied
                  and getattr(item, "calculation_valid", True) is not False)
    owner = reference = None
    qualified = False
    seen_events = set()
    confirmations: list[datetime] = []
    for _, _, kind, item in sorted(events, key=lambda row: (row[0], row[1], row[3].source_index)):
        identity = (kind, int(item.source_index), item.source_time)
        if identity in seen_events:
            continue
        seen_events.add(identity)
        if kind == "StopAll":
            reference = item if int(item.number) >= 3 else None
            owner, confirmations = None, []
            qualified = False
            continue
        if reference is None or qualified:
            continue
        family = str(item.color if kind == "S" else item.family).lower()
        number = None if kind == "S" else int(item.number)
        previous = owner
        owner = advance_dominant_behavior(owner, kind, family, number, item)
        if owner is previous:
            continue
        if previous is None or owner.count == 1:
            confirmations = []
        confirmations.append(item.decision_event_time)
        if owner.armed:
            qualified = True
            yield reference, item, max(reference.decision_event_time, *confirmations)


def detect_bearish(
    chronology, s_zones: Sequence[object], e_zones: Sequence[object],
    stopalls: Sequence[object],
    orders: Callable[[str, int, int, datetime], Sequence[StructureOrder]],
    *,
    _run: _PrimaryRun | None = None,
) -> PrimaryResult:
    """Merge independent cycles on exact chronology and one native Order ledger.

    A proposal never commits PH ownership. Only the globally earliest decision
    may mutate the native ledger; that mutation invalidates every pending
    proposal, including cycles waiting without an accepted Order.
    """
    result = PrimaryResult()
    cross = _run.cross if _run is not None else strict_cross
    activated = []
    qualified = False
    seen = set()
    for reference, second, qualification in _matching_seeds(s_zones, e_zones, stopalls):
        qualified = True
        if result.qualification_event_time is None or qualification < result.qualification_event_time:
            result.qualification_event_time = qualification
        identity = (int(reference.source_index), int(second.source_index))
        if identity in seen:
            continue
        seen.add(identity)
        level = as_decimal(chronology.candles[int(reference.source_index)].high)
        crossed = cross(chronology, qualification, level, True)
        if crossed is not None:
            activated.append((crossed, reference, second, qualification))
    activated.sort(key=lambda row: (
        row[0][1], row[3], row[1].source_index, row[2].source_index,
    ))
    if _run is not None:
        _run.schedule = tuple(_activation_identity(row) for row in activated)
    if not activated:
        if qualified:
            result.status = "waiting-for-stopall-break"
        return result
    checkpoints = []
    pending = {}
    promoted_sources = set()
    activation_index = 0
    commit_high = getattr(orders, "confirm_high", None)
    if _run is not None:
        for step in _run.retained_steps():
            activation_index = step.activations
            index, checkpoint, point = step.cycle_index, step.checkpoint, step.point
            if index is None:
                continue
            if index == len(checkpoints):
                checkpoints.append(checkpoint)
            else:
                checkpoints[index] = checkpoint
            if point is None:
                continue
            (result.highs if point.kind == "PH" else result.lows).append(point)
            if point.kind == "PH":
                promoted_sources.add((point.source_index, point.source_time))
                if commit_high is not None:
                    commit_high(point)
        checkpoints = [_refresh_cycle_mbl(chronology, checkpoint, cross) for checkpoint in checkpoints]
    transition = first_bullish_transition(chronology, result, cross=cross) if result.highs else None
    while True:
        for index, checkpoint in enumerate(checkpoints):
            if index not in pending:
                pending[index] = _next_point(chronology, checkpoint, orders,
                    before_event=transition.event_time if transition else None, cross=cross)
        decisions = [(point.decision_event_time, index)
                     for index, (_, point) in pending.items() if point is not None]
        decision = min(decisions, default=None)
        next_activation = (activated[activation_index][0][1]
            if activation_index < len(activated) else None)
        if (transition is not None
                and (decision is None or transition.event_time <= decision[0])
                and (next_activation is None or transition.event_time <= next_activation)):
            result.transition = transition
            break
        if activation_index < len(activated) and (
            decision is None or activated[activation_index][0][1] <= decision[0]
        ):
            # Activate all contexts at an instant before committing its points;
            # ties between points retain deterministic activation order.
            activation = activated[activation_index]
            activation_index += 1
            reference = activation[1]
            if (int(reference.source_index), reference.source_time) in promoted_sources:
                # The historical StopAll is already a confirmed PH. Its stop
                # belongs to PH continuation, not an independent matching leg.
                if _run is not None:
                    _run.steps.append(_PrimaryStep(activation[0][1], activation_index))
                continue
            checkpoint = _activate_cycle(chronology, activation, cross=cross)
            if _run is not None:
                _run.steps.append(_PrimaryStep(
                    activation[0][1], activation_index, len(checkpoints), checkpoint,
                ))
            checkpoints.append(checkpoint)
            continue
        if decision is None:
            break
        _, index = decision
        checkpoint, point = pending.pop(index)
        checkpoints[index] = checkpoint
        target = checkpoint.result.highs if point.kind == "PH" else checkpoint.result.lows
        target.append(point)
        (result.highs if point.kind == "PH" else result.lows).append(point)
        if _run is not None:
            _run.steps.append(_PrimaryStep(
                point.decision_event_time, activation_index, index, checkpoint, point,
            ))
        if point.kind == "PH":
            promoted_sources.add((point.source_index, point.source_time))
            if commit_high is not None:
                commit_high(point)
                pending.clear()
            transition = first_bullish_transition(chronology, result, cross=cross)

    result.cycles = [pending[index][0].result if index in pending else checkpoint.result
                     for index, checkpoint in enumerate(checkpoints)]
    result.mbl = result.cycles[0].mbl
    result.status = result.cycles[-1].status
    if result.transition is not None:
        result.status = "reversed-to-bullish"
    physical_orders = {}
    for cycle in result.cycles:
        for order in cycle.post_pl3_orders:
            physical_orders.setdefault((order.direction, order.first_index, order.break_index), order)
    result.post_pl3_orders = sorted(physical_orders.values(), key=lambda item: (
        item.stop_event_time, -item.first_index, item.break_index,
    ))
    return result


@dataclass(slots=True)
class _CycleCheckpoint:
    result: PrimaryResult
    reference_price: Decimal
    gate_index: int
    cursor: datetime
    phase: str = "PH"
    reset_high: bool = False


def _activation_identity(activation):
    crossed, reference, second, qualification = activation
    return (
        crossed[1], crossed[0], int(reference.source_index), reference.source_time,
        int(second.source_index), second.source_time, qualification,
    )


@dataclass(frozen=True, slots=True)
class _PrimaryStep:
    event_time: datetime
    activations: int
    cycle_index: int | None = None
    checkpoint: _CycleCheckpoint | None = None
    point: PrimaryPoint | None = None


@dataclass(slots=True)
class _PrimaryRun:
    previous: _PrimaryRun | None = None
    dirty_event: datetime | None = None
    schedule: tuple = ()
    steps: list[_PrimaryStep] = field(default_factory=list)
    crossings: dict[tuple, tuple[int, datetime] | None] = field(default_factory=dict)
    projected_points: dict[int, tuple[PrimaryPoint, PrimaryPoint]] = field(default_factory=dict)

    def retained_steps(self):
        if self.previous is None:
            return self.steps
        frontier = self.dirty_event
        old = self.previous.schedule
        position = 0
        while position < min(len(old), len(self.schedule)) and old[position] == self.schedule[position]:
            position += 1
        for schedule in (old, self.schedule):
            if position < len(schedule):
                frontier = min(frontier, schedule[position][0])
        for step in self.previous.steps:
            if step.event_time >= frontier:
                break
            self.steps.append(step)
        return self.steps

    def cross(self, chronology, event, level, above):
        key = event, str(level), above
        if key in self.crossings:
            return self.crossings[key]
        left = bisect_right(chronology.second_times, event)
        if self.previous is not None and key in self.previous.crossings:
            old = self.previous.crossings[key]
            if old is not None and old[1] < self.dirty_event:
                self.crossings[key] = old
                return old
            left = max(left, bisect_left(chronology.second_times, self.dirty_event))
        result = _cross_from(chronology, left, level, above)
        self.crossings[key] = result
        return result


def _refresh_cycle_mbl(chronology, checkpoint, cross):
    mbl = checkpoint.result.mbl
    stop = cross(chronology, mbl.trigger_event_time, mbl.price, False)
    stop_index, stop_time = stop or (None, None)
    if (stop_index, stop_time) == (mbl.stop_index, mbl.stop_event_time):
        return checkpoint
    mbl = replace(mbl, stop_index=stop_index, stop_event_time=stop_time)
    return replace(checkpoint, result=replace(checkpoint.result, mbl=mbl))


def _activate_cycle(chronology, activation, *, cross=strict_cross):
    crossed, reference, second, qualification = activation
    result = PrimaryResult(
        cycle_id=f"bearish:cycle:{reference.source_index}:{second.source_index}",
        qualification_event_time=qualification,
    )
    reference_price = as_decimal(chronology.candles[int(reference.source_index)].high)
    gate_index, cursor = crossed
    source, floor = _extreme(chronology, int(second.source_index), gate_index, False)
    broken = cross(chronology, cursor, floor, False)
    result.mbl = MatchingBehaviorLeg(
        source, chronology.times[source], floor, int(reference.source_index),
        int(second.source_index), gate_index, cursor,
        broken[0] if broken else None, broken[1] if broken else None,
    )
    return _CycleCheckpoint(result, reference_price, gate_index, cursor)


def _next_point(chronology, checkpoint, orders, *, before_event=None, cross=strict_cross):
    """Prospect from committed state without changing shared native ownership.

    Cancel/seek transitions are replayable: a later global PH commitment may
    admit an Order before a previously projected future cancellation.
    """
    result = replace(checkpoint.result, highs=list(checkpoint.result.highs),
                     lows=list(checkpoint.result.lows),
                     post_pl3_orders=list(checkpoint.result.post_pl3_orders))
    phase, reset_high = checkpoint.phase, checkpoint.reset_high
    gate_index, cursor = checkpoint.gate_index, checkpoint.cursor
    reference_price, floor = checkpoint.reference_price, result.mbl.price
    prospective = replace(checkpoint, result=result)
    # Every iteration consumes a strictly later RAW event. No arbitrary
    # feedback-pass cap is part of this algorithm. The PH3 transition is an
    # authoritative event boundary, not an arbitrary loop limit.
    while True:
        high_level = result.highs[-1].price if result.highs else reference_price
        low_level = result.lows[-1].price if result.lows else floor
        high_number = 1 if reset_high or not result.highs else result.highs[-1].number + 1
        low_number = result.lows[-1].number + 1 if result.lows else 1
        if phase == "seek":
            up = cross(chronology, cursor, high_level, True)
            down = cross(chronology, cursor, low_level, False)
            if up is None and down is None:
                result.status = "waiting-for-structure-break"
                return prospective, None
            if up and down and up[1] == down[1]:
                result.status = "ambiguous-raw-boundary-order"
                return prospective, None
            phase = "PH" if up and (down is None or up[1] < down[1]) else "PL"
            gate_index, cursor = up if phase == "PH" else down

        if before_event is not None and cursor >= before_event:
            result.status = "waiting-for-trend-reversal"
            return prospective, None
        number = high_number if phase == "PH" else low_number
        candidates = [item for item in orders(phase, number, gate_index, cursor)
                      if order_meets_structure_gate(phase, item.first_index,
                          item.confirmation_event_time, gate_index, cursor)
                      and item.stop_event_time > item.confirmation_event_time]
        winner = min(candidates, key=lambda item: (
            item.stop_event_time, -item.first_index, item.break_index
        ), default=None)
        cancel = cross(chronology, cursor, floor if phase == "PH" else high_level, phase == "PL")
        cancel_is_next = cancel and (
            (phase == "PL" and number > 3)
            or winner is None or cancel[1] < winner.stop_event_time
        )
        if cancel_is_next:
            raw_position = bisect_right(chronology.second_times, cancel[1]) - 1
            raw = chronology.seconds[raw_position]
            opposing = (as_decimal(raw.high) > high_level if phase == "PH"
                        else as_decimal(raw.low) < floor)
            if opposing:
                result.status = "ambiguous-raw-boundary-order"
                return prospective, None
        if phase == "PL" and number > 3:
            # The taught post-PL3 stage evaluates native Orders but does not
            # define PL4. A later upward break may still start a new PH.
            result.post_pl3_orders = [item for item in candidates
                if cancel is None or item.stop_event_time < cancel[1]]
            if cancel is None:
                result.status = "post-pl3-orders-only"
                return prospective, None
            gate_index, cursor = cancel
            phase = "PH"
            continue
        if cancel and winner and cancel[1] == winner.stop_event_time:
            result.status = "ambiguous-raw-boundary-order"
            return prospective, None
        if cancel and (winner is None or cancel[1] < winner.stop_event_time):
            gate_index, cursor = cancel
            if phase == "PL":
                phase = "PH"
            elif result.lows:
                # Cancelling a pending PH cannot manufacture a break of an
                # existing PL: later PL still requires that previous Low.
                if as_decimal(chronology.seconds[bisect_right(chronology.second_times, cursor)-1].low) < low_level:
                    phase = "PL"
                else:
                    phase = "seek"
            else:
                phase = "PL"
            continue
        if winner is None:
            result.status = f"waiting-for-{phase.lower()}-order-stop"
            return prospective, None
        source, price = _extreme(chronology, gate_index, winner.stop_index, phase == "PH")
        point = PrimaryPoint(phase, number, source, chronology.times[source], price,
                             gate_index, cursor, winner.stop_index,
                             winner.stop_event_time, winner, cycle_id=result.cycle_id)
        prospective.gate_index = gate_index
        prospective.cursor, prospective.phase = winner.stop_event_time, "seek"
        prospective.reset_high = phase == "PL"
        return prospective, point


class NativePrimaryOrders:
    """Read accepted native audit and commit PH parents to its Order owner.

    The owner bucket is the conceptual order direction in the user rules.
    Its native order_direction field names the opposite physical Reaction.
    Reaction Mode A/B is distinct from parent-stop/reset-leg creation type.
    Confirmed PH stops create Order_A through that native owner; unconfirmed
    structure crossings cannot manufacture physical Orders here.
    """

    def __init__(self, chronology, groups, *, on_high=None, direction="bearish"):
        self.chronology, self.groups = chronology, groups
        self.on_high = on_high
        self.direction = direction

    def confirm_high(self, point):
        """Commit PH ownership before subsequent native Order selection."""
        if self.on_high is not None:
            self.on_high(point)

    def __call__(self, kind, number, gate_index, event):
        owner = "bearish" if kind == "PH" else "bullish"
        is_primary = kind == ("PL" if self.direction == "bullish" else "PH")
        physical_direction = self.chronology.opposite_direction(owner)
        eligible = []
        records = []
        for prepared in self.groups[owner].get("OrderAudit", ()):
            reaction, entry = prepared["reaction"], prepared["entry"]
            first, breakout = int(reaction.first_idx), int(reaction.break_idx)
            confirmation = self.chronology.reaction_confirmation(physical_direction, reaction)
            stopped = prepared["crossed"]
            causes = tuple(dict.fromkeys(cause["kind"] for cause in prepared["causes"]))
            if not order_meets_structure_gate("PH" if is_primary else "PL",
                                             first, confirmation, gate_index, event):
                continue
            # PL Order_A's first valid downward Reaction must be canonical.
            if not is_primary and int(entry["reaction_number"]) <= 0:
                continue
            if is_primary and number > 1 and "parent-stop" not in causes:
                continue
            records.append((prepared, first, breakout, confirmation, causes))
        direct = [row for row in records if "parent-stop" in row[4]]
        first_direct = min(direct, key=lambda row: (row[1], row[3], row[2]), default=None)
        for record in records:
            prepared, first, breakout, confirmation, causes = record
            reaction, entry, stopped = prepared["reaction"], prepared["entry"], prepared["crossed"]
            if (not is_primary and "reset-leg" not in causes and record is not first_direct):
                continue
            if stopped is None or stopped[2] <= max(confirmation, event):
                continue
            eligible.append(StructureOrder(
                physical_direction, int(entry["reaction_number"]), first, breakout,
                confirmation, as_decimal(entry["stop_level"]),
                int(entry["stop_source_index"]), int(stopped[0]), stopped[2],
                causes, as_decimal(reaction.box_top), as_decimal(reaction.box_bottom),
                reaction_mode=str(reaction.mode),
                audit_causes=tuple(deepcopy(cause) for cause in prepared["causes"]),
            ))
        return eligible


def _negate_price(value):
    """Reflect a Decimal without context rounding, including long lexemes."""
    return as_decimal(value).copy_negate()


@dataclass(frozen=True, slots=True)
class _ReflectedRow:
    original: object

    @property
    def high(self):
        return _negate_price(self.original.low)

    @property
    def low(self):
        return _negate_price(self.original.high)


class _ReflectedPriceIndex:
    """Reuse immutable original RAW indexes rather than allocate a second tree."""
    def __init__(self, original):
        self.original = original

    def first_greater(self, left, right, level):
        return self.original.first_less(left, right, _negate_price(level))

    def first_less(self, left, right, level):
        return self.original.first_greater(left, right, _negate_price(level))


class _ReflectedChronology:
    def __init__(self, original):
        self.candles = tuple(_ReflectedRow(row) for row in original.candles)
        self.seconds = tuple(_ReflectedRow(row) for row in original.seconds)
        self.times, self.second_times = original.times, original.second_times
        self.lower_index = _ReflectedPriceIndex(original.lower_index)
        self.main_index = original.main_index


def _reflect_structure_order(order):
    return replace(order,
        direction="bearish" if order.direction == "bullish" else "bullish",
        stop_level=_negate_price(order.stop_level),
        box_top=_negate_price(order.box_bottom) if order.box_bottom is not None else None,
        box_bottom=_negate_price(order.box_top) if order.box_top is not None else None)


def detect_bullish(chronology, s_zones, e_zones, stopalls, orders, *, _run=None):
    """Apply the approved bullish mirror without reversing time or native state.

    Only the primary state machine sees reflected price coordinates. Native
    Orders and callbacks see original market prices, physical identities and
    unchanged audit causes. Market candle colors and S/E families never swap.
    """
    point_cache = {}

    def cycle_id(value):
        return value.replace("bearish:cycle:", "bullish:cycle:", 1) if value else value

    def point(item):
        if id(item) not in point_cache:
            old = _run.previous.projected_points.get(id(item)) if _run and _run.previous else None
            if old is not None and old[0] is item:
                projected = old[1]
            else:
                projected = replace(item,
                    kind="PL" if item.kind == "PH" else "PH", price=_negate_price(item.price),
                    order=_reflect_structure_order(item.order), cycle_id=cycle_id(item.cycle_id),
                    identity_source=point(item.identity_source) if item.identity_source else None)
            point_cache[id(item)] = projected
            if _run is not None:
                _run.projected_points[id(item)] = item, projected
        return point_cache[id(item)]

    def status(value):
        return value.replace("ph", "__primary_high__").replace("pl", "ph").replace(
            "__primary_high__", "pl").replace("reversed-to-bullish", "reversed-to-bearish")

    def result(item):
        transition = item.transition
        return replace(item, direction="bullish", highs=[point(row) for row in item.lows],
            lows=[point(row) for row in item.highs],
            mbl=replace(item.mbl, price=_negate_price(item.mbl.price)) if item.mbl else None,
            cycle_id=cycle_id(item.cycle_id), status=status(item.status),
            post_pl3_orders=[_reflect_structure_order(row) for row in item.post_pl3_orders],
            cycles=[result(row) for row in item.cycles],
            transition=(replace(transition, level=_negate_price(transition.level),
                                high=point(transition.high), target_direction="bearish")
                        if transition else None))

    class ReflectedOrders:
        def __call__(self, kind, number, gate, event):
            actual_kind = "PL" if kind == "PH" else "PH"
            return [_reflect_structure_order(row) for row in orders(actual_kind, number, gate, event)]

        def confirm_high(self, item):
            callback = getattr(orders, "confirm_high", None)
            if callback is not None:
                callback(point(item))

    return result(detect_bearish(_ReflectedChronology(chronology), s_zones, e_zones,
                                stopalls, ReflectedOrders(), _run=_run))


class LivePrimaryContinuation:
    """Carry confirmed primary cycles and revalidate the open Order proposal."""

    def __init__(self, direction, chronology, s_zones, e_zones, stopalls, orders):
        if direction not in {"bearish", "bullish"}:
            raise ValueError("Primary continuation requires a trading direction.")
        self._detect = detect_bullish if direction == "bullish" else detect_bearish
        self._timeframe = chronology.timeframe
        self._times = chronology.times
        self._run = _PrimaryRun()
        self._result = self._detect(chronology, s_zones, e_zones, stopalls, orders, _run=self._run)

    @property
    def result(self) -> PrimaryResult:
        return self._result

    def update(self, chronology, s_zones, e_zones, stopalls, orders, *, first_dirty_event: datetime):
        """Continue with fresh Orders and the earliest revised market/Order event.

        Matching-seed changes can rewind the schedule further. Retained point
        registrations rebuild the accepted native ledger in their original
        order before any newly open proposal is evaluated.
        """
        if chronology.timeframe != self._timeframe:
            raise ValueError("Primary continuation requires the original analysis timeframe.")
        if not isinstance(first_dirty_event, datetime):
            raise TypeError("Primary continuation requires an exact changed event time.")
        frontier = first_dirty_event
        # Point and MBL source selection includes the complete decision or
        # trigger main. A later lower row in that candle can revise its price.
        for times in (self._times, chronology.times):
            index = bisect_right(times, first_dirty_event) - 1
            if index >= 0 and first_dirty_event < times[index] + self._timeframe:
                frontier = min(frontier, times[index])
        run = _PrimaryRun(self._run, frontier)
        result = self._detect(chronology, s_zones, e_zones, stopalls, orders, _run=run)
        run.previous = None
        self._run, self._result = run, result
        self._times = chronology.times
        return result
