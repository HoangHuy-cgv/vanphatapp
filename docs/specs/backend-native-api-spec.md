# Ranh Giới Backend Native API (Frappe/ERPNext Thin Wrappers)

> **SSOT:** Mọi quy tắc backend tập trung tại file này. `AGENTS.md` §5 chỉ tóm tắt. Code thực tế: `apps/vanphat_portal/vanphat_portal/api/`.

## 1. Module Map & Trách Nhiệm (đo lại 2026-09-15: P1–P3 xong)
| Module | Native chính | Trách nhiệm |
|---|---|---|
| `order.py` | Sales Order, Quotation (nháp tính thuế), Payment Entry, Customer Credit Limit | Lifecycle đơn, preview doc-driven (`_price_via_doc`), trục pass-through (`cylinder_spec`), tab counts |
| `bao_gia.py` | Quotation, Item, File | Báo giá, `calculate_packaging`, link-search Customer, preview đọc số native |
| `item.py` | Item, BOM | Catalog full-server (filters/or_filters/count), BOM 2-tier, cache Redis |
| `customer.py`/`supplier.py`/`user.py` | Customer/Supplier/User | Master login-only + `or_filters` + paginate, truthful empty |

- Wrapper mỏng: bọc native, không chứa nghiệp vụ trùng native. Không re-export ghi đè câm (bug S4 đã chốt SSOT).

## 2. Native-First Lookup (Khi Cần Dữ Liệu Mới)
1. Tìm DocType/field/method native có sẵn (mapping SSOT: `erpnext-native-vi-en-mapping.md`).
2. Không có → `frappe.db.get_list` / `frappe.qb` / `frappe.cache` / `has_permission`.
3. Vẫn thiếu → thin wrapper trong `vanphat_portal.api.*`.
4. Hết cách → Custom field (`custom_` prefix) + ADR + ánh xạ mapping. Cấm custom trùng native.

## 3. Query Chuẩn (Chữa N+1 + limit=500)
- List: `frappe.db.get_list(doctype, fields=[...], filters=..., or_filters=..., order_by=..., start=..., page_length=...)`.
- `page_length` mặc định 15, trần 100. Cấm `limit=500` rồi filter/lọc bằng Python (`order.py::list_orders` hiện tại — slice S2).
- Join nhiều DocType (Customer alias, SO Item đầu, Item `custom_alias`): **1 query `frappe.qb`** thay vì vòng lặp `get_value`/`get_all` từng dòng (N+1 — slice S2).
- Soi SQL bằng `debug=True` khi nghi ngờ. Raw SQL chỉ cho báo cáo join phức tạp, cấm mutation production.
- Master data nhạy cảm: `get_list` (tôn trọng permission), cấm `get_all` bypass.

## 4. Chuẩn Method (GET/POST, Commit, Response)
- GET cho read/preview, POST cho create/submit/cancel. Không GET gây mutation.
- POST tự `frappe.db.commit()` sau khi persist. Không commit nửa chừng rồi tiếp tục tính toán phụ thuộc.
- Response: `{message: ...}` (Frappe tự bọc). Lỗi: `frappe.throw(msg)` → `{exc, exc_type}` cho client toast.
- Trạng thái buồng lái tính server từ native: `order_status_label/class` từ `status`/`docstatus`/`advance_paid`; `outstanding_amount = grand_total - advance_paid`; `deposit_pct`; `required_deposit` từ `Payment Terms Template` + `Customer Credit Limit` (xóa hằng số Python tiến tới native — slice S9).

## 5. Cache Redis
- Key PHẢI chứa mọi params: `vp:items:list|tab=<t>&q=<q>&page=<p>` (hiện tại key thiếu params → stale cross-filter — slice S3).
- TTL 300s. Invalidate chủ động qua `doc_events` (`Item`, `Quotation`, `Customer`, `Sales Order` `on_update`) thay vì endpoint guest xả cache (`clear_catalog_cache allow_guest` — slice S3 đóng).
- Không cache dữ liệu per-user/permission-sensitive chung key.

## 6. Bảo Mật (Đóng 4 Lỗ Hổng Đã Biết — Slices S5/S6)
- Xóa `allow_guest=True` khỏi master data nội bộ (`item.get_list`, `customer.get_list/get_detail`, `clear_catalog_cache`).
- Portal bắt buộc login + role check (`System Manager`, `Sales User`, `Accounts User`, `Manufacturing User`, `Stock User`).
- GET chi tiết: `get_doc` + `frappe.has_permission()` tại nơi action; child table truyền `parent` để check quyền (không trả cả doc thừa field nhạy cảm).
- CSRF: mọi POST qua `api()` đã gắn token; không whitelist POST không cần auth.
- Fallback CSV (`customer.py`, `item.py` `_load_csv_*`): thay bằng truthful empty state + log server. DB trống → `[]`, không đọc file hệ thống thay thế.

## 7. Giá & Thuế Native (P1+P2 Sếp duyệt 2026-09-15 — ADR-002)
- VAT doc-driven: gán Sales Taxes and Charges Template (Default theo Company → Tax Rule theo KH)
  lên Quotation nháp trong memory, `calculate_taxes_and_totals`, đọc
  `total/total_taxes_and_charges/grand_total`. Cấm `round(net*rate)` tay trong flow preview/báo giá/đơn.
- Trục pass-through NCC: `cylinder_spec {qty, unit_price, supplier}` — giá NCC quyết, Vạn Phát
  mua đi bán lại. Thiếu giá → `cylinder_pending: true`, totals `null` truthful. Cấm mọi hằng số/fallback số trục.
- Cọc: `Payment Terms Template` (`invoice_portion`) + `Customer Credit Limit` (Trả sau = 0đ).
- Tab phân loại chuỗi `NGCS/TMD` → `Item Group` filter server khi có data (giữ tạm, S9-phạm-vi sau).

## 8. Cấm Tuyệt Đối (Nhắc Lại Từ AGENTS.md)
- `get_all` cho master nhạy cảm, `allow_guest` dữ liệu nội bộ, raw SQL CRUD thường, re-export ghi đè câm, cache key thiếu params, `limit=500` + filter Python.
- Toán tiền/thuế tay trong Python, mọi hằng số/fallback giá trục (`3100000`, `CYLINDER_STANDARD_RATE`, `_get_cylinder_rate`).
