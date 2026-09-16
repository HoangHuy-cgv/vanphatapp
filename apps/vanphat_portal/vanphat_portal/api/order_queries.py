"""Đọc danh sách / chi tiết Sales Order (tách từ order.py, Task 6b).

Không whitelist ở đây — wrapper giữ ở `order.py`.
"""

import frappe

from vanphat_portal.api._common import page_result, paginate, text
from vanphat_portal.api._guards import require_doc
from vanphat_portal.api.order_pricing import (
	_default_deposit_pct,
	_credit_limit,
	_credit_limit_map,
	_deposit_pct_map,
	_get_deposit_pct,
	_is_cylinder_line,
	_item_product_group,
	_order_product_group,
	_order_status,
	_order_tab,
	_order_tab_of_group,
	_required_deposit,
)


# Đọc danh sách / chi tiết
# --------------------------------------------------------------------------


def _get_sales_order(name):
	"""Load 1 Sales Order, thiếu → throw rõ mã (dùng chung queries + actions)."""
	if not frappe.db.exists("Sales Order", name):
		frappe.throw("Không tìm thấy đơn hàng " + str(name))
	return frappe.get_doc("Sales Order", name)


def _order_lines_for(order_names):
	"""1 query cho dòng hàng cả trang → {order: (cylinder_total_net, product_qty)}."""
	if not order_names:
		return {}
	SOI = frappe.qb.DocType("Sales Order Item")
	try:
		rows = (
			frappe.qb.from_(SOI)
			.select(SOI.parent, SOI.item_code, SOI.item_name, SOI.qty, SOI.amount)
			.where(SOI.parent.isin(order_names))
			.run(as_dict=True)
		)
	except Exception:
		return {}

	lines = {}
	for row in rows:
		cylinder_total, product_qty = lines.setdefault(row.get("parent"), (0.0, 0.0))
		if _is_cylinder_line(row.get("item_code"), row.get("item_name")):
			cylinder_total += frappe.utils.flt(row.get("amount"))
		else:
			product_qty += frappe.utils.flt(row.get("qty"))
		lines[row.get("parent")] = (cylinder_total, product_qty)
	return lines


