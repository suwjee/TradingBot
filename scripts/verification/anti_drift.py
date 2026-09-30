#!/usr/bin/env python3
# created_at: 2026-09-30T16:20:59+03:30
# last_modified_at: 2026-09-30T16:33:27+03:30
"""Read-only structural/documentation anti-drift verifier for TradingBot."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence
from urllib.parse import unquote, urlsplit

VALID_ROLES = {"normative", "reference", "procedure", "evidence"}
VALID_LIFECYCLES = {"maintained", "historical", "generated", "deprecated"}
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
SEVERITY_ORDER = {"ERROR": 0, "WARNING": 1, "INFO": 2}
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: str
    file: str
    line: int | None
    message: str
    hint: str

    def sort_key(self) -> tuple[object, ...]:
        return (
            SEVERITY_ORDER.get(self.severity, 99),
            self.file.casefold(),
            self.line if self.line is not None else -1,
            self.code,
            self.message,
        )


@dataclass(frozen=True)
class FrontMatter:
    values: dict[str, object]
    lines: dict[str, int]
    end_line: int


@dataclass
class Report:
    mode: str
    diagnostics: list[Diagnostic]

    def ordered(self) -> list[Diagnostic]:
        return sorted(self.diagnostics, key=Diagnostic.sort_key)

    def by_severity(self, severity: str) -> list[Diagnostic]:
        return [item for item in self.ordered() if item.severity == severity]

    @property
    def status(self) -> str:
        return "FAIL" if self.by_severity("ERROR") else "PASS"

    def to_dict(self) -> dict[str, object]:
        errors = [asdict(item) for item in self.by_severity("ERROR")]
        warnings = [asdict(item) for item in self.by_severity("WARNING")]
        info = [asdict(item) for item in self.by_severity("INFO")]
        return {
            "status": self.status,
            "mode": self.mode,
            "repository_root": ".",
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "summary": {
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(info),
                "diagnostics": len(errors) + len(warnings) + len(info),
            },
        }


class VerifierRuntimeError(RuntimeError):
    pass


class CaseResolver:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self._entries: dict[Path, tuple[set[str], dict[str, list[str]]]] = {}

    def _directory_entries(self, directory: Path) -> tuple[set[str], dict[str, list[str]]]:
        directory = directory.resolve()
        cached = self._entries.get(directory)
        if cached is not None:
            return cached
        try:
            names = [entry.name for entry in directory.iterdir()]
        except OSError:
            names = []
        exact = set(names)
        folded: dict[str, list[str]] = {}
        for name in names:
            folded.setdefault(name.casefold(), []).append(name)
        result = (exact, folded)
        self._entries[directory] = result
        return result

    def resolve(self, relative: PurePosixPath) -> tuple[str, Path | None, str | None]:
        current = self.root
        actual_parts: list[str] = []
        for part in relative.parts:
            if part in {"", "."}:
                continue
            if part == "..":
                if current == self.root:
                    return "outside", None, None
                current = current.parent
                if actual_parts:
                    actual_parts.pop()
                continue
            exact, folded = self._directory_entries(current)
            if part in exact:
                chosen = part
            else:
                matches = folded.get(part.casefold(), [])
                if not matches:
                    return "missing", None, None
                chosen = sorted(matches)[0]
                actual_parts.append(chosen)
                return "case-mismatch", current / chosen, "/".join(actual_parts)
            actual_parts.append(chosen)
            current = current / chosen
        return "ok", current, "/".join(actual_parts)


def repo_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def looks_like_repo_root(path: Path) -> bool:
    return (
        (path / "AGENTS.md").is_file()
        and (path / "engineering" / "docs" / "documentation-governance.md").is_file()
    )


def discover_repo_root(explicit: str | None = None) -> Path:
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        if looks_like_repo_root(candidate):
            return candidate
        raise VerifierRuntimeError(
            f"Explicit --root is not a TradingBot repository root: {candidate}"
        )

    candidates = [Path(__file__).resolve().parent, Path.cwd().resolve()]
    seen: set[Path] = set()
    for start in candidates:
        start = start if start.is_dir() else start.parent
        for candidate in (start, *start.parents):
            candidate = candidate.resolve()
            if candidate in seen:
                continue
            seen.add(candidate)
            if looks_like_repo_root(candidate):
                return candidate
    raise VerifierRuntimeError(
        "Unable to discover the TradingBot repository root; pass --root with a valid checkout."
    )


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise VerifierRuntimeError(f"UTF-8 documentation read failed for {path}: {exc}") from exc
    except OSError as exc:
        raise VerifierRuntimeError(f"Unable to read {path}: {exc}") from exc


def parse_front_matter(text: str) -> FrontMatter | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return FrontMatter(values={"__malformed__": "missing-closing-delimiter"}, lines={}, end_line=1)

    values: dict[str, object] = {}
    positions: dict[str, int] = {}
    current_list: str | None = None
    for index in range(1, end):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("-") and current_list:
            item = stripped[1:].strip().strip('"\'')
            value = values.setdefault(current_list, [])
            if isinstance(value, list):
                value.append(item)
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if not match:
            current_list = None
            continue
        key, value_text = match.group(1), match.group(2).strip()
        positions[key] = index + 1
        if value_text:
            values[key] = value_text.strip('"\'')
            current_list = None
        else:
            values[key] = []
            current_list = key
    return FrontMatter(values=values, lines=positions, end_line=end + 1)


def timestamp_valid(value: object) -> bool:
    if not isinstance(value, str) or not TIMESTAMP_RE.fullmatch(value):
        return False
    if any(token in value.upper() for token in ("YYYY", "TODO", "TBD", "PLACEHOLDER", "<", ">", "${")):
        return False
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def iter_governed_documents(root: Path) -> list[Path]:
    docs_root = root / "engineering" / "docs"
    documents = sorted((path for path in docs_root.rglob("*.md") if path.is_file()), key=lambda p: p.as_posix().casefold())
    root_readme = root / "README.md"
    if root_readme.is_file():
        root_meta = parse_front_matter(read_text(root_readme))
        if root_meta and root_meta.values.get("lifecycle") == "maintained":
            documents.append(root_readme)
    return documents


def validate_metadata(root: Path, path: Path, text: str) -> tuple[list[Diagnostic], FrontMatter | None]:
    diagnostics: list[Diagnostic] = []
    relative = repo_path(root, path)
    meta = parse_front_matter(text)
    in_maintained_surface = path.is_relative_to(root / "engineering" / "docs")
    if meta is None:
        if in_maintained_surface:
            diagnostics.append(Diagnostic(
                "META001", "ERROR", relative, 1,
                "Maintained documentation surface file has no YAML frontmatter.",
                "Add governance-compliant metadata without changing document authority."
            ))
        return diagnostics, None
    if "__malformed__" in meta.values:
        diagnostics.append(Diagnostic(
            "META002", "ERROR", relative, 1,
            "YAML frontmatter is not closed by a second '---' delimiter.",
            "Repair the metadata block before using this document as maintained guidance."
        ))
        return diagnostics, meta

    for field in ("title", "document_role", "lifecycle", "owner", "last_modified_at"):
        if not meta.values.get(field):
            diagnostics.append(Diagnostic(
                "META003", "ERROR", relative, 1,
                f"Required maintained-document metadata field '{field}' is missing or empty.",
                "Add the field according to Documentation Governance."
            ))

    role = meta.values.get("document_role")
    if isinstance(role, str) and role not in VALID_ROLES:
        diagnostics.append(Diagnostic(
            "META004", "ERROR", relative, meta.lines.get("document_role"),
            f"Unsupported document_role '{role}'.",
            f"Use one of: {', '.join(sorted(VALID_ROLES))}."
        ))
    lifecycle = meta.values.get("lifecycle")
    if isinstance(lifecycle, str) and lifecycle not in VALID_LIFECYCLES:
        diagnostics.append(Diagnostic(
            "LIFE001", "ERROR", relative, meta.lines.get("lifecycle"),
            f"Unsupported lifecycle '{lifecycle}'.",
            f"Use one of: {', '.join(sorted(VALID_LIFECYCLES))}."
        ))
    if in_maintained_surface and lifecycle in {"historical", "generated"}:
        diagnostics.append(Diagnostic(
            "LIFE002", "ERROR", relative, meta.lines.get("lifecycle"),
            f"{lifecycle.title()} material is placed in the maintained engineering/docs surface.",
            "Move/classify it according to Documentation Governance; do not present it as Current maintained guidance."
        ))

    for field in ("created_at", "last_modified_at"):
        if field in meta.values and not timestamp_valid(meta.values[field]):
            diagnostics.append(Diagnostic(
                "TIME001", "ERROR", relative, meta.lines.get(field),
                f"Metadata field '{field}' is not YYYY-MM-DDTHH:MM:SS±HH:MM.",
                "Use a real timestamp with seconds and numeric timezone offset; never fabricate an unknown creation time."
            ))
    scope = meta.values.get("scope")
    if scope is not None and not (isinstance(scope, list) and all(isinstance(item, str) and item for item in scope)):
        diagnostics.append(Diagnostic(
            "META005", "WARNING", relative, meta.lines.get("scope"),
            "scope metadata is present but is not a non-empty YAML list of strings.",
            "Use a bounded list when scope is needed, or omit the optional field."
        ))
    return diagnostics, meta


def strip_fenced_code(text: str) -> list[tuple[int, str]]:
    output: list[tuple[int, str]] = []
    in_fence = False
    fence_char = ""
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_char = marker
            elif marker == fence_char:
                in_fence = False
                fence_char = ""
            continue
        if in_fence:
            continue
        # Inline code is not an active Markdown link or prose rule.
        scrubbed = re.sub(r"`[^`]*`", "", line)
        output.append((number, scrubbed))
    return output


def extract_links(text: str) -> list[tuple[int, str, str]]:
    links: list[tuple[int, str, str]] = []
    for line_number, line in strip_fenced_code(text):
        for match in MARKDOWN_LINK_RE.finditer(line):
            label = match.group(1).strip()
            target = match.group(2).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1].strip()
            links.append((line_number, label, target))
    return links


def normalize_relative_target(source_relative: PurePosixPath, raw_target: str) -> tuple[PurePosixPath | None, str]:
    split = urlsplit(raw_target)
    if split.scheme.lower() in EXTERNAL_SCHEMES or split.netloc:
        return None, ""
    if raw_target.startswith("//"):
        return None, ""
    path_text = unquote(split.path)
    fragment = unquote(split.fragment)
    if not path_text:
        return source_relative, fragment
    if path_text.startswith("/"):
        return None, fragment
    combined = source_relative.parent.joinpath(PurePosixPath(path_text.replace("\\", "/")))
    parts: list[str] = []
    for part in combined.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                return PurePosixPath(".."), fragment
            parts.pop()
        else:
            parts.append(part)
    return PurePosixPath(*parts), fragment


def github_heading_slugs(text: str) -> set[str]:
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    for _, line in strip_fenced_code(text):
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = re.sub(r"<[^>]+>", "", match.group(1))
        heading = re.sub(r"[`*_~]", "", heading)
        heading = unicodedata.normalize("NFKC", heading).strip().lower()
        heading = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE)
        base = re.sub(r"\s+", "-", heading)
        index = counts.get(base, 0)
        counts[base] = index + 1
        slug = base if index == 0 else f"{base}-{index}"
        slugs.add(slug)
    return slugs


def validate_links(
    root: Path,
    path: Path,
    text: str,
    resolver: CaseResolver,
    anchor_cache: dict[Path, set[str]],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    relative = PurePosixPath(repo_path(root, path))
    for line, _label, raw_target in extract_links(text):
        target, fragment = normalize_relative_target(relative, raw_target)
        if target is None:
            continue
        if target.parts and target.parts[0] == "..":
            diagnostics.append(Diagnostic(
                "LINK001", "ERROR", relative.as_posix(), line,
                f"Internal Markdown link escapes the repository: {raw_target}",
                "Point the link at a repository-relative Current/evidence target."
            ))
            continue
        status, resolved, actual = resolver.resolve(target)
        if status == "missing":
            diagnostics.append(Diagnostic(
                "LINK001", "ERROR", relative.as_posix(), line,
                f"Internal Markdown link target does not exist: {raw_target}",
                "Update the link to the Current path or restore the intended target."
            ))
            continue
        if status == "case-mismatch":
            diagnostics.append(Diagnostic(
                "PATH001", "ERROR", relative.as_posix(), line,
                f"Markdown link casing does not match the repository path: {raw_target}",
                f"Use exact repository casing; resolved path begins as '{actual}'."
            ))
            continue
        if status != "ok" or resolved is None:
            continue
        if fragment and resolved.is_file() and resolved.suffix.lower() == ".md":
            slugs = anchor_cache.get(resolved)
            if slugs is None:
                slugs = github_heading_slugs(read_text(resolved))
                anchor_cache[resolved] = slugs
            if fragment.casefold() not in {slug.casefold() for slug in slugs}:
                diagnostics.append(Diagnostic(
                    "LINK002", "WARNING", relative.as_posix(), line,
                    f"Markdown anchor could not be matched conservatively: #{fragment}",
                    "Verify the target heading/anchor; this warning is non-blocking because GitHub slugging has edge cases."
                ))
    return diagnostics


def metadata_index(root: Path, documents: Sequence[Path]) -> dict[Path, FrontMatter | None]:
    return {path.resolve(): parse_front_matter(read_text(path)) for path in documents}


def navigation_checks(
    root: Path,
    meta_by_path: dict[Path, FrontMatter | None],
    resolver: CaseResolver,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    nav = root / "engineering" / "docs" / "README.md"
    if not nav.is_file():
        return [Diagnostic(
            "NAV001", "ERROR", "engineering/docs/README.md", None,
            "Maintained documentation navigation file is missing.",
            "Restore the Documentation Governance navigation owner."
        )]
    nav_text = read_text(nav)
    nav_relative = PurePosixPath("engineering/docs/README.md")
    superseded: set[str] = set()
    for meta in meta_by_path.values():
        if not meta:
            continue
        value = meta.values.get("supersedes")
        if isinstance(value, str) and value:
            superseded.add(PurePosixPath(value.replace("\\", "/")).as_posix())

    for line, _label, raw_target in extract_links(nav_text):
        target, _ = normalize_relative_target(nav_relative, raw_target)
        if target is None or (target.parts and target.parts[0] == ".."):
            continue
        target_text = target.as_posix()
        if target_text in superseded:
            diagnostics.append(Diagnostic(
                "STALE001", "ERROR", nav_relative.as_posix(), line,
                f"Maintained navigation targets a superseded document: {target_text}",
                "Point navigation to the Current maintained owner; link Historical material only as evidence."
            ))
        status, resolved, _actual = resolver.resolve(target)
        if status != "ok" or resolved is None or not resolved.is_file():
            continue
        try:
            is_docs_target = resolved.resolve().is_relative_to((root / "engineering" / "docs").resolve())
        except ValueError:
            is_docs_target = False
        if not is_docs_target or resolved.suffix.lower() != ".md":
            continue
        meta = meta_by_path.get(resolved.resolve()) or parse_front_matter(read_text(resolved))
        lifecycle = meta.values.get("lifecycle") if meta else None
        if lifecycle != "maintained":
            diagnostics.append(Diagnostic(
                "NAV002", "ERROR", nav_relative.as_posix(), line,
                f"Current maintained navigation points to lifecycle '{lifecycle or 'unknown'}': {target_text}",
                "Current owner navigation must target maintained documentation."
            ))
    return diagnostics


def ownership_checks(
    root: Path,
    meta_by_path: dict[Path, FrontMatter | None],
    resolver: CaseResolver,
) -> list[Diagnostic]:
    """Detect only objectively provable supersession/maintained conflicts."""
    diagnostics: list[Diagnostic] = []
    for source, meta in sorted(meta_by_path.items(), key=lambda item: repo_path(root, item[0]).casefold()):
        if not meta or meta.values.get("lifecycle") != "maintained":
            continue
        value = meta.values.get("supersedes")
        if not isinstance(value, str) or not value:
            continue
        target = PurePosixPath(value.replace("\\", "/"))
        status, resolved, _actual = resolver.resolve(target)
        if status != "ok" or resolved is None or not resolved.is_file():
            continue
        target_meta = meta_by_path.get(resolved.resolve())
        if not target_meta:
            continue
        if target_meta.values.get("lifecycle") == "maintained":
            diagnostics.append(Diagnostic(
                "OWN001", "ERROR", repo_path(root, source), meta.lines.get("supersedes"),
                f"Document supersedes another document that is still marked maintained: {target.as_posix()}",
                "Retain only one Current maintained owner; reclassify/archive the superseded document according to Governance."
            ))
    return diagnostics


def authority_link_checks(root: Path, resolver: CaseResolver, superseded: set[str]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    agents = root / "AGENTS.md"
    if not agents.is_file():
        return [Diagnostic("AUTH001", "ERROR", "AGENTS.md", None, "Root AGENTS.md is missing.", "Restore the root authority contract.")]
    relative = PurePosixPath("AGENTS.md")
    for line, _label, raw_target in extract_links(read_text(agents)):
        target, _ = normalize_relative_target(relative, raw_target)
        if target is None or (target.parts and target.parts[0] == ".."):
            continue
        if target.as_posix() in superseded:
            diagnostics.append(Diagnostic(
                "STALE002", "ERROR", "AGENTS.md", line,
                f"Root authority links to a superseded document: {target.as_posix()}",
                "Link root authority to the Current maintained owner."
            ))
        status, _resolved, actual = resolver.resolve(target)
        if status == "missing":
            diagnostics.append(Diagnostic(
                "AUTH002", "ERROR", "AGENTS.md", line,
                f"Root AGENTS.md link target is missing: {raw_target}",
                "Repair the authority/navigation link to the Current path."
            ))
        elif status == "case-mismatch":
            diagnostics.append(Diagnostic(
                "PATH002", "ERROR", "AGENTS.md", line,
                f"Root AGENTS.md link casing is incorrect: {raw_target}",
                f"Use exact repository casing; resolved path begins as '{actual}'."
            ))
    return diagnostics


def mutable_snapshot_checks(root: Path, path: Path, text: str, meta: FrontMatter | None) -> list[Diagnostic]:
    if not meta or meta.values.get("lifecycle") != "maintained":
        return []
    relative = repo_path(root, path)
    if relative.startswith("engine/algorithms/") or relative.startswith("engineering/archive/") or relative.startswith("engineering/verification/"):
        return []
    diagnostics: list[Diagnostic] = []
    strong_sha = re.compile(
        r"\bcurrent\s+authoritative\b.{0,80}\bcommit\s+[0-9a-f]{7,40}\b.{0,80}\bmust\s+match\b",
        re.IGNORECASE,
    )
    exact_inventory = re.compile(
        r"\b(?:must\s+(?:always\s+)?(?:have|contain|include)|there\s+(?:are|must\s+be))\s+exactly\s+\d+\s+(?:engine\s+)?(?:files?|modules?|tests?|test\s+cases?|routes?|endpoints?)\b",
        re.IGNORECASE,
    )
    fixed_head = re.compile(
        r"\b(?:current|authoritative)\s+(?:git\s+)?head\b.{0,60}\b[0-9a-f]{7,40}\b",
        re.IGNORECASE,
    )
    permanent_version = re.compile(
        r"\b(?:authoritative|permanent(?:ly)?\s+pinned|must\s+match)\b.{0,60}\bv?\d+\.\d+(?:\.\d+)?\b",
        re.IGNORECASE,
    )
    for line_number, line in strip_fenced_code(text):
        if strong_sha.search(line):
            diagnostics.append(Diagnostic(
                "DRIFT001", "ERROR", relative, line_number,
                "Maintained documentation makes a specific commit the Current authoritative contract.",
                "Describe the durable rule and discover the Current revision dynamically; keep commit IDs in evidence."
            ))
        elif exact_inventory.search(line):
            diagnostics.append(Diagnostic(
                "DRIFT002", "WARNING", relative, line_number,
                "Maintained prose appears to freeze an exact mutable inventory count.",
                "Prefer dynamic discovery unless the number is a genuine compatibility/protocol contract."
            ))
        elif fixed_head.search(line):
            diagnostics.append(Diagnostic(
                "DRIFT003", "WARNING", relative, line_number,
                "Maintained prose appears to use a fixed Git HEAD/commit as durable truth.",
                "Keep revision identities in evidence and describe the durable owner/contract instead."
            ))
        elif permanent_version.search(line):
            diagnostics.append(Diagnostic(
                "DRIFT004", "WARNING", relative, line_number,
                "Maintained prose may be treating a mutable version as durable authority.",
                "Confirm this is a real compatibility requirement; otherwise discover the Current version dynamically."
            ))
    return diagnostics


def git_command(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=env,
    )


def tracked_paths(root: Path) -> list[str]:
    probe = git_command(root, "rev-parse", "--is-inside-work-tree")
    if probe.returncode == 0 and probe.stdout.strip() == b"true":
        result = git_command(root, "ls-files", "-z")
        if result.returncode != 0:
            raise VerifierRuntimeError(result.stderr.decode("utf-8", errors="replace").strip() or "git ls-files failed")
        return sorted(
            (entry.decode("utf-8", errors="surrogateescape") for entry in result.stdout.split(b"\0") if entry),
            key=str.casefold,
        )
    paths: list[str] = []
    excluded_parts = {".git", "node_modules", "__pycache__"}
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted([name for name in dirs if name not in excluded_parts], key=str.casefold)
        directory_path = Path(directory)
        for name in sorted(files, key=str.casefold):
            paths.append(repo_path(root, directory_path / name))
    return sorted(paths, key=str.casefold)


def repository_integrity_checks(root: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    required = [
        ".gitignore",
        ".gitattributes",
        "AGENTS.md",
        "engineering/docs/documentation-governance.md",
        "engineering/docs/README.md",
        "engineering/docs/verification/repository-integrity.md",
    ]
    resolver = CaseResolver(root)
    for relative in required:
        status, _resolved, actual = resolver.resolve(PurePosixPath(relative))
        if status == "missing":
            diagnostics.append(Diagnostic(
                "REPO001", "ERROR", relative, None,
                f"Required repository-governance path is missing: {relative}",
                "Restore the maintained owner/configuration path."
            ))
        elif status == "case-mismatch":
            diagnostics.append(Diagnostic(
                "PATH003", "ERROR", relative, None,
                f"Required repository-governance path has incorrect casing: {relative}",
                f"Use exact repository casing; resolved path begins as '{actual}'."
            ))

    folded: dict[str, list[str]] = {}
    for relative in tracked_paths(root):
        folded.setdefault(relative.casefold(), []).append(relative)
    for paths in sorted((sorted(values) for values in folded.values() if len(values) > 1), key=lambda x: x[0].casefold()):
        diagnostics.append(Diagnostic(
            "PATH004", "ERROR", paths[0], None,
            f"Tracked paths collide when compared case-insensitively: {', '.join(paths)}",
            "Resolve the case-only collision explicitly so Windows/Linux checkouts agree."
        ))
    return diagnostics


def changed_paths(root: Path) -> set[str]:
    probe = git_command(root, "rev-parse", "--is-inside-work-tree")
    if probe.returncode != 0 or probe.stdout.strip() != b"true":
        raise VerifierRuntimeError("--mode changed requires a Git working tree.")
    commands = [
        ("diff", "--name-only", "-z"),
        ("diff", "--cached", "--name-only", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ]
    paths: set[str] = set()
    for args in commands:
        result = git_command(root, *args)
        if result.returncode != 0:
            raise VerifierRuntimeError(result.stderr.decode("utf-8", errors="replace").strip() or f"git {' '.join(args)} failed")
        paths.update(
            entry.decode("utf-8", errors="surrogateescape")
            for entry in result.stdout.split(b"\0")
            if entry
        )
    return paths


def verify_repository(root: Path, mode: str = "full") -> Report:
    root = root.resolve()
    documents = iter_governed_documents(root)
    changed = changed_paths(root) if mode == "changed" else None
    diagnostics: list[Diagnostic] = []
    resolver = CaseResolver(root)
    anchor_cache: dict[Path, set[str]] = {}
    meta_by_path = metadata_index(root, documents)

    selected: list[Path] = []
    for path in documents:
        relative = repo_path(root, path)
        if mode == "full" or relative in (changed or set()) or relative == "engineering/docs/README.md":
            selected.append(path)

    for path in selected:
        text = read_text(path)
        metadata_diagnostics, meta = validate_metadata(root, path, text)
        diagnostics.extend(metadata_diagnostics)
        diagnostics.extend(validate_links(root, path, text, resolver, anchor_cache))
        diagnostics.extend(mutable_snapshot_checks(root, path, text, meta))

    superseded: set[str] = set()
    for meta in meta_by_path.values():
        if meta:
            value = meta.values.get("supersedes")
            if isinstance(value, str) and value:
                superseded.add(PurePosixPath(value.replace("\\", "/")).as_posix())

    diagnostics.extend(navigation_checks(root, meta_by_path, resolver))
    diagnostics.extend(ownership_checks(root, meta_by_path, resolver))
    diagnostics.extend(authority_link_checks(root, resolver, superseded))
    diagnostics.extend(validate_links(root, root / "AGENTS.md", read_text(root / "AGENTS.md"), resolver, anchor_cache))
    root_readme = root / "README.md"
    if root_readme.is_file():
        diagnostics.extend(validate_links(root, root_readme, read_text(root_readme), resolver, anchor_cache))
    diagnostics.extend(repository_integrity_checks(root))
    return Report(mode=mode, diagnostics=diagnostics)


def render_human(report: Report, verbose: bool = False) -> str:
    lines = [
        f"TradingBot anti-drift: {report.status}",
        f"Mode: {report.mode}",
        f"Errors: {len(report.by_severity('ERROR'))} | Warnings: {len(report.by_severity('WARNING'))} | Info: {len(report.by_severity('INFO'))}",
    ]
    diagnostics = report.ordered()
    if diagnostics:
        lines.append("")
        for item in diagnostics:
            location = item.file
            if item.line is not None:
                location += f":{item.line}"
            lines.append(f"{item.severity} {item.code} {location} — {item.message}")
            if verbose and item.hint:
                lines.append(f"  hint: {item.hint}")
    return "\n".join(lines)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Read-only TradingBot documentation/repository anti-drift verifier.")
    result.add_argument("--root", help="Explicit TradingBot repository root. Auto-discovered by default.")
    result.add_argument("--mode", choices=("full", "changed"), default="full", help="Full repository validation or local changed-files validation.")
    result.add_argument("--format", choices=("human", "json"), default="human", dest="output_format", help="Diagnostic output format.")
    result.add_argument("--verbose", action="store_true", help="Include remediation hints in human output.")
    return result


def runtime_failure(output_format: str, message: str) -> int:
    diagnostic = Diagnostic("RUN001", "ERROR", ".", None, message, "Fix the verifier/runtime/configuration problem and rerun.")
    report = Report(mode="runtime", diagnostics=[diagnostic])
    if output_format == "json":
        payload = report.to_dict()
        payload["runtime_error"] = True
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_human(report, verbose=True), file=sys.stderr)
    return 2


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = discover_repo_root(args.root)
        report = verify_repository(root, mode=args.mode)
    except (VerifierRuntimeError, OSError) as exc:
        return runtime_failure(args.output_format, str(exc))

    if args.output_format == "json":
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_human(report, verbose=args.verbose))
    return 1 if report.by_severity("ERROR") else 0


if __name__ == "__main__":
    raise SystemExit(main())
