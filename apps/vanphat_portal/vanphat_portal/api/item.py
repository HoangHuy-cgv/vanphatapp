"""Whitelisted Item & Master Catalog APIs for Van Phat Portal (S5/S6: login-only, truthful).

Provides high-performance, strictly mapped ERPNext Native item catalog data
and associated 2-tier Bill of Materials (BOM) for the minimalist industrial cockpit.
DB trống → [] (truthful, không CSV fallback).
"""

import frappe

from vanphat_portal.api._common import page_result, paginate, text
from vanphat_portal.api._guards import require_doc

# Cột tìm kiếm dùng chung cho cả `or_filters` (get_list) lẫn qb — 1 nguồn duy nhất.
SEARCH_COLUMNS = (
	"item_code",
	"item_name",
	"custom_alias",
	"customer_code",
	"custom_structure_layers",
	"description",
)
# Sếp chốt: tab Sản phẩm = hàng bán/xưởng TP+NGCS+TMD+BTP (88 mã); NVL/TRUC tab riêng.
SP_PREFIXES = ("TP-", "NGCS-", "TMD-", "BTP-")
CATEGORY_PREFIX = {"btp": "BTP-", "nvl": "NVL-", "truc": "TRUC-"}

CATALOG_FIELDS = [
	"item_code",
	"item_name",
	"custom_alias",
	"item_group",
	"stock_uom",
	"brand",
	"default_material_request_type",
	"standard_rate",
	"min_order_qty",
	"safety_stock",
	"disabled",
	"is_stock_item",
	"is_sales_item",
	"is_purchase_item",
	# SPEC native 2026-09-15: Item native KHÔNG có field `customer` (verify 135 fields).
	# Variant KH đọc qua `customer_code` (ERPNext tự join từ customer_items.ref_code
	# qua fill_customer_code) + `customer_items` ở get_detail (as_dict kèm dòng con).
	"customer_code",
	"custom_structure_layers",
	"custom_thickness_mic",
	"custom_film_width_mm",
	"custom_pouch_width_mm",
	"custom_pouch_length_mm",
	"custom_gusset_mm",
	"custom_cut_length_mm",
	"custom_print_tech",
	"custom_accessory_spec",
	"custom_cylinder_item",
	"custom_cylinder_qty",
	"custom_cylinder_location",
	"description",
]


def clear_catalog_cache(*args, **kwargs):
	"""Xóa cache catalog nội bộ — KHÔNG whitelist, chỉ doc_events gọi trực tiếp.

	Sếp chốt 2026-09-15: bỏ whitelist (giảm 27 còn 26 endpoint, xóa W1).
	`hooks.py doc_events` trỏ thẳng hàm này, không đi qua HTTP.
	Nhận *args/**kwargs vì Frappe doc_events truyền doc vào hook.
	"""
	try:
		frappe.cache().delete_keys("vp:items:list|*")
		frappe.cache().delete_keys("vanphat:catalog:*")
	except Exception:
		pass
	return {"success": True}


def _query_items_qb(fields, filters, prefixes=None, like=None, start=0, page_length=15):
	"""Query Item bằng qb: 1 query rows + 1 query count dùng CHUNG điều kiện.

	Dùng cho tab SP (4 prefix TP/NGCS/TMD/BTP) và mọi case search (khớp list/count).
	"""
	IT = frappe.qb.DocType("Item")

	def condition(query):
		for key, value in (filters or {}).items():
			if isinstance(value, (list, tuple)) and len(value) == 2 and str(value[0]).lower() == "like":
				query = query.where(getattr(IT, key).like(value[1]))
			else:
				query = query.where(getattr(IT, key) == value)
		if prefixes:
			prefix_cond = None
			for prefix in prefixes:
				clause = IT.item_code.like(f"{prefix}%")
				prefix_cond = clause if prefix_cond is None else (prefix_cond | clause)
			query = query.where(prefix_cond)
		if like:
			search_cond = None
			for column in SEARCH_COLUMNS:
				clause = getattr(IT, column).like(like)
				search_cond = clause if search_cond is None else (search_cond | clause)
			query = query.where(search_cond)
		return query

	try:
		from frappe.query_builder import Order

		rows = (
			condition(frappe.qb.from_(IT).select(*[getattr(IT, field) for field in fields]))
			.orderby(IT.modified, order=Order.desc)
			.limit(page_length)
			.offset(start)
			.run(as_dict=True)
		)
	except Exception:
		rows = []
	try:
		count_rows = condition(
			frappe.qb.from_(IT).select(frappe.query_builder.functions.Count("*").as_("c"))
		).run(as_dict=True)
		total = int(count_rows[0].get("c") or 0) if count_rows else 0
	except Exception:
		total = 0
	return rows, total


