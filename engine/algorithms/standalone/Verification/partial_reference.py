"""Partial independently expressed reference. NOT a full TradingBot engine."""
from decimal import Decimal
from datetime import datetime
from itertools import groupby


def containment(intervals, start, end):
    return [item for a,b,item in intervals if a < start and b >= end]


def ordered_naive(values):
    return all(type(v) is datetime and v.tzinfo is None for v in values) and list(values) == sorted(values)


def normalize(x):
    return x if isinstance(x, Decimal) else Decimal(str(x))


def strict(direction, value, level):
    return (value < level) if direction == 'bullish' else (value > level)


def confirmation(direction, value, level):
    return strict(direction, level, value)


def aggregate(rows, timeframe, lower_only=False):
    # Normalize once, using the first representation in the type/value class.
    cache={}
    def prices(row):
        return tuple(cache.setdefault((type(row[k]),row[k]), normalize(row[k])) for k in ('open','high','low','close'))
    normalized=[(int(row['time']), *prices(row)) for row in rows]
    def reduce_by(key):
        result=[]
        for t, items in groupby(normalized, key=key):
            it=iter(items); _,o,h,l,c=next(it)
            for _,_,hi,lo,cl in it:
                if hi>h: h=hi
                if lo<l: l=lo
                c=cl
            result.append(dict(time=t,open=o,high=h,low=l,close=c))
        return result
    return reduce_by(lambda r:r[0]), [] if lower_only else reduce_by(lambda r:r[0]//timeframe*timeframe)


V,R,P='trueFalse','trueFalseRepairTime','trueFalseRepeated'
PRIORITY={'sZones':{'blue':1,'red':3},'eZones':{'blue':2,'red':4}}

def tf(direction, group, crossing=None, closed=None):
    primary='primaryLows' if direction=='bullish' else 'primaryHighs'
    events={}
    for family in (primary,'stopAlls','eZones','sZones'):
        for row in group.get(family,[]):
            for label in (V,R,P): row.pop(label,None)
            if row.get('calculationValid') is not False:
                events.setdefault(row['sourceTime'],(family,row))
    basics=[]; stop_groups=[[]]
    for source in sorted(events):
        family,row=events[source];row[V]=None
        if family==primary:
            stop_groups.append([])
            if row['number'] in (1,2,3): row[V]='T' if row['number']==1 else 'F'
        elif family=='stopAlls':stop_groups[-1].append(row)
        else: basics.append((family,row))
    seen={}; history={}; started=False
    def mark_repair(row,t):
        if crossing is not None and R not in row:
            result=crossing(direction,t,row['price'])
            if result is not None:row[R]=result
    for family,row in basics:
        s=family=='sZones';started=started or s
        if not started:continue
        rank=(PRIORITY[family][str(row['color' if s else 'family']).lower()],0 if s else row['number'])
        source=row['sourceTime']; weaker=[k for k in history if k<rank]
        engulf=any(history[k][2]>=2 for k in weaker)
        parent=seen.get(row.get('parentSourceTime'))
        verdict='T' if s or engulf else ('F' if parent=='T' else 'T') if parent is not None else ('F' if row['number']%2 else 'T')
        seen[source]=row[V]=verdict
        for k in weaker:
            older,nrepair,_=history.pop(k)
            if older[V]=='F' and nrepair==1:mark_repair(older,source)
        if engulf:history={k:(a,b,0) for k,(a,b,c) in history.items()}
        a=b=1
        if rank in history:
            old,ar,br=history[rank]
            if old[V]==verdict:
                a+=ar;b+=br
                if verdict=='F':
                    if old.get(R,-1)>=source:old.pop(R)
                    mark_repair(row,source)
        history[rank]=(row,a,b)
    for group_rows in stop_groups:
        prev=prev_end=max_end=0; start=None; origin=None; prefix=[]; fresh=False
        for row in group_rows:
            n=row['number']
            if start is None or n<=prev:
                prev_end=prev;max_end=max(max_end,prev_end);start=origin=n;prefix=[];fresh=False
            elif fresh:origin=n;fresh=False
            prev=n;row[V]='T' if (n-origin)%2==0 else 'F'
            if n<=max_end:
                prefix.append(row)
                if n in (prev_end,max_end) and (closed is None or closed(row)):
                    for r in prefix:r[P]=True;r[V]='T' if (r['number']-start)%2==0 else 'F'
                    fresh=True
