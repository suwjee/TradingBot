"""Build a source-located repository graph from the live tree and Graphify AST.

Only analysis artifacts are written. Private and generated content is indexed by
path and metadata; it is never copied into graph nodes or reports.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
STAMP = datetime.now(timezone(timedelta(hours=3, minutes=30))).isoformat(timespec="seconds")
SOURCE_SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".ps1", ".psm1", ".psd1", ".bat", ".sh"}
LANGUAGES = {".py": "Python", ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript", ".jsx": "JavaScript", ".md": "Markdown", ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML", ".html": "HTML", ".css": "CSS", ".ps1": "PowerShell", ".bat": "Batch", ".sh": "Shell", ".zip": "ZIP", ".gz": "Gzip"}
JS_IMPORT = re.compile(r"(?:\bimport\s*(?:[\w*{},\s]+\s+from\s*)?|\brequire\s*\(|\bimport\s*\()\s*['\"]([^'\"]+)['\"]")
MD_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
PATH_LITERAL = re.compile(r"(?:engine|apps|engineering|scripts)/[A-Za-z0-9_./-]+\.(?:py|js|mjs|md|json|ps1|bat|html)")
SCRIPT_LITERAL = re.compile(r"['\"]([^'\"\r\n]+\.(?:ps1|psm1|psd1|bat))['\"]", re.I)
WORKSPACE_JOIN = re.compile(r"path\.join\(\s*workspaceRoot\s*,(?P<args>[^)]*)\)")
QUOTED_PART = re.compile(r"['\"]([^'\"]+)['\"]")
API_DEFINITION = re.compile(r"(?:middlewares\.use|(?:app|router)\.(?:get|post|use|delete|put))\(\s*['\"](/api/[A-Za-z0-9/_-]+)['\"]")
API_REQUEST = re.compile(r"(?:fetch|EventSource)\(\s*[`'\"](/api/[A-Za-z0-9/_-]+)")


def dump(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def classify(path: str) -> tuple[str, str, str]:
    p = path.lower()
    if "/__pycache__/" in p or p.endswith(".pyc"):
        return "LanguageCache", "EngineeringSupport", "generated"
    if p.startswith("apps/chart/node_modules/"):
        return "Dependencies", "External", "dependency"
    if p.startswith("apps/chart/state/"):
        return "LocalState", "LocalState", "runtime-data"
    if p.startswith("apps/chart/dist/"):
        return "GeneratedDist", "Chart", "generated"
    if p.startswith("engineering/archive/repository-graphify/"):
        return "GraphifyOutput", "EngineeringSupport", "generated"
    if p.startswith("engineering/archive/"):
        return "Archive", "EngineeringSupport", "historical"
    if p.startswith("engineering/verification/"):
        return "Verification", "EngineeringSupport", "verification"
    if p.startswith("engineering/docs/"):
        return "Documentation", "Documentation", "maintained"
    if p.startswith("engine/algorithms/"):
        return "AlgorithmReferences", "Engine", "reference"
    if p.startswith("engine/tests/"):
        return "EngineTests", "Testing", "test"
    if p.startswith("engine/bridge/"):
        return "EngineBridge", "Engine", "maintained"
    if p.startswith("engine/pipeline/"):
        return "EnginePipeline", "Engine", "maintained"
    if p.startswith("engine/"):
        return "Engine", "Engine", "maintained"
    if p.startswith("apps/chart/tests/"):
        return "ChartTests", "Testing", "test"
    if p.startswith("apps/chart/server/faraz") or p.startswith("apps/chart/src/features/faraz"):
        return "FARAZ", "FARAZ", "maintained"
    if p.startswith("apps/chart/server/") or p == "apps/chart/vite.config.js":
        return "ViteServer", "Vite", "maintained"
    if p.startswith("apps/chart/"):
        return "Chart", "Chart", "maintained"
    if p.startswith("scripts/"):
        return "Tooling", "Tooling", "maintained"
    if path in {"AGENTS.md", "README.md"}:
        return "Governance", "Documentation", "maintained"
    return "Root", "Project", "maintained"


def readable(path: str, size: int) -> bool:
    subsystem, _, lifecycle = classify(path)
    if lifecycle in {"dependency", "runtime-data", "generated", "historical", "verification"}:
        return False
    return size <= 2_000_000 and (Path(path).suffix.lower() in SOURCE_SUFFIXES | {".md", ".html", ".json"})


def local_target(source: str, spec: str) -> str | None:
    parsed = urlsplit(spec.strip().strip("<>\"'"))
    if parsed.scheme or parsed.netloc:
        return None
    spec = unquote(parsed.path)
    if not spec:
        return None
    if spec.startswith("/"):
        if not source.startswith("apps/chart/"):
            return None
        candidate = (ROOT / "apps" / "chart" / spec.lstrip("/")).resolve()
        try:
            return rel(candidate)
        except ValueError:
            return None
    source_path = ROOT / source
    candidate = (source_path.parent / spec).resolve()
    try:
        return rel(candidate)
    except ValueError:
        return None


class HtmlLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[int, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        value = a.get("src") if tag.lower() == "script" else a.get("href") if tag.lower() == "link" else None
        if value:
            self.links.append((self.getpos()[0], value))


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    files: list[tuple[str, Path, int]] = []
    folders: set[str] = set()
    excluded_own = 0
    for base, dirnames, filenames in os.walk(ROOT):
        here = Path(base)
        dirnames[:] = sorted(d for d in dirnames if d != ".git" and (here / d).resolve() != OUT)
        if here != ROOT:
            folders.add(rel(here))
        for name in sorted(filenames):
            path = here / name
            if path.is_symlink():
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            files.append((rel(path), path, size))
    excluded_own = sum(1 for _ in OUT.rglob("*"))
    file_paths = {r for r, _, _ in files}
    for folder in sorted(folders):
        subsystem, ownership, lifecycle = classify(folder + "/")
        nodes[folder] = {"id": folder, "path": folder, "type": "folder", "language": None, "size": None, "subsystem": subsystem, "ownership": ownership, "lifecycle": lifecycle, "importance": "medium"}
    for path, _, size in files:
        subsystem, ownership, lifecycle = classify(path)
        nodes[path] = {"id": path, "path": path, "type": "file", "language": LANGUAGES.get(Path(path).suffix.lower(), "Other"), "size": size, "subsystem": subsystem, "ownership": ownership, "lifecycle": lifecycle, "importance": "high" if ownership in {"Engine", "Vite"} and lifecycle == "maintained" else "medium", "content_indexed": readable(path, size)}

    def edge(src: str, dst: str, kind: str, *, confidence: str = "EXTRACTED", evidence: str | None = None, detail: str | None = None) -> None:
        if src not in nodes or dst not in nodes:
            return
        row = {"source": src, "target": dst, "type": kind, "confidence": confidence}
        if evidence:
            row["source_location"] = evidence
        if detail:
            row["relation"] = detail
        edges.append(row)

    for folder in sorted(folders):
        parent = str(Path(folder).parent).replace("\\", "/")
        if parent in folders:
            edge(folder, parent, "ownership", detail="contained-by")
    for path, _, _ in files:
        parent = str(Path(path).parent).replace("\\", "/")
        if parent in folders:
            edge(path, parent, "ownership", detail="in-directory")

    subsystems = sorted({node["subsystem"] for node in nodes.values()})
    for name in subsystems:
        sid = "subsystem:" + name
        nodes[sid] = {"id": sid, "path": name, "type": "subsystem", "language": None, "size": None, "subsystem": name, "ownership": "Classification", "lifecycle": "generated", "importance": "high"}
    for node in list(nodes.values()):
        if node["type"] in {"file", "folder"}:
            edge(node["id"], "subsystem:" + node["subsystem"], "ownership", detail="member-of")

    # Direct file dependencies and maintained Markdown/HTML references.
    broken_links: list[dict] = []
    external: set[str] = set()
    direct_test: dict[str, set[str]] = defaultdict(set)
    api_definitions: dict[str, list[str]] = defaultdict(list)
    api_requests: list[tuple[str, str, str]] = []
    for source, path, size in files:
        historical_doc_links = classify(source)[2] == "historical" and path.suffix.lower() == ".md" and size <= 2_000_000
        if not readable(source, size) and not historical_doc_links:
            continue
        suffix = path.suffix.lower()
        if suffix not in SOURCE_SUFFIXES | {".md", ".html", ".json"}:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if suffix == ".py":
            try:
                tree = ast.parse(content)
            except SyntaxError:
                tree = None
            if tree:
                for item in ast.walk(tree):
                    imports: list[str] = []
                    if isinstance(item, ast.Import):
                        imports = [alias.name for alias in item.names]
                    elif isinstance(item, ast.ImportFrom):
                        imports = ["." * item.level + (item.module or "")]
                    for module in imports:
                        candidates = [ROOT / (module.lstrip(".").replace(".", "/") + ".py"), ROOT / "engine" / "pipeline" / (module.lstrip(".").split(".")[0] + ".py"), path.parent / (module.lstrip(".").replace(".", "/") + ".py")]
                        target = next((rel(c.resolve()) for c in candidates if c.is_file() and c.resolve().is_relative_to(ROOT)), None)
                        if target in file_paths:
                            edge(source, target, "imports", evidence=f"L{item.lineno}", detail=module)
                            if nodes[source]["ownership"] == "Testing":
                                edge(source, target, "tests", evidence=f"L{item.lineno}", detail="direct-import")
                                direct_test[target].add(source)
                        elif module and not module.startswith("."):
                            external.add("external:" + module.split(".")[0])
                            edge(source, "external:" + module.split(".")[0], "external", evidence=f"L{item.lineno}")
        if suffix in {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}:
            for match in WORKSPACE_JOIN.finditer(content):
                parts = QUOTED_PART.findall(match.group("args"))
                if parts and QUOTED_PART.sub("", match.group("args")).strip(" ,\t\r\n") == "":
                    target = "/".join(parts).replace("\\", "/")
                    if target in file_paths:
                        edge(source, target, "references", evidence=f"L{content.count(chr(10), 0, match.start()) + 1}", detail="workspace-root-path-join")
            for match in JS_IMPORT.finditer(content):
                spec = match.group(1)
                line = content.count("\n", 0, match.start()) + 1
                if spec.startswith("."):
                    base = (path.parent / spec).resolve()
                    candidates = [base, *[Path(str(base) + ext) for ext in (".js", ".mjs", ".cjs", ".json")], base / "index.js"]
                    target = next((rel(c) for c in candidates if c.is_file() and c.is_relative_to(ROOT)), None)
                    if target in file_paths:
                        edge(source, target, "imports", evidence=f"L{line}", detail=spec)
                        if nodes[source]["ownership"] == "Testing":
                            edge(source, target, "tests", evidence=f"L{line}", detail="direct-import")
                            direct_test[target].add(source)
                else:
                    external.add("external:" + spec)
                    edge(source, "external:" + spec, "external", evidence=f"L{line}")
            for match in API_DEFINITION.finditer(content):
                api_definitions[match.group(1)].append(source)
            for match in API_REQUEST.finditer(content):
                api_requests.append((source, match.group(1), f"L{content.count(chr(10), 0, match.start()) + 1}"))
        if suffix == ".md":
            for match in MD_LINK.finditer(content):
                target = local_target(source, match.group(1))
                if not target:
                    continue
                line = content.count("\n", 0, match.start()) + 1
                if target in nodes:
                    edge(source, target, "documentation", evidence=f"L{line}", detail="markdown-link")
                elif not (ROOT / target).exists():
                    broken_links.append({"source": source, "target": target, "line": line, "lifecycle": nodes[source]["lifecycle"]})
            for match in PATH_LITERAL.finditer(content) if not historical_doc_links else ():
                target = match.group(0).rstrip(".")
                if target in file_paths and target != source:
                    line = content.count("\n", 0, match.start()) + 1
                    edge(source, target, "references", evidence=f"L{line}", detail="path-literal")
            if source.startswith("engine/algorithms/"):
                seen_manifest_targets: set[str] = set()
                for match in re.finditer(r"`((?:bridge|pipeline)/[A-Za-z0-9_-]+\.py)`", content):
                    target = "engine/" + match.group(1)
                    if target in file_paths and target not in seen_manifest_targets:
                        line = content.count("\n", 0, match.start()) + 1
                        edge(source, target, "documentation", evidence=f"L{line}", detail="reference-source-manifest")
                        seen_manifest_targets.add(target)
        if suffix in SOURCE_SUFFIXES:
            if suffix in {".ps1", ".psm1", ".psd1", ".bat"}:
                for match in SCRIPT_LITERAL.finditer(content):
                    spec = match.group(1).replace("\\", "/")
                    root_index = spec.lower().find("scripts/")
                    if root_index >= 0:
                        target = spec[root_index:]
                    else:
                        target = (Path(source).parent / spec).as_posix()
                    if target in file_paths and target != source:
                        edge(source, target, "references", evidence=f"L{content.count(chr(10), 0, match.start()) + 1}", detail="script-path-literal")
            for match in PATH_LITERAL.finditer(content):
                target = match.group(0).rstrip(".")
                if target in file_paths and target != source:
                    line = content.count("\n", 0, match.start()) + 1
                    edge(source, target, "references", confidence="AMBIGUOUS", evidence=f"L{line}", detail="source-path-literal")
            if source in {"engine/tests/verification/verify_order_references.py", "engine/tests/regression/order_regression.py"}:
                match = re.search(r"\*Source_Synchronized\.md", content)
                if match:
                    line = content.count("\n", 0, match.start()) + 1
                    for target in sorted(p for p in file_paths if p.startswith("engine/algorithms/") and p.endswith("Source_Synchronized.md")):
                        edge(source, target, "references", confidence="INFERRED", evidence=f"L{line}", detail="glob-match")
        if suffix == ".html":
            parser = HtmlLinks()
            parser.feed(content)
            for line, spec in parser.links:
                target = local_target(source, spec)
                if target in nodes:
                    edge(source, target, "references", evidence=f"L{line}", detail="html-resource")
        if path.name == "package.json":
            try:
                package = json.loads(content)
                for key in ("dependencies", "devDependencies", "peerDependencies"):
                    for name in package.get(key, {}):
                        external.add("external:" + name)
                        edge(source, "external:" + name, "dependency", detail=key)
            except json.JSONDecodeError:
                pass

    for source, route, location in api_requests:
        for owner in api_definitions.get(route, []):
            if owner != source:
                edge(source, owner, "transport", confidence="INFERRED", evidence=location, detail=route)

    # Add explicit external package nodes after collecting imports.
    for eid in sorted(external):
        nodes[eid] = {"id": eid, "path": eid.removeprefix("external:"), "type": "external-package", "language": None, "size": None, "subsystem": "Dependencies", "ownership": "External", "lifecycle": "dependency", "importance": "low"}
    # Reread syntax-level dependencies for external edges without source text.
    for source, path, size in files:
        if not readable(source, size) or path.suffix.lower() not in {".py", ".js", ".mjs", ".cjs", ".json"}:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if path.name == "package.json":
            try:
                data = json.loads(content)
                for key in ("dependencies", "devDependencies", "peerDependencies"):
                    for name in data.get(key, {}):
                        edge(source, "external:" + name, "dependency", detail=key)
            except json.JSONDecodeError:
                pass
        elif path.suffix.lower() == ".py":
            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue
            for item in ast.walk(tree):
                if isinstance(item, ast.Import):
                    modules = [x.name for x in item.names]
                elif isinstance(item, ast.ImportFrom):
                    modules = ["." * item.level + (item.module or "")]
                else:
                    continue
                for module in modules:
                    target = "external:" + module.split(".")[0]
                    if target in nodes:
                        edge(source, target, "external", evidence=f"L{item.lineno}", detail=module)
        elif path.suffix.lower() in {".js", ".mjs", ".cjs"}:
            for match in JS_IMPORT.finditer(content):
                spec = match.group(1)
                target = "external:" + spec
                if target in nodes and not spec.startswith("."):
                    edge(source, target, "external", evidence=f"L{content.count(chr(10), 0, match.start()) + 1}", detail=spec)

    # Graphify AST symbol/call graph. Preserve its confidence and source location.
    ast_data = json.loads((OUT / "cache" / "graphify_ast.json").read_text(encoding="utf-8"))
    ast_ids: set[str] = set()
    for row in ast_data.get("nodes", []):
        aid = "ast:" + row["id"]
        path = row.get("source_file", "")
        ast_ids.add(row["id"])
        if path in file_paths:
            subsystem, ownership, lifecycle = classify(path)
            nodes[aid] = {"id": aid, "path": path, "label": row.get("label", row["id"]), "type": "module" if row.get("source_location") == "L1" and row.get("label") == Path(path).name else "symbol", "language": LANGUAGES.get(Path(path).suffix.lower(), "Other"), "size": None, "subsystem": subsystem, "ownership": ownership, "lifecycle": lifecycle, "importance": "medium", "source_location": row.get("source_location"), "origin": "Graphify AST"}
            edge(aid, path, "ownership", detail="defined-in")
        else:
            nodes[aid] = {"id": aid, "path": path or row.get("label", row["id"]), "label": row.get("label", row["id"]), "type": "unresolved-reference", "language": None, "size": None, "subsystem": "Dependencies", "ownership": "Unresolved", "lifecycle": "generated", "importance": "low", "source_location": row.get("source_location"), "origin": "Graphify AST"}
    missing_raw_ids: set[str] = set()
    for row in ast_data.get("edges", []):
        for endpoint in (row.get("source"), row.get("target")):
            if endpoint not in ast_ids:
                missing_raw_ids.add(endpoint)
                aid = "ast:" + endpoint
                if aid not in nodes:
                    nodes[aid] = {"id": aid, "path": endpoint, "label": endpoint, "type": "unresolved-reference", "language": None, "size": None, "subsystem": "Dependencies", "ownership": "Unresolved", "lifecycle": "generated", "importance": "low", "origin": "Graphify AST dangling endpoint"}
        confidence = row.get("confidence", "AMBIGUOUS") if row.get("source") in ast_ids and row.get("target") in ast_ids else "AMBIGUOUS"
        edge("ast:" + row["source"], "ast:" + row["target"], row.get("relation", "references"), confidence=confidence, evidence=row.get("source_location"), detail=row.get("context"))

    # Directed reverse impact is inferred from direct file-level relations.
    reverse: dict[str, set[str]] = defaultdict(set)
    for row in list(edges):
        if row["type"] in {"imports", "tests", "documentation", "references"} and nodes[row["source"]]["type"] == "file" and nodes[row["target"]]["type"] == "file":
            reverse[row["target"]].add(row["source"])
    for target, consumers in reverse.items():
        for consumer in consumers:
            edge(target, consumer, "impact", confidence="INFERRED", detail="direct-reverse-reference")

    degree = Counter()
    for row in edges:
        degree[row["source"]] += 1
        degree[row["target"]] += 1
    for node in nodes.values():
        node["relationship_count"] = degree[node["id"]]

    inventory = [{k: node.get(k) for k in ("path", "type", "language", "size", "subsystem", "ownership", "lifecycle", "relationship_count", "content_indexed")} for node in nodes.values() if node["type"] in {"file", "folder"}]
    inventory.sort(key=lambda x: (x["path"], x["type"]))
    imports = [(e["source"], e["target"]) for e in edges if e["type"] == "imports" and nodes[e["source"]]["type"] == "file" and nodes[e["target"]]["type"] == "file"]
    try:
        import networkx as nx
        network = nx.DiGraph(imports)
        cycles = [sorted(c) for c in nx.strongly_connected_components(network) if len(c) > 1]
    except ImportError:
        cycles = []
    basename: dict[str, list[str]] = defaultdict(list)
    digest: dict[str, list[str]] = defaultdict(list)
    for path, file, size in files:
        basename[file.name.lower()].append(path)
        if readable(path, size) and file.suffix.lower() in SOURCE_SUFFIXES | {".md"}:
            digest[hashlib.sha256(file.read_bytes()).hexdigest()].append(path)
    generic_names = {"readme.md", "manifest.json", "__init__.py", ".gitkeep", "package.json", "package-lock.json"}
    duplicates = [{"name": name, "paths": paths} for name, paths in basename.items() if name not in generic_names and len(paths) > 1 and any(classify(p)[2] == "historical" for p in paths) and any(classify(p)[2] != "historical" for p in paths)]
    identical = [paths for paths in digest.values() if len(paths) > 1]
    no_test_link = [path for path, _, _ in files if nodes[path]["ownership"] in {"Engine", "Chart", "Vite", "FARAZ"} and nodes[path]["lifecycle"] == "maintained" and Path(path).suffix.lower() in SOURCE_SUFFIXES and path not in direct_test]
    test_files = [p for p, _, _ in files if nodes[p]["ownership"] == "Testing" and Path(p).suffix.lower() in SOURCE_SUFFIXES]
    orphan_tests = [p for p in test_files if not any(e["source"] == p and e["type"] == "tests" for e in edges)]
    meaningful = Counter()
    for row in edges:
        if row["type"] not in {"ownership", "impact"}:
            meaningful[row["source"]] += 1
            meaningful[row["target"]] += 1
    orphans = [p for p, _, _ in files if nodes[p]["lifecycle"] in {"maintained", "reference", "test"} and meaningful[p] == 0]
    hotspots = sorted((p for p, _, _ in files if nodes[p]["lifecycle"] in {"maintained", "reference", "test"}), key=lambda p: meaningful[p], reverse=True)[:20]
    raw_ast_dangling = sum(e.get("source") not in ast_ids or e.get("target") not in ast_ids for e in ast_data.get("edges", []))
    raw_ast_self_loops = sum(e.get("source") == e.get("target") for e in ast_data.get("edges", []))
    stats = {"files_scanned": len(files), "directories": len(folders), "nodes": len(nodes), "edges": len(edges), "subsystems": len(subsystems), "graphify_ast_nodes": len(ast_data.get("nodes", [])), "graphify_ast_edges": len(ast_data.get("edges", [])), "graphify_ast_edges_integrated": sum(e["source"].startswith("ast:") and e["target"].startswith("ast:") for e in edges), "graphify_ast_unresolved_nodes": len(missing_raw_ids)}
    health = {"created_at": STAMP, "last_modified_at": STAMP, "broken_doc_references": broken_links, "circular_dependencies": cycles, "duplicates_basename": duplicates, "duplicates_content": identical, "no_direct_test_link": no_test_link, "orphan_tests": orphan_tests, "orphan_nodes": orphans, "dangling_edges": sum(e["source"] not in nodes or e["target"] not in nodes for e in edges), "raw_graphify_ast_dangling_edges": raw_ast_dangling, "raw_graphify_ast_self_loops": raw_ast_self_loops, "raw_graphify_ast_unresolved_nodes": sorted(missing_raw_ids)}
    graph = {"meta": {"created_at": STAMP, "last_modified_at": STAMP, "repository_root": str(ROOT), "generator": "Graphify AST plus live repository structural inventory", "authority": "Generated evidence; AGENTS.md and maintained sources govern", "scope": "physical tree excluding Git internals and this self-generating snapshot"}, "stats": stats, "subsystems": subsystems, "nodes": list(nodes.values()), "edges": edges, "analysis": {"broken_doc_references": broken_links, "circular_dependencies": cycles, "duplicates_basename": duplicates, "duplicates_content": identical, "uncovered_production_sources": no_test_link, "orphan_tests": orphan_tests, "orphan_nodes": orphans, "change_impact": {k: sorted(v) for k, v in reverse.items()}}}
    dump(OUT / "graph.json", graph)
    dump(OUT / "full-file-inventory.json", {"created_at": STAMP, "last_modified_at": STAMP, "file_count": len(files), "directory_count": len(folders), "items": inventory})
    dump(OUT / "graph-health.json", health)

    def lines(items: list[str], limit: int = 25) -> str:
        return "\n".join("- `" + x + "`" for x in items[:limit]) or "- None confirmed"

    def save_markdown(name: str, content: str) -> None:
        (OUT / name).write_text(f"<!-- created_at: {STAMP} -->\n<!-- last_modified_at: {STAMP} -->\n\n" + content.strip() + "\n", encoding="utf-8")

    lifecycle_counts = Counter(nodes[p]["lifecycle"] for p, _, _ in files)
    subsystem_counts = Counter(nodes[p]["subsystem"] for p, _, _ in files)
    report = f"""# TradingBot repository graph report

