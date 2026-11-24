# V9 — measured complexity, CPU/RSS and paired timing interpretation

> **Scope:** V9 is instrumentation only. No production engine optimization was performed, and observed timing ratios compare the historical pinned Original to unchanged V8.1. All 7 RAWs 30s native both-direction output preserved.

## Selected-site AST work counters (not all interpreter instructions)

| 5s RAW rows | Original work sites | V8.1 work sites | Original 2N/N | V8.1 2N/N |
|---:|---:|---:|---:|---:|
| 100,000 | 777,242 | 478,889 | — | — |
| 250,000 | 4,323,363 | 2,590,779 | — | — |
| 500,000 | 25,232,015 | 14,611,797 | 5.836 | 5.640 |
| 1,000,000 | 103,463,583 | 58,967,847 | 4.100 | 4.036 |

These selected-site counters grow superlinearly on the supplied synthetic fixture. They establish a hotspot hypothesis, **not** a formal worst-case complexity classification and not a count of every Python operation.

## One-million-row, native, UNPROFILED ABBA benchmark

- Three alternating blocks; 12 full native direction=both calculations on one host.
- Median Original wall time: **451.202 s**.
- Median V8.1 wall time: **370.680 s**.
- Observed median Original/V8.1 ratio: **1.2172**.
- This does **not** constitute V9 speedup. Hardware/cold-warm cache differences still matter.

## Real full RAW, three repeated ABBA/BAAB blocks per dataset

| Dataset index | Original median wall (s) | V8.1 median wall (s) | Original/V8.1 ratio |
|---:|---:|---:|---:|
| 5 | 2.042 | 2.405 | 0.8490 |
| 2 | 2.089 | 1.758 | 1.1885 |
| 3 | 62.844 | 53.477 | 1.1752 |
| 6 | 74.732 | 79.942 | 0.9348 |

V8.1 was slower than original in two of the four sampled real datasets and faster in two. Therefore universal speedup claims are unsupported. The branch `refactor` retains V8.1 as performance reference and pinned Original as correctness oracle.

## Internal Trace coverage limitation

8/8 selected-site synthetic metering and stable-output verification **do not establish complete internal semantic trace**. Source AST audit identified 103 potentially state-mutating functions not directly watched; runtime call profiling on OIL 15,061 rows showed 81 invoked (Original 141,332 calls; V8.1 140,901). This is a heuristic audit, not proof of 103 actual semantic mutators. Full semantic coverage gate remains `INCOMPLETE`.