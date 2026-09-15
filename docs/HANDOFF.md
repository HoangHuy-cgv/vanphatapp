# HANDOFF — session close 2026-09-16

Commit mới nhất: `2446188`. Cây sạch. GATE PASS. Tests 54.

## Đã làm session này

1. Audit `AGENTS.md` + interview Sếp → `5d1f4ef` (ask/decide split, skill map, confusion protocol, checkpoint 75%).
2. Dọn sâu local (Sếp chọn Dọn sâu): xóa 9 script một-lần, `data/raw-data` (15M), `archive/audit-upstream` (272M). Local 627M → 341M → `0a10064`.
3. Simplify `order.py`: gộp công thức HOLD/cọc thành `_required_deposit` + `_order_status` + `_order_detail_status`. Tests 48 → 54.
4. Đồng bộ VPS theo local HEAD: sync `apps/`+`tests/`+`scripts/`, xóa 9 script stale + 5 CSV stale, restart containers — code mới đã chạy (`_required_deposit` grep=4, `list_orders` OK).
5. Xóa 15 SO seed `DH-2609-001→015` trên VPS (Sếp chốt: VPS trống đơn, chỉ giữ danh mục). `list_orders.total_count=0`. Masters intact: Items 293, Customers 117, Suppliers 14, BOMs 68, Users 13.
6. VPS disk 16%, `apt-get clean` gỡ 232M cache. Không wipe DB/site (Sếp đổi ý → chỉ xóa đơn).

## Tồn đọng (theo docs/BACKLOG.md, Sếp pick 1)

1. **2-step deposit flow** — Sales request → Accounting confirm (hiện Accounting-only `record_order_deposit`).
2. **Vitest** — blocked: no npm registry + unwritable `~/.npm`.
3. **Transmission optimization** — Argo/PoP/edge cache/split detail (queries đã tối ưu, 7 queries/page).

## Standing debts

- BTP `is_sales_item`, MST gaps, retail rolls chưa mã, TMD classification, golden engine tests.
- Frontend tests 0/8, axe chưa cài, remote + push chưa cấu hình.
- KNOWN test: `_item_product_group("TMD-...", "Túi nilon HD...")` → "Túi màng ghép" (cần Sếp chốt phân loại TMD).

## Lưu ý session sau

- Code-first SSOT: code thắng khi lệch docs. Docs mới tiếng Anh tối giản.
- Không đọc `archive/`. Không `git push` khi chưa có lệnh.
- p95 mới nhất: list 213ms / detail 302ms qua tunnel; 13ms in-VPS (đo lúc còn 15 SO seed — seed đã xóa).
- Xóa đơn seed dùng SQL trực tiếp (delete_doc via bench execute không ăn); đơn thật sau này phải cancel+delete chuẩn.
