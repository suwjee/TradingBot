"""Summarize real profiler evidence without mixing instrumented benchmark time."""
from __future__ import annotations
from datetime import datetime
import json
from zoneinfo import ZoneInfo
from matrix import EVIDENCE


def main():
    lines = ["---", "title: Engine measured CPU and allocation hotspots", "document_role: evidence", "lifecycle: generated", "owner: engine-zero-difference-audit",
             "last_modified_at: " + datetime.now(ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds"), "---", "", "# Measured profiles", "",
             "These are separate cProfile/tracemalloc runs of the complete supported Bridge pipeline. Instrumented wall/CPU figures are not normal benchmark results and are never used as a before/after speedup. The initial Bridge module import precedes cProfile enablement; engine loading/main processing are instrumented. Normal cold CLI measurements independently include startup/import and output I/O.", "",
             "Original profiles were captured against the unchanged initial production manifest before the separately authorized key-order repair. Three normal-output comparisons PASS; XAU historical Bullish profile completes normally but retains the known aggregate-key-order comparison FAIL. That failure is not normalized to PASS. Fresh post-repair profiling remains a separate gate before implementation."]
    targets = ["_carried_orders_for_parent", "_post_stop_accepted_orders_for_parent", "_zone", "_register_order_audit", "geometry_is_internal", "__init__"]
    for directory in sorted((EVIDENCE / "before/profile").iterdir()):
        if not (directory / "metadata.json").exists():
            continue
        metadata = json.loads((directory / "metadata.json").read_bytes())
        stats = json.loads((directory / "stats.json").read_bytes())
        total = next(item["cumulative_seconds"] for item in stats if item["function"] == "main" and item["file"].endswith("trading_pipeline.py"))
        lines.extend(["", "## " + directory.name, "", f"Engine exit: {metadata['exit_code']}; stable CLI comparison: {metadata['status']}; instrumented wall {metadata['instrumented_wall_seconds']:.6f}s, CPU {metadata['instrumented_cpu_seconds']:.6f}s. Raw cpu.prof, stats.json and top-cumulative.txt are retained in `{directory.relative_to(EVIDENCE).as_posix()}/`.", "",
                      "| Owner / function | Original line | Calls | Self seconds | Cumulative seconds | Fraction of main cumulative |",
                      "| --- | ---: | ---: | ---: | ---: | ---: |"])
        selected = [item for item in stats if item["function"] in targets and "/engine/" in item["file"].replace("\\", "/")]
        for item in selected[:10]:
            name = item["file"].replace("\\", "/").split("/")[-1] + ":" + item["function"]
            lines.append(f"| {name} | {item['line']} | {item['calls']} | {item['self_seconds']:.6f} | {item['cumulative_seconds']:.6f} | {100*item['cumulative_seconds']/total:.2f}% |")
    alloc = EVIDENCE / "before/alloc/usoil-oct22-5s-bearish-legacy-no-primary/metadata.json"
    if alloc.exists():
        metadata = json.loads(alloc.read_bytes())
        lines.extend(["", "## Allocation probe", "", f"USOIL October22,15,061 RAW rows,5s Bearish, legacy/primary disabled: engine exit{metadata['exit_code']}, stable comparison{metadata['status']}. Python traced current {metadata['tracemalloc_current_bytes']:,}B, peak {metadata['tracemalloc_peak_bytes']:,}B at trace depth5. Instrumented wall {metadata['instrumented_wall_seconds']:.3f}s is tracing overhead evidence, not a normal runtime. Raw allocations.json retains eighty line/size/count records. Python allocations exclude much native/runtime memory; OS process WorkingSet is a separate metric."])
    lines.extend(["", "## Ranked interpretation and protections", "",
                  "1. **Carried accepted Orders, OrderAudit original1410-1468:** each miss scans mutable ledger rows and eagerly allocates parent creation history, a second creation list and B generator before unchanged strict lifecycle/confirmation/stop predicates. The XAU October26 Bullish profile records27,911calls and14.924 cumulative seconds; the B extraction generator resumes4,638,677times. Broad scan cost remains O(ledger + causes + initial window + output sort). The first experiment should remove redundant temporary history/generator work, preserve eager failure order, minimum-parent selection, native object identity, stable insertion/sort ties and all cache invalidation. No new retained memory or index is needed. Detailed schema/mutation/error audit: reviews/carried-query-candidate.md. Regression protection includes real ledger fixtures, malformed/partial rows, strict/inclusive boundaries, both directions, native snapshots and all22 RAW/smoke scenarios.", "",
                  "2. **Post-stop accepted Order query, OrderAudit1471:** scans candidate confirmation suffixes and constructs/sorts physical matches. Existing cache depends on confirmation-index size and resets. A creation/liveness index would need all cause-only mutations, revocations/restorations and residual insertion rank; adding it now is materially riskier than local allocation reduction. Worst-case extra index O(ledger+causes) plus mutation cost; no such index is accepted.", "",
                  "3. **E discovery/rebuild, E378/788/1218 and Bridge1939/2274:** dominates cumulative runtime through repeated _zone calls, accepted Order queries and dependent reconciliation. Existing NlogN sparse extreme tables are reconstructed per detector; reuse across rebuilt detectors or regimes broadens lifetime and could retain stale mutable context. Repeated fresh prefixes/suffixes are an explicit semantic isolation obligation. Do not remove passes or share detector state merely to improve the displayed time.", "",
                  "4. **Blue internal geometry, Blue458:** repeated full behavior geometry checks are measurable in the supplied profile. A per-invocation containment index may be a later opportunity, but it must preserve exact inclusive/strict containment, identity and first/last semantics. Public Blue version/output compatibility also needs current convention review. No proposed indexed rule has been implemented or claimed equivalent.", "",
                  "Cumulative function fractions overlap along call chains and must not be summed. Counts/profile percentages are input-specific observations, not permanent project facts. Fewer source lines, static complexity bounds and historical improvements are not measurements of the current candidate.", ""])
    (EVIDENCE / "06_PROFILE_HOTSPOTS.md").write_text("\n".join(lines), encoding="utf-8")
    print("Wrote06_PROFILE_HOTSPOTS.md from completed raw profiles")


if __name__ == "__main__":
    main()
