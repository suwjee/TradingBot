"""StopAll detection over authoritative S/E output."""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Sequence


STOPALL_VERSION = "1.3.0"


def _d(value: object) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


@dataclass(frozen=True)
class StopAll:
    direction: str
    number: int
    source_index: int
    source_time: datetime
    price: Decimal
    decision_index: int
    decision_time: datetime
    decision_event_time: datetime
    gate_type: str
    gate_event_time: datetime
    stopped_behavior_type: str
    stopped_behavior_key: str
    stopped_behavior_count: int
    underlying_e_family: str
    underlying_e_number: int
    order_direction: str
    order_reaction_number: int
    order_mode: str
    order_causes: tuple[str, ...]
    order_parent_stop_cause_time: datetime | None
    order_reset_leg_reset_time: datetime | None
    order_reset_leg_break_time: datetime | None
    order_first_index: int
    order_first_time: datetime
    order_break_index: int
    order_break_time: datetime
    order_confirmation_time: datetime
    order_box_top: Decimal
    order_box_top_source_index: int
    order_box_top_source_time: datetime
    order_box_bottom: Decimal
    order_box_bottom_source_index: int
    order_box_bottom_source_time: datetime
    order_stop_level: Decimal
    order_stop_source_index: int
    order_stop_source_time: datetime
    stop_index: int | None
    stop_time: datetime | None
    stop_event_time: datetime | None


