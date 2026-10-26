"""Bearish Primary-High/Low state and the immutable matching behavior leg.

Only the bearish algorithm has been specified. Native Reaction, Reset,
dominance, physical Order identity and stop geometry remain owned by their
existing engines. No bullish primary calculation is inferred here.
"""
from __future__ import annotations

from bisect import bisect_right
from copy import deepcopy
from dataclasses import dataclass, field, replace
from datetime import datetime
from decimal import Decimal
from typing import Callable, Sequence

from core_utils import as_decimal
from lifecycle_engine import advance_dominant_behavior
from order_audit_engine import relabel_primary_causes

PL_PH_VERSION = "1.2.2"
PL_PH_LAST_MODIFIED = "2026-10-26T19:31:03+03:30"


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


def resolve_primary_highs(primary, *, through_index):
    """Resolve physical PH ownership after independent logical confirmation.

    Each candle has one final number. The greatest coincident local number
    wins; a strictly higher subsequent high continues the preceding final
    number. Logical cycle/reset states and their Order eligibility stay intact.
    Filter confirmations before reconciliation so future roles cannot rename
    an earlier requested horizon.
    """
    physical = {}
    cycle_order = {cycle.cycle_id: index for index, cycle in
                   enumerate(getattr(primary, "cycles", ()))}
    for point in primary.highs:
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
        if result and winner.price > result[-1].price:
            number = max(number, result[-1].number + 1)
        result.append(replace(winner, number=number,
                              identity_source=identity.identity_source or identity))
    return result


def relabel_primary_order(order, highs):
    """Keep frozen structure Order snapshots aligned with final PH names."""
    labels = {point.source_time: f"PH{point.number}" for point in highs}
    return replace(order, audit_causes=tuple(relabel_primary_causes(order.audit_causes, labels)))


def formed_matching_legs(primary, *, through_index):
    """A qualified candidate becomes MBL only after its first confirmed PH.

    Keep the frozen candidate internally for cancellation/Order chronology;
    neither activation alone nor a future PH confirms a leg at this horizon.
    """
    for cycle in getattr(primary, "cycles", None) or [primary]:
        if cycle.mbl is None or cycle.mbl.trigger_index > through_index:
            continue
        confirmation = min((point for point in cycle.highs
                            if point.decision_index <= through_index),
                           key=lambda point: point.decision_event_time, default=None)
        if confirmation is not None:
            yield cycle, confirmation


def resolve_stopall_ownership(stopalls, primary: PrimaryResult, *, through_index: int):
    """A confirmed PH owns its candle; retain the causal StopAll history.

    A future PH confirmation must not remove the StopAll from an earlier
    requested horizon. The supplied historical collection is never mutated.
    """
    promoted = {(point.source_index, point.source_time) for point in primary.highs
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
) -> PrimaryResult:
    """Merge independent cycles on exact chronology and one native Order ledger.

    A proposal never commits PH ownership. Only the globally earliest decision
    may mutate the native ledger; that mutation invalidates every pending
    proposal, including cycles waiting without an accepted Order.
    """
    result = PrimaryResult()
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
        crossed = strict_cross(chronology, qualification, level, True)
        if crossed is not None:
            activated.append((crossed, reference, second, qualification))
    if not activated:
        if qualified:
            result.status = "waiting-for-stopall-break"
        return result
    activated.sort(key=lambda row: (
        row[0][1], row[3], row[1].source_index, row[2].source_index,
    ))
    checkpoints = []
    pending = {}
    promoted_sources = set()
    activation_index = 0
    while True:
        for index, checkpoint in enumerate(checkpoints):
            if index not in pending:
                pending[index] = _next_point(chronology, checkpoint, orders)
        decisions = [(point.decision_event_time, index)
                     for index, (_, point) in pending.items() if point is not None]
        decision = min(decisions, default=None)
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
                continue
            checkpoints.append(_activate_cycle(chronology, activation))
            continue
        if decision is None:
            break
        _, index = decision
        checkpoint, point = pending.pop(index)
        checkpoints[index] = checkpoint
        target = checkpoint.result.highs if point.kind == "PH" else checkpoint.result.lows
        target.append(point)
        (result.highs if point.kind == "PH" else result.lows).append(point)
        if point.kind == "PH":
            promoted_sources.add((point.source_index, point.source_time))
            commit_high = getattr(orders, "confirm_high", None)
            if commit_high is not None:
                commit_high(point)
                pending.clear()

    result.cycles = [pending[index][0].result for index in range(len(checkpoints))]
    result.mbl = result.cycles[0].mbl
    result.status = result.cycles[-1].status
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


