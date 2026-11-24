"""Fused exact selected-event comparator and legacy integrity audit.

One decompression/JSON decode of each main event stream. All existing sidecar
checks still run. Exact canonical byte comparison, not digest-only equivalence.
The capture schema and full-semantic coverage status are deliberately unchanged.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from audit_trace_coverage import iter_inspected, SCHEMAS
from strict_trace_gate_v9 import Stream, SCHEMA, unique, invalid_constant, compare_streams
from verify_streamed_stage_sidecars import audit as audit_stage

SCHEMAS.add(SCHEMA)


def strict_decode(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique, parse_constant=invalid_constant)


class AuditedStream(Stream):
    def __init__(self, path):
        super().__init__(path)
        self.integrity = None

    def rows(self):
        self.integrity = yield from iter_inspected(self.path, decode=strict_decode, fast_marker=True)


def audit_pair(original, candidate):
    """Return exact comparator report and all integrity reports; fail closed.

    No PASS unless both main streams reach verified EOF, and all sidecars pass.
    Exceptions from integrity auditing are deliberately propagated.
    """
    streams = [AuditedStream(original), AuditedStream(candidate)]
    comparison = compare_streams(*streams, fast_equal=True)
    if any(s.integrity is None for s in streams):
        raise ValueError(f'Incomplete or invalid main trace: {comparison}')
    reports = []
    for stream in streams:
        main = stream.integrity
        stage = audit_stage(Path(str(stream.path) + '.manifest.json'))
        if main['integrity'] != 'PASS' or main['missing_required'] or stage['status'] != 'PASS_INTEGRITY_ONLY':
            raise ValueError(f'Trace/sidecar integrity failed: {stream.path}')
        reports.append({'integrity': main, 'stage_integrity': stage})
    return {'comparison': comparison, 'reports': reports}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original', type=Path); p.add_argument('candidate', type=Path)
    p.add_argument('--out', required=True, type=Path)
    a=p.parse_args()
    result=audit_pair(a.original,a.candidate)
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    return {'PASS':0,'FAIL':1,'INCOMPLETE':2}[result['comparison']['selected_event_status']]

if __name__=='__main__':
    raise SystemExit(main())
