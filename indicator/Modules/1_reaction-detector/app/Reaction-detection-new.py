from __future__ import annotations

import argparse
import bisect
import os
import re
import sys
import time
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Sequence


TIMESTAMP_FORMAT = "%d-%m-%Y %H:%M:%S"
USER_DATE_FORMAT = "%Y-%m-%d"
USER_TIME_FORMAT = "%H-%M-%S"
USER_DATETIME_FORMAT = f"{USER_DATE_FORMAT} {USER_TIME_FORMAT}"
ENGINE_VERSION = "9.3.0"
CANDLE_PATTERN = re.compile(
    r"^\s*(\d+)\s*\|\s*"
    r"((?:(?:\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s+)?"
    r"\d{2}:\d{2}:\d{2})\s*\|\s*"
    r"(\w+)\s*\|\s*"
    r"O=([\d.]+)\s+H=([\d.]+)\s+L=([\d.]+)\s+C=([\d.]+)"
)

def trace(message: str, *args: object) -> None:
    return None


class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    enabled = True

    @classmethod
    def apply(cls, text: str, *codes: str) -> str:
        if not cls.enabled:
            return text
        return f"{''.join(codes)}{text}{cls.RESET}"


@dataclass(frozen=True)
class Candle:
    index: int
    timestamp: datetime
    display_time: str
    tag: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal


@dataclass
class Candidate:
    first_idx: int
    first_time: str
    box_top_source_idx: int
    box_top_source_time: str
    box_top: Decimal
    box_bottom_source_idx: int
    box_bottom_source_time: str
    box_bottom: Decimal
    mode: str
    anchor_idx: int | None = None
    anchor_value: Decimal | None = None
    leg_boundary_value: Decimal | None = None
    break_idx: int | None = None
    break_time: str | None = None
    intrabar_start: datetime | None = None
    cross_direction_origin: bool = False
    cross_direction_chain_owner: bool = False


@dataclass(frozen=True)
class ResetEvent:
    index: int
    display_time: str
    second_time: str | None
    broken_level: Decimal
    from_first_idx: int


@dataclass(frozen=True)
class IntrabarAnalysis:
    event_second: Candle
    extreme: Decimal
    extreme_source: Candle


@dataclass(frozen=True)
class DetectionResult:
    direction: str
    reactions: list[Candidate]
    resets: list[ResetEvent]
    start_index: int
    end_index: int


def enable_windows_ansi() -> None:
    if os.name == "nt":
        os.system("")


def configure_console_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def log(level: str, message: str) -> None:
    now = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": Style.CYAN,
        "LOAD": Style.BLUE,
        "OK": Style.GREEN,
        "WARN": Style.YELLOW,
        "ERROR": Style.RED,
        "RUN": Style.MAGENTA,
        "SAVE": Style.GREEN,
    }
    color = colors.get(level, Style.WHITE)
    label = Style.apply(f"{level:>5}", Style.BOLD, color)
    stamp = Style.apply(now, Style.DIM)
    print(f"{stamp}  {label}  {message}")


def print_banner() -> None:
    width = 74
    title = "REACTION DETECTOR"
    subtitle = "30s Engine  |  1s Intrabar Chronology  |  Exact Decimal"
    print()
    print(Style.apply("+" + "=" * (width - 2) + "+", Style.CYAN))
    print(
        Style.apply("|", Style.CYAN)
        + Style.apply(title.center(width - 2), Style.BOLD, Style.WHITE)
        + Style.apply("|", Style.CYAN)
    )
    print(
        Style.apply("|", Style.CYAN)
        + Style.apply(subtitle.center(width - 2), Style.DIM, Style.WHITE)
        + Style.apply("|", Style.CYAN)
    )
    print(Style.apply("+" + "=" * (width - 2) + "+", Style.CYAN))
    print()


def print_section(title: str, color: str = Style.CYAN) -> None:
    print()
    print(Style.apply(f"[{title}] " + "-" * max(1, 62 - len(title)), Style.BOLD, color))


def parse_timestamp(value: str) -> datetime:
    value = value.strip()
    if re.fullmatch(r"\d{2}:\d{2}:\d{2}", value):
        return datetime.strptime(value, "%H:%M:%S")
    for date_format in ("%Y-%m-%d %H:%M:%S", TIMESTAMP_FORMAT):
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            pass
    raise ValueError(
        "Expected candle timestamp YYYY-MM-DD HH:MM:SS or "
        f"DD-MM-YYYY HH:MM:SS; received: {value}"
    )


def classify_candle_color(open_price: Decimal, close_price: Decimal) -> str:
    """Match Lightweight Charts: Open <= Close is an up/green candle."""
    return "GREEN" if open_price <= close_price else "RED"


def read_candles(path: Path) -> list[Candle]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    candles: list[Candle] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            match = CANDLE_PATTERN.match(line)
            if not match:
                continue

            try:
                display_time = match.group(2)
                open_price = Decimal(match.group(4))
                high = Decimal(match.group(5))
                low = Decimal(match.group(6))
                close_price = Decimal(match.group(7))
                candles.append(
                    Candle(
                        index=int(match.group(1)),
                        timestamp=parse_timestamp(display_time),
                        display_time=display_time,
                        tag=classify_candle_color(open_price, close_price),
                        open=open_price,
                        high=high,
                        low=low,
                        close=close_price,
                    )
                )
            except (ValueError, InvalidOperation) as exc:
                raise ValueError(f"Invalid candle at {path}:{line_number}: {exc}") from exc

    if not candles:
        raise ValueError(f"No candles were parsed from: {path}")

    for position, candle in enumerate(candles):
        if candle.index != position:
            raise ValueError(
                "Main and formatted one-second candle indices must be contiguous "
                f"from zero. Expected {position}, found {candle.index} in {path}."
            )

    return candles


class DetectorBase:
    def __init__(
        self,
        candles: Sequence[Candle],
        one_second_candles: Sequence[Candle],
        start_index: int,
        end_index: int,
    ) -> None:
        self.candles = candles
        self.seconds = one_second_candles
        self.start_index = start_index
        self.end_index = end_index
        self.main_times = [candle.timestamp for candle in candles]
        self.second_times = [candle.timestamp for candle in one_second_candles]
        self._reaction_break_index_cache: dict[str, tuple[int, list[int]]] = {}

        if len(candles) > 1:
            self.timeframe = candles[1].timestamp - candles[0].timestamp
        else:
            self.timeframe = timedelta(seconds=1)

        if self.timeframe.total_seconds() <= 0:
            raise ValueError("Main timeframe must be positive.")

    def trace_state(
        self,
        direction: str,
        candle: Candle,
        mode: str,
        state: str,
        candidate: Candidate | None,
    ) -> None:
        trace(
            "STATE | direction=%s | index=%s | time=%s | mode=%s | state=%s | "
            "tag=%s | O=%s | H=%s | L=%s | C=%s | candidate_first=%s | "
            "candidate_top=%s | candidate_bottom=%s",
            direction,
            candle.index,
            candle.display_time,
            mode,
            state,
            candle.tag,
            candle.open,
            candle.high,
            candle.low,
            candle.close,
            candidate.first_idx if candidate else None,
            candidate.box_top if candidate else None,
            candidate.box_bottom if candidate else None,
        )

    def seconds_between(self, start: datetime, end: datetime) -> Iterable[Candle]:
        left = bisect.bisect_left(self.second_times, start)
        right = bisect.bisect_left(self.second_times, end)
        return self.seconds[left:right]

    def main_source_for_time(self, timestamp: datetime) -> Candle | None:
        position = bisect.bisect_right(self.main_times, timestamp) - 1
        if position < self.start_index or position > self.end_index:
            return None
        end = (
            self.candles[position + 1].timestamp
            if position + 1 < len(self.candles)
            else self.candles[position].timestamp + self.timeframe
        )
        if timestamp < end:
            return self.candles[position]
        return None

    def minimum_low(self, start_index: int, end_index: int) -> tuple[Decimal, Candle]:
        source = self.candles[start_index]
        for index in range(start_index + 1, end_index + 1):
            candle = self.candles[index]
            if candle.low < source.low:
                source = candle
        return source.low, source

    def maximum_high(self, start_index: int, end_index: int) -> tuple[Decimal, Candle]:
        source = self.candles[start_index]
        for index in range(start_index + 1, end_index + 1):
            candle = self.candles[index]
            if candle.high > source.high:
                source = candle
        return source.high, source


