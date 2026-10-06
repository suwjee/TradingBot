"""Read-only snapshot and safe extraction of the explicitly authoritative package."""
from pathlib import Path
import ast, hashlib, json, os, re, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    package = ROOT / 'engine/engine.zip'
    target = OUT / 'package'
    entries = []
    with zipfile.ZipFile(package) as z:
        for info in z.infolist():
            destination = (target / info.filename).resolve()
            if not destination.is_relative_to(target.resolve()):
                raise ValueError(info.filename)
            entries.append({'path': info.filename, 'size': info.file_size,
                            'zip_datetime': info.date_time, 'directory': info.is_dir()})
        z.extractall(target)
    save('package-inventory.json', {'sha256': digest(package), 'entries': entries})
    files = []
    for base, dirs, names in os.walk(ROOT):
        # Inventory is complete, including dependency/cache paths; .git internals are metadata.
        if Path(base) == ROOT:
            dirs[:] = [d for d in dirs if d != '.git']
        for name in names:
            path = Path(base) / name
            info = path.stat()
            files.append({'path': str(path.relative_to(ROOT)), 'size': info.st_size,
                          'mtime_ns': info.st_mtime_ns})
    save('project-file-inventory.json', files)
    modules = []
    snapshots = {}
    for path in sorted(target.rglob('*.py')):
        relative = path.relative_to(target)
        text = path.read_text(encoding='utf-8-sig')
        tree = ast.parse(text)
        constants = {}
        imports = []
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                functions.append({'name': node.name, 'start': node.lineno, 'end': node.end_lineno,
                                  'kind': type(node).__name__})
            elif isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or '')
            elif isinstance(node, ast.Assign):
                for item in node.targets:
                    if isinstance(item, ast.Name) and ('VERSION' in item.id or 'MODIFIED' in item.id):
                        try: constants[item.id] = ast.literal_eval(node.value)
                        except (ValueError, TypeError): pass
        live = ROOT / 'engine' / relative
        modules.append({'path': str(relative), 'hash': digest(path), 'lines': len(text.splitlines()),
                        'metadata': constants, 'imports': sorted(set(imports)), 'definitions': functions,
                        'live_exists': live.exists(),
                        'live_hash': digest(live) if live.exists() else None,
                        'live_matches_package': live.exists() and digest(live) == digest(path)})
    for path in (ROOT / 'engine').rglob('*'):
        if path.is_file(): snapshots[str(path.relative_to(ROOT))] = digest(path)
    for path in (ROOT / 'apps/chart/state/data/RAW').rglob('*.json'):
        snapshots[str(path.relative_to(ROOT))] = digest(path)
    save('protected-pre-hashes.json', snapshots)
    save('source-map.json', modules)
    save('git-before.json', {'head': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                             'status': subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT,text=True)})
    refs = []
    for path in sorted((target / 'algorithms').glob('*.md')):
        content = path.read_text(encoding='utf-8-sig')
        # Full specification prose retained separately; embedded source remains in full references.
        start = re.search(r'^## 16[. \u2014-]', content, re.M)
        prose = content[:start.start()] if start else content
        (OUT / (('bearish' if 'Bearish' in path.name else 'bullish') + '-rules.md')).write_text(prose,encoding='utf-8')
        refs.append({'path': str(path.relative_to(target)), 'hash':digest(path),
                     'lines':len(content.splitlines()), 'prose_lines':len(prose.splitlines())})
    save('reference-inventory.json',refs)
    print(json.dumps({'package_files':sum(not e['directory'] for e in entries),
                      'project_files':len(files), 'modules':len(modules),
                      'mismatches':[m['path'] for m in modules if not m['live_matches_package']],
                      'references':refs},indent=2))

if __name__ == '__main__': main()
