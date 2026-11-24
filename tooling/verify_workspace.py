"""Fail closed if a project source tree, raw data or an unapproved root is tracked."""
import hashlib
import json
import subprocess
from pathlib import Path, PurePosixPath


def verify(root: Path) -> None:
    files = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z']).decode('utf-8').split('\0')
    roots = {'.github', '.gitignore', '.sonarcloud.properties', 'sonar-project.properties', 'AGENTS.md', 'README.md', 'STATE.json', 'archive', 'baselines', 'journal', 'prompts', 'protocols', 'tooling', 'versions'}
    for name in filter(None, files):
        path = PurePosixPath(name)
        if path.parts[0] not in roots or any(part in ('apps', 'engine', 'GPT_bot', 'node_modules', '.scratch', '__pycache__') for part in path.parts):
            raise ValueError(f'Forbidden tracked path: {name}')
        if path.suffix == '.py' and not (path.parts[0] == 'tooling' or (len(path.parts) >= 4 and path.parts[0] == 'versions' and path.parts[2] == 'tooling')):
            raise ValueError(f'Python outside refactor tooling: {name}')
        if path.suffix in ('.zip', '.gz', '.exe', '.dll', '.pyc') or path.name.startswith('RAW '):
            raise ValueError(f'Unapproved raw/binary artifact: {name}')
    state = json.loads((root / 'STATE.json').read_text())
    if state['branch'] != 'refactor':
        raise ValueError('Branch policy mismatch')
    baseline = json.loads((root / 'baselines/manifest.json').read_text())
    patch = root / 'baselines/V8.1.patch'
    if hashlib.sha256(patch.read_bytes()).hexdigest() != baseline['v81_patch_sha256']:
        raise ValueError('V8.1 patch hash mismatch')
    for path in (root / 'versions').rglob('*.json'):
        json.loads(path.read_text(encoding='utf-8'))
    print('Standalone workspace, tracked paths, phase JSON and frozen patch digest PASS')


if __name__ == '__main__':
    verify(Path(__file__).resolve().parents[1])
