from collections import Counter
import ast
from datetime import datetime
import json
from pathlib import Path
import re
import zipfile
from zoneinfo import ZoneInfo
from audit import ROOT,AUDIT,git,digest

stats=json.loads((AUDIT/'final-audit.json').read_text())
inventory=json.loads((AUDIT/'baseline-inventory.json').read_text())
manifest=json.loads((AUDIT/'cleanup-manifest.json').read_text())
tracked=(AUDIT/'github-files.txt').read_text().splitlines()
physical=(AUDIT/'physical-files.txt').read_text().splitlines()

def tree(paths):
    root={}
    for path in paths:
        node=root
        for part in path.split('/'):
            node=node.setdefault(part,{})
    lines=['TradingBot/']
    def render(node,prefix=''):
        items=sorted(node.items(),key=lambda item:(not bool(item[1]),item[0]))
        for index,(name,children) in enumerate(items):
            last=index==len(items)-1
            lines.append(prefix+('└── ' if last else '├── ')+name+('/' if children else ''))
            if children:render(children,prefix+('    ' if last else '│   '))
    render(root)
    return '\n'.join(lines)

physical_tree=tree(physical)
github_tree=tree(tracked)
(AUDIT/'physical-tree.txt').write_text(physical_tree+'\n',encoding='utf-8')
(AUDIT/'github-tree.txt').write_text(github_tree+'\n',encoding='utf-8')

history_objects=git('rev-list','--objects','--all').stdout.decode(errors='replace').splitlines()
historical_secret_paths=[]
for line in history_objects:
    parts=line.split(' ',1)
    if len(parts)<2:continue
    path=parts[1]
    if path.endswith('.gitkeep'):continue
    if re.search(r'(?:^|/)(?:secret|secrets)/|\.dpapi\.json$|(?:^|/)\.env$|\.(?:pem|key)$',path,re.I):historical_secret_paths.append(path)
(AUDIT/'secret-history-audit.json').write_text(json.dumps({'artifact_paths_found':len(historical_secret_paths),'scope':'All locally available Git refs; authentication/environment/key filenames. No history rewrite or historical-value scan.'},indent=2))

validations=[
('Baseline npm.cmd test','PASS','156 tests; baseline-node-tests.log'),
('Baseline python -B -m pytest -q -p no:cacheprovider tests','PASS','21 tests; baseline-python-tests.log'),
('node --test tests/local-state-paths.test.mjs before implementation','FAIL','Expected red test: storage resolver did not exist.'),
('node --test tests/local-state-paths.test.mjs after implementation','PASS','3 external storage checks.'),
('npm.cmd ci','PASS','18 packages installed from unchanged lockfile; npm-ci.log'),
('npm.cmd test after centralization','PASS','159 tests; final-node-tests.log'),
('python -B -m pytest -q -p no:cacheprovider tests/engine/unit','PASS','21 tests.'),
('python -B tests/engine/helpers/verify_order_references.py','PASS','13 exact embedded Python modules per direction.'),
('python -B tests/engine/regression/order_regression.py --help','PASS','Relocated runner initializes and exposes supported options.'),
('npm.cmd run build','PASS','55 modules; reproducible dist. Existing >500 kB chunk warning.'),
('python -B external structural_checks.py','PASS','23 Python AST files, 50 Node syntax files, 66 relative imports, 36 links, normal dynamic Engine load.'),
('PowerShell AST and storage block checks','PASS','Default, absolute/relative overrides and in-repository rejection.'),
('First live-storage-check.mjs probe','FAIL','Probe used file= instead of the existing endpoint\'s id= parameter. Probe corrected; application contract preserved.'),
('Corrected live-storage-check.mjs','PASS','14,140-row real migrated RAW returned unchanged; /info shell available.'),
('Pre-stage and staged credential/path scan','PASS','102 indexed files; no findings or local-state/test artifacts.'),
('Physical and Git-index Engine SHA-256 comparison','PASS','16 protected files unchanged versus the initial working tree.'),
('RAW and metadata SHA-256 comparison','PASS','22 moved data/sidecar/placeholder files unchanged.'),
('git diff --cached --check','FAIL','Four inherited protected-file whitespace warnings: both exact references, bridge and Order module. Engine bytes intentionally preserved.'),
('git diff --cached --check -- . :!engine','PASS','Cleanup-owned staged changes pass. Markdown hard line breaks have explicit whitespace policy.'),
('Final index, untracked, ignored tests and physical state audit','PASS','102 tracked; 39 local tests; no unstaged/unexplained untracked files or prohibited local-state directories.'),
('Full market regression / independent directional correctness','SKIPPED','No calculation source or RAW bytes changed; user cleanup instruction excludes a new market run solely for layout changes.'),
('Graphify, commit, push','SKIPPED','Explicitly prohibited by this task.'),
]
(AUDIT/'validation-results.json').write_text(json.dumps(validations,indent=2))

