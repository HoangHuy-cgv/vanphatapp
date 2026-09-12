# TÀI LIỆU ĐẶC TẢ MASTER DATA & BẢNG ÁNH XẠ THUẬT NGỮ ERPNEXT NATIVE
**Ngành ứng dụng:** Bao bì mềm & Màng ghép phức hợp (Flexible Packaging)  
**Phiên bản hệ thống:** ERPNext Native (Bản chuẩn không cần code thêm)

---

## PHẦN 1: BẢNG ÁNH XẠ THUẬT NGỮ (TERMINOLOGY MAPPING)
*Đối chiếu giữa ngôn ngữ hệ thống ERPNext (English Native) và ngôn ngữ vận hành thực tế tại xưởng bao bì.*

| ERPNext Native (English) | Wording Xưởng Bao Bì (Tiếng Việt) | Ý nghĩa & Bản chất nghiệp vụ tại xưởng |
| :--- | :--- | :--- |
| **Item** | Mã hàng / Mặt hàng | Đối tượng vật lý được quản lý trong hệ thống (thành phẩm túi, cuộn màng, nguyên liệu hạt, mực, vòi...). |
| **Item Code** | Mã định danh sản phẩm | Mã duy nhất dùng để quét barcode, in tem kiện hàng (`TP-00001`, `TNG-01`). Được tạo tự động bởi hệ thống. |
| **Item Name** | Tên sản phẩm hiển thị (UI) | Tên rút gọn, ngắn gọn hiển thị trên màn hình giao diện để nhân viên bán hàng chọn nhanh (`TopGia 2L - Đắm say`). |
| **Description** | Mô tả chi tiết kỹ thuật | Chuỗi mô tả đầy đủ quy cách túi (kích thước, loại đáy, loại vòi, cấu trúc màng) dùng để in ra báo giá và hóa đơn PDF gửi khách. |
| **Item Group** | Nhóm hàng / Cây danh mục | Cây phân loại dùng để định khoản kế toán tài khoản doanh thu, tài khoản giá vốn và kho mặc định. |
| **Brand** | Nhãn hàng / Thương hiệu | Nhãn hiệu in trên bao bì (`TopGia`, `Minh Râu`, `Tanzy`...). Dùng để lọc báo cáo doanh thu theo hãng. |
| **Customer** | Khách hàng / Pháp nhân mua | Đơn vị ký hợp đồng, nhận hóa đơn VAT và thanh toán công nợ (Công ty Thương Mại A, Xưởng gia công B...). |
| **Customer Details** *(bảng con trong Item)* | Khách được phép mua hàng | Danh sách các Khách hàng được phép mua mã túi in độc quyền này (chặn bán nhầm bao bì giữa các bên). |
| **Item Price** | Bảng giá theo khách | Cho phép set giá bán khác nhau cho từng khách hàng trên cùng 1 mã túi (ví dụ: bán cho Cty TM giá sỉ, bán cho xưởng gia công giá khác). |
| **Item Template** | Phôi mẫu túi cha | Dùng để quản lý mặt hàng có nhiều biến thể mẫu in (ví dụ: Phôi túi nước giặt in sẵn). |
| **Item Variant** | Mã biến thể con | Các mã sản phẩm con được sinh tự động từ Template (13 mã túi nước giặt in sẵn). |
| **Item Attribute** | Thuộc tính biến thể | Các đặc tính tạo nên sự khác biệt của biến thể: `Dung tích` (2kg, 3.5kg) và `Mẫu in / Hương` (Mẫu 01 đến 13). |
| **Make to Order (MTO)** | Sản xuất theo đơn hàng riêng | Hàng in thương hiệu độc quyền của khách (TopGia, Tanzy...), chỉ chạy máy khi khách lên đơn PO. |
| **Make to Stock (MTS)** | Sản xuất lưu kho (Hàng sẵn) | 13 mã túi nước giặt in sẵn đại trà, sản xuất hàng loạt lưu kho để giao ngay khi khách cần. |
| **Purchase to Order (PTO)** | Hàng thương mại / Mua theo đơn | Hàng xưởng không sản xuất mà mua lại từ NCC (như Túi màng đơn PE, PP). Có đơn bán mới làm đơn mua. |
| **Bill of Materials (BOM)** | Định mức vật tư sản xuất | Công thức sản xuất 1 túi: gồm bao nhiêu kg màng thân, màng đáy mộc, bao nhiêu cái vòi, nắp, zipper, hao hụt keo/mực. |
| **Work Order** | Lệnh sản xuất xưởng | Lệnh chuyển xuống cho các tổ máy: In ống đồng -> Ghép màng -> Chia cuộn -> Cắt dán túi/hàn vòi. |
| **Print Format** | Mẫu in chứng từ (PDF) | Mẫu in Báo giá, Đơn hàng, Phiếu xuất kho dùng ngôn ngữ Jinja2 để tự động ghép các trường kỹ thuật. |

