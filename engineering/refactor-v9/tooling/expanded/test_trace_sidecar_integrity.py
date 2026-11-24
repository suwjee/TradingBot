#!/usr/bin/env python3
"""Mutation tests for independently verifiable compressed Trace/Sidecar v3.

Tests each invariant on intentionally corrupted test-only trace snapshots.
Never opens nor changes production or baseline files.
"""
from __future__ import annotations
import copy,gzip,hashlib,json,shutil,tempfile
from pathlib import Path
from dataclasses import dataclass
from semantic_trace_v3 import EventWriter
from audit_trace_coverage import inspect

@dataclass(frozen=True)
class FakeCandle:
    index:int
    price:str

def write_case(folder):
    folder.mkdir(parents=True,exist_ok=True)
    path=folder/'events.gz';w=EventWriter(path)
    w.save_collection([FakeCandle(n,'100.000'+str(n)) for n in range(40)])
    w.emit({'stage':'trading_pipeline','method':'timed.stage_start','phase_label':'A',
            'direction':'bullish','result':{'status':'complete_supported','value':None}})
    w.emit({'stage':'e_zone_detector','method':'EZoneDetector._zone','direction':'bullish',
            'result':{'status':'complete_supported','value':{'$decimal':'100.005'}}})
    w.emit({'stage':'trading_pipeline','method':'timed.stage_end','phase_label':'A',
            'direction':'bullish','result':{'status':'complete_supported','value':None}})
    w.close();return path

def run(out):
    cases=[]
    with tempfile.TemporaryDirectory() as tmp:
        work=Path(tmp)
        basic=write_case(work/'seed');assert inspect(basic)['integrity']=='PASS'
        cases.append({'case':'unchanged_self_check','status':'PASS'})
        variants=['modified_decimal','dropped_event','out_of_order_stage','event_hash_corruption',
                  'ordered_collection_corruption','ordered_collection_key_swap','missing_sidecar','wrong_event_ordinal']
        for kind in variants:
            base=work/kind
            shutil.copytree(basic.parent,base)
            trace=base/'events.gz'
            sidecar=next(base.glob('*.collection.*.gz'))
            manifest=base/'events.gz.manifest.json'
            rows=[json.loads(x) for x in gzip.open(trace,'rt')]
            meta=json.loads(manifest.read_text())
            if kind=='modified_decimal':rows[1]['result']['value']['$decimal']='100.006'
            if kind=='dropped_event':rows.pop(1)
            if kind=='out_of_order_stage':rows[0],rows[2]=rows[2],rows[0]
            if kind=='wrong_event_ordinal':rows[1]['event_ordinal']=999
            if kind in ('modified_decimal','dropped_event','out_of_order_stage','wrong_event_ordinal'):
                with gzip.open(trace,'wt') as z:
                    for x in rows:z.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
            if kind=='event_hash_corruption':
                t=trace.read_bytes();trace.write_bytes(t[:-1]+bytes([t[-1]^0x80]))
            if kind in ('ordered_collection_corruption','ordered_collection_key_swap'):
                records=[json.loads(x) for x in gzip.open(sidecar,'rt')]
                if kind=='ordered_collection_corruption':records[0]['source_value']['$fields'][1][1]='changed'
                else:records[0],records[1]=records[1],records[0]
                with gzip.open(sidecar,'wt') as z:
                    for x in records:z.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
            if kind=='missing_sidecar':sidecar.unlink()
            try:inspect(trace)
            except Exception:status='PASS'
            else:status='FAIL'
            cases.append({'case':kind,'expected':'FAIL','assertion':status})
    result={'status':'PASS' if all(x.get('status',x.get('assertion'))=='PASS' for x in cases) else 'FAIL',
            'tests':cases,'tested':'sha, CRC, ordinals, ordered sidecar records and stage boundaries'}
    Path(out).write_text(json.dumps(result,indent=2));print(result['status'],len(cases));return result['status']=='PASS'
if __name__=='__main__':
    import sys
    raise SystemExit(0 if run(sys.argv[1]) else 1)
