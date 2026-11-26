# CP381 — S Order-backed construction

Pinned source: `53460e68538ac790ab969084c1c7101e5ca833d7`; B04-07 1054–1224. 326 category rows, 69 W1, 257 additional, 6 supplements; 2887 prior rows revalidated without overlap.

### W3 CP381 — Order-backed Simple/Advanced construction (S39)

- **S39 (1054–1064)**: Receive and unpack exact caller A stop and first supplied Order match; no second canonical Order lookup.
- **S39 (1065–1079)**: Resolve canonical Order stop triple first through mixin provider, then S29 timing. S30 called only if timing before; failure propagates before decision initialization.
- **S39 (1081–1092)**: Initialize behavior start at A stop, decision None, use_pre False. Pre candidate selects simple source/red reference and trend ordinal zero. S31 returned candidate time becomes behavior start and candidate gate.
- **S39 (1093–1107)**: Preliminary S37 race begins at Order confirmation with fallback flag true. None exits entire route; nonfallback sets use_pre; fallback clears decision but retains pre candidate. No unconditional second attempt.
- **S39 (1109–1116)**: If not use_pre reset behavior start to exact A-stop and call S16 again, even if timing previously queried. Advanced flag only nonnull nested match.
- **S39 (1117–1131)**: Advanced branch uses Order bottom source bullish or top source otherwise. Normalize full main trend extreme, not raw box edge; nested confirmation becomes gate, red_source None.
- **S39 (1132–1144)**: Non-pre, nonadvanced simple branch uses S15 first qualifying trend match; None exits. S17 inclusive last-equal main candidate geometry.
- **S39 (1145–1153)**: Evaluate red_source pre candidate if present else S24 post-order candidate even though later non-pre Red ignores it. Preserve native call/exception effects; gate aligned confirmation.
- **S39 (1154–1165)**: Only absent decision invokes S37 normal mode default fallback false. If None exit. No repeated race for retained pre decision.
- **S39 (1166–1174)**: Unpack color, decision position/main/event; convert Order Break even on Blue. Red uses pre source only when use_pre and red_source nonnull; otherwise S13 first-equal inclusive Break..decision. Blue retains prior selected source.
- **S39 (1176–1189)**: Convert First, top source, bottom source in order, then construct SZone; parent A source int/time, original supplied price and stop triple.
- **S39 (1190–1206)**: Preserve original Order direction/number and mode str, First/Break main times, supplied confirmation and normalized top plus source provenance in argument order.
- **S39 (1207–1216)**: Normalize bottom and its source time, carry canonical stop level/index/time; Reset fields null. No replacement Order or second stop proof.
- **S39 (1217–1224)**: Return selected source/price and separate decision main/index/event; frozen record not accepted ledger or lifecycle assertion.

Canonical Order stop is delegated to the provider, not independently recreated by S39. Supplied physical identity and accepted lifecycle remain independent cross-owner obligations.
