from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from dataclasses import asdict, replace
import random
from types import SimpleNamespace


APP_DIR = Path(__file__).resolve().parent
TEST_ROOT = APP_DIR.parent
WORKSPACE_ROOT = APP_DIR.parents[3]
FORMATTED_INPUT = WORKSPACE_ROOT / "market-data" / "tmp" / "reaction-detector" / "legacy-formatted-input"
APP_PATH = APP_DIR / "Reaction-detection-new.py"
START = datetime(2026, 8, 11, 17, 13, 30)
END = datetime(2026, 8, 11, 19, 50, 0)


def load_module():
    spec = importlib.util.spec_from_file_location("reaction_detection_new", APP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {APP_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def reference_mirror_candles(module, candles):
    """Independent test reflection; does not call production mirror helpers."""
    return [replace(c, open=-c.open, high=-c.low, low=-c.high, close=-c.close,
                    tag={"GREEN": "RED", "RED": "GREEN"}.get(c.tag, c.tag))
            for c in candles]


def reflected_result(result):
    value = asdict(result)
    value['direction'] = 'bearish' if result.direction == 'bullish' else 'bullish'
    for item in value['reactions']:
        item['box_top'], item['box_bottom'] = -item['box_bottom'], -item['box_top']
        for suffix in ('idx', 'time'):
            a, b = 'box_top_source_'+suffix, 'box_bottom_source_'+suffix
            item[a], item[b] = item[b], item[a]
        for key in ('anchor_value', 'leg_boundary_value'):
            if item[key] is not None:
                item[key] = -item[key]
    for item in value['resets']:
        item['broken_level'] = -item['broken_level']
    return value


def chart_doji_regression(module):
    """Use real OHLC classification, including dojis, without historical input."""
    bridge_path = WORKSPACE_ROOT / "indicator/indicator-settings/backend/reaction_bridge.py"
    spec = importlib.util.spec_from_file_location("doji_bridge_test", bridge_path)
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    for o, c, expected in (("9", "10", "GREEN"), ("10", "9", "RED"),
                           ("10", "10.000", "GREEN"), ("0", "-0", "GREEN")):
        assert module.classify_candle_color(Decimal(o), Decimal(c)) == expected
    cases = (
        ("bearish", [(10,11,8,9),(9,10,"8.5",9),(9,"9.5",7,8)], 1),
        ("bullish", [(9,11,8,10),(10,11,9,10),(10,"10.5",9,"9.5"),
                     ("9.5",12,"9.4","11.5")], 2),
    )
    for direction, bars, expected_first in cases:
        rows = []
        for o, h, low, c in bars:
            for price in [o]*5+[h]*5+[low]*5+[c]*15:
                rows.append(dict(time=1800000000+len(rows), open=str(price),
                                 high=str(price), low=str(price), close=str(price)))
        lower, main = bridge.build_candle_views(module, rows, 30)
        assert main == bridge.build_candles(module, rows, 30)
        assert main[1].open == main[1].close and main[1].tag == "GREEN"
        assert all(c.tag == "GREEN" for c in lower)
        original = [asdict(c) for c in main]
        legacy = module.BearishDetector if direction == "bearish" else module.BullishDetector
        for detector in (legacy(main, lower, 0, len(main)-1),
                         module.UnifiedReactionDetector(main, lower, 0, len(main)-1, direction)):
            result = detector.detect()
            assert result.reactions and result.reactions[0].first_idx == expected_first
        assert [asdict(c) for c in main] == original
    blue = bridge.load_module("doji_blue_test", WORKSPACE_ROOT / "indicator/Modules/2_blue-line/app/blue_line.py")
    reaction = SimpleNamespace(first_idx=0, break_idx=0, box_top=Decimal(10), box_bottom=Decimal(0))
    for close, bull_count, bear_count in (("5", 1, 0), ("4", 0, 1)):
        candles = bridge.build_candles(module, [dict(time=1800000000, open="5",
                                                    high="11", low="0", close=close)], 30)
        for direction, reference, expected in (("bullish", 0, bull_count), ("bearish", 10, bear_count)):
            _, strikes = blue.count_scale_strikes(direction, reaction, candles, [], Decimal(reference), 30)
            assert len(strikes) == expected, (direction, close)
    print("PASS: chart GREEN-doji classification, aggregation and directional eligibility")


def reference_mirror_regression(module):
    """Compare complete outputs and geometry, not only event counts."""
    rng = random.Random(931)
    fixtures = [
        [(99,101,95,96),(96,99,93,98),(98,99,94,96),(96,103,96,102)],
        [(100,105,99,102),(102,110,90,101),(101,108,95,104),(104,109,92,98)],
    ]
    for _ in range(80):
        rows = []
        previous = 100
        for index in range(18):
            close = previous + rng.choice((-4,-2,-1,1,2,4))
            rows.append((previous, max(previous, close)+rng.randrange(4),
                         min(previous, close)-rng.randrange(4), close))
            previous = close
        fixtures.append(rows)
    base = datetime(2026, 1, 1)
    for number, rows in enumerate(fixtures):
        main, lower = [], []
        for index, (o,h,l,c) in enumerate(rows):
            stamp = base+timedelta(seconds=index*30)
            main.append(module.Candle(index,stamp,str(stamp),
                module.classify_candle_color(Decimal(o),Decimal(c)),
                Decimal(o),Decimal(h),Decimal(l),Decimal(c)))
            prices = [o]*5+[h]*5+[l]*5+[c]*15
            for price in prices:
                stamp = base+timedelta(seconds=len(lower))
                lower.append(module.Candle(len(lower),stamp,str(stamp),'GREEN',
                    *[Decimal(price)]*4))
        mirrored = reference_mirror_candles(module, main)
        # Lower rows are flat dojis: actual chart color stays GREEN even
        # after price reflection. Main rows in these mirror cases are non-doji.
        mirrored_lower = [replace(c, tag=module.classify_candle_color(c.open, c.close))
                          for c in reference_mirror_candles(module, lower)]
        bull = module.UnifiedReactionDetector(main,lower,0,len(main)-1,'bullish')
        bear = module.UnifiedReactionDetector(mirrored,mirrored_lower,0,len(main)-1,'bearish')
        assert asdict(bear.detect()) == reflected_result(bull.detect()), number
        for reset in (0, len(main)//2):
            a = bull._first_geometry_after_reset('bullish', reset)
            b = bear._first_geometry_after_reset('bearish', reset)
            wrapped = module.DetectionResult('bullish', [a] if a else [], [],0,len(main)-1)
            assert ([asdict(b)] if b else []) == reflected_result(wrapped)['reactions'], (number, reset)
    print('PASS: 82 full-output directional mirror histories and bounded geometry checks')


if __name__ == "__main__":
    module = load_module()
    chart_doji_regression(module)
    reference_mirror_regression(module)
    candles = module.read_candles(FORMATTED_INPUT / "30S-formated.txt")
    seconds = module.read_candles(FORMATTED_INPUT / "1S-formated.txt")
    start, end = module.select_range(candles, START, END)
    assert (start, end) == (4572, 4885)

    detector = module.UnifiedReactionDetector(
        candles, seconds, start, end, "bearish"
    )
    result = detector.detect()
    protected_bearish = {
        1: (4577, 4577, Decimal("4401.4500"), 4580, 4577, Decimal("4404.2100"), "A"),
        2: (4583, 4582, Decimal("4392.7600"), 4586, 4585, Decimal("4396.7050"), "B"),
        3: (4587, 4587, Decimal("4392.0850"), 4588, 4587, Decimal("4395.1600"), "B"),
        4: (4589, 4589, Decimal("4390.2650"), 4591, 4590, Decimal("4393.3650"), "B"),
        5: (4603, 4602, Decimal("4388.8200"), 4604, 4603, Decimal("4390.7400"), "A"),
        6: (4604, 4604, Decimal("4388.8050"), 4605, 4604, Decimal("4390.2000"), "B"),
        7: (4606, 4605, Decimal("4385.9500"), 4609, 4608, Decimal("4390.0200"), "B"),
    }
    for number, expected in protected_bearish.items():
        reaction = result.reactions[number - 1]
        actual = (
            reaction.first_idx,
            reaction.box_bottom_source_idx,
            reaction.box_bottom,
            reaction.break_idx,
            reaction.box_top_source_idx,
            reaction.box_top,
            reaction.mode,
        )
        assert actual == expected, (number, actual, expected)

    report = module.build_report(result, candles, APP_PATH.name)
    assert "**StructureTop:**" not in report
    assert "**StructureBottom:**" not in report
    assert all(reaction.first_idx != 4837 for reaction in result.reactions)

    bullish_start_time = datetime(2026, 8, 11, 19, 50, 0)
    bullish_end_time = datetime(2026, 8, 11, 21, 16, 0)
    bullish_start, bullish_end = module.select_range(
        candles, bullish_start_time, bullish_end_time
    )
    bullish_result = module.UnifiedReactionDetector(
        candles, seconds, bullish_start, bullish_end, "bullish"
    ).detect()
    # Directional post-Reset earliest-completion search yields 14
    # directional Bullish reactions because opposite patterns no longer own
    # or unlock Bullish state after Reset. Index 4967 is a lower leg floor,
    # so it cannot be FirstRed.
    expected_bullish = (
        (4888, 4887, Decimal("4381.2500"), 4889, 4888, Decimal("4380.1750"), "A"),
        (4892, 4891, Decimal("4383.0800"), 4901, 4898, Decimal("4380.6300"), "B"),
        (4918, 4918, Decimal("4384.9450"), 4929, 4922, Decimal("4382.9250"), "A"),
        (4930, 4929, Decimal("4385.1050"), 4932, 4930, Decimal("4384.1700"), "B"),
        (4952, 4951, Decimal("4382.0000"), 4954, 4953, Decimal("4381.2500"), "A"),
        (4955, 4955, Decimal("4382.5050"), 4956, 4955, Decimal("4381.9300"), "B"),
        (4960, 4960, Decimal("4384.8550"), 4961, 4961, Decimal("4384.5750"), "B"),
        (4964, 4963, Decimal("4384.2950"), 4965, 4964, Decimal("4383.4900"), "A"),
        (4975, 4974, Decimal("4384.0100"), 4976, 4975, Decimal("4383.2900"), "A"),
        (4980, 4980, Decimal("4383.9850"), 4981, 4980, Decimal("4383.1750"), "A"),
        (4993, 4993, Decimal("4382.7350"), 4994, 4993, Decimal("4382.1750"), "A"),
        (5001, 5000, Decimal("4383.7800"), 5005, 5003, Decimal("4381.8850"), "A"),
        (5042, 5041, Decimal("4377.2500"), 5045, 5043, Decimal("4376.0200"), "A"),
        (5046, 5046, Decimal("4378.0550"), 5049, 5047, Decimal("4376.7150"), "B"),
    )
    actual_bullish = tuple(
        (
            reaction.first_idx,
            reaction.box_top_source_idx,
            reaction.box_top,
            reaction.break_idx,
            reaction.box_bottom_source_idx,
            reaction.box_bottom,
            reaction.mode,
        )
        for reaction in bullish_result.reactions
    )
    assert actual_bullish == expected_bullish, actual_bullish

    leg_floor_start, leg_floor_end = module.select_range(
        candles,
        datetime(2026, 8, 10, 17, 29, 0),
        datetime(2026, 8, 11, 6, 13, 0),
    )
    leg_floor_reactions = module.UnifiedReactionDetector(
        candles, seconds, leg_floor_start, leg_floor_end, "bullish"
    ).detect().reactions
    assert (
        leg_floor_reactions[0].first_idx,
        leg_floor_reactions[0].box_top_source_idx,
        leg_floor_reactions[0].box_top,
        leg_floor_reactions[0].break_idx,
        leg_floor_reactions[0].box_bottom_source_idx,
        leg_floor_reactions[0].box_bottom,
        leg_floor_reactions[0].mode,
    ) == (1851, 1850, Decimal("4325.6250"), 1859, 1858, Decimal("4321.9200"), "A")
    assert (leg_floor_reactions[1].first_idx, leg_floor_reactions[1].mode) == (
        1860,
        "B",
    )
    # User-confirmed reactions 1..11 remain unchanged by v8.0.15.
    expected_first_eleven = (
        (1851, 1850, Decimal("4325.6250"), 1859, 1858, Decimal("4321.9200"), "A"),
        (1860, 1859, Decimal("4325.7750"), 1861, 1860, Decimal("4324.1950"), "B"),
        (1868, 1868, Decimal("4327.5950"), 1870, 1869, Decimal("4325.3500"), "A"),
        (1875, 1874, Decimal("4331.2250"), 1876, 1875, Decimal("4329.9550"), "B"),
        (1884, 1883, Decimal("4336.5350"), 1891, 1889, Decimal("4332.5250"), "A"),
        (1894, 1894, Decimal("4340.3350"), 1897, 1895, Decimal("4337.1650"), "B"),
        (1901, 1901, Decimal("4347.7150"), 1903, 1902, Decimal("4344.9250"), "B"),
        (1904, 1903, Decimal("4348.2300"), 1908, 1905, Decimal("4345.5600"), "B"),
        (1910, 1909, Decimal("4349.9800"), 1911, 1911, Decimal("4348.1950"), "B"),
        (1922, 1922, Decimal("4349.0300"), 1929, 1925, Decimal("4345.3000"), "A"),
        (1932, 1931, Decimal("4350.1450"), 1937, 1935, Decimal("4347.9600"), "B"),
    )
    actual_first_eleven = tuple(
        (
            reaction.first_idx,
            reaction.box_top_source_idx,
            reaction.box_top,
            reaction.break_idx,
            reaction.box_bottom_source_idx,
            reaction.box_bottom,
            reaction.mode,
        )
        for reaction in leg_floor_reactions[:11]
    )
    assert actual_first_eleven == expected_first_eleven, actual_first_eleven

    # New normative example: after Reaction 11 Reset, Bearish patterns at
    # 18:18:30 and 18:22:00 are irrelevant. The first healthy Bullish reaction
    # is 18:25:00 and the next Normal Search begins at 18:26:30.
    reaction_12 = leg_floor_reactions[11]
    reaction_13 = leg_floor_reactions[12]
    assert (
        reaction_12.first_idx,
        reaction_12.box_top_source_idx,
        reaction_12.box_top,
        reaction_12.break_idx,
        reaction_12.box_bottom_source_idx,
        reaction_12.box_bottom,
        reaction_12.mode,
    ) == (1956, 1955, Decimal("4344.1350"), 1958, 1956, Decimal("4342.9200"), "A")
    assert (
        reaction_13.first_idx,
        reaction_13.box_top_source_idx,
        reaction_13.box_top,
        reaction_13.break_idx,
        reaction_13.box_bottom_source_idx,
        reaction_13.box_bottom,
        reaction_13.mode,
    ) == (1959, 1959, Decimal("4345.7450"), 1966, 1960, Decimal("4343.2800"), "B")

    # After Reaction 20 Reset at 18:59:30, the direct FirstRed 19:00:00
    # confirms at 19:00:30 before the later Anchor-based 19:01:00 candidate.
    reaction_20 = leg_floor_reactions[19]
    reaction_21 = leg_floor_reactions[20]
    assert (reaction_20.first_idx, reaction_20.break_idx) == (2021, 2022)
    assert (
        reaction_21.first_idx,
        reaction_21.box_top_source_idx,
        reaction_21.box_top,
        reaction_21.break_idx,
        reaction_21.box_bottom_source_idx,
        reaction_21.box_bottom,
        reaction_21.mode,
    ) == (2026, 2026, Decimal("4349.6500"), 2027, 2026, Decimal("4348.7750"), "A")

    # Reaction 22 remains unchanged. Its Reset is RED 19:02:30. The immediate
    # GREEN 19:03:30 -> RED 19:04:00 sequence is ineligible because the RED
    # makes a lower leg floor (4348.0250 < 4349.1200). It must not be emitted;
    # the next chronological eligible owner is FirstRed 19:07:00.
    reaction_22 = leg_floor_reactions[21]
    reaction_23 = leg_floor_reactions[22]
    assert (reaction_22.first_idx, reaction_22.break_idx) == (2028, 2030)
    assert all(reaction.first_idx != 2034 for reaction in leg_floor_reactions)
    assert (
        reaction_23.first_idx,
        reaction_23.break_idx,
        reaction_23.mode,
    ) == (2040, 2062, "A")

    # Reaction 30: BoxTop source precedes FirstRed. Exclude the source
    # candle's Low, then include every candle through Breakout. The earliest
    # minimum is GREEN 20:02:30, not FirstRed 20:03:00.
    reaction_30 = next(
        reaction for reaction in leg_floor_reactions
        if reaction.first_idx == 2152
    )
    assert (
        reaction_30.first_idx,
        reaction_30.box_top_source_idx,
        reaction_30.break_idx,
        reaction_30.box_bottom_source_idx,
        reaction_30.box_bottom,
    ) == (2152, 2150, 2156, 2151, Decimal("4352.6850"))

    # v8.0.24 chronological same-candle contract: 22:50:09 first breaks
    # BoxTop, so FirstRed 22:49:30 is a healthy reaction. The later strict Low
    # at 22:50:17 is its Reset; the candle remainder cannot seed a successor.
    same_candle_reaction = next(
        reaction for reaction in leg_floor_reactions
        if reaction.first_idx == 2485
    )
    assert (
        same_candle_reaction.break_idx,
        same_candle_reaction.box_bottom,
        same_candle_reaction.mode,
    ) == (2486, Decimal("4382.8450"), "A")
    same_candle_reset = next(
        reset for reset in module.UnifiedReactionDetector(
            candles, seconds, leg_floor_start, leg_floor_end, "bullish"
        ).detect().resets
        if reset.from_first_idx == 2485
    )
    assert (
        same_candle_reset.index,
        same_candle_reset.second_time,
        same_candle_reset.broken_level,
    ) == (2486, "2026-08-10 22:50:17", Decimal("4382.8450"))
    reaction_after_2250 = next(
        reaction for reaction in leg_floor_reactions
        if reaction.first_idx == 2491
    )
    assert reaction_after_2250.mode == "A"

    # The same rule restores FirstRed 22:28:00. At 22:29:30 the candle first
    # confirms above 4379.1750 and only at 22:29:37 Resets below 4378.6050.
    same_candle_start, same_candle_end = module.select_range(
        candles,
        datetime(2026, 8, 10, 2, 7, 0),
        datetime(2026, 8, 10, 22, 32, 0),
    )
    same_candle_bullish = module.UnifiedReactionDetector(
        candles, seconds, same_candle_start, same_candle_end, "bullish"
    ).detect()
    restored_2228 = next(
        reaction for reaction in same_candle_bullish.reactions
        if reaction.first_idx == 2442
    )
    assert (
        restored_2228.break_idx,
        restored_2228.box_top,
        restored_2228.box_bottom,
    ) == (2445, Decimal("4379.1750"), Decimal("4378.6050"))
    restored_2228_reset = next(
        reset for reset in same_candle_bullish.resets
        if reset.from_first_idx == 2442
    )
    assert (
        restored_2228_reset.index,
        restored_2228_reset.second_time,
    ) == (2445, "2026-08-10 22:29:37")

    # User-confirmed v8.0.24 example: Reaction 6 Resets at 02:02:30. The next
    # Leg-Start is FirstRed 02:03:30. In 02:04:00, 02:04:00 breaks BoxTop
    # 4393.5300, then 02:04:16 strictly crosses BoxBottom 4393.2700. Emit the
    # reaction first and its same-candle Reset second.
    case_start, case_end = module.select_range(
        candles,
        datetime(2026, 8, 11, 1, 33, 30),
        datetime(2026, 8, 11, 2, 6, 0),
    )
    case_result = module.UnifiedReactionDetector(
        candles, seconds, case_start, case_end, "bullish"
    ).detect()
    restored_0203 = next(
        reaction for reaction in case_result.reactions
        if reaction.first_time == "2026-08-11 02:03:30"
    )
    assert (
        restored_0203.break_time,
        restored_0203.box_top,
        restored_0203.box_bottom,
        restored_0203.mode,
    ) == (
        "2026-08-11 02:04:00",
        Decimal("4393.5300"),
        Decimal("4393.2700"),
        "A",
    )
    restored_0203_reset = next(
        reset for reset in case_result.resets
        if reset.from_first_idx == restored_0203.first_idx
    )
    assert (
        restored_0203_reset.display_time,
        restored_0203_reset.second_time,
        restored_0203_reset.broken_level,
    ) == (
        "2026-08-11 02:04:00",
        "2026-08-11 02:04:16",
        Decimal("4393.2700"),
    )

    # Post-Reset search evaluates every eligible local candidate and selects
    # the one with the earliest strict Breakout, not the earliest start that
    # remains unresolved. These are the user-confirmed missing reactions.
    post_reset_range = module.UnifiedReactionDetector(
        candles, seconds, case_start,
        module.select_range(
            candles,
            datetime(2026, 8, 11, 1, 33, 30),
            datetime(2026, 8, 11, 6, 35, 0),
        )[1],
        "bullish",
    ).detect()
    restored_0456 = next(
        reaction for reaction in post_reset_range.reactions
        if reaction.first_time == "2026-08-11 04:56:00"
    )
    assert (
        restored_0456.break_time,
        restored_0456.box_top,
        restored_0456.box_bottom,
        restored_0456.mode,
    ) == (
        "2026-08-11 04:56:30",
        Decimal("4415.7550"),
        Decimal("4413.7300"),
        "A",
    )
    # The earlier valid owner at 05:35:00 must not be skipped in favour of
    # the nested/later 05:56:00 candidate.
    corrected_0535 = next(
        reaction for reaction in post_reset_range.reactions
        if reaction.first_time == "2026-08-11 05:35:00"
    )
    assert (corrected_0535.break_time, corrected_0535.mode) == (
        "2026-08-11 05:36:00", "A"
    )
    assert all(
        reaction.first_time != "2026-08-11 05:56:00"
        for reaction in post_reset_range.reactions
    )
    assert all(
        reaction.first_time != "2026-08-11 06:23:00"
        for reaction in post_reset_range.reactions
    )
    corrected_0627 = next(
        reaction for reaction in post_reset_range.reactions
        if reaction.first_time == "2026-08-11 06:27:00"
    )
    assert (corrected_0627.break_time, corrected_0627.mode) == (
        "2026-08-11 06:30:30", "A"
    )

    nested_start, nested_end = module.select_range(
        candles, datetime(2026, 8, 11, 1, 33, 30),
        datetime(2026, 8, 11, 11, 16, 0),
    )
    nested_result = module.UnifiedReactionDetector(
        candles, seconds, nested_start, nested_end, "bullish"
    ).detect()
    corrected_1111 = next(
        reaction for reaction in nested_result.reactions
        if reaction.first_time == "2026-08-11 11:11:30"
    )
    assert corrected_1111.break_time == "2026-08-11 11:15:00"
    assert all(
        reaction.first_time != "2026-08-11 11:13:00"
        for reaction in nested_result.reactions
    )

    # Exact Bearish mirror: Breakdown occurs first inside the confirmation
    # candle, then a later strict High crosses the confirmed BoxTop. Emit the
    # Bearish reaction and its same-candle Reset in that order.
    mirror_time = datetime(2026, 1, 2, 0, 0, 0)
    mirror_main_facts = (
        ("RED", "102", "90", "101", "91"),
        ("GREEN", "101", "94", "95", "100"),
        ("GREEN", "103", "89", "95", "96"),
    )
    mirror_main = [
        module.Candle(
            index=i,
            timestamp=mirror_time + timedelta(seconds=30 * i),
            display_time=(mirror_time + timedelta(seconds=30 * i)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            tag=tag,
            open=Decimal(open_price),
            high=Decimal(high),
            low=Decimal(low),
            close=Decimal(close),
        )
        for i, (tag, high, low, open_price, close) in enumerate(mirror_main_facts)
    ]
    mirror_second_facts = (
        (0, "RED", "102", "90"),
        (30, "GREEN", "101", "94"),
        (60, "RED", "100", "89"),
        (61, "GREEN", "103", "95"),
    )
    mirror_seconds = [
        module.Candle(
            index=i,
            timestamp=mirror_time + timedelta(seconds=offset),
            display_time=(mirror_time + timedelta(seconds=offset)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            tag=tag,
            open=Decimal(low if tag == "GREEN" else high),
            high=Decimal(high),
            low=Decimal(low),
            close=Decimal(high if tag == "GREEN" else low),
        )
        for i, (offset, tag, high, low) in enumerate(mirror_second_facts)
    ]
    mirror_same_candle = module.UnifiedReactionDetector(
        mirror_main, mirror_seconds, 0, 2, "bearish"
    ).detect()
    assert len(mirror_same_candle.reactions) == 1, (
        mirror_same_candle.reactions,
        mirror_same_candle.resets,
    )
    assert (
        mirror_same_candle.reactions[0].first_idx,
        mirror_same_candle.reactions[0].break_idx,
        mirror_same_candle.reactions[0].box_top,
        mirror_same_candle.reactions[0].box_bottom,
    ) == (1, 2, Decimal("101"), Decimal("90"))
    assert len(mirror_same_candle.resets) == 1
    assert (
        mirror_same_candle.resets[0].index,
        mirror_same_candle.resets[0].second_time,
        mirror_same_candle.resets[0].broken_level,
    ) == (2, "2026-01-02 00:01:01", Decimal("101"))

    # After the later Reset, rejected early post-Reset pairs do not terminate
    # search. FirstRed 23:27:00 confirms at RED 23:27:30; that RED confirmation
    # stays above 4388.1050 and immediately seeds the next Normal reaction,
    # which confirms at 23:28:00.
    starts_2327 = [
        reaction for reaction in leg_floor_reactions
        if reaction.first_idx in (2560, 2561)
    ]
    assert [
        (
            reaction.first_idx,
            reaction.break_idx,
            reaction.box_bottom,
            reaction.mode,
        )
        for reaction in starts_2327
    ] == [
        (2560, 2561, Decimal("4388.1050"), "A"),
        (2561, 2562, Decimal("4388.1200"), "B"),
    ]

    # Exact Bearish mirror: a higher internal GREEN below the unanchored
    # LegCeiling updates BoxTop and cannot erase FirstGreen before Breakdown.
    mirror_base = datetime(2026, 1, 1, 0, 0, 0)
    mirror_rows = (
        ("RED", "10", "8.8", "9.5"),
        ("RED", "9", "8", "8.4"),
        ("GREEN", "8.5", "8.2", "8.4"),
        ("GREEN", "9.5", "8.1", "9.2"),
        ("RED", "9.1", "7.5", "7.7"),
    )
    mirror_candles = [
        module.Candle(
            index=index,
            timestamp=mirror_base + timedelta(seconds=30 * index),
            display_time=(mirror_base + timedelta(seconds=30 * index)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            tag=row[0],
            open=Decimal(row[3]),
            high=Decimal(row[1]),
            low=Decimal(row[2]),
            close=Decimal(row[3]),
        )
        for index, row in enumerate(mirror_rows)
    ]
    mirror_result = module.BearishDetector(
        mirror_candles, mirror_candles, 0, len(mirror_candles) - 1
    ).detect()
    assert len(mirror_result.reactions) == 1
    mirror_reaction = mirror_result.reactions[0]
    assert (
        mirror_reaction.first_idx,
        mirror_reaction.box_top,
        mirror_reaction.box_top_source_idx,
        mirror_reaction.break_idx,
    ) == (2, Decimal("9.5"), 3, 4)

    # Exact mirror is exercised on the maintained real Bearish range: every
    # reaction immediately following a recorded Bearish Reset must be Mode A;
    # no Bullish owner/Reset is consulted by the directional loop.
    bearish_start, bearish_end = module.select_range(
        candles,
        datetime(2026, 8, 10, 2, 56, 30),
        datetime(2026, 8, 10, 7, 38, 0),
    )
    bearish_directional = module.UnifiedReactionDetector(
        candles, seconds, bearish_start, bearish_end, "bearish"
    ).detect()
    reference = module.UnifiedReactionDetector(
        reference_mirror_candles(module, candles),
        reference_mirror_candles(module, seconds),
        bearish_start, bearish_end, "bullish",
    ).detect()
    # Bearish snapshots follow the user-approved Bullish reference, including
    # reset metadata; old independent Bearish totals are no longer authority.
    assert asdict(bearish_directional) == reflected_result(reference)
    assert bearish_directional.reactions[-1].first_idx == 661
    assert bearish_directional.reactions[-1].mode == "B"

    # Bearish Reaction 50: Reset candle 09:14:00 defines the structural
    # ceiling only. It cannot become BoxTop. Track BoxTop from the RED context
    # through Breakdown, yielding 4378.3550 at 09:18:00.
    review_start, review_end = module.select_range(
        candles,
        datetime(2026, 8, 11, 5, 23, 0),
        datetime(2026, 8, 11, 11, 53, 0),
    )
    reviewed_bearish = module.UnifiedReactionDetector(
        candles, seconds, review_start, review_end, "bearish"
    ).detect().reactions
    reaction_50 = next(
        reaction for reaction in reviewed_bearish
        if reaction.first_idx == 3618
    )
    assert (
        reaction_50.first_idx,
        reaction_50.box_bottom_source_idx,
        reaction_50.box_bottom,
        reaction_50.break_idx,
        reaction_50.box_top_source_idx,
        reaction_50.box_top,
        reaction_50.mode,
    ) == (3618, 3618, Decimal("4372.3850"), 3624, 3621, Decimal("4378.3550"), "A")

    # After the later Reset, Bullish FirstRed 14:16:30 confirms at 14:17:00.
    # Its RED confirmation candle is the immediate Anchor for the Bearish
    # FirstGreen 14:17:30. Earlier Bullish detail cannot leak into this box.
    extended_review_end = module.select_range(
        candles,
        datetime(2026, 8, 11, 5, 23, 0),
        datetime(2026, 8, 11, 14, 30, 0),
    )[1]
    extended_bearish = module.UnifiedReactionDetector(
        candles, seconds, review_start, extended_review_end, "bearish"
    ).detect().reactions
    corrected_1417 = next(
        reaction for reaction in extended_bearish if reaction.first_idx == 4220
    )
    assert (
        corrected_1417.box_bottom_source_idx,
        corrected_1417.box_bottom,
        corrected_1417.break_idx,
        corrected_1417.box_top_source_idx,
        corrected_1417.box_top,
        corrected_1417.mode,
    ) == (4218, Decimal("4379.1100"), 4223, 4219, Decimal("4380.4050"), "A")

    try:
        module.select_range(candles, START + timedelta(seconds=1), END)
    except ValueError as exc:
        assert "FROM does not exist" in str(exc)
    else:
        raise AssertionError("A missing FROM candle must be rejected")

    try:
        module.select_range(candles, START, END + timedelta(seconds=1))
    except ValueError as exc:
        assert "TO does not exist" in str(exc)
    else:
        raise AssertionError("A missing TO candle must be rejected")

    try:
        module.select_range(candles, END, START)
    except ValueError as exc:
        assert "TO must be later" in str(exc)
    else:
        raise AssertionError("TO earlier than FROM must be rejected")

    future_now = datetime(2026, 8, 11, 18, 0, 0)
    try:
        module.select_range(candles, START, END, now=future_now)
    except ValueError as exc:
        assert "current system time" in str(exc)
    else:
        raise AssertionError("TO later than current system time must be rejected")

    prompted_values = iter((START + timedelta(seconds=1), END, START, END))
    original_prompt_datetime = module.prompt_datetime
    module.prompt_datetime = lambda *_args, **_kwargs: next(prompted_values)
    try:
        chosen_from, chosen_to, chosen_start, chosen_end = (
            module.choose_range_interactively(candles, START, END)
        )
    finally:
        module.prompt_datetime = original_prompt_datetime
    assert (chosen_from, chosen_to, chosen_start, chosen_end) == (
        START,
        END,
        4572,
        4885,
    )

    print(
        "PASS: unified v9 chronological candidate ownership, refine-or-Reset contract, immediate opposite-"
        "Anchor handoff, corrected Bearish 09:18 and 14:17 boxes, exact "
        "mirrors, same-candle Reset seed exclusion, and range validation."
    )
