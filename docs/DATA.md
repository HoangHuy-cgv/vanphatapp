# DATA

Source: `data/clean-data/*.csv` (import via `scripts/import_master_data.py`). Counts: xem CSV trực tiếp (code là truth — không ghi số cứng ở đây).

## Item Groups (10, native tree)

Cuộn Màng Ghép BTP · Hóa Chất & Keo Ghép · Màng In Ống Đồng · Màng Thô NVL · Phế Liệu Thu Hồi · Phụ Kiện Bao Bì · Trục In Ống Đồng · Túi Màng Ghép Đặt Riêng · Túi Màng Đơn · Túi Nước Giặt Có Sẵn (NGCS)

Prefixes: TP- (custom pouch, 1 customer each) · BTP- (roll; only sellers `is_sales_item=1`) · NGCS- (stock pouch, multi-customer via `custom_screen_print_brand`) · TMD- (single-film, outsourced) · NVL- (raw) · TRUC- (cylinder asset).

## UOM (5)

Túi (whole) · Kg · m · Cây (whole) · Cái (fractional allowed — carton pro-rata e.g. 2.5).

## Key native fields

- Customer: `customer_name` (legal), `alias` (cockpit), `payment_terms` (deposit terms; Trả sau ⟺ 0% portion + Credit Limit), `customer_items` child table (TP exclusivity: 1 TP = 1 customer).
- Item: `customer_code` (native-joined variant code), `custom_alias`, `custom_structure_layers` (e.g. `PET/PA/PE`), `custom_print_tech` (Select), `custom_accessory_spec` (Select), `min_order_qty`.
- Sales Order Item: `custom_screen_print_brand` (NGCS brand print).
- Naming: masters `KH-.#####`, `NCC-.#####`, `TRUC-{Mã laser NCC}` (no reset); transactions `PREFIX-.YY..MM.-.###` (monthly reset): `BG-` `DH-` `MH-` `LSX-` `GH-` `NH-` `HD-` `PT-` `PC-`.

## Rules

- Never invent schema. Custom field only when native proven absent + ADR + this file entry.
- Full EN↔VI field tables: `specs/erpnext-fields.md` (reference, load on demand).
- Packaging math (GSM/yield/pouch areas/glue/scrap, 2-tier quote, cylinder isolation): `specs/packaging-math.md` (R&D constants — NOT native).
