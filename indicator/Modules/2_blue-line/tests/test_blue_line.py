from __future__ import annotations

import unittest
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from app.blue_line import count_scale_strikes, detect_blue_lines


@dataclass
class Candle:
    index: int
    timestamp: datetime
    tag: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal


@dataclass
class Reaction:
    first_idx: int
    break_idx: int
    box_top: Decimal
    box_bottom: Decimal
    mode: str = "B"
    leg_boundary_value: Decimal | None = None
    anchor_value: Decimal | None = None


@dataclass
class Reset:
    index: int
    display_time: str
    broken_level: Decimal
    from_first_idx: int
    second_time: str | None = None


def candle(index: int, tag: str, high: str, low: str) -> Candle:
    stamp = datetime(2026, 8, 11, 6, 36, 30) + timedelta(seconds=30 * index)
    high_value, low_value = Decimal(high), Decimal(low)
    if tag == "GREEN":
        open_value, close_value = low_value, high_value
    elif tag == "RED":
        open_value, close_value = high_value, low_value
    else:
        open_value = close_value = (high_value + low_value) / 2
    return Candle(index, stamp, tag, open_value, high_value, low_value, close_value)


class BlueLineTests(unittest.TestCase):
    def test_leg_start_scale_prefers_anchor_over_range_open_boundary(self):
        candles = [
            candle(0, "RED", "4390.16", "4389.595"),
            candle(1, "GREEN", "4391.1", "4389.785"),
            candle(2, "RED", "4390.7", "4390.175"),
            candle(3, "GREEN", "4390.385", "4390.075"),
            candle(4, "GREEN", "4391.245", "4390.43"),
        ]
        reactions = [
            Reaction(
                0, 1, Decimal("4390.395"), Decimal("4389.595"), "A",
                Decimal("4389.89"), Decimal("4388.98"),
            ),
            Reaction(2, 4, Decimal("4391.1"), Decimal("4390.075"), "B"),
        ]
        lines = detect_blue_lines("bullish", reactions, candles, [], 30)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].reaction_number, 2)
        self.assertEqual(lines[0].previous_strike_count, 0)
        self.assertEqual(lines[0].strike_count, 1)

    def test_reset_creates_one_fifth_blue_line_and_requires_spacing(self):
        candles = [
            candle(0, "RED", "110", "100"),
            candle(1, "GREEN", "121", "105"),
            candle(2, "RED", "112", "97"),
            candle(3, "GREEN", "122", "106"),
            candle(4, "RED", "111", "96"),
        ]
        reactions = [
            Reaction(0, 1, Decimal("120"), Decimal("100"), "A", Decimal("90")),
            Reaction(2, 3, Decimal("121"), Decimal("97"), "A", Decimal("90")),
        ]
        resets = [
            Reset(2, candles[2].timestamp.strftime("%Y-%m-%d %H:%M:%S"), Decimal("100"), 0),
            Reset(4, candles[4].timestamp.strftime("%Y-%m-%d %H:%M:%S"), Decimal("97"), 2),
        ]
        lines = detect_blue_lines("bullish", reactions, candles, [], 30, resets)
        reset_lines = [line for line in lines if line.kind == "reset"]
        self.assertEqual([line.source_index for line in reset_lines], [2, 4])
        self.assertEqual(reset_lines[0].line_price, Decimal("100"))
        self.assertEqual(reset_lines[1].line_price, Decimal("99"))

    def test_reset_that_forms_before_stopping_prior_blue_is_visual_a_only(self):
        candles = [
            candle(0, "RED", "110", "100"),
            candle(1, "GREEN", "121", "105"),
            candle(2, "RED", "112", "97"),
            candle(3, "GREEN", "122", "106"),
            candle(4, "RED", "111", "96"),
        ]
        reactions = [
            Reaction(0, 1, Decimal("120"), Decimal("100"), "A", Decimal("90")),
            Reaction(2, 3, Decimal("121"), Decimal("99"), "A", Decimal("90")),
        ]
        resets = [
            Reset(2, candles[2].timestamp.strftime("%Y-%m-%d %H:%M:%S"), Decimal("100"), 0),
            Reset(4, candles[4].timestamp.strftime("%Y-%m-%d %H:%M:%S"), Decimal("99"), 2),
        ]
        lines = detect_blue_lines("bullish", reactions, candles, [], 30, resets)
        self.assertEqual([line.calculation_valid for line in lines], [True, False])
        self.assertLess(lines[1].source_extreme, lines[0].source_extreme)

    def test_bearish_reset_is_exact_upper_fifth_mirror(self):
        candles = [
            candle(0, "GREEN", "110", "100"),
            candle(1, "RED", "108", "90"),
            candle(2, "GREEN", "120", "100"),
        ]
        reactions = [
            Reaction(0, 1, Decimal("110"), Decimal("90"), "A", Decimal("120"))
        ]
        resets = [
            Reset(2, candles[2].timestamp.strftime("%Y-%m-%d %H:%M:%S"), Decimal("110"), 0)
        ]
        lines = detect_blue_lines("bearish", reactions, candles, [], 30, resets)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].kind, "reset")
        self.assertEqual(lines[0].line_price, Decimal("116"))
        self.assertEqual(lines[0].source_extreme, Decimal("120"))

    def test_scale_blue_blocks_immediate_reset_blue(self):
        candles = [
            candle(0, "RED", "110", "99"),
            candle(1, "GREEN", "108", "101"),
            candle(2, "RED", "109", "97"),
            candle(3, "GREEN", "111", "100"),
            candle(4, "RED", "109", "95"),
            candle(5, "GREEN", "121", "105"),
            candle(6, "RED", "108", "94"),
        ]
        reactions = [
            Reaction(0, 1, Decimal("120"), Decimal("99"), "A", Decimal("90")),
            Reaction(2, 5, Decimal("120"), Decimal("95"), "B"),
        ]
        resets = [
            Reset(6, candles[6].timestamp.strftime("%Y-%m-%d %H:%M:%S"), Decimal("95"), 2)
        ]
        lines = detect_blue_lines("bullish", reactions, candles, [], 30, resets)
        self.assertEqual([line.kind for line in lines], ["scale"])

    def test_suppressed_scale_still_becomes_next_reference(self):
        candles = [
            candle(0, "RED", "110", "105"), candle(1, "GREEN", "121", "105"),
            candle(2, "RED", "111", "103"), candle(3, "GREEN", "122", "104"),
            candle(4, "RED", "112", "101"), candle(5, "GREEN", "113", "102"),
            candle(6, "RED", "111", "99"), candle(7, "GREEN", "123", "100"),
            candle(8, "RED", "113", "97"), candle(9, "GREEN", "114", "98"),
            candle(10, "RED", "112", "95"), candle(11, "GREEN", "124", "96"),
        ]
        reactions = [
            Reaction(0, 1, Decimal("120"), Decimal("105"), "A", Decimal("90")),
            Reaction(2, 3, Decimal("121"), Decimal("103"), "B"),
            Reaction(4, 7, Decimal("122"), Decimal("99"), "B"),
            Reaction(8, 11, Decimal("123"), Decimal("95"), "B"),
        ]
        lines = detect_blue_lines("bullish", reactions, candles, [], 30)
        self.assertEqual(
            [
                (line.reaction_number, line.previous_strike_count, line.strike_count)
                for line in lines
            ],
            [(2, 0, 1)],
        )

    def test_one_healthy_reaction_unlocks_later_scale_blue(self):
        candles = [
            candle(0, "RED", "110", "105"), candle(1, "GREEN", "121", "105"),
            candle(2, "RED", "111", "103"), candle(3, "GREEN", "122", "104"),
            candle(4, "RED", "119", "115"), candle(5, "GREEN", "123", "116"),
            candle(6, "RED", "117", "110"), candle(7, "GREEN", "124", "111"),
        ]
        reactions = [
            Reaction(0, 1, Decimal("120"), Decimal("105"), "A", Decimal("90")),
            Reaction(2, 3, Decimal("121"), Decimal("103"), "B"),
            Reaction(4, 5, Decimal("122"), Decimal("115"), "B"),
            Reaction(6, 7, Decimal("123"), Decimal("110"), "B"),
        ]
        lines = detect_blue_lines("bullish", reactions, candles, [], 30)
        self.assertEqual([line.reaction_number for line in lines], [2, 4])

    def test_user_confirmed_0640_two_strike_example(self):
        start = datetime(2026, 8, 11, 6, 37, 30)
        facts = [
            ("RED", "4411.96", "4411.26"),
            ("GREEN", "4413.465", "4411.27"),
            ("GREEN", "4413.915", "4413.115"),
            ("GREEN", "4414.805", "4413.23"),
            ("RED", "4415.01", "4413.485"),
            ("RED", "4413.77", "4412.43"),
            ("GREEN", "4413.83", "4412.595"),
            ("RED", "4413.885", "4412.375"),
            ("GREEN", "4413.76", "4412.44"),
            ("GREEN", "4414.56", "4413.365"),
            ("GREEN", "4415.35", "4414.3"),
        ]
        candles = []
        for index, (tag, high, low) in enumerate(facts):
            item = candle(index, tag, high, low)
            item.timestamp = start + timedelta(seconds=30 * index)
            candles.append(item)
        reactions = [
            Reaction(0, 1, Decimal("4412.47"), Decimal("4411.26"), "A", Decimal("4409.855")),
            Reaction(4, 10, Decimal("4415.01"), Decimal("4412.375"), "B"),
        ]
        lines = detect_blue_lines("bullish", reactions, candles, [], 30)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].strike_count, 2)
        self.assertEqual(lines[0].source_time, datetime(2026, 8, 11, 6, 41, 0))
        self.assertEqual(lines[0].source_extreme, Decimal("4412.375"))

    def test_bullish_counts_separated_strikes_and_draws_on_final_low(self):
        candles = [
            candle(0, "RED", "110", "99"),
            candle(1, "GREEN", "108", "101"),
            candle(2, "RED", "109", "97"),
            candle(3, "GREEN", "111", "100"),
            candle(4, "GREEN", "121", "105"),
        ]
        reactions = [
            Reaction(0, 1, Decimal("120"), Decimal("99"), "A", Decimal("90")),
            Reaction(0, 4, Decimal("120"), Decimal("97"), "B"),
        ]
        lines = detect_blue_lines("bullish", reactions, candles, [], 30)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].previous_strike_count, 1)
        self.assertEqual(lines[0].strike_count, 2)
        self.assertEqual(lines[0].source_index, 2)
        self.assertEqual(lines[0].line_price, Decimal("101"))
        self.assertEqual(
            lines[0].start_time,
            lines[0].source_time - timedelta(seconds=30),
        )
        self.assertEqual(
            lines[0].end_time,
            lines[0].source_time + timedelta(seconds=30),
        )
        self.assertEqual(lines[0].end_time - lines[0].start_time, timedelta(seconds=60))

    def test_equal_fibonacci_boundary_is_not_a_strike(self):
        candles = [candle(0, "GREEN", "120", "100")]
        reaction = Reaction(0, 0, Decimal("120"), Decimal("100"))
        level, strikes = count_scale_strikes(
            "bullish", reaction, candles, [], Decimal("87.63754045307443365695792880"), 30
        )
        self.assertEqual(level, Decimal("100.0000000000000000000000000"))
        self.assertEqual(strikes, [])

        bearish = [candle(0, "RED", "100", "80")]
        bearish_reaction = Reaction(0, 0, Decimal("100"), Decimal("80"))
        bearish_level, bearish_strikes = count_scale_strikes(
            "bearish",
            bearish_reaction,
            bearish,
            [],
            Decimal("112.3624595469255663430420712"),
            30,
        )
        self.assertEqual(bearish_level, Decimal("100.0000000000000000000000000"))
        self.assertEqual(bearish_strikes, [])

    def test_bearish_is_exact_mirror(self):
        candles = [
            candle(0, "GREEN", "101", "90"),
            candle(1, "RED", "99", "88"),
            candle(2, "GREEN", "103", "89"),
            candle(3, "RED", "100", "87"),
            candle(4, "RED", "99", "79"),
        ]
        reactions = [
            Reaction(0, 1, Decimal("101"), Decimal("80"), "A", Decimal("110")),
            Reaction(0, 4, Decimal("103"), Decimal("80"), "B"),
        ]
        lines = detect_blue_lines("bearish", reactions, candles, [], 30)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].previous_strike_count, 1)
        self.assertEqual(lines[0].strike_count, 2)
        self.assertEqual(lines[0].source_index, 2)
        self.assertEqual(lines[0].line_price, Decimal("98.33333333333333333333333333"))

    def test_same_one_second_candle_may_penetrate_and_break(self):
        main = [candle(0, "RED", "121", "95")]
        second = Candle(
            0,
            main[0].timestamp + timedelta(seconds=7),
            "RED",
            Decimal("118"),
            Decimal("121"),
            Decimal("95"),
            Decimal("117"),
        )
        reaction = Reaction(0, 0, Decimal("120"), Decimal("95"))
        _, strikes = count_scale_strikes(
            "bullish", reaction, main, [second], Decimal("90"), 30
        )
        self.assertEqual(len(strikes), 1)
        self.assertEqual(strikes[0].source_index, 0)

        bearish_main = [candle(0, "GREEN", "105", "79")]
        bearish_second = Candle(
            0,
            bearish_main[0].timestamp + timedelta(seconds=9),
            "GREEN",
            Decimal("82"),
            Decimal("105"),
            Decimal("79"),
            Decimal("83"),
        )
        bearish_reaction = Reaction(0, 0, Decimal("105"), Decimal("80"))
        _, bearish_strikes = count_scale_strikes(
            "bearish", bearish_reaction, bearish_main, [bearish_second], Decimal("110"), 30
        )
        self.assertEqual(len(bearish_strikes), 1)
        self.assertEqual(bearish_strikes[0].source_index, 0)


if __name__ == "__main__":
    unittest.main()
