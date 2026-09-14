# Todo List: Tối Giản Danh Mục (Elon Musk Cockpit) & Tích Hợp Vào SPA

- [x] Task 1: Backend API Whitelisted Cho Master Items (`vanphat_portal/api/item.py` & `serve-portal.mjs`)
  - Viết `vanphat_portal/api/item.py` với `get_list()` và `get_detail(item_code)`.
  - Cập nhật `serve-portal.mjs` chuyển hướng `/master-data` sang `/portal?view=items`.
  - Kiểm tra endpoints qua curl: 100% PASS.

- [x] Task 2: Xây dựng Slide-Over Component `DrawerItemDetail.vue`
  - Giao diện drawer slide-over từ mép phải theo hệ thiết kế Unified Industrial Dark.
  - 4 Khối thông số kỹ thuật mật độ cao, chips màu cấu trúc màng, bảng BOM 2 cấp.
  - Xử lý phím tắt `Esc` và click ngoài vùng nền: Hoàn thành 100%.

- [x] Task 3: Tích Hợp Master Catalog Cockpit View Vào `App.vue`
  - Đổi nút "Danh mục" trên Sidebar thành nút chuyển view SPA: `view = 'items'`, có badge số lượng.
  - Header: Tiêu đề "Danh mục mặt hàng", ô tìm kiếm tức thì.
  - Thanh 7 Tab nghiệp vụ công nghiệp: `Tất cả`, `Thành phẩm TP`, `Phôi NGCS`, `Túi mua ngoài TMD`, `Cuộn màng BTP`, `Nguyên vật liệu NVL`, `Trục in TRUC`.
  - Bảng dữ liệu mật độ cao, font `Inter`, số `tabular-nums`, hover sáng bóng, click mở drawer.
  - Hoàn thành 100%.

- [x] Task 4: Build Vite & Visual Verification với Chrome DevTools
  - Biên dịch `npm run build` thành công 100% (892ms).
  - Khởi chạy server và chụp ảnh kiểm chứng visual proof (2 ảnh: `catalog_cockpit_view.png`, `catalog_drawer_item_detail.png`).
  - Chạy `verify-catalog-page.mjs`: 26/26 checks PASS.

- [x] Task 5: Rà Soát Kích Thước & Chuẩn Hóa Đáy Túi Từ Raw-Data
  - [x] Đối soát 100% 45 mặt hàng `TP-` từ `tien do dat hang ncc.xlsx` và `TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx`.
  - [x] Loại bỏ `gusset=45` hardcode trong `generate_master_data_csv.py`: Gán $G=0$ cho toàn bộ túi 3 biên (Enzy, SKX, TopGia).
  - [x] Tái tạo `item_master.csv` chuẩn xác 100% (293 dòng).
  - [x] Cập nhật `App.vue` và `DrawerItemDetail.vue` hiển thị kích thước túi 3 biên không có nhãn Đáy (`250 x 300 mm`).
  - [x] Build & chụp ảnh kiểm chứng Chrome DevTools visual proof cho các mặt hàng Enzy Hạt Nêm (`catalog_cockpit_enzy.png`, `catalog_drawer_enzy_detail.png`).
  - [x] Chạy test suite `verify-catalog-page.mjs`: **38/38 checks PASS 100%**.

- [x] Task 6: Chuẩn Hóa Cấu Trúc Vật Liệu & Màng Ghép SSOT
  - [x] Thống nhất 1 chuẩn duy nhất cho dấu phân cách: dùng duy nhất `/` (loại bỏ hoàn toàn `//`).
  - [x] Chuẩn hóa lớp hàn dán PE: chỉ dùng `PE sữa` hoặc `PE trong` (loại bỏ `PES`, `LLDPE`, `/PE` trần).
  - [x] Tích hợp hàm `normalize_layers` và làm sạch dữ liệu trong `generate_master_data_csv.py`.
  - [x] Thêm chuẩn SSOT vào Mục 6 của `AGENTS.md`.
  - [x] Bổ sung assertions kiểm thử trong `verify-catalog-page.mjs`: **42/42 checks PASS 100%**.
  - [x] Build Vite và kiểm chứng trên Chrome DevTools (`catalog_table_material_standard.png`, `catalog_enzy_drawer_material_standard.png`).

