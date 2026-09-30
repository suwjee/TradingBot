# Complete Project Engineering Audit, Architecture Reconstruction, UI/UX Technical Reference, Security Review, and AI Operational Documentation

I want you to fully understand this project before making any change, fix, refactor, optimization, architectural modification, UI modification, dependency change, configuration change, or new development.

You must first perform a **complete, deep, systematic, engineering-level review of the entire project**.

The purpose of this task is not to modify the application.

The purpose is to reconstruct a complete and verifiable engineering understanding of the current project and create technical reference documentation that future engineers and AI coding agents can use without repeatedly reverse-engineering the entire repository.

You must become familiar with the project's:

* complete repository structure
* architecture
* backend
* frontend
* UI/UX
* runtime behavior
* startup sequence
* data flow
* state management
* lifecycle rules
* ownership rules
* APIs and bridges
* configuration
* environment handling
* build system
* deployment
* security
* testing
* dependencies
* performance architecture
* assets
* coding patterns
* frontend pages
* routes
* tabs
* screens
* shared components
* page-specific components
* styling
* design system
* error handling
* logging
* generated artifacts
* CI/CD
* infrastructure
* operational rules

The final result must be a **complete Digital Engineering Map of the current project**.

---

# Mandatory Codex Desktop Plugin Requirement

This audit must use the following installed Codex Desktop plugins:

1. `Superpowers`
2. `Codex Security`

Both plugins have specific responsibilities defined below.

They are not interchangeable.

Neither plugin replaces direct source-code analysis.

The **current repository source code remains the primary source of truth**.

---

# Source-of-Truth Hierarchy

When information conflicts, use the following hierarchy:

1. Current project-owned source code
2. Directly observed runtime behavior
3. Current configuration and package manifests
4. Lock files
5. Tests, fixtures, regression baselines, and golden files
6. Build and deployment configuration
7. Existing project documentation
8. Superpowers workflow conclusions
9. Codex Security findings
10. General framework knowledge or conventions

General programming knowledge must never override evidence from the current project.

Plugin output is supporting evidence, not an authoritative replacement for source inspection.

---

# Mandatory Superpowers Responsibilities

`Superpowers` is the **audit orchestration and completeness-control layer**.

Use Superpowers from the beginning of the task.

Superpowers must:

## 1. Build the Audit Execution Plan

Before detailed analysis begins, use Superpowers to divide the complete audit into logical workstreams.

At minimum track:

* repository inventory
* backend architecture
* frontend architecture
* configuration
* dependencies
* runtime
* build
* deployment
* security
* performance
* testing
* UI/UX
* individual page analysis
* documentation generation
* coverage verification
* final cross-check

The plan must cover the entire repository.

Do not treat the plan as a substitute for reading source files.

---

## 2. Maintain a Completion Checklist

Superpowers must maintain a logical checklist of all audit stages.

Each stage must be tracked as one of:

* Not Started
* In Progress
* Complete
* Partially Verified
* Blocked
* Not Applicable

A stage may only be marked `Complete` when its evidence has actually been inspected.

---

## 3. Prevent Large-Repository Coverage Gaps

If the repository is large, Superpowers must divide analysis into manageable waves.

Example waves may include:

* root/configuration
* backend
* frontend
* shared modules
* tests
* assets
* infrastructure
* security
* UI/UX
* documentation

However, every project-owned file must eventually appear in the audit inventory.

No file may disappear merely because the context is large.

---

## 4. Track Cross-Stage Dependencies

Superpowers must identify when one stage cannot be finalized before another.

Examples:

* page documentation cannot be finalized before routes and entry components are known
* dependency analysis cannot be finalized before manifests and imports are reviewed
* security documentation cannot be finalized before Codex Security findings are validated
* deployment architecture cannot be finalized before build/runtime configuration is understood

---

## 5. Track Open Questions and Unverified Areas

Superpowers must maintain a list of:

* unresolved ambiguities
* conflicting evidence
* unverified runtime behavior
* unverified binary contents
* missing external services
* incomplete configuration
* files whose role is uncertain

Never silently convert uncertainty into assumptions.

---

## 6. Perform Audit Checkpoints

After each major workstream, Superpowers must verify:

* whether all expected files were inspected
* whether discovered dependencies were followed
* whether related files were inspected
* whether documentation is traceable to source
* whether a later discovery invalidates an earlier conclusion

---

## 7. Perform Final Completeness Review

Before this audit may be declared complete, Superpowers must independently compare:

* repository inventory
* reviewed file list
* frontend page inventory
* route inventory
* backend subsystem inventory
* documentation sections
* security findings
* unverified areas
* required outputs

Superpowers must actively look for missing coverage.

Do not use Superpowers only for initial planning.

It must also participate in final completeness verification.

---

# What Superpowers Must NOT Do

Superpowers must not:

* invent project architecture
* infer missing files
* assume framework behavior without source evidence
* modify application source during this audit
* replace manual source-code analysis
* silently mark incomplete stages complete
* resolve ambiguity through speculation
* treat its own workflow output as technical proof

Technical claims must still be supported by the repository.

---

# Mandatory Codex Security Responsibilities

`Codex Security` is the **specialized security-analysis layer**.

Use Codex Security only after the initial repository inventory and major architecture boundaries are understood.

This allows the security scan to be interpreted in the real project context.

Codex Security must be used in **scan/analyze/investigate mode only** during this audit.

Do not automatically apply security fixes.

---

## 1. Security Scan Scope

Use Codex Security to inspect applicable project areas including:

* application source
* backend code
* frontend code
* configuration
* authentication
* authorization
* session handling
* token handling
* secrets
* environment variables
* API boundaries
* filesystem operations
* file uploads
* file downloads
* path handling
* command execution
* subprocess execution
* database access
* deserialization
* HTML rendering
* template rendering
* dynamic evaluation
* network requests
* WebSocket handling
* CORS
* CSP
* cookies
* security headers
* cryptography usage
* private/public keys
* webhook handling
* CI/CD
* Docker
* reverse proxy configuration
* deployment configuration
* dependency risk
* dangerous third-party packages
* insecure defaults
* privilege boundaries
* trust boundaries

