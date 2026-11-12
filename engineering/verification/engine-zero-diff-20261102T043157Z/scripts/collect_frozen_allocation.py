"""Run the fresh post-repair allocation baseline after all normal paired work."""
import json
from pathlib import Path
import subprocess
import sys
import time
from matrix import EVIDENCE, ROOT, save

while True:
    progress = EVIDENCE / "discovery/paired-progress.json"
    if progress.exists() and json.loads(progress.read_bytes()).get("stage") == "complete":
        break
    time.sleep(3)

case = "usoil-oct22-5s-bearish-legacy-no-primary"
command = [sys.executable, "-B", str(Path(__file__).with_name("instrumented.py")), "alloc", "repaired-before", case,
           "--baseline-phase", "repaired-before", "--source-root", str(EVIDENCE / "discovery/repaired-source-before")]
result = subprocess.run(command, cwd=ROOT)
save(EVIDENCE / "discovery/frozen-allocation-completion.json", {"status": "PASS" if result.returncode == 0 else "FAIL", "command": command, "exit_code": result.returncode})
raise SystemExit(result.returncode)
