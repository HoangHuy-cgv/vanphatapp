"""Whitelisted User APIs for Van Phat Portal.

Provides strictly mapped ERPNext Native User master data.
"""

import os
import csv
import frappe

CLEAN_DATA_DIR = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "../../../..", "data", "clean-data")
)


def _load_csv_users():
	csv_path = os.path.join(CLEAN_DATA_DIR, "user_master.csv")
	if not os.path.exists(csv_path):
		return []
	with open(csv_path, mode="r", encoding="utf-8-sig") as f:
		reader = csv.DictReader(f)
		return list(reader)


@frappe.whitelist(allow_guest=True)
def get_list(query=None, department=None):
	"""Return internal system users filtered by query string and department."""
	q = (query or "").strip().lower()
	dept = (department or "").strip()

	try:
		filters = {"enabled": 1, "user_type": "System User"}
		if dept:
			filters["department"] = dept
		fields = [
			"name", "email", "first_name", "last_name", "full_name",
			"user_type", "role_profile_name", "mobile_no", "department",
			"designation", "enabled"
		]
		users = frappe.get_all("User", filters=filters, fields=fields, order_by="name asc")
		if q:
			users = [
				u for u in users
				if q in (u.get("name") or "").lower()
				or q in (u.get("full_name") or "").lower()
				or q in (u.get("email") or "").lower()
				or q in (u.get("mobile_no") or "").lower()
				or q in (u.get("department") or "").lower()
				or q in (u.get("designation") or "").lower()
				or q in (u.get("role_profile_name") or "").lower()
			]
		return users
	except Exception:
		# Fallback to CSV
		items = _load_csv_users()
		if dept:
			items = [u for u in items if u.get("department") == dept]
		if q:
			items = [
				u for u in items
				if q in (u.get("name") or "").lower()
				or q in (u.get("full_name") or "").lower()
				or q in (u.get("email") or "").lower()
				or q in (u.get("mobile_no") or "").lower()
				or q in (u.get("department") or "").lower()
				or q in (u.get("designation") or "").lower()
				or q in (u.get("role_profile_name") or "").lower()
				or q in (u.get("roles") or "").lower()
			]
		return items
