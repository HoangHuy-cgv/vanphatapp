# Handoff Chuyển Giao Session Mới — ERP & Portal Vạn Phát (vanphatapp)
*Thời điểm cập nhật: 2026-09-13 | Trọng tâm: Chuẩn hoá Danh mục Master Data & Raw-Data theo Wording ERPNext Native*

---

## 1. TỔNG KẾT HIỆN TRẠNG ĐÃ HOÀN THÀNH (SESSION NÀY)

### 1.1. Hoàn Thiện Toàn Diện Trang Đơn Hàng (`/orders`) — 100% Sạch & Chuẩn
1. **Chia 3 Tab Nghiệp Vụ Riêng Biệt (Phương án 2 SSOT)**:
   - Tab 1: **`Xưởng sản xuất`** (Theo dõi hàng tự gia công Ghép $\rightarrow$ Cắt $\rightarrow$ Vòi, cột `VẬT TƯ & MÁY`).
   - Tab 2: **`Túi NGCS`** (Theo dõi phôi túi nước giặt in sẵn & tiến độ NCC in lụa, cột `IN LỤA NCC`).
   - Tab 3: **`Mua ngoài trọn gói`** (Theo dõi túi màng đơn HD/PE/PP và túi mua đứt NCC, cột `HẠN GIAO NCC`).
   - Tích hợp **Smart SLA Alert**: Tự động tính hạn giao NCC (`Còn x ngày`, `Hôm nay giao`, `Trễ x ngày` đỏ rực báo động giục hàng).
   - Triệt tiêu 100% mã code rác (`DH-`, `TP-`, `KH-`) trên tiêu đề và dữ liệu hiển thị table.
2. **Modal Tạo Đơn Hàng Mới (`ModalCreateOrder.vue`) — 1 Bước Duy Nhất (Single-Step Cockpit)**:
   - Tách rời hoàn toàn khỏi form Báo giá. Header trang Đơn hàng đổi thành nút **`+ Tạo đơn hàng`**.
   - Thao tác trực tiếp trên **Sản phẩm ĐÃ CÓ MÃ trong danh mục**: Chọn mã hàng là tự bung kích thước, cấu trúc màng, đơn giá chuẩn, người dùng **không phải gõ lại**.
   - **Tự động thích ứng thông minh theo 2 quy trình sản xuất**:
     - **Quy trình 1: MTO Sản phẩm độc quyền theo khách (`Túi màng ghép` / `Cuộn màng ghép`)**: Chọn khách $\rightarrow$ Lọc sản phẩm độc quyền của khách (VD: `Minh Râu 3.2Kg` của `DS 888`) $\rightarrow$ Bung bảng nhập các **Mẫu in / Màu sắc** (`Màu Hồng 10.000`, `Màu Tím 10.000`), nút `+ Thêm mẫu in`, checkbox trục in.
     - **Quy trình 2: MTS Phôi dùng chung (`Túi NGCS` / `Túi màng đơn`)**: Chọn khách $\rightarrow$ Nhập thương hiệu in lụa của khách (VD: `FUSIMI - Nước giặt cao cấp`) $\rightarrow$ Bảng chọn **Nhiều mã phôi khác nhau** (`NGCS Đỏ lớn 5.000`, `NGCS Đen lớn 5.000`), nút `+ Thêm loại phôi`.
   - Tự động tính tiền hàng, thuế VAT 8%, tiền trục, tổng thanh toán và tiền cọc yêu cầu 50%.
3. **Drawer Chi Tiết Đơn Hàng Mới (`DrawerOrderDetail.vue`)**:
   - **Hỗ trợ Multi-SKU / Multi-Variants**: Liệt kê rõ từng dòng mẫu in/hương vị kèm thumbnail ảnh maquette riêng (`44px`, click bung Lightbox phóng to), số lượng, đơn giá, thành tiền.
   - **Ẩn triệt để 100% chất liệu không dùng**: Chỉ hiển thị các chip màng thực tế của sản phẩm (VD chỉ dùng `PET`, `PA`, `PE sữa` thì chỉ render đúng 3 chip này).
   - **Tài chính tối giản, font to rõ**: Tiền hàng, VAT 8%, Tiền trục, **TỔNG THANH TOÁN** (In đậm `18px`), Đã cọc, Còn phải thu.
   - **Tiến độ vận hành không nhãn rác**: Triệt tiêu chữ "Vật tư màng", "Công đoạn máy", "Sản lượng", hiển thị trực tiếp value kèm thanh tiến độ mỏng.
   - **Font chữ chuẩn**: Chuẩn hóa toàn bộ lên `14px - 16px`, tương phản cao, số liệu `tabular-nums`.
   - **Footer State Machine**: HOLD $\rightarrow$ Ô cọc nhanh tại chỗ; Đang chạy $\rightarrow$ Báo cáo xưởng; Sẵn sàng giao $\rightarrow$ `+ XUẤT GIAO HÀNG` full-width sáng xanh.

