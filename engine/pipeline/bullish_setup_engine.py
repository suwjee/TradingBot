"""Calculation-owned bullish chart schematics; no order execution or trade ledger.

Native detectors retain formation, numbering and ownership. This stage consumes
their accepted immutable events and classifies the user's movement/entry rules.
"""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from functools import partial
import heapq
from operator import delitem, setitem

from core_utils import as_decimal
from lifecycle_engine import sequence_priority
from reaction_engine import LowerTimeframeIndex

SETUP_VERSION = "1.0.0"


@dataclass(slots=True)
class StopAllAssessment:
    source_index: int
    source_time: datetime
    number: int
    decision_event_time: datetime
    scope_id: str
    ignored_prefix: bool
    reference_high: Decimal
    reference_source_index: int
    status: str | None = None
    status_event_time: datetime | None = None
    reason: str = "awaiting-stop-or-successor"
    predecessor_source_indexes: tuple[int, ...] = ()


@dataclass(slots=True)
class BehaviorAssessment:
    kind: str
    source_index: int
    source_time: datetime
    decision_event_time: datetime
    anchor_source_index: int
    status: str | None = None
    status_event_time: datetime | None = None


@dataclass(frozen=True, slots=True)
class SetupAnnotation:
    id: str
    anchor_kind: str
    anchor_number: int
    anchor_source_index: int
    anchor_source_time: datetime
    anchor_decision_event_time: datetime
    cycle_id: str | None
    behavior_kind: str | None
    behavior_source_index: int | None
    behavior_source_time: datetime | None
    confirmation_event_time: datetime
    entry_index: int
    entry_time: datetime
    close_event_time: datetime
    entry_price: Decimal
    stop_price: Decimal
    target_price: Decimal
    width_bars: int = 50
    risk_reward: Decimal = Decimal(4)


@dataclass(frozen=True, slots=True)
class ReferenceBreak:
    scope_id: str
    event_time: datetime
    source_index: int
    reference_high: Decimal
    reference_source_index: int


@dataclass(slots=True)
class SetupResult:
    assessments: list[StopAllAssessment] = field(default_factory=list)
    behaviors: list[BehaviorAssessment] = field(default_factory=list)
    setups: list[SetupAnnotation] = field(default_factory=list)
    breakouts: list[ReferenceBreak] = field(default_factory=list)
    phase: str = "stopall"


@dataclass(slots=True)
class _Scope:
    identity: str
    rows: list = field(default_factory=list)
    behaviors: list = field(default_factory=list)
    parity: dict = field(default_factory=lambda: {0: None, 1: None})
    priority: int | None = None
    break_scheduled: bool = False
    blocked: bool = False


@dataclass(slots=True)
class _Movement:
    root: int
    epoch: int
    prefix: int
    reference_high: Decimal
    reference_source_index: int
    source_time: datetime
    extent: int = 0
    scopes: dict = field(default_factory=dict)


def _native_chains(stopalls, stop_times):
    """Reproduce native max-stopped ancestry, including multi-chain joins."""
    active, roots, predecessors = [], {}, {}
    for item in sorted(stopalls, key=lambda r: (r.source_time, r.source_index)):
        key = int(item.source_index)
        if int(item.number) > 1:
            consumed = [r for r in active if stop_times[r.source_index] is not None
                        and stop_times[r.source_index] <= item.decision_event_time]
            candidates = [r for r in consumed if int(r.number) == int(item.number)-1]
            parent = max(candidates, key=lambda r: (r.source_time, r.source_index), default=None)
            roots[key] = roots[parent.source_index] if parent is not None else key
            predecessors[key] = tuple(r.source_index for r in consumed)
            consumed_ids = {r.source_index for r in consumed}
            active = [r for r in active if r.source_index not in consumed_ids]
        else:
            roots[key], predecessors[key] = key, ()
            if (str(getattr(item,"donor_type","")).upper() == "S"
                    or getattr(item,"gate_type",None) == "opposite-s-group-stop"):
                active = []
        active.append(item)
    return roots, predecessors


