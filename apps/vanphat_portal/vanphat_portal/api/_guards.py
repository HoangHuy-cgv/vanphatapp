"""Cổng quyền native cho `vanphat_portal.api.*` (Sếp chốt 2026-09-15).

Hướng native ERPNext (docs.frappe.io/erpnext/role-based-permissions):
1 user kiêm nhiệm nhiều role; mỗi role giữ quyền trên từng DocType trong
Role Permission Manager. Code KHÔNG tự phát minh ma trận — chỉ gọi 2 API native:
- `frappe.get_roles()` → user đang có role gì (để gác cổng hành động đặc thù).
- `frappe.has_permission(doctype, ptype, doc?)` → role + User Permissions của
  user có cho phép hành động đó trên DocType/doc đó không.

Quy ước dùng trong mọi endpoint:
- READ list/detail/preview/boot/config: `has_permission(doctype, "read")`.
  Danh sách nhạy cảm nội bộ (User): thêm `require_roles("System Manager")`.
- CREATE (tạo đơn/báo giá): `has_permission(doctype, "create")`.
- WRITE trên chứng từ (ghi cọc/xác nhận): `has_permission(doctype, "write", doc)`
  + role hành động (`Accounts User`/`Accounts Manager` hoặc `Sales User`/Manager).
- SUBMIT (submit đơn/báo giá, duyệt HOLD): `has_permission(doctype, "submit", doc)`
  + role hành động. Riêng duyệt HOLD: độc quyền Kế toán.
"""

import frappe


def require_roles(*roles):
	"""Chặn ngay nếu user hiện tại không có role nào trong danh sách.

	Một user kiêm nhiệm nhiều role: chỉ cần 1 role khớp là qua (OR).
	"""
	user_roles = set(frappe.get_roles() or [])
	if not user_roles.intersection(set(roles)):
		frappe.throw(
			"Không có quyền thực hiện thao tác này (cần role: {}).".format(", ".join(roles)),
			frappe.PermissionError,
		)
	return True


def require_doc(doctype, ptype, doc=None, name=None):
	"""Gác cổng DocType native: role + User Permissions tại nơi action.

	`doc` là object đã load (check tới cấp chứng từ); `name` là mã để check
	khi chưa load doc. Không đạt → `frappe.PermissionError` cho client toast.
	"""
	if doc is None and name:
		try:
			if frappe.db.exists(doctype, name):
				doc = frappe.get_doc(doctype, name)
		except Exception:
			doc = None
	if not frappe.has_permission(doctype, ptype, doc or name):
		frappe.throw(
			"Không có quyền {} {} {}.".format(_ptype_vi(ptype), _doctype_vi(doctype), name or ""),
			frappe.PermissionError,
		)
	return True


def _doctype_vi(doctype):
	return {
		"Sales Order": "đơn hàng",
		"Quotation": "báo giá",
		"Customer": "khách hàng",
		"Supplier": "nhà cung cấp",
		"Item": "mặt hàng",
		"BOM": "BOM",
		"User": "người dùng",
		"Payment Terms Template": "điều khoản thanh toán",
	}.get(doctype, doctype)


def _ptype_vi(ptype):
	return {
		"read": "xem",
		"write": "sửa",
		"create": "tạo",
		"submit": "duyệt",
		"cancel": "hủy",
	}.get(ptype, ptype)
