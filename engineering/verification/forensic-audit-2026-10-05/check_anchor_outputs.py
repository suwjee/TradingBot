"""Locate regression anchors in recorded unmodified engine outputs."""
from pathlib import Path
import json
from datetime import datetime
from zoneinfo import ZoneInfo
OUT=Path(__file__).resolve().parent
result={}
def local(value):
    return datetime.fromtimestamp(value,ZoneInfo('Asia/Tehran')).strftime('%Y-%m-%d %H:%M:%S') if isinstance(value,(int,float)) else str(value)
for label,relative in [('USOIL-target','raw-30s/raw-14-30s-1.stdout.json'),
                       ('USOIL-continuous','finest-union/raw-00-30s-1.stdout.json'),
                       ('XAUUSD-anchor','raw-30s/raw-08-30s-1.stdout.json'),
                       ('XAUUSD-continuous','finest-union/raw-01-30s-1.stdout.json')]:
    data=json.loads((OUT/relative).read_bytes()); entries={}
    for direction,body in data['directions'].items():
        if label.startswith('USOIL'):
            entries[direction]={'StopAllTargets':[x for x in body['stopAlls'] if local(x['sourceTime']).startswith(('2026-09-25 08:51:00','2026-10-02 20:20:00'))]}
        else:
            selected=[o for o in body['orderAudit'] if local(o['firstTime']).startswith('2026-09-29 20:32:00')]
            entries[direction]={'physicalOrdersAtAnchor':selected,
                                'visibleAAtEarlierSource':[a for a in body['aZones'] if local(a['sourceTime']).startswith('2026-09-29 20:15:30')]}
    result[label]={'output':relative,'entries':entries}
(OUT/'regression-anchor-outputs.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
for label,item in result.items():
    for direction,values in item['entries'].items():
        print(label,direction,json.dumps(values))
