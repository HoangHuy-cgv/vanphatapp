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
	"""Return Sales Orders filtered by Cockpit Tab and search query with server pagination."""
	import math
	tab_filter = (tab or "").strip().lower()
	q = (query or "").strip().lower()
	p = max(1, int(page or 1))
	pl = max(1, int(page_length or 15))

	try:
		orders = frappe.get_list(
			"Sales Order",
			fields=[
				"name",
				"transaction_date",
				"customer",
				"customer_name",
				"grand_total",
				"advance_paid",
				"status",
				"docstatus",
			],
			order_by="creation desc",
			limit=500,
		)
	except Exception:
		orders = []

	processed_orders = []
	tab_counts = {"xuong_sx": 0, "ngcs": 0, "mua_ngoai": 0, "all": 0}

	for o in orders:
		gt = frappe.utils.flt(o.grand_total)
		adv = frappe.utils.flt(o.advance_paid)
		o["advance_paid"] = adv
		o["outstanding_amount"] = max(0.0, gt - adv)
		o["deposit_pct"] = round((adv / gt * 100), 1) if gt > 0 else 0

		# Lấy alias khách hàng
		try:
			cust_alias = frappe.db.get_value("Customer", o.customer, "alias")
		except Exception:
			cust_alias = None
		o["customer_alias"] = cust_alias or o.customer_name or o.customer

		# Lấy tóm tắt mặt hàng đầu tiên & tổng số lượng
		try:
			items = frappe.get_all(
				"Sales Order Item",
				filters={"parent": o.name},
				fields=["item_code", "item_name", "qty", "uom"],
				order_by="idx asc",
			)
		except Exception:
			items = []

		if items:
			first_it = items[0]
			o["item_name"] = first_it.item_name
			o["qty"] = sum(frappe.utils.flt(it.get("qty") or 0) for it in items)
			o["uom"] = first_it.uom or "Túi"
			try:
				it_alias = frappe.db.get_value("Item", first_it.item_code, "custom_alias")
			except Exception:
				it_alias = None
			o["custom_alias"] = it_alias or first_it.item_name
		else:
			o["item_name"] = "—"
			o["custom_alias"] = "—"
			o["qty"] = 0
			o["uom"] = "Túi"

		# Phân loại tab buồng lái
		it_code = (items[0].get("item_code") or "").upper() if items else ""
		it_name = (items[0].get("item_name") or "").lower() if items else ""
		if "NGCS" in it_code or "ngcs" in it_name:
			o["order_tab"] = "ngcs"
			o["product_group"] = "Túi NGCS"
		elif "TMD" in it_code or "đơn" in it_name or "màng đơn" in it_name:
			o["order_tab"] = "mua_ngoai"
			o["product_group"] = "Túi màng đơn"
		else:
			o["order_tab"] = "xuong_sx"
			o["product_group"] = "Túi màng ghép"

		# Đếm tổng theo tab
		tab_counts["all"] += 1
		if o["order_tab"] in tab_counts:
			tab_counts[o["order_tab"]] += 1

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

		# Lọc theo Tab trên Server nếu có yêu cầu
		if tab_filter and tab_filter != "all":
			if tab_filter == "ngcs" and o["order_tab"] != "ngcs":
				continue
			if tab_filter == "xuong_sx" and o["order_tab"] != "xuong_sx":
				continue
			if tab_filter == "mua_ngoai" and o["order_tab"] != "mua_ngoai":
				continue

		# Lọc theo Search Query nếu có
		if q:
			search_space = f"{o['name']} {o['customer_alias']} {o['item_name']} {o['custom_alias']}".lower()
			if q not in search_space:
				continue

		processed_orders.append(o)

	total_count = len(processed_orders)
	total_pages = max(1, math.ceil(total_count / pl))
	start = (p - 1) * pl
	end = start + pl
	paginated_orders = processed_orders[start:end]

	return {
		"orders": paginated_orders,
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

	# Quy tắc Vàng: Cọc 50% tiền hàng + 100% TIỀN TRỤC
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