class BullishDetector(DetectorBase):
    def green_run_peak_before(self, first_red_index: int) -> tuple[Decimal, Candle]:
        run_end = first_red_index - 1
        if run_end < self.start_index or self.candles[run_end].tag != "GREEN":
            raise ValueError("Mode-A FirstRed must immediately follow a GREEN candle.")

        run_start = run_end
        while run_start > self.start_index and self.candles[run_start - 1].tag == "GREEN":
            run_start -= 1
        return self.maximum_high(run_start, run_end)

    def breakout_analysis(
        self, candidate: Candidate, breakout_candle: Candle
    ) -> IntrabarAnalysis | None:
        start_index = (
            candidate.box_top_source_idx + 1
            if candidate.box_top_source_idx < candidate.first_idx
            else candidate.box_top_source_idx
        )
        start = candidate.intrabar_start or self.candles[start_index].timestamp
        end = breakout_candle.timestamp + self.timeframe
        minimum_low: Decimal | None = None
        minimum_time: datetime | None = None

        for second in self.seconds_between(start, end):
            if minimum_low is None or second.low < minimum_low:
                minimum_low = second.low
                minimum_time = second.timestamp
            if second.high > candidate.box_top:
                source = self.main_source_for_time(minimum_time) if minimum_time else None
                if minimum_low is None or source is None:
                    return None
                return IntrabarAnalysis(second, minimum_low, source)
        return None

    def mode_a_invalidation_before_breakout(
        self, candidate: Candidate, candle: Candle
    ) -> bool:
        # A Mode-A candidate belongs to the complete leg that opened at the
        # analysis/Reset boundary.  Later lower RED candles are internal
        # BoxBottom updates; only a strict break of the frozen leg floor can
        # invalidate the candidate before its BoxTop breaks.
        invalidation_level = (
            candidate.anchor_value
            if candidate.anchor_value is not None
            else candidate.leg_boundary_value
        )
        if invalidation_level is None:
            return False

        if candle.low >= invalidation_level:
            return False
        if candle.high <= candidate.box_top:
            return True

        end = candle.timestamp + self.timeframe
        for second in self.seconds_between(candle.timestamp, end):
            if second.low < invalidation_level:
                return True
            if second.high > candidate.box_top:
                return False
        return True

    def confirmed_reset_before_breakout(
        self, candidate: Candidate | None, candle: Candle, confirmed_bottom: Decimal
    ) -> bool:
        if candidate is None or candle.high <= candidate.box_top:
            return True

        end = candle.timestamp + self.timeframe
        for second in self.seconds_between(candle.timestamp, end):
            if second.low < confirmed_bottom:
                return True
            if second.high > candidate.box_top:
                return False
        return True

    def post_breakout_reset(
        self,
        analysis: IntrabarAnalysis | None,
        box_bottom: Decimal,
        breakout_candle: Candle,
    ) -> Candle | None:
        if analysis is None:
            return None
        end = breakout_candle.timestamp + self.timeframe
        for second in self.seconds_between(
            analysis.event_second.timestamp + timedelta(microseconds=1), end
        ):
            if second.low < box_bottom:
                return second
        return None

    def detect(self) -> DetectionResult:
        reactions: list[Candidate] = []
        resets: list[ResetEvent] = []
        mode = "A"
        state = "SCANNING"
        last_confirmed_bottom: Decimal | None = None
        last_confirmed_first_idx: int | None = None
        running_peak: Decimal | None = None
        running_peak_src: int | None = None
        leg_open_low: Decimal | None = None
        leg_just_started = True
        anchor_red: Candle | None = None
        anchor_red_origin: str | None = None
        reset_context: Candle | None = None
        candidate: Candidate | None = None

        for index in range(self.start_index, self.end_index + 1):
            candle = self.candles[index]
            self.trace_state("bullish", candle, mode, state, candidate)

            reset_detected = (
                last_confirmed_bottom is not None and candle.low < last_confirmed_bottom
            )
            reset_occurs_first = reset_detected
            if reset_detected and state == "WAITING":
                reset_occurs_first = self.confirmed_reset_before_breakout(
                    candidate, candle, last_confirmed_bottom
                )

            if reset_occurs_first:
                resets.append(
                    ResetEvent(
                        index=candle.index,
                        display_time=candle.display_time,
                        second_time=None,
                        broken_level=last_confirmed_bottom,
                        from_first_idx=last_confirmed_first_idx,
                    )
                )
                candidate = None
                last_confirmed_bottom = None
                last_confirmed_first_idx = None
                running_peak = None
                running_peak_src = None
                mode = "A"
                state = "SCANNING"
                leg_open_low = None
                leg_just_started = True
                anchor_red = candle if candle.tag == "RED" else None
                anchor_red_origin = "reset" if candle.tag == "RED" else None
                reset_context = candle
                continue

            if state == "WAITING":
                assert candidate is not None

                if (
                    candidate.mode == "A"
                    and self.mode_a_invalidation_before_breakout(candidate, candle)
                ):
                    candidate = None
                    state = "SCANNING"
                    anchor_red = candle if candle.tag == "RED" else None
                    anchor_red_origin = (
                        "candidate_invalidation" if candle.tag == "RED" else None
                    )
                    continue

                if candle.low < candidate.box_bottom:
                    candidate.box_bottom = candle.low
                    candidate.box_bottom_source_idx = candle.index
                    candidate.box_bottom_source_time = candle.display_time

                if candle.high > candidate.box_top:
                    candidate.break_idx = candle.index
                    candidate.break_time = candle.display_time
                    analysis = self.breakout_analysis(candidate, candle)

                    if (
                        candidate.box_bottom_source_idx == candle.index
                        and analysis is not None
                    ):
                        candidate.box_bottom = analysis.extreme
                        candidate.box_bottom_source_idx = analysis.extreme_source.index
                        candidate.box_bottom_source_time = (
                            analysis.extreme_source.display_time
                        )

                    confirmed = replace(candidate)
                    reactions.append(confirmed)
                    last_confirmed_bottom = confirmed.box_bottom
                    last_confirmed_first_idx = confirmed.first_idx
                    running_peak = candle.high
                    running_peak_src = candle.index
                    mode = "B"
                    state = "SCANNING"
                    candidate = None

                    reset_second = self.post_breakout_reset(
                        analysis, last_confirmed_bottom, candle
                    )
                    if reset_second is not None:
                        resets.append(
                            ResetEvent(
                                index=candle.index,
                                display_time=candle.display_time,
                                second_time=reset_second.display_time,
                                broken_level=last_confirmed_bottom,
                                from_first_idx=last_confirmed_first_idx,
                            )
                        )
                        last_confirmed_bottom = None
                        last_confirmed_first_idx = None
                        running_peak = None
                        running_peak_src = None
                        mode = "A"
                        state = "SCANNING"
                        leg_open_low = None
                        leg_just_started = True
                        anchor_red = candle if candle.tag == "RED" else None
                        anchor_red_origin = "reset" if candle.tag == "RED" else None
                        reset_context = candle
                        continue

                    if candle.tag == "RED":
                        candidate = Candidate(
                            first_idx=candle.index,
                            first_time=candle.display_time,
                            box_top_source_idx=candle.index,
                            box_top_source_time=candle.display_time,
                            box_top=running_peak,
                            box_bottom_source_idx=candle.index,
                            box_bottom_source_time=candle.display_time,
                            box_bottom=candle.low,
                            mode="B",
                        )
                        state = "WAITING"
                continue

            if mode == "A":
                if leg_just_started:
                    leg_open_low = candle.low
                    leg_just_started = False
                    previous_reset = reset_context
                    reset_context = None
                    if candle.tag == "RED":
                        if (
                            previous_reset is not None
                            and previous_reset.tag == "GREEN"
                            and candle.low >= previous_reset.low
                        ):
                            green_high, green_source = self.green_run_peak_before(
                                candle.index
                            )
                            if green_high >= candle.high:
                                box_top = green_high
                                box_top_source = green_source
                            else:
                                box_top = candle.high
                                box_top_source = candle
                            candidate = Candidate(
                                first_idx=candle.index,
                                first_time=candle.display_time,
                                box_top_source_idx=box_top_source.index,
                                box_top_source_time=box_top_source.display_time,
                                box_top=box_top,
                                box_bottom_source_idx=candle.index,
                                box_bottom_source_time=candle.display_time,
                                box_bottom=candle.low,
                                mode="A",
                                leg_boundary_value=leg_open_low,
                            )
                            state = "WAITING"
                            trace(
                                "EVENT | direction=bullish | "
                                "type=LEG_OPEN_CANDIDATE_CREATED | first=%s | "
                                "top=%s | bottom=%s | reset_index=%s",
                                candle.index,
                                box_top,
                                candle.low,
                                previous_reset.index,
                            )
                        else:
                            anchor_red = candle
                            anchor_red_origin = "leg_open"
                    continue

                previous = self.candles[index - 1]
                passes = False
                box_top: Decimal | None = None
                box_top_source: Candle | None = None

                if previous.tag == "GREEN" and candle.tag == "RED":
                    if (
                        anchor_red is not None
                        and anchor_red_origin == "candidate_invalidation"
                        and previous.low < anchor_red.low
                        and candle.low < anchor_red.low
                    ):
                        anchor_red = None
                        anchor_red_origin = None

                    if anchor_red is not None:
                        passes = candle.low >= anchor_red.low
                    elif candle.low >= previous.low or candle.low >= leg_open_low:
                        passes = True

                    if passes:
                        green_high, green_source = self.green_run_peak_before(candle.index)
                        if green_high >= candle.high:
                            box_top = green_high
                            box_top_source = green_source
                        else:
                            box_top = candle.high
                            box_top_source = candle

                if passes:
                    assert box_top is not None and box_top_source is not None
                    candidate = Candidate(
                        first_idx=candle.index,
                        first_time=candle.display_time,
                        box_top_source_idx=box_top_source.index,
                        box_top_source_time=box_top_source.display_time,
                        box_top=box_top,
                        box_bottom_source_idx=candle.index,
                        box_bottom_source_time=candle.display_time,
                        box_bottom=candle.low,
                        mode="A",
                        anchor_idx=anchor_red.index if anchor_red else None,
                        anchor_value=anchor_red.low if anchor_red else None,
                        leg_boundary_value=leg_open_low,
                    )
                    state = "WAITING"
                elif candle.tag == "RED":
                    anchor_red = candle
                    anchor_red_origin = "scan"
                elif candle.tag in {"DOJI", "NEUTRAL"}:
                    anchor_red = None
                    anchor_red_origin = None
            else:
                if candle.tag == "RED":
                    box_top = candle.high
                    box_top_source_idx = candle.index
                    if running_peak is not None and running_peak >= box_top:
                        box_top = running_peak
                        box_top_source_idx = running_peak_src

                    bottom_start = (
                        box_top_source_idx + 1
                        if box_top_source_idx < candle.index
                        else candle.index
                    )
                    bottom, bottom_source = self.minimum_low(bottom_start, candle.index)
                    candidate = Candidate(
                        first_idx=candle.index,
                        first_time=candle.display_time,
                        box_top_source_idx=box_top_source_idx,
                        box_top_source_time=self.candles[
                            box_top_source_idx
                        ].display_time,
                        box_top=box_top,
                        box_bottom_source_idx=bottom_source.index,
                        box_bottom_source_time=bottom_source.display_time,
                        box_bottom=bottom,
                        mode="B",
                    )
                    state = "WAITING"

                if running_peak is None or candle.high > running_peak:
                    running_peak = candle.high
                    running_peak_src = candle.index

        return DetectionResult(
            direction="bullish",
            reactions=reactions,
            resets=resets,
            start_index=self.start_index,
            end_index=self.end_index,
        )


def mirror_candle(candle: Candle) -> Candle:
    """Internal coordinate/role adapter; never reclassify a market candle here.

    Input dojis are GREEN in both market directions, matching the chart.
    Swapping that tag inside the Bullish reference makes its RED/FirstRed
    branch implement the original GREEN/FirstGreen Bearish branch. This is
    not permission to treat a market doji as RED or emit a changed chart color.
    """
    return replace(
        candle,
        open=candle.open.copy_negate(), high=candle.low.copy_negate(),
        low=candle.high.copy_negate(), close=candle.close.copy_negate(),
        tag={"GREEN": "RED", "RED": "GREEN"}.get(candle.tag, candle.tag),
    )


def mirror_candidate(candidate: Candidate | None) -> Candidate | None:
    if candidate is None:
        return None
    return replace(
        candidate,
        box_top=candidate.box_bottom.copy_negate(),
        box_bottom=candidate.box_top.copy_negate(),
        box_top_source_idx=candidate.box_bottom_source_idx,
        box_top_source_time=candidate.box_bottom_source_time,
        box_bottom_source_idx=candidate.box_top_source_idx,
        box_bottom_source_time=candidate.box_top_source_time,
        anchor_value=(candidate.anchor_value.copy_negate()
                      if candidate.anchor_value is not None else None),
        leg_boundary_value=(candidate.leg_boundary_value.copy_negate()
                            if candidate.leg_boundary_value is not None else None),
    )


def mirror_analysis(analysis: IntrabarAnalysis | None) -> IntrabarAnalysis | None:
    if analysis is None:
        return None
    return IntrabarAnalysis(
        mirror_candle(analysis.event_second), analysis.extreme.copy_negate(),
        mirror_candle(analysis.extreme_source),
    )


