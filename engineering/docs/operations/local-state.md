---
title: TradingBot Local Operational State
document_role: reference
lifecycle: maintained
owner: local-state
created_at: 2026-09-30T15:00:00+03:30
last_modified_at: 2026-09-30T15:00:00+03:30
---

# TradingBot Local Operational State

## Purpose

This document defines ownership and lifecycle rules for local operational state.
It answers:

> What local data exists during development/runtime, who owns it, how persistent is it, and how can it be handled safely?

This document does not define UI behavior, trading semantics, release policy, or repository integrity rules.

## State classification

Local state must be classified by ownership and lifecycle, not by filename.

Common categories discovered from the current project may include:

- runtime state;
- user workspace state;
- session/authentication state;
- cache;
- temporary files;
- generated local output;
- logs;
- RAW market evidence;
- verification artifacts.

New categories must be evaluated from the owning component.

## Ownership model

Every local state item must have an identified:

- owner component;
- lifecycle;
- persistence level;
- rebuildability status;
- cleanup safety rule.

Examples:

- Chart workspace state owns user layout, drawing and preference persistence.
- FARAZ integration owns authentication/session state handling.
- Vite/runtime tooling owns development runtime artifacts.
- Engine temporary calculations own short-lived calculation data.

Memory state and persistent local state are different concepts.

## Secrets

Secrets must never be stored in:

- Git;
- documentation;
- tests;
- fixtures;
- logs;
- reports.

Never expose passwords, tokens, cookies, API keys or credentials. Document handling rules only.

## FARAZ and authentication state

Authentication/session data is operational state owned by the integration layer.

Documentation may describe:

- ownership;
- persistence model;
- lifecycle;
- invalidation/recovery rules.

Actual secret values must never be documented.

## Chart workspace state

Workspace persistence belongs to the Chart/UI state owner.

Examples of owned concepts:

- drawings;
- layouts;
- preferences;
- user workspace persistence.

This document does not duplicate UI/UX interaction contracts.

## RAW data policy

RAW market data is immutable evidence.

Rules:

- never modify RAW to make tests pass;
- never automatically delete RAW;
- do not treat RAW as cache;
- discover current RAW locations dynamically when required.

A RAW filename inventory is not maintained here because repository structure evolves.

## Cache policy

Caches are classified individually.

Before deletion determine:

- owner;
- rebuildability;
- invalidation requirements;
- evidence value;
- tracking state.

A cache name does not prove that deletion is safe.

## Cleanup policy

Before deleting local state:

1. identify owner;
2. determine lifecycle;
3. determine rebuildability;
4. determine evidence value;
5. inspect Git tracking status;
6. confirm no recovery or audit purpose exists.

No automatic deletion rule may be based only on filename, extension, or directory name.

## Relationship with repository integrity

Local state explains operational ownership.
Repository Integrity explains classification, tracking and protection boundaries.
They must remain separate responsibilities.
