# ADR-008: Rebuild ERPNext Native v16 Baseline & Portal Cockpit (5 Tabs Catalog + Quick CRUD + Quotation Engine)

## Status
Accepted (2026-09-16 — Sếp approved)

## Date
2026-09-16

## Context
- Ứng dụng trước đây cố gắng xây dựng toàn bộ quy trình đơn hàng, duyệt cọc, quản lý khách hàng, nhà cung cấp và người dùng trên giao diện custom Portal (`OrdersView.vue`, `components/order/*`, `api/order.py`, `customer.py`, `supplier.py`, `user.py`).
- Cách làm này dẫn đến việc trùng lặp logic nặng nề giữa Portal và ERPNext Native Desk, phát sinh rủi ro sai lệch số liệu kế toán/thuế, bảo mật và khó bảo trì khi ERPNext nâng cấp phiên bản.
- Tuy nhiên, giao diện ERPNext Desk nguyên bản lại quá nhiều thông tin, phức tạp và gây ngợp đối với nhân viên kinh doanh và vận hành hàng ngày khi chỉ cần tra cứu nhanh quy cách bao bì, thông số trục in, hoặc liên hệ đối tác.
- Do đó, cần phân định ranh giới rành mạch: Cái gì Desk làm tốt (kế toán, kho, quy trình đơn hàng, mua hàng, sản xuất) thì để Desk làm 100%; cái gì người dùng cần nhanh, gọn, trực quan (báo giá R&D, tra cứu danh mục) thì đưa lên Portal Cockpit.

## Decision
1. **Chuyển giao 100% Vòng đời Đơn hàng & Giao dịch nặng cho ERPNext Desk Native:**
   - Xóa bỏ `views/OrdersView.vue`, `components/order/*`, `ModalCreateOrder.vue` và các API backend `api/order*.py`, `api/user.py`.
   - Toàn bộ nghiệp vụ `Sales Order`, `Purchase Order`, `Work Order`, `Stock Entry`, `Payment Entry` được nhân viên thực hiện trực tiếp trên ERPNext Desk.
2. **Xây dựng Van Phat Portal thành Cockpit Siêu tốc (p95 < 200ms) với 4 Visual Baseline:**
   - **Modal Báo Giá Bước 1 (`ModalStep1Sale.vue`):** Nhập thông số bao bì nhanh (loại túi, kích thước, cấu trúc màng, vòi, số lượng, chọn KH).
   - **Drawer Báo Giá Bước 2 (`DrawerStep2Director.vue`):** Giám đốc duyệt giá với công cụ R&D tính toán theo cuộn màng (chạy 2 con khổ rộng, báo giá 2 nấc tròn cuộn vs đúng số lượng, bóc tách tiền trục riêng), tạo nháp `Quotation` native xuống ERPNext.
   - **Trang Danh mục Cockpit (`CatalogView.vue`):**
     - Gồm 5 Tab thực thể trọng yếu: `[Sản phẩm]` (TP/NGCS/TMD/BTP), `[Trục in]` (TRUC-), `[Khách hàng]` (KH-), `[Nhà cung cấp]` (NCC-), `[Nguyên vật liệu]` (NVL-).
     - Thiết kế 1 dòng Header: `[Tabs] + [Thanh tìm kiếm tức thì] + [Nút thêm mới]`.
     - Bảng tinh gọn 5–7 cột, click dòng mở Drawer xem chi tiết kỹ thuật.
     - Hỗ trợ **Quick CRUD Drawer**: Cho phép nhân viên thêm/sửa nhanh Khách hàng, Sản phẩm, Trục in trực tiếp qua Drawer tinh gọn trên Portal rồi lưu thẳng xuống Frappe DocTypes (`Customer`, `Item`).
   - **Trang Đăng nhập (`www/login.html` + `login.py`):** Đăng nhập native Frappe session.
3. **Backend API mỏng (Thin Facade):**
   - Chỉ giữ: `api/bao_gia.py`, `api/item.py`, `api/customer.py`, `api/supplier.py`, `api/_common.py`, `api/_guards.py`.

## Consequences
- Hệ thống giảm được hàng nghìn dòng code dư thừa và phức tạp trong frontend và backend.
- Đảm bảo tính toàn vẹn 100% cho số liệu kế toán và quy trình nghiệp vụ trên ERPNext Native.
- Người dùng có một Cockpit cực nhanh, thân thiện, không bị rối mắt bởi giao diện Desk ERP, đồng thời vẫn đáp ứng khả năng thêm mới / tra cứu thông tin hàng ngày.
