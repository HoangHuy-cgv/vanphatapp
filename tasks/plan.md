# Plan: Variant KH về native `Item.customer_items`

## Vùng legacy được chạm
- `scripts/generate_master_data_csv.py` (sinh thêm customer_items.csv)
- `scripts/import_master_data.py` (nạp bảng con + dry-run FK)
- `apps/vanphat_portal/vanphat_portal/api/item.py` (bỏ `customer` + variant phẳng → `customer_code`)
- `data/clean-data/item_master.csv` (bỏ 2 cột gộp), `data/clean-data/customer_items.csv` (mới)
- `fixtures/custom_field.json` (xóa entry variant), `mapping.md`, `masterdata-spec` (xong), `ADR-004` (thêm mục), SPEC này
- `scripts/serve-portal.mjs` (mock khớp API mới — nếu có đọc variant)

## Vùng CẤM chạm
- Mọi file Vue (variant_name trong ModalCreateOrder là tên dòng đơn tạm — giữ nguyên)
- Pricing/BOM/cache/doc_events/`custom_cylinder_code`/credit/payment

## Slice triển khai (mỏng, từng lát verify)
1. **Slice 1 — CSV + sinh liệu**: script xuất customer_items.csv (45 dòng TP, TRUC/NGCS/TMD/NVL/BTP không dòng); item_master.csv bỏ 2 cột `customer`, `custom_customer_variant_code`. Verify: đếm dòng + dry-run FK.
2. **Slice 2 — Import bench**: import_master_data.py nạp `customer_items` vào Item (1 TP = 1 dòng con), dry-run báo FK. Verify: `--dry-run` pass.
3. **Slice 3 — API native**: item.py bỏ `customer` + variant phẳng, thêm `customer_code` vào fields/search/count; get_detail giữ nguyên (as_dict kèm customer_items). Verify: py_compile + browser-test mock.
4. **Slice 4 — Tài liệu**: mapping.md + ADR-004 (thêm mục) + fixtures (xóa entry). Verify: grep = 0 reference cũ.
5. **Checkpoint**: full dry-run + build + browser-test → commit (không push).

## Rủi ro
- Bench thật chưa có ở đây → import thật do Sếp chạy staging; ở đây chỉ dry-run logic.
- `customer_code` do ERPNext tự join (fill_customer_code) — mock serve-portal phải tự join tay.
