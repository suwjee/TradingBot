import gzip
import json
import tempfile
import unittest
from pathlib import Path
from e_zone_decision_trace import compare, markers
from summarize_synthetic_execution import summarize
from order_audit_mutation_trace import sites
from live_protocol_trace import stable_messages
from run_verified_trace_pair_v9 import source_check
import hashlib

SOURCE = '''class EZoneDetector:
    def _zone(self, choices):
        for match in choices:
            if self._order_created_only_by_disowned_s(match):
                continue
            order_match = match
            break
        if order_match is None:
            return None
        if self._live_continuation is not None:
            return self._live_continuation.zone(order_match)
        return self._build_zone(order_match)
'''


class DecisionTraceTests(unittest.TestCase):
    def test_all_markers_and_guard_drift(self):
        self.assertEqual(set(markers(SOURCE).values()), {'reject_disowned_s', 'select', 'no_match', 'live_route', 'native_route'})
        with self.assertRaises(ValueError):
            markers(SOURCE.replace('continue', 'break'))

    def test_comparator_mutations(self):
        a = [{'ordinal': 1, 'kind': 'reject_disowned_s', 'price': {'$decimal': '1.000'}, 'source_line': 10},
             {'ordinal': 2, 'kind': 'return', 'result': None, 'source_line': 11}]
        with tempfile.TemporaryDirectory() as root:
            x, y = Path(root) / 'x.gz', Path(root) / 'y.gz'
            def write(path, rows):
                with gzip.open(path, 'wt') as f:
                    for row in rows:
                        f.write(json.dumps(row) + '\n')
            write(x, a)
            for label, rows, status in [
                ('source line only', [{**a[0], 'source_line': 99}, a[1]], 'PASS'),
                ('decimal scale', [{**a[0], 'price': {'$decimal': '1.00'}}, a[1]], 'FAIL'),
                ('decision', [{**a[0], 'kind': 'select'}, a[1]], 'FAIL'),
                ('missing return', [a[0]], 'FAIL'),
                ('order', [{**a[1], 'ordinal': 1}, {**a[0], 'ordinal': 2}], 'FAIL'),
            ]:
                with self.subTest(label=label):
                    write(y, rows)
                    self.assertEqual(compare(x, y)['status'], status)
            a[0]['price'] = {'$unordered_set_NONCANONICAL': [1, 2]}
            write(x, a); write(y, a)
            self.assertEqual(compare(x, y)['status'], 'INCOMPLETE')

    def test_execution_summary_fail_closed(self):
        case = {'records': 1000000, 'raw_sha256': 'a', 'stable_output_sha256': 'b'}
        pair = {'status': 'INCOMPLETE', 'stable_output_status': 'PASS', 'selected_event_status': 'INCOMPLETE',
                'rows': [{'variant': v, 'native_exit': 0, 'integrity': 'PASS', 'stable_sha256': 'b'} for v in ('original', 'v81')]}
        with tempfile.TemporaryDirectory() as root:
            d = Path(root)
            for changes, code, expected in [(pair, 2, True), ({**pair, 'rows': pair['rows'][:1]}, 2, False),
                                             ({**pair, 'selected_event_status': 'FAIL'}, 1, False), (pair, 137, False)]:
                (d / 'pair_report.json').write_text(json.dumps(changes))
                s, result = summarize(d, case, code)
                self.assertEqual(result, expected)
                self.assertEqual(s['full_semantic_state_status'], 'INCOMPLETE')

    def test_order_audit_site_mapping(self):
        source = "class OrderAuditEngineMixin:\n    def _register_order_audit(self):\n        ledger[key] = entry\n        audit_causes.add(cause)\n"
        self.assertEqual(set(sites(source).values()), {'insert_order', 'add_parent_cause'})
        with self.assertRaises(ValueError):
            sites(source.replace('audit_causes.add(cause)', 'audit_causes.clear()'))

    def test_exact_live_telemetry_boundary(self):
        payload = b'{"timeframe":30,"directions":{"bullish":{"price":"1.000"},"bearish":{}},"timings":{"phasesMs":{"A":1.0},"bridgeTotalMs":2.0}}'
        a = b'{"type":"update","payload":' + payload + b'}\n'
        stable, schema, _ = stable_messages(a)
        self.assertEqual(stable_messages(a.replace(b'2.0', b'7.0'))[:2], (stable, schema))
        self.assertNotEqual(stable_messages(a.replace(b'1.000', b'1.00'))[0], stable)
        with self.assertRaises(ValueError):
            stable_messages(a.replace(b'2.0', b'true'))

    def test_pinned_runtime_source_closure_excludes_test_files(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            for dirname in ('bridge', 'pipeline', 'tests'):
                (root / dirname).mkdir()
            f = root / 'bridge' / 'source.py'; f.write_bytes(b'x = 1\n')
            (root / 'tests' / 'test_source.py').write_text('assert True\n')
            expected = {'bridge/source.py': hashlib.sha256(f.read_bytes()).hexdigest()}
            self.assertEqual(source_check(root, expected), 1)
            (root / 'pipeline' / 'unexpected.py').write_text('x = 2\n')
            with self.assertRaises(ValueError):
                source_check(root, expected)


if __name__ == '__main__':
    unittest.main()
