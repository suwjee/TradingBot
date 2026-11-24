"""Read-only scoped Live RAW lineage, bucket/view and OrderAudit delta proof."""
from __future__ import annotations
import argparse,gzip,json,os,subprocess,sys,tempfile,time
from pathlib import Path
from ledger_delta_v9 import Observer,ABSENT,snapshot,sha,source_check,verify_replay
from compare_ledger_delta_v9 import compare_streams
from strict_golden import stable_payload,parse

class LiveObserver(Observer):
    def __init__(self,root,d,c):
        super().__init__(root,d,c)
        self.paths[str((root/'bridge/live_pipeline.py').resolve())]={
            'LiveRawSource.__init__','LiveRawSource.append','LiveRawSource.append_delta','LiveRawSource._append_rows',
            'LivePipelineContinuation.__init__','LivePipelineContinuation.append'}
    @staticmethod
    def fresh(obj):
        kind=type(obj).__name__
        if kind=='LiveRawSource':
            if not hasattr(obj,'_raw_sha256'):return ABSENT
            return snapshot({'raw_sha256':obj._raw_sha256,'prefix_digest':obj._prefix_hash.hexdigest(),'end':obj._end,'ending':obj._ending,'last_time':obj._last_time,'catchup':obj._catchup})
        if kind=='LivePipelineContinuation':
            if not hasattr(obj,'_market_views'):return ABSENT
            b,v=obj._buckets,obj._market_views
            # Preserve key type and insertion order, not type-object process address.
            prices=[((k[0].__module__,k[0].__qualname__,k[1]),value) for k,value in b._prices.items()]
            return snapshot({'timeframe':b.timeframe,'last_raw_time':b.last_raw_time,'second_buckets':b.second_buckets,'main_buckets':b.main_buckets,'price_cache':prices,'view_seconds':v.seconds,'view_candles':v.candles,'index_sizes':[None if x is None else x.size for x in (v.lower_index,v.main_index)]})
        return Observer.fresh(obj)

def worker(root,out,argv):
    sys.path.insert(0,str(root/'bridge'));import live_pipeline
    dp=out/'delta.jsonl.gz';cp=out/'checkpoints.jsonl.gz'
    start=time.perf_counter()
    with gzip.open(dp,'xb',compresslevel=3) as d,gzip.open(cp,'xb',compresslevel=3) as c:
        obs=LiveObserver(root,d,c);sys.argv=[str(root/'bridge/live_pipeline.py'),*argv]
        if sys.gettrace() is not None:raise ValueError('already tracing')
        sys.settrace(obs.trace)
        try:rc=live_pipeline.main()
        finally:sys.settrace(None)
        obs.finish()
    r={'native_exit':rc,'wall_s':time.perf_counter()-start,'calls':dict(obs.calls),'outer_calls':dict(obs.outer),'gaps':obs.gaps,'index_checks':obs.index_checks,'replay':verify_replay(dp,cp),'delta_sha256':sha(dp.read_bytes()),'checkpoints_sha256':sha(cp.read_bytes())}
    (out/'observer-report.json').write_text(json.dumps(r,indent=2)+'\n');return rc

def prefix(data,n):
    rows=data[1:-1].split(b'},{');result=b'['+b'},{'.join(rows[:n])+b'}]'
    if len(parse(result))!=n:raise ValueError('prefix mismatch')
    return result

def request(raw,digest=None,base=None):
    h={'bytes':len(raw),'sha256':digest or sha(raw)}
    if base is not None:h['baseSha256']=base
    return json.dumps(h,separators=(',',':')).encode()+b'\n'+raw

def stable_messages(data):
    stable=[];kinds=[];schemas=[]
    for line in data.splitlines():
        obj=parse(line);kind=obj['type'];kinds.append([kind,obj.get('code')])
        if kind in ('seed','update'):
            env=b'{"type":"seed","ready":true,"payload":' if kind=='seed' else b'{"type":"update","payload":'
            if not line.startswith(env) or not line.endswith(b'}}'):raise ValueError('envelope mismatch')
            b,s=stable_payload(line[len(env):-1]);stable.append(env+b+b'}');schemas.append(s)
        elif kind=='error' and list(obj)==['type','code','message']:stable.append(line)
        else:raise ValueError('unexpected message')
    return stable,kinds,schemas

