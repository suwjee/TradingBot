# CU — Core utilities

```text
AS_DECIMAL(x):
  IF x is Decimal: RETURN x
  RETURN Decimal(string(x))
ORDER_IDENTITY(first, break): RETURN (integer(first), integer(break))
REACTION_IDENTITY(r): RETURN ORDER_IDENTITY(r.first_idx, r.break_idx)
ORDERED_NAIVE_DATETIMES(values):
  RETURN all exact datetime instances with null timezone AND nondecreasing
CONTAINMENT(intervals, query_start, query_end):
  FOR (start,end,payload) IN original input order:
    IF start < query_start AND end >= query_end: YIELD payload
```
An equivalent index partitions inputs into chronological runs whenever either start or end decreases. Within each run find stop=lower_bound(starts, query_start), first=lower_bound(ends,query_end,0,stop); yield payload[first:stop]. Build O(n), space O(n); a sorted run queries O(log n + k). Identity is physical First/Break, with direction owned by context. Containment was compared against the pinned oracle for 1,200 synthetic cases; ordered-naive/Decimal comparisons were also tested.