### 1.2. Kiểm Thử & Quản Lý Mã Nguồn
- **Vite Build**: Pass 100% trong ~1.05s, không lỗi cảnh báo.
- **Headless Chrome Visual Proof**: Đã chụp và đối soát trực quan 5 màn hình:
  - `modal_create_order_mto.png` (Modal MTO DS888)
  - `modal_create_order_ngcs.png` (Modal MTS FUSIMI)
  - `drawer_baba_variants.png` (BABA 2 Mẫu in + Trục)
  - `drawer_minhrau_variants.png` (Minh Râu 2 Màu)
  - `drawer_fusimi_ngcs.png` (NGCS 2 Mã phôi)
### 1.3. Tối Giản Danh Mục Mặt Hàng Master Data (Elon Musk Cockpit), Rà Soát Raw-Data & Triệt Tiêu Hardcode (Hoàn tất 100%)
1. **Triệt tiêu 100% trang HTML tĩnh độc lập (`master-data.html`)**:
   - Chuyển đổi nút "Danh mục" trên Sidebar thành nút chuyển view SPA native (`view = 'items'`) có badge hiển thị số lượng mặt hàng (`293`).
   - Tự động chuyển hướng (HTTP 302 Redirect) các truy cập `/master-data` về `/portal?view=items`.
2. **Thiết kế buồng lái công nghiệp mật độ cao theo triết lý Elon Musk**:
   - Xóa bỏ tiêu đề "Danh mục mặt hàng" và các card thống kê chiếm diện tích; đưa toàn bộ Tabs và Ô Search lên **cùng 1 line duy nhất**.
   - Bỏ tab "Tất cả" và bỏ hoàn toàn bộ lọc cung ứng thừa ("Tất cả cung ứng", "Xưởng SX", "Mua ngoài").
   - **6 Tab nghiệp vụ chuẩn xác** gắn badge số lượng: `Túi màng ghép` (45), `Túi NGCS` (15), `Túi màng đơn` (12), `Cuộn Màng` (16), `Nguyên vật liệu` (48), `Trục in` (157).
   - **Instant Search Reactive cùng line**: Ô tìm kiếm đặt cạnh các Tab, phản hồi tức thì theo mã, tên, khách hàng, cấu trúc màng (`PET/PA/PE`).
3. **Chuẩn hóa Bảng Dữ Liệu Tinh Gọn (6 Cột — Ẩn Khách Hàng, Đáy Riêng Biệt, R x D x Dày)**:
   - **Ẩn cột Khách hàng**: Giữ lại trọn vẹn thông tin khách hàng trong Drawer khi click xem chi tiết; trên bảng ẩn cột này để tăng mật độ thông tin kỹ thuật.
   - **Chỉ sử dụng tên ngắn**: Render duy nhất `it.custom_alias || it.item_name`, triệt tiêu dòng phụ đề tên pháp lý dài dòng.
   - **Cột Chất liệu đơn dòng**: Chỉ hiển thị cấu trúc màng (`PET//PA/PE sữa`, `PET/AL/PE`...), không để độ dày dòng dưới làm dày bảng.
   - **Cột Kích thước thống nhất (Rộng x Dài x Dày)**: Ghi rõ quy cách hình học gồm cả độ dày màng, vd: `280 x 340 mm x 230 mic`, `250 x 300 mm x 150 mic`.
   - **Tách Cột Đáy riêng biệt**: Có nếp gấp đáy thì ghi kích thước đáy màu hổ phách đậm (vd: `45 mm`, `50 mm`), không có đáy (túi 3 biên, màng cuộn) thì để null (`—`).
   - Bảng 6 cột chuẩn: `Mã sản phẩm` (14%), `Tên sản phẩm` (27%), `Chất liệu` (21%), `Kích thước (R x D x Dày)` (20%), `Đáy` (11%), `ĐVT` (7%).