---

## PHẦN 2: THIẾT KẾ CÂY NHÓM HÀNG & PHÂN LOẠI SẢN PHẨM (SẾP CHỐT)

### 1. Cấu Trúc Cây Nhóm Hàng Chuẩn (2 Nhóm Lớn: Túi & Màng)
```text
All Item Groups
├── 1. MÀNG (Film)
│   ├── 1.1. Màng đơn nguyên vật liệu (NVL: PET, PA, PE, MPET, CPP, AL, Hạt nhựa, Hóa chất keo/dung môi)
│   └── 1.2. Cuộn màng ghép (BTP / Thành phẩm: Input máy cắt túi hoặc bán cho máy đóng gói tự động — In trục/Offset, thiết kế riêng từng khách)
├── 2. TÚI (Pouch)
│   ├── 2.1. Túi màng đơn (Bán đại trà cho mọi khách — In lụa)
│   └── 2.2. Túi màng ghép
│       ├── Túi nước giặt có sẵn (NGCS: Mẫu in sẵn của Vạn Phát thiết kế, bán đại trà, in lụa lần 2 brandname của khách)
│       └── Túi màng ghép đặt riêng (In trục/offset theo thiết kế của khách, bán độc quyền 1 khách)
│           ├── Túi đáy đứng (Doypack: Nước giặt, xốt, chất lỏng — có vòi / không vòi)
│           ├── Túi 3 biên (Flat / Three-side seal)
│           ├── Túi xếp hông (Side Gusset)
│           ├── Túi lưng giữa (Center Seal)
│           └── Túi 8 cạnh (Flat Bottom / Box Pouch)
├── 3. PHỤ KIỆN TÚI (Accessories)
│   ├── Vòi (Spouts: Phi 8.6, 10, 15, 16, 22, 28, 33...)
│   ├── Zipper (Dây kéo)
│   └── Hàn kín (Chỉ dán nhiệt, không gắn phụ kiện)
└── 4. TRỤC IN (Cylinders)
    └── Trục in ống đồng theo mẫu riêng của từng khách
```

---

### 2. Ma Trận Công Nghệ In & Phụ Kiện Túi
* **Công nghệ in:**
  * **In trục (Ống đồng) & In offset:** Dành riêng cho Túi màng ghép đặt riêng và Cuộn màng ghép.
  * **In lụa:** Dành cho Túi màng đơn và in lụa lần 2 (in Brandname/Logo của khách) lên Túi NGCS in sẵn.
* **Phụ kiện miệng túi:**
  * **Đóng vòi (Spout):** Chủ lực cho túi nước giặt đáy đứng.
  * **Zipper (Khóa kéo):** Túi thực phẩm, nông sản, bột.
  * **Hàn kín (Heat seal):** Hàn nhiệt phẳng miệng túi.

---

### 3. Quy Chuẩn Đơn Vị Tính (UOM) Chuẩn Hóa Toàn Hệ Thống (Sếp duyệt)
Hệ thống sử dụng đúng 5 đơn vị tính chuẩn mực, không dùng từ ngữ thừa:
1. **`Túi`**: Áp dụng cho toàn bộ thành phẩm túi (Túi NGCS và Túi màng ghép đặt riêng).
2. **`Kg`**: Áp dụng cho Túi màng đơn bán theo cân, Màng thô NVL (PET, PA, PE sữa, MPET, AL), Hóa chất ghép màng (Keo, Curing agent, EA).
3. **`m`**: Chuẩn duy nhất đo chiều dài cuộn (thay thế hoàn toàn 'Mét Dài'). Áp dụng cho Màng in NVL (PET in), Cuộn màng ghép BTP và Dây Zipper.
4. **`Cây`**: Áp dụng cho Trục in ống đồng.
5. **`Cái`**: Áp dụng cho Phụ kiện vòi, nắp và thùng carton đóng gói.

---

### 4. Quy Tắc Đặt Tên `item_name` Tối Giản & Tách Bạch Dữ Liệu UI/UX
Tuân thủ nguyên tắc ERPNext Native: `item_name` dài không quá 25 ký tự, không gộp thông số kỹ thuật (độ dày, cấu trúc màng, kích thước WxL), mọi thông số kỹ thuật chi tiết đưa vào `description` và 25 Custom Fields kỹ thuật:

