"""Bounded actual-RAW Reaction/Blue/A audit, preserves every RAW byte."""
from __future__ import annotations
import argparse
from dataclasses import replace
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import sys
from time import perf_counter

from probes import ROOT, pack
import reaction_engine as reaction
from reaction_engine import UnifiedReactionDetector, MarketChronology, build_behavior_reaction_views
import blue_line_detector as blue
from a_zone_detector import AZoneDetector

spec=importlib.util.spec_from_file_location("audit_bridge",ROOT/"package"/"bridge"/"trading_pipeline.py")
bridge=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=bridge
spec.loader.exec_module(bridge)

def audit(path):
    started=perf_counter()
    raw_bytes=path.read_bytes()
    rows=json.loads(raw_bytes.decode("utf-8-sig"))
    sec_buckets,main_buckets=bridge.build_candle_buckets(rows,30)
    seconds=bridge.build_candle_objects(reaction,sec_buckets)
    candles=bridge.build_candle_objects(reaction,main_buckets)
    chronology=MarketChronology(candles,seconds,30)
    results={d:UnifiedReactionDetector(candles,seconds,0,len(candles)-1,d).detect()
             for d in ("bullish","bearish")}
    build_behavior_reaction_views(results,chronology)
    findings={}
    for direction,result in results.items():
        leaks=[]
        previous=None
        for number,r in enumerate(result.reactions,1):
            ref=(r.anchor_value if r.anchor_value is not None else r.leg_boundary_value) if r.mode=="A" else (
                previous.box_bottom if direction=="bullish" else previous.box_top)
            level,strikes=blue.count_scale_strikes(direction,r,chronology,ref)
            confirmed=chronology.reaction_confirmation(direction,r)
            bc=candles[r.break_idx]
            # Check strikes sourced by Break against lower rows through confirmation.
            for strike in strikes:
                if strike.source_index!=r.break_idx: continue
                eligible=chronology.lower_window(bc.timestamp,confirmed.replace(microsecond=1))
                attr="low" if direction=="bullish" else "high"
                eligible_extreme=(min(getattr(x,attr) for x in eligible) if direction=="bullish"
                                  else max(getattr(x,attr) for x in eligible))
                later=(strike.extreme<eligible_extreme if direction=="bullish" else strike.extreme>eligible_extreme)
                if later:
                    events=[x for x in chronology.lower_window(confirmed.replace(microsecond=1),bc.timestamp+chronology.timeframe)
                            if getattr(x,attr)==strike.extreme]
                    capped=replace(bc,low=min(x.low for x in eligible),high=max(x.high for x in eligible))
                    oracle_candles=list(candles);oracle_candles[r.break_idx]=capped
                    oracle=MarketChronology(oracle_candles,seconds,30)
                    _,capped_strikes=blue.count_scale_strikes(direction,r,oracle,ref)
                    leaks.append({"reaction_number":number,"reaction":pack(r),"confirmation":str(confirmed),
                                  "fibonacci":str(level),"strike":pack(strike),"eligible_extreme":str(eligible_extreme),
                                  "actual_strikes":pack(strikes),"strikes_with_break_extreme_capped_at_confirmation":pack(capped_strikes),
                                  "post_confirmation_extreme_rows":pack(events)})
            previous=r
        lines=blue.detect_blue_lines(direction,result.reactions,chronology,result.resets)
        for leak in leaks:
            leak["emitted_scale_blue_for_same_reaction"]=pack([x for x in lines if x.kind=="scale" and x.reaction_number==leak["reaction_number"]])
        # A standalone oracle namespace uses unchanged source for Blue sequencing,
        # substituting only the reference-required Break extreme eligibility.
        # The imported production module and chronology remain unmodified.
        def capped_count(d,r,ch,ref,candles_by_index=None):
            conf=ch.reaction_confirmation(d,r)
            bc=ch.candles[r.break_idx]
            eligible=ch.lower_window(bc.timestamp,conf.replace(microsecond=1))
            if not eligible:return blue.count_scale_strikes(d,r,ch,ref,candles_by_index)
            capped=replace(bc,low=min(x.low for x in eligible),high=max(x.high for x in eligible))
            cc=list(ch.candles);cc[r.break_idx]=capped
            och=MarketChronology(cc,ch.seconds,30)
            return blue.count_scale_strikes(d,r,och,ref)
        oracle_namespace=dict(vars(blue));oracle_namespace["count_scale_strikes"]=capped_count
        exec(inspect.getsource(blue.detect_blue_lines),oracle_namespace)
        oracle_lines=oracle_namespace["detect_blue_lines"](direction,result.reactions,chronology,result.resets)
        actual_packed=pack(lines);oracle_packed=pack(oracle_lines)
        first_diff=next((i for i,(a,b) in enumerate(zip(actual_packed,oracle_packed)) if a!=b),None)
        if first_diff is None and len(actual_packed)!=len(oracle_packed):first_diff=min(len(actual_packed),len(oracle_packed))
        blue_diff={"actual_count":len(lines),"oracle_count":len(oracle_lines),"first_difference_ordinal":first_diff+1 if first_diff is not None else None,
                   "actual_first_difference":actual_packed[first_diff] if first_diff is not None and first_diff<len(actual_packed) else None,
                   "oracle_first_difference":oracle_packed[first_diff] if first_diff is not None and first_diff<len(oracle_packed) else None}
        if first_diff is not None and first_diff<len(lines):
            rr=result.reactions[lines[first_diff].reaction_number-1]
            blue_diff["owning_reaction"]=pack(rr)
            blue_diff["owning_confirmation"]=str(chronology.reaction_confirmation(direction,rr))
        detector=AZoneDetector(direction,result.reactions,lines,chronology)
        try:
            zones=detector.detect(); a_status={"status":"PASS","count":len(zones)}
            oracle_zones=AZoneDetector(direction,result.reactions,oracle_lines,chronology).detect()
            a_status["oracle_count"]=len(oracle_zones)
            a_status["oracle_outputs_equal"]=pack(zones)==pack(oracle_zones)
            z_diff=next((i for i,(a,b) in enumerate(zip(pack(zones),pack(oracle_zones))) if a!=b),None)
            if z_diff is not None:
                a_status["first_difference_ordinal"]=z_diff+1
                a_status["actual_first_difference"]=pack(zones[z_diff])
                a_status["oracle_first_difference"]=pack(oracle_zones[z_diff])
        except Exception as exc:
            a_status={"status":"FAIL","type":type(exc).__name__,"message":str(exc)}
        first=result.reactions[0] if result.reactions else None
        initial_reuse=None
        if first:
            helper=UnifiedReactionDetector(candles,seconds,0,len(candles)-1,direction)
            hc=helper.bull if direction=="bullish" else helper.bear
            analysis=(hc.breakout_analysis(first,candles[first.break_idx]) if direction=="bullish"
                      else hc.breakdown_analysis(first,candles[first.break_idx]))
            seeded=helper._candidate_from_confirmation_remainder(direction,first,candles[first.break_idx],analysis)
            if seeded:
                for c in candles[first.break_idx+1:]:
                    previous_reset=c.low<first.box_bottom if direction=="bullish" else c.high>first.box_top
                    confirms=c.high>seeded.box_top if direction=="bullish" else c.low<seeded.box_bottom
                    if previous_reset: break
                    if confirms:
                        initial_reuse={"initial":pack(first),"missing_seed":pack(seeded),"would_confirm_at":str(c.timestamp),
                                       "canonical_id_present":any(x.first_idx==seeded.first_idx and x.break_idx==c.index for x in result.reactions)}
                        break
        findings[direction]={"reactions":len(result.reactions),"resets":len(result.resets),"blue":len(lines),
                             "post_confirmation_strike_count":len(leaks),"post_confirmation_strikes":leaks[:12],
                             "blue_eligibility_oracle_difference":blue_diff,
                             "initial_reuse":initial_reuse,"a":a_status}
    return {"raw":str(path),"sha256":hashlib.sha256(raw_bytes).hexdigest(),"rows":len(rows),
            "main_count":len(candles),"timeframe":30,"timezone":"Asia/Tehran", "findings":findings,
            "duration_seconds":round(perf_counter()-started,3)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--file",type=Path);args=parser.parse_args()
    files=[args.file] if args.file else sorted((p for p in Path("apps/chart/state/data/RAW").rglob("*.json")
              if "5S" in p.name and not p.name.endswith(".meta.json")),key=lambda p:p.stat().st_size)[:2]
    evidence=[]
    for file in files:
        case=audit(file);evidence.append(case)
        print(json.dumps({"raw":file.name,"duration":case["duration_seconds"],"findings":
            {d:{k:v for k,v in data.items() if k not in ("post_confirmation_strikes","initial_reuse")}
             for d,data in case["findings"].items()}},ensure_ascii=False),flush=True)
    Path(__file__).with_name("raw-evidence.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")

if __name__=="__main__": main()