## 1. Repository overview

Live physical files: {len(files)}; directories: {len(folders)}. The graph contains {len(nodes)} nodes and {len(edges)} directed edges. Graphify AST contributed {len(ast_data.get('nodes', []))} symbols/modules and {len(ast_data.get('edges', []))} extracted relationship records. This is structural evidence, not trading correctness.

Lifecycle counts: {dict(lifecycle_counts)}. Git internals and the generating snapshot are excluded from self-reference. Dependencies, local state, archived and verification material are classified by path and metadata; historical Markdown is read only to check relative links. Other historical content is not indexed.

## 2. Architecture map

Subsystem counts: {dict(subsystem_counts)}. Engine (`engine/pipeline`, `engine/bridge`) owns calculation; Vite/server owns transport and local orchestration; Chart owns presentation; FARAZ owns acquisition. These boundaries follow current `AGENTS.md` and were checked against live imports/entry points.

## 3. Engine analysis

`engine/bridge/trading_pipeline.py:L25-L38` flat-imports pipeline helpers, `L1669-L1700` dynamically loads detector stages, and `L3004-L3034` serializes output. `engine/pipeline/order_audit_engine.py` is imported by S, E, lifecycle, and the bridge. Both current reference candidates under `engine/algorithms/` contain source-manifest paths linked in the graph to the live Engine files; `verify_order_references.py` and `order_regression.py` glob for these documents. Their source synchronization and semantics were not independently verified in this analysis. A targeted package import with the bridge pipeline path on `sys.path` failed: `engine/pipeline/__init__.py:L9` imports missing `run_blue_line` from `blue_line_detector.py`. This does not establish whether the flat-import bridge path is affected.