- [x] Task 7: Cố Định Tiêu Đề, Tabs, Search Bar & Header Cột Bảng Khi Cuộn Trang (Sticky Layout)
  - [x] Thiết lập `height: 100vh; overflow: hidden;` cho `.portal-layout` và `.main-content`.
  - [x] Cố định đỉnh buồng lái cho `.catalog-header-cockpit` và `.page-head` (`flex-shrink: 0`).
  - [x] Tách `.table-container` thành scroll container độc lập (`flex: 1; min-height: 0; overflow-y: auto;`).
  - [x] Ghim sticky cho dòng tiêu đề cột bảng `thead th` (`position: sticky; top: 0; z-index: 5; background: #1a1f27; box-shadow: 0 1px 0 #3a424e`).
  - [x] Thêm assertions kiểm thử trong `verify-catalog-page.mjs`: **46/46 checks PASS 100%**.
  - [x] Build Vite và kiểm chứng trực tiếp qua Chrome DevTools khi scroll bảng (`catalog_sticky_header_scrolled.png`).

- [x] Task 8: Tối Giản Drawer Chi Tiết Mặt Hàng Theo Triết Lý Elon Musk (Ultra-minimalist Cockpit)
  - [x] Loại bỏ triệt để các tiêu đề phân mục cồng kềnh (1., 2., 3., 4.) và nhãn giải thích dài dòng.
  - [x] Triệt tiêu 100% nhãn thừa mục Trục in: hiển thị thanh đơn duy nhất `TRUC-... • In trục ống đồng • Kho Vạn Phát` (kèm số cây, kích thước nếu có).
  - [x] Tối giản hóa Header Drawer: kết hợp Item Code badge, Procurement badge, Unit price và nút Close gọn nhẹ.
  - [x] Tối giản thông số bao bì, kích thước túi, bước dao, phụ kiện; loại bỏ hoàn toàn các đoạn văn xuôi tutorial/giải thích lý do thiếu BOM.
  - [x] Bổ sung assertions kiểm thử trong `verify-catalog-page.mjs`: **48/48 checks PASS 100%**.
  - [x] Build Vite & chụp ảnh kiểm chứng visual proof trên Chrome DevTools cho cả túi có đáy/BOM (`TP-00001` - `catalog_drawer_minimalist_888.png`) và túi 3 biên phẳng (`TP-00040` - `catalog_drawer_minimalist_enzy.png`).

- [x] Task 9: Tăng Cỡ Chữ (Font-Size Scaling) Toàn Bộ Trang Danh Mục & Drawer
  - [x] Nâng cỡ chữ các cột bảng danh mục từ `12px` lên `14px` - `15px` (`App.vue`).
  - [x] Nâng cỡ chữ các tab, badge và ô tìm kiếm lên `12.5px` - `14.5px`.
  - [x] Nâng cỡ chữ Drawer chi tiết mặt hàng (`DrawerItemDetail.vue`): Hero `20px`, tiêu chuẩn túi `15px`, badge màng `13px`, bảng BOM `14px`.
  - [x] Giữ nguyên 100% màu sắc và layout theo đúng chỉ đạo ("khoan điều chỉnh các mục khác").
  - [x] Build Vite production thành công 100% (898ms).
  - [x] Chạy bộ kiểm thử tự động `verify-catalog-page.mjs`: **48/48 checks PASS 100%**.
  - [x] Chụp ảnh kiểm chứng visual proof thực tế trên Chrome DevTools (`catalog_table_font_boosted.png`, `catalog_drawer_font_boosted.png`).

- [x] Task 10: Siết Chặt Quy Tắc Chỉ Sử Dụng Tên Ngắn / Alias Trên Toàn Bộ UI/UX (Short Alias Enforcement)
  - [x] Tầng 1 (Hiến pháp): Đưa Mandatory UI Display Rule (Short Alias Enforcement SSOT) vào Mục 3 của `AGENTS.md`.
  - [x] Tầng 2 (Data Contract): Bổ sung cột `custom_alias` vào `bom_items.csv` trong `scripts/generate_packaging_boms.py` (tất cả 251 dòng vật tư đều có alias sạch).
  - [x] Tầng 2 (Backend API): Nâng cấp API `get_detail` (`item.py` & `serve-portal.mjs`) tự động map/resolve `custom_alias` cho BOM items.
  - [x] Tầng 3 (Frontend): Bảng BOM `DrawerItemDetail.vue` hiển thị `bi.custom_alias` đơn dòng; xóa bỏ hoàn toàn dòng phụ đề `hero-sub` lặp lại tên pháp lý dài.
  - [x] Tầng 3 (Đồng bộ): Ưu tiên `custom_alias` trên Bảng Đơn Hàng (`App.vue`) và Dropdown sản phẩm (`ModalCreateOrder.vue`).
  - [x] Tầng 4 (CI Gate): Bổ sung Section 8 vào `scripts/verify-catalog-page.mjs`: quét cấm các tiền tố danh pháp dài ("Cuộn màng PET in...", "Dung môi công nghiệp..."). **54/54 checks PASS 100%**.
  - [x] Build Vite production thành công trong 940ms.
  - [x] Chụp ảnh kiểm chứng Chrome DevTools trực quan cho `BTP-00001` (`catalog_bom_alias_enforced.png`).

