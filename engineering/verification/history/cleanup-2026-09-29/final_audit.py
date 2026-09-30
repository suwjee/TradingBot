from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from audit import ROOT, AUDIT, classify, digest, git

LOCAL = ROOT.with_name(ROOT.name + '-Local')
baseline = json.loads((AUDIT/'baseline-inventory.json').read_text())
actions = json.loads((AUDIT/'migration-actions.json').read_text(encoding='utf-8-sig'))

def project_files():
    files=[]
    for current,dirs,names in os.walk(ROOT):
        dirs[:]=[d for d in dirs if d!='.git']
        files.extend(Path(current)/name for name in names)
    return sorted(files)

def scan(paths, indexed=False):
    findings=[]
    patterns={
        'private-key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
        'cloud-access-key':re.compile(rb'\bAKIA[A-Z0-9]{16}\b'),
        'github-token':re.compile(rb'\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),
        'api-secret-key':re.compile(rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b'),
        'literal-auth-value':re.compile(rb'''(?i)["'](?:password|passwd|api_key|apiKey|x-access-token|farazSession|authorization)["']\s*:\s*["']([^"'\r\n]{8,})["']'''),
    }
    for relative in paths:
        if re.search(r'(?i)(?:^|/)(secret|runtime|data|node_modules|graphify-out)(?:/|$)|\.dpapi\.json$',relative):
            findings.append({'path':relative,'type':'forbidden-local-state-path'})
            continue
        content=git('show',':'+relative).stdout if indexed else (ROOT/relative).read_bytes()
        for kind,pattern in patterns.items():
            for match in pattern.finditer(content):
                if kind=='literal-auth-value':
                    value=match[1]
                    if value.startswith((b'test-',b'example',b'<',b'$')) or b'...' in value: continue
                findings.append({'path':relative,'line':content[:match.start()].count(b'\n')+1,'type':kind})
    return findings

paths=[p.relative_to(ROOT).as_posix() for p in project_files() if 'tests' not in p.relative_to(ROOT).parts]
findings=scan(paths)
(AUDIT/'pre-stage-secret-audit.json').write_text(json.dumps({'status':'PASS' if not findings else 'FAIL','files':len(paths),'findings':findings},indent=2))
print(json.dumps({'pre_stage_files':len(paths),'secret_findings':findings}))
assert not findings

if '--stage' in sys.argv:
    result=git('add','-A','--','.')
    (AUDIT/'stage-command.log').write_bytes(result.stdout+result.stderr)
    assert result.returncode==0
    tracked=git('ls-files','-z').stdout.decode().strip('\0').split('\0')
    findings=scan(tracked,indexed=True)
    forbidden=[p for p in tracked if p.startswith(('tests/','apps/chart/tests/','data/','runtime/','graphify-out/','docs/graphify/','tmp/')) or any(x in p.split('/') for x in ['node_modules','dist','__pycache__','.pytest_cache','.vite','.vite-temp'])]
    untracked=git('ls-files','--others','--exclude-standard','-z').stdout.decode().strip('\0')
    unstaged=git('diff','--name-only').stdout.decode().strip()
    protected=json.loads((AUDIT/'protected-engine-hashes.json').read_text())
    engine_diff=[p for p,h in protected.items() if digest(ROOT/p)!=h]
    engine_index_diff=[p for p,h in protected.items() if hashlib.sha256(git('show',':'+p).stdout).hexdigest()!=h]
    raw_diff=[r['path'] for r in baseline if r['classification']=='MARKET_DATA' and digest(LOCAL/r['path'])!=r['sha256_before']]
    source_diff=[r['path'] for r in baseline if r['path'].startswith(('apps/chart/src/','apps/chart/scripts/')) and digest(ROOT/r['path'])!=r['sha256_before']]
    leftover=[]
    for current,dirs,names in os.walk(ROOT):
        dirs[:]=[d for d in dirs if d!='.git']
        for d in dirs:
            if d in ['data','runtime','tmp','graphify-out','node_modules','dist','__pycache__','.pytest_cache','.cache','.vite','.vite-temp','.benchmarks']:
                leftover.append((Path(current)/d).relative_to(ROOT).as_posix())
    manifest=[]
    for row in baseline:
        original=row['path']; destination=ROOT/original; operation='KEEP';reason='Maintained project content or local test'
        selected=[a for a in actions if original==a['source'] or original.startswith(a['source']+'/')]
        if selected:
            action=max(selected,key=lambda a:len(a['source']))
            operation=action['action'];reason=action['reason']
            if operation=='DELETE':destination=None
            else:
                destination=Path(action['destination'])/original[len(action['source']):].lstrip('/')
                operation='MOVE' if destination.is_relative_to(ROOT) else 'MOVE_OUTSIDE_REPOSITORY'
        current=(destination.relative_to(ROOT).as_posix() if destination and destination.is_relative_to(ROOT) else str(destination) if destination else '')
        secret=row['classification']=='SECRET'
        manifest.append({**row,'action':operation,'destination':current if not secret else 'EXTERNAL_SECRET_STORAGE','reason':reason,'tracked_after':current in tracked,'sha256_after':digest(destination) if destination and destination.exists() and not secret else ''})
    original_destinations={r['destination'] for r in manifest}
    for p in project_files():
        relative=p.relative_to(ROOT).as_posix()
        if relative not in original_destinations:
            manifest.append({'path':relative,'classification':classify(relative),'size':p.stat().st_size,'tracked_before':False,'sha256_before':'','action':'TRACK' if relative in tracked else 'KEEP','destination':relative,'reason':'New maintained documentation/configuration or local path regression','tracked_after':relative in tracked,'sha256_after':digest(p)})
    for row in manifest:
        if row['classification']=='SECRET':row['path']='SECRET_FILE_FOUND';row['sha256_before']='';row['sha256_after']=''
    fields=list(manifest[0])
    with (AUDIT/'cleanup-manifest.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(manifest)
    (AUDIT/'cleanup-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    physical=[p.relative_to(ROOT).as_posix() for p in project_files()]
    (AUDIT/'physical-files.txt').write_text('\n'.join(physical)+'\n',encoding='utf-8')
    (AUDIT/'github-files.txt').write_text('\n'.join(tracked)+'\n',encoding='utf-8')
    baseline_tracked=set((AUDIT/'baseline-tracked.txt').read_text().splitlines())
    newly_tracked=[p for p in tracked if p not in baseline_tracked]
    stats={'original_files':len(baseline),'physical_files':len(physical),'tracked_files':len(tracked),'local_test_files':sum(p.startswith('tests/') for p in physical),'action_counts':dict(Counter(r['action'] for r in manifest)),'newly_tracked':newly_tracked,'secret_audit':'PASS' if not findings else 'FAIL','secret_findings':findings,'forbidden_index_paths':forbidden,'untracked':untracked,'unstaged':unstaged,'engine_hash_diff':engine_diff,'engine_index_hash_diff':engine_index_diff,'raw_hash_diff':raw_diff,'application_source_hash_diff':source_diff,'local_state_directories_remaining':leftover,'head':git('rev-parse','HEAD').stdout.decode().strip(),'branch':git('branch','--show-current').stdout.decode().strip(),'tracked_tests':len([p for p in tracked if p.startswith('tests/')])}
    (AUDIT/'final-audit.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
    for name,args in [('final-status',['status','--short']),('final-staged-stat',['diff','--cached','--stat']),('final-staged-diff',['diff','--cached','--binary']),('final-name-status',['diff','--cached','--name-status','-M'])]:
        output=git(*args);(AUDIT/(name+'.txt')).write_bytes(output.stdout+output.stderr)
    checks=[findings,forbidden,untracked,unstaged,engine_diff,engine_index_diff,raw_diff,source_diff,leftover]
    stats['verdict']='REPOSITORY_STRUCTURE_READY_FOR_GITHUB' if not any(checks) else 'REPOSITORY_STRUCTURE_NOT_READY'
    (AUDIT/'final-audit.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
    print(json.dumps(stats,indent=2))
    assert not any(checks)
