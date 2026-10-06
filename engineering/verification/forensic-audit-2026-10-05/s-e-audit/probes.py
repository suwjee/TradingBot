"""Read-only S/E source contract probes; artificial input, never market RAW."""
from __future__ import annotations

import json
import sys
from dataclasses import fields, replace
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

AUDIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AUDIT / "package" / "pipeline"))
from reaction_engine import Candle, Candidate, MarketChronology, mirror_candle, mirror_candidate
from s_zone_detector import SZone, SZoneDetector
from e_zone_detector import EZoneDetector
from lifecycle_engine import sequence_priority
from order_audit_engine import OrderBResetLeg, PostBehaviorStop

BASE = datetime(2000, 1, 1)

def moment(second):
    return BASE + timedelta(seconds=second)

def candle(index, second, low="100", high="120"):
    stamp = moment(second)
    return Candle(index, stamp, stamp.strftime("%Y-%m-%d %H:%M:%S"), "GREEN",
                  Decimal("110"), Decimal(high), Decimal(low), Decimal("111"))

def physical(first, breakout):
    first_text = moment(first * 30).strftime("%Y-%m-%d %H:%M:%S")
    return Candidate(first, first_text, first, first_text, Decimal("120"),
                     first, first_text, Decimal("100"), "A", break_idx=breakout,
                     break_time=moment(breakout * 30).strftime("%Y-%m-%d %H:%M:%S"))

def s_zone(direction, source=60, decision=110, stop=35, formation="type4"):
    vals = {f.name: None for f in fields(SZone)}
    vals.update(direction=direction, color="blue", formation_type=formation,
                a_ordinal=1, a_source_index=0, a_source_time=moment(0),
                a_price=Decimal("110" if direction == "bullish" else "-110"),
                a_stop_index=stop//30, a_stop_time=moment(stop//30*30),
                a_stop_event_time=moment(stop), source_index=source//30,
                source_time=moment(source),
                price=Decimal("100" if direction == "bullish" else "-100"),
                decision_index=decision//30, decision_time=moment(decision//30*30),
                decision_event_time=moment(decision))
    return SZone(**vals)

def chronology(direction, low_events=(), high_events=()):
    lower = [candle(i, i, "99" if i in low_events else "100",
                    "121" if i in high_events else "120") for i in range(360)]
    main = [candle(i, i*30,
                   str(min(c.low for c in lower[i*30:(i+1)*30])),
                   str(max(c.high for c in lower[i*30:(i+1)*30]))) for i in range(12)]
    if direction == "bearish":
        lower = [mirror_candle(c) for c in lower]
        main = [mirror_candle(c) for c in main]
    return MarketChronology(main, lower, 30)

def order_tie(direction):
    market = chronology(direction, {125, 190, 250}, {275})
    first = physical(5, 6)
    second = physical(7, 8)
    if direction == "bearish":
        first, second = mirror_candidate(first), mirror_candidate(second)
    parent = s_zone(direction)
    reset_reaction = physical(1, 2)
    if direction == "bearish":
        reset_reaction = mirror_candidate(reset_reaction)
    leg = OrderBResetLeg(PostBehaviorStop("A", 0, moment(0), moment(35)),
                        "A", 0, moment(0), parent.a_price,
                        reset_reaction, moment(65), 3,
                        Decimal("100" if direction == "bullish" else "-100"),
                        moment(95), Decimal("100" if direction == "bullish" else "-100"),
                        2, moment(60), moment(125), 2, second, moment(250))
    detector = EZoneDetector(direction, [], [first, second], [parent], [], market,
                             sequence_priority=sequence_priority, order_b_legs=[leg])
    detector.register_order_b_reset_legs([leg])
    actual = detector._zone("blue", 1, "S", parent, moment(125))
    candidates = detector.order_candidates(moment(125), allow_bounded_continue=True)
    eligible = [c for c in candidates if c[6] is not None]
    expected = min(eligible, key=lambda c: (c[6][2], -c[1].first_idx))
    return {"direction": direction,
            "candidate_orders": [{"first":c[1].first_idx,"break":c[1].break_idx,
                                  "confirm":c[2].isoformat(),"stop":c[6][2].isoformat(),
                                  "causes":c[7]} for c in eligible],
            "expected_first":expected[1].first_idx,
            "actual_first":actual.order_first_index,
            "decision":actual.decision_event_time.isoformat(),
            "contradiction":actual.order_first_index != expected[1].first_idx}

