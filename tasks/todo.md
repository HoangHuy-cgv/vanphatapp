# Ephemeral Todo — Simplify backend API xong

## Done
- Harness `frappe` giả + 41 test đặc tả (không cần bench).
- `_common.py` gom helper; order/item/bao_gia/customer/supplier/user hết lặp + hết N+1.
- Tiền native thống nhất (trục chưa VAT, qty bỏ trục), POST tự commit, bỏ hằng số chết.
- Drawer dùng `product_total`; build + budget gate PASS.

## Chờ Sếp (thứ tự trong tasks/plan.md)
- Bench staging đo p95 thật; role check/permission nhánh qb; phân loại TMD; mốc HOLD list.
