# Plan: Backlog sau cleanup (Sếp duyệt thứ tự)

## Đã xong
- Ignore build hash-churn; entry `www/portal.html` + `public/frontend/index.html` tracked.
- `DrawerCustomerDetail` đọc bảng con native (hết liệt rỗng).
- Hook check-only + CSV LF gốc.
- **Simplify + tối ưu backend API**: `_common.py`, hết N+1 (`list_orders` 33→6 query/trang,
  BOM alias 1 query, detail 1 query Item), tiền native thống nhất (trục chưa VAT,
  `product_total = net_total − cylinder_total`, `qty` bỏ trục), count báo giá khớp filter,
  POST tự commit, bỏ `FALLBACK_VAT_RATE`. Lưới an toàn: 41 test trong `apps/vanphat_portal/tests/`.

## Còn lại (chờ Sếp ra việc)
1. **Remote + push**: chưa có remote — Sếp cho URL + lệnh explicit.
2. **Bench staging ERPNext thật**: import 293 items + 45 dòng con + BOM; verify
   VAT doc-driven, Credit Limit, **đo p95 thật cho `list_orders` (mục tiêu <200ms)** rồi
   mới chốt hiệu năng; đo LCP/INP/CLS. Cấu hình **Default Company = Bao Bì Vạn Phát**.
3. **Role check + permission**: nhánh qb (`order.list_orders`, `item.get_list` khi search/tab SP)
   chưa áp permission như `get_list`; thêm role check theo spec §6.
4. **Enforce BTP ở Đơn bán**: `is_sales_item=0` mới ở data; luồng Báo giá/Đơn bán
   portal chưa lọc cờ này.
5. **MST KH 0/117**: không xuất được hóa đơn VAT thật.
6. **Cuộn màng tiêu**: chưa có mã — Sếp báo sau (BTP bán được hiện chỉ 00015).
7. **Phân loại TMD ở drawer**: `_item_product_group` chưa bắt được tên thật "Túi nilon HD..."
   → Sếp chốt phân loại theo `item_group`/prefix thay vì chuỗi tên.
8. **Mốc HOLD ở danh sách đơn** đang dùng `grand_total*0.5` (gồm VAT + trục) trong khi drawer
   dùng `required_deposit` — cần thống nhất một công thức.
9. **Golden test engine báo giá** (`calculate_packaging_quotation`) trước khi chạm vào
   (ADR-002: slice engine riêng, chờ Sếp duyệt).