@frappe.whitelist()
def get_list(query=None, item_group=None, supply_type=None, category=None, page=1, page_length=15):
	"""P3 full-server: filters + or_filters like + start/page_length + db.count.

	Docs: frappe.db.get_list(doctype, filters, or_filters, fields, order_by, start,
	page_length) tự áp permission (https://docs.frappe.io/framework/user/en/api/database).
	DB lọc, vỏ chỉ hiển thị — không lấy thừa + filter Python. Nhánh qb KHÔNG tự
	áp permission như get_list → cổng require_doc("Item", "read") ở đầu (Sếp chốt).
	"""
	require_doc("Item", "read")
	q = text(query)
	grp = text(item_group)
	supply = text(supply_type)
	cat = text(category).lower()
	p, pl, start = paginate(page, page_length)
	like = f"%{q}%" if q else None

	# S3: key chứa MỌI params + roles (cache chung key rò dữ liệu vượt quyền) —
	# key cũ thiếu q gây stale cross-filter
	roles_key = ",".join(sorted(frappe.get_roles() or []))
	cache_key = f"vp:items:list|roles={roles_key}|tab={cat}|grp={grp}|supply={supply}|q={q.lower()}|page={p}|pl={pl}"
	try:
		cached = frappe.cache().get_value(cache_key)
		if cached:
			return cached
	except Exception:
		pass

	filters = {}
	if grp:
		filters["item_group"] = grp
	if supply:
		filters["default_material_request_type"] = supply
	prefix = CATEGORY_PREFIX.get(cat)
	if prefix:
		filters["item_code"] = ["like", f"{prefix}%"]
	or_filters = [["Item", column, "like", like] for column in SEARCH_COLUMNS] if like else None

	# S5: db.get_list tôn trọng permission (không get_all bypass); lỗi DB → [] truthful.
	# Tab SP (4 prefix OR) + mọi case có q đều đi qb 1 query (khớp count, chữa N+1).
	if cat == "sp" or or_filters:
		items, total_count = _query_items_qb(
			CATALOG_FIELDS, filters, SP_PREFIXES if cat == "sp" else None, like, start, pl
		)
	else:
		items = frappe.db.get_list(
			"Item",
			fields=CATALOG_FIELDS,
			filters=filters or None,
			order_by="modified desc",
			start=start,
			page_length=pl,
		)
		total_count = frappe.db.count("Item", filters)

	result = page_result("items", items, p, pl, total_count)
	try:
		frappe.cache().set_value(cache_key, result, expires_in_sec=300)
	except Exception:
		pass
	return result


def _bom_item_aliases(bom_items):
	"""{item_code: custom_alias} cho cả BOM bằng 1 query (chữa N+1 từng dòng)."""
	codes = [row.item_code for row in bom_items if row.item_code]
	if not codes:
		return {}
	try:
		rows = frappe.db.get_list(
			"Item",
			filters={"name": ["in", codes]},
			fields=["name", "custom_alias"],
			page_length=len(codes),
		)
	except Exception:
		return {}
	return {row["name"]: row.get("custom_alias") for row in rows}


