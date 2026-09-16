import frappe

no_cache = 1


def get_context(context):
	if not frappe.session.user or frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/portal"
		raise frappe.Redirect
	context.no_cache = 1
	context.title = "Báo giá — Vạn Phát Portal"
	context.csrf_token = frappe.sessions.get_csrf_token()
	return context
