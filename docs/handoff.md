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
- **Còn nợ:** chốt stack UI (Sếp quyết theo số POC); 19 endpoint thiếu quyền (rủi ro cao nhất,
  cần Sếp chốt ai-được-làm-gì); dọn hardcode client; Vitest chưa cài (không ra được npm);
  chưa đo p95 trên bench staging; `Default Company = Bao Bì Vạn Phát` phải cấu hình ở site.
- Chi tiết đầy đủ: `tasks/plan.md` (12 mục), `CONSTRAINTS.md` (luật + ngoại lệ W1/W2).
