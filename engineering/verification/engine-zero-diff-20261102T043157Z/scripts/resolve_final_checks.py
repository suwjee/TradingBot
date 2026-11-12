"""Retain the initial helper failure and rerun only changed comparison checks."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from matrix import EVIDENCE, ROOT, save

path = EVIDENCE / "discovery/final-checks.json"
archive = EVIDENCE / "discovery/final-checks-initial.json"
if not archive.exists():
    archive.write_bytes(path.read_bytes())
records = json.loads(path.read_bytes())
scripts = Path(__file__).resolve().parent
replacements = {}
cli = json.loads((EVIDENCE / "discovery/cli-contract-comparison.json").read_bytes())
assert cli["status"] == "PASS" and len(cli["cases"]) == 7
replacements["cli-contract"] = {
    "name": "cli-contract", "command": [sys.executable, "-B", str(scripts / "cli_contract_check.py"), "--evidence-name", "cli-contract-v2"],
    "status": "PASS", "exit_code": 0, "log": str(EVIDENCE / "discovery/final-cli-contract-rerun.log"),
    "verified_after_execution_utc": datetime.now(timezone.utc).isoformat(),
    "supersedes": "final-checks-initial.json / cli-contract FAIL; unsupported test-only --e-zones option and empty-stdout assumption; original failure/partial artifacts retained",
}
for name, script in [("lexical-harness-unit", "test_lexical_output.py"), ("lexical-output", "lexical_output_check.py")]:
    command = [sys.executable, "-B", str(scripts / script)]
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = EVIDENCE / "discovery" / f"final-{name}-rerun.log"
    log.write_bytes(result.stdout)
    replacements[name] = {"name": name, "command": command, "status": "PASS" if result.returncode == 0 else "FAIL", "exit_code": result.returncode, "log": str(log), "verified_after_execution_utc": datetime.now(timezone.utc).isoformat(), "reason": "Comparator empty-input guard changed; original successful check retained in initial archive"}
    assert result.returncode == 0, result.stdout.decode(errors="replace")
updated = [replacements.get(record["name"], record) for record in records]
assert all(record["status"] == "PASS" for record in updated)
save(path, updated)
decision_path = EVIDENCE / "discovery/retention-decision.json"
decision = json.loads(decision_path.read_bytes())
decision["final_gates"] = "PASS"
decision["completion_claim"] = False
save(decision_path, decision)
print(json.dumps({"status": "PASS", "checks": len(updated), "cli_cases": len(cli["cases"])}))
