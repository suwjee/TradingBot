"""Record final structure, classified changes and reproducible delivery packages."""
from pathlib import Path
from datetime import datetime
import csv
import hashlib
import json
import os
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent.parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode('utf-8').splitlines()

def all_files():
    result = []
    for folder, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d != '.git')
        result.extend(Path(folder) / name for name in sorted(files))
    return sorted(result)

def main():
    integrity = json.loads((OUT / 'integrity-results.json').read_text(encoding='utf-8'))
    assert integrity['status'] == 'PASS'
    baseline = json.loads((OUT / 'inventory.json').read_text(encoding='utf-8'))
    mapped = {row['destination']: row for row in baseline}
    source = sorted(set(git('ls-files', '--cached', '--others', '--exclude-standard')))
    source = [name for name in source if (ROOT / name).is_file()]
    excluded = ('apps/chart/state/', 'apps/chart/tests/', 'engine/tests/',
                'engineering/archive/', 'engineering/verification/', '.git/',
                'apps/chart/node_modules/', 'apps/chart/dist/')
    assert not [name for name in source if name.startswith(excluded)]
    assert not ROOT.with_name(ROOT.name + '-Local').exists()
    secret_patterns = [re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
                       re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}'),
                       re.compile(rb'github_pat_[A-Za-z0-9_]{40,}'),
                       re.compile(rb'AKIA[0-9A-Z]{16}')]
    findings = [name for name in source if any(p.search((ROOT / name).read_bytes()) for p in secret_patterns)]
    assert not findings, f'Credential pattern detected in delivery source: {findings}'
    (OUT / 'source-tree.txt').write_text('\n'.join(['TradingBot/ (source delivery; ignored local state excluded)', *source]) + '\n', encoding='utf-8')
    (OUT / 'final-git-status.txt').write_text('\n'.join(git('status', '--short')) + '\n', encoding='utf-8')
    with (OUT / 'final-tracked.diff').open('wb') as handle:
        subprocess.run(['git', 'diff', '--no-ext-diff'], cwd=ROOT, stdout=handle, check=True)
    changed = set(integrity['changed_files'])
    moved_patterns = sorted({row['source'].replace('\\', '/') for row in baseline if row['action'] == 'move'} |
                            {Path(row['source']).name for row in baseline if row['action'] == 'move' and row['source'].startswith('docs/') and not row['source'].startswith('docs/graphify/')} |
                            {'TradingBot-Local', 'tests/chart/', 'tests/engine/'})
    pattern_prefixes = {pattern.split('/')[0] for pattern in moved_patterns}
    path_audit = []
    skipped = {}
    for path in all_files():
        name = path.relative_to(ROOT).as_posix()
        if '/state/' in name or '/node_modules/' in name or '/dist/' in name or path.suffix not in {'.md', '.txt', '.py', '.ps1', '.bat', '.js', '.mjs', '.json', '.csv'}:
            skipped[name] = 'Private state, generated dependencies/build, or non-text preserved evidence.'
            continue
        content = path.read_text(encoding='utf-8-sig', errors='replace').replace('\\', '/')
        if not any(prefix in content for prefix in pattern_prefixes):
            continue
        hits = [pattern for pattern in moved_patterns if pattern in content]
        if not hits:
            continue
        if name.startswith(('engineering/archive/', 'engineering/verification/')):
            classification = 'Immutable historical evidence or migration/recovery record; not active runtime dependencies.'
        elif name.startswith('engineering/docs/architecture/'):
            classification = 'Dated architecture body; leading note explicitly supersedes every old path.'
        elif name.startswith('engineering/docs/'):
            classification = 'Migration history or explicitly superseded historical protocol example.'
        elif '/tests/' in name:
            classification = 'Test assertion or historical proof context; active imports and defaults verified separately.'
        else:
            classification = 'Review current executable context; path may refer to the new engineering/docs owner.'
        path_audit.append(dict(path=name, classification=classification, matching_old_paths=hits))
    (OUT / 'old-path-audit.json').write_text(json.dumps(dict(status='CLASSIFIED',
        searched_old_patterns=len(moved_patterns), matching_files=path_audit, skipped_files=skipped,
        limitation='Private state is inventoried by metadata; generated dependencies and binary historical bundles are preserved rather than interpreted.'), indent=2) + '\n', encoding='utf-8')
    with (OUT / 'final-diff-classification.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['old_path', 'new_path', 'classification', 'reason'])
        writer.writeheader()
        for row in baseline:
            name = row['destination']
            if row['action'] != 'move' and name not in changed:
                continue
            kind = 'move'
            reason = 'Colocate existing content with its architectural owner; exact bytes retained.'
            if name in changed:
                if name.startswith('engineering/docs/') or name in {'README.md', 'AGENTS.md'}:
                    kind = 'documentation-path repair'
                    reason = 'Repair current navigation/storage guidance; label immutable dated bodies as historical.'
                elif '/tests/' in name:
                    kind = 'path/import repair'
                    reason = 'Repair local test discovery, imports, fixture containment or production-only inventory.'
                elif name == 'scripts/start.ps1':
                    kind = 'compatibility adjustment'
                    reason = 'Keep the public launcher path and use the shared internal-state resolver.'
                else:
                    kind = 'configuration-path repair'
                    reason = 'Internal state ownership, test command, ignored local content or Vite serving/watcher boundaries.'
            writer.writerow(dict(old_path=row['source'], new_path=name, classification=kind, reason=reason))
        for name in source:
            if name not in mapped:
                writer.writerow(dict(old_path='', new_path=name, classification='documentation-path repair',
                                     reason='New maintained navigation or migration evidence.'))
        writer.writerow(dict(old_path='', new_path='apps/chart/tests/unit/vite-state-policy.test.mjs',
                             classification='configuration-path repair', reason='Real exported Vite configuration regression tests.'))
    tests = sorted(path for owner in ('apps/chart/tests', 'engine/tests')
                   for path in (ROOT / owner).rglob('*')
                   if path.is_file() and '__pycache__' not in path.parts)
    tests = [path for path in tests if path.suffix in {'.py', '.mjs'}]
    package_path = OUT / 'TradingBot-single-root-source.zip'
    test_path = OUT / 'TradingBot-local-tests.zip'
    readme = OUT / 'readme.txt'
    assert readme.is_file(), 'Finalize delivery readme before packaging.'
    base_readme = readme.read_text(encoding='utf-8').split('\nChanged/moved executable or maintained files\n', 1)[0]
    lines = ['\nChanged/moved executable or maintained files\n',
             'Old path | New path | Version | Final modification datetime\n']
    version = json.loads((ROOT / 'apps/chart/package.json').read_text())['version']
    for name in sorted(changed | {name for name in source if name not in mapped} |
                       {'apps/chart/tests/unit/vite-state-policy.test.mjs'}):
        path = ROOT / name
        row = mapped.get(name, {})
        stamp = datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec='seconds')
        lines.append(f"{row.get('source', '(new)')} | {name} | {version if name == 'apps/chart/package.json' else 'not separately versioned'} | {stamp}\n")
    readme.write_text(base_readme + ''.join(lines), encoding='utf-8')
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in source:
            archive.write(ROOT / name, name)
        archive.write(readme, 'readme.txt')
    with zipfile.ZipFile(test_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in tests:
            archive.write(path, path.relative_to(ROOT).as_posix())
        archive.writestr('readme.txt', 'Restore paths under TradingBot. Chart: npm.cmd test from apps/chart. Engine: python -B -m pytest -q -p no:cacheprovider -p no:benchmark engine/tests/unit from root. Production source is in the separate source package.\n')
    for package, expected in ((package_path, {name: ROOT / name for name in source}),
                              (test_path, {path.relative_to(ROOT).as_posix(): path for path in tests})):
        with zipfile.ZipFile(package) as archive:
            assert set(archive.namelist()) == set(expected) | {'readme.txt'}
            assert archive.testzip() is None
            for name, path in expected.items():
                assert archive.read(name) == path.read_bytes(), f'Package bytes differ: {name}'
    recorded = datetime.now().astimezone().isoformat(timespec='seconds')
    release = dict(status='PASS', recorded_at=recorded, source_files=len(source), local_test_files=len(tests),
                   secret_pattern_findings=findings, excluded_owner_subtrees=list(excluded),
                   packages={path.name: dict(sha256=digest(path), bytes=path.stat().st_size)
                             for path in (package_path, test_path)},
                   package_entries_equal_current_source=True,
                   node=subprocess.check_output(['node', '--version']).decode().strip(),
                   python=subprocess.check_output(['python', '--version']).decode().strip(),
                   branch=git('branch', '--show-current')[0], head=git('rev-parse', 'HEAD')[0],
                   chart_package_version=json.loads((ROOT / 'apps/chart/package.json').read_text())['version'],
                   index_unchanged=(ROOT / '.git/index').read_bytes() == (OUT / 'baseline-git-index').read_bytes())
    assert release['index_unchanged']
    (OUT / 'delivery-manifest.json').write_text(json.dumps(release, indent=2) + '\n', encoding='utf-8')
    for name in ('physical-tree.txt', 'final-physical-inventory.csv'):
        (OUT / name).touch(exist_ok=True)
    files = all_files()
    directory_paths = []
    for folder, dirs, _ in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d != '.git')
        directory_paths.extend((Path(folder) / name).relative_to(ROOT).as_posix() + '/' for name in dirs)
    assert {path.name for path in ROOT.iterdir() if path.is_dir()} == {'.git', 'apps', 'engine', 'engineering', 'scripts'}
    (OUT / 'physical-tree.txt').write_text('\n'.join([
        f'TradingBot/ complete physical file inventory at {recorded}; .git metadata excluded',
        '.git/ (existing version-control metadata; preserved and separately verified)',
        *sorted([*directory_paths, *(path.relative_to(ROOT).as_posix() for path in files)]),
    ]) + '\n', encoding='utf-8')
    with (OUT / 'final-physical-inventory.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(['path', 'bytes', 'modified_at'])
        for path in all_files():
            stat = path.stat()
            writer.writerow([path.relative_to(ROOT).as_posix(), stat.st_size,
                             datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec='seconds')])
    print(json.dumps(release, indent=2))

if __name__ == '__main__':
    main()
