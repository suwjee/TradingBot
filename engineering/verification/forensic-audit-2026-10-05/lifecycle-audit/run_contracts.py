"""Preload archive-authoritative source before running pre-existing unit contracts."""
import json
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT / "package" / "pipeline"))
import core_utils, direction_policy, reaction_engine, order_audit_engine, lifecycle_engine, s_zone_detector, e_zone_detector
import pytest
mods=(core_utils,direction_policy,reaction_engine,order_audit_engine,lifecycle_engine,s_zone_detector,e_zone_detector)
assert all(str(ROOT / "package") in x.__file__ for x in mods)
print(json.dumps({x.__name__:x.__file__ for x in mods},indent=2))
project=ROOT.parents[2]
sys.exit(pytest.main(["-q","-p","no:cacheprovider",
    str(project / "engine" / "tests" / "unit" / "test_stopall_dominance.py"),
    str(project / "engine" / "tests" / "unit" / "test_order_audit_lifecycle_contracts.py")]))