Only inspect categories actually applicable to the project.

---

## 2. Vulnerability Classes

Where applicable, Codex Security should specifically investigate risks such as:

* injection
* SQL injection
* command injection
* template injection
* XSS
* DOM XSS
* path traversal
* unsafe file access
* insecure direct object access
* authorization bypass
* authentication weaknesses
* unsafe deserialization
* unsafe `eval`
* unsafe dynamic code execution
* server-side request forgery
* insecure CORS
* insecure CSP
* secret leakage
* hardcoded credentials
* insecure token storage
* session weaknesses
* sensitive-data exposure
* dependency vulnerabilities
* unsafe subprocess use
* insecure file upload
* insecure file download
* unsafe temporary-file handling
* insecure cryptographic use

Do not report a vulnerability merely because a dangerous-looking function exists.

The complete data flow and reachable usage must be considered.

---

## 3. Security Findings Must Be Manually Validated

Every important finding produced by Codex Security must be checked against the actual source code.

For every finding classify it as:

* `Confirmed`
* `Likely but not fully verified`
* `False Positive`
* `Not Applicable`
* `Not verifiable from current source`

Do not copy raw scanner findings directly into final documentation without validation.

---

## 4. Security Finding Evidence

For each confirmed or unresolved security finding, document:

* finding title
* affected file
* affected function/class/component
* relevant source location
* entry point
* data source
* data flow
* trust boundary
* dangerous operation
* existing validation or protection
* realistic impact
* reachability
* Codex Security finding status
* manual validation status
* remediation direction

Do not implement the remediation during this audit.

---

## 5. Dependency Security

Codex Security must inspect dependency risk where supported.

Cross-check findings against:

* package manifests
* lock files
* imported libraries
* actual source usage
* version constraints

Clearly distinguish:

`Installed dependency`

from:

`Dependency actually used by the project`

and:

`Potential dependency risk`

from:

`Confirmed exploitable project path`.

---

## 6. Sensitive Data Protection

Codex Security may inspect sensitive configuration, but real secret values must never appear in:

* chat output
* documentation
* security findings
* examples
* tables
* logs copied into documentation

Replace real secret values with:

`[REDACTED_SECRET]`

or identify only the variable name:

`Environment variable: API_KEY`

Never reproduce passwords, tokens, private keys, credentials, session secrets, signing keys, or cloud secrets.

---

## 7. Security Reconciliation Pass

After the normal source security review and Codex Security scan are both complete, compare them.

Create three logical groups:

### Manual-only findings

Issues discovered through direct source review but not reported by Codex Security.

### Codex-Security-only findings

Issues reported by Codex Security that were not initially noticed manually.

### Overlapping findings

Issues independently identified by both.

Then validate all three groups against source code.

---

## 8. Final Security Pass

Before final delivery, use Codex Security again where useful to review unresolved high-impact security areas.

Do not declare security review complete while an important scanner finding remains unexplained.

---

# What Codex Security Must NOT Do

Codex Security must not:

* automatically fix vulnerabilities
* modify source files
* modify dependencies
* update package versions
* rotate secrets
* expose secrets
* rewrite configuration
* change authentication
* change authorization
* change deployment
* replace direct source review
* cause an unvalidated scanner result to be documented as fact

---

# Plugin Conflict Rule

If Superpowers, Codex Security, existing documentation, or source analysis disagree:

**the current source code and verified runtime behavior win.**

Document the disagreement when relevant.

Do not hide it.

---

# Plugin Availability Rule

Before beginning the audit, verify that:

* Superpowers is available
* Codex Security is available

If either plugin is unavailable, explicitly report:

`Required plugin unavailable: <plugin name>`

Do not falsely claim that the plugin was used.

Do not claim `Full project review completed` until the plugin requirement has either been satisfied or explicitly documented as an accepted limitation.

---

# Fundamental Rule

Do not assume anything based only on:

* file names
* folder names
* common project patterns
* framework conventions
* visual appearance
* previous knowledge
* similar applications
* comments without supporting implementation
* package names
* naming conventions
* documentation that conflicts with source
* plugin output

Every technical statement in the final documentation must be based on actual project evidence.

If something cannot be confirmed, explicitly write:

`Not verified from current source`

If runtime verification was required but unavailable, use:

`Not verified from current runtime`

If a dependency or external system cannot be accessed, use:

`External integration not verified`

If ambiguity materially affects accuracy:

**ask before making an assumption.**

---

# Audit Modification Policy

The application itself must not be changed during this audit.

Application source code is read-only for this task.

Allowed activities include:

* reading
* searching
* parsing
* analyzing
* tracing
* indexing
* documenting
* running read-only inspection commands
* running safe tests
* running safe linting
* running safe builds when required for verification
* running the application locally when required for runtime verification
* inspecting generated output
* using Superpowers
* using Codex Security

The only project files that may be intentionally created or modified are the required audit documentation files and, if necessary, the existing `AGENTS.md` or `AGENT.md`.

Do not make behavior changes.

---

# Repository Integrity Protection

Before starting:

1. inspect current Git status if Git is available
2. record pre-existing modified/untracked files
3. never overwrite unrelated user changes
4. do not use destructive Git operations
5. do not use `git reset --hard`
6. do not use destructive `git clean`
7. distinguish pre-existing changes from audit-generated files

After finishing:

compare repository state against the initial state.

Only expected documentation changes may remain.

If tests/builds generate temporary artifacts, do not confuse them with project-owned source.

Never delete a pre-existing user file merely to restore repository cleanliness.

---

# Audit Evidence Standard

Every major conclusion must be traceable.

Where practical record:

* path
* file
* module
* class
* function
* component
* route
* selector
* CSS variable
* configuration key
* package
* manifest entry
* relevant line or line range

Important architectural claims should be supported by more than a file name.

Trace implementation relationships.

---

# Documentation Language Requirement

All generated documentation and the final audit summary must use:

**clear, simple, fluent, readable, professional technical English.**

Technical identifiers must remain exactly as implemented.

Do not translate:

* file names
* folder names
* module names
* package names
* functions
* classes
* variables
* routes
* API names
* components
* selectors
* CSS variables
* page identifiers
* tab identifiers
* configuration keys

Avoid marketing language.

Avoid vague wording.

Use concise language where possible and detail where necessary.

---

# Required Outputs

At the end of the audit, the following files must exist and be complete:

`/docs/TradingBot_Technical_Architecture.md`

`/docs/TradingBot_UI_UX_Technical_Reference.md`

Also review:

`/AGENTS.md`

or, if the real project uses:

`/AGENT.md`

use that file instead.

Do not create both.

Do not create a duplicate using the wrong filename.

---

# Stage 0 — Superpowers Audit Initialization

Use Superpowers before deep analysis.

Create an audit plan.

The plan must cover every stage in this prompt.

Establish:

* audit workstreams
* file-review strategy
* large-file strategy
* dependency-following strategy
* frontend page-discovery strategy
* security scan point
* documentation strategy
* final verification strategy

Do not modify source code.

---

# Stage 1 — Baseline Repository Snapshot

Before detailed interpretation, record the current repository state.

Determine where possible:

* repository root
* Git repository presence
* current branch
* current Git status
* root files
* top-level directories
* package managers
* languages
* apparent source roots
* documentation roots
* test roots
* build roots
* deployment roots

Do not infer responsibilities yet.

This stage is inventory, not interpretation.

---

# Stage 2 — Complete Repository Inventory

Scan the entire repository/workspace.

Discover every relevant:

* folder
* subfolder
* source file
* backend file
* frontend file
* module
* package
* page
* route
* tab
* screen
* view
* layout
* component
* hook
* service
* utility
* helper
* API handler
* bridge
* pipeline
* engine
* worker
* state manager
* model
* schema
* type
* DTO
* configuration file
* environment file
* build file
* deployment file
* script
* test
* fixture
* baseline
* snapshot
* documentation file
* stylesheet
* asset
* font
* icon
* image
* SVG
* JSON file
* YAML file
* TOML file
* XML file
* package manifest
* lock file
* CI/CD file
* Docker file
* reverse proxy configuration
* editor configuration
* linter configuration
* formatter configuration
* database file
* migration
* seed
* generated file
* legacy file
* deprecated file
* backup file
* hidden file
* dotfile

Do not omit a project-owned file because it is large, old, unusual, complex, hidden, generated, or difficult to understand.

---

# Stage 3 — File Classification Manifest

Classify discovered files into categories such as:

* Backend
* Frontend
* Shared
* Configuration
* Build
* Deployment
* Security-sensitive
* Test
* Fixture
* Baseline
* Asset
* Documentation
* Generated
* Third-party
* Binary
* Legacy
* Unknown

Also track review state.

For each project-owned file, eventually record:

* path
* category
* purpose
* reviewed status
* verification status
* related subsystem

The final documentation must make coverage auditable.

---

# Stage 4 — Mandatory Review of Project-Owned Files

Every project-owned file must be reviewed.

At minimum inspect security/configuration files including:

* `.env`
* `.env.*`
* environment configuration
* authentication configuration
* authorization configuration
* session configuration
* token configuration
* database configuration
* OAuth configuration
* certificate configuration
* key configuration
* cloud configuration
* webhook configuration
* CORS
* CSP
* security headers
* `.gitignore`
* `.gitattributes`
* `.gitmodules`
* `.vscode`
* CI/CD
* GitHub Actions
* GitLab CI
* Dockerfile
* Docker Compose
* Nginx
* Apache
* build configuration
* package manifests
* lock files
* linter configuration
* formatter configuration
* testing configuration
* migrations
* seeds
* shell scripts
* PowerShell
* batch scripts
* workers
* services
* runtime configuration

Do not classify files as unimportant merely from their names.

---

# Stage 5 — Sensitive File Handling

Sensitive files must still be reviewed.

Never expose real secret values.

Determine:

* where each secret is configured
* how it is loaded
* which module consumes it
* whether it is hardcoded
* whether it comes from environment variables
* whether it is passed to frontend code
* whether it enters logs
* its architectural role
* its lifecycle
* storage risk
* deployment implications

Redact actual values.

---

# Stage 6 — Very Large Files

Large files may not be skipped.

Divide them into logical sections.

Inspect all important:

* imports
* constants
* configuration
* types
* classes
* functions
* handlers
* state
* side effects
* initialization
* data flow
* integration points
* public interfaces
* helpers
* serialization
* errors
* cleanup
* caching
* performance-sensitive paths

Do not write:

`File too large, skipped`

---

# Stage 7 — Binary, Generated, and Third-Party Content

For binary files:

* identify type
* inspect metadata
* find references
* determine project role
* mark internal contents `Unverified` only where inspection is not practical

For third-party directories such as:

* `node_modules`
* virtual environments
* caches
* package caches
* build caches

do not inspect every third-party file line by line.

Instead use:

* manifests
* lock files
* imports
* source usage
* build configuration

Every custom project-owned file remains in scope.

---

# Stage 8 — Complete Repository Tree

Create a complete real repository tree inside:

`/docs/TradingBot_Technical_Architecture.md`

Use the actual project.

Do not create a hypothetical tree.

Clearly identify generated or third-party directories where useful.

---

# Stage 9 — Folder-by-Folder Reference

For every important folder document:

* full path
* category
* purpose
* file types
* architectural responsibility
* incoming dependencies
* outgoing dependencies
* production importance
* development-only status
* generated status
* configuration role
* UI role
* backend role
* calculation role
* testing role

