# ADR-002: Fallback hằng số thương mại khi native chưa cấu hình (S9)

## Status
Accepted (2026-09-14)

## Date
2026-09-14

## Context
S9 native-first yêu cầu VAT/cọc/trục lấy từ ERPNext native:
- VAT 8% → `Sales Taxes and Charges Template` theo Company.
- Giá trục 3.1M → `Item Price` của mã `TRUC-` (selling).
- Cọc 50% → `Payment Terms Template` (`invoice_portion` dòng đầu) của Customer.
- Trả sau/cọc 0đ → `Customer Credit Limit` (đã dùng từ S1).

Thực tế staging/production hiện tại chưa chắc đã có đủ 3 native trên
(template thuế mặc định, bảng giá trục, payment terms từng KH).
Không được để API vỡ khi thiếu cấu hình — phải fallback có kiểm soát.

## Decision
- Lookup native trước (`order._get_vat_rate/_get_cylinder_rate/_get_deposit_pct`), `try/except` mọi lỗi → fallback:
  - `FALLBACK_VAT_RATE = 8.0`, `FALLBACK_CYLINDER_RATE = 3.1M`, `FALLBACK_DEPOSIT_PCT = 0.5`.
- Fallback giữ đúng số cũ S1–S8 (behavior không đổi khi native trống) — S9 chỉ thêm đường lookup, không đổi số mặc định.
- `get_price_preview` trả thêm `deposit_pct` (%) để client hiển thị đúng khi template cọc khác 50%.
- Hằng số engine công nghệ (`DENSITIES/PRICES/SETUP_FIXED/BOX_COST/GLUE_COST`, scrap 8%/6.5%/5.5%, surplus `*0.5`) KHÔNG native hóa — là định mức xưởng, không có DocType native tương ứng; giữ nguyên có ghi chú.

## Alternatives Considered
- **Bắt buộc cấu hình native, không fallback (throw khi thiếu)**: Pros — ép sạch data. Cons — vỡ portal trên site chưa setup, Sếp/Kế toán chưa kịp nhập template. Rejected.
- **Giữ hardcode, không lookup**: Pros — đơn giản. Cons — đi ngược native-first, đổi thuế/cọc phải sửa code + deploy. Rejected.

## Consequences
- Khi Kế toán cấu hình đủ template + Item Price, portal tự dùng số native, không cần deploy.
- Cần 1 checklist setup native cho site mới (Sales Taxes Template mặc định, Price List trục, Payment Terms KH).
- `calculate_packaging_quotation` (`cylinder_unit_price=3.5M` default) chưa đụng — engine R&D, S9-phạm-vi sau khi chốt Item Price trục chuẩn (3.1M vs 3.5M lệch, cần Sếp chốt).