class _ReflectedCandles(Sequence[Candle]):
    """Read-only coordinate view; allocate only candles used by the scan."""

    def __init__(self, source: Sequence[Candle]) -> None:
        self.source = source

    def __len__(self) -> int:
        return len(self.source)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [mirror_candle(candle) for candle in self.source[index]]
        return mirror_candle(self.source[index])


class BearishDetector(DetectorBase):
    """Execute the Bullish reference state machine in reflected coordinates.

    This is a coordinate adapter, not a second rule implementation. Both the
    initial Leg-Start and opposite-anchor queries use the same reference rules.
    Exact Decimal sign copying avoids context rounding during reflection.
    """

    def __init__(self, candles, one_second_candles, start_index, end_index):
        super().__init__(candles, one_second_candles, start_index, end_index)
        self.reference = BullishDetector(
            candles, one_second_candles, start_index, end_index,
        )
        # Time indexes are invariant under price reflection. Construct them
        # from the original rows; lazily transform OHLC only when consumed.
        self.reference.candles = _ReflectedCandles(candles)
        self.reference.seconds = _ReflectedCandles(one_second_candles)

    def red_run_bottom_before(self, first_green_index):
        value, source = self.reference.green_run_peak_before(first_green_index)
        return value.copy_negate(), mirror_candle(source)

    def breakdown_analysis(self, candidate, breakdown_candle):
        return mirror_analysis(self.reference.breakout_analysis(
            mirror_candidate(candidate), mirror_candle(breakdown_candle),
        ))

    def invalidation_high_break_before_breakdown(self, candidate, candle):
        return self.reference.mode_a_invalidation_before_breakout(
            mirror_candidate(candidate), mirror_candle(candle),
        )

    def confirmed_reset_before_breakdown(self, candidate, candle, confirmed_top):
        return self.reference.confirmed_reset_before_breakout(
            mirror_candidate(candidate), mirror_candle(candle),
            confirmed_top.copy_negate(),
        )

    def post_breakdown_reset(self, analysis, box_top, breakdown_candle):
        result = self.reference.post_breakout_reset(
            mirror_analysis(analysis), box_top.copy_negate(),
            mirror_candle(breakdown_candle),
        )
        return mirror_candle(result) if result is not None else None

    def detect(self) -> DetectionResult:
        result = self.reference.detect()
        return DetectionResult(
            direction="bearish",
            reactions=[mirror_candidate(candidate) for candidate in result.reactions],
            resets=[replace(reset, broken_level=reset.broken_level.copy_negate())
                    for reset in result.resets],
            start_index=result.start_index, end_index=result.end_index,
        )



def format_price(value: Decimal) -> str:
    return f"{value:.4f}"


def safe_timestamp(timestamp: datetime) -> str:
    return timestamp.strftime("%d-%m-%Y %H-%M-%S")


