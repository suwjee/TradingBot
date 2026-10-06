"""Recheck saved full-RAW trace with immutable source and RAW chronology only."""
from __future__ import annotations
import importlib.util
import hashlib
import json
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

OUT = Path(__file__).resolve().parent
AUDIT = OUT.parent
sys.path.insert(0,str(AUDIT))
sys.path.insert(0,str(AUDIT/"package/pipeline"))
from run_raw_matrix import command

def obj(data):
    result={}
    for key,value in data.items():
        if isinstance(value,str) and len(value)>=19 and value[4:5]=="-" and value[10:11]==" ":
            try:value=datetime.fromisoformat(value)
            except ValueError:pass
        if key in {"price","a_price","parent_price","order_stop_level","continuation_level","blue_1_stop_level","blue_2_stop_level"} and value is not None:
            value=Decimal(value)
        result[key]=value
    return SimpleNamespace(**result)

def main():
    path=AUDIT/"package/bridge/trading_pipeline.py"
    spec=importlib.util.spec_from_file_location("s_e_trace_bridge",path)
    bridge=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=bridge
    spec.loader.exec_module(bridge)
    raw=json.loads((AUDIT/"raw-registry.json").read_text(encoding="utf-8"))[8]
    raw_hash_before=hashlib.sha256(Path(raw["path"]).read_bytes()).hexdigest()
    assert raw_hash_before==raw["sha256"]
    args=bridge.parse_arguments(command(Path(raw["path"]),30,raw["first"],raw["last"])[3:])
    timings={}
    engines=bridge.load_engines(args,timings)
    market=bridge.prepare_market_context(args,engines,timings)
    # Reaction only; no Blue/A/S/E/Order_B feedback recalculation.
    reaction_result=engines.reaction.UnifiedReactionDetector(market.candles,market.seconds,0,len(market.candles)-1,"bullish").detect()
    trend=reaction_result.reactions
    blue=engines.blue_line.detect_blue_lines("bullish",trend,market.chronology,reaction_result.resets)
    events=json.loads((AUDIT/"traces/raw-08-30s.events.json").read_text(encoding="utf-8"))
    target_time=datetime.fromisoformat("2026-09-29 20:15:30")
    output=[]
    for i,event in enumerate(events):
        if event["kind"]!="full-direction-pass" or event["direction"]!="bullish":continue
        target=next(obj(a) for a in event["allA"] if a["source_time"]==str(target_time))
        initial=[obj(z) for z in event["initialS"]]
        invalid_s={tuple(z) for z in event["invalidS"]}
        original_windows=[(datetime.fromisoformat(a),datetime.fromisoformat(b) if b else None) for a,b in event["ownershipWindows"]]
        rejected_windows={(z.a_stop_event_time,z.decision_event_time.replace()) for z in initial if (str(z.source_time),z.source_index) in invalid_s}
        # Remove only windows attached to explicitly invalid S, retaining unresolved
        # windows and valid historical S, regardless of public visibility.
        filtered_windows=[w for w in original_windows if not any(w[0]==start and w[1] is not None and abs((w[1]-decision).total_seconds())<=0.000002 for start,decision in rejected_windows)]
        all_a=[obj(a) for a in event["allA"]]
        detector=engines.s_zone.SZoneDetector("bullish",trend,[],blue,all_a,market.chronology)
        detector.a_ownership_windows[:]=original_windows
        before=detector._a_owned_by_s(target)
        source_event=detector._a_source_event_time(target)
        blocking=[(str(a),str(b)) for a,b in original_windows if a<=source_event and (b is None or source_event<b)]
        traced_eligible={a["source_time"] for a in event["eligibleA"]}
        original_eligible={str(a.source_time) for a in detector.eligible_a_zones}
        assert original_eligible==traced_eligible, "Reconstructed original ownership differs from saved trace"
        detector.a_ownership_windows[:]=filtered_windows
        after=detector._a_owned_by_s(target)
        revived=[a for a in detector.eligible_a_zones if str(a.source_time) not in traced_eligible]
        discovery=events[i+1]
        assert discovery["kind"]=="order-b-discovery"
        eligible=[obj(a) for a in event["eligibleA"]]
        assert target_time not in {a.source_time for a in eligible}
        inputs=eligible+[target]
        s=[obj(z) for z in discovery["acceptedS"]]
        e=[obj(z) for z in discovery["acceptedE"]]
        stopalls=[obj(z) for z in discovery["acceptedStopAll"]]
        stop_detector=engines.e_zone.EZoneDetector("bullish",[],[],s,[],market.chronology,sequence_priority=engines.lifecycle.sequence_priority)
        stop_finder=lambda z:stop_detector.parent_stop("S" if hasattr(z,"a_source_time") else "E",z)
        a_stop_finder=lambda a:detector.first_a_stop(a.price,detector._a_confirmation_time(a))
        valid,invalid=engines.lifecycle.split_a_zones_by_dominant_stops(inputs,s,e,stopalls,market.candles,"bullish",stop_finder,
                                trend_reactions=trend,confirmation_finder=detector.reaction_confirmation_time,a_stop_event_finder=a_stop_finder)
        stopped_before=[]
        for z in [*s,*e,*stopalls]:
            found=stop_finder(z)
            if found and z.source_time<target.source_time and found[-1]<=target.source_time:
                stopped_before.append({"type":"S" if hasattr(z,"a_source_time") else "E" if hasattr(z,"family") else "StopAll",
                                      "source":str(z.source_time),"price":str(z.price),"stop":str(found[-1]),
                                      "priority":engines.lifecycle.module_priority(z)})
        stopped_before.sort(key=lambda z:(z["stop"],z["priority"]))
        individual=[]
        for restored in revived:
            restored_valid,restored_invalid=engines.lifecycle.split_a_zones_by_dominant_stops(eligible+[restored],s,e,stopalls,market.candles,"bullish",stop_finder,
                                trend_reactions=trend,confirmation_finder=detector.reaction_confirmation_time,a_stop_event_finder=a_stop_finder)
            individual.append({"source":str(restored.source_time),"source_index":restored.source_index,"price":str(restored.price),
                               "valid_after_production_dominant_split":any(a.source_time==restored.source_time for a in restored_valid),
                               "invalid_after_production_dominant_split":any(a.source_time==restored.source_time for a in restored_invalid)})
        output.append({"pass":len(output),"source_event":str(source_event),"target_trigger":str(target.trigger_event_time),
                       "target_price":str(target.price),"blocking_windows":blocking,"owned_original":before,"owned_without_explicit_invalid_s":after,
                       "target_accepted_after_production_dominant_split":any(a.source_time==target_time for a in valid),
                       "target_invalid_after_production_dominant_split":any(a.source_time==target_time for a in invalid),
                       "stopped_accepted_owners_before_target":stopped_before[-5:],
                       "reconstructed_original_eligibility_equals_trace":True,"invalid_S_window_count_removed":len(original_windows)-len(filtered_windows),
                       "all_revived_A_individual_checks":individual})
    raw_hash_after=hashlib.sha256(Path(raw["path"]).read_bytes()).hexdigest()
    assert raw_hash_after==raw_hash_before
    result={"raw_index":8,"timeframe":30,"rows":raw["rows"],"timezone":"Asia/Tehran", "RAW_unchanged":raw_hash_before==raw_hash_after,
            "RAW_sha256_before":raw_hash_before,"RAW_sha256_after":raw_hash_after,
            "method":"saved trace; same production RAW chronology and canonical Bullish Reaction only; no full Engine rerun",
            "passes":output}
    (OUT/"trace-analysis.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
