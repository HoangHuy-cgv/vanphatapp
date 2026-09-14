# Plan: Backlog sau audit kiến trúc (Sếp duyệt thứ tự)

## Đã xong
- **Simplify + tối ưu backend API**: `_common.py`, hết N+1 (`list_orders` 33→6 query/trang,
  BOM alias 1 query, detail 1 query Item), tiền native thống nhất (trục chưa VAT,
  `product_total = net_total − cylinder_total`, `qty` bỏ trục), count báo giá khớp filter,
  POST tự commit, bỏ `FALLBACK_VAT_RATE`. 41 test trong `apps/vanphat_portal/tests/`.
- **Chuẩn "tối ưu" có máy kiểm**: `CONSTRAINTS.md` (5 trục + floor + ratchet) và
  `scripts/constraints-check.py` (floor 0,1s trong pre-commit; ratchet `--init` để ghi baseline).
- **Guard frontend**: `apps/vanphat_portal/frontend/check-composables.mjs` — import + khởi tạo
  mọi composable trong Node; bắt lỗi mà `vite build` không thấy.
- **Fix lỗi production**: `serverPricingInitial` thiếu từ `d30fdd6` → modal "Tạo đơn hàng"
  ném ReferenceError, chết hoàn toàn. Đã sửa, đã kiểm chứng trên Chrome thật.
- **POC bỏ frappe-ui** (nhánh `poc/no-frappe-ui`): entry JS 145→49 kB gzip, CSS 54→6 kB gzip.
- Ghim `frappe-ui` đúng `1.0.0-beta.64` (nhánh beta, stable vẫn là 0.1.278).
- **ADR-005 (2026-09-14, em quyết định theo ủy quyền):** config native là SSOT của giao diện
  (Custom Field/Property Setter/DocType Layout/Data Masking/Website Theme), code custom chỉ ở tầng
  visual; giữ Modal 1 + Drawer 2, cấm portal list native cho Sales Order (frappe#42640 còn mở);
  hoãn Frappe Studio tới khi đủ 3 điều kiện mở lại. UI spec §7 (§7.1 flow raw-data, §7.2 config native)
  + DoD 13–15 đã chốt theo yêu cầu Sếp: không đào tạo, click-chọn thay dropdown, visual theo flow raw-data.
- **ADR-006 (2026-09-15, em quyết định theo ủy quyền):** một ngữ nghĩa tiền + một công thức
  HOLD + một envelope list + `api()` là đường fetch duy nhất (kể cả upload). Đối chiếu
  docs ↔ code phát hiện preview tính `product_total` gồm VAT (lệch list/drawer), list HOLD
  mốc `grand_total*0.5` (lệch drawer), master lists trả mảng trần, 2 `fetch()` trực tiếp,
  `page_length: 500`, client math/set-state sau mutate, user cứng. Slice nhất-quán này sửa hết.

## Còn lại (chờ Sếp ra việc)
1. **Quyền — rủi ro cao nhất**: 19/24 endpoint chưa có cổng quyền; `order.list_orders` và
   `item.get_list` đi `frappe.qb` nên **bỏ qua permission model**; 4 mutation (tạo/submit SO,
   ghi cọc, duyệt ngoại lệ) không có role gate. Cần Sếp chốt **ai được làm gì**.
2. **Chốt stack frontend**: xem số đo POC ở nhánh `poc/no-frappe-ui` rồi quyết
   (giữ frappe-ui ghim version / tự viết 3 component / theo reviewer đổi shadcn-vue).
   ↳ Sếp đổi ưu tiên (2026-09-14): chỉ phân tích Studio trước, **không cài** — xem ADR-005.
   Rà lại Studio khi đủ 3 điều kiện mở lại.
3. **Rút config cứng trong Vue ra native (ADR-005):** vật liệu màng (`DrawerStep2Director.vue:59-120`),
   default vật liệu (`useStep2DirectorForm.js:21`), 4 option nhóm SP (`ModalCreateOrder.vue:49-52`),
   print_type (`ModalStep1Sale.vue:117-134,292`), nhóm + `qty` mặc định (`useCreateOrderForm.js:85,100,226,278`).
   Dùng field native sẵn có (`custom_print_tech`, `custom_accessory_spec`); Custom Field mới phải kèm
   ADR + mapping entry (AGENTS.md).
4. **Vitest**: chưa cài được (máy này không ra được npm registry + `~/.npm` không ghi được).
5. **Remote + push**: chưa có remote — Sếp cho URL + lệnh explicit.
6. **Bench staging ERPNext thật**: import master data; đo **p95 thật cho `list_orders` (<200ms)**;
   đo LCP/INP/CLS; cấu hình **Default Company = Bao Bì Vạn Phát** (thiếu là tạo đơn báo lỗi).
7. **Enforce BTP ở Đơn bán**: `is_sales_item=0` mới ở data; portal chưa lọc cờ này.
8. **MST KH 0/117**: không xuất được hóa đơn VAT thật.
9. **Cuộn màng tiêu**: chưa có mã — Sếp báo sau (BTP bán được hiện chỉ 00015).
10. **Phân loại TMD ở drawer**: `_item_product_group` chưa bắt được tên thật "Túi nilon HD..."
    → Sếp chốt phân loại theo `item_group`/prefix thay vì chuỗi tên.
11. ~~**Mốc HOLD ở danh sách đơn** đang dùng `grand_total*0.5`~~ → **xong trong slice ADR-006**:
    list + drawer chung một công thức (Trả trước AND `0 < advance_paid < required_deposit`).
12. **Golden test engine báo giá** (`calculate_packaging_quotation`) trước khi chạm vào
    (ADR-002: slice engine riêng, chờ Sếp duyệt).
13. **Rút config cứng còn lại trong Vue ra native (ADR-005/ADR-006, không thuộc slice nhất-quán):**
    `<select>` nhóm SP/KH/thanh toán trong `ModalCreateOrder.vue` → nút click-chọn +
    search-select đọc native; defaults `qty`/vật liệu/nhóm SP → `min_order_qty`/Item Group tree;
    plan item 3 cũ gộp vào đây.
