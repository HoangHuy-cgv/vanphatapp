# ADR-004: Phân loại KH trả trước/trả sau + field NCC/Item native (Sếp chốt 2026-09-15)

## Ngữ cảnh
Hỏi đáp Sếp chốt: backend native-first, frontend vỏ no-logic, mapping.md SSOT.
Audit 3 luồng phát hiện: `credit_limit` phẳng không phải native, `supplier_primary_phone`
không tồn tại trong ERPNext chuẩn, `customer_ref_code` custom đa nghĩa thiếu prefix.

## Quyết định
1. **KH: bỏ `credit_limit`, phân loại từ `payment_terms`.**
   `Customer` native không có field phẳng `credit_limit` (native là child table
   `Customer Credit Limit` theo Company). 115/117 KH "Cọc 50%" + 0đ = Trả trước;
   2/117 "Gối đầu 30 ngày" + hạn mức = Trả sau. CSV/UI/backend dùng `payment_terms`
   (resolve sang Payment Terms Template khi có ERPNext thật).
2. **NCC: giữ `alias` + `tax_id` (native thật), sửa phone.**
   Audit ERPNext chuẩn: `alias` (Data unique) + `tax_id` (tab Tax) đều native.
   `supplier_primary_phone` KHÔNG tồn tại → đổi sang `mobile_no` (fetch từ Contact).
   `primary_address` text staging, khi import tách DocType `Address` riêng.
3. **Item: tách `customer_ref_code` đa nghĩa.**
   TP = mã biến thể KH → `custom_customer_variant_code` mới; TRUC = mã laser NCC →
   dùng `custom_cylinder_code` chính chủ (TRUC để variant trống). Bảng alias-first,
   ref thô không lên bảng, chi tiết vào drawer.
4. **Brand/owner audit:** TP 45/45 đủ customer+variant+brand thật (brand≠chủ sở hữu,
   VD Minh Râu thuộc DS COSMETIC); NGCS/TMD/NVL/BTP trống customer/variant,
   brand là filler — UI ẩn filler, chỉ hiện brand + KH sở hữu cho TP.

## Hệ quả
- CSV tái sinh: customer (bỏ credit), supplier (mobile_no), item (variant tách).
- API: supplier select `mobile_no`; item select/search `custom_customer_variant_code`.
- UI: drawer KH Trả trước/Trả sau; drawer NCC đọc `mobile_no`; bảng KH bỏ tooltip hạn mức.
