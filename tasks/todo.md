# Ephemeral Todo: Chuẩn Hóa Bộ Dữ Liệu Giao Dịch (Transactions)

> **Policy**: File này là bảng nháp tạm thời (Ephemeral Scratchpad). Khi hoàn thành và commit Git, dọn sạch task cũ.

## Active Milestone: Transactions Dataset (ERPNext Native v16)

- [ ] Task 1: Trích xuất & chuẩn hóa Đơn bán hàng (`Sales Order` & `Sales Order Item`) từ `TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx` thành `sales_order_master.csv` và `sales_order_items.csv`.
- [ ] Task 2: Trích xuất & chuẩn hóa Đơn mua hàng NCC (`Purchase Order` & `Purchase Order Item`) từ `tien do dat hang ncc.xlsx` và `TIEN DO MUA HÀNG NCC T8.xlsx` thành `purchase_order_master.csv` và `purchase_order_items.csv`.
- [ ] Task 3: Trích xuất & chuẩn hóa Lệnh sản xuất xưởng (`Work Order`) từ `TIẾN ĐỘ SẢN XUẤT.xlsx` thành `work_order_master.csv`.
- [ ] Task 4: Trích xuất & chuẩn hóa Bút toán thu chi cọc (`Payment Entry`) từ `THU CHI - 2026 vanphat.xlsx` thành `payment_entry_master.csv`.
- [ ] Task 5: Viết bộ test kiểm thử đối soát toàn vẹn (Integrity Verification) cho dữ liệu giao dịch và cập nhật CI Gate.
