"""Small behavior-neutral primitives shared by calculation engines."""

from __future__ import annotations

from bisect import bisect_left
from collections.abc import Iterable, Iterator, Sequence
from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeAlias, TypeVar

CORE_UTILS_VERSION = "1.1.0"


_Payload = TypeVar("_Payload")


class ChronologicalContainmentIndex(Generic[_Payload]):
    """Find enclosing intervals with a strict start and inclusive end."""

    def __init__(self, intervals: Iterable[tuple[datetime, datetime, _Payload]]) -> None:
        self._runs: list[tuple[list[datetime], list[datetime], list[_Payload]]] = []
        starts: list[datetime] = []
        ends: list[datetime] = []
        payloads: list[_Payload] = []
        for start, end, payload in intervals:
            # Keep chronological runs separate to preserve the caller's order.
            if starts and (start < starts[-1] or end < ends[-1]):
                self._runs.append((starts, ends, payloads))
                starts, ends, payloads = [], [], []
            starts.append(start)
            ends.append(end)
            payloads.append(payload)
        if starts:
            self._runs.append((starts, ends, payloads))

    def enclosing(self, start: datetime, end: datetime) -> Iterator[_Payload]:
        for starts, ends, payloads in self._runs:
            stop = bisect_left(starts, start)
            first = bisect_left(ends, end, 0, stop)
            for position in range(first, stop):
                yield payloads[position]


def ordered_naive_datetimes(values: Sequence[datetime]) -> bool:
    """Check whether a search can use bisect without reordering records."""
    return all(type(value) is datetime and value.tzinfo is None for value in values) and all(
        values[index - 1] <= values[index] for index in range(1, len(values))
    )


def as_decimal(value: object) -> Decimal:
    """Preserve Decimal values and normalize other numeric inputs losslessly."""
    return value if isinstance(value, Decimal) else Decimal(str(value))


OrderIdentity: TypeAlias = tuple[int, int]


def order_identity(first_index: object, break_index: object) -> OrderIdentity:
    """Return the canonical physical Order/Reaction geometry identity."""
    return int(first_index), int(break_index)


def reaction_identity(reaction: object) -> OrderIdentity:
    """Return ``(FirstIndex, BreakIndex)`` for a Reaction-like object."""
    return int(reaction.first_idx), int(reaction.break_idx)