4. **Rà soát Raw-Data gốc và Giải mã thông số "Đáy 45mm"**:
   - Đối soát file gốc `data/raw-data/tien do dat hang ncc.xlsx` (Sheet `CHỜ SẢN XUẤT`, dòng 16-19) bằng `fastexcel`:
     - Các mặt hàng Enzy Hạt Nêm (900g, 450g, 220g) và Enzy Rắc Cơm là **Túi phẳng 3 biên** $\rightarrow$ Không có đáy (`gusset = 0`).
     - SKX Đậu Nành (`TP-00039`) và TopGia MBTP (`TP-00019`) $\rightarrow$ Phẳng, không có đáy (`gusset = 0`).
     - Chỉ có dòng Doypack (như 888 Nước giặt, túi vòi chiết) mới có nếp gấp đáy đứng (`gusset = 45mm`).
   - Đã cập nhật lại `item_master.csv` 293 dòng chuẩn xác 100%.
5. **Simplify Code trong `scripts/generate_master_data_csv.py`**:
   - Định nghĩa bộ tuple tham số tường minh 8 phần tử `(name, customer, structure, pouch_type, w, l, gusset, thick, film_w)` cho từng sản phẩm.
   - Triệt tiêu 100% việc gán mặc định hay hardcode `gusset=45` và `film_w=w*2+100`.
6. **Slide-Over Drawer Chi Tiết Mặt Hàng (`DrawerItemDetail.vue`)**:
   - Mở mượt mà khi click vào bất kỳ dòng nào trong bảng, hỗ trợ phím `Esc` và click backdrop.
   - Tự động hiển thị nhãn `Kích thước túi (W x L)` khi không có đáy và `Kích thước túi (W x L + Đáy)` khi có đáy.
   - **4 Khối thông số kỹ thuật mật độ cao**: Định danh & Cung ứng ERPNext, Cấu trúc màng & Quy cách bao bì, Trục in ống đồng, Bảng định mức BOM 2 cấp.
7. **Chuẩn hóa Vật liệu & Cấu trúc màng ghép SSOT (Thống nhất dấu "/" và phân loại "PE sữa" / "PE trong")**:
   - **Thống nhất 1 chuẩn duy nhất cho dấu phân cách**: Chỉ dùng duy nhất dấu gạch chéo đơn `/` (chuẩn quốc tế ISO/ASTM và ERPNext). Tuyệt đối cấm dùng `//`. Bóc tách các lớp màng trong Vue component `DrawerItemDetail.vue` (`split('/')`) đạt độ tin cậy 100%, không bị badge rỗng.
   - **Chuẩn hóa lớp hàn dán PE**: Chỉ được dùng `PE sữa` (Opaque White PE, tỷ trọng 0.930 g/cm³, cản sáng cho túi nước giặt, hóa mỹ phẩm) hoặc `PE trong` (Clear PE, tỷ trọng 0.925 g/cm³, độ trong suốt cao cho thực phẩm, hạt nêm, đậu nành). Tuyệt đối cấm dùng các ký hiệu viết tắt tuỳ tiện như `PES`, `LLDPE` hay để đuôi `/PE` trơ trọi.
   - **Đưa vào hiến pháp kỹ thuật AGENTS.md (Mục 6)**: Ràng buộc vĩnh viễn mọi Agent tuân thủ chuẩn cấu trúc này trong toàn bộ catalog, BOM và thuật toán báo giá.
   - **Tự động hóa trong `scripts/generate_master_data_csv.py`**: Tích hợp hàm chuẩn hóa tự động `normalize_layers` và làm sạch toàn bộ tuple dữ liệu khai báo gốc (`custom_pouches`, `ngcs_sizes`, `btp_items`).
