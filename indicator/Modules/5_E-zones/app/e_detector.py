"""Recursive E detection over authoritative S and Reaction output."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from typing import Callable, Sequence


E_VERSION = "6.1.2"


@dataclass(frozen=True)
class EZone:
    direction: str
    family: str
    number: int
    parent_type: str
    parent_source_index: int
    parent_source_time: datetime
    parent_price: Decimal
    parent_stop_index: int
    parent_stop_time: datetime
    parent_stop_event_time: datetime
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
    source_index: int
    source_time: datetime
    price: Decimal
    decision_index: int
    decision_time: datetime
    decision_event_time: datetime


OrderMatch = tuple[
    int, object, datetime, Decimal, int, datetime,
    tuple[int, datetime, datetime] | None, tuple[str, ...],
    datetime | None, datetime | None, datetime | None,
]


def _d(value: object) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


class _CrossIndex:
    """Find the first strict High/Low crossing without rescanning candles."""

    def __init__(self, candles: Sequence[object]) -> None:
        size = 1
        while size < len(candles):
            size *= 2
        self.size = size
        self.length = len(candles)
        self.minimum: list[Decimal | None] = [None] * (2 * size)
        self.maximum: list[Decimal | None] = [None] * (2 * size)
        for position, candle in enumerate(candles):
            self.minimum[size + position] = _d(getattr(candle, "low"))
            self.maximum[size + position] = _d(getattr(candle, "high"))
        for node in range(size - 1, 0, -1):
            left, right = node * 2, node * 2 + 1
            low_left, low_right = self.minimum[left], self.minimum[right]
            high_left, high_right = self.maximum[left], self.maximum[right]
            self.minimum[node] = (
                low_right if low_left is None else low_left
                if low_right is None else min(low_left, low_right)
            )
            self.maximum[node] = (
                high_right if high_left is None else high_left
                if high_right is None else max(high_left, high_right)
            )

    def first_less(self, left: int, right: int, level: Decimal) -> int | None:
        return self._first(1, 0, self.size, left, right, level, True)

    def first_greater(self, left: int, right: int, level: Decimal) -> int | None:
        return self._first(1, 0, self.size, left, right, level, False)

    def _first(
        self, node: int, start: int, end: int, left: int, right: int,
        level: Decimal, less: bool,
    ) -> int | None:
        if end <= left or right <= start or start >= self.length:
            return None
        extreme = self.minimum[node] if less else self.maximum[node]
        if extreme is None or (extreme >= level if less else extreme <= level):
            return None
        if end - start == 1:
            return start
        middle = (start + end) // 2
        found = self._first(node * 2, start, middle, left, right, level, less)
        return found if found is not None else self._first(
            node * 2 + 1, middle, end, left, right, level, less
        )


_LOWER_INDEX_CACHE: dict[
    int,
    tuple[Sequence[object], list[object], list[datetime], _CrossIndex],
] = {}


def _shared_lower_index(
    candles: Sequence[object],
) -> tuple[list[object], list[datetime], _CrossIndex]:
    """Reuse the immutable lower-candle search index within one bridge run."""
    key = id(candles)
    cached = _LOWER_INDEX_CACHE.get(key)
    if cached is not None and cached[0] is candles:
        return cached[1], cached[2], cached[3]
    ordered = sorted(candles, key=lambda item: getattr(item, "timestamp"))
    times = [getattr(item, "timestamp") for item in ordered]
    cross_index = _CrossIndex(ordered)
    _LOWER_INDEX_CACHE[key] = (candles, ordered, times, cross_index)
    return ordered, times, cross_index


class EDetector:
    _SEQUENCE_PRIORITY = {
        ("E", "red"): 4, ("S", "red"): 3,
        ("E", "blue"): 2, ("S", "blue"): 1,
    }

    def __init__(
        self,
        direction: str,
        trend_reactions: Sequence[object],
        opposite_reactions: Sequence[object],
        s_zones: Sequence[object],
        trend_resets: Sequence[object],
        opposite_resets: Sequence[object],
        candles: Sequence[object],
        lower_candles: Sequence[object],
        timeframe_seconds: int,
        start_index: int = 0,
        end_index: int | None = None,
        geometry_finder: Callable[[str, int, int], object | None] | None = None,
        direct_geometry_finder: Callable[
            [str, int, int, datetime], object | None
        ] | None = None,
        blocked_order_first_times: set[datetime] | None = None,
        initial_order_audit: dict[tuple[int, int], dict[str, object]] | None = None,
        reset_geometry_finder: Callable[
            [str, int, int, int], object | None
        ] | None = None,
        sequence_resets: dict[datetime, int] | None = None,
    ) -> None:
        if direction not in {"bullish", "bearish"}:
            raise ValueError("Direction must be 'bullish' or 'bearish'.")
        self.direction = direction
        self.sequence_resets = dict(sequence_resets or {})
        self.order_direction = "bearish" if direction == "bullish" else "bullish"
        self._reset_time_cache: dict[int, datetime] = {}
        self._confirmation_cache: dict[tuple[object, ...], datetime] = {}
        self.trend_reactions = list(trend_reactions)
        self.opposite_reactions = list(opposite_reactions)
        self.s_zones = sorted(
            s_zones,
            key=lambda item: (
                getattr(item, "source_time"),
                int(getattr(item, "source_index")),
            ),
        )
        self.opposite_resets = sorted(opposite_resets, key=self._reset_time)
        self.candles = list(candles)
        self.lower, self.lower_times, self._lower_cross_index = (
            _shared_lower_index(lower_candles)
        )
        self.timeframe = timedelta(seconds=timeframe_seconds)
        self.times = [getattr(item, "timestamp") for item in self.candles]
        self.start_index = int(start_index)
        self.end_index = len(self.candles) - 1 if end_index is None else int(end_index)
        self.range_start = self.times[self.start_index]
        self.range_end = self.times[self.end_index] + self.timeframe
        self.geometry_finder = geometry_finder
        self.direct_geometry_finder = direct_geometry_finder or geometry_finder
        self.reset_geometry_finder = reset_geometry_finder
        self.blocked_order_first_times = blocked_order_first_times or set()
        self.initial_order_audit = initial_order_audit or {}
        self._geometry_evidence_cache: dict[tuple[datetime, datetime], bool] = {}
        self._order_b_geometry_cache: dict[
            tuple[datetime, datetime, datetime],
            tuple[int, object, datetime] | None,
        ] = {}
        self._next_outer_reset_cache: dict[int, datetime | None] = {}
        self._cross_order_cache: dict[
            tuple[datetime, Decimal], tuple[int, datetime, datetime] | None
        ] = {}
        self._trigger_cross_cache: dict[tuple[datetime, Decimal], datetime | None] = {}
        self._reset_leg_geometry_cache: dict[tuple[int, datetime], tuple[datetime, Decimal] | None] = {}
        self._order_candidates_cache: dict[
            tuple[datetime, datetime | None, bool], tuple[OrderMatch, ...]
        ] = {}
        self.order_audit: dict[tuple[int, int], dict[str, object]] = {}
        self._synthetic_order_cache: list[
            tuple[int, object, datetime, datetime, datetime]
        ] | None = None
        self._audit_synthetic_order_cache: list[
            tuple[int, object, datetime, datetime, datetime]
        ] | None = None
        self._trend_first_times = [
            self._reaction_first_time(item) for item in self.trend_reactions
        ]
        self._trend_confirmations = [
            self._confirmation_for(item, self.direction)
            for item in self.trend_reactions
        ]
        self._opposite_first_times = [
            self._reaction_first_time(item) for item in self.opposite_reactions
        ]
        self._opposite_confirmations = [
            self._confirmation(item) for item in self.opposite_reactions
        ]
        self._trend_by_confirmation = sorted(
            zip(
                self._trend_confirmations,
                self._trend_first_times,
                self.trend_reactions,
            ),
            key=lambda item: item[0],
        )
        self._trend_confirmation_times = [item[0] for item in self._trend_by_confirmation]
        self._opposite_reset_times_by_first: dict[int, list[datetime]] = {}
        for reset in self.opposite_resets:
            self._opposite_reset_times_by_first.setdefault(
                int(getattr(reset, "from_first_idx")), []
            ).append(self._reset_time(reset))
        self._opposite_reset_events = [
            (self._reset_time(item), item) for item in self.opposite_resets
        ]
        self._opposite_reset_times = [item[0] for item in self._opposite_reset_events]
        self._opposite_by_first_index = {
            int(getattr(item, "first_idx")): item
            for item in self.opposite_reactions
        }
        self.visual_lifecycle_starts: set[datetime] = set()

    def _reset_time(self, reset: object) -> datetime:
        cache_key = id(reset)
        cached = self._reset_time_cache.get(cache_key)
        if cached is not None:
            return cached
        second = getattr(reset, "second_time", None)
        if second:
            value = datetime.strptime(second, "%Y-%m-%d %H:%M:%S")
        else:
            display = getattr(reset, "display_time", None)
            value = (
                datetime.strptime(display, "%Y-%m-%d %H:%M:%S")
                if display
                else getattr(reset, "timestamp")
            )
        self._reset_time_cache[cache_key] = value
        return value

    def _main_index(self, value: datetime) -> int:
        return max(0, bisect_right(self.times, value) - 1)

    def _lower_window(self, start: datetime, end: datetime | None = None) -> list[object]:
        left = bisect_left(self.lower_times, start)
        right = len(self.lower) if end is None else bisect_left(self.lower_times, end)
        return self.lower[left:right]

    def _stop_value(self, item: object) -> Decimal:
        return _d(getattr(item, "low" if self.direction == "bullish" else "high"))

    def _strict_stop(self, value: Decimal, level: Decimal) -> bool:
        return value < level if self.direction == "bullish" else value > level

    def _first_parent_stop(self, source_time: datetime, level: Decimal) -> tuple[int, datetime] | None:
        left = bisect_left(self.lower_times, max(source_time, self.range_start))
        right = bisect_left(self.lower_times, self.range_end)
        position = (
            self._lower_cross_index.first_less(left, right, level)
            if self.direction == "bullish"
            else self._lower_cross_index.first_greater(left, right, level)
        )
        if position is None:
            return None
        event = self.lower_times[position]
        return self._main_index(event), event

    def _confirmation_for(self, reaction: object, direction: str) -> datetime:
        cache_key = (
            direction,
            int(getattr(reaction, "first_idx")),
            int(getattr(reaction, "break_idx")),
            _d(getattr(reaction, "box_top")),
            _d(getattr(reaction, "box_bottom")),
            getattr(reaction, "intrabar_start", None),
        )
        cached = self._confirmation_cache.get(cache_key)
        if cached is not None:
            return cached
        index = int(getattr(reaction, "break_idx"))
        candle = self.candles[index]
        start = getattr(reaction, "intrabar_start", None) or getattr(candle, "timestamp")
        end = getattr(candle, "timestamp") + self.timeframe
        level = _d(getattr(reaction, "box_top" if direction == "bullish" else "box_bottom"))
        for item in self._lower_window(start, end):
            value = _d(getattr(item, "high" if direction == "bullish" else "low"))
            if (direction == "bullish" and value > level) or (
                direction == "bearish" and value < level
            ):
                value = getattr(item, "timestamp")
                self._confirmation_cache[cache_key] = value
                return value
        value = getattr(candle, "timestamp")
        self._confirmation_cache[cache_key] = value
        return value

    def _confirmation(self, reaction: object) -> datetime:
        return self._confirmation_for(reaction, self.order_direction)

    def _reaction_first_time(self, reaction: object) -> datetime:
        return getattr(self.candles[int(getattr(reaction, "first_idx"))], "timestamp")

    def _strict_trigger_cross(self, start: datetime, level: Decimal) -> datetime | None:
        cache_key = (start, level)
        cached = self._trigger_cross_cache.get(cache_key)
        if cached is not None:
            return cached
        left = bisect_left(self.lower_times, start)
        right = bisect_left(self.lower_times, self.range_end)
        position = (
            self._lower_cross_index.first_less(left, right, level)
            if self.direction == "bullish"
            else self._lower_cross_index.first_greater(left, right, level)
        )
        result = None if position is None else self.lower_times[position]
        self._trigger_cross_cache[cache_key] = result
        return result

    def _reset_leg_geometry(
        self, reset: object, reset_time: datetime,
    ) -> tuple[datetime, Decimal] | None:
        """Return the inclusive Break-to-Reset leg start and outer boundary."""
        cache_key = (int(getattr(reset, "from_first_idx")), reset_time)
        cached = self._reset_leg_geometry_cache.get(cache_key)
        if cached is not None:
            return cached
        owner = self._opposite_by_first_index.get(
            int(getattr(reset, "from_first_idx"))
        )
        if owner is None:
            self._reset_leg_geometry_cache[cache_key] = None
            return None
        start_index = int(getattr(owner, "break_idx"))
        end_index = self._main_index(reset_time)
        if end_index < start_index:
            self._reset_leg_geometry_cache[cache_key] = None
            return None
        boundary = self._stop_value(self.candles[start_index])
        for candle in self.candles[start_index + 1 : end_index + 1]:
            value = self._stop_value(candle)
            better = value < boundary if self.direction == "bullish" else value > boundary
            if better:
                boundary = value
        result = self.times[start_index], boundary
        self._reset_leg_geometry_cache[cache_key] = result
        return result

    def _reset_leg_has_simple_trend_reaction(
        self, leg_start: datetime, boundary_cross: datetime,
    ) -> bool:
        key = (leg_start, boundary_cross)
        cached = self._geometry_evidence_cache.get(key)
        if cached is not None:
            return cached
        left = bisect_left(self._trend_confirmation_times, leg_start)
        right = bisect_right(self._trend_confirmation_times, boundary_cross)
        result = left < right
        self._geometry_evidence_cache[key] = result
        return result

    def _first_order_b_geometry(
        self, reset_time: datetime, boundary_cross: datetime, deadline: datetime,
    ) -> tuple[int, object, datetime] | None:
        """Return the first structurally owned Order_B geometry after its gate."""
        cache_key = (reset_time, boundary_cross, deadline)
        if cache_key in self._order_b_geometry_cache:
            return self._order_b_geometry_cache[cache_key]
        end_index = min(self.end_index, bisect_left(self.times, deadline) - 1)
        if self.geometry_finder is None:
            self._order_b_geometry_cache[cache_key] = None
            return None

        def find_geometry(gate_index: int) -> object | None:
            if gate_index > end_index:
                return None
            if self.reset_geometry_finder is not None:
                reset_index = self._main_index(reset_time)
                gate_time = self.times[gate_index]
                gate_owner = self._opposite_by_first_index.get(gate_index)
                # A non-canonical First that is already open in the main
                # candle containing the lower-timeframe gate belongs to the
                # pre-gate leg.  Canonical ownership may start on that candle;
                # otherwise the bounded Reset search begins on the next one.
                reset_gate_index = (
                    gate_index
                    if gate_owner is not None
                    and self._reaction_first_time(gate_owner) == gate_time
                    else gate_index + 1
                )
                return self.reset_geometry_finder(
                    self.order_direction,
                    reset_index,
                    reset_gate_index,
                    end_index,
                )
            assert self.geometry_finder is not None
            return self.geometry_finder(
                self.order_direction, gate_index, end_index
            )

        gate_event = boundary_cross
        while gate_event < deadline:
            gate_index = self._main_index(gate_event)
            geometry = find_geometry(gate_index)
            if geometry is None:
                break
            gate_time = self.times[gate_index]
            if self._reaction_first_time(geometry) == gate_time:
                matching = self._opposite_by_first_index.get(
                    int(getattr(geometry, "first_idx"))
                )
                if (
                    matching is None
                    or int(getattr(matching, "break_idx"))
                    != int(getattr(geometry, "break_idx"))
                ):
                    geometry = find_geometry(gate_index + 1)
                    if geometry is None:
                        break
            confirmation = self._confirmation_for(
                geometry, self.order_direction
            )
            if confirmation >= deadline:
                break

            geometry_first = self._reaction_first_time(geometry)
            if (
                self.direction == "bullish"
                and geometry_first in self.blocked_order_first_times
            ):
                # The leg context may keep an internal head alive after the
                # Reset boundary has crossed. Geometry whose First opens in
                # that closed interval cannot own the resumed outer E space.
                next_index = max(
                    gate_index, int(getattr(geometry, "first_idx"))
                ) + 1
                if next_index > end_index:
                    break
                gate_event = self.times[next_index]
                continue
            owner_position = bisect_right(
                self._opposite_first_times, geometry_first
            ) - 1
            owner = (
                self.opposite_reactions[owner_position]
                if owner_position >= 0 else None
            )
            if owner is not None:
                owner_first = self._reaction_first_time(owner)
                owner_resets = self._opposite_reset_times_by_first.get(
                    int(getattr(owner, "first_idx")), []
                )
                owner_reset = next(
                    (value for value in owner_resets if value > geometry_first),
                    None,
                )
                owner_already_reset = any(
                    value <= geometry_first for value in owner_resets
                )
                # Opposite-Reaction ownership is directionally independent.
                # A trend-side Reset cannot release or invalidate this owner;
                # only a Reset belonging to that owner can do so.
                active_owner = not owner_already_reset
                if active_owner:
                    owner_confirmation = self._confirmation(owner)
                    if owner_first >= gate_time:
                        if owner_confirmation >= deadline:
                            break
                        result = owner_position + 1, owner, owner_confirmation
                        self._order_b_geometry_cache[cache_key] = result
                        return result
                    if owner_reset is None or owner_reset >= deadline:
                        break
                    gate_event = owner_reset
                    continue

            existing = self._opposite_by_first_index.get(
                int(getattr(geometry, "first_idx"))
            )
            if (
                existing is not None
                and int(getattr(existing, "break_idx"))
                == int(getattr(geometry, "break_idx"))
            ):
                result = owner_position + 1, existing, confirmation
            else:
                result = 0, geometry, confirmation
            self._order_b_geometry_cache[cache_key] = result
            return result

        self._order_b_geometry_cache[cache_key] = None
        return None

    def _next_outer_reset_time(
        self, reset_position: int, fallback: datetime,
    ) -> datetime:
        """Return the next non-nested Reset boundary.

        A reaction that starts after the current Reset belongs to a nested leg
        and cannot close the outer ResetLeg owner.
        """
        if reset_position in self._next_outer_reset_cache:
            cached = self._next_outer_reset_cache[reset_position]
            return fallback if cached is None else cached
        reset_time, _ = self._opposite_reset_events[reset_position]
        result = None
        for next_time, next_reset in self._opposite_reset_events[reset_position + 1:]:
            owner_first = self.times[int(getattr(next_reset, "from_first_idx"))]
            if owner_first <= reset_time:
                result = next_time
                break
        self._next_outer_reset_cache[reset_position] = result
        return fallback if result is None else result

    def _direct_order_is_unlocked(self, reaction: object, context_start: datetime) -> bool:
        """Reject an order First that precedes Reset of the active trend reaction."""
        first = self._reaction_first_time(reaction)
        right = bisect_left(self._trend_confirmation_times, first)
        left = bisect_right(self._trend_confirmation_times, context_start, 0, right)
        if left >= right:
            return True
        owner = self._trend_by_confirmation[right - 1][2]
        reset_times = self._opposite_reset_times_by_first.get(
            int(getattr(owner, "first_idx")), []
        )
        return bool(reset_times) and min(reset_times) < first

    def _replacement_order(
        self,
        owner: object,
        owner_confirmation: datetime,
        owner_stop_event: datetime,
    ) -> tuple[int, object, datetime, datetime] | None:
        """Find the first order created by a complete behavioral-reset cycle."""
        reset_left = bisect_right(self._opposite_reset_times, owner_confirmation)
        reset_right = bisect_left(self._opposite_reset_times, owner_stop_event)
        reset_events = self._opposite_reset_events[reset_left:reset_right]
        owner_first_index = int(getattr(owner, "first_idx"))
        for position, (reset_time, reset) in enumerate(reset_events):
            reset_owner_index = int(getattr(reset, "from_first_idx"))
            reset_owner_first = self.times[reset_owner_index]
            if (
                reset_owner_index != owner_first_index
                and reset_owner_first < owner_confirmation
            ):
                continue
            # A Reset of the provisional order, or of a later opposite
            # reaction in its still-open lifecycle, can originate the
            # replacement leg. Stale reactions from before that lifecycle
            # cannot take ownership.
            absolute_position = bisect_left(self._opposite_reset_times, reset_time)
            next_opposite_reset = self._next_outer_reset_time(
                absolute_position, owner_stop_event
            )
            leg = self._reset_leg_geometry(reset, reset_time)
            if leg is None:
                continue
            leg_start, trigger = leg
            crossing = self._strict_trigger_cross(reset_time, trigger)
            if crossing is None or crossing >= min(next_opposite_reset, owner_stop_event):
                continue
            if not self._reset_leg_has_simple_trend_reaction(leg_start, crossing):
                continue
            gate_time = self.times[self._main_index(crossing)]
            order_start = bisect_left(self._opposite_first_times, gate_time)
            for order_position in range(order_start, len(self.opposite_reactions)):
                reaction = self.opposite_reactions[order_position]
                first = self._opposite_first_times[order_position]
                confirmation = self._opposite_confirmations[order_position]
                if first >= gate_time and confirmation >= crossing and confirmation < owner_stop_event:
                    return order_position + 1, reaction, confirmation, reset_time
        return None

    def _reset_leg_evidence(
        self, reaction: object, context_start: datetime
    ) -> tuple[datetime, datetime] | None:
        """Return the Reset and strict-break events that created ``reaction``."""
        order_first = self._reaction_first_time(reaction)
        order_confirmation = self._confirmation(reaction)
        # Mode-B ownership starts with the current E-space lifecycle. A Reset
        # that occurred before the parent stop belongs to an older lifecycle
        # and cannot create an order for this parent.
        reset_left = bisect_left(self._opposite_reset_times, context_start)
        reset_right = bisect_right(
            self._opposite_reset_times, order_confirmation
        )
        reaction_first_index = int(getattr(reaction, "first_idx"))
        for reset_position in range(reset_left, reset_right):
            reset_time, reset = self._opposite_reset_events[reset_position]
            next_reset = self._next_outer_reset_time(
                reset_position, self.range_end
            )
            if order_confirmation >= next_reset:
                continue
            leg = self._reset_leg_geometry(reset, reset_time)
            if leg is None:
                continue
            leg_start, boundary = leg
            crossing = self._strict_trigger_cross(reset_time, boundary)
            if crossing is None or crossing > order_confirmation:
                continue
            if not self._reset_leg_has_simple_trend_reaction(leg_start, crossing):
                continue
            first_after_crossing = self._first_order_b_geometry(
                reset_time, crossing, next_reset
            )
            if (
                order_confirmation >= crossing
                and first_after_crossing is not None
                and int(getattr(first_after_crossing[1], "first_idx"))
                == reaction_first_index
            ):
                return reset_time, crossing
        return None

    def _is_reset_leg_order(
        self, reaction: object, context_start: datetime
    ) -> bool:
        """Whether ``reaction`` is the first order of a complete Reset leg."""
        return self._reset_leg_evidence(reaction, context_start) is not None

    def _legacy_reset_leg_evidence(
        self, reaction: object, context_start: datetime,
    ) -> tuple[datetime, datetime] | None:
        """Return the established audit cause without changing E eligibility."""
        order_first = self._reaction_first_time(reaction)
        order_confirmation = self._confirmation(reaction)
        reset_left = bisect_left(self._opposite_reset_times, context_start)
        reset_right = bisect_right(self._opposite_reset_times, order_confirmation)
        reaction_first_index = int(getattr(reaction, "first_idx"))
        for reset_position in range(reset_left, reset_right):
            reset_time, reset = self._opposite_reset_events[reset_position]
            next_reset = self._next_outer_reset_time(reset_position, self.range_end)
            if order_confirmation >= next_reset:
                continue
            leg = self._reset_leg_geometry(reset, reset_time)
            if leg is None:
                continue
            leg_start, boundary = leg
            crossing = self._strict_trigger_cross(reset_time, boundary)
            if crossing is None or crossing > order_confirmation:
                continue
            if self.geometry_finder is not None:
                aligned = self.geometry_finder(
                    self.direction,
                    bisect_left(self.times, leg_start),
                    self._main_index(crossing),
                ) is not None
            else:
                left = bisect_left(self._trend_confirmation_times, leg_start)
                right = bisect_right(self._trend_confirmation_times, crossing)
                aligned = left < right
            if not aligned:
                continue
            gate_time = self.times[self._main_index(crossing)]
            first_after = bisect_left(self._opposite_first_times, gate_time)
            if (
                order_first >= gate_time
                and first_after < len(self.opposite_reactions)
                and int(getattr(self.opposite_reactions[first_after], "first_idx"))
                == reaction_first_index
            ):
                return reset_time, crossing
        return None

    def _order_cause_evidence(
        self,
        reaction: object,
        parent_stop: datetime,
        selected_from_direct_search: bool,
    ) -> tuple[tuple[str, ...], datetime | None, datetime | None, datetime | None]:
        """Describe why the selected E-space order is eligible.

        A reaction can satisfy both creation paths.  Existing unconsumed orders
        are explicitly identified instead of being mislabeled as newly created
        after the current parent stop.
        """
        causes: list[str] = []
        parent_stop_cause = None
        reset_time = None
        reset_break = None

        if selected_from_direct_search:
            causes.append("parent-stop")
            parent_stop_cause = parent_stop

        reset_evidence = self._reset_leg_evidence(reaction, parent_stop)
        if reset_evidence is not None:
            causes.append("reset-leg")
            reset_time, reset_break = reset_evidence

        if not causes:
            causes.append("carried-live")
        return tuple(causes), parent_stop_cause, reset_time, reset_break

    def _order_stop(
        self, number: int, reaction: object, context_start: datetime | None = None,
    ) -> tuple[Decimal, int, datetime]:
        if str(getattr(reaction, "mode")) == "A":
            value = getattr(reaction, "anchor_value", None)
            if value is None:
                value = getattr(reaction, "leg_boundary_value")
            index = getattr(reaction, "anchor_idx", None)
            if index is None:
                index = int(getattr(reaction, "first_idx"))
            index = int(index)
            return _d(value), index, getattr(self.candles[index], "timestamp")
        first = self._reaction_first_time(reaction)
        if context_start is not None and first == context_start:
            attribute = (
                "box_top" if self.order_direction == "bearish" else "box_bottom"
            )
            source_attribute = f"{attribute}_source_idx"
            index = int(getattr(reaction, source_attribute))
            return (
                _d(getattr(reaction, attribute)),
                index,
                getattr(self.candles[index], "timestamp"),
            )
        if number <= 1:
            raise ValueError("Mode-B order reaction has no previous reaction.")
        previous = self.opposite_reactions[number - 2]
        if context_start is not None and not self._direct_order_is_unlocked(
            previous, context_start
        ):
            anchor_value = getattr(previous, "anchor_value", None)
            anchor_index = getattr(previous, "anchor_idx", None)
            if anchor_value is not None and anchor_index is not None:
                index = int(anchor_index)
                return _d(anchor_value), index, getattr(self.candles[index], "timestamp")
        if self.order_direction == "bearish":
            index = int(getattr(previous, "box_top_source_idx"))
            return _d(getattr(previous, "box_top")), index, getattr(self.candles[index], "timestamp")
        index = int(getattr(previous, "box_bottom_source_idx"))
        return _d(getattr(previous, "box_bottom")), index, getattr(self.candles[index], "timestamp")

    def _first_healthy_direct_geometry(
        self, start: datetime,
    ) -> tuple[int, object, datetime] | None:
        """Return the first healthy geometry after an A/S/E strict stop.

        A candidate completes normally when the active prior reaction is not
        Reset before its confirmation. If that prior reaction is Reset first,
        the search restarts strictly after the Reset candle and the first
        complete geometry owns the new leg.
        """
        if self.direct_geometry_finder is None:
            return None
        # Geometry needs its complete context candle at or after the exact
        # stop event. A First candle that already opened before the lower-time-
        # frame stop cannot be attributed to that stop.
        search_index = self._main_index(start)
        search_event = start
        restarted = False
        while search_index <= self.end_index:
            candidate = self.direct_geometry_finder(
                self.order_direction, search_index, self.end_index, search_event
            )
            if candidate is None:
                return None
            first = self._reaction_first_time(candidate)
            if (
                first in self.blocked_order_first_times
                and first == self.times[self._main_index(start)]
            ):
                search_index = int(getattr(candidate, "first_idx")) + 1
                search_event = first
                continue
            confirmation = self._confirmation_for(
                candidate, self.order_direction
            )
            owner_position = bisect_right(
                self._opposite_confirmations, search_event
            ) - 1
            prior = (
                self.opposite_reactions[owner_position]
                if owner_position >= 0 else None
            )
            reset_before_confirmation = None
            if prior is not None:
                for reset_time in self._opposite_reset_times_by_first.get(
                    int(getattr(prior, "first_idx")), []
                ):
                    if search_event < reset_time <= confirmation:
                        reset_before_confirmation = reset_time
                        break
            if reset_before_confirmation is not None:
                search_index = self._main_index(reset_before_confirmation)
                search_event = reset_before_confirmation
                restarted = True
                continue

            prior_position = bisect_left(self._opposite_first_times, first) - 1
            number = prior_position + 2
            gate_decision = getattr(candidate, "order_gate_decision", None)
            if restarted:
                candidate = replace(candidate, mode="A")
            elif prior is not None:
                candidate = replace(candidate, mode="B")
            if gate_decision is not None:
                setattr(candidate, "order_gate_decision", gate_decision)
            return number, candidate, confirmation
        return None

    def order_candidates(
        self, start: datetime, continuous_deadline: datetime | None = None,
        audit_legacy: bool = False,
    ) -> list[OrderMatch]:
        """Return every valid E-space order formed before this E decision.

        The direct parent-stop order and ResetLeg orders are independent.
        Resetting a valid order never erases it.  If one reaction satisfies
        both creation paths it is returned once with both causes.
        """
        cache_key = (start, continuous_deadline, audit_legacy)
        cached = self._order_candidates_cache.get(cache_key)
        if cached is not None:
            return list(cached)

        by_geometry: dict[tuple[int, int], OrderMatch] = {}
        gate_time = self.times[self._main_index(start)]
        synthetic: list[tuple[int, object, datetime, datetime, datetime]] = []

        selected_cache = (
            self._audit_synthetic_order_cache
            if audit_legacy else self._synthetic_order_cache
        )
        if selected_cache is not None:
            synthetic = [
                item for item in selected_cache
                if item[3] >= start
            ]
        elif self.geometry_finder is not None:
            all_synthetic = []
            for reset_position, (reset_time, reset) in enumerate(
                self._opposite_reset_events
            ):
                reset_owner = self._opposite_by_first_index.get(
                    int(getattr(reset, "from_first_idx"))
                )
                if reset_owner is None:
                    continue
                leg = self._reset_leg_geometry(reset, reset_time)
                if leg is None:
                    continue
                leg_start, boundary = leg
                crossing = self._strict_trigger_cross(reset_time, boundary)
                if crossing is None:
                    continue
                next_reset = self._next_outer_reset_time(
                    reset_position, self.range_end
                )
                if crossing >= next_reset:
                    continue
                if audit_legacy:
                    if self.geometry_finder(
                        self.direction,
                        bisect_left(self.times, leg_start),
                        self._main_index(crossing),
                    ) is None:
                        continue
                    first_index = self._main_index(crossing)
                    end_index = min(
                        self.end_index,
                        max(first_index, bisect_left(self.times, next_reset) - 1),
                    )
                    geometry = self.geometry_finder(
                        self.order_direction, first_index, end_index
                    )
                    if geometry is None:
                        continue
                    existing = self._opposite_by_first_index.get(
                        int(getattr(geometry, "first_idx"))
                    )
                    if (
                        existing is not None
                        and int(getattr(existing, "break_idx"))
                        == int(getattr(geometry, "break_idx"))
                    ):
                        geometry = existing
                        number = self.opposite_reactions.index(existing) + 1
                    else:
                        number = 0
                    confirmation = self._confirmation_for(
                        geometry, self.order_direction
                    )
                else:
                    if not self._reset_leg_has_simple_trend_reaction(
                        leg_start, crossing
                    ):
                        continue
                    order_b = self._first_order_b_geometry(
                        reset_time, crossing, next_reset
                    )
                    if order_b is None:
                        continue
                    number, geometry, confirmation = order_b
                all_synthetic.append(
                    (number, geometry, confirmation, reset_time, crossing)
                )
            if audit_legacy:
                self._audit_synthetic_order_cache = all_synthetic
            else:
                self._synthetic_order_cache = all_synthetic
            synthetic = [item for item in all_synthetic if item[3] >= start]

        direct_pool: list[tuple[int, object, datetime]] = []
        geometric_direct = self._first_healthy_direct_geometry(start)
        independent_gate = gate_time
        direct_position = bisect_left(
            self._opposite_first_times, independent_gate
        )
        blocked_same_candle = False
        while (
            direct_position < len(self.opposite_reactions)
            and self._opposite_first_times[direct_position]
            in self.blocked_order_first_times
            and self._opposite_first_times[direct_position]
            == self.times[self._main_index(start)]
        ):
            blocked_same_candle = True
            direct_position += 1
        independent = None
        if direct_position < len(self.opposite_reactions):
            independent = (
                direct_position + 1,
                self.opposite_reactions[direct_position],
                self._opposite_confirmations[direct_position],
            )
        geometric_gate_decision = (
            getattr(geometric_direct[1], "order_gate_decision", None)
            if geometric_direct is not None else None
        )
        prefer_geometric = (
            continuous_deadline is not None
            and geometric_direct is not None
            and geometric_gate_decision == "restart"
            and (
                continuous_deadline == self.range_end
                or continuous_deadline < geometric_direct[2]
            )
        )
        if prefer_geometric:
            direct_pool.append(geometric_direct)
        elif independent is not None:
            direct_pool.append(independent)
        elif geometric_direct is not None:
            direct_pool.append(geometric_direct)
        if direct_pool:
            number, reaction, confirmation = min(
                direct_pool,
                key=lambda item: (self._reaction_first_time(item[1]), item[2]),
            )
            level, source, source_time = self._order_stop(number, reaction)
            crossed = self._cross_order(confirmation, level)
            key = (int(getattr(reaction, "first_idx")), int(getattr(reaction, "break_idx")))
            by_geometry[key] = (
                number, reaction, confirmation, level, source, source_time,
                crossed, ("parent-stop",), start, None, None,
            )

        for number, reaction, confirmation, reset_time, reset_break in synthetic:
            if confirmation < start:
                continue
            level, source, source_time = self._order_stop(number, reaction)
            crossed = self._cross_order(confirmation, level)
            key = (int(getattr(reaction, "first_idx")), int(getattr(reaction, "break_idx")))
            existing = by_geometry.get(key)
            causes = (
                tuple(dict.fromkeys((*existing[7], "reset-leg")))
                if existing is not None else ("reset-leg",)
            )
            by_geometry[key] = (
                number, reaction, confirmation, level, source, source_time,
                crossed, causes,
                existing[8] if existing is not None else None,
                reset_time, reset_break,
            )

        known_stops = [
            item[6][2] for item in by_geometry.values()
            if item[6] is not None
        ]
        provisional_deadline = min(known_stops) if known_stops else self.range_end
        if self.direction == "bullish" and continuous_deadline is not None:
            provisional_deadline = min(provisional_deadline, continuous_deadline)
        for position, reaction in enumerate(self.opposite_reactions):
            confirmation = self._opposite_confirmations[position]
            if confirmation < start:
                continue
            if confirmation > provisional_deadline:
                break
            evidence = (
                self._legacy_reset_leg_evidence(reaction, start)
                if audit_legacy else self._reset_leg_evidence(reaction, start)
            )
            if evidence is None:
                continue
            reset_time, reset_break = evidence
            number = position + 1
            level, source, source_time = self._order_stop(number, reaction)
            crossed = self._cross_order(confirmation, level)
            key = (
                int(getattr(reaction, "first_idx")),
                int(getattr(reaction, "break_idx")),
            )
            existing = by_geometry.get(key)
            causes = (
                tuple(dict.fromkeys((*existing[7], "reset-leg")))
                if existing is not None else ("reset-leg",)
            )
            by_geometry[key] = (
                number, reaction, confirmation, level, source, source_time,
                crossed, causes,
                existing[8] if existing is not None else None,
                reset_time, reset_break,
            )
            if crossed is not None:
                provisional_deadline = min(provisional_deadline, crossed[2])

        stopped = [item[6][2] for item in by_geometry.values() if item[6] is not None]
        decision_deadline = min(stopped) if stopped else self.range_end
        # An inherited live S order can decide this E before any newly
        # discovered order confirms. Such later geometry belongs to a later
        # lifecycle and must not enter this parent's eligibility ledger.
        if self.direction == "bullish" and continuous_deadline is not None:
            decision_deadline = min(decision_deadline, continuous_deadline)
        eligible = [
            item for item in by_geometry.values()
            if item[2] <= decision_deadline
        ]
        result = sorted(
            eligible,
            key=lambda item: (
                item[6][2] if item[6] is not None else self.range_end,
                self._reaction_first_time(item[1]),
            ),
        )
        self._order_candidates_cache[cache_key] = tuple(result)
        return result

    def _first_order(
        self, start: datetime, continuous_deadline: datetime | None = None,
    ) -> OrderMatch | None:
        candidates = [
            item for item in self.order_candidates(start, continuous_deadline)
            if item[6] is not None
        ]
        return candidates[0] if candidates else None

    def _blue_parent_superseded(self, parent: object, parent_stop: datetime) -> bool:
        """A confirmed later Red S closes an older Blue-E order lifecycle."""
        return str(getattr(parent, "family")) == "blue" and any(
            str(getattr(item, "color")) == "red"
            and getattr(item, "source_time") > getattr(parent, "source_time")
            and getattr(item, "decision_event_time") < parent_stop
            for item in self.s_zones
        )

    def _register_order_audit(
        self, parent_type: str, parent: object, parent_stop: datetime,
    ) -> None:
        if any(parent.source_time < reset <= parent_stop
               for reset in self.sequence_resets):
            return
        if (
            self.direction == "bullish" and parent_type == "E"
            and self._blue_parent_superseded(parent, parent_stop)
        ):
            # Enforce the same ownership rule during provisional discovery
            # and final audit. Otherwise a closed branch can seed a carried
            # order into another parent before final reconciliation.
            return
        inherited_owner = None
        if parent_type == "S":
            inherited_owner = self._unconsumed_s_order(parent, parent_stop)
        carried_owner = self._carried_order_for_parent(parent, parent_stop)
        continuous_deadline = None
        if parent_type == "S" and carried_owner is None:
            continuous_deadline = (
                inherited_owner[6][2]
                if inherited_owner is not None and inherited_owner[6] is not None
                else self.range_end
            )
        matches = self.order_candidates(
            parent_stop, continuous_deadline,
        )
        gate_owned = self._gate_owned_initial_order(parent_stop)
        if gate_owned is not None:
            gate_confirmation = gate_owned[2]
            matches = [
                item for item in matches
                if (
                    "reset-leg" in item[7]
                    or self._reaction_first_time(item[1]) <= gate_confirmation
                )
            ]
        gate_time = self.times[self._main_index(parent_stop)]
        ledger_gate = [
            entry for entry in self.order_audit.values()
            if self._reaction_first_time(entry["reaction"]) == gate_time
            and entry.get("stop_cross") is not None
            and entry["stop_cross"][2] >= parent_stop
        ]
        if ledger_gate:
            owner_confirmation = min(
                entry["confirmation_time"] for entry in ledger_gate
            )
            matches = [
                item for item in matches
                if (
                    "reset-leg" in item[7]
                    or self._reaction_first_time(item[1]) <= owner_confirmation
                )
            ]
        for match in matches:
            number, reaction, confirmation, level, source, source_time = match[:6]
            crossed, causes = match[6], match[7]
            reset_evidence = None
            if "reset-leg" in causes:
                if number == 0:
                    reset_evidence = (
                        None
                        if self._reset_by_proven_order(reaction, confirmation)
                        else (
                            (match[9], match[10])
                            if match[9] is not None and match[10] is not None
                            else None
                        )
                    )
                else:
                    reset_evidence = self._legacy_reset_leg_evidence(
                        reaction, parent_stop
                    )
            # Audit is an eligibility ledger, not a provisional-candidate log.
            # A geometric Order_B may legitimately have reaction number zero,
            # while a canonical reaction may still fail Reset ownership.  Admit
            # either only after at least one creation cause is proven.
            if "parent-stop" not in causes and reset_evidence is None:
                continue
            key = (
                int(getattr(reaction, "first_idx")),
                int(getattr(reaction, "break_idx")),
            )
            entry = self.order_audit.setdefault(key, {
                "reaction_number": number,
                "reaction": reaction,
                "confirmation_time": confirmation,
                "stop_level": level,
                "stop_source_index": source,
                "stop_source_time": source_time,
                "stop_cross": crossed,
                "causes": set(),
            })
            audit_causes = entry["causes"]
            assert isinstance(audit_causes, set)
            if "parent-stop" in causes:
                family = str(getattr(parent, "color", getattr(parent, "family", "")))
                number_value = getattr(parent, "number", None)
                parent_label = parent_type
                if parent_type == "E" and number_value is not None:
                    parent_label = f"E{number_value}"
                if parent.source_time in self.sequence_resets:
                    parent_label = f"StopAll{self.sequence_resets[parent.source_time]}"
                    family = ""
                audit_causes.add(
                    (
                        "parent-stop", parent_label, family, parent_stop,
                        getattr(parent, "source_time"),
                    )
                )
            if reset_evidence is not None:
                audit_causes.add((
                    "reset-leg", reset_evidence[0], reset_evidence[1],
                ))

    def _reset_by_proven_order(
        self, reaction: object, confirmation: datetime,
    ) -> bool:
        """Whether a provisional geometry is Reset by a proven live order."""
        proven = set(self.initial_order_audit)
        proven.update(
            identity for identity, entry in self.order_audit.items()
            if entry.get("causes")
        )
        first = self._reaction_first_time(reaction)
        left = bisect_left(self._opposite_reset_times, first)
        right = bisect_right(self._opposite_reset_times, confirmation)
        for _, reset in self._opposite_reset_events[left:right]:
            owner = self._opposite_by_first_index.get(
                int(getattr(reset, "from_first_idx"))
            )
            if owner is None:
                continue
            identity = (
                int(getattr(owner, "first_idx")),
                int(getattr(owner, "break_idx")),
            )
            if identity in proven:
                return True
        return False

    def _enrich_order_audit_reset_causes(self) -> None:
        """Attach established Reset evidence without changing E eligibility."""
        if not self.s_zones or not self.order_audit:
            return
        lifecycle_start = min(
            getattr(item, "decision_event_time") for item in self.s_zones
        )
        if self._audit_synthetic_order_cache is None:
            self.order_candidates(
                lifecycle_start, audit_legacy=True
            )
        reset_evidence: dict[tuple[int, int], tuple[datetime, datetime]] = {}
        for _, reaction, _, reset_time, reset_break in (
            self._audit_synthetic_order_cache or []
        ):
            if reset_time < lifecycle_start:
                continue
            identity = (
                int(getattr(reaction, "first_idx")),
                int(getattr(reaction, "break_idx")),
            )
            current = reset_evidence.get(identity)
            if current is None or reset_time < current[0]:
                reset_evidence[identity] = (reset_time, reset_break)
        for identity, (reset_time, reset_break) in reset_evidence.items():
            entry = self.order_audit.get(identity)
            if entry is None:
                continue
            causes = entry["causes"]
            assert isinstance(causes, set)
            causes.add(("reset-leg", reset_time, reset_break))

    def visual_order_lifecycle(
        self, start: datetime,
    ) -> list[tuple[int, object, datetime, Decimal, int, datetime,
                    tuple[int, datetime, datetime] | None, bool]]:
        """Return only orders admitted by the E lifecycle, including live ones.

        This is presentation/audit output.  It follows the same direct and
        Reset-leg replacement gates as ``_first_order`` but does not require a
        stop crossing, so a valid still-live order can be drawn without
        changing E calculation.
        """
        position = bisect_left(self._opposite_first_times, start)
        owner = None
        for order_position in range(position, len(self.opposite_reactions)):
            reaction = self.opposite_reactions[order_position]
            first = self._opposite_first_times[order_position]
            confirmation = self._opposite_confirmations[order_position]
            if first >= start and confirmation >= start:
                owner = (order_position + 1, reaction, confirmation, start)
                break
        if owner is None:
            return []

        lifecycle = []
        is_replacement = False
        while owner is not None:
            number, reaction, confirmation, context = owner
            level, source, source_time = self._order_stop(
                number, reaction, context
            )
            crossed = self._cross_order(confirmation, level)
            lifecycle.append(
                (
                    number, reaction, confirmation, level, source,
                    source_time, crossed, is_replacement,
                )
            )
            deadline = crossed[2] if crossed is not None else self.range_end
            owner = self._replacement_order(reaction, confirmation, deadline)
            is_replacement = True
        return lifecycle

    def _parent_stop(self, parent_type: str, parent: object) -> tuple[int, datetime] | None:
        if parent_type == "S":
            start = getattr(parent, "decision_event_time")
        else:
            # An E can only stop after the order-stop event that confirms it.
            start = getattr(parent, "decision_event_time")
        return self._first_parent_stop(start, _d(getattr(parent, "price")))

    def _cross_order(
        self, start: datetime, level: Decimal
    ) -> tuple[int, datetime, datetime] | None:
        cache_key = (start, level)
        if cache_key in self._cross_order_cache:
            return self._cross_order_cache[cache_key]
        left = bisect_left(self.lower_times, max(start, self.range_start))
        right = bisect_left(self.lower_times, self.range_end)
        position = (
            self._lower_cross_index.first_greater(left, right, level)
            if self.order_direction == "bearish"
            else self._lower_cross_index.first_less(left, right, level)
        )
        if position is None:
            self._cross_order_cache[cache_key] = None
            return None
        event = self.lower_times[position]
        index = self._main_index(event)
        result = index, getattr(self.candles[index], "timestamp"), event
        self._cross_order_cache[cache_key] = result
        return result

    def _unconsumed_s_order(
        self, parent: object, parent_stop: datetime
    ) -> OrderMatch | None:
        """Reuse a Blue S order whose stop did not decide the S itself."""
        if (
            str(getattr(parent, "color")) != "blue"
            or getattr(parent, "order_confirmation_time", None) is None
            or getattr(parent, "order_stop_level", None) is None
        ):
            return None
        confirmation = getattr(parent, "order_confirmation_time")
        stop_level = _d(getattr(parent, "order_stop_level"))
        crossed = self._cross_order(confirmation, stop_level)
        if crossed is None or crossed[2] < parent_stop:
            return None
        reaction = SimpleNamespace(
            mode=getattr(parent, "order_mode"),
            first_idx=getattr(parent, "order_first_index"),
            break_idx=getattr(parent, "order_break_index"),
            box_top=getattr(parent, "order_box_top"),
            box_top_source_idx=getattr(parent, "order_box_top_source_index"),
            box_bottom=getattr(parent, "order_box_bottom"),
            box_bottom_source_idx=getattr(parent, "order_box_bottom_source_index"),
        )
        return (
            int(getattr(parent, "order_reaction_number")),
            reaction,
            confirmation,
            stop_level,
            int(getattr(parent, "order_stop_source_index")),
            getattr(parent, "order_stop_source_time"),
            crossed,
            ("carried-live",), None, None, None,
        )

    def _active_prior_order(
        self, parent_stop: datetime
    ) -> OrderMatch | None:
        """Return the nearest already-formed order whose stop is still live."""
        right = bisect_left(self._opposite_first_times, parent_stop)
        for position in range(right - 1, -1, -1):
            reaction = self.opposite_reactions[position]
            confirmation = self._opposite_confirmations[position]
            if confirmation + self.timeframe < parent_stop:
                continue
            try:
                level, source, source_time = self._order_stop(
                    position + 1, reaction
                )
            except ValueError:
                continue
            crossed = self._cross_order(confirmation, level)
            if crossed is None or crossed[2] < parent_stop:
                continue
            return (
                position + 1, reaction, confirmation, level,
                source, source_time, crossed,
                ("carried-live",), None, None, None,
            )
        return None

    def _initial_order_match(
        self, entry: dict[str, object], causes: tuple[str, ...],
    ) -> OrderMatch:
        reaction = entry["reaction"]
        confirmation = entry["confirmation_time"]
        level = _d(entry["stop_level"])
        crossed = self._cross_order(confirmation, level)
        return (
            int(entry["reaction_number"]), reaction, confirmation, level,
            int(entry["stop_source_index"]), entry["stop_source_time"],
            crossed, causes, None, None, None,
        )

    def _gate_owned_initial_order(
        self, parent_stop: datetime,
    ) -> OrderMatch | None:
        """Keep an A-owned order that starts in the parent-stop candle.

        The already-open A lifecycle owns that candle.  A later ordinary
        Reaction cannot be relabeled as a new Order_A merely because the S/E
        parent stopped while the earlier order was still forming or live.
        """
        gate_time = self.times[self._main_index(parent_stop)]
        matches: list[OrderMatch] = []
        for entry in self.initial_order_audit.values():
            reaction = entry["reaction"]
            first = self._reaction_first_time(reaction)
            confirmation = entry["confirmation_time"]
            if first != gate_time or confirmation < parent_stop:
                continue
            match = self._initial_order_match(entry, ("carried-live",))
            crossed = match[6]
            if crossed is None or crossed[2] < parent_stop:
                continue
            matches.append(match)
        return min(
            matches,
            key=lambda item: (item[6][2], self._reaction_first_time(item[1])),
            default=None,
        )

    def _carried_order_for_parent(
        self, parent: object, parent_stop: datetime,
    ) -> OrderMatch | None:
        """Return an order formed and left live inside this parent lifecycle."""
        lifecycle_start = getattr(parent, "decision_event_time")
        matches: list[OrderMatch] = []
        for entry in self.order_audit.values():
            created_events: list[datetime] = []
            reset_evidence: tuple[datetime, datetime] | None = None
            for cause in entry.get("causes", set()):
                if cause[0] == "parent-stop":
                    created_events.append(cause[3])
                elif cause[0] == "reset-leg":
                    created_events.append(cause[1])
                    reset_evidence = (cause[1], cause[2])
            if not created_events:
                continue
            created = min(created_events)
            confirmation = entry["confirmation_time"]
            crossed = entry.get("stop_cross")
            if (
                created <= lifecycle_start
                or created >= parent_stop
                or confirmation > parent_stop
                or crossed is None
                or crossed[2] < parent_stop
            ):
                continue
            causes = (
                ("carried-live", "reset-leg")
                if reset_evidence is not None
                else ("carried-live",)
            )
            reaction = entry["reaction"]
            matches.append((
                int(entry["reaction_number"]), reaction, confirmation,
                _d(entry["stop_level"]), int(entry["stop_source_index"]),
                entry["stop_source_time"], crossed, causes, None,
                reset_evidence[0] if reset_evidence is not None else None,
                reset_evidence[1] if reset_evidence is not None else None,
            ))
        return min(
            matches,
            key=lambda item: (item[6][2], -int(getattr(item[1], "first_idx"))),
            default=None,
        )

    def _blocked_by_gate_owned_order(self, zone: EZone) -> bool:
        """Reject only a nested Order_A, while preserving its child lineage."""
        if "parent-stop" not in zone.order_causes or "reset-leg" in zone.order_causes:
            return False
        gate_owned = self._gate_owned_initial_order(zone.parent_stop_event_time)
        return (
            gate_owned is not None
            and gate_owned[2] < zone.order_first_time
        )

    def _reset_evidence_for_order(
        self, first_index: int, break_index: int,
    ) -> tuple[datetime, datetime] | None:
        for _, reaction, _, reset_time, reset_break in (
            self._synthetic_order_cache or []
        ):
            if (
                int(getattr(reaction, "first_idx")) == first_index
                and int(getattr(reaction, "break_idx")) == break_index
            ):
                return reset_time, reset_break
        return None

    def _extreme_between(self, start: datetime, end: datetime) -> tuple[int, datetime, Decimal]:
        # E source ownership is candle-based: include the complete main candle
        # containing the parent stop and the complete main candle containing
        # the order stop. Lower-timeframe chronology decides whether each stop
        # happened, but it must not truncate either boundary candle's OHLC.
        start_index = max(self.start_index, self._main_index(start))
        end_index = min(self.end_index, self._main_index(end))
        source = self.candles[start_index]
        value = self._stop_value(source)
        for item in self.candles[start_index + 1 : end_index + 1]:
            candidate = self._stop_value(item)
            better = candidate < value if self.direction == "bullish" else candidate > value
            if better:
                source, value = item, candidate
        return int(getattr(source, "index")), getattr(source, "timestamp"), value

    def _zone(
        self, family: str, number: int, parent_type: str,
        parent: object, stop_event: datetime,
    ) -> EZone | None:
        # Every E-space cycle starts at the strict parent stop. The order First
        # must itself strictly cross the active parent/reset boundary.
        inherited = (
            self._unconsumed_s_order(parent, stop_event)
            if parent_type == "S"
            else None
        )
        gate_owned = self._gate_owned_initial_order(stop_event)
        carried = self._carried_order_for_parent(parent, stop_event)
        self._register_order_audit(parent_type, parent, stop_event)
        # A stopped E opens a new direct search at its own stop candle. An
        # older order formed before that event cannot replace the first valid
        # post-stop order. S may still pass its explicitly unconsumed Blue
        # order through the dedicated inheritance rule above.
        direct = self._first_order(
            stop_event,
            (
                inherited[6][2]
                if parent_type == "S" and carried is None
                and inherited is not None and inherited[6] is not None
                else self.range_end
                if parent_type == "S" and carried is None
                else None
            ),
        )
        choices = [
            item for item in (direct, inherited, carried)
            if item is not None and item[6] is not None
        ]
        order_match = min(
            choices,
            key=lambda item: (item[6][2], -int(getattr(item[1], "first_idx"))),
            default=None,
        )
        if order_match is None:
            return None
        (
            order_number, order, order_confirmation, order_stop,
            stop_source, stop_source_time, crossed, order_causes,
            order_parent_stop_cause_time, order_reset_leg_reset_time,
            order_reset_leg_break_time,
        ) = order_match
        if crossed is None:
            return None
        order_decision_index, order_decision_time, order_decision_event = crossed
        decision_event = max(stop_event, order_decision_event)
        decision_index = self._main_index(decision_event)
        decision_time = getattr(self.candles[decision_index], "timestamp")
        source_index, source_time, price = self._extreme_between(stop_event, decision_event)
        parent_stop_index = self._main_index(stop_event)
        order_first_index = int(getattr(order, "first_idx"))
        top_source = int(getattr(order, "box_top_source_idx"))
        bottom_source = int(getattr(order, "box_bottom_source_idx"))
        return EZone(
            direction=self.direction,
            family=family,
            number=number,
            parent_type=parent_type,
            parent_source_index=int(getattr(parent, "source_index")),
            parent_source_time=getattr(parent, "source_time"),
            parent_price=_d(getattr(parent, "price")),
            parent_stop_index=parent_stop_index,
            parent_stop_time=getattr(self.candles[parent_stop_index], "timestamp"),
            parent_stop_event_time=stop_event,
            order_direction=self.order_direction,
            order_reaction_number=order_number,
            order_mode=str(getattr(order, "mode")),
            order_causes=order_causes,
            order_parent_stop_cause_time=order_parent_stop_cause_time,
            order_reset_leg_reset_time=order_reset_leg_reset_time,
            order_reset_leg_break_time=order_reset_leg_break_time,
            order_first_index=order_first_index,
            order_first_time=getattr(self.candles[order_first_index], "timestamp"),
            order_break_index=int(getattr(order, "break_idx")),
            order_break_time=getattr(self.candles[int(getattr(order, "break_idx"))], "timestamp"),
            order_confirmation_time=order_confirmation,
            order_box_top=_d(getattr(order, "box_top")),
            order_box_top_source_index=top_source,
            order_box_top_source_time=getattr(self.candles[top_source], "timestamp"),
            order_box_bottom=_d(getattr(order, "box_bottom")),
            order_box_bottom_source_index=bottom_source,
            order_box_bottom_source_time=getattr(self.candles[bottom_source], "timestamp"),
            order_stop_level=order_stop,
            order_stop_source_index=stop_source,
            order_stop_source_time=stop_source_time,
            source_index=source_index,
            source_time=source_time,
            price=price,
            decision_index=decision_index,
            decision_time=decision_time,
            decision_event_time=decision_event,
        )

    def detect(self) -> list[EZone]:
        # Reconciliation may rerun this detector with accepted StopAll gates.
        # Do not seed the new pass with future orders from the previous pass.
        self.order_audit.clear()
        self.visual_lifecycle_starts.clear()
        candidates: list[EZone] = []

        # Discover S-owned orders before walking recursive E chains.  A valid
        # order formed inside an E parent's lifetime must remain available even
        # when that S branch is reconciled later than the E branch.
        for s_zone in self.s_zones:
            stop = self._parent_stop("S", s_zone)
            if stop is not None:
                self._register_order_audit("S", s_zone, stop[1])

        for s_zone in self.s_zones:
            stop = self._parent_stop("S", s_zone)
            if stop is None:
                continue
            _, stop_event = stop

            # Every fully formed S starts an independent E chain. E1 remains
            # visible when E2 is later formed; numbering is advanced only by
            # a strict stop of the immediately previous E in that chain.
            family = str(getattr(s_zone, "color"))
            number = 1

            parent_type: str = "S"
            parent: object = s_zone
            chain_sources: set[int] = set()
            while True:
                zone = self._zone(family, number, parent_type, parent, stop_event)
                if zone is None:
                    break
                if zone.source_index in chain_sources:
                    break
                candidates.append(zone)
                chain_sources.add(zone.source_index)
                parent_type, parent = "E", zone
                next_stop = self._parent_stop("E", zone)
                if next_stop is None:
                    break
                _, stop_event = next_stop
                number += 1
        # Resolve competing chains chronologically.  A stopped E is removed
        # from the active set immediately; it remains only as historical
        # output and cannot affect a later family or number.
        by_source: dict[int, list[EZone]] = {}
        for zone in candidates:
            by_source.setdefault(zone.source_index, []).append(zone)
        # A later E continuation can supersede a provisional E that was
        # started directly from an S before the continuation was confirmed.
        # Keep the later, deeper (bullish) / higher (bearish) structure.  This
        # This prevents a provisional S-owned object from consuming the active
        # chain before the later confirmed continuation.
        pending = sorted(
            by_source.values(),
            key=lambda item: (
                min(zone.source_time for zone in item),
                min(zone.decision_event_time for zone in item),
            ),
        )
        numbered: list[EZone] = []
        active: list[EZone] = []
        sequence_start: datetime | None = None

        candidates_by_source_time = {
            (item.source_index, item.source_time): item
            for item in candidates
        }

        children_by_parent: dict[tuple[int, object], list[EZone]] = {}
        s_children_by_source: dict[tuple[int, object], list[EZone]] = {}
        for item in candidates:
            if item.parent_type == "E":
                children_by_parent.setdefault(
                    (item.parent_source_index, item.parent_source_time), []
                ).append(item)
            elif item.parent_type == "S":
                s_children_by_source.setdefault(
                    (item.source_index, item.source_time), []
                ).append(item)

        def valid_order(zone: EZone) -> bool:
            if self._blocked_by_gate_owned_order(zone):
                return False
            if (
                zone.parent_type == "S"
                or zone.order_mode != "B"
                or zone.family != "blue"
            ):
                return True
            children = children_by_parent.get(
                (zone.source_index, zone.source_time), []
            )
            for child in children:
                for competing in s_children_by_source.get(
                    (child.source_index, child.source_time), []
                ):
                    if competing.decision_event_time <= child.decision_event_time:
                        return False
            return True

        def invalidated_only_by_future_s(zone: EZone) -> bool:
            if valid_order(zone) or zone.parent_type != "E":
                return False
            children = children_by_parent.get(
                (zone.source_index, zone.source_time), []
            )
            parent_times = {
                competing.parent_source_time
                for child in children
                for competing in s_children_by_source.get(
                    (child.source_index, child.source_time), []
                )
                if competing.decision_event_time <= child.decision_event_time
            }
            return any(value > zone.source_time for value in parent_times)

        def parent_active(zone: EZone, seen: set[tuple[int, datetime]] | None = None) -> bool:
            if zone.parent_type == "S":
                parent_s = next(
                    (
                        item for item in self.s_zones
                        if int(getattr(item, "source_index"))
                        == zone.parent_source_index
                        and getattr(item, "source_time")
                        == zone.parent_source_time
                    ),
                    None,
                )
                if parent_s is None:
                    return False
                if sequence_start is not None and (
                    parent_s.source_time <= sequence_start
                    or parent_s.a_source_time < sequence_start
                ):
                    return False
                prior_e = [
                    item for item in numbered
                    if getattr(item, "source_time")
                    < zone.source_time
                    and (sequence_start is None or item.source_time > sequence_start)
                ]
                if not prior_e:
                    return True
                prior = max(
                    prior_e, key=lambda item: getattr(item, "source_time")
                )
                rebuilt_after_e = (
                    getattr(parent_s, "source_time")
                    > getattr(prior, "source_time")
                    and getattr(parent_s, "a_source_time")
                    >= getattr(prior, "source_time")
                )
                # A still-unconsumed Red S is not invalidated by a nested
                # Blue E. Its later strict stop owns the Red transition.
                dominant_s = (
                    str(getattr(parent_s, "color")) == "red"
                    and prior.family == "blue"
                    and parent_s.source_time < prior.source_time
                    and not any(
                        item.parent_type == "S"
                        and item.parent_source_time == zone.parent_source_time
                        for item in numbered
                    )
                )
                return rebuilt_after_e or dominant_s
            if zone.parent_source_time == sequence_start:
                # The StopAll source is a valid order gate, but never an
                # active E whose family/number could leak across the reset.
                return True
            if any(
                item.source_index == zone.parent_source_index
                and item.source_time == zone.parent_source_time
                for item in active
            ):
                return True
            identity = (zone.parent_source_index, zone.parent_source_time)
            if seen is None:
                seen = set()
            if identity in seen:
                return False
            seen.add(identity)
            skipped_parent = candidates_by_source_time.get(identity)
            return (
                skipped_parent is not None
                and not valid_order(skipped_parent)
                and parent_active(skipped_parent, seen)
            )

        def stopped_by(zone: EZone, prior: EZone) -> bool:
            if zone.decision_event_time <= prior.decision_event_time:
                return False
            if self.direction == "bullish":
                return zone.price < prior.price
            return zone.price > prior.price

        for group in pending:
            eligible = [
                item for item in group
                if valid_order(item) and parent_active(item)
            ]
            if not eligible:
                continue
            # A lower-priority S cannot steal an active E continuation.
            # Red S may supersede Blue E, but no S supersedes Red E.
            # Color follows the accepted stopped parent's reconciled family.
            eligible = [
                item
                for item in eligible
                if not (
                    item.parent_type == "S"
                    and any(
                        stopped_by(item, owner)
                        and (owner.family == "red" or item.family == "blue")
                        and any(
                            child.parent_type == "E"
                            and child.parent_source_index == owner.source_index
                            and child.parent_source_time == owner.source_time
                            and child.decision_event_time
                            >= item.decision_event_time
                            for child in candidates
                        )
                        for owner in active
                    )
                )
            ]
            if not eligible:
                continue
            current_owners = [
                item for item in eligible
                if not (
                    item.parent_type == "E"
                    and item.family == "blue"
                    and any(
                        str(getattr(s_zone, "color")) == "red"
                        and getattr(s_zone, "source_time")
                        > item.parent_source_time
                        and getattr(s_zone, "decision_event_time")
                        < item.parent_stop_event_time
                        for s_zone in self.s_zones
                    )
                )
            ]
            if current_owners:
                eligible = current_owners
            def ownership_priority(item: EZone) -> int:
                parent = next((prior for prior in active
                    if item.parent_type == "E"
                    and prior.source_time == item.parent_source_time), None)
                parent_family = parent.family if parent else item.family
                return self._SEQUENCE_PRIORITY[(item.parent_type, parent_family)]

            zone = min(
                eligible,
                key=lambda item: (
                    item.decision_event_time,
                    -ownership_priority(item),
                    item.parent_stop_event_time,
                ),
            )
            stopped_by_family: dict[str, list[EZone]] = {"red": [], "blue": []}
            for prior in active:
                if stopped_by(zone, prior):
                    stopped_by_family[prior.family].append(prior)

            parent_identity = (zone.parent_source_index, zone.parent_source_time)
            parent_is_active = (
                zone.parent_type == "S"
                or zone.parent_source_time == sequence_start
            ) or any(
                (item.source_index, item.source_time) == parent_identity
                for item in active
            )
            if not parent_is_active:
                reset_evidence = self._reset_evidence_for_order(
                    zone.order_first_index, zone.order_break_index
                )
                if reset_evidence is not None:
                    zone = replace(
                        zone,
                        order_causes=("reset-leg",),
                        order_parent_stop_cause_time=None,
                        order_reset_leg_reset_time=reset_evidence[0],
                        order_reset_leg_break_time=reset_evidence[1],
                    )

            owner = next((item for item in active
                          if zone.parent_type == "E"
                          and item.source_time == zone.parent_source_time), None)
            # Color follows the accepted stopped parent, not merely the most
            # recent S. A still-unbroken Red S does not recolor a nested E.
            parent_family = owner.family if owner is not None else zone.family

            if parent_family == "red":
                family = "red"
                number = (
                    max(item.number for item in stopped_by_family["red"]) + 1
                    if stopped_by_family["red"]
                    else 1
                )
            elif stopped_by_family["red"]:
                family = "red"
                number = max(item.number for item in stopped_by_family["red"]) + 1
            elif parent_family == "blue":
                family = "blue"
                number = (
                    max(item.number for item in stopped_by_family["blue"]) + 1
                    if stopped_by_family["blue"]
                    else 1
                )
            elif stopped_by_family["blue"]:
                family = "blue"
                number = max(item.number for item in stopped_by_family["blue"]) + 1
            else:
                family = zone.family
                number = 1
            stopped_ids = {
                (item.source_index, item.source_time)
                for values in stopped_by_family.values() for item in values
            }
            active = [
                item for item in active
                if (item.source_index, item.source_time) not in stopped_ids
            ]
            numbered_zone = replace(zone, family=family, number=number)
            numbered.append(numbered_zone)
            if zone.source_time in self.sequence_resets:
                active.clear()
                sequence_start = zone.source_time
            else:
                active.append(numbered_zone)
        def collect_lineage(zone: EZone, seen: set[tuple[int, datetime]]) -> None:
            identity = (zone.source_index, zone.source_time)
            if identity in seen:
                return
            seen.add(identity)
            self.visual_lifecycle_starts.add(zone.parent_stop_event_time)
            if zone.parent_type == "S":
                return
            parent = candidates_by_source_time.get(
                (zone.parent_source_index, zone.parent_source_time)
            )
            if parent is not None:
                collect_lineage(parent, seen)

        numbered_ids = {
            (item.source_index, item.source_time) for item in numbered
        }
        numbered.extend(
            item for item in candidates
            if invalidated_only_by_future_s(item)
            and (item.source_index, item.source_time) not in numbered_ids
            and not any(item.parent_source_time < reset <= item.source_time
                        for reset in self.sequence_resets)
        )

        lineage_seen: set[tuple[int, datetime]] = set()
        for zone in numbered:
            collect_lineage(zone, lineage_seen)

        numbered = [replace(item, parent_type="StopAll")
                    if item.parent_type == "E"
                    and item.parent_source_time in self.sequence_resets
                    else item for item in numbered]

        # Audit only accepted S/E state. Provisional candidate chains must not
        # create visible or reported order genders.
        self.order_audit.clear()
        accepted_parents: list[tuple[str, object]] = [
            ("S", item) for item in self.s_zones
        ] + [("StopAll" if item.source_time in self.sequence_resets else "E", item)
             for item in numbered]
        for parent_type, parent in accepted_parents:
            stop = self._parent_stop(parent_type, parent)
            if stop is None:
                continue
            if parent_type == "E":
                # A later accepted Red S owns the behavioral color and closes
                # older Blue-E continuation state. The historical E remains
                # visible, but its later price crossing cannot open an order.
                if self._blue_parent_superseded(parent, stop[1]):
                    continue
            self._register_order_audit(parent_type, parent, stop[1])

        # Every order embedded in an accepted E is effective by definition.
        # Keep it in audit even when its provisional parent was skipped and
        # the child was reattached to the nearest active ancestor.
        for zone in numbered:
            identity = (zone.order_first_index, zone.order_break_index)
            if identity in self.order_audit:
                continue
            reaction = self._opposite_by_first_index.get(zone.order_first_index)
            if (
                reaction is None
                or int(getattr(reaction, "break_idx")) != zone.order_break_index
            ):
                continue
            causes: set[tuple[object, ...]] = set()
            if zone.order_parent_stop_cause_time is not None:
                parent_label = zone.parent_type
                if zone.parent_type == "E":
                    parent_zone = next(
                        (
                            item for item in numbered
                            if item.source_index == zone.parent_source_index
                            and item.source_time == zone.parent_source_time
                        ),
                        None,
                    )
                    if parent_zone is not None:
                        parent_label = f"E{parent_zone.number}"
                if zone.parent_source_time in self.sequence_resets:
                    parent_label = f"StopAll{self.sequence_resets[zone.parent_source_time]}"
                causes.add((
                    "parent-stop",
                    parent_label,
                    "" if zone.parent_source_time in self.sequence_resets else zone.family,
                    zone.parent_stop_event_time,
                    zone.parent_source_time,
                ))
            if (
                zone.order_reset_leg_reset_time is not None
                and zone.order_reset_leg_break_time is not None
            ):
                causes.add((
                    "reset-leg",
                    zone.order_reset_leg_reset_time,
                    zone.order_reset_leg_break_time,
                ))
            self.order_audit[identity] = {
                "reaction_number": zone.order_reaction_number,
                "reaction": reaction,
                "confirmation_time": zone.order_confirmation_time,
                "stop_level": zone.order_stop_level,
                "stop_source_index": zone.order_stop_source_index,
                "stop_source_time": zone.order_stop_source_time,
                "stop_cross": (
                    zone.decision_index,
                    zone.decision_time,
                    zone.decision_event_time,
                ),
                "causes": causes,
            }

        self._enrich_order_audit_reset_causes()

        # A retained order can have Reset-leg evidence predating its new
        # StopAll gate. Preserve that proven secondary cause in the emitted
        # object as well as the ledger; it never changes selection or weight.
        for index, zone in enumerate(numbered):
            if zone.parent_type != "StopAll":
                continue
            entry = self.order_audit.get((zone.order_first_index, zone.order_break_index))
            reset_causes = sorted(cause for cause in entry["causes"]
                                  if cause[0] == "reset-leg") if entry else []
            if reset_causes and "reset-leg" not in zone.order_causes:
                cause = reset_causes[0]
                numbered[index] = replace(
                    zone, order_causes=(*zone.order_causes, "reset-leg"),
                    order_reset_leg_reset_time=cause[1],
                    order_reset_leg_break_time=cause[2],
                )

        return sorted(
            numbered,
            key=lambda item: (item.source_time, item.source_index),
        )


def detect_e_zones(
    direction: str,
    trend_reactions: Sequence[object],
    opposite_reactions: Sequence[object],
    s_zones: Sequence[object],
    trend_resets: Sequence[object],
    opposite_resets: Sequence[object],
    candles: Sequence[object],
    lower_candles: Sequence[object],
    timeframe_seconds: int,
    start_index: int = 0,
    end_index: int | None = None,
    geometry_finder: Callable[[str, int, int], object | None] | None = None,
    direct_geometry_finder: Callable[
        [str, int, int, datetime], object | None
    ] | None = None,
    blocked_order_first_times: set[datetime] | None = None,
    initial_order_audit: dict[tuple[int, int], dict[str, object]] | None = None,
    reset_geometry_finder: Callable[
        [str, int, int, int], object | None
    ] | None = None,
) -> list[EZone]:
    return EDetector(
        direction,
        trend_reactions,
        opposite_reactions,
        s_zones,
        trend_resets,
        opposite_resets,
        candles,
        lower_candles,
        timeframe_seconds,
        start_index,
        end_index,
        geometry_finder,
        direct_geometry_finder,
        blocked_order_first_times,
        initial_order_audit,
        reset_geometry_finder,
    ).detect()
