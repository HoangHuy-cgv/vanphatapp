# BẢN ĐỒ ĐẶC TẢ HỆ THỐNG (SSOT CAPABILITY MAP) — BAO BÌ VẠN PHÁT

> **Nguyên Tắc Tối Thượng:** 
> 1. **ERPNext Native làm Backend:** 100% logic nghiệp vụ, công thức tính toán, trạng thái chứng từ và phân quyền nằm ở Backend Frappe/ERPNext v16 (`vanphat_portal.api`).
> 2. **Frontend là Lớp Vỏ Mỏng (Thin Client):** Vue 3 SPA chỉ nhận dữ liệu hiển thị (data-binding) và phát sự kiện, tuyệt đối không chứa logic tính toán hay phán đoán trạng thái.
> 3. **Một Nguồn Chân Lý Duy Nhất (Single Source of Truth - SSOT):** Mỗi thông tin chỉ tồn tại ở đúng một file chuyên trách, load on-demand theo ngữ cảnh. Tuyệt đối cấm sao chép rải rác dẫn đến xung đột ngầm.

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

### [Module 1: Schema, Thuật Ngữ & Naming Series](file:///var/home/huy/vanphatapp/docs/specs/erpnext-native-vi-en-mapping.md)
- **Tệp SSOT:** `docs/specs/erpnext-native-vi-en-mapping.md`
- **Nội dung:** 
  - Quy chuẩn Naming Series Frappe Native v16 reset tự động hàng tháng (`KH-.#####`, `NCC-.#####`, `DH-.YY..MM.-.###`, `BG-.YY..MM.-.###`, `MH-.YY..MM.-.###`, `LSX-`, `GH-`, `NH-`, `HD-`, `PT-`, `PC-`).
  - Ánh xạ 100% fieldnames tiếng Anh sang tiếng Việt của 16 DocTypes ERPNext Native (`Customer`, `Item`, `Sales Order`, `Quotation`, `Purchase Order`, `Supplier`, `Work Order`, `Delivery Note`, `Purchase Receipt`, `Sales Invoice`, `Payment Entry`, `Warehouse`, `Operation`, `Workstation`, `BOM`, `User`).
- **Khi nào tải:** Bất kỳ khi nào viết Python API, ORM migration, Schema fixture, hoặc thiết kế câu truy vấn dữ liệu.

### [Module 2: Master Data, Phân Cấp Bao Bì & Kịch Bản Bán Hàng](file:///var/home/huy/vanphatapp/docs/specs/erpnext-packaging-masterdata-spec.md)
- **Tệp SSOT:** `docs/specs/erpnext-packaging-masterdata-spec.md`
- **Nội dung:**
  - Cây phân cấp nhóm hàng (`MÀNG`, `TÚI`, `PHỤ KIỆN`, `TRỤC IN`).
  - Chuẩn mực 5 ĐVT (`Túi`, `Kg`, `m`, `Cây`, `Cái`).
  - Quy tắc định danh: `item_name` (pháp lý đầy đủ cho hóa đơn/hợp đồng) vs `custom_alias` (thương mại ngắn gọn cho buồng lái tác nghiệp).
  - 5 Kịch bản kinh doanh: MTS (túi nước giặt có sẵn in sẵn), MTO (sản xuất theo đơn đặt độc quyền), PTO (túi màng đơn mua ngoài), 1 Brand nhiều chủ, Sản phẩm ngừng kinh doanh.
- **Khi nào tải:** Khi làm việc với danh mục hàng hóa, phân loại sản phẩm, hoặc thiết lập quy trình tạo đơn hàng.

### [Module 3: Toán Kỹ Thuật & Thuật Toán Sản Xuất](file:///var/home/huy/vanphatapp/docs/specs/packaging-calculation-spec.md)
- **Tệp SSOT:** `docs/specs/packaging-calculation-spec.md`
- **Nội dung:**
  - Công thức GSM, Yield diện tích màng theo tỷ trọng ASTM D792.
  - Công thức tính diện tích trải của túi 3 biên, túi xếp hông, túi đáy đứng Doypack.
  - Định mức keo khô, dung môi EA bay hơi trong sấy.
  - Ma trận hao hụt (Scrap Matrix) qua từng công đoạn thổi, in, ghép, cắt, đóng vòi.
  - Thuật toán báo giá 2 nấc: Nấc 1 (Tròn cuộn $1.500\text{ m}$ tối ưu) vs Nấc 2 (Đúng số lượng yêu cầu kèm phụ phí rủi ro màng thừa).
  - Nguyên tắc bóc tách độc lập tiền trục in ống đồng (`TRUC-`) khỏi giá túi.
- **Khi nào tải:** Khi lập trình API tính giá, sinh định mức BOM, hoặc tính toán khối lượng màng/keo.

### [Module 4: Chuẩn Giao Diện Buồng Lái Công Nghiệp](file:///var/home/huy/vanphatapp/docs/specs/ui-cockpit-baseline-spec.md)
- **Tệp SSOT:** `docs/specs/ui-cockpit-baseline-spec.md`
- **Nội dung:**
  - 5 Trụ cột buồng lái: Header 1 dòng, Bảng khóa cứng 1 dòng single-line, Trạng thái thuần màu 14px in đậm, Số liệu căn phải tabular-nums, Drawer chiều sâu kỹ thuật.
  - Bảng màu Industrial Dark Palette và Typography font `Inter` native.
  - Nguyên tắc Thin-Client: Cấm tính toán tiền và logic trạng thái ở Vue.
- **Khi nào tải:** Khi thiết kế hoặc chỉnh sửa bất kỳ giao diện nào (Page, Drawer, Modal, Table).

### [Module 5: Kiến Trúc Frontend Thin Client](file:///var/home/huy/vanphatapp/docs/specs/frontend-architecture-spec.md)
- **Tệp SSOT:** `docs/specs/frontend-architecture-spec.md`
- **Nội dung:**
  - Stack lock Vue 3 + `<script setup>` + hash router + Frappe UI + Vite Zero-Node.
  - Ngưỡng tách component (> 500 bắt buộc), data fetching chỉ qua `api()` + debounce/Abort, route lazy + `keep-alive` có kiểm soát, build target + budget.
- **Khi nào tải:** Khi viết/sửa bất kỳ file nào trong `apps/vanphat_portal/frontend/src/`.

### [Module 6: Ranh Giới Backend Native API](file:///var/home/huy/vanphatapp/docs/specs/backend-native-api-spec.md)
- **Tệp SSOT:** `docs/specs/backend-native-api-spec.md`
- **Nội dung:**
  - Module map 6 API, lookup native-first 4 tầng, query `get_list`/`frappe.qb` chữa N+1, chuẩn GET/POST + commit, cache key đủ params + invalidate `doc_events`, checklist bảo mật, lộ trình native hóa hằng số VAT/cọc/trục.
- **Khi nào tải:** Khi viết/sửa bất kỳ file nào trong `apps/vanphat_portal/vanphat_portal/api/`.
