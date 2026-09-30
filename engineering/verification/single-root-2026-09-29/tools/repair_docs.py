"""Repair current navigation and storage guidance without rewriting historical evidence."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
def write(rel, text):
    p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')

write('README.md', '''# TradingBot

TradingBot is a Windows candlestick workstation. The chart application acquires and displays candles, drawings, indicators and review tables. Python under `engine/` owns trading calculations; the browser renders serialized results.

## Project ownership

| Owner | Responsibility |
| --- | --- |
| `apps/chart/` | Browser application, local HTTP/SSE server, application state and chart tests |
| `engine/` | Calculation bridge, stage owners, current exact-source references and local Engine verification |
| `engineering/` | Maintained documentation, historical archives and local verification evidence |

The root `scripts/` directory preserves the public Windows startup paths used by existing shortcuts and the VMware shared checkout. Root Git/editor files, `AGENTS.md` and this README stay at their tool discovery boundaries.

**Every project-owned file stays inside this TradingBot directory.** RAW and sidecars use `apps/chart/state/data/raw/`, persistent drawings/calculations/templates use `apps/chart/state/cache/`, FARAZ authentication uses `apps/chart/state/secret/`, and temporary files use `apps/chart/state/tmp/`. State, component tests, archives, verification output, dependencies and build output remain Git-ignored. See [local storage](engineering/docs/operations/local-state.md).

`TRADINGBOT_LOCAL_STATE_ROOT` is optional. Its default is `apps/chart/state`; a configured value must resolve to that directory or a descendant. External roots and source directories are rejected. Vite denies direct static access to state; the established `/api` resources remain available.

## Install and start

Use Node.js `20.19+` (Node.js 22 requires `22.12+`) and Python `3.12+`. Python runtime dependencies are `orjson` and `tzdata`.

```powershell
Set-Location 'D:\\My-Projects\\TradingBot'
.\\scripts\\launch.bat
```

The launcher checks runtimes and installs missing dependencies before starting Vite. For manual development:

```powershell
python -m pip install orjson tzdata
Set-Location apps/chart
npm.cmd ci
npm.cmd run dev -- --host 127.0.0.1 --configLoader native
```

Build with `npm.cmd run build` from `apps/chart`. These commands keep generated output inside the project.

## Local verification and navigation

Tests are intentionally local-only under `apps/chart/tests/` and `engine/tests/`; a fresh GitHub clone requires the local test bundle. Run `npm.cmd test` from `apps/chart` and `python -B -m pytest -q -p no:cacheprovider -p no:benchmark engine/tests/unit` from the root. See [local verification](engineering/docs/development/local-tests.md).

Read [AGENTS.md](AGENTS.md) and the [operating protocol](engineering/docs/ai/operating-protocol.md) before engineering work. Trading semantics require the Intelligence Plugin and canonical Knowledge Vault. The [engineering document index](engineering/docs/README.md) and [single-root migration report](engineering/docs/verification/single-root-migration.md) describe current navigation and the dated migration evidence.
''')
write('engineering/docs/README.md', '''# Engineering documentation

This directory owns maintained project guidance. Current production paths remain under `apps/chart/` and `engine/`; all project-owned local content remains inside the checkout.

| Responsibility | Maintained document |
| --- | --- |
| AI operating process | [Operating protocol](ai/operating-protocol.md) |
| Architecture | [Technical architecture](architecture/technical-architecture.md), [UI/UX reference](architecture/ui-ux-reference.md) |
| Source/reference engineering | [Standalone references](development/standalone-reference-specification.md), [Zero-difference refactor](development/zero-difference-refactor.md) |
| Local verification | [Local tests](development/local-tests.md), [Repository integrity](verification/repository-integrity.md) |
| Operations | [Local storage](operations/local-state.md) |
| Engineering review | [Audit workflow](verification/engineering-audit-workflow.md) |
| Migration evidence | [Single-root migration](verification/single-root-migration.md) |

Architecture audit bodies retain their original dated evidence; their location notes identify the current layout. Historical Graphify, regression and source-recovery artifacts live in ignored `engineering/archive/`. Local command logs, manifests and recovery snapshots live in ignored `engineering/verification/`.

The only current directional references are the two source-synchronized documents in `engine/algorithms/`. Semantic authority follows root AGENTS and Plugin/Vault retrieval; historical archived documents are supporting evidence only.
''')
write('engineering/docs/operations/local-state.md', '''# Project-local workstation state

All TradingBot-owned files stay inside the existing project root. The chart and FARAZ servers share `apps/chart/server/local-state-paths.js`; the Windows launcher invokes this same resolver after validating Node.js.

`TRADINGBOT_LOCAL_STATE_ROOT` defaults to `<project>/apps/chart/state`. Absolute and project-relative overrides are accepted only within this dedicated subtree. The resolver rejects external paths, source paths and junctions escaping the subtree.

```powershell
# Default state: no override is needed.
.\\scripts\\launch.bat

# Optional profile inside the same project.
$env:TRADINGBOT_LOCAL_STATE_ROOT = 'apps/chart/state/profile'
.\\scripts\\launch.bat
```

| Path below the state root | Owner and contents |
| --- | --- |
| `data/raw/` | Market candle arrays and metadata sidecars, preserving resource IDs and filenames |
| `cache/drawings/` | Persistent user drawings |
| `cache/indicator-calculations/`, `cache/indicator-templates/` | Serialized calculations and templates |
| `secret/` | FARAZ authentication; Git-ignored and never included in reports or delivery packages |
| `tmp/faraz-candle-exports/` | Temporary acquisition and export files on the same volume as RAW |

Vite denies direct static access to state, local tests and engineering archives/verification through both normal paths and `/@fs/`. State changes are excluded from the development watcher. Existing `/api` persistence and RAW response contracts remain active.

The 2026-09-29 migration moved the former sibling directory's data, caches and authentication into state without rewriting their contents. Historical archives moved to `engineering/archive/`; previous cleanup proof moved to `engineering/verification/history/cleanup-2026-09-29/`. The former `TradingBot-Local` directory was removed only after becoming empty. Root `scripts/` stays as a compatibility boundary for existing Windows and VMware startup commands.

RAW inventory APIs may regenerate metadata sidecars during ordinary use. That runtime behavior is distinct from the byte-preserving file migration. User-requested export destinations remain user-selected external deliverables, rather than the application's persistent state location.
''')
write('engineering/docs/development/local-tests.md', '''# Component-local verification

All test-only code is local and Git-ignored. A fresh clone needs the local test bundle before running these commands.

| Path | Responsibility |
| --- | --- |
| `apps/chart/tests/unit/` | Chart, server, storage and filesystem access contracts |
| `engine/tests/unit/` | Order/lifecycle contracts |
| `engine/tests/verification/` | Exact source-reference reconstruction and RAW provenance checks |
| `engine/tests/regression/` | Selected-RAW runners and saved-result comparison |
| `engine/tests/benchmarks/` | Synthetic benchmark generation and execution |

```powershell
# From apps/chart
npm.cmd ci
npm.cmd test
npm.cmd run build

# From the repository root
python -B -m pytest -q -p no:cacheprovider -p no:benchmark engine/tests/unit
python -B engine/tests/verification/verify_order_references.py
python -B engine/tests/regression/order_regression.py --help
```

Current selected-RAW defaults use `apps/chart/state/data/raw/`; optional state overrides must remain inside the dedicated state subtree. Give runners an explicit output directory under `engineering/verification/`. Production-source inventories include only the root Engine package marker, bridge and pipeline; component tests are not production source or embedded-reference inventory.

HPZR2 tools preserve historical snapshot expectations and archived evidence. Their dated assertions are not current complete Engine proof. The regression comparer intentionally checks absolute RAW paths; comparisons across a relocation require an explicit reviewed input mapping while retaining all RAW hashes/rows/ranges/configuration checks.

Algorithm correctness, source regression, directional parity and independent real-data validation require separate scoped evidence. Storage/AST/import checks establish structural integrity. Full market regression is not required solely for a storage-only migration with byte-identical Engine and RAW; any Engine or chronological behavior change uses the operating protocol's full applicable gate.
''')
write('engineering/docs/verification/repository-integrity.md', '''# Repository integrity verification

Protect all current calculation source, Engine styles and the two current exact-source references against unintended byte changes. Move RAW, sidecars, persistent caches and archived evidence without rewriting them. Preserve the initial Git index, dirty state, recursive inventory and recovery snapshot under ignored `engineering/verification/` inside the project.

Run fresh chart/Python tests, build, syntax checks, normal dynamic bridge loading and exact embedded-source reconstruction for both references. Check actual HTTP RAW loading and both static and `/@fs/` denial of private state. Verify the launcher invokes the same dedicated state resolver as the server. Review complete path maps, all current imports/links and the final physical tree.

All project-owned files stay inside the checkout. Git excludes app state, component tests, engineering archives/verification output, dependencies and generated builds. Ignore status and physical containment are separate checks. Do not stage credentials, RAW or saved state merely because they are now physically inside the project.

Current source/reference bytes and complete stable serialized outputs are compared independently. These checks establish structural equivalence, not independent trading correctness or resolution of existing Reference narrative discrepancies. No trading-source or algorithm changes are authorized by storage reorganization. A new full-all-market RAW regression is not required solely for storage/layout migration with unchanged calculation and input bytes; selected complete RAW before/after comparisons may provide additional bounded runtime evidence.

Migration reports classify remaining old paths as historical evidence, reconstruction contracts, migration history or compatibility commands. Archived tools retain old coordinates and are not active runnable tools. Re-run relevant verification after later changes; old reports do not establish a current PASS.
''')

for rel in ['engineering/docs/architecture/technical-architecture.md','engineering/docs/architecture/ui-ux-reference.md']:
    p=ROOT/rel;data=p.read_bytes();first,rest=data.split(b'\n',1)
    note=('> Current layout/storage update: 2026-09-29. State is inside `apps/chart/state/`; component tests are under `apps/chart/tests/` and `engine/tests/`. The entire dated audit body below, including old paths and commands, is historical evidence. See [current storage](../operations/local-state.md) and [current document index](../README.md).\n').encode()
    p.write_bytes(note+rest)

p=ROOT/'engineering/docs/verification/engineering-audit-workflow.md';data=p.read_bytes()
data=data.replace(b'/docs/TradingBot_Technical_Architecture.md',b'/engineering/docs/architecture/technical-architecture.md')
data=data.replace(b'/docs/TradingBot_UI_UX_Technical_Reference.md',b'/engineering/docs/architecture/ui-ux-reference.md')
p.write_bytes(data)

note=('> Current precedence/location note (2026-09-29): explicit user instruction and root AGENTS govern this document. Trading semantics require Plugin/Vault retrieval before source interpretation. For this structural task, the live working tree is authoritative; package/bootstrap and authority examples below are subordinate. Production Engine paths and exact references remain unchanged. Component tests and state use the current engineering document index.\n\n').encode()
for rel in ['engineering/docs/ai/operating-protocol.md','engineering/docs/development/zero-difference-refactor.md','engineering/docs/development/standalone-reference-specification.md']:
    p=ROOT/rel;p.write_bytes(note+p.read_bytes())
p=ROOT/'engineering/docs/development/zero-difference-refactor.md';data=p.read_bytes().replace(b'TradingBot_AI_Operating_Protocol.md',b'engineering/docs/ai/operating-protocol.md');p.write_bytes(data)

p=ROOT/'AGENTS.md';s=p.read_text(encoding='utf-8-sig')
s=s.replace('`tests/chart/unit/`','`apps/chart/tests/unit/`').replace('`tests/engine/unit/`','`engine/tests/unit/`')
s=s.replace('pytest -q -p no:cacheprovider tests/engine/unit','pytest -q -p no:cacheprovider -p no:benchmark engine/tests/unit')
s=s.replace('29 local-only Node test files; cleanup verification ran 159 tests.','29 local-only Node test files; the 2026-09-29 baseline had 159 tests; internal-state coverage adds three tests.')
s=s.replace('| `<local-state-root>/data/raw/` | External authoritative candle arrays and metadata sidecars. |','| `apps/chart/state/data/raw/` | Project-local candle arrays and metadata sidecars. |')
s=s.replace('| `<local-state-root>/cache/`, `<local-state-root>/secret/` | External user drawings, templates, calculation caches, and FARAZ session state; preserve by default. |','| `apps/chart/state/cache/`, `apps/chart/state/secret/` | Project-local user drawings, templates, calculations and FARAZ authentication; ignored and preserved by default. |')
s=s.replace('| `docs/` | Maintained architecture, algorithm, UI, audit, cleanup, validation, and Graphify evidence. |','| `engineering/docs/`, `engineering/archive/`, `engineering/verification/` | Maintained guidance, ignored historical evidence and local verification artifacts. |')
s=s.replace('creates external state directories','creates project-local state directories through the shared resolver')
s=s.replace('[TradingBot_Technical_Architecture.md](docs/architecture/TradingBot_Technical_Architecture.md)','[Technical architecture](engineering/docs/architecture/technical-architecture.md)')
s=s.replace('The external historical `archive/docs/graphify/rebuild-2026-09-23/` snapshot','The project-local historical `engineering/archive/docs/graphify/rebuild-2026-09-23/` snapshot')
s=s.replace('The dated Graphify snapshot is now external archived evidence under the local-state root, `archive/docs/graphify/rebuild-2026-09-23/`.','The dated Graphify snapshot is ignored project-local archived evidence under `engineering/archive/docs/graphify/rebuild-2026-09-23/`.')
s=s.replace('`docs/graphify/rebuild-2026-09-19/` remains preserved','`engineering/archive/repository-graphify/rebuild-2026-09-19/` remains preserved')
s=s.replace('Do not expose or copy `runtime/cache/secret` contents.','Do not expose or copy `apps/chart/state/secret/` values into logs, reports or delivery packages.')
start=s.index('## L. Documentation Index');end=s.index('## M. Repository Storage Policy')
s=s[:start]+'''## L. Documentation Index

- [Engineering index](engineering/docs/README.md): current maintained document navigation.
- [Operating protocol](engineering/docs/ai/operating-protocol.md): engineering and delivery requirements, subordinate to root authority.
- [Technical architecture](engineering/docs/architecture/technical-architecture.md) and [UI/UX reference](engineering/docs/architecture/ui-ux-reference.md): dated evidence with current navigation notes.
- [Local storage](engineering/docs/operations/local-state.md), [Local tests](engineering/docs/development/local-tests.md) and [Repository integrity](engineering/docs/verification/repository-integrity.md): current storage and validation rules.
- [Single-root migration](engineering/docs/verification/single-root-migration.md): complete movement and validation evidence.
- [Bullish Reference](engine/algorithms/TradingBot_Bullish_Algorithm_Reference_V5.4.19_EX1_Source_Synchronized.md) and [Bearish Reference](engine/algorithms/TradingBot_Bearish_Algorithm_Reference_V5.4.19_EX1_Source_Synchronized.md): unchanged current exact-source references.

Historical Graphify/regression material stays in ignored `engineering/archive/`; old build scripts and path strings inside those bundles are historical evidence, not active tool entry points. Every Graphify execution still requires explicit approval.

`AGENTS.md` is the canonical root entry point. No nested project AGENTS was found in the current source inventory.

'''+s[end:]
start=s.index('## M. Repository Storage Policy')
s=s[:start]+'''## M. Repository Storage Policy

All project-owned content stays inside `D:\\My-Projects\\TradingBot`. Three primary owners are `apps/`, `engine/` and `engineering/`. `scripts/` remains a root tooling exception preserving established Windows/VMware startup paths. Root Git/editor configuration, AGENTS and README stay at discovery boundaries.

`TRADINGBOT_LOCAL_STATE_ROOT` defaults to `apps/chart/state`; configured roots may select only that dedicated subtree or a descendant. The shared resolver rejects source directories, external paths and escaping junctions. The launcher uses the same resolver. RAW, caches, secrets and temporary files remain project-local and Git-ignored. Direct Vite file access to state is denied; its normal API contracts remain available.

Tests live beside their owners under ignored `apps/chart/tests/` and `engine/tests/`; chart tests run with `npm.cmd test` from `apps/chart`. Engine production-source discovery excludes test code. Dependencies/build output remain reproducible and ignored. Historical Graphify/regression artifacts live in ignored `engineering/archive/`; migration snapshots, maps and logs live in ignored `engineering/verification/`. Only the two source-synchronized references under `engine/algorithms/` are current references.
'''
p.write_text(s,encoding='utf-8')

write('engineering/archive/README.md', '''# Preserved historical evidence

Everything in this ignored directory is preserved project-local evidence, not active production authority or runnable current tooling. Dated source copies, graphs, regression results and manifests retain their original bytes and recorded paths.

`docs/` contains archives formerly held by the external state root. `repository-graphify/` contains the separate current checkout's old Graphify bundle; it is deliberately separate to avoid overwriting historical duplicates. `documentation/docs.zip` preserves the user's document archive unchanged.

Archived build/migration scripts may contain old absolute roots, docs paths or external storage policies. Those strings describe their original context. Do not run such scripts or promote their source copies to Current. Graphify execution always requires separate user approval.
''')
print('Updated live documentation/navigation; preserved historical audit bodies and archive contents.')
