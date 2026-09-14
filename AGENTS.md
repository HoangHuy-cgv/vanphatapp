# AGENTS.md - Van Phat Packaging ERP & Portal

## 1. Operating Persona & Protocols
- **Language & Persona**: ALWAYS communicate in Vietnamese. Address User as `Sếp`, self as `em`. User dictates business rules; Assistant dictates technical architecture and execution.
- **Anti-Sycophancy**: NEVER agree performatively. Challenge flawed assumptions, performance regressions, or boundary violations directly with quantitative evidence before proposing solutions.
- **Zero Speculation & ERPNext Native Wording**: NEVER speculate or fabricate fields, DocTypes, or attributes. STRICTLY use ERPNext native columns and DocTypes officially mapped in `docs/specs/erpnext-native-vi-en-mapping.md`. Forbidden to use data from `archive/`.
- **Mandatory Pre-Action Skill Inspection**: For any non-trivial task, Agent MUST inspect the relevant skill via the `skill` tool before execution. Never apply skills implicitly.
- **Clean-on-Done & Ephemeral Scratchpad Policy**: Code, tests, and Git history are the ONLY SSOT. Once a milestone is committed, immediately reset/clean `tasks/todo.md`. Never accumulate historical tasks across milestones. `docs/handoff.md` is strictly an operational rolling pointer (< 25 lines) overwritten every session, NEVER appended.

## 2. Native-First Architecture (Nguyên Tắc Tối Thượng)

Thứ tự ưu tiên bắt buộc khi cần bất kỳ dữ liệu/logic nào — luôn chọn tầng cao nhất còn đáp ứng được:

1. **ERPNext native DocType / field / method** (`Quotation`, `Sales Order`, `Payment Entry`, `BOM`, `Item Price`, `Sales Taxes and Charges Template`, `Payment Terms Template`, `Customer Credit Limit`, `UOM`, `Item Group`, `File`).
2. **Frappe framework API** (`frappe.db.get_list` + `filters/start/page_length/order_by`, `frappe.qb` cho join, `frappe.cache`, `frappe.has_permission`, naming series `tabSeries`).
3. **Thin wrapper** trong `vanphat_portal.api.*` — chỉ bọc native, không chứa nghiệp vụ trùng native.
4. **Custom field / Custom DocType** — CHỈ khi chứng minh được native không có và không cấu hình được; bắt buộc tiền tố `custom_`, ghi ADR vào `docs/decisions/`, ánh xạ vào `erpnext-native-vi-en-mapping.md`.

**Cấm tuyệt đối:**
- Custom trùng chức năng native đã có (tự chế status/đặt cọc/thuế khi native `status`, `docstatus`, `advance_paid`, `Sales Taxes and Charges Template` đã có).
- Raw SQL cho CRUD thông thường (`frappe.qb`/`get_list` là chuẩn; raw SQL chỉ cho báo cáo join phức tạp, cấm mutation trực tiếp production).
- Hằng số thương mại hardcode ở frontend (`vatRate = 0.08`, `cylinderRate = 3100000`) — và cấm hardcode trong Python: VAT doc-driven (gán Sales Taxes Template lên draft doc, đọc số ERPNext tính — ADR-002); giá trục pass-through NCC qua `cylinder_spec {qty, unit_price, supplier}`, cấm mọi fallback số trục; cọc từ `Payment Terms Template` + `Customer Credit Limit`.
- `frappe.get_all` cho master data nhạy cảm (bypass permission) — bắt buộc `get_list`.
- `@frappe.whitelist(allow_guest=True)` cho dữ liệu nội bộ — portal bắt buộc login + role check (`System Manager`, `Sales User`, `Accounts User`, `Manufacturing User`, `Stock User`).
- Toán tiền/thuế tay trong Python (`round(net*rate)`, `qty*rate` build dòng trục ở client) — preview/báo giá/đơn đọc số native đã tính.

