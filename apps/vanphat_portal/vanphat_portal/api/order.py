"""Dedicated Order Management & Sales Order Lifecycle APIs for Van Phat Portal.

Handles ERPNext Native Sales Order lifecycle:
- Listing with backend tab filtering (NGCS, Xưởng SX, Mua ngoài)
- Order detail extraction with cylinder vs product separation
- Server-side price & deposit preview (Zero client-side financial math)
- Order creation, deposit recording, accountant approval, and submission

Nguyên tắc tiền (ADR-002 + ADR-006 + AGENTS.md) — MỘT ngữ nghĩa duy nhất mọi màn:
- VAT/net/grand đọc số ERPNext đã tính (`net_total`/`total_taxes_and_charges`/`grand_total`).
  Không nhân hệ số VAT tay ở bất kỳ màn nào.
- Tiền trục = giá NCC pass-through (CHƯA VAT); tiền hàng = `net_total` native − tiền trục
  (chưa VAT, không trục); `qty` chỉ cộng dòng túi/cuộn (bỏ dòng trục).
- Bất biến: `product_total + cylinder_total + vat_amount = grand_total`.
- Chỉ còn 1 fallback được phép: % cọc 50% khi KH chưa có Payment Terms Template (có ghi log).
"""

import frappe

from vanphat_portal.api._common import (
	as_json,
	page_result,
	paginate,
	resolve_customer,
	text,
)
from vanphat_portal.api._guards import require_doc, require_roles

FALLBACK_DEPOSIT_PCT = 0.5
DEFAULT_ORDER_NAMING_SERIES = "DH-.YY..MM.-.###"


# --------------------------------------------------------------------------
# Phân loại dòng hàng — 1 chỗ duy nhất cho cả list lẫn drawer
# --------------------------------------------------------------------------


def _is_cylinder_line(item_code, item_name):
	"""Dòng trục in: mã chứa `TRUC-` hoặc tên chứa `trục`/`truc` (không phân biệt hoa thường)."""
	code = (item_code or "").upper()
	name = (item_name or "").lower()
	return "TRUC-" in code or "trục" in name or "truc" in name


def _order_tab(item_code, item_name):
	"""Tab buồng lái theo dòng hàng đầu (idx=1): ngcs | mua_ngoai | xuong_sx."""
	code = (item_code or "").upper()
	name = (item_name or "").lower()
	if "NGCS" in code or "ngcs" in name:
		return "ngcs"
	if "TMD" in code or "màng đơn" in name:
		return "mua_ngoai"
	return "xuong_sx"


def _order_product_group(tab):
	"""Nhãn nhóm hiển thị theo tab buồng lái."""
	return {"ngcs": "Túi NGCS", "mua_ngoai": "Túi màng đơn"}.get(tab, "Túi màng ghép")


def _item_product_group(item_code, item_name):
	"""Nhóm sản phẩm của MỘT dòng hàng không phải trục (drawer: 4 nhóm)."""
	code = (item_code or "").upper()
	name = (item_name or "").lower()
	if "NGCS" in code or "in sẵn" in name or "ngcs" in name:
		return "Túi NGCS"
	if "cuộn" in name or "màng ghép" in name:
		return "Cuộn màng ghép"
	if "màng đơn" in name or "hd" in code or "pe đơn" in name:
		return "Túi màng đơn"
	return "Túi màng ghép"


def _order_tab_of_group(product_group):
	return {
		"Túi NGCS": "ngcs",
		"Túi màng đơn": "mua_ngoai",
	}.get(product_group, "xuong_sx")


# --------------------------------------------------------------------------
# Payload & pass-through trục (ADR-002)
# --------------------------------------------------------------------------


