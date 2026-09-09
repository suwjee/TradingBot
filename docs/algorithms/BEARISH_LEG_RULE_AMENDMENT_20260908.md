---
id: RULE-TRADINGBOT-BEARISH-LEG-AMENDMENT-20260908
type: correction
status: symmetric
direction: bearish
authority: user-approved-exact-mirror-2026-09-08
implementation_verification: full-xauusd-30s-logical-reflection-zero-differences
timezone: Asia/Tehran
---

# Bearish counterpart of the bullish leg amendment

This document mirrors the general semantics in
BULLISH_LEG_RULE_AMENDMENT_20260907.md after explicit user authorization.
The bullish historical corrections and 144-test result remain bullish evidence;
neither is copied into a bearish acceptance claim. Symmetric status records
completed full-XAUUSD 30-second logical reflection with zero differing fields.

1. Bearish S resolves canonical same-candle continuation after exact A stop in
   that continuation's own ordinary bullish Order Reaction context. Supply initial
   Order geometry and gate/confirmation finders directionally as in bullish.
2. Inherited bullish Order eligibility ends at its strict Low stop. A later
   confirmation cannot enter that parent's audit, even if it shares a main
   candle or an otherwise valid reset-leg cause.
3. A superseded Blue-E branch cannot seed a later Order ledger once an eligible
   later confirmed Red S owns the lifecycle. Keep red/blue names and priority.
4. A bearish A in a newly confirmed higher Reaction head can remain eligible
   when head precedes A, head.High > A.price, and head Reaction confirms before
   A source. Preserve owner consumption independently.
5. An invalid bearish head with an actual pending S owns its window until its
   exact High > head boundary stop. Bullish Firsts inside that live window
   cannot own resumed outer E space. Heads without pending S do not block.
6. Choose the dominant owner by the latest main candle containing its strict
   stop. Only then apply same-candle priority and sequence number. Old E
   sequence numbers cannot override newer lifecycles. An isolated range has
   no pre-range owner and may produce a different valid A.
7. Rejected A/S remain internal evidence only where required. Public labels,
   counts, lists, audit geometry, and downstream accepted parents cannot
   originate from rejected objects. Restore lineage only for actual accepted
   final children, following the reference closure rules.

All price inequalities mirror exactly; time bounds, strictness, source ownership,
family, cause merging, numbering, and nullability retain the reference semantics.
Market doji remains GREEN while the internal Reaction role is reflected.

## Verification contract

Only the user-selected XAUUSD data is acceptance authority. Verify logical
reflection of Bullish, not independent Bearish historical trading correctness.

Retain original bullish output and review expectations. Add bearish counterpart
tests using generated/reflected inputs and exact event/source assertions; do not
invent bearish historical equivalents for the bullish example times. Check E
audit as well as E zones, because equal visible zones can hide extra late orders.

Run integrated bridge, the user-selected full XAUUSD data, range isolation, and
split-source equivalence. Record the actual resulting pass/fail/skip evidence
in C:/Users/msadr/Desktop/NEW/verification/full_parity_evidence/.
The completed maintained-source full-file reflection has zero differences.
This is symmetry evidence, not independent Bearish trading validation.
