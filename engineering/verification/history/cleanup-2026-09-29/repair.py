from pathlib import Path
import json
import os
import re

ROOT = Path(r'D:\My-Projects\TradingBot')
LOCAL = ROOT.with_name(ROOT.name + '-Local')

def edit(path, callback):
    content = path.read_bytes()
    text = content.decode('utf-8-sig')
    result = callback(text)
    if result != text:
        path.write_bytes(result.encode('utf-8'))

for path in (ROOT / 'tests/chart/unit').glob('*.mjs'):
    edit(path, lambda s: s.replace('../src/', '../../../apps/chart/src/').replace('../server/', '../../../apps/chart/server/').replace('../apps/chart/', '../../../apps/chart/'))
    if path.name == 'indicator-range-input.test.mjs':
        edit(path, lambda s: s.replace('path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")', 'path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "..", "apps", "chart")'))

faraz_test = ROOT / 'tests/chart/unit/faraz-candle-api.test.mjs'
def repair_faraz(s):
    s = s.replace('createFarazCandleApi, findCandleCoverageGaps', 'createFarazCandleApi as createProductionFarazCandleApi, findCandleCoverageGaps')
    anchor = 'async function listenForApi(t, api) {'
    s = s.replace(anchor, 'function createFarazCandleApi(options) {\n  return createProductionFarazCandleApi({ ...options, localStateRoot: `${options.workspaceRoot}-Local` });\n}\n\n' + anchor)
    s = s.replace('path.join(workspaceRoot, "runtime", "cache", "secret")', 'path.join(`${workspaceRoot}-Local`, "secret")')
    s = s.replace('path.join(workspaceRoot, "runtime", "cache", "secret", "faraz-session.dpapi.json")', 'path.join(`${workspaceRoot}-Local`, "secret", "faraz-session.dpapi.json")')
    s = s.replace('path.join(workspaceRoot, "data", "raw")', 'path.join(`${workspaceRoot}-Local`, "data", "raw")')
    s = s.replace('path.join(workspaceRoot, job.savedPath)', 'path.join(`${workspaceRoot}-Local`, job.savedPath)')
    s = s.replace('path.join(workspaceRoot, continued.savedPath)', 'path.join(`${workspaceRoot}-Local`, continued.savedPath)')
    s = s.replace('t.after(() => fs.rmSync(workspaceRoot, { recursive: true, force: true }));', 't.after(() => {\n    fs.rmSync(workspaceRoot, { recursive: true, force: true });\n    fs.rmSync(`${workspaceRoot}-Local`, { recursive: true, force: true });\n  });')
    return s
edit(faraz_test, repair_faraz)

for path in (ROOT / 'tests/engine').rglob('*.py'):
    edit(path, lambda s: s.replace('Path(__file__).resolve().parents[1]', 'Path(__file__).resolve().parents[3]'))
    if path.name == 'order_regression.py':
        edit(path, lambda s: s.replace('RAW_ROOT = ROOT / "data" / "raw"', 'LOCAL_STATE = Path(os.environ.get("TRADINGBOT_LOCAL_STATE_ROOT", ROOT.with_name(ROOT.name + "-Local")))\nRAW_ROOT = LOCAL_STATE / "data" / "raw"').replace('str(ROOT / "tests")', 'str(ROOT / "tests" / "engine" / "helpers")'))
    if path.name == 'hpzr2_verify_saved.py':
        edit(path, lambda s: s.replace('import json', 'import json\nimport os').replace('EVIDENCE = ROOT / "docs" / "hpzr2-regression-2026-09-23"\nRAW = ROOT / "data" / "raw"', 'LOCAL_STATE = Path(os.environ.get("TRADINGBOT_LOCAL_STATE_ROOT", ROOT.with_name(ROOT.name + "-Local")))\nEVIDENCE = LOCAL_STATE / "archive" / "docs" / "hpzr2-regression-2026-09-23"\nRAW = LOCAL_STATE / "data" / "raw"'))

manifest = ROOT / 'apps/chart/package.json'
edit(manifest, lambda s: s.replace('node --test tests/*.test.mjs', 'node --test ../../tests/chart/unit/*.test.mjs'))