def _cylinder_spec_state(spec):
	"""Chuẩn hóa `cylinder_spec` → {qty, unit_price, supplier, pending}.

	`pending` = có số cây nhưng chưa có giá NCC → tổng/cọc chưa chốt (truthful).
	"""
	spec = spec if isinstance(spec, dict) else {}
	qty = int(spec.get("qty") or spec.get("cylinder_count") or 0)
	price = frappe.utils.flt(spec.get("unit_price") or 0)
	return {
		"qty": qty,
		"unit_price": price,
		"supplier": text(spec.get("supplier")),
		"pending": qty > 0 and price <= 0,
	}


def _cylinder_item_name(qty, supplier):
	return f"Trục in ({qty} cây, NCC {supplier or '—'})"[:140]


# --------------------------------------------------------------------------
# Thuế / cọc native
# --------------------------------------------------------------------------


def _resolve_tax_template(company=None, customer=None):
	"""P1: Sales Taxes and Charges Template (Default theo Company → template mặc định)."""
	template = None
	try:
		if company and frappe.db.exists("Company", company):
			template = frappe.db.get_value(
				"Sales Taxes and Charges Template",
				{"company": company, "is_default": 1},
				"name",
			) or frappe.db.get_value("Sales Taxes and Charges Template", {"company": company}, "name")
		if not template:
			template = frappe.db.get_value("Sales Taxes and Charges Template", {"is_default": 1}, "name")
	except Exception:
		template = None
	return template


def _deposit_pct_from_template(template):
	"""% cọc từ dòng đầu Payment Terms Template. 0.0 = thiếu/không hợp lệ."""
	if not template:
		return 0.0
	try:
		rows = frappe.db.get_list(
			"Payment Terms Template Detail",
			filters={"parent": template},
			fields=["invoice_portion"],
			order_by="idx asc",
			page_length=1,
		)
	except Exception:
		return 0.0
	portion = frappe.utils.flt(rows[0].get("invoice_portion")) if rows else 0.0
	return portion / 100.0 if portion > 0 else 0.0


def _deposit_pct_map(customers):
	"""{customer: % cọc} cho nhiều KH bằng 2 query (chữa N+1 khi list đơn).

	ADR-002: KH chưa có template → 50% và GHI LOG, không im lặng.
	"""
	names = [name for name in dict.fromkeys(customers) if name]
	pcts = dict.fromkeys(names, FALLBACK_DEPOSIT_PCT)
	if not names:
		return pcts

	templates = {}
	try:
		rows = frappe.db.get_list(
			"Customer",
			filters={"name": ["in", names]},
			fields=["name", "payment_terms"],
			page_length=len(names),
		)
		templates = {row["name"]: row.get("payment_terms") for row in rows if row.get("payment_terms")}
	except Exception:
		templates = {}

	by_template = {}
	for name, template in templates.items():
		if template not in by_template:
			by_template[template] = _deposit_pct_from_template(template)
		if by_template[template] > 0:
			pcts[name] = by_template[template]

	missing = sorted(
		name for name in names if by_template.get(templates.get(name), 0.0) <= 0
	)
	if missing:
		frappe.logger("vanphat_portal").warning(
			"Dùng cọc mặc định 50%% cho KH thiếu Payment Terms Template: %s",
			", ".join(missing),
		)
	return pcts


def _get_deposit_pct(customer=None):
	"""% cọc của MỘT khách — chỉ có một đường tính duy nhất (bọc `_deposit_pct_map`)."""
	name = resolve_customer(customer)
	if not name:
		return FALLBACK_DEPOSIT_PCT
	return _deposit_pct_map([name])[name]


def _credit_limit(customer):
	"""Credit Limit native (>0 = Trả sau). Lỗi/thiếu → 0."""
	if not customer:
		return 0.0
	try:
		return frappe.utils.flt(
			frappe.db.get_value("Customer Credit Limit", {"parent": customer}, "credit_limit")
		)
	except Exception:
		return 0.0


