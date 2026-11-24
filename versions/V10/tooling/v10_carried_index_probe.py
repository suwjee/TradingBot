"""Experimental explicit-notification carried creation index, not a runtime patch.
Uses frozen V8.1 validator as the oracle. No inferred ownership/invalidation.
"""
import argparse, bisect, hashlib, json, random, sys, time
from collections import Counter
from datetime import datetime,timedelta,timezone
from decimal import Decimal, getcontext
from pathlib import Path
from types import SimpleNamespace

SHA='87e1d9beae3617b26e6cfca94d87506988037f37331316073c8ea822d2725268'
class ExplicitRowIndex:
    """Caller must notify every changed row; authoritative ledger kept intact.
    Rebuild on deletion/reset, invalid previous index, or timezone conflict.
    No runtime fallback or callback alias proof; only this closed experiment.
    """
    def __init__(self,ledger,validate):
        self.ledger=ledger; self.validate=validate;self.counts=Counter();self.rebuild()
    def rebuild(self):
        self.keys=list(self.ledger);self.ordinals={k:i for i,k in enumerate(self.keys)}
        self.index=self.validate(list(self.ledger.values()));self.by_ordinal={};self.counts['full_build']+=1
        if self.index is not None:
            for t,o in self.index[0]:self.by_ordinal.setdefault(o,[]).append(t)
    def notify(self,key,op):
        if op=='structure' or self.index is None:
            self.rebuild();return
        new=op=='append'
        if new:
            if key in self.ordinals or len(self.ledger)!=len(self.keys)+1 or next(reversed(self.ledger))!=key:raise ValueError('invalid explicit append')
            ordinal=len(self.keys);self.keys.append(key);self.ordinals[key]=ordinal
        else:
            if op!='replace' or key not in self.ordinals or len(self.ledger)!=len(self.keys):raise ValueError('invalid explicit replacement')
            ordinal=self.ordinals[key]
        row=self.validate([self.ledger[key]]); self.counts['row_validation']+=1
        if row is None:
            self.rebuild();return
        events,tz=self.index
        old=self.by_ordinal.pop(ordinal,[])
        for t in old:
            pos=bisect.bisect_left(events,(t,ordinal))
            if pos==len(events) or events[pos]!=(t,ordinal):raise ValueError('lost previous event')
            events.pop(pos)
        fresh,new_tz=row
        if events and fresh and tz is not new_tz:
            self.rebuild();return
        if not events:tz=new_tz if fresh else None
        for t,_ in fresh:bisect.insort_right(events,(t,ordinal));self.by_ordinal.setdefault(ordinal,[]).append(t)
        self.index=(events,tz)
    def query(self,left,right):
        if self.index is None:return None
        events,tz=self.index
        if left.tzinfo is not tz or right.tzinfo is not tz:return None
        a=bisect.bisect_right(events,(left,len(self.keys)));b=bisect.bisect_left(events,(right,-1))
        return [self.ledger[self.keys[o]] for o in sorted({o for _,o in events[a:b]})]

