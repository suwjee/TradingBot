# Directional mirror matrix

### 13.6 Master Bullish ↔ Bearish directional mirror matrix

This matrix governs upstream directional transformation. Section 13.4b separately defines the explicitly approved primary mirror and fresh directional regime contract. This matrix is normative for the upstream directional transformation. Bullish is the canonical geometry; Bearish is derived mechanically. A row marked **directional** must transform exactly as shown. A concept listed in Section 13.7 is invariant and must not be direction-flipped.

| Rule / primitive | Bullish | Bearish | Classification |
|---|---|---|---|
| Direction name | `bullish` | `bearish` | directional |
| Directional extreme field | `Low` / `low` | `High` / `high` | directional |
| Opposite extreme field | `High` / `high` | `Low` / `low` | directional |
| Better directional extreme | lower (`<`) | higher (`>`) | directional |
| Directional aggregate | `minimum` / `min` | `maximum` / `max` | directional |
| First Reaction role | `FirstRed` / `RED` | `FirstGreen` / `GREEN` | directional |
| Pre-First context role | `GREEN` | `RED` | directional |
| Reaction confirmation | first strict `High > BoxTop` | first strict `Low < BoxBottom` | directional |
| Reaction confirmation edge | `BoxTop` | `BoxBottom` | directional |
| Opposite evolving box edge | `BoxBottom` | `BoxTop` | directional |
| Reaction Reset | first strict `Low < confirmed BoxBottom` | first strict `High > confirmed BoxTop` | directional |
| Blue Fibonacci level | `BoxTop − 0.618 × (BoxTop − reference)` | `BoxBottom + 0.618 × (reference − BoxBottom)` | directional |
| New Scale strike | strictly lower `Low` | strictly higher `High` | directional |
| Scale-strike confirmation color | `GREEN` | `RED` | directional |
| Scale Blue source extreme | decisive `Low` | decisive `High` | directional |
| Scale Blue line price | `Low + (High − Low) / 3` | `High − (High − Low) / 3` | directional |
| Reset Blue source extreme | Reset-candle `Low` | Reset-candle `High` | directional |
| Reset Blue line price | `Low + (High − Low) / 5` | `High − (High − Low) / 5` | directional |
| Blue strict stop | first directional `Low < source_extreme` | first directional `High > source_extreme` | directional |
| Ordinary A source selection | minimum `Low` | maximum `High` | directional |
| A frozen source after trigger | minimum `Low` through exact confirmation | maximum `High` through exact confirmation | directional |
| A strict stop | directional strict lower penetration | directional strict upper penetration | directional |
| S Type-3 source | minimum `Low`, last owner on equality | maximum `High`, last owner on equality | directional |
| S Type-4 source | minimum `Low`, last owner on equality | maximum `High`, last owner on equality | directional |
| S Blue candidate crossing | strict lower directional cross | strict upper directional cross | directional |
| Physical opposite Order direction used by current behavior | Bearish Reaction/Order | Bullish Reaction/Order | directional |
| Physical Order strict stop in current calculation | `High > OrderStop` | `Low < OrderStop` | directional |
| S Red race event | physical Order `High > OrderStop` | physical Order `Low < OrderStop` | directional |
| E parent/behavior strict stop | lower directional penetration | upper directional penetration | directional |
| Armed S/E owner strict stop | first lower-TF `Low < owner price` | first lower-TF `High > owner price` | directional |
| Direct E-child donor | exact owner identity and parent-stop provenance | exact owner identity and parent-stop provenance | invariant |
| E source | minimum `Low` across complete boundary candles | maximum `High` across complete boundary candles | directional |
| Order_B reset Reaction role | Bullish reset Reaction / `FirstRed` | Bearish reset Reaction / `FirstGreen` | directional |
| Order_B frozen boundary | `LL = minimum Low(...)` | `HH = maximum High(...)` | directional |
| Order_B anchor extension | `LL < anchor Low` | `HH > anchor High` | directional |
| Order_B strict break after Reset | first calculation candle containing post-Reset `Low < LL` | first calculation candle containing post-Reset `High > HH` | directional |
| Order_B canonical opposite Reaction | first canonical Bearish Reaction | first canonical Bullish Reaction | directional |
| DirectionPolicy `strict_cross` | `<` | `>` | directional |
| DirectionPolicy `better_extreme` | `<` | `>` | directional |
| DirectionPolicy `choose_extreme` | `min` | `max` | directional |
| DirectionPolicy `confirmation_cross` | `>` | `<` | directional |
| Reaction mechanical reflection used internally | `O,H,L,C` canonical coordinates | `O'=-O, H'=-L, L'=-H, C'=-C` plus role reflection | implementation mirror |

All strict rows remain strict. Equality is not converted into a crossing in either direction.

### 13.7 Direction-invariant contract matrix

The following semantics are intentionally identical in Bullish and Bearish. Mirroring any of these merely because price direction changes is an error.

| Invariant | Exact contract |
|---|---|
| Time / chronology | configured calculation-timeframe ownership is invariant; lower-TF chronology is used only for explicitly required within-candle ordering/provenance and is not mirrored |
| Doji | `close == open` is always `GREEN` |
| Decimal | price-sensitive decisions use Decimal semantics; direction does not change numeric representation |
| Strict equality | equality never satisfies a strict crossing |
| Exact StopAll owner | one exact S/E identity; count `1` is highest but unarmed; count `>=2` arms the latest occurrence |
| Replacement and chronology | unrelated higher formation disarms lower future eligibility; a completed earlier strict stop remains valid |
| Retrospective E source | exact direct child may reuse its matched parent stop; independent accepted E may donate the current armed owner stop only in its own source candle with strict source extreme, before E decision; later-bucket stop ineligible |
| Physical identity | canonical Reaction/Order identity is `(FirstIndex, BreakIndex)` |
| Provenance concepts | `parent-stop`, `reset-leg`, `carried-live`, `accepted-live` retain the same meanings |
| Stage ownership | Reaction, Blue, A, S, E, OrderAudit, Lifecycle/StopAll owners remain the same modules |
| Behavior-family names | `S Blue`, `S Red`, `E Blue`, `E Red`, and `StopAll` names are not color-swapped |
| S/E dominance priority | `S Blue < E Blue < S Red < E Red`; A is excluded and StopAll is a boundary |
| Numbering | Reaction, E and StopAll numbering rules remain structurally identical |
| Stable ordering | deterministic tie keys retain the same semantic ordering contract |
| Public/internal meaning | visibility/internal-state semantics do not reverse with market direction |
| Serialization schema | public field names and response shape are identical across directions |
| Hard StopAll boundary | historical boundary/reset semantics are identical |
| Calculation vs presentation | internal historical evidence may survive even when not public |
| Canonical membership | geometry-only evidence cannot become a physical canonical Order in either direction |
| Invalid S parentage | an explicitly invalid S cannot create/retain `parent-stop` cause in either direction |
| Order cause merge | multiple causes may attach to one physical identity without duplicating the Order |
| E same-source priority | Red E outranks Blue E; within family, higher number wins; remaining exact ties preserve earlier accepted object |
| S Type-3/Type-4 tie | earlier exact decision event wins; Type-3 owns only a true exact-event tie |
| S decision same-position race | exact same lower-TF position for Order stop and candidate cross produces no S decision |
