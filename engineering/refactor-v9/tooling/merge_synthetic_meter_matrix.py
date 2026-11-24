#!/usr/bin/env python3
"""Fail closed combining two independent metered runs, exactly 4 sizes x 2 variants."""
import argparse,json,hashlib
from pathlib import Path
NEEDED={(n,v) for n in (100000,250000,500000,1000000) for v in ('original','v81')}

def main(out,a,b):
 all_rows={}
 for f in (a,b):
  data=json.loads(Path(f).read_text())
  for row in data['rows']:
   key=(row['bars'],row['variant'])
   if key in all_rows:
    prev=all_rows[key]
    if (row.get('selected_instrumented_operations'),row.get('stable_sha256'),row.get('status'))!=(prev.get('selected_instrumented_operations'),prev.get('stable_sha256'),prev.get('status')):
     raise ValueError('overlap differs '+str(key))
   all_rows[key]=row
 missing=NEEDED-set(all_rows)
 failures=[key for key,row in all_rows.items() if row.get('status')!='PASS' or row.get('stable_pass') is not True or row.get('telemetry_schema_pass') is not True]
 report={'status':'PASS' if not missing and not failures else 'INCOMPLETE',
         'scope':'SELECTED AST SITES ONLY, never total Python operations',
         'expected':8,'completed':len(all_rows),'missing':sorted([list(x) for x in missing]),
         'failures':[list(x) for x in failures],
         'rows':[all_rows[key] for key in sorted(all_rows)]}
 Path(out).write_text(json.dumps(report,indent=2))
 print(report['status'],report['completed'],'/',report['expected'])
 return 0 if report['status']=='PASS' else 2
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--first',required=True);p.add_argument('--second',required=True);x=p.parse_args();raise SystemExit(main(x.out,x.first,x.second))