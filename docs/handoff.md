# Handoff — Variant native xong, commit 7bc7f79 (SSOT rolling, <25 dòng)

> Commit: `7bc7f79` variant KH về native customer_items (tiếp `1f68ad5`).
> Quy ước: Sếp/em, tiếng Việt. Không `git push` khi chưa lệnh.

- Bỏ 2 cột gộp customer+variant khỏi item_master (293 dòng sạch).
- Mới customer_items.csv (45 TP, 1 TP = 1 KH); API search customer_code.
- Nguyên tắc ngành vào masterdata-spec: TP/BTP 1 KH; NGCS/TMD in lụa.
- Verify: dry-run FK 0 lỗi, search 888-3.2KG-HONG → TP-00001, browser sạch.
- Mock: http://127.0.0.1:8080/portal (log /tmp/portal-server.log).
- Còn: bench staging ERPNext thật + `git push` (chờ lệnh Sếp).
