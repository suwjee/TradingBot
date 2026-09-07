# TradingBot UI/UX design rules

## Purpose and authority

This document preserves the existing visual language of the QG Chart
Workstation. Use it for every new screen, panel, control, modal, chart overlay,
or responsive change. The current implementation remains the final visual
authority, especially:

- `lightweight-charts/src/styles/tokens.css` for design tokens;
- `lightweight-charts/src/styles/app.css` and `candle-export.css` for component
  behavior and breakpoints;
- `lightweight-charts/src/main.js` for component semantics and interaction;
- the maintained UI tests for observable behavior.

When this document disagrees with the maintained UI, preserve the maintained UI
and update this document in the same change.

## Product character

The product is a dense, professional, desktop-first trading workstation—not a
marketing site. The visual character is quiet, precise, lightweight, and
data-first:

- bright neutral canvas and white work surfaces;
- restrained blue only for primary selection, focus, and affirmative actions;
- green/red only for market direction, success, or destructive states;
- thin borders, compact spacing, modest radius, and very limited decoration;
- the chart and its data are visually dominant; controls are supporting tools.

Do not introduce glassmorphism, gradients, oversized cards, playful
illustrations, decorative emoji, neon effects, or unrelated design systems.

## Tokens are mandatory

Use existing `--ui-*` and `--chart-*` tokens. Do not add raw color, spacing,
radius, shadow, z-index, or motion values inside new components unless a new
semantic token is first added to `tokens.css` and reused.

| Concern | Existing system |
|---|---|
| Canvas / surface | `--ui-bg-canvas`, `--ui-bg-surface`, `--ui-bg-subtle` |
| Text | `--ui-text-primary`, `--ui-text-secondary`, `--ui-text-muted` |
| Borders | `--ui-border-subtle`, `--ui-border`, `--ui-border-strong` |
| Primary action / selection | `--ui-accent`, hover, active, and soft variants |
| Semantic feedback | `--ui-positive`, `--ui-negative`, `--ui-warning`, `--ui-danger` and soft variants |
| Layout | `--ui-topbar-height` (44px), `--ui-rail-width` (44px), `--ui-shell-gap` (4px) |
| Control density | `--ui-control-sm` (26px), `md` (30px), `lg` (32px) |
| Shape / elevation | `--ui-radius-xs` through `lg`; existing shadow tokens only |
| Layers | named `--ui-z-*` levels; never arbitrary z-index escalation |

The compatibility aliases at the end of `tokens.css` are legacy support; new
work should prefer the `--ui-*` names.

## Typography and icons

- Use Inter for UI text and JetBrains Mono (or `--ui-font-mono`) only for
  timestamps, prices, data values, and code-like identifiers.
- Preserve the compact hierarchy: controls at 10–13px, labels/body at 12–13px,
  panel headings at 15–17px. Do not add large display typography.
- Use the existing Material Symbols icon set through the project helper. Every
  icon-only action needs an accessible name and an existing tooltip pattern.
- Use text plus an icon for unfamiliar or consequential actions. Color alone
  must never carry a state or trading meaning.

## Layout and component patterns

- Preserve the workstation shell: compact top bar, 44px tool rail, chart-first
  center area, and contextual side panels/popovers rather than permanent large
  cards.
- Reuse existing control classes/patterns (`.btn`, `.control`, `.icon-btn`,
  `.tf`, settings panels, picker cards, toast) before inventing new variants.
- New panels use white/subtle surfaces, thin borders, existing radius tokens,
  modest elevation, a clear title, and scrollable body content. Do not put
  horizontal scrolling inside a panel merely to preserve desktop layout.
- Place destructive actions apart from primary actions and use the existing
  danger token. Require confirmation for irreversible actions.
- Keep chart overlays anchored to candle time and price; never to viewport
  pixels. Chart UI must not obscure price/axis information unnecessarily.

## Interaction, states, and feedback

Every interactive control must have default, hover, active/selected, keyboard
focus, disabled, and busy/error behavior where relevant. Follow the existing
100ms/160ms motion tokens and standard easing; motion is feedback, not
decoration. `prefers-reduced-motion` must keep working.

- Use semantic `<button>`, `<input>`, `<select>`, and `<label>` elements where
  possible; do not replace them with clickable `div`s.
- Keep tab order aligned with visual order. A visible focus indicator is
  required for all keyboard-operable controls, including controls in dialogs,
  menus, and panels.
- Do not hide keyboard focus under a sticky bar, chart overlay, or panel.
- Compact desktop controls may remain 26–32px to retain workstation density,
  but their rail/menu hit region must be at least 44px where practical. On
  touch layouts, provide 44px target areas or sufficient spacing to avoid
  accidental activation.
- Never make hover the only way to reveal an action or state. Use tooltips as
  supplementary explanation, not as the sole accessible label.
- Use existing toast and inline feedback patterns for success, blocked actions,
  loading, and errors. Do not silently fail or use `alert()`.

## Responsive and fullscreen behavior

The maintained breakpoints are approximately 1180px (panel pressure), 900px
(compact chart header), 760px (mobile rail/panel layout), 520px, and 440px.
Use these first; add a breakpoint only for a demonstrated layout failure.

- On narrower screens, reflow and collapse secondary controls before hiding a
  primary action or the chart state.
- Preserve the current mobile header pan and touch-safe drawing access. Avoid
  fixed-width layouts or horizontal viewport overflow.
- Preserve fullscreen behavior: chart stays the primary surface and nonessential
  chrome yields to it without breaking focus, escape, or restoration behavior.

## Accessibility and data visualization

- Maintain text/background contrast of at least 4.5:1 for normal text. Do not
  weaken existing focus, disabled, or semantic contrast without testing it.
- Associate visible labels with inputs. Error text belongs near its field and
  must state the corrective action.
- Give icon-only buttons `aria-label`; use `aria-pressed`/selected semantics for
  toggles and timeframe chips when their visual state changes.
- Chart colors retain their established meanings: bullish `#089981`, bearish
  `#f23645`, primary blue `#2962ff`. Pair colors with labels, shape, pattern,
  or tooltip when the meaning is essential.

## Required UI change workflow

1. Inspect the nearest existing component and its tests before designing.
2. Reuse a token and component pattern; extend the token system only when a
   missing semantic concept is proven.
3. Implement desktop, narrow, touch, focus, disabled, loading, and error
   states together.
4. Run focused UI tests and `npm run build` from `lightweight-charts/`.
5. Manually check keyboard navigation, focus visibility, narrow viewport, and
   fullscreen when the affected interaction needs it.
6. Update this document when a durable visual rule, token, breakpoint, or
   component pattern changes.

## Pre-merge checklist

- No raw visual values or arbitrary z-index in the new component.
- No duplicate visual calculation of a Python-owned trading concept.
- Interactive controls have names, focus, and keyboard behavior.
- Responsive layout has no viewport-level horizontal scroll.
- The chart remains the dominant surface and semantic colors retain meaning.
- Relevant tests and production build pass.
