# Plan: Backlog sau cleanup (Sếp duyệt thứ tự)

## Đã xong (commit cleanup)
- Ignore build hash-churn; entry `www/portal.html` + `public/frontend/index.html` tracked.
- `DrawerCustomerDetail` đọc bảng con native (hết liệt rỗng).
- Hook check-only + CSV LF gốc.

## Còn lại (chờ Sếp ra việc)
1. **Remote + push**: chưa có remote — Sếp cho URL + lệnh explicit.
2. **Bench staging ERPNext thật**: import 293 items + 45 dòng con + BOM; verify
   VAT doc-driven, Credit Limit, đo LCP/INP/CLS.
3. **Enforce BTP ở Đơn bán**: `is_sales_item=0` mới ở data; luồng Báo giá/Đơn bán
   portal chưa lọc cờ này.
4. **MST KH 0/117**: không xuất được hóa đơn VAT thật.
5. **0 test Python + 0 CI workflow**: mới có ruff/pre-commit.
6. **Cuộn màng tiêu**: chưa có mã — Sếp báo sau (BTP bán được hiện chỉ 00015).
