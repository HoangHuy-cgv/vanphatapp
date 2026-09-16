# BỘ QUYẾT ĐỊNH NGHIỆP VỤ & ĐỐI SOÁT DỮ LIỆU GỐC (BUSINESS DECISIONS FAQ) — BAO BÌ VẠN PHÁT

> **Mục đích:** Nguồn chân lý duy nhất (SSOT) ghi nhận 40 quyết định chính thức của Ban Giám Đốc (Sếp chốt) để xử lý toàn bộ các điểm mờ, xung đột số liệu, quy chuẩn mã trục, cấu trúc BOM, gộp đối tác và chuẩn hóa từ vựng theo ERPNext Native v16.
> **Nguyên tắc xuyên suốt:** Dữ liệu thô (raw-data) là gốc đối chiếu. Mọi suy đoán cá nhân không có căn cứ đều bị loại bỏ. Các trường thiếu thông tin tin cậy được để trống hoặc dùng giá trị mặc định được Sếp duyệt.

---

## PHẦN I: NGUYÊN TẮC XỬ LÝ DỮ LIỆU & NGUỒN GỐC (Q01 – Q07)

### Q01: Ngưỡng duyệt dữ liệu từ văn bản ảnh / OCR trước khi đưa vào Master CSV
- **Căn cứ thực tế:** Dữ liệu từ 22 tab Google Sheet và các file scan/ảnh chụp thực tế có độ sắc nét khác nhau.
- **Quyết định của Sếp:** **Chỉ đưa vào CSV các thông tin có độ tin cậy cao** (chữ số rõ ràng, đối chiếu khớp chứng từ). Chỗ nào mờ hoặc nghi ngờ thì để trống, tuyệt đối không tự suy luận điền bừa vào Master CSV.

### Q02: Quy ước ghi chú "Bước cắt" trong Định mức sản xuất (BOM)
- **Căn cứ thực tế:** Một số tài liệu cũ ghi công thức bước cắt ≈ 1.65× dao item (khổ dao 2 lane), nhưng đây không phải quy ước áp dụng đồng loạt cho mọi túi.
- **Quyết định của Sếp:** **Chỉ khi có thông số chính xác từ phiếu sản xuất hoặc lệnh xưởng mới ghi nhận.** Hiện tại BOM không ghi chú bước cắt mặc định suy đoán.

### Q03: Quy chuẩn mã định danh Trục in ống đồng (`item_code` DocType `Item`)
- **Căn cứ thực tế:** File quản lý trục in của xưởng lưu 155 bộ trục, trong đó hầu hết mang mã khắc laser của nhà cung cấp trục (Kiến Tâm, Trang Tín...).
- **Quyết định của Sếp:** **Giữ nguyên mã laser NCC làm định danh chính thức.** Mã sản phẩm trục trên ERPNext lấy trực tiếp theo cú pháp: `TRUC-{Mã laser NCC}` (ví dụ: `TRUC-G4010806`, `TRUC-G4006940`). Không tự chế mã tăng dần vô nghĩa làm mất liên kết với quả trục vật lý tại xưởng.

### Q04: Xử lý link ảnh sai lệch trong bảng kê báo giá (Sheet BG491811)
- **Căn cứ thực tế:** Dòng báo giá sốt phô mai trong Google Sheet gắn nhầm link ảnh chuối Del Monte.
- **Quyết định của Sếp:** **Bỏ trống link ảnh** đối với dòng này. Chỉ gắn link ảnh khi hình ảnh khớp 100% với mẫu bao bì thực tế.

### Q05: Thông số kỹ thuật (Kích thước, Dao cắt, Cấu trúc màng) của 13 mã Túi NGCS
- **Căn cứ thực tế:** 13 mã Túi nước giặt có sẵn (NGCS) đã dựng tên chuẩn theo 3 size (Nhỏ, Trung, Lớn) và màu nền, nhưng chưa có phiếu đo kích thước chính thức.
- **Quyết định của Sếp:** **Giữ spec kỹ thuật trống** trong `item_master.csv`, chưa tạo BOM cho NGCS cho đến khi xưởng đo đạc và cung cấp bản vẽ thông số chính thức.

