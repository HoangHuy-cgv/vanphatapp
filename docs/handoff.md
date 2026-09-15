# Handoff — Slice cleanup triple-rule (SSOT rolling, <25 dòng)

> Nhánh `master` (ghim `frappe-ui 1.0.0-beta.64`). Không `git push` khi chưa lệnh.

- **Mục tiêu:** docs, code, rule cùng một ngữ cảnh (triple rule) trước khi đụng nợ
  quyền/bench/Vitest (Sếp hoãn — plan mục Còn lại).
- **Đã dọn code:** CSS overlay chết ×2, biến submit chết ×6, ảnh mẫu cứng ×3,
  `defineExpose` chết ×3, `loadAllCatalogData` → `loadInitialTabData` (chỉ tải tab mở),
  JSON mock local ×2, `serve-portal.mjs` gắn boundary LOCAL ONLY.
- **Đã cập nhật docs:** README + specs/README (triple rule) + plan gọn (Đã xong/Còn lại)
  + SPEC variant (lệnh verify mới) + link tương đối.
- **Số:** 27 endpoint/22 ungated (nợ quyền) · entry ~145 kB · 46 test backend · guard 8/8.
- Chi tiết: `tasks/todo.md`, `tasks/plan.md`.