def pair(a):
    case=json.loads(a.case.read_text());data=a.raw.read_bytes()
    if sha(data)!=case['raw_sha256']:raise ValueError('RAW mismatch')
    seed,update,latest=(prefix(data,n) for n in (1700,1800,1900));delta=latest[len(update)-1:-1]
    if update[:-1]+delta+b']'!=latest:raise ValueError('delta mismatch')
    changed=latest.replace(b'98.393',b'98.394',1)
    if changed==latest:raise ValueError('missing controlled mutation')
    packet=request(delta,sha(latest),'0'*64)+request(update,'0'*64)+request(update)+request(delta,sha(latest),sha(update))+request(changed)
    a.out.mkdir(parents=True,exist_ok=False);rows=[];messages=[];schemas=[];kinds=[]
    with tempfile.TemporaryDirectory() as t:
        seedfile=Path(t)/'seed.json';seedfile.write_bytes(seed)
        for variant,root in [('original',a.original_engine),('v81',a.v81_engine)]:
            source_check(root,case['source_sha256'][variant]);out=a.out/variant;out.mkdir()
            cmd=[sys.executable,'-B',str(Path(__file__).resolve()),'--worker',str(root.resolve()),str(out.resolve())]
            for flag,name in [('reaction-engine','reaction_engine.py'),('blue-line-engine','blue_line_detector.py'),('a-zone-engine','a_zone_detector.py'),('s-zone-engine','s_zone_detector.py'),('e-zone-engine','e_zone_detector.py'),('lifecycle-engine','lifecycle_engine.py')]:cmd+=['--'+flag,str(root/'pipeline'/name)]
            parsed=parse(seed);cmd+=['--data',str(seedfile),'--timeframe','30','--raw-timeframe','5','--from-time',str(parsed[0]['time']),'--to-time',str(parsed[-1]['time']),'--direction','both','--blue-lines','enabled','--a-zones','enabled','--s-zones','enabled','--pl-ph','enabled','--bridge-output']
            proc=subprocess.run(cmd,input=packet,capture_output=True,env={**os.environ,'PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1','TRADINGBOT_LIVE_RAW_SOURCE':str(seedfile)})
            (out/'native.jsonl').write_bytes(proc.stdout);(out/'stderr.log').write_bytes(proc.stderr)
            r=json.loads((out/'observer-report.json').read_text());r['variant']=variant
            b,k,s=stable_messages(proc.stdout);messages.append(b);kinds.append(k);schemas.append(s);r['message_sha256']=[sha(x) for x in b];rows.append(r)
            if proc.returncode!=1 or r['native_exit']!=1:raise ValueError('expected terminal history rejection')
            source_check(root,case['source_sha256'][variant])
    streams={f:compare_streams(a.out/'original'/f,a.out/'v81'/f) for f in ('delta.jsonl.gz','checkpoints.jsonl.gz')}
    expected=[['seed',None],['error','RAW_DELTA_MISMATCH'],['error','RAW_RETRY'],['update',None],['update',None],['error','RAW_CHANGED']]
    native_ok=messages[0]==messages[1] and schemas[0]==schemas[1] and kinds[0]==kinds[1]==expected
    ok=native_ok and all(x['status']=='PASS' for x in streams.values()) and not any(x['gaps'] for x in rows) and sha(a.raw.read_bytes())==case['raw_sha256']
    r={'status':'PASS' if ok else 'FAIL_OR_INCOMPLETE','scope':'Actual Live worker session with exact lineage, bucket rows, price-cache keys/values, candle views and index sizes plus observed OrderAudit boundaries. Index internals, arbitrary Live state and intra-boundary mutations not certified.','source_raw_sha256':case['raw_sha256'],'source_sha256':case['source_sha256'],'prefixes':[1700,1800,1900],'packet_sha256':sha(packet),'native_stable_bytes_equal':native_ok,'messages':kinds,'streams':streams,'variants':rows,'full_semantic_state_status':'INCOMPLETE'}
    (a.out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],streams);return 0 if ok else 2

def main():
    if len(sys.argv)>1 and sys.argv[1]=='--worker':return worker(Path(sys.argv[2]),Path(sys.argv[3]),sys.argv[4:])
    p=argparse.ArgumentParser();p.add_argument('--original-engine',type=Path,required=True);p.add_argument('--v81-engine',type=Path,required=True);p.add_argument('--raw',type=Path,required=True);p.add_argument('--case',type=Path,required=True);p.add_argument('--out',type=Path,required=True);return pair(p.parse_args())
if __name__=='__main__':raise SystemExit(main())