## 3. Van Phat Industrial Cockpit Baseline (UI/UX Rules)
- **Reference Spec**: All UI views MUST comply with `docs/specs/ui-cockpit-baseline-spec.md`.
- **Elon Musk Minimalist Content**: Zero tutorial notes, zero explanatory prose, zero helper subtitles. The UI is an industrial operational cockpit, not a manual.
- **Short Alias Enforcement (SSOT)**: 100% of UI views, tables, drawers, and child rows MUST prioritize `custom_alias`. STRICTLY PROHIBIT rendering full legal `item_name` as static text (tooltip `:title` only).
- **The 5 Mandatory Pillars**:
  1. *Header 1 dòng*: `[Tabs] + [Quick Search flex-1] + [Action Button]`. Zero sub-filter chips, zero secondary dropdown bars.
  2. *Khóa cứng 1 dòng (Single-line)*: Tables locked to 5–7 core columns, height 42–46px. Every cell contains 1 value only. Strictly forbid stacking ID subtitles under names. Hide non-essential columns (e.g. credit limit) to give full width to long legal names.
  3. *Trạng thái chữ + màu 14px in đậm (WCAG 1.4.1)*: Mọi trạng thái PHẢI có text label tiếng Việt phân biệt (VD "Chờ cọc" vs "Đã duyệt" vs "Quá hạn") tô màu theo bảng chuẩn (Amber/Sky/Emerald/Red/Tím). Màu KHÔNG BAO GIỜ là kênh duy nhất — text là bắt buộc. Zero borders, zero background boxes, zero bullet dots (`●`), zero icons. Text contrast ≥ 4.5:1 (xem ADR-001).
  4. *Chuẩn số liệu & Căn lề*: Column headers 1–3 words. All numeric columns right-aligned (`text-right`) in bold `tabular-nums`. Hide 100% unused columns (e.g. empty BOM rate).
  5. *Drawer đảm nhiệm 100% chiều sâu*: Main table is for rapid glance; 100% technical specs, BOM breakdowns, tooling, and debt details belong in slide-over drawers (`role=dialog aria-modal`, `Esc`/backdrop đóng, restore focus về nút trigger).
- **A11y & Responsive floor**: text thường contrast ≥ 4.5:1; mọi input có `<label>`; badge số có `aria-label`; touch target ≥ 24px; breakpoints 1024 (sidebar icon-only) / 768 (drawer full-screen) / 320 (card thay table). Skeleton truthful `aria-busy`, empty state nêu bước tiếp theo, error toast có retry.

## 4. Frontend Architecture (Vue 3 Thin Client)
- **Reference Spec**: `docs/specs/frontend-architecture-spec.md`.
- **Stack lock**: Vue 3 Composition API + `<script setup>`, vue-router hash history, `frappe-ui`, Vite, Zero-Node (static do Frappe Nginx serve tại `/portal`). Cấm React/Svelte/HTMX/Alpine/Jinja-ad-hoc.
- **Thin view**: route view là composition surface; logic stateful/side-effect → `composables/useXxx.js`, UI section → child component (props down/events up). Ngưỡng tách: > 500 dòng bắt buộc tách, > 300 dòng cảnh báo (`ModalCreateOrder.vue` 1193 + `DrawerOrderDetail.vue` 1091 đã vượt — xem slice S7).
- **Data fetching**: CHỈ qua `api()` trong `composables/useSession.js` (tự prefix `/api/method/vanphat_portal.api.*`, gắn CSRF, unwrap `message`). Search debounce 250–300ms + `AbortController` hủy request cũ, chỉ render response mới nhất. Cấm `v-html`, cấm filter `.filter()`/`startsWith('TP-')` trên dataset monolithic, cấm mock/fallback CSV, cấm sinh ID client.
- **Perf**: route `() => import()` động 100%; drawer/modal nặng `defineAsyncComponent` + `<Suspense>`; `keep-alive` CHỈ cho list đọc nhiều (`include` + `max` 5–10, refresh `onActivated`, cleanup `onDeactivated`); `build.target` tối thiểu baseline-widely-available; budget initial JS gzip ≤ 170KB (warn) / 300KB (fail), chunk warn 500KB.
- **Format-only ở client**: `Intl.NumberFormat('vi-VN')` cho hiển thị; mọi tiền/thuế/cọc/BOM/tồn kho/status do backend trả sẵn.

