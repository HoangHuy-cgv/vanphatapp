# Todo: Extract raw-data → CSV nguồn ERPNext native

- [x] Task 0: Move clean-data cũ vào archive + đẻ 10 template CSV (chỉ header).
- [x] Task 1: DS KH + DS NCC → 329 KH + 69 NCC (anydoc; phân loại để trống Q8).
- [x] Task 2: MÀNG + TRỤC IN → 8 NVL màng + 155 TRUC (Q11–Q13).
- [x] Task 3: IGC + KOVA + sổ cọc + chờ SX + Sheet Orders → 21 TP + 14 NGCS + 14 TMD + CI 17 khớp (Q14/Q16/Q20/Q24).
- [x] Task 4: PDF scan OCR (PET-AL-PE + Củ Chi + Thủ Đức hosted) (Q17).
- [x] Task 5: JPG subagent ảnh 11 file (6 chứng từ vào CSV, 4 loại, 1 mờ) (Q28–Q30).
- [ ] Task 6: BOM (0 BOM — chờ Sếp chốt cấu trúc/công thức Q20/Q23/Q24/Q34).
- [x] Task 8: Sheet 22 tab dump + 4 KH + spec 2 đơn + user/permissions evidence (Q26/Q31/Q32/Q33).
- [ ] Task 7: Sếp duyệt 35 câu hỏi → copy templates sang clean-data + commit atomic.

## Checkpoint sau extract

- [x] import_master_data.py --dry-run FK 0 lỗi (221 Item, CI 17 khớp).
- [x] unittest BE xanh (số lượng xem code — không ghi số cứng).
