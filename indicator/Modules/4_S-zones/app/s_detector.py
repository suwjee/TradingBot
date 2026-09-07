"""Exact S detection over authoritative Reaction and A output."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable, Sequence


S_VERSION = "4.1.2"


@dataclass(frozen=True)
class SZone:
    direction: str
    color: str
    formation_type: str
    a_ordinal: int
    a_source_index: int
    a_source_time: datetime
    a_price: Decimal
    a_stop_index: int
    a_stop_time: datetime
    a_stop_event_time: datetime
    order_direction: str | None
    order_reaction_number: int | None
    order_mode: str | None
    order_first_index: int | None
    order_first_time: datetime | None
    order_break_index: int | None
    order_break_time: datetime | None
    order_confirmation_time: datetime | None
    order_box_top: Decimal | None
    order_box_top_source_index: int | None
    order_box_top_source_time: datetime | None
    order_box_bottom: Decimal | None
    order_box_bottom_source_index: int | None
    order_box_bottom_source_time: datetime | None
    order_stop_level: Decimal | None
    order_stop_source_index: int | None
    order_stop_source_time: datetime | None
    reset_reaction_number: int | None
    reset_time: datetime | None
    source_index: int
    source_time: datetime
    price: Decimal
    decision_index: int
    decision_time: datetime
    decision_event_time: datetime


def _decimal(value: object) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


class SDetector:
    def __init__(
        self,
        direction: str,
        trend_reactions: Sequence[object],
        opposite_reactions: Sequence[object],
        trend_blue_lines: Sequence[object],
        a_zones: Sequence[object],
        candles: Sequence[object],
        lower_candles: Sequence[object],
        timeframe_seconds: int,
        start_index: int | None = None,
        end_index: int | None = None,
        opposite_resets: Sequence[object] = (),
        initial_order_geometry: Callable[[int, datetime, int], object | None] | None = None,
    ) -> None:
        if direction not in {"bullish", "bearish"}:
            raise ValueError("Direction must be 'bullish' or 'bearish'.")
        if timeframe_seconds < 1:
            raise ValueError("Timeframe must be at least one second.")
        self.direction = direction
        self.order_direction = "bearish" if direction == "bullish" else "bullish"
        self.trend_reactions = list(trend_reactions)
        self.opposite_reactions = list(opposite_reactions)
        self.opposite_resets = list(opposite_resets)
        self.initial_order_geometry = initial_order_geometry
        self.trend_blue_lines = list(trend_blue_lines)
        self.a_zones = sorted(
            a_zones,
            key=lambda item: (
                getattr(item, "reaction_break_time"),
                int(getattr(item, "source_index")),
            ),
        )
        self.candles = list(candles)
        self.lower = sorted(
            lower_candles, key=lambda item: getattr(item, "timestamp")
        )
        self.timeframe = timedelta(seconds=timeframe_seconds)
        self.candle_times = [getattr(item, "timestamp") for item in self.candles]
        self.lower_times = [getattr(item, "timestamp") for item in self.lower]
        self.start_index = 0 if start_index is None else int(start_index)
        self.end_index = (
            len(self.candles) - 1 if end_index is None else int(end_index)
        )
        if not 0 <= self.start_index <= self.end_index < len(self.candles):
            raise ValueError("Invalid S analysis range.")
        self.range_start = self.candle_times[self.start_index]
        self.range_end = self.candle_times[self.end_index] + self.timeframe
        self.order_audit: dict[tuple[int, int], dict[str, object]] = {}
        # A strict A stop reserves its continuation for S, including a race
        # that has no order or decision yet. A decided S reopens at its source.
        self.a_ownership_windows: list[tuple[datetime, datetime | None]] = []
        self._reset_blue_formation_by_reaction: dict[int, datetime] = {}
        self._reset_time_cache: dict[int, datetime] = {}
        self._opposite_by_first_index = {
            int(getattr(item, "first_idx")): (number, item)
            for number, item in enumerate(self.opposite_reactions, start=1)
        }

        for line in self.trend_blue_lines:
            if not bool(getattr(line, "calculation_valid", True)):
                continue
            if str(getattr(line, "kind")) != "reset":
                continue
            reaction_number = int(getattr(line, "reaction_number"))
            if reaction_number not in self._reset_blue_formation_by_reaction:
                self._reset_blue_formation_by_reaction[reaction_number] = (
                    self._blue_formation_time(line)
                )

    def _main_index(self, timestamp: datetime) -> int:
        index = bisect_right(self.candle_times, timestamp) - 1
        if index < 0:
            raise ValueError("Lower-timeframe event precedes the main candles.")
        return index

    def _lower_window(
        self, start: datetime, end: datetime | None
    ) -> list[object]:
        left = bisect_left(self.lower_times, start)
        right = len(self.lower) if end is None else bisect_left(self.lower_times, end)
        return self.lower[left:right]

    def _reaction_confirmation_time(
        self, reaction: object, direction: str
    ) -> datetime:
        break_index = int(getattr(reaction, "break_idx"))
        break_candle = self.candles[break_index]
        candle_start = getattr(break_candle, "timestamp")
        start = getattr(reaction, "intrabar_start", None) or candle_start
        if start < candle_start or start >= candle_start + self.timeframe:
            start = candle_start
        end = candle_start + self.timeframe
        level = _decimal(
            getattr(reaction, "box_top" if direction == "bullish" else "box_bottom")
        )
        for item in self._lower_window(start, end):
            value = _decimal(
                getattr(item, "high" if direction == "bullish" else "low")
            )
            if (direction == "bullish" and value > level) or (
                direction == "bearish" and value < level
            ):
                return getattr(item, "timestamp")
        return candle_start

    def _reset_time(self, reset: object) -> datetime:
        key = id(reset)
        cached = self._reset_time_cache.get(key)
        if cached is not None:
            return cached
        second = getattr(reset, "second_time", None)
        if second:
            result = datetime.strptime(second, "%Y-%m-%d %H:%M:%S")
        else:
            display = getattr(reset, "display_time", None)
            result = (
                datetime.strptime(display, "%Y-%m-%d %H:%M:%S")
                if display
                else getattr(reset, "timestamp")
            )
        self._reset_time_cache[key] = result
        return result

    def _a_confirmation_time(self, zone: object) -> datetime:
        number = int(getattr(zone, "reaction_number"))
        if number < 1 or number > len(self.trend_reactions):
            raise ValueError("A refers to a missing trend reaction.")
        return self._reaction_confirmation_time(
            self.trend_reactions[number - 1], self.direction
        )

    def _trend_extreme(self, candle: object) -> Decimal:
        return _decimal(
            getattr(candle, "low" if self.direction == "bullish" else "high")
        )

    def _a_stopped(self, value: Decimal, level: Decimal) -> bool:
        return value < level if self.direction == "bullish" else value > level

    def _first_a_stop(
        self, level: Decimal, start: datetime
    ) -> tuple[int, datetime, datetime] | None:
        lower_items = self._lower_window(max(start, self.range_start), self.range_end)
        for item in lower_items:
            if self._a_stopped(self._trend_extreme(item), level):
                event_time = getattr(item, "timestamp")
                index = self._main_index(event_time)
                return index, getattr(self.candles[index], "timestamp"), event_time
        if lower_items:
            return None
        start_index = max(self.start_index, bisect_left(self.candle_times, start))
        for item in self.candles[start_index : self.end_index + 1]:
            if self._a_stopped(self._trend_extreme(item), level):
                return (
                    int(getattr(item, "index")),
                    getattr(item, "timestamp"),
                    getattr(item, "timestamp"),
                )
        return None

    def _first_order_after(
        self, a_stop_event_time: datetime
    ) -> tuple[int, object, datetime] | None:
        for number, reaction in enumerate(self.opposite_reactions, start=1):
            first_index = int(getattr(reaction, "first_idx"))
            first_time = getattr(self.candles[first_index], "timestamp")
            if first_time <= a_stop_event_time:
                # A canonical continuation can reuse the candle whose prior
                # confirmation stopped A. Its ordinary order starts a fresh
                # behavioral context; the global predecessor is not its order.
                if (
                    self.initial_order_geometry is not None
                    and number > 1
                    and first_index == self._main_index(a_stop_event_time)
                    and getattr(reaction, "intrabar_start", None) is not None
                    and int(getattr(self.opposite_reactions[number - 2], "break_idx"))
                    == first_index
                    and self._reaction_confirmation_time(
                        self.opposite_reactions[number - 2], self.order_direction
                    ) == a_stop_event_time
                ):
                    order = self.initial_order_geometry(
                        first_index, a_stop_event_time, self.end_index
                    )
                    if order is None:
                        return None
                    confirmation = self._reaction_confirmation_time(order, self.order_direction)
                    if confirmation <= a_stop_event_time:
                        raise ValueError("Initial order must confirm after the exact A stop.")
                    ordinal = next((
                        ordinal for ordinal, item in enumerate(self.opposite_reactions, 1)
                        if (int(getattr(item, "first_idx")), int(getattr(item, "break_idx")))
                        == (int(getattr(order, "first_idx")), int(getattr(order, "break_idx")))
                    ), 0)
                    return ordinal, order, confirmation
                continue
            confirmation = self._reaction_confirmation_time(
                reaction, self.order_direction
            )
            if confirmation > a_stop_event_time:
                return number, reaction, confirmation
        return None

    def _candidate_source(
        self, start_index: int, end_index: int
    ) -> tuple[int, datetime, Decimal]:
        if end_index < start_index:
            raise ValueError("S candidate range ends before the A stop.")
        source = self.candles[start_index]
        value = self._trend_extreme(source)
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = self._trend_extreme(item)
            better = (
                candidate < value
                if self.direction == "bullish"
                else candidate > value
            )
            if better:
                source = item
                value = candidate
        return int(getattr(source, "index")), getattr(source, "timestamp"), value

    def _candidate_source_last(
        self, start_index: int, end_index: int
    ) -> tuple[int, datetime, Decimal]:
        """Return the directional extreme, assigning equality to the last candle."""
        if end_index < start_index:
            raise ValueError("S candidate range ends before it starts.")
        source = self.candles[start_index]
        value = self._trend_extreme(source)
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = self._trend_extreme(item)
            better_or_equal = (
                candidate <= value
                if self.direction == "bullish"
                else candidate >= value
            )
            if better_or_equal:
                source = item
                value = candidate
        return int(getattr(source, "index")), getattr(source, "timestamp"), value

    def _first_trend_reaction_after_order(
        self, order_confirmation_time: datetime
    ) -> tuple[int, object, datetime] | None:
        for number, reaction in enumerate(self.trend_reactions, start=1):
            confirmation = self._reaction_confirmation_time(
                reaction, self.direction
            )
            if confirmation > order_confirmation_time:
                return number, reaction, confirmation
        return None

    def _first_trend_reaction_after_stop(
        self, stop_event_time: datetime
    ) -> tuple[int, object, datetime] | None:
        """Find the aligned reaction after the A stop.

        In the pre-order candidate case the aligned reaction may be fully
        confirmed before the opposite order reaction itself is confirmed.
        It still owns the candidate-side Blue validation.
        """
        for number, reaction in enumerate(self.trend_reactions, start=1):
            confirmation = self._reaction_confirmation_time(
                reaction, self.direction
            )
            if confirmation > stop_event_time:
                return number, reaction, confirmation
        return None

    def _nested_trend_reaction(
        self, order: object, order_confirmation_time: datetime
    ) -> tuple[int, object, datetime] | None:
        order_first_index = int(getattr(order, "first_idx"))
        order_break_index = int(getattr(order, "break_idx"))
        order_first = getattr(self.candles[order_first_index], "timestamp")
        order_top = _decimal(getattr(order, "box_top"))
        order_bottom = _decimal(getattr(order, "box_bottom"))
        for number, reaction in enumerate(self.trend_reactions, start=1):
            first_index = int(getattr(reaction, "first_idx"))
            break_index = int(getattr(reaction, "break_idx"))
            first = getattr(self.candles[first_index], "timestamp")
            if (
                first <= order_first
                or first_index <= order_first_index
                or break_index > order_break_index
                or first >= order_confirmation_time
            ):
                continue
            confirmation = self._reaction_confirmation_time(
                reaction, self.direction
            )
            wholly_inside = (
                _decimal(getattr(reaction, "box_top")) <= order_top
                and _decimal(getattr(reaction, "box_bottom")) >= order_bottom
            )
            if confirmation <= order_confirmation_time and wholly_inside:
                return number, reaction, confirmation
        return None

    def _simple_candidate(
        self, order: object, reaction: object
    ) -> tuple[int, datetime, Decimal]:
        """Use the inclusive order-Break to aligned-Break interval."""
        return self._candidate_source_last(
            int(getattr(order, "break_idx")),
            int(getattr(reaction, "break_idx")),
        )

    def _type3_reset_leg(
        self, reset: object
    ) -> tuple[int, datetime, Decimal] | None:
        """Return Order_B-equivalent inclusive Break-to-Reset geometry."""
        owner_match = self._opposite_by_first_index.get(
            int(getattr(reset, "from_first_idx"))
        )
        if owner_match is None:
            return None
        _, owner = owner_match
        start_index = int(getattr(owner, "break_idx"))
        end_index = self._main_index(self._reset_time(reset))
        if end_index < start_index:
            return None
        return self._candidate_source_last(start_index, end_index)

    def _type3_has_trend_reaction(
        self, a_stop_event: datetime, crossing: datetime
    ) -> bool:
        return any(
            a_stop_event
            < self._reaction_confirmation_time(reaction, self.direction)
            <= crossing
            for reaction in self.trend_reactions
        )

    def _first_type3(
        self,
        a_stop_event: datetime,
        deadline: datetime,
    ) -> tuple[int, datetime, Decimal, int, datetime, int, datetime, datetime] | None:
        """Find the first no-order Reset-leg S decision before a new order."""
        reset_times_by_owner: dict[int, list[datetime]] = {}
        for reset in self.opposite_resets:
            reset_times_by_owner.setdefault(
                int(getattr(reset, "from_first_idx")), []
            ).append(self._reset_time(reset))

        eligible: set[int] = set()
        for reaction in self.opposite_reactions:
            first_index = int(getattr(reaction, "first_idx"))
            confirmation = self._reaction_confirmation_time(
                reaction, self.order_direction
            )
            # A reaction whose Breakout and the A stop share the finest
            # available candle is already the pre-stop owner: its confirmation
            # threshold is crossed before the slightly deeper A-stop level in
            # the accepted Type-3 geometry.
            if confirmation > a_stop_event:
                continue
            if any(
                reset_time <= a_stop_event
                for reset_time in reset_times_by_owner.get(first_index, [])
            ):
                continue
            eligible.add(first_index)

        winner = None
        for reset in sorted(self.opposite_resets, key=self._reset_time):
            owner_first = int(getattr(reset, "from_first_idx"))
            reset_time = self._reset_time(reset)
            if (
                owner_first not in eligible
                or reset_time <= a_stop_event
                or reset_time >= deadline
            ):
                continue
            leg = self._type3_reset_leg(reset)
            if leg is None:
                continue
            source_index, source_time, boundary = leg
            crossing = None
            for item in self._lower_window(reset_time, deadline):
                if self._candidate_crossed(item, boundary):
                    crossing = getattr(item, "timestamp")
                    break
            if crossing is None:
                continue
            if not self._type3_has_trend_reaction(a_stop_event, crossing):
                continue
            decision_index = self._main_index(crossing)
            owner_number = self._opposite_by_first_index[owner_first][0]
            candidate = (
                source_index,
                source_time,
                boundary,
                decision_index,
                getattr(self.candles[decision_index], "timestamp"),
                owner_number,
                reset_time,
                crossing,
            )
            if winner is None or candidate[-1] < winner[-1]:
                winner = candidate
        return winner

    def _candidate_for_trend_reaction(
        self,
        order_confirmation_time: datetime,
        reaction: object,
        fallback_start_index: int,
    ) -> tuple[int, datetime, Decimal]:
        anchor_value = getattr(reaction, "anchor_value", None)
        anchor_index = getattr(reaction, "anchor_idx", None)
        if anchor_value is not None and anchor_index is not None:
            source = self.candles[int(anchor_index)]
            return (
                int(anchor_index),
                getattr(source, "timestamp"),
                _decimal(anchor_value),
            )
        first_index = int(getattr(reaction, "first_idx"))
        start_index = max(self.start_index, min(fallback_start_index, first_index))
        return self._candidate_source(start_index, first_index)

    def _candidate_after_order(
        self,
        order_confirmation_time: datetime,
        reaction: object,
    ) -> tuple[int, datetime, Decimal]:
        """Find a candidate strictly after the order is confirmed.

        A reaction anchor is authoritative only when it is also after the
        order confirmation.  Otherwise the earliest extreme in the candles
        following the confirmation through the reaction First owns the
        candidate.
        """
        first_index = int(getattr(reaction, "first_idx"))
        start_index = bisect_left(self.candle_times, order_confirmation_time)
        start_index = max(self.start_index, min(start_index, first_index))
        anchor_index = getattr(reaction, "anchor_idx", None)
        anchor_value = getattr(reaction, "anchor_value", None)
        if anchor_index is not None and int(anchor_index) >= start_index:
            source = self.candles[int(anchor_index)]
            return (
                int(anchor_index),
                getattr(source, "timestamp"),
                _decimal(anchor_value),
            )
        candidate = self._candidate_source(start_index, first_index)
        containing_index = self._main_index(order_confirmation_time)
        if containing_index < start_index:
            # Do not discard the valid remainder of an intrabar confirmation
            # candle, or import an extreme that occurred before confirmation.
            remainder = self._lower_window(
                order_confirmation_time,
                self.candle_times[containing_index] + self.timeframe,
            )
            for item in remainder:
                value = self._trend_extreme(item)
                if self._a_stopped(value, candidate[2]) or value == candidate[2]:
                    candidate = (
                        containing_index, self.candle_times[containing_index], value
                    )
        return candidate

    def _a_source_event_time(self, zone: object) -> datetime:
        """Locate the source extreme, including an A-stop main candle."""
        source = getattr(zone, "source_time")
        price = _decimal(getattr(zone, "price"))
        for item in self._lower_window(source, source + self.timeframe):
            if self._trend_extreme(item) == price:
                return getattr(item, "timestamp")
        return source

    def _a_owned_by_s(self, zone: object) -> bool:
        event_time = self._a_source_event_time(zone)
        return any(
            start <= event_time and (end is None or event_time < end)
            for start, end in self.a_ownership_windows
        )

    @property
    def eligible_a_zones(self) -> list[object]:
        """A candidates outside stopped-parent S ownership, before rendering."""
        return [zone for zone in self.a_zones if not self._a_owned_by_s(zone)]

    def _candidate_timing(
        self,
        a_stop_index: int,
        order: object,
        order_confirmation_time: datetime,
    ) -> str:
        """Return whether the candidate is formed before or after the order.

        Equality belongs to the after-order case. A strict penetration of the
        A-stop candle extreme is required before the candidate may belong to
        the pre-order leg.
        """
        stop_extreme = self._trend_extreme(self.candles[a_stop_index])
        boundary = _decimal(
            getattr(
                order,
                "box_bottom" if self.direction == "bullish" else "box_top",
            )
        )
        if self.direction == "bullish":
            return "after" if boundary <= stop_extreme else "before"
        return "after" if boundary >= stop_extreme else "before"

    def _candidate_before_order(
        self,
        a_stop_index: int,
        order: object,
        a_stop_event_time: datetime | None = None,
    ) -> tuple[int, datetime, Decimal]:
        """Use the lowest/highest leg extreme from A-stop through order First."""
        if a_stop_event_time is None:
            a_stop_event_time = self.candle_times[a_stop_index]
        first_index = int(getattr(order, "first_idx"))
        candidate = self._candidate_source(a_stop_index, first_index)
        stop_candle_end = self.candle_times[a_stop_index] + self.timeframe
        eligible_stop_remainder = self._lower_window(
            a_stop_event_time, stop_candle_end
        )
        if not eligible_stop_remainder:
            return candidate
        source = eligible_stop_remainder[0]
        value = self._trend_extreme(source)
        for item in eligible_stop_remainder[1:]:
            item_value = self._trend_extreme(item)
            better = (
                item_value < value
                if self.direction == "bullish"
                else item_value > value
            )
            if better:
                source = item
                value = item_value
        later_candidate = (
            self._candidate_source(a_stop_index + 1, first_index)
            if first_index > a_stop_index
            else None
        )
        if later_candidate is not None:
            better = (
                later_candidate[2] < value
                if self.direction == "bullish"
                else later_candidate[2] > value
            )
            if better:
                return later_candidate
        return a_stop_index, self.candle_times[a_stop_index], value

    def _candidate_event_time(
        self,
        source_index: int,
        level: Decimal,
        not_before: datetime,
    ) -> datetime:
        """Return the first lower-timeframe event that forms the candidate."""
        source_time = self.candle_times[source_index]
        for item in self._lower_window(
            max(source_time, not_before), source_time + self.timeframe
        ):
            if self._trend_extreme(item) == level:
                return getattr(item, "timestamp")
        return max(source_time, not_before)

    def _blue_formation_time(self, line: object) -> datetime:
        explicit = getattr(line, "formation_time", None)
        if explicit is not None:
            return explicit
        source_index = int(getattr(line, "source_index"))
        source_time = getattr(self.candles[source_index], "timestamp")
        if str(getattr(line, "kind")) != "reset":
            reaction_number = int(getattr(line, "reaction_number"))
            if 1 <= reaction_number <= len(self.trend_reactions):
                return self._reaction_confirmation_time(
                    self.trend_reactions[reaction_number - 1], self.direction
                )
            return source_time
        broken_level = getattr(line, "broken_level", None)
        if broken_level is None:
            return source_time
        end = source_time + self.timeframe
        for item in self._lower_window(source_time, end):
            value = _decimal(
                getattr(item, "low" if self.direction == "bullish" else "high")
            )
            crossed = (
                value < _decimal(broken_level)
                if self.direction == "bullish"
                else value > _decimal(broken_level)
            )
            if crossed:
                return getattr(item, "timestamp")
        return source_time

    def _candidate_cross_has_blue(
        self,
        reaction_number: int,
        event_time: datetime,
    ) -> bool:
        """Return whether the candidate cross has its aligned Reset Blue.

        The Reset Blue belongs to the same-direction reaction, but it does
        not have to be drawn on the candidate candle or on the candle that
        crosses the candidate.  Its exact formation event only needs to be
        no later than the candidate crossing event.
        """
        if reaction_number < 1 or reaction_number > len(self.trend_reactions):
            return False
        formation_time = self._reset_blue_formation_by_reaction.get(reaction_number)
        return formation_time is not None and formation_time <= event_time

    def _has_ordinary_trend_reaction(
        self, behavior_start: datetime, event_time: datetime
    ) -> bool:
        """Return whether ordinary aligned geometry completed in the leg.

        Order/S behavior deliberately consumes the maintained reaction output
        as geometry, without requiring its Reset Blue to own the event.  The
        reaction may complete before or after the opposite order confirms, but
        it must complete after the active A-stop behavior begins and no later
        than the candidate crossing.
        """
        for reaction in self.trend_reactions:
            confirmation = self._reaction_confirmation_time(
                reaction, self.direction
            )
            if behavior_start < confirmation <= event_time:
                return True
        return False

    def _find_boundary_source(
        self, value: Decimal, end_index: int
    ) -> tuple[int, datetime]:
        attribute = "high" if self.order_direction == "bearish" else "low"
        for item in self.candles[self.start_index : end_index + 1]:
            if _decimal(getattr(item, attribute)) == value:
                return int(getattr(item, "index")), getattr(item, "timestamp")
        raise ValueError("Cannot locate the Mode-A order leg-head source.")

    def _order_stop(
        self, order_number: int, reaction: object
    ) -> tuple[Decimal, int, datetime]:
        if str(getattr(reaction, "mode")) == "A":
            raw_level = getattr(reaction, "anchor_value", None)
            if raw_level is None:
                raw_level = getattr(reaction, "leg_boundary_value", None)
            if raw_level is None:
                raise ValueError("Mode-A order reaction has no leg-head boundary.")
            level = _decimal(raw_level)
            source_index = getattr(reaction, "anchor_idx", None)
            if source_index is None:
                source_index, source_time = self._find_boundary_source(
                    level, int(getattr(reaction, "first_idx"))
                )
            else:
                source_index = int(source_index)
                source_time = getattr(self.candles[source_index], "timestamp")
            return level, source_index, source_time

        if order_number <= 1:
            raise ValueError("Mode-B order reaction has no previous healthy reaction.")
        previous = self.opposite_reactions[order_number - 2]
        if self.order_direction == "bearish":
            return (
                _decimal(getattr(previous, "box_top")),
                int(getattr(previous, "box_top_source_idx")),
                getattr(
                    self.candles[int(getattr(previous, "box_top_source_idx"))],
                    "timestamp",
                ),
            )
        return (
            _decimal(getattr(previous, "box_bottom")),
            int(getattr(previous, "box_bottom_source_idx")),
            getattr(
                self.candles[int(getattr(previous, "box_bottom_source_idx"))],
                "timestamp",
            ),
        )

    def _candidate_crossed(self, candle: object, level: Decimal) -> bool:
        value = self._trend_extreme(candle)
        return self._a_stopped(value, level)

    def _order_stop_crossed(self, candle: object, level: Decimal) -> bool:
        if self.order_direction == "bearish":
            return _decimal(getattr(candle, "high")) > level
        return _decimal(getattr(candle, "low")) < level

    def _decision(
        self,
        candidate_level: Decimal,
        order_stop_level: Decimal,
        start: datetime,
        trend_reaction_number: int,
        behavior_start: datetime,
        candidate_start: datetime | None = None,
        fallback_on_unqualified_cross: bool = False,
    ) -> tuple[str, int, datetime, datetime] | None:
        lower_items = self._lower_window(max(start, self.range_start), self.range_end)
        for item in lower_items:
            event_time = getattr(item, "timestamp")
            candidate_cross = (
                self._candidate_crossed(item, candidate_level)
                and (candidate_start is None or event_time >= candidate_start)
            )
            order_cross = self._order_stop_crossed(item, order_stop_level)
            if candidate_cross and order_cross:
                return None
            if order_cross:
                index = self._main_index(event_time)
                return (
                    "red",
                    index,
                    getattr(self.candles[index], "timestamp"),
                    event_time,
                )
            if (
                candidate_cross
                and (
                self._candidate_cross_has_blue(trend_reaction_number, event_time)
                or self._has_ordinary_trend_reaction(behavior_start, event_time)
                )
            ):
                index = self._main_index(event_time)
                return (
                    "blue",
                    index,
                    getattr(self.candles[index], "timestamp"),
                    event_time,
                )
            if candidate_cross and fallback_on_unqualified_cross:
                index = self._main_index(event_time)
                return (
                    "fallback",
                    index,
                    getattr(self.candles[index], "timestamp"),
                    event_time,
                )
        if lower_items:
            return None

        start_index = max(
            self.start_index, bisect_right(self.candle_times, start) - 1
        )
        for item in self.candles[start_index : self.end_index + 1]:
            event_time = getattr(item, "timestamp")
            candidate_cross = (
                self._candidate_crossed(item, candidate_level)
                and (candidate_start is None or event_time >= candidate_start)
            )
            order_cross = self._order_stop_crossed(item, order_stop_level)
            if candidate_cross and order_cross:
                return None
            if order_cross:
                return (
                    "red",
                    int(getattr(item, "index")),
                    event_time,
                    event_time,
                )
            if (
                candidate_cross
                and (
                self._candidate_cross_has_blue(trend_reaction_number, event_time)
                or self._has_ordinary_trend_reaction(behavior_start, event_time)
                )
            ):
                return (
                    "blue",
                    int(getattr(item, "index")),
                    event_time,
                    event_time,
                )
            if candidate_cross and fallback_on_unqualified_cross:
                return (
                    "fallback",
                    int(getattr(item, "index")),
                    event_time,
                    event_time,
                )
        return None

    def detect(self) -> list[SZone]:
        output: list[SZone] = []
        self.a_ownership_windows.clear()
        self.order_audit.clear()
        cycle_start_time = self.range_start
        for zone_offset, zone in enumerate(self.a_zones):
            a_ordinal = zone_offset + 1
            if self._a_owned_by_s(zone):
                continue
            source_time = getattr(zone, "source_time")
            if source_time <= cycle_start_time and output:
                continue
            if source_time < cycle_start_time:
                continue
            next_a_confirmation = None
            if zone_offset + 1 < len(self.a_zones):
                next_a_confirmation = self._a_confirmation_time(
                    self.a_zones[zone_offset + 1]
                )
            a_price = _decimal(getattr(zone, "price"))
            a_stop = self._first_a_stop(a_price, self._a_confirmation_time(zone))
            if a_stop is None:
                continue
            a_stop_index, a_stop_time, a_stop_event_time = a_stop
            # A newer A confirmed before this A ever stops owns the unopened
            # lifecycle. Once the strict A stop occurs first, however, this
            # cycle is locked and must reach its S decision independently.
            if (
                next_a_confirmation is not None
                and a_stop_event_time >= next_a_confirmation
            ):
                continue
            self.a_ownership_windows.append((a_stop_event_time, None))
            order_match = self._first_order_after(a_stop_event_time)
            type3_deadline = (
                order_match[2] if order_match is not None else self.range_end
            )
            type3 = self._first_type3(a_stop_event_time, type3_deadline)
            if type3 is not None:
                (
                    source_index,
                    s_source_time,
                    price,
                    decision_index,
                    decision_time,
                    reset_reaction_number,
                    reset_time,
                    decision_event_time,
                ) = type3
                output.append(
                    SZone(
                        direction=self.direction,
                        # Type-3 is the same Blue behavior in either price
                        # direction. Family colors encode S/E priority, so
                        # reflecting prices must not promote it to Red.
                        color="blue",
                        formation_type="type3",
                        a_ordinal=a_ordinal,
                        a_source_index=int(getattr(zone, "source_index")),
                        a_source_time=getattr(zone, "source_time"),
                        a_price=a_price,
                        a_stop_index=a_stop_index,
                        a_stop_time=a_stop_time,
                        a_stop_event_time=a_stop_event_time,
                        order_direction=None,
                        order_reaction_number=None,
                        order_mode=None,
                        order_first_index=None,
                        order_first_time=None,
                        order_break_index=None,
                        order_break_time=None,
                        order_confirmation_time=None,
                        order_box_top=None,
                        order_box_top_source_index=None,
                        order_box_top_source_time=None,
                        order_box_bottom=None,
                        order_box_bottom_source_index=None,
                        order_box_bottom_source_time=None,
                        order_stop_level=None,
                        order_stop_source_index=None,
                        order_stop_source_time=None,
                        reset_reaction_number=reset_reaction_number,
                        reset_time=reset_time,
                        source_index=source_index,
                        source_time=s_source_time,
                        price=price,
                        decision_index=decision_index,
                        decision_time=decision_time,
                        decision_event_time=decision_event_time,
                    )
                )
                cycle_start_time = s_source_time
                self.a_ownership_windows[-1] = (
                    a_stop_event_time,
                    max(a_stop_event_time, s_source_time + self.timeframe),
                )
                continue
            if order_match is None:
                continue
            order_number, order, order_confirmation_time = order_match
            order_stop_level, order_stop_source_index, order_stop_source_time = (
                self._order_stop(order_number, order)
            )
            self.order_audit[
                (int(getattr(order, "first_idx")), int(getattr(order, "break_idx")))
            ] = {
                "reaction_number": order_number,
                "reaction": order,
                "confirmation_time": order_confirmation_time,
                "stop_level": order_stop_level,
                "stop_source_index": order_stop_source_index,
                "stop_source_time": order_stop_source_time,
                "a_source_time": source_time,
                "a_stop_event_time": a_stop_event_time,
            }
            candidate_timing = self._candidate_timing(
                a_stop_index, order, order_confirmation_time
            )
            pre_order_candidate = (
                self._candidate_before_order(
                    a_stop_index,
                    order,
                    a_stop_event_time=a_stop_event_time,
                )
                if candidate_timing == "before"
                else None
            )
            decision_behavior_start = a_stop_event_time
            decision = None
            use_pre_order_candidate = False
            if pre_order_candidate is not None:
                formation_type = "simple"
                source_index, source_time, price = pre_order_candidate
                red_source = pre_order_candidate
                trend_reaction_number = 0
                candidate_event_time = self._candidate_event_time(
                    source_index, price, a_stop_event_time
                )
                decision_behavior_start = candidate_event_time
                decision_candidate_start = candidate_event_time
                decision = self._decision(
                    price,
                    order_stop_level,
                    order_confirmation_time,
                    trend_reaction_number,
                    decision_behavior_start,
                    decision_candidate_start,
                    fallback_on_unqualified_cross=True,
                )
                if decision is None:
                    continue
                if decision[0] != "fallback":
                    use_pre_order_candidate = True
                else:
                    decision = None
            if not use_pre_order_candidate:
                decision_behavior_start = a_stop_event_time
                nested_match = self._nested_trend_reaction(
                    order, order_confirmation_time
                )
                advanced_blue = nested_match is not None
            if not use_pre_order_candidate and advanced_blue:
                formation_type = "advanced"
                red_source = None
                trend_reaction_number, trend_reaction, trend_confirmation_time = (
                    nested_match
                )
                source_index = int(
                    getattr(
                        order,
                        "box_bottom_source_idx"
                        if self.direction == "bullish"
                        else "box_top_source_idx",
                    )
                )
                source_time = getattr(self.candles[source_index], "timestamp")
                price = self._trend_extreme(self.candles[source_index])
                decision_candidate_start = trend_confirmation_time
            elif not use_pre_order_candidate:
                formation_type = "simple"
                trend_match = self._first_trend_reaction_after_order(
                    order_confirmation_time
                )
                if trend_match is None:
                    continue
                trend_reaction_number, trend_reaction, trend_confirmation_time = (
                    trend_match
                )
                source_index, source_time, price = self._simple_candidate(
                    order, trend_reaction
                )
                red_source = (
                    pre_order_candidate
                    if pre_order_candidate is not None
                    else self._candidate_after_order(
                        order_confirmation_time, trend_reaction
                    )
                )
                decision_candidate_start = trend_confirmation_time
            order_first_index = int(getattr(order, "first_idx"))
            if decision is None:
                decision = self._decision(
                    price,
                    order_stop_level,
                    order_confirmation_time,
                    trend_reaction_number,
                    decision_behavior_start,
                    decision_candidate_start,
                )
            if decision is None:
                continue
            color, decision_index, decision_time, decision_event_time = decision
            if color == "red" and red_source is not None:
                source_index, source_time, price = red_source
            order_break_index = int(getattr(order, "break_idx"))
            box_top_source_index = int(getattr(order, "box_top_source_idx"))
            box_bottom_source_index = int(getattr(order, "box_bottom_source_idx"))
            output.append(
                SZone(
                    direction=self.direction,
                    color=color,
                    formation_type=formation_type,
                    a_ordinal=a_ordinal,
                    a_source_index=int(getattr(zone, "source_index")),
                    a_source_time=getattr(zone, "source_time"),
                    a_price=a_price,
                    a_stop_index=a_stop_index,
                    a_stop_time=a_stop_time,
                    a_stop_event_time=a_stop_event_time,
                    order_direction=self.order_direction,
                    order_reaction_number=order_number,
                    order_mode=str(getattr(order, "mode")),
                    order_first_index=order_first_index,
                    order_first_time=getattr(
                        self.candles[order_first_index], "timestamp"
                    ),
                    order_break_index=order_break_index,
                    order_break_time=getattr(
                        self.candles[order_break_index], "timestamp"
                    ),
                    order_confirmation_time=order_confirmation_time,
                    order_box_top=_decimal(getattr(order, "box_top")),
                    order_box_top_source_index=box_top_source_index,
                    order_box_top_source_time=getattr(
                        self.candles[box_top_source_index], "timestamp"
                    ),
                    order_box_bottom=_decimal(getattr(order, "box_bottom")),
                    order_box_bottom_source_index=box_bottom_source_index,
                    order_box_bottom_source_time=getattr(
                        self.candles[box_bottom_source_index], "timestamp"
                    ),
                    order_stop_level=order_stop_level,
                    order_stop_source_index=order_stop_source_index,
                    order_stop_source_time=order_stop_source_time,
                    reset_reaction_number=None,
                    reset_time=None,
                    source_index=source_index,
                    source_time=source_time,
                    price=price,
                    decision_index=decision_index,
                    decision_time=decision_time,
                    decision_event_time=decision_event_time,
                )
            )
            cycle_start_time = source_time
            self.a_ownership_windows[-1] = (
                a_stop_event_time, source_time + self.timeframe
            )
        return sorted(
            output,
            key=lambda item: (item.source_time, item.decision_event_time),
        )


def detect_s_zones(
    direction: str,
    trend_reactions: Sequence[object],
    opposite_reactions: Sequence[object],
    trend_blue_lines: Sequence[object],
    a_zones: Sequence[object],
    candles: Sequence[object],
    lower_candles: Sequence[object],
    timeframe_seconds: int,
    start_index: int | None = None,
    end_index: int | None = None,
    opposite_resets: Sequence[object] = (),
) -> list[SZone]:
    return SDetector(
        direction,
        trend_reactions,
        opposite_reactions,
        trend_blue_lines,
        a_zones,
        candles,
        lower_candles,
        timeframe_seconds,
        start_index,
        end_index,
        opposite_resets,
    ).detect()


def visible_a_zones(
    a_zones: Sequence[object], s_zones: Sequence[object]
) -> list[object]:
    """Return A objects whose source candle is not occupied by a final S."""
    occupied = {
        int(getattr(item, "source_index"))
        for item in s_zones
    }
    return [
        item
        for item in a_zones
        if int(getattr(item, "source_index")) not in occupied
    ]


run_s = detect_s_zones
