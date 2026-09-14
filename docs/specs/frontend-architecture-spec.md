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

## 3. Data Fetching — Chỉ Qua `api()` (kể cả upload FormData — ADR-006)
- SSOT client: `composables/useSession.js::api()` — tự prefix `/api/method/vanphat_portal.api.*`, gắn `X-Frappe-CSRF-Token`, unwrap `message`, toast lỗi thống nhất, hỗ trợ `signal` (AbortController) + `silent` + `FormData` (upload `upload_file`: không set `Content-Type` tay để browser gắn boundary, vẫn gắn CSRF + toast + signal). Cấm mọi `fetch()` trực tiếp trong `src/`.
- Luật:
  - Search/tab/pagination: debounce 250–300ms + abort request cũ, chỉ render response mới nhất (chống race).
  - GET cho read/preview, POST cho create/submit. Không GET gây mutation.
  - Đọc đúng envelope `page_result`; không đỡ mảng trần (sau migrate customer/supplier/user — ADR-006).
  - Picker tham chiếu (customer/supplier/user) tải một lần qua envelope (`default 100, max 100` + filter server ở backend); không xin `page_length` vượt trần 100. Slice sau paginate picker + search server.
  - Cấm: `fetch` trực tiếp rải rác, `.filter()`/`startsWith('TP-')` phân tab trên dataset monolithic, fallback CSV/mock, sinh ID client (`Math.random`), mutate trạng thái local không qua backend, **tự tính lại `rate`/`amount`/`qty` từ field tiền ở client** (ADR-006: `DrawerOrderDetail` fallback `rate = product_total/qty`, `totalItemQty .reduce`, `QuotesView calculatePackaging .reduce` + `|| 5000` — đã xóa), **tự set `order_state`/`completed_qty`/`is_hold` sau mutate** (đọc lại từ response/server).
  - Không identity/user/email cứng trong client (`giamdoc@vanphat.com` đã xóa — ADR-006; sidebar hiện trạng thái đăng nhập thật từ `get_boot`).
  - Format-only ở client: `Intl.NumberFormat('vi-VN')`. Mọi tiền/thuế/cọc/BOM/tồn kho/status do backend trả sẵn.
  - VAT doc-driven + trục pass-through NCC (`cylinder_spec {qty, unit_price, supplier}` — ADR-002): cấm math tay và mọi fallback số trục.

## 4. Router & Code-Splitting
- Hiện trạng (đã làm, sửa mô tả cũ "import tĩnh" cho đúng code): 3 route lazy động 100%
  (`OrdersView`/`QuotesView`/`CatalogView` qua `() => import()` — `router/index.js:4-6`) + 4 redirect,
  bọc `Suspense` + `keep-alive include="OrdersView,CatalogView,QuotesView" :max="5"` (`App.vue:104-117`).
  Form tạo đơn/báo giá KHÔNG keep-alive (tránh state cũ).
- Chuẩn mục tiêu còn lại: drawers/modals nặng qua `defineAsyncComponent` +
  `loadingComponent delay:200 + errorComponent/timeout:3000`.
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

## 7. Cấm Tuyệt Đối (Nhắc Lại Từ AGENTS.md + ADR-006)
- Client math tài chính + toán tiền/thuế tay trong Python — preview/báo giá/đơn đọc số native đã tính
  (một ngữ nghĩa tiền duy nhất: `product_total = net_total − cylinder_total`, chưa VAT, không trục — ADR-006).
- `fetch()` trực tiếp trong `src/` (kể cả upload — đi qua `api()` hỗ trợ FormData).
- `<select>` cho ≤ 8 phương án (chuẩn là nút click-chọn `role=radiogroup`/`radio`; `<select>` còn lại
  trong ModalCreateOrder là nợ plan item 3, không phải chuẩn).
- Hardcode config UI mới trong Vue (options/defaults/labels/thứ tự từ native — ADR-005/ADR-006);
  cái đã lỡ hardcode rút dần theo plan item 3, không thêm mới.
- `keep-alive` trần không `include/max`, static import toàn bộ route.
- Tailwind v4 (preset frappe-ui chỉ hỗ trợ v3); CSS entry trùng Tailwind directives; 2 `FrappeUIProvider` (toast double).
