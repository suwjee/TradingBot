---
id: RULE-TRADINGBOT-BULLISH-LEG-AMENDMENT-20260907
type: correction
status: verified
direction: bullish
authority: user-lesson-2026-09-06-and-correction-2026-09-07
timezone: Asia/Tehran
---

# Bullish leg review amendment

This amendment supersedes conflicting statements in earlier working notes.
All persisted records remain English; the chat language is independent.

The user corrected `2026-08-18 22:55:00 S blue`: it is invalid. The review
CSV therefore records `False`, and final visibility must suppress that S.

The maintained implementation now contains seven narrow changes:

1. Bullish S can resolve a canonical same-candle continuation after the exact
   A stop in the continuation's own ordinary Reaction context.
2. Bullish inherited-order eligibility ends at the inherited order's strict
   stop; later confirmations do not enter that parent's audit.
3. A superseded Blue-E branch cannot seed a later order ledger after a later
   confirmed Red S owns the lifecycle.
4. A bullish A inside a newly confirmed lower Reaction head can remain valid
   when the head is before the A, `head.Low < A.price`, and the head Reaction
   confirms before the A source. Existing owner consumption is preserved.
5. An invalid bullish leg head that has an actual pending S candidate owns the
   internal window until its exact strict stop. Opposite-Reaction Firsts opened
   before that stop cannot own the resumed outer E space. A head without a
   pending S candidate does not block unrelated orders. This makes `06:01:30`
   invalid and selects `06:05:30` as the first eligible Order_B after the
   `05:41:30` head stops at `06:03:58`.
6. Bullish leg ownership selects the owner whose strict stop belongs to the
   latest main candle. Only stops in that same candle are resolved by module
   priority and sequence number. This prevents an older high-number E from
remaining dominant across later lifecycles. In the full-file run, the A
candidates at `2026-08-20 08:44:00`, `09:08:00`, and `10:25:30` are therefore
rejected, while `09:49:00 A` remains public. An isolated range beginning at
`08:08:00` has no prior owner and therefore calculates `08:44:00 A` as valid.
7. Rejected A/S candidates remain internal lifecycle evidence and are omitted
   from the public payload. The chart defensively removes legacy invalid
   objects, so they cannot create labels, counts, list entries, or order shapes.

The user confirmed that Order audit `16:38:00` and S blue `23:45:30` are also
correct calculated outputs. They are now durable positive rows in the review
CSV. The CSV defines the minimum required behaviors; additional outputs are
allowed when they arise from the unmodified general calculation rules.

The combined canonical-XAUUSD suite returns 144 passed and 0 failed, including
the independent-range physical-file equivalence regressions. The
`06:13:30 E1 blue` has parent S=`05:18:30`, orderFirst=`06:05:30`,
orderMode=`B`, cause=`reset-leg`, confirmation=`06:10:42`, Stop source
`06:02:30`, Stop=`4401.800`, and strict stop event=`06:30:56`. No
timestamp-specific production exception is used.

The user-confirmed `01:52:30 A` / `02:07:30 Order_B` / `02:10:30 S blue` /
`02:30:00 E1 blue` chain is already covered by exact parent, Stop source,
Stop level, cause, and chronology assertions. The user authorized the exact
Bearish counterpart on 2026-09-08; its completed full-XAUUSD verification
establishes logical symmetry, not independent Bearish historical validation.
