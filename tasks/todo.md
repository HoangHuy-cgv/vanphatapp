# Todo List: Trang 1 — Đơn Hàng & Tiền Cọc

- [x] Task 1: Nâng cấp Backend APIs Quản Lý Đơn Hàng & Tiền Cọc (`bao_gia.py`)
  - Nâng cấp `list_orders` (advance_paid, outstanding_amount, item_name, total_qty).
  - Viết `get_order_details(name)`, `record_order_deposit(name, amount, is_vip_guarantee, note)` và `submit_sales_order(name)`.
  - Files: `apps/vanphat_portal/vanphat_portal/api/bao_gia.py`

- [x] Task 2: Xây dựng Component Drawer Chi Tiết Đơn Hàng (`DrawerOrderDetail.vue`)
  - Giao diện slideover từ phải sang, theme Industrial Dark.
  - Hiển thị mặt hàng, tổng tiền, số tiền đã cọc, còn nợ, % cọc.
  - Hộp xác nhận cọc & nút Submit đơn hàng.
  - Files: `apps/vanphat_portal/frontend/src/components/DrawerOrderDetail.vue`

- [x] Task 3: Tích hợp Bảng Đơn Hàng Mới vào `App.vue`
  - Cập nhật bảng `orders` (bổ sung cột Đã cọc, Còn nợ, Mặt hàng).
  - Thêm sự kiện `@click="openOrderDetail"` mở Drawer.
  - Giữ nguyên 100% `quotes`, `ModalStep1Sale.vue`, `DrawerStep2Director.vue`.
  - Files: `apps/vanphat_portal/frontend/src/App.vue`

- [x] Task 4: Kiểm Thử & Biên Dịch Vite
  - Build frontend: `yarn build` thành công 100% không lỗi.
  - Output đồng bộ vào `vanphat_portal/public/frontend/` và `vanphat_portal/www/portal.html`.
