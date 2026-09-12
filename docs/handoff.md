# Handoff Chuyển Giao Session Mới — ERP & Portal Vạn Phát (vanphatapp)
*Thời điểm bàn giao: 2026-09-12 | Cập nhật sau khi hoàn thành Danh mục Nhóm A & Hoàn thiện Frontend Portal + Drawer*

---

## 1. TỔNG KẾT HIỆN TRẠNG ĐÃ HOÀN THÀNH 100%

### 1.1. Kiến Trúc Hệ Thống & Tech Stack (Strict SSOT)
- **Văn bản quy chuẩn duy nhất**: [AGENTS.md](../AGENTS.md) (Vue 3 + Frappe UI + Tailwind CSS, Zero-Node production runtime, cấm tiệt openpyxl, dùng fastexcel / python-calamine lõi Rust).
- **Mã nguồn đã dọn dẹp**: Không còn file spec rải rác hay script cũ gây nhiễu context.

### 1.2. Dữ Liệu Nền Tảng Nhóm A (Clean Datasets & Scripts)
Đã sinh hoàn chỉnh bộ dữ liệu sạch tại [data/clean-data/](file:///var/home/huy/vanphatapp/data/clean-data/):
1. [item_master.csv](file:///var/home/huy/vanphatapp/data/clean-data/item_master.csv): **275 mặt hàng** chuẩn hóa theo chuỗi mã (`TP-`, `NVL-`, `BTP-`, `TRUC-`, `NGCS-`).
2. [item_spec.csv](file:///var/home/huy/vanphatapp/data/clean-data/item_spec.csv): **275 thông số kỹ thuật** đặc thù bao bì (độ dày, bước cắt dao, cấu trúc ghép, loại vòi).
3. [warehouses.csv](file:///var/home/huy/vanphatapp/data/clean-data/warehouses.csv): **5 kho** tinh gọn (Kho NVL, Kho BTP, Kho TP, Kho Phế Liệu, Kho Trục In).
4. [suppliers.csv](file:///var/home/huy/vanphatapp/data/clean-data/suppliers.csv): **10 Nhà Cung Cấp** verified từ sổ công nợ.
5. [operations.csv](file:///var/home/huy/vanphatapp/data/clean-data/operations.csv): **5 công đoạn & trạm máy** (In ống đồng, Ghép màng khô, Chia cuộn, Cắt túi đáy đứng, Đóng vòi).
6. [bom_master.csv](file:///var/home/huy/vanphatapp/data/clean-data/bom_master.csv) & [bom_items.csv](file:///var/home/huy/vanphatapp/data/clean-data/bom_items.csv): **60 Định mức BOM 2 cấp** (BOM túi thành phẩm và Sub-BOM cuộn màng ghép BTP) với **218 dòng chi tiết** vật tư.
7. [scripts/import_master_data.py](file:///var/home/huy/vanphatapp/scripts/import_master_data.py): Script nạp dữ liệu tự động, kiểm thử Dry-run **100% Passed**.

### 1.3. Giao Diện Frontend Portal (Vue 3 + Tailwind CSS - Đã Nghiệm Thu UX/UI)
- **Trang Login**: Đạt chuẩn, căn chỉnh thẳng hàng với thương hiệu, Autofill font lock.
- **Trang Portal (`/portal`)**:
  - **Logo**: Trích xuất logo monogram **VP đỏ** nguyên bản từ website `baobivanphat.com`, bỏ khung nền trắng thô, hiệu ứng drop-shadow tinh tế.
  - **Sidebar tinh gọn (216px)**: Icon SVG, badge số lượng Báo giá & Đơn hàng, chân trang hiển thị User profile + Nút Logout (đã kết nối route API logout).
  - **Typography & Bảng Portal**: Font chữ tăng lên `15px`, tiêu đề cột `13.5px`, padding thoáng đãng, phân cấp thị giác rõ ràng.
- **Modal Bước 1 (Sale)**: 5 dáng bao bì thích ứng thông minh, chọn trục, tìm kiếm khách hàng nhanh.
- **Drawer Bước 2 (Giám đốc)**:
  - Bỏ khối kịch bản tính giá 2 nấc theo yêu cầu, tập trung trực tiếp vào bảng danh sách mẫu in (Tên mẫu in, Số lượng, Đơn giá).
  - Thay chip `PE` đơn lẻ thành 2 chip riêng biệt: **`PE sữa`** và **`PE trong`** (tổng 9 chip chia 4 nhóm màng).
  - Bỏ toàn bộ khung viền hộp thô cứng (`spec-box`, `spec-line`, `mat-chip`), thiết kế phẳng và thanh thoát.
  - Cả **9 chip chất liệu nằm thẳng hàng trên đúng 1 line duy nhất (`flex-wrap: nowrap`)**.
  - Đồng bộ **cùng 1 kích thước font (`14px`)** cho toàn bộ cụm thông tin đầu Drawer (Tên KH, Badges dáng túi/phụ kiện/in ấn/trục in, Mô tả sản phẩm, Kích thước kỹ thuật).
- **Gói build**: Đã build tĩnh `npm run build` sẵn sàng tại `apps/vanphat_portal/vanphat_portal/public/frontend/` và `www/portal.html`.

### 1.4. Hạ Tầng VPS (`13.213.13.201` - `app.vanphat.io.vn`)
- **Trạng thái**: 10 Docker containers đang UP ổn định tại cổng 8080.
- **Database MariaDB `_745a2e8c74667527`**: Trắng 100% (0 Items, 0 Customers, 0 BOMs), sẵn sàng nhận nạp dữ liệu sạch khi có lệnh `"Chạy script"`.

---

## 2. VIỆC CÒN TỒN ĐỌNG (BACKLOG CẦN XỬ LÝ)

### 2.1. Việc Cần Xử Lý Tiếp Theo (Next Priority)
1. **Đồng bộ mã nguồn App & Bản build Frontend lên VPS Staging**:
   - Đồng bộ thư mục `apps/vanphat_portal` (backend API `bao_gia.py` và thư mục static `vanphat_portal/public/frontend/` + `www/portal.html`) lên máy chủ VPS `13.213.13.201`.
2. **Nạp Master Data Nhóm A vào MariaDB trên VPS**:
   - Khi Sếp duyệt lệnh `"Chạy script"`, thực thi nạp 275 items, 5 kho, 10 nhà cung cấp, 5 operations, 60 BOMs vào MariaDB VPS.
3. **Kiểm thử End-to-End Báo giá trên VPS**:
   - Thử nghiệm tạo báo giá từ Portal ngoài web $\rightarrow$ Kiểm tra đơn Báo giá (Quotation) xuất hiện tự động trong hệ thống ERPNext trên VPS.

### 2.2. Dữ Liệu Nhóm B (Kinh Doanh & Tài Chính)
1. **Danh mục Khách hàng**: Trích xuất từ các file Excel đơn cọc và công nợ để tạo danh sách khách hàng và thương hiệu chuẩn.
2. **Bảng giá bán theo đối tác & Số dư tồn kho ban đầu**.

---

## 3. CÂU LỆNH MẪU KHI MỞ SESSION MỚI

Khi Sếp mở session mới, Sếp chỉ cần gửi câu lệnh sau:

```text
Đọc docs/handoff.md và tiếp tục triển khai:
1. Đồng bộ mã nguồn app và bản build Frontend mới lên VPS app.vanphat.io.vn.
2. Nạp Master Data Nhóm A vào MariaDB trên VPS và kiểm thử End-to-End luồng tạo Báo giá.
```