### Q06: Ranh giới sử dụng ảnh mẫu so với thông số kỹ thuật (Case Túi 888 3.2KG)
- **Căn cứ thực tế:** Từng có sự nhầm lẫn lấy kích thước túi 888 3.2KG (thành phẩm riêng của khách DS COSMETIC) áp cho túi NGCS size Lớn.
- **Quyết định của Sếp:** **Chỉ khi đọc được chính xác thông số kỹ thuật in trên hình/chứng từ của đúng mã đó mới được đưa vào spec.** Không được lấy kích thước túi đặt riêng (TP) của khách này gán sang hàng đại trà (NGCS).

### Q07: Thứ tự ưu tiên khi có xung đột dữ liệu giữa File Raw và Google Sheet
- **Căn cứ thực tế:** Có trường hợp MST hoặc tên khách hàng giữa file Excel tổng hợp nội bộ và file Hợp đồng/Đơn đặt hàng gốc bị lệch nhau.
- **Quyết định của Sếp:** **File tài liệu gốc (Raw Files: Hợp đồng PDF/Word, Đơn đặt hàng scan có chữ ký, Phiếu xuất kho) là Nguồn chân lý gốc (Ground Truth).** Google Sheet chỉ đóng vai trò bảng kê đối chiếu bổ sung.

---

## PHẦN II: KHÁCH HÀNG & NHÀ CUNG CẤP (Q08 – Q10, Q21, Q35)

### Q08: Quy chuẩn phân loại và bổ sung trường thông tin cho 329 Khách hàng
- **Căn cứ thực tế:** File Excel danh sách khách hàng raw chỉ có 8 cột cơ bản (STT, Mã, Tên, Địa chỉ, MST/CCCD, SĐT). Thiếu `customer_type`, `customer_group`, `territory`, `payment_terms`.
- **Quyết định của Sếp:** 
  - Phân loại: **297 Công ty (`Company`)** (có MST doanh nghiệp) và **32 Cá nhân (`Individual`)** (hộ kinh doanh, cá nhân, số CCCD).
  - Phân vùng `territory`: Mặc định `Việt Nam` (hoặc miền theo địa chỉ).
  - Điều khoản thanh toán `payment_terms`: Áp dụng chính sách mặc định theo nhóm khách hàng (đặt cọc trước khi sản xuất).

### Q09: Xử lý trùng lặp Nhà cung cấp và lọc bỏ các dòng phi NCC
- **Căn cứ thực tế:** Danh mục NCC raw có các dòng nội bộ hoặc chi phí dịch vụ văn phòng (`DIEN THOAI`, `EFY/BHXH`, `INTERNET`, `EZ-COC`, `KC-VECHAI`).
- **Quyết định của Sếp:** **Lọc bỏ hoàn toàn các dòng phi NCC** khỏi `supplier_master.csv`. Đối tác cung ứng vật tư, gia công được chuẩn hóa về đúng 65 nhà cung cấp thực tế.

### Q10: Xử lý đối tác trùng mã và gộp dữ liệu theo Mã số thuế (MST)
- **Căn cứ thực tế:** Khách hàng DS COSMETIC xuất hiện ở 2 dòng (`COC-888` tiền cọc và `KC-SHARK1` kèm MST 3703187371); PET UNIVERSE, DTH cũng bị lặp mã.
- **Quyết định của Sếp:** **Gộp triệt để theo Mã số thuế pháp nhân.** Dùng MST `3703187371` cho `CÔNG TY CỔ PHẦN DS COSMETIC` (mã KH duy nhất: `KH-00184`, alias: `DS COSMETIC`). Tương tự đã gộp DTH và PET UNIVERSE.

### Q21: Tiếp nhận 4 Khách hàng mới từ Sổ theo dõi cọc đơn hàng
- **Căn cứ thực tế:** Sổ cọc ghi nhận giao dịch với 4 khách hàng không có trong file Excel khách hàng cũ: CÔNG TY ANH PHÁT, CÔNG TY VIETCOAT, CÔNG TY ECO WIPES, CÔNG TY AMYCO.
- **Quyết định của Sếp:** **Thêm mới 4 khách hàng này vào Master Data** với đầy đủ thông tin pháp nhân và gán mã định danh `KH-` chuẩn ERPNext.

