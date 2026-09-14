# Handoff: Con Trỏ Vận Hành & Chuyển Giao Session

- **Mã Commit Gần Nhất**: `4de50b1` (sẵn sàng commit mới)
- **Trạng Thái CI/CD & Production Build**:
  - Python: `order.py`, `item.py`, `bao_gia.py` biên dịch 100% không lỗi.
  - Vite build: Thành công 100% (`npm run build`, bundle 73.00 kB gzip).
  - Runtime: Frappe Zero-Node production `portal.html` đồng bộ.
- **Hạng Mục Vừa Hoàn Thành**:
  - Dọn sạch 100% logic tính toán tài chính (VAT, cọc, tiền trục) khỏi Vue; chuyển sang API server `order.get_price_preview`.
  - Triệt tiêu hoàn toàn client-side tab/category filtering (`filter`, `startsWith`); chuyển thành tham số truy vấn MariaDB (`order.list_orders`, `item.get_list`).
  - Tách module độc lập `vanphat_portal.api.order` và nâng cấp router API client `useSession.js`.
  - Cập nhật điều khoản chống tái phạm nghiêm ngặt tại Mục 3 trong `AGENTS.md`.
- **Nhiệm Vụ Trọng Tâm Tiếp Theo**:
  - Triển khai Compact Pagination bar và Dual-layer Form Validation Guard theo chỉ đạo của Sếp.
