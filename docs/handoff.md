# Handoff — sau slice p95 + wipe prod (SSOT rolling, <25 dòng)

> Nhánh `master` (`5009c43`). Không `git push` khi chưa lệnh.

- **Định hướng chốt:** local mới nhất, prod wipe + deploy fresh từ HEAD.
  Triple rule ghim: backend native + config native + visual custom.
- **Đã xong:** quyền 26 endpoint (`api_ungated=0`) · p95 thật (list 213ms,
  detail 302ms qua tunnel; 13ms trong VPS — app nhanh, tunnel chậm) ·
  import fresh-site 293 Item/117 KH · 48 test + GATE PASS.
- **Rule/docs nhất quán:** CONSTRAINTS + backend/frontend spec + plan/todo/handoff
  cùng số liệu mới (48 test, p95 §9, entry 142KB).
- **Chờ Sếp:** cọc 2 bước → Vitest → tối ưu đường truyền.
- Chi tiết: `tasks/plan.md`, `docs/specs/backend-native-api-spec.md` §9.
