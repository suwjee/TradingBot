import ast
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(r'D:\My-Projects\TradingBot')
AUDIT = Path(__file__).resolve().parent
errors = []
python_files = list((ROOT / 'engine').rglob('*.py')) + list((ROOT / 'tests/engine').rglob('*.py'))
for path in python_files:
    ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))

js_files = [p for scope in ['apps/chart/src','apps/chart/server','apps/chart/scripts'] for p in (ROOT/scope).rglob('*') if p.suffix in ['.js','.mjs']]
js_files += [ROOT / 'apps/chart/vite.config.js']
imports = []
for path in js_files:
    result = subprocess.run(['node','--check',str(path)], capture_output=True)
    if result.returncode: errors.append({'file':str(path),'error':'Node syntax check failed'})
    text = path.read_text(encoding='utf-8-sig')
    for match in re.finditer(r'''(?:\bfrom\s*|\bimport\s*\(?\s*)['"](\.[^'"]+)['"]''', text):
        target = (path.parent/match[1]).resolve()
        imports.append({'source':path.relative_to(ROOT).as_posix(),'target':str(target),'exists':target.exists()})
        if not target.exists(): errors.append({'file':str(path),'error':'Missing relative import','target':str(target)})

links=[]
for path in [ROOT/'README.md',ROOT/'AGENTS.md',*(ROOT/'docs').rglob('*.md')]:
    text=path.read_text(encoding='utf-8-sig')
    for match in re.finditer(r'\[[^\]\n]+\]\(([^)\n]+)\)',text):
        href=match[1].split('#')[0].strip('<>')
        if not href or re.match(r'\w+://',href): continue
        target=(path.parent/href).resolve()
        links.append({'source':path.relative_to(ROOT).as_posix(),'target':href,'exists':target.exists()})
        if not target.exists(): errors.append({'file':str(path),'error':'Broken Markdown link','target':href})

bridge_path=ROOT/'engine/bridge/trading_pipeline.py'
spec=importlib.util.spec_from_file_location('cleanup_bridge',bridge_path)
bridge=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=bridge
spec.loader.exec_module(bridge)
argv=[]
for flag,file in [('reaction-engine','reaction_engine.py'),('blue-line-engine','blue_line_detector.py'),('a-zone-engine','a_zone_detector.py'),('s-zone-engine','s_zone_detector.py'),('e-zone-engine','e_zone_detector.py'),('lifecycle-engine','lifecycle_engine.py')]:
    argv.extend(['--'+flag,str(ROOT/'engine/pipeline'/file)])
argv.extend(['--data',str(ROOT.with_name('TradingBot-Local')/'data/raw'),'--timeframe','30','--from-time','0','--to-time','30','--direction','both'])
bundle=bridge.load_engines(bridge.parse_arguments(argv),{})
assert bundle is not None

baseline=json.loads((AUDIT/'baseline-inventory.json').read_text())
protected=json.loads((AUDIT/'protected-engine-hashes.json').read_text())
from audit import digest
engine_diff=[p for p,h in protected.items() if not (ROOT/p).exists() or digest(ROOT/p)!=h]
raw_diff=[r['path'] for r in baseline if r['classification']=='MARKET_DATA' and digest(ROOT.with_name('TradingBot-Local')/r['path'])!=r['sha256_before']]
results={'python_ast_files':len(python_files),'node_syntax_files':len(js_files),'relative_imports':len(imports),'markdown_links':len(links),'normal_bridge_dynamic_load':'PASS','engine_protected_files':len(protected),'engine_hash_diff':engine_diff,'raw_files':sum(r['classification']=='MARKET_DATA' for r in baseline),'raw_hash_diff':raw_diff,'errors':errors}
(AUDIT/'structural-checks.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
(AUDIT/'relative-imports.json').write_text(json.dumps(imports,indent=2),encoding='utf-8')
(AUDIT/'markdown-links.json').write_text(json.dumps(links,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
assert not errors and not engine_diff and not raw_diff
