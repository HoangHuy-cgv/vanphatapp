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

## PHẦN 2: THIẾT KẾ MASTER DATA CHUẨN ERPNEXT NATIVE

### 1. Cây Nhóm Hàng (Sếp chốt 2026-09-11 theo 09-san-pham-chinh + NH-0001..0019)
```text
All Item Groups
├── Màng nguyên vật liệu (NVL: Màng PE / PA / PET / Màng khác + Hạt nhựa + Hóa chất + Vật tư + Trục in)
└── Thành phẩm túi — 4 nhánh:
    ├── Nhánh 1. Túi màng ghép (có vòi: 888, Lamy, Xốt, BABA, Topgia… / không vòi)
    ├── Nhánh 2. Túi màng đơn (túi 1 lớp bán Kg: cây đàn, Phong Nguyên, LOTUS…)
    ├── Nhánh 3. Cuộn màng ghép (BTP: input cắt túi hoặc bán nguyên cuộn)
    └── Nhánh 4. Túi NGCS (in sẵn OEM: TP-0001..0013, 3 lớp tự SX / 4 lớp mua Trang Tín)
```
(Mã: TP- túi hoàn chỉnh, NVL- màng/keo, BTP- cuộn ghép, TRUC- trục. Chi tiết NH: `01-master-data.md` §1.3.)

---

### 2. Quy Chuẩn Đặt Mã Hàng (`Item Code`) Bằng Naming Series
Hệ thống tự động nhảy số, loại bỏ hoàn toàn việc con người tự viết tắt gây trùng lặp:

* **`TP-.#####`** *(Túi hoàn chỉnh)*: `TP-00001`, `TP-00002`...
* **`NVL-.#####`** *(NVL màng đơn + keo/dung môi)*: `NVL-00001`, `NVL-00002`...
* **`BTP-.#####`** *(Cuộn ghép + túi chưa vòi)*: `BTP-00001`, `BTP-00002`...
* **`TRUC-.#####`** *(Trục in ống đồng)*: `TRUC-00001`, `TRUC-00002`...
(Sếp duyệt 2026-09-11: bỏ MD/CM/TNG, chỉ giữ NVL/BTP/TP/TRUC.)

---

### 3. Quy Chuẩn Tên Hiển Thị (UI) & Tên In PDF (Print Format)

* **Trên màn hình giao diện (`Item Name`):** Siêu ngắn gọn theo công thức:  
  **`[Brand / Loại] + [Dung tích] + [Đặc trưng cốt lõi]`**
  * Ví dụ: `TopGia 2L - Đắm say` *(20 ký tự, không bao giờ vỡ giao diện grid)*.
* **Trên phiếu in PDF gửi khách (`Print Format / Jinja2`):**  
  Mẫu in sẽ tự động ghép các trường kỹ thuật thành một dòng hoàn chỉnh:
  ```jinja2
  {{ doc.item_name }} (Cấu trúc: {{ doc.item_group }} | Đáy: {{ doc.bottom_type }} | Vòi: {{ doc.spout_type }})
  ```
  * Kết quả hiển thị trên PDF:  
    *TopGia 2L - Đắm say (Cấu trúc: Túi đáy đứng màng ghép phức hợp | Đáy: Ghép rời | Vòi: Phi 22 kèm quai xách oval)*

---

## PHẦN 3: CÁC KỊCH BẢN VẬN HÀNH THỰC TẾ (USE CASES)

### Kịch bản 1: Túi in sẵn bán đại trà (MTS) — UNKNOWN (Sếp 2026-09-11)
* Danh sách mã in sẵn thực tế chưa xác minh (file in-lụa có 40+ mẫu, không khớp bộ 13 mã cũ). Chờ Sếp cung cấp danh sách mới dựng Template/biến thể.
* Vận hành (khi có danh sách): tồn min-max, thiếu hàng chạy Work Order bù kho.

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

---

## PHẦN 4: NGUYÊN TẮC CHUẨN HÓA KỸ THUẬT BAO BÌ (ĐÁY & VÒI)

1. **Túi xếp hông:** Mặc định hiểu là **Không vòi** và **Không phải túi đáy đứng Doypack**. Không chia nhánh thừa thãi trên cây thư mục.
2. **Túi 8 cạnh đáy phẳng (Box Pouch):** Bản chất là **ghép đáy phẳng rời độc lập**, hàn 4 cạnh đáy kết hợp 4 cạnh thân tạo thành chiếc hộp tự đứng vững chãi.
3. **Túi đáy đứng có vòi (Túi nước giặt):** Đáy có thể gập liền thân (chừa trắng) hoặc ghép đáy rời từ cuộn màng thứ 2. Vòi được hàn nhiệt phẳng ở đỉnh hoặc góc chéo.
