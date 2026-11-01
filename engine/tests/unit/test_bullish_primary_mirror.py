"""Approved bullish primary rules and exact directional reflection."""
from dataclasses import replace
from decimal import Decimal
from types import SimpleNamespace as NS

from test_pl_ph_detector import fixture, initial, order
from reaction_engine import MarketChronology
import PL_PH_detector as primary
import pytest


def mirror_values(values):
    original, s_zones, e_zones, stopalls = values
    rows = [NS(**{**vars(row), "open": -row.open, "high": -row.low,
                  "low": -row.high, "close": -row.close}) for row in original.candles]
    return MarketChronology(rows, rows, 30), s_zones, e_zones, stopalls


def run_bullish(values, choices):
    chronology = values[0]
    def resolve(kind, number, index, event):
        return [order(chronology, index, *args) for args in choices.get((kind, index), [])]
    return primary.detect_bullish(*values, resolve)


def test_bullish_stopall_low_break_selects_minimum_pl_and_fixed_maximum_mbl():
    values = mirror_values(fixture(initial()))
    result = run_bullish(values, {("PL", 8): [(10,)]})
    assert result.direction == "bullish"
    assert [(p.kind, p.number, p.source_index, p.decision_index, p.price)
            for p in result.lows] == [("PL", 1, 9, 10, Decimal("-110"))]
    assert (result.mbl.source_index, result.mbl.price) == (7, Decimal("-80"))
    assert len(list(primary.formed_matching_legs(result, through_index=10))) == 1
    assert list(primary.formed_matching_legs(result, through_index=9)) == []


def test_bullish_reference_equality_does_not_activate_a_cycle():
    values = mirror_values(fixture({8: ("100", "80")}))
    assert run_bullish(values, {}).mbl is None


def test_bullish_secondary_ph_uses_its_own_break_to_order_stop_maximum():
    values = mirror_values(fixture(initial({12: ("100", "79"), 13: ("99", "70")})))
    result = run_bullish(values, {("PL", 8): [(10,)], ("PH", 12): [(15,)]})
    assert [(p.kind, p.number, p.source_index, p.price) for p in result.highs] == [
        ("PH", 1, 13, Decimal("-70"))]


def test_bullish_third_pl_stop_reverses_all_cycles_without_pl4():
    values = mirror_values(fixture(initial({12: ("111", "90"), 13: ("120", "90"),
        16: ("121", "90"), 17: ("130", "90"), 20: ("131", "90")})))
    result = run_bullish(values, {("PL", 8): [(10,)], ("PL", 12): [(14,)],
                                ("PL", 16): [(18,)], ("PL", 20): [(22,)]})
    assert [point.number for point in result.lows] == [1, 2, 3]
    assert result.transition.index == 20
    assert result.transition.level == Decimal("-130")
    assert result.transition.target_direction == "bearish"
    assert result.transition.high.kind == "PL"
    assert result.status == "reversed-to-bearish"


def test_bullish_equal_pl3_low_does_not_reverse():
    values = mirror_values(fixture(initial({12: ("111", "90"), 13: ("120", "90"),
        16: ("121", "90"), 17: ("130", "90"), 20: ("130", "90")})))
    result = run_bullish(values, {("PL", 8): [(10,)], ("PL", 12): [(14,)], ("PL", 16): [(18,)]})
    assert result.transition is None


def test_lower_physical_pl_continues_final_number_after_local_reset():
    from test_primary_high_numbering import high
    lows = [replace(high(2, 5, 8, "110", "first"), kind="PL", price=Decimal("-110")),
            replace(high(1, 9, 12, "120", "second"), kind="PL", price=Decimal("-120"))]
    result = NS(lows=lows, cycles=[])
    assert [p.number for p in primary.resolve_primary_lows(result, through_index=12)] == [2, 3]
    assert [p.number for p in primary.resolve_primary_lows(result, through_index=10)] == [2]


def test_bullish_mirror_retains_real_order_prices_and_physical_provenance():
    values = mirror_values(fixture(initial()))
    native = replace(order(values[0], 8, 10, direction="bearish"),
                     stop_level=Decimal("-77"), box_top=Decimal("-70"),
                     box_bottom=Decimal("-100"),
                     audit_causes=({"kind": "parent-stop", "parent": "S", "price": "-77"},))
    result = primary.detect_bullish(*values, lambda *args: [native])
    actual = result.lows[0].order
    assert actual == native
    assert native.audit_causes[0]["price"] == "-77"


