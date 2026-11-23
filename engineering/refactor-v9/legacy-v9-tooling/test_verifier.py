#!/usr/bin/env python3
"""Controlled Golden comparison mutation tests, including a known upstream verifier blind spot."""
import json,zipfile,hashlib
from pathlib import Path
from strict_golden import stable_payload,stable_match,verify_freeze
from first_divergence import compare

WORK=Path(__file__).resolve().parents[1]
GOLDEN_ZIP=Path('/mnt/data/V9_inputs/TradingBot_GitHubMain_Baseline_30s_Both_01d54ecf_20261123_v1.zip')
D=json.loads((WORK/'golden/input_manifest.json').read_text())
FIVE=[x for x in D['dataset'] if x['nominal_raw_seconds']==5]
manifest={'baseline_git_commit':D['commit'],'datasets':[{'id':str(i),'file':x['name'],'records':x['raw_bars'],'first_time':x['first_time'],'last_time':x['last_time'],'raw_sha256':x['sha256']} for i,x in enumerate(FIVE)]}
with zipfile.ZipFile(GOLDEN_ZIP) as z:
 for x in manifest['datasets']:
  stem=Path(x['file']).stem.replace(' ','_')
  x['stable_output_sha256']=hashlib.sha256(z.read('runs/github_baseline/'+stem+'.stable.json')).hexdigest()
