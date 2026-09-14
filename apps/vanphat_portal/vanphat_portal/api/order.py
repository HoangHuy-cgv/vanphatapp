"""Dedicated Order Management & Sales Order Lifecycle APIs for Van Phat Portal.

Handles ERPNext Native Sales Order lifecycle:
- Listing with backend tab filtering (NGCS, Xưởng SX, Mua ngoài)
- Order detail extraction with cylinder vs product separation
- Server-side price & deposit preview (Zero client-side financial math)
- Order creation, deposit recording, accountant approval, and submission
"""

import frappe

# S9: fallback khi native chưa cấu hình (chi tiết xem docs/decisions/ADR-002-native-pricing-fallback.md).
# P1+P2 (goal mới, Sếp duyệt): VAT doc-driven — ERPNext tính trên draft doc, không math tay;
# giá trục pass-through NCC — API không lookup/không fallback số nào (Sếp: trục do NCC quyết giá).
FALLBACK_VAT_RATE = 8.0
FALLBACK_DEPOSIT_PCT = 0.5


def _resolve_tax_template(company=None, customer=None):
	"""P1: resolve Sales Taxes and Charges Template (Default theo Company → Tax Rule theo KH)."""
	template = None
	try:
		if company and frappe.db.exists("Company", company):
			template = frappe.db.get_value(
				"Sales Taxes and Charges Template",
				{"company": company, "is_default": 1},
				"name",
			) or frappe.db.get_value(
				"Sales Taxes and Charges Template", {"company": company}, "name"
			)
		if not template:
			template = frappe.db.get_value(
				"Sales Taxes and Charges Template", {"is_default": 1}, "name"
			)
	except Exception:
		template = None
	return template


def _get_vat_rate(company=None):
	"""GIỮ cho list/detail đọc nhanh (không dựng doc). Preview chính dùng _price_via_doc (P1 doc-driven)."""
	template = _resolve_tax_template(company)
	if template:
		try:
			rows = frappe.db.get_list(
				"Sales Taxes and Charges",
				filters={"parent": template},
				fields=["rate"],
				page_length=10,
			)
			for r in rows:
				rate = frappe.utils.flt(r.get("rate"))
				if rate > 0:
					return rate
		except Exception:
			pass
	return FALLBACK_VAT_RATE


def _resolve_customer_name(customer):
	"""Chuẩn hóa customer id/alias/name → name native."""
	if not customer:
		return None
	try:
		if frappe.db.exists("Customer", customer):
			return customer
		return frappe.db.get_value("Customer", {"alias": customer}, "name") or frappe.db.get_value(
			"Customer", {"customer_name": customer}, "name"
		)
	except Exception:
		return None


