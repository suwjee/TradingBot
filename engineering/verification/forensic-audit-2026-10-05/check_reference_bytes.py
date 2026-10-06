"""Distinguish exact byte synchronization from newline-only equivalence."""
from pathlib import Path
import ast, hashlib, json, re
OUT=Path(__file__).resolve().parent
records=[]
for ref in (OUT/'package/algorithms').glob('*.md'):
    entries=[]
    for match in re.finditer(rb'<!-- EXACT-SOURCE-BEGIN:([^\r\n]+) -->\r?\n````python\r?\n(.*?)````\r?\n<!-- EXACT-SOURCE-END:\1 -->',ref.read_bytes(),re.S):
        path=match[1].decode(); embedded=match[2]; actual_path=OUT/'package'/path
        actual=actual_path.read_bytes() if actual_path.exists() else None
        normal=lambda b:b.replace(b'\r\n',b'\n')
        entries.append({'path':path,'exists':actual is not None,'exactBytesEqual':embedded==actual,
                        'newlineNormalizedEqual':actual is not None and normal(embedded)==normal(actual),
                        'embeddedCRLF':embedded.count(b'\r\n'),'actualCRLF':actual.count(b'\r\n') if actual is not None else None,
                        'embeddedBytes':len(embedded),'actualBytes':len(actual) if actual is not None else None,
                        'ASTEqual':actual is not None and ast.dump(ast.parse(embedded))==ast.dump(ast.parse(actual))})
    records.append({'reference':ref.name,'entries':entries})
(OUT/'reference-byte-analysis.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
for row in records:
    print(json.dumps({'reference':row['reference'],'entries':len(row['entries']),
                     'exact':sum(i['exactBytesEqual'] for i in row['entries']),
                     'newlineEqual':sum(i['newlineNormalizedEqual'] for i in row['entries']),
                     'ASTEqual':sum(i['ASTEqual'] for i in row['entries']),
                     'nonNewlineDifferences':[i for i in row['entries'] if i['exists'] and not i['newlineNormalizedEqual']]}))
