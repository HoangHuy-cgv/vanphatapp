# Handoff Chuyển Giao Session Mới — ERP & Portal Vạn Phát (vanphatapp)
*Thời điểm bàn giao: 2026-09-12 | Cập nhật sau khi hoàn thành Danh mục Nhóm A & Hoàn thiện Frontend Portal + Drawer*

---

## 1. TỔNG KẾT HIỆN TRẠNG ĐÃ HOÀN THÀNH 100%

### 1.1. Kiến Trúc & Định Hướng (Local-First Build Mode)
- **Định hướng chiến lược theo lệnh Sếp**: Tập trung hoàn thiện 100% tại môi trường **Local** trước khi đưa lên Cloud/Staging.
- **Git Checkpoint**: Đã tạo commit `681fd11` ("feat: complete portal & drawer UI, logo, and master data nhom A pipeline") lưu toàn bộ mã nguồn và dữ liệu sạch.
- **Dọn dẹp VPS Staging (`13.213.13.201`)**: Đã tắt sạch 10 containers docker (`docker compose down`) và xóa trắng mã nguồn ứng dụng tại `/opt/vanphat/apps/vanphat_portal` theo chỉ đạo của Sếp. VPS hiện ở trạng thái 0 container chạy, an toàn tuyệt đối.

### 1.2. Dữ Liệu Nền Tảng Nhóm A (Đã Nạp & Tích Hợp Vào Local Server)
Đã nạp toàn bộ dữ liệu sạch tại [data/clean-data/](file:///var/home/huy/vanphatapp/data/clean-data/) vào server Local:
1. [item_master.csv](file:///var/home/huy/vanphatapp/data/clean-data/item_master.csv): **275 mặt hàng** chuẩn hóa (`TP-`, `NVL-`, `BTP-`, `TRUC-`, `NGCS-`).
2. [item_spec.csv](file:///var/home/huy/vanphatapp/data/clean-data/item_spec.csv): **275 thông số kỹ thuật** đặc thù bao bì.
3. [warehouses.csv](file:///var/home/huy/vanphatapp/data/clean-data/warehouses.csv): **5 kho** tinh gọn.
4. [suppliers.csv](file:///var/home/huy/vanphatapp/data/clean-data/suppliers.csv): **10 Nhà Cung Cấp** verified.
5. [operations.csv](file:///var/home/huy/vanphatapp/data/clean-data/operations.csv): **5 công đoạn & trạm máy**.
6. [bom_master.csv](file:///var/home/huy/vanphatapp/data/clean-data/bom_master.csv) & [bom_items.csv](file:///var/home/huy/vanphatapp/data/clean-data/bom_items.csv): **60 Định mức BOM 2 cấp** với **218 dòng chi tiết** vật tư.
7. **Trang Rà Soát Dữ Liệu Trực Quan Web**: Đã tạo trang review trực tiếp tại **`http://localhost:8080/master-data`** với bộ lọc thời gian thực cho từng bảng dữ liệu (Mặt hàng, Specs, BOMs, Kho, NCC, Khách hàng).

### 1.3. Kiểm Thử End-to-End Báo Giá & Đơn Hàng Tại Local (Task 4 Đạt 100%)
- **Hệ thống Server Local**: File `scripts/serve-portal.mjs` đang chạy daemon tại cổng 8080, phục vụ đầy đủ API mô phỏng chuẩn Frappe REST API.
- **Quy trình End-to-End đã kiểm thử thành công**:
  1. *Tìm kiếm khách hàng*: Tìm kiếm realtime theo danh mục 48 khách hàng thực tế (vd: Lâm Gia, VMT Group, An Nhiên...).
  2. *Soạn báo giá*: Bước 1 (Sale) chọn dáng túi + kích thước $\rightarrow$ Bước 2 (Giám đốc) chọn màng (PET/AL/PE sữa), nhập số lượng và đơn giá $\rightarrow$ Tính toán tiền trục cách ly và thuế VAT 8%.
  3. *Lưu trữ bền vững*: Báo giá mới tự động gán mã `BG-2026-xxxx` và lưu vào `data/local_quotations.json`.
  4. *Luồng duyệt & chốt đơn*:
     - Nút "Gửi QLSX" chuyển trạng thái sang `Open`.
     - Nút "Chốt" chuyển trạng thái sang `Ordered` và sinh tự động Đơn bán hàng `SO-2026-xxxx` tại tab Đơn hàng (`data/local_orders.json`).
     - Nút "Rớt" đánh dấu `Lost` kèm lý do.

---

## 2. VIỆC CÒN TỒN ĐỌNG CHO SESSION MỚI (BACKLOG)

1. **Rà soát dữ liệu Nhóm A cùng Sếp**:
   - Sếp mở trình duyệt tại `http://localhost:8080/master-data` để rà soát danh sách 275 items, 60 BOMs, quy cách kỹ thuật.
2. **Trải nghiệm và hoàn thiện luồng Báo giá Local**:
   - Sếp vào `http://localhost:8080/portal` để trực tiếp tạo các báo giá mẫu, kiểm tra tính thuận tiện của các thao tác Sale và Giám đốc.
3. **Master Data Nhóm B (Kinh doanh & Tài chính - Làm sau cùng theo chỉ đạo)**:
   - Khai thác mở rộng danh sách khách hàng đầy đủ, bảng giá phân phối và số dư tồn kho ban đầu từ file Excel cũ khi 4 việc trên đã nghiệm thu xong.

---

## 3. CÂU LỆNH MẪU KHI MỞ SESSION MỚI

```text
Đọc docs/handoff.md và tiếp tục phát triển chế độ Local-first:
1. Giữ vững server preview http://localhost:8080/portal và http://localhost:8080/master-data.
2. Tiếp tục hoàn thiện các tính năng nghiệp vụ theo yêu cầu của Sếp.
```


