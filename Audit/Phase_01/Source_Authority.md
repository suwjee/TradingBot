# Phase 01 — Source authority and governance

**Status:** VERIFIED for implementation-baseline selection. **Discovery:** 2026-11-26.

The user's explicit requirement takes precedence: the latest committed production source on `refs/heads/main` is the only implementation baseline for algorithm extraction. At discovery it resolves to `466eb875070f02cd0dbfb105033422bbe2fd8c70`. Read source from this immutable commit, not from mutable branch URLs, other branches, uploaded source packages, historical releases, an older ZIP or a higher apparent module version.

| Evidence class | Role |
|---|---|
| Explicit current user instruction | Main-first baseline, English documentation, no project source in algorithm |
| Current main root AGENTS.md | Governing procedure and distinction between actual and intended behavior |
| Current main GPT_bot/AGENTS.md and Operating Protocol | Subordinate portable workflow companions |
| Current main production Bridge/Pipeline | Authoritative executable behavior for this reconstruction |
| Current main accepted Bullish/Bearish and primary/T-F references | Supplemental intended semantics and synchronized evidence; never substitute embedded source for the directly discovered current source |
| Current tests, RAW, approved regression anchors and configuration | Verification evidence; not invented trading rules |
| Golden archive, older releases, historical reports, uploaded guidance, prior AI output | Historical evidence only |

Root governance separately identifies TradingBot Intelligence and the canonical Knowledge Vault as intended-semantic sources. No direct TradingBot Intelligence/Vault connector was exposed during discovery. This is disclosed, not filled by inference. The explicit main-first requirement still fixes actual implementation unambiguously; potential intended-semantic discrepancies must be recorded and not silently resolved. No rule was changed.

## Main governance documents inspected

- `AGENTS.md` (Git blob cb9b8c178a998600bd900d01f207d782cc7aa862)
- `GPT_bot/AGENTS.md` (db89d35b9832f42a94dcb24af54d900925af92ee)
- `GPT_bot/TradingBot_AI_Operating_Protocol.md` (3ae9627ebca06c8976ad1ee9ff623d8a57b2e796)
- `GEMINI.md`, `README.md`, `.gitignore`, `.gitattributes`, maintained engineering documentation index, documentation governance, testing, reference maintenance, architecture, local state, Chart package manifest and current anti-drift workflow. The full texts of the three governing documents were retrieved; the authority, discovery, verification and ownership clauses were reviewed for this phase. Inventory identities are in Repository_Discovery.json.

The user-uploaded AGENTS.md and Operating Protocol are not byte-identical to the current main documents. They are not selected as governing source. See Conflicts_Register.md.

## Baseline change control

Before every subsequent phase, resolve main again. If its head changes, pin the new head, compare all production, reference, test and relevant configuration blobs, and document affected specifications and evidence before proceeding. A change of commit with identical production blobs still requires checking changed governance and tests. Never blend source snapshots silently. Keep old verification records append-only and label their tested commit. The older Golden oracle remains a fixed historical optimization-regression anchor; main is the actual implementation source for this task.

No source or executable test code is stored in the algorithm branch. Reference to a source path or digest in Audit is metadata only.
