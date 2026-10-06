"""Validate the delivered report, evidence pointers and stated counts."""
from pathlib import Path
from collections import Counter
import json, re
OUT=Path(__file__).resolve().parent
def load(p):return json.loads((OUT/p).read_text(encoding='utf-8'))
report=(OUT/'AUDIT_REPORT.md').read_text(encoding='utf-8')
headings=re.findall(r'^## (\d+)\. ',report,re.M)
assert list(map(int,headings))==list(range(1,21)),headings
findings=load('findings.json')
assert len(findings)==13 and len({i['BUG ID'] for i in findings})==13
assert Counter(i['CONFIDENCE'] for i in findings)=={'CONFIRMED':10,'HIGH-CONFIDENCE':3}
assert all(len(i)==23 and all(v for v in i.values()) for i in findings)
matrix=load('verification-matrix.json')
assert all(i['status'] in ('PASS','FAIL','NOT RUN','INCOMPLETE') for i in matrix)
summary=load('audit-summary.json')
assert summary['completeDirectionCalculations']==84
assert summary['rawInvariantCases']==42 and summary['rawInvariantFailures']==0
assert summary['rawInvariantCheckStatuses']=={'PASS':504}
assert summary['repeatStatuses']=={'PASS':8}
assert summary['sourceFiles']==12 and summary['sourceLines']==12735
for value in ('protectedStatus','packageAndLiveSourceStatus','preexistingGitStatus'):
    assert summary['integrity'][value]=='PASS'
for i in load('reference-byte-analysis.json'):
    assert len(i['entries'])==13
    assert sum(e['exactBytesEqual'] for e in i['entries'])==1
    assert sum(e['newlineNormalizedEqual'] for e in i['entries'])==12
    assert sum(e['ASTEqual'] for e in i['entries'])==12
raw=load('raw-decimal-validation.json')
assert len(raw['exactValidation'])==15
assert all(i['exactOHLC']=='PASS' and i['numericLexemeValuesPreserved']=='PASS' for i in raw['exactValidation'])
unique={e['time'] for r in raw['oneSecondVersusFiveSecond'] for e in r['examples']}
assert len(unique)==3
missing=[]; targets=[]
for match in re.finditer(r'\]\((<?D:/[^)]+)\)',report):
    target=match[1].strip('<>')
    targets.append(target)
    if not Path(target).exists():missing.append(target)
assert not missing,missing
for relative in ('unit-tests.log','chart-unit-tests.log','restored-index-failures.log'):
    assert (OUT/relative).stat().st_size>0
assert "cannot import name 'run_blue_line'" in (OUT/'package-import.log').read_text(encoding='utf-8')
assert 'reaction-audit/probe-evidence.json' in report
assert 'newline-normalized embedded source' in report.lower()
print(json.dumps({'reportStructure':'PASS','sections':20,'requiredFindingFields':'PASS','findings':13,
                  'verificationMatrix':'PASS','checks':len(matrix),'reportedCounts':'PASS',
                  'localEvidenceLinks':'PASS','linksChecked':len(targets),'protectedIntegrity':'PASS',
                  'referenceByteClaims':'PASS','RAWDecimalClaims':'PASS','crossGranularityUniqueDifferences':3},indent=2))