class UnifiedReactionDetector(DetectorBase):
    """Unified v9 directional post-Reset engine.

    The proven directional detectors supply only the initial Leg-Start. After
    that first confirmation this class owns Normal search and directional
    post-Reset continuation.  A Reset always searches for the first healthy
    reaction in the same direction as the requested/output leg; patterns in
    the opposite direction never gate or unlock that search.
    """

    def __init__(
        self,
        candles: Sequence[Candle],
        one_second_candles: Sequence[Candle],
        start_index: int,
        end_index: int,
        output_direction: str,
    ) -> None:
        super().__init__(candles, one_second_candles, start_index, end_index)
        self.output_direction = output_direction
        self.bull = BullishDetector(
            candles, one_second_candles, start_index, end_index
        )
        self.bear = BearishDetector(
            candles, one_second_candles, start_index, end_index
        )
        self.all_reactions: dict[str, list[Candidate]] = {
            "bullish": [],
            "bearish": [],
        }
        self.all_resets: dict[str, list[ResetEvent]] = {
            "bullish": [],
            "bearish": [],
        }

    def _append_reaction(self, direction: str, candidate: Candidate) -> bool:
        # A confirmed adjacent opposite-direction Anchor may extend the outer
        # boundary, but it must never shrink the candidate's own box.
        opposite_anchor_is_confirmed = False
        if (
            candidate.break_idx is not None
            and candidate.anchor_idx is not None
            and candidate.anchor_idx + 1 == candidate.first_idx
            and self.all_resets[direction]
        ):
            reset_index = self.all_resets[direction][-1].index
            opposite_detector = (
                BullishDetector if direction == "bearish" else BearishDetector
            )(
                self.candles,
                self.seconds,
                reset_index,
                candidate.first_idx,
            )
            opposite_anchor_is_confirmed = any(
                reaction.break_idx == candidate.anchor_idx
                for reaction in opposite_detector.detect().reactions
            )

        if opposite_anchor_is_confirmed:
            anchor = self.candles[candidate.anchor_idx]
            first = self.candles[candidate.first_idx]
            if direction == "bearish":
                # A RED Leg-Start with a higher ceiling than FirstGreen owns
                # the leg boundary; FirstGreen must keep its own BoxBottom.
                if anchor.high <= first.high:
                    candidate.box_bottom = anchor.low
                    candidate.box_bottom_source_idx = anchor.index
                    candidate.box_bottom_source_time = anchor.display_time
            else:
                # Exact mirror: a GREEN Leg-Start whose floor is below
                # FirstRed owns the leg boundary; FirstRed keeps its BoxTop.
                if anchor.low >= first.low:
                    candidate.box_top = anchor.high
                    candidate.box_top_source_idx = anchor.index
                    candidate.box_top_source_time = anchor.display_time

        # When the opposite structural boundary source precedes First, its
        # opposite extreme is excluded. Recalculate that opposite edge from
        # the eligible post-boundary window through the confirmation candle.
        if candidate.break_idx is not None:
            if (
                direction == "bullish"
                and candidate.box_top_source_idx < candidate.first_idx
            ):
                analysis = self.bull.breakout_analysis(
                    candidate, self.candles[candidate.break_idx]
                )
                if analysis is not None:
                    candidate.box_bottom = analysis.extreme
                    candidate.box_bottom_source_idx = analysis.extreme_source.index
                    candidate.box_bottom_source_time = analysis.extreme_source.display_time
            elif (
                direction == "bearish"
                and candidate.box_bottom_source_idx < candidate.first_idx
            ):
                analysis = self.bear.breakdown_analysis(
                    candidate, self.candles[candidate.break_idx]
                )
                if analysis is not None:
                    candidate.box_top = analysis.extreme
                    candidate.box_top_source_idx = analysis.extreme_source.index
                    candidate.box_top_source_time = analysis.extreme_source.display_time

        self.all_reactions[direction].append(replace(candidate))
        trace(
            "UNIFIED EVENT | type=REACTION_CONFIRMED | direction=%s | "
            "number=%s | first=%s | break=%s | top=%s | bottom=%s | mode=%s",
            direction,
            len(self.all_reactions[direction]),
            candidate.first_idx,
            candidate.break_idx,
            candidate.box_top,
            candidate.box_bottom,
            candidate.mode,
        )
        return True

    def _append_reset(
        self,
        direction: str,
        candle: Candle,
        level: Decimal,
        first_idx: int,
        second_time: str | None = None,
    ) -> None:
        self.all_resets[direction].append(
            ResetEvent(
                index=candle.index,
                display_time=candle.display_time,
                second_time=second_time,
                broken_level=level,
                from_first_idx=first_idx,
            )
        )
        trace(
            "UNIFIED EVENT | type=RESET | direction=%s | index=%s | "
            "time=%s | broken_level=%s",
            direction,
            candle.index,
            candle.display_time,
            level,
        )

    def _refine(
        self, direction: str, candidate: Candidate, candle: Candle
    ) -> IntrabarAnalysis | None:
        helper = self.bull if direction == "bullish" else self.bear
        analysis = (
            helper.breakout_analysis(candidate, candle)
            if direction == "bullish"
            else helper.breakdown_analysis(candidate, candle)
        )
        if analysis is None:
            return None
        if direction == "bullish" and candidate.box_bottom_source_idx == candle.index:
            candidate.box_bottom = analysis.extreme
            candidate.box_bottom_source_idx = analysis.extreme_source.index
            candidate.box_bottom_source_time = analysis.extreme_source.display_time
        if direction == "bearish" and candidate.box_top_source_idx == candle.index:
            candidate.box_top = analysis.extreme
            candidate.box_top_source_idx = analysis.extreme_source.index
            candidate.box_top_source_time = analysis.extreme_source.display_time
        return analysis

    def _candidate_from_confirmation_remainder(
        self,
        direction: str,
        confirmed: Candidate,
        candle: Candle,
        analysis: IntrabarAnalysis | None,
    ) -> Candidate | None:
        """Reuse a correctly colored confirmation candle for the next reaction."""
        required_tag = "RED" if direction == "bullish" else "GREEN"
        if candle.tag != required_tag or analysis is None:
            return None
        # A cross-direction Leg-Start confirmation candle may simultaneously
        # become the first candle of the next same-direction reaction. Its
        # decisive second belongs to the new box boundary, so no second,
        # still-more-extreme tick is required. Other confirmations retain the
        # ordinary fresh post-event boundary requirement.
        # Every confirmation opens Normal Search. If its main candle has the
        # required start color, that complete candle is the next First candle,
        # regardless of whether the confirmed reaction was Mode A or Mode B.
        whole_confirmation_candle = True
        remainder_start = (
            candle.timestamp
            if whole_confirmation_candle
            else analysis.event_second.timestamp + timedelta(microseconds=1)
        )
        remainder_end = candle.timestamp + self.timeframe
        seconds = list(self.seconds_between(remainder_start, remainder_end))
        if not seconds:
            return None
        if direction == "bullish":
            top_second = max(seconds, key=lambda item: (item.high, -item.timestamp.timestamp()))
            bottom_second = min(seconds, key=lambda item: (item.low, item.timestamp))
            if (
                not whole_confirmation_candle
                and top_second.high <= analysis.event_second.high
            ):
                return None
            return Candidate(
                first_idx=candle.index,
                first_time=candle.display_time,
                box_top_source_idx=candle.index,
                box_top_source_time=candle.display_time,
                box_top=top_second.high,
                box_bottom_source_idx=candle.index,
                box_bottom_source_time=candle.display_time,
                box_bottom=bottom_second.low,
                mode="B",
                intrabar_start=remainder_start,
            )
        bottom_second = min(seconds, key=lambda item: (item.low, item.timestamp))
        top_second = max(seconds, key=lambda item: (item.high, -item.timestamp.timestamp()))
        if (
            not whole_confirmation_candle
            and bottom_second.low >= analysis.event_second.low
        ):
            return None
        return Candidate(
            first_idx=candle.index,
            first_time=candle.display_time,
            box_top_source_idx=candle.index,
            box_top_source_time=candle.display_time,
            box_top=top_second.high,
            box_bottom_source_idx=candle.index,
            box_bottom_source_time=candle.display_time,
            box_bottom=bottom_second.low,
            mode="B",
            intrabar_start=remainder_start,
        )

    def _first_initial(self, direction: str) -> Candidate | None:
        initial_result = (
            self.bull.detect() if direction == "bullish" else self.bear.detect()
        )
        return (
            replace(initial_result.reactions[0])
            if initial_result.reactions
            else None
        )

    def _first_same_direction_after_reset(
        self, direction: str, reset_index: int
    ) -> Candidate | None:
        """Find the first base reaction in the reset direction after Reset.

        Same-direction search runs concurrently with the structural boundary
        race. Only its first confirmation is eligible here; after it confirms,
        the unified loop resumes after its break candle and owns subsequent
        Normal Search.
        """
        detector_class = BullishDetector if direction == "bullish" else BearishDetector
        # The Reset candle is the first eligible candle.  Including the
        # previous candle can resurrect the reaction that was just Reset and
        # prevents the first complete post-Reset geometry from owning the leg.
        search_start = max(self.start_index, reset_index)
        local_detector = detector_class(
            self.candles,
            self.seconds,
            search_start,
            self.end_index,
        )
        local_result = local_detector.detect()
        if not local_result.reactions:
            return None
        candidate = replace(local_result.reactions[0])
        candidate.mode = "A"
        return candidate

    def _first_direct_same_direction_after_reset(
        self, direction: str, reset_index: int
    ) -> Candidate | None:
        """Return the first structurally owned reaction after Reset.

        The earliest eligible candidate owns the evolving leg until it either
        confirms or its outer leg boundary is strictly crossed. A nested local
        pattern cannot confirm while that owner is unresolved. If the boundary
        breaks first, restart strictly after that event. Bearish is the exact
        price/color mirror of Bullish.
        """
        context_tag = "GREEN" if direction == "bullish" else "RED"
        first_tag = "RED" if direction == "bullish" else "GREEN"
        blocked_through = reset_index

        for first_index in range(reset_index + 1, self.end_index + 1):
            first = self.candles[first_index]
            if first_index <= blocked_through:
                continue
            if first.tag != first_tag or self.candles[first_index - 1].tag != context_tag:
                continue

            candidate = self._build_direct_candidate(
                direction, reset_index, first_index
            )
            if candidate is None:
                continue
            confirmed, invalidation_index = self._scan_direct_candidate(
                direction, candidate, self.end_index
            )
            if confirmed is not None:
                return confirmed
            if invalidation_index is None:
                continue
            blocked_through = invalidation_index

        return None

    def _first_geometry_after_reset(
        self, direction: str, reset_index: int, end_index: int | None = None,
    ) -> Candidate | None:
        """Return the first complete same-direction geometry after Reset.

        This search intentionally does not apply the normal Reset/invalidation
        gate.  In an E space, the reset-leg rule only requires the geometric
        Top-Bottom-Top / Bottom-Top-Bottom structure.
        """
        first_tag = "RED" if direction == "bullish" else "GREEN"
        context_tag = "GREEN" if direction == "bullish" else "RED"
        limit = self.end_index if end_index is None else min(end_index, self.end_index)
        for first_index in range(reset_index + 1, limit + 1):
            if (
                self.candles[first_index].tag != first_tag
                or self.candles[first_index - 1].tag != context_tag
            ):
                continue
            candidate = self._build_direct_candidate(
                direction, reset_index, first_index
            )
            if candidate is None:
                continue
            for scan in range(first_index + 1, limit + 1):
                candle = self.candles[scan]
                if direction == "bullish":
                    if candle.low < candidate.box_bottom:
                        candidate.box_bottom = candle.low
                        candidate.box_bottom_source_idx = candle.index
                        candidate.box_bottom_source_time = candle.display_time
                    if candle.high > candidate.box_top:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        return candidate
                else:
                    if candle.high > candidate.box_top:
                        candidate.box_top = candle.high
                        candidate.box_top_source_idx = candle.index
                        candidate.box_top_source_time = candle.display_time
                    if candle.low < candidate.box_bottom:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        return candidate
        return None

    def first_simple_geometry_after_gate(
        self,
        direction: str,
        reset_index: int,
        gate_index: int,
        end_index: int | None = None,
    ) -> Candidate | None:
        """Find the first E Order_B geometry from its actual Reset context.

        The Order_B gate is opened later by a strict lower-timeframe boundary
        crossing, but its simple geometry still belongs to the Reset that
        created the leg.  Reconstructing it from ``gate_index - 1`` invents a
        new Reset context and can promote a pattern that is not an
        authoritative reaction.  This bounded helper preserves the real Reset
        while restricting First to the gate candle or later.
        """
        first_tag = "RED" if direction == "bullish" else "GREEN"
        context_tag = "GREEN" if direction == "bullish" else "RED"
        limit = self.end_index if end_index is None else min(end_index, self.end_index)
        start = max(reset_index + 1, gate_index)
        for first_index in range(start, limit + 1):
            if (
                self.candles[first_index].tag != first_tag
                or self.candles[first_index - 1].tag != context_tag
            ):
                continue
            candidate = self._build_direct_candidate(
                direction, reset_index, first_index
            )
            if candidate is None:
                continue
            # The earliest eligible post-gate candidate owns this Reset leg.
            # It must survive the outer boundary inherited from ``reset_index``;
            # a later local candidate cannot recover a leg whose owner was
            # strictly invalidated before confirmation.
            confirmed, _ = self._scan_direct_candidate(
                direction, candidate, limit
            )
            return confirmed
        return None

    def _reaction_break_indices(self, direction: str) -> list[int]:
        """Cached ascending `break_idx` values mirroring `all_reactions[direction]`.

        `all_reactions[direction]` is append-only and strictly non-decreasing
        in `break_idx`, so this index list can be reused via bisect instead of
        rescanning the full reaction history on every gate lookup.
        """
        reactions = self.all_reactions[direction]
        cached = self._reaction_break_index_cache.get(direction)
        if cached is not None and cached[0] == len(reactions):
            return cached[1]
        indices = [int(reaction.break_idx) for reaction in reactions]
        self._reaction_break_index_cache[direction] = (len(reactions), indices)
        return indices

    def first_order_reaction_after_gate(
        self,
        direction: str,
        gate_index: int,
        end_index: int | None = None,
        gate_event_time: datetime | None = None,
    ) -> Candidate | None:
        """Return direct Order_A geometry from continuous Reaction context."""
        limit = self.end_index if end_index is None else min(end_index, self.end_index)
        if gate_index < self.start_index or gate_index >= limit:
            return None

        def confirmed_no_later_than_gate(reaction: Candidate) -> bool:
            break_index = int(reaction.break_idx)
            if break_index < gate_index or gate_event_time is None:
                return break_index <= gate_index
            if break_index > gate_index:
                return False
            break_candle = self.candles[break_index]
            start = reaction.intrabar_start or break_candle.timestamp
            end = break_candle.timestamp + self.timeframe
            level = reaction.box_bottom if direction == "bearish" else reaction.box_top
            for lower in self.seconds_between(start, end):
                crossed = (
                    lower.low < level
                    if direction == "bearish"
                    else lower.high > level
                )
                if crossed:
                    return lower.timestamp <= gate_event_time
            return break_candle.timestamp <= gate_event_time

        reactions = self.all_reactions[direction]
        break_indices = self._reaction_break_indices(direction)
        # `break_indices` is non-decreasing and duplicate-free for this
        # engine's reaction stream, so every reaction strictly before
        # `gate_index` is automatically confirmed; only a reaction whose
        # `break_idx` equals `gate_index` needs the fine-grained intrabar
        # check via `confirmed_no_later_than_gate`.
        cut = bisect.bisect_left(break_indices, gate_index)
        history = list(reactions[:cut])
        if cut < len(reactions) and break_indices[cut] == gate_index:
            if confirmed_no_later_than_gate(reactions[cut]):
                history.append(reactions[cut])
        search_start = gate_index + 1
        if not history:
            result = self._earliest_confirmed_geometry(
                direction, search_start, limit
            )
            if result is not None:
                setattr(result, "order_gate_decision", "no-history")
            return result

        owner = max(history, key=lambda item: int(item.break_idx))
        boundary_end = max(int(owner.first_idx), gate_index - 1)
        gate = self.candles[gate_index]
        if direction == "bearish":
            outer_boundary, _ = self.maximum_high(
                int(owner.first_idx), boundary_end
            )
            gate_boundary = gate.low
        else:
            outer_boundary, _ = self.minimum_low(
                int(owner.first_idx), boundary_end
            )
            gate_boundary = gate.high

        event_start = gate_event_time or gate.timestamp
        event_end = self.candles[limit].timestamp + self.timeframe
        decision: tuple[str, Candle] | None = None
        for lower in self.seconds_between(event_start, event_end):
            if direction == "bearish":
                outer_cross = lower.high > outer_boundary
                gate_cross = lower.low < gate_boundary
            else:
                outer_cross = lower.low < outer_boundary
                gate_cross = lower.high > gate_boundary
            if outer_cross:
                decision = ("restart", lower)
                break
            if gate_cross:
                decision = ("continue", lower)
                break

        if decision is None:
            return None
        if decision[0] == "restart":
            source = self.main_source_for_time(decision[1].timestamp)
            if source is None:
                return None
            search_start = int(source.index) + 1
        if search_start > limit:
            return None
        result = self._earliest_confirmed_geometry(
            direction, search_start, limit
        )
        if result is not None:
            setattr(result, "order_gate_decision", decision[0])
        return result

    def _earliest_confirmed_geometry(
        self, direction: str, start_index: int, end_index: int | None = None,
    ) -> Candidate | None:
        """Return the geometry whose strict confirmation occurs first.

        Multiple First candidates may overlap. Order-gender chronology belongs
        to the structure that completes first, not necessarily to the oldest
        still-unconfirmed First candle.
        """
        first_tag = "RED" if direction == "bullish" else "GREEN"
        context_tag = "GREEN" if direction == "bullish" else "RED"
        limit = self.end_index if end_index is None else min(end_index, self.end_index)
        active: list[Candidate] = []
        reset_index = max(self.start_index, start_index - 1)
        for scan in range(start_index, limit + 1):
            candle = self.candles[scan]
            if (
                scan > reset_index
                and candle.tag == first_tag
                and self.candles[scan - 1].tag == context_tag
            ):
                candidate = self._build_direct_candidate(
                    direction, reset_index, scan
                )
                if candidate is not None:
                    active.append(candidate)

            confirmed: list[Candidate] = []
            for candidate in active:
                if scan <= candidate.first_idx:
                    continue
                if direction == "bullish":
                    if candle.low < candidate.box_bottom:
                        candidate.box_bottom = candle.low
                        candidate.box_bottom_source_idx = candle.index
                        candidate.box_bottom_source_time = candle.display_time
                    if candle.high > candidate.box_top:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        confirmed.append(candidate)
                else:
                    if candle.high > candidate.box_top:
                        candidate.box_top = candle.high
                        candidate.box_top_source_idx = candle.index
                        candidate.box_top_source_time = candle.display_time
                    if candle.low < candidate.box_bottom:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        self._refine(direction, candidate, candle)
                        confirmed.append(candidate)
            if confirmed:
                return min(confirmed, key=lambda item: item.first_idx)
        return None

    def _build_direct_candidate(
        self, direction: str, reset_index: int, first_index: int
    ) -> Candidate | None:
        context_tag = "GREEN" if direction == "bullish" else "RED"
        first_tag = "RED" if direction == "bullish" else "GREEN"
        first = self.candles[first_index]
        if (
            first_index <= reset_index
            or first.tag != first_tag
            or self.candles[first_index - 1].tag != context_tag
        ):
            return None

        context_start = first_index - 1
        while (
            context_start - 1 >= reset_index
            and self.candles[context_start - 1].tag == context_tag
        ):
            context_start -= 1
        local_start = context_start
        while (
            local_start - 1 >= reset_index
            and self.candles[local_start - 1].tag == first_tag
        ):
            local_start -= 1

        if direction == "bullish":
            local_floor, _ = self.minimum_low(local_start, first_index - 1)
            if first.low < local_floor:
                return None
            box_top, top_source = self.maximum_high(context_start, first_index)
            leg_boundary, leg_source = self.minimum_low(
                reset_index, first_index - 1
            )
            return Candidate(
                first_index, first.display_time,
                top_source.index, top_source.display_time, box_top,
                first_index, first.display_time, first.low,
                mode="A", anchor_idx=leg_source.index,
                anchor_value=leg_boundary, leg_boundary_value=leg_boundary,
            )

        local_ceiling, _ = self.maximum_high(local_start, first_index - 1)
        if first.high > local_ceiling:
            return None
        box_bottom, bottom_source = self.minimum_low(context_start, first_index)
        leg_boundary, leg_source = self.maximum_high(
            reset_index, first_index - 1
        )
        return Candidate(
            first_index, first.display_time,
            first_index, first.display_time, first.high,
            bottom_source.index, bottom_source.display_time, box_bottom,
            mode="A", anchor_idx=leg_source.index,
            anchor_value=leg_boundary, leg_boundary_value=leg_boundary,
        )

    def _partition_intrabar_turn_boundary(
        self,
        direction: str,
        local_start: int,
        first_index: int,
        boundary: Decimal,
        source: Candle,
    ) -> tuple[Decimal, Candle]:
        """Exclude an extreme made before a later structural turn in one bar.

        Example: a RED context candle makes its low first, then a new structural
        high, and only afterwards FirstGreen begins. The pre-turn low belongs
        to the old leg and cannot become the new Bearish BoxBottom. Bullish is
        the exact high/low mirror.
        """
        context_index = first_index - 1
        if source.index != context_index or local_start >= context_index:
            return boundary, source

        context = self.candles[context_index]
        first = self.candles[first_index]
        seconds = list(
            self.seconds_between(
                context.timestamp,
                first.timestamp + self.timeframe,
            )
        )
        context_seconds = [
            second
            for second in seconds
            if context.timestamp
            <= second.timestamp
            < context.timestamp + self.timeframe
        ]
        if not context_seconds:
            return boundary, source

        if direction == "bearish":
            reference_high, _ = self.maximum_high(
                local_start, context_index - 1
            )
            low_second = min(
                context_seconds, key=lambda item: (item.low, item.timestamp)
            )
            turn_second = next(
                (
                    second
                    for second in context_seconds
                    if second.timestamp > low_second.timestamp
                    and second.high > reference_high
                ),
                None,
            )
            if turn_second is None:
                return boundary, source
            eligible = [
                second
                for second in seconds
                if second.timestamp > turn_second.timestamp
            ]
            if not eligible:
                return boundary, source
            selected = min(eligible, key=lambda item: (item.low, item.timestamp))
            selected_source = self.main_source_for_time(selected.timestamp)
            return (
                (selected.low, selected_source)
                if selected_source is not None
                else (boundary, source)
            )

        reference_low, _ = self.minimum_low(local_start, context_index - 1)
        high_second = max(
            context_seconds, key=lambda item: (item.high, -item.timestamp.timestamp())
        )
        turn_second = next(
            (
                second
                for second in context_seconds
                if second.timestamp > high_second.timestamp
                and second.low < reference_low
            ),
            None,
        )
        if turn_second is None:
            return boundary, source
        eligible = [
            second for second in seconds if second.timestamp > turn_second.timestamp
        ]
        if not eligible:
            return boundary, source
        selected = max(
            eligible, key=lambda item: (item.high, -item.timestamp.timestamp())
        )
        selected_source = self.main_source_for_time(selected.timestamp)
        return (
            (selected.high, selected_source)
            if selected_source is not None
            else (boundary, source)
        )

    def _scan_direct_candidate(
        self, direction: str, candidate: Candidate, stop_index: int
    ) -> tuple[Candidate | None, int | None]:
        for scan in range(candidate.first_idx + 1, stop_index + 1):
            candle = self.candles[scan]
            confirms = (
                candle.high > candidate.box_top
                if direction == "bullish"
                else candle.low < candidate.box_bottom
            )
            invalidates = self._owner_boundary_before_confirmation(
                direction, candidate, candle
            )
            if invalidates:
                return None, scan
            if direction == "bullish" and candle.low < candidate.box_bottom:
                candidate.box_bottom = candle.low
                candidate.box_bottom_source_idx = candle.index
                candidate.box_bottom_source_time = candle.display_time
            if direction == "bearish" and candle.high > candidate.box_top:
                candidate.box_top = candle.high
                candidate.box_top_source_idx = candle.index
                candidate.box_top_source_time = candle.display_time
            if confirms:
                candidate.break_idx = scan
                candidate.break_time = candle.display_time
                self._refine(direction, candidate, candle)
                return candidate, None
        return None, None

    def _owner_boundary_before_confirmation(
        self, direction: str, candidate: Candidate, candle: Candle
    ) -> bool:
        """Return whether structural alignment is lost before confirmation.

        A Bearish Leg-Start Top must not rise above its outer ceiling.
        A Bullish Leg-Start Bottom must not fall below its outer floor.
        Equality preserves the unresolved candidate. If a strict invalidation
        competes with confirmation in the same main candle, ordered one-second
        data decides which event occurred first.
        """
        boundary = candidate.leg_boundary_value
        if boundary is None:
            return False

        if direction == "bullish":
            reaches_boundary = candle.low < boundary
            confirms = candle.high > candidate.box_top
        else:
            reaches_boundary = candle.high > boundary
            confirms = candle.low < candidate.box_bottom
        if not reaches_boundary:
            return False
        if not confirms:
            return True

        end = candle.timestamp + self.timeframe
        for second in self.seconds_between(candle.timestamp, end):
            if direction == "bullish":
                if second.low < boundary:
                    return True
                if second.high > candidate.box_top:
                    return False
            else:
                if second.high > boundary:
                    return True
                if second.low < candidate.box_bottom:
                    return False
        return True

    def _opposite_candidate_from_active_reset(
        self, reset_direction: str, reset_index: int
    ) -> Candidate | None:
        """Seed the new opposite leg from the candle that Resets active ownership.

        A Bearish Reset candle that is RED is immediately FirstRed for the new
        Bullish leg.  A Bullish Reset candle that is GREEN is the exact
        FirstGreen mirror.  Internal extremes update the opposite box until
        its strict confirmation; a later generic candidate cannot replace it.
        """
        direction = "bearish" if reset_direction == "bullish" else "bullish"
        required_tag = "GREEN" if direction == "bearish" else "RED"
        reset = self.candles[reset_index]
        if reset.tag != required_tag:
            return None
        candidate = Candidate(
            first_idx=reset_index,
            first_time=reset.display_time,
            box_top_source_idx=reset_index,
            box_top_source_time=reset.display_time,
            box_top=reset.high,
            box_bottom_source_idx=reset_index,
            box_bottom_source_time=reset.display_time,
            box_bottom=reset.low,
            mode="A",
        )
        scan = reset_index + 1
        while scan <= self.end_index:
            candle = self.candles[scan]
            if direction == "bullish":
                if candle.low < candidate.box_bottom:
                    candidate.box_bottom = candle.low
                    candidate.box_bottom_source_idx = candle.index
                    candidate.box_bottom_source_time = candle.display_time
                if candle.high > candidate.box_top:
                    candidate.break_idx = candle.index
                    candidate.break_time = candle.display_time
                    self._refine(direction, candidate, candle)
                    return candidate
            else:
                if candle.high > candidate.box_top:
                    candidate.box_top = candle.high
                    candidate.box_top_source_idx = candle.index
                    candidate.box_top_source_time = candle.display_time
                if candle.low < candidate.box_bottom:
                    candidate.break_idx = candle.index
                    candidate.break_time = candle.display_time
                    self._refine(direction, candidate, candle)
                    return candidate
            scan += 1
        return None

    def _after_double_reset(
        self,
        direction: str,
        reset_index: int,
    ) -> tuple[str | None, Candidate | None, int]:
        """Start a fresh two-direction race after an outer-boundary Reset."""
        candidates = [
            (candidate_direction, self._first_same_direction_after_reset(
                candidate_direction, reset_index
            ))
            for candidate_direction in (
                direction, "bearish" if direction == "bullish" else "bullish"
            )
        ]
        confirmed = [
            (candidate_direction, candidate)
            for candidate_direction, candidate in candidates
            if candidate is not None and candidate.break_idx is not None
        ]
        if confirmed:
            earliest_break = min(candidate.break_idx for _, candidate in confirmed)
            earliest = [
                (candidate_direction, candidate)
                for candidate_direction, candidate in confirmed
                if candidate.break_idx == earliest_break
            ]
            if len(earliest) == 1:
                winner_direction, winner = earliest[0]
            else:
                # Same-main-candle ties require exact intrabar chronology. The
                # directional confirmation helpers already refine to the first
                # decisive second; compare those event timestamps.
                winner_direction, winner = min(
                    earliest,
                    key=lambda item: self.candles[item[1].break_idx].timestamp,
                )
            trace(
                "UNIFIED EVENT | type=DOUBLE_RESET_DIRECTION_RACE | "
                "winner=%s | first=%s | break=%s",
                winner_direction,
                winner.first_idx,
                winner.break_idx,
            )
            return winner_direction, winner, winner.break_idx + 1
        return None, None, self.end_index + 1

    def _structural_gate(
        self, reset_direction: str, previous: Candidate, reset_index: int
    ) -> tuple[str | None, Candidate | None, int]:
        """Resolve one frozen Gate and return (direction, reaction, next index)."""
        reset = self.candles[reset_index]
        trigger_tag = "GREEN" if reset_direction == "bullish" else "RED"
        trigger_index = reset_index
        while (
            trigger_index <= self.end_index
            and self.candles[trigger_index].tag != trigger_tag
        ):
            trigger_index += 1
        if trigger_index > self.end_index:
            return None, None, self.end_index + 1

        trigger = self.candles[trigger_index]
        if reset_direction == "bullish":
            structure_bottom, bottom_source = self.minimum_low(
                reset_index, trigger_index
            )
            structure_top, top_source = self.maximum_high(
                previous.break_idx, trigger_index
            )
        else:
            structure_top, top_source = self.maximum_high(
                reset_index, trigger_index
            )
            structure_bottom, bottom_source = self.minimum_low(
                previous.break_idx, trigger_index
            )
        trace(
            "UNIFIED EVENT | type=STRUCTURE_FROZEN | reset_direction=%s | "
            "reset=%s | trigger=%s | top=%s@%s | bottom=%s@%s",
            reset_direction,
            reset_index,
            trigger_index,
            structure_top,
            top_source.index,
            structure_bottom,
            bottom_source.index,
        )

        same_direction_candidate = self._first_geometry_after_reset(
            reset_direction, reset_index
        )
        direct_same_direction_candidate = (
            self._first_direct_same_direction_after_reset(
                reset_direction, reset_index
            )
        )
        if (
            direct_same_direction_candidate is not None
            and (
                same_direction_candidate is None
                or direct_same_direction_candidate.break_idx
                < same_direction_candidate.break_idx
            )
        ):
            same_direction_candidate = direct_same_direction_candidate
        opposite_direction = "bearish" if reset_direction == "bullish" else "bullish"
        opposite_direction_candidate = self._first_same_direction_after_reset(
            opposite_direction, reset_index
        )
        # The Reset candle inherits opposite-leg ownership only when the
        # reaction being Reset was itself the confirmed cross-direction owner
        # of the current Gate.  Applying this to an ordinary same-direction
        # chain would swallow its already-valid Normal Search successor.
        reset_event_is_exact = bool(
            self.all_resets[reset_direction]
            and self.all_resets[reset_direction][-1].from_first_idx
            == previous.first_idx
            and self.all_resets[reset_direction][-1].index == reset_index
        )
        reset_seeded_opposite = (
            self._opposite_candidate_from_active_reset(
                reset_direction, reset_index
            )
            if previous.cross_direction_chain_owner and reset_event_is_exact
            else None
        )
        if (
            reset_seeded_opposite is not None
            and (
                opposite_direction_candidate is None
                or reset_seeded_opposite.break_idx
                == opposite_direction_candidate.break_idx
            )
        ):
            opposite_direction_candidate = reset_seeded_opposite

        race_index = trigger_index + 1
        while race_index <= self.end_index:
            candle = self.candles[race_index]
            top_break = candle.high > structure_top
            bottom_break = candle.low < structure_bottom
            if top_break and bottom_break:
                top_first = reset_direction == "bullish"
                end = candle.timestamp + self.timeframe
                for second in self.seconds_between(candle.timestamp, end):
                    crosses_top = second.high > structure_top
                    crosses_bottom = second.low < structure_bottom
                    if crosses_top or crosses_bottom:
                        top_first = (reset_direction == "bullish"
                                     if crosses_top and crosses_bottom else crosses_top)
                        break
                top_break, bottom_break = top_first, not top_first

            # After a healthy reaction is Reset, the first complete geometry
            # in that same direction owns the new reaction.  The opposite
            # direction is considered only after its main boundary branch.
            if (
                same_direction_candidate is not None
                and same_direction_candidate.break_idx == race_index
            ):
                trace(
                    "UNIFIED EVENT | type=POST_RESET_SAME_DIRECTION | "
                    "direction=%s | first=%s | break=%s",
                    reset_direction,
                    same_direction_candidate.first_idx,
                    same_direction_candidate.break_idx,
                )
                return reset_direction, same_direction_candidate, race_index + 1

            if (
                opposite_direction_candidate is not None
                and opposite_direction_candidate.break_idx == race_index
            ):
                trace(
                    "UNIFIED EVENT | type=POST_RESET_OPPOSITE_REACTION | "
                    "direction=%s | first=%s | break=%s",
                    opposite_direction,
                    opposite_direction_candidate.first_idx,
                    opposite_direction_candidate.break_idx,
                )
                return (
                    opposite_direction,
                    opposite_direction_candidate,
                    race_index + 1,
                )

            if reset_direction == "bullish" and bottom_break:
                box_top, box_top_source = self.maximum_high(
                    trigger_index, race_index
                )
                candidate = Candidate(
                    first_idx=trigger_index,
                    first_time=trigger.display_time,
                    box_top_source_idx=box_top_source.index,
                    box_top_source_time=box_top_source.display_time,
                    box_top=box_top,
                    box_bottom_source_idx=bottom_source.index,
                    box_bottom_source_time=bottom_source.display_time,
                    box_bottom=structure_bottom,
                    break_idx=race_index,
                    break_time=candle.display_time,
                    mode="A",
                )
                self._refine("bearish", candidate, candle)
                return "bearish", candidate, race_index + 1

            if reset_direction == "bearish" and top_break:
                box_bottom, box_bottom_source = self.minimum_low(
                    trigger_index, race_index
                )
                candidate = Candidate(
                    first_idx=trigger_index,
                    first_time=trigger.display_time,
                    box_top_source_idx=top_source.index,
                    box_top_source_time=top_source.display_time,
                    box_top=structure_top,
                    box_bottom_source_idx=box_bottom_source.index,
                    box_bottom_source_time=box_bottom_source.display_time,
                    box_bottom=box_bottom,
                    break_idx=race_index,
                    break_time=candle.display_time,
                    mode="A",
                )
                self._refine("bullish", candidate, candle)
                return "bullish", candidate, race_index + 1

            same_direction_break = (
                reset_direction == "bullish" and top_break
            ) or (reset_direction == "bearish" and bottom_break)
            if same_direction_break:
                direction = reset_direction
                required_tag = "RED" if direction == "bullish" else "GREEN"
                first_index = race_index
                while (
                    first_index <= self.end_index
                    and self.candles[first_index].tag != required_tag
                ):
                    first_index += 1
                if first_index > self.end_index:
                    return None, None, self.end_index + 1
                first = self.candles[first_index]
                if direction == "bullish":
                    box_top, box_top_source = self.maximum_high(
                        race_index, first_index
                    )
                    candidate = Candidate(
                        first_idx=first_index,
                        first_time=first.display_time,
                        box_top_source_idx=box_top_source.index,
                        box_top_source_time=box_top_source.display_time,
                        box_top=box_top,
                        box_bottom_source_idx=first_index,
                        box_bottom_source_time=first.display_time,
                        box_bottom=first.low,
                        mode="A",
                    )
                else:
                    box_bottom, box_bottom_source = self.minimum_low(
                        race_index, first_index
                    )
                    candidate = Candidate(
                        first_idx=first_index,
                        first_time=first.display_time,
                        box_top_source_idx=first_index,
                        box_top_source_time=first.display_time,
                        box_top=first.high,
                        box_bottom_source_idx=box_bottom_source.index,
                        box_bottom_source_time=box_bottom_source.display_time,
                        box_bottom=box_bottom,
                        mode="A",
                    )

                scan = first_index + 1
                while scan <= self.end_index:
                    current = self.candles[scan]
                    if direction == "bullish":
                        if current.low < structure_bottom:
                            self._append_reset(
                                "bullish", current, structure_bottom, first_index
                            )
                            if (
                                opposite_direction_candidate is not None
                                and opposite_direction_candidate.first_idx == scan + 1
                            ):
                                return (
                                    opposite_direction,
                                    opposite_direction_candidate,
                                    opposite_direction_candidate.break_idx + 1,
                                )
                            return self._after_double_reset("bullish", scan)
                        if current.low < candidate.box_bottom:
                            candidate.box_bottom = current.low
                            candidate.box_bottom_source_idx = current.index
                            candidate.box_bottom_source_time = current.display_time
                        if current.high > candidate.box_top:
                            candidate.break_idx = current.index
                            candidate.break_time = current.display_time
                            self._refine("bullish", candidate, current)
                            return "bullish", candidate, scan + 1
                    else:
                        if current.high > structure_top:
                            self._append_reset(
                                "bearish", current, structure_top, first_index
                            )
                            if (
                                opposite_direction_candidate is not None
                                and opposite_direction_candidate.first_idx == scan + 1
                            ):
                                return (
                                    opposite_direction,
                                    opposite_direction_candidate,
                                    opposite_direction_candidate.break_idx + 1,
                                )
                            return self._after_double_reset("bearish", scan)
                        if current.high > candidate.box_top:
                            candidate.box_top = current.high
                            candidate.box_top_source_idx = current.index
                            candidate.box_top_source_time = current.display_time
                        if current.low < candidate.box_bottom:
                            candidate.break_idx = current.index
                            candidate.break_time = current.display_time
                            self._refine("bearish", candidate, current)
                            return "bearish", candidate, scan + 1
                    scan += 1
                return None, None, self.end_index + 1
            race_index += 1
        return None, None, self.end_index + 1

    def detect(self) -> DetectionResult:
        direction = self.output_direction
        initial = self._first_initial(direction)
        if initial is None:
            return DetectionResult(
                direction=direction,
                reactions=[],
                resets=[],
                start_index=self.start_index,
                end_index=self.end_index,
            )
        self._append_reaction(direction, initial)
        previous = initial
        index = initial.break_idx + 1
        running_value = self.candles[initial.break_idx].high if direction == "bullish" else self.candles[initial.break_idx].low
        running_source = initial.break_idx
        candidate: Candidate | None = None
        initial_break_candle = self.candles[initial.break_idx]
        initial_helper = self.bull if direction == "bullish" else self.bear
        initial_analysis = (
            initial_helper.breakout_analysis(initial, initial_break_candle)
            if direction == "bullish"
            else initial_helper.breakdown_analysis(initial, initial_break_candle)
        )
        initial_reset_second = (
            initial_helper.post_breakout_reset(
                initial_analysis, initial.box_bottom, initial_break_candle
            )
            if direction == "bullish"
            else initial_helper.post_breakdown_reset(
                initial_analysis, initial.box_top, initial_break_candle
            )
        )
        pending_reset_index = (
            initial.break_idx if initial_reset_second is not None else None
        )
        if initial_reset_second is not None:
            self._append_reset(
                direction,
                initial_break_candle,
                initial.box_bottom if direction == "bullish" else initial.box_top,
                initial.first_idx,
                initial_reset_second.display_time,
            )

        while index <= self.end_index:
            candle = self.candles[index]
            self.trace_state("unified-" + direction, candle, "B", "WAITING" if candidate else "SCANNING", candidate)
            reset = pending_reset_index is not None or (
                candle.low < previous.box_bottom
                if direction == "bullish"
                else candle.high > previous.box_top
            )
            candidate_break = candidate is not None and (
                candle.high > candidate.box_top if direction == "bullish" else candle.low < candidate.box_bottom
            )
            if reset and candidate_break:
                if direction == "bullish":
                    reset = self.bull.confirmed_reset_before_breakout(candidate, candle, previous.box_bottom)
                else:
                    reset = self.bear.confirmed_reset_before_breakdown(candidate, candle, previous.box_top)
            if reset:
                reset_index = (
                    pending_reset_index
                    if pending_reset_index is not None
                    else index
                )
                reset_candle = self.candles[reset_index]
                pending_reset_index = None
                level = previous.box_bottom if direction == "bullish" else previous.box_top
                already_recorded = (
                    self.all_resets[direction]
                    and self.all_resets[direction][-1].from_first_idx
                    == previous.first_idx
                )
                if not already_recorded:
                    self._append_reset(
                        direction, reset_candle, level, previous.first_idx
                    )
                # A Reset reopens the ordinary same-direction ownership gate.
                # The geometric relaxation belongs only to the cross-direction
                # structural/E path and must not relabel every normal Reset.
                direct_candidate = self._first_direct_same_direction_after_reset(
                    direction, reset_index
                )
                # Both paths are valid interpretations of the same requested-
                # direction restart. The chronologically first confirmation
                # wins; a later Anchor-based candidate must never hide an
                # already complete direct post-Reset color sequence.
                structural = direct_candidate
                if structural is None or structural.break_idx is None:
                    break
                structural.mode = "A"
                structural.cross_direction_origin = False
                structural.cross_direction_chain_owner = False
                if not self._append_reaction(direction, structural):
                    candidate = None
                    index = structural.break_idx + 1
                    pending_reset_index = structural.break_idx
                    continue
                previous = structural
                index = structural.break_idx + 1
                running_value = self.candles[structural.break_idx].high if direction == "bullish" else self.candles[structural.break_idx].low
                running_source = structural.break_idx
                break_candle = self.candles[structural.break_idx]
                helper = self.bull if direction == "bullish" else self.bear
                analysis = (
                    helper.breakout_analysis(structural, break_candle)
                    if direction == "bullish"
                    else helper.breakdown_analysis(structural, break_candle)
                )
                post_reset_second = (
                    helper.post_breakout_reset(
                        analysis, structural.box_bottom, break_candle
                    )
                    if direction == "bullish"
                    else helper.post_breakdown_reset(
                        analysis, structural.box_top, break_candle
                    )
                )
                if post_reset_second is not None:
                    reset_level = (
                        structural.box_bottom
                        if direction == "bullish"
                        else structural.box_top
                    )
                    self._append_reset(
                        direction,
                        break_candle,
                        reset_level,
                        structural.first_idx,
                        post_reset_second.display_time,
                    )
                    # The confirmation candle has already reset the reaction
                    # after its exact intrabar confirmation. Its remainder
                    # cannot seed a Normal successor. Restart from the next
                    # main candle as a fresh Leg-Start search.
                    candidate = None
                    pending_reset_index = structural.break_idx
                else:
                    candidate = self._candidate_from_confirmation_remainder(
                        direction, structural, break_candle, analysis
                    )
                continue

            if candidate is not None:
                if direction == "bullish":
                    if candle.low < candidate.box_bottom:
                        candidate.box_bottom = candle.low
                        candidate.box_bottom_source_idx = candle.index
                        candidate.box_bottom_source_time = candle.display_time
                    if candle.high > candidate.box_top:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        analysis = self._refine(direction, candidate, candle)
                        post_reset_second = self.bull.post_breakout_reset(
                            analysis, candidate.box_bottom, candle
                        )
                        self._append_reaction(direction, candidate)
                        previous = replace(candidate)
                        running_value = candle.high
                        running_source = candle.index
                        if post_reset_second is not None:
                            self._append_reset(
                                direction,
                                candle,
                                previous.box_bottom,
                                previous.first_idx,
                                post_reset_second.display_time,
                            )
                            candidate = None
                            pending_reset_index = candle.index
                        else:
                            candidate = self._candidate_from_confirmation_remainder(
                                direction, previous, candle, analysis
                            )
                else:
                    if candle.high > candidate.box_top:
                        candidate.box_top = candle.high
                        candidate.box_top_source_idx = candle.index
                        candidate.box_top_source_time = candle.display_time
                    if candle.low < candidate.box_bottom:
                        candidate.break_idx = candle.index
                        candidate.break_time = candle.display_time
                        analysis = self._refine(direction, candidate, candle)
                        post_reset_second = self.bear.post_breakdown_reset(
                            analysis, candidate.box_top, candle
                        )
                        self._append_reaction(direction, candidate)
                        previous = replace(candidate)
                        running_value = candle.low
                        running_source = candle.index
                        if post_reset_second is not None:
                            self._append_reset(
                                direction,
                                candle,
                                previous.box_top,
                                previous.first_idx,
                                post_reset_second.display_time,
                            )
                            candidate = None
                            pending_reset_index = candle.index
                        else:
                            candidate = self._candidate_from_confirmation_remainder(
                                direction, previous, candle, analysis
                            )
            else:
                if direction == "bullish" and candle.tag == "RED":
                    top = max(running_value, candle.high)
                    top_source = running_source if running_value >= candle.high else candle.index
                    bottom_start = top_source + 1 if top_source < candle.index else candle.index
                    bottom, bottom_source = self.minimum_low(bottom_start, candle.index)
                    candidate = Candidate(candle.index, candle.display_time, top_source, self.candles[top_source].display_time, top, bottom_source.index, bottom_source.display_time, bottom, mode="B")
                elif direction == "bearish" and candle.tag == "GREEN":
                    bottom = min(running_value, candle.low)
                    bottom_source = running_source if running_value <= candle.low else candle.index
                    top_start = bottom_source + 1 if bottom_source < candle.index else candle.index
                    top, top_source = self.maximum_high(top_start, candle.index)
                    candidate = Candidate(candle.index, candle.display_time, top_source.index, top_source.display_time, top, bottom_source, self.candles[bottom_source].display_time, bottom, mode="B")
            if direction == "bullish" and (running_value is None or candle.high > running_value):
                running_value, running_source = candle.high, candle.index
            if direction == "bearish" and (running_value is None or candle.low < running_value):
                running_value, running_source = candle.low, candle.index
            index += 1

        return DetectionResult(
            direction=self.output_direction,
            reactions=self.all_reactions[self.output_direction],
            resets=self.all_resets[self.output_direction],
            start_index=self.start_index,
            end_index=self.end_index,
        )


