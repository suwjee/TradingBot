"""Test-only operation counters. No production state access or mutation."""
from collections import defaultdict
COUNTS=defaultdict(int)
def tick(tag):
    COUNTS[tag]+=1
def tap(tag, func, *args, **kwargs):
    COUNTS[tag]+=1
    return func(*args,**kwargs)
def save(path):
    import json
    from pathlib import Path
    Path(path).write_text(json.dumps({'coverage':'SELECTED_AST_LOOP_SORT_HEAP_AND_CACHE_OPERATIONS_ONLY',
                 'counts':dict(sorted(COUNTS.items()))},indent=2),encoding='utf8')
