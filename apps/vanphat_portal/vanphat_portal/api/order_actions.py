"""Ghi: cọc, duyệt ngoại lệ, submit, tạo đơn (tách từ order.py, Task 6c).

Không whitelist ở đây — wrapper giữ ở `order.py`.
"""

import frappe

from vanphat_portal.api._common import as_json, resolve_customer, text
from vanphat_portal.api._guards import require_doc, require_roles
from vanphat_portal.api.order_pricing import (
	_cylinder_item_name,
	_cylinder_spec_state,
	_default_deposit_pct,
	_get_deposit_pct,
	_credit_limit,
	_order_status,
	_required_deposit,
	_resolve_tax_template,
	DEFAULT_ORDER_NAMING_SERIES,
	SETTINGS_DOCTYPE,
)
from vanphat_portal.api.order_queries import _get_sales_order, _order_lifecycle


# Ghi: cọc, duyệt ngoại lệ, submit, tạo đơn
# --------------------------------------------------------------------------


def record_order_deposit(name, amount=0, note=""):
	"""Kế toán xác nhận cọc cho Sales Order (Sếp chốt 2026-09-15: chỉ Kế toán).

	Trước đây Sales cũng bấm trực tiếp; từ slice quyền này Sales chỉ "yêu cầu",
	Kế toán là người xác nhận duy nhất (flow 2 bước làm slice riêng).
	"""
	require_roles("Accounts User", "Accounts Manager")
	require_doc("Sales Order", "write", name=name)
	doc = _get_sales_order(name)
	if doc.docstatus == 2:
		frappe.throw("Đơn hàng đã bị hủy, không thể ghi nhận cọc.")

	amt = frappe.utils.flt(amount)
	if amt <= 0:
		frappe.throw("Số tiền cọc phải lớn hơn 0.")

	new_advance = frappe.utils.flt(doc.advance_paid) + amt
	doc.db_set("advance_paid", new_advance)
	doc.add_comment(
		"Comment",
		text=f"Ghi nhận cọc: {amt:,.0f} đ. Tổng đã cọc: {new_advance:,.0f} đ. Ghi chú: {note}",
	)
	doc.reload()
	frappe.db.commit()

	life = _order_lifecycle(doc)
	if life["can_submit"]:
		doc.submit()
		frappe.db.commit()
		after = _order_lifecycle(doc)
		return {
			"name": doc.name,
			"auto_submitted": True,
			"order_state": after["order_state"],
			"success": True,
		}

	return {
		"name": doc.name,
		"advance_paid": doc.advance_paid,
		"outstanding_amount": life["outstanding_amount"],
		"order_state": life["order_state"],
		"is_hold": life["is_hold"],
		"success": True,
	}


def accountant_approve_procurement(name, note=""):
	"""Kế toán duyệt ngoại lệ đơn HOLD → chuyển bước 'Mua hàng NCC' (độc quyền Kế toán)."""
	require_roles("Accounts User", "Accounts Manager")
	require_doc("Sales Order", "submit", name=name)
	doc = _get_sales_order(name)
	doc.add_comment(
		"Comment",
		text=(
			"Kế toán phê duyệt chuyển bước 'Mua hàng NCC' "
			f"(Duyệt ngoại lệ đơn HOLD): {note or 'Kế toán xác nhận cho chạy tiếp'}"
		),
	)

	if doc.docstatus == 0:
		doc.flags.ignore_mandatory = True
		doc.submit()

	frappe.db.commit()
	return {
		"name": doc.name,
		"status": "Đã chuyển Mua hàng NCC",
		"docstatus": doc.docstatus,
		"success": True,
	}


def submit_sales_order(name):
	"""Sales kích hoạt đơn đủ cọc (Sếp chốt: Sales User/Manager + submit native)."""
	require_roles("Sales User", "Sales Manager", "System Manager")
	require_doc("Sales Order", "submit", name=name)
	doc = _get_sales_order(name)
	if doc.docstatus != 0:
		frappe.throw("Chỉ có thể submit đơn hàng ở trạng thái Nháp (Draft).")

	life = _order_lifecycle(doc)
	if life["is_hold"]:
		frappe.throw(
			"Đơn hàng đang ở trạng thái HOLD (cọc thiếu). "
			"Chỉ Kế toán mới có quyền bấm nút 'Mua hàng NCC' để duyệt tiếp."
		)
	if not life["can_submit"]:
		frappe.throw(
			"Đơn hàng chưa đủ điều kiện (cần cọc {}% tiền hàng + 100% tiền trục, "
			"tổng cần: {:,.0f} đ).".format(
				round(_get_deposit_pct(doc.customer) * 100.0, 1), life["required_deposit"]
			)
		)

	doc.submit()
	frappe.db.commit()
	return {"name": doc.name, "status": doc.status, "docstatus": doc.docstatus}


