"""Whitelisted Supplier APIs for Van Phat Portal (S5/S6: login-only, truthful).

Provides strictly mapped ERPNext Native Supplier master data.
Portal bắt buộc login — không guest. DB trống → [] (truthful, không CSV fallback).
"""

import frappe


@frappe.whitelist()
def get_list(query=None, supplier_group=None, page=1, page_length=100):
	"""Return suppliers filtered by query string and supplier group."""
	q = (query or "").strip().lower()
	grp = (supplier_group or "").strip()
	like = f"%{q}%" if q else None

	filters = {"disabled": 0}
	if grp:
		filters["supplier_group"] = grp
	fields = [
		"name", "supplier_name", "alias", "supplier_group",
		"supplier_type", "country", "payment_terms",
		"default_currency", "tax_id", "primary_address",
		"supplier_primary_contact", "supplier_primary_phone", "disabled"
	]
	or_filters = [
		["Supplier", "name", "like", like],
		["Supplier", "supplier_name", "like", like],
		["Supplier", "alias", "like", like],
		["Supplier", "supplier_group", "like", like],
		["Supplier", "tax_id", "like", like],
	] if like else None
	# S5: get_list tôn trọng permission (không get_all bypass)
	return frappe.db.get_list("Supplier", filters=filters, or_filters=or_filters, fields=fields, order_by="name asc",
		start=(max(1, int(page or 1)) - 1) * min(100, max(1, int(page_length or 100))),
		page_length=min(100, max(1, int(page_length or 100))))


@frappe.whitelist()
def get_detail(name=None):
	"""Return detailed supplier information (login + permission check)."""
	if not name:
		return None
	if not frappe.db.exists("Supplier", name):
		return None
	doc = frappe.get_doc("Supplier", name)
	if not frappe.has_permission("Supplier", "read", doc):
		frappe.throw("Không có quyền xem nhà cung cấp.", frappe.PermissionError)
	return doc.as_dict()
