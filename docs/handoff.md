# Handoff Session Mới — Dự Án Vạn Phát (vanphatapp)
*Thời điểm bàn giao: 2026-09-12 — Sếp duyệt mở session mới để context sạch 100%*

---

## 1. Mục Tiêu Phiên Mới
Triển khai **Quy trình 3 bước chuẩn hóa & nạp Master Data** vào ERPNext Native theo định hướng **Native Desk + Customize Form** đã chốt:
1. **Bước 1 (Schema & Form Tinh Gọn)**: Đối soát cột dữ liệu trong Excel SSOT với `Item` native; xác định trường giữ lại, Custom Fields đặc thù bao bì (độ dày, khổ, bước cắt, đáy, vòi); lập danh sách ẩn các trường rác không dùng.
2. **Bước 2 (Làm Sạch Dữ Liệu Nguồn)**: Chuẩn hóa toàn bộ mã và tên từ `data/raw-data/` theo Naming Series (`TP-`, `NVL-`, `BTP-`, `TRUC-`) và quy tắc tên `{Brand} {Dung tích} - {Mẫu in}`.
3. **Bước 3 (Nạp & Nghiệm Thu)**: Nạp danh mục nền (UOM, Item Group, Customer, Supplier) → Nạp Item Master vào Form tinh gọn → Đối soát số lượng/khách hàng.

---

## 2. Hiện Trạng Hệ Thống & Workspace Đã Dọn Sạch
- **Tên dự án**: `vanphatapp` (Đường dẫn: `~/vanphatapp` -> `/var/home/huy/workspace`).
- **Git status**: `nothing to commit, working tree clean` (commit `ae1ac95`).
- **Quy tắc làm việc**: Duy nhất [AGENTS.md](file:///var/home/huy/workspace/AGENTS.md) (Tiếng Việt; Sếp quyết business, em quyết technical; không tự ý commit/push). Đã xóa bỏ `CONSTRAINTS.md` và `floor-guard`.
- **Cấu hình cá nhân**: Đã di chuyển toàn bộ ra ngoài repo tại `~/system-config/` (`logid.cfg`, `fcitx5-lotus`, script LED).
- **Kho tham khảo đóng băng**: Toàn bộ code upstream ERPNext/Frappe 272MB và script cũ đã chuyển vào [archive/](file:///var/home/huy/workspace/archive) (Hỏi Sếp trước khi đụng vào).
- **Mã nguồn Portal & Báo giá**: Giữ nguyên vẹn tại [apps/vanphat_portal](file:///var/home/huy/workspace/apps/vanphat_portal) (Modal 1 Sale + Drawer 2 Giám đốc) để sẵn sàng nhúng vào Desk.

---

## 3. Quyết Định Kiến Trúc Đã Chốt (Hard Locks)
1. **Trục chính là ERPNext Native Desk**: Dùng Desk làm giao diện vận hành cốt lõi cho Báo giá, Đơn hàng, Mua hàng, Tồn kho, Lệnh sản xuất.
2. **Không viết portal web độc lập cho từng module**: Tránh gánh nặng bảo trì và việc tái tạo lại các tính năng native (phân quyền, audit trail, print format, filters).
3. **Tích hợp Form tính giá bao bì vào Desk**: Form 2 bước hiện tại (Modal 1 + Drawer 2) sẽ được tích hợp làm Desk Page hoặc Custom Action ngay trong Frappe Desk.
4. **Quy tắc Master Data**:
   - Brand ≠ Khách (VD: Minh Râu = brand, DS Cosmetic = khách hàng). Tên hiển thị: `{brand} {Dung tích} - {Mẫu in}`.
   - Chuỗi sản xuất: Ghép → Cắt → Đóng vòi. Cuộn ghép = BTP lưỡng dụng. Túi sau cắt = TP. Vòi/zipper/hàn miệng = Phụ kiện.
   - 4 nhánh TP: Ghép / Màng đơn / Cuộn ghép (BTP) / NGCS (13 mã legacy `TP-0001..0013`). Cấm prefix `MD`.
   - Khách & Đối tác: Topgia (KOVAA túi nước giặt + Phong Tín là khách hàng túi đựng màng bọc; Fani không tồn tại). Trang Tín là Nhà cung cấp. NCC vòi: Access; trục in: Doyung You.

---

## 4. Nguồn Dữ Liệu SSOT Bắt Buộc
Chỉ sử dụng dữ liệu trong [data/raw-data/](file:///var/home/huy/workspace/data/raw-data) (không dùng nguồn ngoài):
1. `TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx` (Giá bán, đơn cọc thực tế).
2. `MÀNG.xlsx` (Giá nhập NVL, quy cách màng).
3. `TIẾN ĐỘ SẢN XUẤT.xlsx` (Cấu trúc ghép màng, in ấn).
4. `CÔNG NỢ PHẢI TRẢ NHÀ CUNG CẤP.xlsx` (Danh sách NCC verified).
5. `cong no phai thu cua khach.xlsx` (Danh sách Khách hàng verified).

---

## 5. Tài Liệu Nghiệp Vụ Đi Kèm
- [docs/specs/erpnext-packaging-masterdata-spec.md](file:///var/home/huy/workspace/docs/specs/erpnext-packaging-masterdata-spec.md): Wording ánh xạ thuật ngữ ERPNext native và cấu trúc cây nhóm hàng.
- [docs/specs/packaging-calculation-spec.md](file:///var/home/huy/workspace/docs/specs/packaging-calculation-spec.md): Công thức tính định mức màng, hao hụt, giá trục và báo giá.

---

## 6. Câu Lệnh Mẫu Cho Sếp Khi Mở Session Mới
Sếp chỉ cần copy đoạn sau vào ô chat của session mới:

```text
Đọc docs/handoff.md và bắt đầu triển khai Bước 1: Đối soát Schema giữa data/raw-data/ (MÀNG.xlsx, TIẾN ĐỘ, Đơn cọc) với DocType Item của ERPNext native. Xác định các trường giữ lại, các Custom Field bao bì cần thêm và danh sách các trường rác cần disable trên Form Item.
```
