#!/usr/bin/env python3
"""Read-only exact-byte TradingBot stable-output verification; no JSON reserialization.
Only the final top-level numeric timings.phasesMs and timings.bridgeTotalMs are excluded.
All object/array order and every non-timing byte remain untouched.
"""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

GOLDEN_ZIP_SHA256 = '080175abbd7a3895596230b40783062901deb38c0cc8dd3b97fc058ef21cbb88'
GOLDEN_COMMIT = '01d54ecf0149ebd15de92798be18810b6e2eb791'
class InvalidSerialization(ValueError): pass

def sha256(b): return hashlib.sha256(b).hexdigest()

def reject_duplicates(pairs):
    d = {}
    for k, v in pairs:
        if k in d: raise InvalidSerialization('Duplicate JSON key: '+k)
        d[k] = v
    return d

def reject_constant(value): raise InvalidSerialization('Non-finite JSON number: '+value)

def parse(raw):
    try: return json.loads(raw, object_pairs_hook=reject_duplicates, parse_constant=reject_constant)
    except (ValueError, TypeError) as e: raise InvalidSerialization(str(e)) from e

def stable_payload(raw):
    if not isinstance(raw,bytes): raise TypeError('Input must be original serialized bytes')
    obj = parse(raw)
    if not isinstance(obj,dict) or 'error' in obj: raise InvalidSerialization('Non-object or error output')
    if obj.get('timeframe') != 30 or set(obj.get('directions',{})) != {'bullish','bearish'}:
        raise InvalidSerialization('Incorrect timeframe or direction/order')
    if list(obj)[-1] != 'timings': raise InvalidSerialization('timings must be final top-level field')
    timing = obj['timings']
    if not isinstance(timing,dict) or list(timing) != ['phasesMs','bridgeTotalMs']:
        raise InvalidSerialization('timings keys or order modified')
    phase = timing['phasesMs']
    if not isinstance(phase,dict) or not phase: raise InvalidSerialization('Missing phase timing table')
    if not all(type(x) in (int,float) for x in phase.values()) or type(timing['bridgeTotalMs']) not in (int,float):
        raise InvalidSerialization('timings measurement must be numeric, no bool')
    marker = b',"timings":'
    off = raw.rfind(marker)
    if off <= 0 or not raw.rstrip(b'\r\n').endswith(b'}'): raise InvalidSerialization('Noncanonical end-of-document timings field')
    stable = raw[:off]+b'}'
    prior = parse(stable)
    if not isinstance(prior,dict) or list(prior) != list(obj)[:-1] or prior != {k:v for k,v in obj.items() if k!='timings'}:
        raise InvalidSerialization('timings marker was not the true last top-level field')
    schema = {'phase_keys':list(phase),'phase_types':[type(x).__name__ for x in phase.values()],
              'total_type':type(timing['bridgeTotalMs']).__name__, 'timing_keys':list(timing)}
    return stable,schema

def stable_match(golden, candidate, golden_metrics):
    reference, rs = stable_payload(golden)
    data, cs = stable_payload(candidate)
    expected_schema = golden_metrics['telemetry_contract']
    if {k:rs[k] for k in expected_schema} != expected_schema:
        raise InvalidSerialization('Golden telemetry mismatch with frozen metrics')
    return {'bytes_equal':data==reference,'timing_schema_equal':cs==rs,
            'golden_stable_sha256':sha256(reference),'candidate_stable_sha256':sha256(data),
            'first_diff_byte':next((i for i,(a,b) in enumerate(zip(reference,data)) if a!=b),min(len(reference),len(data))) if data!=reference else None}

def verify_freeze(zip_path, manifest):
    from zipfile import ZipFile
    zip_path = Path(zip_path)
    if sha256(zip_path.read_bytes()) != GOLDEN_ZIP_SHA256: raise InvalidSerialization('Frozen ZIP digest mismatch')
    with ZipFile(zip_path) as z:
        if z.testzip() is not None:raise InvalidSerialization('Frozen ZIP CRC error')
        original = json.loads(z.read('input_manifest.json'))
        if original['commit'] != GOLDEN_COMMIT: raise InvalidSerialization('Frozen ZIP commit mismatch')
        originals={row['name']:row for row in original['dataset'] if row['nominal_raw_seconds']==5}
        if set(originals)!={row['file'] for row in manifest['datasets']}: raise InvalidSerialization('Dataset identity mismatch')
        for d in manifest['datasets']:
            if originals[d['file']]['sha256']!=d['raw_sha256']: raise InvalidSerialization('RAW manifest mismatch')
            stem=Path(d['file']).stem.replace(' ','_');base='runs/github_baseline/'+stem
            stable=z.read(base+'.stable.json'); raw=z.read(base+'.json')
            if sha256(stable)!=d['stable_output_sha256']:raise InvalidSerialization('Stable fingerprint mismatch '+stem)
            computed,schema=stable_payload(raw)
            if computed != stable: raise InvalidSerialization('Stored stable file inconsistent '+stem)
            recorded=json.loads(z.read(base+'.metrics.json'))['telemetry_contract']
            if {k:schema[k] for k in recorded}!=recorded: raise InvalidSerialization('Original telemetry mismatch '+stem)
    return True