def _price_via_doc(customer=None, company=None, items=None, cylinder_spec=None):
	"""P1 doc-driven: dựng Quotation nháp trong memory, gán tax template, để ERPNext tính.

	Không insert DB. Đọc total/total_taxes_and_charges/grand_total do native tính.
	P2: dòng trục cộng pass-through từ cylinder_spec (giá NCC) — không lookup/không fallback.
	"""
	items_list = items or []
	if isinstance(items_list, str):
		items_list = frappe.parse_json(items_list) or []
	spec = cylinder_spec or {}
	if isinstance(spec, str):
		spec = frappe.parse_json(spec) or {}

	company = company or frappe.defaults.get_user_default("Company")
	cust_name = _resolve_customer_name(customer)
	if not cust_name:
		frappe.throw("Thiếu khách hàng — chọn Customer trước khi đối soát giá.")
	if not company:
		frappe.throw("Thiếu Company — cấu hình Global Defaults trước.")

	so_items = []
	for it in items_list:
		qty = frappe.utils.flt(it.get("qty") or 0)
		rate = frappe.utils.flt(it.get("rate") or 0)
		if qty <= 0:
			continue
		so_items.append({
			"item_name": (it.get("item_name") or it.get("variant_name") or "Mặt hàng")[:140],
			"qty": qty,
			"uom": it.get("uom") or "Cái",
			"conversion_factor": 1,
			"rate": rate,
		})
	if not so_items:
		frappe.throw("Chưa có dòng hàng hợp lệ để đối soát giá.")

	# P2 pass-through: giá trục do NCC quyết — Vạn Phát chỉ mua đi bán lại, không chốt số nào.
	cyl_qty = int(spec.get("qty") or spec.get("cylinder_count") or 0)
	cyl_price = spec.get("unit_price")
	cyl_supplier = (spec.get("supplier") or "").strip()
	cylinder_pending = bool(cyl_qty > 0) and not (cyl_price and frappe.utils.flt(cyl_price) > 0)
	if cyl_qty > 0 and not cylinder_pending:
		so_items.append({
			"item_name": f"Trục in ({cyl_qty} cây, NCC {cyl_supplier or '—'})"[:140],
			"qty": cyl_qty,
			"uom": "Cây",
			"conversion_factor": 1,
			"rate": frappe.utils.flt(cyl_price),
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
	grand = frappe.utils.flt(doc.grand_total) or (net_total + tax_amount)
	vat_rate = round(tax_amount / net_total * 100.0, 1) if net_total else 0.0
	return {
		"net_total": net_total,
		"vat_rate": vat_rate,
		"vat_amount": tax_amount,
		"tax_template": template,
		"grand_total": grand,
		"cylinder_pending": cylinder_pending,
		"cylinder_supplier": cyl_supplier or None,
	}


def _get_deposit_pct(customer=None):
	"""S9: % cọc từ Payment Terms Template của Customer; thiếu → fallback 50%.

	Credit Limit > 0 (Trả sau) do caller quyết cọc 0đ — hàm này chỉ trả % cho trả trước.
	"""
	try:
		if customer:
			name = customer if frappe.db.exists("Customer", customer) else frappe.db.get_value(
				"Customer", {"alias": customer}, "name"
			) or frappe.db.get_value("Customer", {"customer_name": customer}, "name")
			if name:
				template = frappe.db.get_value("Customer", name, "payment_terms")
				if template:
					terms = frappe.db.get_list(
						"Payment Terms Template Detail",
						filters={"parent": template},
						fields=["invoice_portion"],
						order_by="idx asc",
						page_length=1,
					)
					if terms and frappe.utils.flt(terms[0].get("invoice_portion")) > 0:
						return frappe.utils.flt(terms[0].get("invoice_portion")) / 100.0
	except Exception:
		pass
	return FALLBACK_DEPOSIT_PCT


@frappe.whitelist()
def get_price_preview(payload=None, items=None, customer=None, has_new_cylinders=False, cylinder_count=0,
		cylinder_spec=None, company=None):
	"""P1+P2 doc-driven + pass-through (Sếp duyệt, thay math tay S9).

	- VAT: ERPNext tính trên Quotation nháp (_price_via_doc), không round(net*rate) tay.
	- Trục: cylinder_spec {qty, unit_price, supplier} — giá NCC quyết, không lookup/không fallback số.
	- Giữ params cũ (has_new_cylinders/cylinder_count) để tương thích caller cũ: khi thiếu
	  cylinder_spec mà có has_new_cylinders → cylinder_pending=True (truthful chờ giá NCC).
	Enforces SSOT: Zero client-side math.
	"""
	data = frappe.parse_json(payload) if isinstance(payload, str) else (payload or {})
	if not items and data.get("items"):
		items = data.get("items")
	if not customer and data.get("customer"):
		customer = data.get("customer")
	if not cylinder_spec and data.get("cylinder_spec"):
		cylinder_spec = data.get("cylinder_spec")
	if not company and data.get("company"):
		company = data.get("company")
	if "has_new_cylinders" in data:
		has_new_cylinders = data.get("has_new_cylinders")
	if "cylinder_count" in data:
		cylinder_count = data.get("cylinder_count")

	items_list = items or []
	if isinstance(items_list, str):
		items_list = frappe.parse_json(items_list) or []
	spec = cylinder_spec or {}
	if isinstance(spec, str):
		spec = frappe.parse_json(spec) or {}
	if has_new_cylinders and int(cylinder_count or 0) > 0 and not spec.get("qty"):
		spec = {**spec, "qty": int(cylinder_count)}

	priced = _price_via_doc(customer=customer, company=company, items=items_list, cylinder_spec=spec)
	net_total = priced["net_total"]
	vat_rate = priced["vat_rate"]
	vat_amount = priced["vat_amount"]
	product_total = net_total + vat_amount
	grand_total = priced["grand_total"]

	# 5. Xác định điều khoản thanh toán & hạn mức tín dụng khách hàng
	payment_type = "Trả trước"
	credit_limit = 0.0
	cust_name = _resolve_customer_name(customer)
	if cust_name:
		try:
			credit_limit = frappe.db.get_value("Customer Credit Limit", {"parent": cust_name}, "credit_limit") or 0.0
			if credit_limit > 0:
				payment_type = "Trả sau"
		except Exception:
			credit_limit = 0.0
	deposit_pct = _get_deposit_pct(cust_name)

	# P2: tiền trục pass-through — pending (chờ giá NCC) thì total chưa chốt, báo truthful
	cyl_qty = int(spec.get("qty") or spec.get("cylinder_count") or 0)
	cyl_price = frappe.utils.flt(spec.get("unit_price") or 0)
	cylinder_total = (cyl_qty * cyl_price) if (cyl_qty > 0 and cyl_price > 0) else 0.0

	# 6. Quy tắc Vàng: Trả sau cọc 0đ; Trả trước cọc theo Payment Terms + 100% tiền trục (đã có giá NCC)
	if payment_type == "Trả sau":
		required_deposit = 0.0
	else:
		required_deposit = round((product_total * deposit_pct) + cylinder_total)

	return {
		"net_total": net_total,
		"vat_rate": vat_rate,
		"vat_amount": vat_amount,
		"tax_template": priced["tax_template"],
		"product_total": product_total,
		"cylinder_count": cyl_qty,
		"cylinder_rate": cyl_price or None,
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


@frappe.whitelist()
def list_orders(tab=None, query=None, page=1, page_length=15):
	"""Return Sales Orders filtered by Cockpit Tab and search query with server pagination.

	S2: 1 query `frappe.qb` join SO + SO Item (idx=1) + Customer alias + Item custom_alias.
	Server paginate bằng limit/offset (trần page_length 100); tab/search lọc trong SQL.
	Tab phân loại từ item_code native (NGCS/TMD) — S9 chuyển Item Group filter server.
	"""
	import math

	from pypika import Order
	tab_filter = (tab or "").strip().lower()
	q = (query or "").strip().lower()
	p = max(1, int(page or 1))
	pl = min(100, max(1, int(page_length or 15)))

	SO = frappe.qb.DocType("Sales Order")
	SOI = frappe.qb.DocType("Sales Order Item")
	CUST = frappe.qb.DocType("Customer")
	ITEM = frappe.qb.DocType("Item")
	# pypika Table.alias là None (trùng tên attr nội bộ) → dùng .field("alias")
	CUST_ALIAS = CUST.field("alias")

	def tab_of(code, iname):
		c = (code or "").upper()
		n = (iname or "").lower()
		if "NGCS" in c or "ngcs" in n:
			return "ngcs"
		if "TMD" in c or "màng đơn" in n:
			return "mua_ngoai"
		return "xuong_sx"

	base_cond = (SO.docstatus != 2)
	if q:
		like = f"%{q}%"
		base_cond = base_cond & (
			(SO.name.like(like)) | (SO.customer_name.like(like)) | (SO.customer.like(like))
			| (CUST_ALIAS.like(like)) | (SOI.item_name.like(like)) | (ITEM.custom_alias.like(like))
		)
	if tab_filter == "ngcs":
		base_cond = base_cond & ((SOI.item_code.like("NGCS%")) | (SOI.item_name.like("%ngcs%")))
	elif tab_filter == "mua_ngoai":
		base_cond = base_cond & ((SOI.item_code.like("TMD%")) | (SOI.item_name.like("%màng đơn%")))
	elif tab_filter == "xuong_sx":
		base_cond = base_cond & (
			(SOI.item_code.not_like("NGCS%")) & (SOI.item_code.not_like("TMD%"))
			& (SOI.item_name.not_like("%ngcs%")) & (SOI.item_name.not_like("%màng đơn%"))
		)

	def row_query():
		return (
			frappe.qb.from_(SO)
			.left_join(SOI)
			.on((SOI.parent == SO.name) & (SOI.idx == 1))
			.left_join(CUST)
			.on(CUST.name == SO.customer)
			.left_join(ITEM)
			.on(ITEM.name == SOI.item_code)
			.select(
				SO.name,
				SO.transaction_date,
				SO.customer,
				SO.customer_name,
				SO.grand_total,
				SO.advance_paid,
				SO.status,
				SO.docstatus,
				CUST_ALIAS.as_("customer_alias"),
				SOI.item_code,
				SOI.item_name,
				SOI.qty,
				SOI.uom,
				ITEM.custom_alias,
			)
			.where(base_cond)
		)

	from frappe.query_builder.functions import Count

	# Query đếm/tổng: build riêng từ cùng FROM/JOIN/WHERE (không reuse select list)
	def count_query():
		return (
			frappe.qb.from_(SO)
			.left_join(SOI)
			.on((SOI.parent == SO.name) & (SOI.idx == 1))
			.left_join(CUST)
			.on(CUST.name == SO.customer)
			.left_join(ITEM)
			.on(ITEM.name == SOI.item_code)
			.select(Count("*").as_("c"))
			.where(base_cond)
		)

	try:
		total_count = count_query().run(as_dict=True)[0].get("c", 0) or 0
	except Exception:
		total_count = 0

	start = (p - 1) * pl
	page_rows = []
	try:
		page_rows = (row_query().orderby(SO.creation, order=Order.desc).limit(pl).offset(start)).run(as_dict=True)
	except Exception:
		page_rows = []

	# Tab counts: 1 query group theo item_code/item_name (không N+1)
	count_q = (
		frappe.qb.from_(SO)
		.left_join(SOI)
		.on((SOI.parent == SO.name) & (SOI.idx == 1))
		.select(SOI.item_code, SOI.item_name, Count("*").as_("c"))
		.where((SO.docstatus != 2) & ((SO.name.like(f"%{q}%")) if q else (SO.docstatus != 2)))
		.groupby(SOI.item_code, SOI.item_name)
	)
	tab_counts = {"xuong_sx": 0, "ngcs": 0, "mua_ngoai": 0, "all": 0}
	try:
		for crow in count_q.run(as_dict=True):
			t = tab_of(crow.get("item_code"), crow.get("item_name"))
			n = int(crow.get("c") or 0)
			tab_counts["all"] += n
			if t in tab_counts:
				tab_counts[t] += n
	except Exception:
		pass

	# S9: lookup native 1 lần cho cả trang (VAT theo Company) + cache % cọc theo KH
	_page_company = frappe.defaults.get_user_default("Company")
	vat_rate = _get_vat_rate(_page_company)
	vat_factor = 1 + vat_rate / 100.0
	_deposit_pct_cache = {}

	processed_orders = []
	for r in page_rows:
		o = dict(r)
		gt = frappe.utils.flt(o.get("grand_total"))
		adv = frappe.utils.flt(o.get("advance_paid"))
		o["advance_paid"] = adv
		o["outstanding_amount"] = max(0.0, gt - adv)
		o["deposit_pct"] = round((adv / gt * 100), 1) if gt > 0 else 0
		# S1 giữ: cọc = 50% tiền hàng + 100% trục TRUC- (1 query qb/đơn: rows + SUM Python)
		try:
			agg_q = (
				frappe.qb.from_(SOI)
				.select(SOI.item_code, SOI.item_name, SOI.amount, SOI.qty)
				.where(SOI.parent == o.get("name"))
			)
			agg_rows = agg_q.run(as_dict=True)
		except Exception:
			agg_rows = []
		# S9: VAT/cọc native (lookup 1 lần/ngoài vòng lặp, fallback ADR-002)
		cyl_total = 0.0
		total_qty = 0.0
		for _it in agg_rows:
			total_qty += frappe.utils.flt(_it.get("qty") or 0)
			_code = (_it.get("item_code") or "").upper()
			_iname = (_it.get("item_name") or "").lower()
			if "TRUC-" in _code or "trục" in _iname:
				cyl_total += frappe.utils.flt(_it.get("amount")) * vat_factor
		if not total_qty:
			total_qty = frappe.utils.flt(o.get("qty")) or 0
		product_total = max(0.0, gt - cyl_total)
		o["cylinder_total"] = cyl_total
		o["product_total"] = product_total
		o["vat_rate"] = vat_rate
		_cust = o.get("customer")
		if _cust not in _deposit_pct_cache:
			_deposit_pct_cache[_cust] = _get_deposit_pct(_cust)
		o["required_deposit"] = round((product_total * _deposit_pct_cache[_cust]) + cyl_total)

		# Alias + mặt hàng đầu từ JOIN (không get_value từng dòng)
		o["customer_alias"] = o.get("customer_alias") or o.get("customer_name") or o.get("customer")
		o["item_code"] = o.get("item_code")
		o["item_name"] = o.get("item_name") or "—"
		o["qty"] = total_qty
		o["uom"] = o.get("uom") or "Túi"
		o["custom_alias"] = o.get("custom_alias") or o.get("item_name") or "—"

		# Phân loại tab buồng lái (cùng hàm tab_of với count SQL)
		t = tab_of(o.get("item_code"), o.get("item_name"))
		o["order_tab"] = t
		o["product_group"] = "Túi NGCS" if t == "ngcs" else ("Túi màng đơn" if t == "mua_ngoai" else "Túi màng ghép")

		# Trạng thái buồng lái tính toán chuẩn mực tại backend ERPNext
		if o.get("is_hold") or "HOLD" in (o.get("order_state") or ""):
			o["order_status_label"] = "HOLD"
			o["order_status_class"] = "status-hold"
		elif o.get("docstatus") == 1:
			o["order_status_label"] = "Đã duyệt"
			o["order_status_class"] = "status-ordered"
		elif adv > 0 and adv < (gt * 0.5):
			o["order_status_label"] = "HOLD"
			o["order_status_class"] = "status-hold"
		elif adv >= (gt * 0.5):
			o["order_status_label"] = "Đã duyệt"
			o["order_status_class"] = "status-ordered"
		else:
			o["order_status_label"] = "Chờ cọc"
			o["order_status_class"] = "status-draft"

		# Lọc Python đã thay bằng WHERE SQL ở trên — giữ đoạn này làm guard hiếm (join null)
		processed_orders.append(o)

	total_pages = max(1, math.ceil(total_count / pl)) if total_count else 1

	return {
		"orders": processed_orders,
		"page": p,
		"page_length": pl,
		"total_count": total_count,
		"total_pages": total_pages,
		"tab_counts": tab_counts,
	}


@frappe.whitelist()
def get_order_details(name):
	"""Return comprehensive single Sales Order details for the inspection drawer."""
	if not frappe.db.exists("Sales Order", name):
		frappe.throw("Không tìm thấy đơn hàng " + str(name))
	doc = frappe.get_doc("Sales Order", name)
	credit_limit = 0.0
	try:
		credit_limit = frappe.db.get_value("Customer Credit Limit", {"parent": doc.customer}, "credit_limit") or 0.0
	except Exception:
		credit_limit = 0.0
	payment_type = "Trả sau" if credit_limit > 0 else "Trả trước"

	advance_paid = frappe.utils.flt(doc.advance_paid)
	grand_total = frappe.utils.flt(doc.grand_total)
	outstanding_amount = max(0.0, grand_total - advance_paid)

	# Bóc tách tiền trục in (TRUC-) và tiền hàng (túi/cuộn màng) — S9: hệ số VAT native
	vat_rate = _get_vat_rate(doc.company)
	vat_factor = 1 + vat_rate / 100.0
	cylinder_total = 0.0
	product_total = 0.0
	items = []
	product_group = "Túi màng ghép"

	for it in doc.items:
		code = (it.item_code or "").upper()
		it_name = it.item_name or ""
		amt = frappe.utils.flt(it.amount)
		is_cyl = "TRUC-" in code or "trục" in it_name.lower() or "truc" in it_name.lower()

		if is_cyl:
			cylinder_total += amt * vat_factor
		else:
			product_total += amt * vat_factor
			if "NGCS" in code or "in sẵn" in it_name.lower() or "ngcs" in it_name.lower():
				product_group = "Túi NGCS"
			elif "cuộn" in it_name.lower() or "màng ghép" in it_name.lower():
				product_group = "Cuộn màng ghép"
			elif "màng đơn" in it_name.lower() or "hd" in code or "pe đơn" in it_name.lower():
				product_group = "Túi màng đơn"
			else:
				product_group = "Túi màng ghép"

		items.append({
			"item_code": it.item_code,
			"item_name": it.item_name,
			"qty": it.qty,
			"rate": it.rate,
			"amount": it.amount,
			"uom": it.uom,
			"is_cylinder": is_cyl,
		})

	# Quy tắc Vàng: cọc theo Payment Terms + 100% TIỀN TRỤC (P1 doc-driven: đọc số native đã tính)
	deposit_pct_cfg = _get_deposit_pct(doc.customer)
	net_total = frappe.utils.flt(doc.net_total) or max(0.0, grand_total - frappe.utils.flt(doc.total_taxes_and_charges))
	vat_amount = frappe.utils.flt(doc.total_taxes_and_charges)
	required_deposit = round((product_total * deposit_pct_cfg) + cylinder_total)
	deposit_pct = round((advance_paid / grand_total * 100), 1) if grand_total > 0 else 0

	# Trạng thái nghiệp vụ
	is_hold = False
	can_submit = False

	if payment_type == "Trả sau":
		can_submit = (doc.docstatus == 0)
		order_state = "Chính thức (Trả sau)" if doc.docstatus == 1 else "Chờ kích hoạt (Trả sau)"
	else:
		if advance_paid >= required_deposit:
			can_submit = (doc.docstatus == 0)
			order_state = "Chính thức (Đã cọc >=50%)" if doc.docstatus == 1 else "Đủ cọc (Chờ kích hoạt)"
		elif advance_paid > 0:
			is_hold = True
			can_submit = False
			order_state = "HOLD (Thiếu cọc)"
		else:
			can_submit = False
			order_state = "Chờ cọc"

	cust_alias = ""
	try:
		cust_alias = frappe.db.get_value("Customer", doc.customer, "alias")
	except Exception:
		pass

	first_code = doc.items[0].item_code if doc.items else ""
	brand = ""
	materials = []
	dimensions_text = ""
	if first_code:
		try:
			brand = frappe.db.get_value("Item", first_code, "brand") or ""
			layers_raw = frappe.db.get_value("Item", first_code, "custom_structure_layers") or ""
			if layers_raw:
				materials = [s.strip() for s in layers_raw.split("/") if s.strip()]
			dimensions_text = frappe.db.get_value("Item", first_code, "description") or ""
		except Exception:
			pass

	order_tab = "ngcs" if product_group == "Túi NGCS" else ("mua_ngoai" if product_group == "Túi màng đơn" else "xuong_sx")

	return {
		"name": doc.name,
		"transaction_date": str(doc.transaction_date),
		"customer": doc.customer,
		"customer_name": doc.customer_name,
		"customer_alias": cust_alias or doc.customer_name,
		"brand": brand or "VẠN PHÁT",
		"payment_type": payment_type,
		"product_group": product_group,
		"order_tab": order_tab,
		"materials": materials,
		"dimensions_text": dimensions_text,
		"uom": doc.items[0].uom if doc.items else "Túi",
		"qty": sum(frappe.utils.flt(it.qty) for it in doc.items if not getattr(it, "is_cylinder", False)),
		"grand_total": grand_total,
		"net_total": net_total,
		"vat_rate": vat_rate,
		"vat_amount": vat_amount,
		"product_total": product_total,
		"cylinder_total": cylinder_total,
		"advance_paid": advance_paid,
		"outstanding_amount": outstanding_amount,
		"required_deposit": required_deposit,
		"deposit_pct": deposit_pct,
		"order_state": order_state,
		"is_hold": is_hold,
		"can_submit": can_submit,
		"status": doc.status,
		"docstatus": doc.docstatus,
		"credit_limit": credit_limit,
		"items": items,
	}


@frappe.whitelist()
def record_order_deposit(name, amount=0, note=""):
	"""Record customer advance payment against a Sales Order."""
	if not frappe.db.exists("Sales Order", name):
		frappe.throw("Không tìm thấy đơn hàng " + str(name))
	doc = frappe.get_doc("Sales Order", name)
	if doc.docstatus == 2:
		frappe.throw("Đơn hàng đã bị hủy, không thể ghi nhận cọc.")

	amt = frappe.utils.flt(amount)
	if amt <= 0:
		frappe.throw("Số tiền cọc phải lớn hơn 0.")

	new_advance = frappe.utils.flt(doc.advance_paid) + amt
	doc.db_set("advance_paid", new_advance)
	doc.add_comment("Comment", text=f"Ghi nhận cọc: {amt:,.0f} đ. Tổng đã cọc: {new_advance:,.0f} đ. Ghi chú: {note}")
	doc.reload()

	details = get_order_details(name)
	if details["can_submit"]:
		doc.submit()
		return {"name": doc.name, "auto_submitted": True, "order_state": "Chính thức (Đã cọc >=50%)", "success": True}

	return {
		"name": doc.name,
		"advance_paid": doc.advance_paid,
		"outstanding_amount": max(0.0, frappe.utils.flt(doc.grand_total) - frappe.utils.flt(doc.advance_paid)),
		"order_state": details["order_state"],
		"is_hold": details["is_hold"],
		"success": True,
	}


@frappe.whitelist()
def accountant_approve_procurement(name, note=""):
	"""Accountant approval for HOLD orders."""
	if not frappe.db.exists("Sales Order", name):
		frappe.throw("Không tìm thấy đơn hàng " + str(name))
	doc = frappe.get_doc("Sales Order", name)
	doc.add_comment("Comment", text=f"Kế toán phê duyệt chuyển bước 'Mua hàng NCC' (Duyệt ngoại lệ đơn HOLD): {note or 'Kế toán xác nhận cho chạy tiếp'}")

	if doc.docstatus == 0:
		doc.flags.ignore_mandatory = True
		doc.submit()

	return {"name": doc.name, "status": "Đã chuyển Mua hàng NCC", "docstatus": doc.docstatus, "success": True}


@frappe.whitelist()
def submit_sales_order(name):
	"""Submit draft sales order when deposit conditions are satisfied."""
	if not frappe.db.exists("Sales Order", name):
		frappe.throw("Không tìm thấy đơn hàng " + str(name))
	doc = frappe.get_doc("Sales Order", name)
	if doc.docstatus != 0:
		frappe.throw("Chỉ có thể submit đơn hàng ở trạng thái Nháp (Draft).")

	details = get_order_details(name)
	if details["is_hold"]:
		frappe.throw("Đơn hàng đang ở trạng thái HOLD (cọc thiếu). Chỉ Kế toán mới có quyền bấm nút 'Mua hàng NCC' để duyệt tiếp.")
	if not details["can_submit"]:
		frappe.throw(f"Đơn hàng chưa đủ điều kiện (Cần cọc 50% tiền hàng + 100% tiền trục, tổng cần: {details['required_deposit']:,.0f} đ).")

	doc.submit()
	return {"name": doc.name, "status": doc.status, "docstatus": doc.docstatus}


@frappe.whitelist()
def create_sales_order(payload):
	"""Accept new order payload, create native ERPNext Sales Order with DH- series."""
	payload = frappe.parse_json(payload) if isinstance(payload, str) else (payload or {})
	company = payload.get("company") or frappe.defaults.get_user_default("Company")
	if not company:
		companies = frappe.get_all("Company", limit=1)
		company = companies[0].name if companies else "Bao Bì Vạn Phát"

	customer_id = (payload.get("customer") or payload.get("customer_id") or "").strip()
	if not customer_id:
		frappe.throw("Thiếu khách hàng — vui lòng chọn Customer.")

	if not frappe.db.exists("Customer", customer_id):
		cust = frappe.db.get_value("Customer", {"alias": customer_id}, "name") or frappe.db.get_value("Customer", {"customer_name": customer_id}, "name")
		if cust:
			customer_id = cust

	delivery_date = payload.get("delivery_date") or frappe.utils.add_days(frappe.utils.today(), 7)

	items_data = payload.get("items") or []
	if not items_data and payload.get("lines"):
		items_data = payload.get("lines")

	so_items = []
	for it in items_data:
		code = (it.get("item_code") or "").strip()
		it_name = (it.get("item_name") or it.get("variant_name") or code)[:140]
		qty = frappe.utils.flt(it.get("qty") or 1)
		rate = frappe.utils.flt(it.get("rate") or 0)
		uom = it.get("uom") or "Túi"

		so_item = {
			"item_name": it_name,
			"description": it_name,
			"qty": qty,
			"rate": rate,
			"uom": uom,
			"conversion_factor": 1,
			"delivery_date": delivery_date,
		}
		if code and frappe.db.exists("Item", code):
			so_item["item_code"] = code
		elif code:
			so_item["item_code"] = code

		so_items.append(so_item)

	# P2 pass-through (Sếp duyệt): dòng trục cộng từ cylinder_spec.payload — giá NCC quyết.
	# Thiếu giá → KHÔNG tự thêm dòng, KHÔNG fallback số; đơn tạo không trục, bổ sung sau khi có giá NCC.
	cyl_spec = payload.get("cylinder_spec") or {}
	if isinstance(cyl_spec, str):
		cyl_spec = frappe.parse_json(cyl_spec) or {}
	if payload.get("has_new_cylinders") and payload.get("cylinder_count"):
		cyl_qty = int(payload.get("cylinder_count") or cyl_spec.get("qty") or 0)
		cyl_price = frappe.utils.flt(cyl_spec.get("unit_price") or 0)
		cyl_supplier = (cyl_spec.get("supplier") or "").strip()
		if cyl_qty > 0 and cyl_price > 0:
			so_items.append({
				"item_code": "TRUC-IN",
				"item_name": f"Trục in ({cyl_qty} cây, NCC {cyl_supplier or '—'})"[:140],
				"description": f"Trục in theo báo giá NCC ({cyl_qty} cây)",
				"qty": cyl_qty,
				"rate": cyl_price,
				"uom": "Cây",
				"conversion_factor": 1,
				"delivery_date": delivery_date,
			})

	doc = frappe.get_doc({
		"doctype": "Sales Order",
		"naming_series": payload.get("naming_series") or "DH-.YY..MM.-.###",
		"customer": customer_id,
		"delivery_date": delivery_date,
		"transaction_date": payload.get("transaction_date") or frappe.utils.today(),
		"company": company,
		"order_type": "Sales",
		"items": so_items,
	})

	doc.flags.ignore_mandatory = True
	doc.flags.ignore_permissions = True
	doc.insert()

	return {
		"name": doc.name,
		"status": doc.status,
		"grand_total": doc.grand_total,
		"success": True,
	}


@frappe.whitelist()
def make_order_from_quotation(name, naming_series=None, delivery_date=None):
	"""Convert approved Quotation to Sales Order."""
	from erpnext.selling.doctype.quotation.quotation import make_sales_order

	doc = frappe.get_doc("Quotation", name)
	if doc.docstatus != 1 or doc.status not in ("Open", "Partially Ordered"):
		frappe.throw("Chỉ chốt từ báo giá đã duyệt (Open).")
	order = make_sales_order(name)
	order.naming_series = naming_series or "DH-.YY..MM.-.###"
	if not order.get("delivery_date"):
		order.delivery_date = delivery_date or frappe.utils.today()
	order.insert()
	return {"sales_order": order.name, "quotation": doc.name}