baseline_status=(AUDIT/'baseline-status-short.txt').read_text()
sections=[]
def section(number,title,body):sections.append(f'## {number}. {title}\n\n{body}\n')
section(1,'FINAL VERDICT',stats['verdict'])
section(2,'PROJECT ROOT',str(ROOT))
section(3,'GIT TOPOLOGY',f"Root: {ROOT}\n\nBranch: `{stats['branch']}`; HEAD: `{stats['head']}`. `origin/main` points to the same locally recorded commit. Secondary local branch: `rewrite-stable-2`. Tags: `2.0.0`, `v2.1.0`. No nested Git repositories or submodules found. A separate existing Codex worktree is registered and untouched. Pre-existing staged, unstaged, deleted and untracked work is captured in baseline-status-short.txt, original index, binary diffs and source archive. No fetch/history rewrite/commit/push occurred.")
section(4,'ORIGINAL TREE ANALYSIS','915 files inventoried recursively, excluding Git internals. Classification counts:\n\n'+ '\n'.join(f'- {name}: {count}' for name,count in sorted(Counter(row['classification'] for row in inventory).items()))+'\n\nNo UNKNOWN files remained. Application drawing source, review.html, RAW migration API and Engine styles have live callers and remain. Documentation copies were evaluated against the current Plugin Reference Registry. Generated duplicate results were externally archived; production source was preserved.')
section(5,'REMOVED REPOSITORY-LOCAL STATE','`data/`, all `runtime/` state, root `tmp/`, root/docs Graphify output, node_modules, dist, Vite accidental-path output, pytest/Python caches and benchmark caches are absent physically. No .gitkeep skeleton remains inside the repository. Original regenerable files were removed after classification; valuable state and historical evidence were moved externally. Regenerated dependencies/build/cache files were preserved in external regenerated-artifacts after automatic approval review rejected their deletion.')
section(6,'EXTERNAL LOCAL STATE','Root: `D:\\My-Projects\\TradingBot-Local`. RAW: `data/raw/`; persistent caches: `cache/`; authentication: `secret/`; temporary state: `tmp/`; remaining historical runtime state: `runtime/`. Historical evidence: `archive/`. Secret reporting: `SECRET_FILE_FOUND`, `MOVED_OUTSIDE_REPOSITORY`, `NOT_TRACKED`. No values were read into reports or Git.')
section(7,'FILE CLEANUP','Original 915 files: 454 regenerable files deleted; 49 files moved within the checkout; 330 files externalized; 82 original files kept in place. Ten new files were added (nine repository files and one local test), yielding 141 physical files: 102 tracked and 39 local tests. Two superseded directional documentation copies were removed from the current-reference set and preserved externally. Unresolved classifications: 0. Generated artifacts recreated during validation were subsequently moved outside and are not counted as original-file removals.')
section(8,'UNUSED / OBSOLETE FILES','Completed one-off `extract_order_module.py`, `extract_s_order_methods.py` and `build_order_references.py` were externally archived: their baseline/default reference version is superseded and they have no active production caller. Superseded `docs/AGEN.md`, the prior engineering-audit request, and completed audit plans were archived. Node/Python/Vite/pytest/benchmark/build output is regenerable. Unknown or irreplaceable evidence was not deleted.')
section(9,'DUPLICATES','Current directional ownership is unique: retain the exact two 5.4.19-EX1 references under engine/algorithms. Older docs-level references no longer look current. Duplicate Graphify trees and equal-hash generated regression cases were removed from repository structure and preserved externally with their provenance. Equal drawing files belong to distinct chart identities and were preserved. No production source was removed solely because hashes matched.')
section(10,'DOCS STRUCTURE','```text\ndocs/\n  README.md\n  algorithms/README.md\n  architecture/\n  development/ (protocol, specifications, local test workflow, plans/specs)\n  operations/Local_State.md\n  verification/Repository_Integrity.md\n  history/ (dated reports and index)\n```\n\nLive Markdown navigation: 36 links verified. Dated audit prose remains explicitly labeled historical; existing Reference narrative discrepancies remain disclosed.')
section(11,'TEST STRUCTURE','```text\ntests/                         LOCAL ONLY / GIT-IGNORED\n  chart/unit/                  29 Node files\n  engine/unit/                 2 Python files\n  engine/helpers/              2 verification files\n  engine/regression/           4 runner/comparison files\n  engine/benchmarks/           2 reusable benchmark files\n```\n\n`GIT_TRACKED = NO`; indexed test files: 0. Imports, actual bridge-test roots, synthetic FARAZ fixtures, runner RAW roots and package scripts were repaired. Local suites remain runnable after reinstalling dependencies.')
section(12,'APPLICATION STRUCTURE','Retained apps/chart: index.html, review.html, package.json, unchanged package-lock.json, vite.config.js, scripts/dev-server.mjs, server/ and src/. New shared server/local-state-paths.js governs external state. Browser source and drawing source bytes are unchanged from the initial working tree. Vite/FARAZ storage paths, cache-session clearing and startup configuration use the same external state policy.')
section(13,'ENGINE STRUCTURE','Retained engine/__init__.py, bridge/, pipeline/, algorithms/ and styles/. All 13 Python files, two references and imported CSS are byte-identical to the initial working tree. Existing pre-task Engine differences versus HEAD are staged under the user\'s complete-staging instruction; they were not authored by cleanup.')
section(14,'.GITIGNORE','Local /tests/; node_modules; Python/test caches; Vite caches; dist/build; coverage/benchmarks; local environments; temporary/log/editor/OS state. Defensive rules exclude data/runtime/tmp/secret/graphify remnants; the actual directories are also absent. Broad source extensions are not ignored. .gitattributes preserves exact Engine bytes and supports intentional Markdown hard line breaks.')
section(15,'NEWLY TRACKED FILES','23 final paths were absent from the starting index (includes moved documents). Full list:\n\n'+ '\n'.join('- `'+p+'`' for p in stats['newly_tracked'])+'\n\nPreviously untracked current Order module, both exact references, operating protocol and Bridge Output specification/plan are now indexed alongside new navigation/storage/configuration files.')
section(16,'UNTRACKED AUDIT','`LEGITIMATE_UNTRACKED_FILES = 0`\n\n`UNEXPLAINED_UNTRACKED_FILES = 0`\n\nAll remaining physical files outside Git are the explicitly ignored 39-file local test tree.')
section(17,'PRODUCTION SOURCE PROTECTION','`ENGINE_ALGORITHM_SOURCE_MODIFIED = NO`\n\n`ENGINE_ALGORITHM_SOURCE_HASH_DIFF = 0`\n\nComparison covers the current initial working tree versus final disk and Git index, not historical HEAD. All browser src/ and chart operational entry files are also unchanged versus the baseline.')
section(18,'REFERENCE PROTECTION','Bullish SHA-256: `d3a0b89c59f1304ddefe6f6931cedf7ea2e17a15893c63d652c89489f3e6387f`; Bearish SHA-256: `109753d7d056b6b9ee173cc7f47472b53a77174d26e89f38b00b81061f310e18`. Both remain current 5.4.19-EX1 exact bytes, and each reconstructs all 13 Python files. The four canonical narrative scope discrepancies are pre-existing and untouched; exact reconstruction does not claim semantic agreement.')
section(19,'SECRET AUDIT',f"`SECRET_AUDIT = PASS` for prospective and staged 102-file content, forbidden state paths and authentication artifacts. No values exposed. Historical authentication/key/environment artifact filenames found across locally available refs: {len(historical_secret_paths)}. This is a bounded content/pattern and history-path audit, not an exhaustive historical-secret proof. No history rewrite.")
section(20,'VALIDATION','| Command/check | Result | Evidence/scope |\n| --- | --- | --- |\n'+'\n'.join(f'| `{command}` | {status} | {detail} |' for command,status,detail in validations))
section(21,'PHYSICAL LOCAL PROJECT TREE','141 files; Git internals omitted from display. Tests are LOCAL ONLY / GIT-IGNORED.\n\n```text\n'+physical_tree+'\n```')
section(22,'EFFECTIVE GITHUB TREE','Generated from git ls-files; 102 files.\n\n```text\n'+github_tree+'\n```')
section(23,'GIT STATUS','PRE-EXISTING USER CHANGES are preserved in baseline-status-short.txt, baseline-diff.txt, baseline-diff-cached.txt, baseline-index and pre-cleanup-project.zip; historical/generated dirty work moved to archive/. Includes Engine modifications, old reference/test deletions, current reference/Order additions, manual-review source/test and Vite changes.\n\nCHANGES MADE BY THIS TASK: storage resolver and callers, launcher paths, test relocation/import/fixture configuration, .gitignore/.gitattributes, documentation organization/navigation, local-state externalization and index normalization. Full per-path ownership/actions/hashes are in cleanup-manifest.csv. Final status has staged changes only; no unstaged changes.')
section(24,'STAGED STATE','All intended current GitHub content and removals are staged. The effective index contains 102 project files and zero tests/local-state/generated artifacts. HEAD remains unchanged. No commit or push occurred. Review final-name-status.txt and final-staged-diff.txt. Release ZIP and local-test bundle remain external.')
section(25,'REMAINING ISSUES','No repository-cleanup blockers. Non-blocking preserved issues: four inherited whitespace diagnostics in protected files, the existing frontend chunk-size warning, and four previously disclosed Reference narrative discrepancies. No new market correctness claim is made. The original development server was stopped for migration and remains stopped; a later launch reinstalls dependencies. The earlier commentary count of 1,005 files was incorrect; the immutable inventory proves 915.')
section(26,'FINAL CONCLUSION',stats['verdict'])
(AUDIT/'FINAL_REPORT.md').write_text('\n'.join(sections),encoding='utf-8')