def first_geometric_reaction(
    candles: Sequence[Candle],
    seconds: Sequence[Candle],
    start_index: int,
    end_index: int,
    direction: str,
) -> Candidate | None:
    """Return the first complete geometry without the Reset ownership gate.

    This narrow public seam is for E ResetLeg evidence.  It preserves the
    authoritative candle-color, box construction, strict confirmation and
    intrabar refinement rules while intentionally omitting ordinary Reset
    ownership, exactly as required by the E contract.
    """
    if direction not in {"bullish", "bearish"}:
        raise ValueError("Direction must be 'bullish' or 'bearish'.")
    if not candles or end_index < start_index:
        return None
    reset_index = max(0, int(start_index) - 1)
    detector = UnifiedReactionDetector(
        candles,
        seconds,
        reset_index,
        min(int(end_index), len(candles) - 1),
        direction,
    )
    return detector._first_geometry_after_reset(
        direction, reset_index, min(int(end_index), len(candles) - 1)
    )


def output_file_name(direction: str, start: datetime, end: datetime) -> str:
    prefix = "GREENbox" if direction == "bullish" else "REDbox"
    return f"{prefix} from {safe_timestamp(start)} _ to {safe_timestamp(end)}.txt"


def build_report(
    result: DetectionResult,
    candles: Sequence[Candle],
    script_name: str,
) -> str:
    bullish = result.direction == "bullish"
    direction_title = "Bullish" if bullish else "Bearish"
    algorithm_version = f"v{ENGINE_VERSION}"
    lines: list[str] = [
        f"# {direction_title} Reaction Analysis (Algorithm {algorithm_version})",
        "",
        f"Generated exclusively by {script_name} from the supplied candle inputs.",
        f"Analysis range: Index {result.start_index} "
        f"({candles[result.start_index].display_time}) through Index "
        f"{result.end_index} ({candles[result.end_index].display_time}).",
        "No reaction value is manually inserted, overridden, or corrected.",
        "",
        f"# Total {direction_title} Reactions Found: {len(result.reactions)}",
        "",
        "---",
        "",
    ]

    previous_break: Candidate | None = None
    for number, reaction in enumerate(result.reactions, start=1):
        mode_label = "Leg-Start Rule" if reaction.mode == "A" else "Normal Search"
        lines.append(f"### Reaction {number}  <sub>({mode_label})</sub>")

        if bullish:
            if previous_break is None:
                lines.append("- **Previous Breakout:** None - start of analysis range")
            else:
                lines.append(
                    f"- **Previous Breakout:** Index {previous_break.break_idx} "
                    f"({previous_break.break_time})"
                )
            lines.extend(
                [
                    f"- **Reaction Box Start (FirstRed):** Index {reaction.first_idx} "
                    f"({reaction.first_time})",
                    f"- **BoxTop Source:** Index {reaction.box_top_source_idx} "
                    f"({reaction.box_top_source_time})",
                    f"- **BoxTop:** {format_price(reaction.box_top)}",
                    f"- **Reaction Box End / Breakout:** Index {reaction.break_idx} "
                    f"({reaction.break_time})",
                    f"- **BoxBottom Source:** Index {reaction.box_bottom_source_idx} "
                    f"({reaction.box_bottom_source_time})",
                    f"- **BoxBottom:** {format_price(reaction.box_bottom)}",
                ]
            )
        else:
            if previous_break is None:
                lines.append("- **Previous Breakdown:** None - start of analysis range")
            else:
                lines.append(
                    f"- **Previous Breakdown:** Index {previous_break.break_idx} "
                    f"({previous_break.break_time})"
                )
            lines.extend(
                [
                    f"- **Reaction Box Start (FirstGreen):** Index {reaction.first_idx} "
                    f"({reaction.first_time})",
                    f"- **BoxBottom Source:** Index {reaction.box_bottom_source_idx} "
                    f"({reaction.box_bottom_source_time})",
                    f"- **BoxBottom:** {format_price(reaction.box_bottom)}",
                    f"- **Reaction Box End / Breakdown:** Index {reaction.break_idx} "
                    f"({reaction.break_time})",
                    f"- **BoxTop Source:** Index {reaction.box_top_source_idx} "
                    f"({reaction.box_top_source_time})",
                    f"- **BoxTop:** {format_price(reaction.box_top)}",
                ]
            )

        lines.extend(["- **Status:** Confirmed", ""])
        previous_break = reaction

    lines.extend(["---", "", "## Reset Events", ""])
    for event in result.resets:
        second_detail = (
            f" at {event.second_time} inside the candle" if event.second_time else ""
        )
        if bullish:
            lines.append(
                f"- **Reset at Index {event.index} ({event.display_time})**"
                f"{second_detail} - low broke below previous BoxBottom "
                f"({format_price(event.broken_level)})"
            )
        else:
            lines.append(
                f"- **Reset at Index {event.index} ({event.display_time})**"
                f"{second_detail} - high broke above previous BoxTop "
                f"({format_price(event.broken_level)})"
            )

    lines.extend(["", "---", "", "## Summary Table", ""])
    if bullish:
        lines.extend(
            [
                "| # | Mode | FirstRed | BoxTop Src | BoxTop | Breakout | "
                "BoxBottom Src | BoxBottom |",
                "|---|------|----------|------------|--------|----------|"
                "---------------|-----------|",
            ]
        )
        for number, reaction in enumerate(result.reactions, start=1):
            mode_label = "Leg-Start" if reaction.mode == "A" else "Normal"
            lines.append(
                f"| {number} | {mode_label} | {reaction.first_time} "
                f"(idx {reaction.first_idx}) | idx {reaction.box_top_source_idx} | "
                f"{format_price(reaction.box_top)} | {reaction.break_time} "
                f"(idx {reaction.break_idx}) | idx {reaction.box_bottom_source_idx} | "
                f"{format_price(reaction.box_bottom)} |"
            )
    else:
        lines.extend(
            [
                "| # | Mode | FirstGreen | BoxBottom Src | BoxBottom | Breakdown | "
                "BoxTop Src | BoxTop |",
                "|---|------|------------|---------------|-----------|-----------|"
                "------------|--------|",
            ]
        )
        for number, reaction in enumerate(result.reactions, start=1):
            mode_label = "Leg-Start" if reaction.mode == "A" else "Normal"
            lines.append(
                f"| {number} | {mode_label} | {reaction.first_time} "
                f"(idx {reaction.first_idx}) | idx {reaction.box_bottom_source_idx} | "
                f"{format_price(reaction.box_bottom)} | {reaction.break_time} "
                f"(idx {reaction.break_idx}) | idx {reaction.box_top_source_idx} | "
                f"{format_price(reaction.box_top)} |"
            )

    return "\n".join(lines) + "\n"


