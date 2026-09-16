# Copyright (c) 2026, Van Phat and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VanPhatSettings(Document):
	# Single config — không logic tiền ở đây, portal đọc qua get_single_value.
	pass
