---
title: TradingBot UI/UX Reference
document_role: reference
lifecycle: maintained
owner: ui-ux
scope:
  - chart
  - workspace
  - trading-result-presentation
  - drawings
  - manual-review
  - faraz-ui
  - algorithm-reference-ui
  - responsive-accessibility
last_modified_at: 2026-10-04T05:09:22+03:30
---

# TradingBot UI/UX Reference

## 1. Purpose

This document is the maintained reference for the **Current TradingBot user interface and user experience**. It describes implemented user-facing workflows, workspace behavior, Chart interaction, result presentation, drawings, Manual Review, FARAZ-facing interaction, UI state, persistence expectations, responsive behavior, accessibility mechanisms, and frontend/backend ownership boundaries.

It documents behavior and responsibility rather than today's frontend file layout. Internal components may be reorganized without requiring this document to change when the user-visible contract remains the same.

This document does **not** define trading semantics. Current Engine behavior and accepted trading specifications remain owned by the current Source and canonical trading-knowledge system.

## 2. Authority and related owners

This reference is subordinate to the root [`AGENTS.md`](../../../AGENTS.md) and [Documentation Governance](../documentation-governance.md).

Use the following owner boundaries:

- [Technical Architecture](technical-architecture.md) owns subsystem/process/transport architecture.
- [Local State](../operations/local-state.md) owns persistence placement and operational storage rules.
- [AI Engineering Workflow](../ai/engineering-workflow.md) owns repository engineering procedure.
- Current Engine Source and accepted Algorithm References own trading semantics.
- This document owns maintained **user-visible UI/UX behavior**.

Current implementation claims in this document are reconstructed from the live Chart/frontend Source, its UI-facing server contracts, and current UI contract tests. Historical screenshots, audits, and reports are evidence only.

## 3. UI/UX principles

The maintained UI follows these durable principles:

1. **Chart-first workstation.** Market data, chart interaction, drawings, calculation controls, and finalized result overlays share one workstation shell.
2. **Presentation is not trading authority.** Chart displays finalized Engine results; it does not independently repair or recreate trading decisions.
3. **Workspace ownership is explicit.** Chart, FARAZ, and Algorithm modes reveal only the controls relevant to the active workspace.
4. **User intent is visible.** Long operations expose progress or status; destructive operations require explicit user action; failures remain observable.
5. **Presentation state is separate from calculation truth.** Colors, visibility, offsets, filters, panels, and review decisions may change without rewriting Engine state.
6. **Responsive behavior preserves access.** Narrow layouts reflow, scroll, or overlay controls instead of defining a separate mobile product.
7. **Performance optimizations remain presentation-only.** Display density/LOD must not alter RAW authority or Engine calculation semantics.
8. **Historical UI evidence cannot override the live application.**

## 4. Application and workspace model

### 4.1 Shared workstation shell

The main application uses a shared shell containing:

- a workspace header area;
- workspace navigation;
- the active content surface;
- Chart contextual panels/dialogs;
- a status area for runtime and workflow state.

Workspace switching also changes which header/footer groups are visible. Controls belonging to an inactive workspace are hidden from interaction and accessibility traversal rather than merely covered visually.

### 4.2 Chart workspace

Chart is the primary market workspace. It contains the candle surface, drawing layer, symbol/timeframe controls, chart actions, indicator controls, Object Tree, status information, and user-created/result overlays.

### 4.3 FARAZ workspace

FARAZ is a dedicated acquisition workspace inside the workstation shell. It owns sign-in/session-facing UI, extraction configuration, acquisition progress, local RAW inventory presentation, coverage decisions, and related success/error feedback.

### 4.4 Algorithm workspace

Algorithm is an in-application reference workspace with its own header/navigation. It supports browsing, searching, direction/language presentation, copying, and export of the application reference content.

It is a **reference/presentation surface**, not a replacement for canonical project authority.

### 4.5 Manual Review

Manual Review is a separate report document opened from a persisted calculation identity. It is not a fourth shared-shell workspace. It presents finalized calculation information for human review without changing Engine truth.

### 4.6 Full-screen Chart