def test_bullish_stopall_ownership_is_promoted_only_by_confirmed_primary_pl():
    values = mirror_values(fixture(initial()))
    result = run_bullish(values, {("PL", 8): [(10,)]})
    source = result.lows[0]
    stop = NS(source_index=source.source_index, source_time=source.source_time)
    assert primary.resolve_stopall_ownership([stop], result, through_index=9) == [stop]
    assert primary.resolve_stopall_ownership([stop], result, through_index=10) == []


def test_bullish_primary_native_gate_admits_older_first_and_joint_confirmation():
    from test_order_audit_lifecycle_contracts import detector_state, moment
    from test_pl_ph_detector import accepted_order
    service, _, physical = detector_state("bullish")
    resolver = primary.NativePrimaryOrders(service.chronology,
        {"bullish": {"OrderAudit": [accepted_order(service, physical)]}}, direction="bullish")
    assert len(resolver("PL", 1, 6, moment(190))) == 1
    assert resolver("PL", 1, 6, moment(191)) == []


def test_bullish_secondary_ph_keeps_strict_first_gate_and_first_direct_a_lock():
    from test_order_audit_lifecycle_contracts import detector_state, moment
    from test_pl_ph_detector import accepted_order
    service, _, physical = detector_state("bearish")
    first = accepted_order(service, physical)
    resolver = primary.NativePrimaryOrders(service.chronology,
        {"bearish": {"OrderAudit": [first]}}, direction="bullish")
    assert resolver("PH", 1, 6, moment(190)) == []
    first["crossed"] = None
    later = accepted_order(service, replace(physical, first_idx=6))
    resolver.groups["bearish"]["OrderAudit"].append(later)
    assert resolver("PH", 1, 4, moment(125)) == []


def test_bullish_pl2_rejects_only_b_while_reset_pl1_accepts_it():
    from test_order_audit_lifecycle_contracts import detector_state, moment
    from test_pl_ph_detector import accepted_order
    service, _, physical = detector_state("bullish")
    resolver = primary.NativePrimaryOrders(service.chronology,
        {"bullish": {"OrderAudit": [accepted_order(service, physical, "reset-leg")]}},
        direction="bullish")
    assert resolver("PL", 2, 4, moment(125)) == []
    assert resolver("PL", 1, 4, moment(125))[0].causes == ("reset-leg",)


@pytest.mark.parametrize("changes,choices", [
    (initial({6: ("99", "80"), 10: ("110", "90")}), {("PH", 8): [(11,)]}),
    (initial({12: ("99", "79"), 13: ("99", "70")}),
        {("PH", 8): [(10,)], ("PL", 12): [(15, "reset-leg")]}),
    (initial({12: ("111", "90"), 14: ("111", "79"), 15: ("99", "60")}),
        {("PH", 8): [(10,)], ("PH", 12): [(16,)], ("PL", 14): [(17, "reset-leg")]}),
    (initial({12: ("99", "79"), 13: ("99", "70"), 16: ("111", "90"),
              17: ("115", "90"), 20: ("99", "69"), 21: ("99", "60")}),
        {("PH", 8): [(10,)], ("PL", 12): [(14,)],
         ("PH", 16): [(18,)], ("PL", 20): [(22,)]}),
])
def test_primary_mirror_preserves_decisions_cancellations_and_source_ownership(changes, choices):
    from test_pl_ph_detector import run
    values = fixture(changes)
    bearish = run(values, choices)
    mirrored_choices = {("PL" if kind == "PH" else "PH", gate): rows
                        for (kind, gate), rows in choices.items()}
    bullish = run_bullish(mirror_values(values), mirrored_choices)
    for original, mirrored in ((bearish.highs, bullish.lows), (bearish.lows, bullish.highs)):
        assert [(p.number, p.source_index, p.trigger_index, p.decision_index, p.price)
                for p in original] == [
            (p.number, p.source_index, p.trigger_index, p.decision_index, p.price.copy_negate())
            for p in mirrored]
    assert bearish.mbl.source_index == bullish.mbl.source_index
    assert bearish.mbl.price == bullish.mbl.price.copy_negate()


def test_reflection_preserves_long_decimal_lexemes_under_a_small_context():
    from decimal import localcontext
    values = mirror_values(fixture(initial()))
    exact = Decimal("-110.123456789012345678901234567890")
    values[0].candles[9].low = exact
    # Rebuild the authoritative original index after the fixture change.
    values = (MarketChronology(values[0].candles, values[0].candles, 30), *values[1:])
    with localcontext() as context:
        context.prec = 8
        result = run_bullish(values, {("PL", 8): [(10,)]})
    assert result.lows[0].price == exact
