# AGENTS.md — Van Phat Packaging ERP & Portal

## How we work
- Respond in Vietnamese. Address the user as `Sếp`, yourself as `em`. The user owns business rules; you own technical decisions.
- Disagree with evidence when something is wrong, slow, or unsafe. No performative agreement.
- Never invent schema. Use only DocTypes and fields listed in `docs/specs/erpnext-native-vi-en-mapping.md`. Never read `archive/`.
- When a task matches a skill in the catalog, inspect it with the `skill` tool before acting. Never apply a skill from memory.
- Ask everything through `ask_user_question` (clarifications, choices, confirmations). Never ask in plain text.
- Finish what you start. Keep going until the task's success criteria hold (runs, verified, failures fixed). Do not stop after a first draft.

## Architecture (native-first)
Prefer the highest layer that satisfies the need:
1. ERPNext native DocType / field / method.
2. Frappe API (`get_list` + `filters/start/page_length/order_by`, `frappe.qb` for joins, `frappe.cache`, `has_permission`, `tabSeries`).
3. Thin `vanphat_portal.api.*` wrapper around native. No duplicated business logic.
4. Custom `custom_*` field or DocType only when native is proven absent and unconfigurable, plus an ADR in `docs/decisions/` and a mapping entry.
- Money, tax, deposit, BOM, and status come from native-computed values. The client only formats (`Intl.NumberFormat('vi-VN')`). VAT is doc-driven (ADR-002); cylinder pricing passes through `cylinder_spec {qty, unit_price, supplier}` with no numeric fallback; deposits derive from Payment Terms + Credit Limit.

## Spec router (load on touch, never bulk-read)
| When touching | Load |
|---|---|
| Any data field, naming series, DocType | `docs/specs/erpnext-native-vi-en-mapping.md` |
| Item groups, UOM, TP/BTP/NGCS/TMD rules, saleable flags | `docs/specs/erpnext-packaging-masterdata-spec.md` |
| Pricing or BOM math | `docs/specs/packaging-calculation-spec.md` + `packaging-calculation-engine` skill |
| Any Vue/UI file | `docs/specs/ui-cockpit-baseline-spec.md`, `docs/specs/frontend-architecture-spec.md` |
| Any `vanphat_portal.api.*` file | `docs/specs/backend-native-api-spec.md` |
| Why a past decision was made | `docs/decisions/` |
| Module overview | `docs/specs/README.md` |

## Working method
- Legacy code: read it and add a characterization test before refactoring. No blind refactors.
- New feature: spec → plan (`tasks/plan.md` + `tasks/todo.md`) → thin slices + TDD → review → ship. Declare legacy no-touch zones in the spec.
- Trivial fix (typo, one file, self-contained): implement directly with minimal verification. No spec or plan.
- Code, tests, and git history are the only SSOT. After a committed milestone, reset `tasks/todo.md`. `docs/handoff.md` is a rolling pointer (<25 lines), overwritten per session, never appended.

## UI essentials (details in the baseline spec)
- Tables show `custom_alias`, never full legal `item_name` as static text (tooltip only). Internal codes stay in tooltips and the backend.
- One-line header (`[Tabs] + [Search] + [Action]`); 5–7 single-line columns; status as Vietnamese text plus color (never color alone); numerics right-aligned bold `tabular-nums`.
- Depth lives in drawers (`role=dialog`, Esc/backdrop close, focus restored to the trigger).

## Frontend essentials (details in the frontend spec)
- Vue 3 `<script setup>`, hash router, `frappe-ui`, Vite, Zero-Node static at `/portal`. Split components past 500 lines (warn past 300).
- Fetch only through `api()` in `composables/useSession.js`. Debounce search 250–300ms with `AbortController`; render the latest response only.
- Lazy routes everywhere; heavy drawers/modals async with `<Suspense>`; `keep-alive` for read-heavy lists only. JS gzip budget 170KB warn / 300KB fail.

## Backend essentials (details in the backend spec)
- Modules: `order.py`, `bao_gia.py`, `item.py`, `customer.py` / `supplier.py` / `user.py`. No silent re-export overrides.
- Server-side pagination (`start`/`page_length`, default 15, max 100). Multi-DocType joins go through one `frappe.qb` query. Cache keys include every param (TTL 300s), invalidated via `doc_events`.
- GET reads; POST mutates with its own `db.commit`. Detail reads use `get_doc` + `has_permission` at the action site.

## Never
- `openpyxl`, mock data, `Math.random()` document IDs, or local-only state mutation. Empty DB renders a truthful empty state.
- `frappe.get_all` on permissioned master data (use `get_list`), `allow_guest=True` on internal data, `v-html`, hand-rolled money/tax math, hardcoded commercial constants, or raw-SQL CRUD (complex report joins only, never prod mutation).
- `git push` without an explicit order. Commit atomically with conventional prefixes.

## Pre-commit and verification
- Hooks are check-only: write correctly at the source (LF CSVs via `lineterminator="\n"`, Python tabs). On a hook failure, fix by hand, re-stage, and commit once.
- Bypass hooks (`-c core.hooksPath=/dev/null`) only when a hook loops after a correct manual fix, and state the reason in the commit message. Never bypass to dodge lint or the frappe-pattern gate.
- Run the repo's own focused tests and build after each change; fix failures your change caused. Do not re-run green suites on unchanged code.