def _credit_limit_map(customers):
	"""{customer: credit_limit} cho nhiều KH bằng 1 query (chữa N+1 khi list đơn)."""
	names = [name for name in dict.fromkeys(customers) if name]
	limits = dict.fromkeys(names, 0.0)
	if not names:
		return limits
	try:
		rows = frappe.db.get_list(
			"Customer Credit Limit",
			filters={"parent": ["in", names]},
			fields=["parent", "credit_limit"],
			page_length=len(names),
		)
		for row in rows or []:
			limits[row.get("parent")] = max(
				limits.get(row.get("parent"), 0.0),
				frappe.utils.flt(row.get("credit_limit")),
			)
	except Exception:
		pass
	return limits


# --------------------------------------------------------------------------
# Tính giá doc-driven (preview) — ERPNext tính, vỏ chỉ đọc
# --------------------------------------------------------------------------


def _price_via_doc(customer=None, company=None, items=None, cylinder_spec=None):
	"""Dựng Quotation nháp trong memory, gán tax template, để ERPNext tính.

	Không insert DB. Đọc total/total_taxes_and_charges/grand_total native.
	Dòng trục cộng pass-through từ `cylinder_spec` (giá NCC) — không lookup/không fallback.
	"""
	items_list = as_json(items) or []
	company = company or frappe.defaults.get_user_default("Company")
	cust_name = resolve_customer(customer)
	if not cust_name:
		frappe.throw("Thiếu khách hàng — chọn Customer trước khi đối soát giá.")
	if not company:
		frappe.throw("Thiếu Company — cấu hình Global Defaults trước.")

	so_items = []
	for row in items_list:
		qty = frappe.utils.flt(row.get("qty") or 0)
		if qty <= 0:
			continue
		so_items.append({
			"item_name": (row.get("item_name") or row.get("variant_name") or "Mặt hàng")[:140],
			"qty": qty,
			"uom": row.get("uom") or "Cái",
			"conversion_factor": 1,
			"rate": frappe.utils.flt(row.get("rate") or 0),
		})
	if not so_items:
		frappe.throw("Chưa có dòng hàng hợp lệ để đối soát giá.")

	cyl = _cylinder_spec_state(as_json(cylinder_spec))
	if cyl["qty"] > 0 and not cyl["pending"]:
		so_items.append({
			"item_name": _cylinder_item_name(cyl["qty"], cyl["supplier"]),
			"qty": cyl["qty"],
			"uom": "Cây",
			"conversion_factor": 1,
			"rate": cyl["unit_price"],
		})

	doc = frappe.get_doc({
		"doctype": "Quotation",
		"quotation_to": "Customer",
		"party_name": cust_name,
		"company": company,
		"transaction_date": frappe.utils.today(),
		"order_type": "Sales",
		"items": so_items,
	})
	template = _resolve_tax_template(company, cust_name)
	if template:
		try:
			doc.taxes_and_charges = template
			doc.set_missing_values()
		except Exception:
			pass
	try:
		doc.run_method("calculate_taxes_and_totals")
	except Exception:
		doc.run_method("calculate_totals")

	net_total = frappe.utils.flt(doc.total)
	tax_amount = frappe.utils.flt(doc.total_taxes_and_charges)
	return {
		"net_total": net_total,
		"vat_rate": round(tax_amount / net_total * 100.0, 1) if net_total else 0.0,
		"vat_amount": tax_amount,
		"tax_template": template,
		"grand_total": frappe.utils.flt(doc.grand_total) or (net_total + tax_amount),
		"cylinder_pending": cyl["pending"],
		"cylinder_supplier": cyl["supplier"] or None,
	}


