# TradingBot UI/UX Technical Reference

Evidence date: 2026-09-18  
UI authority: `apps/chart/index.html`, `apps/chart/review.html`, `apps/chart/src/main.js`, project-owned CSS/JS modules, and maintained UI tests

## 1. UI Architecture

TradingBot is a dense, chart-first desktop workstation. It has three implemented surfaces:

1. Main workstation: `apps/chart/index.html` + `apps/chart/src/main.js`.
2. Indicator algorithm/reference view: rendered by `apps/chart/src/algorithm/page.js` and content modules.
3. Manual review page: `apps/chart/review.html` + `apps/chart/src/features/manual-review/entry.js`.

The main shell contains:

- top navigation/action bar;
- left tool rail;
- primary chart workspace;
- OHLC and status overlays;
- drawing toolbar and SVG/canvas overlay layers;
- symbol/RAW-resource selection and range information;
- floating or pinned indicator/settings/object panels;
- dialogs and date/time picker;
- FARAZ candle export/update experience;
- Import / Export chart-transfer action below Trading history, with a two-option modal for moving the current RAW resource and drawings;
- template dropdown;
- status bar, toast, and error-log dialog.

`src/main.js` is the composition root. Smaller modules own bounded mechanics, but the main file owns the integrated DOM wiring and mutable application state.

## 2. Rendering and State Ownership

| UI state | Primary owner |
|---|---|
| Chart instance, series, current RAW/display candles | `src/main.js` |
| LOD and viewport density | `src/chart/lod.js`, `src/chart/view-transform.js`, `src/main.js` |
| Zoom limits | `src/chart/zoom-config.js` |
| Drawing screen/data coordinates | `src/chart/drawing-coordinates.js`, drawing code in `main.js` |
| Workspace panel state | `src/features/workspace-session.js`, `src/ui/workspace-state.js`, `main.js` |
| Indicator execution/visibility/cache | `src/features/indicator-lifecycle.js`, `indicator-cache.js`, `main.js` |
| Popovers | `src/ui/popover.js` |
| Toasts/errors | `src/ui/feedback.js`, `src/ui/log-window.js` |
| Manual review | `src/features/manual-review/*` |
| Algorithm reference | `src/algorithm/page.js` and `src/algorithm/content/*` |

Browser persistence uses `localStorage` for selected resources/timeframes, workspace layout, drawings/context, chart and indicator settings, templates UI state, algorithm language/direction/sidebar state, FARAZ controls, and review statuses. There is no active IndexedDB writer; cache clearing can enumerate/delete IndexedDB databases.

## 3. Design Language

The visual language is a light, professional trading workstation:

- neutral white and cool-gray surfaces;
- high information density and compact controls;
- minimal border/shadow hierarchy;
- blue selection/action accent;
- conventional Bullish green and Bearish red;
- tabular/monospace treatment for prices, timestamps, logs, and technical data;
- floating panels and popovers above a chart-dominant canvas;
- restrained motion with a reduced-motion override.

The implementation is token-first. New UI should consume `apps/chart/src/styles/tokens.css` rather than introduce parallel values without evidence.

## 4. Typography

Token source: `apps/chart/src/styles/tokens.css`.

| Token/use | Value |
|---|---|
| Sans UI | `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, ...` |
| Persian | `Vazirmatn, Tahoma, "Segoe UI", sans-serif` |
| Monospace | `"SFMono-Regular", "SF Mono", Consolas, "Liberation Mono", ...` |
| Numeric | `"Segoe UI Variable Text", "Segoe UI", Arial, sans-serif` |
| 2XS / XS / SM / base / MD / LG / XL | `10 / 11 / 12 / 12 / 13 / 15 / 17px` |
| Weights | `400 / 500 / 600 / 700` |
| Line heights | `1.2 / 1.45 / 1.6` |

Main workstation body text is 12px. Timestamps, object identifiers, OHLC/status data, cache metadata, logs, and raw-table cells use the mono/numeric families. Persian algorithm content switches to `--ui-font-fa`, RTL direction, and right alignment.

The main page loads Inter and Vazirmatn from Google-hosted font CSS. Fallback stacks preserve usability when remote fonts are unavailable.

## 5. Color System

### Surfaces and text

| Role | Value |
|---|---|
| Canvas | `#f5f7fa` |
| Surface | `#ffffff` |
| Subtle surface | `#f8f9fb` |
| Hover | `#f1f3f6` |
| Active | `#e8ecf2` |
| Selected | `#edf3ff` |
| Primary text | `#171a21` |
| Secondary text | `#525c6b` |
| Muted text | `#6f7987` |
| Disabled text | `#9aa2ad` |

### Borders and states

| Role | Value |
|---|---|
| Subtle / normal / strong border | `#eceef2 / #dfe3e8 / #c9d0d8` |
| Selected border | `#d9e3ff` |
| Accent | `#2962ff` |
| Accent hover / active | `#1f54e6 / #1949cf` |
| Accent soft | `#edf2ff` |
| Positive | `#087f70` |
| Negative | `#d83b4b` |
| Warning | `#996000` |
| Danger | `#c92f3d` |
| Focus | `#175cd3` |
| Scrim | `rgba(17, 24, 39, 0.38)` |