8. **Cố Định Tiêu Đề, Tabs, Search Bar & Header Cột Bảng Khi Cuộn Trang (Sticky Cockpit Layout)**:
   - **Fixed Viewport 100vh**: Thiết lập `height: 100vh; overflow: hidden;` cho `.portal-layout` và `.main-content`. Toàn bộ ứng dụng hoạt động như một desktop cockpit thực thụ, triệt tiêu 100% hiện tượng trôi header khi cuộn trang.
   - **Ghim cố định đỉnh buồng lái**: Thanh điều hướng 6 Tab (`Túi màng ghép`, `Túi NGCS`, `Cuộn Màng`, `Trục in`...) và ô tìm kiếm tức thì (`.catalog-header-cockpit`) có `flex-shrink: 0`, luôn hiển thị ở đỉnh trang.
   - **Ghim sticky header cột bảng (`<thead> <th>`)**: Bảng nằm trong container cuộn riêng (`.table-container { overflow-y: auto }`), dòng tiêu đề cột (`MÃ SẢN PHẨM`, `TÊN SẢN PHẨM`, `CHẤT LIỆU`, `KÍCH THƯỚC`, `ĐÁY`, `ĐVT`) được ghim `position: sticky; top: 0` với nền `#1a1f27` và đường viền sắc nét.
   - **Kiểm thử & Bằng chứng trực quan**: Test suite `verify-catalog-page.mjs` đạt **46/46 checks PASS 100%**. Visual proof thực tế trên Chrome DevTools: `catalog_sticky_header_scrolled.png`.
9. **Tối Giản Drawer Chi Tiết Mặt Hàng Theo Triết Lý Elon Musk (Ultra-minimalist Cockpit)**:
   - **Triệt tiêu 100% tiêu đề phân mục và nhãn rác**: Xóa sạch các header số La Mã/thập phân ("1. THÔNG TIN QUY CÁCH BAO BÌ", "2. CƠ CẤU & ĐỘ DÀY MÀNG", "3. TRỤC IN ỐNG ĐỒNG", "4. ĐỊNH MỨC VẬT TƯ SẢN XUẤT (BOM)").
   - **Thanh công cụ Trục in siêu tinh gọn**: Không còn các nhãn "Mã bộ trục:", "Số cây:", "Vị trí kho:". Toàn bộ thông tin được tinh giản thành một thanh duy nhất: `TRUC-G4006940 • In trục ống đồng • Kho Vạn Phát` (hoặc kèm số cây, kích thước nếu có).
   - **Header Drawer mật độ cao**: Đặt trên 1 dòng duy nhất gồm mã hàng `TP-00001` (font-mono sky-blue), badge `Xưởng SX`/`Mua ngoài`, đơn giá niêm yết `5.166 đ / Túi` và nút đóng `✕`.
   - **Hero Block & Packaging Specs tối giản**: Tên ngắn in đậm to rõ, khách hàng kèm mã, mảng badge màng ghép và kích thước hình học `280 x 340 mm (Đáy 45 mm)`, bước dao, phụ kiện; loại bỏ 100% các đoạn văn xuôi giải thích tại sao không có BOM hay hướng dẫn cho người dùng.
   - **Kiểm thử & Visual Proof**: `verify-catalog-page.mjs` đạt **48/48 checks PASS 100%**. Bằng chứng trực quan Chrome DevTools: `catalog_drawer_minimalist_888.png` (Túi 888 Doypack có đáy + BOM) và `catalog_drawer_minimalist_enzy.png` (Túi Enzy 3 biên phẳng không đáy).
10. **Tăng Cỡ Chữ (Font-Size Scaling) Toàn Bộ Trang Danh Mục & Drawer**:
   - Nâng cỡ chữ các cột bảng danh mục từ `12px` lên `14px` - `15px` (`App.vue`).
   - Nâng cỡ chữ các tab, badge và ô tìm kiếm lên `12.5px` - `14.5px`.
    - Nâng cỡ chữ các cột bảng danh mục từ `12px` lên `14px` - `15px` (`App.vue`).
    - Nâng cỡ chữ các tab, badge và ô tìm kiếm lên `12.5px` - `14.5px`.
    - Nâng cỡ chữ Drawer chi tiết mặt hàng (`DrawerItemDetail.vue`): Hero `20px`, tiêu chuẩn túi `15px`, badge màng `13px`, bảng BOM `14px`.
    - Test suite `verify-catalog-page.mjs` đạt **48/48 checks PASS 100%**. Bằng chứng trực quan Chrome DevTools: `catalog_table_font_boosted.png` và `catalog_drawer_font_boosted.png`.
