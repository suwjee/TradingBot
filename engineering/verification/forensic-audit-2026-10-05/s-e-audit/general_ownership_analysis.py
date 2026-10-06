"""Across all saved traces, refute stale S-window output impact independently."""
from __future__ import annotations
import importlib.util
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

OUT=Path(__file__).resolve().parent
AUDIT=OUT.parent
sys.path.insert(0,str(AUDIT))
sys.path.insert(0,str(OUT))
from run_raw_matrix import command
from trace_analysis import obj

def main():
    spec=importlib.util.spec_from_file_location("s_e_general_bridge",AUDIT/"package/bridge/trading_pipeline.py")
    bridge=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=bridge
    spec.loader.exec_module(bridge)
    registry=json.loads((AUDIT/"raw-registry.json").read_text(encoding="utf-8"))
    records=[]
    for path in sorted((AUDIT/"traces").glob("*.events.json")):
        match=re.fullmatch(r"raw-(\d+)-(\d+)s\.events\.json",path.name)
        if not match:continue
        index,tf=map(int,match.groups())
        raw=registry[index]
        raw_hash_before=hashlib.sha256(Path(raw["path"]).read_bytes()).hexdigest()
        assert raw_hash_before==raw["sha256"]
        args=bridge.parse_arguments(command(Path(raw["path"]),tf,raw["first"],raw["last"])[3:])
        timings={}
        engines=bridge.load_engines(args,timings)
        market=bridge.prepare_market_context(args,engines,timings)
        events=json.loads(path.read_text(encoding="utf-8"))
        reactions={}
        blues={}
        for direction in ("bullish","bearish"):
            result=engines.reaction.UnifiedReactionDetector(market.candles,market.seconds,0,len(market.candles)-1,direction).detect()
            reactions[direction]=result.reactions
            blues[direction]=engines.blue_line.detect_blue_lines(direction,result.reactions,market.chronology,result.resets)
        passes={"bullish":0,"bearish":0}
        for i,event in enumerate(events):
            if event["kind"]!="full-direction-pass":continue
            direction=event["direction"]
            discovery=events[i+1]
            assert discovery["kind"]=="order-b-discovery" and discovery["direction"]==direction
            initial=[obj(z) for z in event["initialS"]]
            invalid_s={tuple(z) for z in event["invalidS"]}
            windows=[(datetime.fromisoformat(a),datetime.fromisoformat(b) if b else None) for a,b in event["ownershipWindows"]]
            rejected=[z for z in initial if (str(z.source_time),z.source_index) in invalid_s]
            filtered=[w for w in windows if not any(w[0]==z.a_stop_event_time and w[1] is not None and abs((w[1]-z.decision_event_time).total_seconds())<=0.000002 for z in rejected)]
            detector=engines.s_zone.SZoneDetector(direction,reactions[direction],[],blues[direction],[obj(a) for a in event["allA"]],market.chronology)
            detector.a_ownership_windows[:]=windows
            before={str(a.source_time) for a in detector.eligible_a_zones}
            expected={a["source_time"] for a in event["eligibleA"]}
            assert before==expected,"Reconstructed eligibility must exactly match the observation trace"
            detector.a_ownership_windows[:]=filtered
            revived=[a for a in detector.eligible_a_zones if str(a.source_time) not in expected]
            original_eligible=[obj(a) for a in event["eligibleA"]]
            accepted_s=[obj(z) for z in discovery["acceptedS"]]
            accepted_e=[obj(z) for z in discovery["acceptedE"]]
            accepted_stopall=[obj(z) for z in discovery["acceptedStopAll"]]
            stop_detector=engines.e_zone.EZoneDetector(direction,[],[],accepted_s,[],market.chronology,sequence_priority=engines.lifecycle.sequence_priority)
            stop_finder=lambda z:stop_detector.parent_stop("S" if hasattr(z,"a_source_time") else "E",z)
            a_stop_finder=lambda a:detector.first_a_stop(a.price,detector._a_confirmation_time(a))
            checks=[]
            for a in revived:
                valid,invalid=engines.lifecycle.split_a_zones_by_dominant_stops(original_eligible+[a],accepted_s,accepted_e,accepted_stopall,market.candles,direction,stop_finder,
                                   trend_reactions=reactions[direction],confirmation_finder=detector.reaction_confirmation_time,a_stop_event_finder=a_stop_finder)
                checks.append({"source":str(a.source_time),"index":a.source_index,"price":str(a.price),
                               "valid":any(z.source_time==a.source_time for z in valid),
                               "invalid":any(z.source_time==a.source_time for z in invalid)})
            batch_valid,batch_invalid=engines.lifecycle.split_a_zones_by_dominant_stops(original_eligible+revived,accepted_s,accepted_e,accepted_stopall,market.candles,direction,stop_finder,
                                   trend_reactions=reactions[direction],confirmation_finder=detector.reaction_confirmation_time,a_stop_event_finder=a_stop_finder)
            revived_sources={a.source_time for a in revived}
            batch_revived_valid=[str(a.source_time) for a in batch_valid if a.source_time in revived_sources]
            records.append({"raw_index":index,"raw_path":raw["path"],"timeframe":tf,"direction":direction,"pass":passes[direction],
                            "original_eligible_exactly_reproduced":True,"invalid_S_windows_removed":len(windows)-len(filtered),
                            "revived_A_count":len(checks),"independently_accepted_A_count":sum(c["valid"] for c in checks),"checks":checks,
                            "batch_accepted_revived_A_count":len(batch_revived_valid),"batch_accepted_revived_A_sources":batch_revived_valid})
            passes[direction]+=1
        raw_hash_after=hashlib.sha256(Path(raw["path"]).read_bytes()).hexdigest()
        assert raw_hash_before==raw_hash_after
        for record in records:
            if record["raw_index"]==index and record["timeframe"]==tf:
                record["RAW_sha256_before"]=raw_hash_before
                record["RAW_sha256_after"]=raw_hash_after
                record["RAW_unchanged"]=True
    output={"scope":"all available saved observation traces; RAW chronology, Reaction/Blue, production A dominant split; no full Engine rerun",
            "timezone":"Asia/Tehran","records":records}
    (OUT/"general-ownership-results.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(json.dumps([{k:r[k] for k in ["raw_index","timeframe","direction","pass","invalid_S_windows_removed","revived_A_count","independently_accepted_A_count","batch_accepted_revived_A_count"]} for r in records],indent=2))

if __name__=="__main__":main()
