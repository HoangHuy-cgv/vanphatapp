# ĐẶC TẢ MASTER DATA & PHÂN CẤP SẢN PHẨM BAO BÌ (PACKAGING TAXONOMY)

> **Mục đích:** Nguồn chân lý duy nhất (SSOT) cho cấu trúc cây nhóm hàng, quy chuẩn 5 ĐVT, quy tắc đặt tên sản phẩm, và 5 kịch bản kinh doanh thực tế tại nhà máy Bao Bì Vạn Phát.
> **Nguyên tắc ERPNext Native:** Sử dụng 100% cấu trúc `Item Group`, `Item`, `BOM`, `Customer` của ERPNext Native v16. Ánh xạ chi tiết các trường dữ liệu tham chiếu tại [erpnext-fields.md](./erpnext-fields.md).

---

## 1. CẤU TRÚC CÂY NHÓM HÀNG CHUẨN (ITEM GROUP TAXONOMY — KẾ TOÁN & VẬN HÀNH)

Toàn bộ hàng hóa, vật tư trong nhà máy được phân loại theo cây nhóm hàng 5 nhánh cấp 1 theo chuẩn định khoản kế toán kho và vận hành xưởng:

```text
All Item Groups
├── 1. NGUYÊN VẬT LIỆU (NVL)
│   ├── Màng Thô NVL (PET, PA, PE sữa, PE trong, MPET, CPP, AL)
│   ├── Hóa Chất & Keo Ghép (Keo ghép, Curing agent, Dung môi EA)
│   └── Phụ Kiện Bao Bì (Vòi, Nắp, Zipper, Thùng carton đóng gói)
├── 2. BÁN THÀNH PHẨM (BTP)
│   ├── Màng In Ống Đồng (Cuộn màng PET/BOPP đã in ống đồng, chuẩn bị ghép)
│   └── Cuộn Màng Ghép BTP (Cuộn đã ghép nhiều lớp, đầu vào máy cắt túi hoặc bán cuộn)
│       └── NGUYÊN TẮC CỜ BÁN (Sếp chốt, đúng docs ERPNext Item §3.13 Is Sales Item):
│           Chỉ BTP bán cuộn (hiện tại: BTP-00015 Cuộn Năm Tàu + cuộn màng tiêu khi có mã)
│           được is_sales_item=1. Mọi BTP còn lại là input máy cắt → is_sales_item=0
│           (native chặn ở Quotation/Sales Order, KHÔNG ẩn khỏi danh mục để tra tồn kho/BOM).
├── 3. THÀNH PHẨM (TP)
│   ├── Túi Nước Giặt Có Sẵn (NGCS: Mẫu in sẵn của Vạn Phát, bán đại trà, in lụa brand khách)
│   ├── Túi Màng Ghép Đặt Riêng (TP: In trục ống đồng độc quyền 1 TP = 1 KH)
│   │   ├── Túi đáy đứng (Doypack: Nước giặt, xốt, chất lỏng — có vòi / không vòi)
│   │   ├── Túi 3 biên (Three-side seal / Flat pouch)
│   │   ├── Túi xếp hông (Side Gusset)
│   │   ├── Túi lưng giữa (Center Seal)
│   │   └── Túi 8 cạnh đáy phẳng (Box Pouch / Flat Bottom)
│   └── Túi Màng Đơn (TMD: Bán đại trà — In lụa: HD, PE, PP)
├── 4. TRỤC IN (TRUC)
│   └── Trục In Ống Đồng (Tài sản trục in vật lý, item_code lấy trực tiếp TRUC-{Mã laser NCC})
└── 5. PHẾ LIỆU & THU HỒI
    └── Phế Liệu Thu Hồi (Màng phế liệu thu hồi từ xưởng in, ghép, cắt)
```

---

## 2. QUY CHUẨN 5 ĐƠN VỊ TÍNH (UOM) CHUẨN MỰC

Toàn bộ hệ thống sử dụng đúng 5 đơn vị tính chuẩn mực, không dùng từ ngữ thừa:

1. **`Túi`**: Áp dụng cho toàn bộ thành phẩm túi (Túi NGCS, Túi màng ghép đặt riêng TP, Túi màng đơn TMD).
2. **`Kg`**: Áp dụng cho Màng thô NVL (PET, PA, PE sữa, MPET, AL), Keo ghép, Curing agent, Dung môi EA, Hạt nhựa.
3. **`m`**: Chuẩn duy nhất đo chiều dài cuộn (thay thế hoàn toàn 'Mét Dài'). Áp dụng cho Màng in NVL (PET in), Cuộn màng ghép BTP và Dây Zipper.
4. **`Cây`**: Áp dụng cho Trục in ống đồng vật lý.
5. **`Cái`**: Áp dụng cho Phụ kiện vòi, nắp vòi và thùng carton đóng hàng.

---

## 3. PHÂN LOẠI 2 NHÓM SẢN PHẨM & QUY TẮC ĐỊNH DANH (NAMING RULES)

Hệ thống phân định rạch ròi 2 nhóm sản phẩm thương mại với mục đích cốt lõi: **Khi tạo Báo giá / Đơn hàng, sau khi chọn Phân loại nhóm và chọn Khách hàng, hệ thống tự động FILTER mã sản phẩm để giới hạn danh sách, giúp user tìm kiếm nhanh, chính xác và tuyệt đối không bao giờ nhầm lẫn hàng độc quyền giữa các khách hàng.**

---

### 3.1. NHÓM 1: HÀNG CÓ SẴN (DÙNG CHUNG BÁN CHO TẤT CẢ KHÁCH HÀNG)

- **Bản chất:** Sản xuất hàng loạt hoặc mua sẵn về kho làm phôi trắng / phôi in sẵn. Bán chung cho mọi khách hàng. Khi phát sinh đơn hàng, xưởng chạy công đoạn **In lụa lần 2** theo thương hiệu/mẫu in riêng của từng khách hàng.
- **Nguyên tắc đặt tên:** Tên Item Master và Alias là tên phôi quy cách chung, **TUYỆT ĐỐI KHÔNG mang tên riêng của khách hàng** (tránh trường hợp khách khác mua lại thấy tên khách cũ).
- **Mối liên hệ Khách hàng $\leftrightarrow$ Mẫu in lụa:** Cùng một mã phôi (ví dụ `NGCS-00001` NGCS Lớn Đỏ), khách VIO mua sẽ in mẫu VIO, khách FUSIMI mua sẽ in mẫu FUSIMI. Tên mẫu in lụa được quản lý tại dòng đơn hàng qua trường `custom_screen_print_brand` (hoặc bảng lịch sử mẫu in của khách).

| Phân nhóm con | Quy tắc đặt tên `item_name` | Quy tắc gọi tắt `custom_alias` (UI) | Ví dụ cụ thể |
| :--- | :--- | :--- | :--- |
| **Túi Nước Giặt Có Sẵn (NGCS)** | `TÚI NGCS {Size} {Màu nền} {Mẫu nền}` | `NGCS {Size} {Màu nền}` | - `item_name`: `TÚI NGCS LOẠI LỚN ĐỎ ĐAM MÊ`<br>- `custom_alias`: `NGCS Lớn Đỏ`<br>- `item_name`: `TÚI NGCS THÁI LAN XANH DƯƠNG HOA HỒNG`<br>- `custom_alias`: `NGCS Nhỏ Xanh HH` |
| **Túi Màng Đơn (TMD)** | `{Chất liệu} {Kiểu dáng} {Kích thước WxL}` | `{Chất liệu} {Kiểu} {WxL}` | - `item_name`: `Túi PE Hột Xoài Trắng Sữa 20x30`<br>- `custom_alias`: `PE Hột Xoài 20x30`<br>- `item_name`: `Túi HD Sữa Quai Thỏ 26x43`<br>- `custom_alias`: `HD Quai Thỏ 26x43`<br>- `item_name`: `Túi HD Trắng Sữa Xếp Hông 30x20x30`<br>- `custom_alias`: `HD Xếp Hông 30x20x30` |

---

### 3.2. NHÓM 2: HÀNG THIẾT KẾ RIÊNG (ĐỘC QUYỀN 1 MÃ = 1 KHÁCH HÀNG DUY NHẤT)

