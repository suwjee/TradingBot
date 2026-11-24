#!/usr/bin/env python3
"""Test-only falsification test for V9 mutable sidecar snapshot freshness."""
from __future__ import annotations
import dataclasses, hashlib, json, tempfile
from pathlib import Path
import semantic_trace_v4 as t

@dataclasses.dataclass
class Candidate:
    index: int
    state: str

def main():
    with tempfile.TemporaryDirectory(prefix='v9-sidecar-test-') as directory:
        output=Path(directory)/'trace.jsonl.gz'
        writer=t.EventWriter(output)
        before=[Candidate(i,'pending') for i in range(33)]
        original=[(x.index,x.state) for x in before]
        a=writer.save_collection(before,fresh=True)
        before[17].state='rejected'
        b=writer.save_collection(before,fresh=True)
        assert a['jsonl_sha256']!=b['jsonl_sha256'], 'mutable content drift hidden'
        assert a['snapshot_generation']==1 and b['snapshot_generation']==2
        assert writer.collection_files[0]['fresh_boundary_snapshot']
        assert writer.collection_files[1]['fresh_boundary_snapshot']
        assert original[17][1]=='pending' and before[17].state=='rejected'
        assert all(x.index==i for i,x in enumerate(before))
        writer.close()
        return {'status':'PASS','test':'mutated Candidate list after first snapshot',
                'distinct_digests':True,'generations':[a['snapshot_generation'],b['snapshot_generation']],
                'state_was_not_modified_by_observer':True}

if __name__=='__main__':
    print(json.dumps(main(),indent=2))
