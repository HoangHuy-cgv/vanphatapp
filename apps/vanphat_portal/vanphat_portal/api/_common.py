"""Helper dùng chung cho các wrapper native `vanphat_portal.api.*`.

SSOT cho 3 việc lặp lại ở mọi module danh sách:
1. Chuẩn hóa phân trang (spec §3: mặc định 15, trần 100, sàn 1).
2. Dựng response phân trang thống nhất (`<key>`, page, page_length, total_count, total_pages).
3. Phân giải Customer id/alias/customer_name → `name` native.

Không chứa toán tiền/thuế, không whitelist, không nghiệp vụ mới (ADR-002 giữ nguyên).
"""

import math

import frappe

DEFAULT_PAGE_LENGTH = 15
MAX_PAGE_LENGTH = 100


def text(value):
	"""Chuẩn hóa tham số chuỗi từ HTTP: None/khác kiểu → '' (đã strip)."""
	return str(value or "").strip()


def as_json(value):
	"""Tham số có thể là JSON string (client cũ) hoặc object sẵn."""
	return frappe.parse_json(value) if isinstance(value, str) else value


def paginate(page=None, page_length=None, default=DEFAULT_PAGE_LENGTH, maximum=MAX_PAGE_LENGTH):
	"""Trả `(page, page_length, start)` đã kẹp biên."""
	p = max(1, int(page or 1))
	pl = min(maximum, max(1, int(page_length or default)))
	return p, pl, (p - 1) * pl


def page_result(key, rows, page, page_length, total_count):
	"""Response phân trang thống nhất cho mọi list API."""
	total = int(total_count or 0)
	return {
		key: rows,
		"page": page,
		"page_length": page_length,
		"total_count": total,
		"total_pages": max(1, math.ceil(total / page_length)) if total else 1,
	}


def resolve_customer(customer):
	"""id/alias/customer_name → `name` native Customer. Không thấy/lỗi DB → None."""
	if not customer:
		return None
	try:
		if frappe.db.exists("Customer", customer):
			return customer
		return frappe.db.get_value("Customer", {"alias": customer}, "name") or frappe.db.get_value(
			"Customer", {"customer_name": customer}, "name"
		)
	except Exception:
		return None
