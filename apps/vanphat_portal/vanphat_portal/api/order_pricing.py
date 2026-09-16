"""Giá doc-driven + preview + % cọc + hạn mức (tách từ order.py, Task 6a).

ERPNext tính, vỏ chỉ đọc. Không whitelist ở đây — wrapper giữ ở `order.py`.
"""

import frappe

from vanphat_portal.api._common import as_json, resolve_customer, text

DEFAULT_ORDER_NAMING_SERIES = "DH-.YY..MM.-.###"

SETTINGS_DOCTYPE = "Van Phat Settings"


def _default_deposit_pct():
	"""% cọc mặc định khi KH chưa có Payment Terms Template — từ Single Desk.

	Config native (Sếp xem/sửa ở Desk, không rebuild). Single hoặc field
	thiếu/không hợp lệ → throw rõ tên config, KHÔNG số cứng trong code.
	Quy ước duy nhất: field Percent 0–100 (nhập 50 = 50%); lỗi DB ghi log
	server, message user generic (không lộ internals).
	"""
	try:
		value = frappe.db.get_single_value(SETTINGS_DOCTYPE, "default_deposit_pct")
	except Exception as exc:
		frappe.logger("vanphat_portal").error("Đọc %s.default_deposit_pct lỗi: %s", SETTINGS_DOCTYPE, exc)
		frappe.throw(
			"Thiếu cấu hình {}: liên hệ quản trị kiểm tra Desk.".format(SETTINGS_DOCTYPE)
		)
	if value in (None, ""):
		frappe.throw(
			"Thiếu cấu hình {}: nhập default_deposit_pct ở Desk trước.".format(SETTINGS_DOCTYPE)
		)
	pct = frappe.utils.flt(value)
	if pct <= 0 or pct > 100:
		frappe.throw(
			"Cấu hình {} không hợp lệ: default_deposit_pct phải trong 0–100.".format(SETTINGS_DOCTYPE)
		)
	return pct / 100.0


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


def _required_deposit(payment_type, product_total, deposit_pct, cylinder_total):
	"""MỘT công thức cọc: Trả sau = 0; Trả trước = % terms trên tiền hàng + 100% tiền trục."""
	if payment_type == "Trả sau":
		return 0.0
	return round((product_total * deposit_pct) + cylinder_total)


def _order_status(docstatus, payment_type, advance_paid, required_deposit):
	"""MỘT model trạng thái duy nhất cho list + drawer + mutation (ADR-006).

	Một công thức HOLD: Trả sau không bao giờ HOLD; Trả trước thiếu cọc
	một phần (0 < advance < required) = HOLD. label ngắn cho list
	(`HOLD`/`Đã duyệt`/`Chờ cọc`), state dài cho drawer/mutation
	(`HOLD (Thiếu cọc)`/`Đủ cọc (Chờ kích hoạt)`/...). Trả về dict để
	không còn 2 tuple song song lệch nhau.
	"""
	submitted = docstatus == 1
	is_hold = payment_type == "Trả trước" and 0 < advance_paid < required_deposit
	if payment_type == "Trả sau":
		label = "Đã duyệt"
		css_class = "status-ordered"
		state = "Chính thức (Trả sau)" if submitted else "Chờ kích hoạt (Trả sau)"
		return {
			"label": label,
			"css_class": css_class,
			"state": state,
			"is_hold": False,
			"can_submit": not submitted,
		}
	paid_enough = advance_paid >= required_deposit
	if submitted:
		state = "Chính thức (Đã đủ cọc)" if paid_enough else "Chính thức (Trả trước)"
		return {
			"label": "Đã duyệt",
			"css_class": "status-ordered",
			"state": state,
			"is_hold": False,
			"can_submit": False,
		}
	if is_hold:
		return {
			"label": "HOLD",
			"css_class": "status-hold",
			"state": "HOLD (Thiếu cọc)",
			"is_hold": True,
			"can_submit": False,
		}
	if paid_enough:
		return {
			"label": "Đã duyệt",
			"css_class": "status-ordered",
			"state": "Đủ cọc (Chờ kích hoạt)",
			"is_hold": False,
			"can_submit": True,
		}
	return {
		"label": "Chờ cọc",
		"css_class": "status-draft",
		"state": "Chờ cọc",
		"is_hold": False,
		"can_submit": False,
	}


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


def _deposit_pct_map(customers, default_pct=None):
	"""{customer: % cọc} cho nhiều KH bằng 2 query + 1 đọc Single (chữa N+1 khi list đơn).

	KH chưa có template → % mặc định từ Single `Van Phat Settings` và GHI LOG.
	`default_pct` cho caller đã đọc Single (list_orders) tái dùng — tránh đọc 2 lần.
	Không có KH nào → {} ngay, KHÔNG đọc Single (trang rỗng không throw thiếu-config).
	"""
	names = [name for name in dict.fromkeys(customers) if name]
	if not names:
		return {}
	default_pct = default_pct if default_pct is not None else _default_deposit_pct()
	pcts = dict.fromkeys(names, default_pct)

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
			"Dùng cọc mặc định %s cho KH thiếu Payment Terms Template: %s",
			default_pct,
			", ".join(missing),
		)
	return pcts


def _get_deposit_pct(customer=None):
	"""% cọc của MỘT khách — chỉ có một đường tính duy nhất (bọc `_deposit_pct_map`)."""
	name = resolve_customer(customer)
	if not name:
		return _default_deposit_pct()
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

def price_preview_data(
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
	required_deposit = _required_deposit(payment_type, product_total, deposit_pct, cylinder_total)

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
