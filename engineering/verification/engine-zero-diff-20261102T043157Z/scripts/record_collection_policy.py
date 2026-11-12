"""Make the already-declared collector repetition policy machine-readable."""
import json
from matrix import EVIDENCE, save

cases = json.loads((EVIDENCE / "discovery/workloads.json").read_bytes())
practical_policy = {case["id"]: 2 if case["id"].startswith("usoil-month-") else 5 for case in cases}
save(EVIDENCE / "discovery/collection-policy.json", {
    "basis": "collect_repaired_baseline.py and collect_after.py explicitly select two multi-minute month runs and five practical runs; workloads.repeats=5 is the general recommendation, overridden visibly by those controllers",
    "reason": "Complete untrimmed month RAW takes several minutes per run; actual limited repetitions/dispersion must be disclosed, not treated as five samples",
    "required_repeats": {"before": {case["id"]: 2 for case in cases}, "repaired-before": practical_policy, "after": practical_policy},
})
