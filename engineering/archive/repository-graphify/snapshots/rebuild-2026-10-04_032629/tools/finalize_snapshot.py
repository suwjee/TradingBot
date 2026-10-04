"""Replace historical template prose with findings from this Graphify rebuild."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def markdown(path: Path, body: str, created: str, modified: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"<!-- created_at: {created} -->\n<!-- last_modified_at: {modified} -->\n\n"
        + body.strip() + "\n",
        encoding="utf-8",
    )


def bullets(items: list[str], limit: int = 12) -> str:
    return "\n".join(f"- `{item}`" for item in items[:limit]) or "- None observed"


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    if not out.is_relative_to(root / "engineering" / "archive" / "repository-graphify"):
        raise SystemExit("Output must remain in the repository Graphify archive")
    graph = read_json(out / "graph.json")
    inventory = read_json(out / "full-file-inventory.json")
    health = read_json(out / "graph-health.json")
    extraction = read_json(out / "cache" / "extraction-summary.json")
    created = graph["meta"]["created_at"]
    modified = datetime.now(timezone(timedelta(hours=3, minutes=30))).isoformat(timespec="seconds")
    nodes = graph["nodes"]
    edges = graph["edges"]
    ids = {node["id"] for node in nodes}
    file_nodes = {node["path"] for node in nodes if node["type"] == "file"}
    inventory_files = {item["path"] for item in inventory["items"] if item["type"] == "file"}
    physical_files: set[str] = set()
    for base, dirs, names in os.walk(root):
        here = Path(base)
        dirs[:] = [d for d in dirs if d != ".git" and (here / d).resolve() != out]
        for name in names:
            path = here / name
            if path.is_file() and not path.is_symlink():
                physical_files.add(path.relative_to(root).as_posix())
    bad_edges = [e for e in edges if e["source"] not in ids or e["target"] not in ids]
    ast_edges = [e for e in edges if e["source"].startswith("ast:") and e["target"].startswith("ast:")]
    status_lines = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=root, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    archive_prefix = "engineering/archive/repository-graphify/"
    unrelated_changes = [line for line in status_lines if not line[3:].replace("\\", "/").startswith(archive_prefix)]
    confidence = Counter(e.get("confidence", "UNLABELED") for e in edges)
    lifecycle = Counter(item["lifecycle"] for item in inventory["items"] if item["type"] == "file")
    subsystem = Counter(item["subsystem"] for item in inventory["items"] if item["type"] == "file")
    kind = Counter(e["type"] for e in edges)
    non_ownership = Counter()
    for edge in edges:
        if edge["type"] not in {"ownership", "impact"}:
            if edge["source"] in file_nodes:
                non_ownership[edge["source"]] += 1
            if edge["target"] in file_nodes:
                non_ownership[edge["target"]] += 1
    top_files = [f"{path} ({count} direct links)" for path, count in non_ownership.most_common(12)]
    broken = health["broken_doc_references"]
    current_broken = [x for x in broken if x["lifecycle"] == "maintained"]
    historical_broken = [x for x in broken if x["lifecycle"] == "historical"]
    check = {
        "physical_file_parity": "PASS" if file_nodes == inventory_files == physical_files else "FAIL",
        "edge_endpoints": "PASS" if not bad_edges else "FAIL",
        "ast_edge_integration": "PASS" if len(ast_edges) == extraction["ast_edges"] else "FAIL",
        "ast_source_completion": "PASS" if not extraction["failed_sources"] and extraction["selected_current_code_files"] == extraction["extracted_source_files"] else "FAIL",
        "sensitive_css_content_excluded": "PASS" if all(not n.get("content_indexed", False) for n in nodes if n.get("path") in extraction["skipped_sensitive"]) else "FAIL",
        "working_tree_outside_archive": "PASS" if not unrelated_changes else "FAIL",
        "semantic_extraction": "NOT RUN",
        "runtime_or_trading_tests": "NOT RUN",
    }
    if any(check[k] != "PASS" for k in ("physical_file_parity", "edge_endpoints", "ast_edge_integration", "ast_source_completion", "sensitive_css_content_excluded", "working_tree_outside_archive")):
        raise SystemExit(f"Snapshot validation failed: {check}")
    sections = [
        "# TradingBot repository graph report",
        "## Scope",
        f"The live tree contains {graph['stats']['files_scanned']} physical files and {graph['stats']['directories']} directories outside Git internals and this generating snapshot. The directed graph has {len(nodes)} nodes and {len(edges)} edges across {len(graph['subsystems'])} classified subsystems. Graphify 0.9.63 extracted {extraction['ast_nodes']} nodes and {extraction['ast_edges']} edges from {extraction['extracted_source_files']} current code files. Historical, generated, dependency, verification, and local-state content is represented by path and metadata only; historical Markdown receives local-link checks. The source code extraction and structural documentation links do not establish trading correctness.",
        "## Relationships",
        "\n".join(f"- {name}: {count}" for name, count in kind.most_common(12)),
        "Graphify AST calls and reverse impact edges retain their confidence labels. Inferred edges are navigation hints; direct Source is required for important dependency decisions.",
        "## Main subsystems",
        "\n".join(f"- {name}: {count} physical files" for name, count in subsystem.most_common()),
        "## High-link files",
        bullets(top_files),
        "## Test and documentation signals",
        f"Static analysis found {len(health['no_direct_test_link'])} maintained source files without a direct test import and {len(health['orphan_tests'])} test source files without a direct source import. These are structural signals, not test coverage. It found {len(current_broken)} broken local links in maintained documents and {len(historical_broken)} in historical documents.",
        "## Extraction and interpretation limits",
        f"AST extraction completed for all {extraction['selected_current_code_files']} selected current code files. Semantic LLM extraction of documents was not run; document relationships are local links, explicit path references, and source manifest references. The raw AST has {health['raw_graphify_ast_dangling_edges']} unresolved-endpoint edges and {health['raw_graphify_ast_self_loops']} self loops. Unresolved endpoints remain as AMBIGUOUS nodes in the final graph. Full physical inventory coverage does not mean full content analysis.",
        "## Verification",
        "\n".join(f"- {name}: {result}" for name, result in check.items()),
    ]
    markdown(out / "GRAPH_REPORT.md", "\n\n".join(sections), created, modified)
    health_lines = [
        "# Graph health",
        f"- Final dangling edge endpoints: {len(bad_edges)}.",
        f"- Physical file inventory parity: {check['physical_file_parity']}.",
        f"- AST edge integration: {len(ast_edges)} / {extraction['ast_edges']} ({check['ast_edge_integration']}).",
        f"- Raw unresolved AST endpoint edges: {health['raw_graphify_ast_dangling_edges']}; explicit unresolved nodes: {len(health['raw_graphify_ast_unresolved_nodes'])}.",
        f"- Raw AST self loops: {health['raw_graphify_ast_self_loops']}.",
        f"- Broken local document references: {len(current_broken)} maintained, {len(historical_broken)} historical.",
        f"- Import cycles found by direct-file static analysis: {len(health['circular_dependencies'])}.",
        f"- Edge confidence counts: {dict(confidence)}.",
        "- Semantic document extraction: NOT RUN. Runtime and trading tests: NOT RUN.",
    ]
    markdown(out / "GRAPH_HEALTH.md", "\n".join(health_lines), created, modified)
    report_dir = out / "reports"
    markdown(report_dir / "architecture-report.md", "# Architecture map\n\n" + "\n".join(f"- {name}: {count} physical files" for name, count in subsystem.most_common()) + "\n\nThese are path classifications. Validate runtime relationships against current Source.", created, modified)
    markdown(report_dir / "dependency-report.md", "# Dependency report\n\n" + f"Direct file imports: {kind['imports']}. Reverse impact edges: {kind['impact']} (INFERRED).\n\n## High-link files\n\n" + bullets(top_files) + "\n\nAST call edges may be inferred and raw unresolved endpoints are preserved as ambiguous nodes.", created, modified)
    markdown(report_dir / "ownership-report.md", "# Ownership report\n\n" + "\n".join(f"- {name}: {count} physical files" for name, count in lifecycle.most_common()) + "\n\nGraphify output is generated evidence, not semantic authority.", created, modified)
    markdown(report_dir / "test-impact-report.md", "# Test impact report\n\n" + f"Maintained source files without a direct test import: {len(health['no_direct_test_link'])}. Tests without a direct source import: {len(health['orphan_tests'])}.\n\n## Tests lacking a direct source import\n\n" + bullets(health["orphan_tests"], 50) + "\n\nNo test suite was run for this graph rebuild.", created, modified)
    markdown(report_dir / "documentation-report.md", "# Documentation report\n\n" + f"Broken maintained links: {len(current_broken)}; broken historical links: {len(historical_broken)}.\n\n" + "\n".join(f"- `{row['source']}:{row['line']}` -> `{row['target']}` ({row['lifecycle']})" for row in broken) + "\n\nHistorical links are preserved as evidence; document semantics were not extracted by an LLM.", created, modified)
    markdown(out / "README.md", "# TradingBot Graphify snapshot\n\nThis dated snapshot was rebuilt from the live repository. `graph.json` and `graph.html` contain a directed, navigable graph; `GRAPH_REPORT.md`, `GRAPH_HEALTH.md`, `graph-health.json`, `full-file-inventory.json`, and `reports/` record scope and limits. The `tools/` scripts reproduce extraction, structural graph construction, HTML export, and final reporting in that order. Run them with Graphify 0.9.63 and Python bytecode disabled. The scripts exclude this snapshot from the input inventory. Generated edges are navigation evidence only; the current Source and governed trading knowledge remain authoritative.", created, modified)
    subprocess.run([sys.executable, "-B", str(out / "tools" / "build_graph_html.py"), str(out)], check=True)
    html = (out / "graph.html").read_text(encoding="utf-8")
    if "<html" not in html.lower() or "</html>" not in html.lower() or "TradingBot Repository Graphify" not in html:
        raise SystemExit("HTML export smoke check failed")
    secret_patterns = {
        "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
        "jwt_like": re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
        "credential_assignment": re.compile(r"(?i)(?:api[_-]?key|password|access[_-]?token)\s*[:=]\s*[\"'][^\"']{8,}"),
    }
    scan_paths = [out / "graph.json", out / "graph.html", out / "GRAPH_REPORT.md", out / "GRAPH_HEALTH.md", *(report_dir.glob("*.md"))]
    findings = {name: [p.name for p in scan_paths if pattern.search(p.read_text(encoding="utf-8"))] for name, pattern in secret_patterns.items()}
    if any(findings.values()):
        raise SystemExit(f"Sensitive-pattern scan requires review: {findings}")
    check["html_export"] = "PASS"
    check["sensitive_pattern_scan"] = "PASS"
    outputs = [p for p in out.rglob("*") if p.is_file() and "cache" not in p.relative_to(out).parts and p.name != "manifest.json"]
    manifest = {
        "created_at": created,
        "last_modified_at": modified,
        "repository_root": str(root),
        "commit_analyzed": subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout.strip(),
        "graphify_version": subprocess.run(["graphify", "--version"], capture_output=True, text=True, check=True).stdout.strip(),
        "stats": graph["stats"],
        "extraction": extraction,
        "validation": check,
        "excluded_from_content_extraction": ["archive", "verification", "dependencies", "local state", "generated output"],
        "outputs": [{"path": p.relative_to(out).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(outputs)],
    }
    write_json(out / "manifest.json", manifest)
    print(json.dumps({"stats": graph["stats"], "validation": check, "outputs": len(outputs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