def main():
    p=argparse.ArgumentParser();p.add_argument('--engine-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--scenario',choices=('valid','adversarial'),default='valid');a=p.parse_args();source=a.engine_root/'pipeline/order_audit_engine.py'
    if hashlib.sha256(source.read_bytes()).hexdigest()!=SHA:raise ValueError('reference hash mismatch')
    sys.path.insert(0,str(source.parent.resolve()));from order_audit_engine import OrderAuditEngineMixin
    validate=lambda entries:OrderAuditEngineMixin._validated_carried_creation_index(None,entries)
    rng=random.Random(20261124);base=datetime(2026,1,1);stamp=lambda x:base+timedelta(seconds=x*5)
    def entry(k):
        t=stamp(rng.randrange(120));r=SimpleNamespace(first_idx=k,break_idx=k+1)
        return dict(reaction_number=k+1,reaction=r,confirmation_time=t,stop_level=Decimal('12.3400'),stop_source_index=k,stop_source_time=t,stop_cross=(k,t,t+timedelta(seconds=20)),causes={('parent-stop','E1','red',t,t)},order_b_causes=[])
    ledger={i:entry(i) for i in range(80)};candidate=ExplicitRowIndex(ledger,validate);next_key=80;counts=Counter();elapsed=Counter();checks=0
    # Adversarial full-build controls include invalid rows and mixed timezone.
    for i in range(12000):
        mode=rng.choice((0,1,2,3,4,5,6,10)) if a.scenario=='valid' else rng.randrange(11);key=rng.choice(list(ledger)) if ledger else None
        if not ledger or mode==0:
            key=next_key;next_key+=1;ledger[key]=entry(key);op='append';counts['append']+=1
        elif mode==1:
            del ledger[key];op='structure';counts['delete']+=1
        elif mode==2:
            # Explicitly notified in-place earlier/later cause; duplicates and ties retained.
            row=ledger[key];t=stamp(rng.randrange(120));row['causes'].add(('parent-stop','E2','red',t,t));op='replace';counts['add_parent_cause']+=1
        elif mode==3:
            row=ledger[key];row['order_b_causes'].append({'physicalOrderConfirmationTime':stamp(rng.randrange(120))});op='replace';counts['add_b_cause']+=1
        elif mode==4:
            row=ledger[key];row['causes'].clear();row['order_b_causes'].clear();op='replace';counts['clear_causes']+=1
        elif mode==5:
            ledger[key]=entry(key);op='replace';counts['replace_row']+=1
        elif mode==6:
            row=ledger[key];row['causes']={(c[0],'PH1',c[2],c[3],c[4]) for c in row['causes']};op='replace';counts['relabel']+=1
        elif mode==7:
            row=ledger[key];row['stop_level']=Decimal('NaN');op='replace';counts['invalid_decimal']+=1
        elif mode==8:
            row=ledger[key];row['stop_level']=Decimal('12.3400');op='replace';counts['restore_decimal']+=1
        elif mode==9:
            row=ledger[key];row['confirmation_time']=stamp(0).replace(tzinfo=timezone.utc);op='replace';counts['mixed_timezone']+=1
        else:
            ledger[key]=entry(key);op='replace';counts['restore_row']+=1
        flags=dict(getcontext().flags);t=time.perf_counter_ns();candidate.notify(key,op);elapsed['incremental']+=time.perf_counter_ns()-t
        t=time.perf_counter_ns();reference=validate(list(ledger.values()));elapsed['reference']+=time.perf_counter_ns()-t
        assert dict(getcontext().flags)==flags and candidate.index==reference and (reference is None or candidate.index[1] is reference[1]),(i,mode)
        l=stamp(rng.randrange(120));r=stamp(rng.randrange(120));l,r=min(l,r),max(l,r)
        actual=candidate.query(l,r)
        if reference is None or reference[1] is not l.tzinfo:assert actual is None
        else:
            events=reference[0];rows=list(ledger.values());expected=[rows[j] for j in sorted({j for t,j in events if l<t<r})]
            assert len(expected)==len(actual) and all(x is y for x,y in zip(expected,actual));checks+=1
    assert hashlib.sha256(source.read_bytes()).hexdigest()==SHA
    report={'status':'PASS','seed':20261124,'scenario':a.scenario,'operations':sum(counts.values()),'operation_counts':dict(counts),'successful_range_identity_checks':checks,'index_counts':dict(candidate.counts),'elapsed_validation_only_s':{k:v/1e9 for k,v in elapsed.items()},'scope':'Explicit notified synthetic mutations; exact V8.1 validation oracle, time/ordinal identity, Decimal flags and fallback. Not native runtime invalidation proof. Concurrent execution; no performance promotion.','source_sha256':SHA,'verdict':'EXPERIMENTAL_NOT_PROMOTED'}
    a.out.write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
