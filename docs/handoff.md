# Handoff — Fix hook xong, commit 43d04c8 (SSOT rolling, <25 dòng)

> Commit: `43d04c8` hook check-only + CSV LF gốc (tiếp `64dba7c`).
> Quy ước: Sếp/em, tiếng Việt. Không `git push` khi chưa lệnh.

- Gốc xung đột: DictWriter mặc định \r\n → 8 script thêm lineterminator.
- Hook --fix=no + ruff bỏ --fix (check-only); policy bypass vào AGENTS.md.
- Verify: CR 0/0, commit 1 lần sạch (hết rolling back stash).
- Mock: http://127.0.0.1:8080/portal (log /tmp/portal-server.log).
- Còn: bench staging ERPNext thật + `git push` (chờ lệnh Sếp).
