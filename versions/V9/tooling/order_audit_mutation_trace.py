"""Observe two authoritative OrderAudit mutation sites, without replacing source or classes."""
from __future__ import annotations
import argparse
import ast
import collections
import gzip
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from e_zone_decision_trace import exact, encode
from run_verified_trace_pair_v9 import source_check, hash_file
from semantic_trace_v9 import execute


def sites(raw):
    tree = ast.parse(raw)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'OrderAuditEngineMixin')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_register_order_audit')
    a = [n for n in ast.walk(fn) if isinstance(n, ast.Assign) and ast.unparse(n) == 'ledger[key] = entry']
    b = [n for n in ast.walk(fn) if isinstance(n, ast.Expr) and ast.unparse(n) == 'audit_causes.add(cause)']
    if len(a) != 1 or len(b) != 1:
        raise ValueError('OrderAudit mutation topology changed')
    return {a[0].lineno: 'insert_order', b[0].lineno: 'add_parent_cause'}


class LedgerObserver:
    def __init__(self, source, stream):
        self.source = source.resolve()
        raw = source.read_bytes()
        self.lines = sites(raw)
        self.sha = hashlib.sha256(raw).hexdigest()
        self.stream = stream
        self.pending = {}
        self.counts = collections.Counter()
        self.ordinal = 0
        self.digest = hashlib.sha256()

    def trace(self, frame, event, arg):
        if event != 'call' or frame.f_code.co_qualname != 'OrderAuditEngineMixin._register_order_audit':
            return None
        if Path(frame.f_code.co_filename).resolve() != self.source:
            return None
        self.counts['physical_calls'] += 1
        return self.local

    def local(self, frame, event, arg):
        if event not in ('line', 'return', 'exception'):
            return self.local
        ident = id(frame)
        if ident in self.pending:
            row, before, owner, key, added = self.pending.pop(ident)
            if event == 'exception':
                raise ValueError('Observed mutation raised before completion')
            if row['kind'] == 'insert_order':
                if type(owner) is not dict or owner.get(key) is not added or len(owner) != before + 1:
                    raise ValueError('Order insertion postcondition failed')
                row['post_count'] = len(owner)
            else:
                if type(owner) is not set or owner != before | {added} or len(owner) != len(before)+1:
                    raise ValueError('Parent cause addition postcondition failed')
                row['post_count'] = len(owner)
                row['post_members_observed_iteration'] = exact(list(owner))
            payload = encode(row)+b'\n'
            self.stream.write(payload)
            self.digest.update(payload)
            self.ordinal += 1
            self.counts[row['kind']] += 1
        if event != 'line' or frame.f_lineno not in self.lines:
            return self.local
        loc=frame.f_locals
        kind=self.lines[frame.f_lineno]
        key=loc['key']
        row={'ordinal': self.ordinal+1, 'kind': kind, 'direction': loc['self'].direction,
             'order_identity': exact(key), 'parent_type': loc['parent_type'],
             'parent_source_index': exact(loc['parent'].source_index), 'parent_source_time': exact(loc['parent'].source_time),
             'parent_stop': exact(loc['parent_stop']), 'source_line': frame.f_lineno}
        if kind=='insert_order':
            owner, added=loc['ledger'],loc['entry']
            if type(owner) is not dict or key in owner or type(added['causes']) is not set or added['causes']:
                raise ValueError('Unexpected ledger insertion precondition')
            before=len(owner)
            row['pre_count']=before
            row['entry']=exact({k:v for k,v in added.items() if k!='causes'})
            row['causes_exact_empty_set']=True
        else:
            owner,added=loc['audit_causes'],loc['cause']
            if type(owner) is not set or added in owner:
                raise ValueError('Unexpected cause addition precondition')
            before=frozenset(owner)
            row['pre_count']=len(before)
            # No sorting: save exact observed set iteration separately. The
            # actual addition itself has a chronological order and full identity.
            row['pre_members_observed_iteration']=exact(list(owner))
            row['cause']=exact(added)
        self.pending[ident]=(row,before,owner,key,added)
        return self.local


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--engine-root', type=Path, required=True)
    p.add_argument('--raw', type=Path, required=True)
    p.add_argument('--case', type=Path, required=True)
    p.add_argument('--variant', choices=('original','v81'),required=True)
    p.add_argument('--trace',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args();case=json.loads(a.case.read_text())
    source_check(a.engine_root,case['source_sha256'][a.variant])
    if hash_file(a.raw)!=case['raw_sha256'] or sys.gettrace() is not None:
        raise ValueError('Input hash or trace precondition failed')
    with a.trace.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0,compresslevel=3) as stream:
        observer=LedgerObserver(a.engine_root/'pipeline/order_audit_engine.py',stream)
        sys.settrace(observer.trace)
        try:
            rc=execute(SimpleNamespace(engine_root=a.engine_root,raw=a.raw,from_time=case['first_time'],to_time=case['last_time'],trace_out=None,stage_profile=None,meter_output=None,summary=None))
        finally:sys.settrace(None)
    source_check(a.engine_root,case['source_sha256'][a.variant])
    if hash_file(a.raw)!=case['raw_sha256'] or observer.pending or rc:
        raise ValueError('Execution or source/RAW postcondition failed')
    report={'variant':a.variant,'native_exit':rc,'source_sha256':observer.sha,'sites':observer.lines,
            'counts':dict(observer.counts),'events':observer.ordinal,'jsonl_sha256':observer.digest.hexdigest(),
            'gzip_sha256':hash_file(a.trace),'scope':'Only two _register_order_audit mutation sites; not full ledger, cache or Live state coverage.'}
    a.report.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
