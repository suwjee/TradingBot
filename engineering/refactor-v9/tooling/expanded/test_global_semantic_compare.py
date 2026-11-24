#!/usr/bin/env python3
"""Controlled mutation cases for chronology, tie, parent, prices and status."""
from __future__ import annotations
import copy,gzip,json,tempfile
from pathlib import Path
from global_semantic_trace_compare import report

def write(file,rows):
    with gzip.open(file,'wt',encoding='utf8') as fp:
        for i,row in enumerate(rows,1):
            fp.write(json.dumps({'schema':'tradingbot.v9.internal-observer.v1','event_ordinal':i,**row},separators=(',',':'))+'\n')

def run(out):
    base=[
      {'stage':'reaction_engine','method':'ReactionDetector.detect','direction':'bullish','inputs':{'status':'complete_supported','value':None},'result':{'status':'complete_supported','value':{'source_time':100,'close':{'$decimal':'100.000'}}},'pre_state':{},'post_state':{},'raw_time_observed':100},
      {'stage':'e_zone_detector','method':'EZoneDetector._zone','direction':'bullish','inputs':{'status':'complete_supported','value':None},'result':{'status':'complete_supported','value':{'source_time':110,'parent_source_time':90,'decision_time':115,'price':{'$decimal':'99.995'}}},'pre_state':{},'post_state':{},'raw_time_observed':110},
      {'stage':'lifecycle_engine','method':'detect_stopalls','direction':'bearish','inputs':{'status':'complete_supported','value':None},'result':{'status':'complete_supported','value':{'stopall':120,'winner':'S:2'}},'pre_state':{},'post_state':{},'raw_time_observed':120}
    ]
    variants={'self':(copy.deepcopy(base),'PASS'),
              'price_digit':(copy.deepcopy(base),'FAIL'),
              'parent_source_time':(copy.deepcopy(base),'FAIL'),
              'cross_family_swap':(copy.deepcopy(base),'FAIL'),
              'direction_change':(copy.deepcopy(base),'FAIL'),
              'event_time_tie':(copy.deepcopy(base),'FAIL'),
              'stopall_winner':(copy.deepcopy(base),'FAIL'),
              'drop_event':(copy.deepcopy(base),'FAIL'),
              'unallowed_rejection_reason':(copy.deepcopy(base),'FAIL'),
              'input_only_drift_currently_detected_but_not_failing':(copy.deepcopy(base),'PASS')}
    variants['price_digit'][0][1]['result']['value']['price']['$decimal']='99.996'
    variants['parent_source_time'][0][1]['result']['value']['parent_source_time']=91
    variants['cross_family_swap'][0][:]=[base[1],base[0],base[2]]
    variants['direction_change'][0][1]['direction']='bearish'
    variants['event_time_tie'][0][1]['raw_time_observed']=100
    variants['stopall_winner'][0][2]['result']['value']['winner']='E:1'
    variants['drop_event'][0].pop(1)
    variants['unallowed_rejection_reason'][0][1]['rejection_reason']='NONE'
    variants['input_only_drift_currently_detected_but_not_failing'][0][1]['inputs']['value']='modified'
    tests=[]
    with tempfile.TemporaryDirectory() as t:
        td=Path(t);f=td/'anchor.gz';write(f,base)
        for k,(rows,want) in variants.items():
            cand=td/(k+'.gz');write(cand,rows);got=report(f,cand)
            assertion='PASS' if got['status']==want else 'FAIL'
            if k=='input_only_drift_currently_detected_but_not_failing' and not got['first_input_drifts']:assertion='FAIL'
            tests.append({'case':k,'expected':want,'actual':got['status'],'assertion':assertion,'known_gap':'inputs are reported but not a hard FAIL' if k.startswith('input_only') else None})
    final={'status':'PASS' if all(x['assertion']=='PASS' for x in tests) else 'FAIL','count':len(tests),'tests':tests}
    Path(out).write_text(json.dumps(final,indent=2));return final
if __name__=='__main__':
    import sys
    r=run(sys.argv[1]);print(r['status'],r['count']);sys.exit(r['status']!='PASS')
