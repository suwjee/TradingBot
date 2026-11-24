"""Read-only source-line E-zone candidate decision observation, not full state proof."""
from __future__ import annotations
import argparse
import ast
import collections
import gzip
import hashlib
import itertools
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from semantic_trace_v9 import execute, stable_object


def markers(source):
    tree = ast.parse(source)
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'EZoneDetector')
    method = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == '_zone')
    loop = next(n for n in method.body if isinstance(n, ast.For) and ast.unparse(n.target) == 'match' and ast.unparse(n.iter) == 'choices')
    rejection = [n for n in loop.body if isinstance(n, ast.If) and ast.unparse(n.test).startswith('self._order_created_only_by_disowned_s(')]
    if len(rejection) != 1 or len(rejection[0].body) != 1 or not isinstance(rejection[0].body[0], ast.Continue):
        raise ValueError('Unexpected candidate rejection structure')
    selection = [n for n in loop.body if isinstance(n, ast.Assign) and ast.unparse(n) == 'order_match = match']
    no_match = [n for n in method.body if isinstance(n, ast.If) and ast.unparse(n.test) == 'order_match is None']
    live = [n for n in method.body if isinstance(n, ast.If) and ast.unparse(n.test) == 'self._live_continuation is not None']
    build = [n for n in method.body if isinstance(n, ast.Return) and isinstance(n.value, ast.Call) and ast.unparse(n.value.func) == 'self._build_zone']
    if any(len(x) != 1 for x in (selection, no_match, live, build)):
        raise ValueError('Unexpected candidate decision topology')
    if ast.unparse(no_match[0].body[0]) != 'return None' or not isinstance(live[0].body[0], ast.Return) or ast.unparse(live[0].body[0].value.func) != 'self._live_continuation.zone':
        raise ValueError('Unexpected no-match or Live route')
    return {rejection[0].body[0].lineno: 'reject_disowned_s', selection[0].lineno: 'select',
            no_match[0].body[0].lineno: 'no_match', live[0].body[0].lineno: 'live_route', build[0].lineno: 'native_route'}


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def exact(value):
    return stable_object(value, max_depth=32, allow_namespace=True)


class Observer:
    def __init__(self, source, stream):
        self.source = source.resolve()
        raw = source.read_bytes()
        self.source_sha = hashlib.sha256(raw).hexdigest()
        self.lines = markers(raw)
        self.stream = stream
        self.ordinal = 0
        self.counts = collections.Counter()
        self.digest = hashlib.sha256()
        self.frames = {}
        self.exceptions = 0

    def emit(self, frame, event, value=None):
        loc = frame.f_locals
        data = {'ordinal': self.ordinal + 1, 'call': self.frames[id(frame)], 'kind': event,
                'direction': loc['self'].direction, 'family': loc['family'], 'number': loc['number'],
                'parent_type': loc['parent_type'], 'parent': exact(loc['parent']),
                'parent_stop_event': exact(loc['stop_event'])}
        if event in ('reject_disowned_s', 'select'):
            data['order_match'] = exact(loc['match'])
            data['prospective_source'] = exact(loc['prospective_source'])
        elif event == 'return':
            data['result'] = exact(value)
        data['source_line'] = frame.f_lineno
        payload = encode(data) + b'\n'
        self.stream.write(payload)
        self.digest.update(payload)
        self.ordinal += 1
        self.counts[event] += 1

    def trace(self, frame, event, arg):
        if event != 'call' or frame.f_code.co_qualname != 'EZoneDetector._zone':
            return None
        if Path(frame.f_code.co_filename).resolve() != self.source:
            return None
        self.frames[id(frame)] = self.counts['call'] + 1
        self.emit(frame, 'call')
        return self.local

    def local(self, frame, event, arg):
        if event == 'line' and frame.f_lineno in self.lines:
            self.emit(frame, self.lines[frame.f_lineno])
        elif event == 'exception':
            self.exceptions += 1
        elif event == 'return':
            self.emit(frame, 'return', arg)
            del self.frames[id(frame)]
        return self.local

    def report(self):
        return {'source_sha256': self.source_sha, 'markers': self.lines, 'events': self.ordinal,
                'counts': dict(self.counts), 'jsonl_sha256': self.digest.hexdigest(),
                'exception_events': self.exceptions, 'unclosed_calls': len(self.frames),
                'coverage': 'Executed EZoneDetector._zone decision lines only; other state and unexecuted branches unproven'}


def compare(a, b):
    """Compare exact ordered semantic payload; source lines are version-specific provenance."""
    def rows(path):
        with gzip.open(path, 'rt', encoding='utf-8') as stream:
            for n, line in enumerate(stream, 1):
                row = json.loads(line)
                if row['ordinal'] != n or 'source_line' not in row:
                    raise ValueError('Noncontiguous ordinal or missing source provenance')
                yield {k: v for k, v in row.items() if k != 'source_line'}
    total = count = partial = 0
    first = None
    for x, y in itertools.zip_longest(rows(a), rows(b)):
        total += 1
        left, right = encode(x), encode(y)
        if b'$unordered_set_NONCANONICAL' in left or b'$unordered_set_NONCANONICAL' in right:
            partial += 1
        if left != right:
            count += 1
            if first is None:
                first = {'ordinal': total, 'original': x, 'v81': y}
    return {'status': 'FAIL' if count or not total else 'INCOMPLETE' if partial else 'PASS', 'compared': total,
            'mismatch_count': count, 'noncanonical_positions': partial, 'first_difference': first,
            'full_semantic_state_status': 'INCOMPLETE', 'scope': 'executed E-zone decision events only; no ordered fields normalized'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--engine-root', type=Path, required=True)
    p.add_argument('--raw', type=Path, required=True)
    p.add_argument('--case', type=Path, required=True)
    p.add_argument('--variant', choices=('original', 'v81'), required=True)
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    case = json.loads(a.case.read_text())
    def verify():
        actual = {f.relative_to(a.engine_root).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest()
                  for package in ('bridge', 'pipeline') for f in (a.engine_root / package).rglob('*.py')}
        with a.raw.open('rb') as f:
            if hashlib.file_digest(f, 'sha256').hexdigest() != case['raw_sha256']:
                raise ValueError('RAW hash drift')
        if actual != case['source_sha256'][a.variant]:
            raise ValueError('Frozen source hash drift')
    verify()
    if sys.gettrace() is not None:
        raise RuntimeError('Existing trace hook is not supported')
    with a.trace.open('xb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0, compresslevel=3) as stream:
            observer = Observer(a.engine_root / 'pipeline/e_zone_detector.py', stream)
            sys.settrace(observer.trace)
            try:
                rc = execute(SimpleNamespace(engine_root=a.engine_root, raw=a.raw,
                    from_time=case['first_time'], to_time=case['last_time'], trace_out=None,
                    stage_profile=None, meter_output=None, summary=None))
            finally:
                sys.settrace(None)
    verify()
    report = observer.report()
    report['native_exit'] = rc
    report['variant'] = a.variant
    report['case'] = case['name']
    with a.trace.open('rb') as f:
        report['gzip_sha256'] = hashlib.file_digest(f, 'sha256').hexdigest()
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    if report['unclosed_calls'] or report['exception_events'] or report['counts'].get('call', 0) != report['counts'].get('return', 0):
        raise ValueError('Incomplete branch observation')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