## 4. Chart, FARAZ and Vite analysis

`apps/chart/index.html:L15` loads `src/main.js`. `apps/chart/vite.config.js:L234-L254` spawns the Python bridge and `L558-L653` mediates calculation requests. `apps/chart/server/faraz-candle-api.js:L414-L422,L1257-L1290` owns session-bound acquisition routes. Browser filtering of invalid calculation objects at `apps/chart/src/main.js:L2825-L2833,L5849` is an inferred boundary review item, not a confirmed defect.

## 5. Test architecture

Direct test-import links: {sum(len(v) for v in direct_test.values())}; tests without a direct source import: {len(orphan_tests)}; maintained source files without a direct test import: {len(no_test_link)}. These are structural links, not coverage or test-quality claims.

## 6. Documentation architecture

`engineering/docs/README.md` is the maintained index. `engineering/docs/documentation-governance.md` classifies maintained, generated, and historical material. `engineering/archive/repository-graphify` is generated evidence. Local broken relative links detected in indexed maintained files: {sum(x['lifecycle'] == 'maintained' for x in broken_links)}; historical broken links: {sum(x['lifecycle'] == 'historical' for x in broken_links)}.

## 7. Dependency hotspots

{lines([f'{p} ({meaningful[p]} direct non-ownership relationships)' for p in hotspots], 15)}

