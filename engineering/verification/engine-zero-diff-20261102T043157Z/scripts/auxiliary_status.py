"""Record focused allocation measurement and resumable implementation state."""
from __future__ import annotations
from datetime import datetime
import importlib.util
import json
import sys
import tracemalloc
from pathlib import Path
from zoneinfo import ZoneInfo
from matrix import EVIDENCE, ROOT, save

sys.path.insert(0, str(ROOT / "engine/tests/unit"))
import test_carried_order_query as query

detector, _, physical = query.detector_state("bullish")
entry = query.ledger_entry(physical, parents=range(125, 10125), b_events=[150]*10000)
detector.order_audit = {(5, 6): entry}
detector._initial_order_records()
parent = query.SimpleNamespace(decision_event_time=query.moment(110))
tracemalloc.start(1)
matches = detector._carried_orders_for_parent(parent, query.moment(200))
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
save(EVIDENCE / "discovery/carried-allocation-before-after.json", {
    "method": "Artificial dense-provenance native query; allocation tracing depth1, not a market-reachability claim",
    "before_peak_bytes": 171032, "before_source": "discovery/carried-tests-red.log",
    "after_peak_bytes": peak, "after_current_bytes": current,
    "selected_order_identity_preserved": len(matches) == 1 and matches[0][1] is physical,
})
path = EVIDENCE / "CHECKPOINT.md"
text = path.read_text(encoding="utf-8")
for letter in "DEF":
    text = text.replace(f"- [ ] {letter}:", f"- [x] {letter}:")
stamp = datetime.now(ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds")
block = f"""\n## Latest verified resume state ({stamp})\n\nRepaired-before collection COMPLETE PASS:22 scenarios104 cold runs, all native snapshots,2fresh profiles and3warm cases. discovery/repaired-collection-progress.json records actual completion. Immutable postrepair14Source bytes at discovery/repaired-source-before. Original calculation comparison PASS22,0 unexpected differences; original two mapping-key-order FAILs remain preserved.\n\nCandidate O1 APPLIED only order_audit_engine.py: creation scratch-list reuse/eager B append, version1.8.2/timestamp2026-11-02T11:23:50+03:30. All330 Engine tests PASS and7cold smoke stable comparisons PASS0 differences. Focused artificial allocation current peak {peak}B versus measured171032B baseline; not a real-market memory/speedup claim. Final retention remains pending complete after comparison and comparable performance.\n\nAFTER collector running execsession99123, sequential/no concurrent workloads. Script scripts/collect_after.py; progress discovery/after-collection-progress.json and console discovery/after-collector-console.log. Early native snapshots XAU Oct26bull30s andUSOIL Oct22bear5s PASS exact graph0difference. Then104cold runs, all22native,2profiles,3warm and1allocation run. Do not change production bytes or start concurrent benchmark/tests until finished. Sourceguard frozen at after/source-manifest.json.\n\nFresh independent code reviewer candidate_independent_review running read-only; orders_primary_read researching active RAW regression flags, no workloads. Current References contain preparatoryBridge repair but still need O1 exact-Source sync after candidate decision. Final artifacts09-14 and final tests/anti-drift/report/link/diff guards pending. Need auxiliary alternating paired5seed benchmarks after collector, no hidden seed pin of defaultbaseline.\n\nOlder chronological checkpoint paragraphs below are historical; this block controls current resumable work.\n"""
position = text.index("\n## Current work")
path.write_text(text[:position] + block + text[position:], encoding="utf-8", newline="\n")
print(json.dumps({"after_peak_bytes": peak, "checkpoint": str(path)}))
