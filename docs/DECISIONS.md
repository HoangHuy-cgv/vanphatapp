# DECISIONS (ADR index — newest first)

| ID | Date | Decision | Status |
|---|---|---|---|
| 6 | 2026-09-15 | Single money/HOLD/envelope/fetch semantics | Accepted |
| 5 | 2026-09-14 | Config native = UI SSOT; visual-only custom; defer Studio; no `www.list` for SO until `frappe#42640` fixed | Accepted |
| 4 | 2026-09-15 | Prepaid/postpaid from `payment_terms`; native NCC/Item fields; TP variant → `customer_items` child table | Accepted (supplement) |
| 3 | 2026-09-15 | Drawers = native `<dialog>` (`BaseDrawer`); modals/toast = frappe-ui; no `tabindex` on `<dialog>` | Accepted |
| 2 | 2026-09-15 | VAT doc-driven; cylinder supplier pass-through (no fixed fallback); R&D engine constants stay custom | Accepted |
| 1 | 2026-09-14 | Status = Vietnamese text + color (never color alone), contrast ≥ 4.5:1 | Accepted |

Full rationale: `docs/decisions/ADR-001..006-*.md` (immutable history — never delete; supersede via new ADR).
Reopen Studio only when: tagged release + production docs, frappe-ui v1, real docs.