class _SetupMarket:
    def __init__(self, chronology, through_index):
        self.chronology = chronology
        last = len(chronology.candles) - 1
        end = last if through_index is None else min(last, int(through_index))
        self.horizon = chronology.times[end] + chronology.timeframe if end >= 0 else None
        self.lower_end = bisect_left(chronology.second_times, self.horizon) if self.horizon is not None else 0

    def crossing(self, event, price, *, above=False, inclusive=False):
        chronology = self.chronology
        left = (bisect_left if inclusive else bisect_right)(chronology.second_times, event)
        if left >= self.lower_end:
            return None
        query = chronology.lower_index.first_greater if above else chronology.lower_index.first_less
        position = query(left, self.lower_end, as_decimal(price))
        return None if position is None else chronology.second_times[position]


def _setup_input_events(market, s_zones, e_zones, stopalls, primary_lows):
    horizon = market.horizon
    if horizon is None:
        return [], {}, {}, {}
    native = [r for r in stopalls if r.direction == "bullish"
              and r.decision_event_time < horizon]
    stop_times = {r.source_index: getattr(r, "stop_event_time", None)
                  or market.crossing(r.decision_event_time, r.price, inclusive=True) for r in native}
    roots, predecessors = _native_chains(native, stop_times)
    events, serial = [], 0

    def push(instant, priority, kind, item):
        nonlocal serial
        if instant is not None and instant < horizon:
            events.append((instant, priority, serial, kind, item))
            serial += 1

    for item in sorted(native, key=lambda r: (r.decision_event_time, r.source_time, r.source_index)):
        push(item.decision_event_time, 2, "stopall", item)
        push(stop_times[item.source_index], 0, "stop", item)
    for item in sorted(primary_lows, key=lambda r: (r.decision_event_time, r.source_time,
                                                   r.source_index, -int(r.number), r.cycle_id or "")):
        push(item.decision_event_time, 1, "pl", item)
    behavior_events = [(kind, r) for kind, rows in (("S", s_zones), ("E", e_zones))
                       for r in rows if getattr(r, "direction", "bullish") == "bullish"
                       and getattr(r, "calculation_valid", True)]
    for kind, item in sorted(behavior_events, key=lambda pair: (
            pair[1].decision_event_time,
            -sequence_priority(pair[0], getattr(pair[1], "color" if pair[0] == "S" else "family")),
            pair[1].source_time, pair[1].source_index, pair[0])):
        push(item.decision_event_time, 3, "behavior", (kind, item))

    return sorted(events), stop_times, roots, predecessors


class _SetupState:
    def __init__(self, *, retain=False):
        self.result = SetupResult()
        self.movements, self.states, self.seen_pl, self.pl_numbers = {}, {}, set(), {}
        self.current = self.latest_movement = self.pl_anchor = None
        self.epoch_id = self.pl_start = self.watch_number = 0
        self.watches = {}
        self.undo = [] if retain else None
        self.marks = []

    def attr(self, target, key, value):
        if self.undo is not None:
            self.undo.append(partial(setattr, target, key, getattr(target, key)))
        setattr(target, key, value)

    def put(self, target, key, value):
        if self.undo is not None:
            self.undo.append(partial(setitem, target, key, target[key]) if key in target
                             else partial(delitem, target, key))
        target[key] = value

    def remove(self, target, key):
        if self.undo is not None:
            self.undo.append(partial(setitem, target, key, target[key]))
        del target[key]

    def append(self, target, value):
        if self.undo is not None:
            self.undo.append(target.pop)
        target.append(value)

    def add(self, target, value):
        if self.undo is not None:
            self.undo.append(partial(target.remove, value))
        target.add(value)

    def rewind(self, frontier):
        position = bisect_left(self.marks, frontier, key=lambda mark: mark[0])
        if position < len(self.marks):
            undo_position = self.marks[position][1]
            for reverse in reversed(self.undo[undo_position:]):
                reverse()
            del self.undo[undo_position:]
            del self.marks[position:]


