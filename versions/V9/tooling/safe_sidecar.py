"""Confine manifest-selected audit files to the trusted trace directory."""
from pathlib import Path

def sidecar_path(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or name in {'.', '..'} or '/' in name or '\\' in name or ':' in name or '\x00' in name:
        raise ValueError('Sidecar must be a plain local filename')
    root = root.resolve(strict=True)
    path = root / name
    if path.is_symlink() or path.resolve(strict=True).parent != root or not path.is_file():
        raise ValueError('Sidecar must be a regular file within the trace directory')
    return path