def prompt_direction() -> str:
    print_section("STEP 1 OF 3 - REACTION TYPE", Style.MAGENTA)
    print(f"  {Style.apply('1', Style.BOLD, Style.GREEN)}  Green box  (Bullish reaction)")
    print(f"  {Style.apply('2', Style.BOLD, Style.RED)}  Red box    (Bearish reaction)")
    while True:
        value = input(f"\n  {Style.apply('Select [1/2]:', Style.BOLD)} ").strip().lower()
        if value in {"1", "g", "green", "bullish"}:
            return "bullish"
        if value in {"2", "r", "red", "bearish"}:
            return "bearish"
        log("WARN", "Enter 1 for Green box or 2 for Red box.")


def prompt_date(label: str, default: datetime) -> str:
    default_text = default.strftime(USER_DATE_FORMAT)
    while True:
        raw = input(f"  Date {Style.apply(f'[{default_text}]', Style.DIM)}: ").strip()
        if not raw:
            return default_text
        try:
            datetime.strptime(raw, USER_DATE_FORMAT)
        except ValueError:
            log("WARN", "Invalid date. Use YYYY-MM-DD, for example 2026-08-12.")
            continue
        return raw


def prompt_time(label: str, default: datetime) -> str:
    default_text = default.strftime(USER_TIME_FORMAT)
    while True:
        raw = input(f"  Time {Style.apply(f'[{default_text}]', Style.DIM)}: ").strip()
        if not raw:
            return default_text
        try:
            datetime.strptime(raw, USER_TIME_FORMAT)
        except ValueError:
            log("WARN", "Invalid time. Use HH-MM-SS, for example 22-10-33.")
            continue
        return raw