def _activate_cycle(chronology, activation):
    crossed, reference, second, qualification = activation
    result = PrimaryResult(
        cycle_id=f"bearish:cycle:{reference.source_index}:{second.source_index}",
        qualification_event_time=qualification,
    )
    reference_price = as_decimal(chronology.candles[int(reference.source_index)].high)
    gate_index, cursor = crossed
    source, floor = _extreme(chronology, int(second.source_index), gate_index, False)
    broken = strict_cross(chronology, cursor, floor, False)
    result.mbl = MatchingBehaviorLeg(
        source, chronology.times[source], floor, int(reference.source_index),
        int(second.source_index), gate_index, cursor,
        broken[0] if broken else None, broken[1] if broken else None,
    )
    return _CycleCheckpoint(result, reference_price, gate_index, cursor)


def _next_point(chronology, checkpoint, orders):
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
    # maximum PH/PL number or feedback-pass cap is part of this algorithm.
    while True:
        high_level = result.highs[-1].price if result.highs else reference_price
        low_level = result.lows[-1].price if result.lows else floor
        high_number = 1 if reset_high or not result.highs else result.highs[-1].number + 1
        low_number = result.lows[-1].number + 1 if result.lows else 1
        if phase == "seek":
            up = strict_cross(chronology, cursor, high_level, True)
            down = strict_cross(chronology, cursor, low_level, False)
            if up is None and down is None:
                result.status = "waiting-for-structure-break"
                return prospective, None
            if up and down and up[1] == down[1]:
                result.status = "ambiguous-raw-boundary-order"
                return prospective, None
            phase = "PH" if up and (down is None or up[1] < down[1]) else "PL"
            gate_index, cursor = up if phase == "PH" else down

        number = high_number if phase == "PH" else low_number
        candidates = [item for item in orders(phase, number, gate_index, cursor)
                      if order_meets_structure_gate(phase, item.first_index,
                          item.confirmation_event_time, gate_index, cursor)
                      and item.stop_event_time > item.confirmation_event_time]
        winner = min(candidates, key=lambda item: (
            item.stop_event_time, -item.first_index, item.break_index
        ), default=None)
        cancel = strict_cross(chronology, cursor,
                              floor if phase == "PH" else high_level,
                              phase == "PL")
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

    def __init__(self, chronology, groups, *, on_high=None):
        self.chronology, self.groups = chronology, groups
        self.on_high = on_high

    def confirm_high(self, point):
        """Commit PH ownership before subsequent native Order selection."""
        if self.on_high is not None:
            self.on_high(point)

    def __call__(self, kind, number, gate_index, event):
        owner = "bearish" if kind == "PH" else "bullish"
        physical_direction = self.chronology.opposite_direction(owner)
        eligible = []
        records = []
        for prepared in self.groups[owner].get("OrderAudit", ()):
            reaction, entry = prepared["reaction"], prepared["entry"]
            first, breakout = int(reaction.first_idx), int(reaction.break_idx)
            confirmation = self.chronology.reaction_confirmation(physical_direction, reaction)
            stopped = prepared["crossed"]
            causes = tuple(dict.fromkeys(cause["kind"] for cause in prepared["causes"]))
            if not order_meets_structure_gate(kind, first, confirmation, gate_index, event):
                continue
            # PL Order_A's first valid downward Reaction must be canonical.
            if kind == "PL" and int(entry["reaction_number"]) <= 0:
                continue
            if kind == "PH" and number > 1 and "parent-stop" not in causes:
                continue
            records.append((prepared, first, breakout, confirmation, causes))
        direct = [row for row in records if "parent-stop" in row[4]]
        first_direct = min(direct, key=lambda row: (row[1], row[3], row[2]), default=None)
        for record in records:
            prepared, first, breakout, confirmation, causes = record
            reaction, entry, stopped = prepared["reaction"], prepared["entry"], prepared["crossed"]
            if (kind == "PL" and "reset-leg" not in causes and record is not first_direct):
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
