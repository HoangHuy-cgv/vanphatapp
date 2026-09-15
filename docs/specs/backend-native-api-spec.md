# Ranh Giới Backend Native API (Frappe/ERPNext Thin Wrappers)

> **SSOT:** Mọi quy tắc backend tập trung tại file này. `AGENTS.md` §5 chỉ tóm tắt. Code thực tế: `apps/vanphat_portal/vanphat_portal/api/`.
> Chuẩn tiền/HOLD/envelope duy nhất: xem ADR-006 (thay mọi định nghĩa preview cũ rải rác trước đây).

## 1. Module Map & Trách Nhiệm (đo lại 2026-09-15: P1–P3 xong, ADR-006 chốt 2026-09-15)
| Module | Native chính | Trách nhiệm |
|---|---|---|
| `order.py` | Sales Order, Quotation (nháp tính thuế), Payment Entry, Customer Credit Limit | Lifecycle đơn: `list_orders` (+ tab counts), `get_order_details` (+ `_order_lifecycle`), `get_price_preview` (doc-driven + pass-through), `create/record/submit/approve/make_order` |
| `bao_gia.py` | Quotation, Item, File | Báo giá: `list_quotations`, `search_customers`, `create/submit/lost`, `get_quotation_price_preview`, `calculate_packaging_quotation` (engine R&D — hằng số kỹ thuật xưởng, KHÔNG native hóa, ADR-002), `get_boot` |
| `item.py` | Item, BOM | Catalog full-server (filters/or_filters/count), BOM 2-tier, cache Redis |
| `customer.py`/`supplier.py`/`user.py` | Customer/Supplier/User | Danh mục **envelope** `page_result` + `or_filters` + paginate picker, truthful empty |
| `_common.py` | — | Helper dùng chung, KHÔNG whitelist: `paginate`/`page_result`/`text`/`as_json`/`resolve_customer`. Không chứa nghiệp vụ/không toán tiền |

- Wrapper mỏng: bọc native, không chứa nghiệp vụ trùng native. Không re-export ghi đè câm (bug S4 đã chốt SSOT).

## 2. Native-First Lookup (Khi Cần Dữ Liệu Mới)
1. Tìm DocType/field/method native có sẵn (mapping SSOT: `erpnext-native-vi-en-mapping.md`).
2. Không có → `frappe.db.get_list` / `frappe.qb` / `frappe.cache` / `has_permission`.
3. Vẫn thiếu → thin wrapper trong `vanphat_portal.api.*`.
4. Hết cách → Custom field (`custom_` prefix) + ADR + ánh xạ mapping. Cấm custom trùng native.

## 3. Query Chuẩn (Chữa N+1 + hai lớp page_length — ADR-006)
- List: `frappe.db.get_list(doctype, fields=[...], filters=..., or_filters=..., order_by=..., start=..., page_length=...)`.
- **Hai lớp pagination (ADR-006, không giả vờ một số):** giao dịch (orders/quotations/items)
  `default 15, max 100` (helper `_common.paginate`); picker tham chiếu (customer/supplier/user
  cho ô chọn) `default 100, max 100` + filter server, vì picker hiện tải một lần cho ô chọn.
  Slice sau paginate picker + search server. Cấm `page_length=500` vượt trần và cấm
  `limit=500` rồi filter/lọc bằng Python.
- Join nhiều DocType (Customer alias, SO Item đầu, Item `custom_alias`): **1 query `frappe.qb`** thay vì vòng lặp `get_value`/`get_all` từng dòng (N+1).
- **Sổ đo query/trang (đếm tĩnh theo code, 2026-09-14):**

| Endpoint | Trước | Sau |
|---|---|---|
| `order.list_orders` (15 đơn/trang) | ~3 + 2N ≈ 33 query | **6 query cố định** (count + rows + tab counts + 1 dòng hàng cả trang + 2 cọc/KH) |
| `item.get_detail` (BOM n dòng) | 1 + n query alias | **+1 query** (`["in", codes]`) |
| `order.get_order_details` | 3 query `Item` rời + 3 cọc | **1 query `Item`** + cọc gộp |
| `bao_gia.list_quotations` khi tìm | count chỉ lọc `name` (sai số) | count khớp đúng `or_filters` (1 Criterion) |

  Chưa đo được p95 trên site thật (chưa có bench staging — plan item 2); số trên là đếm tĩnh + harness `apps/vanphat_portal/tests`.
