#!/usr/bin/env python3
"""Controlled mutation tests for the scoped internal semantic trace comparator."""
import copy,gzip,json,tempfile
from pathlib import Path
from compare_internal_fast import compare

def write(p,events):
    with gzip.open(p,'wt',encoding='utf8') as out:
        for i,event in enumerate(events,1):
            out.write(json.dumps({'schema':'tradingbot.v9.internal-observer.v1','event_ordinal':i,**event},separators=(',',':'))+'\n')

def check(outpath):
    base=[{'stage':'e_zone_detector','method':'EZoneDetector._zone','direction':'bullish','inputs':{'status':'complete_supported','value':{'$tuple':[1]}},
           'result':{'status':'complete_supported','value':{'$decimal':'100.00'}},'pre_state':{},'post_state':{},'raw_time_observed':100},
          {'stage':'e_zone_detector','method':'EZoneDetector._zone','direction':'bullish','inputs':{'status':'complete_supported','value':{'$tuple':[2]}},
           'result':{'status':'complete_supported','value':None},'pre_state':{},'post_state':{},'rejection_reason':'NO_ELIGIBLE_ORDER_AFTER_CANONICAL_ROUTE_FILTER'},
          {'stage':'e_zone_detector','method':'EZoneDetector._build_zone','direction':'bearish','inputs':{'status':'complete_supported','value':{}},
           'result':{'status':'complete_supported','value':{'$decimal':'99.995'}},'pre_state':{},'post_state':{},'raw_time_observed':105}]
    tests=[]
    with tempfile.TemporaryDirectory() as td:
        target=Path(td);anchor=target/'anchor.gz';write(anchor,base)
        variants={
            'self_same':(copy.deepcopy(base),'PASS'),
            'one_decimal_digit':(copy.deepcopy(base),'FAIL'),
            'rejection_reason':(copy.deepcopy(base),'FAIL'),
            'same_family_swap':(copy.deepcopy(base),'FAIL'),
            'input_only_drift':(copy.deepcopy(base),'PASS'),
            'cross_family_swap_not_covered':(copy.deepcopy(base),'PASS'),
        }
        variants['one_decimal_digit'][0][0]['result']['value']['$decimal']='100.01'
        variants['rejection_reason'][0][1]['rejection_reason']='DIFFERENT_REASON'
        variants['same_family_swap'][0][:2]=list(reversed(variants['same_family_swap'][0][:2]))
        variants['input_only_drift'][0][0]['inputs']['value']['$tuple'][0]=11
        variants['cross_family_swap_not_covered'][0][:]=[base[2],base[0],base[1]]
        for name,(events,expected) in variants.items():
            path=target/(name+'.gz');write(path,events)
            r=compare(anchor,path)
            # Source event ordinals are intentionally renumbered by writer.
            status='PASS' if r['status']==expected else 'FAIL'
            if name=='input_only_drift' and not r['input_drift']:status='FAIL'
            tests.append({'name':name,'expected':expected,'actual':r['status'],'assertion':status,'scoped_coverage_only':True,'input_drift':r['input_drift']})
    report={'suite':'V9 internal observer comparator mutation (not full semantic trace proof)',
            'status':'PASS' if all(t['assertion']=='PASS' for t in tests) else 'FAIL',
            'tests':tests}
    Path(outpath).write_text(json.dumps(report,indent=2));print(report['status'],len(tests));return report
if __name__=='__main__':
    import sys
    r=check(sys.argv[1] if len(sys.argv)>1 else '/mnt/data/V9_continue/results/V9_INTERNAL_MUTATION_TESTS.json')
    sys.exit(r['status']!='PASS')