def _default_finished_warehouse(company=None):
	"""Kho thành phẩm mặc định cho dòng SO (native bắt source warehouse với stock item).

	Ưu tiên kho có tên chứa 'Thành Phẩm' của đúng company; thiếu → None (để native báo).
	"""
	try:
		abbr = frappe.db.get_value("Company", company, "abbr") if company else None
		filters: dict = {"is_group": 0}
		if abbr:
			filters["company"] = frappe.db.get_value("Company", {"abbr": abbr}, "name") or company
		rows = frappe.db.get_list(
			"Warehouse", filters=filters, fields=["name"], order_by="name asc", page_length=50
		)
		for row in rows or []:
			if "Thành Phẩm" in (row.get("name") or ""):
				return row.get("name")
		return (rows or [{}])[0].get("name")
	except Exception:
		return None


def create_sales_order(payload):
	"""Sales tạo đơn mới (DH- series) — Sếp chốt: Sales User/Manager + create native.

	Sếp chốt 2026-09-15: bỏ `ignore_permissions` — ai không có quyền tạo SO
	trong Role Permission Manager thì API cũng từ chối, không lách.
	"""
	require_roles("Sales User", "Sales Manager", "System Manager")
	require_doc("Sales Order", "create")
	payload = as_json(payload) or {}
	company = payload.get("company") or frappe.defaults.get_user_default("Company")
	if not company:
		frappe.throw("Thiếu Company mặc định — cấu hình Global Defaults (Default Company) trước.")

	customer_id = text(payload.get("customer") or payload.get("customer_id"))
	if not customer_id:
		frappe.throw("Thiếu khách hàng — vui lòng chọn Customer.")
	customer_id = resolve_customer(customer_id) or customer_id

	delivery_date = payload.get("delivery_date") or frappe.utils.add_days(frappe.utils.today(), 7)
	# Kho xuất mặc định cho stock item (native bắt buộc source warehouse khi tạo SO).
	default_wh = text(payload.get("warehouse")) or _default_finished_warehouse(company)
	so_items = []
	for row in payload.get("items") or payload.get("lines") or []:
		code = text(row.get("item_code"))
		item_name = (row.get("item_name") or row.get("variant_name") or code)[:140]
		so_item = {
			"item_name": item_name,
			"description": item_name,
			"qty": frappe.utils.flt(row.get("qty") or 1),
			"rate": frappe.utils.flt(row.get("rate") or 0),
			"uom": row.get("uom") or "Túi",
			"conversion_factor": 1,
			"delivery_date": delivery_date,
		}
		wh = text(row.get("warehouse")) or default_wh
		if wh:
			so_item["warehouse"] = wh
		if code:
			so_item["item_code"] = code
		so_items.append(so_item)

	# P2 pass-through (ADR-006): thiếu giá NCC → KHÔNG tự thêm dòng, KHÔNG fallback số.
	# Dòng trục không dùng item_code cứng: caller gửi đúng mã TRUC- native trong items;
	# ở đây chỉ nhận thêm khi payload nêu rõ mã trục thật.
	cyl = _cylinder_spec_state(as_json(payload.get("cylinder_spec")))
	cyl_item_code = text(payload.get("cylinder_item_code") or cyl.get("item_code"))
	if payload.get("has_new_cylinders") and (payload.get("cylinder_count") or cyl["qty"]):
		cyl_qty = int(payload.get("cylinder_count") or cyl["qty"] or 0)
		if cyl_qty > 0 and cyl["unit_price"] > 0 and cyl_item_code:
			so_items.append({
				"item_code": cyl_item_code,
				"item_name": _cylinder_item_name(cyl_qty, cyl["supplier"]),
				"description": f"Trục in theo báo giá NCC ({cyl_qty} cây)",
				"qty": cyl_qty,
				"rate": cyl["unit_price"],
				"uom": "Cây",
				"conversion_factor": 1,
				"delivery_date": delivery_date,
			})

	doc = frappe.get_doc({
		"doctype": "Sales Order",
		"naming_series": payload.get("naming_series") or DEFAULT_ORDER_NAMING_SERIES,
		"customer": customer_id,
		"delivery_date": delivery_date,
		"transaction_date": payload.get("transaction_date") or frappe.utils.today(),
		"company": company,
		"order_type": "Sales",
		"items": so_items,
	})
	doc.insert()
	frappe.db.commit()

	return {
		"name": doc.name,
		"status": doc.status,
		"grand_total": doc.grand_total,
		"success": True,
	}


def make_order_from_quotation(name, naming_series=None, delivery_date=None):
	"""Sales chốt báo giá đã duyệt → Sales Order (native make_sales_order)."""
	require_roles("Sales User", "Sales Manager", "System Manager")
	require_doc("Quotation", "read", name=name)
	require_doc("Sales Order", "create")
	from erpnext.selling.doctype.quotation.quotation import make_sales_order

	doc = frappe.get_doc("Quotation", name)
	if doc.docstatus != 1 or doc.status not in ("Open", "Partially Ordered"):
		frappe.throw("Chỉ chốt từ báo giá đã duyệt (Open).")
	order = make_sales_order(name)
	order.naming_series = naming_series or DEFAULT_ORDER_NAMING_SERIES
	if not order.get("delivery_date"):
		order.delivery_date = delivery_date or frappe.utils.today()
	order.insert()
	frappe.db.commit()
	return {"sales_order": order.name, "quotation": doc.name}
