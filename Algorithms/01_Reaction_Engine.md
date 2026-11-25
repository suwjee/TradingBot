# RX — Reaction engine

Status: DOCUMENTED / PARTIALLY_VERIFIED package; this module is not independently validated end to end.

Inputs: normalized main candles, lower-timeframe chronology and current direction. Outputs: canonical Reaction/Reset records with physical First/Break identity, native geometry, source and event times. Mode A is a leg-start reaction with fixed anchor boundary and evolving opposite edge; Mode B uses a running extreme. Confirmation is strict. Before confirmation, invalidation/reset no later than the breakout wins; a confirmed reaction can reset in the remaining same main candle only at a later eligible exact event. Public box clipping is distinct from native order geometry. Bearish initial geometry can reflect (-O,-L,-H,-C), but native Doji remains GREEN. The Mode A canonical Order stop considers context from anchor or First-1 back through context, then the extreme through Break inclusive; Mode B uses the preceding healthy same-direction physical Reaction semantic outer edge. Equal eligible extremes retain the earliest owner. Lower-index min/max and first-crossing queries use exact boundaries. Full branch state tables, helper details and continuation contracts are still incomplete.

```text
FOR each eligible chronological candidate:
  maintain candidate geometry using its mode-specific rules
  resolve strict confirmation and invalidation/reset in lower chronology
  IF reset/invalidation precedes or ties confirmation: invalidate or reset
  ELSE IF confirmation exists: publish canonical physical reaction
    search remaining eligible chronology for strictly later reset
```
This pseudocode is a high-level state outline; the detailed supplemental contracts specify the gates. It is not a complete executable state machine.

## Supplemental directional specification

Supplementary material below is the English semantic prose of the existing synchronized references, pinned to 466eb875070f02cd0dbfb105033422bbe2fd8c70. It is not a fresh branch-level proof. Exact production-source appendices are excluded. Historical acceptance examples remain historical.

## 4. Reaction / Reset — ACTIVE Bullish specification

### 4.1 Data and color contract

`Candle` carries `index`, native `timestamp`, display time, immutable market `tag`, and Decimal OHLC. `Candidate` carries First/box sources, Mode A/B, optional anchor and leg boundary, Break, intrabar start, cross-direction gate metadata, public box/number metadata and internal/public ownership flags. `ResetEvent` records main index/time, optional exact lower-TF second, broken level, and the owning Reaction First index.

### 4.2 Canonical directional geometry

For Bullish, the canonical First candle role is **FirstRed** (`RED`) following the opposite context color `GREEN`. Confirmation is the first strict breakout satisfying `High > BoxTop`. The confirmation edge is `BoxTop`. The opposite box edge `BoxBottom` may evolve only through chronology available up to the exact confirmation event.

The source does not maintain an independent hand-written Bearish state machine: Bearish geometry executes the Bullish reference state machine through exact Decimal sign/High-Low/color-role reflection. Therefore the initial leg, Mode-A invalidation, breakout/breakdown priority, Reset priority, post-confirmation handling, and lower-timeframe tie rules share one mechanical geometry contract. The reflected color role is internal coordinate machinery only; market Doji remains GREEN.

### 4.3 Mode A / leg-start ownership

Mode A is the first Reaction of a leg. The detector establishes the contiguous context run, builds the directional First candidate, preserves any qualifying adjacent anchor, and freezes the outer leg boundary. Before confirmation, strict outer-boundary invalidation owns the candidate ahead of confirmation when lower-TF chronology proves it first. In the standalone initial Mode-A WAITING state, an invalidated owner releases search and nested geometry cannot confirm while its selected structural owner remains unresolved. The bounded Unified post-Reset search has the separate completion-selection contract in Section 4.7.

### 4.4 Mode B / normal ownership

