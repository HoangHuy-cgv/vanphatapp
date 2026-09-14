"""Whitelisted Item & Master Catalog APIs for Van Phat Portal (S5/S6: login-only, truthful).

Provides high-performance, strictly mapped ERPNext Native item catalog data
and associated 2-tier Bill of Materials (BOM) for the minimalist industrial cockpit.
DB trống → [] (truthful, không CSV fallback).
"""

import frappe

from vanphat_portal.api._common import page_result, paginate, text

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


@frappe.whitelist()
def clear_catalog_cache(*args, **kwargs):
	"""Clear Redis cache for Van Phat Master Catalog (S3: login-only, doc_events gọi nội bộ).

	S3 đóng guest xả cache: endpoint này chỉ cho user đã login (portal bắt buộc login);
	doc_events Item/Customer/Sales Order/Quotation on_update/on_trash gọi trực tiếp.
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
		rows = (
			condition(frappe.qb.from_(IT).select(*[getattr(IT, field) for field in fields]))
			.orderby(IT.modified, order=frappe.qb.Order.desc)
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
	DB lọc, vỏ chỉ hiển thị — không lấy thừa + filter Python.
	"""
	q = text(query)
	grp = text(item_group)
	supply = text(supply_type)
	cat = text(category).lower()
	p, pl, start = paginate(page, page_length)
	like = f"%{q}%" if q else None

	# S3: key chứa MỌI params (tab/cat/grp/supply/q/page/pl) — key cũ thiếu q gây stale cross-filter
	cache_key = f"vp:items:list|tab={cat}|grp={grp}|supply={supply}|q={q.lower()}|page={p}|pl={pl}"
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