---

# Stage 10 — File-by-File Technical Reference

For every important project file document:

* full path
* file type
* category
* purpose
* responsibilities
* main classes
* main functions
* inputs
* outputs
* state
* dependencies
* consumers
* side effects
* related files
* runtime role
* whether independently modifiable
* likely breakage if changed
* relevant tests
* relevant baselines
* security relevance
* performance relevance

The documentation must allow an engineer to understand a file's responsibility without opening it.

---

# Stage 11 — Dependency Map

Determine actual module relationships.

Identify:

* imports
* dependency direction
* entry points
* leaf modules
* shared utilities
* circular dependencies
* backend/frontend boundaries
* cross-layer dependencies
* dynamic imports
* generated dependencies
* plugin/runtime loading
* service boundaries

Use Mermaid diagrams where useful.

Only include verified relationships.

---

# Stage 12 — Technology Stack

Identify technologies actually used.

For each relevant technology document:

* name
* version if verifiable
* purpose
* files using it
* runtime role
* build role
* whether it is actually used
* whether it appears installed but unused

Inspect:

* languages
* runtimes
* frameworks
* libraries
* package managers
* bundlers
* transpilers
* databases
* ORMs
* API libraries
* serialization libraries
* validation
* logging
* date/time
* Decimal/math
* testing
* chart libraries
* UI libraries
* styling systems

---

# Stage 13 — Architecture Reconstruction

Extract architecture from source code.

Do not assign pattern names without evidence.

Where genuinely present, explain patterns such as:

* Pipeline Architecture
* Layered Architecture
* Event-Driven Architecture
* State Machine
* Detector Pattern
* Bridge
* Adapter
* Strategy
* Repository
* Functional Core
* Shared Utility Layer

Explain actual implementation rather than labels.

---

# Stage 14 — Runtime and Startup

Determine:

* primary entry point
* backend entry point
* frontend entry point
* configuration loading
* module loading
* dynamic loading
* service initialization
* bridge initialization
* worker initialization
* database initialization
* dependency initialization
* frontend boot sequence
* startup order
* shutdown behavior where present

Trace the real sequence.

---

# Stage 15 — Runtime Verification

Where safe and practical, verify important architectural assumptions by executing the project.

You may:

* run safe builds
* run safe tests
* run safe linting
* launch development/runtime processes
* inspect console output
* inspect errors
* inspect generated network/API behavior
* inspect visible UI using available Codex Desktop runtime capabilities

Do not modify project behavior.

Distinguish:

`Verified from source`

from:

`Verified from runtime`

If runtime verification is not possible, state that explicitly.

---

# Stage 16 — Data Flow

Document important end-to-end flows.

Trace:

* input
* parsing
* validation
* normalization
* transformation
* processing
* business logic
* state transitions
* calculation
* reconciliation
* persistence
* serialization
* API/bridge transport
* frontend consumption
* rendering

For each stage identify:

* producer
* consumer
* input
* output
* owner

---

# Stage 17 — API and Communication Interfaces

Inspect:

* REST
* HTTP
* WebSocket
* IPC
* bridge
* CLI
* subprocess
* stdin/stdout
* workers
* JSON protocol
* streams
* events

For each interface document:

* entry point
* method
* request shape
* response shape
* validation
* error behavior
* authentication
* authorization
* producer
* consumer
* lifecycle

---

# Stage 18 — Data Structures

Inspect important:

* classes
* dataclasses
* interfaces
* types
* schemas
* DTOs
* models
* domain objects
* state objects
* result objects
* serialization structures

Document:

* purpose
* important fields
* creator
* consumer
* mutation
* lifecycle
* serialization

---

# Stage 19 — State, Lifecycle, and Ownership

Document:

* state creation
* mutation
* persistent state
* temporary state
* global state
* local state
* cache state
* lifecycle boundaries
* ownership rules
* reset behavior
* cleanup behavior
* invalidation
* cross-module ownership
* concurrency implications where applicable

State ownership must be explicit.

---

# Stage 20 — Error Handling and Logging

Inspect:

* exceptions
* validation errors
* runtime errors
* calculation errors
* API errors
* frontend errors
* user-visible errors
* logging
* telemetry
* retries
* recovery
* fail-fast behavior
* fallback behavior
* swallowed errors
* error boundaries

Trace how errors move through the application.

---

# Stage 21 — Performance Architecture

Inspect performance-sensitive paths including:

* loops
* nested loops
* repeated scans
* repeated parsing
* repeated conversion
* repeated serialization
* repeated I/O
* unnecessary copying
* expensive frontend rendering
* large lists
* large tables
* chart updates
* caching
* indexing
* lookup tables
* binary search
* memoization
* batching
* lazy evaluation
* concurrency
* workers

Where reasonably provable, document complexity such as:

* O(1)
* O(log N)
* O(N)
* O(N log N)
* O(N²)

Do not invent complexity.

Document existing optimization techniques.

---

# Stage 22 — Coding Conventions

Extract actual conventions for:

* naming
* modules
* classes
* functions
* constants
* typing
* comments
* docstrings
* imports
* dependency direction
* utilities
* serialization
* errors
* logging
* version metadata
* modification timestamps
* test naming

---

# Stage 23 — Manual Security Review

Before relying on Codex Security findings, manually inspect security architecture.

Review applicable:

* trust boundaries
* user input
* path handling
* filesystem access
* command execution
* subprocesses
* SQL
* templating
* HTML rendering
* deserialization
* authentication
* authorization
* CORS
* CSP
* cookies
* sessions
* secrets
* environment variables
* credentials
* key management
* dependency exposure
* file upload/download
* external requests

Record source-supported findings only.

---

# Stage 24 — Codex Security Scan

Now run the mandatory Codex Security review.

Codex Security must analyze relevant source, configuration, and dependencies.