readme=['TradingBot repository cleanup source package','Classification: infrastructure/path/documentation cleanup; no algorithm/source byte change.',f'Baseline: {stats["head"]}; branch main; initial current working tree is authority.', 'Reference version before/after: 5.4.19-EX1 unchanged.', 'REGRESSION VERIFIED for applicable structural/local contract checks; full market/independent directional correctness NOT APPLICABLE to this cleanup.', 'Full staged whitespace check: inherited protected-file warnings preserved.', 'No commit, push or Graphify run. Tests, RAW, authentication and state are excluded.', '', 'Current package files (version before -> after; timestamp; purpose):']
own_modified={'apps/chart/vite.config.js','apps/chart/server/faraz-candle-api.js','scripts/start.ps1','apps/chart/package.json','AGENTS.md','.gitignore','.gitattributes','README.md'}
def file_version(path, relative):
    if relative.endswith(('package.json','package-lock.json')): return '3.4.1 -> 3.4.1'
    if relative.startswith('engine/algorithms/'): return '5.4.19-EX1 -> 5.4.19-EX1'
    if relative.startswith('engine/') and path.suffix == '.py':
        versions=[]
        for node in ast.parse(path.read_text(encoding='utf-8-sig')).body:
            if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
                for target in node.targets:
                    if isinstance(target,ast.Name) and target.id.endswith('_VERSION'):
                        versions.append(f'{target.id}={node.value.value} -> {node.value.value}')
        return '; '.join(versions) or 'unversioned -> unversioned'
    return 'unversioned -> unversioned'