### Chart colors

| Role | Value |
|---|---|
| Chart background | `#ffffff` |
| Axis text | `#697386` |
| Axis border | `#e2e5e9` |
| Crosshair | `#8b93a1` |
| Bullish | `#089981` |
| Bearish | `#f23645` |

Indicator and drawing modules use additional colors, but these chart/direction colors are the stable base convention.

## 6. Spacing, Dimensions, and Shape

### Tokens

- Spacing: `4, 8, 12, 16, 20, 24, 32px`.
- Radius: `4, 6, 8, 10px`, plus `999px` pill.
- Control heights: `26, 30, 32px`.
- Touch target: `44px`.
- Top bar: `44px`.
- Status bar: `26px`.
- Left rail: `44px`.
- Floating panel width: `520px`.
- Docked panel width: `360px`.

Panels generally use a 1px `--ui-border`, `--ui-radius-md`, a white surface, and `--ui-shadow-panel` or `--ui-shadow-popover`. Dialogs use the stronger `--ui-shadow-dialog`.

Exact shared shadow tokens:

| Token | Value |
|---|---|
| `--ui-shadow-sm` | `0 1px 2px rgba(16, 24, 40, 0.05)` |
| `--ui-shadow-popover` | `0 12px 32px rgba(16, 24, 40, 0.12), 0 2px 6px rgba(16, 24, 40, 0.06)` |
| `--ui-shadow-panel` | `-10px 0 28px rgba(16, 24, 40, 0.08)` |
| `--ui-shadow-dialog` | `0 24px 64px rgba(16, 24, 40, 0.18)` |

## 7. Layering

The shared z-index contract is:

| Token | Value | Use |
|---|---:|---|
| `--ui-z-chart` | 1 | Chart base |
| `--ui-z-chart-overlay` | 10 | Chart overlays and drawing layers |
| `--ui-z-toolbar` | 30 | Toolbars and fixed interaction surfaces |
| `--ui-z-panel` | 50 | Object tree/settings/algorithm panels |
| `--ui-z-dropdown` | 70 | Dropdowns, contextual actions, tooltips |
| `--ui-z-dialog-backdrop` | 90 | Modal scrim |
| `--ui-z-dialog` | 100 | Modal content |
| `--ui-z-popover-dialog` | 110 | Popovers that must clear dialogs |
| `--ui-z-toast` | 120 | Toast/critical transient feedback |

Local additions use `calc()` relative to these tokens. Examples include range handles at `--ui-z-chart-overlay + 3` and error-log backdrop at `--ui-z-dialog-backdrop + 4`.

## 8. Components and States

### Buttons and icon controls

Compact buttons use transparent or surface backgrounds, tokenized control heights/radii, and Material Symbols. Hover changes background/text; active uses the active surface; selected/expanded uses accent-soft; `:focus-visible` uses an explicit accent outline. Destructive actions switch to danger-soft/danger.

Global disabled controls use `cursor: not-allowed` and `opacity: .46`. Context-specific busy controls can instead use `cursor: wait` and roughly `.5` to `.6` opacity. The update button exposes `data-update-state="loading"`, swaps idle/loading glyph opacity and runs `udSpin`; indicator actions use `.is-loading`; the global chart blocker uses `.loading`; manual review begins with fixed `#review-loading`. Code must restore disabled state and loading classes/attributes in `finally` paths.

The chart-transfer dialog uses the same modal/scrim and focus-restoration contract. Export and import use the Chromium File System Access API on Windows; the export folder contains `manifest.json` plus the exact source RAW, RAW sidecar, and drawing filenames. Import rejects unsafe or malformed bundles before writing and refreshes the symbol inventory before loading the imported drawing state.

### Inputs and selects

Inputs are compact surface controls with 1px borders, tokenized radius, and focus rings. Numeric/date/time values use mono typography. Mobile rules increase important form controls toward the 44px touch target.

Disabled inputs/selects inherit the global `.46` opacity and not-allowed cursor. A disabled color input also disables its adjacent swatch trigger with `pointer-events: none`. Loading is represented by the owning action/control rather than by a universal input spinner.

### Panels

The indicator/settings/object panels can float or pin. On narrow screens, desktop grid/pinning behavior collapses into overlays or a single main-column layout. Panel resize handles have visible focus states.

### Object tree

`src/drawings/object-tree.css` implements hierarchical folders, object rows, visibility/lock/context controls, selected state, nested indentation, and a contextual action menu. At 760px and below it becomes a right-side overlay; at 520px its width and row actions become touch-oriented.

### Drawing toolbar and overlays

`src/drawings/drawing.css` defines a floating tool palette and interactive controls. Drawing geometry remains data/time/price anchored; the screen overlay layer is non-authoritative presentation.

### Dialogs, date/time picker, and popovers

Dialogs use a fixed scrim plus centered card. The custom date/time picker contains month navigation, seven-column day grid, three time selects, and explicit Today/apply behavior. Generic popovers are positioned through `src/ui/popover.js` and use dropdown/dialog z-index contracts.