Full-screen Chart suppresses normal workstation chrome so the chart surface can occupy the available viewport. Leaving full screen restores the normal workspace contract.

## 5. Primary user workflow

A normal Chart-centered workflow is:

1. Start the application and allow the workstation to load the current local RAW inventory.
2. Select a chart/data resource and a supported chart timeframe.
3. Inspect the chart by panning, zooming, moving to specific times, or jumping toward the beginning/end of available chart data.
4. Add or edit drawings when manual annotation is needed.
5. Open the indicator panel, enable calculation, select the required direction, choose an analysis timeframe, and define an inclusive calculation range.
6. Apply the calculation.
7. Observe calculation progress while the request is validated, executed, returned, and prepared for rendering.
8. Inspect finalized result overlays, status information, Object Tree entries, and calculation details.
9. Open Manual Review when a persisted calculation report needs event-by-event human classification.
10. Use FARAZ acquisition/update workflows when additional or repaired source data is required.

The application may restore valid workspace/chart preferences across refresh, but restored presentation state never substitutes for a new authoritative calculation when the calculation context is absent or changed.

## 6. Chart interaction model

### 6.1 Data selection

The symbol/data picker presents locally available RAW resources and their user-facing identity/range information. Selecting a resource loads its candles into Chart.

A chart identity is stable independently of the display filename. The current chart identity and timeframe can also be represented in the tab URL so separate tabs can reopen the same chart with independent timeframe context.

Destructive RAW deletion requires confirmation and removes the selected local resource through the supported server boundary.

### 6.2 Timeframe selection

Chart timeframes are constrained by the selected source data. The UI does not allow a chart timeframe finer than the source timeframe.

Changing chart timeframe rebuilds the displayed chart context and invalidates any active indicator result whose calculation context no longer matches.

### 6.3 Pan, zoom, navigation, and time targeting

The user can pan and zoom the chart using the chart interaction model. Chart redraw and display-density work follow visible-range changes.

Additional navigation includes:

- jumping to a Tehran date/time and centering on the nearest available candle;
- moving toward the first or last available chart region;
- using the crosshair/OHLC presentation to inspect candle values.

The current visible viewport is a presentation concern. It is not automatically the indicator calculation range.

### 6.4 Screenshot and chart transfer

Chart can create a screenshot carrying chart identity/timeframe and Tehran capture-time context.

The Import/Export workflow moves a chart's validated RAW content, metadata, and drawings as one user-facing transfer unit. Importing creates or restores a local chart resource through the server-owned validation boundary.

## 7. Full Chart vs Selected Range UX

The UI distinguishes several different concepts:

| Concept | User-visible meaning |
| --- | --- |
| Visible range | The portion currently visible after pan/zoom. |
| Calculation range | The inclusive From/To candle range selected for indicator calculation. |
| Full-source calculation request | The selected calculation range covers the available chart source. |
| Selected-range calculation request | The selected calculation range covers only part of the available chart source. |
| Presentation range | The range of finalized result information exposed for the requested calculation context. |

### 7.1 Range selection

Indicator range endpoints are anchored to actual chart candles. Users can set them from the date/time controls or move the on-chart handles.

The handles:

- snap to inclusive chart-candle times;
- may define a single-candle range;
- cannot cross each other;
- can be moved by pointer;
- can be adjusted from the keyboard with Left/Right Arrow while focused.

Dragging a range handle previews the changing endpoint on Chart and commits the selected candle time when the interaction finishes.

### 7.2 Calculation boundary

The selected UI range is sent as part of the calculation request. Whether the local server supplies the complete RAW resource or a selected subset to Engine is an architectural transport decision described in [Technical Architecture](technical-architecture.md).

The UI/UX invariant is:

**viewport range, calculation range, and Engine input history are not interchangeable concepts.**

Chart must not imply that whatever is currently visible is necessarily the complete history used by Engine.

### 7.3 Cut-candle workflow

The selected inclusive candle range can also be used by the explicit Cut workflow. The user chooses whether to replace the current RAW resource while retaining its chart identity or create a new local resource with a new identity.

## 8. Indicator configuration and calculation

### 8.1 Configuration

The indicator panel separates calculation inputs from presentation controls and activity/information.

