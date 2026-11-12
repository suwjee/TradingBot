"""Audit-tool contract tests; production Source and RAW are never mutated."""
from __future__ import annotations
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import matrix
from instrumented import GraphSnapshot


class ComparisonTests(unittest.TestCase):
    def test_only_timing_envelope_is_excluded(self):
        a = b'{"version":"1","directions":{},"timings":{"x":1}}'
        b = b'{"version":"1","directions":{},"timings":{"x":9}}'
        self.assertEqual(matrix.stable_bytes(a), matrix.stable_bytes(b))
        self.assertNotEqual(matrix.stable_bytes(a), matrix.stable_bytes(a.replace(b'"1"', b'"2"')))

    def test_numeric_representation_and_key_order_remain_differences(self):
        self.assertNotEqual(matrix.stable_bytes(b'{"x":1}'), matrix.stable_bytes(b'{"x":1.0}'))
        self.assertIsNotNone(matrix.first_diff({"x": 1}, {"x": 1.0}))
        self.assertIsNotNone(matrix.first_diff({"a": 1, "b": 2}, {"b": 2, "a": 1}))

    def test_absence_null_and_array_order_remain_differences(self):
        self.assertIsNotNone(matrix.first_diff({}, {"x": None}))
        self.assertIsNotNone(matrix.first_diff([1, 2], [2, 1]))

    def test_alias_changes_are_visible_for_mutable_sets(self):
        item = {1, 2}
        shared = GraphSnapshot().encode([item, item])
        distinct = GraphSnapshot().encode([{1, 2}, {1, 2}])
        self.assertNotEqual(shared, distinct)

    def test_slot_only_values_are_retained(self):
        class Item:
            __slots__ = ("price",)
        a, b = Item(), Item()
        a.price, b.price = "1.00", "1.0"
        self.assertNotEqual(GraphSnapshot().encode(a), GraphSnapshot().encode(b))


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=matrix.ROOT / "apps/chart/state/tmp")
        self.root = Path(self.directory.name)
        (self.root / "engine").mkdir()
        (self.root / "engine/__init__.py").write_bytes(b"")
        self.evidence = self.root / "evidence"
        (self.evidence / "discovery").mkdir(parents=True)
        initial = [{"path": "engine/__init__.py", "sha256": hashlib.sha256(b"").hexdigest()}]
        matrix.save(self.evidence / "discovery/source-manifest-before.json", initial)
        self.replacement = patch.object(matrix, "EVIDENCE", self.evidence)
        self.replacement.start()

    def tearDown(self):
        self.replacement.stop()
        self.directory.cleanup()

    def test_phase_source_mutation_rejects_resume(self):
        matrix.phase_source_guard("before", self.root)
        (self.root / "engine/__init__.py").write_bytes(b"# change")
        with self.assertRaisesRegex(RuntimeError, "Source changed"):
            matrix.phase_source_guard("before", self.root)

    def test_candidate_cannot_reuse_unknown_source_evidence(self):
        target = self.evidence / "candidate"
        target.mkdir()
        (target / "old.metrics.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "retroactively"):
            matrix.phase_source_guard("candidate", self.root)

    def test_before_does_not_accept_different_initial_source(self):
        (self.root / "engine/__init__.py").write_bytes(b"# change")
        with self.assertRaisesRegex(RuntimeError, "original pre-edit"):
            matrix.phase_source_guard("before", self.root)

    def test_resume_cannot_change_the_compared_baseline_phase(self):
        source = matrix.phase_source_guard("after", self.root)
        raw = self.root / "raw.json"
        raw.write_bytes(b"[]")
        case = {"id": "case", "input": str(raw), "timeframe": 30,
                "from_time": 0, "to_time": 30, "direction": "bullish"}
        target = self.evidence / "after/case"
        target.mkdir()
        matrix.save(target / "run-01.metrics.json", {
            "command": matrix.command(case, self.root),
            "input_sha256_before": matrix.file_sha(raw), "source_manifest": source,
            "explicit_hash_seed": None, "baseline_phase": "repaired-before",
        })
        with self.assertRaisesRegex(RuntimeError, "does not match current request"):
            matrix.run(case, "after", 1, 1800, self.root, "before")

    def test_resume_cannot_change_the_bytecode_cache_control(self):
        source = matrix.phase_source_guard("after", self.root)
        raw = self.root / "raw.json"
        raw.write_bytes(b"[]")
        case = {"id": "case", "input": str(raw), "timeframe": 30,
                "from_time": 0, "to_time": 30, "direction": "bullish"}
        target = self.evidence / "after/case"
        target.mkdir()
        matrix.save(target / "run-01.metrics.json", {
            "command": matrix.command(case, self.root),
            "input_sha256_before": matrix.file_sha(raw), "source_manifest": source,
            "explicit_hash_seed": None, "baseline_phase": "after", "pycache_prefix": None,
        })
        with self.assertRaisesRegex(RuntimeError, "does not match current request"):
            matrix.run(case, "after", 1, 1800, self.root, "after", pycache_prefix="different-empty-cache-root")


if __name__ == "__main__":
    unittest.main()