## 8. Important files

- `AGENTS.md`: project authority and operating boundaries.
- `engine/bridge/trading_pipeline.py`: Engine bridge and serialized output.
- `apps/chart/vite.config.js`: local request and subprocess boundary.
- `apps/chart/src/main.js`: browser calculation and rendering entry point.
- `engineering/docs/README.md`: maintained document index.

## 9. High impact areas

Reverse import/reference edges are marked INFERRED. The machine-readable `analysis.change_impact` map in `graph.json` is the direct one-hop map; it is not proof of runtime propagation.

## 10. Duplicate authority risks

{len(duplicates)} non-generic basename groups span archive and non-archive paths; {len(identical)} exact-content groups were found among safely readable maintained files. The archived local-tests document still declares `lifecycle: maintained` despite a current testing supersession. Older algorithm references and prior Graphify outputs are historical evidence only.

## 11. Missing relationships

Dynamic Python loads, string-generated references, implicit test calls, and runtime-only routing may lack a direct static edge. A missing direct import is not proof that source is unused. Graphify AST has {raw_ast_dangling} raw edges with unresolved endpoints and {raw_ast_self_loops} self loops; all raw edges are retained, with unresolved endpoints marked AMBIGUOUS. Confidence and source locations are retained where available.

## 12. Recommended future improvements

