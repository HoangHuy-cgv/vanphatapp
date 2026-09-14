app_name = "vanphat_portal"
app_title = "Van Phat Portal"
app_publisher = "Van Phat"
app_description = "Visual portal shell. Business logic lives in ERPNext native only."
app_version = "0.0.1"
required_apps = ["frappe", "erpnext"]

# Route /login to custom login template
website_route_rules = [
	{"from_route": "/login", "to_route": "login"},
]

# Fixtures for Packaging Master Data and Naming Series
fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			["dt", "in", ["Item", "Sales Order Item"]]
		]
	},
	{
		"dt": "Property Setter",
		"filters": [
			["doc_type", "in", [
				"Item", "Quotation", "Sales Order", "Customer", "Supplier",
				"Purchase Order", "Work Order", "Delivery Note", "Purchase Receipt",
				"Sales Invoice", "Payment Entry"
			]]
		]
	}
]

# Master Data Cache Invalidation Hooks
doc_events = {
	"Item": {
		"on_update": "vanphat_portal.api.item.clear_catalog_cache",
		"on_trash": "vanphat_portal.api.item.clear_catalog_cache",
	}
}
