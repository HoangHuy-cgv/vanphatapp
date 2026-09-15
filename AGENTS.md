# AGENTS.md — Van Phat Packaging ERP & Portal

ERPNext v16 native backend + thin Vue cockpit for flexible-packaging factory (quotes, orders, deposits, catalog).

## Rules

1. Read `CONSTRAINTS.md` before writing code. Never weaken it to pass.
2. Respond in Vietnamese. User = `Sếp`, self = `em`. User owns business rules; you own technical calls. Disagree with evidence.
3. Never invent schema — see `docs/DATA.md`. Never read `archive/`.
4. Load matching skill via `skill` tool before acting. Never apply from memory.
5. Ask via `ask_user_question` only. Never ask in plain text.
6. Finish what you start: runs, verified, failures fixed.

## Triple rule (non-negotiable)

1. **Backend native** — money, tax, deposit, BOM, stock, status, naming computed by ERPNext DocTypes. `vanphat_portal.api.*` = thin facade, no duplicated logic. Details: `docs/API.md`.
2. **Config native** — options, defaults, labels, order, visibility from Custom Field / Property Setter / DocType Layout / Item Group tree / `min_order_qty` / Payment Terms / Credit Limit / Tax Template. Desk change reaches UI with **no rebuild**.
3. **Visual custom only** — layout, Modal, Drawer, color, click-select, friendly flow language. No money/tax/status/config/option lists in visual code. Details: `docs/UI.md`.

## Map (progressive disclosure — load on touch only)

| Touch | Load |
|---|---|
| API file (`api/*.py`) | `docs/API.md` |
| Vue file (`frontend/src/**`) | `docs/UI.md` |
| Data field, naming, DocType | `docs/DATA.md` |
| Infra, deploy, bench, import | `docs/SETUP.md` |
| Why a decision was made | `docs/DECISIONS.md` |
| Backlog, priorities | `docs/BACKLOG.md` |

## Working method

- Legacy: read + characterization test before refactor. No blind refactors.
- Feature: spec (`docs/BACKLOG.md`) → thin slices + TDD → review → ship.
- Trivial (typo, one file): implement directly, minimal verify.
- SSOT = code + tests + git history.

## Essentials

- Frontend: Vue 3 `<script setup>`, hash router, frappe-ui, Vite, static at `/portal`. Fetch only via `api()` in `composables/useSession.js` (incl. FormData). Read `page_result` envelopes. No client money/qty math, no local mutation after POST (re-read server), no hardcoded identity/config. See `docs/UI.md`.
- Backend: lists return `page_result` envelope. Tx lists default 15/max 100; pickers default 100/max 100 + server filter. One money semantics + one HOLD rule (see `docs/API.md`). GET reads; POST commits itself. Detail reads use `get_doc` + `has_permission`.
- UI: `custom_alias` in tables (codes in tooltips). 1-line header, 5–7 1-line cols, Vietnamese text+color status, right-aligned `tabular-nums`. Depth in drawers.

## Never

- Mock data, `Math.random()` IDs, local-only mutation, `v-html`, `frappe.get_all` on permissioned data, `allow_guest=True` on internal data, hand-rolled money/tax math, hardcoded commercial constants, raw-SQL prod mutation, `openpyxl`.
- `git push` without explicit order. Commit atomically, conventional prefixes.
- Bypass hooks (`-c core.hooksPath=/dev/null`) only on hook-loop after correct manual fix; state reason in message.

## Verify

- `python3 -m unittest discover -s apps/vanphat_portal/tests -p "test_*.py"`
- `node apps/vanphat_portal/frontend/check-composables.mjs`
- `python3 scripts/constraints-check.py` (GATE: PASS to commit)
- `bash scripts/budget-gate.sh` (after build)