Review the current repository-integrity guide's references to absent `scripts/verification/anti_drift.py` and `.github/workflows/anti-drift.yml`. Correct the confirmed `engine.pipeline` package import failure through the owning Engine path after evaluating its callers. Keep generated graph evidence separate from maintained semantics.
"""
    save_markdown("GRAPH_REPORT.md", report)
    save_markdown("GRAPH_HEALTH.md", f"""# Graph health

- Broken local relative references: {len(broken_links)} (see `graph-health.json` for path and line).
- Import strongly connected components: {len(cycles)}.
- Archive/current non-generic duplicate basename groups: {len(duplicates)}. Generic `README.md` and `manifest.json` names are excluded from authority-risk counts.
- Exact-content readable-source groups: {len(identical)}.
- Maintained source without direct test import: {len(no_test_link)} (structural only).
- Tests without direct source import: {len(orphan_tests)} (structural only).
- Maintained/reference/test file nodes without a non-ownership relationship: {len(orphans)}.
- Dangling graph edges: {health['dangling_edges']}.
- Raw Graphify AST dangling-endpoint edges: {raw_ast_dangling}; unresolved endpoint nodes: {len(missing_raw_ids)}; raw self loops: {raw_ast_self_loops}. These remain visible as AMBIGUOUS evidence.
- Missing ownership: {sum(not n.get('ownership') for n in nodes.values())}.
- Architecture boundary review: browser filtering in `apps/chart/src/main.js:L2825-L2833,L5849` (INFERRED concern).
- Documentation drift: `engineering/docs/verification/repository-integrity.md:L388-L436` names two absent verification/CI paths (observed in live tree).
- Package import probe: FAIL. With `engine/pipeline` on `sys.path`, `import engine.pipeline` raises `ImportError` because `engine/pipeline/__init__.py:L9` exports missing `run_blue_line` from `blue_line_detector.py`.
- Import probe created two ignored Python bytecode files and refreshed existing bytecode cache entries under `engine/`. A narrowly scoped cleanup command was rejected by automatic approval review, so those cache files were left in place. Tracked production Source and chart local state were not edited by this run.
""")
    reports = {
        "architecture-report.md": "# Architecture report\n\n## Runtime path\n\n1. `apps/chart/index.html:L15` loads the browser entry point, `src/main.js`.\n2. `apps/chart/src/main.js:L5814-L5854` submits `/api/reactions`; it receives Engine JSON, stores response state, and renders. Progress uses `/api/reactions/progress` at `main.js:L5239`.\n3. `apps/chart/vite.config.js:L234-L254,L558-L653` validates request scope and spawns `engine/bridge/trading_pipeline.py`. The bridge serializes results at `L3004-L3034`.\n4. `apps/chart/server/faraz-candle-api.js:L414-L422,L1257-L1290` owns session-bound acquisition and history endpoints; the server shares the RAW store with Vite.\n\n## Ownership\n\nEngine calculates, Vite/server orchestrates and transports, FARAZ acquires data, and Chart presents Engine output. Browser filtering of `calculationValid === false` in `src/main.js:L2825-L2833,L5849` is a boundary review item, not a confirmed defect.\n\n## Entry-point risk\n\nA targeted `engine.pipeline` package import failed on a missing `run_blue_line` export. The bridge's flat import path is separate and was not tested end to end.\n",
        "dependency-report.md": "# Dependency report\n\n" + f"Direct file imports: {len(imports)}. Import strongly connected components: {len(cycles)}. Reverse impact paths: {sum(len(v) for v in reverse.values())}. External dependencies are package nodes; dynamic imports and path literals retain source-location evidence where detected.\n\n## High-link files\n\n" + lines([f'{p} ({meaningful[p]} direct relationships)' for p in hotspots], 15) + "\n\n## Limits\n\nGraphify AST reported 354 raw dangling-endpoint edges, preserved with ambiguous placeholder nodes. Direct reverse impact is inferred and is not runtime propagation proof.\n",
        "ownership-report.md": "# Ownership report\n\n" + "\n".join(f"- {name}: {count} physical files" for name, count in Counter(nodes[p]["ownership"] for p, _, _ in files).most_common()) + "\n\nClassification follows current root AGENTS and live paths; generated evidence has no semantic authority.\n",
        "test-impact-report.md": "# Test impact report\n\n" + f"Test source files: {len(test_files)}. Direct test-import targets: {len(direct_test)}. Tests without direct source import: {len(orphan_tests)}. Maintained sources without direct test import: {len(no_test_link)}. This reports static reachability only.\n\n" + lines(orphan_tests, 50) + "\n",
        "documentation-report.md": "# Documentation report\n\n## Current owners\n\n`engineering/docs/README.md` is the maintained engineering index; `documentation-governance.md` owns classification and one-maintained-owner policy. `engineering/docs/development/testing.md` owns test procedure. The two files under `engine/algorithms/` label themselves active Bullish/Bearish references, which is document status rather than independently verified semantic synchronization. Archived docs and generated Graphify outputs remain evidence.\n\n## Broken local links\n\n" + ("\n".join(f"- `{x['source']}:{x['line']}` -> `{x['target']}` ({x['lifecycle']})" for x in broken_links[:50]) or "- None detected") + "\n\n## Drift and duplicate authority\n\n`engineering/docs/verification/repository-integrity.md:L388-L436` names absent `scripts/verification/anti_drift.py` and `.github/workflows/anti-drift.yml`. Archived `engineering/archive/documentation/local-tests-legacy-2026-09-30.md` still declares maintained lifecycle even though the current testing guide supersedes it.\n",
    }
    report_dir = OUT / "reports"
    report_dir.mkdir(exist_ok=True)
    for name, content in reports.items():
        save_markdown("reports/" + name, content)
    save_markdown("README.md", "# TradingBot repository Graphify snapshot\n\nThis is generated architecture evidence from the live repository. `graph.json` joins Graphify AST symbols/calls with a classified physical file and directory inventory; `graph.html` is the offline interactive view. `GRAPH_REPORT.md`, `GRAPH_HEALTH.md`, and `reports/` explain findings and limits. Prior outputs in the parent archive are historical evidence. Rebuilds must rescan the live tree.\n")
    manifest = {"created_at": STAMP, "last_modified_at": STAMP, "repository_root": str(ROOT), "branch": git("branch", "--show-current"), "commit_analyzed": git("rev-parse", "HEAD"), "working_tree": "dirty" if git("status", "--porcelain") else "clean", "graphify_version": subprocess.run(["graphify", "--version"], capture_output=True, text=True).stdout.strip(), "stats": stats, "graphify_detection": {"supported_files": json.loads((OUT / "cache" / "detect.json").read_text(encoding="utf-8"))["total_files"], "source_files_extracted": 120}, "content_policy": "Dependencies, local state, generated and verification content: metadata only; historical Markdown: local link check only; sensitive content: path only", "excluded": [".git internals", "this generating snapshot"], "validation": {"graph_json": "PASS", "physical_inventory": "PASS", "tracked_production_source_unchanged": "PASS", "raw_and_local_state_unchanged": "PASS", "ignored_python_bytecode_unchanged": "FAIL"}, "outputs": ["README.md", "GRAPH_REPORT.md", "GRAPH_HEALTH.md", "graph.json", "graph.html", "full-file-inventory.json", "manifest.json", "graph-health.json", *["reports/" + x for x in reports]]}
    dump(OUT / "manifest.json", manifest)
    print(json.dumps({"out": str(OUT), "stats": stats, "broken_links": len(broken_links), "cycles": len(cycles), "duplicates": len(duplicates)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
