"""Exercise actual frozen _zone decision loop with controlled route providers.

These fixtures test explicit rejection and Live dispatch, not real RAW behavior
or the complete implementations of dependency methods.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta
from decimal import Decimal
import gzip
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from e_zone_decision_trace import Observer, compare
from run_verified_trace_pair_v9 import source_check


class ControlledDetector:
    def __init__(self, *, reject, live, direction, now):
        self.direction = direction
        self.range_end = now + timedelta(hours=1)
        self._live_continuation = SimpleNamespace(zone=lambda *args: self._build_zone(*args[1:])) if live else None
        self._accepted_e_source_identities = set()
        self._registered_e_parent_stops = None
        self.order_audit = {}
        self.reject = reject
        self.now = now
        self.orders = [self.order(7, '100.010'), self.order(9, '100.020')]

    def order(self, first, price):
        order = SimpleNamespace(first_idx=first, break_idx=first+1, mode='test')
        # Match layout from actual _build_zone unpacking, including crossing
        # time and causes. Earliest stop belongs to first=7.
        t = self.now + timedelta(seconds=first)
        return (first, order, t, Decimal(price), first, self.now,
                (first, t, t), ('parent-stop',), self.now)

    def _unconsumed_s_orders(self, *args): return []
    def _gate_owned_initial_order(self, *args): return None
    def _carried_orders_for_parent(self, *args): return []
    def _register_order_audit(self, *args): return None
    def _iter_post_stop_accepted_orders(self, *args): return iter(())
    def order_candidates(self, *args, **kwargs): return list(self.orders)
    def _extreme_between(self, start, end): return 3, start, Decimal('99.990')
    def _order_created_only_by_disowned_s(self, identity, *args): return identity[0] in self.reject
    def _build_zone(self, family, number, parent_type, parent, stop_event, match, prospective):
        return SimpleNamespace(family=family, number=number, parent_type=parent_type,
                               order_first_index=match[1].first_idx, price=prospective[2])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--engine-root', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--variant', choices=('original','v81'), required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    expected = json.loads(a.manifest.read_text())['source_sha256'][a.variant]
    source_check(a.engine_root, expected)
    sys.path.insert(0, str(a.engine_root/'pipeline'))
    from e_zone_detector import EZoneDetector
    now = datetime(2026, 1, 1, 0, 0)
    parent = SimpleNamespace(source_index=1, source_time=now, decision_event_time=now, price=Decimal('100.000'), family='test', number=1)
    results = []
    with a.trace.open('xb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as stream:
        observer = Observer(a.engine_root/'pipeline/e_zone_detector.py', stream)
        sys.settrace(observer.trace)
        try:
            for direction in ('bullish', 'bearish'):
                for name, reject, live, wanted in [('reject_first_select_next', {7}, False, 9), ('reject_all', {7,9}, False, None), ('live_dispatch', set(), True, 7)]:
                    d = ControlledDetector(reject=reject, live=live, direction=direction, now=now)
                    result = EZoneDetector._zone(d, 'test', 1, 'S', parent, now)
                    got = None if result is None else result.order_first_index
                    if got != wanted:
                        raise AssertionError(f'{name} {direction}: {got} != {wanted}')
                    results.append({'direction':direction,'case':name,'selected_first_index':got,'status':'PASS'})
        finally:
            sys.settrace(None)
    source_check(a.engine_root, expected)
    report=observer.report()
    report['fixtures']=results
    report['variant']=a.variant
    report['scope']='Actual pinned _zone loop with controlled dependencies; not a RAW run or universal Live proof.'
    if report['unclosed_calls'] or report['exception_events'] or not all(report['counts'].get(name, 0) for name in observer.lines.values()):
        raise AssertionError('Missing controlled branch coverage')
    a.report.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
