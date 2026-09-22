# TradingBot UI/UX Technical Reference

**Audit snapshot:** 2026-09-22

**UI authority:** current `apps/chart` source plus rendered local-browser evidence.
**Scope:** global shell, Chart workspace, FARAZ Exporter, Algorithm reference, Manual Review, shared panels/dialogs and responsive states.

## 1. UI Executive Summary

TradingBot is a light-mode, chart-first desktop workstation implemented with native ES modules and CSS. The main document contains a persistent top toolbar, left navigation rail, central workspace and bottom status bar. Three primary workspaces share the shell: Chart, FARAZ Exporter and Algorithm. Manual Review is a separate `/info` document. The UI is a renderer and interaction layer; Python remains the trading-calculation authority.

## 2. Evidence Boundary

Static evidence came from `index.html`, `review.html`, `main.js`, every frontend module and every project stylesheet. Runtime evidence came from a temporary local mirror on `127.0.0.1:5173`: main Chart, Algorithm, FARAZ, `/info`, a 360×800 viewport and captured console logs. Authenticated FARAZ and populated calculation/report states were not exercised.

## 3. Frontend Technology Stack

- Native HTML, CSS and ES modules; no component framework.
- Lightweight Charts `5.2.1` for price/time rendering.
- Fetch/JSON for APIs and `EventSource` for indicator progress.
- Canvas/DOM overlay logic for drawings and range handles.
- Local storage plus local HTTP persistence for preferences and user state.
- Inline SVG icon factory in `src/ui/icons.js`.

## 4. Physical Page Inventory

| Page | Route | Entry | Status |
|---|---|---|---|
| Workstation | `/` | `index.html` -> `src/main.js` | Fully documented |
| Manual Review | `/info` | `review.html` -> `manual-review/entry.js` | Fully documented |

There are 2 physical pages. The workstation contains 3 fully implemented primary workspaces and multiple panels. Algorithm contains 48 hash-routed virtual reference views: overview, 11 family pages, 34 type pages and 2 supporting references.

## 5. Screen, Tab and Panel Inventory

| Surface | Kind | Owner |
|---|---|---|
| Chart | Primary workspace | `main.js` |
| FARAZ Exporter | Primary workspace | `candle-export.js` |
| Algorithm | Primary workspace / hash router | `algorithm/page.js` |
| Manual Review | Separate page | `manual-review/*` |
| Indicator Configure / Appearance / Activity | 3 tabs | `main.js` |
| FARAZ Previous candles / Time range | 2 mode tabs | `candle-export.js` |
| Symbol and timeframe menus | Popovers | `main.js`, `popover.js` |
| Indicator, object tree, logs, settings | Panels | `main.js` |
| Go-to, cut, update, transfer, coverage decision | Dialog/popover flows | feature owners + `main.js` |

Counts used by this audit: 2 pages, 48 Algorithm virtual routes, 5 explicit content/mode tabs, and 4 primary user-facing screens/views.

## 6. Route Inventory

Browser routes are `/`, `/info`, and the 48 `#algorithm-*` hashes. Backend dependencies comprise 26 API route families documented in the architecture reference. Unknown hashes normalize to `#algorithm-overview`.

## 7. Global Component Tree

```text
app
├─ topbar / workspace header
│  ├─ identity + symbol/timeframe
│  ├─ drawing toolbar
│  └─ chart/workspace actions
├─ left navigation rail
├─ workspace
│  ├─ chart shell + Lightweight Chart
│  ├─ drawing canvas + range handles
│  ├─ FARAZ Exporter (exclusive)
│  └─ Algorithm reference (exclusive)
├─ panels / popovers / dialogs / toast / log window
└─ status bar
```

## 8. Global Layout

The shell reserves `44px` for the top bar, `44px` for the rail and `26px` for the status bar. The chart fills the remaining grid cell and must preserve overflow/resize contracts. Workspaces replace the chart area and mount their own header controls while preserving the rail and status bar.

## 9. Header

The Chart header holds symbol/timeframe selection, thirteen drawing tools and chart actions. Algorithm swaps in back/menu/search/copy/export/direction/language controls. FARAZ reduces the header to page identity. Workspace header mounting/restoration is centralized in `ui/workspace-state.js`.

## 10. Sidebar and Navigation Rail

The rail exposes Dashboard, FARAZ, Chart, Indicator, Object Tree, Algorithm, Alert, History, Import/Export, Logs, Chart settings and Profile. Some entries are placeholders or panel triggers rather than complete screens. Active states use `aria-pressed`/checkbox semantics and the selected visual token. Algorithm also owns an internal collapsible navigation sidebar.

