"""Create a byte-verified source/change bundle without RAW, state or credentials."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent


def main():
    assert json.loads((EVIDENCE / "checks-complete.json").read_bytes())["status"] == "PASS"
    assert (EVIDENCE / "FINAL_REPORT.md").is_file()
    destination = EVIDENCE / "delivery"
    destination.mkdir(exist_ok=True)
    stamp = datetime.now(ZoneInfo("Asia/Tehran")).isoformat(timespec="seconds")
    changed = subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, text=True).splitlines()
    owned = set(json.loads((EVIDENCE / "task-owned-tracked-paths.json").read_bytes()))
    assert set(changed) <= owned, "Review newly changed unrelated paths before creating a task patch."
    deleted = sorted(name for name in changed if not (ROOT / name).exists())
    files = {ROOT / name for name in changed if (ROOT / name).is_file()}
    files.update([ROOT / "engine/__init__.py", *sorted((ROOT / "engine/bridge").rglob("*.py")),
                  *sorted((ROOT / "engine/pipeline").rglob("*.py")),
                  *sorted((ROOT / "engine/styles").rglob("*.css")),
                  *sorted((ROOT / "engine/algorithms").glob("*Source_Synchronized.md"))])
    files.update(path for path in EVIDENCE.rglob("*") if path.is_file() and "delivery" not in path.relative_to(EVIDENCE).parts)
    files.update([*sorted((ROOT / "engine/tests/unit").glob("*.py")), ROOT / "apps/chart/tests/unit/removed-position-state.test.mjs"])
    files = {path for path in files if "__pycache__" not in path.parts and path.suffix not in (".pyc", ".pyo")}
    patch = destination / "tracked-changes.patch"
    subprocess.run(["git", "diff", "--binary", "--output=" + str(patch), "HEAD", "--", *sorted(owned)], cwd=ROOT, check=True)
    archive = destination / "tradingbot-engine-refactor-20261118.zip"
    manifest = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)}
    readme = f"""TradingBot source/change bundle
Created: {stamp}

The current workspace already contains these changes. This bundle preserves
the current Engine Python/style/reference source, changed Chart source,
maintained docs, tests and task evidence. File contents under current/ are
byte-identical to the live workspace at packaging time; SHA-256 is in manifest.json.

This is not a published release or an installer. No RAW, user state, sessions,
tokens, credentials, dependency tree or old engine/engine.zip is included.
The old engine/engine.zip remains an unchanged earlier archive in the workspace.

For a separate checkout, review tracked-changes.patch and the deletion list
before copying files. Merely overlaying current/ does not remove retired files.
Do not overwrite unrelated local work. Read FINAL_REPORT.md and its scope limits.

Deleted tracked paths:
""" + "\n".join(deleted) + "\n"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as bundle:
        bundle.writestr("README.txt", readme)
        bundle.writestr("manifest.json", json.dumps(dict(created_at=stamp, files=manifest, deleted=deleted), indent=2))
        bundle.write(patch, "tracked-changes.patch")
        for path in sorted(files):
            bundle.write(path, "current/" + path.relative_to(ROOT).as_posix())
    with ZipFile(archive) as bundle:
        for path in sorted(files):
            assert bundle.read("current/" + path.relative_to(ROOT).as_posix()) == path.read_bytes(), path
    (destination / "bundle-verification.json").write_text(json.dumps(dict(status="PASS", created_at=stamp,
        files=len(files), zip_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(), deleted=deleted), indent=2), encoding="utf-8")
    print("PASS byte-equivalent bundle", archive, "files", len(files))


if __name__ == "__main__":
    main()
