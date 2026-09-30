"""Verify final deliverables and refresh metadata after documentation review."""
from pathlib import Path
from datetime import datetime
import csv
import hashlib
import json
import os
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent.parent
manifest = json.loads((OUT / 'delivery-manifest.json').read_text(encoding='utf-8'))
test_package = OUT / 'TradingBot-local-tests.zip'
tests = sorted(path for owner in ('apps/chart/tests', 'engine/tests')
               for path in (ROOT / owner).rglob('*')
               if path.is_file() and path.suffix in {'.mjs', '.py'} and '__pycache__' not in path.parts)
with zipfile.ZipFile(test_package, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in tests:
        archive.write(path, path.relative_to(ROOT).as_posix())
    archive.writestr('readme.txt', 'Restore paths under TradingBot. Chart: npm.cmd test from apps/chart. Engine: python -B -m pytest -q -p no:cacheprovider -p no:benchmark engine/tests/unit from root. Production source is in the separate source package.\n')
results = {}
for package_name in manifest['packages']:
    path = OUT / package_name
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        entries = [name for name in archive.namelist() if name != 'readme.txt']
        for name in entries:
            assert archive.read(name) == (ROOT / name).read_bytes(), f'Stale ZIP entry: {name}'
        if 'source' in package_name:
            assert archive.read('readme.txt') == (OUT / 'readme.txt').read_bytes()
            assert b'vite-state-policy.test.mjs' in archive.read('readme.txt')
            source = (OUT / 'source-tree.txt').read_text().splitlines()[1:]
            assert set(entries) == set(source)
        else:
            assert b'-p no:benchmark' in archive.read('readme.txt')
    manifest['packages'][package_name] = dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size)
    results[package_name] = dict(status='PASS', equal_current_entries=len(entries), mismatched_entries=0)
assert (ROOT / '.git/index').read_bytes() == (OUT / 'baseline-git-index').read_bytes()
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT) == (OUT / 'baseline-head.txt').read_bytes()
assert not ROOT.with_name(ROOT.name + '-Local').exists()
manifest['recorded_at'] = datetime.now().astimezone().isoformat(timespec='seconds')
manifest['package_entries_equal_current_source'] = True
(OUT / 'delivery-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
(OUT / 'package-verification-results.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
files = []
directories = []
for folder, dirs, names in os.walk(ROOT):
    dirs[:] = sorted(name for name in dirs if name != '.git')
    directories.extend((Path(folder) / name).relative_to(ROOT).as_posix() + '/' for name in dirs)
    files.extend(Path(folder) / name for name in names)
files.sort()
(OUT / 'physical-tree.txt').write_text('\n'.join([
    f'TradingBot/ complete physical file inventory at {manifest["recorded_at"]}; .git metadata excluded',
    '.git/ (existing version-control metadata; preserved and separately verified)',
    *sorted([*directories, *(path.relative_to(ROOT).as_posix() for path in files)]),
]) + '\n', encoding='utf-8')
with (OUT / 'final-physical-inventory.csv').open('w', newline='', encoding='utf-8') as handle:
    writer = csv.writer(handle)
    writer.writerow(['path', 'bytes', 'modified_at'])
    for path in files:
        stat = path.stat()
        writer.writerow([path.relative_to(ROOT).as_posix(), stat.st_size,
                         datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec='seconds')])
print(json.dumps(dict(status='PASS', package_entries=results, physical_files=len(files), directories=len(directories),
                     head_unchanged=True, index_unchanged=True, external_root_absent=True), indent=2))
