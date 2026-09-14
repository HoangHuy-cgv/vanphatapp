# Handoff — Simplify + tối ưu backend API (SSOT rolling, <25 dòng)

> Commit: refactor backend + harness test + drawer sync (tiếp `fdac52e`).
> Quy ước: Sếp/em, tiếng Việt. Không `git push` khi chưa lệnh (chưa có remote).

- **Lưới an toàn:** `apps/vanphat_portal/tests/` — `frappe_stub.py` + 41 test chạy
  `python3 -m unittest discover -s apps/vanphat_portal/tests -p "test_*.py"` (không cần bench).
- **Backend:** `order.list_orders` từ ~33 query/trang → **6 query cố định**; `item.get_detail`
  hết N+1 alias BOM; `get_order_details` còn 1 query Item; `bao_gia.list_quotations` count
  khớp đúng từ khóa tìm; `_common.py` gom paginate/response/`resolve_customer`/`as_json`.
- **Tiền native:** bỏ `_get_vat_rate`/`FALLBACK_VAT_RATE`; `cylinder_total` chưa VAT,
  `product_total = net_total − cylinder_total`, `qty` bỏ dòng trục; POST tự commit.
- **Thiếu Default Company → báo lỗi** (Sếp chốt): cần cấu hình Default Company = Bao Bì Vạn Phát ở site.
- **Verify:** 41/41 test xanh, ruff + pre-commit xanh, `vite build` OK, budget gate PASS (entry 145KB gzip).
- **Còn nợ (chờ Sếp):** chưa đo p95 trên bench staging; role check + permission cho nhánh qb;
  phân loại TMD ở drawer; mốc HOLD của list đang dùng `grand_total*0.5` (chưa trừ trục).
