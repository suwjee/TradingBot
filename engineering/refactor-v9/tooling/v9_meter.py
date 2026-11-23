"""Test-only operation counters. No production state access or mutation."""
from collections import defaultdict
COUNTS=defaultdict(int)
LAST_REASON=None
def tick(tag):
    global LAST_REASON
    COUNTS[tag]+=1
    if ':reject_no_eligible_order' in tag:LAST_REASON='NO_ELIGIBLE_ORDER_AFTER_CANONICAL_ROUTE_FILTER'
    elif ':skip_disowned_s_order' in tag:LAST_REASON='DISOWNED_S_ROUTE_SKIPPED'
def tap(tag, func, *args, **kwargs):
    COUNTS[tag]+=1
    return func(*args,**kwargs)
def save(path):
    import json
    from pathlib import Path
    Path(path).write_text(json.dumps({'coverage':'SELECTED_AST_LOOP_SORT_HEAP_AND_CACHE_OPERATIONS_ONLY',
                 'counts':dict(sorted(COUNTS.items()))},indent=2),encoding='utf8')
