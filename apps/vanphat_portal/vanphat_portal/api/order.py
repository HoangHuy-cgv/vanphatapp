"""Dedicated Order Management & Sales Order Lifecycle APIs for Van Phat Portal.

Handles ERPNext Native Sales Order lifecycle:
- Listing with backend tab filtering (NGCS, Xưởng SX, Mua ngoài)
- Order detail extraction with cylinder vs product separation
- Server-side price & deposit preview (Zero client-side financial math)
- Order creation, deposit recording, accountant approval, and submission
"""

import frappe


CYLINDER_STANDARD_RATE = 3100000.0
STANDARD_VAT_RATE = 8.0  # 8% VAT standard for packaging manufacturing


@frappe.whitelist()
def get_price_preview(payload=None, items=None, customer=None, has_new_cylinders=False, cylinder_count=0):
	"""Server-side pricing & deposit calculator.

	Enforces SSOT: Zero client-side math. Calculates net_total, VAT, cylinder tooling,
	and required deposit according to Van Phat commercial payment policy.
	"""
	data = frappe.parse_json(payload) if isinstance(payload, str) else (payload or {})
	if not items and data.get("items"):
		items = data.get("items")
	if not customer and data.get("customer"):
		customer = data.get("customer")
	if "has_new_cylinders" in data:
		has_new_cylinders = data.get("has_new_cylinders")
	if "cylinder_count" in data:
		cylinder_count = data.get("cylinder_count")

	items_list = items or []
	if isinstance(items_list, str):
		items_list = frappe.parse_json(items_list)

	# 1. Tính tổng tiền hàng trước thuế (Net Total)
	net_total = 0.0
	for it in items_list:
		qty = frappe.utils.flt(it.get("qty") or 0)
		rate = frappe.utils.flt(it.get("rate") or 0)
		net_total += qty * rate

	# 2. Tính thuế GTGT (VAT)
	vat_amount = round(net_total * (STANDARD_VAT_RATE / 100.0))
	product_total = net_total + vat_amount

	# 3. Tính tiền trục in (Cylinder tooling)
	cyl_count = int(cylinder_count or 0)
	is_new_cyl = bool(has_new_cylinders) and cyl_count > 0
	cylinder_total = (cyl_count * CYLINDER_STANDARD_RATE) if is_new_cyl else 0.0

	# 4. Tổng giá trị đơn hàng (Grand Total)
	grand_total = product_total + cylinder_total

	# 5. Xác định điều khoản thanh toán & hạn mức tín dụng khách hàng
	payment_type = "Trả trước"
	credit_limit = 0.0
	if customer:
		try:
			cust_doc = frappe.db.get_value("Customer", customer, ["name"], as_dict=True)
			if not cust_doc:
				cust_doc = frappe.db.get_value("Customer", {"alias": customer}, ["name"], as_dict=True)
			if cust_doc:
				credit_limit = frappe.db.get_value("Customer Credit Limit", {"parent": cust_doc.name}, "credit_limit") or 0.0
				if credit_limit > 0:
					payment_type = "Trả sau"
		except Exception:
			credit_limit = 0.0

	# 6. Quy tắc Vàng: Khách trả sau cọc 0đ; Khách trả trước cọc 50% tiền hàng sau thuế + 100% tiền trục
	if payment_type == "Trả sau":
		required_deposit = 0.0
	else:
		required_deposit = round((product_total * 0.5) + cylinder_total)

	return {
		"net_total": net_total,
		"vat_rate": STANDARD_VAT_RATE,
		"vat_amount": vat_amount,
		"product_total": product_total,
		"cylinder_count": cyl_count,
		"cylinder_rate": CYLINDER_STANDARD_RATE,
		"cylinder_total": cylinder_total,
		"grand_total": grand_total,
		"payment_type": payment_type,
		"credit_limit": credit_limit,
		"required_deposit": required_deposit,
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

	from frappe.query_builder.functions import Count, Sum

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
		cyl_total = 0.0
		total_qty = 0.0
		for _it in agg_rows:
			total_qty += frappe.utils.flt(_it.get("qty") or 0)
			_code = (_it.get("item_code") or "").upper()
			_iname = (_it.get("item_name") or "").lower()
			if "TRUC-" in _code or "trục" in _iname:
				cyl_total += frappe.utils.flt(_it.get("amount")) * 1.08
		if not total_qty:
			total_qty = frappe.utils.flt(o.get("qty")) or 0
		product_total = max(0.0, gt - cyl_total)
		o["cylinder_total"] = cyl_total
		o["product_total"] = product_total
		o["required_deposit"] = round((product_total * 0.5) + cyl_total)

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

	# Bóc tách tiền trục in (TRUC-) và tiền hàng (túi/cuộn màng)
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
			cylinder_total += amt * 1.08  # Giá sau VAT 8%
		else:
			product_total += amt * 1.08
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

	# Quy tắc Vàng: Cọc 50% tiền hàng + 100% TIỀN TRỤC (S1; S9 native hóa template, hằng số chỉ fallback)
	net_total = frappe.utils.flt(doc.net_total) or max(0.0, grand_total - frappe.utils.flt(doc.total_taxes_and_charges))
	vat_amount = frappe.utils.flt(doc.total_taxes_and_charges) or round(net_total * (8.0 / 100.0))
	required_deposit = round((product_total * 0.5) + cylinder_total)
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
				materials = [l.strip() for l in layers_raw.split("/") if l.strip()]
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
		"vat_rate": 8.0,
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

	# Bổ sung dòng trục in nếu có
	if payload.get("has_new_cylinders") and payload.get("cylinder_count"):
		cyl_qty = int(payload.get("cylinder_count") or 0)
		if cyl_qty > 0:
			so_items.append({
				"item_code": "TRUC-IN",
				"item_name": f"Trục in đồng ({cyl_qty} màu/trục)",
				"description": f"Trục in theo thiết kế mới ({cyl_qty} màu)",
				"qty": cyl_qty,
				"rate": CYLINDER_STANDARD_RATE,
				"uom": "Bộ",
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