- **Bản chất:** In trục ống đồng hoặc in offset theo mẫu thiết kế độc quyền của khách hàng. Mỗi mẫu in là một sản phẩm độc nhất, liên kết 1-1 với khách hàng sở hữu qua bảng con native `Item Customer Detail` (`Item.customer_items`). **TUYỆT ĐỐI CẤM bán cho khách hàng khác.**
- **4 Kiểu túi màng ghép chuẩn:**
  1. **Túi đáy đứng (Doypack):** Nước giặt, nước xả, nước xốt, chất lỏng (có độ mở đáy G).
  2. **Túi xếp hông (Side Gusset):** Túi cà phê, trà, phân bón, thức ăn thú cưng (xếp hông 2 bên).
  3. **Túi lưng giữa (Center Seal):** Túi bánh kẹo, snack, kem, linh kiện (hàn lưng chính giữa).
  4. **Túi 8 cạnh đáy phẳng (Box Pouch / Flat Bottom):** Túi gạo cao cấp, cà phê thượng hạng, hạt dinh dưỡng (đáy đứng hình hộp chữ nhật).
  *(Kèm dạng phẳng truyền thống: Túi 3 biên / Three-side seal).*
- **3 Dạng phụ kiện miệng túi:**
  1. **Vòi (Spout):** Vòi 16mm, Vòi 10mm, Vòi 22mm... (cho túi nước giặt, nước xả, chất lỏng).
  2. **Khóa Zipper:** Bấm miệng túi (cho túi hạt, bột, bánh kẹo).
  3. **Hàn kín:** Không gắn phụ kiện, miệng để mở để khách hàng tự chiết rót và hàn nhiệt khi đóng gói thành phẩm.

| Phân nhóm con | Quy tắc đặt tên `item_name` | Quy tắc gọi tắt `custom_alias` (UI) | Ví dụ cụ thể |
| :--- | :--- | :--- | :--- |
| **Túi Màng Ghép Đặt Riêng (TP)** | `TÚI {KIỂU TÚI} {BRAND} {DUNG TÍCH} {MẪU/MÀU} {PHỤ KIỆN}` | `{Brand} {Dung tích/Mẫu} {Kiểu/PK}` | - `item_name`: `TÚI ĐÁY ĐỨNG MINH RÂU 3.2KG TÍM VÒI 16`<br>- `custom_alias`: `Minh Râu 3.2kg Tím Vòi 16`<br>- `item_name`: `TÚI 3 BIÊN NHÔM 20X30 HÀN KÍN`<br>- `custom_alias`: `Nhôm 20x30 Hàn Kín` |
| **Cuộn Màng Ghép (BTP bán)** | `CUỘN MÀNG {CẤU TRÚC} {BRAND} KHỔ {K}` | `Cuộn {Brand} Khổ {K}` | - `item_name`: `CUỘN MÀNG PET/PE NĂM TÀU KHỔ 560`<br>- `custom_alias`: `Cuộn Năm Tàu K560` |

---

### 3.3. CƠ CHẾ LỌC TỰ ĐỘNG (SMART FILTER) KHI TẠO ĐƠN HÀNG / BÁO GIÁ

Nhằm mục đích tối ưu hóa thao tác người dùng (User Experience):
1. **Bước 1 (Chọn Nhóm):** User chọn một trong 2 nhóm:
   - `Hàng Thiết Kế Riêng` (MTO - Made to Order)
   - `Hàng Có Sẵn` (MTS - Made to Stock)
2. **Bước 2 (Chọn Khách Hàng):** User chọn khách hàng (ví dụ: `CÔNG TY CỔ PHẦN DS COSMETIC` - `KH-00184`).
3. **Bước 3 (Hệ thống tự động lọc danh sách mã):**
   - **Nếu chọn Hàng Thiết Kế Riêng:** Hệ thống chỉ truy vấn bảng con native `Item Customer Detail` (lọc `customer = 'KH-00184'`). Dropdown mã sản phẩm **chỉ hiển thị duy nhất** các mã thuộc về DS COSMETIC (`888 Phấn Thơm`, `Minh Râu Tím`, `Minh Râu Hồng`, `Mẹ Thích 888`). Tuyệt đối không hiển thị mã Kovaa, Samran của khách khác.
   - **Nếu chọn Hàng Có Sẵn:** Hệ thống hiển thị toàn bộ phôi dùng chung (NGCS + TMD). Khi chọn phôi (ví dụ: `NGCS Lớn Đỏ`), trường **Mẫu in lụa của khách hàng** (`custom_screen_print_brand`) sẽ tự động xuất hiện hoặc gợi ý các mẫu in lụa mà khách hàng đó đã đăng ký.

