"""Calculate the fourteen chart position types from finalized indicator events."""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from decimal import Decimal
from heapq import nsmallest
from typing import Callable

from .direction_policy import policy_for
from .lifecycle_engine import sequence_priority

FOUNDATION = frozenset(("sZones", "eZones"))
TARGET_RISK_MULTIPLE = Decimal(4)
LIQUIDITY_LINE_BARS = 1500


def source_event_lookup(lower_index, from_epoch, to_epoch, timeframe):
    """Locate the first RAW occurrence of the accepted source price."""
    def find(direction, source, price):
        extreme = policy_for(direction).extreme_attr
        level = Decimal(price)
        left = bisect_left(lower_index.times, from_epoch(source))
        right = bisect_left(lower_index.times, from_epoch(source + timeframe), lo=left)
        for index in range(left, right):
            candle = lower_index.candles[index]
            if getattr(candle, extreme) == level:
                return to_epoch(candle.timestamp)
        return source

    return find


@dataclass(frozen=True, slots=True)
class PositionEvent:
    collection: str
    source_time: int
    formation_time: int
    decision_time: int
    decision_event_time: int
    closed_at: int
    price: Decimal
    verdict: str | None
    number: int
    rank: tuple[int, int] | None

    @property
    def confirmation_order(self):
        return self.decision_event_time, self.source_time


@dataclass(frozen=True, slots=True)
class PositionSetup:
    anchor: PositionEvent
    trigger: PositionEvent
    entry_price: Decimal
    stopped_at: int | None


def position_source_events(group, direction, timeframe, closed_through, source_event_at):
    """Resolve one owner per source candle, in the order used for T/F."""
    primary_key = "primaryLows" if direction == "bullish" else "primaryHighs"
    owners = {}
    for collection in (primary_key, "stopAlls", "eZones", "sZones"):
        for row in group.get(collection, ()):
            source = row["sourceTime"]
            decision = row.get("decisionTime")
            if (source in owners or source >= closed_through or decision is None
                    or row.get("calculationValid") is False):
                continue
            number = row.get("number", 0)
            rank = None
            if collection == "sZones":
                rank = sequence_priority("s", row["color"]), 0
            elif collection == "eZones":
                rank = sequence_priority("e", row["family"]), number
            raw_price = row["price"]
            formation = (source if source_event_at is None else
                         source_event_at(direction, source, raw_price))
            owners[source] = PositionEvent(
                collection, source, formation, decision, row.get("decisionEventTime") or decision,
                decision + timeframe, Decimal(raw_price), row.get("trueFalse"), number, rank,
            )
    return sorted(owners.values(), key=lambda event: event.source_time)


