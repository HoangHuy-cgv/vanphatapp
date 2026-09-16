# UI (`apps/vanphat_portal/frontend/src/`)

> [!TIP]
> Toàn bộ sơ đồ trực quan (ASCII Wireframes), bố cục chi tiết và layout in ấn A4 được đặc tả tại: [`docs/specs/ui-wireframes.md`](file:///var/home/huy/vanphatapp/docs/specs/ui-wireframes.md).

Stack: Vue 3.5 `<script setup>`, hash router (`CatalogView.vue`), native `<dialog>` (`BaseModal`, `BaseDrawer`, `ConfirmDialog`) + `vue-sonner@2.0.9`, Tailwind CSS v3 standalone, Vite 7. Không sử dụng thư viện UI bên ngoài; tối ưu bundle size và phản hồi cực nhanh (p95 < 200ms).

---

## 1. 4 Thành phần Giao diện Trọng yếu (Visual Baseline)

1. **Modal Báo Giá Bước 1 (`ModalStep1Sale.vue`):**
   - Dùng native `<BaseModal>`.
   - Chọn loại túi (3 biên, Đáy đứng, Xếp hông, 8 cạnh, Cuộn màng), công nghệ in (In trục, In lụa, Không in), phụ kiện vòi (10mm, 16mm, 22mm, Hàn kín).
   - Chọn khách hàng qua ô Link Search tức thời (`search_customers`).
   - Nhập kích thước (Rộng x Dài x Đáy/Hông) và chuyển tiếp dữ liệu sang Bước 2 qua 1 sự kiện `submit` duy nhất.

2. **Drawer Báo Giá Bước 2 (`DrawerStep2Director.vue`):**
   - Dùng native `<BaseDrawer>` trượt từ phải sang.
   - Tự động gọi engine `calculate_packaging_quotation` để hiển thị tính toán R&D xưởng (chạy 2 con, định mức màng/keo).
   - Hiển thị song song **2 kịch bản giá:** Nấc 1 (Tròn cuộn tối ưu - Giá rẻ nhất) vs Nấc 2 (Đúng số lượng yêu cầu - Có đệm rủi ro màng dở).
   - Bóc tách độc lập dòng tiền trục in ống đồng (nếu có).
   - Nút "Tạo Báo Giá" gửi payload xuống ERPNext để tạo `Quotation` native.

3. **Trang Danh mục Cockpit (`CatalogView.vue`):**
   - 1-line Header chuẩn Cockpit: `[5 Tabs Bar] + [Thanh Tìm Kiếm Tức Thời] + [Nút Thêm Mới]`.
   - **5 Tab Thực Thể:**
     * `sp` (Sản phẩm): Tên gọi quen thuộc (`custom_alias`), Loại túi, R x D x Dày, Đáy, ĐVT.
     * `truc` (Trục in): Mã laser NCC (`TRUC-`), Tên sản phẩm in, Khách hàng, Chiều dài, Chu vi, Số màu, Kho trục.
     * `kh` (Khách hàng): Tên gọi tắt (`alias`), Tên pháp nhân, MST, Số điện thoại, Điều khoản cọc.
     * `ncc` (Nhà cung cấp): Tên nhà cung cấp, Phân nhóm vật tư (Màng, Trục, Keo, Phụ kiện), Điện thoại liên hệ.
     * `nvl` (Nguyên vật liệu): Tên màng/vật tư, Độ dày mic, Khổ mm, Tỷ trọng, ĐVT.
   - **Quick CRUD Drawer:** Click vào dòng mở Drawer xem chi tiết; nút "+ Thêm" mở form tạo nhanh Khách hàng, Sản phẩm, Trục in trực tiếp trên Portal mà không cần truy cập Desk ERP phức tạp.

4. **Trang Đăng Nhập (`www/login.html` + `login.py`):**
   - Giao diện đăng nhập tĩnh, trực tiếp qua session Frappe.

---

## 2. Quy tắc Giao diện & Trải nghiệm Người dùng (Cockpit Baseline)

- **Giao tiếp Dữ liệu:** 100% gọi API qua `api()` trong `composables/useSession.js` (tự đính kèm CSRF token, toast lỗi tiếng Việt, `AbortSignal`). Nhận dữ liệu qua phong bì chuẩn `page_result`.
- **Không Math tiền/thuế ở Client:** Mọi số tiền hiển thị theo định dạng tiền tệ Việt Nam `Intl.NumberFormat('vi-VN')`. Thuế và tổng tiền Quotation đọc từ số server trả về.
- **Tìm kiếm Debounce:** Debounce 250–300ms + hủy request cũ (`AbortController`) để chỉ render kết quả tìm kiếm mới nhất.
- **Tối ưu Thao tác (≤ 8 lựa chọn):** Dùng các nút bấm chọn nhanh (Click-Select buttons với `role="radiogroup"`, kích thước touch $\ge 44$px).
- **Bộ lọc Trực quan & Bảng Tinh gọn:** Bảng 5–7 cột, hàng cao 42–46px, số liệu căn phải font mono `tabular-nums`. Trạng thái luôn có chữ tiếng Việt kèm màu nền chuẩn contrast $\ge 4.5:1$.
- **Native Overlays:** Modal dùng `BaseModal` (`<dialog>` + `showModal()`), Drawer dùng `BaseDrawer` (`<dialog>`), Xác nhận dùng `ConfirmDialog` (`role="alertdialog"`). Không đặt thuộc tính `tabindex` trên thẻ `<dialog>`.
