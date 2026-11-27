"""Evaluate T/F from final indicator behavior, independently of formation."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from decimal import Decimal
from operator import itemgetter

from direction_policy import policy_for
from lifecycle_engine import sequence_priority

VERDICT = "trueFalse"
REPAIR = "trueFalseRepairTime"
REPEATED = "trueFalseRepeated"
REPEAT_COUNT = "trueFalseRepeatCount"
REPEAT_F = "trueFalseRepeatF"


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
class BasicRun:
    first: dict
    history_id: int
    count: int = 0
    latest_f: dict | None = None
    singleton_f: dict | None = None


def _basic_rank(key, row):
    if key == "sZones":
        return sequence_priority("s", row["color"]), 0
    return sequence_priority("e", row["family"]), row["number"]


def _repeat_predecessor_rank(rank, family):
    """Return the only repeat rank that can directly set this E to T."""
    priority, number = rank
    if number == 1:
        return sequence_priority("s", family), 0
    return priority, number - 1


def _crossed_verdict(references, rank, price):
    """Find the latest strictly crossed reference at the largest smaller rank."""
    for other in sorted(references, reverse=True):
        if other < rank:
            history = references[other]
            position = bisect_left(history, price, key=itemgetter(0))
            if position:
                return history[position - 1][1]
    return None


def _basic_verdicts(direction, events, first_crossing):
    # Active ranks descend from the oldest run to the newest. A larger
    # behavior only ends smaller runs, which are at the top of the stack.
    runs = []
    references = {}
    history_id = 0
    started = False
    lower_is_further = policy_for(direction).extreme_attr == "low"

    def repair(row, start):
        if first_crossing is not None and REPAIR not in row:
            crossed = first_crossing(direction, start, row["price"])
            if crossed is not None:
                row[REPAIR] = crossed

    for key, row in events:
        if key not in ("sZones", "eZones"):
            # Restarts end runs but keep the existing independent repair
            # eligibility of singleton Fs displaced by a later larger rank.
            references.clear()
            history_id += 1
            started = False
            continue

        is_s = key == "sZones"
        if is_s:
            started = True
        if not started:
            continue
        rank = _basic_rank(key, row)
        time = row["sourceTime"]
        predecessor_rank = None if is_s else _repeat_predecessor_rank(rank, row["family"])
        repeated_predecessor = False
        while runs and runs[-1][0] < rank:
            prior_rank, prior = runs.pop()
            if prior_rank == predecessor_rank and prior.history_id == history_id:
                repeated_predecessor = prior.count >= 2
            if prior.singleton_f is not None:
                repair(prior.singleton_f, time)
        price = Decimal(row["price"])
        if lower_is_further:
            price = price.copy_negate()
        if is_s or repeated_predecessor:
            verdict = "T"
        else:
            reference = _crossed_verdict(references, rank, price)
            if reference is not None:
                verdict = "F" if reference == "T" else "T"
            else:
                verdict = "F" if row["number"] % 2 else "T"
        row[VERDICT] = verdict

        # An equally or more easily crossed newer reference always wins at this rank.
        history = references.setdefault(rank, [])
        while history and history[-1][0] >= price:
            history.pop()
        history.append((price, verdict))

        if runs and runs[-1][0] == rank:
            run = runs[-1][1]
            if run.history_id != history_id:
                run = BasicRun(row, history_id)
                runs[-1] = rank, run
        else:
            run = BasicRun(row, history_id)
            runs.append((rank, run))

        run.count += 1
        if run.count == 2:
            run.first[REPEAT_COUNT] = 1
            run.first[REPEATED] = True
        if run.count >= 2:
            row[REPEAT_COUNT] = run.count
            row[REPEATED] = True

        if verdict == "T":
            run.singleton_f = None
            continue

        previous_f = run.latest_f
        run.latest_f = row
        if previous_f is None:
            run.singleton_f = row
            continue

        run.singleton_f = None
        previous_f[REPEAT_F] = row[REPEAT_F] = True
        # A strict crossing before replacement is historical evidence.
        # From this source onward the newest F supplies the repair level.
        repair(previous_f, previous_f["sourceTime"])
        previous_crossing = previous_f.get(REPAIR)
        if previous_crossing is not None and previous_crossing >= time:
            del previous_f[REPAIR]
        repair(row, time)


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
            row.pop(REPEAT_COUNT, None)
            row.pop(REPEAT_F, None)
            if row.get("calculationValid") is not False:
                by_source.setdefault(row["sourceTime"], (key, row))
    events = sorted(by_source.values(), key=lambda event: event[1]["sourceTime"])
    stops = []
    for key, row in events:
        # A published candidate with no verdict receives a neutral label.
        row[VERDICT] = None
        if key == primary_key:
            _stopall_verdicts(stops, stopall_confirmation_closed)
            stops.clear()
            if row["number"] in (1, 2, 3):
                row[VERDICT] = "T" if row["number"] == 1 else "F"
        elif key == "stopAlls":
            stops.append(row)
    _basic_verdicts(direction, events, first_crossing)
    _stopall_verdicts(stops, stopall_confirmation_closed)