class PositionRules:
    """Resolve setups in one independent trend segment."""

    def __init__(self, direction, timeframe, closed_through, close_at, first_crossing):
        self.policy = policy_for(direction)
        self.timeframe = timeframe
        self.closed_through = closed_through
        self.close_at = close_at
        self.first_crossing = first_crossing
        self.buy = direction == "bullish"
        self.primary_key = "primaryLows" if self.buy else "primaryHighs"
        self.stop_events: dict[PositionEvent, int | None] = {}

    def stop_time(self, anchor):
        if anchor not in self.stop_events:
            crossed = self.first_crossing(
                self.policy.direction, anchor.formation_time, str(anchor.price),
            )
            self.stop_events[anchor] = (
                crossed if crossed is not None and crossed < self.closed_through else None
            )
        return self.stop_events[anchor]

    def setup(self, anchor, trigger):
        entry = self.close_at(trigger.decision_time)
        if entry is None:
            return None
        return PositionSetup(anchor, trigger, Decimal(entry), self.stop_time(anchor))

    def first_s(self, pairs, *, ready_at=0, before=None, strict=False):
        for anchor, signal in pairs:
            if (signal.closed_at > self.closed_through or signal.closed_at < ready_at
                    or (before is not None and signal.closed_at >= before)
                    or anchor.decision_event_time > signal.decision_event_time
                    or anchor.closed_at > signal.closed_at
                    or signal.formation_time <= anchor.formation_time
                    or self.policy.strict_cross(signal.price, anchor.price)
                    or (strict and signal.price == anchor.price)):
                continue
            stopped_at = self.stop_time(anchor)
            if stopped_at is not None and stopped_at <= signal.formation_time:
                continue
            setup = self.setup(anchor, signal)
            if setup is not None:
                return setup
        return None

    def two_stage(self, pairs_for_verdict, ready_at):
        first = self.first_s(pairs_for_verdict("T", None), ready_at=ready_at)
        if first is None:
            return None, None
        if first.stopped_at is None:
            return first, None
        second = self.first_s(
            pairs_for_verdict("F", first.stopped_at),
            ready_at=max(ready_at, first.trigger.closed_at),
        )
        return first, second

    def foundation(self, events):
        for ready_at, window in position_windows(events, {"stopAlls", self.primary_key}):
            fundamentals = [event for event in window if event.collection in FOUNDATION]
            signals = sorted((event for event in fundamentals if event.collection == "sZones"),
                             key=lambda event: event.confirmation_order)
            if not signals:
                continue
            t_anchors, f_anchors = foundation_anchors(fundamentals)

            def pairs(verdict, stopped_at):
                anchors = t_anchors if verdict == "T" else (
                    anchor for anchor in f_anchors if anchor.formation_time >= stopped_at
                )
                return foundation_pairs(signals, tuple(anchors))

            first, second = self.two_stage(pairs, ready_at)
            yield "1.1", first
            yield "1.2", second

    def stopall(self, events):
        for ready_at, window in position_windows(events, {self.primary_key}):
            owned = stopall_signal_pairs(window)

            def pairs(verdict, stopped_at):
                return ((anchor, signal) for anchor, signal in owned
                        if anchor.verdict == verdict
                        and (stopped_at is None or anchor.formation_time >= stopped_at))

            first, second = self.two_stage(pairs, ready_at)
            yield "2.1", first
            yield "2.2", second

    def primary(self, events):
        first = second = third = None
        for event in events:
            if event.collection != self.primary_key:
                continue
            if first is None and event.number == 1:
                first = event
            elif first is not None and second is None and event.number == 2:
                second = event
            elif second is not None and event.number == 3:
                third = event
                break

        if first is None:
            return
        signals = sorted(
            (event for event in events if event.collection == "sZones"
             and first.source_time < event.source_time
             and (second is None or event.source_time < second.source_time)),
            key=lambda event: event.confirmation_order,
        )
        entry_one = self.first_s(((first, signal) for signal in signals), strict=True,
                                 before=second.closed_at if second is not None else None)
        yield "3.1", entry_one
        if (second is None or second.closed_at > self.closed_through
                or first.closed_at > second.closed_at or not stopped_by(entry_one, second.closed_at)):
            return
        entry_two = self.setup(second, second)
        yield "3.2", entry_two
        if (entry_one is None and third is not None and third.closed_at <= self.closed_through
                and second.closed_at <= third.closed_at and stopped_by(entry_two, third.closed_at)):
            yield "3.3", self.setup(third, third)

    def serialize(self, number, setup):
        side = "Buy" if self.buy else "Sell"
        label = number + ("B" if self.buy else "S")
        anchor, trigger = setup.anchor, setup.trigger
        entry = setup.entry_price
        stop = anchor.price
        reward = abs(entry - stop) * TARGET_RISK_MULTIPLE
        if number.startswith("3."):
            owner = ("PL" if self.buy else "PH") + number[-1]
        else:
            owner = ("Foundation_" if number.startswith("1.") else "StopAll_") + anchor.verdict

        output = {
            "id": f"{label}:{anchor.source_time}:{trigger.source_time}",
            "type": label,
            "algorithm": f"{side}_{owner}",
            "side": side.lower(),
            "anchorSourceTime": anchor.source_time,
            "triggerSourceTime": trigger.source_time,
            "entryTime": trigger.decision_time,
            "entryPrice": str(entry),
            "stopPrice": str(stop),
            "targetPrice": str(entry + reward if self.buy else entry - reward),
        }
        if setup.stopped_at is not None:
            output["stopEventTime"] = setup.stopped_at
            if setup.stopped_at < trigger.closed_at:
                output["preEntryStop"] = True
        return output


def stopped_by(setup, time):
    return setup is None or (setup.stopped_at is not None and setup.stopped_at < time)


def position_windows(events, boundaries):
    ready_at = 0
    window = []
    for event in events:
        if event.collection in boundaries:
            if window:
                yield ready_at, window
            ready_at = event.closed_at
            window = []
        else:
            window.append(event)
    if window:
        yield ready_at, window


def foundation_anchors(events):
    t_anchors, f_anchors = [], []
    largest_rank = (0, 0)
    for event in events:
        if event.verdict == "T":
            t_anchors.append(event)
        elif event.verdict == "F" and event.rank > largest_rank:
            f_anchors.append(event)
        largest_rank = max(largest_rank, event.rank)
    return t_anchors, f_anchors


def foundation_pairs(signals, anchors):
    for signal in signals:
        for anchor in anchors:
            if anchor.source_time >= signal.source_time:
                break
            yield anchor, signal


def stopall_signal_pairs(events):
    pairs = []
    owner = None
    for event in events:
        if event.collection == "stopAlls":
            owner = event
        elif owner is not None and event.collection == "sZones":
            pairs.append((owner, event))
    return sorted(pairs, key=lambda pair: pair[1].confirmation_order)