mapping = {
    'docs/TradingBot_Technical_Architecture.md': 'docs/architecture/TradingBot_Technical_Architecture.md',
    'docs/TradingBot_UI_UX_Technical_Reference.md': 'docs/architecture/TradingBot_UI_UX_Technical_Reference.md',
    'docs/TradingBot_AI_Operating_Protocol.md': 'docs/development/TradingBot_AI_Operating_Protocol.md',
    'docs/TradingBot_Repository_Baseline.md': 'docs/history/TradingBot_Repository_Baseline.md',
    'docs/TradingBot_Project_Audit.md': 'docs/history/TradingBot_Project_Audit.md',
    'docs/TradingBot_Cleanup_Report.md': 'docs/history/TradingBot_Cleanup_Report.md',
    'docs/TradingBot_Validation_Report.md': 'docs/history/TradingBot_Validation_Report.md',
    'docs/superpowers/specs/2026-09-23-bridge-output-projection-design.md': 'docs/development/specs/Bridge_Output_Projection.md',
    'docs/superpowers/plans/2026-09-23-bridge-output-projection.md': 'docs/development/plans/2026-09-23-bridge-output-projection.md',
    'apps/chart/tests/': 'tests/chart/unit/',
    'scripts/order_regression.py': 'tests/engine/regression/order_regression.py',
    'scripts/compare_order_regressions.py': 'tests/engine/regression/compare_order_regressions.py',
    'scripts/hpzr2_regression.py': 'tests/engine/regression/hpzr2_regression.py',
    'scripts/hpzr2_verify_saved.py': 'tests/engine/regression/hpzr2_verify_saved.py',
}

for path in [ROOT / 'AGENTS.md', *(ROOT / 'docs').rglob('*.md')]:
    def repair_doc(s):
        for old,new in mapping.items():
            s = s.replace(old,new)
            s = s.replace(old.replace('/', '\\'),new.replace('/', '\\'))
        if path.name == 'AGENTS.md':
            s = s.replace('[Bullish Reference](docs/TradingBot_Bullish_Algorithm_Reference.md)', '[Bullish Reference](engine/algorithms/TradingBot_Bullish_Algorithm_Reference_V5.4.19_EX1_Source_Synchronized.md)')
            s = s.replace('[Bearish Reference](docs/TradingBot_Bearish_Algorithm_Reference.md)', '[Bearish Reference](engine/algorithms/TradingBot_Bearish_Algorithm_Reference_V5.4.19_EX1_Source_Synchronized.md)')
            s = re.sub(r'^- \[Graphify.*$', '- Graphify outputs are external local archives; every Graphify execution still requires explicit approval.', s, flags=re.M)
            s = re.sub(r'^- \[Current Graphify Rebuild.*$', '', s, flags=re.M)
            s = s.replace('No nested `AGENTS.md` is currently needed:', 'No nested `AGENTS.md` was found during the 2026-09-29 inventory:')
            s = s.replace('The current verified structural snapshot is `docs/graphify/rebuild-2026-09-23/`; the top-level graph files under `docs/graphify/` mirror it for compatibility.', 'The dated Graphify snapshot is now external archived evidence under the local-state root, `archive/docs/graphify/rebuild-2026-09-23/`. It is not part of the tracked repository.')
            s = s.replace('`data/raw/` | Authoritative candle arrays and metadata sidecars.', '`<local-state-root>/data/raw/` | External authoritative candle arrays and metadata sidecars.')
            s = s.replace('`runtime/cache/` | User drawings, templates, calculation caches, and FARAZ session state; preserve by default.', '`<local-state-root>/cache/`, `<local-state-root>/secret/` | External user drawings, templates, calculation caches, and FARAZ session state; preserve by default.')
            s = s.replace('creates runtime directories, sets', 'creates external state directories, sets')
            s = s.replace('`TRADINGBOT_PYTHON` and `TRADINGBOT_PROJECT_ROOT`', '`TRADINGBOT_PYTHON`, `TRADINGBOT_PROJECT_ROOT`, and `TRADINGBOT_LOCAL_STATE_ROOT`')
            s += '\n## M. Repository Storage Policy\n\nMachine state resolves through `TRADINGBOT_LOCAL_STATE_ROOT`, defaulting to a sibling directory named `<checkout-name>-Local`. The shared application resolver rejects repository-internal roots. RAW, cache, secrets, and temporary state stay external. Tests live under ignored `/tests/`; chart tests run with `npm.cmd test` from `apps/chart`. Dependencies/build output are reproducible and excluded. Historical Graphify and regression output is external archived evidence. Only the two current source-synchronized references under `engine/algorithms/` are current references.\n'
        elif path.parts[-2] == 'history' or 'plans' in path.parts:
            s = '> HISTORICAL SNAPSHOT. Versions, paths, commands, and verification results below describe the recorded run; use the current README and operations documentation for today\'s layout.\n\n' + s
        elif path.parts[-2] == 'architecture':
            s = '> Current layout/storage update: 2026-09-29. Local state now lives outside the checkout; tests are local-only under `/tests/`. The dated audit evidence below remains a historical snapshot. See [repository storage](../operations/Local_State.md) and the [documentation index](../README.md) for current navigation.\n\n' + s
        return s
    edit(path,repair_doc)

print('Repaired chart/Python test paths, storage fixtures, package command, and maintained documentation navigation.')