### Q35: Chuẩn hóa 329 Khách hàng và cơ chế Unique `customer_name` trên ERPNext
- **Căn cứ thực tế:** ERPNext v16 bắt buộc trường `customer_name` phải là duy nhất (Unique) trên toàn hệ thống. Trong file raw có trường hợp trùng tên thương mại nhưng khác chi nhánh/mã.
- **Quyết định của Sếp:** Gộp 3 alias trùng (DS COSMETIC, AMYCO, VCOS); các trường hợp trùng tên pháp lý được phân biệt bằng địa chỉ/chi nhánh để đảm bảo nạp 100% vào database ERPNext không bị chặn lỗi unique constraint.

---

## PHẦN III: TRỤC IN ỐNG ĐỒNG & TÀI SẢN XƯỞNG (Q11, Q13)

### Q11: Quản lý 155 bộ Trục in ống đồng lưu tại kho Vạn Phát và gửi tại kho NCC
- **Căn cứ thực tế:** Xưởng có 155 bộ trục in, gồm 113 bộ lưu tại kho Vạn Phát, 20 bộ gửi tại NCC Trang Tín, 17 bộ gửi tại Kiến Tâm, 4 bộ gửi tại Tuệ Nhi, và 1 bộ trả khách (`G3000042`).
- **Quyết định của Sếp:** **Nhập đủ 155 bộ trục vào hệ thống ERPNext.** Toàn bộ trục dù nằm ở kho nào vẫn là tài sản thuộc sở hữu hoặc quản lý của Vạn Phát. Vị trí lưu trữ vật lý được ghi nhận chính xác tại trường `custom_cylinder_location` (`VẠN PHÁT`, `TRANG TÍN`, `KIẾN TÂM`, `TUỆ NHI`).

### Q13: Quy chuẩn Tên gọi tắt (Alias) và Thương hiệu (Brand) của Trục in
- **Căn cứ thực tế:** File quản lý trục chỉ có quy cách dài/chu vi và tên sản phẩm, không có cột alias.
- **Quyết định của Sếp:** 
  - `custom_alias`: Đặt theo cấu trúc `Trục {Tên sản phẩm rút gọn}` ở dạng Title Case (ví dụ: `Trục Nước Giặt Sachpoong 3.2kg`, `Trục Topgia Hoa Nắng 1L`).
  - `brand`: Điền theo thương hiệu của sản phẩm bao bì tương ứng.

---

## PHẦN IV: NGUYÊN VẬT LIỆU, MÀNG GHÉP & BÁN THÀNH PHẨM (Q12, Q14, Q15, Q17, Q18, Q24, Q32, Q34, Q36)

### Q12: Danh mục Màng thô Nguyên vật liệu (NVL)
- **Căn cứ thực tế:** Bảng kê màng có nhiều dòng ghi số lượng bằng 0 (chỉ mang tính chất báo giá tham khảo).
- **Quyết định của Sếp:** **Chỉ tạo mã NVL cho 8 loại màng có giao dịch nhập kho thực tế** (PET12, MPET12, PA15, PE trong, AL6...). Các dòng số lượng 0 không tạo mã tồn kho ảo.

### Q14 & Q24: Xác định cấu trúc màng ghép từ Đơn in màng PET và Sheet Chờ sản xuất
- **Căn cứ thực tế:** Đơn hàng từ khách IGC chỉ ghi đặt in màng ngoài PET12, không ghi cấu trúc các lớp ghép bên trong. Trong khi đó, Sheet "CHỜ SẢN XUẤT" có đầy đủ thông số đối chiếu.
- **Quyết định của Sếp:** **Sử dụng cấu trúc kỹ thuật từ Sheet "CHỜ SẢN XUẤT"** để điền cấu trúc màng ghép (`custom_structure_layers`) cho các sản phẩm TP (ví dụ: BABA là `PET/MPET/PA/PE trong`, SOFIA là `PET12/MPET12/PA15/PE165`, MINH RÂU là `PET/PA/PES`).

