"""Exact Blue Line (ENG) detection over confirmed healthy reactions."""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Sequence


FIBONACCI_RATIO = Decimal("0.618")


@dataclass(frozen=True)
class ScaleStrike:
    source_index: int
    source_time: datetime
    extreme: Decimal


@dataclass(frozen=True)
class BlueLine:
    direction: str
    kind: str
    reaction_number: int
    previous_strike_count: int | None
    strike_count: int | None
    fibonacci_level: Decimal | None
    source_index: int
    source_time: datetime
    source_extreme: Decimal
    broken_level: Decimal | None
    line_price: Decimal
    start_time: datetime
    end_time: datetime
    calculation_valid: bool = True


def _is_color(candle: object, color: str) -> bool:
    return str(getattr(candle, "tag")).upper() == color


def _main_candle(candles_by_index: dict[int, object], index: int) -> object:
    try:
        return candles_by_index[index]
    except KeyError as exc:
        raise ValueError(f"Missing main candle index {index}.") from exc


def _stops_on_index(
    direction: str,
    line: object,
    candles: Sequence[object],
    start_index: int,
    end_index: int,
) -> bool:
    level = Decimal(getattr(line, "source_extreme"))
    for candle in candles[max(0, start_index) : end_index + 1]:
        extreme = Decimal(getattr(candle, "low" if direction == "bullish" else "high"))
        if (
            extreme < level
            if direction == "bullish"
            else extreme > level
        ):
            return int(getattr(candle, "index")) == end_index
    return False


def fibonacci_level(direction: str, reaction: object, reference: Decimal) -> Decimal:
    if direction == "bullish":
        top = Decimal(getattr(reaction, "box_top"))
        return top - FIBONACCI_RATIO * (top - reference)
    if direction == "bearish":
        bottom = Decimal(getattr(reaction, "box_bottom"))
        return bottom + FIBONACCI_RATIO * (reference - bottom)
    raise ValueError("Direction must be 'bullish' or 'bearish'.")


def _intrabar_pending_confirmation(
    direction: str,
    seconds: Sequence[object],
    reaction: object,
    comparison_extreme: Decimal,
    start_time: datetime,
    break_time: datetime,
    timeframe_seconds: int,
    candles_by_index: dict[int, object],
    second_times: Sequence[datetime] | None = None,
    main_times: Sequence[datetime] | None = None,
) -> ScaleStrike | None:
    end_time = break_time + timedelta(seconds=timeframe_seconds)
    if second_times is None:
        second_times = [getattr(candle, "timestamp") for candle in seconds]
    left = bisect_left(second_times, start_time)
    right = bisect_left(second_times, end_time)
    relevant = seconds[left:right]
    if not relevant:
        return None

    break_level = Decimal(
        getattr(reaction, "box_top" if direction == "bullish" else "box_bottom")
    )
    eligible: list[object] = []
    for second in relevant:
        extreme = Decimal(getattr(second, "low" if direction == "bullish" else "high"))
        penetrates = (
            extreme < comparison_extreme
            if direction == "bullish"
            else extreme > comparison_extreme
        )
        if penetrates:
            eligible.append(second)
        breaks = (
            Decimal(getattr(second, "high")) > break_level
            if direction == "bullish"
            else Decimal(getattr(second, "low")) < break_level
        )
        if breaks and eligible:
            decisive = (
                min(eligible, key=lambda item: Decimal(getattr(item, "low")))
                if direction == "bullish"
                else max(eligible, key=lambda item: Decimal(getattr(item, "high")))
            )
            decisive_time = getattr(decisive, "timestamp")
            if main_times is None:
                main_times = [
                    getattr(candles_by_index[index], "timestamp")
                    for index in sorted(candles_by_index)
                ]
            source_position = bisect_left(main_times, decisive_time)
            if (
                source_position >= len(main_times)
                or main_times[source_position] > decisive_time
            ):
                source_position -= 1
            source = candles_by_index.get(source_position)
            if source is None:
                raise ValueError("Cannot map decisive one-second candle to a main candle.")
            return ScaleStrike(
                source_index=int(getattr(source, "index")),
                source_time=getattr(source, "timestamp"),
                extreme=Decimal(
                    getattr(decisive, "low" if direction == "bullish" else "high")
                ),
            )
    return None


