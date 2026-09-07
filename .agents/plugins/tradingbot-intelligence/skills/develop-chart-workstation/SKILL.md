---
name: develop-chart-workstation
description: Build, refactor, debug, or verify the TradingBot Lightweight Charts workstation, bridge integration, drawing tools, and payload rendering without duplicating indicator logic in JavaScript.
---

# Develop chart workstation

- Read root `AGENTS.md`, `AI-Directories/PROJECT_MAP.md`,
  `AI-Directories/UI_UX_DESIGN_RULES.md`, the package manifest, bridge, and
  affected components first.
- Python owns calculation. JavaScript renders returned objects and UI state.
- Keep rendered objects time/price anchored and display times in `Asia/Tehran`.
- Preserve bridge and serialization contracts; avoid recalculation for style-only
  changes.
- Run focused Node tests and `npm run build`; exercise a real bridge request if
  calculations or serialization changed.
