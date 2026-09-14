# Kế Hoạch Triển Khai: Chuẩn Hóa Nhất Quán 1 Font Chữ (Inter Native ERPNext) Trên Toàn Hệ Thống

## 1. Định Hướng Kỹ Thuật (ERPNext v16 Native SSOT)
- **Chuẩn Font**: Đồng nhất 1 font chữ duy nhất: `InterVariable` / `Inter` theo chuẩn native của ERPNext v16 (`--font-stack`).
- **Nạp Font Hai Tầng**:
  1. Tầng Webfont: Google Fonts Inter (400, 500, 600, 700, 800) với tập ký tự tiếng Việt đầy đủ trong `index.html`.
  2. Tầng Offline/Intranet: Import `@font-face` từ `frappe-ui/src/fonts/Inter/inter.css` trong `portal.css` để bảo đảm 100% offline sẵn sàng.
- **CSS Reset Thừa Kế Toàn Cục**:
  - `button, input, select, textarea { font-family: inherit; }` xóa bỏ hoàn toàn font `Arial` mặc định của trình duyệt.
- **Khử Monospace Rời Rạc & Kích Hoạt Inter `tabular-nums`**:
  - Toàn bộ class `.font-mono`, `.badge-payment-*`, các drawer chi tiết chuyển về `font-family: inherit` và kích hoạt tính năng `font-variant-numeric: tabular-nums; font-feature-settings: "tnum"`.
  - Giúp các con số (kích thước, định mức, số tiền, MST, SĐT) thẳng hàng tuyệt đối như monospace nhưng cùng 1 nét chữ typography Inter sang trọng.
- **Rà Soát Toàn Bộ Các View, Drawer & Modal**:
  - `index.html`
  - `portal.css`
  - `OrdersView.vue`
  - `DrawerItemDetail.vue`, `DrawerCustomerDetail.vue`, `DrawerSupplierDetail.vue`, `DrawerUserDetail.vue`, `DrawerOrderDetail.vue`, `DrawerStep2Director.vue`
  - `ModalCreateOrder.vue`, `ModalStep1Sale.vue`

## 2. Phân Rã Tác Vụ Triển Khai
- **Task 1**: Cập nhật `index.html` (Google Fonts Inter với preconnect) & `portal.css` (import local `inter.css`, ERPNext native `--font-sans`, CSS reset kế thừa form/button, chuẩn hóa `.font-mono` và `.badge-payment-*` sang `inherit` + `tabular-nums`).
- **Task 2**: Rà soát và loại bỏ triệt để các khai báo `font-family` monospace/Arial độc lập trong tất cả các file Vue (`OrdersView.vue`, `DrawerCustomerDetail.vue`, `DrawerSupplierDetail.vue`, `DrawerUserDetail.vue`, `DrawerItemDetail.vue`, `ModalCreateOrder.vue`).
- **Task 3**: Biên dịch `npm run build` và chạy test suite tự động `node scripts/verify-catalog-page.mjs`.
- **Task 4**: Kiểm chứng thực tế qua Chrome DevTools MCP trên live browser (đo đạc `fontFamily` đạt 100% Inter trên mọi trang/drawer, chụp ảnh màn hình lưu bằng chứng).
- **Task 5**: Cập nhật tài liệu, con trỏ vận hành `docs/handoff.md` và commit Git nguyên tử.
