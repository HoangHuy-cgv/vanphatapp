# ĐẶC TẢ MASTER DATA & PHÂN CẤP SẢN PHẨM BAO BÌ (PACKAGING TAXONOMY)

> **Mục đích:** Nguồn chân lý duy nhất (SSOT) cho cấu trúc cây nhóm hàng, quy chuẩn 5 ĐVT, quy tắc đặt tên sản phẩm, và 5 kịch bản kinh doanh thực tế tại nhà máy Bao Bì Vạn Phát.
> **Nguyên tắc ERPNext Native:** Sử dụng 100% cấu trúc `Item Group`, `Item`, `BOM`, `Customer` của ERPNext Native v16. Ánh xạ chi tiết các trường dữ liệu tham chiếu tại [erpnext-fields.md](./erpnext-fields.md).

---

## 1. CẤU TRÚC CÂY NHÓM HÀNG CHUẨN (ITEM GROUP TAXONOMY)

Toàn bộ hàng hóa, vật tư trong nhà máy được phân loại theo cây nhóm hàng 4 nhánh cấp 1:

```text
All Item Groups
├── 1. MÀNG (Film)
│   ├── 1.1. Màng đơn nguyên vật liệu (NVL: PET, PA, PE sữa, PE trong, MPET, CPP, AL, Keo, Dung môi EA)
│   └── 1.2. Cuộn màng ghép (BTP: Màng đã ghép nhiều lớp, đầu vào máy cắt túi hoặc bán cho khách chạy máy đóng gói tự động)
│       └── NGUYÊN TẮC CỜ BÁN (Sếp chốt, đúng docs ERPNext Item §3.13 `Is Sales Item`):
│           Chỉ BTP bán cuộn (hiện tại: BTP-00015 Cuộn Năm Tàu + cuộn màng tiêu khi có mã)
│           được `is_sales_item=1`. Mọi BTP còn lại là input máy cắt → `is_sales_item=0`
│           (native chặn ở Quotation/Sales Order, KHÔNG ẩn khỏi danh mục để tra tồn kho/BOM).
├── 2. TÚI (Pouch)
│   ├── 2.1. Túi màng đơn (Bán đại trà — In lụa: HD, PE, PP)
│   └── 2.2. Túi màng ghép
│       ├── Túi nước giặt có sẵn (NGCS: Mẫu in sẵn của Vạn Phát thiết kế, bán đại trà, in lụa brandname của khách)
│       └── Túi màng ghép đặt riêng (TP: In trục ống đồng theo thiết kế độc quyền của từng khách hàng)
│           ├── Túi đáy đứng (Doypack: Nước giặt, xốt, chất lỏng — có vòi / không vòi)
│           ├── Túi 3 biên (Three-side seal / Flat pouch)
│           ├── Túi xếp hông (Side Gusset)
│           ├── Túi lưng giữa (Center Seal)
│           └── Túi 8 cạnh đáy phẳng (Box Pouch / Flat Bottom)
├── 3. PHỤ KIỆN TÚI (Accessories)
│   ├── Vòi (Spouts: Phi 8.6, 10, 15, 16, 22, 28, 33...)
│   ├── Zipper (Dây kéo khóa)
│   └── Thùng carton đóng gói
└── 4. TRỤC IN (Cylinders)
    └── Trục in ống đồng khắc laser theo mẫu riêng của từng khách
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

## 3. QUY TẮC ĐỊNH DANH SẢN PHẨM: `item_name` VS `custom_alias`

Để đảm bảo vừa đáp ứng tính pháp lý khi xuất chứng từ ERPNext vừa tối ưu tốc độ cho buồng lái công nghiệp:

- **`item_name` (Tên pháp lý đầy đủ):** Lưu tên chính xác, đầy đủ quy cách để in Hóa đơn VAT, Hợp đồng kinh tế và Phiếu xuất kho giao nhận.
- **`custom_alias` (Tên thương mại buồng lái):** Tên ngắn gọn (tối đa 25 ký tự), bỏ từ ngữ rườm rà, dùng hiển thị trên 100% màn hình tác nghiệp, bảng dữ liệu, drawer và dropdown.

### Công thức đặt tên theo từng phân nhóm:

1. **Túi Nước Giặt Có Sẵn (NGCS):**
   - Tên buồng lái (`custom_alias`): `NGCS {Size} {Màu} - {Mẫu in}` (Ví dụ: `NGCS Nhỏ Đỏ - Đam Mê`, `NGCS Trung Tím - Nước Hoa`).
2. **Túi Màng Đơn (TMD):**
   - Tên buồng lái (`custom_alias`): `{Chất liệu} {Kiểu quai} {WxL}` (Bỏ chữ "Túi", ví dụ: `HD quai thỏ 17x25`, `PE hột xoài 20x30`).
3. **Túi Màng Ghép Đặt Riêng (TP):**
   - Tên buồng lái (`custom_alias`): `{Brand} {Dung tích} {Biến thể/Màu}` (Ví dụ: `888 3.2Kg Hồng`, `TopGia MBTP`, `Lamy 2Kg Vàng`).
4. **Trục In Ống Đồng (TRUC):**
   - `item_code`: `TRUC-{Mã trục NCC}` (Ví dụ: `TRUC-G4006940`).
   - Tên buồng lái (`custom_alias`): `Trục {Brand} {Dung tích} {Mẫu}` (Không lặp lại mã trục trong ngoặc kép).
5. **Màng NVL & Cuộn BTP:**
   - Màng đơn NVL: `{Vật liệu} K{Khổ} {Độ dày}mic` (Ví dụ: `PA K700 15mic`, `PE sữa K700 190mic`).
   - Cuộn BTP: `Cuộn {Brand} - {Mẫu in}` (Ví dụ: `Cuộn 888 - Phấn Thơm`).

---

## 4. NĂM KỊCH BẢN KINH DOANH & SẢN XUẤT THỰC TẾ (SẾP DUYỆT)

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
