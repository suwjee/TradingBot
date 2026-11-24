#!/usr/bin/env python3
"""Two-call test for V9 observer's authoritative boundary snapshot cache safety."""
import json,tempfile
from pathlib import Path
from dataclasses import dataclass
import semantic_trace_v4 as trace

@dataclass
class Candidate:
    index:int
    state:str

Candidate.__module__='reaction_engine'  # synthetic type tag for same sidecar route

class EZoneDetector:
    def __init__(self):
        self._last_candidate_zones=[Candidate(i,'pending') for i in range(40)]
        self.order_audit={}
        self._accepted_e_source_identities={}
        self.visual_lifecycle_starts=[]
        self._consumed_s_evidence=set()

def main():
 with tempfile.TemporaryDirectory() as root:
  trace._CONTEXT_WRITER=trace.EventWriter(Path(root)/'events.jsonl.gz')
  try:
   obj=EZoneDetector()
   first=trace.authoritative_boundary_snapshot('e_zone_detector','EZoneDetector.detect',obj)
   obj._last_candidate_zones[20].state='rejected'
   second=trace.authoritative_boundary_snapshot('e_zone_detector','EZoneDetector.detect',obj)
   a=first['fields']['_last_candidate_zones']['value']['$ordered_collection_snapshot']
   b=second['fields']['_last_candidate_zones']['value']['$ordered_collection_snapshot']
   assert a['jsonl_sha256']!=b['jsonl_sha256']
   assert b['snapshot_generation']==2
   assert obj._last_candidate_zones[20].state=='rejected'
   print(json.dumps({'status':'PASS','detects_mutation':True,'state_not_modified':True,'fresh_snapshots':2}))
  finally:
   trace._CONTEXT_WRITER.close();trace._CONTEXT_WRITER=None
if __name__=='__main__':main()