def _run_setup_events(market, state, inputs, *, frontier=None):
    chronology = market.chronology
    result = state.result
    external, stop_times, roots, predecessors = inputs
    events = [event for event in external if frontier is None or event[0] >= frontier]
    heapq.heapify(events)
    # All static events retain priority over later-created watches on a tie.
    watch_offset = len(external)
    main_prices = None

    def queue_watch(number, watch):
        instant, level, kind, item = watch
        crossing = market.crossing(instant, level, above=kind == "break")
        if crossing is not None:
            heapq.heappush(events, (crossing, 4 if kind == "break" else 0,
                                    watch_offset + number, kind, (number, item)))

    for number, watch in state.watches.items():
        queue_watch(number, watch)

    def watch(instant, level, kind, item):
        number = state.watch_number
        state.attr(state, "watch_number", number + 1)
        event = (instant, level, kind, item)
        state.put(state.watches, number, event)
        queue_watch(number, event)

    def enter(anchor, anchor_kind, instant, behavior=None):
        if anchor.get("entered"):
            return
        state.put(anchor, "entered", True)
        item = anchor["item"]
        index = chronology.main_index(instant, clamp=True)
        candle = chronology.candles[index]
        entry, stop = as_decimal(candle.close), as_decimal(item.price)
        if entry <= stop:
            return
        state.attr(result, "phase", "pl" if anchor_kind == "PL" else "stopall")
        kind, source = behavior if behavior is not None else (None, None)
        identity = f"bullish:setup:{anchor_kind}:{item.source_time.isoformat()}:{item.decision_event_time.isoformat()}"
        state.append(result.setups, SetupAnnotation(identity, anchor_kind, int(item.number),
            int(item.source_index), item.source_time, item.decision_event_time,
            getattr(item, "cycle_id", None), kind,
            int(source.source_index) if source else None, source.source_time if source else None,
            instant, index, candle.timestamp, candle.timestamp + chronology.timeframe,
            entry, stop, entry + Decimal(4)*(entry-stop)))

    def classify(anchor, status, instant, reason):
        row, scope, movement = anchor["row"], anchor["scope"], anchor["movement"]
        parity = row.number % 2
        if status == "F":
            state.put(scope.parity, parity, "F")
            for other in scope.rows:
                if other.number % 2 == parity:
                    state.attr(other, "status", "F")
                    state.attr(other, "status_event_time", instant)
                    state.attr(other, "reason", reason if other is row else "inherited-parity-failure")
            for owner_parity, behavior in scope.behaviors:
                if owner_parity == parity:
                    state.attr(behavior, "status", "F")
                    state.attr(behavior, "status_event_time", instant)
            if scope.priority == parity:
                state.attr(scope, "priority", 1-parity if scope.parity[1-parity] == "T" else None)
            if all(value == "F" for value in scope.parity.values()) and not scope.break_scheduled:
                state.attr(scope, "break_scheduled", True)
                if not row.ignored_prefix and movement.epoch == state.epoch_id:
                    watch(instant, movement.reference_high, "break", (scope, movement))
        else:
            if scope.parity[parity] != "F":
                state.put(scope.parity, parity, "T")
                state.attr(row, "status", "T")
                state.attr(row, "status_event_time", instant)
                state.attr(row, "reason", reason)
                if scope.priority is None:
                    state.attr(scope, "priority", parity)

    def stop(anchor, instant):
        state.put(anchor, "stopped", True)
        if anchor["retired"] or anchor["row"].status == "F":
            return
        classify(anchor, "F" if anchor["had_behavior"] else "T", instant,
                 "behavior-then-stop" if anchor["had_behavior"] else "stop-without-behavior")

    while events:
        instant, _, _, kind, item = heapq.heappop(events)
        if state.undo is not None:
            state.marks.append((instant, len(state.undo)))
        if kind in {"pl-stop", "break"}:
            number, item = item
            state.remove(state.watches, number)
        current, pl_anchor = state.current, state.pl_anchor
        if kind == "stop":
            if item.source_index in state.states:
                stop(state.states[item.source_index], instant)
        elif kind == "pl-stop":
            if pl_anchor is not None and pl_anchor["item"] is item:
                state.put(pl_anchor, "stopped", True)
        elif kind == "break":
            scope, movement = item
            if movement.epoch == state.epoch_id and not scope.blocked:
                state.attr(scope, "blocked", True)
                state.attr(result, "phase", "waiting-for-larger-movement")
                state.append(result.breakouts, ReferenceBreak(scope.identity, instant,
                    chronology.main_index(instant, clamp=True), movement.reference_high,
                    movement.reference_source_index))
        elif kind == "pl":
            physical = (item.source_index, item.source_time)
            cycle = getattr(item, "cycle_id", None)
            if physical in state.seen_pl or int(item.number) <= state.pl_numbers.get(cycle, 0):
                continue
            state.add(state.seen_pl, physical)
            state.put(state.pl_numbers, cycle, int(item.number))
            state.attr(state, "epoch_id", state.epoch_id + 1)
            state.attr(state, "pl_start", chronology.main_index(instant, clamp=True))
            state.attr(state, "pl_anchor", {"item": item, "entered": False, "stopped": False})
            state.attr(state, "current", None)
            state.attr(state, "latest_movement", None)
            state.attr(result, "phase", "pl")
            watch(instant, item.price, "pl-stop", item)
        elif kind == "stopall":
            if current is not None and not current["stopped"] and not current["retired"]:
                old_stop = stop_times.get(current["item"].source_index)
                if old_stop is None or instant < old_stop:
                    classify(current, "T", instant, "successor-before-stop")
                    state.put(current, "retired", True)
            root = roots[item.source_index]
            movement = state.movements.get(root)
            if movement is None:
                latest = state.latest_movement
                prefix = latest.extent if latest is not None else 0
                if main_prices is None:
                    main_prices = LowerTimeframeIndex(chronology.candles)
                high, source = main_prices.range_maximum(state.pl_start,
                    chronology.main_index(instant, clamp=True)+1)
                movement = _Movement(root, state.epoch_id, prefix, high, source, item.source_time)
                state.put(state.movements, root, movement)
                state.attr(state, "latest_movement", movement)
            state.attr(movement, "extent", max(movement.extent, int(item.number)))
            ignored = int(item.number) <= movement.prefix
            scope = movement.scopes.get(ignored)
            if scope is None:
                suffix = "prefix" if ignored else "candidate"
                scope = _Scope(f"bullish:setup-scope:{movement.source_time.isoformat()}:{suffix}")
                state.put(movement.scopes, ignored, scope)
            row = StopAllAssessment(item.source_index, item.source_time, int(item.number),
                instant, scope.identity, ignored, movement.reference_high,
                movement.reference_source_index, predecessor_source_indexes=predecessors[item.source_index])
            state.append(scope.rows, row)
            state.append(result.assessments, row)
            current = {"item": item, "row": row, "scope": scope, "movement": movement,
                       "had_behavior": False, "stopped": False, "retired": False, "entered": False}
            state.put(state.states, item.source_index, current)
            state.attr(state, "current", current)
            if scope.parity[row.number % 2] == "F":
                state.attr(row, "status", "F")
                state.attr(row, "status_event_time", instant)
                state.attr(row, "reason", "inherited-parity-failure")
            native_stop = stop_times[item.source_index]
            if native_stop is not None and native_stop <= instant:
                stop(current, instant)
            first = state.states.get(root)
            if (row.number == 2 and movement.prefix == 0 and first is not None
                    and first["had_behavior"] and first["row"].reason == "behavior-then-stop"
                    and movement.epoch == state.epoch_id
                    and not scope.blocked and not (pl_anchor and not pl_anchor["entered"])
                    and not current["stopped"]):
                state.attr(scope, "priority", 0)
                enter(current, "StopAll", instant)
        else:
            behavior_kind, behavior = item
            pl_entry = False
            if pl_anchor and not pl_anchor["entered"] and not pl_anchor["stopped"]:
                if instant > pl_anchor["item"].decision_event_time:
                    enter(pl_anchor, "PL", instant, item)
                    pl_entry = True
            if current is None or current["stopped"] or current["retired"]:
                continue
            anchor, row, scope = current["item"], current["row"], current["scope"]
            if instant <= anchor.decision_event_time:
                continue
            first_behavior = not current["had_behavior"]
            state.put(current, "had_behavior", True)
            record = BehaviorAssessment(behavior_kind, behavior.source_index, behavior.source_time,
                                        instant, anchor.source_index)
            if row.status == "F":
                record.status, record.status_event_time = "F", instant
            state.append(result.behaviors, record)
            parity = row.number % 2
            state.append(scope.behaviors, (parity, record))
            initial = row.number == 1 and current["movement"].prefix == 0
            allowed = scope.parity[parity] != "F" and (initial or
                (scope.parity[parity] == "T" and scope.priority == parity))
            if (first_behavior and not pl_entry and allowed and not row.ignored_prefix and not scope.blocked
                    and current["movement"].epoch == state.epoch_id):
                if scope.priority is None:
                    state.attr(scope, "priority", parity)
                enter(current, "StopAll", instant, item)


