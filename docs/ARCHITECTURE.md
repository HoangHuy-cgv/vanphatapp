# ARCHITECTURE

## Stack

Frappe/ERPNext v16.34.2 (digest-pinned image) + Vue 3.5 + Vite 7 + vue-router 4 (hash) + Tailwind v3 standalone (no external UI preset) + Native HTML5 `<dialog>` + `vue-sonner@2.0.9` (ADR-007). Zero-Node static served at `/portal`. MariaDB + Redis + Cloudflare Tunnel + R2 backup (`infra/`).

## Layers (highest capable wins)

1. ERPNext native DocType/field/method.
2. Frappe API (`get_list`, `frappe.qb`, `frappe.cache`, `has_permission`).
3. Thin `vanphat_portal.api.*` facade. No duplicated business logic.
4. `custom_*` field/DocType only when native proven absent + ADR entry + DATA.md entry.

## Modules

| Code | Native | Responsibility |
|---|---|---|
| `api/order.py` (~1000 lines) | Sales Order, Quotation, Payment Entry, Customer Credit Limit | Order lifecycle: `list_orders`, `get_order_details`, `get_price_preview`, create/record/submit/approve/make |
| `api/bao_gia.py` | Quotation, Item, File | `list_quotations`, customers search, create/submit/lost, price preview, `calculate_packaging_quotation` (R&D engine — workshop constants, NOT native), `get_boot` |
| `api/item.py` | Item, BOM | Full-server catalog, 2-tier BOM, Redis cache |
| `api/customer.py` `supplier.py` `user.py` | Customer/Supplier/User | Envelope `page_result` lists + server-filtered pickers |
| `api/_common.py` | — | `paginate`/`page_result`/`text`/`as_json`/`resolve_customer`. No whitelist, no logic, no money |
| `api/_guards.py` | — | `require_roles` (OR) + `require_doc` (`has_permission` to doc level, Vietnamese errors) |
| `frontend/src/` | — | 3 lazy views (Orders/Quotes/Catalog) + 12 components (BaseModal, ConfirmDialog, BaseDrawer, ModalCreateOrder, ModalStep1Sale, drawers, ArtworkBox) + 9 composables. Sole HTTP: `api()` in `useSession.js`. Overlays: native `<dialog>` only; toast: `vue-sonner`; Step1→Step2 contract: single `submit` event |

## Boundaries

- Portal owns ~6 flows (quote, order, deposit, workshop, delivery, lookup). Desk owns config + master data + rest.
- 1 user holds many roles; Desk Role Permission Manager + User Permissions hold the matrix; code gates at action site.
- Measured p95 2026-09-15 (fresh site, 293 Items/117 Customers/15 SOs): list 213ms / detail 302ms via tunnel; 13ms/7ms in-VPS (tunnel +~200ms, not queries). Re-measure: `scripts/measure_p95.py`.
