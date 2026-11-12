"""Read-only repository/input inventory and byte-exact pre-edit source capture."""
from __future__ import annotations

import ast
import csv
import hashlib
import importlib.metadata
import json
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[1]
ROOT = EVIDENCE.parents[2]


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(name: str, value: object) -> None:
    (EVIDENCE / "discovery" / name).write_text(json.dumps(value, indent=2), encoding="utf-8")


def main() -> None:
    rows = []
    production = []
    for path in sorted((ROOT / "engine").rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            kind = "bytecode-cache"
        elif "tests" in path.parts:
            kind = "test-" + path.relative_to(ROOT / "engine" / "tests").parts[0]
        elif "algorithms" in path.parts:
            kind = "accepted-reference"
        elif path.suffix == ".py":
            kind = "package-marker" if path.name == "__init__.py" else "production-source"
            production.append(path)
        elif path.suffix == ".zip":
            kind = "archive-not-runtime"
        else:
            kind = "support-asset"
        data = path.read_bytes()
        version = ""
        if path.suffix == ".py":
            text = data.decode("utf-8-sig")
            found = re.findall(r'^([A-Z_]*VERSION)\s*=\s*[\"\']([^\"\']+)', text, re.M)
            version = "; ".join(f"{key}={value}" for key, value in found)
        rows.append({"path": relative, "classification": kind, "bytes": len(data),
                     "sha256": hashlib.sha256(data).hexdigest(),
                     "line_count": len(data.splitlines()) if path.suffix in {".py", ".md", ".css"} else "",
                     "source_version": version, "current_status": "live" if kind != "archive-not-runtime" else "not-selected",
                     "full_read_status": "PENDING" if kind in {"production-source", "package-marker", "accepted-reference"} else "NOT APPLICABLE"})
    target = EVIDENCE / "01_ENGINE_FILE_INVENTORY.csv"
    if target.exists():
        raise RuntimeError("Initial inventory already exists; preserve it")
    with target.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = []
    imports = []
    for path in production:
        relative = path.relative_to(ROOT)
        destination = EVIDENCE / "discovery" / "source-before" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise RuntimeError(f"Snapshot exists: {destination}")
        shutil.copyfile(path, destination)
        manifest.append({"path": relative.as_posix(), "sha256": digest(path), "bytes": path.stat().st_size})
        tree = ast.parse(path.read_bytes(), filename=str(path))
        imports.extend({"file": relative.as_posix(), "line": node.lineno, "import": ast.unparse(node)}
                       for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
    save("source-manifest-before.json", manifest)
    save("imports.json", imports)
    raw = []
    raw_roots = [ROOT / "apps" / "chart" / "state" / "data", ROOT.parent / "TradingBot-Knowledge" / "07_DATA"]
    for raw_root in raw_roots:
        if not raw_root.exists():
            continue
        for path in sorted(raw_root.rglob("*.json")):
            if path.name.endswith((".meta.json", ".sidecar.json", ".coverage.json")):
                continue
            data = path.read_bytes()
            if not data.lstrip(b"\xef\xbb\xbf \r\n\t").startswith(b"["):
                continue
            items = json.loads(data.decode("utf-8-sig"))
            if not isinstance(items, list) or not items or not isinstance(items[0], dict) or "open" not in items[0]:
                continue
            gaps = [int(b["time"]) - int(a["time"]) for a, b in zip(items, items[1:])]
            raw.append({"path": str(path), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                        "rows": len(items), "first_time": items[0]["time"], "last_time": items[-1]["time"],
                        "min_step_seconds": min(gaps) if gaps else None,
                        "nonpositive_steps": sum(gap <= 0 for gap in gaps)})
    save("raw-inputs-before.json", raw)
    packages = {}
    for name in ["orjson", "tzdata", "pytest", "hypothesis", "psutil", "numpy"]:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "NOT INSTALLED"
    save("environment.json", {"captured_at": datetime.now(timezone.utc).isoformat(), "python": sys.version,
                              "executable": sys.executable, "platform": platform.platform(), "packages": packages,
                              "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                              "git_branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()})
    print(json.dumps({"engine_inventory": len(rows), "production_python_files": len(production),
                      "raw": raw, "packages": packages}, indent=2))


if __name__ == "__main__":
    main()
