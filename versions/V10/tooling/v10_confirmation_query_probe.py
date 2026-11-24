"""V10 isolated query experiment; does NOT modify or invoke a new runtime path.
Exact reference loop extracted from pinned V8.1 _compute_direct_parent_stop_order.
"""
import argparse, ast, csv, datetime as dt, hashlib, json, random, statistics, time, tracemalloc
from pathlib import Path
from types import SimpleNamespace

SOURCE_SHA='87e1d9beae3617b26e6cfca94d87506988037f37331316073c8ea822d2725268'
def reference_from_source(path):
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    tree=ast.parse(raw);cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='OrderAuditEngineMixin'); fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='_compute_direct_parent_stop_order')
    node=next(x for x in fn.body if isinstance(x,ast.If) and ast.unparse(x.test)=='confirmation_after is not None' and any(isinstance(y,ast.While) for y in x.body))
    assert ast.unparse(node.body[0].test)=='direct_position < len(self.opposite_reactions) and self._opposite_confirmations[direct_position] <= confirmation_after'
    module=ast.parse('def reference(self, direct_position, confirmation_after):\n    return direct_position\n');module.body[0].body.insert(0,node);ns={};exec(compile(ast.fix_missing_locations(module),str(path),'exec'),ns)
    return ns['reference'],node.lineno

class ConfirmationIndex:
    """Immutable fixed sequence: first position >= left with value strictly > threshold.
    No sorting; no use in production; no mutable-cache claim.
    """
    def __init__(self,values):
        if type(values) is not tuple or any(type(v) is not dt.datetime or v.tzinfo is not None for v in values):raise TypeError('only immutable naive native datetime sequence supported')
        self.values=values;self.length=len(values);self.size=1 << max(0,(len(values)-1).bit_length());self.tree=[None]*(2*self.size);self.tree[self.size:self.size+self.length]=values
        for i in range(self.size-1,0,-1):
            a,b=self.tree[2*i],self.tree[2*i+1];self.tree[i]=a if b is None or (a is not None and a>=b) else b
    def first_gt(self,left,threshold):
        if type(left) is not int or not 0<=left<=self.length:raise ValueError('invalid left')
        if threshold is None:return left
        if type(threshold) is not dt.datetime or threshold.tzinfo is not None:raise TypeError('unsupported threshold')
        def search(i,lo,hi):
            val=self.tree[i]
            if hi<=left or val is None or val<=threshold:return self.length
            if hi-lo==1:return lo
            m=(lo+hi)//2;v=search(i*2,lo,m)
            return v if v!=self.length else search(i*2+1,m,hi)
        return search(1,0,self.size)

def main():
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args();ref,line=reference_from_source(args.source);rng=random.Random(20261124);base=dt.datetime(2026,1,1);stamp=lambda k:base+dt.timedelta(seconds=k*5)
    suites=[];total=0
    for name,size in [('empty',0),('one',1),('duplicate_nonmonotone',128),('ordered_with_ties',2048),('stress',8192)]:
        # Fixed synthetic sequences, not market outputs: exact native datetimes with ties and gaps.
        values=tuple(stamp(v) for v in ([rng.randrange(max(1,size//3)) for _ in range(size)] if name in ('duplicate_nonmonotone','stress') else sorted(rng.randrange(max(1,size//3)) for _ in range(size))))
        items=tuple(object() for _ in values);obj=SimpleNamespace(opposite_reactions=items,_opposite_confirmations=values)
        tracemalloc.start();t=time.perf_counter_ns();idx=ConfirmationIndex(values);build=(time.perf_counter_ns()-t)/1e9;_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        queries=[(rng.randrange(size+1), None if j%19==0 else stamp(rng.choice([-1,0,size//3+1,rng.randrange(max(1,size//3))]))) for j in range(2500)]
        runs=[];expected=None
        for mode in ('reference','index','index','reference'):
            t=time.perf_counter_ns();res=[ref(obj,l,h) if mode=='reference' else idx.first_gt(l,h) for l,h in queries];wall=(time.perf_counter_ns()-t)/1e9
            if expected is None:expected=res
            assert expected==res
            assert all((p==size or items[p] is items[q]) for p,q in zip(expected,res))
            runs.append({'mode':mode,'wall_s':wall})
        scanned=sum((p-l)+(p<size) for (l,h),p in zip(queries,expected) if h is not None and l<size)
        suites.append(dict(name=name,length=size,queries=len(queries),status='PASS',build_s=build,build_traced_peak_bytes=peak,reference_examined_rows=scanned,results_sha256=hashlib.sha256(json.dumps(expected).encode()).hexdigest(),runs=runs,median_wall_s={m:statistics.median(r['wall_s'] for r in runs if r['mode']==m) for m in ('reference','index')}));total+=len(queries)
    # Rebuild after change; the prior immutable snapshot remains unchanged; no production mutation/invalidation proven.
    old=(stamp(0),stamp(0));new=(stamp(0),stamp(2));before=ConfirmationIndex(old);after=ConfirmationIndex(new);assert before.first_gt(0,stamp(1))==2 and after.first_gt(0,stamp(1))==1
    r=dict(status='PASS',source_sha256=SOURCE_SHA,source_line=line,seed=20261124,total_queries=total,suites=suites,isolated_rebuild_control='PASS',scope='Only extracted confirmation-skip subquery; excludes gate/blocking/geometry/Order selection. Synthetic microbenchmark, not native hotpath frequency or promotion.',verdict='EXPERIMENTAL_NOT_PROMOTED',full_state_gate='INCOMPLETE');args.out.write_text(json.dumps(r,indent=2)+'\n');print('V10 isolated',total,'exact queries PASS')
if __name__=='__main__':main()
