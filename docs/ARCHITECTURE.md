# ARCHITECTURE

## 1. Công nghệ & Nền tảng (Stack)

* **Backend & Core ERP:** Frappe Framework & ERPNext v16.34.2 native. MariaDB 10.6+ & Redis Cache.
* **Frontend Portal:** Vue 3.5 `<script setup>` + Vite 7 + Tailwind CSS v3 standalone + Native HTML5 `<dialog>` (`BaseModal`, `BaseDrawer`, `ConfirmDialog`) + `vue-sonner@2.0.9`. Hash router (`CatalogView.vue`). Served static tại `/portal`.
* **Zero External Heavy UI Library:** Không dùng các UI library nặng; 100% overlay dùng `<dialog>` native trình duyệt để đảm bảo tốc độ p95 < 200ms.

---

## 2. Phân tầng & Ranh giới Hệ thống (Boundaries)

### 2.1. ERPNext Desk Native (Nghiệp vụ cốt lõi & Vận hành nặng)
ERPNext Desk đảm nhiệm 100% các phân hệ giao dịch, quy trình phê duyệt, chuỗi cung ứng và kế toán:
* **Bán hàng (Selling):** Quản lý vòng đời `Sales Order` (duyệt cọc, chốt giao hàng, hợp đồng kinh tế).
* **Mua hàng (Buying):** `Purchase Order` mua màng thô (Tuệ Nhi, Kiến Tâm...), đặt ngoài túi TMD (Thanh Tùng), gia công trục in (DONGYUN).
* **Sản xuất (Manufacturing):** Quản lý `BOM` (màng, keo, vòi), lệnh sản xuất `Work Order` (công đoạn In $\rightarrow$ Ghép $\rightarrow$ Cắt $\rightarrow$ Đóng vòi).
* **Kho vận (Stock):** `Stock Entry` xuất/nhập/tồn kho cuộn màng NVL, phôi NGCS, thành phẩm TP, thu hồi phế liệu.
* **Kế toán & Tài chính (Accounts):** `Payment Entry` (phiếu thu cọc, chi tiền NCC, sổ quỹ, theo dõi công nợ).

### 2.2. Van Phat Portal (Cockpit Siêu tốc cho Kinh doanh & Kỹ thuật)
Giải quyết triệt để vấn đề: *Giao diện Desk ERP quá nhiều thông tin, rối mắt và phức tạp đối với nhân viên thao tác hàng ngày.*
Portal được thiết kế như một **Cockpit 1 dòng tinh gọn** với 4 visual trọng yếu:
1. **Modal Báo Giá Bước 1 (`ModalStep1Sale.vue`):** Nhân viên Sales nhập nhanh loại túi, kích thước (R x D x Đáy), cấu trúc màng, vòi, số lượng và chọn khách hàng.
2. **Drawer Báo Giá Bước 2 (`DrawerStep2Director.vue`):** Giám đốc duyệt giá dựa trên công thức tính toán R&D xưởng (chạy 2 con khổ rộng, báo giá 2 nấc tròn cuộn vs đúng số lượng, tiền trục tách riêng) và tạo nháp `Quotation` native xuống ERPNext.
3. **Trang Danh mục Cockpit (`CatalogView.vue`):** 5 tab thực thể tra cứu tức thì:
   * `[Sản phẩm]`: Bao bì thành phẩm TP độc quyền, NGCS, TMD, BTP bán cuộn (kèm drawer chi tiết quy cách + BOM).
   * `[Trục in]`: Tra cứu tài sản trục in ống đồng (`TRUC-`), khổ dài, chu vi, số màu, vị trí kho.
   * `[Khách hàng]`: Tra cứu danh bạ KH, tên pháp lý, tên gọi tắt (`alias`), điều khoản cọc, danh sách túi.
   * `[Nhà cung cấp]`: Tra cứu danh bạ NCC (Màng thô, Gia công trục, Keo/hóa chất, Phụ kiện).
   * `[Nguyên vật liệu]`: Tra cứu màng thô (PET, MPET, PA, PE...), keo ghép, vòi.
   * Hỗ trợ **Quick CRUD Drawer**: Thêm/sửa nhanh Khách hàng, Sản phẩm, Trục in mà không phải vào Desk.
4. **Trang Đăng nhập (`www/login.html` + `login.py`):** Xác thực native Frappe session.

---

## 3. Bản đồ Module Backend (`apps/vanphat_portal/vanphat_portal/api/`)

| Module | Phụ trách Native DocType | Nhiệm vụ chính |
| :--- | :--- | :--- |
| `api/bao_gia.py` | `Quotation`, `Item`, `File` | Công cụ tính giá R&D xưởng (`calculate_packaging_quotation`), tìm kiếm KH nhanh, tạo nháp `Quotation` native. |
| `api/item.py` | `Item`, `BOM`, `Item Group` | Full-server catalog 5 nhóm hàng, tra cứu quy cách, Trục in, NVL, BOM 2 tầng, Redis cache. |
| `api/customer.py` | `Customer` | Tra cứu nhanh KH, lấy chi tiết, Quick Create/Update KH từ Portal Drawer xuống `Customer` native. |
| `api/supplier.py` | `Supplier` | Tra cứu danh bạ NCC theo phân nhóm vật tư. |
| `api/_common.py` | — | Tiện ích chuẩn: `paginate`, `page_result`, `text`, `as_json`. Không chứa business logic. |
| `api/_guards.py` | — | Kiểm tra quyền truy cập native: `require_roles`, `require_doc`. |

*Loại bỏ hoàn toàn:* `api/order.py`, `order_queries.py`, `order_pricing.py`, `order_actions.py`, `user.py`.

---

## 4. Nguyên tắc Bất biến (Core Invariants)

1. **Native-First:** Dữ liệu luôn được lưu vào DocType chuẩn của ERPNext (`Customer`, `Supplier`, `Item`, `Quotation`, `BOM`). Trường tùy biến (`custom_*`) chỉ được thêm khi native chứng minh không có.
2. **Không trùng lặp Logic:** Portal không tính toán thuế, không duyệt công nợ hay xử lý vòng đời đơn hàng; tất cả giao dịch sau báo giá được chuyển giao hoàn toàn cho ERPNext Desk Native.
3. **Tiền trục độc lập:** Tiền trục in ống đồng thanh toán riêng cho đơn hàng đầu, tuyệt đối không gộp vào đơn giá 1 túi thành phẩm.
