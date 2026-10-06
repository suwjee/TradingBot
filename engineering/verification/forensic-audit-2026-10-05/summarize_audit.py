"""Read evidence only; report bounded coverage and protected-file integrity."""
from pathlib import Path
from collections import Counter
import hashlib, importlib.metadata, json, platform, subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]

def load(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))

def main():
    source = load('source-map.json')
    original = load('raw-registry.json')
    matrices = {folder: load(folder+'/manifest.json') for folder in
                ('raw-30s','raw-60s','raw-5s','determinism','finest-union')}
    protected = load('protected-pre-hashes.json')
    mismatches = []
    for relative, expected in protected.items():
        path = ROOT / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        if actual != expected:
            mismatches.append({'path':relative,'expected':expected,'actual':actual})
    package_errors = []
    for item in source:
        for location in (ROOT/'engine'/item['path'], OUT/'package'/item['path']):
            actual = hashlib.sha256(location.read_bytes()).hexdigest()
            if actual != item['hash']:
                package_errors.append(str(location))
    before = load('git-before.json')
    status = subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT,text=True)
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    owned = 'engineering/verification/forensic-audit-2026-10-05/'
    prior = {line for line in before['status'].splitlines() if owned not in line}
    now = {line for line in status.splitlines() if owned not in line}
    git_diff = {'added':sorted(now-prior),'removed':sorted(prior-now),'headBefore':before['head'],'headAfter':head}
    integrity = {'protectedFilesChecked':len(protected),'protectedStatus':'PASS' if not mismatches else 'FAIL',
                 'protectedMismatches':mismatches,'packageAndLiveSourceStatus':'PASS' if not package_errors else 'FAIL',
                 'packageErrors':package_errors,'preexistingGitStatus':'PASS' if prior==now and head==before['head'] else 'FAIL',
                 'gitDeltaOutsideOwnedAudit':git_diff,
                 'chartProductionBaseline':'INCOMPLETE - no initial chart byte hashes; current hashes recorded by boundary reviewer'}
    (OUT/'integrity-final.json').write_text(json.dumps(integrity,indent=2),encoding='utf-8')
    counts = {}
    for folder, records in matrices.items():
        counts[folder]={'runs':len(records),'directionsPerRun':2,
                        'executionCounts':dict(Counter(r.get('execution','INCOMPLETE') for r in records)),
                        'timeframes':sorted({r['timeframe'] for r in records}),
                        'totalWallSeconds':round(sum(r.get('wallSeconds',0) for r in records),2),
                        'longestWallSeconds':round(max((r.get('wallSeconds',0) for r in records),default=0),2)}
    invariants = load('raw-invariants.json')
    repeat = [r for r in matrices['determinism'] if 'determinism' in r]
    summary = {'auditStartLocalDate':'2026-10-05','auditCompletionLocalDate':'2026-10-06','timezone':'Asia/Tehran',
               'engineZipSha256':protected['engine\\engine.zip'],
               'python':platform.python_version(),'dependencies':{n:importlib.metadata.version(n) for n in ('orjson','pytest','tzdata')},
               'sourceFiles':len(source),'sourceLines':sum(i['lines'] for i in source),
               'sourceDefinitionNodes':sum(len(i['definitions']) for i in source),
               'modules':[{k:i[k] for k in ('path','hash','lines','metadata')} for i in source],
               'originalRAWFiles':len(original),'originalRAWSuppliedRows':sum(i['rows'] for i in original),
               'matrices':counts,'completeDirectionCalculations':2*sum(len(v) for v in matrices.values()),
               'repeatComparisons':len(repeat),'repeatStatuses':dict(Counter(i['determinism'] for i in repeat)),
               'rawInvariantCases':len(invariants),'rawInvariantFailures':sum(len(i['failures']) for i in invariants),
               'rawInvariantCheckStatuses':dict(Counter(v for i in invariants for v in i['checks'].values())),
               'configurationCases':len(load('configurations/manifest.json')),'integrity':integrity}
    (OUT/'audit-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('modules','integrity')},indent=2))
    print(json.dumps(integrity,indent=2))

if __name__ == '__main__':
    main()
