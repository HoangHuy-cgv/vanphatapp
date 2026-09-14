# Handoff: Con Trỏ Vận Hành & Chuyển Giao Session

- **Mã Commit Hiện Tại**: `c14b3df` (`refactor(portal): simplify App.vue removing dead count computed and unused css`)
- **Trạng Thái CI/CD & Test**:
  - Test Suite `scripts/verify-catalog-page.mjs`: **77/77 checks PASSED 100%**.
  - Production Build: Vite build thành công sạch sẽ (972ms).
  - Live Portal: Hoạt động trực tiếp tại `http://localhost:8080/portal?view=catalog`.
- **Chân Lý Dữ Liệu Đã Hoàn Tất (SSOT)**:
  - 4 Danh mục Master Data cốt lõi: Mặt hàng (`Item` 293), Khách hàng (`Customer` 117), Nhà cung cấp (`Supplier` 14), Người dùng (`User` 11).
  - Codebase được simplify sạch sẽ, loại bỏ code chết theo chuẩn Clean-on-Done.
- **Nhiệm Vụ Trọng Tâm Session Tiếp Theo**:
  1. **Khóa 1 line & Nhất quán Tiêu đề cột**: Ép `white-space: nowrap !important;` cho toàn bộ `thead th`, chuẩn hóa phong cách viết hoa/thường nhất quán giữa các bảng.
  2. **Rà soát & Tái cấu trúc Cột Danh mục**:
     - *Khách hàng*: Bổ sung cột **Mã số thuế (MST)** và **Phương thức thanh toán** / Hạn mức nợ trực diện trên bảng.
     - *Nhà cung cấp*: Đảm bảo cột **Mã số thuế (MST)** và **Phương thức thanh toán** hiển thị rõ ràng.
     - Ẩn các cột thứ yếu sang Drawer để tối ưu không gian hiển thị bảng.