(WORK/'tooling/inputs_verified.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
assert verify_freeze(GOLDEN_ZIP,manifest)

# Match upstream GitHub verifier signature/logic as audited; does not validate timing extra keys.
def upstream_legacy_stable(raw):
 obj=json.loads(raw)
 if 'error' in obj:raise ValueError('Engine returned error')
 if obj.get('timeframe')!=30 or set(obj.get('directions',[]))!={'bullish','bearish'}:raise ValueError('Directions')
 marker=b',"timings":';off=raw.rfind(marker)
 if off<0 or not raw.endswith(b'}'):raise ValueError('missing timing')
 timing=obj['timings'];phase=timing['phasesMs']
 schema={'phase_keys':list(phase),'phase_types':[type(v).__name__ for v in phase.values()],
         'total_type':type(timing['bridgeTotalMs']).__name__}
 if not all(isinstance(v,(int,float)) and not isinstance(v,bool) for v in phase.values()):raise ValueError('not numeric')
 return raw[:off]+b'}',schema

s=FIVE[2];stem=Path(s['name']).stem.replace(' ','_');base=WORK/'golden/runs/github_baseline'/stem
original=Path(str(base)+'.json').read_bytes();expected,expected_schema=stable_payload(original)
meta=json.loads(Path(str(base)+'.metrics.json').read_text())
mutations={}
def rebuild(obj):return json.dumps(obj,separators=(',',':'),ensure_ascii=False).encode()
obj=json.loads(original)
mutations['one_decimal_digit']=original.replace(b'"boxTop":"',b'"boxTop":"9',1)
changed=json.loads(original);changed['directions']['bullish']['orderAudit'][0]['parentType']='_V9_MUTATION_';mutations['order_parent']=rebuild(changed)
changed=json.loads(original);changed['directions']['bullish']['reactions'][:2]=list(reversed(changed['directions']['bullish']['reactions'][:2]));mutations['reaction_swap']=rebuild(changed)
changed=json.loads(original);changed['directions']['bullish'],changed['directions']['bearish']=changed['directions']['bearish'],changed['directions']['bullish'];mutations['direction_swap']=rebuild(changed)
changed=json.loads(original);changed['directions']['bullish']['blueLines'].pop(0);mutations['delete_blue']=rebuild(changed)
changed=json.loads(original);changed['directions']['bullish']['eZones'][0]['number']+=999;mutations['tie_or_ordinal']=rebuild(changed)
changed=json.loads(original);changed['timings']['phasesMs']['Read source file']='not_numeric';mutations['timing_value_type']=rebuild(changed)
changed=json.loads(original);changed['timings']['phasesMs']['unrecognized_v9_key']=10.0;mutations['timing_phase_extra_key']=rebuild(changed)
changed=json.loads(original);changed['timings']['unrecognized_v9_key']=10.0;mutations['timing_top_extra_key']=rebuild(changed)
changed=json.loads(original);changed['timings']['bridgeTotalMs']+=777.;mutations['timing_value_only_allowed']=rebuild(changed)
results=[]
for name,blob in mutations.items():
 should_pass=name=='timing_value_only_allowed';legacy_accept=False
 try:
  legacy_stable,legacy_schema=upstream_legacy_stable(blob)
  legacy_accept=(legacy_stable==upstream_legacy_stable(original.rstrip(b'\n'))[0] and legacy_schema==upstream_legacy_stable(original.rstrip(b'\n'))[1])
 except Exception:pass
 strict_accept=False;error=None
 try:
  actual,sch=stable_payload(blob)
  strict_accept=actual==expected and sch==expected_schema
 except Exception as e:error=f'{type(e).__name__}: {e}'
 results.append({'test':name,'expected':'PASS' if should_pass else 'FAIL','actual':'PASS' if strict_accept else 'FAIL',
                 'test_status':'PASS' if strict_accept==should_pass else 'FAIL', 'upstream_accepts_mutation':legacy_accept,
                 'strict_error':error})
# The published verify_golden.py literally requires raw.endswith(b'}'), whereas native print() appends newline.
upstream_native_accepts=True
try:upstream_legacy_stable(original)
except Exception:upstream_native_accepts=False
results.append({'test':'upstream_native_newline_rejected','expected':'FAIL','actual':'FAIL' if not upstream_native_accepts else 'PASS',
                'test_status':'PASS' if not upstream_native_accepts else 'FAIL',
                'reason':'Upstream verifier rejects original valid native payload ending \n'})
# Trace comparator synthetic line insertion, source provenance, event swaps.

import gzip
tracefolder=WORK/'output';tracefolder.mkdir(exist_ok=True)
synthetic=[{'stage':'Reaction','direction':'bullish','raw_time':100,'entity_id':'1','field':'base','provenance':{'sourceIndex':1}},
           {'stage':'OrderAudit','direction':'bearish','raw_time':105,'entity_id':'2','field':'tie','provenance':{'parent':1}},
           {'stage':'StopAll','direction':'bearish','raw_time':110,'entity_id':'3','field':'reset','provenance':{}}]
a=tracefolder/'mutation_reference.jsonl';a.write_text(''.join(json.dumps(x)+'\n' for x in synthetic))
for name,arr in [('self',synthetic),('field_edit',[synthetic[0],{**synthetic[1],'field':'changed'},synthetic[2]]),('swap',[synthetic[1],synthetic[0],synthetic[2]]),('delete',synthetic[:-1]),('add',synthetic+[synthetic[2]])]:
 b=tracefolder/('mutation_'+name+'.jsonl');b.write_text(''.join(json.dumps(x)+'\n' for x in arr));r=compare(a,b)
 expected=name=='self';results.append({'test':'first_diff_'+name,'expected':'PASS' if expected else 'FAIL','actual':'PASS' if r['equal'] else 'FAIL',
                                       'test_status':'PASS' if r['equal']==expected else 'FAIL','first_diff':r['first_divergence']['field'] if r['first_divergence'] else None})
report={'freeze_self_check':'PASS','tests':results,'all_test_assertions_pass':all(x['test_status']=='PASS' for x in results),
        'upstream_verifier_finding':'The upstream version rejects valid native output ending newline, and after stripping that newline its schema comparator accepts extra top-level timings keys.'}
(WORK/'output/V9_FIRST_DIFF_TESTS.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({'freeze_self_check':'PASS','mutations':len(results),'passes':sum(x['test_status']=='PASS' for x in results),'legacy_timing_top_extra_key_accepted':next(x['upstream_accepts_mutation'] for x in results if x['test']=='timing_top_extra_key')},indent=2))
assert report['all_test_assertions_pass']
