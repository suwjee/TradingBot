"""Recompute acceptance from saved final-source measurements and exact bytes."""
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
SCRATCH = ROOT / "apps/chart/state/tmp/engine-refactor-20261117"
RETIRED = {"setupVersion", "setupPhase", "positionSetups", "stopAllAssessments", "behaviorAssessments", "setupReferenceBreaks"}


def strip_retired(value):
    if isinstance(value, dict):
        return {key: strip_retired(item) for key, item in value.items() if key not in RETIRED}
    if isinstance(value, list):
        return [strip_retired(item) for item in value]
    return value


def main():
    results = []
    for symbol in ("USOIL", "XAUUSD"):
        for direction in ("bullish", "bearish"):
            measurements = {"removed": [], "optimized": []}
            stable = None
            for run in range(3):
                for variant in measurements:
                    path = SCRATCH / "matrix" / f"{variant}-{symbol}-{direction}-{run}"
                    data = path.with_suffix(".stable.json").read_bytes()
                    if stable is None:
                        stable = data
                    assert data == stable, (symbol, direction, variant, run, "stable bytes or repeat differs")
                    measurements[variant].append(json.loads(path.with_suffix(".summary.json").read_bytes()))
            baseline = statistics.median(item["wall_seconds"] for item in measurements["removed"])
            optimized = statistics.median(item["wall_seconds"] for item in measurements["optimized"])
            baseline_cpu = statistics.median(item["cpu_seconds"] for item in measurements["removed"])
            optimized_cpu = statistics.median(item["cpu_seconds"] for item in measurements["optimized"])
            results.append(dict(symbol=symbol, direction=direction, runs=3, baseline_median_seconds=baseline,
                optimized_median_seconds=optimized, speedup=baseline / optimized,
                cpu_speedup=baseline_cpu / optimized_cpu,
                baseline_peak_working_set_median_bytes=statistics.median(item["peak_working_set_bytes"] for item in measurements["removed"]),
                optimized_peak_working_set_median_bytes=statistics.median(item["peak_working_set_bytes"] for item in measurements["optimized"]),
                measurements=measurements, stable_comparison="PASS: direct byte equality across all six outputs; timing telemetry only excluded"))
    original = json.loads((SCRATCH / "profile-original/full-bullish.stable.json").read_bytes())
    removed = json.loads((SCRATCH / "matrix/removed-USOIL-bullish-0.stable.json").read_bytes())
    assert json.dumps(strip_retired(original), separators=(",", ":")) == json.dumps(removed, separators=(",", ":"))
    (EVIDENCE / "performance-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("PASS: feature-removal-only comparison (six fields), all four full-RAW modes, three repeats each, exact stable bytes")
    for row in results:
        print(row["symbol"], row["direction"], f"{row['baseline_median_seconds']:.3f}s -> {row['optimized_median_seconds']:.3f}s = {row['speedup']:.3f}x")


if __name__ == "__main__":
    main()
