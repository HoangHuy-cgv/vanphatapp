# Implementation Plan: Chuẩn Hóa Dữ Liệu Giao Dịch Thực Tế (Transaction Datasets)

## Mục Tiêu
Trích xuất và chuẩn hóa toàn bộ dữ liệu giao dịch thực tế từ các file Excel gốc sang các file CSV định dạng chuẩn ERPNext Native v16, đảm bảo tính toàn vẹn khóa ngoại (Foreign Keys) liên kết với Master Data đã có (`Item`, `Customer`, `Supplier`, `User`).

## Các Phân Hệ Giao Dịch Cốt Lõi
1. **Đơn Bán Hàng (`Sales Order`)**:
   - `sales_order_master.csv`: `name`, `customer`, `transaction_date`, `delivery_date`, `grand_total`, `status`...
   - `sales_order_items.csv`: `parent`, `item_code`, `qty`, `rate`, `amount`...
2. **Đơn Mua Hàng Nhà Cung Cấp (`Purchase Order`)**:
   - `purchase_order_master.csv` & `purchase_order_items.csv` (In gia công, Keo, Dung môi, Vòi, In lụa).
3. **Lệnh Sản Xuất Xưởng (`Work Order`)**:
   - `work_order_master.csv` (Tiến độ 24 đợt chạy máy xưởng: Ghép, Cắt, Đóng gói).
4. **Bút Toán Thu Chi & Cọc (`Payment Entry`)**:
   - `payment_entry_master.csv` (Thu tiền cọc đơn hàng, thanh toán tiền hàng NCC).

## Tiêu Chí Nghiệm Thu (Acceptance Criteria)
- 100% mã hàng `item_code`, mã khách `customer`, mã NCC `supplier` khớp chính xác với Master Data.
- Script trích xuất tự động `scripts/generate_transaction_data_csv.py` sử dụng `fastexcel` / `python-calamine`.
- Test suite kiểm tra tính toàn vẹn đạt 100% PASS.
