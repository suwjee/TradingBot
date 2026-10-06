"""Independent RAW checks; completion alone is never semantic correctness."""
from pathlib import Path
from bisect import bisect_left, bisect_right
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo
import importlib.util, json, orjson

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
spec=importlib.util.spec_from_file_location('raw_order_verifier',ROOT/'engine/tests/verification/verify_order_b_raw.py')
verifier=importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)

def main():
  records=[]
  for folder in ('raw-30s','raw-60s','raw-5s','determinism','finest-union'):
    manifest=OUT/folder/'manifest.json'
    if not manifest.exists(): continue
    for case in json.loads(manifest.read_text(encoding='utf-8')):
      if case.get('execution')!='PASS': continue
      payload_path=OUT/folder/(case['name']+'.stdout.json')
      data=json.loads(payload_path.read_bytes())
      rows=orjson.loads(Path(case['rawPath']).read_bytes())
      tf=case['timeframe']
      times=[int(row['time']) for row in rows]
      lows=[Decimal(str(row['low'])) for row in rows]
      highs=[Decimal(str(row['high'])) for row in rows]
      main=[]
      for time,low,high in zip(times,lows,highs):
        bucket=time//tf*tf
        if main and main[-1][0]==bucket:
            old=main[-1]; main[-1]=(bucket,min(old[1],low),max(old[2],high))
        else: main.append((bucket,low,high))
      record={'case':case['name'],'folder':folder,'checks':{},'failures':[],'counts':{}}
      try:
          result=verifier.verify(Path(case['rawPath']),payload_path,tf)
          record['checks']['orderBPublishedProvenance']='PASS'
          record['counts']['orderBLegsVerified']=result
      except AssertionError:
          record['checks']['orderBPublishedProvenance']='FAIL'
      for direction,body in data['directions'].items():
        seen=set()
        opposite='bearish' if direction=='bullish' else 'bullish'
        canonical={(r['firstIndex'],r['breakIndex']) for r in data['directions'][opposite]['reactions']}
        projection={(o['firstCandle']['index'],o['structure']['breakoutCandle']['index']):o
                    for o in body.get('bridgeOutput',{}).get('orderAudit',[])}
        for order in body['orderAudit']:
          identity=(order['firstIndex'],order['breakIndex'])
          if identity in seen: record['failures'].append({'check':'duplicatePhysicalIdentity','direction':direction,'order':identity})
          seen.add(identity)
          if identity not in canonical: record['failures'].append({'check':'canonicalOrderMembership','direction':direction,'order':identity})
          if not order['causes']: record['failures'].append({'check':'validCreatingCause','direction':direction,'order':identity})
          event=order['stopHitEventTime']
          projected=projection.get(identity)
          confirmation_text=projected['structure']['breakoutCandle']['eventTime'] if projected else None
          confirmation=(int(datetime.strptime(confirmation_text,'%Y-%m-%d %H:%M:%S').replace(tzinfo=ZoneInfo('Asia/Tehran')).timestamp())
                        if confirmation_text else None)
          if confirmation is not None:
            for cause in order['causes']:
              if cause['kind']=='parent-stop' and cause['eventTime']>=confirmation:
                record['failures'].append({'check':'parentStopNotBeforePhysicalConfirmation','direction':direction,'order':identity,
                                          'confirmation':confirmation,'cause':cause})
          if event is not None:
            # Confirmation is physically strict; same lower row is retained by source,
            # so separate later-event requirement is not silently invented here.
            level=Decimal(order['stopLevel'])
            left=bisect_left(times,confirmation if confirmation is not None else order['breakTime'])
            eligible=[i for i in range(left,bisect_right(times,event))
                      if (highs[i]>level if direction=='bullish' else lows[i]<level)]
            if not eligible or times[eligible[-1]]!=event:
                record['failures'].append({'check':'strictOrderStopAtRecordedTime','direction':direction,'order':identity,'event':event})
            if confirmation is not None and (not eligible or times[eligible[0]]!=event):
                record['failures'].append({'check':'firstStrictOrderStopAfterExactConfirmation','direction':direction,'order':identity,
                                          'event':event,'firstStrict':times[eligible[0]] if eligible else None})
        for e in body['eZones']:
          order=next((o for o in body['orderAudit'] if (o['firstIndex'],o['breakIndex'])==(e['orderFirstIndex'],e['orderBreakIndex'])),None)
          if order is None: record['failures'].append({'check':'EOrderProvenanceResolves','direction':direction,'E':e['sourceIndex']}); continue
          stop=order['stopHitEventTime']
          if stop is None: record['failures'].append({'check':'EHasStrictOrderStop','direction':direction,'E':e['sourceIndex']}); continue
          if e['decisionEventTime']!=max(e['parentStopEventTime'],stop):
            record['failures'].append({'check':'EDecisionEvent','direction':direction,'E':e['sourceIndex']})
          first=e['parentStopIndex']; last=e['decisionIndex']
          # For E with a carried earlier Order stop, interval remains parent-stop
          # through actual Order stop; main source must be in that closed interval.
          order_stop_idx=order['stopHitIndex']
          if order_stop_idx>=first:
            prices=[m[1 if direction=='bullish' else 2] for m in main[first:order_stop_idx+1]]
            expected=min(prices) if direction=='bullish' else max(prices)
            expected_index=first+prices.index(expected)
            if Decimal(e['price'])!=expected or e['sourceIndex']!=expected_index:
              record['failures'].append({'check':'ECompleteBoundaryCandleGeometry','direction':direction,'E':e['sourceIndex'],
                                         'expectedSource':expected_index,'expectedPrice':str(expected),'actualPrice':e['price']})
        for stage in ('reactions','resets','blueLines','aZones','sZones','eZones','stopAlls'):
          for item in body[stage]:
            for k,v in item.items():
              if k in ('boxTop','boxBottom','price','sourceExtreme','linePrice','stopLevel','brokenLevel','fibonacciLevel') and v is not None and not isinstance(v,str):
                record['failures'].append({'check':'DecimalStringSerialization','direction':direction,'stage':stage,'field':k})
        record['counts'][direction]={'physicalOrders':len(seen),'E':len(body['eZones'])}
      categories=('duplicatePhysicalIdentity','canonicalOrderMembership','validCreatingCause','strictOrderStopAtRecordedTime',
                  'EOrderProvenanceResolves','EHasStrictOrderStop','EDecisionEvent','ECompleteBoundaryCandleGeometry','DecimalStringSerialization',
                  'firstStrictOrderStopAfterExactConfirmation','parentStopNotBeforePhysicalConfirmation')
      for category in categories:
        record['checks'][category]='FAIL' if any(x['check']==category for x in record['failures']) else 'PASS'
      records.append(record)
      print(json.dumps({'case':case['name'],'folder':folder,'failures':len(record['failures']),'orderB':record['checks']['orderBPublishedProvenance']}),flush=True)
  (OUT/'raw-invariants.json').write_text(json.dumps(records,indent=2),encoding='utf-8')

if __name__=='__main__': main()
