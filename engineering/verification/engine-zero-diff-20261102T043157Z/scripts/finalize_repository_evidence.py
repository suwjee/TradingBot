"""Capture final live inventory, byte guards, review patch and local-link evidence."""
from __future__ import annotations
import csv
from datetime import datetime
import difflib
import json
from pathlib import Path
import re
import subprocess
from zoneinfo import ZoneInfo
from export_final_reports import md
from export_baseline_reports import write_csv
from matrix import EVIDENCE, ROOT, file_sha, phase_source_guard, save


def git(*arguments):
    return subprocess.run(["git", *arguments], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    manifest = phase_source_guard("after", ROOT)
    with (EVIDENCE / "01_ENGINE_FILE_INVENTORY.csv").open(encoding="utf-8", newline="") as stream:
        original = {row["path"]: row for row in csv.DictReader(stream)}
    rows = []
    for path in sorted((ROOT / "engine").rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        old = original.get(relative)
        raw = path.read_bytes()
        source = raw.decode("utf-8") if path.suffix in {".py", ".md", ".json", ".toml", ".txt"} else None
        version = re.search(r'(?m)^\w+VERSION\s*=\s*"([^"]+)"', source or "")
        classification = old["classification"] if old else "test" if "tests" in path.parts else "new-unclassified"
        rows.append({"path": relative, "classification": classification, "bytes": len(raw), "sha256": file_sha(path),
                     "line_count": len(source.splitlines()) if source is not None else "", "source_version": version[1] if version else "",
                     "current_status": "live" if classification != "archive-not-runtime" else "not-selected",
                     "full_read_status": old["full_read_status"] if old else "YES - NEW TEST AUTHORED AND INDEPENDENTLY REVIEWED" if path.suffix == ".py" and "tests" in path.parts else "NOT APPLICABLE",
                     "initial_sha256": old["sha256"] if old else "NOT PRESENT INITIALLY", "changed_since_initial": old is None or old["sha256"] != file_sha(path)})
    assert not any(row["classification"] == "new-unclassified" for row in rows)
    assert all(relative in {row["path"] for row in rows} for relative in manifest)
    write_csv("01_ENGINE_FILE_INVENTORY_FINAL.csv", rows)
    head, branch, status, staged, whitespace = git("rev-parse", "HEAD"), git("branch", "--show-current"), git("status", "--porcelain=v1", "-uall"), git("diff", "--cached", "--binary"), git("diff", "--check")
    assert all(result.returncode == 0 for result in [head, branch, status, staged, whitespace])
    assert head.stdout.decode().strip() == "afb586b69ecd6e12bcef30e2dbc4163e764dfcdb"
    assert not staged.stdout, "Unexpected staged work must be preserved/reported"
    (EVIDENCE / "discovery/git-status-final.txt").write_bytes(status.stdout)
    (EVIDENCE / "discovery/git-diff-check-final.log").write_bytes(whitespace.stdout + whitespace.stderr)
    patch = git("diff", "--binary")
    assert patch.returncode == 0
    content = patch.stdout
    for relative in ["engine/tests/unit/test_carried_order_query.py", "engine/tests/unit/test_regime_output_determinism.py"]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        content += "".join(difflib.unified_diff([], text.splitlines(keepends=True), fromfile="/dev/null", tofile="b/"+relative)).encode()
    (EVIDENCE / "source-diffs/full-code-and-reference.patch").write_bytes(content)
    save(EVIDENCE / "discovery/git-final.json", {"branch": branch.stdout.decode().strip(), "head": head.stdout.decode().strip(), "staged_diff_bytes": len(staged.stdout), "diff_check": "PASS", "status_file": "git-status-final.txt", "code_reference_patch_sha256": file_sha(EVIDENCE / "source-diffs/full-code-and-reference.patch"), "no_commit_push_tag_release": True})
    links = sorted(path for path in EVIDENCE.glob("[0-9][0-9]_*") if path.is_file())
    md("INDEX.md", "Engine audit evidence index", "The original BEFORE is retained separately from the repaired-before optimization baseline. Read14 then10/11/12 for the scope and limits. All linked artifacts are local generated evidence, not algorithm authority.\n\n" + "\n".join(f"- [{path.name}]({path.name})" for path in links) + "\n\nReproduction scripts are under scripts/, immutable source/RAW/environment manifests under discovery/, full outputs under before/, repaired-before/, after/, and independent reviews under reviews/. No publication occurred.")
    checked_links = []
    for path in [EVIDENCE / "INDEX.md"]:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            resolved = (path.parent / target).resolve()
            checked_links.append({"document": str(path), "target": target, "exists": resolved.is_file()})
    assert all(row["exists"] for row in checked_links)
    save(EVIDENCE / "discovery/added-local-link-check.json", checked_links)
    print(json.dumps({"inventory_files": len(rows), "production_modules": len(manifest), "added_links": len(checked_links), "status": "PASS"}))


if __name__ == "__main__":
    main()
