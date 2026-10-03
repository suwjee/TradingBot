<!-- created_at: 2026-09-30T17:56:06+03:30 -->
<!-- last_modified_at: 2026-09-30T17:56:06+03:30 -->

# Architecture report

## Runtime path

1. `apps/chart/index.html:L15` loads the browser entry point, `src/main.js`.
2. `apps/chart/src/main.js:L5814-L5854` submits `/api/reactions`; it receives Engine JSON, stores response state, and renders. Progress uses `/api/reactions/progress` at `main.js:L5239`.
3. `apps/chart/vite.config.js:L234-L254,L558-L653` validates request scope and spawns `engine/bridge/trading_pipeline.py`. The bridge serializes results at `L3004-L3034`.
4. `apps/chart/server/faraz-candle-api.js:L414-L422,L1257-L1290` owns session-bound acquisition and history endpoints; the server shares the RAW store with Vite.

## Ownership

Engine calculates, Vite/server orchestrates and transports, FARAZ acquires data, and Chart presents Engine output. Browser filtering of `calculationValid === false` in `src/main.js:L2825-L2833,L5849` is a boundary review item, not a confirmed defect.

## Entry-point risk

A targeted `engine.pipeline` package import failed on a missing `run_blue_line` export. The bridge's flat import path is separate and was not tested end to end.
