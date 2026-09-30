"""Apply exact test-owned path repairs after the reviewed physical moves."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[4]
for p in (ROOT/'apps/chart/tests/unit').glob('*.mjs'):
    data=p.read_bytes()
    data=data.replace(b'../../../apps/chart/', b'../../')
    data=data.replace(b'"../../../apps/chart"', b'"../.."')
    if p.name=='faraz-candle-api.test.mjs':
        # Only this fixture's explicitly inventoried sibling state path changes.
        data=data.replace(b'`${workspaceRoot}-Local`', b'path.join(workspaceRoot, "apps", "chart", "state")')
        data=data.replace(b'`${options.workspaceRoot}-Local`', b'path.join(options.workspaceRoot, "apps", "chart", "state")')
        # The workspace cleanup already contains the state; avoid a redundant removal.
        data=data.replace(b'    fs.rmSync(path.join(workspaceRoot, "apps", "chart", "state"), { recursive: true, force: true });\r\n', b'')
    p.write_bytes(data)
p=ROOT/'apps/chart/package.json'
data=p.read_bytes().replace(b'node --test ../../tests/chart/unit/*.test.mjs',b'node --test tests/unit/*.test.mjs')
p.write_bytes(data)
p=ROOT/'engine/tests/verification/verify_order_references.py'
data=p.read_bytes().replace(b'for source in ENGINE.rglob("*.py") if "__pycache__" not in source.parts',
                          b'for source in [ENGINE / "__init__.py", *sorted((ENGINE / "bridge").rglob("*.py")), *sorted((ENGINE / "pipeline").rglob("*.py"))] if "__pycache__" not in source.parts')
p.write_bytes(data)
p=ROOT/'engine/tests/regression/order_regression.py'
data=p.read_bytes()
data=data.replace(b'ROOT.with_name(ROOT.name + "-Local")',b'ROOT / "apps" / "chart" / "state"')
data=data.replace(b'ROOT / "tests" / "engine" / "helpers"',b'ROOT / "engine" / "tests" / "verification"')
data=data.replace(b'for path in sorted(ENGINE.rglob("*.py"))',b'for path in [ENGINE / "__init__.py", *sorted((ENGINE / "bridge").rglob("*.py")), *sorted((ENGINE / "pipeline").rglob("*.py"))]')
data=data.replace(b'*V5.4.13*OrderAB.md',b'*Source_Synchronized.md')
p.write_bytes(data)
p=ROOT/'engine/tests/regression/hpzr2_verify_saved.py'
data=p.read_bytes().replace(b'ROOT.with_name(ROOT.name + "-Local")',b'ROOT / "engineering"')
p.write_bytes(data)
print('Repaired component test imports, package discovery, and production-only verification inventories.')