def count_scale_strikes(
    direction: str,
    reaction: object,
    candles: Sequence[object],
    one_second_candles: Sequence[object],
    reference: Decimal,
    timeframe_seconds: int,
    candles_by_index: dict[int, object] | None = None,
    second_times: Sequence[datetime] | None = None,
    main_times: Sequence[datetime] | None = None,
) -> tuple[Decimal, list[ScaleStrike]]:
    """Return the exact 0.618 level and confirmed strikes for one reaction."""
    if timeframe_seconds < 1:
        raise ValueError("Timeframe must be at least one second.")
    level = fibonacci_level(direction, reaction, reference)
    if candles_by_index is None:
        candles_by_index = {
            int(getattr(candle, "index")): candle for candle in candles
        }
    first_index = int(getattr(reaction, "first_idx"))
    break_index = int(getattr(reaction, "break_idx"))
    reaction_candles = [
        _main_candle(candles_by_index, index)
        for index in range(first_index, break_index + 1)
    ]
    confirming_color = "GREEN" if direction == "bullish" else "RED"
    strikes: list[ScaleStrike] = []
    pending: ScaleStrike | None = None

    for candle in reaction_candles:
        last_extreme = strikes[-1].extreme if strikes else level
        candle_extreme = Decimal(
            getattr(candle, "low" if direction == "bullish" else "high")
        )
        is_new = (
            candle_extreme < last_extreme
            if direction == "bullish"
            else candle_extreme > last_extreme
        )
        if is_new and (
            pending is None
            or (
                candle_extreme < pending.extreme
                if direction == "bullish"
                else candle_extreme > pending.extreme
            )
        ):
            pending = ScaleStrike(
                source_index=int(getattr(candle, "index")),
                source_time=getattr(candle, "timestamp"),
                extreme=candle_extreme,
            )

        if pending is not None and _is_color(candle, confirming_color):
            strikes.append(pending)
            pending = None

    if pending is not None:
        break_candle = reaction_candles[-1]
        intrabar = _intrabar_pending_confirmation(
            direction=direction,
            seconds=one_second_candles,
            reaction=reaction,
            comparison_extreme=strikes[-1].extreme if strikes else level,
            start_time=pending.source_time,
            break_time=getattr(break_candle, "timestamp"),
            timeframe_seconds=timeframe_seconds,
            candles_by_index=candles_by_index,
            second_times=second_times,
            main_times=main_times,
        )
        if intrabar is not None:
            strikes.append(intrabar)

    return level, strikes


