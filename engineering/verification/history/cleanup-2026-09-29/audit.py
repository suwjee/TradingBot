import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile
from collections import Counter

ROOT = Path(r'D:\My-Projects\TradingBot')
AUDIT = Path(__file__).resolve().parent

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=False)

def classify(rel):
    parts = rel.split('/')
    name = parts[-1]
    if '.git' in parts: return 'GIT_INTERNAL'
    if 'node_modules' in parts: return 'DEPENDENCY_INSTALLATION'
    if '__pycache__' in parts or name.endswith(('.pyc', '.pyo')): return 'CACHE'
    if any(p in parts for p in ['.pytest_cache', '.benchmarks', '.vite', '.vite-temp', '.cache']): return 'CACHE'
    if rel.startswith('data/'): return 'MARKET_DATA'
    if rel.startswith('runtime/') and ('secret' in parts): return 'SECRET'
    if rel.startswith('runtime/'): return 'RUNTIME_STATE'
    if rel.startswith('tmp/'): return 'TEMPORARY'
    if rel.startswith('graphify-out/') or rel.startswith('docs/graphify/'): return 'GRAPHIFY_OUTPUT'
    if 'dist' in parts: return 'GENERATED_BUILD'
    if rel.startswith('tests/') or '/tests/' in rel or name.startswith(('test_', 'verify_')): return 'TEST'
    if rel.startswith('engine/algorithms/'): return 'ALGORITHM_REFERENCE'
    if rel.startswith('engine/'): return 'PRODUCTION_SOURCE'
    if rel.startswith('docs/hpzr2-') or rel.startswith('docs/order-architecture-'): return 'VALIDATION_OUTPUT'
    if rel.startswith('docs/'): return 'DOCUMENTATION'
    if name in ['AGENTS.md', 'AGEN.md'] or 'Operating_Protocol' in name: return 'PROJECT_INSTRUCTION'
    if rel.startswith('scripts/') or '/scripts/' in rel: return 'OPERATIONAL_SCRIPT'
    if rel.startswith('apps/chart/src/') or rel.startswith('apps/chart/server/') or name.endswith('.html'): return 'APPLICATION_SOURCE'
    if name.endswith(('.json', '.js', '.md')) or name.startswith('.'): return 'PROJECT_CONFIGURATION'
    return 'UNKNOWN'

def baseline():
    AUDIT.mkdir(parents=True, exist_ok=True)
    commands = {
        'root': ['rev-parse','--show-toplevel'], 'git-dir': ['rev-parse','--git-dir'],
        'branch': ['branch','--show-current'], 'head': ['rev-parse','HEAD'],
        'status-short': ['status','--short'], 'status-branch': ['status','--branch'],
        'tracked': ['ls-files'], 'untracked': ['ls-files','--others','--exclude-standard'],
        'ignored': ['ls-files','--others','-i','--exclude-standard'],
        'diff-stat': ['diff','--stat'], 'diff': ['diff','--binary'],
        'diff-cached': ['diff','--cached','--binary'], 'submodules': ['submodule','status'],
        'branches': ['branch','-avv'], 'remotes': ['remote','-v'],
        'tags': ['tag','--list'], 'worktrees': ['worktree','list','--porcelain'],
        'topology': ['log','--all','--oneline','--decorate','--graph','-50'],
        'secret-history': ['log','--all','--format=%H','--','runtime/cache/secret','runtime/secret','*.dpapi.json'],
    }
    exits = {}
    for name,args in commands.items():
        result = git(*args)
        (AUDIT / f'baseline-{name}.txt').write_bytes(result.stdout + result.stderr)
        exits[name] = result.returncode
    shutil.copy2(ROOT / '.git/index', AUDIT / 'baseline-index')
    tracked = set(git('ls-files','-z').stdout.decode().split('\0'))
    rows, directories, nested, protected = [], [], [], {}
    for current, dirs, files in os.walk(ROOT):
        current_path = Path(current)
        rel_dir = current_path.relative_to(ROOT).as_posix()
        directories.append(rel_dir)
        if '.git' in dirs:
            nested.append((current_path / '.git').relative_to(ROOT).as_posix())
            dirs.remove('.git')
        for name in files:
            path = current_path / name
            rel = path.relative_to(ROOT).as_posix()
            if name in ['.git','.gitmodules']: nested.append(rel)
            category = classify(rel)
            hashed = category not in ['DEPENDENCY_INSTALLATION', 'CACHE', 'GENERATED_BUILD', 'GRAPHIFY_OUTPUT', 'SECRET']
            sha = digest(path) if hashed else ''
            rows.append({'path':rel,'classification':category,'size':path.stat().st_size,'tracked_before':rel in tracked,'sha256_before':sha})
            if rel.startswith('engine/') and category != 'CACHE': protected[rel] = sha
    (AUDIT / 'baseline-inventory.json').write_text(json.dumps(rows,indent=2), encoding='utf-8')
    (AUDIT / 'baseline-directories.json').write_text(json.dumps(directories,indent=2), encoding='utf-8')
    (AUDIT / 'protected-engine-hashes.json').write_text(json.dumps(protected,indent=2), encoding='utf-8')
    (AUDIT / 'baseline-topology.json').write_text(json.dumps({'markers':nested,'command_exits':exits},indent=2), encoding='utf-8')
    with zipfile.ZipFile(AUDIT / 'pre-cleanup-project.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for row in rows:
            if row['classification'] in ['PRODUCTION_SOURCE','ALGORITHM_REFERENCE','APPLICATION_SOURCE','PROJECT_CONFIGURATION','PROJECT_INSTRUCTION','DOCUMENTATION','OPERATIONAL_SCRIPT','TEST','UNKNOWN']:
                archive.write(ROOT / row['path'],row['path'])
    print(json.dumps({'files':len(rows),'directories':len(directories),'bytes':sum(r['size'] for r in rows),'classifications':dict(Counter(r['classification'] for r in rows)),'git_markers':nested,'protected_engine_files':len(protected),'command_exits':exits,'baseline':str(AUDIT)}))

if __name__ == '__main__': baseline()