- [x] Task 11: Khắc Phục Lệch Cột Định Mức & Đơn Giá Bảng BOM (DrawerItemDetail.vue)
  - [x] Phát hiện Root Cause: `<style scoped>` trong `DrawerItemDetail.vue` thiếu selector `.text-right { text-align: right; }`, khiến `<td>` bị căn trái `text-align: start` trong khi `<th>` căn phải.
  - [x] Thêm định nghĩa CSS `.text-right` và `.bom-table th.text-right, .bom-table td.text-right` trong `<style scoped>`.
  - [x] Điều chỉnh tối ưu tỷ lệ độ rộng 4 cột: 22% (Mã VT) - 44% (Tên nguyên liệu alias) - 17% (Định mức) - 17% (Đơn giá).
  - [x] Bổ sung Section 9 kiểm tra tự động căn lề mép phải vào `scripts/verify-catalog-page.mjs`: **60/60 checks PASS 100%**.
  - [x] Build Vite production thành công trong 906ms.
  - [x] Chụp ảnh kiểm chứng Chrome DevTools thực tế (`catalog_bom_alignment_fixed.png`).

- [x] Task 12: Làm Sạch Danh Mục Trục In (Triệt Tiêu Lặp Lại Mã Trục Trong Tên Sản Phẩm)
  - [x] Loại bỏ hoàn toàn việc nối `({ma_truc})` vào tên sản phẩm và alias trong `scripts/generate_master_data_csv.py`.
  - [x] Giữ trọn vẹn thông tin nhận diện sản phẩm (mùi hương, màu sắc, loại dung tích) từ dữ liệu gốc.
  - [x] Tái tạo `item_master.csv`: 157 bộ trục in đều có tên ngắn gọn, chuẩn nghiệp vụ bao bì.
  - [x] Thêm Section 10 kiểm tra tự động vào `scripts/verify-catalog-page.mjs`: **64/64 checks PASS 100%**.
  - [x] Chụp ảnh kiểm chứng Chrome DevTools trực quan tab Trục in (`catalog_truc_clean_names.png`).

- [x] Task 13: Tái Cấu Trúc Tab Danh Mục Mặt Hàng (Gộp thành Tab "Sản phẩm")
  - [x] Gộp: Túi màng ghép (45), Túi NGCS (15), Túi màng đơn (12), Cuộn màng (16) vào Tab `Sản phẩm` (88).
  - [x] Buồng lái 3 Tab chính: `Sản phẩm` (88), `Nguyên vật liệu` (48), `Trục in` (157).
  - [x] Bổ sung thanh chip lọc phân loại con trong tab Sản phẩm: `Tất cả` (88), `Túi ghép` (45), `Túi NGCS` (15), `Cuộn màng` (16), `Màng đơn` (12).

- [x] Task 14: Xây Dựng Backend Whitelisted APIs Cho Khách Hàng, NCC & Người Dùng
  - [x] Viết API `customer.py`, `supplier.py`, `user.py` trong `vanphat_portal/api/`.
  - [x] Đồng bộ endpoints trong `serve-portal.mjs` (`customer.get_list`, `customer.get_detail`, `supplier.get_list`, `supplier.get_detail`, `user.get_list`).

- [x] Task 15: Xây Dựng Giao Diện Buồng Lái Cho Khách Hàng, NCC & Người Dùng
  - [x] Bổ sung 3 nút điều hướng trên Sidebar: `Khách hàng` (117), `Nhà cung cấp` (14), `Người dùng` (11).
  - [x] Xây dựng bảng danh mục Khách hàng + Slide-over Drawer xem chi tiết (`DrawerCustomerDetail.vue`).
  - [x] Xây dựng bảng danh mục Nhà cung cấp + Slide-over Drawer xem chi tiết (`DrawerSupplierDetail.vue`).
  - [x] Xây dựng bảng danh mục Người dùng + Slide-over Drawer xem chi tiết (`DrawerUserDetail.vue`).

