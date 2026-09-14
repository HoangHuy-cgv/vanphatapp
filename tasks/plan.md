# Implementation Plan: Thống Nhất Toàn Bộ Master Data Vào Trang "Danh Mục" (Elon Musk Cockpit)

## Mục Tiêu
1. Gỡ bỏ 3 nút riêng lẻ `Khách hàng`, `Nhà cung cấp`, `Người dùng` trên Sidebar. Sidebar chỉ giữ 1 nút duy nhất **`Danh mục`** (`view = 'catalog'` hoặc `view = 'items'`) với tổng badge 435 bản ghi.
2. Tái cấu trúc trang Mặt hàng thành trang **`Danh mục`** chứa trọn vẹn 6 phân hệ Master Data:
   - **`Sản phẩm`** (88) [kèm sub-filter chips: Tất cả (88), Túi ghép (45), Túi NGCS (15), Cuộn màng (16), Màng đơn (12)]
   - **`Nguyên vật liệu`** (48)
   - **`Trục in`** (157)
   - **`Khách hàng`** (117)
   - **`Nhà cung cấp`** (14)
   - **`Người dùng`** (11)
3. Tìm kiếm tức thì thích ứng theo từng tab trên cùng dòng buồng lái (Elon Musk single-row cockpit).
4. Tích hợp trọn vẹn 4 slide-over drawers: `DrawerItemDetail`, `DrawerCustomerDetail`, `DrawerSupplierDetail`, `DrawerUserDetail`.
5. Đảm bảo toàn bộ 78+ automated tests pass và kiểm chứng trực quan bằng Chrome DevTools MCP.

## Task Breakdown
- [ ] Task 1: Tái Cấu Trúc Sidebar & Navigation State trong `App.vue` (Nút "Danh mục", loại bỏ 3 nút thừa)
- [ ] Task 2: Xây Dựng Thanh 6 Tab Buồng Lái & Ô Tìm Kiếm Thích Ứng Trong View `Danh mục`
- [ ] Task 3: Kết Nối Bảng Dữ Liệu Tương Ứng & 4 Slide-Over Drawers Vào View `Danh mục`
- [ ] Task 4: Cập Nhật & Mở Rộng Bộ Kiểm Thử Tự Động `scripts/verify-catalog-page.mjs`
- [ ] Task 5: Build Vite Production & Chụp Ảnh Kiểm Chứng Trực Quan Bằng Chrome DevTools MCP
