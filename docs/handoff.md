# Handoff — Cờ bán BTP xong, commit 64dba7c (SSOT rolling, <25 dòng)

> Commit: `64dba7c` chỉ BTP-00015 bán cuộn (tiếp `715d60d`).
> Quy ước: Sếp/em, tiếng Việt. Không `git push` khi chưa lệnh.

- BTP-00015 Năm Tàu is_sales=1; 15 BTP còn lại input máy cắt (=0).
- Cách native (docs Item §3.13): tắt cờ chặn ở Đơn bán, không ẩn danh mục.
- Cuộn màng tiêu chưa có mã — Sếp báo sau; nguyên tắc vào masterdata-spec.
- Verify: CSV saleable [BTP-00015], input 15, dry-run sạch, compile OK.
- Mock: http://127.0.0.1:8080/portal (log /tmp/portal-server.log).
- Còn: bench staging ERPNext thật + `git push` (chờ lệnh Sếp).
