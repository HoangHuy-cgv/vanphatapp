# Handoff — UI tên quen xong, commit f739883 (SSOT rolling, <25 dòng)

> Commit: `f739883` ẩn mã nội bộ, hiện tên quen + mã biến thể (tiếp `7bc7f79`).
> Quy ước: Sếp/em, tiếng Việt. Không `git push` khi chưa lệnh.

- Bảng Catalog: bỏ cột TP-, tên quen alias + customer_code (888-3.2KG-HONG).
- Drawer: badge mã biến thể, hero tên quen + ref KH; mã nội bộ chỉ tooltip.
- Search server-side gõ tên nào cũng ra; tên pháp lý chỉ tooltip/hóa đơn.
- Verify: browser 404/errors 0, 15 dòng, first 888 3.2Kg Hồng + variant.
- Mock: http://127.0.0.1:8080/portal (log /tmp/portal-server.log).
- Còn: bench staging ERPNext thật + `git push` (chờ lệnh Sếp).
