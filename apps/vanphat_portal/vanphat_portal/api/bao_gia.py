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
			"naming_series": payload.get("naming_series") or "BG-.YY..MM.-.###",
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
		sub = frappe.utils.flt(doc.total)
		tax = frappe.utils.flt(doc.total_taxes_and_charges)
		if not tax and sub:
			tax = round(sub * (8.0 / 100.0))
		return {
			"total_qty": doc.total_qty or 0,
			"subtotal": sub,
			"vat_rate": 8.0,
			"cylinder_total": 0,
			"tax_amount": tax,
			"grand_total": frappe.utils.flt(doc.grand_total) or (sub + tax),
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
	# SSOT server: VAT 8% tính tại backend, client chỉ hiển thị (S1; S9 native hóa template)
	vat_rate = 8.0
	tax_amount = round(subtotal * (vat_rate / 100.0))
	return {
		"total_qty": total_qty,
		"subtotal": subtotal,
		"vat_rate": vat_rate,
		"cylinder_total": 0,
		"tax_amount": tax_amount,
		"grand_total": subtotal + tax_amount,
	}


# Packaging calculation domain constants (SSOT)
DENSITIES = {
	"PET": 1.34,
	"PA": 1.14,
	"PES": 0.93,
	"PE": 0.925,
	"PE_TRONG": 0.925,
	"MPET": 1.40,
	"AL": 2.70,
	"OPP": 0.905,
	"CPP": 0.90,
	"MCPP": 0.91,
}

PRICES = {
	"PET": 47000.0,
	"PA": 81000.0,
	"PES": 51500.0,
	"PE": 45000.0,
	"PE_TRONG": 42500.0,
	"MPET": 57000.0,
	"AL": 160000.0,
	"OPP": 43000.0,
	"CPP": 46000.0,
	"MCPP": 48000.0,
}

DEFAULT_THICKNESS = {
	"PET": 12.0,
	"OPP": 20.0,
	"PA": 15.0,
	"AL": 7.0,
	"MPET": 12.0,
	"PES": 100.0,
	"PE": 100.0,
	"CPP": 30.0,
	"MCPP": 25.0,
}

SPOUT_PRICES = {"10": 180.0, "16": 227.0, "22": 356.0}

L_ROLL = 1500.0
SETUP_FIXED = 3500000.0
BOX_COST = 36.6
GLUE_COST_PER_M2 = 450.0
DEFAULT_CYLINDER_PRICE = 3500000.0


def compute_pouch_area(pouch_type, w_m, l_m, g_m):
	"""Calculate 2D surface area of flexible pouch based on shape standard."""
	pt = str(pouch_type or "").lower()
	if "3_bien" in pt or "three_side" in pt:
		return 2.0 * w_m * l_m
	if "xep_hong" in pt or "gusset" in pt or "lung" in pt:
		return 2.0 * (w_m + g_m) * (l_m + 0.015)
	if "8_canh" in pt or "flat_bottom" in pt:
		return 2.0 * w_m * l_m + 2.0 * g_m * l_m + w_m * g_m
	# Default: Túi đáy đứng (Doypack)
	return 2.0 * w_m * (l_m + g_m / 2.0)


def get_scrap_rate(num_rolls):
	"""Loss / scrap rate based on actual production batch volume."""
	if num_rolls <= 1:
		return 0.08
	return 0.065 if num_rolls <= 2 else 0.055


def normalize_layers(layers, total_thickness=None):
	"""Parse and normalize layer structure from array of dicts or list of strings."""
	if isinstance(layers, str):
		layers = frappe.parse_json(layers) or []

	if not layers:
		return [
			{"material": "PET", "thickness": 12.0},
			{"material": "PA", "thickness": 15.0},
			{"material": "PES", "thickness": 190.0},
		]

	normalized = []
	for item in layers:
		if isinstance(item, dict):
			mat = str(item.get("material", "PE")).upper().replace(" ", "_")
			thick = float(item.get("thickness") or DEFAULT_THICKNESS.get(mat, 50.0))
			normalized.append({"material": mat, "thickness": thick})
		elif isinstance(item, str):
			mat = item.strip().upper().replace(" ", "_")
			thick = DEFAULT_THICKNESS.get(mat, 50.0)
			normalized.append({"material": mat, "thickness": thick})

	if total_thickness and float(total_thickness) > 0 and len(normalized) > 1:
		tot = float(total_thickness)
		other_thick = sum(l["thickness"] for l in normalized[:-1])
		if tot > other_thick:
			normalized[-1]["thickness"] = tot - other_thick

	return normalized


@frappe.whitelist(allow_guest=True)
def calculate_packaging_quotation(
	pouch_type="day_dung_co_voi",
	width_mm=280,
	length_mm=340,
	gusset_mm=45,
	layers=None,
	spout_type="16mm",
	desired_qty=5000,
	target_margin=0.30,
	lanes=None,
	cylinder_qty=0,
	cylinder_unit_price=3500000.0,
):
	"""Tính toán định mức màng & dự toán giá theo chuẩn sản xuất Vạn Phát.

	Nguyên tắc sản xuất & báo giá:
	1. Tiền trục in: Khách chưa có trục thì báo giá trục riêng (dòng riêng),
	   tuyệt đối không gộp tiền trục vào đơn giá túi.
	2. Tính tròn cuộn: Luôn chạy tròn cuộn màng (chuẩn L_ROLL = 1.500m).
	   Nếu khách lấy ít hơn sản lượng tròn cuộn, xưởng vẫn chạy tròn cuộn,
	   phần túi dư (surplus) nhập kho lưu trữ để bán tiếp cho đơn hàng sau.
	3. Tối ưu 2 lane (khổ to): Với các khổ túi vừa/nhỏ (W <= 360mm), xưởng chọn màng
	   khổ to chạy 2 con (2 lane) trên trục in để tối ưu tốc độ máy và triệt tiêu màng dở dang.
	"""
	import math

	try:
		width_mm = float(width_mm or 0)
		length_mm = float(length_mm or 0)
		gusset_mm = float(gusset_mm or 0)
		desired_qty = max(1, int(desired_qty or 5000))
		target_margin = float(target_margin if target_margin is not None else 0.30)
		cylinder_qty = max(0, int(cylinder_qty or 0))
		cylinder_unit_price = float(cylinder_unit_price or DEFAULT_CYLINDER_PRICE)
	except (TypeError, ValueError):
		frappe.throw("Thông số kích thước hoặc số lượng không hợp lệ.")

	# Tự động chọn 2 lane nếu khổ túi width <= 360mm (vừa khổ trục 750-900mm và màng 700-800mm)
	active_lanes = (
		2 if (lanes is None or str(lanes).strip() == "") and width_mm <= 360 else max(1, int(lanes or 1))
	)

	norm_layers = normalize_layers(layers)

	# 1. Bước cắt dao & Diện tích túi
	l_cut_m = length_mm / 1000.0
	a_pouch = compute_pouch_area(pouch_type, width_mm / 1000.0, length_mm / 1000.0, gusset_mm / 1000.0)

	# 2. Khối lượng và chi phí màng & keo ghép
	pouch_weight_g = sum(a_pouch * l["thickness"] * DENSITIES.get(l["material"], 0.93) for l in norm_layers)
	film_cost_raw = sum(
		(a_pouch * l["thickness"] * DENSITIES.get(l["material"], 0.93) / 1000.0) * PRICES.get(l["material"], 50000.0)
		for l in norm_layers
	)
	glue_cost_raw = a_pouch * GLUE_COST_PER_M2

	# 3. Phụ kiện vòi
	spout_price = 0.0
	if spout_type:
		st = str(spout_type).lower()
		for code, price in SPOUT_PRICES.items():
			if code in st:
				spout_price = price
				break

	# 4. Tính toán sản lượng theo cuộn chuẩn 1.500m
	bags_per_roll = int((L_ROLL * active_lanes * (1.0 - get_scrap_rate(1))) / l_cut_m) if l_cut_m > 0 else 0
	num_rolls = max(1, int(math.ceil(desired_qty / float(bags_per_roll)))) if bags_per_roll > 0 else 1
	q_optimal = num_rolls * bags_per_roll
	q_surplus = max(0, q_optimal - desired_qty)
	scrap_batch = get_scrap_rate(num_rolls)

	# Chi phí NVL chuẩn
	raw_material_unit = (film_cost_raw + glue_cost_raw + spout_price) * (1.0 + scrap_batch)
	raw_film_glue_unit = (film_cost_raw + glue_cost_raw) * (1.0 + scrap_batch)

	# Nấc 1: Số lượng tối ưu tròn cuộn (Đơn giá tốt nhất)
	mfg_optimal = (SETUP_FIXED / q_optimal) + 800.0
	cogs_optimal = raw_material_unit + mfg_optimal + BOX_COST
	margin_div = (1.0 - target_margin) if target_margin < 1.0 else 1.0
	price_optimal = round(cogs_optimal / margin_div, 0)

	# Nấc 2: Số lượng khách yêu cầu (Đơn giá cao hơn bù đắp setup và tồn dư)
	if desired_qty >= q_optimal:
		cogs_desired = cogs_optimal
		price_desired = price_optimal
		surplus_risk_buffer = 0.0
	else:
		surplus_risk_buffer = (q_surplus * raw_film_glue_unit * 0.5) / float(desired_qty)
		mfg_desired = (SETUP_FIXED / desired_qty) + 800.0
		cogs_desired = raw_material_unit + mfg_desired + BOX_COST + surplus_risk_buffer
		price_desired = round(cogs_desired / margin_div, 0)

	cylinder_total = cylinder_qty * cylinder_unit_price
	cylinder_quote = {
		"qty": cylinder_qty,
		"unit_price": cylinder_unit_price,
		"total": cylinder_total,
		"is_billed_separately": True,
		"note": "Tiền trục in ống đồng thanh toán riêng cho đơn hàng đầu (nếu khách chưa có trục). Không cộng vào đơn giá túi.",
	}

	add_on_cost_for_full = max(0, int(price_optimal * q_optimal - price_desired * desired_qty))
	price_savings = max(0, int(price_desired - price_optimal))

	return {
		"step_cut_mm": round(l_cut_m * 1000.0, 1),
		"area_m2": round(a_pouch, 4),
		"weight_g": round(pouch_weight_g, 2),
		"roll_length_m": L_ROLL,
		"lanes": active_lanes,
		"bags_per_roll": bags_per_roll,
		"target_margin": target_margin,
		"scenarios": {
			"optimal_whole_roll": {
				"rolls": num_rolls,
				"qty": q_optimal,
				"cogs": round(cogs_optimal, 0),
				"rate": price_optimal,
				"total": price_optimal * q_optimal,
				"label": f"Tròn {num_rolls} cuộn ({q_optimal:,} túi) — ĐƠN GIÁ TỐT NHẤT",
				"note": "Tối ưu 100% cuộn màng, không phát sinh chi phí tồn dư rủi ro.",
			},
			"requested_qty": {
				"rolls_required": num_rolls,
				"qty": desired_qty,
				"surplus_bags_warehouse": q_surplus,
				"cogs": round(cogs_desired, 0),
				"rate": price_desired,
				"total": price_desired * desired_qty,
				"label": f"Đúng số lượng yêu cầu ({desired_qty:,} túi) — ĐƠN GIÁ CAO HƠN",
				"note": f"Đơn giá cao hơn do bù đắp chi phí setup máy và rủi ro màng dở dang {q_surplus:,} túi dư nếu khách không đặt lại.",
			},
		},
		"upsell_recommendation": {
			"extra_cost_to_get_full_batch": add_on_cost_for_full,
			"extra_bags_received": q_surplus,
			"unit_price_savings": price_savings,
			"pitch": f"Khách chỉ cần thêm {add_on_cost_for_full:,} đ là nhận thêm trọn vẹn {q_surplus:,} túi với đơn giá rẻ hơn {price_savings:,} đ/túi!",
		},
		"cylinder_quote": cylinder_quote,
		"total_order_amount_desired": (price_desired * desired_qty) + cylinder_total,
		"total_order_amount_optimal": (price_optimal * q_optimal) + cylinder_total,
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

# Re-export order lifecycle methods from dedicated order.py module for backward compatibility
from vanphat_portal.api.order import (
	get_price_preview,
	list_orders,
	get_order_details,
	record_order_deposit,
	accountant_approve_procurement,
	submit_sales_order,
	create_sales_order,
	make_order_from_quotation,
)

@frappe.whitelist()
def get_boot():
	"""Shell boot: CSRF token + user (static portal.html has no Jinja)."""
	return {
		"user": frappe.session.user,
		"csrf_token": frappe.sessions.get_csrf_token(),
		"company": frappe.defaults.get_user_default("Company"),
	}
