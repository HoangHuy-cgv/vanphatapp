# CONSTRAINTS — quality bar (numbers + checker)

Triple rule (binding): **backend native + config native + visual custom** (see `AGENTS.md`).
Applies to every change. Do not weaken this file to pass a change.

Run (no bench, no network, no Node):

```bash
python3 scripts/constraints-check.py          # floor + ratchet (~1s)
python3 scripts/constraints-check.py floor    # floor only (~0.1s, pre-commit)
python3 scripts/constraints-check.py --init   # rewrite baseline to current numbers
bash scripts/budget-gate.sh                   # bundle weight gate
```

## Floor — must be 0 (GATE: FAIL on violation, no exceptions)

| id | Rule |
|---|---|
| `mock_random_id` | No `Math.random()` as document ID |
| `guest_api` | No `allow_guest=True` on internal data |
| `permissioned_get_all` | No `frappe.get_all` on permissioned master data (use `get_list`) |
| `raw_html` | No `v-html` |
| `suppression` | No checker-silencing comments (`@ts-ignore`, `eslint-disable`, `# noqa`, `type: ignore`, `istanbul ignore`, `Stryker disable`, `nosemgrep`, `gitleaks:allow`) |
| `secret` | No keys/secrets in source |
| `stub` | No `NotImplementedError`/`TODO`/`FIXME` standing in for API implementation |
| `raw_fetch` | No direct `fetch(` in `frontend/src` — all HTTP via `api()` (`composables/useSession.js` only excluded impl) |
| `hardcoded_user` | No hardcoded email/user in client (identity from `get_boot`) |
| `hardcoded_config` | No new hardcoded option lists/defaults/labels/order in Vue (config from native) |

Tighten silently; loosen loudly (Exceptions table entry with owner + expiry).

## Ratchet — only improve vs `.constraints-baseline.json`

| Metric | Now | Direction |
|---|---|---|
| `api_ungated` (of 26 endpoints) | 0 | keep 0 |
| `client_identity` | 0 | down |
| `client_money_math` | 0 | down |
| `client_qty_reduce` | 0 | down |
| `client_magic_fallback` | 0 | down |
| `client_hardcoded_qty` | 0 | down |
| `swallowed_catch` | 1 | down |
| `entry_gzip_kb` | 142 | down/hold (warn 170 / fail 300) |
| `fe_test_files` | 0 | up (target ≥ 8) |
| `fe_guard_ok` | 1 | hold 1 |
| `py_tests` | 48 | up (never down) |

Checker: `scripts/constraints-check.py` (floor rules + ratchet + `api_ungated` AST ledger + bundle size + py tests + composables guard).

## Architecture boundary

1. ERPNext native is SSOT for money/tax/deposit/BOM/stock/status/naming. `api/*` = thin facade. One money semantics + one HOLD rule (`docs/API.md`).
2. Portal owns ~6 flows (quote, order, deposit, workshop, delivery, lookup). Desk owns config + master data + everything undesigned.
3. Client collects input → calls `api()` → renders. No money/qty math, no commercial fallbacks, no identity/config hardcodes. Reads `page_result` envelopes.
4. Mutations re-read server. No local `order_state`/`is_hold` sets; no success toast on API error.
5. Permissions native: Desk holds role matrix; code gates via `get_roles()` + `has_permission()` (`api/_guards.py`). `api_ungated = 0`. No `ignore_permissions` in user APIs.
6. Stack locked: Vue 3.5 + Vite 7 + vue-router 4 hash + Tailwind v3 + `frappe-ui@1.0.0-beta.64` exact. No Studio on production until 3 reopen conditions (`docs/DECISIONS.md`). No `www.list` for Sales Order until `frappe#42640` fixed.

## Exceptions

| ID | Rule | Path | Reason | Owner | Expiry |
|---|---|---|---|---|---|
| W2 | `api_ungated` | `bao_gia.get_boot` | Returns only own session user + CSRF token | em | 2026-12-14 |
