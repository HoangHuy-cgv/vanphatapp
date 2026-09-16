# ADR-002: VAT doc-driven + giá trục pass-through NCC (thay fallback số cố định)

## Status
Superseded S9 → Accepted mới (2026-09-15, Sếp duyệt)

## Date
2026-09-15

## Context
- Sếp quyết: VAT theo flow doc-driven (ERPNext tính trên chứng từ, vỏ chỉ đọc).
- Sếp quyết: giá trục KHÔNG cố định số nào (không 3.1M, không 3.5M) — trục do NCC quyết giá,
  Vạn Phát chỉ mua đi bán lại. Mọi fallback số trục trong code đều sai định hướng.
- P1+P2 đã triển khai: `_price_via_doc` dựng Quotation nháp trong memory + `cylinder_spec`
  pass-through (`d30fdd6`).

## Decision
- VAT: gán Sales Taxes and Charges Template (Default theo Company → Tax Rule theo KH) lên
  draft doc, gọi `calculate_taxes_and_totals`, đọc `total/total_taxes_and_charges/grand_total`.
  Không `round(net*rate)` tay trong flow preview/báo giá/đơn.
- Trục: API nhận `cylinder_spec {qty, unit_price, supplier}` từ vỏ (giá NCC báo).
  Thiếu giá → `cylinder_pending: true`, `grand_total_final/required_deposit_final: null`
  (truthful, vỏ hiển thị "Chờ giá NCC"). Cấm mọi hằng số/fallback giá trục trong code.
- Cọc: giữ Payment Terms Template (`invoice_portion`) + Credit Limit (Trả sau = 0đ);
  fallback 50% chỉ khi KH chưa có template (ghi log, không im lặng).
- Hằng số engine công nghệ R&D (`DENSITIES/PRICES/SETUP_FIXED/...`, scrap, surplus)
  KHÔNG native hóa — là định mức xưởng, không có DocType native tương ứng.

## Alternatives Considered
- **Fallback 3.1M khi thiếu giá NCC**: Pros — đơn luôn có số. Cons — sai sự thật
  (bán giá mình tự đặt, không phải giá NCC), Sếp bác explicitly. Rejected.
- **Lookup Item Price TRUC- duy nhất** (S9 cũ): Pros — 1 SSOT. Cons — trục nhiều giá
  tùy tình huống, 1 giá duy nhất sai bản chất. Rejected, thay bằng pass-through.

## Consequences
- Vỏ phải có ô nhập NCC + giá trục (đã có ở ModalCreateOrder P1P2).
- Cần checklist setup native cho site mới: Sales Taxes Template mặc định + Tax Rule.
- `calculate_packaging_quotation` (engine R&D, `cylinder_unit_price` default) là việc riêng,
  xử lý khi Sếp duyệt slice engine.
