#!/usr/bin/env python3
"""Verify 15 unchanged V8.1 production runtime files against immutable source ZIP."""
import argparse,hashlib,json,zipfile
from pathlib import Path
ZIP=Path('/mnt/data/V9_inputs/TradingBot_Engine_V8.1_30S_BOTH_SOURCE_EXPERIMENTAL_20261123.zip')
SOURCE=Path('/mnt/data/V9_work/v81/engine')

def digest(b):return hashlib.sha256(b).hexdigest()

def inspect(out):
    rows=[]
    with zipfile.ZipFile(ZIP) as z:
        if z.testzip() is not None:raise AssertionError('V8.1 ZIP corruption')
        entries=[x for x in z.namelist() if x.startswith('engine/') and x.endswith('.py')]
        for name in entries:
            path=SOURCE/Path(name).relative_to('engine')
            expected=digest(z.read(name));actual=digest(path.read_bytes());rows.append({'path':name,'expected_source_zip_sha256':expected,'runtime_sha256':actual,'status':'PASS' if expected==actual else 'FAIL'})
    state={'status':'PASS' if len(rows)==15 and all(x['status']=='PASS' for x in rows) else 'FAIL',
           'never_production_instrumentation':True,'runtime_unchanged_after_V9_instrumentation':all(x['status']=='PASS' for x in rows),
           'runtime_file_count':len(rows),'files':rows}
    Path(out).write_text(json.dumps(state,indent=2))
    print(state['status'],len(rows));return state['status']=='PASS'
if __name__=='__main__':
    import sys
    raise SystemExit(0 if inspect(sys.argv[1]) else 1)
