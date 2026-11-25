# LB — Live Bridge

Exact append lineage uses SHA-256 over RAW byte prefix; full append and delta support catch-up, strict source chronology, transactional bucket append and rollback; retry resets views after failure. Bucket append supports nondecreasing time but source lineage requires strictly increasing time. Trading stages replay in the public path. See [transport contract](23_Live_Transport_Contract.md) for explicit transport state transitions. Full transaction/worker integration is unverified.
