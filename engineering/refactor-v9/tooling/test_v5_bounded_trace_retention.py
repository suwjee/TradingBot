#!/usr/bin/env python3
"""Verify v5 observer bounded retention, eviction, and lossless recapture.

All mutated inputs are standalone test fixtures, never user RAW or Engine state.
"""
from __future__ import annotations
import tempfile,hashlib,json
from pathlib import Path
import semantic_trace_v5 as v5

def run():
 with tempfile.TemporaryDirectory(prefix='tradingbot-v9-v5-') as d:
  writer=v5.EventWriter(Path(d)/'out.jsonl.gz')
  writer.collection_retention_budget=1600
  writer.collection_max_objects=2
  a=[1,2,3];b=[4,5,6];c=[7,8,9]
  x1=writer.save_collection(a)
  assert writer.save_collection(a)==x1
  writer.save_collection(b)
  writer.save_collection(c)
  assert len(writer.collection_objects)<=2
  assert writer.collection_evictions>=1
  assert id(a) not in writer.collection_refs
  assert writer.save_collection(a)['jsonl_sha256']==x1['jsonl_sha256']
  assert writer.collection_evictions>=2
  first=writer.save_collection(b)
  b.append(42)
  fresh=writer.save_collection(b,fresh=True)
  assert first['jsonl_sha256']!=fresh['jsonl_sha256']
  assert fresh['fresh_boundary_snapshot'] is True
  big=list(range(40))
  before=writer.collection_nonretained
  xx=writer.save_collection(big)
  yy=writer.save_collection(big)
  assert xx['jsonl_sha256']==yy['jsonl_sha256']
  assert writer.collection_nonretained-before==2
  assert id(big) not in writer.collection_refs
  assert writer.collection_retained_estimate <= writer.collection_retention_budget
  writer.emit({'stage':'synthetic','method':'test','direction':'bullish',
               'result':{'status':'complete_supported','value':123},
               'inputs':{'status':'complete_supported','value':[]}})
  m=writer.close()
  assert m['events']==1 and m['collection_lru_evictions']>=2
  assert m['strong_collection_retention_estimate_bytes']<=m['strong_collection_retention_budget_bytes']
  assert v5.stream_file_sha256(writer.dest)==m['gzip_sha256']
  for x in m['ordered_collection_sidecars']:
   assert v5.stream_file_sha256(Path(d)/x['file'])==x['gzip_sha256']
  print('V5_MEMORY_BOUNDED_RETENTION: 10/10 PASS; no engine or user RAW modified')
if __name__=='__main__':run()