Before calculation can start, the current UI requires:

- indicator enabled;
- a selected trend direction;
- a valid ordered range inside available data.

When a required choice is missing, the user receives an error and the relevant control is focused where practical.

### 8.2 Calculation reuse vs recalculation

If the current finalized result already matches the same calculation context, changing presentation-only settings can update appearance without rerunning Engine.

Changes to calculation identity/context—such as source, direction, analysis timeframe, chart timeframe, or selected calculation range—require an appropriate calculation result for that new context.

Server-side result cache reuse may make a repeated request faster, but cache status is presented as reuse information rather than semantic authority.

### 8.3 Progress

During a calculation the Apply control is disabled and the progress UI tracks the request from browser/server work through Engine phases and result preparation.

Progress events are presented incrementally. The completed result also exposes summarized timing/activity information useful for inspection without changing the result itself.

### 8.4 Completion and failure

On success:

- the finalized payload becomes the active indicator result;
- presentation objects are rebuilt from that payload;
- Chart redraws;
- indicator/cache status is refreshed;
- calculation details/activity become available.

On failure:

- the result is not presented as successful;
- the indicator status and footer expose the failure state;
- an error notification is shown;
- diagnostic activity is recorded for user inspection;
- the Apply control is re-enabled after the request finishes.

If the selected RAW changes while a request is queued or running, the server rejects the stale calculation. The user can Apply again against the current RAW; the stale result does not become the active indicator result.

## 9. Trading-result presentation

Chart projects finalized result collections into visual objects such as:

- Reaction regions/markers;
- Blue Lines;
- A, S, E, and StopAll labels/objects;
- physical Order presentations;
- Order-stop presentations;
- OrderAudit-backed Order objects when they are not already represented by a visible behavior.

These are **presentation projections of Engine output**. The frontend may filter objects explicitly marked invalid for presentation, but it does not create alternative trading decisions.

### 9.1 Visibility and appearance

Users can control presentation properties such as visibility, line/fill appearance, label styling, and selected object appearance.

Presentation objects may support UI-only customization such as:

- hidden/visible state;
- lock state;
- color/style changes;
- display offsets;
- label appearance.

Such changes do not rewrite the underlying Engine payload.

### 9.2 Object Tree

The Object Tree provides a shared inspection/selection surface for user drawings and current indicator presentation objects.

Selecting an object can focus it in the Chart context. Object visibility, locking, grouping/organization, and deletion actions remain UI concerns.

## 10. Drawings and annotations

### 10.1 Creation

Chart provides user drawing/annotation tools for line/shape/freehand/measurement/position-style workflows and related annotations implemented by the current toolset.

Drawing points are stored in canonical chart time/price coordinates so presentation-density changes do not redefine their market position.

Most completed drawing tools return to cursor mode after creation; freehand brush interaction remains armed for repeated strokes until the user changes/cancels the tool.

### 10.2 Selection and editing

A drawing can be selected on Chart or from the Object Tree. Current interaction supports applicable operations such as:

- moving the drawing;
- editing endpoints/geometry;
- style changes;
- lock/unlock;
- hide/show;
- duplication;
- deletion.

Line drawing supports constrained directional placement while the relevant modifier is held.

### 10.3 Drawing toolbar

The drawing toolbar itself has persistent ordering. Desktop users can reorder tools by drag and can move a focused tool with the implemented keyboard reorder shortcut. On narrow touch-oriented layouts, the header/toolbar favors horizontal panning instead of desktop drag-reordering.

### 10.4 Undo and redo

Undo/redo snapshots cover user drawings and compatible presentation-object state. Indicator presentation snapshots are restored only when they belong to the same active calculation identity; stale calculation objects are not revived across a different calculation.

### 10.5 Persistence

Drawings are saved through the server-backed drawing store. Browser storage is also used as a recovery/fallback path for compatible local drawing state.

Stored drawings are validated before use. Invalid recovered entries are separated from valid drawings instead of causing valid drawings to be discarded.

Persistence location details belong to [Local State](../operations/local-state.md).

## 11. Manual Review

### 11.1 Entry

Manual Review is opened from a calculation that has a valid persisted report identity. It opens as a separate browser document/tab under the report route.