Do not allow it to modify the project.

Capture its findings for manual validation.

---

# Stage 25 — Security Finding Validation

Review every meaningful Codex Security result against source.

For each finding determine:

* confirmed
* likely
* false positive
* not applicable
* unverified

Determine actual reachability and impact.

Never present unvalidated scanner output as fact.

---

# Stage 26 — Security Architecture Reference

Inside:

`TradingBot_Technical_Architecture.md`

include a dedicated security section covering:

* security architecture
* trust boundaries
* sensitive modules
* authentication
* authorization
* secrets
* environment handling
* file handling
* command execution
* dependency security
* browser/frontend security
* CI/CD security
* deployment security
* confirmed findings
* unresolved findings
* false-positive notes where useful
* recommended future remediation areas

Do not implement fixes.

---

# Stage 27 — Testing Architecture

Inspect:

* unit tests
* integration tests
* regression tests
* E2E tests
* fixtures
* baselines
* snapshots
* golden files
* manual validation
* CI tests
* mocks
* test utilities

Map tests to subsystems.

Identify unprotected critical code.

---

# Stage 28 — Build and Deployment Architecture

Inspect:

* build commands
* package scripts
* bundlers
* compilers
* environment selection
* build-time variables
* release artifacts
* Docker
* reverse proxies
* CI/CD
* deployment files
* runtime configuration
* production entry points
* static asset generation
* source maps
* migrations
* startup commands

Document what is verified and what depends on unavailable external systems.

---

# Stage 29 — Backend Technical Reference File

Write backend and architecture findings into:

`/docs/TradingBot_Technical_Architecture.md`

It must include at minimum:

1. Executive Technical Overview
2. Audit Scope & Verification Method
3. Repository Snapshot
4. Complete Repository Tree
5. Folder-by-Folder Reference
6. File-by-File Reference
7. Technology Stack
8. Runtime Architecture
9. Startup Sequence
10. Module Dependency Map
11. Backend Architecture
12. Frontend/Backend Boundary
13. Data Flow
14. Core Domain Objects
15. APIs / Bridges / Interfaces
16. State Management
17. Lifecycle & Ownership
18. Serialization
19. Error Handling
20. Logging
21. Configuration
22. Build System
23. Deployment
24. Performance Architecture
25. Caching & Indexing
26. Coding Conventions
27. Testing Architecture
28. Security Architecture
29. Security Findings
30. Technical Debt
31. Architecture Risks
32. Change Impact Map
33. Where To Make Changes
34. Dependency Impact Reference
35. Extension Guidelines
36. Refactor Safety Rules
37. Production-Critical Files
38. Development-Only Files
39. Generated Files
40. Sensitive Configuration Reference
41. Runtime Verification Results
42. Unverified Areas
43. Complete File Responsibility Matrix

---

# Stage 30 — Frontend Technology Stack

Inspect:

* frontend framework
* rendering library
* router
* state management
* CSS approach
* component library
* icons
* animations
* chart library
* visualization
* forms
* utilities
* font loading
* asset handling
* API client
* caching
* frontend build tools

Versions must only be documented when verifiable.

---

# Stage 31 — Complete Page / Tab / Screen Inventory

Identify every user-facing:

* page
* tab
* screen
* view
* tool
* workspace
* dashboard section
* route
* nested route
* major functional frontend area

Examples such as `Chart`, `Faraz Exporter`, or `Manual Review` are only examples.

Discover the actual project dynamically.

No user-facing page may be omitted.

---

# Stage 32 — Separate Reference for Every Page

Every discovered page, tab, screen, or major frontend feature must have a dedicated subsection inside:

`/docs/TradingBot_UI_UX_Technical_Reference.md`

Do not combine unrelated pages into a generic frontend description.

---

# Stage 33 — Mandatory Per-Page Analysis

For every page document:

## Identity

* page name
* route
* URL
* route key
* navigation entry
* parent layout
* entry component
* source files

## Purpose

* purpose
* workflow
* supported user actions

## Source Map

* page file
* child components
* styles
* hooks
* state
* services
* API clients
* helpers
* assets
* icons
* dialogs
* utilities

## Component Tree

Create the real component hierarchy.

## Layout

Document:

* rows
* columns
* regions
* widths
* heights
* scrolling
* fixed areas
* sticky areas
* overlays
* resize behavior

## Header

Document page-specific header behavior.

## Sidebar

Document page-specific sidebar behavior.

## Footer / Status Bar

Document where applicable.

## Toolbar and Controls

Document:

* buttons
* menus
* filters
* selectors
* toggles
* inputs
* date controls
* context menus

## Data Flow

Trace data from source to rendering.

## Backend Dependencies

Identify all related backend services/modules/interfaces.

## State

Document:

* local
* global
* URL
* cached
* persisted
* temporary

## Styling

Document:

* surfaces
* colors
* fonts
* sizes
* weights
* borders
* radius
* shadows
* spacing
* tokens

## Icons

Document icon usage.

## Animation

Document transitions and motion.

## Dialogs

Document dialogs/modals/drawers.

## Tables

Document table behavior where applicable.

## Charts

Document visualization behavior where applicable.

## Loading State

Document actual loading UI.

## Empty State

Document actual empty UI.

## Error State

Document actual error UI.

## Success State

Document actual feedback.

## Responsive Behavior

Document real breakpoints and layout changes.

## Accessibility

Document:

* keyboard
* focus
* ARIA
* labels
* tab order
* contrast
* screen-reader considerations

## Performance

Document frontend hotspots.

## Security

Document page-specific security boundaries.

## Change Map

Explain exactly where a future engineer should start to modify the page.

Include:

* primary page file
* components
* styles
* state
* API/service
* backend
* tests
* regression risk
* dependent shared components

---

# Stage 34 — Page Isolation Rule

The frontend must be documented at two levels:

1. global frontend architecture
2. individual page architecture

