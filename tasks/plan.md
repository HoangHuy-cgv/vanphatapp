# Kế Hoạch Triển Khai: Tinh Chỉnh Bảng Danh Mục (Single-Line Headers, Cột KH/NCC & User SĐT)

## 1. Định Hướng Kỹ Thuật (Elon Musk & Cockpit Philosophy)
1. **Khóa cứng tiêu đề 1 dòng**: Thiết lập `white-space: nowrap !important; overflow: hidden; text-overflow: ellipsis; user-select: none;` cho `.data-table th` trong `portal.css`.
2. **Đồng nhất phong cách tiêu đề**: Thống nhất template HTML sang Title Case chuẩn mực, CSS tự động viết hoa với font chữ 13.5px, letter-spacing 0.04em, loại bỏ toàn bộ chú thích thô trong ngoặc như `(ALIAS)`.
3. **Tái cấu trúc cột Khách hàng & Nhà cung cấp**:
   - Khách hàng: `Tên gọi tắt (kèm mã mờ)` | `Tên pháp nhân` | `Mã số thuế` | `Thanh toán` | `Hạn mức nợ`.
   - Nhà cung cấp: `Tên gọi tắt (kèm mã mờ)` | `Tên pháp nhân` | `Mã số thuế` | `Thanh toán` | `Nhóm cung ứng`.
   - Bỏ cột mã riêng biệt để tối ưu diện tích cho MST và Phương thức thanh toán.
4. **Tinh chỉnh bảng Người dùng (User)**:
   - Cột 1: `SĐT đăng nhập` (`mobile_no` dạng số mono rõ nét, kèm email mờ). Hỗ trợ tìm kiếm theo SĐT trong `filteredUsers`.
   - Cột 2: `Họ và tên` (`full_name`).
   - Cột 3: `Phòng ban` (`department`).
   - Cột 4: `Chức vụ & Vai trò` (`designation` kèm badge `role_profile_name` tinh gọn, khử hoàn toàn trùng lặp 2 cột).
   - Cột 5: `Trạng thái` (Badge hoạt động `● Hoạt động`).

## 2. Phân Rã Tác Vụ Triển Khai
- **Task 1**: Cập nhật CSS bảng trong `portal.css` (khóa cứng `th` 1 dòng không wrap, styling badge điều khoản thanh toán & trạng thái).
- **Task 2**: Đồng nhất tiêu đề cột & tái cấu trúc cột Khách hàng, Nhà cung cấp và Người dùng trong `CatalogView.vue`.
- **Task 3**: Chạy test tự động `node scripts/verify-catalog-page.mjs` & build Vite production.
- **Task 4**: Kiểm chứng giao diện thực tế qua Chrome DevTools MCP (kiểm tra tab KH, NCC, User).