def shared_s_before_gate(direction):
    market = chronology(direction, {10}, {15})
    detector = SZoneDetector(direction, [], [], [], [], market)
    parent = s_zone(direction, source=0, decision=110, stop=35, formation="type3")
    reaction = replace(physical(0, 0), mode="B")
    if direction == "bearish":
        reaction = mirror_candidate(reaction)
    entry = {"reaction":reaction, "reaction_number":2, "confirmation_time":moment(10),
             "stop_level":Decimal("120" if direction=="bullish" else "-120"),
             "stop_source_index":0,"stop_source_time":moment(0),
             "stop_cross":(0,moment(0),moment(15))}
    assert detector._shared_order_stop_cross(entry["confirmation_time"], entry["stop_level"]) == entry["stop_cross"]
    actual = detector.reconcile_shared_order_stops([parent], [entry])[0]
    return {"direction":direction,"source":parent.source_time.isoformat(),
            "a_stop":parent.a_stop_event_time.isoformat(),
            "input_decision":parent.decision_event_time.isoformat(),
            "actual_decision":actual.decision_event_time.isoformat(),
            "decision_before_a_stop":actual.decision_event_time < actual.a_stop_event_time,
            "actual_order_direction":actual.order_direction,
            "expected_order_direction":detector.order_direction,
            "accepted_order_identity":[actual.order_first_index,actual.order_break_index]}

def shared_s_direction_after_gate(direction):
    market=chronology(direction,{70},{90})
    detector=SZoneDetector(direction,[],[],[],[],market)
    parent=replace(s_zone(direction,source=60,decision=110,stop=35,formation="type3"),
                   price=Decimal("99" if direction=="bullish" else "-99"))
    reaction=replace(physical(2,2),mode="B")
    if direction=="bearish":reaction=mirror_candidate(reaction)
    entry={"reaction":reaction,"reaction_number":2,"confirmation_time":moment(70),
           "stop_level":Decimal("120" if direction=="bullish" else "-120"),
           "stop_source_index":0,"stop_source_time":moment(0),
           "stop_cross":(3,moment(90),moment(90))}
    assert detector._shared_order_stop_cross(entry["confirmation_time"],entry["stop_level"])==entry["stop_cross"]
    actual=detector.reconcile_shared_order_stops([parent],[entry])[0]
    assert actual.decision_event_time>=actual.a_stop_event_time
    return {"direction":direction,"source":str(actual.source_time),"a_stop":str(actual.a_stop_event_time),
            "decision":str(actual.decision_event_time),"color":actual.color,
            "actual_order_direction":actual.order_direction,"expected_order_direction":detector.order_direction,
            "missing_order_direction":actual.order_direction!=detector.order_direction}

def overlapping_windows(direction):
    market = chronology(direction)
    zone = SimpleNamespace(source_time=moment(90),price=Decimal("100" if direction=="bullish" else "-100"),
                           source_index=3, trigger_event_time=moment(50), reaction_break_time=moment(90))
    detector = SZoneDetector(direction, [], [], [], [zone], market)
    # Both windows are allowed by detect() when a trigger after the first handoff
    # is independent. It may then open a newer S handoff before its own source event.
    earlier, later = (moment(35),moment(111)),(moment(65),moment(121))
    detector.a_ownership_windows[:] = [earlier, later]
    actual_forward = detector._a_owned_by_s(zone)
    detector.a_ownership_windows[:] = [later, earlier]
    actual_reverse = detector._a_owned_by_s(zone)
    return {"direction":direction,"chronological_windows":actual_forward,
            "reverse_windows":actual_reverse,"order_dependent":actual_forward != actual_reverse}

def main():
    result = {"scope":"artificial production-source contract probes, not RAW correctness",
              "order_equal_stop_tie":[order_tie(d) for d in ("bullish","bearish")],
              "shared_s_before_a_gate":[shared_s_before_gate(d) for d in ("bullish","bearish")],
              "shared_s_direction_after_a_gate":[shared_s_direction_after_gate(d) for d in ("bullish","bearish")],
              "overlapping_s_ownership":[overlapping_windows(d) for d in ("bullish","bearish")]}
    print(json.dumps(result,indent=2))
    (Path(__file__).parent/"probe-results.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")

if __name__ == "__main__":
    main()
