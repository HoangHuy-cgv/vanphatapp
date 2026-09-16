# CONSTRAINTS — quality bar (instruction + review tay, guard = script native có chủ)

Triple rule (binding): **backend native + config native + visual custom** (see `AGENTS.md`).
Applies to every change. Do not weaken this file to pass a change.

Enforce: review bắt buộc + CI native (unittest, 2 FE guard, vite build, budget-gate). Không merge khi chưa có review checklist. Guard FE = script native có chủ, chạy bằng runtime chuẩn (`node`, `vite build`): `check-composables.mjs` (runtime scope composable) + `check-ui.mjs` (Design System token qua `@vue/compiler-sfc`). Không checker AST monolithic tự chế kiểu `constraints-check.py` đã xóa.
Skill khi review: `code-review-and-quality` + `quality-code-review` + `.agents/references/vanphat-overlay.md` (load cả 3, không dùng memory).

## Review tiers (bắt buộc, chống skip — gọn từ 3-tier ngày 2026-09-16)

| Tier | Điều kiện | Thực thi |
|---|---|---|
| 1 | ≤100 lines, không chạm tiền/quyền/cọc | 1 agent, checklist rút gọn + Floor 11 |
| 2 | Mọi thứ còn lại (>100 lines, tiền/HOLD/VAT/deposit, API, PR lớn) | 3-agent (correctness+Triple rule / security+Floor 11 / performance+N+1) + `bash scripts/review-gate.sh`; PR lớn kèm OCR đối trọng khi Sếp yêu cầu |

Bỏ Tier 3 riêng: repo 1 dev + 1 agent, toàn push trực tiếp master — OCR delegate chỉ chạy khi Sếp gọi tên. Ngưỡng 300 lines trong gate giữ làm signal cảnh báo, không tách tier.

Review output: findings JSON `[{path,content,severity: critical|high|medium|low,category}]`, severity theo `code-review-and-quality` (Critical block merge, Nit optional). Im lặng khi không chắc (precision > recall).

## Floor — luật cấm (review tay, vi phạm = sửa code, không exception)

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
| `mock_server` | No mock server/CSRF/API/local-JSON preview (`serve-portal.mjs` deleted 2026-09-15; browser test = prod + `TEST-` docs + cleanup) |

Tighten silently; loosen loudly (Exceptions table entry with owner + expiry).

## Ratchet — hướng đi (so với số hiện tại, không baseline file)

| Metric | Now | Direction |
|---|---|---|
| `api_ungated` (of 26 endpoints) | 0 | keep 0 |
| `client_identity` | 0 | down |
| `client_money_math` | 0 | down |
| `client_qty_reduce` | 0 | down |
| `client_magic_fallback` | 0 | down |
| `client_hardcoded_qty` | 0 | down |
| `swallowed_catch` | 1 | down |
| `entry_gzip_kb` | 52 | down/hold (budget-gate decides warn/fail; agent picks optimal, no hard lock) |
| `fe_test_files` | 0 | up (target ≥ 8) |
| `fe_guard_ok` | 2 | hold 2 (`check-composables.mjs` + `check-ui.mjs`) |
| `py_tests` | 68 | up (never down) |

## Architecture boundary (diễn giải Triple rule — chuẩn ở `AGENTS.md`, chi tiết ở docs)

1. Backend native là SSOT (`docs/API.md`). Portal ~6 flows, Desk giữ config + master data.
2. Client thu input → `api()` → render; mutate xong đọc lại server (`docs/UI.md`).
3. Quyền native: Desk giữ matrix, code gate tại action site, `api_ungated = 0`.
4. Stack + budget: agent chọn tối ưu, `budget-gate.sh` quyết warn/fail. Không Studio prod / `www.list` cho SO cho tới khi reopen conditions (`docs/DECISIONS.md`) + `frappe#42640` được vá.

## Exceptions

| ID | Rule | Path | Reason | Owner | Expiry |
|---|---|---|---|---|---|
| W2 | `api_ungated` | `bao_gia.get_boot` | Returns only own session user + CSRF token | em | 2026-12-14 |