### Q15: Quản lý Keo ghép, Chất đóng rắn và Dung môi trong NVL và BOM
- **Căn cứ thực tế:** Đơn đặt hàng SUNGDO thể hiện rõ việc mua keo ghép màng D-9822K và chất đóng rắn CL-3196K (đơn giá 78.000đ/kg).
- **Quyết định của Sếp:** **Đưa keo ghép và chất đóng rắn vào danh mục `Item` (Nhóm Hóa Chất & Keo Ghép) và cấu thành trong BOM sản xuất** để tính đúng định mức giá thành màng ghép phức hợp.

### Q17: Khai thác dữ liệu từ các tài liệu Scan OCR lỗi font (PET-AL-PE, Củ Chi, Thủ Đức)
- **Căn cứ thực tế:** File scan kỹ thuật `PET-AL-PE.pdf` bị lỗi font một số ký tự nhưng cấu trúc lớp màng hiển thị rõ.
- **Quyết định của Sếp:** **Chỉ trích xuất cấu trúc màng `PET/AL/PE`** đưa vào thông số sản phẩm; các trường kích thước không chắc chắn thì để trống chờ xác nhận.

### Q18: Xử lý mã kho nội bộ NVL (A01 đến P02)
- **Căn cứ thực tế:** Sổ kho có các mã vị trí kệ/kho như A01..P02.
- **Quyết định của Sếp:** **Mã kho nội bộ chỉ ghi vào trường `description`** để thủ kho nhận biết vị trí. Mã sản phẩm chính thức trên ERPNext bắt buộc dùng tiền tố chuẩn `NVL-#####`.

### Q32: Bảng tỷ trọng vật liệu màng (Density) chuẩn dùng trong sản xuất
- **Căn cứ thực tế:** Có sự chênh lệch nhỏ giữa tỷ trọng phòng thí nghiệm ASTM và tỷ trọng thực tế xưởng chạy trong sheet "MÀNG GHI CHÚ" (PET 1.34, PA 1.14, PES 0.93, PE trong 0.925, AL 2.7, MPET 1.4).
- **Quyết định của Sếp:** **Áp dụng bảng tỷ trọng sản xuất thực tế tại sheet "MÀNG GHI CHÚ"** làm cơ sở tính toán GSM, Yield và giá thành R&D bao bì.

### Q34 & Q36: Nguyên tắc phân loại và tạo mã Cuộn màng ghép (BTP)
- **Căn cứ thực tế:** Cuộn màng sau khi ghép có 2 mục đích: (1) Đưa thẳng sang máy cắt túi nội bộ; (2) Bán cuộn thành phẩm cho khách hàng tự đóng gói.
- **Quyết định của Sếp:** 
  - **Chỉ tạo mã `BTP-` và bật cờ bán `is_sales_item=1` đối với cuộn ghép bán trực tiếp cho khách** (hiện tại có `BTP-00015 Cuộn Năm Tàu` và cuộn màng hạt tiêu).
  - Cuộn màng ghép chạy luân chuyển nội bộ máy in → máy ghép → máy cắt thì không tạo mã thương phẩm riêng mà quản lý theo công đoạn Lệnh sản xuất.
  - Xóa bỏ các mã BTP dư thừa trước đây; 6 BOM túi TP viết lại chi tiết gồm: Màng in (m) + Màng thô (kg) + Keo/dung môi + Phụ kiện vòi.

---

## PHẦN V: THÀNH PHẨM TÚI (TP, NGCS, TMD) & QUY CÁCH (Q16, Q19, Q20, Q22, Q25, Q27 – Q30, Q37 – Q40)

### Q16 & Q40: Quy chuẩn Tên gọi tắt (Alias) và Thương hiệu (Brand) của Thành phẩm
- **Căn cứ thực tế:** Khách hàng đặt in túi độc quyền mang các thương hiệu riêng: KOVA, TOPGIA, SAMRAN, LAMY, BABA, MINH RÂU, ECO WIPES...
- **Quyết định của Sếp:**
  - Với Túi màng ghép đặt riêng (TP): `brand` = Tên thương hiệu của khách. `custom_alias` rút gọn chuẩn Title Case: `{Brand} {Dung tích} {Mẫu in}` (Ví dụ: `Minh Râu 3.2kg Hồng`, `Topgia 1L Hoa Nắng`).
  - Với Túi nước giặt có sẵn (NGCS) và Túi màng đơn (TMD): `brand` **để trống** trên Master Item vì đây là hàng phôi dùng chung; brand in lụa của từng khách được ghi nhận tại dòng đơn hàng `custom_screen_print_brand`.
  - Riêng mã `TP-00035` (Túi FUTA in không trục): `brand` để trống.

