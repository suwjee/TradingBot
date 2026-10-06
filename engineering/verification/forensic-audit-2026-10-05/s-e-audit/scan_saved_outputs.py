"""Scan complete saved JSON outputs; skip matrix runs still writing files."""
import gzip
import json
from pathlib import Path

AUDIT=Path(__file__).resolve().parents[1]
cases=[]
equal_stop_candidates=[]
checked=[]
skipped=[]
for folder in ("raw-30s","raw-60s"):
    for file in sorted((AUDIT/folder).glob("*-1.stable.json.gz")):
        try:
            payload=json.loads(gzip.decompress(file.read_bytes()))
        except (OSError,EOFError,json.JSONDecodeError) as error:
            skipped.append({"file":str(file),"reason":str(error)})
            continue
        checked.append(str(file))
        for direction,body in payload.get("directions",{}).items():
            for zone in body.get("sZones",[]):
                if zone.get("orderFirstIndex") is not None and zone.get("orderDirection") is None:
                    cases.append({"file":str(file),"direction":direction,
                                  **{k:zone[k] for k in ("sourceTime","formationType","color","orderFirstIndex","orderBreakIndex","aStopEventTime","decisionEventTime")}})
            ledger={(a["firstIndex"],a["breakIndex"]):a for a in body.get("orderAudit",[])}
            by_stop={}
            for row in ledger.values():
                if row.get("stopHitEventTime") is not None:
                    by_stop.setdefault(row["stopHitEventTime"],[]).append(row)
            for zone in body.get("eZones",[]):
                selected=ledger.get((zone["orderFirstIndex"],zone["orderBreakIndex"]))
                if selected is None or selected.get("stopHitEventTime") is None:continue
                crossing=selected["stopHitEventTime"]
                if crossing<=zone["parentStopEventTime"]:continue
                later=[a for a in by_stop.get(crossing,()) if a["firstIndex"]>zone["orderFirstIndex"] and a["firstTime"]>zone["parentStopEventTime"]]
                if later:
                    equal_stop_candidates.append({"file":str(file),"direction":direction,
                            "E_source":zone["sourceTime"],"E_parent_stop":zone["parentStopEventTime"],"shared_order_stop":crossing,
                            "selected_order":[zone["orderFirstIndex"],zone["orderBreakIndex"]],
                            "later_orders":[[a["firstIndex"],a["breakIndex"]] for a in later]})
result={"checked_files":checked,"skipped":skipped,"cases":cases,"equal_stop_candidates_requiring_trace":equal_stop_candidates}
(AUDIT/"s-e-audit/RAW-order-direction-findings.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"checked":len(checked),"skipped":len(skipped),"cases":len(cases),"equal_stop_candidates":len(equal_stop_candidates),"tie_examples":equal_stop_candidates[:5]},indent=2))
