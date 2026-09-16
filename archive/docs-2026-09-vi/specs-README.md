# BẢN ĐỒ ĐẶC TẢ HỆ THỐNG (SSOT CAPABILITY MAP) — BAO BÌ VẠN PHÁT

> **Triple rule ghim (Sếp chốt 2026-09-15): backend native + config native + visual custom.**
> 1. **ERPNext Native làm Backend:** logic nghiệp vụ, công thức tính toán, trạng thái chứng từ
>    nằm ở DocType/controller native; `vanphat_portal.api` chỉ là façade mỏng.
> 2. **Config native làm SSOT giao diện:** options/defaults/labels/thứ tự/ẩn-hiện từ Custom Field /
>    Property Setter / DocType Layout / Item Group / `min_order_qty` / Payment Terms / Credit Limit.
> 3. **Visual custom phần còn lại:** Vue cockpit chỉ viết bố cục, Modal/Drawer, màu, nút click-chọn,
>    diễn đạt flow thân thiện — cấm chứa tiền/thuế/trạng thái/cấu hình.
> 4. **Một Nguồn Chân Lý Duy Nhất (SSOT):** Mỗi thông tin chỉ tồn tại ở đúng một file chuyên trách,
>    load on-demand theo ngữ cảnh. Tuyệt đối cấm sao chép rải rác dẫn đến xung đột ngầm.

---

## BẢN ĐỒ 6 MODULE ĐẶC TẢ CHUYÊN BIỆT (LOAD ON-DEMAND)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              BẢN ĐỒ ĐẶC TẢ HỆ THỐNG (SSOT)                                     │
├───────────────────────────────┬──────────────────────────────────┬─────────────────────────────┤
│ Module Đặc Tả                 │ Tệp Tin SSOT Duy Nhất            │ Trách Nhiệm Chuyên Trách    │
├───────────────────────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 1. Schema & Naming Series     │ erpnext-native-vi-en-mapping.md  │ 16 DocTypes, Native Fields, │
│                               │                                  │ Naming Series (KH-, DH-...) │
├───────────────────────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 2. Phân Cấp Hàng & Kịch Bản   │ erpnext-packaging-masterdata-    │ Cây 4 nhóm hàng, 5 UOM,     │
│                               │ spec.md                          │ 5 kịch bản bán (MTS, MTO)   │
├───────────────────────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 3. Toán Kỹ Thuật Sản Xuất     │ packaging-calculation-spec.md    │ GSM, Keo/Dung môi, Đóng vòi,│
│                               │                                  │ Hao hụt, Báo giá 2 nấc      │
├───────────────────────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 4. Chuẩn Buồng Lái UI/UX      │ ui-cockpit-baseline-spec.md      │ 5 Trụ cột buồng lái, Dark   │
│                               │                                  │ Palette, WCAG 1.4.1, DoD      │
├───────────────────────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 5. Kiến Trúc Frontend         │ frontend-architecture-spec.md    │ Vue thin client, router,    │
│                               │                                  │ budget, ngưỡng tách 500L    │
├───────────────────────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 6. Ranh Giới Backend Native   │ backend-native-api-spec.md       │ Thin wrapper, get_list/qb,  │
│                               │                                  │ cache key, native hóa rates │
└───────────────────────────────┴──────────────────────────────────┴─────────────────────────────┘
```

---

## CHI TIẾT ĐỊNH TUYẾN & RANH GIỚI TỪNG MODULE

### [Module 1: Schema, Thuật Ngữ & Naming Series](./erpnext-native-vi-en-mapping.md)
- **Tệp SSOT:** `docs/specs/erpnext-native-vi-en-mapping.md`
- **Nội dung:**
  - Quy chuẩn Naming Series Frappe Native v16 reset tự động hàng tháng (`KH-.#####`, `NCC-.#####`, `DH-.YY..MM.-.###`, `BG-.YY..MM.-.###`, `MH-.YY..MM.-.###`, `LSX-`, `GH-`, `NH-`, `HD-`, `PT-`, `PC-`).
  - Ánh xạ 100% fieldnames tiếng Anh sang tiếng Việt của 16 DocTypes ERPNext Native (`Customer`, `Item`, `Sales Order`, `Quotation`, `Purchase Order`, `Supplier`, `Work Order`, `Delivery Note`, `Purchase Receipt`, `Sales Invoice`, `Payment Entry`, `Warehouse`, `Operation`, `Workstation`, `BOM`, `User`).
- **Khi nào tải:** Bất kỳ khi nào viết Python API, ORM migration, Schema fixture, hoặc thiết kế câu truy vấn dữ liệu.

### [Module 2: Master Data, Phân Cấp Bao Bì & Kịch Bản Bán Hàng](./erpnext-packaging-masterdata-spec.md)
- **Tệp SSOT:** `docs/specs/erpnext-packaging-masterdata-spec.md`
- **Nội dung:**
  - Cây phân cấp nhóm hàng (`MÀNG`, `TÚI`, `PHỤ KIỆN`, `TRỤC IN`).
  - Chuẩn mực 5 ĐVT (`Túi`, `Kg`, `m`, `Cây`, `Cái`).
  - Quy tắc định danh: `item_name` (pháp lý đầy đủ cho hóa đơn/hợp đồng) vs `custom_alias` (thương mại ngắn gọn cho buồng lái tác nghiệp).
  - 5 Kịch bản kinh doanh: MTS (túi nước giặt có sẵn in sẵn), MTO (sản xuất theo đơn đặt độc quyền), PTO (túi màng đơn mua ngoài), 1 Brand nhiều chủ, Sản phẩm ngừng kinh doanh.
