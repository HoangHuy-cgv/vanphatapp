# Plan: Backlog sau cleanup triple-rule (Sếp duyệt thứ tự)

## Đã xong
- **Simplify + tối ưu backend API**: `_common.py`, hết N+1, tiền native một ngữ nghĩa
  (`product_total = net_total − cylinder_total`, trục chưa VAT, `qty` bỏ trục), count báo giá
  khớp filter, POST tự commit, bỏ `FALLBACK_VAT_RATE`. 46 test trong `apps/vanphat_portal/tests/`.
- **Chuẩn "tối ưu" có máy kiểm**: `CONSTRAINTS.md` (triple rule ghim + 5 trục + floor 10 luật +
  ratchet) và `scripts/constraints-check.py` (floor trong pre-commit; `--init` ghi baseline).
- **Guard frontend**: `apps/vanphat_portal/frontend/check-composables.mjs` — import + khởi tạo
  mọi composable trong Node; bắt lỗi mà `vite build` không thấy.
- **Ghim `frappe-ui 1.0.0-beta.64`** (POC bỏ frappe-ui ở nhánh `poc/no-frappe-ui` giữ làm dự phòng).
- **ADR-005 (2026-09-14)**: config native là SSOT giao diện, visual custom duy nhất; cấm portal list
  native cho SO (frappe#42640 còn mở); hoãn Studio tới khi đủ 3 điều kiện. UI §7 + DoD 13–15
  (không đào tạo, click-chọn, flow raw-data).
- **ADR-006 (2026-09-15)**: một ngữ nghĩa tiền + một HOLD + một envelope + `api()` duy nhất.
- **Triple rule slice (2026-09-15, `b1de2ff`)**: 3 endpoints config native
  (`get_product_groups/get_payment_options/get_print_config`); ModalCreateOrder bỏ `<select>`
  cứng → nút click-chọn + search-select KH; DrawerStep2 vật liệu từ cấu trúc màng native;
  `qty` gợi ý từ `min_order_qty`; picker KH/NCC/User paginate + search server.
- **Cleanup (slice này)**: xóa CSS chết, biến submit chết, ảnh mẫu cứng, `defineExpose` chết,
  `loadAllCatalogData` tải thừa; xóa JSON mock local; `serve-portal.mjs` gắn boundary LOCAL ONLY;
  docs/rule/policy/skill cùng một ngữ cảnh (triple rule).

## Còn lại (chờ Sếp ra việc — KHÔNG đụng trước khi Sếp chốt)
1. **Quyền — rủi ro cao nhất**: 22/27 endpoint chưa cổng quyền (gồm 3 endpoint config mới —
   chờ cổng chung); `order.list_orders` và `item.get_list` đi `frappe.qb` nên **bỏ qua
   permission model**; 4 mutation (tạo/submit SO, ghi cọc, duyệt ngoại lệ) không role gate.
   Cần Sếp chốt **ai được làm gì**.
2. **Bench staging ERPNext thật**: import master data (`data/clean-data/` + `scripts/import_master_data.py`);
   đo **p95 thật cho `list_orders` (<200ms)**; đo LCP/INP/CLS; cấu hình
   **Default Company = Bao Bì Vạn Phát** (thiếu là tạo đơn báo lỗi).
3. **Vitest**: chưa cài được (máy này không ra được npm registry + `~/.npm` không ghi được).
4. **Stack frontend**: giữ `frappe-ui` ghim version (POC dự phòng ở nhánh `poc/no-frappe-ui`).
   Rà lại Studio khi đủ 3 điều kiện mở lại (ADR-005 §5).
5. **Remote + push**: chưa có remote — Sếp cho URL + lệnh explicit.
6. **Nợ nghiệp vụ chờ Sếp**: enforce BTP `is_sales_item=0` ở Đơn bán; MST KH 0/117; cuộn màng tiêu
   chưa mã (BTP bán được hiện chỉ 00015); phân loại TMD theo `item_group`/prefix;
   golden test engine báo giá `calculate_packaging_quotation` (slice riêng, ADR-002).
