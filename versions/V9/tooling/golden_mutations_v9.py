"""Exact mutation controls on the frozen Golden document, not edited Golden files."""
import argparse,json,copy,hashlib
from pathlib import Path
from zipfile import ZipFile
from strict_golden import stable_payload,GOLDEN_ZIP_SHA256,sha256

def main():
 p=argparse.ArgumentParser();p.add_argument('--golden',type=Path,required=True);p.add_argument('--case',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert sha256(a.golden.read_bytes())==GOLDEN_ZIP_SHA256;c=json.loads(a.case.read_text());stem=Path(c['name']).stem.replace(' ','_')
 with ZipFile(a.golden) as z:
  raw=z.read('runs/github_baseline/'+stem+'.json');stable=z.read('runs/github_baseline/'+stem+'.stable.json')
 orig=json.loads(raw);ref,rs=stable_payload(raw);assert ref==stable and sha256(ref)==c['stable_output_sha256'];ser=lambda x:json.dumps(x,ensure_ascii=True,separators=(',',':')).encode();assert ser(orig)==raw.rstrip(b'\r\n'),'reserialization would contaminate mutation'
 tests=[]
 def run(name,fn,accepted=False):
  x=copy.deepcopy(orig);fn(x);data=ser(x);assert data!=ser(orig)
  try:b,s=stable_payload(data);same=b==ref and s==rs;error=None
  except ValueError as e:same=False;error=str(e)
  assert same==accepted,name;tests.append({'test':name,'expected_acceptance':accepted,'actual_acceptance':same,'status':'PASS','error':error})
 b=lambda x:x['directions']['bullish']
 run('decimal_digit',lambda x:b(x)['reactions'][0].__setitem__('boxTop','9'+b(x)['reactions'][0]['boxTop']))
 run('order_parent_provenance',lambda x:b(x)['orderAudit'][0].__setitem__('causes',['tampered_parent']))
 run('reaction_order',lambda x:b(x)['reactions'].__setitem__(slice(0,2),list(reversed(b(x)['reactions'][:2]))))
 run('direction',lambda x:x['directions'].__setitem__('bullish',x['directions']['bearish']))
 run('delete_blue',lambda x:b(x)['blueLines'].pop(0))
 run('candidate_tie',lambda x:b(x)['eZones'][0].__setitem__('number',b(x)['eZones'][0]['number']+1))
 run('timing_type',lambda x:x['timings']['phasesMs'].__setitem__(next(iter(x['timings']['phasesMs'])),'wrong'))
 run('timing_unknown_key',lambda x:x['timings'].__setitem__('extra',1))
 run('timing_unknown_phase',lambda x:x['timings']['phasesMs'].__setitem__('extra',1.0))
 run('timing_measurement_only',lambda x:x['timings'].__setitem__('bridgeTotalMs',x['timings']['bridgeTotalMs']+100.0),True)
 a.out.write_text(json.dumps({'status':'PASS','frozen_reference_sha256':sha256(ref),'controls':tests,'scope':'strict verifier on authentic pinned output; no oracle edits'},indent=2)+'\n');print(len(tests),'PASS')
if __name__=='__main__':main()