### Toast and error log

The toast is a fixed three-column surface with icon, copy, close button, and timed progress. Success/error/info styles use positive/danger/accent tokens. The error-log dialog presents timestamped entries, message, details, and stack/preformatted content.

### Candle export/update UI

`src/styles/candle-export.css` and `src/features/candle-export.js` implement FARAZ authentication/status, date ranges, metrics, progress, raw tables, coverage decisions, logs, cancellation, and download/open controls. The raw table uses sticky headers and mono numeric cells.

### Indicator templates

The template dropdown contains title/actions, search, saved-template list, current markers, delete controls, empty state, and import/export actions. It uses the dropdown layer, 16px outer radius, compact 40px rows, and explicit keyboard focus.

### Algorithm reference

`src/algorithm/styles.css` provides a two-column reference layout, searchable navigation, direction/module color families, code blocks, tables, copy controls, and English/Persian switching. Under 760px the sidebar becomes an overlay with scrim; narrower breakpoints simplify spacing and typography.

### Manual review

`src/features/manual-review/review.css` implements metrics, filters, grouped days/events, review-state controls, bulk actions, calculation metadata, skip link, mobile stacking, and print rules. This page has its own compact design variables but remains visually compatible with the main workstation.

## 9. Icons

The primary icon system is Material Symbols (`material-symbols-outlined`) plus centralized icon helpers in `src/ui/icons.js`. Most icons are 14–19px inside 24–32px compact controls. Touch-oriented/narrow-screen actions expand the hit area without proportionally increasing glyph size.

Playwright vendor assets under `node_modules` contain browser/product icons; they are not used as TradingBot design-system icons.

## 10. Responsive Architecture

Observed breakpoints are implementation-specific rather than one global scale:

- 1180px: workstation density/panel/export adjustments.
- 1120px: algorithm page changes.
- 900px: main shell reductions.
- 860px: algorithm layout changes.
- 800px and 720px: manual review layout.
- 760px: primary workstation/panel/toolbar mobile transition.
- 560/520/490px: narrow algorithm, panel, cache/update, and form behavior.
- 440/420/400/380px: smallest export, toast, controls, algorithm, and review adaptations.

At narrow widths:

- the rail remains approximately 44px;
- pinned-panel desktop columns collapse;
- side panels become overlays;
- horizontal toolbar areas may scroll;
- symbol/range content wraps or stacks;
- dialogs use reduced padding and viewport width;
- action hit targets increase;
- toast width becomes `calc(100vw - 16px)`;
- review cards and metadata grids stack.

This is adaptive browser support, not a separate mobile information architecture. Do not claim that every desktop workflow has been live-tested on mobile.

## 11. Accessibility and Motion

Implemented conventions include:

- semantic buttons/inputs/selects in the maintained HTML/JS paths;
- `:focus-visible` outlines on interactive controls;
- manual-review skip link;
- readable hover/focus/selected distinctions beyond color in many components;
- 44px touch targets for critical narrow-screen controls;
- `prefers-reduced-motion: reduce` overrides in tokens and component CSS;
- print-specific manual-review rules;
- Persian direction and font handling.

Static inspection does not prove complete keyboard navigation, screen-reader naming, focus trapping, or contrast compliance. Those require browser/accessibility testing.

## 12. Chart and Indicator Rendering Rules

- Python calculation payloads are authoritative.
- JavaScript converts serialized objects into render models; it must not recreate detector decisions.
- Rendering must preserve candle timestamps, prices, ownership identities, order, and visibility state.
- LOD may reduce display density but must not replace RAW input for calculations or exports.
- Drawings must remain time/price anchored across pan, zoom, resize, and timeframe projection.
- `Asia/Tehran` is the maintained display-time contract.
- Bullish/Bearish colors must remain semantically consistent across chart objects, badges, audit, and reference pages.

## 13. Reusable UI Rules

1. Read `tokens.css` and the affected component stylesheet before adding values.
2. Prefer existing compact control, panel, dropdown, dialog, toast, and table patterns.
3. Preserve IDs and state/persistence contracts when changing markup.
4. Use CSS-first visual changes; JavaScript changes require state/event/render justification.
5. Keep technical numeric data mono/tabular and user-facing prose in the sans/Persian families.
6. Use the shared z-index scale; do not solve layering with arbitrary extreme values.
7. Maintain visible keyboard focus and reduced-motion behavior.
8. Preserve touch access at narrow widths and avoid viewport-wide horizontal overflow.
9. Do not move trading calculations into browser code.
10. Validate the main workstation, algorithm page, and manual review separately; they have different responsive rules.

## 14. Known UI Risks

- `src/main.js` has broad ownership and high regression coupling.
- Generated `dist` is not proven synchronized with current source.
- Many component-specific media queries make responsive behavior distributed rather than centrally modeled.
- LAN-exposed backend mutations are reachable from the same browser surface without an application authentication layer.
- Remote fonts can change perceived typography when unavailable.
- Static CSS/source review does not replace real-browser visual, keyboard, accessibility, overflow, and z-index verification.
