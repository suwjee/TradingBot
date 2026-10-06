"""Read-only deterministic forensic probes; no production mutation."""
from __future__ import annotations
import dataclasses
from datetime import datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "package" / "pipeline"))
from reaction_engine import (Candle, Candidate, BullishDetector, BearishDetector,
    UnifiedReactionDetector, MarketChronology, mirror_candle, mirror_candidate,
    LowerTimeframeIndex)
from blue_line_detector import count_scale_strikes
from a_zone_detector import AZoneDetector, BlueState

D = Decimal
T = datetime(2026, 10, 5, 12, 0, 0)  # synthetic Asia/Tehran-local scenario

def row(index, second, o, h, l, c):
    t = T + timedelta(seconds=second)
    vals = [D(str(v)) for v in (o, h, l, c)]
    return Candle(index, t, t.strftime("%Y-%m-%d %H:%M:%S"),
                  "GREEN" if vals[3] >= vals[0] else "RED", *vals)

def main_and_lower(data):
    main = [row(i, i * 30, *values) for i, values in enumerate(data)]
    lower = []
    for i, values in enumerate(data):
        o, h, l, c = values
        # Each 5s candle carries consistent aggregate geometry.
        for j in range(6):
            lower.append(row(len(lower), i * 30 + 5 * j, o, h, l, c))
    return main, lower