After a confirmed Reaction, normal search uses the running directional context and the required First color. A confirmation main candle may itself seed the next Mode-B First only when the post-confirmation remainder does not first Reset the just-confirmed structure. The confirmation candle can be the next First when its market color has the required role. First check strictly later RAW within that same candle for an immediate Reset against the confirmed opposite edge. A strict Reset there disqualifies reuse. With no such Reset and with RAW rows available, use the entire confirmation candle from its main open through its exclusive end to build the successor box. BoxTop is its maximum RAW High and BoxBottom is its minimum RAW Low, with the earliest RAW occurrence on equality. Both edge source indexes and times name the main candle. Mode B starts its intrabar search at that main open. The full-candle geometry rule and the later-only Reset check apply after the initial and later confirmed Reactions in both directions.

This handoff applies identically to the **initial confirmed Reaction** and to every later confirmed Reaction. Initial-confirmation status is not a reason to discard an otherwise eligible same-candle continuation; a same-remainder Reset still owns precedence exactly as before.

### 4.5 Exact confirmation and published box

If the Break main candle owns the full-main-candle opposite extreme, only lower-TF prices at or before the first strict confirmation may define the published opposite edge. Later prices in that same main candle cannot retroactively alter Reaction/Order geometry. If lower-TF chronology cannot prove a refinement, detector geometry is retained rather than guessed. Equal eligible extremes retain the earliest main-candle owner.

### 4.6 Reset

A confirmed Bullish Reaction resets only on the first strict `Low < confirmed BoxBottom` event. Equality is not Reset. When Reset and confirmation/break activity share a main candle, selected lower-TF ordering decides which event owns the state transition. Reset reopens **same-direction** Reaction ownership; opposite-direction patterns do not gate that search. A Reset event with an exact lower-TF second exposes that exact second; otherwise the owning main-candle start is the fallback representation.

### 4.7 Post-Reset structural owner vs geometry-only evidence

After Reset, `_first_direct_same_direction_after_reset` scans eligible First candidates in chronological First-index order within the configured end index. It returns a candidate only if confirmation wins before strict loss of its frozen owning boundary. If invalidation wins first, candidates with First indexes at or before that invalidation main index are blocked. A candidate unfinished at the bounded end is skipped, so a later eligible candidate that completes healthily may be returned. The standalone initial Mode-A WAITING state retains its selected unfinished structural owner. The returned healthy result joins the canonical same-direction Reaction stream. `_first_geometry_after_reset` separately returns complete geometry without lifecycle acceptance; generic geometry alone cannot create Order_A. An unfinished or invalidated bounded geometry alone cannot create Order_A. The **special complete post-A-stop physical Order_A** is an explicit exception: it is independently confirmed, after the parent stop, and recorded by S OrderAudit without appending a new public canonical Reaction.

### 4.8 Internal Reaction ownership

Cross-direction internal protection is determined after both directions exist. A candidate is internal only when its temporal/box structure is contained by a healthy opposite Reaction and the complete lower-timeframe physical path through its confirmation remains inside the protecting box. Internal identity affects behavior/public ownership; it does not delete historical calculation evidence or renumber the canonical Reaction stream.

## 4. Reaction / Reset — ACTIVE Bearish specification

### 4.1 Data and color contract

`Candle` carries `index`, native `timestamp`, display time, immutable market `tag`, and Decimal OHLC. `Candidate` carries First/box sources, Mode A/B, optional anchor and leg boundary, Break, intrabar start, cross-direction gate metadata, public box/number metadata and internal/public ownership flags. `ResetEvent` records main index/time, optional exact lower-TF second, broken level, and the owning Reaction First index.

### 4.2 Canonical directional geometry

For Bearish, the canonical First candle role is **FirstGreen** (`GREEN`) following the opposite context color `RED`. Confirmation is the first strict breakdown satisfying `Low < BoxBottom`. The confirmation edge is `BoxBottom`. The opposite box edge `BoxTop` may evolve only through chronology available up to the exact confirmation event.