If no valid report identity exists, or the persisted report cannot be found/loaded, the review page shows an inline failure state rather than fabricating a report.

### 11.2 Review surface

Manual Review presents a chronological event timeline based on finalized calculation/report data. Events are grouped by Tehran calendar day and organized by behavior families/subtypes.

The review surface provides:

- calculation metadata;
- behavior-family/subtype filters;
- date-range filtering;
- event-by-event True/False/Unselected review state;
- day-scoped bulk True/False actions for currently visible events;
- expandable finalized Bridge detail;
- copyable Bridge detail;
- a generated human-review report;
- copy/download of the review report.

Bridge detail is a display-only view of finalized supplied data. It does not infer a new behavior or Order identity from row position.

### 11.3 Review persistence

Human review selections persist locally per report identity/content identity. Filtering an event out of the current view does not reinterpret its underlying event data.

Review state is human annotation. It is not Engine state and is not fed back as a trading calculation decision.

### 11.4 Review navigation

Manual Review is intentionally independent of Chart interaction. Users return to the workstation by switching/closing browser tabs rather than by mutating the originating Chart calculation from the report.

## 12. FARAZ user experience

FARAZ UI is a market-data acquisition workflow, not a trading-calculation workflow.

### 12.1 Authentication/session state

The workspace visibly distinguishes connected, disconnected, waiting-for-login, rejected/expired, and error conditions where applicable.

When not connected, extraction controls remain unavailable. Sign-in is user-driven through the supported browser/session flow. The UI can refresh session status, open FARAZ in a browser, and sign out through supported controls.

Secret/session contents are never a user-facing trading result and must not be exposed in maintained documentation.

### 12.2 Acquisition modes

The exporter supports both:

- a previous-candle/count-oriented workflow;
- an explicit time-range workflow.

The current Chart context can supply sensible defaults, while the FARAZ workspace retains user-editable acquisition settings.

### 12.3 Extraction progress

While extraction is active the workspace exposes user-readable stage, elapsed time, packet/progress information, received-row/candle information, validation state, and bounded recent activity.

A running extraction can be cancelled through the explicit cancellation action.

### 12.4 Coverage decisions

If FARAZ cannot provide all requested source intervals after the normal recovery path, the UI does not silently present the request as fully successful.

Instead, the coverage decision dialog explains the unresolved source gap and asks the user to either:

- cancel without publishing an incomplete result; or
- explicitly continue from the first available source data when that option is available.

Focus moves into the decision dialog and keyboard Tab navigation is constrained to its decision controls while it is active.

### 12.5 Local RAW inventory and Chart update

The FARAZ workspace shows the local RAW inventory with sorting, refresh, and confirmed deletion actions.

Chart also exposes an update-data workflow for the currently loaded RAW resource. That workflow can check/repair gaps or obtain newer closed candles, shows staged progress, and reports success/warning/failure without inventing missing candles.

FARAZ acquisition and Chart update affect input data availability. They do not define trading semantics.

## 13. Algorithm reference workspace

The Algorithm workspace provides an in-app reading/navigation experience for algorithm-related reference content.

Current user-facing capabilities include:

- overview/family/type/reference navigation through URL hash state;
- search within the reference navigation;
- Bullish/Bearish presentation switching for supported mirrored content;
- English/Persian explanation presentation;
- collapsible/off-canvas navigation depending on viewport;
- copy of the current page in a reusable textual/rich form;
- export of the reference view through supported browser save/print flows.

Language, direction, and applicable navigation preferences persist locally.

The Algorithm workspace is a convenience reference surface. Canonical project authority remains governed by root AGENTS, project knowledge, current Source, and accepted Algorithm References.

## 14. UI state ownership