def detect_blue_lines(
    direction: str,
    reactions: Sequence[object],
    candles: Sequence[object],
    one_second_candles: Sequence[object],
    timeframe_seconds: int,
    resets: Sequence[object] = (),
) -> list[BlueLine]:
    """Detect scale and Reset Blue Lines over authoritative engine events."""
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    candles_by_index = {int(getattr(candle, "index")): candle for candle in candles}
    second_times = [getattr(candle, "timestamp") for candle in one_second_candles]
    main_times = [getattr(candle, "timestamp") for candle in candles]
    output: list[BlueLine] = []
    previous_reaction: object | None = None
    previous_count: int | None = None
    has_blue_line = False
    healthy_reactions_since_blue = 0
    resets_by_first: dict[int, list[object]] = {}
    for reset in resets:
        resets_by_first.setdefault(int(getattr(reset, "from_first_idx")), []).append(reset)

    for reaction_number, reaction in enumerate(reactions, start=1):
        leg_start = str(getattr(reaction, "mode")) == "A"
        if leg_start:
            # An explicit Anchor is the actual leg-head extreme immediately
            # preceding FirstRed/FirstGreen. The broader range-open boundary
            # is only the fallback when no Anchor exists.
            boundary = getattr(reaction, "anchor_value", None)
            if boundary is None:
                boundary = getattr(reaction, "leg_boundary_value", None)
            if boundary is None:
                raise ValueError("Leg-Start reaction is missing its leg-head boundary.")
            reference = Decimal(boundary)
            previous_count = None
        else:
            if previous_reaction is None:
                raise ValueError("A Normal reaction cannot precede the Leg-Start reaction.")
            reference = Decimal(
                getattr(
                    previous_reaction,
                    "box_bottom" if direction == "bullish" else "box_top",
                )
            )

        level, strikes = count_scale_strikes(
            direction,
            reaction,
            candles,
            one_second_candles,
            reference,
            timeframe_seconds,
            candles_by_index,
            second_times,
            main_times,
        )
        scale_candidate = previous_count is not None and len(strikes) > previous_count
        scale_emitted = False
        if scale_candidate and (
            not has_blue_line or healthy_reactions_since_blue >= 1
        ):
            decisive = strikes[-1]
            source = _main_candle(candles_by_index, decisive.source_index)
            high = Decimal(getattr(source, "high"))
            low = Decimal(getattr(source, "low"))
            line_price = (
                low + (high - low) / Decimal(3)
                if direction == "bullish"
                else high - (high - low) / Decimal(3)
            )
            output.append(
                BlueLine(
                    direction=direction,
                    kind="scale",
                    reaction_number=reaction_number,
                    previous_strike_count=previous_count,
                    strike_count=len(strikes),
                    fibonacci_level=level,
                    source_index=decisive.source_index,
                    source_time=decisive.source_time,
                    source_extreme=decisive.extreme,
                    broken_level=None,
                    line_price=line_price,
                    start_time=decisive.source_time
                    - timedelta(seconds=timeframe_seconds),
                    end_time=decisive.source_time
                    + timedelta(seconds=timeframe_seconds),
                )
            )
            has_blue_line = True
            healthy_reactions_since_blue = 0
            scale_emitted = True

        # The reaction carrying a scale Blue Line is not spacing for its own
        # following Reset. Every other confirmed healthy reaction is spacing,
        # including one whose scale candidate was suppressed by the lock.
        if has_blue_line and not scale_emitted:
            healthy_reactions_since_blue += 1

        for reset in resets_by_first.get(int(getattr(reaction, "first_idx")), []):
            if has_blue_line and healthy_reactions_since_blue < 1:
                continue
            reset_index = int(getattr(reset, "index"))
            source = _main_candle(candles_by_index, reset_index)
            high = Decimal(getattr(source, "high"))
            low = Decimal(getattr(source, "low"))
            line_price = (
                low + (high - low) / Decimal(5)
                if direction == "bullish"
                else high - (high - low) / Decimal(5)
            )
            source_time = getattr(source, "timestamp")
            output.append(
                BlueLine(
                    direction=direction,
                    kind="reset",
                    reaction_number=reaction_number,
                    previous_strike_count=None,
                    strike_count=None,
                    fibonacci_level=None,
                    source_index=reset_index,
                    source_time=source_time,
                    source_extreme=low if direction == "bullish" else high,
                    broken_level=Decimal(getattr(reset, "broken_level")),
                    line_price=line_price,
                    start_time=source_time - timedelta(seconds=timeframe_seconds),
                    end_time=source_time + timedelta(seconds=timeframe_seconds),
                    calculation_valid=(
                        not output
                        or not (
                            _stops_on_index(
                                direction,
                                output[-1],
                                candles,
                                int(getattr(output[-1], "source_index")) + 1,
                                reset_index,
                            )
                            and (
                                low < Decimal(getattr(output[-1], "source_extreme"))
                                if direction == "bullish"
                                else high > Decimal(getattr(output[-1], "source_extreme"))
                            )
                        )
                    ),
                )
            )
            has_blue_line = True
            healthy_reactions_since_blue = 0
        previous_reaction = reaction
        previous_count = len(strikes)

    return output


run_blue_line = detect_blue_lines