def list_orders(tab=None, query=None, page=1, page_length=15):
	"""Danh sách Sales Order theo tab + tìm kiếm, phân trang server (spec §3).

	Bộ query CỐ ĐỊNH cho mọi trang (không N+1):
	1 count + 1 rows + 1 tab counts + 1 dòng hàng cả trang + 1 alias KH + 1 Single
	+ 2 query cọc/KH.
	Tab counts tính theo đúng từ khóa đang tìm (khớp danh sách), không phụ thuộc tab đang mở.
	Đường qb KHÔNG tự áp permission như get_list → cổng read ở đầu (Sếp chốt 2026-09-15;
	Sếp chọn "thấy hết công ty" nên chưa thêm User Permissions lọc theo owner).
	Alias KH đọc bằng 1 query `get_list` batch (native, tôn trọng permission) thay vì
	JOIN qb — pypika `Table.alias` là attr nội bộ nên `.field("alias")` nổ TypeError
	trên prod (bắt được khi đo p95 staging 2026-09-15).
	"""
	require_doc("Sales Order", "read")
	from frappe.query_builder import Order
	from frappe.query_builder.functions import Count

	SO = frappe.qb.DocType("Sales Order")
	SOI = frappe.qb.DocType("Sales Order Item")
	ITEM = frappe.qb.DocType("Item")

	tab_filter = text(tab).lower()
	q = text(query).lower()
	p, pl, start = paginate(page, page_length)
	like = f"%{q}%" if q else None

	# Tìm theo alias KH: resolve alias → mã KH trước (1 query native), rồi OR
	# vào điều kiện qb (thay JOIN CUST — pypika Table.alias nổ TypeError trên prod).
	alias_names: list = []
	if like:
		try:
			alias_hits = frappe.db.get_list(
				"Customer",
				filters={"alias": ["like", like]},
				fields=["name"],
				page_length=pl,
			)
			alias_names = [row.get("name") for row in alias_hits or [] if row.get("name")]
		except Exception:
			alias_names = []

	tab_where = None
	if tab_filter == "ngcs":
		tab_where = (SOI.item_code.like("NGCS%")) | (SOI.item_name.like("%ngcs%"))
	elif tab_filter == "mua_ngoai":
		tab_where = (SOI.item_code.like("TMD%")) | (SOI.item_name.like("%màng đơn%"))
	elif tab_filter == "xuong_sx":
		tab_where = (
			(SOI.item_code.not_like("NGCS%"))
			& (SOI.item_code.not_like("TMD%"))
			& (SOI.item_name.not_like("%ngcs%"))
			& (SOI.item_name.not_like("%màng đơn%"))
		)

	def base_query(include_tab=True):
		"""Cùng FROM/JOIN/WHERE cho rows, count và tab counts."""
		builder = (
			frappe.qb.from_(SO)
			.left_join(SOI)
			.on((SOI.parent == SO.name) & (SOI.idx == 1))
			.left_join(ITEM)
			.on(ITEM.name == SOI.item_code)
		)
		where = SO.docstatus != 2
		if like:
			search = (
				(SO.name.like(like))
				| (SO.customer_name.like(like))
				| (SO.customer.like(like))
				| (SOI.item_name.like(like))
				| (ITEM.custom_alias.like(like))
			)
			if alias_names:
				search = search | (SO.customer.isin(alias_names))
			where = where & search
		if include_tab and tab_where is not None:
			where = where & tab_where
		return builder.where(where)

	try:
		total_count = int(
			base_query().select(Count("*").as_("c")).run(as_dict=True)[0].get("c") or 0
		)
	except Exception:
		total_count = 0

	page_rows = []
	try:
		page_rows = (
			base_query()
			.select(
				SO.name,
				SO.transaction_date,
				SO.customer,
				SO.customer_name,
				SO.net_total,
				SO.total_taxes_and_charges,
				SO.grand_total,
				SO.advance_paid,
				SO.status,
				SO.docstatus,
				SOI.item_code,
				SOI.item_name,
				SOI.uom,
				ITEM.custom_alias,
			)
			.orderby(SO.creation, order=Order.desc)
			.limit(pl)
			.offset(start)
			.run(as_dict=True)
		)
	except Exception:
		page_rows = []

	tab_counts = {"xuong_sx": 0, "ngcs": 0, "mua_ngoai": 0, "all": 0}
	try:
		count_rows = (
			base_query(include_tab=False)
			.select(SOI.item_code, SOI.item_name, Count("*").as_("c"))
			.groupby(SOI.item_code, SOI.item_name)
			.run(as_dict=True)
		)
		for row in count_rows:
			count = int(row.get("c") or 0)
			tab_counts["all"] += count
			tab = _order_tab(row.get("item_code"), row.get("item_name"))
			if tab in tab_counts:
				tab_counts[tab] += count
	except Exception:
		pass

	# Tiền/trạng thái: 1 query dòng hàng cả trang + 1 alias KH + 1 Single + 2 query cọc/KH (thay N+1 cũ)
	lines = _order_lines_for([row.get("name") for row in page_rows])
	customers = [row.get("customer") for row in page_rows]
	default_pct = _default_deposit_pct() if any(customers) else None
	deposit_pcts = _deposit_pct_map(customers, default_pct)
	credit_limits = _credit_limit_map(customers)
	alias_map = _customer_alias_map(customers)

	orders = []
	for row in page_rows:
		order = dict(row)
		grand_total = frappe.utils.flt(order.get("grand_total"))
		net_total = frappe.utils.flt(order.get("net_total"))
		vat_amount = frappe.utils.flt(order.get("total_taxes_and_charges"))
		advance_paid = frappe.utils.flt(order.get("advance_paid"))
		cylinder_total, product_qty = lines.get(order.get("name"), (0.0, 0.0))
		product_total = max(0.0, net_total - cylinder_total)
		cfg_pct = deposit_pcts.get(order.get("customer"), default_pct)
		credit_limit = credit_limits.get(order.get("customer"), 0.0)
		payment_type = "Trả sau" if credit_limit > 0 else "Trả trước"
		required_deposit = _required_deposit(payment_type, product_total, cfg_pct, cylinder_total)

		order["advance_paid"] = advance_paid
		order["outstanding_amount"] = max(0.0, grand_total - advance_paid)
		order["deposit_pct"] = round(advance_paid / grand_total * 100, 1) if grand_total > 0 else 0
		order["cylinder_total"] = cylinder_total
		order["product_total"] = product_total
		order["vat_amount"] = vat_amount
		order["vat_rate"] = round(vat_amount / net_total * 100.0, 1) if net_total else 0.0
		order["required_deposit"] = required_deposit
		order["payment_type"] = payment_type
		order["credit_limit"] = credit_limit
		order["qty"] = product_qty

		# Alias KH từ batch map (không get_value từng dòng, không JOIN qb)
		order["customer_alias"] = (
			alias_map.get(order.get("customer")) or order.get("customer_name") or order.get("customer")
		)
		order["item_name"] = order.get("item_name") or "—"
		order["uom"] = order.get("uom") or "Túi"
		order["custom_alias"] = order.get("custom_alias") or order.get("item_name") or "—"

		tab = _order_tab(order.get("item_code"), order.get("item_name"))
		order["order_tab"] = tab
		order["product_group"] = _order_product_group(tab)

		# ADR-006: MỘT model trạng thái cho list + drawer — Trả trước AND thiếu cọc.
		# Trả sau không bao giờ HOLD. Đơn đã duyệt giữ nguyên "Đã duyệt".
		st = _order_status(
			order.get("docstatus"), payment_type, advance_paid, required_deposit
		)
		order["is_hold"] = st["is_hold"]
		order["order_status_label"] = st["label"]
		order["order_status_class"] = st["css_class"]

		orders.append(order)

	result = page_result("orders", orders, p, pl, total_count)
	result["tab_counts"] = tab_counts
	return result


