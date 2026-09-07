# TradingBot agent instructions

## Read order

Before changing behavior, read `AI-Directories/README.md`, then the linked
document for the owning area. The executable code and its focused tests are
authoritative; AI summaries are navigation and safety aids.

For any UI, interaction, responsive, accessibility, or visual change, also read
`AI-Directories/UI_UX_DESIGN_RULES.md` and the relevant existing stylesheet.

## Core invariants

- Python owns indicator calculations. Browser code consumes and renders the
  payload; it must not recreate Reaction, Blue, A, S, E, or StopAll logic.
- The maintained pipeline is `Reaction -> Blue Line -> A -> S -> E -> StopAll`.
- Use `Decimal(str(value))` for price decisions. Do not introduce float
  tolerances. A break/stop comparison is strict unless the authoritative code
  explicitly says otherwise.
- Runtime candle color is `Open <= Close => GREEN`; doji is GREEN.
- Use `Asia/Tehran` for local time rendering and validation.
- Preserve unrelated dirty working-tree changes. Never stage broadly.

## Required verification

- Python-only changes: compile affected files and run focused tests.
- Bridge/serialization changes: also exercise the corresponding bridge path.
- Frontend changes: run the focused Node tests and `npm run build` in
  `lightweight-charts` when the change can affect the production bundle.
- Performance work: follow `SPEED_CODING_RULES.md`; output equivalence is a
  correctness requirement, not an optional benchmark result.