def calculate_positions(group, close_at: Callable, first_crossing: Callable, *, direction,
                        timeframe, closed_through, source_event_at: Callable | None = None):
    """Publish positions from final T/F and confirmed trigger closes for one regime."""
    end = group.get("calculationEndTime")
    limit = closed_through if end is None else min(closed_through, end)
    rules = PositionRules(direction, timeframe, limit, close_at, first_crossing)
    events = position_source_events(group, direction, timeframe, limit, source_event_at)
    output = [
        rules.serialize(label, setup)
        for family in (rules.foundation, rules.stopall, rules.primary)
        for label, setup in family(events)
        if setup is not None
    ]
    return sorted(output, key=lambda row: (row["entryTime"], row["type"], row["anchorSourceTime"]))


def _liquidity_runs(events):
    """Group identical F anchors until a larger Foundation rank ends their run."""
    active, runs = [], []
    for index, event in enumerate(events):
        while active and active[-1][0] < event.rank:
            active.pop()
        if event.verdict != "F":
            continue
        if not active or active[-1][0] != event.rank:
            run = []
            runs.append(run)
            active.append((event.rank, run))
        active[-1][1].append(index)
    return runs


def _liquidity_triggers(events, index, direct_sweep, bullish):
    """Find closed S/E evidence in favorable source geometry before the breach."""
    anchor = events[index]
    for candidate_index in range(index + 1, len(events)):
        candidate = events[candidate_index]
        if direct_sweep is not None and candidate.formation_time >= direct_sweep:
            break
        favorable = candidate.price > anchor.price if bullish else candidate.price < anchor.price
        if favorable:
            yield max(anchor.closed_at, candidate.closed_at)


def _liquidity_line_end(times, source, direct_sweep, timeframe):
    start = bisect_left(times, source)
    if start == len(times) or times[start] != source:
        return None
    cap = start + LIQUIDITY_LINE_BARS
    if direct_sweep is not None:
        hit = bisect_right(times, direct_sweep, lo=start) - 1
        if hit <= cap:
            return times[hit]
    if cap < len(times):
        return times[cap]
    return times[-1] + (cap - len(times) + 1) * timeframe


def calculate_liquidity(group, first_crossing, *, direction, timeframe,
                        closed_through, source_event_at, candle_times):
    """Publish Foundation liquidity and its separate chart eligibility in one regime."""
    end = group.get("calculationEndTime")
    limit = closed_through if end is None else min(closed_through, end)
    events = position_source_events(group, direction, timeframe, limit, source_event_at)
    bullish = direction == "bullish"
    primary_key = "primaryLows" if bullish else "primaryHighs"
    favorable_direction = "bearish" if bullish else "bullish"
    output = []
    for _, window in position_windows(events, {"stopAlls", primary_key}):
        confirmed = [event for event in window if event.closed_at <= limit]
        for run in _liquidity_runs(confirmed):
            repeated = len(run) > 1
            group_time = confirmed[run[0]].source_time if repeated else None
            group_confirmation = (
                nsmallest(2, (confirmed[index].closed_at for index in run))[-1] if repeated else None
            )
            shared_sweep = next_formation = None
            for index in reversed(run):
                anchor = confirmed[index]
                price = str(anchor.price)
                direct = first_crossing(direction, anchor.formation_time + 1, price)
                if direct is not None and direct >= closed_through:
                    direct = None
                move = first_crossing(favorable_direction, anchor.formation_time + 1, price)
                if move is not None and (move >= limit or (direct is not None and move >= direct)):
                    move = None

                if direct is not None and (next_formation is None or direct < next_formation):
                    shared_sweep = direct if shared_sweep is None else min(direct, shared_sweep)
                collected = min((time for time in (direct, shared_sweep) if time is not None), default=None)
                next_formation = anchor.formation_time

                visible = None if group_confirmation is None else max(anchor.closed_at, group_confirmation)
                if visible != anchor.closed_at:
                    ordinary = min(_liquidity_triggers(confirmed, index, direct, bullish), default=None)
                    if ordinary is not None:
                        visible = ordinary if visible is None else min(ordinary, visible)
                if move is None and visible is None:
                    continue
                output.append({
                    "sourceTime": anchor.source_time,
                    "price": price,
                    "movementTime": move,
                    "visibleFrom": visible,
                    "repeatGroupSourceTime": group_time,
                    "directSweepTime": direct,
                    "collectedTime": collected,
                    "lineEndTime": (_liquidity_line_end(candle_times, anchor.source_time, direct, timeframe)
                                    if visible is not None else None),
                })
    return sorted(output, key=lambda row: row["sourceTime"])