def _order_lifecycle(doc):
	"""Trạng thái nghiệp vụ + tiền của MỘT Sales Order, chỉ đọc số native.

	Dùng chung cho drawer và các mutation (cọc/submit) — không đọc lại doc nặng.
	"""
	cylinder_total = 0.0
	product_qty = 0.0
	for row in doc.items or []:
		if _is_cylinder_line(row.item_code, row.item_name):
			cylinder_total += frappe.utils.flt(row.amount)
		else:
			product_qty += frappe.utils.flt(row.qty)

	net_total = frappe.utils.flt(doc.net_total)
	vat_amount = frappe.utils.flt(doc.total_taxes_and_charges)
	grand_total = frappe.utils.flt(doc.grand_total) or (net_total + vat_amount)
	product_total = max(0.0, net_total - cylinder_total)
	advance_paid = frappe.utils.flt(doc.advance_paid)
	credit_limit = _credit_limit(doc.customer)
	payment_type = "Trả sau" if credit_limit > 0 else "Trả trước"
	required_deposit = _required_deposit(
		payment_type, product_total, _get_deposit_pct(doc.customer), cylinder_total
	)

	# Cùng 1 model trạng thái với list (Trả sau không bao giờ HOLD).
	st = _order_status(doc.docstatus, payment_type, advance_paid, required_deposit)
	order_state, is_hold, can_submit = st["state"], st["is_hold"], st["can_submit"]

	return {
		"net_total": net_total,
		"vat_amount": vat_amount,
		"vat_rate": round(vat_amount / net_total * 100.0, 1) if net_total else 0.0,
		"grand_total": grand_total,
		"product_total": product_total,
		"cylinder_total": cylinder_total,
		"product_qty": product_qty,
		"advance_paid": advance_paid,
		"outstanding_amount": max(0.0, grand_total - advance_paid),
		"deposit_pct": round(advance_paid / grand_total * 100, 1) if grand_total > 0 else 0,
		"required_deposit": required_deposit,
		"payment_type": payment_type,
		"credit_limit": credit_limit,
		"order_state": order_state,
		"is_hold": is_hold,
		"can_submit": can_submit,
	}


