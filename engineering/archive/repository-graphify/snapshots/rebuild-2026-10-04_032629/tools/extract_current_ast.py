"""Extract the current project code graph without indexing local or archived content."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from graphify.detect import detect
from graphify.extract import extract


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    if not out.is_relative_to(root / "engineering" / "archive" / "repository-graphify"):
        raise SystemExit("Output must remain in the repository Graphify archive")
    cache = out / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    result = detect(
        root,
        extra_excludes=[
            "engineering/archive/**",
            "engineering/verification/**",
            "apps/chart/state/**",
            "apps/chart/node_modules/**",
            "apps/chart/dist/**",
        ],
        cache_root=cache,
    )
    safe_roots = ("apps/chart/", "engine/", "scripts/")
    excluded = ("apps/chart/state/", "apps/chart/node_modules/", "apps/chart/dist/")
    code = []
    for raw_path in result["files"].get("code", []):
        path = Path(raw_path).resolve()
        relative = path.relative_to(root).as_posix()
        if relative.startswith(safe_roots) and not relative.startswith(excluded):
            code.append(path)
    code.sort()
    if not code:
        raise SystemExit("No current code files were selected")
    ast = extract(code, cache_root=cache, root=root, parallel=False)
    (cache / "detect.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    (cache / "graphify_ast.json").write_text(json.dumps(ast, ensure_ascii=False), encoding="utf-8")
    summary = {
        "detected_supported_files": result["total_files"],
        "detected_code_files": len(result["files"].get("code", [])),
        "selected_current_code_files": len(code),
        "extracted_source_files": len(ast.get("extracted_sources", [])),
        "failed_sources": [str(x) for x in ast.get("failed_sources", [])],
        "ast_nodes": len(ast.get("nodes", [])),
        "ast_edges": len(ast.get("edges", [])),
        "skipped_sensitive": [Path(p).resolve().relative_to(root).as_posix() for p in result.get("skipped_sensitive", [])],
        "semantic_extraction": "NOT RUN; maintained Markdown receives structural link analysis only",
    }
    (cache / "extraction-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    if summary["failed_sources"] or summary["extracted_source_files"] != len(code):
        raise SystemExit("AST extraction was incomplete")


if __name__ == "__main__":
    main()
