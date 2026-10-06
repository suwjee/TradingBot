"""Full-engine reflection on synthetic continuous history, independent of market RAW."""
from decimal import Decimal
from pathlib import Path
import json, random, subprocess
from run_raw_matrix import OUT, command

PRICE_KEYS={'boxTop','boxBottom','sourceExtreme','brokenLevel','linePrice','fibonacciLevel','price','parentPrice',
            'blue1StopLevel','blue2StopLevel','continuationLevel','aPrice','orderBoxTop','orderBoxBottom','orderStopLevel','stopLevel',
            'anchorBehaviorExtreme','resetBrokenLevel','legBoundary'}
SWAPS={'boxTop':'boxBottom','boxBottom':'boxTop','boxTopSourceIndex':'boxBottomSourceIndex','boxBottomSourceIndex':'boxTopSourceIndex',
       'boxTopSourceTime':'boxBottomSourceTime','boxBottomSourceTime':'boxTopSourceTime',
       'orderBoxTop':'orderBoxBottom','orderBoxBottom':'orderBoxTop',
       'orderBoxTopSourceIndex':'orderBoxBottomSourceIndex','orderBoxBottomSourceIndex':'orderBoxTopSourceIndex',
       'orderBoxTopSourceTime':'orderBoxBottomSourceTime','orderBoxBottomSourceTime':'orderBoxTopSourceTime'}

def reflect(value,key=''):
    if value is None:return None
    if isinstance(value,list):return [reflect(x,key) for x in value]
    if isinstance(value,dict):return {SWAPS.get(k,k):reflect(v,k) for k,v in value.items()}
    if key in PRICE_KEYS:return str(Decimal('10000')-Decimal(str(value)))
    if key in ('direction','orderDirection'): return {'bullish':'bearish','bearish':'bullish'}[value]
    return value

def numeric_equal(a,b):
    if isinstance(a,dict) and isinstance(b,dict):return a.keys()==b.keys() and all(numeric_equal(a[k],b[k]) for k in a)
    if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(numeric_equal(x,y) for x,y in zip(a,b))
    if isinstance(a,str) and isinstance(b,str):
        try:return Decimal(a)==Decimal(b)
        except Exception:return a==b
    return a==b

def main():
    root=OUT/'runtime-mirror'; root.mkdir(exist_ok=True)
    rng=random.Random(1947)
    rows=[]; price=4000; start=1789000020
    for block in range(1200):
        changes=[rng.choice([x for x in range(-8,9) if x]) for _ in range(6)]
        if sum(changes)==0: changes[-1]+=1 if changes[-1]>0 else -1
        for j,change in enumerate(changes):
            close=price+change
            rows.append({'time':start+(block*6+j)*5,'open':price,
                         'high':max(price,close)+rng.randint(0,8),
                         'low':min(price,close)-rng.randint(0,8),'close':close})
            price=close
    mirrored=[{'time':r['time'],'open':10000-r['open'],'high':10000-r['low'],
               'low':10000-r['high'],'close':10000-r['close']} for r in rows]
    outputs=[]
    for name,input_rows in [('original',rows),('reflected',mirrored)]:
        path=root/(name+'.synthetic.json'); path.write_text(json.dumps(input_rows),encoding='utf-8')
        cmd=command(path,30,rows[0]['time'],rows[-1]['time']); cmd.remove('--bridge-output')
        completed=subprocess.run(cmd,capture_output=True,timeout=180)
        (root/(name+'.stdout.json')).write_bytes(completed.stdout)
        (root/(name+'.stderr.log')).write_bytes(completed.stderr)
        if completed.returncode: raise RuntimeError(completed.stdout.decode())
        outputs.append(json.loads(completed.stdout)['directions'])
    records=[]
    for direction in ('bullish','bearish'):
      other='bearish' if direction=='bullish' else 'bullish'
      for stage,items in outputs[0][direction].items():
        expected=reflect(items); actual=outputs[1][other][stage]
        first=next((i for i,(a,b) in enumerate(zip(expected,actual)) if not numeric_equal(a,b)),None)
        equal=numeric_equal(expected,actual)
        records.append({'direction':direction,'stage':stage,'count':len(items),'reflectedCount':len(actual),
                        'status':'PASS' if equal else 'FAIL','firstIndex':first,
                        'expected':expected[first] if first is not None else None,'actual':actual[first] if first is not None else None})
    (root/'results.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    print(json.dumps(records,indent=2))

if __name__=='__main__':main()
