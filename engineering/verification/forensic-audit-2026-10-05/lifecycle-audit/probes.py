"""Read-only lifecycle forensic probes; production/RAW files are never changed."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from bisect import bisect_left, bisect_right
from dataclasses import asdict, fields
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace as NS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PACKAGE = ROOT / "package"
sys.path.insert(0, str(PACKAGE / "pipeline"))
import lifecycle_engine as lc
from a_zone_detector import AZone
from e_zone_detector import EZone
from reaction_engine import Candle, MarketChronology
from s_zone_detector import SZone, SZoneDetector
from order_audit_engine import prepare_order_audit

BASE = datetime(2000, 1, 1)
def t(s): return BASE + timedelta(seconds=s)
def candle(index, seconds, low="100", high="120", close="110"):
    stamp = t(seconds)
    return Candle(index, stamp, stamp.strftime("%Y-%m-%d %H:%M:%S"), "GREEN",
                  Decimal("110"), Decimal(high), Decimal(low), Decimal(close))
def s_zone(direction, source, decision, color="blue", price=None, a_source=0):
    data = {field.name: None for field in fields(SZone)}
    data.update(direction=direction, color=color, formation_type="type4", a_ordinal=1,
        a_source_index=a_source//30, a_source_time=t(a_source), a_price=Decimal("110"),
        a_stop_index=1, a_stop_time=t(30), a_stop_event_time=t(35),
        source_index=source//30, source_time=t(source),
        price=Decimal(price or ("100" if direction == "bullish" else "120")),
        decision_index=decision//30, decision_time=t(decision//30*30), decision_event_time=t(decision),
        order_mode="B" if color == "red" else None)
    return SZone(**data)
def e_zone(direction, source, decision, family="red", number=1, price=None, parent=None, parent_stop=None):
    data={field.name: None for field in fields(EZone)}
    data.update(direction=direction, family=family, number=number,
        source_index=source//30, source_time=t(source), price=Decimal(price or ("100" if direction=="bullish" else "120")),
        decision_index=decision//30, decision_time=t(decision//30*30), decision_event_time=t(decision),
        order_direction="bearish" if direction=="bullish" else "bullish", order_reaction_number=1,
        order_mode="B", order_causes=("parent-stop",), order_parent_stop_cause_time=parent_stop,
        order_first_index=source//30, order_first_time=t(source), order_break_index=source//30,
        order_break_time=t(source), order_confirmation_time=t(decision-5), order_box_top=Decimal("120"),
        order_box_top_source_index=source//30, order_box_top_source_time=t(source), order_box_bottom=Decimal("100"),
        order_box_bottom_source_index=source//30, order_box_bottom_source_time=t(source),
        order_stop_level=Decimal("120" if direction=="bullish" else "100"), order_stop_source_index=source//30,
        order_stop_source_time=t(source))
    if parent is not None:
        data.update(parent_type="S" if hasattr(parent,"a_source_time") else "E",
            parent_source_index=parent.source_index,parent_source_time=parent.source_time,
            parent_price=parent.price,parent_stop_index=int((parent_stop-BASE).total_seconds())//30,
            parent_stop_time=t(int((parent_stop-BASE).total_seconds())//30*30),parent_stop_event_time=parent_stop)
    return EZone(**data)
def a_zone(direction, source, price=None, provenance=30, trigger=None):
    data={field.name:None for field in fields(AZone)}
    data.update(direction=direction, source_index=source//30, source_time=t(source),
        price=Decimal(price or ("100" if direction=="bullish" else "120")),
        blue_1_source_time=t(provenance),blue_2_source_time=t(provenance),
        continuation_source_time=t(provenance),reaction_first_time=t(provenance),
        trigger_event_time=t(trigger if trigger is not None else provenance))
    return AZone(**data)
def chronology(direction, stops=(), length=301):
    lower=[candle(i,i*5,low="99" if direction=="bullish" and i*5 in stops else "100",
                          high="121" if direction=="bearish" and i*5 in stops else "120") for i in range(length//5+1)]
    return MarketChronology([candle(i,i*30) for i in range(length//30+1)],lower,30)
def summarize(zones):
    return [{"number":z.number,"source":z.source_time,"gate":z.gate_event_time,
             "gate_type":z.gate_type,"owner":z.stopped_behavior_key,"count":z.stopped_behavior_count} for z in zones]

results=[]
for direction in ("bullish","bearish"):
    # Real Candle chronology + real SZone/AZone show left insertion rounds an intrabar event upward.
    main=[candle(i,i*30) for i in range(5)]
    sz=s_zone(direction,0,35)
    az=[a_zone(direction,30),a_zone(direction,60)]
    observed=lc.visible_a_zones_after_s_stops(az,[sz],main)
    results.append({"case":"A_S_transition_rounding","direction":direction,
        "S_source":sz.source_time,"S_decision":sz.decision_event_time,
        "containing_index":bisect_right([x.timestamp for x in main],sz.decision_event_time)-1,
        "actual_excluded_index":bisect_left([x.timestamp for x in main],sz.decision_event_time),
        "retained_A_sources":[a.source_time for a in observed],
        "expected_retained_A_sources":[t(60)],"mismatch":observed!=[az[1]]})

    # Changing only a future head stop changes which PAST opposite First gets blocked.
    invalid=a_zone(direction,30)
    opposite=NS(first_idx=2)
    missing=lc.blocked_orders_while_invalid_leg_heads_are_live([invalid],[opposite],main,direction,lambda _z:None)
    later=lc.blocked_orders_while_invalid_leg_heads_are_live([invalid],[opposite],main,direction,lambda _z:(3,t(90),t(95)))
    results.append({"case":"live_invalid_head_missing_stop","direction":direction,
        "head_source":invalid.source_time,"opposite_First":t(60),
        "blocked_without_future_stop":sorted(missing),"blocked_with_future_stop":sorted(later),
        "prefix_changes":missing!=later})

    # Refute a mock-stop artifact using the actual S first_a_stop API and lower-TF prices.
    invalid=a_zone(direction,30,price="99" if direction=="bullish" else "121")
    lower=[candle(i,i*5,low="99" if direction=="bullish" and i*5>=30 else "100",
                  high="121" if direction=="bearish" and i*5>=30 else "120") for i in range(19)]
    main=[candle(i,i*30,low="99" if direction=="bullish" and i>=1 else "100",
                  high="121" if direction=="bearish" and i>=1 else "120") for i in range(4)]
    prefix=MarketChronology(main,lower,30)
    after_lower=lower+[candle(19,95,low="98" if direction=="bullish" else "100",
                                   high="122" if direction=="bearish" else "120")]
    after_main=main[:3]+[candle(3,90,low="98" if direction=="bullish" else "100",
                                    high="122" if direction=="bearish" else "120")]
    extension=MarketChronology(after_main,after_lower,30)
    ds=[SZoneDetector(direction,[],[],[],[],c) for c in (prefix,extension)]
    events=[d.first_a_stop(invalid.price,invalid.source_time) for d in ds]
    blocks=[lc.blocked_orders_while_invalid_leg_heads_are_live([invalid],[opposite],c.candles,direction,
        lambda z,d=d:d.first_a_stop(z.price,z.source_time)) for d,c in zip(ds,(prefix,extension))]
    results.append({"case":"live_invalid_head_real_stop_API","direction":direction,
        "prefix_first_stop":events[0],"extension_first_stop":events[1],
        "prefix_blocked":sorted(blocks[0]),"extended_blocked":sorted(blocks[1]),
        "past_order_first":t(60),"prefix_changes":blocks[0]!=blocks[1]})

    # Old high-priority stop at 45, newest low-priority stop at 95. A provenance straddles newest only.
    older=e_zone(direction,0,5,"red")
    newer=e_zone(direction,60,65,"blue")
    aa=a_zone(direction,120,provenance=60)
    stops={id(older):t(45),id(newer):t(95)}
    visible=lc.visible_a_zones_after_module_boundaries([aa],[],[older,newer],direction,lambda x:stops[id(x)])
    results.append({"case":"A_boundary_priority_over_latest_stop","direction":direction,
        "old_Red_stop":t(45),"new_Blue_stop":t(95),"A_source":t(120),"A_min_provenance":t(60),
        "selected_owner":lc.dominant_module([older,newer]).family,
        "A_visible":bool(visible),"expected_A_visible_for_latest_stop":False})

    # Lower source cannot discard older higher owner that survived past its formation.
    older=e_zone(direction,0,5,"red")
    newer=e_zone(direction,30,35,"blue")
    sz=s_zone(direction,90,110,price="99" if direction=="bullish" else "121",a_source=60)
    stopped={id(older):t(80),id(newer):None}
    visible=lc.visible_s_zones_after_module_resets([sz],[older,newer],direction,lambda x:stopped[id(x)])
    baseline=lc.visible_s_zones_after_module_resets([sz],[older],direction,lambda x:stopped[id(x)])
    results.append({"case":"S_latest_source_discards_larger_owner","direction":direction,
        "older_Red_stop":t(80),"newer_Blue_source":t(30),"newer_Blue_decision":t(35),"S_source":t(90),
        "visible_with_lower_E":bool(visible),"visible_without_lower_E":bool(baseline)})

    # Exact-owner direct-parent narrow exception, strict equality, count1/count2; all production types.
    c=chronology(direction,(120,))
    first=s_zone(direction,0,10,"red")
    latest=s_zone(direction,30,40,"red")
    donor=e_zone(direction,120,190,parent=latest,parent_stop=t(120))
    equal=lc.detect_stopalls(direction,[first,latest],[donor],chronology(direction,()))
    before=copy.deepcopy((first,latest,donor))
    valid=lc.detect_stopalls(direction,[first,latest],[donor],c)
    single=lc.detect_stopalls(direction,[latest],[donor],c)
    wrong_data=asdict(donor);wrong_data["parent_source_time"]=first.source_time
    wrong=lc.detect_stopalls(direction,[first,latest],[EZone(**wrong_data)],c)
    results.append({"case":"exact_owner_contract_controls","direction":direction,
        "strict_equal_result":summarize(equal),"direct_parent_result":summarize(valid),
        "single_result":summarize(single),"wrong_parent_result":summarize(wrong),
        "inputs_unchanged":(first,latest,donor)==before,
        "pass":not equal and len(valid)==1 and not single and not wrong and (first,latest,donor)==before})

    ef=e_zone(direction,0,10,"red",2)
    el=e_zone(direction,30,40,"red",2)
    child=e_zone(direction,120,190,"red",3,parent=el,parent_stop=t(120))
    direct=lc.detect_stopalls(direction,[],[ef,el,child],c)
    impossible=asdict(child); impossible["decision_event_time"]=t(115)
    after_decision=lc.detect_stopalls(direction,[],[ef,el,EZone(**impossible)],c)
    wrong_stop=asdict(child);wrong_stop["parent_stop_event_time"]=t(125)
    mismatch=lc.detect_stopalls(direction,[],[ef,el,EZone(**wrong_stop)],c)
    results.append({"case":"direct_E_parent_controls","direction":direction,
        "valid":summarize(direct),"stop_after_donor_decision":summarize(after_decision),
        "wrong_exact_parent_stop":summarize(mismatch),
        "pass":len(direct)==1 and direct[0].stopped_behavior_key=="E2 red" and not after_decision and not mismatch})

    # Production call chain: accepted A selection -> E rebuild -> final OrderAudit.
    helper_path=ROOT.parents[2]/"engine"/"tests"/"unit"/"test_order_audit_lifecycle_contracts.py"
    spec=importlib.util.spec_from_file_location("audit_lifecycle_test_helpers",helper_path)
    helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
    d,parent,physical=helpers.detector_state(direction,invalid=True)
    zone=d._zone("blue",1,"S",parent,t(125))
    assert zone is not None
    identity=(physical.first_idx,physical.break_idx)
    accepted_source,rejected_source=t(0),t(30)
    ledger={identity:{"reaction_number":1,"reaction":physical,"confirmation_time":t(190),
        "stop_level":Decimal("120" if direction=="bullish" else "100"),
        "stop_source_index":4,"stop_source_time":t(125),
        "a_source_time":rejected_source,"a_stop_event_time":t(65),
        "a_causes":[(rejected_source,t(65)),(accepted_source,t(35))]}}
    frozen_ledger=copy.deepcopy(ledger)
    selected,blocked=lc.resolve_order_context(ledger,{accepted_source},{t(150)},[],set(),[],d.candles,direction,lambda _z:None)
    d.initial_order_audit=selected
    d.rebuild_accepted_order_audit([zone])
    prepared=prepare_order_audit(d,0,11,accepted_a_sources={accepted_source},required_identities={identity})
    prepared_causes=[cause for item in prepared for cause in item["causes"]]
    results.append({"case":"rejected_A_cause_restoration","direction":direction,
        "accepted_A_source":accepted_source,"rejected_A_source":rejected_source,
        "selected_primary_A_source":selected[identity]["a_source_time"],
        "selected_a_causes":selected[identity]["a_causes"],
        "rebuilt_causes":sorted(d.order_audit[identity]["causes"],key=str),
        "final_prepared_causes":prepared_causes,"ledger_unchanged":ledger==frozen_ledger,
        "rejected_A_in_final":any(c.get("parentType")=="A" and c.get("parentSourceTime")==rejected_source for c in prepared_causes)})

output={"authority_module":lc.__file__,"probe_cases":results}
(HERE / "probe-results.json").write_text(json.dumps(output,default=str,indent=2),encoding="utf-8")
print(json.dumps(output,default=str,indent=2))