---

## 4. TRẠM MÁY, CÔNG ĐOẠN & COST CENTER MÁY THỔI (Sếp chốt)

- **4 kho** (không tách kho NCC): NVL · BTP · TP · TRUC. Trục gửi NCC giữ
  (Trang Tín 20 + Kiến Tâm 17 + Tuệ Nhi 4) vẫn là tài sản Vạn Phát, theo dõi
  nơi giữ tại `custom_cylinder_location` từng trục.
- **4 trạm / 4 công đoạn** (dùng theo luồng, không phải tuyến tính):
  `THOI-MANG` (WS-THOI-01 Máy Thổi PE Liên Doanh) · `GHEP-MANG` · `CAT-TUI` · `DONG-VOI`.
  Vạn Phát KHÔNG in trục (đặt mua túi/màng in từ NCC), không QC/đóng thùng riêng.
- **4 luồng sản xuất** (Sếp chốt):
  1. **Túi màng ghép TP**: mua túi TP từ NCC → giao thẳng; hoặc mua màng in + màng NVL →
     `GHEP-MANG` → `CAT-TUI` → giao; hoặc → `DONG-VOI` → giao (túi có vòi).
  2. **Túi NGCS**: gửi phôi → in lụa brand khách → `DONG-VOI` → giao.
  3. **Túi màng đơn TMD**: mua về → in lụa brand khách → giao (không qua máy xưởng).
  4. **Cuộn màng bán**: mua màng in + màng NVL → `GHEP-MANG` → giao cuộn (mới tạo mã BTP khi bán).
- **Hàng lỗi + phế liệu → bán phế** (Sếp chốt, không tái chế): 2 mã riêng theo nguồn để tách doanh thu —
  `Phế Thổi PE` (mã kho P01: biên/đầu cuộn lỗi máy thổi, cost center máy thổi) và
  `Phế Ghép` (mã kho P02: đầu cuộn + màng lỗi khâu ghép, Vạn Phát). ĐVT Kg, được phép bán, không BOM.
- **Máy thổi = NCC ngoài + cost center riêng**: tách biệt doanh số bán hàng
  và chi phí thổi. Thực tế Vạn Phát vận hành, dùng quỹ Vạn Phát, đứng ra
  thu-chi, cuối tháng chốt sổ 1 lần với đối tác liên doanh.
  Khi bật `with_operations=1` ở BOM, giờ máy thổi hạch toán vào cost center
  riêng, không lẫn giá thành ghép/cắt/vòi.

## 5. NĂM KỊCH BẢN KINH DOANH & SẢN XUẤT THỰC TẾ (SẾP DUYỆT)

### Kịch bản 1: Túi In Sẵn Bán Đại Trà (MTS - Make to Stock)
- **Bản chất:** Túi nước giặt có sẵn (NGCS) được sản xuất hàng loạt lưu kho theo 3 size chuẩn, khách mua số lượng ít có thể lấy ngay:
  1. *Size Nhỏ (1.8L – 2.4L):* Cấu trúc **PET/MPET/PA/PE sữa**, dày **220 mic**, Vòi **16mm**.
  2. *Size Trung (3 – 3.6Kg):* Cấu trúc **PET/PA/PE sữa**, kích thước **28x34 cm**, dày **230 mic**, Vòi **16mm**.
  3. *Size Lớn (3.5L – 5L):* Cấu trúc **PET/MPET/PA/PE sữa**, dày **250 mic**, Vòi **16mm**.
- **1 mã NGCS bán cho NHIỀU khách** (mẫu in sẵn của Vạn Phát, không độc quyền) → KHÔNG gán customer cố định (customer/variant để trống).
- **In ấn lần 2 (bắt buộc để phân biệt):** Túi NGCS qua in lụa thủ công, in brandname của từng khách lên túi để tạo sự khác biệt. Nhân viên chọn brand in lụa tại trường `custom_screen_print_brand` trên Sales Order Item.