## 11. Footer and Status Bar

The status bar reports health, indicator/cache/FARAZ state, visible candle count, visible range, stable chart ID and clock. On workspace views it remains available. Buttons navigate to related settings/status surfaces. At 360px the rendered DOM retained the health, indicator, cache and FARAZ controls.

## 12. Toolbars and Controls

Chart tools: Cursor, Trend line, Horizontal line, Vertical line, Horizontal ray, Fibo retracement, Brush, Rectangle, Circle, Long position, Short position, Text, Path and Measure. Actions include cut, selected-range calculation, update, undo/redo, hide, screenshot, report, fullscreen, cache reload and go-to-date. Tool ordering supports drag and `Alt+Left/Right` keyboard reordering.

## 13. Design Tokens

`tokens.css` is the semantic source of truth. Core surfaces: canvas `#f5f7fa`, surface `#fff`, subtle `#f8f9fb`, hover `#f1f3f6`, selected `#edf3ff`. Text: `#171a21`, `#525c6b`, `#6f7987`, disabled `#9aa2ad`. Accent `#2962ff`; positive `#087f70`; negative `#d83b4b`; warning `#996000`; focus `#175cd3`.

## 14. Chart Color System

Chart chrome uses white background, axis text `#697386`, axis border `#e2e5e9`, crosshair `#8b93a1`, bullish `#089981` and bearish `#f23645`. Runtime chart settings remain authoritative; token aliases are presentation defaults, not engine semantics.

## 15. Algorithm Color System

Each family has a stable accent/soft pair: Reaction neutral, Reset brown, Blue Line blue, A purple, S red/teal, E blue/red, Order Audit amber, StopAll green and Bridge slate. Direction toggle changes textual projection; Bearish is explicitly labeled derived.

## 16. Typography

Primary stack: Inter/system UI; Persian: Vazirmatn/Tahoma; code: SFMono/Consolas. Token sizes run from 10px to 17px with weights 400-700. Chart chrome is intentionally compact; Algorithm overview reaches 28px and Manual Review headings 19-25px by viewport. Numeric areas use tabular/numeric-friendly stacks.

## 17. Spacing and Geometry

Spacing tokens are 4, 8, 12, 16, 20, 24 and 32px. Radii are 4, 6, 8, 10 and pill. Controls are 26, 30 and 32px; touch target token is 44px. Floating panel width is 520px and docked panel width is 360px.

## 18. Elevation and Layers

Shadows cover small, popover, side panel and dialog elevations. Z layers: chart 1, chart overlay 10, toolbar 30, panel 50, dropdown 70, dialog backdrop 90, dialog 100, popover-dialog 110, toast 120. New overlays must use these tokens instead of arbitrary stacking values.

## 19. Motion

Motion tokens are 100ms/160ms with `cubic-bezier(.2,.8,.2,1)`. Sidebar, disclosure and popover transitions use them. `prefers-reduced-motion` sets durations to zero and component styles remove remaining transitions/scroll behavior.

## 20. Icons

Icons are generated as inline SVG by `ui/icons.js`. Buttons pair accessible names/tooltips with icon-only visuals. Avoid emoji or external icon libraries; add icons to the shared factory and preserve stroke/size conventions.

## 21. Forms

Controls use explicit labels or `aria-label`, visible disabled states and semantic input types. FARAZ settings remain disabled until a session exists. Date/time controls show Tehran-readable values next to local inputs. Validation must remain both structural in the browser and authoritative on the server.

## 22. Tables

FARAZ local inventory is sortable across filename, symbol, broker, timeframe, dates, count and size. Algorithm object contracts use horizontally scrollable minimum-width tables. Manual Review uses event/collection groupings rather than a single grid. Preserve keyboard focus and small-screen overflow.

## 23. Charts and Drawing Layer

Lightweight Charts owns candles, axes and crosshair. Custom drawing anchors are stored in raw time/price coordinates and transformed at render time. LOD may reduce displayed candles but must not redefine stored anchors. The drawing canvas, hit testing, object tree and undo/redo are coupled consumers.

## 24. Loading, Empty, Error and Success States

- Loading: indicator SSE progress, FARAZ job progress, review loading copy and update progress.
- Empty: zero candles/NULL identity, no local RAW files, no packet activity, no review identity.
- Error: health control, toast/log window, operation-specific errors and failed review paragraph.
- Success: ready/cache states, saved/export messages, completed FARAZ validation and calculation results.