class StopAllDetector:
    _SEQUENCE_PRIORITY = {
        ("s", "blue"): 1,
        ("e", "blue"): 2,
        ("s", "red"): 3,
        ("e", "red"): 4,
    }

    def __init__(
        self,
        direction: str,
        s_zones: Sequence[object],
        e_zones: Sequence[object],
        candles: Sequence[object],
        lower_candles: Sequence[object],
        timeframe_seconds: int,
    ) -> None:
        if direction not in {"bullish", "bearish"}:
            raise ValueError("Direction must be 'bullish' or 'bearish'.")
        self.direction = direction
        self.s_zones = list(s_zones)
        self.e_zones = sorted(
            e_zones, key=lambda item: (item.source_time, item.source_index)
        )
        self.candles = list(candles)
        self.lower = sorted(lower_candles, key=lambda item: item.timestamp)
        self.lower_times = [item.timestamp for item in self.lower]
        self.times = [item.timestamp for item in self.candles]
        self.timeframe = timedelta(seconds=timeframe_seconds)

    def _strict_stop(
        self, start: datetime, level: Decimal
    ) -> tuple[int, datetime, datetime] | None:
        position = bisect_left(self.lower_times, start)
        for item in self.lower[position:]:
            value = _d(item.low if self.direction == "bullish" else item.high)
            if (self.direction == "bullish" and value < level) or (
                self.direction == "bearish" and value > level
            ):
                index = max(0, bisect_left(self.times, item.timestamp) - 1)
                if index + 1 < len(self.times) and self.times[index + 1] <= item.timestamp:
                    index += 1
                return index, self.times[index], item.timestamp
        return None

    @staticmethod
    def _e_key(item: object) -> tuple[str, int]:
        return str(item.family), int(item.number)

    @staticmethod
    def _dominates_e(new: tuple[str, int], old: tuple[str, int]) -> bool:
        new_family, new_number = new
        old_family, old_number = old
        if new_family == old_family:
            return new_number > old_number
        # Red is always the dominant E family. A higher-numbered Blue E must
        # not separate or replace an active Red group.
        return new_family == "red" and old_family == "blue"

    @classmethod
    def _sequence_priority(cls, kind: str, family: str) -> int:
        return cls._SEQUENCE_PRIORITY[(kind, family)]

    @classmethod
    def _active_sequence_priority(
        cls, s_key: str | None, e_key: tuple[str, int] | None,
    ) -> int:
        if e_key is not None:
            return cls._sequence_priority("e", e_key[0])
        if s_key is not None:
            return cls._sequence_priority("s", s_key)
        return 0

    def _stopall_from_e(
        self,
        item: object,
        number: int,
        gate_type: str,
        gate_event: datetime,
        behavior_type: str,
        behavior_key: str,
        behavior_count: int,
    ) -> StopAll:
        return StopAll(
            direction=self.direction,
            number=number,
            source_index=int(item.source_index),
            source_time=item.source_time,
            price=_d(item.price),
            decision_index=int(item.decision_index),
            decision_time=item.decision_time,
            decision_event_time=item.decision_event_time,
            gate_type=gate_type,
            gate_event_time=gate_event,
            stopped_behavior_type=behavior_type,
            stopped_behavior_key=behavior_key,
            stopped_behavior_count=behavior_count,
            underlying_e_family=str(item.family),
            underlying_e_number=int(item.number),
            order_direction=str(item.order_direction),
            order_reaction_number=int(item.order_reaction_number),
            order_mode=str(item.order_mode),
            order_causes=tuple(getattr(item, "order_causes", ())),
            order_parent_stop_cause_time=getattr(
                item, "order_parent_stop_cause_time", None
            ),
            order_reset_leg_reset_time=getattr(
                item, "order_reset_leg_reset_time", None
            ),
            order_reset_leg_break_time=getattr(
                item, "order_reset_leg_break_time", None
            ),
            order_first_index=int(item.order_first_index),
            order_first_time=item.order_first_time,
            order_break_index=int(item.order_break_index),
            order_break_time=item.order_break_time,
            order_confirmation_time=item.order_confirmation_time,
            order_box_top=_d(item.order_box_top),
            order_box_top_source_index=int(item.order_box_top_source_index),
            order_box_top_source_time=item.order_box_top_source_time,
            order_box_bottom=_d(item.order_box_bottom),
            order_box_bottom_source_index=int(item.order_box_bottom_source_index),
            order_box_bottom_source_time=item.order_box_bottom_source_time,
            order_stop_level=_d(item.order_stop_level),
            order_stop_source_index=int(item.order_stop_source_index),
            order_stop_source_time=item.order_stop_source_time,
            stop_index=None,
            stop_time=None,
            stop_event_time=None,
        )

    def detect(self) -> list[StopAll]:
        s_events = sorted(
            self.s_zones, key=lambda item: (item.source_time, item.source_index)
        )
        s_position = 0
        s_key: str | None = None
        s_count = 0
        e_key: tuple[str, int] | None = None
        e_count = 0
        active: list[StopAll] = []
        output: list[StopAll] = []

        for e_item in self.e_zones:
            while s_position < len(s_events) and (
                s_events[s_position].source_time < e_item.source_time
            ):
                s_item = s_events[s_position]
                color = str(s_item.color)
                incoming_priority = self._sequence_priority("s", color)
                active_priority = self._active_sequence_priority(s_key, e_key)
                if e_key is None and s_key == color:
                    s_count += 1
                elif incoming_priority > active_priority:
                    s_key, s_count = color, 1
                    e_key, e_count = None, 0
                s_position += 1

            e_decision = e_item.decision_event_time
            stopped_active = []
            for item in active:
                stop = self._strict_stop(item.decision_event_time, item.price)
                if stop is not None and stop[2] <= e_decision:
                    stopped_active.append((item, stop))
            if stopped_active:
                highest = max(item.number for item, _ in stopped_active)
                gate_event = min(stop[2] for _, stop in stopped_active)
                zone = self._stopall_from_e(
                    e_item, highest + 1, "stopall-stop", gate_event,
                    "StopAll", f"StopAll{highest}", len(stopped_active),
                )
                stopped_ids = {id(item) for item, _ in stopped_active}
                active = [item for item in active if id(item) not in stopped_ids]
                output.append(zone)
                active.append(zone)
                s_key = e_key = None
                s_count = e_count = 0
                continue

            new_key = self._e_key(e_item)
            # Once a dominant group has stopped, this E supplies the winning
            # order only. Its family/number need not match the stopped group.
            qualifies_e = e_key is not None and e_count >= 2
            qualifies_s = (
                e_key is None
                and s_key is not None
                and s_count >= 2
            )
            if qualifies_e or qualifies_s:
                parent = max(
                    (
                        item for item in (
                            self.e_zones if qualifies_e else self.s_zones
                        )
                        if item.source_time < e_item.source_time
                        and (
                            self._e_key(item) == e_key if qualifies_e
                            else str(item.color) == s_key
                        )
                    ),
                    key=lambda item: item.source_time,
                )
                gate = self._strict_stop(parent.decision_event_time, _d(parent.price))
                if gate is not None and gate[2] <= e_decision:
                    zone = self._stopall_from_e(
                        e_item, 1, "sequence-group-stop", gate[2],
                        "E" if qualifies_e else "S",
                        (
                            f"E{e_key[1]} {e_key[0]}" if qualifies_e
                            else f"S {s_key}"
                        ),
                        e_count if qualifies_e else s_count,
                    )
                    output.append(zone)
                    active.append(zone)
                    s_key = e_key = None
                    s_count = e_count = 0
                    continue

            if e_key == new_key:
                e_count += 1
            else:
                incoming_priority = self._sequence_priority("e", new_key[0])
                active_priority = self._active_sequence_priority(s_key, e_key)
                replaces_active = incoming_priority > active_priority
                advances_e = (
                    e_key is not None
                    and incoming_priority == active_priority
                    and self._dominates_e(new_key, e_key)
                )
                if replaces_active or advances_e:
                    e_key, e_count = new_key, 1
                    s_key, s_count = None, 0
            # A lower-priority Sequence event remains valid output but cannot
            # replace or separate the active dominant group.

        completed = []
        for item in output:
            stop = self._strict_stop(item.decision_event_time, item.price)
            completed.append(
                StopAll(**{
                    **item.__dict__,
                    "stop_index": stop[0] if stop else None,
                    "stop_time": stop[1] if stop else None,
                    "stop_event_time": stop[2] if stop else None,
                })
            )
        return completed


def detect_stopalls(
    direction: str,
    s_zones: Sequence[object],
    e_zones: Sequence[object],
    candles: Sequence[object],
    lower_candles: Sequence[object],
    timeframe_seconds: int,
) -> list[StopAll]:
    return StopAllDetector(
        direction, s_zones, e_zones, candles, lower_candles, timeframe_seconds
    ).detect()
