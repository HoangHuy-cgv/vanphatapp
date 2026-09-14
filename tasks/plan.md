# Kế Hoạch Triển Khai: Xử Lý Điểm Nghẽn, Xung Đột Ngầm & Chuẩn Hóa Buồng Lái Cockpit Toàn Diện

## 1. Định Hướng Kỹ Thuật (SSOT & ERPNext Native v16)
- **Rules & Clean-up**: Duy nhất 1 file `AGENTS.md` gốc; loại bỏ tệp rác `master-data.html` (972 KB).
- **Naming Series**: Đồng bộ 100% mã sang `KH-#####`, `NCC-#####`, `DH-.YY..MM.-.###`, `BG-.YY..MM.-.###`.
- **Backend Schema & Fixtures**: Khắc phục bộ lọc Property Setter trong `hooks.py`, bổ sung fixture options cho `Quotation` & `Sales Order`, an toàn hóa truy vấn `credit_limit` từ child table `Customer Credit Limit`.
- **Cockpit 5 Trụ Cột**:
  1. Header 1 dòng: Tabs + Quick Search + Action Button.
  2. Bảng khóa cứng 1 dòng single-line: Bỏ progress bar, mỗi ô 1 giá trị.
  3. Trạng thái thuần màu 14px in đậm: Bỏ toàn bộ border, background hộp, bullet dot `●`.
  4. Số liệu tabular-nums căn phải.
  5. Drawer đảm nhiệm 100% chiều sâu: Chuyển các nút tác nghiệp từ bảng chính vào Drawer.

## 2. Phân Rã Tác Vụ
- [x] **Task 1**: Xóa bỏ `apps/vanphat_portal/frontend/AGENTS.md` và `www/master-data.html`.
- [x] **Task 2**: Chuẩn hóa Naming Series & Clean-data (`extract_customer_master_from_raw.py`, `extract_supplier_master_from_raw.py`, `customer_master.csv`, `supplier_master.csv`, `local_orders.json`, `local_quotations.json`, `serve-portal.mjs`).
- [x] **Task 3**: Cấu hình Backend fixtures & Native queries (`hooks.py`, `property_setter.json`, `customer.py`, `bao_gia.py`).
- [x] **Task 4**: Chuẩn hóa giao diện buồng lái Cockpit Baseline (`OrdersView.vue`, `QuotesView.vue`, `CatalogView.vue`, `DrawerItemDetail.vue`, `DrawerUserDetail.vue`, `DrawerOrderDetail.vue`, `DrawerStep2Director.vue`, `portal.css`).
- [x] **Task 5**: Mở rộng `verify-catalog-page.mjs`, build Vite, kiểm chứng trình duyệt và cập nhật `docs/handoff.md`.