## 25. Accessibility

Observed controls expose accessible names and pressed/expanded state. Algorithm provides skip navigation, semantic headings, navigation landmarks, direction/language groups and focus targets. FARAZ uses labeled regions, progressbar, tables and disabled semantics. Keyboard support covers popovers, Escape, tabs, disclosures, drawing reorder and dialogs. Focus rings use `--ui-focus`.

## 26. Responsive System

Global styles use breakpoints around 1180, 900, 760, 520, 420 and 400px; Algorithm adds 1120, 860, 760, 560 and 380px; Manual Review uses 900 and 590/560px. At 760px Algorithm sidebar becomes an off-canvas panel with scrim. At 360×800, Chart/FARAZ/Algorithm retained semantic navigation and controls; Algorithm exposed an explicit navigation button and off-canvas contents.

## 27. Performance UX

LOD protects chart rendering for >100k rows. Expensive indicator work is delegated to Python and cached. SSE keeps the UI responsive during calculation. FARAZ logs and progress summarize packets rather than rendering every raw response. The large single JS bundle and large `main.js` increase startup and maintenance cost.

## 28. Frontend Security

The UI does not render credentials, but FARAZ status can display user ID/name/phone returned by the local API. Remote Google Fonts create an external request. Import/export, delete, cut, update and browser-launch actions rely on an unauthenticated local backend; frontend confirmations are not security boundaries. Content uses text assignment/escaping in the reviewed renderers; no confirmed DOM-XSS sink was found.

## 29. Shared State and Persistence

`main.js` owns live chart identity, candles, series, drawings, selected range, indicator results/settings, workspace and update state. Feature modules hold bounded state for FARAZ jobs, review snapshots, caches and workspace sessions. Local-storage keys persist layout/preferences; drawings/templates/results also use server persistence.

## 30. Shared Component Map

| Component | Owner | Consumers |
|---|---|---|
| Icons | `ui/icons.js` | shell, panels, Algorithm, FARAZ |
| Feedback/toast | `ui/feedback.js` | main operations |
| Popover | `ui/popover.js` | menus and controls |
| Workspace header | `ui/workspace-state.js` | Chart, Algorithm, FARAZ |
| Chart identity | `ui/chart-identity.js` | chart, persistence, API requests |
| RAW filename contract | `features/raw-file-contract.js` | inventory/update/export |
| Indicator cache/lifecycle | feature modules | main chart, report, review |
| Tokens | `styles/tokens.css` | every page/workspace |

## 31. Workstation — Frontend Technical Reference

### Overview

Route `/`; entry `index.html` and `main.js`. Purpose: select RAW data, inspect/chart candles, draw, calculate indicators, manage workspace state and open related tools.

### User Workflow

Select symbol/timeframe -> load candles -> navigate/zoom/draw -> choose indicator settings/range -> calculate -> inspect overlays/report -> optionally update, cut, export or review.

### Source Map and Component Tree

Primary owner `main.js`; chart contracts under `src/chart`; drawings under `src/drawings`; cache/range/update/raw/session/review under `src/features`; shared UI under `src/ui`; styles under `src/styles`. Backend dependencies: symbols, candles, reactions/progress/cache, drawings, templates, chart transfer and candle-file routes.

### Layout and States

Persistent topbar/rail/statusbar surround the chart. Panels float or dock. Symbol/timeframe popovers, update choices, dialogs, toasts and log window overlay the chart. Empty runtime shows `NULL`, zero candles and em-dash OHLC. Errors surface through health and logs.

### Modification Guide and Regression Risk

Change chart orchestration in `main.js` only after tracing helpers. Changes to time coordinates, LOD, resize or persisted IDs are high risk. Run drawing, view-transform, zoom, range, cache/lifecycle, workspace and browser responsive checks.

## 32. FARAZ Exporter — Frontend Technical Reference

### Overview

Workspace on `/`, opened by `#candleExportBtn`; owner `features/candle-export.js` with `styles/candle-export.css`. Purpose: acquire authenticated FARAZ history, verify exact coverage and save canonical RAW files.

### User Workflow

Sign in/check session -> choose symbol/timeframe/host -> choose Previous candles or Time range -> start -> monitor packets/coverage -> explicitly cancel or continue if source coverage is incomplete -> validate saved file -> inspect/open inventory.

### Component Tree and Data Flow

