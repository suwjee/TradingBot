"""Independent streaming exact validation of scoped lifecycle observer output."""
import argparse,collections,gzip,hashlib,itertools,json
from pathlib import Path
from zipfile import ZipFile
from ledger_delta_v9 import strict_json,sha
from strict_golden import stable_payload,GOLDEN_ZIP_SHA256
from lifecycle_transition_v9 import NESTED,OUTER

def header(row):
    if type(row) is not list or len(row)!=3 or row[:2]!=['tuple',0] or len(row[2])!=5:raise ValueError('bad trace envelope')
    n,method,point,direction,_=row[2]
    if n[0]!='int' or len(n)!=2 or not n[1].isdigit() or n[1].startswith('0'):raise ValueError('bad ordinal')
    if method[0]!='str' or point[0]!='str' or method[1] not in NESTED|OUTER or point[1] not in ('entry','return'):raise ValueError('bad event marker')
    if direction not in (['none'],['str','bullish'],['str','bearish']):raise ValueError('bad direction')
    return int(n[1]),method[1],point[1],direction

def diff(a,b,path=()):
    if type(a) is not type(b):return {'typed_path':list(path),'kind':'type'}
    if isinstance(a,list):
        for i,(x,y) in enumerate(zip(a,b)):
            v=diff(x,y,(*path,i))
            if v is not None:return v
        if len(a)!=len(b):return {'typed_path':list(path),'kind':'length','original_length':len(a),'v81_length':len(b)}
        return None
    return None if a==b else {'typed_path':list(path),'kind':'value','original':a,'v81':b}

def inspect(path,report):
    count=0;stack=[];counts=collections.Counter();digest=hashlib.sha256()
    with gzip.open(path,'rb') as f:
        for line in f:
            if not line.endswith(b'\n'):raise ValueError('truncated record')
            digest.update(line);count+=1;n,m,p,d=header(strict_json(line))
            if n!=count:raise ValueError('event ordinal discontinuity')
            if m in NESTED|{'StopAllDetector._detect_events'}:
                if p=='entry':stack.append((m,d))
                elif not stack or stack.pop()!=(m,d):raise ValueError('unmatched transition')
            elif p!='return':raise ValueError('unexpected entry')
            counts[m+':'+p]+=1
    if not count or stack or count!=report['events'] or dict(counts)!=report['counts'] or digest.hexdigest()!=report['jsonl_sha256']:raise ValueError('stream report mismatch')
    if sha(path.read_bytes())!=report['gzip_sha256']:raise ValueError('gzip digest mismatch')
    return count

def compare(a,b):
    count=0;first=None;equal=0
    with gzip.open(a,'rb') as x,gzip.open(b,'rb') as y:
        for l,r in itertools.zip_longest(x,y):
            count+=1
            if l==r:equal+=1;continue
            if first is None:
                left=None if l is None else strict_json(l);right=None if r is None else strict_json(r)
                first={'ordinal':count,'original_header':None if left is None else header(left),'v81_header':None if right is None else header(right),'difference':diff(left,right),'original_sha256':None if l is None else sha(l),'v81_sha256':None if r is None else sha(r)}
    return {'events':count,'equal':equal,'first_difference':first,'status':'PASS' if count and count==equal else 'FAIL'}

def audit(case,root,gold):
    result={};outputs=[];schemas=[];paths=[];reports=[]
    with ZipFile(gold) as z:
        key='runs/github_baseline/'+Path(case['name']).stem.replace(' ','_')+'.stable.json';g=z.read(key)
    assert sha(g)==case['stable_output_sha256']
    for variant in ('original','v81'):
        path=root/variant/'trace.jsonl.gz';r=json.loads((root/variant/'report.json').read_text());assert r['native_exit']==0 and r['variant']==variant and r['records']==case['records'] and r['source_sha256']==case['source_sha256'][variant] and r['raw_sha256']==case['raw_sha256'];inspect(path,r);paths.append(path);reports.append(r)
        stable,sch=stable_payload((root/(variant+'.native.json')).read_bytes());outputs.append(stable);schemas.append(sch)
    c=compare(*paths);same=outputs[0]==outputs[1]==g and schemas[0]==schemas[1]
    return {**c,'records':case['records'],'golden_byte_and_timing_schema_equality':same,'golden_sha256':sha(g),'status':'PASS' if c['status']=='PASS' and same else 'FAIL','variants':reports,'full_semantic_state_status':'INCOMPLETE'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--result',type=Path,required=True);p.add_argument('--golden',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert sha(a.golden.read_bytes())==GOLDEN_ZIP_SHA256;r=audit(json.loads(a.case.read_text()),a.result,a.golden);a.out.write_text(json.dumps(r,indent=2)+'\n');print(r['records'],r['events'],r['status'],flush=True);raise SystemExit(0 if r['status']=='PASS' else 1)
if __name__=='__main__':main()
