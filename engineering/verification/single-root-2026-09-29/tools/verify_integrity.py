"""Verify complete relocation, protected bytes, source imports and live document links."""
from pathlib import Path
import ast
import hashlib
import json
import os
import re
import subprocess
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent.parent
rows=json.loads((OUT/'inventory.json').read_text())
changed=[];missing=[];engine=[];raw=[];archives=[];regenerated=[]
for item in rows:
    target=ROOT/item['destination']
    if item['owner']=='generated-dependency-build-cache' and item['origin']=='project' and item['action']=='keep':
        regenerated.append(item['destination'])
        continue
    if not target.is_file():missing.append(item['destination']);continue
    if item['sha256'] and hashlib.sha256(target.read_bytes()).hexdigest()!=item['sha256']:
        changed.append(item['destination'])
    if item['origin']=='project' and item['source'].startswith('engine/') and item['owner']=='calculation-authority':
        engine.append(item['destination'])
    if item['origin']=='external' and item['source'].startswith('data/'):
        raw.append(item['destination'])
    if item['destination'].startswith(('engineering/archive/', 'engineering/verification/history/')):
        archives.append(item['destination'])
assert not missing, missing
assert not [x for x in changed if x in engine+raw+archives], 'Protected source/RAW/evidence changed'
assert not ROOT.with_name(ROOT.name+'-Local').exists(), 'External state root still exists'
assert (ROOT/'.git/index').read_bytes()==(OUT/'baseline-git-index').read_bytes(), 'Initial Git index changed'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT)==(OUT/'baseline-head.txt').read_bytes(), 'HEAD changed'

source_files=[]
for base in [ROOT/'apps/chart', ROOT/'engine']:
    for directory,dirs,files in os.walk(base):
        dirs[:]=[d for d in dirs if d not in {'node_modules','state','__pycache__','dist','.vite','.vite-temp'}]
        source_files.extend(Path(directory)/f for f in files if f.endswith(('.js','.mjs','.py','.html','.css')))
broken_imports=[];js=[];python=[];subprocess_imports=[]
for p in source_files:
    content=p.read_text(encoding='utf-8-sig')
    if p.suffix=='.py':ast.parse(content,filename=str(p));python.append(p)
    if p.suffix in ('.js','.mjs'):
        r=subprocess.run(['node','--check',str(p)],capture_output=True)
        assert r.returncode==0,r.stderr.decode(errors='replace')
        js.append(p)
        for m in re.finditer(r'(?:from\s+|import\s*\(\s*|import\s*)[\"\'](\.{1,2}/[^\"\']+)',content):
            relative=m[1].split('?')[0]
            if (p.parent/relative).exists():continue
            # Node --eval modules resolve from the chart test runner's cwd,
            # not from the file containing the inline program string.
            line_start=content.rfind('\n',0,m.start())+1
            prefix=content[line_start:m.start()]
            is_inline_eval=('const program =' in prefix and
                            "['--input-type=module', '-e', program]" in content and
                            'execFileSync(process.execPath' in content)
            if is_inline_eval and (ROOT/'apps/chart'/relative).is_file():
                subprocess_imports.append((p.relative_to(ROOT).as_posix(),relative,'apps/chart'))
                continue
            broken_imports.append((p.relative_to(ROOT).as_posix(),relative))
assert not broken_imports,broken_imports
links=[];broken_links=[]
for p in [ROOT/'README.md',ROOT/'AGENTS.md',*(ROOT/'engineering/docs').rglob('*.md')]:
    text=p.read_text(encoding='utf-8-sig')
    for m in re.finditer(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',text):
        target=m[1].split('#')[0].strip('<>')
        if not target or re.match(r'^[a-zA-Z]+:',target):continue
        links.append((p.relative_to(ROOT).as_posix(),target))
        if not (p.parent/unquote(target)).exists():broken_links.append((p.relative_to(ROOT).as_posix(),target))
assert not broken_links,broken_links
local_ignored=[ROOT/'apps/chart/state',ROOT/'apps/chart/tests',ROOT/'engine/tests',ROOT/'engineering/archive',ROOT/'engineering/verification']
for p in local_ignored:
    r=subprocess.run(['git','check-ignore',str(p.relative_to(ROOT))+'/'],cwd=ROOT,capture_output=True)
    assert r.returncode==0, f'Local-only path is not ignored: {p}'
result=dict(status='PASS',physical_baseline_files=len(rows),moves=sum(x['action']=='move' for x in rows),
            preserved_engine_files=len(engine),preserved_raw_and_sidecar_files=len(raw),preserved_archive_evidence_files=len(archives),
            changed_files=changed,missing_files=missing,source_syntax=dict(python=len(python),javascript=len(js)),
            imports_broken=broken_imports,inline_node_eval_imports=subprocess_imports,links_checked=len(links),links_broken=broken_links,
            external_root_exists=False,index_unchanged=True,head_unchanged=True)
(OUT/'integrity-results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
