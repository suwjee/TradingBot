"""Bounded read-only Bridge Output probes against extracted package Source."""
from pathlib import Path
from dataclasses import asdict, is_dataclass
from types import SimpleNamespace as NS
from datetime import datetime
from decimal import Decimal
import copy, importlib.util, json, sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/"package"/"pipeline"))
import core_utils, direction_policy, reaction_engine, order_audit_engine, lifecycle_engine, s_zone_detector, e_zone_detector
spec=importlib.util.spec_from_file_location("audit_projection_bridge",ROOT/"package"/"bridge"/"trading_pipeline.py")
bridge=importlib.util.module_from_spec(spec);sys.modules[spec.name]=bridge;spec.loader.exec_module(bridge)
helper_path=ROOT.parents[2]/"engine"/"tests"/"unit"/"test_order_audit_lifecycle_contracts.py"
spec=importlib.util.spec_from_file_location("audit_projection_helpers",helper_path)
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)

def normalize(value):
    if is_dataclass(value):return normalize(asdict(value))
    if isinstance(value,dict):return {str(k):normalize(v) for k,v in value.items()}
    if isinstance(value,(list,tuple,set,frozenset)):return sorted((normalize(v) for v in value),key=str) if isinstance(value,(set,frozenset)) else [normalize(v) for v in value]
    if isinstance(value,(datetime,Decimal)):return str(value)
    if hasattr(value,"__dict__"):return normalize(vars(value))
    return value

results=[]
for direction in ("bullish","bearish"):
    detector,parent,physical=helpers.detector_state(direction)
    zone=detector._zone("blue",1,"S",parent,helpers.moment(125))
    accepted=detector.rebuild_accepted_order_audit([zone])
    prepared=order_audit_engine.prepare_order_audit(detector,0,11)
    market=bridge.MarketContext(detector.lower,detector.candles,detector.lower_index,detector.chronology,0,11)
    projection=bridge.BridgeProjection(direction=direction,market=market,prepared_order_audit=prepared,order_direction=detector.order_direction)
    strict=bridge._bridge_proven_strict_event(market,direction,parent.price,helpers.moment(125))
    equal=bridge._bridge_proven_strict_event(market,direction,parent.price,helpers.moment(120))
    beyond=bridge._bridge_proven_strict_event(market,direction,parent.price,helpers.moment(400))
    assert strict==helpers.moment(125) and equal is None and beyond is None
    current=projection.current_order(parent,"S","blue",strict)
    wrong=projection.current_order(parent,"S","red",strict)
    stale=projection.current_order(parent,"S","blue",helpers.moment(126))
    assert current is not None and wrong is None and stale is None
    prior=normalize(detector.order_audit)
    frozen_parent=copy.deepcopy(parent)
    frozen_zone=copy.deepcopy(zone)
    before_resets=copy.deepcopy(detector.sequence_resets)
    state=NS(full_e_detectors={direction:detector},full_s_detectors={},
             full_lines_by_direction={direction:[]},results={direction:NS(reactions=[])})
    visibility=NS(blue_lines=[],projection_s_zones=[parent],projection_e_zones=accepted,projection_stopalls=[])
    output=bridge.build_bridge_output(direction,market,state,visibility,[],[],[],[],[parent],accepted,[],prepared)
    assert normalize(detector.order_audit)==prior and parent==frozen_parent and zone==frozen_zone and detector.sequence_resets==before_resets
    # Exact source parent lookup must not borrow a different same-index timestamp.
    exact=bridge._bridge_parent_behavior_for_e(projection,direction,zone,{(parent.source_index,parent.source_time):parent},{},{})
    wrong_identity=bridge._bridge_parent_behavior_for_e(projection,direction,zone,{(parent.source_index,helpers.moment(61)):parent},{},{})
    assert exact["color"]=="Blue" and wrong_identity["color"] is None
    results.append({"direction":direction,"strict_recorded_event":str(strict),
        "equality_does_not_select_later_cross":equal,"outside_horizon":beyond,
        "exact_parent_cause_join":current is not None,"wrong_family_declined":wrong is None,
        "wrong_event_declined":stale is None,"semantic_detector_inputs_unchanged":True,
        "same_index_wrong_time_parent_declined":wrong_identity["color"] is None,
        "counts":{k:len(v) for k,v in output.items()}})

spec=importlib.util.spec_from_file_location("audit_independent_reaction_probes",ROOT/"reaction-audit"/"probes.py")
reaction_probes=importlib.util.module_from_spec(spec);spec.loader.exec_module(reaction_probes)
independent={}
for name in ("initial_confirmation_reuse","blue_post_confirmation_extreme","blue_intrabar_ignores_first_confirmation","sparse_first_main_gap"):
    reaction_probes.__dict__[name]()
    independent[name]="REPRODUCED_BOTH_DIRECTIONS"
result={"bridge_module":bridge.__file__,"projection_probes":results,"independent_reaction_refutation":independent}
(HERE/"projection-probe-results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))