## 5. Backend API Boundaries (Thin Wrappers over Native)
- **Reference Spec**: `docs/specs/backend-native-api-spec.md`.
- **Module map**: `order.py` (Sales Order lifecycle + preview giá/cọc), `bao_gia.py` (Quotation + `calculate_packaging`), `item.py` (Item/BOM catalog + cache), `customer.py`/`supplier.py`/`user.py` (master data). Không re-export ghi đè câm (bug `get_price_preview` đã biết — slice S4).
- **Pagination server-side**: `frappe.db.get_list(doctype, fields, filters, or_filters, order_by, start, page_length)`; `page_length` mặc định 15, trần tối đa 100; cấm `limit=500` rồi filter Python/client; join nhiều DocType bằng `frappe.qb` 1 query (chữa N+1); `debug=True` khi soi SQL.
- **Chuẩn method**: GET cho read/preview, POST cho create/submit (tự `db.commit`); response `{message:...}`, lỗi `{exc, exc_type}`; trạng thái buồng lái (`order_status_label/class`, `required_deposit`, `outstanding_amount`, `deposit_pct`) tính server từ native `status/docstatus/advance_paid/Credit Limit`.
- **Cache**: key PHẢI chứa mọi params (`vp:items:list|tab=&q=&page=`), TTL 300s, invalidate chủ động qua `doc_events` (Item/Quotation/Customer/Sales Order `on_update`); cấm endpoint guest xả cache.
- **GET chi tiết**: `get_doc` + `has_permission` tại nơi action; child table truyền `parent` để check quyền.

## 6. Strict Prohibitions (Còn Hiệu Lực)
- **Forbidden Libraries**: `openpyxl` STRICTLY PROHIBITED (memory stalls). Use `fastexcel` or `python-calamine`.
- **Zero Mock Data & Zero In-Memory Simulation**: Cấm `mockData.js`/`dummy.json`/fixture hardcode, cấm `Math.random()` sinh ID chứng từ, cấm mutate trạng thái local không qua backend. DB trống → empty state truthful.
- **API-First & Backend-Persistence**: 100% CRUD/workflow (create, deposit, approve, submit, cancel) qua `vanphat_portal.api.*`, persist MariaDB trước khi update UI.
- **Production Runtime**: Zero-Node. Vite static served by Frappe Nginx / Gunicorn.
- **Git Boundaries**: Commit atomically with conventional commit prefixes. NEVER `git push` unless explicitly ordered.
- **Pre-commit Gates (check-only, no auto-fix)**: Hooks chỉ kiểm tra, KHÔNG tự sửa file (tránh xung đột stash tốn vòng commit). Viết đúng từ gốc (CSV `newline="\n"`, Python tabs). Hook báo lỗi → sửa tay → `git add` → commit lại.
- **Hook Bypass (ngoại lệ duy nhất)**: Chỉ bypass (`-c core.hooksPath=/dev/null`) khi hook xung đột stash sau khi đã sửa tay đúng mà hook vẫn restore vòng lặp — ghi rõ lý do vào message commit. Cấm bypass để lách ruff/forbid-patterns.
- **Database Safety**: Schema sync via standard bench commands. Raw SQL mutations against production MariaDB only with caution + backup.

## 7. Quality Gates (Definition of Done)
- Mọi slice: có baseline → fix → re-measure cùng điều kiện; thay đổi trong noise (±5%) thì revert + ghi ledger.
- UI checklist: Single-line 42–46px / Zero subtitle / Status text+màu / Header 1 dòng / Số right tabular-nums / Clean columns / Drawer Esc+focus-restore / 100% Inter / Zero client logic (chi tiết `ui-cockpit-baseline-spec.md` §5).
- A11y: contrast 4.5:1, không keyboard trap (WCAG 2.1.2), drawer `role=dialog` + focus trap + restore.
- Perf: bundle trong budget, Lighthouse CI không regress, RUM `web-vitals` p75 (LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1; LAN gate LCP ≤ 1.5s).
- Security: không guest lộ master data, không `get_all` sai chỗ, không XSS (`v-html`), CSRF đầy đủ POST.

## 8. Domain Knowledge & SSOT References
Agent MUST read and adhere to official project specifications in `docs/specs/` load on-demand instead of guessing business logic:
- Central Capability Map: `docs/specs/README.md`
- ERPNext Native Schema, Fields & Naming Series: `docs/specs/erpnext-native-vi-en-mapping.md`
- Master Data & Packaging Taxonomy: `docs/specs/erpnext-packaging-masterdata-spec.md`
- Packaging Calculation Engine & Math: `docs/specs/packaging-calculation-spec.md`
- UI Cockpit Baseline & Thin Client: `docs/specs/ui-cockpit-baseline-spec.md`
- Frontend Architecture (Vue/Vite): `docs/specs/frontend-architecture-spec.md`
- Backend Native API (Frappe/ERPNext): `docs/specs/backend-native-api-spec.md`
- Architecture Decisions: `docs/decisions/` (ADR-001: Pillar 3 vs WCAG 1.4.1, ...)
