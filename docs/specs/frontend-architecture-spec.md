# Kiến Trúc Frontend Thin Client (Vue 3 + Vite + Frappe UI)

> **SSOT:** Mọi quy tắc frontend tập trung tại file này. `AGENTS.md` §4 chỉ tóm tắt. Code thực tế: `apps/vanphat_portal/frontend/src/`.

## 1. Stack Lock & Ranh Giới (phương án R Sếp duyệt 2026-09-15)
- Vue 3.5 Composition API + `<script setup>`, vue-router 4 hash history, `frappe-ui@1.0.0-beta.64`, Vite 7, Tailwind v3 + preset `frappe-ui/tailwind` (spread `content`), Zero-Node (static do Frappe Nginx serve tại `/portal`).
- `main.js`: CSS entry `@import 'frappe-ui/style.css'` (không Tailwind directives trùng), `<FrappeUIProvider>` đúng 1 lần ở root (mount `dialog.*`/`toast.*` portals; 2 provider = toast double).
- Cấm: React/Svelte/HTMX/Alpine/Jinja-ad-hoc, Options API cho code mới, `v-html`, jQuery/DOM thủ công thay reactive state, Tailwind v4 (preset shape không tương thích — skill frappe-ui SETUP.md).
- Route view = composition surface (app shell + wiring + feature composition). Logic stateful/side-effect → `composables/useXxx.js`. UI section → child component (props down / events up).

## 2. Ngưỡng Tách Component (Enforced)
| Dòng SFC | Hành động |
|---|---|
| > 500 | Bắt buộc tách trước khi thêm tính năng mới |
| 300–500 | Cảnh báo, tách khi chạm vào file |
| < 300 | Giữ nguyên nếu đơn trách nhiệm |

- Thực trạng sau S7+P4 (đo lại 2026-09-15): `ModalCreateOrder.vue` ~954, `DrawerOrderDetail.vue` ~970, `DrawerStep2Director.vue` ~827, `CatalogView.vue` ~631 + 6 composables (~1.1k dòng có tổ chức). Drawers cuốn chiếu sang `BaseDrawer` native `<dialog>`.
- Mỗi component mới: 1 câu mô tả trách nhiệm duy nhất trong PR/commit message.

## 3. Data Fetching — Chỉ Qua `api()` (migrate dần sang `useCall`/`useList`/`useDoc`)
- SSOT client hiện tại: `composables/useSession.js::api()` — tự prefix `/api/method/vanphat_portal.api.*`, gắn `X-Frappe-CSRF-Token`, unwrap `message`, toast lỗi thống nhất, hỗ trợ `signal` (AbortController) + `silent`.
- Đích frappe-ui v2 (không deprecated trong 1.x — v1-release plan): code mới dùng `useCall` (whitelisted method/REST), `useList` (list phân trang/filter), `useDoc` (1 doc reactive), `useDoctype`/`useNewDoc` (ghi/draft). Code `api()` cũ giữ nguyên, migrate khi chạm file.
- Luật:
  - Search/tab/pagination: debounce 250–300ms + abort request cũ, chỉ render response mới nhất (chống race).
  - GET cho read/preview, POST cho create/submit. Không GET gây mutation.
  - Cấm: `fetch` trực tiếp rải rác, `.filter()`/`startsWith('TP-')` phân tab trên dataset monolithic, fallback CSV/mock, sinh ID client (`Math.random`), mutate trạng thái local không qua backend.
  - Format-only ở client: `Intl.NumberFormat('vi-VN')`. Mọi tiền/thuế/cọc/BOM/tồn kho/status do backend trả sẵn.
  - VAT doc-driven + trục pass-through NCC (`cylinder_spec {qty, unit_price, supplier}` — ADR-002): cấm math tay và mọi fallback số trục.

## 4. Router & Code-Splitting
- Hiện trạng: 3 route import tĩnh (`OrdersView`, `QuotesView`, `CatalogView`) + 4 redirect, bọc `keep-alive` trần.
- Chuẩn mục tiêu:
  - Route `() => import()` động 100% (Orders/Quotes/Catalog + Drawer/Modal nặng qua `defineAsyncComponent` + `<Suspense>`).
  - `keep-alive`: CHỈ list đọc nhiều, có `include` + `max` 5–10, refresh `onActivated`, cleanup `onDeactivated`. Không keep-alive form tạo đơn (tránh state cũ).
  - Hash history giữ nguyên (khớp Frappe serve static, không cần server rewrite).

## 5. Build & Performance Budget (phương án R Sếp duyệt 2026-09-15)
- Xóa `build.target` cứng → về default `baseline-widely-available` (= chrome111/edge111/firefox114/safari16.4, mốc 2026-01-01 — vite.dev/config/build-options). Chỉ giữ target thấp hơn khi còn máy xưởng < Chrome 111.
- Xóa `manualChunks vendor-vue` (tự chia vendor dễ phản tác dụng — vite#12209; Rolldown deprecated → `advancedChunks`). Giữ route-lazy + async drawers + `Suspense`; thêm `loadingComponent delay:200 + errorComponent/timeout:3000` cho drawers.
- Budget (làm rõ đơn vị): `chunkSizeWarningLimit: 500` (uncompressed, theo V8); CI gate trên **gzip**: initial warn 170KB / fail 300KB, async chunk warn 500KB. Gate chạy trên `dist` static (`scripts/budget-gate.sh`), `reportCompressedSize: true`.
- `modulePreload.polyfill: false` khi toàn bộ máy nội bộ đạt Baseline; font Inter subset latin+vietnamese + `font-display:swap`.
- Đo: `vite-bundle-visualizer` + Lighthouse CI khi có staging (không regress Perf/A11y/Best-practice).
- RUM sau deploy: `web-vitals` p75 — LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1 (LAN gate nội bộ: LCP ≤ 1.5s). Chưa có bench staging → chưa đo runtime, cấm bịa số.

## 6. A11y & UX Áp Cho Mọi View
- Theo cockpit spec §5 DoD 12 mục: text+màu trạng thái, contrast ≥ 4.5:1, label cho input, `aria-label` badge số, touch ≥ 24px, drawer native `<dialog>` + `BaseDrawer` (`showModal`, Esc/inert/focus miễn phí từ browser, cấm `tabindex` trên `<dialog>`), skeleton `aria-busy` truthful, empty state có bước tiếp theo, error toast có retry.
- Breakpoints: 1024 sidebar icon-only, 768 drawer full-screen, 320 card thay table.
- Modals giữa màn hình → `Dialog` chính chủ frappe-ui (`v-model:open`, đối chiếu API trong `node_modules` bản beta đang dùng); confirm/nhập liệu đơn giản → `dialog.confirm/danger/prompt`; `after-leave` reset form.

## 7. Cấm Tuyệt Đối (Nhắc Lại Từ AGENTS.md)
- Client math tài chính + toán tiền/thuế tay trong Python — preview/báo giá/đơn đọc số native đã tính (VAT doc-driven, trục pass-through NCC — ADR-002).
- `keep-alive` trần không `include/max`, static import toàn bộ route.
- Tailwind v4 (preset frappe-ui chỉ hỗ trợ v3); CSS entry trùng Tailwind directives; 2 `FrappeUIProvider` (toast double).
