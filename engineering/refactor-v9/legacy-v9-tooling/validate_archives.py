#!/usr/bin/env python3
"""Post-package independent zip CRC, embedded checksums, compile and extracted source smoke. Test-only."""
import hashlib,json,os,subprocess,sys,tempfile,zipfile,py_compile
from pathlib import Path
D=Path('/mnt/data/V9_delivery');O=Path('/mnt/data/V9_work/output')
A=[]
for archive in sorted(D.glob('*.zip')):
 print('VALIDATING',archive.name,flush=True)
 chk=hashlib.sha256(archive.read_bytes()).hexdigest();expect=(D/(archive.name+'.sha256')).read_text().split()[0]
 assert chk==expect
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None; print('CRC DONE',flush=True)
  lines=z.read('SHA256SUMS.txt').decode().splitlines();files=[]
  for line in lines:
   sha,name=line.split(None,1);name=name.strip().lstrip('*')
   assert hashlib.sha256(z.read(name)).hexdigest()==sha,name
   files.append(name)
   if len(files)%45==0:print('HASHED',len(files),flush=True)
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)
   z.extractall(path); print('EXTRACT DONE',flush=True)
   pyfiles=list(path.rglob('*.py'))
   for i,p in enumerate(pyfiles):
    if i%10==0:print('COMPILING',i,len(pyfiles),flush=True)
    py_compile.compile(str(p),doraise=True)
   report={'archive':archive.name,'zip_sha256':chk,'bytes':archive.stat().st_size,'member_count':len(files),
           'zip_crc':'PASS','embedded_sha256sums':'PASS','extraction':'PASS','source_py_compile':len(pyfiles),'smoke_status':'NOT APPLICABLE'}
   if 'VERIFICATION' in archive.name:
    engine=path/'verified_source_V8.1/engine';raw=Path('/mnt/data/RAW FOREXCOM_XAUUSD 5S FROM 2026-10-08 19-35-30 TO 2026-10-09 18-14-25.json')
    flags=['reaction-engine','blue-line-engine','a-zone-engine','s-zone-engine','e-zone-engine','lifecycle-engine']
    names=['reaction_engine.py','blue_line_detector.py','a_zone_detector.py','s_zone_detector.py','e_zone_detector.py','lifecycle_engine.py']
    cmd=[sys.executable,'-B',str(engine/'bridge/trading_pipeline.py')]
    for f,n in zip(flags,names):cmd+=['--'+f,str(engine/'pipeline'/n)]
    cmd+=['--data',str(raw),'--timeframe','30','--raw-timeframe','5','--direction','both',
          '--from-time','1791475530','--to-time','1791557065',
          '--blue-lines','enabled','--a-zones','enabled','--s-zones','enabled','--pl-ph','enabled','--bridge-output']
    print('SMOKE START',flush=True)
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1'},timeout=90)
    print('SMOKE DONE',p.returncode,flush=True)
    assert p.returncode==0,p.stderr[-400:]
    sys.path.insert(0,'/mnt/data/V9_work/tooling')
    from strict_golden import stable_payload,sha256
    stable,_=stable_payload(p.stdout)
    frozen=json.loads(Path('/mnt/data/V9_work/tooling/inputs_verified.json').read_text());expected=next(x['stable_output_sha256'] for x in frozen['datasets'] if x['records']==15542)
    assert sha256(stable)==expected
    report['smoke_status']='PASS';report['smoke_rows']=15542;report['smoke_stable_sha256']=sha256(stable)
   A.append(report)
   print(json.dumps({'archive':archive.name,'status':'PASS','files':len(files),'py_compile':len(pyfiles),'smoke':report['smoke_status']}),flush=True)
(D/'V9_ARCHIVE_AUDIT.json').write_text(json.dumps({'status':'INCOMPLETE','archives':A,'archive_integrity':'PASS',
 'release_incomplete_reason':'full internal semantic execution trace and scanned-row/heap/cache counters absent; no repeated paired performance promotion'},indent=2))
