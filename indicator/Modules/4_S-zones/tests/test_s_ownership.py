"""Mirrored S source chronology and stopped-A ownership contracts."""

from datetime import datetime, timedelta
from decimal import Decimal
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


PATH = Path(__file__).resolve().parents[1] / "app" / "s_detector.py"
SPEC = importlib.util.spec_from_file_location("s_ownership_tests", PATH)
S = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = S
SPEC.loader.exec_module(S)
BASE = datetime(2026, 1, 1)


def candle(index, high, low, *, second=None, direction="bearish"):
    high, low = Decimal(str(high)), Decimal(str(low))
    if direction == "bullish":
        high, low = Decimal(30) - low, Decimal(30) - high
    return SimpleNamespace(
        index=index, timestamp=BASE + timedelta(seconds=index * 30 if second is None else second),
        high=high, low=low,
    )


@pytest.mark.parametrize("direction", ["bearish", "bullish"])
@pytest.mark.parametrize("peak_after", [True, False])
def test_order_confirmation_candle_uses_only_eligible_remainder(direction, peak_after):
    main = [candle(i, h, l, direction=direction) for i, (h, l) in enumerate(
        [(18, 8), (13, 9), (12, 10)]
    )]
    lower = [
        candle(0, 14 if peak_after else 18, 9, second=5, direction=direction),
        candle(1, 18 if peak_after else 14, 9, second=15, direction=direction),
        candle(2, 13, 9, second=30, direction=direction),
    ]
    reaction = SimpleNamespace(
        first_idx=2, anchor_idx=0,
        anchor_value=Decimal(18) if direction == "bearish" else Decimal(12),
    )
    detector = S.SDetector(direction, [], [], [], [], main, lower, 30)
    index, source, price = detector._candidate_after_order(BASE + timedelta(seconds=10), reaction)
    expected = Decimal(18 if peak_after else 14)
    if direction == "bullish":
        expected = Decimal(30) - expected
    assert (index, source, price) == (0, BASE, expected)


@pytest.mark.parametrize("direction", ["bearish", "bullish"])
def test_partial_main_candle_without_lower_data_does_not_import_early_extreme(direction):
    main = [candle(i, h, 8, direction=direction) for i, h in enumerate([18, 13, 12])]
    detector = S.SDetector(direction, [], [], [], [], main, [], 30)
    reaction = SimpleNamespace(first_idx=2, anchor_idx=0, anchor_value=Decimal(18))
    index, _, price = detector._candidate_after_order(BASE + timedelta(seconds=10), reaction)
    assert index == 1
    assert price == (Decimal(13) if direction == "bearish" else Decimal(17))


@pytest.mark.parametrize("direction", ["bearish", "bullish"])
def test_unresolved_stopped_a_reserves_s_lifecycle_without_an_order(direction):
    main = [candle(i, h, l, direction=direction) for i, (h, l) in enumerate(
        [(10, 8), (9, 7), (11, 8), (12, 8), (11, 7), (10, 6)]
    )]
    lower = [
        candle(0, 10, 8, second=0, direction=direction),
        candle(1, 9, 7, second=35, direction=direction),
        candle(2, 11, 8, second=70, direction=direction),
        candle(3, 12, 8, second=95, direction=direction),
        candle(4, 10, 6, second=155, direction=direction),
    ]
    reactions = [
        SimpleNamespace(break_idx=1, box_bottom=Decimal(8), box_top=Decimal(22)),
        SimpleNamespace(break_idx=5, box_bottom=Decimal(7), box_top=Decimal(23)),
    ]
    zones = [SimpleNamespace(
        source_index=i, source_time=main[i].timestamp,
        price=main[i].high if direction == "bearish" else main[i].low,
        reaction_number=n + 1, reaction_break_time=main[reactions[n].break_idx].timestamp,
    ) for n, i in enumerate([0, 3])]
    detector = S.SDetector(direction, reactions, [], [], zones, main, lower, 30)
    assert detector.detect() == []  # No order means no invented S.
    assert detector.eligible_a_zones == [zones[0]]
    assert detector.a_ownership_windows == [(BASE + timedelta(seconds=70), None)]
    assert detector.order_audit == {}
    assert detector.detect() == []  # Reusing a detector must not retain stale windows.
    assert detector.eligible_a_zones == [zones[0]]


@pytest.mark.parametrize("direction", ["bearish", "bullish"])
def test_ownership_includes_stop_second_and_releases_after_s_source(direction):
    main = [candle(i, 10 + i, 8, direction=direction) for i in range(5)]
    lower = [candle(i, 10 + i, 8, second=30 * i + 5, direction=direction) for i in range(5)]
    detector = S.SDetector(direction, [], [], [], [], main, lower, 30)
    detector.a_ownership_windows = [(BASE + timedelta(seconds=35), BASE + timedelta(seconds=120))]
    zones = [SimpleNamespace(
        source_time=c.timestamp, price=c.high if direction == "bearish" else c.low
    ) for c in main]
    assert [detector._a_owned_by_s(z) for z in zones] == [False, True, True, True, False]


