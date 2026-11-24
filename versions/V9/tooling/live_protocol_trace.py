"""Exact byte-stable comparison of a bounded real-RAW Live worker session."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from run_verified_trace_pair_v9 import source_check
from strict_golden import stable_payload, parse


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prefix(data, n):
    if not (data.startswith(b'[{') and data.endswith(b'}]')):
        raise ValueError('Expected frozen compact array')
    rows = data[1:-1].split(b'},{')
    if not 0 < n < len(rows):
        raise ValueError('Invalid seed size')
    answer = b'[' + b'},{'.join(rows[:n]) + b'}]'
    if len(parse(answer)) != n:
        raise ValueError('Prefix count mismatch')
    return answer


def request(raw, digest=None, base=None):
    header = {'bytes': len(raw), 'sha256': digest or sha(raw)}
    if base is not None:
        header['baseSha256'] = base
    return json.dumps(header, separators=(',', ':')).encode() + b'\n' + raw


def stable_messages(raw):
    result = []
    schemas = []
    kinds = []
    for line in raw.splitlines():
        obj = parse(line)
        kind = obj['type']
        kinds.append((kind, obj.get('code')))
        if kind in ('seed', 'update'):
            envelope = b'{"type":"seed","ready":true,"payload":' if kind == 'seed' else b'{"type":"update","payload":'
            if not line.startswith(envelope) or not line.endswith(b'}}'):
                raise ValueError('Live envelope schema/order drift')
            value, schema = stable_payload(line[len(envelope):-1])
            result.append(envelope + value + b'}')
            schemas.append(schema)
        elif kind == 'error':
            if list(obj) != ['type', 'code', 'message']:
                raise ValueError('Error schema drift')
            result.append(line)
        else:
            raise ValueError('Unexpected Live message kind')
    return result, schemas, kinds


def run(root, seed, packet, variant, out):
    args = [sys.executable, '-B', str(root / 'bridge/live_pipeline.py')]
    for name, filename in [('reaction-engine','reaction_engine.py'), ('blue-line-engine','blue_line_detector.py'),
                           ('a-zone-engine','a_zone_detector.py'), ('s-zone-engine','s_zone_detector.py'),
                           ('e-zone-engine','e_zone_detector.py'), ('lifecycle-engine','lifecycle_engine.py')]:
        args += ['--'+name, str(root / 'pipeline' / filename)]
    data = parse(seed.read_bytes())
    args += ['--data', str(seed), '--timeframe', '30', '--raw-timeframe', '5',
             '--from-time', str(data[0]['time']), '--to-time', str(data[-1]['time']),
             '--direction', 'both', '--blue-lines', 'enabled', '--a-zones', 'enabled',
             '--s-zones', 'enabled', '--pl-ph', 'enabled', '--bridge-output']
    start = time.perf_counter()
    proc = subprocess.run(args, input=packet, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1','TRADINGBOT_LIVE_RAW_SOURCE':str(seed)})
    wall = time.perf_counter()-start
    (out / f'{variant}.stdout.jsonl').write_bytes(proc.stdout)
    (out / f'{variant}.stderr.log').write_bytes(proc.stderr)
    stable, schemas, kinds = stable_messages(proc.stdout)
    return {'variant': variant,'exit': proc.returncode,'wall_s': wall,'messages': kinds,
            'stable_message_sha256': [sha(s) for s in stable], 'timing_schemas': schemas}, stable


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--original-engine',type=Path,required=True)
    p.add_argument('--v81-engine',type=Path,required=True)
    p.add_argument('--raw',type=Path,required=True)
    p.add_argument('--case',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    case=json.loads(a.case.read_text()); data=a.raw.read_bytes()
    if sha(data)!=case['raw_sha256']:
        raise ValueError('RAW SHA mismatch')
    source_check(a.original_engine,case['source_sha256']['original']);source_check(a.v81_engine,case['source_sha256']['v81'])
    seed, update, latest = (prefix(data,n) for n in (1700,1800,1900))
    delta=latest[len(update)-1:-1]
    if not delta.startswith(b',') or update[:-1]+delta+b']'!=latest:
        raise ValueError('Append delta mismatch')
    changed=latest.replace(b'98.393',b'98.394',1)
    if changed==latest:
        raise ValueError('Controlled corrupt-prefix fixture unavailable')
    packet=(request(delta,digest=sha(latest),base='0'*64)+request(update,digest='0'*64)+request(update)
            +request(delta,digest=sha(latest),base=sha(update))+request(changed))
    a.out.mkdir(parents=True,exist_ok=False)
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'seed.json';path.write_bytes(seed)
        original, x=run(a.original_engine,path,packet,'original',a.out)
        candidate, y=run(a.v81_engine,path,packet,'v81',a.out)
    expected=[('seed',None),('error','RAW_DELTA_MISMATCH'),('error','RAW_RETRY'),('update',None),('update',None),('error','RAW_CHANGED')]
    source_check(a.original_engine,case['source_sha256']['original']);source_check(a.v81_engine,case['source_sha256']['v81'])
    ok=(original['exit']==candidate['exit']==1 and original['messages']==candidate['messages']==expected
        and x==y and original['timing_schemas']==candidate['timing_schemas'] and sha(a.raw.read_bytes())==case['raw_sha256'])
    report={'status':'PASS' if ok else 'FAIL','full_semantic_state_status':'INCOMPLETE',
            'scope':'Real RAW derived exact prefixes; Live worker seed, retry, full append, delta append, changed history rejection. No claim of arbitrary Live state coverage.',
            'source_raw_sha256':case['raw_sha256'],'source_raw_records':case['records'],'prefixes':[1700,1800,1900],
            'seed_sha256':sha(seed),'full_append_sha256':sha(update),'final_append_sha256':sha(latest),'packet_sha256':sha(packet),
            'original':original,'v81':candidate}
    (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],original['messages'],candidate['messages'],original['stable_message_sha256'])
    raise SystemExit(0 if ok else 1)


if __name__=='__main__':main()