11. **Siết Chặt Quy Tắc Chỉ Sử Dụng Tên Ngắn / Alias Trên Toàn Bộ UI/UX (Short Alias Enforcement)**:
    - **Tầng 1 (Hiến pháp kỹ thuật)**: Bổ sung điều khoản bất khả xâm phạm *Mandatory UI Display Rule (Short Alias Enforcement SSOT)* vào Mục 3 của `AGENTS.md`. Cấm tiệt việc render tĩnh `item_name` dài dòng, chỉ được dùng `custom_alias` ngắn gọn.
    - **Tầng 2 (Data Contract & Backend)**: Bổ sung cột `custom_alias` vào `bom_items.csv` trong `scripts/generate_packaging_boms.py` (251 dòng vật tư đều có alias). Cập nhật API `item.py` và `serve-portal.mjs` tự động map/resolve `custom_alias` cho BOM items.
    - **Tầng 3 (Frontend)**: Tối giản bảng BOM `DrawerItemDetail.vue` hiển thị `bi.custom_alias` đơn dòng (VD: `PET in 888 Phấn Thơm`, `PE sữa K750 190mic`, `Keo D-9700`, `Dung Môi EA`); xóa bỏ hoàn toàn dòng phụ đề `hero-sub` lặp lại tên pháp lý dài. Đồng bộ `custom_alias` trên Bảng Đơn hàng `App.vue` và Dropdown chọn phôi `ModalCreateOrder.vue`.
    - **Tầng 4 (CI Gate Assertion)**: Bổ sung Section 8 vào `scripts/verify-catalog-page.mjs` quét cấm tiền tố danh pháp dài. Test suite nâng lên **54/54 checks PASS 100%**. Bằng chứng trực quan: `catalog_bom_alias_enforced.png`.
12. **Khắc Phục Lệch Cột Định Mức & Đơn Giá Bảng BOM (`DrawerItemDetail.vue`)**:
    - **Nguyên nhân gốc**: `<style scoped>` trong `DrawerItemDetail.vue` thiếu selector `.text-right { text-align: right; }`, khiến dữ liệu `<td>` bị trình duyệt áp dụng mặc định `text-align: start` (căn trái) trong khi `<th>` căn phải.
    - **Xử lý**: Bổ sung selector `.text-right` và `.bom-table th.text-right, .bom-table td.text-right` vào scoped CSS; cân chỉnh tỷ lệ độ rộng 4 cột (22% - 44% - 17% - 17%) giúp số liệu và đơn vị `tabular-nums` thẳng tắp mép phải. Bằng chứng trực quan: `catalog_bom_alignment_fixed.png`.
13. **Làm Sạch Danh Mục Trục In (Triệt Tiêu 100% Lặp Lại Mã Trục Trong Tên Sản Phẩm)**:
    - **Vấn đề**: Cột 1 ghi `TRUC-G4010806`, cột 2 lại lặp lại `Trục Sachpoong 3.2Kg (G4010806)`, gây dư thừa thị giác và vi phạm triết lý tối giản buồng lái.
    - **Xử lý**: Nâng cấp hàm `clean_cylinder_title` trong `scripts/generate_master_data_csv.py` loại bỏ hoàn toàn việc nối `({ma_truc})` vào tên/alias; giữ trọn vẹn thông tin nhận diện sản phẩm gốc (Hương Phấn Thơm Hồng, Huyền Bí Tím, Đam Mê Đỏ, Lau Sàn, Rửa Chén, Dung tích, Màu sắc). Tái tạo `item_master.csv` sạch 100%. Bằng chứng trực quan: `catalog_truc_clean_names.png`.
    - **CI Gate**: Nâng tổng số kiểm thử tự động trong `scripts/verify-catalog-page.mjs` lên **64/64 checks PASS 100%**.

