"""Recursive E-zone and Order calculation from authoritative S/Reaction state.

Owns parent-stop, carried-live, and Reset-leg Order discovery; recursive E
chains; accepted Order causes; and E family/number reconciliation. Cross-stage
public visibility and StopAll grouping are delegated to the lifecycle engine.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Callable, Sequence

from core_utils import as_decimal, order_identity, reaction_identity
from direction_policy import policy_for


E_ZONE_VERSION = "6.6.2"


@dataclass(frozen=True, slots=True)
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


class EZoneDetector:
    def __init__(
        self,
        direction: str,
        trend_reactions: Sequence[object],
        opposite_reactions: Sequence[object],
        s_zones: Sequence[object],
        trend_resets: Sequence[object],
        opposite_resets: Sequence[object],
        chronology: object,
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
        sequence_priority: Callable[[str, str], int] | None = None,
        invalid_s_root_identities: set[tuple[datetime, int]] | None = None,
    ) -> None:
        if direction not in {"bullish", "bearish"}:
            raise ValueError("Direction must be 'bullish' or 'bearish'.")
        self.direction = direction
        self.policy = policy_for(direction)
        if sequence_priority is None:
            raise ValueError("EZoneDetector requires the shared sequence-priority resolver.")
        self.sequence_priority = sequence_priority
        self.invalid_s_root_identities = set(invalid_s_root_identities or set())
        self.sequence_resets = dict(sequence_resets or {})
        self._sequence_reset_times = sorted(self.sequence_resets)
        self.order_direction = chronology.opposite_direction(direction)
        self.chronology = chronology
        self.trend_reactions = list(trend_reactions)
        self.opposite_reactions = list(opposite_reactions)
        self.s_zones = sorted(
            s_zones,
            key=lambda item: (
                getattr(item, "source_time"),
                int(getattr(item, "source_index")),
            ),
        )
        red_s_events = [
            (getattr(item, "source_time"), getattr(item, "decision_event_time"))
            for item in self.s_zones
            if str(getattr(item, "color")) == "red"
        ]
        self._red_s_source_times = [item[0] for item in red_s_events]
        self._red_s_suffix_min_decision: list[datetime] = []
        suffix_min: datetime | None = None
        for _, decision_time in reversed(red_s_events):
            if suffix_min is None or decision_time < suffix_min:
                suffix_min = decision_time
            self._red_s_suffix_min_decision.append(suffix_min)
        self._red_s_suffix_min_decision.reverse()
        self.opposite_resets = sorted(opposite_resets, key=self._reset_time)
        self.candles = chronology.candles
        self.lower = chronology.seconds
        self.lower_times = chronology.second_times
        self.lower_index = chronology.lower_index
        self.timeframe = chronology.timeframe
        self.times = chronology.times
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
        self._reset_leg_geometry_cache: dict[
            tuple[int, datetime], tuple[datetime, Decimal] | None
        ] = {}
        self._order_candidates_cache: dict[
            tuple[datetime, datetime | None, bool, bool, bool], tuple[OrderMatch, ...]
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
        self._consumed_s_evidence: list[tuple[object, tuple[int, datetime]]] = []
        self._last_candidate_zones: list[EZone] = []

    def _reset_time(self, reset: object) -> datetime:
        return self.chronology.reset_time(reset)

    def _main_index(self, value: datetime) -> int:
        return self.chronology.main_index(value, clamp=True)


    def _first_cross_position(
        self, left: int, right: int, level: Decimal, *, less: bool
    ) -> int | None:
        """Return the first strict lower-timeframe crossing in [left, right)."""
        if self.lower_index is not None:
            return (
                self.lower_index.first_less(left, right, level)
                if less
                else self.lower_index.first_greater(left, right, level)
            )
        field = "low" if less else "high"
        for position in range(left, right):
            value = as_decimal(getattr(self.lower[position], field))
            if value < level if less else value > level:
                return position
        return None

    def _stop_value(self, item: object) -> Decimal:
        return as_decimal(getattr(item, self.policy.extreme_attr))


    def _first_parent_stop(
        self, source_time: datetime, level: Decimal
    ) -> tuple[int, datetime] | None:
        left = bisect_left(self.lower_times, max(source_time, self.range_start))
        right = bisect_left(self.lower_times, self.range_end)
        position = self._first_cross_position(
            left, right, level, less=self.direction == "bullish"
        )
        if position is None:
            return None
        event = self.lower_times[position]
        return self._main_index(event), event

    def _confirmation_for(self, reaction: object, direction: str) -> datetime:
        return self.chronology.reaction_confirmation(direction, reaction)

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
        position = self._first_cross_position(
            left, right, level, less=self.direction == "bullish"
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
        result = any(
            not bool(getattr(self._trend_by_confirmation[position][2], "behavior_internal", False))
            for position in range(left, right)
        )
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
            if geometry_first in self.blocked_order_first_times:
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
                self._order_b_geometry_cache[cache_key] = result
                return result

            # Reset-leg local geometry is only a search aid; without an exact
            # published Reaction identity it cannot create an Order.
            next_index = int(getattr(geometry, "first_idx")) + 1
            if next_index > end_index:
                break
            gate_event = self.times[next_index]
            continue

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
                if (
                    first >= gate_time
                    and confirmation >= crossing
                    and confirmation < owner_stop_event
                ):
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
            # Audit and calculation use the same Reset-leg evidence contract.
            # A behavior-internal trend Reaction cannot unlock Order_B merely
            # because local geometry can rediscover it.
            aligned = self._reset_leg_has_simple_trend_reaction(
                leg_start, crossing
            )
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


    def _order_stop(
        self, number: int, reaction: object, context_start: datetime | None = None,
    ) -> tuple[Decimal, int, datetime]:
        del context_start  # Provenance never manufactures a context-only stop.
        return self.chronology.canonical_order_stop(
            self.order_direction,
            number,
            reaction,
            self.opposite_reactions,
            start_index=self.start_index,
        )

    def order_stop(
        self, reaction_number: int, reaction: object
    ) -> tuple[Decimal, int, datetime]:
        """Public audit API for canonical Order stop provenance."""
        return self._order_stop(reaction_number, reaction)


    def _first_healthy_direct_geometry(
        self, start: datetime, allow_bounded_continue: bool = False,
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

            identity = (
                int(getattr(candidate, "first_idx")),
                int(getattr(candidate, "break_idx")),
            )
            canonical_position = next((
                pos for pos, item in enumerate(self.opposite_reactions)
                if (
                    int(getattr(item, "first_idx")),
                    int(getattr(item, "break_idx")),
                ) == identity
            ), None)
            if canonical_position is None:
                # Only the S->E parent-stop path may admit a noncanonical
                # bounded Reaction, and only when exact gate chronology proves
                # continuation of the already-open post-Reset leg.
                if (
                    allow_bounded_continue
                    and getattr(candidate, "order_gate_decision", None) == "continue"
                ):
                    return 0, candidate, confirmation
                search_index = int(getattr(candidate, "first_idx")) + 1
                search_event = first
                continue
            candidate = self.opposite_reactions[canonical_position]
            number = canonical_position + 1
            confirmation = self._opposite_confirmations[canonical_position]
            return number, candidate, confirmation
        return None

    def _synthetic_reset_leg_orders(
        self, start: datetime, audit_legacy: bool
    ) -> list[tuple[int, object, datetime, datetime, datetime]]:
        """Return Reset-leg orders discovered from bounded post-Reset geometry."""
        selected_cache = (
            self._audit_synthetic_order_cache
            if audit_legacy
            else self._synthetic_order_cache
        )
        if selected_cache is not None:
            return [item for item in selected_cache if item[3] >= start]
        if self.geometry_finder is None:
            return []

        all_synthetic: list[
            tuple[int, object, datetime, datetime, datetime]
        ] = []
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
                    existing is None
                    or int(getattr(existing, "break_idx"))
                    != int(getattr(geometry, "break_idx"))
                ):
                    continue
                geometry = existing
                number = self.opposite_reactions.index(existing) + 1
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
        return [item for item in all_synthetic if item[3] >= start]

    def _trend_leg_direct_order(
        self, start: datetime,
    ) -> tuple[int, object, datetime] | None:
        """Return bounded direct Order_A after a newly confirmed trend leg.

        A stopped E may be followed by a fresh same-direction Reaction before
        the next opposite public Reaction exists.  That trend confirmation
        establishes the new forming-leg boundary.  The first bounded opposite
        geometry after that exact confirmation may own direct Order_A when the
        shared gate resolver proves ``continue``.  This is not Reset-leg
        Order_B evidence and therefore does not relax Reset-leg canonicality.
        """
        if self.direct_geometry_finder is None:
            return None
        position = bisect_right(self._trend_confirmation_times, start)
        while position < len(self._trend_by_confirmation):
            confirmation, first_time, trend = self._trend_by_confirmation[position]
            position += 1
            if first_time <= start:
                continue
            if bool(getattr(trend, "behavior_internal", False)):
                continue
            break_index = int(getattr(trend, "break_idx"))
            candidate = self.direct_geometry_finder(
                self.order_direction, break_index, self.end_index, confirmation
            )
            if candidate is None:
                continue
            if getattr(candidate, "order_gate_decision", None) != "continue":
                continue
            candidate_confirmation = self._confirmation_for(
                candidate, self.order_direction
            )
            if self._reaction_first_time(candidate) <= confirmation:
                continue
            identity = (
                int(getattr(candidate, "first_idx")),
                int(getattr(candidate, "break_idx")),
            )
            canonical_position = next((
                index for index, reaction in enumerate(self.opposite_reactions)
                if (
                    int(getattr(reaction, "first_idx")),
                    int(getattr(reaction, "break_idx")),
                ) == identity
            ), None)
            if canonical_position is not None:
                return (
                    canonical_position + 1,
                    self.opposite_reactions[canonical_position],
                    self._opposite_confirmations[canonical_position],
                )
            return 0, candidate, candidate_confirmation
        return None

    def _direct_parent_stop_order(
        self,
        start: datetime,
        continuous_deadline: datetime | None,
        allow_bounded_continue: bool,
    ) -> tuple[int, object, datetime] | None:
        """Select the direct parent-stop Order without Reset-leg evidence."""
        gate_time = self.times[self._main_index(start)]
        geometric_direct = self._first_healthy_direct_geometry(
            start, allow_bounded_continue
        )
        direct_position = bisect_left(self._opposite_first_times, gate_time)
        while (
            direct_position < len(self.opposite_reactions)
            and self._opposite_first_times[direct_position]
            in self.blocked_order_first_times
            and self._opposite_first_times[direct_position] == gate_time
        ):
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
            if geometric_direct is not None
            else None
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
        independent_cross = None
        if independent is not None:
            independent_level, _, _ = self._order_stop(
                independent[0], independent[1]
            )
            independent_cross = self._cross_order(
                independent[2], independent_level
            )

        direct_pool: list[tuple[int, object, datetime]] = []
        if prefer_geometric:
            direct_pool.append(geometric_direct)
        elif (
            allow_bounded_continue
            and geometric_direct is not None
            and geometric_direct[0] == 0
            and geometric_gate_decision == "continue"
            and (
                independent is None
                or self._reaction_first_time(geometric_direct[1])
                < self._reaction_first_time(independent[1])
            )
        ):
            direct_pool.append(geometric_direct)
        elif (
            geometric_direct is not None
            and independent_cross is None
            and (
                independent is None
                or self._reaction_first_time(geometric_direct[1])
                < self._reaction_first_time(independent[1])
            )
        ):
            direct_pool.append(geometric_direct)
        elif independent is not None:
            direct_pool.append(independent)

        if not direct_pool:
            return None
        return min(
            direct_pool,
            key=lambda item: (self._reaction_first_time(item[1]), item[2]),
        )

    def _merge_order_candidate(
        self,
        by_geometry: dict[tuple[int, int], OrderMatch],
        number: int,
        reaction: object,
        confirmation: datetime,
        cause: str,
        *,
        parent_stop_cause_time: datetime | None = None,
        reset_time: datetime | None = None,
        reset_break: datetime | None = None,
    ) -> OrderMatch:
        """Merge one provenance cause into a single physical Order identity."""
        level, source, source_time = self._order_stop(number, reaction)
        crossed = self._cross_order(confirmation, level)
        key = reaction_identity(reaction)
        existing = by_geometry.get(key)
        existing_causes = existing[7] if existing is not None else ()
        causes = tuple(dict.fromkeys((*existing_causes, cause)))
        if cause == "parent-stop":
            parent_cause = parent_stop_cause_time
            reset_cause_time = existing[9] if existing is not None else None
            reset_cause_break = existing[10] if existing is not None else None
        else:
            parent_cause = existing[8] if existing is not None else None
            reset_cause_time = reset_time
            reset_cause_break = reset_break
        match: OrderMatch = (
            number,
            reaction,
            confirmation,
            level,
            source,
            source_time,
            crossed,
            causes,
            parent_cause,
            reset_cause_time,
            reset_cause_break,
        )
        by_geometry[key] = match
        return match

    def _add_canonical_reset_leg_orders(
        self,
        by_geometry: dict[tuple[int, int], OrderMatch],
        start: datetime,
        provisional_deadline: datetime,
        audit_legacy: bool,
    ) -> datetime:
        """Merge canonical Reset-leg evidence up to the current decision bound."""
        for position, reaction in enumerate(self.opposite_reactions):
            confirmation = self._opposite_confirmations[position]
            if confirmation < start:
                continue
            if confirmation > provisional_deadline:
                break
            evidence = (
                self._legacy_reset_leg_evidence(reaction, start)
                if audit_legacy
                else self._reset_leg_evidence(reaction, start)
            )
            if evidence is None:
                continue
            reset_time, reset_break = evidence
            match = self._merge_order_candidate(
                by_geometry,
                position + 1,
                reaction,
                confirmation,
                "reset-leg",
                reset_time=reset_time,
                reset_break=reset_break,
            )
            if match[6] is not None:
                provisional_deadline = min(
                    provisional_deadline, match[6][2]
                )
        return provisional_deadline

    def order_candidates(
        self,
        start: datetime,
        continuous_deadline: datetime | None = None,
        audit_legacy: bool = False,
        allow_bounded_continue: bool = False,
        allow_trend_leg_continue: bool = False,
    ) -> list[OrderMatch]:
        """Return every valid E-space Order formed before this E decision."""
        cache_key = (
            start,
            continuous_deadline,
            audit_legacy,
            allow_bounded_continue,
            allow_trend_leg_continue,
        )
        cached = self._order_candidates_cache.get(cache_key)
        if cached is not None:
            return list(cached)

        by_geometry: dict[tuple[int, int], OrderMatch] = {}
        direct = self._direct_parent_stop_order(
            start, continuous_deadline, allow_bounded_continue
        )
        if direct is not None:
            self._merge_order_candidate(
                by_geometry,
                *direct,
                "parent-stop",
                parent_stop_cause_time=start,
            )

        if allow_trend_leg_continue:
            trend_direct = self._trend_leg_direct_order(start)
            if trend_direct is not None:
                self._merge_order_candidate(
                    by_geometry,
                    *trend_direct,
                    "parent-stop",
                    parent_stop_cause_time=start,
                )

        for number, reaction, confirmation, reset_time, reset_break in (
            self._synthetic_reset_leg_orders(start, audit_legacy)
        ):
            if confirmation < start:
                continue
            self._merge_order_candidate(
                by_geometry,
                number,
                reaction,
                confirmation,
                "reset-leg",
                reset_time=reset_time,
                reset_break=reset_break,
            )

        known_stops = [
            item[6][2]
            for item in by_geometry.values()
            if item[6] is not None
        ]
        provisional_deadline = min(known_stops) if known_stops else self.range_end
        if continuous_deadline is not None:
            provisional_deadline = min(
                provisional_deadline, continuous_deadline
            )
        provisional_deadline = self._add_canonical_reset_leg_orders(
            by_geometry,
            start,
            provisional_deadline,
            audit_legacy,
        )

        stopped = [
            item[6][2]
            for item in by_geometry.values()
            if item[6] is not None
        ]
        decision_deadline = min(stopped) if stopped else self.range_end
        if continuous_deadline is not None:
            decision_deadline = min(decision_deadline, continuous_deadline)
        eligible = [
            item
            for item in by_geometry.values()
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
        allow_bounded_continue: bool = False,
        allow_trend_leg_continue: bool = False,
    ) -> OrderMatch | None:
        candidates = [
            item for item in self.order_candidates(
                start, continuous_deadline,
                allow_bounded_continue=allow_bounded_continue,
                allow_trend_leg_continue=allow_trend_leg_continue,
            )
            if item[6] is not None
        ]
        return candidates[0] if candidates else None

    def _has_sequence_reset_between(
        self, start: datetime, end: datetime,
    ) -> bool:
        """Return whether a known hard reset lies in ``(start, end]``."""
        position = bisect_right(self._sequence_reset_times, start)
        return (
            position < len(self._sequence_reset_times)
            and self._sequence_reset_times[position] <= end
        )

    def _blue_parent_superseded(self, parent: object, parent_stop: datetime) -> bool:
        """A confirmed later Red S closes an older Blue-E order lifecycle."""
        if str(getattr(parent, "family")) != "blue":
            return False
        position = bisect_right(
            self._red_s_source_times, getattr(parent, "source_time")
        )
        return (
            position < len(self._red_s_suffix_min_decision)
            and self._red_s_suffix_min_decision[position] < parent_stop
        )

    def _register_order_audit(
        self, parent_type: str, parent: object, parent_stop: datetime,
    ) -> None:
        if self._has_sequence_reset_between(parent.source_time, parent_stop):
            return
        if (
            parent_type == "E"
            and self._blue_parent_superseded(parent, parent_stop)
        ):
            # Enforce the same ownership rule during provisional discovery
            # and final audit. Otherwise a closed branch can seed a carried
            # order into another parent before final reconciliation.
            return
        inherited_owners: list[OrderMatch] = []
        if parent_type == "S":
            inherited_owners = self._unconsumed_s_orders(parent, parent_stop)
        carried_owners = self._carried_orders_for_parent(parent, parent_stop)
        # Exact mirror contract: Bullish and Bearish use the same lifecycle
        # representative/deadline rule; only underlying price comparisons flip.
        inherited_owner = inherited_owners[0] if inherited_owners else None
        carried_owner = carried_owners[0] if carried_owners else None
        continuous_deadline = None
        if parent_type == "S" and carried_owner is None:
            continuous_deadline = (
                inherited_owner[6][2]
                if inherited_owner is not None and inherited_owner[6] is not None
                else self.range_end
            )
        order_search_start = parent_stop
        if (
            parent_type == "S"
            and carried_owner is not None
            and carried_owner[6] is not None
        ):
            order_search_start = max(parent_stop, carried_owner[6][2])
        matches = self.order_candidates(
            order_search_start, continuous_deadline,
            allow_bounded_continue=(parent_type == "S"),
            allow_trend_leg_continue=(parent_type == "E"),
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
        return self._first_parent_stop(start, as_decimal(getattr(parent, "price")))

    def parent_stop(
        self, parent_type: str, parent: object
    ) -> tuple[int, datetime] | None:
        """Public lifecycle API for the first strict parent stop."""
        return self._parent_stop(parent_type, parent)


    def _cross_order(
        self, start: datetime, level: Decimal
    ) -> tuple[int, datetime, datetime] | None:
        cache_key = (start, level)
        if cache_key in self._cross_order_cache:
            return self._cross_order_cache[cache_key]
        left = bisect_left(self.lower_times, max(start, self.range_start))
        right = bisect_left(self.lower_times, self.range_end)
        position = self._first_cross_position(
            left, right, level, less=self.order_direction != "bearish"
        )
        if position is None:
            self._cross_order_cache[cache_key] = None
            return None
        event = self.lower_times[position]
        index = self._main_index(event)
        result = index, getattr(self.candles[index], "timestamp"), event
        self._cross_order_cache[cache_key] = result
        return result

    def cross_order(
        self, confirmation_time: datetime, stop_level: Decimal
    ) -> tuple[int, datetime, datetime] | None:
        """Public audit API for an Order stop crossing."""
        return self._cross_order(confirmation_time, stop_level)


    def _unconsumed_s_orders(
        self, parent: object, parent_stop: datetime
    ) -> list[OrderMatch]:
        """Return every Blue-S Order whose stop did not decide the S itself."""
        if (
            str(getattr(parent, "color")) != "blue"
            or getattr(parent, "order_confirmation_time", None) is None
            or getattr(parent, "order_stop_level", None) is None
        ):
            return []
        confirmation = getattr(parent, "order_confirmation_time")
        stop_level = as_decimal(getattr(parent, "order_stop_level"))
        crossed = self._cross_order(confirmation, stop_level)
        if crossed is None or crossed[2] < parent_stop:
            return []
        reaction = SimpleNamespace(
            mode=getattr(parent, "order_mode"),
            first_idx=getattr(parent, "order_first_index"),
            break_idx=getattr(parent, "order_break_index"),
            box_top=getattr(parent, "order_box_top"),
            box_top_source_idx=getattr(parent, "order_box_top_source_index"),
            box_bottom=getattr(parent, "order_box_bottom"),
            box_bottom_source_idx=getattr(parent, "order_box_bottom_source_index"),
        )
        return [(
            int(getattr(parent, "order_reaction_number")),
            reaction,
            confirmation,
            stop_level,
            int(getattr(parent, "order_stop_source_index")),
            getattr(parent, "order_stop_source_time"),
            crossed,
            ("carried-live",), None, None, None,
        )]



    def _initial_order_match(
        self, entry: dict[str, object], causes: tuple[str, ...],
    ) -> OrderMatch:
        reaction = entry["reaction"]
        confirmation = entry["confirmation_time"]
        level = as_decimal(entry["stop_level"])
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

    def _carried_orders_for_parent(
        self, parent: object, parent_stop: datetime,
    ) -> list[OrderMatch]:
        """Return every Order formed and left live inside this parent lifecycle."""
        lifecycle_start = getattr(parent, "decision_event_time", None)
        if lifecycle_start is None:
            # Lightweight compatibility callers may provide only the fields
            # needed to identify a parent.  Without an exact lifecycle event
            # there is no carried-live window to evaluate.
            return []
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
                as_decimal(entry["stop_level"]), int(entry["stop_source_index"]),
                entry["stop_source_time"], crossed, causes, None,
                reset_evidence[0] if reset_evidence is not None else None,
                reset_evidence[1] if reset_evidence is not None else None,
            ))

        # Orders created by stopped A zones arrive through the initial audit
        # ledger.  They can become live during a later S lifecycle even when
        # their creation cause predates that S's decision event.  Formation,
        # confirmation and strict-stop chronology determine ownership here.
        for entry in self.initial_order_audit.values():
            reaction = entry["reaction"]
            first = self._reaction_first_time(reaction)
            confirmation = entry["confirmation_time"]
            if first < lifecycle_start or confirmation > parent_stop:
                continue
            match = self._initial_order_match(entry, ("carried-live",))
            crossed = match[6]
            if crossed is None or crossed[2] < parent_stop:
                continue
            matches.append(match)
        return sorted(
            matches,
            key=lambda item: (item[6][2], -int(getattr(item[1], "first_idx"))),
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
            self._unconsumed_s_orders(parent, stop_event)
            if parent_type == "S"
            else []
        )
        gate_owned = self._gate_owned_initial_order(stop_event)
        carried = self._carried_orders_for_parent(parent, stop_event)
        self._register_order_audit(parent_type, parent, stop_event)
        # A stopped E opens a new direct search at its own stop candle. An
        # older order formed before that event cannot replace the first valid
        # post-stop order. S may still pass its explicitly unconsumed Blue
        # order through the dedicated inheritance rule above.
        # Exact mirror contract: one representative per creation path in both
        # directions, followed by the shared final stop-event race.
        inherited_one = inherited[0] if inherited else None
        carried_one = carried[0] if carried else None
        direct = self._first_order(
            stop_event,
            (
                inherited_one[6][2]
                if parent_type == "S" and carried_one is None
                and inherited_one is not None and inherited_one[6] is not None
                else self.range_end
                if parent_type == "S" and carried_one is None
                else None
            ),
            allow_bounded_continue=(parent_type == "S"),
            allow_trend_leg_continue=(parent_type == "E"),
        )
        choices = [
            item for item in (direct, inherited_one, carried_one)
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
            parent_price=as_decimal(getattr(parent, "price")),
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
            order_box_top=as_decimal(getattr(order, "box_top")),
            order_box_top_source_index=top_source,
            order_box_top_source_time=getattr(self.candles[top_source], "timestamp"),
            order_box_bottom=as_decimal(getattr(order, "box_bottom")),
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

    def set_consumed_s_evidence(
        self, evidence: Sequence[tuple[object, object]],
    ) -> None:
        """Register non-public S evidence that continues a stopped larger E."""
        self._consumed_s_evidence = [
            (
                s_zone,
                (int(getattr(owner, "source_index")), getattr(owner, "source_time")),
            )
            for s_zone, owner in evidence
        ]

    def _apply_consumed_s_evidence(self, zones: Sequence[EZone]) -> list[EZone]:
        result = list(zones)
        for s_zone, owner_id in self._consumed_s_evidence:
            owner = next(
                (
                    item for item in result
                    if (item.source_index, item.source_time) == owner_id
                ),
                None,
            )
            if owner is None:
                continue
            continuation = self.continuation_chain_from_s(owner, s_zone)
            result = self.replace_with_earlier_continuation(
                result, owner, continuation
            )
        return result

    def continuation_chain_from_s(
        self, owner: EZone, s_zone: object,
    ) -> list[EZone]:
        """Build the E continuation opened by one S consumed by a stopped E.

        The S remains a calculation/evidence object, not a new public owner.
        Its first E inherits the stopped larger E's reconciled family and next
        number.  Recursive children are then rebuilt from the promoted E so
        Order discovery and stop chronology remain native E calculations.
        """
        stopped = self._parent_stop("S", s_zone)
        if stopped is None:
            return []
        _, stop_event = stopped
        family = str(getattr(owner, "family"))
        number = int(getattr(owner, "number")) + 1
        parent_type = "S"
        parent: object = s_zone
        chain: list[EZone] = []
        seen_sources: set[int] = set()
        while True:
            zone = self._zone(family, number, parent_type, parent, stop_event)
            if zone is None or zone.source_index in seen_sources:
                break
            parent_source_time = getattr(parent, "source_time")
            if self._has_sequence_reset_between(
                parent_source_time, zone.source_time
            ):
                break
            chain.append(zone)
            seen_sources.add(zone.source_index)
            next_stop = self._parent_stop("E", zone)
            if next_stop is None:
                break
            _, stop_event = next_stop
            parent_type, parent = "E", zone
            number += 1
        return chain

    def replace_with_earlier_continuation(
        self, base_zones: Sequence[EZone], owner: EZone, continuation: Sequence[EZone],
    ) -> list[EZone]:
        """Replace an owner's not-yet-decided descendant branch when an earlier one wins."""
        if not continuation:
            return list(base_zones)
        owner_id = (owner.source_index, owner.source_time)
        by_id = {(item.source_index, item.source_time): item for item in base_zones}

        def descends_from_owner(item: EZone) -> bool:
            current = item
            seen: set[tuple[int, datetime]] = set()
            while current.parent_type == "E":
                parent_id = (current.parent_source_index, current.parent_source_time)
                if parent_id == owner_id:
                    return True
                if parent_id in seen:
                    return False
                seen.add(parent_id)
                parent = by_id.get(parent_id)
                if parent is None:
                    return False
                current = parent
            return False

        direct_children = [
            item for item in base_zones
            if item.parent_type == "E"
            and (item.parent_source_index, item.parent_source_time) == owner_id
        ]
        first = continuation[0]
        if direct_children:
            winner = min(
                direct_children,
                key=lambda item: (item.decision_event_time, item.source_time),
            )
            if first.decision_event_time >= winner.decision_event_time:
                return list(base_zones)

        kept = [item for item in base_zones if not descends_from_owner(item)]
        merged = [*kept, *continuation]
        return self.resolve_same_source_conflicts(merged)

    def resolve_same_source_conflicts(
        self, zones: Sequence[EZone],
    ) -> list[EZone]:
        """Keep exactly one accepted E behavior for each physical source candle.

        Candidate discovery may legitimately reach the same source through
        multiple S/E lineages.  Those alternatives are evidence only; once E
        reconciliation has assigned an accepted family/number, a lower-ranked
        alternative at that *same physical source* is not a second behavior.

        Dominance is the shared project rule: Red E outranks Blue E regardless
        of number, and within the same family the higher E number outranks the
        lower number.  Exact ties preserve the earlier accepted object so this
        resolver never rewrites provenance merely to deduplicate output.
        """
        winners: dict[tuple[int, datetime], EZone] = {}
        order: list[tuple[int, datetime]] = []

        def outranks(candidate: EZone, current: EZone) -> bool:
            candidate_priority = self.sequence_priority("e", candidate.family)
            current_priority = self.sequence_priority("e", current.family)
            if candidate_priority != current_priority:
                return candidate_priority > current_priority
            if candidate.family == current.family and candidate.number != current.number:
                return candidate.number > current.number
            return False

        for zone in zones:
            identity = (int(zone.source_index), zone.source_time)
            current = winners.get(identity)
            if current is None:
                winners[identity] = zone
                order.append(identity)
            elif outranks(zone, current):
                winners[identity] = zone

        result = [winners[identity] for identity in order]
        result.sort(
            key=lambda item: (
                item.source_time, item.source_index, item.decision_event_time,
            )
        )
        return result

    def restore_independent_s_roots(
        self, dominant_zones: Sequence[EZone],
    ) -> list[EZone]:
        """Restore calculation-valid E1 roots owned directly by accepted S.

        E dominance chooses which chain owns larger-module continuation, but
        formation of a new E behavior is independent: every accepted, stopped
        S may still form its own direct E1.  A reconciled dominant zone that
        came from that same S is therefore replaced by the original direct
        root (family/number from the S chain), while missing roots are added.
        Suppressed S evidence consumed by a larger E is not in ``self.s_zones``
        and cannot manufacture a competing E1 through this path.
        """
        # A physical source already owned by an accepted E cannot also keep
        # an S parent alive for downstream E-root restoration. Public lifecycle
        # finality already gives that candle to E; applying the same ownership
        # here prevents a provisional same-source S from manufacturing a later
        # E1 after reconciliation.
        dominant_sources = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in dominant_zones
        }
        accepted_s = {
            (int(getattr(item, "source_index")), getattr(item, "source_time"))
            for item in self.s_zones
            if (int(getattr(item, "source_index")), getattr(item, "source_time"))
            not in dominant_sources
        }
        roots = [
            item for item in self._last_candidate_zones
            if item.parent_type == "S"
            and int(item.number) == 1
            and (item.parent_source_index, item.parent_source_time) in accepted_s
        ]
        result = list(dominant_zones)
        for root in roots:
            parent_id = (root.parent_source_index, root.parent_source_time)
            same_parent = [
                item for item in result
                if item.parent_type == "S"
                and (item.parent_source_index, item.parent_source_time) == parent_id
            ]
            if same_parent:
                winner = min(
                    same_parent,
                    key=lambda item: (item.decision_event_time, item.source_time),
                )
                result = [item for item in result if item is not winner]
                result.append(root)
            elif not any(
                item.source_index == root.source_index
                and item.source_time == root.source_time
                and item.parent_type == root.parent_type
                and item.parent_source_index == root.parent_source_index
                and item.parent_source_time == root.parent_source_time
                for item in result
            ):
                result.append(root)
        return self.resolve_same_source_conflicts(result)

    def _discover_candidate_chains(self) -> list[EZone]:
        """Build provisional recursive E chains from every stopped S parent.

        Calculation-invalid S evidence is still audited normally.  It loses
        only the right to open a *competing cross-family E root* when its exact
        physical source is already occupied by a native E continuation.  This
        prevents a dead A→S branch from retroactively deleting/recoloring the
        existing E chain while preserving same-family provenance and OrderAudit.
        """
        # Discover S-owned orders before walking recursive E chains.  A valid
        # order formed inside an E parent's lifetime must remain available even
        # when that S branch is reconciled later than the E branch.
        for s_zone in self.s_zones:
            stop = self._parent_stop("S", s_zone)
            if stop is not None:
                self._register_order_audit("S", s_zone, stop[1])

        chains: list[tuple[object, list[EZone]]] = []
        candidates: list[EZone] = []
        for s_zone in self.s_zones:
            stop = self._parent_stop("S", s_zone)
            if stop is None:
                continue
            _, stop_event = stop

            # Every fully formed S starts an independent provisional E chain.
            # Final lifecycle eligibility is resolved after all candidate
            # continuations are visible, so exact same-source cross-family
            # collisions can be judged without timestamp/fixture exceptions.
            family = str(getattr(s_zone, "color"))
            number = 1

            parent_type: str = "S"
            parent: object = s_zone
            chain_sources: set[int] = set()
            chain: list[EZone] = []
            while True:
                zone = self._zone(family, number, parent_type, parent, stop_event)
                if zone is None:
                    break
                if zone.source_index in chain_sources:
                    break
                chain.append(zone)
                candidates.append(zone)
                chain_sources.add(zone.source_index)
                parent_type, parent = "E", zone
                next_stop = self._parent_stop("E", zone)
                if next_stop is None:
                    break
                _, stop_event = next_stop
                number += 1
            if chain:
                chains.append((s_zone, chain))

        if not self.invalid_s_root_identities or not candidates:
            return candidates

        continuation_families: dict[tuple[datetime, int], set[str]] = {}
        for zone in candidates:
            if zone.parent_type != "E":
                continue
            identity = (zone.source_time, int(zone.source_index))
            continuation_families.setdefault(identity, set()).add(zone.family)

        blocked_roots: set[tuple[datetime, int]] = set()
        for s_zone, _ in chains:
            identity = (
                getattr(s_zone, "source_time"),
                int(getattr(s_zone, "source_index")),
            )
            if identity not in self.invalid_s_root_identities:
                continue
            s_family = str(getattr(s_zone, "color"))
            if any(
                family != s_family
                for family in continuation_families.get(identity, set())
            ):
                blocked_roots.add(identity)

        if not blocked_roots:
            return candidates

        return [
            zone
            for s_zone, chain in chains
            if (
                getattr(s_zone, "source_time"),
                int(getattr(s_zone, "source_index")),
            ) not in blocked_roots
            for zone in chain
        ]

    def _reconcile_candidate_chains(
        self, candidates: list[EZone]
    ) -> list[EZone]:
        """Resolve competing E chains into the accepted chronological lifecycle."""
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
                return self.sequence_priority(item.parent_type, parent_family)

            # One physical E source may be reachable through competing
            # Red/Blue S/E lineages.  Family priority is authoritative at the
            # physical source: Red outranks Blue even when the Blue candidate
            # happens to reach its decision a few lower-timeframe ticks
            # earlier.  Chronology remains the tie-breaker *within* the same
            # behavioral priority.  Applying this before chain reconciliation
            # prevents the dominant Red candidate from being discarded before
            # the final same-source resolver can see it.
            zone = min(
                eligible,
                key=lambda item: (
                    -ownership_priority(item),
                    item.decision_event_time,
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
            and not self._has_sequence_reset_between(
                item.parent_source_time, item.source_time
            )
        )

        lineage_seen: set[tuple[int, datetime]] = set()
        for zone in numbered:
            collect_lineage(zone, lineage_seen)

        numbered = [replace(item, parent_type="StopAll")
                    if item.parent_type == "E"
                    and item.parent_source_time in self.sequence_resets
                    else item for item in numbered]
        return numbered

    def _rebuild_accepted_order_audit(
        self, numbered: list[EZone]
    ) -> list[EZone]:
        """Rebuild Order Audit from accepted S/E/StopAll state only."""
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
            identity = order_identity(zone.order_first_index, zone.order_break_index)
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
            entry = self.order_audit.get(
                order_identity(zone.order_first_index, zone.order_break_index)
            )
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

    def detect(self) -> list[EZone]:
        """Discover, reconcile and audit recursive E lifecycles."""
        self.order_audit.clear()
        self.visual_lifecycle_starts.clear()
        candidates = self._discover_candidate_chains()
        self._last_candidate_zones = list(candidates)
        numbered = self._reconcile_candidate_chains(candidates)
        numbered = self._apply_consumed_s_evidence(numbered)
        numbered = self.resolve_same_source_conflicts(numbered)
        return self._rebuild_accepted_order_audit(numbered)


def detect_e_zones(
    direction: str,
    trend_reactions: Sequence[object],
    opposite_reactions: Sequence[object],
    s_zones: Sequence[object],
    trend_resets: Sequence[object],
    opposite_resets: Sequence[object],
    chronology: object,
    start_index: int = 0,
    end_index: int | None = None,
    geometry_finder: Callable[[str, int, int], object | None] | None = None,
    direct_geometry_finder: Callable[[str, int, int, datetime], object | None] | None = None,
    blocked_order_first_times: set[datetime] | None = None,
    initial_order_audit: dict[tuple[int, int], dict[str, object]] | None = None,
    reset_geometry_finder: Callable[[str, int, int, int], object | None] | None = None,
    sequence_priority: Callable[[str, str], int] | None = None,
    invalid_s_root_identities: set[tuple[datetime, int]] | None = None,
) -> list[EZone]:
    return EZoneDetector(
        direction,
        trend_reactions,
        opposite_reactions,
        s_zones,
        trend_resets,
        opposite_resets,
        chronology,
        start_index,
        end_index,
        geometry_finder,
        direct_geometry_finder,
        blocked_order_first_times,
        initial_order_audit,
        reset_geometry_finder,
        sequence_priority=sequence_priority,
        invalid_s_root_identities=invalid_s_root_identities,
    ).detect()
