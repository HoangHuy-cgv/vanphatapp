import frappe

no_cache = 1


def get_context(context):
	if frappe.session.user and frappe.session.user != "Guest":
		# TRIỆT ĐỂ desk redirect (Sếp chốt 2026-09-16): redirect-to chỉ nhận
		# đúng /portal hoặc path con /portal/...; reject "..", backslash,
		# //evil, http... Kín cả traversal /portal/../desk.
		redirect_to = None
		if hasattr(frappe.local, "request") and frappe.local.request:
			redirect_to = frappe.local.request.args.get("redirect-to")
		if not redirect_to or "\\" in redirect_to or ".." in redirect_to:
			redirect_to = "/portal"
		elif not (redirect_to == "/portal" or redirect_to.startswith("/portal/")):
			redirect_to = "/portal"
		frappe.local.flags.redirect_location = redirect_to
		raise frappe.Redirect
	context.no_cache = 1
