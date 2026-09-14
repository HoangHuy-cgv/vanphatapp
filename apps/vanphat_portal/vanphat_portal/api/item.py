"""Whitelisted Item & Master Catalog APIs for Van Phat Portal.

Provides high-performance, strictly mapped ERPNext Native item catalog data
and associated 2-tier Bill of Materials (BOM) for the minimalist industrial cockpit.
"""

import os
import csv
import frappe

CLEAN_DATA_DIR = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "../../../..", "data", "clean-data")
)


def _load_csv_items():
	csv_path = os.path.join(CLEAN_DATA_DIR, "item_master.csv")
	if not os.path.exists(csv_path):
		return []
	with open(csv_path, mode="r", encoding="utf-8-sig") as f:
		reader = csv.DictReader(f)
		return list(reader)


def _load_csv_boms():
	boms_path = os.path.join(CLEAN_DATA_DIR, "bom_master.csv")
	items_path = os.path.join(CLEAN_DATA_DIR, "bom_items.csv")
	if not os.path.exists(boms_path) or not os.path.exists(items_path):
		return {}

	bom_tree = {}
	with open(boms_path, mode="r", encoding="utf-8-sig") as f:
		for row in csv.DictReader(f):
			bom_tree[row.get("bom_no")] = {
				"master": row,
				"items": []
			}

	with open(items_path, mode="r", encoding="utf-8-sig") as f:
		for row in csv.DictReader(f):
			b_no = row.get("bom_no")
			if b_no in bom_tree:
				bom_tree[b_no]["items"].append(row)

	return bom_tree


@frappe.whitelist(allow_guest=True)
def clear_catalog_cache(*args, **kwargs):
	"""Clear Redis cache for Van Phat Master Catalog."""
	try:
		frappe.cache().delete_keys("vanphat:catalog:*")
	except Exception:
		pass
	return {"success": True}


@frappe.whitelist(allow_guest=True)
def get_list(query=None, item_group=None, supply_type=None, category=None, page=1, page_length=15):
	"""Return master items filtered by query string, item group, supply type, or cockpit category with Redis cache and pagination."""
	import math
	q = (query or "").strip().lower()
	grp = (item_group or "").strip()
	supply = (supply_type or "").strip()
	cat = (category or "").strip().lower()
	p = max(1, int(page or 1))
	pl = max(1, int(page_length or 15))

	cache_key = f"vanphat:catalog:{cat}:{grp}:{supply}:{p}:{pl}" if not q else None
	if cache_key:
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
	try:
		filters = {}
		if grp:
			filters["item_group"] = grp
		if supply:
			filters["default_material_request_type"] = supply

		raw_items = frappe.get_list(
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
			limit=500
		)
	except Exception:
		raw_items = _load_csv_items()
		if grp:
			raw_items = [it for it in raw_items if it.get("item_group") == grp]
		if supply:
			raw_items = [it for it in raw_items if it.get("default_material_request_type") == supply]

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

	if cache_key:
		try:
			frappe.cache().set_value(cache_key, res, expires_in_sec=300)
		except Exception:
			pass

	return res


@frappe.whitelist(allow_guest=True)
def get_detail(item_code):
	"""Return item specification and associated BOM details for the slide-over drawer."""
	code = (item_code or "").strip()
	if not code:
		frappe.throw("Thiếu item_code")

	# Try fetching from DB
	item = None
	bom = None

	try:
		if frappe.db.exists("Item", code):
			item = frappe.get_doc("Item", code).as_dict()
			default_bom = frappe.db.get_value("BOM", {"item": code, "is_default": 1, "is_active": 1}, "name")
			if not default_bom:
				default_bom = frappe.db.get_value("BOM", {"item": code, "is_active": 1}, "name")
			if default_bom:
				bom_doc = frappe.get_doc("BOM", default_bom)
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
	except Exception:
		pass

	# Fall back to clean-data CSV
	csv_items = _load_csv_items()
	items_map = {it.get("item_code"): it.get("custom_alias") for it in csv_items}
	for it in csv_items:
		if it.get("item_code") == code:
			item = it
			break

	if not item:
		frappe.throw(f"Không tìm thấy mặt hàng {code}", frappe.DoesNotExistError)

	bom_tree = _load_csv_boms()
	for b_no, b in bom_tree.items():
		if b["master"].get("item") == code:
			for bi in b.get("items", []):
				if not bi.get("custom_alias"):
					bi["custom_alias"] = items_map.get(bi.get("item_code")) or bi.get("item_name")
			bom = b
			break

	return {"item": item, "bom": bom}
