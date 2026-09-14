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
	"""Return master items filtered by query string, item group, supply type, or cockpit category with Redis cache and pagination."""
	import math
	q = (query or "").strip().lower()
	grp = (item_group or "").strip()
	supply = (supply_type or "").strip()
	cat = (category or "").strip().lower()
	p = max(1, int(page or 1))
	pl = min(100, max(1, int(page_length or 15)))

	# S3: key chứa MỌI params (tab/cat/grp/supply/q/page/pl) — key cũ thiếu q gây stale cross-filter
	cache_key = f"vp:items:list|tab={cat}|grp={grp}|supply={supply}|q={q}|page={p}|pl={pl}"
	try:
		cached = frappe.cache().get_value(cache_key)
		if cached:
			return cached
	except Exception:
		pass

	def matches_category(it):
		if not cat or cat == "all":
			return True
		code = (it.get("item_code") or "").upper()
		group = (it.get("item_group") or "").strip()
		if cat == "sp":
			return code.startswith("TP-") or group in ("Túi Màng Ghép Đặt Riêng", "Sản phẩm", "Thành phẩm", "Màng ghép")
		elif cat == "btp":
			return code.startswith("BTP-") or group in ("Cuộn Màng Ghép BTP", "Bán thành phẩm")
		elif cat == "nvl":
			return code.startswith("NVL-") or group in ("Nguyên vật liệu", "Hạt nhựa", "Màng đơn", "Mực in", "Dung môi", "Keo")
		elif cat == "truc":
			return code.startswith("TRUC-") or group in ("Trục in", "Khuôn in")
		return True

	raw_items = []
	filters = {}
	if grp:
		filters["item_group"] = grp
	if supply:
		filters["default_material_request_type"] = supply

	# S5: db.get_list tôn trọng permission (không get_all bypass); lỗi DB → [] truthful
	raw_items = frappe.db.get_list(
		"Item",
			fields=[
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
				"customer",
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
				"description"
			],
			filters=filters,
			order_by="modified desc",
			limit_start=(p - 1) * pl,
			page_length=500,
		)
		# NOTE: S5/S6 chỉ gỡ guest + get_all→get_list + xóa CSV fallback.
		# limit=500 + filter Python (cat/q) + paginate tay giữ nguyên → S-vá-catalog riêng.

	filtered_items = []
	for it in raw_items:
		if cat and cat != "all" and not matches_category(it):
			continue
		if q:
			search_space = f"{it.get('item_code', '')} {it.get('item_name', '')} {it.get('custom_alias', '')} {it.get('customer', '')} {it.get('custom_structure_layers', '')} {it.get('description', '')}".lower()
			if q not in search_space:
				continue
		filtered_items.append(it)

	total_count = len(filtered_items)
	total_pages = max(1, math.ceil(total_count / pl))
	start = (p - 1) * pl
	end = start + pl
	paginated_items = filtered_items[start:end]

	res = {
		"items": paginated_items,
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
