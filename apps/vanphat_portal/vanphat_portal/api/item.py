"""Whitelisted Item & Master Catalog APIs for Van Phat Portal (S5/S6: login-only, truthful).

Provides high-performance, strictly mapped ERPNext Native item catalog data
and associated 2-tier Bill of Materials (BOM) for the minimalist industrial cockpit.
DB trống → [] (truthful, không CSV fallback).
"""

import frappe


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


@frappe.whitelist()
def get_list(query=None, item_group=None, supply_type=None, category=None, page=1, page_length=15):
	"""P3 full-server: filters + or_filters like + start/page_length + db.count.

	Docs: frappe.db.get_list(doctype, filters, or_filters, fields, order_by, start,
	page_length) tự áp permission (https://docs.frappe.io/framework/user/en/api/database).
	DB lọc, vỏ chỉ hiển thị — không lấy thừa + filter Python.
	"""
	import math
	q = (query or "").strip()
	grp = (item_group or "").strip()
	supply = (supply_type or "").strip()
	cat = (category or "").strip().lower()
	p = max(1, int(page or 1))
	pl = min(100, max(1, int(page_length or 15)))

	# S3: key chứa MỌI params (tab/cat/grp/supply/q/page/pl) — key cũ thiếu q gây stale cross-filter
	cache_key = f"vp:items:list|tab={cat}|grp={grp}|supply={supply}|q={q.lower()}|page={p}|pl={pl}"
	try:
		cached = frappe.cache().get_value(cache_key)
		if cached:
			return cached
	except Exception:
		pass

	fields = [
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
	filters = {}
	if grp:
		filters["item_group"] = grp
	if supply:
		filters["default_material_request_type"] = supply
	# category cockpit → điều kiện native (prefix mã + item_group), S9 chuyển Item Group filter khi có data
	if cat == "sp":
		filters["item_code"] = ["like", "TP-%"]
	elif cat == "btp":
		filters["item_code"] = ["like", "BTP-%"]
	elif cat == "nvl":
		filters["item_code"] = ["like", "NVL-%"]
	elif cat == "truc":
		filters["item_code"] = ["like", "TRUC-%"]
	or_filters = None
	if q:
		like = f"%{q}%"
		or_filters = [
			["Item", "item_code", "like", like],
			["Item", "item_name", "like", like],
			["Item", "custom_alias", "like", like],
			["Item", "customer_code", "like", like],
			["Item", "custom_structure_layers", "like", like],
			["Item", "description", "like", like],
		]

	# S5: db.get_list tôn trọng permission (không get_all bypass); lỗi DB → [] truthful
	items = frappe.db.get_list(
		"Item",
		fields=fields,
		filters=filters or None,
		or_filters=or_filters,
		order_by="modified desc",
		start=(p - 1) * pl,
		page_length=pl,
	)
	total_count = frappe.db.count("Item", filters) if not or_filters else None
	if total_count is None:
		# có q: count cùng điều kiện bằng qb (get_list không trả total)
		total_count = _count_items(filters, like if q else None)
	total_pages = max(1, math.ceil(total_count / pl)) if total_count else 1

	res = {
		"items": items,
		"page": p,
		"page_length": pl,
		"total_count": total_count,
		"total_pages": total_pages,
	}

	try:
		frappe.cache().set_value(cache_key, res, expires_in_sec=300)
	except Exception:
		pass

	return res


def _count_items(filters, like=None):
	"""Đếm Item cùng điều kiện get_list (dùng khi có or_filters)."""
	IT = frappe.qb.DocType("Item")
	qb = frappe.qb.from_(IT).select(frappe.query_builder.functions.Count("*").as_("c"))
	for k, v in (filters or {}).items():
		if isinstance(v, (list, tuple)) and len(v) == 2 and str(v[0]).lower() == "like":
			qb = qb.where(getattr(IT, k).like(v[1]))
		else:
			qb = qb.where(getattr(IT, k) == v)
	if like:
		cond = None
		for col in ["item_code", "item_name", "custom_alias", "customer_code", "custom_structure_layers", "description"]:
			c = getattr(IT, col).like(like)
			cond = c if cond is None else (cond | c)
		qb = qb.where(cond)
	try:
		rows = qb.run(as_dict=True)
		return int(rows[0].get("c") or 0) if rows else 0
	except Exception:
		return 0


@frappe.whitelist()
def get_detail(item_code):
	"""Return item specification and associated BOM details for the slide-over drawer.

	S5/S6: login + permission check; không CSV fallback — DB trống → throw truthful.
	"""
	code = (item_code or "").strip()
	if not code:
		frappe.throw("Thiếu item_code")
	if not frappe.db.exists("Item", code):
		frappe.throw(f"Không tìm thấy mặt hàng {code}", frappe.DoesNotExistError)

	item = frappe.get_doc("Item", code)
	if not frappe.has_permission("Item", "read", item):
		frappe.throw("Không có quyền xem mặt hàng.", frappe.PermissionError)
	item = item.as_dict()
	bom = None

	default_bom = frappe.db.get_value("BOM", {"item": code, "is_default": 1, "is_active": 1}, "name")
	if not default_bom:
		default_bom = frappe.db.get_value("BOM", {"item": code, "is_active": 1}, "name")
	if default_bom:
		bom_doc = frappe.get_doc("BOM", default_bom)
		if not frappe.has_permission("BOM", "read", bom_doc):
			frappe.throw("Không có quyền xem định mức.", frappe.PermissionError)
		bom_items = []
		for bi in bom_doc.items:
			bi_dict = bi.as_dict()
			alias = frappe.db.get_value("Item", bi.item_code, "custom_alias")
			bi_dict["custom_alias"] = alias or bi.item_name or bi.item_code
			bom_items.append(bi_dict)
		bom = {
			"master": bom_doc.as_dict(),
			"items": bom_items
		}
	return {"item": item, "bom": bom}
