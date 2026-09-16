# API (`apps/vanphat_portal/vanphat_portal/api/`)

Hệ thống API mỏng (Thin Facade) phục vụ trực tiếp cho Van Phat Portal Cockpit. Mọi danh sách trả về theo cấu trúc phong bì phân trang chuẩn: `page_result` (`{<key>, page, page_length, total_count, total_pages}`).

---

## 1. Phân hệ Báo Giá (`api/bao_gia.py`)

| Endpoint | Quyền hạn (`_guards.py`) | Mô tả & Chức năng |
| :--- | :--- | :--- |
| `list_quotations` | `require_doc("Quotation", "read")` | Danh sách Báo giá từ DocType `Quotation` native, phân trang full-server (mặc định 15 dòng, trần 100). |
| `search_customers` | `require_doc("Customer", "read")` | Tìm kiếm nhanh khách hàng cho ô Khách hàng tại Modal Bước 1 (`name`, `customer_name`, `disabled=0`). |
| `calculate_packaging_quotation` | `require_doc("Item", "read")` | R&D Engine tính toán màng, keo, vòi, chạy 2 lane khổ rộng và trả về 2 kịch bản giá (Nấc 1: Tròn cuộn tối ưu; Nấc 2: Đúng số lượng yêu cầu bù rủi ro màng dở). |
| `get_quotation_price_preview` | `require_doc("Quotation", "read")` | Xem trước số tiền thuế VAT và tổng tiền từ Quotation nháp ERPNext. |
| `create_quotation` | `require_roles("Sales User", "Sales Manager", "System Manager")` + `require_doc("Quotation", "create")` | Tạo nháp chứng từ `Quotation` native với series `BG-.YY..MM.-.###`, gắn file thiết kế (nếu có). |

---

## 2. Phân hệ Danh Mục Hàng Hóa & Trục In (`api/item.py`)

| Endpoint | Quyền hạn (`_guards.py`) | Mô tả & Chức năng |
| :--- | :--- | :--- |
| `get_list` | `require_doc("Item", "read")` | Danh sách hàng hóa theo danh mục (`sp`: TP/NGCS/TMD/BTP; `truc`: Trục in; `nvl`: Màng/Keo/Vòi), hỗ trợ tìm kiếm tức thì và phân trang. |
| `get_detail` | `require_doc("Item", "read")` | Lấy chi tiết thông số kỹ thuật (kích thước, cấu trúc màng, vòi), định mức BOM 2 tầng (`BOM` native) và mã khách hàng độc quyền. |
| `quick_create_item` | `require_roles("Sales Manager", "System Manager")` + `require_doc("Item", "create")` | Tạo nhanh Item native trực tiếp từ Drawer của Portal. |
| `quick_update_item` | `require_roles("Sales Manager", "System Manager")` + `require_doc("Item", "write")` | Cập nhật thông số Item native trực tiếp từ Drawer của Portal. |

---

## 3. Phân hệ Đối Tác (`api/customer.py` & `api/supplier.py`)

| Endpoint | Quyền hạn (`_guards.py`) | Mô tả & Chức năng |
| :--- | :--- | :--- |
| `customer.get_list` | `require_doc("Customer", "read")` | Danh sách khách hàng native (`KH-`), hiển thị tên gọi tắt (`alias`), tên pháp nhân, MST, điều khoản cọc. |
| `customer.get_detail` | `require_doc("Customer", "read")` | Chi tiết khách hàng và danh sách các mặt hàng túi màng ghép độc quyền thuộc khách hàng đó. |
| `customer.quick_create` | `require_roles("Sales User", "Sales Manager", "System Manager")` + `require_doc("Customer", "create")` | Tạo nhanh khách hàng mới từ Drawer Portal. |
| `customer.quick_update` | `require_roles("Sales User", "Sales Manager", "System Manager")` + `require_doc("Customer", "write")` | Cập nhật nhanh thông tin khách hàng từ Drawer Portal. |
| `supplier.get_list` | `require_doc("Supplier", "read")` | Danh sách nhà cung cấp native (`NCC-`) theo phân nhóm vật tư (Màng thô, Trục in, Keo, Phụ kiện). |
| `supplier.get_detail` | `require_doc("Supplier", "read")` | Chi tiết nhà cung cấp và thông tin liên hệ. |

---

## 4. Bảo Mật & Tiêu Chuẩn Truy Vấn

* **Phân quyền chặt chẽ:** Sử dụng `_guards.py` (`require_roles` + `require_doc` kiểm tra quyền DocType native). Cấm tuyệt đối `ignore_permissions=True` hoặc `allow_guest=True` trên các dữ liệu nghiệp vụ.
* **Không SQL Mutation trực tiếp:** 100% lệnh tạo/sửa dùng Frappe Document API (`get_doc`, `insert()`, `save()`, `db.commit()`) để kích hoạt đầy đủ validation hook của ERPNext.
* **Chống N+1 Query:** Mọi danh sách được truy vấn qua `frappe.db.get_list` hoặc `frappe.qb` với chỉ mục phù hợp.