def prompt_datetime(title: str, default: datetime, step: int) -> datetime:
    color = Style.GREEN if title == "FROM" else Style.RED
    print_section(f"STEP {step} OF 3 - {title}", color)
    print(Style.apply("  Enter date and time in two separate fields.", Style.DIM))
    while True:
        date_text = prompt_date(title, default)
        time_text = prompt_time(title, default)
        try:
            return datetime.strptime(f"{date_text} {time_text}", USER_DATETIME_FORMAT)
        except ValueError as exc:
            log("WARN", f"Invalid date/time: {exc}. Please enter both fields again.")


def parse_cli_datetime(value: str) -> datetime:
    accepted_formats = (USER_DATETIME_FORMAT, "%Y-%m-%d %H:%M:%S", TIMESTAMP_FORMAT)
    for date_format in accepted_formats:
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            pass
    raise argparse.ArgumentTypeError(
        "Expected YYYY-MM-DD HH-MM-SS (preferred), for example "
        f"2026-08-12 22-10-33; received: {value}"
    )


def select_range(
    candles: Sequence[Candle],
    start: datetime,
    end: datetime,
    now: datetime | None = None,
) -> tuple[int, int]:
    current_time = now or datetime.now()
    if end < start:
        raise ValueError("TO must be later than or equal to FROM.")
    if end > current_time:
        raise ValueError(
            "TO cannot be later than the current system time "
            f"({current_time.strftime(USER_DATETIME_FORMAT)})."
        )

    times = [candle.timestamp for candle in candles]
    start_index = bisect.bisect_left(times, start)
    if start_index >= len(times) or times[start_index] != start:
        raise ValueError(
            "FROM does not exist in the 30-second candle file. "
            "Please select the range again."
        )
    end_index = bisect.bisect_left(times, end)
    if end_index >= len(times) or times[end_index] != end:
        raise ValueError(
            "TO does not exist in the 30-second candle file. "
            "Please select the range again."
        )
    return start_index, end_index


