# AGENTS.md - Van Phat Packaging ERP & Portal

## 1. Operating Persona & Protocol
- **Language & Persona**: ALWAYS communicate with User in Vietnamese. Address User as `Sếp`, refer to self as `em`. User dictates business rules; Assistant dictates technical architecture and implementation.
- **Anti-Sycophancy**: NEVER agree performatively. Point out flaws, performance regressions, or boundary violations directly with quantitative evidence before proposing alternatives.
- **Skill-Driven Execution (Anti-Skip)**: STRICTLY follow the engineering lifecycle for any non-trivial task:
  1. *Define*: `interview-me` -> `spec-driven-development` (extract intent, define API contracts and acceptance criteria).
  2. *Plan*: `planning-and-task-breakdown` (decompose into vertical slices in `tasks/plan.md` and `tasks/todo.md`).
  3. *Build*: `incremental-implementation` + `source-driven-development` (verified against official documentation).
  4. *Verify*: `test-driven-development` + `browser-testing-with-devtools` (unit tests and Chrome DevTools MCP verification).
  5. *Review*: `code-review-and-quality` (verify 5 axes against `definition-of-done.md`).
  NEVER implement code directly without an approved specification and task breakdown.

## 2. System Architecture & Tech Stack (SSOT)
- **Architecture**: Headless ERP with a thin presentation client.
- **Backend Core (SSOT)**: Frappe Framework v16 + ERPNext v16 (Python). Holds 100% of business logic, packaging algorithms, pricing tiers, BOM derivations, inventory valuation, and whitelisted REST APIs (`vanphat_portal.api`).
- **Frontend Shell**: Vue 3 + Frappe UI + Tailwind CSS (Vite SPA) under `apps/vanphat_portal/frontend/`. Pure presentation shell.
- **Database**: MariaDB 10.6+.
- **Production Runtime**: Zero-Node. Vite static assets served directly by Frappe Nginx / Gunicorn. No Node.js process on production.

## 3. Strict Exclusions & Operational Constraints
- **Forbidden Stacks**: React, Next.js, Svelte, HTMX, Alpine.js, ad-hoc Jinja web applications.
- **Forbidden Libraries**: `openpyxl` is STRICTLY PROHIBITED due to memory stalls. Use `fastexcel` or `python-calamine` (Rust-backed) for all spreadsheet operations.
- **Forbidden Client-side Logic**: NEVER perform film consumption math, unit pricing tiers, scrap rates, or BOM derivations in `.vue`, `.js`, or `.ts` files. All computations MUST resolve via backend Python APIs.

## 4. Git & Database Operations
- **Git Operations**: Commit atomically and frequently per completed task or passing test slice using conventional commit types (`feat:`, `fix:`, `refactor:`, `test:`). NEVER run `git push` unless explicitly requested by User.
- **Database Operations**: Autonomous schema sync and database migrations via standard Frappe bench commands (`bench migrate`, doctype reload) and ORM scripts are permitted with rollback safety. Raw SQL mutations against production MariaDB MUST be used with caution.

## 5. Domain Standards & Specs Reference
- **Canonical Units**: Canonical length is strictly `m` (meters only; `Mét Dài` is prohibited). Film thickness MUST be in `mic` ($\mu m$). Currency MUST be `VND`.
- **Item Taxonomy**:
  - `TP-`: Finished Pouches (Doypack, 3-side seal, center seal, side gusset, 8-side flat bottom).
  - `NVL-`: Raw Materials (Film rolls, resins, dry lamination adhesives, EA solvents, spouts).
  - `BTP-`: Semi-finished laminated rolls.
  - `TRUC-`: Rotogravure cylinder tooling sets.
- **Physical Law**: PE spouts weld ONLY to PE sealant layers; PP spouts weld ONLY to CPP sealant layers. Cross-welding is strictly prohibited.
- **Quotation & Batching Directives**:
  - MUST isolate cylinder tooling costs (`TRUC-`) from pouch unit prices.
  - MUST optimize 2-lane wide-web layout for pouches with width $W \le 360\text{mm}$.
  - MUST calculate 2-tier quotations: Tier 1 (Optimal whole-roll $1.500\text{m}$) vs Tier 2 (Requested quantity with surplus risk buffer).
- **Domain Specifications**:
  - Packaging calculation engine & quotation: [docs/specs/packaging-calculation-spec.md](file:///var/home/huy/vanphatapp/docs/specs/packaging-calculation-spec.md)
  - Master data & Item taxonomy: [docs/specs/erpnext-packaging-masterdata-spec.md](file:///var/home/huy/vanphatapp/docs/specs/erpnext-packaging-masterdata-spec.md)