14. **Gộp Tab Mặt Hàng Thành "Sản Phẩm" (88 Mã) & Tích Hợp Sub-Filters (Hoàn Tất 100%)**:
    - Gộp: Túi màng ghép (45), Túi NGCS (15), Cuộn màng (16), Túi màng đơn (12) thành Tab `Sản phẩm` (88).
    - Thanh điều hướng mặt hàng chỉ còn 3 Tab buồng lái chính: `Sản phẩm (88)` | `Nguyên vật liệu (48)` | `Trục in (157)`.
    - Thanh chip lọc con phản hồi tức thì: `Tất cả (88)`, `Túi ghép (45)`, `Túi NGCS (15)`, `Cuộn màng (16)`, `Màng đơn (12)`.
15. **Bổ Sung Toàn Diện 3 Danh Mục Master Data Lên Sidebar & Buồng Lái Cockpit**:
    - **Danh mục Khách hàng (`Customer` - 117 khách)**: View bảng 6 cột kèm hạn mức công nợ VND căn phải; Slide-over Drawer `DrawerCustomerDetail.vue` hiển thị MST, điều khoản cọc/gối đầu, địa chỉ, người liên hệ và danh sách mặt hàng độc quyền.
    - **Danh mục Nhà cung cấp (`Supplier` - 14 NCC)**: Giữ nguyên 14 NCC cốt lõi thực tế; View bảng kèm nhóm cung ứng và MST; Slide-over Drawer `DrawerSupplierDetail.vue`.
    - **Danh mục Người dùng & Phân quyền (`User` - 11 nhân sự)**: View bảng nhân sự nội bộ; Slide-over Drawer `DrawerUserDetail.vue` hiển thị bộ vai trò ERPNext Native và aliases.
16. **Hệ Thống Whitelisted REST APIs & CI Gate**:
    - Tạo các controller chuẩn Frappe v16: `customer.py`, `supplier.py`, `user.py`.
    - Nâng cấp test suite tự động `scripts/verify-catalog-page.mjs`: **78/78 checks PASS 100%**.
    - Chụp 8 ảnh kiểm chứng visual proof Chrome DevTools: `items_products_grouped.png`, `items_cuon_mang_subfilter.png`, `customers_view.png`, `customer_drawer_ds_cosmetic.png`, `suppliers_view.png`, `supplier_drawer_sungdo.png`, `users_view.png`, `user_drawer_lam_doan.png`.

17. **Thống Nhất Toàn Bộ Master Data Vào Trang "Danh Mục" Duy Nhất (Single Catalog Cockpit)**:
    - **Tối giản Sidebar triệt để**: Gỡ bỏ 3 nút riêng lẻ `Khách hàng`, `Nhà cung cấp`, `Người dùng`. Sidebar chỉ còn **1 nút duy nhất mang tên `Danh mục`** với tổng badge 435 bản ghi.
    - **Hệ thống 6 Tab buồng lái cấp 1 trên đỉnh trang `Danh mục`**:
      1. `Sản phẩm` (88) — Gồm 5 sub-filter chips: Tất cả (88), Túi ghép (45), Túi NGCS (15), Cuộn màng (16), Màng đơn (12).
      2. `Nguyên vật liệu` (48) — Màng thô NVL, keo ghép, hóa chất, phụ kiện.
      3. `Trục in` (157) — Toàn bộ bộ trục in ống đồng với tên chuẩn hóa không lặp mã.
      4. `Khách hàng` (117) — Khách hàng & chính sách công nợ gối đầu / cọc 50%.
      5. `Nhà cung cấp` (14) — 14 NCC cung ứng hạt nhựa, màng, keo, gia công.
      6. `Người dùng` (11) — 11 tài khoản nhân sự với vai trò ERPNext Native.
    - **Tìm kiếm tức thì thích ứng (Adaptive Search)**: Đặt cùng hàng bên phải thanh tabs, tự động đổi placeholder theo tab đang chọn.
    - **Tối ưu buồng lái tab Sản phẩm & Khóa Tab Name 1 Line (Elon Musk Minimalist)**:
      - Bỏ chip filter "Tất cả (88)", 4 chips nghiệp vụ (`Túi ghép (45)`, `Túi NGCS (15)`, `Cuộn màng (16)`, `Màng đơn (12)`) chuyển sang click-toggle (bỏ chọn để xem tất cả).
      - Bỏ badge count sau ô search, thu gọn ô search xuống 250px.
      - Đưa sub-filter chips xuống thanh sub-toolbar chuyên biệt ngay trên bảng sản phẩm, giải phóng hoàn toàn không gian hàng điều hướng.
      - Khóa cứng `white-space: nowrap !important; flex-shrink: 0;` cho tất cả 6 tab và thẻ `span`, ẩn scrollbar ngang bằng `scrollbar-width: none`. Đảm bảo 100% các tab name (`Sản phẩm`, `Nguyên vật liệu`, `Trục in`, `Khách hàng`, `Nhà cung cấp`, `Người dùng`) nằm thẳng hàng trên 1 dòng duy nhất, không bao giờ bị ngắt chữ 2 hàng.
    - **Slide-Over Drawers liên kết đầy đủ**: Chuyển đổi và mở mượt mà cả 4 slide-over drawers (`DrawerItemDetail`, `DrawerCustomerDetail`, `DrawerSupplierDetail`, `DrawerUserDetail`).
    - **CI Gate**: Toàn bộ **77/77 checks PASSED 100%** trong `scripts/verify-catalog-page.mjs`.
    - **Visual Proof**: Chụp và kiểm chứng qua Chrome DevTools MCP: `unified_catalog_singleline_tabs.png`, `unified_catalog_subfilter_active.png`, `unified_catalog_products.png`, `unified_catalog_customers.png`, `unified_catalog_customer_drawer.png`, `unified_catalog_suppliers.png`, `unified_catalog_supplier_drawer.png`, `unified_catalog_users.png`, `unified_catalog_user_drawer.png`, `unified_catalog_search_enzy.png`.