The source does not maintain an independent hand-written Bearish state machine: Bearish geometry executes the Bullish reference state machine through exact Decimal sign/High-Low/color-role reflection. Therefore the initial leg, Mode-A invalidation, breakout/breakdown priority, Reset priority, post-confirmation handling, and lower-timeframe tie rules share one mechanical geometry contract. The reflected color role is internal coordinate machinery only; market Doji remains GREEN.

### 4.3 Mode A / leg-start ownership

Mode A is the first Reaction of a leg. The detector establishes the contiguous context run, builds the directional First candidate, preserves any qualifying adjacent anchor, and freezes the outer leg boundary. Before confirmation, strict outer-boundary invalidation owns the candidate ahead of confirmation when lower-TF chronology proves it first. In the standalone initial Mode-A WAITING state, an invalidated owner releases search and nested geometry cannot confirm while its selected structural owner remains unresolved. The bounded Unified post-Reset search has the separate completion-selection contract in Section 4.7.

### 4.4 Mode B / normal ownership

After a confirmed Reaction, normal search uses the running directional context and the required First color. A confirmation main candle may itself seed the next Mode-B First only when the post-confirmation remainder does not first Reset the just-confirmed structure. The confirmation candle can be the next First when its market color has the required role. First check strictly later RAW within that same candle for an immediate Reset against the confirmed opposite edge. A strict Reset there disqualifies reuse. With no such Reset and with RAW rows available, use the entire confirmation candle from its main open through its exclusive end to build the successor box. BoxTop is its maximum RAW High and BoxBottom is its minimum RAW Low, with the earliest RAW occurrence on equality. Both edge source indexes and times name the main candle. Mode B starts its intrabar search at that main open. The full-candle geometry rule and the later-only Reset check apply after the initial and later confirmed Reactions in both directions.

This handoff applies identically to the **initial confirmed Reaction** and to every later confirmed Reaction. Initial-confirmation status is not a reason to discard an otherwise eligible same-candle continuation; a same-remainder Reset still owns precedence exactly as before.

### 4.5 Exact confirmation and published box

If the Break main candle owns the full-main-candle opposite extreme, only lower-TF prices at or before the first strict confirmation may define the published opposite edge. Later prices in that same main candle cannot retroactively alter Reaction/Order geometry. If lower-TF chronology cannot prove a refinement, detector geometry is retained rather than guessed. Equal eligible extremes retain the earliest main-candle owner.

### 4.6 Reset

A confirmed Bearish Reaction resets only on the first strict `High > confirmed BoxTop` event. Equality is not Reset. When Reset and confirmation/break activity share a main candle, selected lower-TF ordering decides which event owns the state transition. Reset reopens **same-direction** Reaction ownership; opposite-direction patterns do not gate that search. A Reset event with an exact lower-TF second exposes that exact second; otherwise the owning main-candle start is the fallback representation.

### 4.7 Post-Reset structural owner vs geometry-only evidence

After Reset, `_first_direct_same_direction_after_reset` scans eligible First candidates in chronological First-index order within the configured end index. It returns a candidate only if confirmation wins before strict loss of its frozen owning boundary. If invalidation wins first, candidates with First indexes at or before that invalidation main index are blocked. A candidate unfinished at the bounded end is skipped, so a later eligible candidate that completes healthily may be returned. The standalone initial Mode-A WAITING state retains its selected unfinished structural owner. The returned healthy result joins the canonical same-direction Reaction stream. `_first_geometry_after_reset` separately returns complete geometry without lifecycle acceptance; generic geometry alone cannot create Order_A. An unfinished or invalidated bounded geometry alone cannot create Order_A. The **special complete post-A-stop physical Order_A** is an explicit exception: it is independently confirmed, after the parent stop, and recorded by S OrderAudit without appending a new public canonical Reaction.

### 4.8 Internal Reaction ownership

Cross-direction internal protection is determined after both directions exist. A candidate is internal only when its temporal/box structure is contained by a healthy opposite Reaction and the complete lower-timeframe physical path through its confirmation remains inside the protecting box. Internal identity affects behavior/public ownership; it does not delete historical calculation evidence or renumber the canonical Reaction stream.