Session card; locked settings; data-source form; range modes; job status/progress; connection info; saved-file checks; packet log; action bar; local RAW table; coverage-decision dialog. It calls all `/api/faraz/*` routes plus candle update/verification and `/api/symbols`.

### States, Responsive, Accessibility and Security

Locked/no-session, ready, running, awaiting decision, canceled, failed and completed states are explicit. At 360px all labeled regions and controls remained in the semantic DOM; wide inventory scrolls. Profile fields are sensitive. Authentication and integrity must remain server-authoritative.

### Modification Guide and Regression Risk

UI behavior belongs in `candle-export.js`; transport/recovery belongs in `faraz-candle-api.js`; names/metadata in RAW contract/store. Coverage decisions, exact bounds, no-progress recovery and never-saving-incomplete behavior are critical regressions.

## 33. Algorithm Reference — Frontend Technical Reference

### Overview

Workspace on `/` with 48 `#algorithm-*` virtual routes. Owners: `algorithm/page.js`, `mirror.js`, content files and `algorithm/styles.css`. It documents 10 Bullish families, 30 Bullish calculation types, Bridge with 4 types, Reaction geometry and Glossary.

### Route Map

Overview; family and type routes for Reaction, Reset, Blue Line, A, S red, S blue, E blue, E red, Order Audit and StopAll; Bridge family and four Bridge type routes; Reaction geometry; Glossary. Invalid hashes return to overview.

### Controls and State

Back, navigation toggle, search, copy, HTML/PDF export, Bullish/Bearish-derived direction and English/Persian language. Language, direction and sidebar state persist in local storage. Route scroll positions are restored.

### Layout, Responsive and Accessibility

Desktop uses a 270px internal sidebar and readable content up to 960px; collapsed width is 54px. At <=760px it becomes off-canvas with scrim; rendered 360px evidence showed explicit open/close navigation and complete content landmarks. Hash links, headings, skip link and focus restoration support keyboard navigation.

### Security and Accuracy

Content is compiled from local JS objects and escaped before HTML output. Export opens/writes a generated document or file handle. Bearish wording is a derived presentation and must never be promoted to independent numerical authority. Source line/version statistics embedded in `AUDITED_FILES` are currently stale and should be regenerated or removed.

## 34. Manual Review — Frontend Technical Reference

### Overview

Physical `/info` page. `manual-review/tab.js` opens it with a calculation identity; `entry.js` fetches the saved payload; `render.js` builds filters, event groups, bridge detail and report export; `review.css` owns layout.

### Workflow and Dependencies

Open from Calculation report -> resolve `/api/info/...` -> render calculation metadata -> filter by date/family/type -> assign review states -> inspect bridge YAML -> copy/export report. Without identity, rendered runtime correctly showed `This report has no calculation identity.`

### Layout and States

Desktop uses sticky filter sidebar plus report content. It collapses at <=900px and compacts at <=590/560px. Loading, missing identity, fetch/render error, empty filtered collection and populated success are separate states. Print styles remove interactive chrome.

### Security and Regression Risk

The page displays saved calculation content and review annotations; escaping and identity validation are mandatory. Payload-contract changes require coordinated bridge, API and renderer updates plus `manual-review.test.mjs`.

## 35. Dialog and Popover Reference

Dialogs include go-to date, cut range, selected update mode, transfer, settings and FARAZ coverage decision. Popovers include symbol/timeframe and small action menus. Preserve initial focus, Escape handling, focus containment where modal, scrim/layer tokens and explicit destructive labels.

## 36. Indicator Panel Reference

Configure owns direction/timeframe/stage switches and calculation inputs. Appearance owns render-only visibility/color/line settings. Activity owns progress/status/cache evidence. Calculation identity must exclude appearance-only choices but include every numerical input and selected range.

## 37. Object Tree and Drawing Reference

The object tree projects drawing/chart objects, visibility and selection. Drawing tools share hit testing, raw coordinate storage, style controls and undo/redo. Hiding drawings is presentation-only. Any schema change requires persistence migration or tolerant reading.

## 38. RAW Inventory and Update UI

Inventory groups canonical broker/symbol/timeframe files with chart IDs and metadata. Update offers three exclusive modes, uses the source timeframe, merges chronologically, does not overwrite valid collisions and distinguishes source absence from retryable failure. Cut can replace or create a new canonical range.

## 39. Chart Transfer UI

Import/export moves chart identity, drawings and related state through a validated bundle. The UI must communicate replacement scope before import; the server rejects malformed versions/paths. Treat imported content as untrusted.

## 40. Information Architecture