- **Khi nào tải:** Khi làm việc với danh mục hàng hóa, phân loại sản phẩm, hoặc thiết lập quy trình tạo đơn hàng.

### [Module 3: Toán Kỹ Thuật & Thuật Toán Sản Xuất](./packaging-calculation-spec.md)
- **Tệp SSOT:** `docs/specs/packaging-calculation-spec.md`
- **Nội dung:**
  - Công thức GSM, Yield diện tích màng theo tỷ trọng ASTM D792.
  - Công thức tính diện tích trải của túi 3 biên, túi xếp hông, túi đáy đứng Doypack.
  - Định mức keo khô, dung môi EA bay hơi trong sấy.
  - Ma trận hao hụt (Scrap Matrix) qua từng công đoạn thổi, in, ghép, cắt, đóng vòi.
  - Thuật toán báo giá 2 nấc: Nấc 1 (Tròn cuộn $1.500\text{ m}$ tối ưu) vs Nấc 2 (Đúng số lượng yêu cầu kèm phụ phí rủi ro màng thừa).
  - Nguyên tắc bóc tách độc lập tiền trục in ống đồng (`TRUC-`) khỏi giá túi.
- **Khi nào tải:** Khi lập trình API tính giá, sinh định mức BOM, hoặc tính toán khối lượng màng/keo.

### [Module 4: Chuẩn Giao Diện Buồng Lái Công Nghiệp](ui-cockpit-baseline-spec.md)
- **Tệp SSOT:** `docs/specs/ui-cockpit-baseline-spec.md`
- **Nội dung:**
  - 5 Trụ cột buồng lái: Header 1 dòng, Bảng khóa cứng 1 dòng single-line, Trạng thái chữ+màu 14px, Số liệu căn phải tabular-nums, Drawer chiều sâu kỹ thuật.
  - Bảng màu Industrial Dark Palette và Typography font `Inter` native.
  - Triple rule 3 (visual custom): click-chọn `radiogroup` ≤ 8 phương án, search-select cho danh sách động, flow raw-data, không đào tạo.
- **Khi nào tải:** Khi thiết kế hoặc chỉnh sửa bất kỳ giao diện nào (Page, Drawer, Modal, Table).

### [Module 5: Kiến Trúc Frontend Thin Client](frontend-architecture-spec.md)
- **Tệp SSOT:** `docs/specs/frontend-architecture-spec.md`
- **Nội dung:**
  - Stack lock Vue 3 + `<script setup>` + hash router + Frappe UI + Vite Zero-Node.
  - Ngưỡng tách component (> 500 bắt buộc), data fetching chỉ qua `api()` (kể cả FormData) + debounce/Abort, route lazy + `keep-alive` có kiểm soát, build target + budget.
  - Đọc envelope `page_result`, picker paginate + search server, config endpoints native.
- **Khi nào tải:** Khi viết/sửa bất kỳ file nào trong `apps/vanphat_portal/frontend/src/`.

### [Module 6: Ranh Giới Backend Native API](backend-native-api-spec.md)
- **Tệp SSOT:** `docs/specs/backend-native-api-spec.md`
- **Nội dung:**
  - Module map API (order/bao_gia/item/customer/supplier/user + `_common`), lookup native-first 4 tầng, query `get_list`/`frappe.qb` chữa N+1, chuẩn GET/POST + commit, cache key đủ params + invalidate `doc_events`, một ngữ nghĩa tiền + một HOLD (ADR-006), envelope `page_result`, endpoints config native (`get_product_groups/get_payment_options/get_print_config`).
- **Khi nào tải:** Khi viết/sửa bất kỳ file nào trong `apps/vanphat_portal/vanphat_portal/api/`.

---

## BẢN ĐỒ SKILL (khi nào gọi skill nào — AGENTS.md §How we work)

| Việc | Skill | Ghi chú |
|---|---|---|
| Tính giá / BOM / định mức màng-keo | `packaging-calculation-engine` | Kèm `packaging-calculation-spec.md`; engine R&D là hằng số xưởng, không native hóa (ADR-002) |
| Component / Dialog / toast frappe-ui | `frappe-ui` | Đọc `SETUP.md` khi dựng trang; đối chiếu API trong `node_modules` bản beta đang dùng |
| Bất kỳ file Vue / router / Vite | `vue-best-practices` | Composition API + `<script setup>` |
| Viết API / whitelist / permission | `api-development` | + `frappe-app-dev` cho app/bench/site |
| DocType / field / controller mới | `frappe-doctype-development` | Custom field mới phải kèm ADR + mapping entry |
| Ghi ADR / docs | `documentation-and-adrs` | ADR mới đánh số tiếp, không xóa ADR cũ |
| Chất lượng bar / CONSTRAINTS | `constraint-driven-development` | Siết im lặng, nới phải to tiếng + Exceptions |
| Review trước merge | `code-review-and-quality` | Chạy sau mỗi slice |