def choose_range_interactively(
    candles: Sequence[Candle], available_start: datetime, available_end: datetime
) -> tuple[datetime, datetime, int, int]:
    """Prompt until both exact candle boundaries and time ordering are valid."""
    while True:
        from_time = prompt_datetime("FROM", available_start, 2)
        to_time = prompt_datetime("TO", available_end, 3)
        try:
            start_index, end_index = select_range(candles, from_time, to_time)
        except ValueError as exc:
            log("ERROR", str(exc))
            log("INFO", "Please enter FROM and TO again.")
            continue
        return from_time, to_time, start_index, end_index


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Interactive Bullish/Bearish reaction detector."
    )
    parser.add_argument("--direction", choices=("bullish", "bearish"))
    parser.add_argument("--from", dest="from_time", type=parse_cli_datetime)
    parser.add_argument("--to", dest="to_time", type=parse_cli_datetime)
    parser.add_argument("--input-30s", type=Path)
    parser.add_argument("--input-1s", type=Path)
    parser.add_argument("--result-dir", type=Path)
    parser.add_argument("--no-color", action="store_true")
    return parser


def main() -> int:
    configure_console_encoding()
    args = build_argument_parser().parse_args()
    Style.enabled = not args.no_color and sys.stdout.isatty()
    enable_windows_ansi()
    print_banner()

    app_dir = Path(__file__).resolve().parent
    workspace_root = app_dir.parents[3]
    temporary_input = workspace_root / "market-data" / "tmp" / "reaction-detector" / "legacy-formatted-input"
    input_30s = args.input_30s or temporary_input / "30S-formated.txt"
    input_1s = args.input_1s or temporary_input / "1S-formated.txt"
    result_dir = args.result_dir or workspace_root / "Results" / "reaction-detector"

    started = time.perf_counter()
    log("LOAD", f"Reading main candles: {input_30s}")
    candles = read_candles(input_30s)
    log("OK", f"Loaded {len(candles):,} main candles.")

    log("LOAD", f"Reading one-second candles: {input_1s}")
    one_second_candles = read_candles(input_1s)
    log("OK", f"Loaded {len(one_second_candles):,} one-second candles.")

    available_start = candles[0].timestamp
    available_end = candles[-1].timestamp
    log(
        "INFO",
        f"Available range: {available_start.strftime(USER_DATETIME_FORMAT)}  ->  "
        f"{available_end.strftime(USER_DATETIME_FORMAT)}",
    )

    direction = args.direction or prompt_direction()
    if args.from_time is None and args.to_time is None:
        from_time, to_time, start_index, end_index = choose_range_interactively(
            candles, available_start, available_end
        )
    else:
        from_time = args.from_time or prompt_datetime("FROM", available_start, 2)
        to_time = args.to_time or prompt_datetime("TO", available_end, 3)
        start_index, end_index = select_range(candles, from_time, to_time)

    actual_start = candles[start_index].timestamp
    actual_end = candles[end_index].timestamp

    selected_count = end_index - start_index + 1
    direction_label = "Green box / Bullish" if direction == "bullish" else "Red box / Bearish"
    print_section("CALCULATING REACTIONS", Style.MAGENTA)
    log("RUN", f"Direction: {direction_label}")
    log("RUN", f"Main-candle range: Index {start_index} through {end_index}")
    log("RUN", f"Processing {selected_count:,} main candles...")

    detector = UnifiedReactionDetector(
        candles,
        one_second_candles,
        start_index,
        end_index,
        direction,
    )

    result = detector.detect()
    report = build_report(result, candles, Path(__file__).name)

    result_dir.mkdir(parents=True, exist_ok=True)
    output_path = result_dir / output_file_name(direction, actual_start, actual_end)
    output_path.write_text(report, encoding="utf-8", newline="\n")

    elapsed = time.perf_counter() - started
    print_section("COMPLETED", Style.GREEN)
    log("OK", f"Confirmed reactions: {len(result.reactions):,}")
    log("OK", f"Reset events: {len(result.resets):,}")
    log("SAVE", f"Output saved to: {output_path}")
    log("INFO", f"Elapsed time: {elapsed:.2f} seconds")
    FILE_LOGGER.info(
        "RUN END | status=success | direction=%s | reactions=%s | resets=%s | "
        "elapsed_seconds=%.2f | output=%s",
        direction, len(result.reactions), len(result.resets), elapsed, output_path,
    )
    print()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print()
        log("WARN", "Operation cancelled by user.")
        if FILE_LOGGER.handlers:
            FILE_LOGGER.warning("RUN END | status=cancelled")
        raise SystemExit(130)
    except Exception as exc:
        print()
        log("ERROR", str(exc))
        if FILE_LOGGER.handlers:
            FILE_LOGGER.exception("RUN END | status=error | error=%s", exc)
        raise SystemExit(1)