for relative in tracked:
    p=ROOT/relative
    version=file_version(p,relative)
    timestamp=datetime.fromtimestamp(p.stat().st_mtime,ZoneInfo('Asia/Tehran')).strftime('%Y-%m-%d %H:%M:%S %z Asia/Tehran')
    purpose='storage/configuration/documentation update' if relative in own_modified else 'protected current Engine/reference bytes' if relative.startswith('engine/') else 'retained/organized current project content'
    readme.append(f'{relative} | {version} | {timestamp} | {purpose}')
(AUDIT/'readme.txt').write_text('\n'.join(readme)+'\n',encoding='utf-8')
with zipfile.ZipFile(AUDIT/'TradingBot-clean-repository-2026-09-29.zip','w',zipfile.ZIP_DEFLATED) as package:
    for relative in tracked:package.write(ROOT/relative,relative)
    package.write(AUDIT/'readme.txt','readme.txt')
with zipfile.ZipFile(AUDIT/'TradingBot-local-tests-2026-09-29.zip','w',zipfile.ZIP_DEFLATED) as package:
    for relative in physical:
        if relative.startswith('tests/'):package.write(ROOT/relative,relative)
with zipfile.ZipFile(AUDIT/'TradingBot-clean-repository-2026-09-29.zip') as package:
    assert package.testzip() is None
    assert set(package.namelist())==set(tracked)|{'readme.txt'}
    for relative in tracked:assert digest(ROOT/relative)==__import__('hashlib').sha256(package.read(relative)).hexdigest()
summary={'report':str(AUDIT/'FINAL_REPORT.md'),'release_zip_files':len(tracked)+1,'local_test_bundle_files':stats['local_test_files'],'historical_secret_artifact_paths':len(historical_secret_paths),'verdict':stats['verdict']}
(AUDIT/'delivery-verification.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
