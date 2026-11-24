#!/usr/bin/env python3
"""Test-only lossless streamed stage snapshots with nested million-scale-style values."""
import gzip,hashlib,json,tempfile
from decimal import Decimal
from pathlib import Path
from semantic_trace_v9 import EventWriter

def main():
  with tempfile.TemporaryDirectory() as root:
    p=Path(root)/'trace.jsonl.gz';w=EventWriter(p)
    source=[{'open':Decimal('12.000'), 'close':Decimal('12.001'),'price_as_string':'12.000'} for _ in range(16000)]
    nested={'input':{'raw':source},'metadata':{'name':'unmodified'}}
    before=(source[0]['open'],source[-1]['close'],len(source))
    rep=w.safe_stage_value(nested,'Parse Raw')
    assert rep['status']=='complete_supported',rep
    assert len(w.stage_output_files)==1
    meta=w.stage_output_files[0]
    assert meta['record_count']==len(source)
    assert meta['partial_elements']==0
    with gzip.open(Path(str(p)+'.stage.0001.jsonl.gz'),'rt') as f:
      first=json.loads(next(f)); second=json.loads(next(f))
    assert first['source_value']['value']['$mapping'][0][1]=={'$decimal':'12.000'}
    assert first['source_ordinal']==0 and second['source_ordinal']==1
    assert (source[0]['open'],source[-1]['close'],len(source))==before
    assert w.collection_retained_estimate<=w.collection_retention_budget
    w.close()
    assert meta['jsonl_sha256'] and meta['gzip_sha256']
    print('V9_NESTED_LARGE_STAGE_STREAM: 8/8 PASS; source sequence unchanged')
if __name__=='__main__':main()
