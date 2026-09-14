# Handoff — Slice nhất-quán ADR-006 (SSOT rolling, <25 dòng)

> Nhánh `master` (đã ghim `frappe-ui 1.0.0-beta.64`). Không `git push` khi chưa lệnh.

- **ADR-006 (2026-09-15):** một ngữ nghĩa tiền + một HOLD + một envelope list +
  `api()` là đường fetch duy nhất. Fix vênh preview-HOLD-envelope-fetch.
- **Docs đã xong:** ADR-006 + AGENTS + 2 specs + CONSTRAINTS §4 + plan (item 11 xong,
  item 13 gom nợ `<select>`/config-cứng) + todo slice này.
- **Đang sửa code:** backend (preview/HOLD/envelope/TRUC-IN) → frontend (api FormData,
  bỏ fetch/5000/math/set-local/user-cứng) → verify (tests/guard/constraints/build).
- **Số cũ:** 19/24 ungated · entry 142 kB · 41 test backend · 0 test frontend.
- Chi tiết: `tasks/todo.md`, `tasks/plan.md`, `docs/decisions/ADR-006-*`.
