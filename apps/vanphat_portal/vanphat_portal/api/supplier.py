"""Whitelisted Supplier APIs for Van Phat Portal.

Provides strictly mapped ERPNext Native Supplier master data.
"""

import os
import csv
import frappe

CLEAN_DATA_DIR = os.path.abspath(
	os.path.join(os.path.dirname(__file__), "../../../..", "data", "clean-data")
)


def _load_csv_suppliers():
	csv_path = os.path.join(CLEAN_DATA_DIR, "supplier_master.csv")
	if not os.path.exists(csv_path):
		return []
	with open(csv_path, mode="r", encoding="utf-8-sig") as f:
		reader = csv.DictReader(f)
		return list(reader)


@frappe.whitelist(allow_guest=True)
def get_list(query=None, supplier_group=None):
	"""Return suppliers filtered by query string and supplier group."""
	q = (query or "").strip().lower()
	grp = (supplier_group or "").strip()

	try:
		filters = {"disabled": 0}
		if grp:
			filters["supplier_group"] = grp
		fields = [
			"name", "supplier_name", "alias", "supplier_group",
			"supplier_type", "country", "payment_terms",
			"default_currency", "tax_id", "primary_address",
			"supplier_primary_contact", "supplier_primary_phone", "disabled"
		]
		supps = frappe.get_all("Supplier", filters=filters, fields=fields, order_by="name asc")
		if q:
			supps = [
				s for s in supps
				if q in (s.get("name") or "").lower()
				or q in (s.get("supplier_name") or "").lower()
				or q in (s.get("alias") or "").lower()
				or q in (s.get("supplier_group") or "").lower()
				or q in (s.get("tax_id") or "").lower()
			]
		return supps
	except Exception:
		# Fallback to CSV
		items = _load_csv_suppliers()
		if grp:
			items = [s for s in items if s.get("supplier_group") == grp]
		if q:
			items = [
				s for s in items
				if q in (s.get("name") or "").lower()
				or q in (s.get("supplier_name") or "").lower()
				or q in (s.get("alias") or "").lower()
				or q in (s.get("supplier_group") or "").lower()
				or q in (s.get("tax_id") or "").lower()
			]
		return items


@frappe.whitelist(allow_guest=True)
def get_detail(name=None):
	"""Return detailed supplier information."""
	if not name:
		return None

	try:
		doc = frappe.get_doc("Supplier", name)
		return doc.as_dict()
	except Exception:
		items = _load_csv_suppliers()
		for s in items:
			if s.get("name") == name or s.get("supplier_name") == name or s.get("alias") == name:
				return s
		return None