1. **Nhóm Túi Nước Giặt Có Sẵn (NGCS):**
   * Công thức: **`NGCS {Size} {Màu} - {Mẫu in}`**
   * Ví dụ: `NGCS Nhỏ Đỏ - Đam Mê`, `NGCS Trung Tím - Nước Hoa`, `NGCS Lớn Vàng - Ban Mai` (18 - 23 ký tự).
   * Vận hành: Bán đại trà, nhân viên chọn thương hiệu in lụa lần 2 qua dropdown `custom_screen_print_brand` trên Sales Order.
2. **Nhóm Túi Màng Đơn Dùng Chung (TMD):**
   * Công thức: **`{Chất liệu} {Kiểu quai} {WxL}`** (Bỏ hẳn chữ "Túi")
   * Ví dụ: `HD quai thỏ 17x25`, `PE hột xoài 20x30`, `PP 32x45`, `HD quai thỏ 30x20x30` (8 - 18 ký tự).
3. **Nhóm Túi Màng Ghép Đặt Riêng (TP):**
   * Công thức: **`{Brand} {Dung tích} {Biến thể/Màu}`** (Bỏ hẳn chữ "Túi" và dấu gạch nối thừa)
   * Ví dụ: `888 3.2Kg Hồng`, `888 2Kg Tím`, `Minh Râu 3.2Kg Tím`, `TopGia MBTP`, `Lamy 2Kg Vàng` (10 - 18 ký tự).
4. **Nhóm Trục In Ống Đồng (TRUC):**
   * `item_code`: `TRUC-{Mã trục NCC}` (Ví dụ `TRUC-G4006940`). Khớp 100% mã khắc laser vật lý.
   * `item_name`: `Trục {Tên ngắn} ({Mã trục})` (Ví dụ: `Trục Sachpoong (G4010806)`, `Trục Sandokkaebi (G4006940)`).
5. **Nhóm Màng NVL & BTP:**
   * Màng đơn NVL: `{Vật liệu} K{Khổ} {Độ dày}mic` (Ví dụ `PA K700 15mic`, `PE sữa K700 190mic`).
   * Màng In NVL: `PET in {Brand} - {Mẫu in}`, ĐVT: **`m`** (Ví dụ `PET in 888 - Phấn Thơm`).
   * Cuộn Màng Ghép BTP: `Cuộn {Brand} - {Mẫu in}`, ĐVT: **`m`** (Ví dụ `Cuộn 888 - Phấn Thơm`).
   * Phụ kiện vòi: `Vòi 16mm`, `Vòi 10mm`, `Vòi 22mm` (ĐVT: Cái, không phân biệt thẳng/xéo).
   * Phụ kiện zipper: `Dây Zipper`, ĐVT: **`m`**.

---

### Kịch bản 1: Túi in sẵn bán đại trà (MTS) — BẢNG GIÁ NỘI BỘ CHÍNH THỨC 27/05/2026 (GIÁM ĐỐC DUYỆT)
Túi nước giặt có sẵn (NGCS) được chuẩn hóa theo 3 size quy chuẩn:
1. **Size Nhỏ (`1.8L – 2.4L`)**:
   - Tên kỹ thuật: `TÚI ĐỰNG NƯỚC GIẶT CÓ VÒI (Size Nhỏ)`
   - Cấu trúc màng: **4 Lớp PET/MPET/PA/PE**, Độ dày: **220 Mic**, Vòi: **16mm**.
   - Báo giá nội bộ: Giá HĐ 4.000 đ + Giá in lụa 2.500 đ $\rightarrow$ Đơn giá chưa VAT: **6.500 đ** (gồm VAT 8%: 6.820 đ).
   - Quy cách in lụa lần 2: Đã bao gồm in thương hiệu cho 2 mặt (tổng 2 màu) theo từng mã màu.
2. **Size Trung (`3 – 3.6Kg`)**:
   - Tên kỹ thuật: `TÚI ĐỰNG NƯỚC GIẶT KHÔNG TÊN 3 LỚP (Size Trung)`
   - Cấu trúc màng: **3 Lớp PET//PA/PES**, Kích thước: **28x34 cm**, Độ dày: **230 Mic**, Vòi: **16mm**.
   - Báo giá bậc thang theo số lượng (Chưa VAT):
     - 500 – 1.000 túi: **7.368 đ** (gồm VAT: 7.680 đ)
     - 1.100 – 2.000 túi: **7.208 đ** (gồm VAT: 7.520 đ)
     - 2.100 – 4.000 túi: **7.068 đ** (gồm VAT: 7.380 đ)
     - Trên 4.100 túi: **6.768 đ** (gồm VAT: 7.080 đ)
