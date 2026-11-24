#!/usr/bin/env python3
"""Detect and disambiguate same-name Python property getter/setter trace events.

Fail closed if the anticipated pinned source property layout changed.
This diagnostic cannot certify different-frequency getters as semantically equal.
"""
from __future__ import annotations
import argparse,collections,gzip,json,ast
from pathlib import Path

SOURCES={
 'original':Path('/mnt/data/V9_work/golden/github_engine_commit_01d54ecf/engine/pipeline/e_zone_detector.py'),
 'v81':Path('/mnt/data/V9_work/v81/engine/pipeline/e_zone_detector.py'),
}

def resolve(source):
    root=ast.parse(source.read_text())
    rows={}
    for obj in ast.walk(root):
        if isinstance(obj,(ast.FunctionDef,ast.AsyncFunctionDef)) and obj.name=='sequence_resets':
            for d in obj.decorator_list:
                if isinstance(d,ast.Name) and d.id=='property':label='property_getter'
                elif isinstance(d,ast.Attribute) and d.attr=='setter':label='property_setter'
                else:continue
                # Python co_firstlineno at decorator rather than def is stable
                rows[min(x.lineno for x in obj.decorator_list)]=label
    if sorted(rows.values())!=['property_getter','property_setter']:
        raise AssertionError('Unexpected property accessor identities in '+str(source)+': '+str(rows))
    return rows

def load(path,rolemap):
    result=collections.defaultdict(list)
    with gzip.open(path,'rt') as f:
        for line in f:
            ev=json.loads(line)
            if ev.get('module')=='e_zone_detector.py' and ev.get('method')=='sequence_resets':
                start=ev['source_first_line']
                if start not in rolemap:
                    raise AssertionError('Unexpected ambiguous accessor '+str(start))
                role=rolemap[start]
                result[role].append({'return':ev['return'],
                                     'pre_selected_state':ev['pre_selected_state'],
                                     'post_selected_state':ev['post_selected_state']})
    return result

def run(orig,candidate,out):
    role_o=resolve(SOURCES['original']);role_v=resolve(SOURCES['v81'])
    a=load(orig,role_o);b=load(candidate,role_v)
    g1=a['property_getter'];g2=b['property_getter'];s1=a['property_setter'];s2=b['property_setter']
    if len(s1)!=len(s2):status='SETTER_CALL_COUNT_DIFF';equal=False
    else:equal=(s1==s2);status='SETTER_SELECTED_COUNTS_EQUAL' if equal else 'SETTER_SELECTED_COUNTS_DIFF'
    result={'status':'DIAGNOSTIC_ONLY_NOT_FULL_SEMANTIC_PASS','pinned_original_line_roles':role_o,
            'v81_line_roles':role_v,'original_getter_calls':len(g1),'v81_getter_calls':len(g2),
            'original_setter_calls':len(s1),'v81_setter_calls':len(s2),
            'getter_count_difference':len(g1)-len(g2),
            'setter_selective_state_and_return_equal':equal,
            'setter_status':status,
            'getter_return_sequence_exactly_equal':len(g1)==len(g2) and g1==g2,
            'important_limitation':'Fewer getter calls are not behavioral differences by themselves. The sampled instance state is count-only. The getter samples are not aligned by decision event time or owner identity. Do not relabel semantic coverage as PASS.'}
    Path(out).write_text(json.dumps(result,indent=2));print(result)
    return 0 if equal else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('original');p.add_argument('v81');p.add_argument('--out',required=True);a=p.parse_args()
    raise SystemExit(run(a.original,a.v81,a.out))