# Plan: Extract raw-data → CSV nguồn ERPNext native cho app

## Objective

Đọc hiểu toàn bộ `data/raw-data/` (excel, word, google sheet, image, pdf),
tổng hợp + extract data điền vào 10 CSV template chuẩn wording ERPNext native
tại `data/templates/` (header giữ nguyên theo `scripts/import_master_data.py`),
làm nguồn input cho app. `archive/clean-data-untrusted-2026-09-15/` không đáng
tin — chỉ dùng đối chiếu header, không dùng số.

## Nguồn SSOT

- Schema + header CSV: `scripts/import_master_data.py` (`load_csv`, `ITEM_GROUPS`, `UOM_DEFINITIONS`).
- Wording field EN↔VI: `docs/specs/erpnext-fields.md`.
- Toán màng/trục/báo giá: `docs/specs/packaging-math.md` + skill `packaging-calculation-engine`.
- Phân loại hàng + quy tắc 1 TP = 1 KH: `docs/specs/packaging-taxonomy.md`.
- Công cụ đọc: lệnh global `anydoc` (excel/word/PDF-text), `anydoc --ocr hosted`
  (PDF scan), subagent model ảnh (JPG).
- Google Sheet ERP-VANPHAT (đã verify sống, không hỏi lại key/link):
  key `/var/home/huy/.config/gspread/service_account.json`
  (email `google-sheet@gentle-cable-507501-d5.iam.gserviceaccount.com`,
  project `gentle-cable-507501-d5`); mở bằng `gspread.service_account()` +
  `open_by_key("1zG1Rw-KzDy0gyUwvp1mOt0d5G_YlL6T1l8cvfR-Nq00")`
  (title `Bản sao của ERP-VANPHAT 3.0`).
  Tab extract CSV: `Quotes` gid 1001698411 (3 dòng BG185373/BG694366/BG491811),
  `BagSpecs` gid 772689383 (2 mẫu), `Customers` gid 584506154 (6 KH),
  `Suppliers` gid 143539944 (1 NCC), `RawMaterials` gid 436373666,
  `Materials` gid 1577032572, `Density` gid 1909469466,
  `MasterData` gid 1605810945.

## Task list

### Phase 1 — Template + nền (xong mới extract)

- [x] Task 0: Move clean-data cũ → `archive/clean-data-untrusted-2026-09-15/`, đẻ 10 template tại `data/templates/` (chỉ header).
  - Acceptance: `data/clean-data/` không còn; template đủ 10 header khớp import script.
  - Verify: `git status --short`, `head -n 1 data/templates/*.csv`.
  - Files: `data/templates/*.csv`.

### Checkpoint: Template

- [ ] Header khớp `import_master_data.py`, Sếp duyệt plan này.

### Phase 2 — Extract theo nhóm nguồn (song song, mỗi slice ≤5 file)

- [ ] Task 1: Excel DS KH + DS NCC → `customer_master.csv`, `supplier_master.csv` (anydoc).
  - Acceptance: tên pháp lý + alias + MST + địa chỉ có nguồn file/dòng; thiếu để trống.
  - Verify: `anydoc <file>` exit 0; CSV mở được, header nguyên.
  - Files: `data/templates/customer_master.csv`, `data/templates/supplier_master.csv`.
- [ ] Task 2: Excel MÀNG + TRỤC IN + đơn đặt màng Anh Tùng (docx) + ĐĐH SUNGDO → `item_master.csv` NVL/BTP/TRUC (anydoc).
  - Acceptance: vật liệu/khổ/dày/đơn giá/mã trục/dài/chu vi/số cây/vị trí có nguồn; không suy khổ cuộn.
  - Verify: đối chiếu `packaging-math.md` (GSM/yield), header nguyên.
  - Files: `data/templates/item_master.csv`.
- [ ] Task 3: Word/PDF-text đơn IGC (NGCS/SOFTY/TANZY/BABA/SAMRAN) + HDKT KOVA → `item_master.csv` TP/NGCS + `customer_items.csv` (anydoc).
  - Acceptance: brand/kích thước R/D/dày/đáy/dao/cấu trúc/vòi/trục có nguồn file; 1 TP = 1 KH.
  - Verify: `customer_items` 1 mã đúng 1 KH; header nguyên.
  - Files: `data/templates/item_master.csv`, `data/templates/customer_items.csv`.
- [ ] Task 4: PDF scan (Củ Chi, Thủ Đức, PET-AL-PE) → bổ sung Task 2–3 (`anydoc --ocr hosted`).
  - Acceptance: ghi rõ trang OCR + độ tin cậy; số mờ để trống.
  - Verify: exit 0/3 có log; không bịa số OCR.
- [ ] Task 5: JPG (~8 ảnh đơn + túi mẫu, subagent model ảnh) → text cấu trúc Sếp duyệt trước khi vào CSV.
  - Acceptance: mỗi ảnh có text trích + Sếp duyệt; ảnh mẫu chỉ tham khảo, không thành spec.
  - Verify: text trích lưu kèm tên ảnh; chưa duyệt chưa vào CSV.
- [ ] Task 6: Excel tồn NVL/NGCS + đơn cọc + tiến độ SX/mua hàng + thu chi → `bom_master.csv`, `bom_items.csv` (anydoc; số tồn/cọc là tham khảo, BOM chỉ từ cấu trúc đã duyệt).
  - Acceptance: BOM có nguồn cấu trúc; tồn/cọc không biến thành định mức.
  - Verify: `import_master_data.py --dry-run` FK 0 lỗi.
  - Files: `data/templates/bom_master.csv`, `data/templates/bom_items.csv`.

### Checkpoint: Extract

- [ ] 10 CSV điền từ raw-only, cột thiếu để trống + sheet `THIEU-SO.md` liệt kê số cần Sếp cấp.
- [ ] `python3 scripts/import_master_data.py --dry-run` FK 0 lỗi; `unittest` BE xanh.

### Phase 3 — Chốt nguồn input

- [ ] Task 7: Copy `data/templates/*.csv` → `data/clean-data/*.csv` (sau khi Sếp duyệt số), commit atomic.
  - Acceptance: Sếp lệnh mới copy + commit; diff cũ/mới có báo cáo.
  - Verify: `git status`, unittest + `check-composables.mjs` xanh.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| OCR/JPG đọc sai số | High | Text trích Sếp duyệt trước khi vào CSV; số mờ để trống |
| Google Sheet (đã có key/link, không hỏi lại) | Low | Dùng key + gid đã verify ở §Nguồn SSOT; thêm Task 8 extract Sheet |
| Suy luận khổ cuộn/dao | High | Cấm suy luận; thiếu = trống + xin Sếp |

## Open questions (Sếp quyết, qua ask_user_question)

- Ngưỡng duyệt text ảnh/OCR trước khi vào CSV?

- [ ] Task 8: Extract Google Sheet (key + gid đã verify, không hỏi lại) →
  đối chiếu/bổ sung `customer_master` (6 KH), `supplier_master` (1 NCC),
  `item_master` (Quotes 3 dòng + Materials + Density + MasterData danh mục),
  BagSpecs 2 mẫu (tham khảo kiểu túi).
  - Acceptance: ghi rõ nguồn tab/gid; Sheet chỉ bổ sung, raw file vẫn là gốc khi lệch.
  - Verify: `gspread.service_account()` + `open_by_key` đọc sống; header nguyên.
