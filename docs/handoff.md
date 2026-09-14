# Handoff — Audit kiến trúc + chuẩn "tối ưu" có máy kiểm (SSOT rolling, <25 dòng)

> Nhánh `master` (đã ghim `frappe-ui 1.0.0-beta.64`) + nhánh POC `poc/no-frappe-ui`.
> Quy ước: Sếp/em, tiếng Việt. Không `git push` khi chưa lệnh (chưa có remote).

- **Chuẩn "tối ưu" giờ nằm ở `CONSTRAINTS.md`** (5 trục: Sự thật / Quyền / Kiểm chứng /
  Trọng lượng-tốc độ / Tiếp cận) + `scripts/constraints-check.py`: `floor` 0,1s (đã nối
  pre-commit), `ratchet` so với `.constraints-baseline.json`, `--init` để ghi baseline.
- **Số hôm nay:** 19/24 endpoint chưa cổng quyền · 6 chỗ `qty` cứng · 2 reduce qty ·
  1 user cứng · 1 toast thành công giả · entry 142 kB gzip · 41 test backend · 0 test frontend.
- **Lỗi production đã sửa:** thiếu `serverPricingInitial` (`useCreateOrderForm.js`) làm modal
  "Tạo đơn hàng" chết; guard `check-composables.mjs` bắt được, Chrome thật xác nhận mở/đóng được.
- **POC UI ở nhánh `poc/no-frappe-ui`:** bỏ frappe-ui, tự viết ModalShell/ToastHost/DialogHost
  trên `<dialog>` native. Đo cùng app, cùng cấu hình: **entry JS 145→49 kB gzip (-66%)**,
  **CSS 54→6 kB gzip (-89%)**, tổng js+css 241→96 kB gzip (-60%). Smoke test CDP xanh
  (boot, modal mở, Esc đóng, 0 console error). Chưa đổi lockfile; chưa port token/animation.
- **ADR-005 (2026-09-14, bằng chứng đã xác minh cùng ngày):** config native là SSOT
  của giao diện, code custom chỉ ở tầng visual; giữ Modal 1 + Drawer 2, bỏ portal list native
  cho Sales Order (frappe#42640 Open, chưa assignee, rò field permlevel + `read` ⇒ `print`);
  hoãn Studio (0 release, docs 1 trang, pin frappe-ui beta.25, issues cơ bản còn mở).
  UI spec §7/§7.1/§7.2 + DoD 13–15 chốt: không đào tạo, click-chọn, flow raw-data, config native.
- **Còn nợ:** rút config cứng trong Vue ra native (plan item 3 — vật liệu màng, nhóm SP,
  print_type, qty mặc định); 19 endpoint thiếu quyền (đang hoãn theo ý Sếp); Vitest chưa cài;
  chưa đo p95 trên bench staging; `Default Company = Bao Bì Vạn Phát` phải cấu hình ở site.
- Chi tiết đầy đủ: `tasks/plan.md` (12 mục), `CONSTRAINTS.md` (luật + ngoại lệ W1/W2).