Shared rules must not hide page-specific differences.

Document both global and per-page implementations for:

* Header
* Sidebar
* Footer
* toolbar
* tables
* charts
* forms
* modals
* controls
* navigation
* typography
* spacing
* colors
* state

---

# Stage 35 — Shared Component Analysis

For each important shared component document:

* path
* purpose
* consumers
* pages
* props/configuration
* shared behavior
* shared styles
* page-specific variations
* modification impact
* regression risk

---

# Stage 36 — Information Architecture

Inventory:

* navigation
* routes
* layouts
* pages
* tabs
* panels
* menus
* drawers
* modals
* dialogs
* cards
* tables
* charts
* filters
* forms
* tooltips
* notifications
* context menus
* empty states
* loading states
* errors

---

# Stage 37 — Design Language

Extract actual design behavior.

Inspect:

* density
* hierarchy
* surface design
* borders
* radius
* shadows
* spacing
* alignment
* grids
* card hierarchy
* panel hierarchy

Do not invent a design system that does not exist.

---

# Stage 38 — Color System

Extract actual:

* backgrounds
* surfaces
* primary
* secondary
* accent
* text
* muted text
* borders
* dividers
* success
* warning
* error
* info
* bullish
* bearish
* blue
* red
* chart colors
* hover
* active
* selected
* disabled
* focus
* overlays

Where available document:

* token
* CSS variable
* HEX
* RGB/HSL
* usage

Separate light/dark themes if both exist.

---

# Stage 39 — Typography

Document actual:

* font families
* fallback fonts
* sources
* loading
* sizes
* weights
* line heights
* letter spacing
* transformations

Include page-specific differences.

---

# Stage 40 — Spacing

Extract actual:

* margin
* padding
* gap
* section spacing
* component spacing
* layout spacing

Document any consistent scale only if supported by source.

---

# Stage 41 — Layout System

Inspect:

* CSS Grid
* Flexbox
* dimensions
* min/max sizes
* positioning
* fixed
* sticky
* absolute
* overflow
* breakpoints
* responsive rules

---

# Stage 42 — Header

Document global and page-specific headers.

Include:

* source
* dimensions
* layout
* color
* borders
* typography
* icons
* buttons
* interaction
* responsiveness

---

# Stage 43 — Sidebar

Document global and page-specific sidebars.

Include:

* source
* width
* collapsed width
* sections
* filters
* hierarchy
* icons
* labels
* padding
* gaps
* active state
* hover
* selected state
* scrolling
* responsive behavior

---

# Stage 44 — Footer / Status Bar

Document all global and page-specific implementations.

If none exists, explicitly state that.

---

# Stage 45 — Component Reference

For important components document:

* purpose
* source
* consumers
* dimensions
* colors
* typography
* border
* radius
* shadow
* spacing
* state
* hover
* focus
* active
* selected
* disabled
* loading
* animation
* responsive behavior

---

# Stage 46 — Forms

Inspect:

* Input
* Select
* Checkbox
* Radio
* Toggle
* Search
* Date/time
* Filters
* Buttons
* validation
* errors
* focus
* disabled states

---

# Stage 47 — Icons

Inspect:

* icon library
* custom SVG
* size
* stroke
* fill
* color
* semantic meaning
* interaction states
* page usage

---

# Stage 48 — Motion

Inspect:

* transitions
* duration
* easing
* transform
* opacity
* hover motion
* modal animation
* drawer animation
* sidebar animation
* tabs
* loading
* charts
* page transition

Do not invent missing motion rules.

---

# Stage 49 — Trading / Chart UI

If charting or trading visualization exists, provide a dedicated technical reference covering:

* entry point
* route/tab
* component hierarchy
* chart library
* initialization
* data source
* candles
* colors
* lines
* overlays
* grid
* axes
* labels
* markers
* behavior labels
* tooltip
* zoom
* pan
* crosshair
* drawing layers
* z-index
* events
* toolbar
* sidebar
* filters
* dialogs
* settings
* state
* backend dependencies
* refresh
* performance

---

# Stage 50 — Special Project Pages

If pages such as `Faraz Exporter`, `Manual Review`, or other specialized tools exist, create dedicated complete references.

Do not assume they exist from their names alone.

Derive implementation from source.

---

# Stage 51 — Every Other Page

Apply the same analysis depth to every discovered page.

No page may receive less analysis merely because it was not named in this prompt.

---

# Stage 52 — Responsive Design

Inspect real behavior for applicable viewport ranges.

Document actual breakpoints.

If the UI is not responsive, say so.

Do not invent mobile support.

---

# Stage 53 — Accessibility

Inspect:

* semantic HTML
* ARIA
* keyboard support
* focus
* tab order
* labels
* contrast
* reduced motion
* screen-reader support

Separate implemented behavior from missing behavior.

---

# Stage 54 — UI Change Map

Inside:

`/docs/TradingBot_UI_UX_Technical_Reference.md`

create:

`Where To Make UI Changes`

For every common UI change identify:

* main source
* stylesheet
* component
* state
* token
* API dependency
* backend dependency
* affected pages
* tests
* regression risk

---

# Stage 55 — UI/UX Technical Reference File

The UI/UX file must include at minimum:

1. UI Executive Overview
2. Audit Verification Method
3. Frontend Technology Stack
4. Frontend Folder Tree
5. Frontend File Responsibility Map
6. Complete Page / Route / Tab Inventory
7. Information Architecture
8. Global Layout Architecture
9. Global Design Language
10. Design Tokens
11. Color Palette
12. Typography
13. Spacing
14. Border / Radius / Shadow
15. Header
16. Sidebar
17. Footer
18. Navigation
19. Shared Components
20. Buttons
21. Forms
22. Tables
23. Cards / Panels
24. Charts
25. Modals
26. Dialogs
27. Drawers
28. Icons
29. Animations
30. Loading States
31. Empty States
32. Error States
33. Responsive Design
34. Accessibility
35. Z-index
36. Interaction Patterns
37. UX Conventions
38. UI Technical Debt
39. UI Change Map
40. Page-by-Page Reference
41. Tab-by-Tab Reference
42. Screen-by-Screen Reference
43. Component-by-Component Reference
44. File-by-File Frontend Reference
45. Cross-Page Shared Component Matrix
46. Page-to-Backend Dependency Matrix
47. Page Change Impact Matrix
48. Runtime UI Verification
49. Unverified UI Areas