### Kịch bản 2: Hàng Đặt In Riêng Độc Quyền (MTO - Make to Order)
- **Bản chất:** Sản phẩm màng ghép in trục ống đồng độc quyền theo thương hiệu của khách (TopGia, Tanzy, Minh Râu, 888...).
- **NGUYÊN TẮC NGÀNH (1 TP = 1 KH duy nhất):** Túi màng ghép TP và cuộn màng ghép BTP sản xuất riêng cho đúng 1 khách, vì NVL là cuộn PET in theo mẫu thiết kế riêng của khách đó — không bao giờ bán chung. Mã biến thể (VD `888-3.2KG-HONG`) là tiếng nói của đúng khách sở hữu (DS COSMETIC), mã TP- là tiếng nói nội bộ Vạn Phát.
- **Vận hành trên ERPNext:**
  - Mã sản phẩm: `TP-#####`.
  - Khách hàng sở hữu duy nhất: gán tại trường `customer` và bảng `customer_items` (1 dòng con 1 KH — KHÔNG bao giờ có dòng thứ 2 cho TP/BTP).
  - Chỉ khi có Đơn đặt hàng bán (`Sales Order`), hệ thống mới phát sinh Lệnh sản xuất xưởng (`Work Order`).

### Kịch bản 3: Hàng Mua Ngoài Thương Mại (PTO - Purchase to Order)
- **Bản chất:** Hàng xưởng không sản xuất mà mua lại từ NCC (như Túi màng đơn PE, PP).
- **1 mã TMD bán cho NHIỀU khách** (hàng chợ, không độc quyền) → KHÔNG gán customer cố định.
- **In lụa phân biệt như NGCS:** Túi màng đơn qua in lụa thủ công, in brandname của từng khách lên túi. Brand in lụa ghi tại `custom_screen_print_brand` trên Sales Order Item.
- **Vận hành trên ERPNext:** `default_material_request_type = "Purchase"`. Khi duyệt `Sales Order`, hệ thống liên kết trực tiếp tạo Đơn mua hàng NCC (`Purchase Order`), hàng nhập về kho là xuất giao ngay.

### Kịch bản 4: 1 Thương Hiệu Nhiều Chủ Sở Hữu
- **Thực tế nghiệp vụ:** Thương hiệu `Topgia` thuộc 2 chủ: KOVAA (túi nước giặt) và Phong Tín (túi màng bọc thực phẩm) $\rightarrow$ Khác mặt hàng, tạo 2 mã `TP` riêng biệt cùng mang `brand = Topgia`.
- **Làm rõ (tránh hiểu nhầm):** Mỗi mã TP vẫn chỉ thuộc 1 KH duy nhất (nguyên tắc kịch bản 2). Trường hợp "bán cho đại lý" không dùng chung mã TP — mỗi đại lý/kênh có mã TP riêng nếu mẫu in khác, hoặc dùng `Item Price` riêng từng khách trên cùng mã NGCS/TMD (hàng chợ, kịch bản 1/3).

### Kịch bản 5: Quản Lý Vòng Đời Sản Phẩm Ngừng Kinh Doanh (Disabled Items)
- Các mã sản phẩm đã ngừng bán thương phẩm trên thị trường (như túi 888 0.6Kg) được gán cờ `disabled = 1` và `is_sales_item = 0`.
- Vẫn lưu giữ đầy đủ mã trục in vật lý (`TRUC-`) để theo dõi tài sản và phục vụ bảo quản tại kho.

---

## 5. NGUYÊN TẮC QUY CÁCH KỸ THUẬT BAO BÌ (ĐÁY & VÒI)

1. **Túi xếp hông:** Mặc định là **Không vòi** và **Không phải túi Doypack**.
2. **Túi 8 cạnh đáy phẳng (Box Pouch):** Ghép đáy phẳng rời độc lập, hàn 4 cạnh đáy kết hợp 4 cạnh thân.
3. **Túi đáy đứng có vòi (Doypack):** Vòi hàn nhiệt tại miệng túi (giữa đỉnh hoặc góc chéo 45 độ). Đáy có độ mở G $\ge 30\text{ mm}$ giúp túi tự đứng vững khi chứa chất lỏng.
