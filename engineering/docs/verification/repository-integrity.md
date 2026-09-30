---
title: TradingBot Repository Integrity Verification
document_role: procedure
lifecycle: maintained
owner: repository-integrity
created_at: 2026-09-30T15:00:00+03:30
last_modified_at: 2026-09-30T15:00:00+03:30
---

# TradingBot Repository Integrity Verification

## Purpose

This document defines how repository correctness is classified, protected and verified.

It answers:

> What belongs inside the repository, how is it classified, tracked, validated and protected from accidental corruption?

It does not define release content or trading correctness.

## Repository classification model

Classification is based on ownership and lifecycle, not filename.

Content categories include:

- maintained source;
- documentation;
- tests;
- generated output;
- verification evidence;
- archive/history;
- runtime/local state;
- temporary data.

A directory name alone does not determine authority.

## Git tracking rules

Actual Git state is authoritative.

Do not rely only on `.gitignore`.

An ignored path may already be tracked. A tracked path may still be historical, generated, or evidence material.

Verification must distinguish:

- tracked files;
- ignored files;
- untracked files;
- generated files;
- local runtime state.

## Generated files

Generated does not automatically mean:

- ignored;
- disposable;
- irrelevant.

Some generated outputs are valuable verification evidence or reproducible artifacts.

Classify before removal.

## Archive handling

Archive contains historical/reference material.

Rules:

- historical is not Current authority;
- do not silently delete historical evidence;
- do not link archive documents as current maintained guidance.

## Verification evidence

Verification artifacts prove previous observations only.

Important rule:

`old PASS != current PASS`

A previous report does not replace a current verification run.

## Duplicate detection

Search for:

- duplicated Source copies;
- stale documentation copies;
- extracted archives;
- outdated generated snapshots.

Do not delete automatically. Classify first.

## Source authority protection

Prevent:

- stale Source copies becoming authority;
- generated snapshots replacing live Source;
- archive material replacing Current files.

Current production Source remains the executable implementation authority.

## Cross-platform integrity

Verify:

- path casing;
- rename correctness;
- line ending rules;
- Windows/Linux compatibility.

Follow current `.gitattributes` policy.

## Production versus repository boundary

Repository content and production release content are separate concepts.

This document defines integrity boundaries only and does not duplicate release documentation.

## Validation checklist

Before completion verify:

- tracking rules are based on Git state;
- no fixed file counts are used;
- no fixed hashes are used as authority;
- no fixed versions are used as authority;
- archive is separated from Current guidance;
- generated output is separated from authority;
- production and repository boundaries remain clear;
- links and metadata are valid.

## Phase boundary

Repository integrity changes must not modify:

- Engine Source;
- Chart Source;
- Vite Source;
- FARAZ Source;
- Algorithm References;
- Plugin/Vault;
- RAW;
- tests.
