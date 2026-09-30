"""Rebuild the TradingBot source graph while keeping private data out of outputs."""

from __future__ import annotations

import collections
import hashlib
import json
import re
import subprocess
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from graphify.analyze import god_nodes, suggest_questions, surprising_connections
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.detect import detect
from graphify.diagnostics import diagnose_extraction, format_diagnostic_report
from graphify.export import generate_html, to_json
from graphify.extract import extract
from graphify.report import generate


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs" / "graphify" / "rebuild-2026-09-23"
RAW_DIR = OUTPUT / "raw-run"
GRAPHIFY_VERSION = "0.9.63"
GRAPHIFYY_VERSION = "0.9.42"


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def file_slug(relative_path: str) -> str:
    stem = PurePosixPath(relative_path).with_suffix("").as_posix()
    return re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_").lower()


class HtmlReferences(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[int, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        value = attributes.get("src") if tag.lower() == "script" else None
        if tag.lower() == "link":
            value = attributes.get("href")
        if value:
            self.references.append((self.getpos()[0], value))


def title_words(value: str) -> list[str]:
    value = re.sub(r"([a-z])([A-Z])", r"\1 \2", value)
    return [word.capitalize() for word in re.split(r"[^A-Za-z0-9]+", value) if word]


def main() -> None:
    ROOT.mkdir(exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    detect_result = detect(ROOT, extra_excludes=["docs/graphify/**"])
    categories = detect_result["files"]
    source_paths = [Path(path) for path in categories.get("code", [])]
    markdown_paths = [Path(path) for path in categories.get("document", []) if Path(path).suffix.lower() == ".md"]
    raw = extract(source_paths + markdown_paths, cache_root=ROOT, root=ROOT, parallel=False)
    write_json(RAW_DIR / ".graphify_detect.json", detect_result)
    write_json(RAW_DIR / ".graphify_extract_raw.json", raw)

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    built_at = datetime.now().astimezone().isoformat(timespec="seconds")
    raw_health = diagnose_extraction(raw, directed=True, root=ROOT)

    nodes = list(raw.get("nodes", []))
    edges = list(raw.get("edges", []))
    node_by_id = {node["id"]: node for node in nodes}
    file_node_by_path: dict[str, str] = {}
    for node in nodes:
        source_file = node.get("source_file")
        if source_file and node.get("label") == PurePosixPath(source_file).name and node.get("source_location") == "L1":
            file_node_by_path[source_file.replace("\\", "/")] = node["id"]

    def add_file_node(
        relative_path: str,
        file_type: str,
        *,
        source_kind: str,
        sensitive: bool = False,
    ) -> str:
        relative_path = PurePosixPath(relative_path).as_posix()
        if relative_path in file_node_by_path:
            return file_node_by_path[relative_path]
        node_id = file_slug(relative_path)
        if node_id in node_by_id:
            raise RuntimeError(f"file-node id collision for {relative_path}: {node_id}")
        node = {
            "id": node_id,
            "label": PurePosixPath(relative_path).name,
            "file_type": file_type,
            "source_file": relative_path,
            "source_location": "L1",
            "_origin": "graphify_scope_index",
            "node_kind": "file",
            "source_kind": source_kind,
        }
        if sensitive:
            node.update(
                {
                    "sensitivity": "detector-classified; content intentionally omitted",
                    "content_indexed": False,
                }
            )
        nodes.append(node)
        node_by_id[node_id] = node
        file_node_by_path[relative_path] = node_id
        return node_id

    # Include detector-unclassified files and detector-sensitive CSS as path-only nodes.
    for absolute_path in detect_result.get("unclassified", []):
        relative_path = Path(absolute_path).resolve().relative_to(ROOT).as_posix()
        suffix = Path(relative_path).suffix.lower()
        kind = "code" if suffix in {".css", ".bat"} else "document"
        add_file_node(relative_path, kind, source_kind="unclassified-path-only")
    for absolute_path in detect_result.get("skipped_sensitive", []):
        relative_path = Path(absolute_path).resolve().relative_to(ROOT).as_posix()
        add_file_node(relative_path, "code", source_kind="sensitive-path-only", sensitive=True)

    # Safely index CSS custom-property names only. Values never enter graph nodes or outputs.
    sensitive_css_path = "apps/chart/src/styles/tokens.css"
    sensitive_css_text = (ROOT / sensitive_css_path).read_text(encoding="utf-8", errors="replace")
    property_pattern = re.compile(r"(--[A-Za-z0-9_-]+)\s*:")
    redacted_css = property_pattern.sub("[CSS_PROPERTY]:", sensitive_css_text)
    risk_flags = {
        "private_key_marker": bool(re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", redacted_css, re.I)),
        "jwt_like_value": bool(re.search(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}", redacted_css)),
        "credential_assignment": bool(
            re.search(
                r"(?i)(?:api[_-]?key|password|secret|access[_-]?token)\s*[:=]\s*[\"'][^\"']{8,}",
                redacted_css,
            )
        ),
        "long_high_entropy_literals": sum(
            1
            for value in re.findall(r"[A-Za-z0-9+/=_-]{32,}", redacted_css)
            if len(set(value)) > 15
        ),
    }
    safe_css_identifiers: list[tuple[str, int]] = []
    if not any(risk_flags.values()):
        for line_number, line in enumerate(sensitive_css_text.splitlines(), 1):
            safe_css_identifiers.extend((match.group(1), line_number) for match in property_pattern.finditer(line))
    sensitive_file_id = file_node_by_path.get(sensitive_css_path)
    for identifier, line_number in safe_css_identifiers:
        identifier_id = f"{sensitive_file_id}__property_{file_slug(identifier)}"
        if identifier_id not in node_by_id:
            property_node = {
                "id": identifier_id,
                "label": identifier,
                "file_type": "code",
                "source_file": sensitive_css_path,
                "source_location": f"L{line_number}",
                "identifier_only": True,
                "value_indexed": False,
                "_origin": "redacted_css_identifier",
            }
            nodes.append(property_node)
            node_by_id[identifier_id] = property_node
        edges.append(
            {
                "source": sensitive_file_id,
                "target": identifier_id,
                "relation": "contains",
                "confidence": "EXTRACTED",
                "source_file": sensitive_css_path,
                "source_location": f"L{line_number}",
                "weight": 1.0,
                "_origin": "redacted_css_identifier",
            }
        )
    if sensitive_file_id:
        node_by_id[sensitive_file_id]["safe_identifiers_indexed"] = bool(safe_css_identifiers)
        node_by_id[sensitive_file_id]["values_indexed"] = False

    # HTML contributes its entry-point node and literal local script/style links only.
    html_paths = [
        Path(path).resolve().relative_to(ROOT).as_posix()
        for path in categories.get("document", [])
        if Path(path).suffix.lower() == ".html"
    ]
    html_edges: list[dict] = []
    for relative_path in html_paths:
        source_id = add_file_node(relative_path, "document", source_kind="html-entrypoint")
        parser = HtmlReferences()
        parser.feed((ROOT / relative_path).read_text(encoding="utf-8", errors="replace"))
        for line_number, raw_url in parser.references:
            url = urlsplit(raw_url)
            if url.scheme or url.netloc or not url.path:
                continue
            target = unquote(url.path).lstrip("/")
            if target.startswith("src/"):
                target = "apps/chart/" + target
            else:
                target = (PurePosixPath(relative_path).parent / target).as_posix()
            target = PurePosixPath(target).as_posix()
            target_id = file_node_by_path.get(target)
            if target_id:
                html_edges.append(
                    {
                        "source": source_id,
                        "target": target_id,
                        "relation": "references",
                        "confidence": "EXTRACTED",
                        "source_file": relative_path,
                        "source_location": f"L{line_number}",
                        "weight": 1.0,
                        "_origin": "literal_html_reference",
                    }
                )

    # Known direct import targets that were unresolved by the AST resolver.
    external_modules = {
        "argparse": ("Python stdlib: argparse", "argparse", "python-stdlib"),
        "array": ("Python stdlib: array", "array", "python-stdlib"),
        "bisect": ("Python stdlib: bisect", "bisect", "python-stdlib"),
        "dataclasses": ("Python stdlib: dataclasses", "dataclasses", "python-stdlib"),
        "decimal": ("Python stdlib: decimal", "decimal", "python-stdlib"),
        "importlib_util": ("Python stdlib: importlib.util", "importlib.util", "python-stdlib"),
        "json": ("Python stdlib: json", "json", "python-stdlib"),
        "orjson": ("Python package: orjson", "orjson", "python-package"),
        "pathlib": ("Python stdlib: pathlib", "pathlib", "python-stdlib"),
        "sys": ("Python stdlib: sys", "sys", "python-stdlib"),
        "time": ("Python stdlib: time", "time", "python-stdlib"),
        "types": ("Python stdlib: types", "types", "python-stdlib"),
        "typing": ("Python stdlib: typing", "typing", "python-stdlib"),
        "unittest": ("Python stdlib: unittest", "unittest", "python-stdlib"),
        "zoneinfo": ("Python stdlib: zoneinfo", "zoneinfo", "python-stdlib"),
        "ref_lightweight_charts": ("npm package: lightweight-charts", "lightweight-charts", "npm-package"),
        "ref_playwright_core": ("npm package: playwright-core", "playwright-core", "npm-package"),
        "ref_vite": ("npm package: vite", "vite", "npm-package"),
        "ref_node_assert_strict": ("Node.js built-in: node:assert/strict", "node:assert/strict", "node-builtin"),
        "ref_node_child_process": ("Node.js built-in: node:child_process", "node:child_process", "node-builtin"),
        "ref_node_crypto": ("Node.js built-in: node:crypto", "node:crypto", "node-builtin"),
        "ref_node_fs": ("Node.js built-in: node:fs", "node:fs", "node-builtin"),
        "ref_node_http": ("Node.js built-in: node:http", "node:http", "node-builtin"),
        "ref_node_net": ("Node.js built-in: node:net", "node:net", "node-builtin"),
        "ref_node_os": ("Node.js built-in: node:os", "node:os", "node-builtin"),
        "ref_node_path": ("Node.js built-in: node:path", "node:path", "node-builtin"),
        "ref_node_perf_hooks": ("Node.js built-in: node:perf_hooks", "node:perf_hooks", "node-builtin"),
        "ref_node_stream": ("Node.js built-in: node:stream", "node:stream", "node-builtin"),
        "ref_node_test": ("Node.js built-in: node:test", "node:test", "node-builtin"),
        "ref_node_url": ("Node.js built-in: node:url", "node:url", "node-builtin"),
    }
    missing_targets = sorted(
        {edge.get("target") for edge in edges if edge.get("target") not in node_by_id}
    )
    # AGENTS.md directly links to these generated docs. Keep their path nodes, not old contents.
    referenced_graphify_docs = {
        "docs_graphify_readme": "docs/graphify/README.md",
        "docs_graphify_rebuild_2026_09_19_readme": "docs/graphify/rebuild-2026-09-19/README.md",
        "docs_graphify_rebuild_2026_09_23_readme": "docs/graphify/rebuild-2026-09-23/README.md",
    }
    for relative_path in referenced_graphify_docs.values():
        add_file_node(relative_path, "document", source_kind="generated-doc-reference-only")
    for relative_path in referenced_graphify_docs.values():
        absolute_alias = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            str((ROOT / relative_path).resolve()),
        ).strip("_").lower()
        if absolute_alias not in missing_targets or absolute_alias in node_by_id:
            continue
        alias_node = {
            "id": absolute_alias,
            "label": f"Path reference alias: {PurePosixPath(relative_path).name}",
            "file_type": "concept",
            "source_file": "",
            "resolved_source_file": relative_path,
            "_origin": "graphify_markdown_path_alias",
        }
        nodes.append(alias_node)
        node_by_id[absolute_alias] = alias_node
        edges.append(
            {
                "source": absolute_alias,
                "target": file_node_by_path[relative_path],
                "relation": "resolves_to",
                "confidence": "INFERRED",
                "source_file": relative_path,
                "source_location": "L1",
                "weight": 1.0,
                "_origin": "graphify_markdown_path_alias",
            }
        )

    local_aliases = {
        "core_utils": "engine/pipeline/core_utils.py",
        "direction_policy": "engine/pipeline/direction_policy.py",
    }
    for alias, relative_path in local_aliases.items():
        if alias not in node_by_id:
            alias_node = {
                "id": alias,
                "label": f"{alias} import alias",
                "file_type": "concept",
                "source_file": "",
                "module_specifier": alias,
                "resolved_source_file": relative_path,
                "resolution": "inferred by unique in-repository module basename",
                "_origin": "graphify_local_import_alias",
            }
            nodes.append(alias_node)
            node_by_id[alias] = alias_node
        target = file_node_by_path.get(relative_path)
        if not target:
            raise RuntimeError(f"local import target missing from graph: {relative_path}")
        edges.append(
            {
                "source": alias,
                "target": target,
                "relation": "resolves_to",
                "confidence": "INFERRED",
                "source_file": relative_path,
                "source_location": "L1",
                "weight": 1.0,
                "_origin": "graphify_local_import_resolution",
            }
        )

    for target_id in missing_targets:
        if target_id in node_by_id or target_id in local_aliases:
            continue
        if target_id in external_modules:
            label, specifier, kind = external_modules[target_id]
            node = {
                "id": target_id,
                "label": label,
                "file_type": "concept",
                "source_file": "",
                "module_specifier": specifier,
                "dependency_kind": kind,
                "external_dependency": True,
                "_origin": "graphify_explicit_import_target",
            }
        elif target_id in file_node_by_path.values():
            continue
        elif target_id in {file_slug(path) for path in referenced_graphify_docs.values()}:
            continue
        else:
            raise RuntimeError(f"unmapped import/reference target; refusing to invent a node: {target_id}")
        nodes.append(node)
        node_by_id[target_id] = node

    # Represent launcher-declared data/cache directories without enumerating their contents.
    launcher_text = (ROOT / "scripts" / "start.ps1").read_text(encoding="utf-8", errors="replace")
    launcher_id = file_node_by_path.get("scripts/start.ps1")
    for line_number, line in enumerate(launcher_text.splitlines(), 1):
        match = re.search(r"'([^']+)'", line)
        if not match:
            continue
        relative_scope = match.group(1).replace("\\", "/").strip("/")
        if not relative_scope.startswith(("data/raw", "runtime/cache", "runtime/tmp")):
            continue
        scope_id = "scope_" + re.sub(r"[^A-Za-z0-9]+", "_", relative_scope).strip("_").lower()
        if scope_id not in node_by_id:
            scope_node = {
                "id": scope_id,
                "label": f"Data scope: {relative_scope} (contents not indexed)",
                "file_type": "concept",
                "source_file": "",
                "scope_path": relative_scope + "/",
                "content_indexed": False,
                "sensitivity": "user data / runtime state",
                "_origin": "graphify_directory_scope",
            }
            nodes.append(scope_node)
            node_by_id[scope_id] = scope_node
        if launcher_id:
            edges.append(
                {
                    "source": launcher_id,
                    "target": scope_id,
                    "relation": "references",
                    "confidence": "EXTRACTED",
                    "source_file": "scripts/start.ps1",
                    "source_location": f"L{line_number}",
                    "weight": 1.0,
                    "_origin": "literal_launcher_directory",
                }
            )

    policy_id = "sensitive_runtime_content_excluded"
    if policy_id not in node_by_id:
        policy_node = {
            "id": policy_id,
            "label": "Sensitive runtime content excluded",
            "file_type": "concept",
            "source_file": "",
            "content_indexed": False,
            "policy": "Credential/session values and runtime/cache/secret contents were not read, copied, or emitted.",
            "_origin": "graphify_confidentiality_scope",
        }
        nodes.append(policy_node)
        node_by_id[policy_id] = policy_node

    # Bounded, source-located semantic layer authored from explicit maintained
    # documentation. This is not an LLM extraction and never reads private data.
    document_paths = {
        Path(path).resolve().relative_to(ROOT).as_posix(): str(Path(path).resolve())
        for path in categories.get("document", [])
    }
    semantic_specs = [
        {
            "source_path": "AGENTS.md",
            "source_location": "L7",
            "suffix": "system_calculation_authority",
            "label": "Python engine is the calculation authority",
            "description": "The browser workstation acquires and displays chart data, while Python under engine/ owns trading calculations.",
            "targets": [
                ("apps/chart/src/main.js", "L18"),
                ("apps/chart/vite.config.js", "L23"),
                ("engine/bridge/trading_pipeline.py", "L25"),
            ],
        },
        {
            "source_path": "AGENTS.md",
            "source_location": "L39-L42",
            "suffix": "http_sse_python_runtime_boundary",
            "label": "Browser, Vite, Python runtime boundary",
            "description": "The documented request path crosses browser HTTP JSON/SSE, Vite middleware, a Python subprocess, and serialized results returned to browser views.",
            "targets": [
                ("apps/chart/src/main.js", "L42"),
                ("apps/chart/vite.config.js", "L39-L40"),
                ("engine/bridge/trading_pipeline.py", "L40-L41"),
            ],
        },
        {
            "source_path": "AGENTS.md",
            "source_location": "L45",
            "suffix": "partial_range_chronology_limit",
            "label": "Partial-range requests have bounded chronology",
            "description": "A partial request streams only selected RAW rows to the bridge; that calculation cannot use chronology outside the supplied range, so the browser must not become a second calculation authority.",
            "targets": [
                ("apps/chart/vite.config.js", "L45"),
                ("engine/bridge/trading_pipeline.py", "L45"),
            ],
        },
        {
            "source_path": "AGENTS.md",
            "source_location": "L54-L56",
            "suffix": "calculation_stage_ownership",
            "label": "Calculation stage order and lifecycle ownership",
            "description": "The bridge coordinates Reaction, Blue, A, S, E, StopAll/lifecycle, visibility, and OrderAudit serialization; stage collections have distinct ownership and nullable public contracts.",
            "targets": [
                ("engine/bridge/trading_pipeline.py", "L54-L56"),
                ("engine/pipeline/reaction_engine.py", "L62"),
                ("engine/pipeline/blue_line_detector.py", "L63"),
                ("engine/pipeline/a_zone_detector.py", "L64"),
                ("engine/pipeline/s_zone_detector.py", "L65"),
                ("engine/pipeline/e_zone_detector.py", "L66"),
                ("engine/pipeline/lifecycle_engine.py", "L67"),
            ],
        },
        {
            "source_path": "AGENTS.md",
            "source_location": "L70",
            "suffix": "numerical_provenance_contract",
            "label": "Numerical, temporal, and provenance invariants",
            "description": "The documented contract preserves Decimal semantics, strict crossings, explicit window boundaries, physical indexes/times, provenance, nulls, and serialization order.",
            "targets": [
                ("engine/pipeline/core_utils.py", "L68"),
                ("engine/pipeline/direction_policy.py", "L68"),
                ("engine/pipeline/reaction_engine.py", "L70"),
            ],
        },
        {
            "source_path": "AGENTS.md",
            "source_location": "L76-L79",
            "suffix": "directional_independence_and_asymmetry",
            "label": "Bullish and Bearish are independent directional contracts",
            "description": "Bearish is not a blanket inversion of Bullish; the reference records separate directional rules and a post-Reset same-Break reset-level asymmetry.",
            "known_asymmetry": "The documented Bullish branch uses analysis.extreme while the corresponding Bearish branch uses stored box_top.",
            "targets": [
                ("engine/pipeline/reaction_engine.py", "L76"),
                ("engine/pipeline/direction_policy.py", "L76"),
                ("docs/TradingBot_Bullish_Algorithm_Reference.md", "L72"),
                ("docs/TradingBot_Bearish_Algorithm_Reference.md", "L72"),
            ],
        },
        {
            "source_path": "AGENTS.md",
            "source_location": "L92",
            "suffix": "raw_storage_validation_boundary",
            "label": "RAW candle integrity belongs to the storage boundary",
            "description": "The RAW resource store owns schema, OHLC, chronology, and atomic-write validation; market-data contents are outside this semantic index.",
            "targets": [
                ("apps/chart/server/raw-resource-store.js", "L92"),
                ("apps/chart/vite.config.js", "L92"),
            ],
        },
        {
            "source_path": "docs/TradingBot_Project_Audit.md",
            "source_location": "L220",
            "suffix": "cleartext_session_storage_risk",
            "label": "FARAZ session persistence is a documented clear-text risk",
            "description": "The project audit documents editable clear-text session and browser-storage persistence; this graph records only the risk and source locations, never credential or session values.",
            "targets": [
                ("apps/chart/server/faraz-candle-api.js", "L220"),
            ],
            "supporting_sources": [
                ("docs/TradingBot_Technical_Architecture.md", "L266"),
                ("docs/TradingBot_Technical_Architecture.md", "L318"),
            ],
            "risk_level": "High (as documented by project audit)",
        },
        {
            "source_path": "docs/TradingBot_Technical_Architecture.md",
            "source_location": "L265-L267",
            "suffix": "local_api_trust_boundary_risk",
            "label": "Local API binding and mutation trust-boundary risk",
            "description": "The architecture audit flags broad local-service binding and missing application authentication/CSRF protections for state-changing APIs; this is a documented risk, not a claim of a fresh security audit.",
            "targets": [
                ("scripts/start.ps1", "L265"),
                ("apps/chart/vite.config.js", "L265-L267"),
                ("apps/chart/server/faraz-candle-api.js", "L265-L267"),
            ],
            "risk_level": "High/Medium (as documented by project architecture audit)",
        },
        {
            "source_path": "AGENTS.md",
            "source_location": "L112",
            "suffix": "graph_sensitive_scope_policy",
            "label": "Graph index excludes sensitive data values and runtime contents",
            "description": "The snapshot indexes safe CSS property names only and represents RAW/runtime locations as directory scopes; CSS values, credential/session values, and runtime data contents are excluded.",
            "targets": [
                ("apps/chart/src/styles/tokens.css", "L112"),
                ("docs/graphify/README.md", "L112"),
                ("docs/graphify/rebuild-2026-09-23/README.md", "L112"),
            ],
            "supporting_sources": [("AGENTS.md", "L138")],
        },
    ]
    semantic_nodes: dict[str, dict] = {}
    semantic_edges: list[dict] = []
    for spec in semantic_specs:
        source_path = spec["source_path"]
        source_absolute = document_paths.get(source_path)
        source_id = file_node_by_path.get(source_path)
        if not source_absolute or not source_id:
            raise RuntimeError(f"semantic source document is not in detector output: {source_path}")
        concept_id = f"{file_slug(source_path)}_{spec['suffix']}"
        node = {
            "id": concept_id,
            "label": spec["label"],
            "file_type": "concept",
            "source_file": source_absolute,
            "source_location": spec["source_location"],
            "description": spec["description"],
            "confidence": "EXTRACTED",
            "confidence_score": 1.0,
            "extraction_method": "host_agent_inline_source_evidence",
            "evidence_basis": "explicit_maintained_documentation",
            "content_indexed": True,
            "sensitive_values_indexed": False,
            "_origin": "bounded_inline_semantic_layer",
        }
        for optional_key in ("known_asymmetry", "risk_level"):
            if optional_key in spec:
                node[optional_key] = spec[optional_key]
        if concept_id in node_by_id:
            raise RuntimeError(f"semantic node id collision: {concept_id}")
        nodes.append(node)
        node_by_id[concept_id] = node
        semantic_nodes[spec["suffix"]] = node
        semantic_edges.append(
            {
                "source": source_id,
                "target": concept_id,
                "relation": "references",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
                "source_file": source_path,
                "source_location": spec["source_location"],
                "context": spec["description"],
                "weight": 1.0,
                "_origin": "bounded_inline_semantic_layer",
            }
        )
        for target_path, source_location in spec.get("targets", []):
            target_id = file_node_by_path.get(target_path)
            if not target_id:
                raise RuntimeError(f"semantic target is not in graph scope: {target_path}")
            semantic_edges.append(
                {
                    "source": concept_id,
                    "target": target_id,
                    "relation": "references",
                    "confidence": "EXTRACTED",
                    "confidence_score": 1.0,
                    "source_file": source_path,
                    "source_location": source_location,
                    "context": spec["description"],
                    "weight": 1.0,
                    "_origin": "bounded_inline_semantic_layer",
                }
            )
        for supporting_path, supporting_location in spec.get("supporting_sources", []):
            supporting_id = file_node_by_path.get(supporting_path)
            if not supporting_id:
                raise RuntimeError(f"semantic supporting document is not in graph scope: {supporting_path}")
            semantic_edges.append(
                {
                    "source": supporting_id,
                    "target": concept_id,
                    "relation": "references",
                    "confidence": "EXTRACTED",
                    "confidence_score": 1.0,
                    "source_file": supporting_path,
                    "source_location": supporting_location,
                    "context": spec["description"],
                    "weight": 1.0,
                    "_origin": "bounded_inline_semantic_layer",
                }
            )

    semantic_hyperedges = [
        {
            "id": "agents_runtime_request_path",
            "label": "Documented browser-to-Python request and response path",
            "nodes": [
                "agents_http_sse_python_runtime_boundary",
                file_node_by_path["apps/chart/src/main.js"],
                file_node_by_path["apps/chart/vite.config.js"],
                file_node_by_path["engine/bridge/trading_pipeline.py"],
            ],
            "confidence": "EXTRACTED",
            "confidence_score": 1.0,
            "source_file": document_paths["AGENTS.md"],
            "source_location": "L39-L42",
        },
        {
            "id": "agents_calculation_stage_sequence",
            "label": "Documented calculation stage sequence and lifecycle output",
            "nodes": [
                "agents_calculation_stage_ownership",
                file_node_by_path["engine/bridge/trading_pipeline.py"],
                file_node_by_path["engine/pipeline/reaction_engine.py"],
                file_node_by_path["engine/pipeline/blue_line_detector.py"],
                file_node_by_path["engine/pipeline/a_zone_detector.py"],
                file_node_by_path["engine/pipeline/s_zone_detector.py"],
                file_node_by_path["engine/pipeline/e_zone_detector.py"],
                file_node_by_path["engine/pipeline/lifecycle_engine.py"],
            ],
            "confidence": "EXTRACTED",
            "confidence_score": 1.0,
            "source_file": document_paths["AGENTS.md"],
            "source_location": "L54-L56",
        },
    ]
    edges.extend(semantic_edges)

    edges.extend(html_edges)
    all_node_ids = {node["id"] for node in nodes}
    unmapped = sorted(
        {edge.get("source") for edge in edges if edge.get("source") not in all_node_ids}
        | {edge.get("target") for edge in edges if edge.get("target") not in all_node_ids}
    )
    if unmapped:
        raise RuntimeError(f"unresolved endpoints remain after explicit resolution: {unmapped[:20]}")

    # Collapse parallel links while retaining all relation/location/context evidence.
    groups: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    for edge in edges:
        groups[(edge["source"], edge["target"])].append(edge)
    confidence_rank = {"EXTRACTED": 3, "INFERRED": 2, "AMBIGUOUS": 1}
    canonical_edges = []
    for (source, target), group in sorted(groups.items()):
        relation_counts = collections.Counter(edge.get("relation", "references") for edge in group)
        relation = sorted(relation_counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
        confidence = max(
            (edge.get("confidence", "EXTRACTED") for edge in group),
            key=lambda item: confidence_rank.get(item, 0),
        )
        base = max(
            group,
            key=lambda edge: (
                confidence_rank.get(edge.get("confidence"), 0),
                edge.get("weight", 1.0),
                edge.get("relation", ""),
            ),
        ).copy()
        base.update(
            {
                "source": source,
                "target": target,
                "relation": relation,
                "confidence": confidence,
                "weight": max((float(edge.get("weight", 1.0)) for edge in group), default=1.0),
            }
        )
        variants: collections.Counter = collections.Counter()
        for edge in group:
            score = edge.get("confidence_score")
            key = (
                edge.get("relation", "references"),
                edge.get("confidence", "EXTRACTED"),
                edge.get("source_file", ""),
                edge.get("source_location", ""),
                edge.get("context", ""),
                float(score) if score is not None else -1.0,
            )
            variants[key] += 1
        if len(group) > 1:
            base["evidence_count"] = len(group)
            base["relation_variants"] = sorted({edge.get("relation", "references") for edge in group})
            base["edge_evidence"] = [
                {
                    "relation": relation_name,
                    "confidence": evidence_confidence,
                    "source_file": source_file,
                    "source_location": source_location,
                    **({"context": context} if context else {}),
                    **({"confidence_score": score} if score >= 0 else {}),
                    "occurrences": count,
                }
                for (
                    relation_name,
                    evidence_confidence,
                    source_file,
                    source_location,
                    context,
                    score,
                ), count in sorted(variants.items())
            ]
        scored_edges = [edge for edge in group if edge.get("confidence") == confidence and "confidence_score" in edge]
        if scored_edges:
            base["confidence_score"] = max(float(edge["confidence_score"]) for edge in scored_edges)
        canonical_edges.append(base)

    normalized = {
        "nodes": nodes,
        "edges": canonical_edges,
        "hyperedges": list(raw.get("hyperedges", [])) + semantic_hyperedges,
        "input_tokens": 0,
        "output_tokens": 0,
    }
    # Preserve detector-absolute provenance in the evidence artifact. Graphify
    # normalizes paths in-place for portable graph.json output.
    normalized_evidence = json.loads(json.dumps(normalized, ensure_ascii=False))
    normalized_health = diagnose_extraction(normalized, directed=True, root=ROOT)
    health_keys = (
        "missing_endpoint_edges",
        "dangling_endpoint_edges",
        "self_loop_edges",
        "directed_same_endpoint_collapsed_edges",
    )
    if any(normalized_health.get(key, 0) for key in health_keys):
        raise RuntimeError(f"normalized extraction health gate failed: {normalized_health}")

    graph = build_from_json(normalized, root=ROOT, directed=True)
    if graph.number_of_nodes() == 0:
        raise RuntimeError("refusing to write an empty graph")
    if graph.number_of_nodes() > 5000:
        raise RuntimeError("graph exceeds 5,000 nodes; warn before generating the HTML visualization")

    communities = cluster(graph)
    cohesion = score_all(graph, communities)
    labels: dict[int, str] = {}
    repeated_labels: collections.Counter = collections.Counter()
    graph_nodes = {node_id: graph.nodes[node_id] for node_id in graph.nodes}
    for community_id, members in communities.items():
        files = collections.Counter(
            node.get("source_file", "")
            for node in (graph_nodes[node_id] for node_id in members)
            if node.get("source_file")
        )
        if files:
            source = PurePosixPath(files.most_common(1)[0][0])
            stem_words = title_words(source.stem)
            parts = source.parts
            if parts[:2] == ("apps", "chart"):
                dirs = [part for part in parts[2:-1] if part not in {"src", "tests", "server"}]
                words = (title_words(dirs[-1]) if dirs else ["Chart"]) + stem_words
            elif parts[0] == "engine":
                dirs = [part for part in parts[:-1] if part != "engine"]
                words = ["Engine"] + (title_words(dirs[-1]) if dirs else []) + stem_words
            elif parts[0] == "docs":
                words = stem_words or title_words(parts[-2])
            elif parts[0] == "scripts":
                words = ["Project", "Scripts"] + stem_words
            else:
                words = stem_words or title_words(parts[-1])
            unique_words = []
            for word in words:
                if word.lower() not in {item.lower() for item in unique_words}:
                    unique_words.append(word)
            label = " ".join(unique_words[:5])
        else:
            names = collections.Counter(
                str(graph_nodes[node_id].get("label", ""))
                for node_id in members
                if graph_nodes[node_id].get("label")
            )
            label = " ".join(title_words(names.most_common(1)[0][0])[:4]) if names else "Project Components"
        label = label or f"Project Components {community_id}"
        repeated_labels[label] += 1
        if repeated_labels[label] > 1:
            label = f"{label} {repeated_labels[label]}"
        labels[community_id] = label

    gods = god_nodes(graph)
    surprises = surprising_connections(graph, communities)
    questions = suggest_questions(graph, communities, labels)
    token_cost = {"input": 0, "output": 0}
    report = generate(
        graph,
        communities,
        cohesion,
        labels,
        gods,
        surprises,
        detect_result,
        token_cost,
        str(ROOT),
        suggested_questions=questions,
        built_at_commit=commit,
    )
    markdown_count = len(markdown_paths)
    report += (
        "\n\n## Corpus scope and sensitive-content handling\n\n"
        f"- Structural extraction: {len(categories.get('code', []))} code files and {markdown_count} Markdown documents; "
        f"{len(html_paths)} HTML entry pages contribute only literal local script/style references.\n"
        f"- Detector classified {detect_result['total_files']} files ({detect_result['total_words']:,} words). "
        f"{len(detect_result.get('unclassified', []))} unclassified paths are represented only as file nodes.\n"
        f"- Detector-sensitive `apps/chart/src/styles/tokens.css` was checked with a redacted pattern scan; risk flags={risk_flags}. "
        f"Only {len(set(name for name, _ in safe_css_identifiers))} custom-property names are indexed; values are omitted.\n"
        "- RAW/runtime directories are scope markers from literal launcher configuration; their contents were not traversed. "
        "Credential/session values and `runtime/cache/secret` contents were not accessed or emitted.\n"
        "- `docs/graphify/` and prior generated Graphify outputs were excluded to avoid self-reference. "
        "The detector pruned vendored/build/cache trees and reported no walk errors.\n"
        f"- Semantic LLM extraction was not run. A bounded host-agent inline layer adds {len(semantic_specs)} concepts, "
        f"{len(semantic_edges)} source-located evidence links, and {len(semantic_hyperedges)} documented hyperedges; "
        "it uses explicit maintained text only, with confidence labels and no private-value indexing. Graphify-generated `INFERRED` edges remain labeled as inferred.\n"
        "- Parallel endpoint links were canonicalized into one directed link each; relation, confidence, source location, "
        "context, and occurrence variants are retained in `edge_evidence`.\n"
    )

    write_json(RAW_DIR / ".graphify_extract.json", normalized_evidence)
    write_json(
        RAW_DIR / ".graphify_analysis.json",
        {
            "communities": {str(key): value for key, value in communities.items()},
            "cohesion": {str(key): value for key, value in cohesion.items()},
            "labels": {str(key): value for key, value in labels.items()},
            "gods": gods,
            "surprises": surprises,
            "questions": questions,
        },
    )
    write_json(
        RAW_DIR / ".graphify_scope.json",
        {
            "classified_files": detect_result["total_files"],
            "classified_words": detect_result["total_words"],
            "code_files": len(categories.get("code", [])),
            "documents": len(categories.get("document", [])),
            "unclassified_paths": [Path(path).resolve().relative_to(ROOT).as_posix() for path in detect_result.get("unclassified", [])],
            "sensitive_paths": [Path(path).resolve().relative_to(ROOT).as_posix() for path in detect_result.get("skipped_sensitive", [])],
            "graphify_outputs_excluded": True,
            "runtime_data_contents_read": False,
        },
    )

    graph_json = OUTPUT / "graph.json"
    html_path = OUTPUT / "graph.html"
    to_json(graph, communities, str(graph_json), force=True, built_at_commit=commit, community_labels=labels)
    (OUTPUT / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    write_json(OUTPUT / ".graphify_labels.json", {str(key): value for key, value in labels.items()})
    generate_html(graph, communities, str(html_path), community_labels=labels)

    serialized = json.loads(graph_json.read_text(encoding="utf-8"))
    serialized_health = diagnose_extraction(
        {"nodes": serialized.get("nodes", []), "edges": serialized.get("links", serialized.get("edges", []))},
        directed=True,
        root=ROOT,
    )
    health = {
        "generated_at": built_at,
        "graphify_version": GRAPHIFY_VERSION,
        "graphifyy_version": GRAPHIFYY_VERSION,
        "built_at_commit": commit,
        "raw_extraction": raw_health,
        "normalized_extraction": normalized_health,
        "serialized_graph": serialized_health,
        "normalization": {
            "raw_nodes": len(raw["nodes"]),
            "raw_edges": len(raw["edges"]),
            "normalized_nodes": len(normalized["nodes"]),
            "normalized_edges": len(normalized["edges"]),
            "raw_dangling_edges": raw_health.get("dangling_endpoint_edges", 0),
            "raw_exact_duplicate_edges": raw_health.get("exact_duplicate_edges", 0),
            "raw_parallel_edge_collapses": raw_health.get("directed_same_endpoint_collapsed_edges", 0),
            "manual_html_references": len(html_edges),
            "resolved_external_modules": len(external_modules),
            "resolved_local_aliases": len(local_aliases),
            "unclassified_path_nodes": len(detect_result.get("unclassified", [])),
            "sensitive_path_nodes": len(detect_result.get("skipped_sensitive", [])),
            "safe_css_identifier_nodes": len(set(name for name, _ in safe_css_identifiers)),
            "sensitive_css_redacted_scan": risk_flags,
            "inline_semantic_concepts": len(semantic_specs),
            "inline_semantic_evidence_links": len(semantic_edges),
            "inline_semantic_hyperedges": len(semantic_hyperedges),
            "private_semantic_values_indexed": False,
        },
        "scope": {
            "classified_files": detect_result["total_files"],
            "total_words": detect_result["total_words"],
            "code": len(categories.get("code", [])),
            "documents": len(categories.get("document", [])),
            "sensitive_skipped": detect_result.get("skipped_sensitive", []),
            "unclassified_count": len(detect_result.get("unclassified", [])),
            "walk_errors": detect_result.get("walk_errors", []),
            "graphify_outputs_excluded": True,
            "raw_data_and_runtime_content_read": False,
        },
        "graph": {
            "nodes": graph.number_of_nodes(),
            "directed_links": graph.number_of_edges(),
            "communities": len(communities),
        },
        "tokens": token_cost,
    }
    write_json(OUTPUT / "graph-health.json", health)
    health_markdown = (
        "# Graph Health — 2026-09-23\n\n"
        f"- Graphify {GRAPHIFY_VERSION} / graphifyy {GRAPHIFYY_VERSION}; source commit `{commit}`.\n"
        f"- Final graph: {graph.number_of_nodes():,} nodes, {graph.number_of_edges():,} directed links, {len(communities)} communities.\n"
        f"- Normalized extraction integrity: missing={normalized_health.get('missing_endpoint_edges', 0)}, "
        f"dangling={normalized_health.get('dangling_endpoint_edges', 0)}, self-loops={normalized_health.get('self_loop_edges', 0)}, "
        f"duplicate endpoint pairs={normalized_health.get('directed_same_endpoint_collapsed_edges', 0)}.\n"
        f"- Serialized graph integrity: missing={serialized_health.get('missing_endpoint_edges', 0)}, "
        f"dangling={serialized_health.get('dangling_endpoint_edges', 0)}, self-loops={serialized_health.get('self_loop_edges', 0)}.\n"
        f"- Raw AST pass had {raw_health.get('dangling_endpoint_edges', 0)} unresolved import/reference endpoints and "
        f"{raw_health.get('directed_same_endpoint_collapsed_edges', 0)} parallel endpoint-edge collapses; direct imports were "
        "resolved to path/external-module nodes and edge variants were preserved in `edge_evidence`.\n"
        f"- Unclassified configuration/style/batch paths are path-only nodes. `tokens.css` redacted scan flags: {risk_flags}; "
        f"{len(set(name for name, _ in safe_css_identifiers))} CSS custom-property names indexed, all values omitted.\n"
        "- RAW/runtime paths are directory-scope markers only. No candles, drawings, caches, credentials, or session contents were read/copied.\n"
        f"- Previous Graphify outputs were excluded from input. No filesystem walk errors. No semantic LLM call was made; "
        f"the source-located inline layer contains {len(semantic_specs)} concepts and {len(semantic_hyperedges)} hyperedges, "
        "all explicitly grounded and value-safe.\n\n"
        "## Raw extractor diagnostic\n\n```text\n"
        + format_diagnostic_report(raw_health)
        + "\n```\n\n## Normalized extraction diagnostic\n\n```text\n"
        + format_diagnostic_report(normalized_health)
        + "\n```\n"
    )
    (OUTPUT / "GRAPH_HEALTH.md").write_text(health_markdown, encoding="utf-8")

    cost = {
        "generated_at": built_at,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "note": "Structural AST/Markdown extraction plus bounded host-agent inline semantic extraction from explicit maintained documentation; no semantic LLM call was made and no private values were indexed.",
        "inline_semantic_concepts": len(semantic_specs),
        "inline_semantic_evidence_links": len(semantic_edges),
        "inline_semantic_hyperedges": len(semantic_hyperedges),
    }
    write_json(OUTPUT / "cost.json", cost)

    def sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    output_names = [
        "graph.json",
        "graph.html",
        "GRAPH_REPORT.md",
        "GRAPH_HEALTH.md",
        "graph-health.json",
        ".graphify_labels.json",
        "cost.json",
    ]
    manifest = {
        "generated_at": built_at,
        "repository_root": str(ROOT),
        "built_at_commit": commit,
        "directed": True,
        "graphify_version": GRAPHIFY_VERSION,
        "graphifyy_version": GRAPHIFYY_VERSION,
        "source_scope": {
            "classified_files": detect_result["total_files"],
            "words": detect_result["total_words"],
            "code": len(categories.get("code", [])),
            "documents": len(categories.get("document", [])),
            "unclassified_path_only": len(detect_result.get("unclassified", [])),
            "sensitive_path_only": len(detect_result.get("skipped_sensitive", [])),
            "graphify_outputs_excluded": True,
            "runtime_and_raw_contents_read": False,
            "private_values_indexed": False,
        },
        "semantic_layer": {
            "method": "bounded host-agent inline source evidence",
            "llm_used": False,
            "concepts": len(semantic_specs),
            "evidence_links": len(semantic_edges),
            "hyperedges": len(semantic_hyperedges),
            "private_values_indexed": False,
        },
        "graph": health["graph"],
        "outputs": [
            {"path": name, "bytes": (OUTPUT / name).stat().st_size, "sha256": sha256(OUTPUT / name)}
            for name in output_names
        ],
    }
    write_json(OUTPUT / "manifest.json", manifest)

    # Preserve the long-standing docs/graphify paths used by existing project references.
    for name in output_names + ["manifest.json"]:
        (ROOT / "docs" / "graphify" / name).write_bytes((OUTPUT / name).read_bytes())

    print(
        json.dumps(
            {
                "commit": commit,
                "nodes": graph.number_of_nodes(),
                "links": graph.number_of_edges(),
                "communities": len(communities),
                "raw_dangling": raw_health.get("dangling_endpoint_edges"),
                "raw_parallel": raw_health.get("directed_same_endpoint_collapsed_edges"),
                "normalized_dangling": normalized_health.get("dangling_endpoint_edges"),
                "normalized_parallel": normalized_health.get("directed_same_endpoint_collapsed_edges"),
                "html_bytes": html_path.stat().st_size,
                "sensitive_files": len(detect_result.get("skipped_sensitive", [])),
                "unclassified_files": len(detect_result.get("unclassified", [])),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