def pack(obj):
    if dataclasses.is_dataclass(obj):
        return {f.name: pack(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, dict): return {str(k): pack(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)): return [pack(x) for x in obj]
    if isinstance(obj, (Decimal, datetime)): return str(obj)
    return obj

def initial_confirmation_reuse():
    main, lower = main_and_lower([(8.5,10,8,9), (9,9.5,8.5,8.7),
                                  (10.5,11,8.6,9.5), (9.5,12,8.7,11.5)])
    results = {}
    for direction, detector in (("bullish", BullishDetector), ("bearish", BearishDetector)):
        m = main if direction == "bullish" else [mirror_candle(x) for x in main]
        s = lower if direction == "bullish" else [mirror_candle(x) for x in lower]
        unified = UnifiedReactionDetector(m,s,0,3,direction).detect()
        reference = detector(m,s,0,3).detect()
        results[direction] = {"unified": pack(unified), "directional": pack(reference)}
        assert [(x.first_idx,x.break_idx) for x in unified.reactions] == [(1,2)]
        assert [(x.first_idx,x.break_idx) for x in reference.reactions] == [(1,2),(2,3)]
    return {"main":pack(main), "lower":pack(lower), "results":results}

def blue_post_confirmation_extreme():
    # Break is GREEN but Low=5 is only seen at 12:01:15, after confirmation 12:01:00.
    main = [row(0,0,8.5,10,8,9), row(1,30,9.5,9.8,9,9.2), row(2,60,9.2,11,5,10)]
    lower = [row(0,0,8.5,10,8,9), row(1,30,9.5,9.8,9,9.2),
             row(2,60,9.2,10.5,9.1,10), row(3,75,10,11,5,10)]
    reaction = Candidate(1,main[1].display_time,0,main[0].display_time,D(10),
                         1,main[1].display_time,D("9"),"A",leg_boundary_value=D(8),
                         break_idx=2,break_time=main[2].display_time)
    results = {}
    for direction in ("bullish","bearish"):
        m = main if direction=="bullish" else [mirror_candle(x) for x in main]
        s = lower if direction=="bullish" else [mirror_candle(x) for x in lower]
        r = reaction if direction=="bullish" else mirror_candidate(reaction)
        chronology = MarketChronology(m,s,30)
        confirmation = chronology.reaction_confirmation(direction,r)
        reference = D(8) if direction=="bullish" else D(-8)
        level,strikes = count_scale_strikes(direction,r,chronology,reference)
        assert len(strikes)==1
        assert strikes[0].extreme == (D(5) if direction=="bullish" else D(-5))
        results[direction] = {"level":str(level),"confirmation":str(confirmation),
            "strikes":pack(strikes),"expected_strike_count_through_confirmation":0}
    return {"main":pack(main),"lower":pack(lower),"results":results}

def blue_intrabar_ignores_first_confirmation():
    main = [row(0,0,8.5,10,8,9),row(1,30,9.5,9.8,9,9.2),row(2,60,10.4,11,5,9.5)]
    lower=[row(0,0,8.5,10,8,9),row(1,30,9.5,9.8,9,9.2),
           row(2,60,10.4,10.5,9.1,9.5),row(3,75,9.5,11,5,9.5)]
    reaction=Candidate(1,main[1].display_time,0,main[0].display_time,D(10),1,
                       main[1].display_time,D(9),"A",leg_boundary_value=D(8),break_idx=2,break_time=main[2].display_time)
    out={}
    for direction in ("bullish","bearish"):
        m=main if direction=="bullish" else [mirror_candle(x) for x in main]
        s=lower if direction=="bullish" else [mirror_candle(x) for x in lower]
        r=reaction if direction=="bullish" else mirror_candidate(reaction)
        chronology=MarketChronology(m,s,30)
        _,strikes=count_scale_strikes(direction,r,chronology,D(8) if direction=="bullish" else D(-8))
        assert len(strikes)==1 and strikes[0].extreme==(D(5) if direction=="bullish" else D(-5))
        out[direction]={"confirmation":str(chronology.reaction_confirmation(direction,r)),"strikes":pack(strikes),
                        "expected_strike_count_through_first_confirmation":0}
    return {"main":pack(main),"lower":pack(lower),"results":out}

def lower_index_differential(seed=5301):
    rng=random.Random(seed)
    candles=[row(i,i*5,0,rng.randint(1,100),-rng.randint(1,100),0) for i in range(128)]
    tree=LowerTimeframeIndex(candles)
    comparisons=0
    for _ in range(500):
        l=rng.randrange(128); r=rng.randrange(l+1,129); level=D(rng.randint(-110,110))
        for attr,method,test in (("low",tree.first_less,lambda x:x<level),("high",tree.first_greater,lambda x:x>level)):
            expected=next((i for i in range(l,r) if test(getattr(candles[i],attr))),None)
            assert method(l,r,level)==expected
            comparisons+=1
        expected_min=min(range(l,r),key=lambda i:(candles[i].low,i))
        expected_max=max(range(l,r),key=lambda i:(candles[i].high,-i))
        assert tree.range_minimum(l,r)==(candles[expected_min].low,expected_min)
        assert tree.range_maximum(l,r)==(candles[expected_max].high,expected_max)
        comparisons+=2
    return {"seed":seed,"comparisons":comparisons,"status":"PASS"}

def sparse_first_main_gap():
    starts=[0,60,90,120]
    values=[(8,10,7,9),(9,9.5,8,8.5),(9,11,8.2,10),(10,10.5,6,7)]
    main=[row(i,start,*v) for i,(start,v) in enumerate(zip(starts,values))]
    lower=[row(i*6+j,start+j*5,*v) for i,(start,v) in enumerate(zip(starts,values)) for j in range(6)]
    out={}
    for direction in ("bullish","bearish"):
        m=main if direction=="bullish" else [mirror_candle(x) for x in main]
        s=lower if direction=="bullish" else [mirror_candle(x) for x in lower]
        detector=UnifiedReactionDetector(m,s,0,3,direction)
        result=detector.detect()
        assert detector.timeframe.total_seconds()==60
        assert result.resets[0].index==2
        assert result.resets[0].second_time==m[3].display_time
        out[direction]={"inferred_timeframe_seconds":detector.timeframe.total_seconds(),"actual_timeframe_seconds":30,
                        "result":pack(result),"expected_reset_main_index":3,"expected_reset_main_time":m[3].display_time}
    return {"main":pack(main),"lower":pack(lower),"results":out}

def earliest_geometry_same_main():
    main,lower=main_and_lower([(10,20,0,15),(15,19,1,14),(14,15,2,14.5),(14.5,14.8,3,14),(14,21,4,20)])
    lower=lower[:24]+[row(24,120,14,16,5,15),row(25,130,15,21,4,20)]
    out={}
    for direction in ("bullish","bearish"):
        m=main if direction=="bullish" else [mirror_candle(x) for x in main]
        s=lower if direction=="bullish" else [mirror_candle(x) for x in lower]
        detector=UnifiedReactionDetector(m,s,0,4,direction)
        chosen=detector._earliest_confirmed_geometry(direction,1,4)
        chronology=MarketChronology(m,s,30)
        choices=[]
        for first in (1,3):
            c=detector._build_direct_candidate(direction,0,first)
            completed,_=detector._scan_direct_candidate(direction,c,4)
            choices.append({"candidate":pack(completed),"confirmation":str(chronology.reaction_confirmation(direction,completed))})
        assert chosen.first_idx==1
        assert choices[0]["confirmation"]>choices[1]["confirmation"]
        out[direction]={"chosen":pack(chosen),"choices":choices,"method_contract_earliest_first_index":3,
                        "production_order_membership_consequence":"NOT_PROVEN"}
    return {"main":pack(main),"lower":pack(lower),"results":out}

def main():
    results={"initial_confirmation_reuse":initial_confirmation_reuse(),
             "blue_post_confirmation_extreme":blue_post_confirmation_extreme(),
             "blue_intrabar_ignores_first_confirmation":blue_intrabar_ignores_first_confirmation(),
             "sparse_first_main_gap":sparse_first_main_gap(),
             "earliest_geometry_same_main":earliest_geometry_same_main(),
             "lower_index_differential":lower_index_differential()}
    out=Path(__file__).with_name("probe-evidence.json")
    out.write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(json.dumps({"evidence":str(out),"initial_reuse":"REPRODUCED_BOTH_DIRECTIONS",
                      "blue_lookahead":"REPRODUCED_BOTH_DIRECTIONS",
                      "sparse_timeframe":"REPRODUCED_BOTH_DIRECTIONS",
                      "lower_index":results["lower_index_differential"]}))

if __name__=="__main__": main()
