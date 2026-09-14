# AGENTS.md - Van Phat Packaging ERP & Portal

## 1. Operating Persona & Protocol
- **Language & Persona**: ALWAYS communicate with User in Vietnamese. Address User as `Sếp`, refer to self as `em`. User dictates business rules; Assistant dictates technical architecture and implementation.
- **Anti-Sycophancy**: NEVER agree performatively. Point out flaws, performance regressions, or boundary violations directly with quantitative evidence before proposing alternatives.
- **Zero Speculation & ERPNext Native Wording Enforcement**: STRICTLY PROHIBIT agent speculation or fabrication of data, fieldnames, or attributes. Agents MUST ONLY use ERPNext native columns and DocTypes that have been officially mapped VI-EN. Mandatory use of ERPNext native wording across all master data catalogs, schema definitions, and portal interfaces. Absolutely forbidden to use data from `archive/`. Reference SSOT mapping: [docs/specs/erpnext-native-vi-en-mapping.md](file:///var/home/huy/vanphatapp/docs/specs/erpnext-native-vi-en-mapping.md).
- **Skill-Driven Execution (Anti-Skip & Mandatory Pre-Action Loading)**: STRICTLY follow the engineering lifecycle for any non-trivial task:
  1. *Define*: `interview-me` -> `spec-driven-development` (extract intent, define API contracts and acceptance criteria).
  2. *Plan*: `planning-and-task-breakdown` (decompose into vertical slices in `tasks/plan.md` and `tasks/todo.md`).
  3. *Build*: `incremental-implementation` + `source-driven-development` (verified against official documentation).
  4. *Verify*: `test-driven-development` + `browser-testing-with-devtools` (unit tests and Chrome DevTools MCP verification).
  5. *Review*: `code-review-and-quality` (verify 5 axes against `definition-of-done.md`).
  **MANDATORY PRE-ACTION SKILL INSPECTION**: Before performing any task, the Agent MUST explicitly load and read the relevant `SKILL.md` via `view_file`. Strictly forbidden to apply skills implicitly or skip reading `SKILL.md`. Every action plan must declare active skills.
  NEVER implement code directly without an approved specification and task breakdown.
- **Clean-on-Done & Anti-Append Policy (Code & Git As Pure SSOT)**:
  - Code, automated test suites, and Git commit history are the ONLY Single Source of Truth (SSOT).
  - `tasks/todo.md` and `tasks/plan.md` are strictly ephemeral working scratchpads for the active milestone ONLY. Once a milestone is completed and committed to Git, agents MUST clean/reset `tasks/todo.md` (remove completed tasks). Accumulating historical tasks across milestones (e.g. Task 1 to Task 20+) is STRICTLY FORBIDDEN.
  - `docs/handoff.md` is an operational rolling pointer (< 25 lines) strictly for session-to-session handoff. Agents MUST ALWAYS OVERWRITE, NEVER APPEND. It MUST only contain: Current Commit hash, Health/CI verification status, and Immediate Next Action. All historical narratives belong in git commit messages and temporary artifacts (`walkthrough.md`), NEVER in repository handoff files.

## 2. System Architecture & Tech Stack (SSOT)
- **Architecture**: Headless ERP with a thin presentation client.
- **Backend Core (SSOT)**: Frappe Framework v16 + ERPNext v16 (Python). Holds 100% of business logic, packaging algorithms, pricing tiers, BOM derivations, inventory valuation, and whitelisted REST APIs (`vanphat_portal.api`).
- **Frontend Shell**: Vue 3 + Frappe UI + Tailwind CSS (Vite SPA) under `apps/vanphat_portal/frontend/`. Pure presentation shell.
- **Database**: MariaDB 10.6+.
- **Production Runtime**: Zero-Node. Vite static assets served directly by Frappe Nginx / Gunicorn. No Node.js process on production.

## 3. Frontend Architecture & Community Pattern Reuse (frappe/crm)
- **Canonical UI Reference**: Generic management views (e.g., Customer list, Sales Order list, filters, tables, search pagination) MUST reuse proven patterns and composables (`createListResource`, `createDocumentResource`, `useCall`) from official Frappe apps (`frappe/crm`, `frappe/helpdesk`, `@frappe/ui`).
- **Packaging Domain Exclusivity**: Core flexible packaging flows (pouch dimensions, multi-layer film selection, 2-lane layout, cylinder tooling isolation) MUST maintain dedicated, high-speed custom interfaces (`ModalStep1Sale`, `DrawerStep2Director`). Never replace tailored packaging flows with generic ERP forms.
- **Theme & Aesthetic Uniformity**: All imported or adapted views MUST strictly conform to Van Phat's Unified Industrial Dark Design System:
  - Background palette: `#0b0f19` (base), `#161b22` (cards/modals), `#1a1f27` (inputs/table headers).
  - Borders: `#3a424e` / `rgba(255,255,255,0.08)`.
  - Brand accents: `#4ea1e0` / `#0284c7`.
  - Packaging layer badges: Sky Blue (print), Amber (barrier), Purple (PA), Emerald (sealant).
  - Typography: Unified font `Inter` with `tabular-nums` for all financial and dimensional figures.
- **Minimalist Content & Elon Musk Philosophy**: When designing pages/views, write ultra-minimalist content. Use short, high-density labels. STRICTLY PROHIBIT tutorial notes, explanatory prose, subheadings that "explain for humans", or verbose helper text unless explicitly requested by User. The UI is an industrial operational cockpit, not a manual.
- **Mandatory UI Display Rule (Short Alias Enforcement SSOT)**: Across 100% of UI/UX views, components, tables, slide-over drawers, BOM child lists, modals, and order lines, ALWAYS prioritize and render `custom_alias` (short commercial name). STRICTLY PROHIBIT rendering full legal `item_name` as static text (only allowed inside tooltip `:title="item_name"`). Child materials in BOM tables MUST also resolve and display `custom_alias` (e.g. `PET in 888 Phấn Thơm`, `PE sữa K750 190mic`, `Keo D-9700`, `Dung Môi EA`), never verbose legal names like `Cuộn màng PET in...` or `Dung môi công nghiệp...`. Subtitles duplicating full legal `item_name` in headers or drawers are strictly prohibited.

## 4. Strict Exclusions & Operational Constraints
- **Forbidden Stacks**: React, Next.js, Svelte, HTMX, Alpine.js, ad-hoc Jinja web applications.
- **Forbidden Libraries**: `openpyxl` is STRICTLY PROHIBITED due to memory stalls. Use `fastexcel` or `python-calamine` (Rust-backed) for all spreadsheet operations.
- **Forbidden Bloatware**: Third-party VoIP (Twilio), external marketing mailers, or unvetted npm packages from copied repos are STRICTLY PROHIBITED.
- **Forbidden Client-side Logic**: NEVER perform film consumption math, unit pricing tiers, scrap rates, or BOM derivations in `.vue`, `.js`, or `.ts` files. All computations MUST resolve via backend Python APIs.

## 5. Git & Database Operations
- **Git Operations**: Commit atomically and frequently per completed task or passing test slice using conventional commit types (`feat:`, `fix:`, `refactor:`, `test:`). NEVER run `git push` unless explicitly requested by User.
- **Database Operations**: Autonomous schema sync and database migrations via standard Frappe bench commands (`bench migrate`, doctype reload) and ORM scripts are permitted with rollback safety. Raw SQL mutations against production MariaDB MUST be used with caution.

## 6. Domain Standards & Specs Reference
- **Canonical Units**: Canonical length is strictly `m` (meters only; `Mét Dài` is prohibited). Film thickness MUST be in `mic` ($\mu m$). Currency MUST be `VND`.
- **Item Taxonomy**:
  - `TP-`: Finished Pouches (Doypack, 3-side seal, center seal, side gusset, 8-side flat bottom).
  - `NVL-`: Raw Materials (Film rolls, resins, dry lamination adhesives, EA solvents, spouts).
  - `BTP-`: Semi-finished laminated rolls.
  - `TRUC-`: Rotogravure cylinder tooling sets.
- **Physical Law**: PE spouts weld ONLY to PE sealant layers; PP spouts weld ONLY to CPP sealant layers. Cross-welding is strictly prohibited.
- **Film Structure & Material Naming Standard**: In multi-layer film structures (`custom_structure_layers`), delimiter MUST strictly be a single forward slash `/` (double slash `//` is strictly forbidden). The sealant PE layer MUST be explicitly designated as either `PE sữa` (opaque white PE) or `PE trong` (clear PE). Abbreviations such as `PES`, `LLDPE`, or bare `/PE` are strictly prohibited.
- **Quotation & Batching Directives**:
  - MUST isolate cylinder tooling costs (`TRUC-`) from pouch unit prices.
  - MUST optimize 2-lane wide-web layout for pouches with width $W \le 360\text{mm}$.
  - MUST calculate 2-tier quotations: Tier 1 (Optimal whole-roll $1.500\text{m}$) vs Tier 2 (Requested quantity with surplus risk buffer).
- **Domain Specifications**:
  - Packaging calculation engine & quotation: [docs/specs/packaging-calculation-spec.md](file:///var/home/huy/vanphatapp/docs/specs/packaging-calculation-spec.md)
  - Master data & Item taxonomy: [docs/specs/erpnext-packaging-masterdata-spec.md](file:///var/home/huy/vanphatapp/docs/specs/erpnext-packaging-masterdata-spec.md)