- [x] Task 16: Kiểm Thử, Build Vite & Chụp Ảnh Kiểm Chứng Visual Proof Chrome DevTools
  - [x] Kiểm thử biên dịch Vite `npm run build` thành công 100% trong 970ms.
  - [x] Chạy test suite `verify-catalog-page.mjs`: **78/78 checks PASS 100%**.
  - [x] Chụp ảnh kiểm chứng Chrome DevTools visual proof cho:
    - Tab Sản phẩm gộp: `items_products_grouped.png`
    - Sub-filter Cuộn màng: `items_cuon_mang_subfilter.png`
    - View Khách hàng: `customers_view.png`
    - Drawer Khách hàng DS Cosmetic: `customer_drawer_ds_cosmetic.png`
    - View Nhà cung cấp: `suppliers_view.png`
    - Drawer NCC Sungdo: `supplier_drawer_sungdo.png`
    - View Người dùng & Phân quyền: `users_view.png`
    - Drawer User Doãn Thị Tường Lam: `user_drawer_lam_doan.png`

- [x] Task 17: Thống Nhất Toàn Bộ Danh Mục Vào Page "Danh Mục" (Elon Musk Cockpit)
  - [x] Xóa 3 nút riêng `Khách hàng`, `Nhà cung cấp`, `Người dùng` trên Sidebar, đổi `Mặt hàng` thành `Danh mục`.
  - [x] Hiển thị badge tổng `catalogTotalCount` (435 bản ghi) trên nút Sidebar `Danh mục`.
  - [x] Thiết kế buồng lái 6 Tabs: `Sản phẩm` (88), `Nguyên vật liệu` (48), `Trục in` (157), `Khách hàng` (117), `Nhà cung cấp` (14), `Người dùng` (11).
  - [x] Giữ thanh sub-filter chips khi active tab là `Sản phẩm`.
  - [x] Đồng bộ ô search bar tức thì và count pill thích ứng theo từng tab.
  - [x] Chuyển đổi linh hoạt giữa 4 bảng dữ liệu và kết nối đầy đủ 4 drawers (`DrawerItemDetail`, `DrawerCustomerDetail`, `DrawerSupplierDetail`, `DrawerUserDetail`).
  - [x] Cập nhật test suite `scripts/verify-catalog-page.mjs` đạt **77/77 checks PASS 100%**.
  - [x] Build Vite production và chụp ảnh kiểm chứng visual proof qua Chrome DevTools MCP:
    - Tab Sản phẩm & 5 Sub-filter chips: `unified_catalog_products.png`
    - Tab Khách hàng (117 KH): `unified_catalog_customers.png`
    - Drawer Khách hàng DS Cosmetic: `unified_catalog_customer_drawer.png`
    - Tab Nhà cung cấp (14 NCC): `unified_catalog_suppliers.png`
    - Drawer NCC Sungdo: `unified_catalog_supplier_drawer.png`
    - Tab Người dùng (11 User): `unified_catalog_users.png`
    - Drawer User Doãn Thị Tường Lam: `unified_catalog_user_drawer.png`
    - Tìm kiếm tức thì trong tab: `unified_catalog_search_enzy.png`

- [x] Task 18: Tối Ưu Buồng Lái Tab Sản Phẩm (Bỏ "Tất Cả", Bỏ Badge Count, Khóa Tab Name Trên 1 Line Duy Nhất)
  - [x] Gỡ bỏ chip filter "Tất cả (88)" tại tab Sản phẩm; 4 chips còn lại (`Túi ghép (45)`, `Túi NGCS (15)`, `Cuộn màng (16)`, `Màng đơn (12)`) chuyển sang cơ chế click-toggle thông minh (click lại để bỏ lọc về toàn bộ 88 sản phẩm).
  - [x] Gỡ bỏ badge count (`... SP`, `... KH`,...) nằm sau ô search box, tinh gọn ô search (`width: 250px`).
  - [x] Đưa sub-filter chips xuống thanh sub-toolbar chuyên biệt ngay trên bảng dữ liệu khi ở tab Sản phẩm, giúp giải phóng hoàn toàn không gian hàng 1.
  - [x] Khóa cứng `white-space: nowrap !important; flex-shrink: 0;` cho toàn bộ 6 tab và thẻ `span` bên trong, ẩn hoàn toàn thanh cuộn ngang bằng `scrollbar-width: none`.
  - [x] Đảm bảo 100% cả 6 tab name (`Sản phẩm`, `Nguyên vật liệu`, `Trục in`, `Khách hàng`, `Nhà cung cấp`, `Người dùng`) hiển thị thẳng tắp trên 1 hàng ngang duy nhất, tuyệt đối không bị ngắt dòng 2 hàng.
  - [x] Kiểm thử tự động: `verify-catalog-page.mjs` đạt **77/77 checks PASS 100%**.
  - [x] Build Vite production thành công trong 1.01s.
  - [x] Chụp ảnh kiểm chứng visual proof Chrome DevTools MCP: `unified_catalog_singleline_tabs.png` và `unified_catalog_subfilter_active.png`.