@frappe.whitelist()
def get_price_preview(
	payload=None,
	items=None,
	customer=None,
	has_new_cylinders=False,
	cylinder_count=0,
	cylinder_spec=None,
	company=None,
):
	"""P1+P2 doc-driven + pass-through: VAT do ERPNext tính, trục theo giá NCC.

	Giữ params cũ (has_new_cylinders/cylinder_count) cho caller cũ: thiếu `cylinder_spec`
	mà có số cây → `cylinder_pending=True` (chờ giá NCC, totals null truthful).
	Enforces SSOT: Zero client-side math. Sếp chốt 2026-09-15: preview = read SO.
	"""
	require_doc("Sales Order", "read")
	data = as_json(payload) or {}
	items = items or data.get("items")
	customer = customer or data.get("customer")
	cylinder_spec = cylinder_spec or data.get("cylinder_spec")
	company = company or data.get("company")
	if "has_new_cylinders" in data:
		has_new_cylinders = data["has_new_cylinders"]
	if "cylinder_count" in data:
		cylinder_count = data["cylinder_count"]

	spec = as_json(cylinder_spec) or {}
	if has_new_cylinders and int(cylinder_count or 0) > 0 and not spec.get("qty"):
		spec = {**spec, "qty": int(cylinder_count)}

	priced = _price_via_doc(
		customer=customer, company=company, items=as_json(items) or [], cylinder_spec=spec
	)
	net_total = priced["net_total"]
	vat_amount = priced["vat_amount"]
	grand_total = priced["grand_total"]

	# Điều khoản thanh toán & hạn mức tín dụng (native)
	cust_name = resolve_customer(customer)
	credit_limit = _credit_limit(cust_name)
	payment_type = "Trả sau" if credit_limit > 0 else "Trả trước"
	deposit_pct = _get_deposit_pct(cust_name)

	# Tiền trục pass-through (chưa VAT); pending thì chưa chốt tổng
	cyl = _cylinder_spec_state(spec)
	cylinder_total = cyl["qty"] * cyl["unit_price"] if not cyl["pending"] else 0.0
	# ADR-006: MỘT ngữ nghĩa tiền mọi màn — tiền hàng = net native − tiền trục
	# (chưa VAT, không trục), khớp list_orders/get_order_details.
	product_total = max(0.0, net_total - cylinder_total)
	# Trả sau cọc 0đ; Trả trước = % Payment Terms trên tiền hàng + 100% tiền trục
	required_deposit = (
		0.0 if payment_type == "Trả sau" else round((product_total * deposit_pct) + cylinder_total)
	)

	return {
		"net_total": net_total,
		"vat_rate": priced["vat_rate"],
		"vat_amount": vat_amount,
		"tax_template": priced["tax_template"],
		"product_total": product_total,
		"cylinder_count": cyl["qty"],
		"cylinder_rate": cyl["unit_price"] or None,
		"cylinder_total": cylinder_total,
		"cylinder_pending": priced["cylinder_pending"],
		"cylinder_supplier": priced["cylinder_supplier"],
		"grand_total": grand_total,
		"grand_total_final": None if priced["cylinder_pending"] else grand_total,
		"payment_type": payment_type,
		"credit_limit": credit_limit,
		"required_deposit": required_deposit,
		"required_deposit_final": None if priced["cylinder_pending"] else required_deposit,
		"deposit_pct": round(deposit_pct * 100.0, 1),
	}


# --------------------------------------------------------------------------
# Đọc danh sách / chi tiết
# --------------------------------------------------------------------------


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