| UI-relevant state | Primary owner | User contract |
| --- | --- | --- |
| Active workspace | Browser UI | Restored when the saved workspace remains valid. |
| Selected chart/timeframe | Browser UI + tab URL | Valid chart identity/timeframe can survive refresh; explicit tab URL state takes precedence where present. |
| Visible pan/zoom range | Chart runtime | Presentation state; not the calculation-range authority. |
| Indicator form/range preferences | Browser UI | May restore for the same chart context; active calculated truth is not reconstructed from form state. |
| Active indicator result | Current calculation context | Cleared when incompatible chart/source/timeframe context changes. |
| Indicator visual overrides | Browser UI | Presentation-only customization; not trading semantics. |
| Drawings | Chart + server-backed local persistence | Restore with the chart; browser fallback may aid recovery. |
| Chart display preferences | Browser UI | Persist locally where current controls support it. |
| Workspace/object-tree preferences | Browser UI | Presentation organization only. |
| FARAZ exporter form/job identity | FARAZ UI | Persists locally enough to restore workflow state when still valid. |
| FARAZ authentication/session | FARAZ/server boundary | Connection state is visible; secret material is not UI trading state. |
| Manual Review decisions | Review browser state | Persist per report identity/content and remain human review annotations. |
| Serialized calculation cache | Local server | May accelerate repeated calculation requests; not UI or semantic authority. |
| Trading calculation/lifecycle state | Engine | Authoritative result source; never reconstructed by Chart preferences. |

## 15. Persistence UX

Users should expect the following current restoration behavior:

- valid workspace choice, selected chart identity, and chart timeframe can restore across refresh;
- chart-tab URL state can reopen a specific chart/timeframe independently of another tab;
- drawings are restored with their chart from supported persisted storage;
- chart/indicator presentation preferences can restore where the current UI explicitly persists them;
- indicator input form/range can restore, but a prior active calculation is not treated as live merely because its form values return;
- FARAZ exporter preferences and a still-valid acquisition job identity can restore;
- Algorithm language/direction/navigation preferences can restore;
- Manual Review True/False selections can restore for the same report identity.

Cache clearing is explicit and scoped. The UI distinguishes calculation cache, browser storage/cache, IndexedDB, drawings, and—only for the broadest clear operation—local FARAZ session state.

Operational directory details are intentionally delegated to [Local State](../operations/local-state.md).

## 16. Navigation and routing

The primary in-application navigation model switches among Chart, FARAZ, and Algorithm workspaces inside one workstation shell.

Routing/state behavior includes:

- Chart identity/timeframe represented in query state where applicable;
- Algorithm reference navigation represented in hash state;
- Manual Review represented by a separate report path opened in another tab/document.

Unknown or stale persisted workspace/navigation values fall back to valid current UI state rather than being treated as authority.

Not every navigation control represents a primary workspace; contextual actions and panels remain owned by their feature.

## 17. Loading, progress, and completion feedback

### Initial/data loading

Loading a chart resource presents an explicit loading state until candle data is available or the request fails.

### Indicator calculation

Indicator calculation has dedicated progress presentation driven by current execution events. The user can see active/completed/failed stages and later inspect calculation activity/timing information.

### Chart data update

Updating the current RAW resource uses a focused progress dialog with staged fetch/compare/save/verification feedback and summary metrics.

### FARAZ extraction

FARAZ extraction reports running stage, elapsed/progress information, validation, activity logs, completion, cancellation, and unresolved-coverage decisions.

### Manual Review

Manual Review begins with a loading state and transitions to the rendered report or a clear inline load/render failure.

### Notifications

Transient success/info/error notifications use semantic presentation. Error notifications use alert semantics; non-error notifications use status semantics. Hovering an active toast pauses its dismissal timer so the message remains readable.

## 18. Error handling and recovery UX

UI error handling aims to preserve user context and present an actionable next step.

Examples of current behavior include:

- invalid indicator prerequisites/ranges are rejected before calculation;
- missing/unavailable data is reported instead of producing an empty success;
- server/Engine calculation failures update indicator status, runtime/error information, and user notification;
- FARAZ authentication/acquisition errors keep the workflow recoverable and expose concise user-readable messages;
- unresolved FARAZ source gaps require explicit user decision;
- malformed drawing persistence does not discard valid recovered drawings;
- missing Manual Review reports remain an inline report error;
- destructive RAW deletion requires explicit confirmation.

A runtime health control reflects recorded application errors and provides access to the current error log. User-facing summaries intentionally avoid dumping sensitive credential/session implementation details.

