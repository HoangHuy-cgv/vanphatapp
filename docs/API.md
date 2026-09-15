# API (`apps/vanphat_portal/vanphat_portal/api/`)

26 endpoints. All lists return `page_result` envelope (`{<key>, page, page_length, total_count, total_pages}`). Tx lists default 15/max 100; pickers default 100/max 100 + server filter.

## Money (single semantics, all screens)

- `net_total`/`vat_amount`/`grand_total` = native doc numbers (VAT via draft-doc `calculate_taxes_and_totals`, never hand-computed).
- `cylinder_total` = supplier pass-through price **before VAT**.
- `product_total = net_total − cylinder_total` (goods before VAT, no cylinder).
- `qty` = bag/roll lines only (no cylinder lines).
- Invariant: `product_total + cylinder_total + vat_amount = grand_total`.
- `required_deposit = product_total × deposit_pct + cylinder_total` (`0` when Trả sau; `*_final = null` when supplier price pending).
- HOLD ⟺ Trả trước AND `0 < advance_paid < required_deposit`. Trả sau never HOLD.

## Permissions (`_guards.py`)

- Reads: `require_doc(<doctype>, "read")`.
- Sales create/submit: `require_roles("Sales User", "Sales Manager", "System Manager")` + `require_doc(..., "create"/"submit")`.
- Accounting only: `require_roles("Accounts User", "Accounts Manager")` — `record_order_deposit` (write SO), `accountant_approve_procurement` (submit SO, HOLD exception).
- `user.get_list`: System Manager only (PII).
- `clear_catalog_cache`: internal (no whitelist), called by `doc_events` directly.
- `get_boot`: allowlisted (own session + CSRF only).
- Banned in user APIs: `ignore_permissions`, `get_all` on permissioned data, `allow_guest` on internal data, raw-SQL prod mutation.

## Queries

- `get_list` (permission-aware) preferred. Multi-DocType joins = one `frappe.qb` query (no N+1).
- Gotchas (bitten on prod): pypika `Table.alias` is internal attr — resolve aliases via batch `get_list`, never `.field("alias")`. `Order` imports from `frappe.query_builder`, not `frappe.qb`.
- `from frappe.query_builder import Order` for `orderby`.
- Cache: key includes roles + all params, TTL 300s, invalidated via `doc_events`.
- Fixed budget: `list_orders` = 7 queries/page (alias resolve + count + rows + tabs + lines + alias batch + deposit/limit).

## Methods

- GET reads/previews; POST creates/submits, commits itself. Errors via `frappe.throw` → `{exc, exc_type}` toast.
- `create_sales_order`: Sales roles + `require_doc(SO, "create")`; `resolve_customer`; default warehouse (finished-goods); cylinder lines only with real `TRUC-` code + supplier price (else pending, no fallback).
- Config endpoints (triple rule 2): `get_product_groups` (Item Group tree + counts + `min_order_qty`), `get_payment_options` (Payment Terms Templates; Trả sau ⟺ 0% portion), `get_print_config` (Custom Field Select options). Empty DB → truthful empty, UI hides block.

## Tests

`apps/vanphat_portal/tests/`: 48 unittest, no bench (`frappe_stub.py`). Covers money invariant, HOLD, deposit flow, role denials, warehouse default.
