---
title: TradingBot Gemini Assistant Instructions & Navigation
document_role: reference
lifecycle: maintained
owner: gemini-assistant
created_at: 2026-10-28T19:00:00+03:30
last_modified_at: 2026-11-20T11:55:09+03:30
---

# TradingBot Gemini navigation

Start with the current [root operating contract](AGENTS.md). It defines task authorization, permitted scope, authority order, and verification. Use the [AI engineering workflow](engineering/docs/ai/engineering-workflow.md) for repository work and the [engineering documentation index](engineering/docs/README.md) to find the maintained owner of a behavior.

## Discover the live project

1. Locate the current checkout or the source package explicitly designated for the task. Inspect its state and preserve existing user work.
2. Identify the owning subsystem. Chart owns interaction and presentation, the local server owns orchestration, FARAZ owns acquisition, and the Engine owns trading calculation. [Technical Architecture](engineering/docs/architecture/technical-architecture.md)
3. For trading semantics, retrieve the configured TradingBot Intelligence Plugin and canonical Vault, then discover the current accepted directional References as directed by the root contract. Read the relevant runtime Source within the authorized scope to establish executable behavior.
4. If intended semantics disagree with executable behavior, record the precise difference and resolve it under the root authority model.
5. Discover live tests and runners. Report the checks that actually ran and the limits of their evidence. [Testing](engineering/docs/development/testing.md)

## External knowledge and historical artifacts

The standalone Knowledge Vault and Intelligence Plugin have their own configuration. Discover the installed runtime and tools from the current environment. Generated Gemini onboarding inventories and maps are historical navigation aids tied to the checkout they recorded. Treat claims from them as evidence and verify material facts with their current owners.

## Workstation and publication boundaries

Use the Chart state resolver for local files. Preserve RAW evidence and keep FARAZ session credentials out of Git, logs, and deliverables. [Local State](engineering/docs/operations/local-state.md)

Use the maintained Git Manager and release workflow when the current user explicitly authorizes publication. Verify the actual remote branch, tag, and release outcome. [Release Operations](scripts/git/README.md)
