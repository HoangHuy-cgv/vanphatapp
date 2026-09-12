app_name = "vanphat_portal"
app_title = "Van Phat Portal"
app_publisher = "Van Phat"
app_description = "Visual portal shell. Business logic lives in ERPNext native only."
app_version = "0.0.1"
required_apps = ["frappe"]

# Route /login to custom login template
website_route_rules = [
	{"from_route": "/login", "to_route": "login"},
]

# Fixtures for Packaging Master Data (DocType Item Customization)
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
			["doc_type", "=", "Item"]
		]
	}
]