## 19. Responsive layout

Responsive behavior is adaptive rather than a separate product mode.

Current layout contracts include:

- the shared header can become horizontally scrollable when controls no longer fit;
- Chart identity/OHLC and status information reflow or simplify on narrower viewports;
- Object Tree changes from a desktop panel model to a viewport-bound overlay;
- drawing editing controls and dialogs reduce/reflow to remain reachable;
- the Algorithm navigation becomes an off-canvas interaction on narrow screens;
- Manual Review changes from sidebar/content columns to a stacked layout and compacts event rows;
- FARAZ tables/panels and workflow controls adapt/scroll as necessary rather than changing acquisition meaning;
- anchored popovers are positioned against the viewport and can flip to remain visible.

Exact breakpoint values and CSS measurements are implementation details unless a future product contract explicitly makes them normative.

## 20. Keyboard and pointer interaction

Important current interaction contracts include:

- normal pointer pan/zoom and chart inspection;
- pointer dragging for selected-range handles;
- Left/Right Arrow adjustment for focused range handles;
- drawing creation, selection, drag/edit, and object manipulation;
- desktop drag-reordering of drawing tools;
- keyboard drawing-toolbar reorder with the implemented modifier plus Left/Right Arrow;
- Escape dismissal/cancellation for supported transient dialogs/pickers/workflows;
- focus restoration when several dialogs/popovers close;
- Algorithm keyboard/navigation focus management;
- keyboard-contained FARAZ coverage decision controls.

Pointer-only convenience must not redefine underlying Chart coordinates; drawing/range interactions resolve back to canonical candle time/price state.

## 21. Accessibility

**Status: PARTIALLY VERIFIED.**

Current Source and UI contract tests provide evidence for:

- semantic button/control labels;
- dialog roles and modal labeling;
- `aria-expanded`, `aria-pressed`, `aria-live`, progressbar, and status/alert state where applicable;
- hidden inactive workspace controls being made inert and `aria-hidden`;
- visible focus styling;
- keyboard-adjustable range endpoints;
- focus movement/restoration for several modal/popover flows;
- keyboard containment in the FARAZ coverage decision;
- screen-reader-only labels/text where needed;
- reduced-motion handling for users requesting less animation.

This document does **not** claim comprehensive WCAG conformance, full screen-reader parity, or complete cross-browser assistive-technology verification without a dedicated current accessibility validation run.

## 22. Performance and LOD UX

Chart can reduce display density for large/zoomed-out datasets using presentation-only level-of-detail aggregation.

The contract is:

- the original candle collection remains canonical for calculation, export, exact date/OHLC lookup, drawings, and hit testing;
- display LOD changes only what is rendered for performance;
- raw-time-to-screen mapping preserves interaction with omitted display candles;
- display-density mode uses hysteresis/stability behavior to avoid unnecessary mode flapping during gestures;
- active gesture handling avoids changing density mode mid-interaction when doing so would destabilize the view.

No LOD or rendering optimization may silently redefine Engine trading semantics.

## 23. Visual design and theming

The current application is intentionally **light-mode** at the global shell level. Chart settings provide user control over chart/presentation properties such as canvas/axis colors, candle colors, time format, scale borders, and crosshair visibility; these are not a global dark/system-theme switch.

Stable visual principles include:

- chart-first hierarchy;
- restrained workstation chrome around the data surface;
- semantic success/warning/error states;
- clear distinction between user drawings and generated trading-result objects;
- overlays/panels layered above Chart without becoming trading authority;
- consistent focus and selected states;
- reduced motion when requested by the operating/browser preference.

Transient CSS measurements, exact colors, animation durations, and component dimensions are implementation details unless intentionally promoted to a product contract.

## 24. Frontend/backend boundaries

### 24.1 Browser ↔ local server

From the user's perspective, Chart initiates local requests for inventory/candles, drawings, calculation, cached reports, templates, transfers, and FARAZ workflows; it receives results, status, progress, or errors.

Transport/process details belong to [Technical Architecture](technical-architecture.md).

### 24.2 Chart ↔ Engine

The critical semantic boundary is:

**Chart presents finalized trading results. Engine owns trading truth.**

