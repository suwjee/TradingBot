"""Prepare the isolated baseline oracle from a local checkout at the pinned revision.

This script is for the verifier, NOT a clean-room implementer. It does not
change the engine or import the entire pipeline.
"""
import argparse
import ast
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--repo", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
engine = args.repo / "engine"
out = args.output
out.mkdir(parents=True, exist_ok=True)

def checked(path, expected):
    data = path.read_bytes()
    actual = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
    if actual != expected:
        raise ValueError(f"Baseline blob mismatch: {path}: {actual}")
    return data

for name, sha in {
    "core_utils.py": "38a1053510c5fb114e1b4290de00a2d3b27fc373",
    "direction_policy.py": "f7d047abde0eb884905f86c1d2beeaaec3f6e07a",
    "true_false.py": "d569d16bc493b9eb5da75ed5594c168751856b6f",
}.items():
    (out / name).write_bytes(checked(engine / "pipeline" / name, sha))

def get_definitions(source, names):
    module = ast.parse(source)
    selected = {}
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            selected[node.name] = ast.get_source_segment(source, node)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    selected[target.id] = ast.get_source_segment(source, node)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in names:
            selected[node.target.id] = ast.get_source_segment(source, node)
    if set(selected) != set(names):
        raise ValueError(f"Missing oracle definitions: {set(names)-set(selected)}")
    return "\n\n".join(selected[name] for name in names) + "\n"

bridge = checked(engine / "bridge" / "trading_pipeline.py", "7b28fa7e93c8980c082cb277fb75556959b1abcf").decode("utf-8")
(out / "buckets.py").write_text(
    "from typing import Iterable, Callable\nfrom decimal import Decimal\nfrom core_utils import as_decimal\n\n" +
    get_definitions(bridge, ["_aggregate_candle_buckets", "build_candle_buckets"]), encoding="utf-8")
lifecycle = checked(engine / "pipeline" / "lifecycle_engine.py", "2885dcbd3af108baadde7510ffd7968ad735c57e").decode("utf-8")
(out / "lifecycle_engine.py").write_text(
    "# Isolated priority mapping only.\n" +
    get_definitions(lifecycle, ["SEQUENCE_PRIORITY", "sequence_priority"]), encoding="utf-8")
print("Prepared isolated baseline oracle:", out)
