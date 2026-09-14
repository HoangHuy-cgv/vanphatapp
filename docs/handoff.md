# Handoff: Con Trỏ Vận Hành & Chuyển Giao Session

- **Mã Commit Hiện Tại**: `aa5342a` (`fix(catalog): reset table scroll to top when switching catalog and order tabs`)
- **Trạng Thái CI/CD & Test**:
  - Test Suite `scripts/verify-catalog-page.mjs`: **100/100 checks PASSED 100%**.
  - Production Build: Vite build thành công sạch sẽ (bundle 72.60 kB gzip).
  - Browser Verification: Đã kiểm chứng trực tiếp bằng Chrome DevTools khi cuộn và đổi tab, `scrollTop` lập tức về 0.
- **Hạng Mục Đã Hoàn Thành**:
  - Sửa bug giữ điểm cuộn (scroll sticking): Thêm `:key="activeCatalogTab"`, `tableContainerRef`, và `resetTableScroll()` trong `CatalogView.vue` và `OrdersView.vue`.
  - Đảm bảo 100% khi chuyển giữa Sản phẩm, NVL, Trục in, Khách hàng, NCC, Người dùng đều lập tức cuộn về đầu trang.
- **Nhiệm Vụ Trọng Tâm Tiếp Theo**:
  - Sẵn sàng nhận chỉ đạo tiếp theo từ Sếp.
