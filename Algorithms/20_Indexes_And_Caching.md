# Indexes and caching

Preserve chronological order and tie behavior. Lower range min/max and first strict crossing queries must return the same selected index and Decimal representation as a direct scan. Containment preserves input runs. Main range extrema and candidate heaps must use their path-specific ties. Invalidate changed-tail dependencies; do not assume caching is behavior neutral without equivalence evidence. Exact contracts are distributed through CU, RX and Live. Full cache invalidation paths and complexity measurements remain incomplete.
