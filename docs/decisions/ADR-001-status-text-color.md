# ADR-001: Trạng thái chữ + màu thay cho color-alone (Pillar 3 vs WCAG 1.4.1)

## Status
Accepted (2026-09-14)

## Date
2026-09-14

## Context
Pillar 3 bản cũ quy định "Color alone classifies" — trạng thái thuần màu 14px bold, zero text/icon/box kèm theo.
Audit Phase 4 (research UX/a11y/RUM, ~10 nguồn W3C/WCAG/APG/web.dev) phát hiện:
- WCAG 2.1 SC 1.4.1 Use of Color: màu KHÔNG được là kênh duy nhất truyền thông tin — vi phạm chắc chắn rớt a11y audit, không phải gu thẩm mỹ.
- Đo thực tế `portal.css` trên nền `#161b22`: text muted `#64748b` chỉ 3.63:1 — rớt AA 4.5:1; các màu trạng thái (amber/emerald/red/sky) đều > 6:1 — đạt.
- Frontend hiện tại ĐÃ render text label tiếng Việt sẵn ("Chờ cọc", "Đã duyệt", "HOLD", "Quá hạn") — chỉ cần giữ + chuẩn hóa, không tốn layout.

## Decision
- Mọi trạng thái PHẢI có **text label tiếng Việt phân biệt + màu** theo bảng chuẩn (Amber/Sky/Emerald/Red/Tím).
- Giữ ý đồ cockpit: chữ 14px bold thuần, zero border/box/bullet/icon — chỉ thêm text (đã có sẵn), không thêm chrome.
- Text trạng thái contrast ≥ 4.5:1; màu nào rớt thì chỉnh hex, không bỏ text.
- Badge số lượng có `aria-label` (VD `aria-label="8 đơn quá hạn"`).

## Alternatives Considered
- **Giữ color-alone nguyên bản**: Pros — mật độ tối đa, đúng ý đồ gốc. Cons — vi phạm WCAG 1.4.1, rớt audit, người mù màu không dùng được. Rejected.
- **Thêm icon/box cạnh màu**: Pros — phân biệt mạnh. Cons — vỡ layout 1 dòng 42–46px, đi ngược triết lý cockpit. Rejected — text sẵn có đã đủ kênh thứ hai.

## Consequences
- Pillar 3 trong `AGENTS.md` + `ui-cockpit-baseline-spec.md` đổi thành "chữ + màu".
- UI checklist §5 cập nhật mục Pure Color Badges → Text+Color.
- Không đổi kiến trúc, không đụng math/backend boundary.