- Soi SQL bằng `debug=True` khi nghi ngờ. Raw SQL chỉ cho báo cáo join phức tạp, cấm mutation production.
- Master data nhạy cảm: `get_list` (tôn trọng permission), cấm `get_all` bypass.
- Nợ tồn: `order.list_orders`/`item.get_list` (nhánh qb) chưa áp permission như `get_list`; cần role check ở tầng endpoint (Sếp chốt sau).

## 4. Chuẩn Method (GET/POST, Commit, Response)
- GET cho read/preview, POST cho create/submit/cancel. Không GET gây mutation.
- POST tự `frappe.db.commit()` sau khi persist (đã áp: `create_sales_order`, `record_order_deposit`,
  `accountant_approve_procurement`, `submit_sales_order`, `create_quotation`, `submit_quotation`,
  `mark_quotation_lost`, `make_order_from_quotation`). Không commit nửa chừng rồi tiếp tục tính toán phụ thuộc.
- Response: envelope `page_result` thống nhất cho MỌI list
  (`{<key>, page, page_length, total_count, total_pages}` — ADR-006); detail/mutate trả
  object (Frappe tự bọc `{message: ...}`). Lỗi: `frappe.throw(msg)` → `{exc, exc_type}` cho client toast.
- Trạng thái buồng lái: một công thức duy nhất list + drawer (ADR-006):
  HOLD ⟺ Trả trước AND `0 < advance_paid < required_deposit`; Trả sau không bao giờ HOLD.
  `order_status_label/class` từ `status`/`docstatus`/`advance_paid`/`required_deposit`;
  `outstanding_amount = grand_total - advance_paid`; `deposit_pct`;
  `required_deposit = product_total × deposit_pct + cylinder_total` (`0` khi Trả sau).
- Thiếu `Default Company`: báo lỗi rõ ràng, KHÔNG hardcode tên công ty (Sếp chốt 2026-09-14 — cấu hình Default Company = Bao Bì Vạn Phát ở site).

## 5. Cache Redis
- Key PHẢI chứa mọi params: `vp:items:list|tab=<t>|grp=<g>|supply=<s>|q=<q>|page=<p>|pl=<pl>`
  (`item.py:138` — đã đủ params từ trước; backend spec cũ mô tả thiếu là sai, sửa theo code).
- TTL 300s. Invalidate chủ động qua `doc_events` (`Item`, `Quotation`, `Customer`, `Sales Order` `on_update`) thay vì endpoint guest xả cache (`clear_catalog_cache allow_guest` — slice S3 đóng).
- Không cache dữ liệu per-user/permission-sensitive chung key.

## 6. Bảo Mật (Đóng 4 Lỗ Hổng Đã Biết — Slices S5/S6; cổng quyền full — Sếp chốt 2026-09-15)
- Xóa `allow_guest=True` khỏi master data nội bộ (`item.get_list`, `customer.get_list/get_detail`, `clear_catalog_cache`).
- Portal bắt buộc login + role check (`System Manager`, `Sales User`, `Accounts User`, `Manufacturing User`, `Stock User`).
- GET chi tiết: `get_doc` + `frappe.has_permission()` tại nơi action; child table truyền `parent` để check quyền (không trả cả doc thừa field nhạy cảm).
- CSRF: mọi POST qua `api()` đã gắn token; không whitelist POST không cần auth.
- Fallback CSV (`customer.py`, `item.py` `_load_csv_*`): thay bằng truthful empty state + log server. DB trống → `[]`, không đọc file hệ thống thay thế.

### 6.1. Ma trận quyền native (Sếp chốt 2026-09-15 — Desk giữ "ai được làm gì", code chỉ gác cổng)
- **Cơ chế native:** 1 user kiêm nhiệm nhiều role; quyền trên từng DocType cấu hình trong
  **Role Permission Manager** (Desk), lọc theo bản ghi bằng **User Permissions**. Code gọi 2 API:
  `frappe.get_roles()` (user có role gì) + `frappe.has_permission(doctype, ptype, doc?)`
  (role + User Permissions có cho phép không). Helper duy nhất: `api/_guards.py`
  (`require_roles` = OR role, `require_doc` = has_permission tới cấp chứng từ + báo lỗi tiếng Việt).
