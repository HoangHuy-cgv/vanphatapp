"""Whitelisted User APIs for Van Phat Portal (S5/S6: login-only, truthful).

Provides strictly mapped ERPNext Native User master data.
Portal bắt buộc login — không guest. DB trống → [] (truthful, không CSV fallback).
"""

import frappe


@frappe.whitelist()
def get_list(query=None, department=None):
	"""Return internal system users filtered by query string and department."""
	q = (query or "").strip().lower()
	dept = (department or "").strip()
	like = f"%{q}%" if q else None

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
	return frappe.db.get_list("User", filters=filters, or_filters=or_filters, fields=fields, order_by="name asc")
