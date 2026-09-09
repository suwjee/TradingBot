---
id: RULE-TRADINGBOT-BEARISH-LEG-20260908
type: trading-rule
status: symmetric
direction: bearish
authority: user-approved-exact-mirror-2026-09-08
implementation_verification: full-xauusd-30s-logical-reflection-zero-differences
timezone: Asia/Tehran
---

# Bearish leg ownership: mirror of the verified bullish rule

This is the authorized directional counterpart of BULLISH_LEG_RULE_VERIFIED.md,
not a claim that its historical bullish review rows were observed in bearish
output. The user approved the mirror of formerly bullish-only rules on
2026-09-08. Symmetric status records full-XAUUSD 30-second reflection with zero
differing output fields. The source bullish behavior remains unchanged.

These rules govern ownership, validity, context, and lineage around the existing
Reaction -> Blue Line -> A -> S -> E -> StopAll formation rules.

1. A bearish leg contains at least one confirmed bearish Reaction. After its
   breakdown, the maximum High looking backward from and including FirstGreen
   identifies the head. A head does not require an A/S/E label. Preserve the
   reference's exact scan boundary and equal-extreme source choice.
2. Exact lower chronology owns stop and confirmation order. High > boundary
   stops a bearish behavior; equality never crosses. Time does not reverse.
3. When an internal behavior and larger owner stop in the same transition,
   the larger owner continues: StopAll > E red > S red > E blue > S blue > A.
   Colors name lifecycle families and are not swapped.
4. If a new head stops before pending internal S formation, abandon that S
   wait and resume the larger owner's E sequence.
5. An invalid bearish head with an actual pending S candidate owns its internal
   window until its exact strict High stop. Bullish Order Firsts opened while
   the head is live cannot own resumed outer E space. Selection resumes after
   head stop. Without an actual pending S, an invalid head blocks no unrelated
   Order.
6. An A inside a newly confirmed higher bearish Reaction head remains eligible
   when the head precedes A, head.High > A.price, and the head Reaction confirms
   before A source. Existing owner consumption still applies.
7. Inherited bullish Order eligibility ends at that Order's strict Low stop.
   A superseded Blue-E branch cannot seed a later ledger after an eligible
   later confirmed Red S owns the lifecycle.
8. Reject invalid A/S from public output and downstream geometry while retaining
   only the internal lifecycle evidence needed by subsequent ownership.
   calculationValid=false legacy objects cannot produce labels or counts.
9. A confirmed Red S has higher S-family priority than a stopped Blue S. When
   a Red S reaches its own source-extreme event after that Blue S stop, it
   remains a public S candidate; equal/lower-priority candidates retain the
   existing strict-stop consumption rule.

The amendment's chronological owner rule applies: first select the latest
stop-containing main candle, then resolve same-candle module/number priority.
A new independent selected raw range starts with empty state and can validly
differ from a full-file run at the same clock time.

## Evidence boundary

Only XAUUSD-based logical reflection of Bullish is acceptance authority.
There is no independent validated Bearish historical reference.

No timestamps or prices in the bullish review CSV are mirrored into asserted
bearish events here. General rules must produce the output; filenames, fixture
identity, hashes, prices, and historical verdicts cannot control runtime.

Verification must include the user-selected XAUUSD file, directional reflection
with full provenance, invalid-head pending/no-pending cases, inherited-order
deadlines, interior heads, chronological dominance, exact stops, equal levels,
and range isolation. Actual command/results belong in the completed verification
record. The completed full-file logical reflection comparison has zero
differences; it does not establish an independent Bearish historical reference.

See BEARISH_INDICATOR_ALGORITHM.md and
BEARISH_LEG_RULE_AMENDMENT_20260908.md for the complete contract.
