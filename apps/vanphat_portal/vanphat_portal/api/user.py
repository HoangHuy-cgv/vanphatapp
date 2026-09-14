"""Whitelisted User APIs for Van Phat Portal (S5/S6: login-only, truthful).

Provides strictly mapped ERPNext Native User master data.
Portal bắt buộc login — không guest. DB trống → [] (truthful, không CSV fallback).
"""

import frappe

from vanphat_portal.api._common import paginate, text


@frappe.whitelist()
def get_list(query=None, department=None, page=1, page_length=100):
	"""Return internal system users filtered by query string and department."""
	q = text(query).lower()
	dept = text(department)
	like = f"%{q}%" if q else None
	_, pl, start = paginate(page, page_length, default=100)

	filters = {"enabled": 1, "user_type": "System User"}
	if dept:
		filters["department"] = dept
	fields = [
		"name", "email", "first_name", "last_name", "full_name",
		"user_type", "role_profile_name", "mobile_no", "department",
		"designation", "enabled"
	]
	or_filters = [
		["User", "name", "like", like],
		["User", "full_name", "like", like],
		["User", "email", "like", like],
		["User", "mobile_no", "like", like],
		["User", "department", "like", like],
		["User", "designation", "like", like],
		["User", "role_profile_name", "like", like],
	] if like else None
	# S5: get_list tôn trọng permission (không get_all bypass)
	return frappe.db.get_list("User", filters=filters, or_filters=or_filters, fields=fields, order_by="name asc",
		start=start, page_length=pl)