Chart may:

- choose/request a calculation context;
- convert finalized result rows into visual objects;
- hide/show/style those objects;
- provide human review/presentation tools.

Chart must not:

- independently calculate a different trading decision;
- repair a disputed Engine state in presentation code;
- reinterpret lifecycle/Order truth to make a visual result look preferable.

If future frontend Source starts making a decision that belongs to Engine, that is an architectural mismatch to report—not a valid UI contract to normalize here.

### 24.3 FARAZ boundary

FARAZ UI owns user interaction for acquiring/verifying source market data. It does not own the trading interpretation of those candles.

## 25. UI/UX invariants

The maintained UI/UX contract requires:

- inactive workspaces do not leak active controls into the user's interaction path;
- visible viewport and calculation range remain distinct concepts;
- result presentation is derived from finalized supplied result data;
- UI appearance changes do not mutate trading semantics;
- user drawings remain user-owned annotations;
- display LOD does not change authoritative source/calculation data;
- Manual Review remains human classification/presentation, not trading feedback;
- FARAZ remains acquisition UX rather than algorithm UX;
- cache reuse never becomes semantic authority;
- secrets/session material is not exposed as UI diagnostic content;
- destructive local-data actions remain explicit;
- historical screenshots/audits do not override live UI behavior.

## 26. Review and update triggers

Review this document when any of the following changes materially:

- a major user workflow is introduced or removed;
- workspace behavior/navigation changes;
- selected-range interaction or user-visible range semantics change;
- result presentation ownership changes;
- drawings/annotation contracts change;
- Manual Review changes materially;
- FARAZ user interaction changes materially;
- persistence/restoration expectations change;
- loading/progress/error behavior changes substantially;
- responsive behavior changes enough to alter control accessibility;
- keyboard/accessibility contracts change;
- LOD/display optimization begins affecting user-visible semantic behavior;
- Chart starts owning logic that should belong to Engine.

Do **not** rewrite this document merely because:

- an internal frontend component/file is added or renamed;
- frontend packages are reorganized;
- tests increase;
- framework/runtime versions change;
- repository revisions or hashes change;
- CSS is refactored without changing interaction/layout contracts;
- an Engine implementation file changes while the final UI contract remains unchanged.

## 27. Future-proof acceptance

This reference remains valid under these ordinary evolutions:

- **New internal Chart component:** no update when behavior/ownership is unchanged.
- **Frontend reorganization:** no update when user contracts remain unchanged.
- **New major workflow:** review/update required.
- **Engine implementation change:** no automatic UI/UX rewrite when presentation contract is unchanged.
- **Selected-range behavior change:** review/update required.
- **CSS-only refactor:** no conceptual rewrite when layout/interaction behavior is unchanged.
- **Responsive contract change:** review/update required.
- **Historical screenshot disagreement:** live Source/runtime wins.
- **Frontend reinterpretation of Engine truth:** report architectural mismatch.
- **New accessibility interaction:** update when it changes the maintained user contract.

## 28. Related maintained documentation

- Root operating contract: [`AGENTS.md`](../../../AGENTS.md)
- Documentation ownership/lifecycle: [Documentation Governance](../documentation-governance.md)
- Maintained documentation navigation: [Engineering Documentation](../README.md)
- System/process boundaries: [Technical Architecture](technical-architecture.md)
- Local persistence/storage: [Local State](../operations/local-state.md)
- AI engineering procedure: [AI Engineering Workflow](../ai/engineering-workflow.md)
- Repository overview: [root README](../../../README.md)

Detailed trading rules belong to the current canonical trading knowledge and accepted Algorithm References discovered according to root AGENTS.

## 29. Historical provenance

The previous file at this maintained path was primarily a dated UI/UX audit snapshot. It contained useful evidence but also mutable counts, versions, pixel measurements, dated runtime observations, screenshot-era conclusions, test-result snapshots, and historical defect/debt reporting.

Its unique body is preserved byte-for-byte at [the archived UI/UX audit](../../archive/documentation/ui-ux-audit-2026-09-22.md).

That archive may explain past observations. It is **HISTORICAL evidence**, not Current UI/UX authority.
