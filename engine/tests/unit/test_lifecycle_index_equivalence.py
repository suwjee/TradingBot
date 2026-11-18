"""Protect owner identity, inclusive lifetimes and stable selection during indexing."""
from datetime import datetime, timedelta
from pathlib import Path
import random
import sys
from types import SimpleNamespace
from decimal import Decimal

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pipeline"))
from order_audit_engine import dominant_post_behavior_stops, PostBehaviorStop
from lifecycle_engine import s_zones_for_module_engines, module_priority, strictly_beyond_boundary

BASE = datetime(2026, 1, 1)


class Chronology:
    def main_index(self, value, *, clamp=False):
        return max(0, int((value - BASE).total_seconds()) // 30)


def legacy_stops(lifetimes, priority):
    selected = {}
    for kind, behavior, event in lifetimes:
        if event is None:
            continue
        active = [item for _, item, end in lifetimes
                  if (getattr(item, "trigger_event_time", None)
                      or getattr(item, "decision_event_time", None) or item.source_time) <= event
                  and (end is None or event <= end)]
        if not active:
            continue
        owner = max(active, key=lambda item: (priority(item), item.number, item.source_time, item.source_index))
        if owner is not behavior:
            continue
        rank = priority(behavior), behavior.number, behavior.source_time, behavior.source_index, event
        index = Chronology().main_index(event, clamp=True)
        if index not in selected or rank > selected[index][0]:
            selected[index] = rank, PostBehaviorStop(kind, behavior.source_index, behavior.source_time, event)
    return sorted((item[1] for item in selected.values()), key=lambda item: (item.event_time, item.behavior_source_index))


@pytest.mark.parametrize("seed", range(20))
def test_dominance_preserves_inclusive_boundaries_ties_and_duplicate_objects(seed):
    rng = random.Random(seed)
    items = []
    for i in range(55):
        source = BASE + timedelta(seconds=rng.randrange(10) * 5)
        item = SimpleNamespace(source_time=source, source_index=rng.randrange(10),
                               number=rng.randrange(4), priority=rng.randrange(4),
                               trigger_event_time=None, decision_event_time=None)
        if i % 3:
            item.decision_event_time = source + timedelta(seconds=rng.randrange(5))
        if i % 5 == 0:
            item.trigger_event_time = source + timedelta(seconds=rng.randrange(5))
        items.append(item)
    lifetimes = [("S" if i % 2 else "E", item,
                  None if i % 7 == 0 else BASE + timedelta(seconds=rng.randrange(15) * 5))
                 for i, item in enumerate(items)]
    lifetimes.extend([("duplicate", items[0], BASE + timedelta(seconds=50)),
                      ("same-object", items[-1], BASE + timedelta(seconds=75))])
    rng.shuffle(lifetimes)
    priority = lambda item: item.priority
    assert dominant_post_behavior_stops(Chronology(), lifetimes, priority) == legacy_stops(lifetimes, priority)


def test_dominance_ranks_each_lifetime_once_in_dense_history():
    size = 700
    lifetimes = [("S", SimpleNamespace(source_time=BASE, source_index=i, number=i),
                  BASE + timedelta(seconds=60)) for i in range(size)]
    calls = 0
    def priority(item):
        nonlocal calls
        calls += 1
        return 1
    actual = dominant_post_behavior_stops(Chronology(), lifetimes, priority)
    assert actual == [PostBehaviorStop("S", size - 1, BASE, BASE + timedelta(seconds=60))]
    assert calls <= size * 2, "Dense histories must not repeatedly rank all active lifetimes."


def legacy_s_zones(s_zones, e_zones, direction):
    ordered_e = sorted(e_zones, key=lambda item: item.source_time)
    visible = []
    for zone in sorted(s_zones, key=lambda item: item.source_time):
        prior_modules = [item for item in [*ordered_e, *visible] if item.source_time < zone.source_time]
        if prior_modules:
            prior = max(prior_modules, key=lambda item: item.source_time)
            if module_priority(zone) <= module_priority(prior):
                if zone.a_source_time < prior.source_time:
                    continue
                boundary = Decimal(str(prior.price))
                if strictly_beyond_boundary(Decimal(str(zone.a_price)), boundary, direction):
                    continue
                if strictly_beyond_boundary(Decimal(str(zone.price)), boundary, direction):
                    continue
        visible.append(zone)
    return visible


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
@pytest.mark.parametrize("seed", range(20))
def test_s_eligibility_preserves_first_equal_source_and_e_precedence(direction, seed):
    rng = random.Random(seed)
    zones, es = [], []
    for i in range(75):
        source = BASE + timedelta(seconds=rng.randrange(12) * 5)
        price = Decimal(rng.choice(("10.0", "10.00", "9", "11")))
        if i % 3:
            zones.append(SimpleNamespace(source_time=source, price=price, color=rng.choice(("red", "blue")),
                a_source_time=BASE + timedelta(seconds=rng.randrange(12) * 5),
                a_price=Decimal(rng.choice(("10.00", "9", "11")))))
        else:
            es.append(SimpleNamespace(source_time=source, price=price, family=rng.choice(("red", "blue"))))
    actual = s_zones_for_module_engines(zones, es, direction)
    expected = legacy_s_zones(zones, es, direction)
    assert [id(item) for item in actual] == [id(item) for item in expected]


def test_s_eligibility_does_not_rescan_prior_history():
    class Zone:
        reads = 0
        color = "red"
        price = a_price = Decimal("10.00")
        def __init__(self, number):
            self.time = self.a_source_time = BASE + timedelta(seconds=number)
        @property
        def source_time(self):
            Zone.reads += 1
            return self.time
    zones = [Zone(i) for i in range(600)]
    actual = s_zones_for_module_engines(zones, [], "bullish")
    assert all(left is right for left, right in zip(actual, zones)) and len(actual) == len(zones)
    assert Zone.reads < 600 * 100, "S eligibility must not rescan the accepted history for every S."
