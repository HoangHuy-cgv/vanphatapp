# ADR-003: Drawers native `<dialog>`, modals + toast frappe-ui (P4 Sếp duyệt)

## Status
Accepted (2026-09-15)

## Date
2026-09-15

## Context
- 6 drawers slide-over phải: frappe-ui Dialog chỉ có `position center|top`, cố bẻ thành
  drawer phải override nặng → ngược tối giản. `aside + role=dialog` tự viết phải gánh
  Esc/focus-trap/inert/z-index tay (S10 `useDrawerDialog`, đã xóa vì trùng).
- 2 modals giữa màn hình + confirm/prompt + toast: tự viết lại trong khi lib có sẵn,
  `main.js` mang tiếng dùng frappe-ui nhưng không dùng gì (grep import = 0).
- Sếp duyệt: học best practice chính chủ, không ngại làm lại (app còn mới).

## Decision
- Drawers → 1 `BaseDrawer.vue` bọc native `<dialog>` + Teleport: `showModal` guard `dlg.open`,
  sync native `close/cancel` (kẻo Esc lệch state), backdrop-click `e.target === dlg`,
  restore focus trigger. Esc/inert/focus/top-layer/`::backdrop` miễn phí từ browser.
  Nguồn: MDN `<dialog>`/`showModal`/top-layer + Vue Teleport.
- Modals → `Dialog` frappe-ui (`v-model:open`, đối chiếu API trong `node_modules` bản beta
  đang dùng, không copy mù docs mới); confirm/prompt → `dialog.confirm/prompt`.
- Toast → `toast.*` lib (đã có `FrappeUIProvider` portals); xóa `CockpitToast.vue` + singleton.
- Animation dialog: `@starting-style` + `transition-behavior: allow-discrete` + liệt kê
  `display/overlay`; backdrop không animate fade-out bằng keyframes; mobile 768px full;
  tôn trọng `prefers-reduced-motion`. Nguồn: Chrome entry-exit + MDN animating dialogs.
- Cấm `tabindex` trên `<dialog>` (MDN).

## Alternatives Considered
- **Giữ `aside` + composable**: Pros — không đụng layout. Cons — nợ z-index/transform,
  tự chịu 100% a11y, trùng code 6 drawers. Rejected.
- **All-in frappe-ui Dialog** (kể cả drawers): Pros — 1 lib. Cons — hack center→right,
  đánh nhau với lib mỗi lần upgrade, không có top-layer thật. Rejected.

## Consequences
- Xóa `useDrawerDialog.js`, `CockpitToast.vue`, CSS overlay/keyframes chết.
- Khi upgrade frappe-ui: đối chiếu Dialog API trong `node_modules` trước (beta ↔ docs mới
  có thể lệch shape như `fieldname` vs `name` ở prompt).
