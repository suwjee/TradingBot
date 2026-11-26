#!/usr/bin/env python3
"""CP287 original-byte recovery. Run in a clean algorithm checkout with Git access."""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = "Audit/Phase_02/Rebaseline_v2_8_7/"
BASE = "c99b4c957e932d9ee70c492ca03ce80711447fc1"
MANIFEST = ROOT + "CP287_Artifact_Recovery_Manifest.json"

def require(ok, detail):
    if not ok:
        raise RuntimeError(detail)

def verify(data, row):
    require(len(data) == row["bytes"], "Size mismatch: " + row["path"])
    require(hashlib.sha256(data).hexdigest() == row["sha256"], "SHA256 mismatch: " + row["path"])
    blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
    require(blob == row["git_blob"], "Git blob mismatch: " + row["path"])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    archive = args.archive.resolve().read_bytes()
    repo = args.repo.resolve()

    def git(*parts):
        return subprocess.run(["git", "-C", str(repo), *parts], check=True, stdout=subprocess.PIPE).stdout

    def line(*parts):
        return git(*parts).decode().strip()

    require(not line("status", "--porcelain"), "Working tree must be clean")
    require(line("branch", "--show-current") == "algorithm", "Checkout algorithm first")
    remote = line("remote", "get-url", "origin").lower().rstrip("/")
    require(remote in {"https://github.com/suwjee/tradingbot.git", "https://github.com/suwjee/tradingbot", "git@github.com:suwjee/tradingbot.git", "git@github.com:suwjee/tradingbot", "ssh://git@github.com/suwjee/tradingbot.git"}, "Unexpected origin")
    git("fetch", "origin", "main", "algorithm")
    head = line("rev-parse", "origin/algorithm")
    require(line("rev-parse", "HEAD") == head, "Local algorithm is not at remote head")
    require(line("rev-parse", "origin/main") == BASE, "main baseline changed")
    manifest = json.loads(git("show", f"{head}:{MANIFEST}"))
    verify(archive, manifest["archive"])
    payloads = {manifest["archive"]["path"]: archive}
    with zipfile.ZipFile(args.archive.resolve()) as z:
        require(z.testzip() is None, "ZIP CRC failure")
        checks = {}
        for entry in z.read("SHA256SUMS.txt").decode().splitlines():
            digest, path = entry.split(maxsplit=1)
            require(path not in checks, "Duplicate checksum entry")
            checks[path] = digest
        for row in manifest["files"]:
            require(z.namelist().count(row["path"]) == 1, "Missing/duplicate member")
            data = z.read(row["path"])
            verify(data, row)
            require(checks.get(row["path"]) == row["sha256"], "Archive manifest mismatch")
            payloads[row["path"]] = data
    index = json.loads(git("show", f"{head}:{ROOT}CP287_Aggregate_Index_v5.json"))
    require(index["baseline"] == BASE and len(index["modules"]) == 16, "Unexpected index")
    declarations = {}
    for source, row in index["modules"].items():
        require(line("rev-parse", f"{BASE}:{source}") == row["source_blob"], "Source blob mismatch: " + source)
        path = ROOT + "Static_v5/" + row["file"]
        data = payloads[path] if path in payloads else git("show", f"{head}:{path}")
        verify(data, dict(row, path=path))
        report = json.loads(data)
        require(report["baseline"] == BASE and report["path"] == source, "Report identity mismatch: " + path)
        for record in report["scope_records"]:
            if record["kind"] in {"ClassDef", "FunctionDef", "AsyncFunctionDef"}:
                require(record["id"] not in declarations, "Duplicate declaration")
                declarations[record["id"]] = record
    inv = json.loads(payloads[ROOT + "CP287_Function_Inventory_v5.json"])
    actual = {record["id"]: record for record in inv["scope_records"]}
    require(inv["baseline"] == BASE and len(actual) == len(inv["scope_records"]) == len(declarations) == index["function_class_count"] == 674 and actual == declarations, "Function inventory does not exactly reconcile")
    print("PASS: archive, three payloads, 16 source blobs, 16 module reports, 674 declaration records")
    if not args.publish:
        print("Verification only: no publication")
        return
    for path in payloads:
        require(not (repo / path).exists(), "Refusing overwrite: " + path)
    for path, data in payloads.items():
        dest = repo / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    git("add", "--", *payloads)
    require(set(line("diff", "--cached", "--name-only").splitlines()) == set(payloads), "Unexpected staged paths")
    for path, data in payloads.items():
        require(git("show", ":" + path) == data, "Git staging altered bytes: " + path)
    git("commit", "-m", "CP287: publish original recovery ZIP and three verified artifacts")
    commit = line("rev-parse", "HEAD")
    git("push", "origin", "HEAD:refs/heads/algorithm")
    git("fetch", "origin", "main", "algorithm")
    require(line("rev-parse", "origin/algorithm") == commit, "Remote HEAD mismatch")
    require(line("rev-parse", "origin/main") == BASE, "main changed")
    for path, data in payloads.items():
        require(git("show", f"origin/algorithm:{path}") == data, "Remote byte mismatch: " + path)
    print("PASS remote publication:", commit)
    print("RB02 final closure review is separate; do not advance automatically.")

if __name__ == "__main__":
    main()