---

## 2. TRỌNG TÂM CHO SESSION TIẾP THEO: CHUẨN HOÁ RAW-DATA GIAO DỊCH (TRANSACTION DATA)

Sau khi đã hoàn thiện 100% 4 danh mục Master Data trụ cột (`Item`, `Customer`, `Supplier`, `User`), trọng tâm tiếp theo là chuẩn hóa các **CHỨNG TỪ GIAO DỊCH THỰC TẾ** từ các file Excel gốc sang các dataset chuẩn ERPNext Native v16:

1. **Đơn Bán Hàng (`Sales Order` & `Sales Order Item`)**:
   - Trích xuất từ `TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx` thành `sales_order_master.csv` và `sales_order_items.csv`.
   - Chuẩn hóa: `name` (SO-...), `customer`, `transaction_date`, `delivery_date`, `advance_paid`, `net_total`, `grand_total`, `status`, chi tiết từng dòng `item_code`, `qty`, `rate`, `amount`.
2. **Đơn Mua Hàng Nhà Cung Cấp (`Purchase Order` & `Purchase Order Item`)**:
   - Trích xuất từ `tien do dat hang ncc.xlsx` và `TIEN DO MUA HÀNG NCC T8.xlsx` thành `purchase_order_master.csv` và `purchase_order_items.csv`.
   - Chuẩn hóa: Đơn in gia công (Tuệ Nhi, Kiến Tâm, Trang Tín), Keo (Sungdo), Dung môi (Thịnh Đạt), Vòi (Access), In lụa (Thanh Tùng).
3. **Lệnh Sản Xuất Xưởng (`Work Order`)**:
   - Trích xuất từ `TIẾN ĐỘ SẢN XUẤT.xlsx` (24 đợt chạy máy xưởng: 888, Phấn Thơm, Softy, Minh Râu...) thành `work_order_master.csv`.
4. **Bút Toán Thu Chi & Cọc (`Payment Entry`)**:
   - Trích xuất từ `THU CHI - 2026 vanphat.xlsx` và sổ công nợ 131/331 thành `payment_entry_master.csv`.

---

## 3. CÂU LỆNH MẪU KHI MỞ ĐẦU SESSION TIẾP THEO

Sếp chỉ cần copy câu lệnh sau và gửi cho em:

```text
Đọc docs/handoff.md và tiếp tục triển khai:
Chuẩn hoá các bộ dữ liệu giao dịch thực tế (Sales Order, Purchase Order, Work Order, Payment Entry) từ raw-data gốc theo đúng 100% wording ERPNext Native v16 (dựa trên docs/specs/erpnext-native-vi-en-mapping.md).
```
