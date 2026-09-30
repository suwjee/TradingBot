"""Freeze physical inventory and an explicit single-root migration map."""
from pathlib import Path
import csv
import hashlib
import json
import os
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[4]
EXTERNAL = ROOT.with_name(ROOT.name + '-Local')
OUT = Path(__file__).resolve().parent.parent
DOCS = {
    'docs/AI/AI_Operating_Protocol.md': 'engineering/docs/ai/operating-protocol.md',
    'docs/Project_Audit/Engineering_Audit_Workflow.md': 'engineering/docs/verification/engineering-audit-workflow.md',
    'docs/architecture/Frontend/UI_UX_Technical_Reference.md': 'engineering/docs/architecture/ui-ux-reference.md',
    'docs/architecture/Project/Technical_Architecture.md': 'engineering/docs/architecture/technical-architecture.md',
    'docs/development/General_Rules/Standalone_Reference_Specification.md': 'engineering/docs/development/standalone-reference-specification.md',
    'docs/development/Refactor_Rules/Zero_Difference_Refactor_Performance_Rules.md': 'engineering/docs/development/zero-difference-refactor.md',
    'docs/development/Test_Rules/Repository_Integrity.md': 'engineering/docs/verification/repository-integrity.md',
    'docs/development/Test_Rules/Local_Test_Workflow.md': 'engineering/docs/development/local-tests.md',
    'docs/operations/Local_State.md': 'engineering/docs/operations/local-state.md',
}

def destination(origin, rel):
    if origin == 'external':
        if rel.startswith(('data/', 'cache/', 'secret/', 'tmp/')):
            return 'apps/chart/state/' + rel
        if rel.startswith('runtime/'):
            return 'apps/chart/state/legacy-runtime/' + rel[8:]
        if rel.startswith('archive/'):
            return 'engineering/archive/' + rel[8:]
        if rel.startswith('cleanup-2026-09-29/'):
            return 'engineering/verification/history/cleanup-2026-09-29/' + rel[19:]
        raise ValueError('Unclassified external path: ' + rel)
    if rel in DOCS:
        return DOCS[rel]
    if rel.startswith('docs/graphify/'):
        return 'engineering/archive/repository-graphify/' + rel[14:]
    if rel.startswith('docs/'):
        raise ValueError('Unclassified current document: ' + rel)
    if rel == 'docs.zip':
        return 'engineering/archive/documentation/docs.zip'
    if rel == 'scripts/launch.bat':
        return 'launch.bat'
    if rel == 'scripts/start.ps1':
        return 'engineering/launch.ps1'
    if rel.startswith('tests/chart/'):
        return 'apps/chart/tests/' + rel[12:]
    if rel.startswith('tests/engine/helpers/'):
        return 'engine/tests/verification/' + rel[21:]
    if rel.startswith('tests/engine/'):
        return 'engine/tests/' + rel[13:]
    return rel

def classify(rel):
    if 'secret/' in rel:
        return 'authentication-state', False
    if 'node_modules/' in rel or '/dist/' in rel or '__pycache__/' in rel or '/.vite' in rel:
        return 'generated-dependency-build-cache', False
    if '/state/data/' in rel:
        return 'immutable-market-data', False
    if '/state/' in rel:
        return 'workstation-local-state', False
    if '/tests/' in rel:
        return 'component-verification', False
    if rel.startswith('engineering/archive/'):
        return 'historical-evidence', False
    if rel.startswith('engineering/verification/'):
        return 'migration-verification-evidence', False
    if rel.startswith('engineering/docs/'):
        return 'engineering-documentation', True
    if rel.startswith('engine/'):
        return 'calculation-authority', True
    if rel.startswith('apps/chart/'):
        return 'chart-application', True
    if rel in ('launch.bat', 'engineering/launch.ps1'):
        return 'windows-startup', True
    return 'repository-tooling-entrypoint', True

def enumerate_files(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != '.git')
        for name in sorted(files):
            yield Path(base) / name

def main():
    records = []
    for origin, root in [('project', ROOT), ('external', EXTERNAL)]:
        for p in enumerate_files(root):
            if OUT == p or OUT in p.parents:
                continue
            rel = p.relative_to(root).as_posix()
            target = destination(origin, rel)
            owner, tracked = classify(target)
            secret = 'secret/' in rel
            digest = None if secret else hashlib.sha256(p.read_bytes()).hexdigest()
            records.append(dict(origin=origin, source=rel, destination=target, owner=owner,
                                prospective_tracked=tracked, bytes=p.stat().st_size,
                                sha256=digest, action='keep' if origin=='project' and rel==target else 'move'))
    seen = {}
    for r in records:
        key = r['destination'].casefold()
        if key in seen:
            raise ValueError('Destination collision: ' + r['destination'])
        seen[key] = r
        for part in Path(r['destination']).parts:
            if part.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))}:
                raise ValueError('Reserved path component: ' + part)
    (OUT/'inventory.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    with (OUT/'path-map.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=records[0].keys());writer.writeheader();writer.writerows(records)
    for name, args in [('status',['status','--porcelain=v1','--untracked-files=all']),
                       ('head',['rev-parse','HEAD']),('index-files',['ls-files']),
                       ('unstaged',['diff','--binary']),('staged',['diff','--cached','--binary'])]:
        (OUT/f'baseline-{name}.txt').write_bytes(subprocess.check_output(['git',*args],cwd=ROOT))
    (OUT/'baseline-git-index').write_bytes((ROOT/'.git/index').read_bytes())
    with zipfile.ZipFile(OUT/'project-before-migration.zip','w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for r in records:
            if r['origin']=='project' and r['owner']!='generated-dependency-build-cache' and r['owner']!='authentication-state':
                z.write(ROOT/r['source'],r['source'])
    print(json.dumps({'files':len(records),'project':sum(r['origin']=='project' for r in records),
                      'external':sum(r['origin']=='external' for r in records),'moves':sum(r['action']=='move' for r in records),
                      'collisions':0,'protected_engine_files':sum(r['origin']=='project' and r['source'].startswith('engine/') for r in records)}))

if __name__ == '__main__':
    main()
