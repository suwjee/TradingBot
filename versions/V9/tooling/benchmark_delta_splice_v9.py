"""Full archived boundary stream equivalence; timings only for splice construction."""
import argparse,gzip,itertools,json,time
from pathlib import Path
from ledger_delta_v9 import ABSENT,make_delta,un64,encode,strict_json
from delta_splice_fast_v9 import make_delta_fast

def bench(root,reference=True):
    current={};count=0;elapsed={'legacy':0,'fast':0};bytes_total=0
    with gzip.open(root/'delta.jsonl.gz','rb') as d,gzip.open(root/'checkpoints.jsonl.gz','rb') as c:
        for left,right in itertools.zip_longest(d,c):
            if left is None or right is None:raise ValueError('length mismatch')
            row,cp=strict_json(left),strict_json(right);count+=1
            if row['ordinal']!=cp['ordinal'] or row['ordinal']!=count or row['owner']!=cp['owner']:raise ValueError('identity mismatch')
            owner=row['owner'];before=current.get(owner,ABSENT);after=un64(cp['snapshot']);bytes_total+=len(after)
            modes=('legacy','fast') if count%2 else ('fast','legacy')
            for m in modes:
                if m=='legacy' and not reference:continue
                fn=make_delta if m=='legacy' else make_delta_fast;t=time.perf_counter_ns();value=fn(before,after);elapsed[m]+=time.perf_counter_ns()-t
                if encode(value)!=encode(row['delta']):raise AssertionError(f'{m} differs at {count}')
            current[owner]=after
    if count==0:raise ValueError('empty evidence')
    return {'status':'PASS','boundaries':count,'snapshot_bytes':bytes_total,'full_archived_delta_bytes_equal':True,'timing_scope':'sum of per-boundary splice construction only; I/O, snapshot capture, replay and compression excluded; alternating execution order, one full stream','seconds':{k:v/1e9 for k,v in elapsed.items()},'reference_executed':reference}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--fast-only',action='store_true');a=p.parse_args();r=bench(a.root,not a.fast_only);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
if __name__=='__main__':main()
