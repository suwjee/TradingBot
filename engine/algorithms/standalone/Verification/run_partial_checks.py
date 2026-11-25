"""Limited checks, not the complete Engine acceptance suite. Baseline files must be supplied separately."""
import argparse,copy,hashlib,json,random,sys,time,platform
from pathlib import Path
from datetime import datetime,timedelta,timezone
from decimal import Decimal
from partial_reference import containment,ordered_naive,strict,confirmation,aggregate,tf,normalize
p=argparse.ArgumentParser();p.add_argument('--oracle',required=True,type=Path);p.add_argument('--raw',required=True,type=Path);p.add_argument('--report',required=True,type=Path);p.add_argument('--part',default='all');args=p.parse_args()
sys.path.insert(0,str(args.oracle));import core_utils as cu, direction_policy as dp,true_false as orig,buckets
expected={'core_utils.py':'38a1053510c5fb114e1b4290de00a2d3b27fc373','direction_policy.py':'f7d047abde0eb884905f86c1d2beeaaec3f6e07a','true_false.py':'d569d16bc493b9eb5da75ed5594c168751856b6f'}
report=json.loads(args.report.read_text()) if args.report.exists() else {'commit':'466eb875070f02cd0dbfb105033422bbe2fd8c70','python':platform.python_version(),'scope':'isolated primitives, TF annotation, batch aggregation only','source_hashes':{},'synthetic_runs':[],'raw_runs':[],'failures':[]}
for f,sha in expected.items():
    b=(args.oracle/f).read_bytes();actual=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest();report['source_hashes'][f]={'git_blob_sha1':actual,'sha256':hashlib.sha256(b).hexdigest(),'matches':actual==sha};assert actual==sha

def check(label,a,b):
    if a!=b:raise AssertionError((label,a,b))
def exact_rows(rows):
    h=hashlib.sha256()
    for r in rows:h.update((str(r['time'])+'|'+ '|'.join(str(r[k].as_tuple()) for k in ('open','high','low','close'))+'\n').encode())
    return len(rows),h.hexdigest()
def save():args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2))
def synthetic(seed):
    rng=random.Random(seed);t=time.perf_counter();n=0
    for _ in range(400):
        start,end=rng.randrange(20),rng.randrange(20);intervals=[(rng.randrange(20),rng.randrange(20),i) for i in range(rng.randrange(35))]
        check('containment',list(cu.ChronologicalContainmentIndex(intervals).enclosing(start,end)),containment(intervals,start,end));n+=1
    epoch=datetime(2000,1,1)
    for vals in [[],[epoch],[epoch,epoch],[epoch+timedelta(seconds=1),epoch],[epoch.replace(tzinfo=timezone.utc)]]:
        check('naive',cu.ordered_naive_datetimes(vals),ordered_naive(vals));n+=1
    for v in [Decimal('1.00'),Decimal('-0.00'),5,'1.000',1.25]:
        check('normalize',cu.as_decimal(v).as_tuple(),normalize(v).as_tuple());n+=1
    for direction in ['bullish','bearish']:
        d=dp.policy_for(direction)
        for a in ['0','-1','1.00','1.0','1.0000000001']:
            for b in ['0','-1','1.00','1.0','1.0000000001']:
                x,y=Decimal(a),Decimal(b)
                check('strict',d.strict_cross(x,y),strict(direction,x,y));check('confirm',d.confirmation_cross(x,y),confirmation(direction,x,y));check('extreme',d.better_extreme(x,y),strict(direction,x,y));n+=3
        for _ in range(400):
            group={k:[] for k in ['sZones','eZones','stopAlls','primaryLows','primaryHighs']}
            for j in range(rng.randint(0,70)):
                k=rng.choice(list(group));row={'sourceTime':rng.randrange(1,50),'price':str(rng.randint(1,9)),'number':rng.randint(1,6),'color':rng.choice(['red','blue']),'family':rng.choice(['red','blue']),'parentSourceTime':rng.randrange(1,50),'calculationValid':rng.choice([True,True,False,None]),'trueFalse':'old','trueFalseRepeated':True,'trueFalseRepairTime':0};group[k].append(row)
            a,b=copy.deepcopy(group),copy.deepcopy(group)
            def cross(d,t,p):return None if (t+int(p))%3==0 else t+int(p)
            def closed(r):return r['sourceTime']%2==0
            cb=cross if rng.randrange(2) else None;cl=closed if rng.randrange(2) else None
            orig.apply_true_false(direction,a,cb,stopall_confirmation_closed=cl);tf(direction,b,cb,cl);check('TF',a,b);n+=1
    for _ in range(100):
        rows=[]
        for j in range(rng.randrange(30)):
            vals=[Decimal(rng.choice(['1.0','1.00','2.00','2','0.0','-0.00'])) for _ in range(4)]
            rows.append(dict(zip(['time','open','high','low','close'],[rng.randrange(-20,80),*vals])))
        timeframe=rng.choice([1,5,60]);lower=rng.choice([True,False]);a=buckets.build_candle_buckets(rows,timeframe,lower_only=lower);b=aggregate(rows,timeframe,lower);check('aggregate',list(map(exact_rows,a)),list(map(exact_rows,b)));n+=1
    return {'seed':seed,'checks':n,'elapsed_seconds':round(time.perf_counter()-t,6),'status':'PASS'}