@frappe.whitelist()
def get_detail(item_code):
	"""Return item specification and associated BOM details for the slide-over drawer.

	S5/S6: login + permission check; không CSV fallback — DB trống → throw truthful.
	"""
	require_doc("Item", "read")
	code = text(item_code)
	if not code:
		frappe.throw("Thiếu item_code")
	if not frappe.db.exists("Item", code):
		frappe.throw(f"Không tìm thấy mặt hàng {code}", frappe.DoesNotExistError)

	item = frappe.get_doc("Item", code)
	if not frappe.has_permission("Item", "read", item):
		frappe.throw("Không có quyền xem mặt hàng.", frappe.PermissionError)
	item = item.as_dict()

	default_bom = frappe.db.get_value("BOM", {"item": code, "is_default": 1, "is_active": 1}, "name")
	if not default_bom:
		default_bom = frappe.db.get_value("BOM", {"item": code, "is_active": 1}, "name")
	if not default_bom:
		return {"item": item, "bom": None}

	bom_doc = frappe.get_doc("BOM", default_bom)
	if not frappe.has_permission("BOM", "read", bom_doc):
		frappe.throw("Không có quyền xem định mức.", frappe.PermissionError)

	aliases = _bom_item_aliases(bom_doc.items)
	bom_items = []
	for row in bom_doc.items:
		row_dict = row.as_dict()
		row_dict["custom_alias"] = aliases.get(row.item_code) or row.item_name or row.item_code
		bom_items.append(row_dict)

	return {"item": item, "bom": {"master": bom_doc.as_dict(), "items": bom_items}}


# Triple rule 2 (config native — Sếp chốt 2026-09-15): nhóm sản phẩm cockpit đọc từ
# Item Group tree native, KHÔNG hardcode 4 <option> trong Vue. Mỗi nhóm gom các
# Item Group con bán được; label/desc/uom từ data thật; min_qty từ min_order_qty.
PRODUCT_GROUPS = (
	{
		"key": "tui_mang_ghep",
		"label": "Túi màng ghép",
		"desc": "Xưởng SX",
		"item_groups": ("Túi Màng Ghép Đặt Riêng",),
		"order_tab": "xuong_sx",
		"uom": "Túi",
	},
	{
		"key": "cuon_mang_ghep",
		"label": "Cuộn màng ghép",
		"desc": "Xưởng SX - Kg",
		"item_groups": ("Cuộn Màng Ghép BTP",),
		"order_tab": "xuong_sx",
		"uom": "Kg",
	},
	{
		"key": "tui_ngcs",
		"label": "Túi NGCS",
		"desc": "In lụa phôi có sẵn",
		"item_groups": ("Túi Nước Giặt Có Sẵn (NGCS)",),
		"order_tab": "ngcs",
		"uom": "Túi",
	},
	{
		"key": "tui_mang_don",
		"label": "Túi màng đơn",
		"desc": "Mua ngoài - Kg",
		"item_groups": ("Túi Màng Đơn",),
		"order_tab": "mua_ngoai",
		"uom": "Kg",
	},
)


@frappe.whitelist()
def get_product_groups():
	"""Nhóm sản phẩm cockpit từ Item Group native (triple rule 2).

	DB trống → nhóm giữ label nhưng count 0 + min_qty null (truthful, không số bịa).
	"""
	require_doc("Item", "read")
	groups = []
	for spec in PRODUCT_GROUPS:
		count = 0
		min_qty = None
		try:
			count = int(
				frappe.db.count("Item", {"item_group": ["in", list(spec["item_groups"])]}) or 0
			)
		except Exception:
			count = 0
		try:
			rows = frappe.db.get_list(
				"Item",
				filters={"item_group": ["in", list(spec["item_groups"])]},
				fields=["min_order_qty"],
				order_by="min_order_qty asc",
				page_length=1,
			)
			if rows and rows[0].get("min_order_qty"):
				min_qty = rows[0].get("min_order_qty")
		except Exception:
			min_qty = None
		groups.append({
			"key": spec["key"],
			"label": spec["label"],
			"desc": spec["desc"],
			"order_tab": spec["order_tab"],
			"uom": spec["uom"],
			"count": count,
			"min_qty": min_qty,
		})
	return {"product_groups": groups}


@frappe.whitelist()
def get_print_config():
	"""Cấu hình in ấn + phụ kiện cockpit từ Custom Field Select native (triple rule 2).

	Đọc `options` của `custom_print_tech` / `custom_accessory_spec` trên Item —
	đổi options trong Customize Form → UI đổi theo, không build lại.
	Field thiếu/trống → list rỗng truthful, UI ẩn khối tương ứng.
	"""
	require_doc("Item", "read")

	def select_options(dt, fieldname):
		try:
			df = frappe.get_meta(dt).get_field(fieldname)
			raw = (df.options if df else "") or ""
			return [line.strip() for line in str(raw).splitlines() if line.strip()]
		except Exception:
			return []

	return {
		"print_techs": select_options("Item", "custom_print_tech"),
		"accessories": select_options("Item", "custom_accessory_spec"),
	}
