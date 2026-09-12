"""Quotation shell API stubs (visual wiring proof only).

Every number below is a fixed literal for wiring proof. No arithmetic here:
all pricing math lives server-side per docs/specs/packaging-calculation-spec.md
and will replace these stubs.
"""

import frappe


@frappe.whitelist()
def list_quotations():
	names = frappe.get_list(
		"Quotation",
		fields=["name", "transaction_date", "customer_name", "grand_total", "status"],
		order_by="creation desc",
		limit=50,
	)
	return names
@frappe.whitelist()
def search_customers(query=""):
	"""Link-search Customer có sẵn cho ô Khách màn 1. Chỉ chọn, không tạo mới."""
	q = (query or "").strip()
	like = f"%{q}%"
	return frappe.get_list(
		"Customer",
		fields=["name", "customer_name"],
		filters={"disabled": 0},
		or_filters=[["Customer", "name", "like", like], ["Customer", "customer_name", "like", like]] if q else None,
		order_by="modified desc",
		limit=10,
	)


@frappe.whitelist()
def create_quotation(payload):
	"""Accept the M1+M2 form payload, create a draft Quotation shell row set.

	Native header: `quotation_to="Customer"` + `party_name` (Dynamic Link),
	not `customer` (oldfieldname, removed in v16). `customer_name` is
	hidden/read-only — server fetches it from Customer, never set here.
	Items need `uom` (reqd); báo giá chưa mã nên `item_code` để trống.
	No arithmetic here; rates come from the director's input verbatim.
	Prereq for `BG-` naming: add `BG-.YYYY.-` to `naming_series` options
	via Customize Form (Property Setter), then pass it in payload.
	"""
	payload = frappe.parse_json(payload) if isinstance(payload, str) else (payload or {})
	company = payload.get("company") or frappe.defaults.get_user_default("Company")
	if not company:
		frappe.throw("Thiếu Company mặc định — cấu hình Global Defaults trước.")
	customer_id = (payload.get("customer_id") or "").strip()
	if not customer_id:
		frappe.throw("Thiếu khách hàng — chọn Customer ở màn 1.")
	doc = frappe.get_doc(
		{
			"doctype": "Quotation",
			"naming_series": payload.get("naming_series") or "SAL-QTN-.YYYY.-",
			"quotation_to": "Customer",
			"party_name": customer_id,
			"company": company,
			"transaction_date": payload.get("transaction_date") or frappe.utils.today(),
			"order_type": "Sales",
			"items": [
				{
					"item_name": (row.get("item_name") or "")[:140],
					"qty": row.get("qty") or 0,
					"uom": row.get("uom") or "Cái",
					"conversion_factor": 1,
					"rate": row.get("rate") or 0,
				}
				for row in (payload.get("lines") or [])
			],
		}
	)
	doc.insert()
	artwork_url = (payload.get("artwork_url") or "").strip()
	if artwork_url.startswith("/files/"):
		file_name = frappe.db.get_value("File", {"file_url": artwork_url}, "name")
		if file_name:
			frappe.db.set_value(
				"File",
				file_name,
				{"attached_to_doctype": "Quotation", "attached_to_name": doc.name},
			)
	return {"name": doc.name}


@frappe.whitelist()
def get_price_preview(quotation=None, lines=None):
	"""Preview figures computed server-side from unsaved rows or a saved doc.

	Frontend sends current M2 `lines`; server sums here so the shell never
	computes. Packaging formula (GSM/keo/hao hụt/VAT) replaces the
	zero placeholders per packaging-calculation-spec.md.
	"""
	if isinstance(lines, str):
		lines = frappe.parse_json(lines) or []
	rows = lines or []
	if quotation and frappe.db.exists("Quotation", quotation):
		doc = frappe.get_doc("Quotation", quotation)
		return {
			"total_qty": doc.total_qty or 0,
			"subtotal": doc.total or 0,
			"cylinder_total": 0,
			"tax_amount": 0,
			"grand_total": doc.grand_total or 0,
		}
	total_qty = 0.0
	subtotal = 0.0
	for row in rows:
		try:
			qty = float(row.get("qty") or 0)
		except (TypeError, ValueError):
			qty = 0.0
		try:
			rate = float(row.get("rate") or 0)
		except (TypeError, ValueError):
			rate = 0.0
		total_qty += qty
		subtotal += qty * rate
	return {
		"total_qty": total_qty,
		"subtotal": subtotal,
		"cylinder_total": 0,
		"tax_amount": 0,
		"grand_total": subtotal,
	}

@frappe.whitelist()
def submit_quotation(name):
	"""Gửi QLSX: submit Draft → Open (native `on_submit`)."""
	doc = frappe.get_doc("Quotation", name)
	if doc.docstatus != 0:
		frappe.throw("Chỉ gửi QLSX từ phiếu nháp (Draft).")
	doc.submit()
	return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def mark_quotation_lost(name, reason=""):
	"""Rớt: native `declare_enquiry_lost` với lý do chi tiết."""
	doc = frappe.get_doc("Quotation", name)
	doc.declare_enquiry_lost([], [], (reason or "").strip() or None)
	doc.reload()
	return {"name": doc.name, "status": doc.status}

@frappe.whitelist()
def list_orders():
	return frappe.get_list(
		"Sales Order",
		fields=["name", "transaction_date", "customer", "grand_total", "status"],
		order_by="creation desc",
		limit=50,
	)


@frappe.whitelist()
def make_order_from_quotation(name, naming_series=None, delivery_date=None):
	"""Chốt: native `make_sales_order` Quotation(Open) → Sales Order(Draft).

	Prereq cho mã `DH-`: thêm `DH-.YYYY.-` vào `naming_series` của
	Sales Order qua Customize Form, rồi truyền `naming_series`.
	"""
	from erpnext.selling.doctype.quotation.quotation import make_sales_order

	doc = frappe.get_doc("Quotation", name)
	if doc.docstatus != 1 or doc.status not in ("Open", "Partially Ordered"):
		frappe.throw("Chỉ chốt từ báo giá đã duyệt (Open).")
	order = make_sales_order(name)
	if naming_series:
		order.naming_series = naming_series
	if not order.get("delivery_date"):
		order.delivery_date = delivery_date or frappe.utils.today()
	order.insert()
	return {"sales_order": order.name, "quotation": doc.name}

@frappe.whitelist()
def get_boot():
	"""Shell boot: CSRF token + user (static portal.html has no Jinja)."""
	return {
		"user": frappe.session.user,
		"csrf_token": frappe.sessions.get_csrf_token(),
		"company": frappe.defaults.get_user_default("Company"),
	}
