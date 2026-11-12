"""Guard exact lexical preservation and narrow telemetry exclusion."""
import unittest
import contextlib
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import lexical_output_check as lexical
from matrix import ROOT, sha
from lexical_output_check import stable_serialized_bytes as stable


class LexicalOutputTests(unittest.TestCase):
    def test_empty_stdout_requires_an_explicit_non_json_error_path(self):
        with self.assertRaises(ValueError):
            stable(b" \r\n")

    def test_only_timing_value_changes_are_ignored(self):
        self.assertEqual(stable(b'{"a":1,"timings":{"t":1},"b":2}\n'), stable(b'{"a":1,"timings":{"t":999.55},"b":2}\n'))

    def test_equivalent_number_lexemes_are_different(self):
        self.assertNotEqual(stable(b'{"a":1e0}'), stable(b'{"a":1.0}'))

    def test_equivalent_string_escapes_are_different(self):
        self.assertNotEqual(stable(b'{"a":"a"}'), stable(b'{"a":"\\u0061"}'))

    def test_whitespace_is_preserved(self):
        self.assertNotEqual(stable(b'{"a":1}'), stable(b'{ "a":1}'))

    def test_key_presence_order_and_nested_timings_are_preserved(self):
        self.assertNotEqual(stable(b'{"a":1}'), stable(b'{"a":1,"timings":{}}'))
        self.assertNotEqual(stable(b'{"a":1,"b":2}'), stable(b'{"b":2,"a":1}'))
        self.assertNotEqual(stable(b'{"a":{"timings":1}}'), stable(b'{"a":{"timings":2}}'))

    def test_quoted_brackets_and_utf8_are_preserved(self):
        self.assertEqual(stable('{"a":"[] } \\" فارسی","timings":{}}'.encode()), '{"a":"[] } \\" فارسی","timings":null}'.encode())

    def test_duplicate_keys_fail_closed(self):
        with self.assertRaises(ValueError):
            stable(b'{"a":1,"a":2}')

    def test_missing_required_repeat_is_incomplete_even_if_present_repeat_matches(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "apps/chart/state/tmp") as directory:
            evidence = Path(directory)
            (evidence / "discovery").mkdir()
            (evidence / "discovery/workloads.json").write_text(json.dumps([{"id": "case", "repeats": 2}]))
            (evidence / "discovery/collection-policy.json").write_text(json.dumps({"required_repeats": {"after": {"case": 2}}}))
            raw = b'{"a":1,"timings":{}}'
            meta = {"status": "PASS", "raw_output_sha256": sha(raw), "input_sha256_before": "same-input",
                    "command": ["python", "-B", "bridge.py", "--timeframe", "30"], "baseline_phase": "repaired-before"}
            for phase in ["repaired-before", "after"]:
                target = evidence / phase / "case"
                target.mkdir(parents=True)
                (target / "run-01.stdout.json").write_bytes(raw)
                (target / "run-01.metrics.json").write_text(json.dumps(meta))
            with patch.object(lexical, "EVIDENCE", evidence), patch("sys.argv", ["lexical"]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(lexical.main(), 1)
            result = json.loads((evidence / "discovery/lexical-repaired-before-vs-after.json").read_bytes())
            self.assertEqual(result["status"], "INCOMPLETE")
            self.assertEqual([item["status"] for item in result["comparisons"]], ["PASS", "INCOMPLETE"])


if __name__ == "__main__":
    unittest.main()