Every real page must have its own subsection.

---

# Stage 56 — Per-Page Reference Template

Use this structure where applicable:

## `<Page Name> — Frontend Technical Reference`

### Overview

### Route / Tab

### Purpose

### User Workflow

### Entry Component

### Related Files

### Component Tree

### Layout

### Header

### Sidebar

### Footer / Status Bar

### Toolbar

### Controls

### Forms

### Tables

### Charts / Visualization

### Modals / Dialogs / Drawers

### Data Flow

### Backend Dependencies

### State Management

### Styling

### Color Usage

### Typography

### Spacing

### Icons

### Animation

### Loading State

### Empty State

### Error State

### Success State

### Responsive Behavior

### Accessibility

### Performance

### Security Considerations

### Dependencies

### Shared Components

### Modification Guide

### Regression Risk

### Related Tests

### Verification Evidence

If a section does not apply, explicitly write:

`Not applicable to this page`

---

# Stage 57 — Page-to-Backend Dependency Matrix

Create a matrix covering all real pages.

Include:

* frontend page
* API/bridge
* backend module
* state/data source
* shared dependency
* change risk

---

# Stage 58 — Page Change Impact Matrix

For every page document:

* main files
* shared dependencies
* other pages affected
* backend impact
* tests required
* regression risk

---

# Stage 59 — Traceability Standard

Every major finding should point to concrete source evidence.

Page documentation must always identify exact source files.

Architecture diagrams must only contain verified relationships.

Security claims must include validated evidence.

Performance claims must identify the relevant implementation.

---

# Stage 60 — Technical Debt and Inconsistencies

Identify but do not fix:

* duplicate code
* duplicate styles
* dead code
* unused modules
* unused components
* unused dependencies
* stale configuration
* inconsistent patterns
* naming inconsistency
* color inconsistency
* spacing inconsistency
* typography inconsistency
* magic numbers
* hardcoded values
* architecture leaks
* coupling
* frontend/backend coupling
* performance risks
* accessibility problems
* UX inconsistencies
* page inconsistencies
* duplicated components
* unsafe shared-component coupling
* missing tests
* stale documentation

Clearly distinguish confirmed issues from possible improvement opportunities.

---

# Stage 61 — AGENTS.md / AGENT.md

After technical references are complete, review the project's existing AI operational file.

Use the actual filename.

This file must remain a concise **Operational AI Guide**, not a duplicate of the large reference documents.

Where necessary it should contain:

* project structure
* architecture boundaries
* source-of-truth files
* coding conventions
* safe modification workflow
* test requirements
* regression requirements
* baselines
* performance rules
* refactor rules
* documentation rules
* packaging rules
* critical files
* important folders
* important pages
* frontend entry points
* page/backend boundaries
* sensitive-file handling
* assumptions AI must never make
* ambiguity rule

Do not rewrite it unnecessarily if already accurate.

---

# Stage 62 — No Application Source Changes

During this audit do not:

* modify algorithms
* modify backend behavior
* modify frontend behavior
* refactor application code
* optimize application code
* upgrade dependencies
* downgrade dependencies
* rename source
* move source
* delete source
* change styles
* change configuration behavior
* change architecture
* apply Codex Security fixes
* apply Superpowers implementation suggestions

Problems must be documented, not fixed.

---

# Stage 63 — Coverage Report

Before completion produce a real coverage accounting.

Include:

* total files discovered
* project-owned files
* reviewed files
* unreviewed files
* partially reviewed files
* backend files
* frontend files
* shared files
* configuration files
* sensitive files
* documentation files
* tests
* fixtures
* baselines
* generated files
* binary files
* third-party files
* unverified files
* pages
* routes
* tabs
* screens/views
* fully documented pages
* partially documented pages
* unverified pages

If important coverage remains incomplete, you may not claim full completion.

---

# Stage 64 — Superpowers Final Coverage Audit

Use Superpowers again.

Compare the initial audit plan against actual work completed.

Superpowers must look specifically for:

* missing stages
* missing folders
* missing source categories
* unreviewed important files
* undocumented pages
* undocumented routes
* undocumented dependencies
* missing backend/frontend relationships
* missing tests
* unexplained unverified areas
* incomplete documentation sections

Do not mark the audit complete solely because documentation files exist.

---

# Stage 65 — Codex Security Final Reconciliation

Review the security work one final time.

Report:

* total meaningful Codex Security findings
* confirmed findings
* likely findings
* false positives
* not-applicable findings
* unresolved findings
* manual-only findings
* overlapping manual/plugin findings

Ensure no raw secrets appear in documentation.

Ensure no security fix was automatically applied.

---

# Stage 66 — Documentation Quality Audit

Re-read both technical references.

Verify:

* tree completeness
* folder coverage
* file coverage
* entry points
* architecture
* dependencies
* data flow
* technology stack
* APIs
* state
* lifecycle
* performance
* security
* testing
* build
* deployment
* all pages
* all routes
* all tabs
* all screens
* component trees
* backend dependencies
* styling
* colors
* typography
* header
* sidebar
* footer
* animation
* responsiveness
* accessibility
* change maps
* file responsibility maps
* page responsibility maps
* unverified sections
* traceability

Do not claim completion if documentation is materially incomplete.

---

# Stage 67 — File Responsibility Standard

After reading:

`TradingBot_Technical_Architecture.md`

