# BACKLOG (Sếp-ordered)

## Next (Sếp picks one)

1. **2-step deposit flow** — Sales requests → Accounting confirms (today: Accounting-only `record_order_deposit`).
2. **Vitest** — blocked: no npm registry + unwritable `~/.npm` on this machine.
3. **Transmission optimization** — Argo/closer PoP/edge cache/split detail (queries already optimal).

## Standing debts

- BTP `is_sales_item` enforcement on sell; customer MST gaps; uns coded retail rolls (only BTP-00015 sellable); TMD classification by `item_group`/prefix; golden engine tests for `calculate_packaging_quotation`.
- Frontend tests ≥ 8 composables (`fe_test_files` = 0).
- axe critical/serious = 0 (tool not installed).
- Remote + push: no remote configured.

## Done (history)

Triple-rule + 3 config endpoints → cleanup → 26-endpoint native permission gates (`api_ungated` 0) → prod wipe + fresh deploy + real p95 (list 213ms/detail 302ms, 13ms in-VPS) → doc restructure → Retire `frappe-ui` → native HTML5 `<dialog>` (`BaseModal`, `ConfirmDialog`) + `vue-sonner@2.0.9` (ADR-007; initial bundle dropped 142KB to 52KB; fixed Step 1→2 quote transition, drawer alignment, catalog action feedback, a11y labeling). Git log is the changelog.
