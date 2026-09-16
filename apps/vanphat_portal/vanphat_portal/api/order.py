"""Dedicated Order Management & Sales Order Lifecycle APIs for Van Phat Portal.

Wrapper mỏng giữ dotted path `vanphat_portal.api.order.*` (Task 6a/6b/6c):
- `order_pricing` — giá doc-driven, preview core, % cọc, hạn mức, phân loại, status.
- `order_queries` — list/detail (read).
- `order_actions` — cọc/duyệt/submit/tạo đơn (write).

Nguyên tắc tiền (ADR-002 + ADR-006 + AGENTS.md) — MỘT ngữ nghĩa duy nhất mọi màn:
xem `order_pricing`. Không logic mới ở file này.
"""

import frappe  # noqa: F401 (giữ import cho caller cũ nếu cần)

from vanphat_portal.api._guards import require_doc
from vanphat_portal.api.order_actions import (
	accountant_approve_procurement as _act_approve,
	create_sales_order as _act_create,
	make_order_from_quotation as _act_make,
	record_order_deposit as _act_deposit,
	submit_sales_order as _act_submit,
	_get_sales_order,
)
from vanphat_portal.api.order_pricing import (
	_credit_limit,
	_credit_limit_map,
	_cylinder_item_name,
	_cylinder_spec_state,
	_default_deposit_pct,
	_deposit_pct_from_template,
	_deposit_pct_map,
	_get_deposit_pct,
	_is_cylinder_line,
	_item_product_group,
	_order_product_group,
	_order_status,
	_order_tab,
	_order_tab_of_group,
	_price_via_doc,
	_required_deposit,
	_resolve_tax_template,
	DEFAULT_ORDER_NAMING_SERIES,
	SETTINGS_DOCTYPE,
	price_preview_data,
)
from vanphat_portal.api.order_queries import (
	_customer_alias,
	_customer_alias_map,
	_first_item_fields,
	_order_lifecycle,
	_order_lines_for,
	get_order_details as _qry_details,
	list_orders as _qry_list,
)


@frappe.whitelist()
def get_price_preview(
	payload=None,
	items=None,
	customer=None,
	has_new_cylinders=False,
	cylinder_count=0,
	cylinder_spec=None,
	company=None,
):
	"""Preview giá doc-driven — wrapper giữ path, core ở `order_pricing`."""
	require_doc("Sales Order", "read")
	return price_preview_data(
		payload=payload,
		items=items,
		customer=customer,
		has_new_cylinders=has_new_cylinders,
		cylinder_count=cylinder_count,
		cylinder_spec=cylinder_spec,
		company=company,
	)


@frappe.whitelist()
def list_orders(tab=None, query=None, page=1, page_length=15):
	"""Danh sách đơn — wrapper giữ path, core ở `order_queries`."""
	return _qry_list(tab=tab, query=query, page=page, page_length=page_length)


@frappe.whitelist()
def get_order_details(name):
	"""Chi tiết đơn — wrapper giữ path, core ở `order_queries`."""
	return _qry_details(name)


@frappe.whitelist()
def record_order_deposit(name, amount=0, note=""):
	"""Ghi nhận cọc (chỉ Kế toán) — wrapper giữ path, core ở `order_actions`."""
	return _act_deposit(name, amount=amount, note=note)


@frappe.whitelist()
def accountant_approve_procurement(name, note=""):
	"""Kế toán duyệt ngoại lệ HOLD — wrapper giữ path, core ở `order_actions`."""
	return _act_approve(name, note=note)


@frappe.whitelist()
def submit_sales_order(name):
	"""Sales kích hoạt đơn đủ cọc — wrapper giữ path, core ở `order_actions`."""
	return _act_submit(name)


@frappe.whitelist()
def create_sales_order(payload):
	"""Tạo đơn — wrapper giữ path, core ở `order_actions`."""
	return _act_create(payload)


@frappe.whitelist()
def make_order_from_quotation(name, naming_series=None, delivery_date=None):
	"""Tạo đơn từ báo giá — wrapper giữ path, core ở `order_actions`."""
	return _act_make(name, naming_series=naming_series, delivery_date=delivery_date)