@frappe.whitelist()
def list_orders(tab=None, query=None, page=1, page_length=15):
	"""Danh sách Sales Order theo tab + tìm kiếm, phân trang server (spec §3).

	Bộ query CỐ ĐỊNH cho mọi trang (không N+1):
	1 count + 1 rows + 1 tab counts + 1 dòng hàng cả trang + 1 alias KH + 2 query cọc/KH.
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

	# Tiền/trạng thái: 1 query dòng hàng cả trang + 1 alias KH + 1 cọc + 1 hạn mức (thay N+1 cũ)
	lines = _order_lines_for([row.get("name") for row in page_rows])
	deposit_pcts = _deposit_pct_map([row.get("customer") for row in page_rows])
	credit_limits = _credit_limit_map([row.get("customer") for row in page_rows])
	alias_map = _customer_alias_map([row.get("customer") for row in page_rows])

	orders = []
	for row in page_rows:
		order = dict(row)
		grand_total = frappe.utils.flt(order.get("grand_total"))
		net_total = frappe.utils.flt(order.get("net_total"))
		vat_amount = frappe.utils.flt(order.get("total_taxes_and_charges"))
		advance_paid = frappe.utils.flt(order.get("advance_paid"))
		cylinder_total, product_qty = lines.get(order.get("name"), (0.0, 0.0))
		product_total = max(0.0, net_total - cylinder_total)
		cfg_pct = deposit_pcts.get(order.get("customer"), FALLBACK_DEPOSIT_PCT)
		credit_limit = credit_limits.get(order.get("customer"), 0.0)
		payment_type = "Trả sau" if credit_limit > 0 else "Trả trước"
		required_deposit = (
			0.0 if payment_type == "Trả sau" else round((product_total * cfg_pct) + cylinder_total)
		)

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

		# ADR-006: MỘT công thức HOLD cho list + drawer — Trả trước AND thiếu cọc.
		# Trả sau không bao giờ HOLD. Đơn đã duyệt giữ nguyên "Đã duyệt".
		is_hold = payment_type == "Trả trước" and 0 < advance_paid < required_deposit
		order["is_hold"] = is_hold
		if order.get("docstatus") == 1:
			order["order_status_label"] = "Đã duyệt"
			order["order_status_class"] = "status-ordered"
		elif is_hold:
			order["order_status_label"] = "HOLD"
			order["order_status_class"] = "status-hold"
		elif payment_type == "Trả sau" or advance_paid >= required_deposit:
			order["order_status_label"] = "Đã duyệt"
			order["order_status_class"] = "status-ordered"
		else:
			order["order_status_label"] = "Chờ cọc"
			order["order_status_class"] = "status-draft"

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
	required_deposit = round((product_total * _get_deposit_pct(doc.customer)) + cylinder_total)

	# Quy tắc Vàng: Trả sau cọc 0đ; Trả trước cọc theo Payment Terms + 100% tiền trục
	is_hold = False
	if payment_type == "Trả sau":
		can_submit = doc.docstatus == 0
		order_state = "Chính thức (Trả sau)" if doc.docstatus == 1 else "Chờ kích hoạt (Trả sau)"
	elif advance_paid >= required_deposit:
		can_submit = doc.docstatus == 0
		order_state = "Chính thức (Đã cọc >=50%)" if doc.docstatus == 1 else "Đủ cọc (Chờ kích hoạt)"
	elif advance_paid > 0:
		is_hold = True
		can_submit = False
		order_state = "HOLD (Thiếu cọc)"
	else:
		can_submit = False
		order_state = "Chờ cọc"

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


@frappe.whitelist()
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
# Ghi: cọc, duyệt ngoại lệ, submit, tạo đơn
# --------------------------------------------------------------------------


def _get_sales_order(name):
	if not frappe.db.exists("Sales Order", name):
		frappe.throw("Không tìm thấy đơn hàng " + str(name))
	return frappe.get_doc("Sales Order", name)


@frappe.whitelist()
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
		return {
			"name": doc.name,
			"auto_submitted": True,
			"order_state": "Chính thức (Đã cọc >=50%)",
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


@frappe.whitelist()
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


@frappe.whitelist()
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
			"Đơn hàng chưa đủ điều kiện (Cần cọc 50% tiền hàng + 100% tiền trục, "
			f"tổng cần: {life['required_deposit']:,.0f} đ)."
		)

	doc.submit()
	frappe.db.commit()
	return {"name": doc.name, "status": doc.status, "docstatus": doc.docstatus}


@frappe.whitelist()
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


@frappe.whitelist()
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