### Q19: Xử lý mã kho nội bộ túi NGCS (TUINGCS...)
- **Căn cứ thực tế:** Sổ kho có các mã gọi tắt dạng TUINGCS.
- **Quyết định của Sếp:** Mã gọi tắt đưa vào `description`. Mã sản phẩm chuẩn hóa thống nhất theo Naming Series: `NGCS-#####`.

### Q20: Sử dụng thông số kỹ thuật từ Sổ theo dõi cọc đơn hàng
- **Căn cứ thực tế:** Sổ cọc ghi nhận thông số chi tiết của nhiều mã TP (cấu trúc màng, độ dày mic, R x D x Đáy, phụ kiện vòi).
- **Quyết định của Sếp:** **Thông số từ Sổ cọc là căn cứ chính thức để thiết lập thông số kỹ thuật cho Thành phẩm (`Item`) và Định mức (`BOM`).**

### Q22: Quy chuẩn sản phẩm Túi PE / HD đặt gia công ngoài từ Cơ sở Thanh Tùng
- **Căn cứ thực tế:** 7 hợp đồng/đơn hàng với Anh Tùng thể hiện việc Vạn Phát đặt Cơ sở Thanh Tùng (Cần Đước) gia công túi PE/HD (Ốc Kiều, Ms.Barun, MTBC An Hữu, Hà Linh...).
- **Quyết định của Sếp:** **Tạo mã nhóm Túi Màng Đơn (`TMD-#####`) và tạo NCC Thanh Tùng.** Đây là hình thức mua thương mại/gia công ngoài (Purchase to Order - PTO), brand in lụa ghi tại đơn bán.

### Q25: Khách hàng sở hữu thương hiệu MINH RÂU
- **Căn cứ thực tế:** Có 2 mã túi nước giặt MINH RÂU (trục G4005883/G4005887) nhưng không có khách hàng tên Minh Râu trong danh sách.
- **Quyết định của Sếp:** **MINH RÂU là thương hiệu độc quyền trực thuộc CÔNG TY CỔ PHẦN DS COSMETIC.** Đã gán chủ sở hữu 2 mã `TP-00022` và `TP-00023` cho `KH-00184` (DS COSMETIC).

### Q27 & Q28: Xử lý chứng từ Túi Lamy Trang Tín và Túi HD Vạn An
- **Căn cứ thực tế:** Đơn mua túi Lamy từ NCC Trang Tín (2 mẫu dùng chung 1 bộ trục in); Ảnh túi HD Bệnh viện Vạn An in 1 màu.
- **Quyết định của Sếp:** 
  - Túi Lamy: Xác nhận quy cách `PET/MPET/PA/PE trong`, 2 mẫu/1 bộ trục, lưu vào `TP-00013` và `TP-00014`.
  - Túi HD Vạn An: Giữ mã Túi màng đơn `TMD-` đã tạo, thuộc nhóm mua ngoài in lụa.

### Q29: Túi Lotus PP và Túi Hồ tiêu Quang Đại Phát
- **Căn cứ thực tế:** Hợp đồng Đặng Điều Tâm mua túi Lotus PP 7 zem (500kg x 66.000đ); Phiếu làm trục DONGYUN cho túi Hồ tiêu Nhật Quang Trị (KH Quang Đại Phát).
- **Quyết định của Sếp:** **Giữ nguyên mã đã tạo:** `TMD-00014` (Túi Lotus PP) gán cho khách Đặng Điều Tâm; `TP-00019` (Túi tiêu NQT) gán cho khách Quang Đại Phát.

### Q30: Đơn hàng màng hạt chia Minh Châu
- **Căn cứ thực tế:** Đơn đặt in màng ghép hạt chia Minh Châu tại Trang Tín trị giá 42 triệu.
- **Quyết định của Sếp:** **Giữ nguyên mã sản phẩm**, thông tin pháp nhân đầy đủ của khách hàng Minh Châu sẽ cập nhật khi phát sinh hợp đồng chính thức.

