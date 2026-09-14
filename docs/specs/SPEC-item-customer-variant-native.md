# SPEC: Variant KH về native `Item.customer_items` (child table `Item Customer Detail`)

## 1. Objective
- Bỏ custom field phẳng `custom_customer_variant_code` (trái native-first, kẹt khi 1 mã TP bán cho 2 KH).
- Dùng native có sẵn: Item.`customer_items` (Table → `Item Customer Detail`: `customer_name` Link Customer, `customer_group` fetch, `ref_code` Data reqd=1, search_index) + Item.`customer_code` (Small Text, ERPNext tự join từ các `ref_code` qua `fill_customer_code`, dùng search).
- Ai dùng: sale tra mã biến thể KH (888-3.2KG-HONG), xưởng đối chiếu mã laser, import CSV 293 mã.
- Thành công: search variant ra đúng TP; 1 TP gắn ≥2 KH được; không còn reference `custom_customer_variant_code` trong code/CSV/mapping.

## 2. Phát hiện xác minh (không suy đoán)
- ERPNext native Item KHÔNG có field `customer`. Code ta đang select/search field `customer` ở `api/item.py:66,103,152` → vỡ trên bench thật (verify: item.json develop 135 fields, `has customer: False`).
- Native có: `customer_items` (Table→Item Customer Detail), `customer_code` (Small Text tự join, search_fields gồm `customer_code`).
- Raw-data: mã biến thể là tiếng nói của KH (888-3.2KG-HONG của DS COSMETIC trên hóa đơn/công nợ), TP-00001 chỉ nội bộ.
- NGUYÊN TẮC NGÀNH (Sếp dạy 2026-09-15, đã ghi vào masterdata-spec kịch bản 1/2/3/4): 1 mã TP/BTP chỉ bán cho đúng 1 KH (NVL là cuộn PET in theo mẫu thiết kế riêng của khách); NGCS/TMD bán nhiều KH, phân biệt bằng in lụa brandname (`custom_screen_print_brand` trên Sales Order Item). Bảng con native mỗi TP đúng 1 dòng con 1 KH.
- Cộng đồng + docs: Ref Code = "Item Code that this customer uses at their end... shown in Sales Orders" ([docs Item §3.15](https://docs.frappe.io/erpnext/item), [discuss 46792](https://discuss.frappe.io/t/item-what-the-customer-details-for/46792)).

## 3. Commands
- Sinh CSV: `python3 scripts/generate_master_data_csv.py`
- Dry-run verify: `python3 scripts/import_master_data.py --dry-run`
- Backend compile: `python3 -m py_compile apps/vanphat_portal/vanphat_portal/api/item.py scripts/import_master_data.py`
- Frontend build: `pnpm --dir apps/vanphat_portal/frontend build` (khi chạm Vue)
- Browser verify: `node scripts/browser-test.mjs` (mock serve-portal)

## 4. Project Structure (vùng chạm / không chạm)
- Chạm: `scripts/generate_master_data_csv.py` (xuất thêm customer_items.csv), `scripts/import_master_data.py` (nạp bảng con), `api/item.py` (select/search native), `mapping.md` + `masterdata-spec` + `ADR-004` (sửa), `fixtures/custom_field.json` (XÓA entry variant — native không cần fixture custom).
- KHÔNG chạm: `customer` phẳng ở API (xóa), `custom_cylinder_code` (TRUC giữ nguyên), toàn bộ Vue (`variant_name` trong ModalCreateOrder là tên dòng đơn tạm, không phải mã KH — giữ nguyên), pricing/BOM/cache/doc_events.

## 5. Code Style (mẫu thay đổi API)
```python
# CŨ (vỡ trên bench thật): fields=[..., "customer", "custom_customer_variant_code", ...]
# MỚI: get_list không join child table; search variant qua customer_code (native tự join)
fields = [..., "customer_code", ...]  # thay 2 field phẳng
or_filters = [..., ["Item", "customer_code", "like", like], ...]
# get_detail: item.as_dict() đã kèm customer_items (dòng con native); drawer đọc ref_code từng KH
```

## 6. Testing Strategy
- TDD characterization trước: script đọc item_master.csv đếm TP có variant (45) + TRUC trống variant (157) → sau refactor đếm customer_items.csv tương ứng.
- Không có bench ERPNext ở đây → verify bằng: dry-run import (FK customer tồn tại), py_compile, browser-test mock (search `888-3.2KG` ra TP-00001).
- Bench staging thật (có Frappe): Sếp chạy `bench --site <site> migrate` + import 1 TP 2 KH kiểm tra bảng con.

## 7. Boundaries
- Luôn: native-first, mapping.md SSOT, không suy đoán field.
- Hỏi trước: xóa cột CSV, đổi response API (frontend chưa dùng variant nên an toàn).
- Không: tạo custom field mới thay thế; chạm Vue/pricing/BOM; `git push` khi chưa lệnh.

## 8. Success Criteria (testable)
1. `grep -r custom_customer_variant_code --include=*.py --include=*.csv --include=*.md --include=*.json .` (trừ archive/spec lịch sử) = 0 kết quả.
2. `api/item.py` không còn `"customer"` phẳng; search dùng `customer_code`.
3. `customer_items.csv` mới: 45 dòng (TP có variant) khớp CSV cũ; dry-run FK pass.
4. `fixtures/custom_field.json` không còn entry variant (giảm 22→21).
5. mapping.md §Customer Details + masterdata-spec kịch bản 2 + ADR-004 cập nhật native.

## 9. Open Questions → Sếp đã chốt (2026-09-15, hỏi đáp từng mục)
- Q1: `customer_items.csv` header `item_code,customer_name,ref_code` (45 dòng TP) — CHỐT tách riêng.
- Q2: `customer_group` để ERPNext tự fetch khi import — CHỐT.
- Q3: ADR-004 giữ lịch sử + thêm mục superseded — CHỐT.
