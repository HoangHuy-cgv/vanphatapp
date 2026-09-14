"""Whitelisted Customer APIs for Van Phat Portal.

Provides strictly mapped ERPNext Native Customer master data.
"""

import os
import csv
import frappe

CLEAN_DATA_DIR = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "../../../..", "data", "clean-data")
)


def _load_csv_customers():
	csv_path = os.path.join(CLEAN_DATA_DIR, "customer_master.csv")
	if not os.path.exists(csv_path):
		return []
	with open(csv_path, mode="r", encoding="utf-8-sig") as f:
		reader = csv.DictReader(f)
		return list(reader)


@frappe.whitelist(allow_guest=True)
def get_list(query=None):
	"""Return customers filtered by query string (code, name, alias, territory)."""
	q = (query or "").strip().lower()

	try:
		filters = {"disabled": 0}
		fields = [
			"name", "customer_name", "alias", "customer_type",
			"customer_group", "territory", "payment_terms",
			"default_currency", "tax_id",
			"primary_address", "customer_primary_contact", "disabled"
		]
		custs = frappe.get_all("Customer", filters=filters, fields=fields, order_by="name asc")
		if q:
			custs = [
				c for c in custs
				if q in (c.get("name") or "").lower()
				or q in (c.get("customer_name") or "").lower()
				or q in (c.get("alias") or "").lower()
				or q in (c.get("territory") or "").lower()
				or q in (c.get("customer_group") or "").lower()
			]
		return custs
	except Exception:
		# Fallback to CSV
		items = _load_csv_customers()
		if q:
			items = [
				c for c in items
				if q in (c.get("name") or "").lower()
				or q in (c.get("customer_name") or "").lower()
				or q in (c.get("alias") or "").lower()
				or q in (c.get("territory") or "").lower()
				or q in (c.get("customer_group") or "").lower()
			]
		return items


@frappe.whitelist(allow_guest=True)
def get_detail(name=None):
	"""Return detailed customer information."""
	if not name:
		return None

	try:
		doc = frappe.get_doc("Customer", name)
		return doc.as_dict()
	except Exception:
		items = _load_csv_customers()
		for c in items:
			if c.get("name") == name or c.get("customer_name") == name or c.get("alias") == name:
				return c
		return None