- **Nhóm đọc catalog (Item/Customer/Supplier + preview/lookup/config):** `has_permission(read)` tương ứng
  (`Item` cho catalog + `get_product_groups`/`get_print_config` + engine R&D; `Customer` cho
  `get_list/get_detail/search_customers`; `Supplier` cho NCC; `Payment Terms Template` cho
  `get_payment_options`; `Quotation` cho `list_quotations`/preview; `Sales Order` cho
  `list_orders`/`get_order_details`/`get_price_preview`). Đường `qb` không tự áp permission như
  `get_list` → cổng read ở đầu mỗi endpoint (Sếp chọn "thấy hết công ty" nên chưa lọc theo owner).
  Cache `get_list` key kèm `roles=` để không rò dữ liệu vượt quyền.
- **Nhóm Sales tạo/chốt (Sales User | Sales Manager | System Manager):** `create_sales_order` (create SO),
  `submit_sales_order` (submit SO — đơn HOLD tự chặn), `make_order_from_quotation` (read BG + create SO),
  `create/submit/lost_quotation` (create/submit/write BG).
- **Nhóm Kế toán độc quyền (Accounts User | Accounts Manager):** `record_order_deposit` (write SO),
  `accountant_approve_procurement` (submit SO — duyệt đơn HOLD).
- **Khóa riêng:** `user.get_list` chỉ System Manager (PII nội bộ); `clear_catalog_cache` bỏ whitelist —
  hàm nội bộ, `doc_events` gọi trực tiếp (26 endpoint còn lại, không còn W1).
- **Cấm:** `ignore_permissions` ở mọi API người dùng (đã xóa khỏi `create_sales_order`).
- **Máy kiểm:** `constraints-check.py → api_ungated = 0` (25 gated + W2 `get_boot`).
  Quyết Sếp còn treo làm slice riêng: flow cọc 2 bước (Sales yêu cầu → Kế toán xác nhận).

## 7. Giá & Thuế Native (P1+P2 Sếp duyệt 2026-09-15 — ADR-002)
- VAT doc-driven: gán Sales Taxes and Charges Template (Default theo Company → Tax Rule theo KH)
  lên Quotation nháp trong memory, `calculate_taxes_and_totals`, đọc
  `total/total_taxes_and_charges/grand_total`. Cấm `round(net*rate)` tay trong flow preview/báo giá/đơn.
- Trục pass-through NCC: `cylinder_spec {qty, unit_price, supplier}` — giá NCC quyết, Vạn Phát
  mua đi bán lại. Thiếu giá → `cylinder_pending: true`, cặp `*_final: null` truthful.
  Cấm mọi hằng số/fallback số trục. Dòng trục tạo đơn KHÔNG dùng `item_code` cứng
  (`"TRUC-IN"` đã xóa — ADR-006); ghi đúng mã `TRUC-` native khi có mã thật.
- Cọc: `Payment Terms Template` (`invoice_portion`) + `Customer Credit Limit` (Trả sau = 0đ).
- **Ngữ nghĩa số tiền duy nhất mọi màn (ADR-006, thay mọi định nghĩa preview cũ):**
  `net_total`/`vat_amount`/`grand_total` là số native trên chứng từ;
  `cylinder_total` = tiền trục **chưa VAT** (giá NCC thuần);
  `product_total = net_total − cylinder_total` (tiền hàng chưa VAT, không gồm trục);
  `qty` = tổng số lượng **chỉ dòng túi/cuộn** (bỏ dòng trục để không trộn đơn vị Túi với Cây).
  Tổng kiểm chứng: `product_total + cylinder_total + vat_amount = grand_total`.
  `required_deposit = product_total × deposit_pct + cylinder_total` (`0` khi Trả sau).
  HOLD duy nhất: Trả trước AND `0 < advance_paid < required_deposit` (Trả sau không HOLD).
  Chỉ còn 1 fallback được phép: `FALLBACK_DEPOSIT_PCT = 0.5` khi KH thiếu template + ghi log.
- Tab phân loại chuỗi `NGCS/TMD` → `Item Group` filter server khi có data (giữ tạm, S9-phạm-vi sau).
  Nợ: `_item_product_group` (drawer) chưa nhận diện TMD vì tên thật "Túi nilon HD..." không khớp nhánh nào —
  cần Sếp chốt phân loại theo `item_group`/prefix thay vì chuỗi tên.

## 8. Cấm Tuyệt Đối (Nhắc Lại Từ AGENTS.md)
- `get_all` cho master nhạy cảm, `allow_guest` dữ liệu nội bộ, raw SQL CRUD thường, re-export ghi đè câm, cache key thiếu params, `limit=500` + filter Python.
- Toán tiền/thuế tay trong Python, mọi hằng số/fallback giá trục (`3100000`, `CYLINDER_STANDARD_RATE`, `_get_cylinder_rate`).
