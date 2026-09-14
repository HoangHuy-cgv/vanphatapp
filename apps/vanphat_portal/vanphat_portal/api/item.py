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
def get_list(query=None, item_group=None, supply_type=None, category=None):
	"""Return master items filtered by query string, item group, supply type, or cockpit category."""
	q = (query or "").strip().lower()
	grp = (item_group or "").strip()
	supply = (supply_type or "").strip()
	cat = (category or "").strip().lower()

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

	# Try fetching from Frappe DB first
	try:
		filters = {}
		if grp:
			filters["item_group"] = grp
		if supply:
			filters["default_material_request_type"] = supply

		items = frappe.get_list(
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
		if cat and cat != "all":
			items = [it for it in items if matches_category(it)]
		if q:
			items = [
				it for it in items
				if q in (it.get("item_code") or "").lower()
				or q in (it.get("item_name") or "").lower()
				or q in (it.get("custom_alias") or "").lower()
				or q in (it.get("customer") or "").lower()
				or q in (it.get("custom_structure_layers") or "").lower()
			]
		if items:
			return items
	except Exception:
		# Fall back to clean-data CSV
		pass

	items = _load_csv_items()
	if grp:
		items = [it for it in items if it.get("item_group") == grp]
	if supply:
		items = [it for it in items if it.get("default_material_request_type") == supply]
	if cat and cat != "all":
		items = [it for it in items if matches_category(it)]
	if q:
		items = [
			it for it in items
			if q in (it.get("item_code") or "").lower()
			or q in (it.get("item_name") or "").lower()
			or q in (it.get("custom_alias") or "").lower()
			or q in (it.get("customer") or "").lower()
			or q in (it.get("custom_structure_layers") or "").lower()
		]

	return items


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
