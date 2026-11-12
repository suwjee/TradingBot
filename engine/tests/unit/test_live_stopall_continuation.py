import pytest

from test_stopall_dominance import chronology, e, moment, s
import lifecycle_engine as engine
from reaction_engine import MarketChronology


def prefix(direction, end, stop_seconds=()):
    full = chronology(direction, stop_seconds)
    return MarketChronology(
        [row for row in full.candles if row.timestamp <= moment(end)],
        [row for row in full.seconds if row.timestamp <= moment(end)],
        30,
    )


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_live_stopall_keeps_armed_owner_and_reuses_the_prior_donor(direction, monkeypatch):
    source = [e(0, 10), e(30, 40), e(120, 130, number=2)]
    session = engine.LiveStopAllContinuation(direction, [], source, prefix(direction, 145, (90,)))
    first, = session.result
    assert first.stop_event_time is None
    longer = [*source, e(210, 220, number=3)]
    market = prefix(direction, 245, (90, 165))
    expected = engine.detect_stopalls(direction, [], longer, market)

    def track(detector, item, *args):
        assert item.source_time > source[-1].source_time
        return constructor(detector, item, *args)

    constructor = engine.StopAllDetector._stopall_from_e
    monkeypatch.setattr(engine.StopAllDetector, "_stopall_from_e", track)
    actual = session.update([], longer, market, first_dirty_main=5)
    assert actual == expected
    assert [(item.number, item.stop_event_time) for item in actual] == [(1, moment(165)), (2, None)]


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
def test_live_stopall_rewinds_a_market_or_upstream_revision(direction):
    s_items = [s(0, 10), s(30, 40)]
    donors = [e(120, 130), e(210, 220, number=2)]
    seed = prefix(direction, 240, (90, 165))
    session = engine.LiveStopAllContinuation(direction, s_items, donors, seed)
    assert len(session.result) == 2

    market = prefix(direction, 270, (165,))
    revised = [*s_items, s(115, 130, "red")]
    expected = engine.detect_stopalls(direction, revised, donors, market)
    actual = session.update(revised, donors, market, first_dirty_main=3)
    assert actual == expected
    assert actual != engine.detect_stopalls(direction, s_items, donors, market)
    assert actual[0].gate_type == "opposite-s-group-stop"
