# created_at: 2026-09-30T16:20:59+03:30
# last_modified_at: 2026-09-30T20:16:20+03:30
"""Tests for the TradingBot read-only anti-drift verifier."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import posixpath
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("anti_drift.py")
SPEC = importlib.util.spec_from_file_location("tradingbot_anti_drift", MODULE_PATH)
assert SPEC and SPEC.loader
anti_drift = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = anti_drift
SPEC.loader.exec_module(anti_drift)


VALID_TS = "2026-09-30T15:08:41+03:30"
ROADMAP_FILE_ANCHORS = {
    ".editorconfig", ".gitattributes", ".gitignore", "AGENTS.md", "README.md",
    "apps/chart/package.json", "apps/chart/package-lock.json",
    "apps/chart/server/faraz-candle-api.js", "apps/chart/vite.config.js",
    "scripts/launch.bat", "scripts/start.ps1",
}


def frontmatter(title: str = "Example", *, role: str = "reference", lifecycle: str = "maintained", owner: str = "example", timestamp: str = VALID_TS, extra: str = "") -> str:
    return (
        "---\n"
        f"title: {title}\n"
        f"document_role: {role}\n"
        f"lifecycle: {lifecycle}\n"
        f"owner: {owner}\n"
        f"last_modified_at: {timestamp}\n"
        f"{extra}"
        "---\n\n"
    )


class RepoFixture:
    def __init__(self, base: Path) -> None:
        self.root = base
        self.write("AGENTS.md", "# AGENTS\n\n[Documentation](engineering/docs/README.md)\n")
        self.write(".gitignore", "*.tmp\n")
        self.write(".gitattributes", "* text=auto\n")
        self.write("README.md", frontmatter("Root", owner="project-navigation") + "# Root\n\n42 ordinary widgets.\n")
        self.write(
            "engineering/docs/documentation-governance.md",
            frontmatter("Governance", role="normative", owner="documentation") + "# Governance\n",
        )
        self.write(
            "engineering/docs/verification/repository-integrity.md",
            frontmatter("Repository Integrity", role="procedure", owner="repository-integrity") + "# Repository Integrity\n",
        )
        self.write(
            "engineering/docs/README.md",
            frontmatter("Docs", owner="documentation")
            + "# Engineering documentation\n\n"
            + "[Governance](documentation-governance.md)\n\n"
            + "[Repository Integrity](verification/repository-integrity.md)\n",
        )
        self.ensure_roadmap_anchors()
        self.write(
            anti_drift.TECHNICAL_ARCHITECTURE.as_posix(),
            self.roadmap_document(),
        )

    def ensure_roadmap_anchors(self) -> None:
        for anchor in anti_drift.ROADMAP_REQUIRED_ANCHORS:
            path = self.root / anchor
            if anchor in ROADMAP_FILE_ANCHORS:
                if path.exists():
                    continue
                self.write(anchor, "# fixture\n")
            else:
                path.mkdir(parents=True, exist_ok=True)

    def roadmap_document(self, *, omit: set[str] | None = None) -> str:
        omit = omit or set()
        source_parent = anti_drift.TECHNICAL_ARCHITECTURE.parent.as_posix()
        rows = []
        for anchor in anti_drift.ROADMAP_REQUIRED_ANCHORS:
            if anchor in omit:
                continue
            target = posixpath.relpath(anchor, start=source_parent)
            rows.append(f"| [`{anchor}`]({target}) | fixture-owner | fixture purpose |")
        return (
            frontmatter("Technical Architecture", owner="architecture")
            + "# Technical Architecture\n\n"
            + "## Current Project Path Roadmap\n\n"
            + "| Current path | Owner / subsystem | Purpose and authority role |\n"
            + "| --- | --- | --- |\n"
            + "\n".join(rows)
            + "\n"
        )

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


def diagnostic_codes(report) -> set[str]:
    return {item.code for item in report.diagnostics}


def tree_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda p: p.as_posix()):
        result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


class AntiDriftTests(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], RepoFixture]:
        temp = tempfile.TemporaryDirectory()
        return temp, RepoFixture(Path(temp.name))

    def test_valid_maintained_document_passes(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/example.md", frontmatter() + "# Example\n")
        report = anti_drift.verify_repository(repo.root)
        self.assertEqual([], report.by_severity("ERROR"))

    def test_valid_project_path_roadmap_passes(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        codes = diagnostic_codes(anti_drift.verify_repository(repo.root))
        self.assertFalse({code for code in codes if code.startswith("ROADMAP")})

    def test_missing_project_path_roadmap_fails(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write(
            anti_drift.TECHNICAL_ARCHITECTURE.as_posix(),
            frontmatter("Technical Architecture", owner="architecture") + "# Technical Architecture\n",
        )
        self.assertIn("ROADMAP001", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_required_project_path_anchor_omission_fails(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write(
            anti_drift.TECHNICAL_ARCHITECTURE.as_posix(),
            repo.roadmap_document(omit={"engine/tests"}),
        )
        self.assertIn("ROADMAP002", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_missing_required_project_path_anchor_fails(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        (repo.root / "apps/chart/vite.config.js").unlink()
        self.assertIn("ROADMAP003", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_historical_roadmap_does_not_replace_current_roadmap(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write(
            "engineering/archive/old-architecture.md",
            "# Historical\n\n## Current Project Path Roadmap\n",
        )
        repo.write(
            anti_drift.TECHNICAL_ARCHITECTURE.as_posix(),
            frontmatter("Technical Architecture", owner="architecture") + "# Technical Architecture\n",
        )
        self.assertIn("ROADMAP001", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_missing_required_metadata_fails(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/example.md", "---\ntitle: Example\nlifecycle: maintained\n---\n# Example\n")
        report = anti_drift.verify_repository(repo.root)
        self.assertIn("META003", diagnostic_codes(report))

    def test_malformed_timestamp_fails(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/example.md", frontmatter(timestamp="not-a-date") + "# Example\n")
        self.assertIn("TIME001", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_timestamp_missing_seconds_fails(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/example.md", frontmatter(timestamp="2026-09-30T15:08+03:30") + "# Example\n")
        self.assertIn("TIME001", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_timestamp_missing_timezone_fails(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/example.md", frontmatter(timestamp="2026-09-30T15:08:41") + "# Example\n")
        self.assertIn("TIME001", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_broken_internal_markdown_link_fails(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/example.md", frontmatter() + "# Example\n\n[Missing](missing.md)\n")
        self.assertIn("LINK001", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_path_case_mismatch_is_detected(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/Target.md", frontmatter("Target") + "# Target\n")
        repo.write("engineering/docs/example.md", frontmatter() + "# Example\n\n[Target](target.md)\n")
        self.assertIn("PATH001", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_valid_relative_link_passes(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/target.md", frontmatter("Target") + "# Target\n")
        repo.write("engineering/docs/example.md", frontmatter() + "# Example\n\n[Target](target.md)\n")
        report = anti_drift.verify_repository(repo.root)
        self.assertNotIn("LINK001", diagnostic_codes(report))
        self.assertNotIn("PATH001", diagnostic_codes(report))

    def test_historical_archive_is_not_treated_as_current_document(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write(
            "engineering/archive/history.md",
            frontmatter("History", role="evidence", lifecycle="historical", owner="history")
            + "# History\n\nCurrent authoritative architecture is commit abc1234 and must match this SHA.\n",
        )
        repo.write("engineering/docs/example.md", frontmatter() + "# Example\n\n[Historical evidence](../archive/history.md)\n")
        report = anti_drift.verify_repository(repo.root)
        self.assertNotIn("DRIFT001", diagnostic_codes(report))
        self.assertEqual([], report.by_severity("ERROR"))

    def test_algorithm_reference_version_and_hash_content_is_excluded(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write(
            "engine/algorithms/TradingBot_Bullish_Algorithm_Reference_V99.1_Source_Synchronized.md",
            "# Algorithm Reference\n\nVersion 99.1\nSHA-256: abcdef1234567890\nCurrent authoritative architecture is commit abc1234 and must match this SHA.\n",
        )
        report = anti_drift.verify_repository(repo.root)
        self.assertNotIn("DRIFT001", diagnostic_codes(report))

    def test_graphify_archive_is_excluded_from_maintained_rules(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write(
            "engineering/archive/repository-graphify/graph.json",
            '{"files": 999999, "sha": "abcdef1234567890"}\n',
        )
        report = anti_drift.verify_repository(repo.root)
        self.assertEqual([], report.by_severity("ERROR"))

    def test_navigation_to_missing_document_fails(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write(
            "engineering/docs/README.md",
            frontmatter("Docs", owner="documentation") + "# Docs\n\n[Missing owner](missing-owner.md)\n",
        )
        report = anti_drift.verify_repository(repo.root)
        self.assertIn("LINK001", diagnostic_codes(report))

    def test_machine_readable_json_output_is_valid(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        completed = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--root", str(repo.root), "--format", "json"],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("PASS", payload["status"])
        self.assertEqual({"diagnostics", "errors", "info", "warnings"}, set(payload["summary"]))

    def test_diagnostics_are_deterministically_ordered(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/z.md", frontmatter("Z") + "# Z\n\n[Missing](z-missing.md)\n")
        repo.write("engineering/docs/a.md", frontmatter("A") + "# A\n\n[Missing](a-missing.md)\n")
        first = [item.sort_key() for item in anti_drift.verify_repository(repo.root).ordered()]
        second = [item.sort_key() for item in anti_drift.verify_repository(repo.root).ordered()]
        self.assertEqual(first, second)
        self.assertEqual(first, sorted(first))

    def test_verifier_does_not_modify_inspected_files(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/example.md", frontmatter() + "# Example\n")
        before = tree_hashes(repo.root)
        anti_drift.verify_repository(repo.root)
        after = tree_hashes(repo.root)
        self.assertEqual(before, after)

    def test_compatibility_version_is_not_a_snapshot_warning(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write(
            "engineering/docs/example.md",
            frontmatter() + "# Example\n\nCompatibility requires Python 3.12+ for this interface.\n",
        )
        self.assertNotIn("DRIFT004", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_historical_sha_is_not_scanned(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/archive/audit.md", "# Audit\n\nCommit abcdef1234567890 was observed.\n")
        self.assertEqual([], anti_drift.verify_repository(repo.root).by_severity("ERROR"))

    def test_code_block_old_path_is_not_an_active_link(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write(
            "engineering/docs/example.md",
            frontmatter() + "# Example\n\n```text\n[Old](missing-old-path.md)\n```\n",
        )
        self.assertNotIn("LINK001", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_maintained_specific_commit_authority_is_error(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write(
            "engineering/docs/example.md",
            frontmatter() + "# Example\n\nCurrent authoritative architecture is commit abc1234 and must match this SHA.\n",
        )
        self.assertIn("DRIFT001", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_superseded_navigation_target_is_error(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/archive/old.md", "# Old\n")
        repo.write(
            "engineering/docs/current.md",
            frontmatter("Current", extra="supersedes: engineering/archive/old.md\n") + "# Current\n",
        )
        repo.write(
            "engineering/docs/README.md",
            frontmatter("Docs", owner="documentation") + "# Docs\n\n[Old](../archive/old.md)\n",
        )
        self.assertIn("STALE001", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_superseded_document_cannot_remain_maintained(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/old.md", frontmatter("Old", owner="old-owner") + "# Old\n")
        repo.write(
            "engineering/docs/current.md",
            frontmatter("Current", owner="current-owner", extra="supersedes: engineering/docs/old.md\n")
            + "# Current\n",
        )
        self.assertIn("OWN001", diagnostic_codes(anti_drift.verify_repository(repo.root)))

    def test_changed_mode_checks_changed_maintained_document(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/example.md", frontmatter() + "# Example\n")
        subprocess.run(["git", "init", "-q", str(repo.root)], check=True)
        subprocess.run(["git", "-C", str(repo.root), "config", "user.email", "phase7@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(repo.root), "config", "user.name", "Phase 7 Test"], check=True)
        subprocess.run(["git", "-C", str(repo.root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo.root), "commit", "-qm", "fixture"], check=True)
        repo.write("engineering/docs/example.md", frontmatter() + "# Example\n\n[Missing](missing.md)\n")
        report = anti_drift.verify_repository(repo.root, mode="changed")
        self.assertIn("LINK001", diagnostic_codes(report))

    def test_cli_exit_codes_distinguish_violation_and_runtime_failure(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        repo.write("engineering/docs/example.md", frontmatter() + "# Example\n\n[Missing](missing.md)\n")
        violation = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--root", str(repo.root), "--format", "json"],
            check=False, text=True, capture_output=True,
        )
        self.assertEqual(1, violation.returncode)
        missing_root = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--root", str(repo.root / "missing"), "--format", "json"],
            check=False, text=True, capture_output=True,
        )
        self.assertEqual(2, missing_root.returncode)
        self.assertTrue(json.loads(missing_root.stdout)["runtime_error"])

    def test_json_output_is_byte_deterministic_for_unchanged_repo(self) -> None:
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        command = [sys.executable, str(MODULE_PATH), "--root", str(repo.root), "--format", "json"]
        first = subprocess.run(command, check=True, text=True, capture_output=True).stdout
        second = subprocess.run(command, check=True, text=True, capture_output=True).stdout
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