a new engineer must be able to answer without manually rediscovering the repository:

* What does this file do?
* What does this folder own?
* Where is this feature implemented?
* Where is this behavior calculated?
* Where is this API created?
* Where is data transformed?
* Where is state managed?
* Where is serialization performed?
* Which file should be changed for this feature?
* Which files depend on it?
* What can break?
* Which tests should run?
* Which documentation must be updated?

If these questions cannot be answered, improve the documentation.

---

# Stage 68 — Page Responsibility Standard

After reading:

`TradingBot_UI_UX_Technical_Reference.md`

a new engineer must be able to select any page and answer:

* What is the page for?
* Which route opens it?
* What is its entry component?
* What is its component tree?
* What files belong to it?
* Which shared components does it use?
* Which styles control it?
* Which global styles affect it?
* Which backend modules does it depend on?
* Which APIs does it call?
* Where is its state?
* Where are its filters?
* Where are its buttons?
* Where is its Sidebar?
* Where is its Header?
* Where are its dialogs?
* Where are its tables?
* Where are its charts?
* Which colors does it use?
* Which typography does it use?
* Which icons does it use?
* Which animations does it use?
* What happens while loading?
* What happens with no data?
* What happens on error?
* How does it respond to viewport changes?
* What other pages can a shared change affect?
* What backend files might be affected?
* Which tests should run?

If not, improve the documentation.

---

# Stage 69 — Completion Criteria

You may only state:

`Full project review completed`

when all of the following are true:

1. Superpowers was used for audit planning.
2. Superpowers final completeness verification was performed.
3. Codex Security was used.
4. Important Codex Security findings were manually validated.
5. The complete repository was scanned.
6. All project-owned files were inventoried.
7. All important files were reviewed.
8. Sensitive files were reviewed safely.
9. Repository tree is documented.
10. Important folders have responsibilities.
11. File Responsibility Map is complete.
12. Backend architecture is understood.
13. Frontend architecture is understood.
14. Runtime/startup is understood or explicitly unverified.
15. Data flow is documented.
16. Dependencies are documented.
17. Technology stack is verified.
18. Testing architecture is documented.
19. Build/deployment is documented.
20. Performance has been reviewed.
21. Security has been reviewed.
22. Every major page is identified.
23. Every route is identified.
24. Every tab is identified.
25. Every major screen/view is identified.
26. Every page has a detailed reference.
27. Every page's source files are mapped.
28. Every page's component tree is mapped.
29. Every page's backend dependencies are mapped.
30. Every page's state is documented.
31. Every page's styling is documented.
32. Every page's change impact is documented.
33. UI design system is extracted.
34. Change maps exist.
35. Both required documentation files are complete.
36. `AGENTS.md` or `AGENT.md` was reviewed.
37. Plugin findings have been reconciled with source evidence.
38. Repository state has been checked for unintended source modifications.
39. No important unverified area remains unexplained.

If any requirement fails, state precisely what remains incomplete.

---

# Stage 70 — Final Chat Report

At completion provide a short technical report.

Use this structure:

`Repository scan: Complete / Incomplete`

`Superpowers planning: Complete / Unavailable / Incomplete`

`Superpowers final coverage audit: Complete / Incomplete`

`Codex Security scan: Complete / Unavailable / Incomplete`

`Codex Security findings validated: <count>`

`Confirmed security findings: <count>`

`Unresolved security findings: <count>`

`Total files discovered: <count>`

`Project-owned files: <count>`

`Files reviewed: <count>`

`Files unverified: <count>`

`Backend analysis: Complete / Issues`

`Frontend analysis: Complete / Issues`

`Runtime verification: Complete / Partial / Not available`

`Pages discovered: <count>`

`Pages fully documented: <count>`

`Routes discovered: <count>`

`Tabs discovered: <count>`

`Screens/views discovered: <count>`

`Repository tree: Complete / Incomplete`

`File responsibility map: Complete / Incomplete`

`Page responsibility map: Complete / Incomplete`

`Page-to-backend dependency map: Complete / Incomplete`

`Change impact map: Complete / Incomplete`

`Technical Architecture Reference: Created / Incomplete`

`UI/UX Technical Reference: Created / Incomplete`

`AGENTS/AGENT: Unchanged / Updated`

`Security-sensitive files: Reviewed / Issues`

`Unintended source changes: None / List`

`Open questions: None / List`

`Unverified areas: None / List`

Keep detailed findings inside the documentation files.

---

# Final Quality Standard

The final documentation must be detailed enough that:

* a Backend Engineer can understand the backend architecture
* a Frontend Engineer can understand the frontend architecture
* a Frontend Engineer can understand every page independently
* a UI/UX Designer can reconstruct the implemented design system
* a DevOps Engineer can understand build and deployment
* a Security Engineer can identify sensitive architecture and validated findings
* an AI coding agent can understand the repository before modification
* an AI coding agent can identify the correct files for a future request
* backend impact of frontend changes can be predicted
* frontend impact of backend changes can be predicted
* regression tests can be identified
* file responsibilities are understandable without rediscovering the codebase
* page responsibilities are understandable without rediscovering the frontend
* security findings are traceable to source
* performance-sensitive areas are identifiable
* modification risks are visible
* unverified areas are explicit

The goal is not merely to produce documentation.

The goal is to produce a **source-grounded, security-reviewed, plugin-assisted, fully traceable Digital Engineering Map of the project**.

---

# Final Writing Rule

All documentation, reports, summaries, findings, risks, page references, technical references, security analysis, UI/UX analysis, and final audit output must use:

**simple, fluent, readable, professional technical English.**

Use clear sentences.

Prefer direct technical explanations.

Preserve original technical identifiers.

Do not translate source identifiers.

Do not guess.

Do not hide uncertainty.

Do not claim completion until the repository, documentation, Superpowers coverage review, and Codex Security validation all satisfy the completion criteria.
