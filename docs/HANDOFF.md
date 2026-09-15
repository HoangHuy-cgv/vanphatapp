# HANDOFF — session close 2026-09-15

Commit mới nhất: `0a10064` (cleanup + simplify). Cây sạch. GATE PASS.

## Đã làm session này

1. Audit `AGENTS.md` + interview Sếp → commit `5d1f4ef` (ask/decide split, skill map, confusion protocol, checkpoint 75%).
2. Dọn sâu (Sếp chọn): xóa 9 script một-lần (`extract_*`, `generate_*`, `browser-test.mjs`, `setup-vps-lightsail.sh`), `data/raw-data` (15M xlsx), `archive/audit-upstream` (272M, ignored). Local 627M → 341M.
3. Simplify `order.py`: gộp công thức HOLD/cọc lặp 3 nơi thành `_required_deposit` + `_order_status` + `_order_detail_status`. Tests 48 → 54. Baseline ratchet cập nhật 54.
4. VPS: không có gì dọn (disk 16%, không dangling); `apt-get clean` gỡ 232M cache. Prod giữ nguyên — Sếp chưa ra lệnh deploy.

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
- p95 mới nhất: list 213ms / detail 302ms qua tunnel; 13ms in-VPS.