### Q37: Xử lý sai lệch số tiền trên Hợp đồng KOVA và Đơn Samran
- **Căn cứ thực tế:** HĐKT KOVA lệch 240.000đ giữa số viết bằng chữ và số cộng dòng; Đơn Samran INS lệch ~2.000đ.
- **Quyết định của Sếp:** **Đối với các mã sản phẩm có xung đột số liệu giá chưa ngã ngũ, tạm thời để giá niêm yết `standard_rate = 0`** (áp dụng cho `TP-00001`, `TP-00002`, `TP-00003`, `TP-00005`). Giá bán sẽ được xác định chính xác theo từng Báo giá (`Quotation`) và Đơn hàng (`Sales Order`) thực tế.

### Q38: Xử lý mẫu bao bì Túi FUTA (In không trục)
- **Căn cứ thực tế:** Hình ảnh túi nước giặt xả FUTA 6 in 1 dung tích 2KG in công nghệ không trục.
- **Quyết định của Sếp:** **Tạo mã `TP-00035`** (công nghệ in ghi `In offset (Không trục)`), khách hàng sở hữu là TRANG UYÊN (`KH-00298`) theo số liệu cọc sản xuất 10.000 túi.

### Q39: Xử lý sai lệch phép tính thành tiền trên đơn hàng MTBC An Hữu
- **Căn cứ thực tế:** Đơn đặt hàng ghi 40kg x 60.000đ nhưng người lập ghi nhầm tổng tiền là 4.200.000đ (thực tế là 2.400.000đ).
- **Quyết định của Sếp:** **Lấy theo đơn giá chuẩn 60.000đ/kg**, ghi chú rõ sự nhầm lẫn vào trường `description` của `TMD-00004`.

---

## PHẦN VI: VẬN HÀNH XƯỞNG, GIAO DỊCH & CHỨNG TỪ (Q23, Q26, Q31, Q33)

### Q23: Căn cứ xây dựng Định mức sản xuất (BOM) và tỷ lệ hao hụt xưởng
- **Căn cứ thực tế:** File tiến độ sản xuất thực tế có tỷ lệ hao hụt dao động theo từng mẻ chạy (hao cắt từ 3% đến 12%).
- **Quyết định của Sếp:** **Định mức BOM chuẩn được xây dựng theo công thức toán học tại `specs/packaging-math.md` với tỷ lệ hao cắt chuẩn là 2.5%.** Số liệu sản xuất từng mẻ chỉ dùng để đối chiếu đánh giá chênh lệch, không dùng số phát sinh cá biệt làm định mức chuẩn.

### Q26 & Q33: Xử lý số liệu Sổ Thu Chi và các giao dịch cũ từ Google Sheet
- **Căn cứ thực tế:** Sổ Thu Chi và Google Sheet chứa hàng trăm dòng nhật ký thu cọc, chi tiền và đơn hàng lịch sử.
- **Quyết định của Sếp:** **Số liệu sổ sách cũ chỉ dùng làm căn cứ đối soát công nợ ban đầu và thông số kỹ thuật, TUYỆT ĐỐI KHÔNG import mù thành chứng từ giao dịch trên ERPNext.** Mọi chứng từ giao dịch (`Sales Order`, `Purchase Order`, `Payment Entry`) trên hệ thống mới sẽ được lập mới từ đầu đúng quy trình chuẩn.

### Q31: Thiết lập Danh mục Kho Hàng, Trạm Máy và Công Đoạn Xưởng
- **Căn cứ thực tế:** Quy trình xưởng thực tế gồm các công đoạn đùn/thổi, ghép, chia cuộn, cắt túi, đóng vòi.
- **Quyết định của Sếp:** Thiết lập chuẩn mực tối thiểu theo đúng thực tế nhà máy Vạn Phát:
  - **4 Kho hàng vật lý:** Kho NVL, Kho BTP, Kho TP, Kho Trục in.
  - **4 Trạm máy chính:** Máy Thổi PE (`WS-THOI-01`), Máy Ghép Màng (`WS-GHEP-01`), Máy Cắt Túi (`WS-CAT-01`), Máy Đóng Vòi (`WS-VOI-01`).
  - **4 Công đoạn sản xuất:** Thổi màng, Ghép màng, Cắt túi, Đóng vòi.
