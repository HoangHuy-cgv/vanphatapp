# Kế Hoạch Triển Khai: Tối Giản, Đúng & Đủ (Minimalist Architecture)

## 1. Định Hướng Kỹ Thuật (Elon Musk & LoB Philosophy)
Triệt tiêu over-engineering, chỉ giữ lại những gì thực sự mang lại giá trị vận hành và hiệu năng:
1. **Single-Bundle (Không tách route)**: Giữ nguyên 1 bundle ~71 kB gzip cho toàn bộ 3 views. Đảm bảo chuyển tab 0ms, không phụ thuộc mạng, không lỗi chunk load.
2. **Teleport ra `<body>`**: Bọc `<Teleport to="body">` cho 6 Drawers và 2 Modals để cô lập CSS stacking context, chống lỗi z-index và overflow clipping.
3. **Nâng cấp `api()` trong `useSession.js`**: Một SSOT duy nhất cho Frappe network calls (tự động gắn CSRF token, auto prefix method, bóc tách message), không đẻ thêm file `useApiClient.js`. Thay thế toàn bộ `fetch` thô.
4. **Dọn dẹp CSS dư thừa trong `CatalogView.vue`**: Chuyển 247 dòng CSS trùng lặp vào `portal.css`, giữ nguyên cấu trúc 4 bảng để đảm bảo Locality of Behavior và không gây prop drilling.

## 2. Phân Rã Tác Vụ Triển Khai
- **Task 1**: Nâng cấp `api()` trong `src/composables/useSession.js` & thay thế toàn bộ `fetch` thô trong `CatalogView.vue` và `OrdersView.vue`.
- **Task 2**: Bọc `<Teleport to="body">` cho toàn bộ 6 Drawers và 2 Modals (`DrawerItemDetail`, `DrawerCustomerDetail`, `DrawerSupplierDetail`, `DrawerUserDetail`, `DrawerOrderDetail`, `DrawerStep2Director`, `ModalStep1Sale`, `ModalCreateOrder`).
- **Task 3**: Trích xuất CSS trùng lặp từ `CatalogView.vue` sang `src/assets/portal.css`.
- **Task 4**: Chạy kiểm thử tự động `scripts/verify-catalog-page.mjs` (yêu cầu 77/77 PASS), build Vite production và kiểm chứng trực quan bằng Chrome DevTools MCP.
