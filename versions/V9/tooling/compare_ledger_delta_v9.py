"""Exact pair proof for completed scoped OrderAudit delta observations."""
import argparse,gzip,itertools,json
from pathlib import Path
from zipfile import ZipFile
from ledger_delta_v9 import sha,verify_replay
from strict_golden import stable_payload,GOLDEN_ZIP_SHA256

def compare_streams(a,b):
    count=0;equal=0;first=None
    with gzip.open(a,'rb') as x,gzip.open(b,'rb') as y:
        for left,right in itertools.zip_longest(x,y):
            count+=1
            if left==right:equal+=1
            elif first is None:first={'ordinal':count,'original_sha256':None if left is None else sha(left),'v81_sha256':None if right is None else sha(right)}
    return {'status':'PASS' if count and count==equal else 'FAIL','positions':count,'equal':equal,'first_difference':first}

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--golden',type=Path,required=True);p.add_argument('--original',type=Path,required=True);p.add_argument('--v81',type=Path,required=True);p.add_argument('--original-native',type=Path,required=True);p.add_argument('--v81-native',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();case=json.loads(a.case.read_text())
    if sha(a.golden.read_bytes())!=GOLDEN_ZIP_SHA256:raise ValueError('Golden archive mismatch')
    with ZipFile(a.golden) as z:
        path='runs/github_baseline/'+Path(case['name']).stem.replace(' ','_')+'.stable.json';gold=z.read(path)
    if sha(gold)!=case['stable_output_sha256']:raise ValueError('Golden case mismatch')
    reports=[];native=[];schemas=[]
    for v,root,np in [('original',a.original,a.original_native),('v81',a.v81,a.v81_native)]:
        r=json.loads((root/'report.json').read_text());reports.append(r)
        if r['variant']!=v or r['records']!=case['records'] or r['raw_sha256']!=case['raw_sha256'] or r['source_sha256']!=case['source_sha256'][v] or r['native_exit']!=0:raise ValueError('Run provenance mismatch')
        for f,k in [('delta.jsonl.gz','delta_gzip_sha256'),('checkpoints.jsonl.gz','checkpoint_gzip_sha256')]:
            if sha((root/f).read_bytes())!=r[k]:raise ValueError('Artifact digest mismatch')
        if verify_replay(root/'delta.jsonl.gz',root/'checkpoints.jsonl.gz')!=r['replay']:raise ValueError('Replay report mismatch')
        b,s=stable_payload(np.read_bytes());native.append(b);schemas.append(s)
    streams={f:compare_streams(a.original/f,a.v81/f) for f in ('delta.jsonl.gz','checkpoints.jsonl.gz')}
    gold_equal=native[0]==native[1]==gold and schemas[0]==schemas[1]
    status='PASS' if gold_equal and all(r['status']=='PASS' for r in streams.values()) and not any(r['gaps'] for r in reports) else 'FAIL_OR_INCOMPLETE'
    result={'case':case['name'],'records':case['records'],'status':status,'native_stable_golden_byte_equality':gold_equal,'golden_sha256':sha(gold),'streams':streams,'variants':reports,'full_semantic_state_status':'INCOMPLETE','scope':'exact observed outer OrderAudit boundary representation only; no complete in-process semantic mutation or Live proof'}
    a.out.write_text(json.dumps(result,indent=2)+'\n');print(case['records'],status,streams,flush=True);raise SystemExit(0 if status=='PASS' else 2)
if __name__=='__main__':main()