if args.part in ('synthetic','all'):
    report['synthetic_runs']=[]
    for seed in (31,73,191):
        try:report['synthetic_runs'].append(synthetic(seed))
        except Exception as e:report['failures'].append({'seed':seed,'error':repr(e)})
    save();print('synthetic',report['synthetic_runs'],report['failures'],flush=True)
paths=sorted(args.raw.glob('RAW*.json'))
if args.part!='synthetic':
    selected=paths if args.part=='all' else [paths[int(args.part)]]
    for path in selected:
        t=time.perf_counter();data=path.read_bytes();rows=json.loads(data.removeprefix(b'\xef\xbb\xbf'),parse_float=Decimal);info={'dataset':path.name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'rows':len(rows),'first_time':rows[0]['time'],'last_time':rows[-1]['time'],'nonincreasing_pairs':sum(a['time']>=b['time'] for a,b in zip(rows,rows[1:])),'invalid_ohlc_rows':sum(not (r['low']<=min(r['open'],r['close'])<=max(r['open'],r['close'])<=r['high']) for r in rows),'cases':[]}
        for timeframe in (1,60,300):
            try:
                t1=time.perf_counter();a=buckets.build_candle_buckets(rows,timeframe,lower_only=timeframe==1);base_time=time.perf_counter()-t1;aa=list(map(exact_rows,a));del a
                t1=time.perf_counter();b=aggregate(rows,timeframe,timeframe==1);candidate_time=time.perf_counter()-t1;bb=list(map(exact_rows,b));del b
                check('RAW '+path.name,aa,bb);info['cases'].append({'tf':timeframe,'lower_only':timeframe==1,'status':'PASS','lower_count':aa[0][0],'main_count':aa[1][0],'lower_exact_sha256':aa[0][1],'main_exact_sha256':aa[1][1],'baseline_seconds':round(base_time,6),'candidate_seconds':round(candidate_time,6)})
            except Exception as e:info['cases'].append({'tf':timeframe,'status':'FAILED','error':repr(e)});report['failures'].append({'dataset':path.name,'tf':timeframe,'error':repr(e)})
        info['elapsed_seconds']=round(time.perf_counter()-t,6);report['raw_runs']=[r for r in report['raw_runs'] if r['dataset']!=path.name]+[info];del rows,data
        save();print(path.name,info['rows'],[(c['tf'],c['status']) for c in info['cases']],flush=True)
report['overall_partial_status']='PASS' if not report['failures'] and len(report['raw_runs'])==len(paths) and len(report['synthetic_runs'])==3 else 'INCOMPLETE_OR_FAILED';save()
