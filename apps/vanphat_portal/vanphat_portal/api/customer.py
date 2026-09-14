"""Whitelisted Customer APIs for Van Phat Portal (S5/S6: login-only, truthful).

Provides strictly mapped ERPNext Native Customer master data.
Portal bắt buộc login — không guest. DB trống → [] (truthful, không CSV fallback).
"""

import frappe

from vanphat_portal.api._common import page_result, paginate, text


@frappe.whitelist()
def get_list(query=None, page=1, page_length=100):
	"""Return customers filtered by query string (code, name, alias, territory).

	ADR-006: envelope `page_result` thống nhất mọi list; picker tham chiếu
	default 100/max 100 + filter server (không tải vượt trần).
	"""
	q = text(query).lower()
	like = f"%{q}%" if q else None
	p, pl, start = paginate(page, page_length, default=100)

	filters = {"disabled": 0}
	fields = [
		"name", "customer_name", "alias", "customer_type",
		"customer_group", "territory", "payment_terms",
		"default_currency", "tax_id",
		"primary_address", "customer_primary_contact", "disabled"
	]
	or_filters = [
		["Customer", "name", "like", like],
		["Customer", "customer_name", "like", like],
		["Customer", "alias", "like", like],
		["Customer", "territory", "like", like],
		["Customer", "customer_group", "like", like],
	] if like else None
	# S5: get_list tôn trọng permission (không get_all bypass)
	rows = frappe.db.get_list("Customer", filters=filters, or_filters=or_filters, fields=fields, order_by="name asc",
		start=start, page_length=pl)
	total_count = frappe.db.count("Customer", filters)
	return page_result("customers", rows, p, pl, total_count)


@frappe.whitelist()
def get_detail(name=None):
	"""Return detailed customer information (login + permission check)."""
	if not name:
		return None
	if not frappe.db.exists("Customer", name):
		return None
	doc = frappe.get_doc("Customer", name)
	if not frappe.has_permission("Customer", "read", doc):
		frappe.throw("Không có quyền xem khách hàng.", frappe.PermissionError)
	return doc.as_dict()
