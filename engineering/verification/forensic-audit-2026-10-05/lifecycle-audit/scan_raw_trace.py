"""Read saved source-level RAW trace; no market execution or source mutation."""
from pathlib import Path
from datetime import datetime,timedelta
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
trace=json.loads((ROOT/"traces"/"raw-08-30s.events.json").read_text(encoding="utf-8"))
payload=json.loads((ROOT/"traces"/"raw-08-30s.payload.json").read_text(encoding="utf-8"))
results=[]
for ordinal,event in enumerate(trace):
    if event.get("kind")!="full-direction-pass":continue
    s=event["acceptedS"]
    eligible=[a for a in event["eligibleA"] if a["source_index"] not in {z["source_index"] for z in s}]
    for z in s:
        decision=datetime.fromisoformat(z["decision_event_time"])
        floor=decision.replace(second=decision.second//30*30,microsecond=0)
        ceil=floor+(timedelta(seconds=30) if decision>floor else timedelta())
        if ceil==floor:continue
        for a in eligible:
            if datetime.fromisoformat(a["source_time"])==ceil:
                invalid=[list(x) for x in event["invalidA"]]
                results.append({"pass":ordinal,"direction":event["direction"],
                    "A_source":a["source_time"],"A_index":a["source_index"],"A_price":a["price"],
                    "A_calculation_invalid":[a["source_time"],a["source_index"]] in invalid,
                    "S_source":z["source_time"],"S_color":z["color"],"S_decision":z["decision_event_time"],
                    "containing_candle":str(floor),"actual_excluded_candle":str(ceil)})
(HERE/"raw-trace-rounding.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
print(json.dumps({"matches":len(results),"cases":results},indent=2))
