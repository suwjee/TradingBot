"""Launch the single maintained Reaction + Blue Line + A regression."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INTEGRATED_TEST = ROOT / "indicator" / "Modules" / "1_reaction-detector" / "app" / "test_user_verified_ranges.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location(
        "integrated_reaction_blue_a_test", INTEGRATED_TEST
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import integrated test: {INTEGRATED_TEST}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
