"""Deterministic synthetic market histories; execute immutable extracted modules."""
from __future__ import annotations
import json
from pathlib import Path
import random
from probes import row, pack
from reaction_engine import UnifiedReactionDetector, MarketChronology, mirror_candle, mirror_candidate
from blue_line_detector import detect_blue_lines
from a_zone_detector import AZoneDetector

def main():
    rng=random.Random(530105)
    cases=0; mirror_checks=0
    for case in range(1500):
        seconds=[]; candles=[]; price=100
        for i in range(40):
            lower=[]
            for j in range(6):
                o=price; price=o+rng.choice([-2,-1,1,2]);
                c=row(i*6+j,i*30+j*5,o,max(o,price)+rng.randrange(3),min(o,price)-rng.randrange(3),price)
                lower.append(c);seconds.append(c)
            # Avoid doji ambiguity in runtime reflection equivalence checks.
            if lower[-1].close==lower[0].open:
                price+=1
                last=lower[-1]
                new=row(last.index,i*30+25,last.open,max(last.high,price),last.low,price)
                lower[-1]=new;seconds[-1]=new
            candles.append(row(i,i*30,lower[0].open,max(x.high for x in lower),min(x.low for x in lower),lower[-1].close))
        actual=UnifiedReactionDetector(candles,seconds,0,39,"bullish").detect()
        reflected=UnifiedReactionDetector([mirror_candle(x) for x in candles],[mirror_candle(x) for x in seconds],0,39,"bearish").detect()
        expected=[pack(mirror_candidate(x)) for x in actual.reactions]
        assert expected==pack(reflected.reactions),case
        mirror_checks+=1
        for direction in ("bullish","bearish"):
            result=actual if direction=="bullish" else UnifiedReactionDetector(candles,seconds,0,39,direction).detect()
            chronology=MarketChronology(candles,seconds,30)
            lines=detect_blue_lines(direction,result.reactions,chronology,result.resets)
            try:
                AZoneDetector(direction,result.reactions,lines,chronology).detect()
            except Exception as exc:
                evidence={"seed":530105,"case":case,"direction":direction,"exception":type(exc).__name__,
                          "message":str(exc),"main":pack(candles),"lower":pack(seconds),"result":pack(result),"lines":pack(lines)}
                Path(__file__).with_name("fuzz-failure.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")
                print(json.dumps({"failure":case,"direction":direction,"exception":str(exc),"cases":cases,"mirror_checks":mirror_checks}))
                return
        cases+=1
    Path(__file__).with_name("fuzz-results.json").write_text(json.dumps({"cases":cases,"mirror_checks":mirror_checks,"status":"PASS"}),encoding="utf-8")
    print(json.dumps({"cases":cases,"mirror_checks":mirror_checks,"status":"PASS"}))

if __name__=="__main__":main()
