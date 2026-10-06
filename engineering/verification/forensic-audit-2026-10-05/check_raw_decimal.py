"""Validate exact OHLC/lexemes and cross-granularity compatibility, read-only."""
from pathlib import Path
from decimal import Decimal
import json, orjson
OUT=Path(__file__).resolve().parent
registry=json.loads((OUT/'raw-registry.json').read_text())
records=[]
fine=None
for idx,item in enumerate(registry):
    raw=Path(item['path']).read_bytes().removeprefix(b'\xef\xbb\xbf')
    exact=json.loads(raw,parse_float=Decimal)
    fast=orjson.loads(raw)
    errors=[]; lexeme_losses=[]
    for i,(a,b) in enumerate(zip(exact,fast)):
        prices={key:Decimal(str(a[key])) for key in ('open','high','low','close')}
        if not all(v.is_finite() for v in prices.values()) or not(prices['low']<=min(prices['open'],prices['close'])<=max(prices['open'],prices['close'])<=prices['high']):
            if len(errors)<5: errors.append(i)
        for key,value in prices.items():
            if value!=Decimal(str(b[key])):
                if len(lexeme_losses)<5:lexeme_losses.append({'row':i,'field':key,'exact':str(value),'fast':str(b[key])})
    records.append({'rawIndex':idx,'rows':len(exact),'exactOHLC':'PASS' if not errors else 'FAIL',
                    'errorExamples':errors,'numericLexemeValuesPreserved':'PASS' if not lexeme_losses else 'FAIL','lossExamples':lexeme_losses})
    if idx==1:
        fine={int(row['time']):{k:Decimal(str(row[k])) for k in ('open','high','low','close')} for row in exact}
    print(idx,len(exact),'exactOHLC',records[-1]['exactOHLC'],'numericLexemes',records[-1]['numericLexemeValuesPreserved'],flush=True)
compat=[]
for idx,item in enumerate(registry):
    if item['nominalSeconds']!=5 or 'XAUUSD' not in item['path']: continue
    rows=orjson.loads(Path(item['path']).read_bytes().removeprefix(b'\xef\xbb\xbf'))
    compared=0; mismatches=0; examples=[]
    for row in rows:
        t=int(row['time']); parts=[fine.get(t+n) for n in range(5)]
        if any(p is None for p in parts):continue
        compared+=1
        aggregate={'open':parts[0]['open'],'close':parts[-1]['close'],
                   'high':max(p['high'] for p in parts),'low':min(p['low'] for p in parts)}
        actual={k:Decimal(str(row[k])) for k in aggregate}
        if aggregate!=actual:
            mismatches+=1
            if len(examples)<5:examples.append({'time':t,'oneSecondAggregate':{k:str(v) for k,v in aggregate.items()},'fiveSecondRAW':{k:str(v) for k,v in actual.items()}})
    compat.append({'rawIndex':idx,'completeFiveSecondBucketsCompared':compared,'differentOHLCBuckets':mismatches,'examples':examples})
    print('cross-granularity',idx,compared,mismatches,flush=True)
result={'exactValidation':records,'oneSecondVersusFiveSecond':compat,
        'crossGranularityMeaning':'Compare only intervals having all five exact one-second rows. Differences, if any, must remain explicit; finer precedence does not rewrite coarser RAW.'}
(OUT/'raw-decimal-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
