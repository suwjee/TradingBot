"""Read bounded progress for the currently running serial verification jobs."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent


def lines(path):
    return path.read_text(errors="replace").splitlines() if path.exists() else []


matrix = lines(EVIDENCE / "matrix.log")
checks = lines(EVIDENCE / "finish-checks.log")
case = next((row for row in reversed(matrix) if row.startswith("START ")), "")
phase = None
match = re.fullmatch(r"START (removed|optimized) (USOIL|XAUUSD) (bullish|bearish) run (\d+)", case)
if match:
    variant, symbol, direction, number = match.groups()
    log = ROOT / "apps/chart/state/tmp/engine-refactor-20261117/matrix" / f"{variant}-{symbol}-{direction}-{int(number)-1}.stderr.log"
    for row in reversed(lines(log)):
        if row.startswith("QG_PROGRESS:"):
            phase = json.loads(row[len("QG_PROGRESS:"):])
            break
step = next((row.removeprefix("START ") for row in reversed(checks) if row.startswith("START ")), "")
detail = lines(EVIDENCE / (step + ".log"))[-2:] if step else []
if step == "replacement-final-sample":
    candidates = [ROOT / "apps/chart/state/tmp/engine-refactor-20261117/matrix" / f"{variant}-USOIL-bullish-0.stderr.log"
                  for variant in ("removed", "optimized")]
    newest = max((path for path in candidates if path.exists()), key=lambda path: path.stat().st_mtime)
    for row in reversed(lines(newest)):
        if row.startswith("QG_PROGRESS:"):
            phase = {"replacement": newest.name, **json.loads(row[len("QG_PROGRESS:"):])}
            break
elif step == "variants":
    variant_dir = ROOT / "apps/chart/state/tmp/engine-refactor-20261117/variants"
    candidates = list(variant_dir.glob("*.stderr.log"))
    live_dir = ROOT / "apps/chart/state/tmp/engine-refactor-20261117/live-variants"
    candidates.extend(live_dir.glob("*.stderr.log"))
    if candidates:
        newest = max(candidates, key=lambda path: path.stat().st_mtime)
        phase = {"bounded_case": newest.stem}
        for row in reversed(lines(newest)):
            if row.startswith("QG_PROGRESS:"):
                phase.update(json.loads(row[len("QG_PROGRESS:"):]))
                break
print(json.dumps(dict(case=case, phase=phase, matrix=matrix[-3:], checks=checks[-3:], check_detail=detail,
    complete=(EVIDENCE / "checks-complete.json").exists(),
    error=any("Traceback" in row or "AssertionError" in row or "RuntimeError" in row for row in matrix[-10:] + checks[-10:]))))