def calculate_bullish_setups(chronology, s_zones, e_zones, stopalls, primary_lows,
                             *, through_index=None):
    """Evaluate complete accepted history up to an inclusive main-candle horizon."""
    market = _SetupMarket(chronology, through_index)
    state = _SetupState()
    inputs = _setup_input_events(market, s_zones, e_zones, stopalls, primary_lows)
    _run_setup_events(market, state, inputs)
    return state.result


def _setup_event_keys(inputs):
    events, _, roots, predecessors = inputs
    keys = []
    for instant, priority, _, kind, item in events:
        behavior = None
        if kind == "behavior":
            behavior, item = item
        geometry = (item.source_index, item.source_time, item.decision_event_time)
        if kind == "stopall":
            geometry += (int(item.number), str(item.price), roots[item.source_index],
                         predecessors[item.source_index])
        elif kind == "pl":
            geometry += (int(item.number), str(item.price), getattr(item, "cycle_id", None))
        keys.append((instant, priority, kind, behavior, geometry))
    return keys


class LiveBullishSetupContinuation:
    """Keep movement state, parity assessments and pending strict watches."""

    def __init__(self, chronology, s_zones, e_zones, stopalls, primary_lows, *, through_index=None):
        self._state = _SetupState(retain=True)
        market = _SetupMarket(chronology, through_index)
        inputs = _setup_input_events(market, s_zones, e_zones, stopalls, primary_lows)
        self._timeframe = chronology.timeframe
        self._horizon = market.horizon
        self._keys = _setup_event_keys(inputs)
        _run_setup_events(market, self._state, inputs)

    @property
    def result(self):
        return deepcopy(self._state.result)

    def update(self, chronology, s_zones, e_zones, stopalls, primary_lows,
               *, first_dirty_event: datetime, through_index=None):
        if chronology.timeframe != self._timeframe:
            raise ValueError("Setup continuation requires the original analysis timeframe.")
        market = _SetupMarket(chronology, through_index)
        inputs = _setup_input_events(market, s_zones, e_zones, stopalls, primary_lows)
        keys = _setup_event_keys(inputs)
        frontier = first_dirty_event
        owner = bisect_right(chronology.times, frontier) - 1
        if owner >= 0 and frontier < chronology.times[owner] + chronology.timeframe:
            frontier = chronology.times[owner]
        if self._horizon is not None:
            frontier = min(frontier, self._horizon)
        if market.horizon is not None:
            frontier = min(frontier, market.horizon)
        for index in range(max(len(self._keys), len(keys))):
            before = self._keys[index] if index < len(self._keys) else None
            after = keys[index] if index < len(keys) else None
            if before != after:
                frontier = min(frontier, *(key[0] for key in (before, after) if key is not None))
                break
        self._state.rewind(frontier)
        _run_setup_events(market, self._state, inputs, frontier=frontier)
        self._keys, self._horizon = keys, market.horizon
        return self.result
