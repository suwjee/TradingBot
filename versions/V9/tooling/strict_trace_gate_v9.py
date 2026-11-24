#!/usr/bin/env python3
"""V9 test-only gate: strict byte-level selected-event comparison.

A PASS in selected_event_status is never a full semantic-state proof. Unknown
input differences fail; unsupported or nondeterministic encodings remain
INCOMPLETE. Known V8.1 call-hint drift is independently counted, not erased.
The excluded physical implementation calls are counted, not silently hidden.
"""
from __future__ import annotations
import argparse, collections, copy, gzip, hashlib, itertools, json
from pathlib import Path
from global_semantic_trace_compare_v9 import IMPL_ONLY

SCHEMA = 'tradingbot.v9.internal-observer.v9'
BOUNDARY = {'timed.stage_start', 'timed.stage_end'}
REP_STATUSES = {'partial_unrepresentable', 'unsupported', 'unclassified'}

def unique(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError(f'duplicate key {k!r}')
        result[k] = v
    return result

def invalid_constant(value):
    raise ValueError(f'nonfinite value: {value}')

def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')

def check_rep(value, loc, issues):
    if isinstance(value, dict):
        status = value.get('status')
        if isinstance(status, str) and status in REP_STATUSES:
            issues[f'{loc}:{status}'] += 1
        for k, v in value.items():
            if k in ('$unordered_set_NONCANONICAL', '$unrepresentable'):
                issues[f'{loc}:{k}'] += 1
            check_rep(v, loc, issues)
    elif isinstance(value, list):
        for v in value:
            check_rep(v, loc, issues)

def exact_call_hint(a, b):
    """Only the source-audited V8.1 `_zone` extra physical-registration hint.
    Same all other payload fields required by caller. No normalization of prices,
    state, semantic results or input ordering; exact byte comparison after removal.
    """
    if a.get('stage') != 'e_zone_detector' or a.get('method') != 'EZoneDetector._zone':
        return False
    left, right = a.get('inputs'), b.get('inputs')
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    if left.get('status') != 'complete_supported' or right.get('status') != 'complete_supported':
        return False
    candidate = copy.deepcopy(right)
    try:
        items = candidate['value']['$kwargs']['value']['$mapping']
        hints = [x for x in items if x[0] == 'pre_registered_s']
        if len(hints) != 1 or type(hints[0][1]) is not bool:
            return False
        parent = candidate['value']['$args']['value']['$tuple'][2]
        if hints[0][1] != (parent == 'S'):
            return False
        items.remove(hints[0])
    except (KeyError, IndexError, TypeError, ValueError):
        return False
    return encode(left) == encode(candidate)

class Stream:
    def __init__(self, path):
        self.path = Path(path)
        self.raw = 0
        self.excluded = collections.Counter()
        self.issues = collections.Counter()
        self.families = collections.Counter()
        self.stage_stack = []
    def rows(self):
        with gzip.open(self.path, 'rt', encoding='utf-8') as f:
            for line in f:
                yield json.loads(line, object_pairs_hook=unique, parse_constant=invalid_constant)
    def records(self):
        for row in self.rows():
            self.raw += 1
            if row.get('schema') != SCHEMA or type(row.get('event_ordinal')) is not int or row['event_ordinal'] != self.raw:
                raise ValueError(f'invalid schema or ordinal at {self.raw}')
            for field in ('stage', 'method', 'direction', 'result'):
                if field not in row:
                    raise ValueError(f'missing {field} at {self.raw}')
            family = row['stage'] + ':' + row['method']
            self.families[family] += 1
            if row['method'] in BOUNDARY and row['stage'] == 'trading_pipeline':
                label = row.get('phase_label')
                if not isinstance(label, str) or not label:
                    raise ValueError(f'missing stage label at {self.raw}')
                if row['method'] == 'timed.stage_start': self.stage_stack.append(label)
                elif not self.stage_stack or self.stage_stack.pop() != label:
                    raise ValueError(f'unbalanced stage at {self.raw}')
            elif 'inputs' not in row:
                self.issues[family + ':missing_inputs'] += 1
            for field in ('result','inputs','pre_inputs','lifecycle_new_events'):
                if field in row and (not isinstance(row[field],dict) or row[field].get('status') != 'complete_supported'):
                    self.issues[family + ':' + field + ':not_complete'] += 1
            check_rep(row, family, self.issues)
            if row.get('lifecycle_existing_state_changed_unverified'):
                self.issues[family+':unverified_lifecycle_mutation'] += 1
            if family in IMPL_ONLY:
                self.excluded[family] += 1
                continue
            yield row
        if self.stage_stack:
            raise ValueError('unclosed stage boundaries')
        if self.raw == 0:
            raise ValueError('empty trace')

def payload(row):
    return {k:v for k,v in row.items() if k not in ('schema','event_ordinal','inputs')}

def compare(original, candidate, max_examples=8):
    return compare_streams(Stream(original),Stream(candidate),max_examples)

def compare_streams(a,b,max_examples=8,fast_equal=False):
    total=equal=known=unknown=diff=0
    examples=[]; first_diff=None
    digests=[hashlib.sha256(),hashlib.sha256()]
    try:
        for x,y in itertools.zip_longest(a.records(),b.records()):
            total += 1
            encoded=[]
            for row,digest in zip((x,y),digests):
                blob=None if row is None else encode({k:v for k,v in row.items() if k not in ('event_ordinal','schema')})
                encoded.append(blob)
                if blob is not None: digest.update(blob+b'\n')
            if fast_equal and x is not None and y is not None and encoded[0] == encoded[1]:
                equal += 1
                continue
            if x is None or y is None or encode(payload(x)) != encode(payload(y)):
                diff += 1
                if first_diff is None:
                    changed = [] if x is None or y is None else [k for k in dict.fromkeys([*payload(x),*payload(y)]) if k not in x or k not in y or encode(x[k]) != encode(y[k])]
                    first_diff = {'position':total,'fields':changed,'original_ordinal':None if x is None else x['event_ordinal'],'candidate_ordinal':None if y is None else y['event_ordinal'],'family':None if x is None else x['stage']+':'+x['method']}
                continue
            equal += 1
            if encode(x.get('inputs')) != encode(y.get('inputs')):
                classified=exact_call_hint(x,y)
                if classified: known += 1
                else: unknown += 1
                if not classified and len(examples)<max_examples:
                    examples.append({'position':total,'family':x['stage']+':'+x['method'],'original_ordinal':x['event_ordinal'],'candidate_ordinal':y['event_ordinal']})
    except (ValueError, KeyError, TypeError, OSError, EOFError) as exc:
        return {'selected_event_status':'FAIL','full_semantic_state_status':'INCOMPLETE','error':str(exc),'compared_positions_before_error':total}
    status='FAIL' if diff or unknown or not total else 'INCOMPLETE' if a.issues or b.issues else 'PASS'
    return {'selected_event_status':status,'full_semantic_state_status':'INCOMPLETE',
            'full_state_limitation':'Only selected observer events; excluded implementation calls and unobserved in-process mutations are not proven equivalent.',
            'compared_positions':total,'noninput_equal_positions':equal,'noninput_mismatches':diff,
            'known_exact_v81_call_hint_drifts':known,'unresolved_input_drifts':unknown,
            'first_noninput_divergence':first_diff,'unresolved_input_examples':examples,
            'original_raw_events':a.raw,'candidate_raw_events':b.raw,
            'excluded_original':dict(a.excluded),'excluded_candidate':dict(b.excluded),
            'original_representation_issues':dict(a.issues),'candidate_representation_issues':dict(b.issues),
            'selected_payload_sha256_original':digests[0].hexdigest(),'selected_payload_sha256_candidate':digests[1].hexdigest()}

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('original');p.add_argument('candidate');p.add_argument('--out',required=True);a=p.parse_args()
    result=compare(a.original,a.candidate);Path(a.out).write_text(json.dumps(result,indent=2)+'\n');print(result['selected_event_status'],result.get('compared_positions'))
    raise SystemExit({'PASS':0,'FAIL':1,'INCOMPLETE':2}[result['selected_event_status']])
