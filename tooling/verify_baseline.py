"""Check the exact frozen source closure without using branch HEAD as an oracle."""
import argparse
import hashlib
import json
from pathlib import Path


def verify(engine: Path, expected: dict[str, str]) -> None:
    actual = {
        file.relative_to(engine).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
        for package in ('pipeline', 'bridge')
        for file in (engine / package).rglob('*.py')
    }
    if actual != expected:
        raise ValueError('Frozen source closure or SHA256 mismatch')
    print(f'{len(actual)} frozen source SHA256 checks PASS')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--variant', choices=('original', 'v81'), required=True)
    args = parser.parse_args()
    verify(args.engine, json.loads(args.manifest.read_text())['source_sha256'][args.variant])


if __name__ == '__main__':
    main()