@pytest.mark.parametrize("direction", ["bearish", "bullish"])
def test_new_a_confirmed_before_parent_stop_can_still_own_a_cycle(direction):
    main = [candle(i, h, l, direction=direction) for i, (h, l) in enumerate(
        [(10, 8), (9, 7), (11, 6), (10, 6)]
    )]
    lower = [
        candle(0, 10, 8, second=0, direction=direction),
        candle(1, 9, 7, second=35, direction=direction),
        candle(2, 9, 6, second=65, direction=direction),
        candle(3, 11, 8, second=70, direction=direction),
    ]
    reactions = [
        SimpleNamespace(break_idx=1, box_bottom=Decimal(8), box_top=Decimal(22)),
        SimpleNamespace(break_idx=2, box_bottom=Decimal(7), box_top=Decimal(23)),
    ]
    zones = [SimpleNamespace(
        source_index=i, source_time=main[i].timestamp,
        price=main[i].high if direction == "bearish" else main[i].low,
        reaction_number=i + 1, reaction_break_time=main[i + 1].timestamp,
    ) for i in range(2)]
    detector = S.SDetector(direction, reactions, [], [], zones, main, lower, 30)
    assert detector.detect() == []
    assert detector.eligible_a_zones == zones
    assert detector.a_ownership_windows == [(BASE + timedelta(seconds=70), None)]


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_simple_candidate_is_inclusive_break_to_break_and_last_wins_ties(direction):
    main = [
        candle(i, high, low, direction=direction)
        for i, (high, low) in enumerate([
            (12, 9), (14, 7), (13, 8), (14, 7), (15, 9),
        ])
    ]
    detector = S.SDetector(direction, [], [], [], [], main, main, 30)
    order = SimpleNamespace(break_idx=1)
    aligned = SimpleNamespace(break_idx=3)
    index, source, _ = detector._simple_candidate(order, aligned)
    assert (index, source) == (3, main[3].timestamp)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_pre_order_candidate_uses_first_tied_extreme_after_exact_a_stop(direction):
    main = [
        candle(i, high, low, direction=direction)
        for i, (high, low) in enumerate([
            (12, 5), (12, 5), (14, 7),
        ])
    ]
    lower = [
        candle(0, 12, 4, second=2, direction=direction),
        candle(1, 12, 5, second=8, direction=direction),
        candle(2, 12, 5, second=35, direction=direction),
    ]
    order = SimpleNamespace(first_idx=1)
    detector = S.SDetector(direction, [], [], [], [], main, lower, 30)
    result = detector._candidate_before_order(
        0, order, a_stop_event_time=BASE + timedelta(seconds=5)
    )
    assert result[:2] == (0, main[0].timestamp)
    assert result[2] == detector._trend_extreme(main[0])
    assert detector._candidate_event_time(
        result[0], result[2], BASE + timedelta(seconds=5)
    ) == BASE + timedelta(seconds=8)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_pre_order_candidate_blue_accepts_valid_reaction_before_order(direction):
    main = [
        candle(i, high, low, direction=direction)
        for i, (high, low) in enumerate([
            (12, 8), (13, 7), (14, 9), (15, 6),
        ])
    ]
    lower = [
        candle(0, 12, 8, second=5, direction=direction),
        candle(1, 13, 7, second=35, direction=direction),
        candle(2, 14, 9, second=65, direction=direction),
        candle(3, 15, 6, second=95, direction=direction),
    ]
    reaction = SimpleNamespace(
        break_idx=2,
        box_top=main[2].high - Decimal(1),
        box_bottom=main[2].low + Decimal(1),
        intrabar_start=None,
    )
    detector = S.SDetector(
        direction, [reaction], [], [], [], main, lower, 30
    )
    candidate_level = main[1].low if direction == "bullish" else main[1].high
    order_stop = Decimal(30) if direction == "bullish" else Decimal(0)
    result = detector._decision(
        candidate_level,
        order_stop,
        BASE + timedelta(seconds=80),
        0,
        BASE + timedelta(seconds=35),
        BASE + timedelta(seconds=35),
    )
    assert result is not None
    assert result[0] == "blue"
    assert result[3] == BASE + timedelta(seconds=95)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_pre_order_order_stop_creates_red_before_candidate_cross(direction):
    main = [
        SimpleNamespace(
            index=index,
            timestamp=BASE + timedelta(seconds=index * 30),
            high=Decimal(40),
            low=Decimal(-10),
        )
        for index in range(4)
    ]
    if direction == "bullish":
        lower = [
            SimpleNamespace(
                timestamp=BASE + timedelta(seconds=85),
                high=Decimal(31),
                low=Decimal(18),
            ),
            SimpleNamespace(
                timestamp=BASE + timedelta(seconds=95),
                high=Decimal(20),
                low=Decimal(16),
            ),
        ]
        candidate_level = Decimal(17)
        order_stop = Decimal(30)
    else:
        lower = [
            SimpleNamespace(
                timestamp=BASE + timedelta(seconds=85),
                high=Decimal(12),
                low=Decimal(-1),
            ),
            SimpleNamespace(
                timestamp=BASE + timedelta(seconds=95),
                high=Decimal(14),
                low=Decimal(5),
            ),
        ]
        candidate_level = Decimal(13)
        order_stop = Decimal(0)
    detector = S.SDetector(
        direction, [], [], [], [], main, lower, 30
    )
    result = detector._decision(
        candidate_level,
        order_stop,
        BASE + timedelta(seconds=80),
        0,
        BASE + timedelta(seconds=35),
        BASE + timedelta(seconds=35),
    )
    assert result is not None
    assert result[0] == "red"
    assert result[3] == BASE + timedelta(seconds=85)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_pre_order_first_candidate_cross_without_reaction_is_rejected(direction):
    main = [
        SimpleNamespace(
            index=index,
            timestamp=BASE + timedelta(seconds=index * 30),
            high=Decimal(40),
            low=Decimal(-10),
        )
        for index in range(5)
    ]
    if direction == "bullish":
        lower = [
            SimpleNamespace(
                timestamp=BASE + timedelta(seconds=85),
                high=Decimal(20),
                low=Decimal(16),
            ),
            SimpleNamespace(
                timestamp=BASE + timedelta(seconds=125),
                high=Decimal(20),
                low=Decimal(15),
            ),
        ]
        candidate_level = Decimal(17)
        order_stop = Decimal(30)
    else:
        lower = [
            SimpleNamespace(
                timestamp=BASE + timedelta(seconds=85),
                high=Decimal(14),
                low=Decimal(5),
            ),
            SimpleNamespace(
                timestamp=BASE + timedelta(seconds=125),
                high=Decimal(15),
                low=Decimal(5),
            ),
        ]
        candidate_level = Decimal(13)
        order_stop = Decimal(0)
    late_reaction = SimpleNamespace(
        break_idx=4,
        box_top=Decimal(19),
        box_bottom=Decimal(6),
        intrabar_start=None,
    )
    detector = S.SDetector(
        direction, [late_reaction], [], [], [], main, lower, 30
    )
    result = detector._decision(
        candidate_level,
        order_stop,
        BASE + timedelta(seconds=80),
        0,
        BASE + timedelta(seconds=35),
        BASE + timedelta(seconds=35),
        fallback_on_unqualified_cross=True,
    )
    assert result is not None
    assert result[0] == "fallback"
    assert result[3] == BASE + timedelta(seconds=85)


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_advanced_reaction_must_be_wholly_inside_order_detail(direction):
    main = [candle(i, 14, 7, direction=direction) for i in range(6)]
    order_top, order_bottom = (
        (Decimal("16"), Decimal("6"))
        if direction == "bullish"
        else (Decimal("24"), Decimal("14"))
    )
    inside = SimpleNamespace(
        first_idx=2, break_idx=3,
        box_top=order_top - Decimal("1"),
        box_bottom=order_bottom + Decimal("1"),
        intrabar_start=None,
    )
    outside = SimpleNamespace(
        first_idx=2, break_idx=3,
        box_top=order_top + Decimal("1"),
        box_bottom=order_bottom + Decimal("1"),
        intrabar_start=None,
    )
    order = SimpleNamespace(
        first_idx=1, break_idx=4,
        box_top=order_top, box_bottom=order_bottom,
    )
    detector = S.SDetector(direction, [outside], [], [], [], main, main, 30)
    confirmation = main[4].timestamp + timedelta(seconds=30)
    assert detector._nested_trend_reaction(order, confirmation) is None
    detector = S.SDetector(direction, [inside], [], [], [], main, main, 30)
    assert detector._nested_trend_reaction(order, confirmation) is not None