def _customer_alias(customer):
	"""Alias native của KH cho buồng lái. Lỗi/thiếu → None."""
	if not customer:
		return None
	try:
		return frappe.db.get_value("Customer", customer, "alias")
	except Exception:
		return None


def _customer_alias_map(customers):
	"""{customer: alias} cho cả trang bằng 1 query (chữa N+1, tôn trọng permission)."""
	names = [name for name in dict.fromkeys(customers) if name]
	if not names:
		return {}
	try:
		rows = frappe.db.get_list(
			"Customer",
			filters={"name": ["in", names]},
			fields=["name", "alias"],
			page_length=len(names),
		)
	except Exception:
		return {}
	return {row.get("name"): row.get("alias") for row in rows or []}


def _first_item_fields(item_code):
	"""brand + lớp cấu trúc + mô tả của mã hàng đầu đơn — 1 query, lỗi → {}."""
	if not item_code:
		return {}
	try:
		return (
			frappe.db.get_value(
				"Item",
				item_code,
				["brand", "custom_structure_layers", "description"],
				as_dict=True,
			)
			or {}
		)
	except Exception:
		return {}


def get_order_details(name):
	"""Return comprehensive single Sales Order details for the inspection drawer."""
	require_doc("Sales Order", "read", name=name)
	doc = _get_sales_order(name)
	life = _order_lifecycle(doc)

	customer_alias = _customer_alias(doc.customer)
	item_fields = _first_item_fields(doc.items[0].item_code if doc.items else "")
	layers_raw = item_fields.get("custom_structure_layers") or ""

	items = []
	product_group = "Túi màng ghép"
	for row in doc.items or []:
		is_cylinder = _is_cylinder_line(row.item_code, row.item_name)
		if not is_cylinder:
			product_group = _item_product_group(row.item_code, row.item_name)
		items.append({
			"item_code": row.item_code,
			"item_name": row.item_name,
			"qty": row.qty,
			"rate": row.rate,
			"amount": row.amount,
			"uom": row.uom,
			"is_cylinder": is_cylinder,
		})

	return {
		"name": doc.name,
		"transaction_date": str(doc.transaction_date),
		"customer": doc.customer,
		"customer_name": doc.customer_name,
		"customer_alias": customer_alias or doc.customer_name,
		"brand": item_fields.get("brand") or "VẠN PHÁT",
		"payment_type": life["payment_type"],
		"product_group": product_group,
		"order_tab": _order_tab_of_group(product_group),
		"materials": [part.strip() for part in layers_raw.split("/") if part.strip()],
		"dimensions_text": item_fields.get("description") or "",
		"uom": doc.items[0].uom if doc.items else "Túi",
		"qty": life["product_qty"],
		"grand_total": life["grand_total"],
		"net_total": life["net_total"],
		"vat_rate": life["vat_rate"],
		"vat_amount": life["vat_amount"],
		"product_total": life["product_total"],
		"cylinder_total": life["cylinder_total"],
		"advance_paid": life["advance_paid"],
		"outstanding_amount": life["outstanding_amount"],
		"required_deposit": life["required_deposit"],
		"deposit_pct": life["deposit_pct"],
		"order_state": life["order_state"],
		"is_hold": life["is_hold"],
		"can_submit": life["can_submit"],
		"status": doc.status,
		"docstatus": doc.docstatus,
		"credit_limit": life["credit_limit"],
		"items": items,
	}


# --------------------------------------------------------------------------