Primary navigation separates market work (Chart), data acquisition (FARAZ), and reference learning (Algorithm). Secondary panels remain contextual to Chart. Manual Review is intentionally isolated in another tab/document so large reports do not compete with chart layout.

## 41. Page-to-Backend Dependency Matrix

| Page/view | Read dependencies | Mutation dependencies |
|---|---|---|
| Chart | symbols, candles, reactions progress/info, drawings, templates | reactions, cache, drawings, templates, cut/delete/update, transfer |
| FARAZ | auth status, job status/download, symbols | auth open/browser/logout, start/cancel/decision/open, history, update/verify |
| Algorithm | local content modules only | local preference state; optional file export |
| Manual Review | `/api/info/...` plus session snapshot | local review state/report copy only |

## 42. Page Change Impact Matrix

| Change | Chart | FARAZ | Algorithm | Review |
|---|---:|---:|---:|---:|
| Tokens/global shell | High | High | High | Medium |
| RAW contract | High | High | Low | Medium |
| Bridge payload | High | Low | High documentation impact | High |
| Workspace header | High | High | High | None |
| FARAZ API | Medium | High | None | None |
| Direction semantics | High | None | High | High |
| Responsive rail/status | High | High | High | None |

## 43. Where to Make UI Changes

- Shell/navigation/chart composition: `main.js`, `app.css`, `qg-modern.css`.
- Global design language: `tokens.css`; retain aliases during migration.
- Chart transforms/LOD/range: `src/chart/*`.
- Drawing tools: `drawing-math.js`, `drawing-coordinates.js`, `main.js`, drawing CSS.
- FARAZ view: `candle-export.js` and `candle-export.css`.
- Algorithm pages/content: `algorithm/page.js`, `content/*`, `styles.css`.
- Manual Review: `manual-review/render.js` and `review.css`.
- Shared icons/popovers/feedback/workspace header: matching `src/ui` module.

## 44. Frontend Test Map

Direct UI-contract tests cover feedback, popovers, screenshot overlay, symbol formatting, workspace state/session, view transforms, zoom, drawing coordinates/tools, indicator range/cache/lifecycle/request and manual review. Data-facing UI contracts are covered by RAW, transfer, update, FARAZ and range-input tests. There is no automated full-browser visual regression suite.

## 45. Rendered Verification Evidence

- Main page title and full toolbar/rail/status landmarks rendered at `127.0.0.1:5173`.
- Algorithm overview rendered 10 families, 30 types, 185 audited slots, 183 unique collection fields, 34 envelope/nested fields and Bridge 4 types.
- FARAZ rendered locked authentication, both range modes, status/connection/validation/log regions and empty RAW inventory.
- `/info` rendered its missing-identity state.
- 360×800 DOM checks preserved FARAZ and Algorithm landmarks/controls.
- Browser console capture after a clean root load contained no warning/error entries.

## 46. UI Risks and Debt

- `main.js` is a high-coupling composition root.
- Some rail items appear as placeholders, which can imply unavailable functionality.
- Compact 10-12px typography may challenge low-vision users despite semantic accessibility.
- Wide tables depend on horizontal scrolling at small sizes.
- Remote fonts weaken offline behavior/privacy.
- The production JS chunk exceeds 500 kB.
- In-app algorithm source/version counts drift manually.

## 47. Unverified UI Areas

Populated million-row chart behavior, all drawing gestures, fullscreen/screenshot file output, authenticated FARAZ, incomplete-coverage dialog with live data, populated review filters and export, real keyboard screen-reader traversal, print/PDF output and cross-browser rendering were not fully exercised.

## 48. UI Regression Checklist

- Preserve IDs, local-storage keys, chart IDs and persisted drawing schema.
- Verify desktop and 360px layouts, focus, Escape and reduced motion.
- Confirm raw time/price anchors after zoom, LOD and resize.
- Confirm all three update modes remain exclusive.
- Confirm selected indicator endpoints are inclusive and cache identity is numerical-only.
- Confirm Algorithm hashes, EN/FA, direction label and exports.
- Confirm Manual Review with and without a calculation identity.
- Check console, 27-test suite and production build.

## 49. Completion and Traceability

Both physical pages, four primary screens/views, 48 Algorithm virtual routes, five explicit tabs/modes, shared panels/dialogs, global tokens and every frontend source/style owner are documented. Runtime proof is partial where external authentication or populated user data would be required. Backend/security details are cross-referenced in `docs/TradingBot_Technical_Architecture.md`.