@pytest.mark.parametrize("direction", ["bullish", "bearish"])
def test_type3_uses_order_b_break_to_reset_leg_and_exact_mirror(direction):
    main = [
        candle(i, high, low, direction=direction)
        for i, (high, low) in enumerate([
            (13, 9), (15, 7), (14, 8), (15, 7),
            (15, 6), (16, 7), (14, 8),
        ])
    ]
    owner = SimpleNamespace(
        first_idx=0, break_idx=1,
        box_top=main[0].high, box_bottom=main[0].low,
        intrabar_start=None,
    )
    aligned = SimpleNamespace(
        first_idx=3, break_idx=4,
        box_top=main[3].high, box_bottom=main[3].low,
        intrabar_start=None,
    )
    reset = SimpleNamespace(
        from_first_idx=0,
        index=3,
        display_time=main[3].timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        second_time=None,
    )
    detector = S.SDetector(
        direction, [aligned], [owner], [], [], main, main, 30,
        opposite_resets=[reset],
    )
    result = detector._first_type3(
        main[2].timestamp,
        main[6].timestamp + timedelta(seconds=30),
    )
    assert result is not None
    # Equal leg extrema at indices 2 and 3 belong to the last candle.
    assert (result[0], result[1]) == (3, main[3].timestamp)
    assert result[7] == main[5].timestamp
