from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_real_matrix import run,W
M=json.loads((W/'tooling/inputs_verified.json').read_text())
item=next(x for x in M['datasets'] if x['records']==97930)
r=run(item,profile=True,tag='v81profile_97k')
(W/'output/V9_CPROFILE_RUN_97K.json').write_text(json.dumps(r,indent=2))
print(json.dumps({'records':r['bars'],'status':r['status'],'wall_s':r['wall_s'],'rss_mib':r['peak_rss_mib'],'parity':r['stable_bytes_equal']}),flush=True)
if r['status']!='PASS':sys.exit(1)
