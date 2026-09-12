import frappe

no_cache = 1


def get_context(context):
	if frappe.session.user and frappe.session.user != "Guest":
		redirect_to = None
		if hasattr(frappe.local, "request") and frappe.local.request:
			redirect_to = frappe.local.request.args.get("redirect-to")
		redirect_to = redirect_to or "/app"
		frappe.local.flags.redirect_location = redirect_to
		raise frappe.Redirect
	context.no_cache = 1
