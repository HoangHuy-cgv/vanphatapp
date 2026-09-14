# Kiến Trúc Frontend Thin Client (Vue 3 + Vite + Frappe UI)

> **SSOT:** Mọi quy tắc frontend tập trung tại file này. `AGENTS.md` §4 chỉ tóm tắt. Code thực tế: `apps/vanphat_portal/frontend/src/`.

## 1. Stack Lock & Ranh Giới
- Vue 3.5 Composition API + `<script setup>`, vue-router 4 hash history, `frappe-ui@1.0.0-beta.63`, Vite 6, Zero-Node (static do Frappe Nginx serve tại `/portal`).
- Cấm: React/Svelte/HTMX/Alpine/Jinja-ad-hoc, Options API cho code mới, `v-html`, jQuery/DOM thủ công thay reactive state.
- Route view = composition surface (app shell + wiring + feature composition). Logic stateful/side-effect → `composables/useXxx.js`. UI section → child component (props down / events up).

## 2. Ngưỡng Tách Component (Enforced)
| Dòng SFC | Hành động |
|---|---|
| > 500 | Bắt buộc tách trước khi thêm tính năng mới |
| 300–500 | Cảnh báo, tách khi chạm vào file |
| < 300 | Giữ nguyên nếu đơn trách nhiệm |

- Thực trạng đã vượt: `ModalCreateOrder.vue` 1193, `DrawerOrderDetail.vue` 1091, `DrawerStep2Director.vue` 935, `CatalogView.vue` 992 → slice S7.
- Mỗi component mới: 1 câu mô tả trách nhiệm duy nhất trong PR/commit message.

## 3. Data Fetching — Chỉ Qua `api()`
- SSOT client: `composables/useSession.js::api()` — tự prefix `/api/method/vanphat_portal.api.*`, gắn `X-Frappe-CSRF-Token`, unwrap `message`, toast lỗi thống nhất, hỗ trợ `signal` (AbortController) + `silent`.
- Luật:
  - Search/tab/pagination: debounce 250–300ms + abort request cũ, chỉ render response mới nhất (chống race).
  - GET cho read/preview, POST cho create/submit. Không GET gây mutation.
  - Cấm: `fetch` trực tiếp rải rác, `.filter()`/`startsWith('TP-')` phân tab trên dataset monolithic, fallback CSV/mock, sinh ID client (`Math.random`), mutate trạng thái local không qua backend.
  - Format-only ở client: `Intl.NumberFormat('vi-VN')`. Mọi tiền/thuế/cọc/BOM/tồn kho/status do backend trả sẵn.

## 4. Router & Code-Splitting
- Hiện trạng: 3 route import tĩnh (`OrdersView`, `QuotesView`, `CatalogView`) + 4 redirect, bọc `keep-alive` trần.
- Chuẩn mục tiêu:
  - Route `() => import()` động 100% (Orders/Quotes/Catalog + Drawer/Modal nặng qua `defineAsyncComponent` + `<Suspense>`).
  - `keep-alive`: CHỈ list đọc nhiều, có `include` + `max` 5–10, refresh `onActivated`, cleanup `onDeactivated`. Không keep-alive form tạo đơn (tránh state cũ).
  - Hash history giữ nguyên (khớp Frappe serve static, không cần server rewrite).

## 5. Build & Performance Budget
- `build.target`: tối thiểu baseline-widely-available (thay `es2015` — target cũ kéo polyfill/transform thừa, tăng bundle).
- Budget: initial JS gzip ≤ 170KB warn / 300KB fail; async chunk warn 500KB. Vượt → tách tiếp, không nâng budget.
- Đo: `vite build --report` + Lighthouse CI (không regress điểm Perf/A11y/Best-practice).
- RUM sau deploy: `web-vitals` p75 — LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1 (LAN gate nội bộ: LCP ≤ 1.5s). Chưa có bench staging → chưa đo runtime, cấm bịa số.

## 6. A11y & UX Áp Cho Mọi View
- Theo cockpit spec §5 DoD 12 mục: text+màu trạng thái, contrast ≥ 4.5:1, label cho input, `aria-label` badge số, touch ≥ 24px, drawer `role=dialog` + focus trap/restore, skeleton `aria-busy` truthful, empty state có bước tiếp theo, error toast có retry.
- Breakpoints: 1024 sidebar icon-only, 768 drawer full-screen, 320 card thay table.

## 7. Cấm Tuyệt Đối (Nhắc Lại Từ AGENTS.md)
- Client math tài chính (VAT 8%, cọc 50%, tiền trục 3.1M) — đã phát hiện tại `QuotesView.vue:327`, `OrdersView.vue:337`, `DrawerOrderDetail.vue` nhiều dòng → slice S1/S9 xóa.
- Hằng số thương mại hardcode — chuyển về backend native templates.
- `keep-alive` trần không `include/max`, static import toàn bộ route, `target es2015`.
