"""Whitelisted User APIs for Van Phat Portal (S5/S6: login-only, truthful).

Provides strictly mapped ERPNext Native User master data.
Portal bắt buộc login — không guest. DB trống → [] (truthful, không CSV fallback).
"""

import frappe

from vanphat_portal.api._common import page_result, paginate, text
from vanphat_portal.api._guards import require_roles


@frappe.whitelist()
def get_list(query=None, department=None, page=1, page_length=100):
	"""Return internal system users filtered by query string and department.

	ADR-006: envelope `page_result` thống nhất mọi list; picker tham chiếu
	default 100/max 100 + filter server (không tải vượt trần).
	"""
	# Sếp chốt 2026-09-15: danh sách User nội bộ (email/SĐT) chỉ System Manager.
	require_roles("System Manager")
	q = text(query).lower()
	dept = text(department)
	like = f"%{q}%" if q else None
	p, pl, start = paginate(page, page_length, default=100)

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
	rows = frappe.db.get_list("User", filters=filters, or_filters=or_filters, fields=fields, order_by="name asc",
		start=start, page_length=pl)
	total_count = frappe.db.count("User", filters)
	return page_result("users", rows, p, pl, total_count)
