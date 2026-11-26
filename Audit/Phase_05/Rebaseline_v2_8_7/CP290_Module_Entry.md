# CP290 / RB05 — Module composition rebaseline entry

Baseline: c99b4c957e932d9ee70c492ca03ce80711447fc1. Status: INCOMPLETE. Named declaration handoff CP289 passed; exact Bridge site linkage remains open for later owner review. This is a source-only module composition stage.

## Current corrections

The V3 reading registry previously described 579 named operation definitions and grouped the ten added Bridge functions into two procedure headings. Split those two into ten individual source-derived definitions, retaining TB103 for stage, TB104 for window constructor, adding TB105–TB112 for the other eight. Source anchors: engine/bridge/trading_pipeline.py:1759–1785,1791–1823. The declared current source inventory is 587 functions; uniqueness and total coverage of the full 23-document registry remain to be verified. Corrected obsolete final visibility signature recheck, closed-prefix reuse and live input-cache description in V3 registry. Current Bridge/T/F detailed module contracts are already revised in part and must be reconciled against current source, not assumed correct from labels.

## Next

Check all 23 V3 documents and their procedure headings against CP289 declarations; repair stale references, verify dependency ownership and module traceability; preserve historical evidence. No runtime/RAW tests, no source changes, no ZIP.
