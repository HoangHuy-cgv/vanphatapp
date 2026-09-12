# Implementation Plan: Trang 1 — Đơn Hàng & Tiền Cọc (Orders & Deposit)

## Overview
Xây dựng màn hình Đơn Hàng chính thức cho Vạn Phát Portal theo chuẩn frappe/crm (danh sách phẳng tinh gọn, click dòng mở Drawer chi tiết từ phải sang), tuân thủ 100% SSOT ERPNext v16 Backend, và tuyệt đối không đụng vào trang Báo Giá hiện tại, Modal 1 và Drawer 2.

## Task Breakdown
1. **Task 1: Backend APIs for Orders & Deposit Control (`bao_gia.py`)**
   - Nâng cấp `list_orders` trả về `advance_paid`, `outstanding_amount`, `item_name`, `total_qty`.
   - Thêm `get_order_details(name)` lấy đầy đủ items, thông tin cọc và điều kiện submit.
   - Thêm `record_order_deposit(name, amount, is_vip_guarantee, note)`.
   - Thêm `submit_sales_order(name)` với validation chặn submit nếu chưa đủ cọc / chưa duyệt VIP.

2. **Task 2: Drawer Chi Tiết Đơn Hàng (`DrawerOrderDetail.vue`)**
   - Xây dựng component slideover từ phải sang theo chuẩn Industrial Dark.
   - Hiển thị bảng chi tiết mặt hàng, số lượng, đơn giá.
   - Hiển thị tiến độ cọc (% cọc, đã cọc, còn nợ).
   - Form nhập cọc / Checkbox bảo lãnh VIP + nút Submit đơn hàng.

3. **Task 3: Tích hợp Trang Đơn Hàng vào `App.vue`**
   - Cập nhật bảng `view === 'orders'` với các cột thực tế: Ngày | Mã | Khách (Alias) | Mặt hàng | SL | Tổng tiền | ĐÃ CỌC | CÒN NỢ | Trạng thái.
   - Bắt sự kiện `@click="openOrderDetail(order)"` để mở Drawer.
   - Giữ nguyên 100% phần `view === 'quotes'`, `ModalStep1Sale.vue`, `DrawerStep2Director.vue`.

4. **Task 4: Build Verification & Testing**
   - Chạy `yarn build` kiểm tra biên dịch Vite.
   - Test luồng click dòng mở Drawer, nhập cọc và submit đơn hàng.
