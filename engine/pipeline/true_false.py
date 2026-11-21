"""Evaluate T/F from final indicator behavior, independently of formation."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from decimal import Decimal

from direction_policy import policy_for
from lifecycle_engine import sequence_priority

VERDICT = "trueFalse"
REPAIR = "trueFalseRepairTime"
REPEATED = "trueFalseRepeated"


def repair_crossing_lookup(lower_index, from_epoch, to_epoch, *, through):
    """Search the bounded original RAW with the reference's own direction."""
    right = bisect_right(lower_index.times, through)

    def find(direction: str, start: int, level: str) -> int | None:
        left = bisect_left(lower_index.times, from_epoch(start), hi=right)
        policy = policy_for(direction)
        search = (lower_index.first_less if policy.extreme_attr == "low"
                  else lower_index.first_greater)
        position = search(left, right, Decimal(level))
        return None if position is None else to_epoch(lower_index.times[position])

    return find


@dataclass(slots=True)
class BasicRepeat:
    latest: dict
    repair_count: int
    verdict_count: int


def _basic_rank(key, row):
    if key == "sZones":
        return sequence_priority("s", row["color"]), 0
    return sequence_priority("e", row["family"]), row["number"]


def _basic_verdicts(direction, events, first_crossing):
    repeats = {}
    known = {}
    started = False

    def repair(row, start):
        if first_crossing is not None and REPAIR not in row:
            crossed = first_crossing(direction, start, row["price"])
            if crossed is not None:
                row[REPAIR] = crossed

    for key, row in events:
        is_s = key == "sZones"
        if is_s:
            started = True
        if not started:
            continue
        rank = _basic_rank(key, row)
        time = row["sourceTime"]
        lower = [other for other in repeats if other < rank]
        parent = known.get(row.get("parentSourceTime"))
        engulf = any(repeats[other].verdict_count >= 2 for other in lower)
        if is_s or engulf:
            verdict = "T"
        elif parent is not None:
            verdict = "F" if parent == "T" else "T"
        else:
            # A final E can outlive a parent hidden by another published behavior.
            verdict = "F" if row["number"] % 2 else "T"
        row[VERDICT] = known[time] = verdict

        for other in lower:
            prior = repeats.pop(other)
            if prior.latest[VERDICT] == "F" and prior.repair_count == 1:
                repair(prior.latest, time)

        if engulf:
            # Start verdict repetition at this behavior; keep existing F repair history.
            for repeat in repeats.values():
                repeat.verdict_count = 0
        previous = repeats.get(rank)
        repair_count = verdict_count = 1
        if previous is not None and previous.latest[VERDICT] == verdict:
            repair_count += previous.repair_count
            verdict_count += previous.verdict_count
            if verdict == "F":
                if previous.latest.get(REPAIR, -1) >= time:
                    previous.latest.pop(REPAIR)
                repair(row, time)
        repeats[rank] = BasicRepeat(row, repair_count, verdict_count)


def _stopall_verdicts(rows, confirmation_closed):
    previous_number = 0
    previous_series_end = largest_prior_end = 0
    group_start = verdict_start = None
    repeated_prefix = []
    restart_verdicts = False
    for row in rows:
        number = row["number"]
        if group_start is None or number <= previous_number:
            previous_series_end = previous_number
            largest_prior_end = max(largest_prior_end, previous_series_end)
            group_start = verdict_start = number
            repeated_prefix.clear()
            restart_verdicts = False
        elif restart_verdicts:
            verdict_start = number
            restart_verdicts = False
        previous_number = number

        row[VERDICT] = "T" if (number - verdict_start) % 2 == 0 else "F"
        if number <= largest_prior_end:
            repeated_prefix.append(row)
            if (number in (previous_series_end, largest_prior_end)
                    and (confirmation_closed is None or confirmation_closed(row))):
                # A larger match absorbs the temporary fresh count after the first match.
                for repeated in repeated_prefix:
                    repeated[REPEATED] = True
                    repeated[VERDICT] = "T" if (repeated["number"] - group_start) % 2 == 0 else "F"
                restart_verdicts = True


def apply_true_false(direction, group, first_crossing=None, *, stopall_confirmation_closed=None):
    """Annotate final rows by source time, without changing native behavior."""
    primary_key = "primaryLows" if direction == "bullish" else "primaryHighs"
    by_source = {}
    # Final native output has one behavior per candle. Match the existing
    # display ownership if a payload also retains a same-source S/E donor.
    for key in (primary_key, "stopAlls", "eZones", "sZones"):
        for row in group.get(key, ()):
            row.pop(VERDICT, None)
            row.pop(REPAIR, None)
            row.pop(REPEATED, None)
            if row.get("calculationValid") is not False:
                by_source.setdefault(row["sourceTime"], (key, row))
    basic = []
    stops = []
    for key, row in sorted(by_source.values(), key=lambda event: event[1]["sourceTime"]):
        # A published candidate with no verdict receives a neutral label.
        row[VERDICT] = None
        if key == primary_key:
            _stopall_verdicts(stops, stopall_confirmation_closed)
            stops.clear()
            if row["number"] in (1, 2, 3):
                row[VERDICT] = "T" if row["number"] == 1 else "F"
        elif key == "stopAlls":
            stops.append(row)
        else:
            basic.append((key, row))
    _basic_verdicts(direction, basic, first_crossing)
    _stopall_verdicts(stops, stopall_confirmation_closed)