3. **Size Lớn (`3.5L – 5L`)**:
   - Tên kỹ thuật: `TÚI ĐỰNG NƯỚC GIẶT CÓ VÒI (Size Lớn)`
   - Cấu trúc màng: **4 Lớp PET/MPET/PA/PE**, Độ dày: **250 Mic**, Vòi: **16mm**.
   - Báo giá nội bộ:
     - 500 – 1.000 túi: Giá HĐ 6.400 đ + In lụa 3.000 đ $\rightarrow$ Chưa VAT: **9.400 đ** (gồm VAT: 9.912 đ).
     - Trên 2.000 túi: Giá HĐ 6.400 đ + In lụa 2.700 đ $\rightarrow$ Chưa VAT: **9.100 đ** (gồm VAT: 9.612 đ).

### Kịch bản 2: Quản lý Hàng in riêng độc quyền (TopGia, Tanzy, Minh Râu...)
* **Loại nghiệp vụ:** Make to Order (MTO - Sản xuất theo đơn đặt hàng).
* **Thiết lập:**
  * Mã tự sinh: `TP-00001`. Tên: `Túi 888 3.2KG - Hồng`.
  * Trường `Brand` = `888`.
  * Gán BOM riêng (trong đó có mã trục in của 888).
* **Vận hành:** Chỉ khi nhân viên tạo `Sales Order` (Đơn đặt hàng) cho khách, nút **Create > Work Order** mới sáng lên để xưởng tiến hành in ấn và gia công túi.

### Kịch bản 3: Túi màng đơn mua ngoài (PE, PP, HD...)
* **Loại nghiệp vụ:** Purchase to Order (PTO / Drop-ship / Trading).
* **Thiết lập:**
  * Thuộc nhóm: `Túi Màng Đơn`.
  * `Default Material Request Type` = **`Purchase`** (không chọn Manufacture).
* **Vận hành:** Khi có Đơn bán hàng (Sales Order) của khách, nhân viên bấm **Create > Purchase Order** để bắn đơn mua sang Nhà cung cấp màng đơn. Hàng về kho là xuất giao ngay, không qua bộ phận sản xuất.

### Kịch bản 4: 1 Brand nhiều chủ / nhiều khách (Sếp chốt 2026-09-11 theo raw-data)
* **Thực tế:** Brand `Topgia` thuộc 2 chủ (Fani đã bỏ): **KOVAA** — túi nước giặt; **Phong Tín** — túi đựng màng bọc thực phẩm. Khác item → 2 mã TP riêng cùng `brand` = Topgia.
* Cùng 1 item nhiều khách (VD 888/Minh Râu của DS COSMETIC): 1 mã TP + bảng `customer_items` + `Item Price` riêng từng khách.
* **Giá:** giá bán lấy từ file Đơn cọc (`TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx`); giá nhập màng/keo từ `MÀNG.xlsx`. Cấm dùng giá chào Google Sheet khi đã có đơn cọc. (Số 2.400/2.550 cũ là ví dụ bịa — bỏ.)

### Kịch bản 5: Quản lý vòng đời sản phẩm & Hàng ngừng bán thương mại (Disabled Items)
* **Thực tế:** Các mã sản phẩm đã ngừng bán thương phẩm trên thị trường (ví dụ: dòng túi `888 0.6Kg` Hồng, Tím, Đỏ, NLS, NRC của DS COSMETIC).
* **Thiết lập trên ERPNext:**
  * Gán cờ `disabled = 1` và `is_sales_item = 0`.
  * Prefix mô tả: `[NGỪNG BÁN THƯƠNG MẠI]`.
  * Vẫn giữ nguyên định danh kỹ thuật trong `item_spec.csv` và mã trục in vật lý (`G4006660`, `G4006655`, `G4005877`, `G4012417`, `G4012418`) đang lưu trữ tại Kho Vạn Phát.
* **Hiệu quả vận hành:** ERPNext tự động lọc bỏ khỏi danh sách tìm kiếm khi tạo Đơn đặt hàng (Sales Order) mới, bảo đảm an toàn cho kinh doanh nhưng bảo toàn toàn vẹn lịch sử kỹ thuật và quản lý tài sản trục in.

---

## PHẦN 4: NGUYÊN TẮC CHUẨN HÓA KỸ THUẬT BAO BÌ (ĐÁY & VÒI)

1. **Túi xếp hông:** Mặc định hiểu là **Không vòi** và **Không phải túi đáy đứng Doypack**. Không chia nhánh thừa thãi trên cây thư mục.
2. **Túi 8 cạnh đáy phẳng (Box Pouch):** Bản chất là **ghép đáy phẳng rời độc lập**, hàn 4 cạnh đáy kết hợp 4 cạnh thân tạo thành chiếc hộp tự đứng vững chãi.
3. **Túi đáy đứng có vòi (Túi nước giặt):** Đáy có thể gập liền thân (chừa trắng) hoặc ghép đáy rời từ cuộn màng thứ 2. Vòi được hàn nhiệt phẳng ở đỉnh hoặc góc chéo.
