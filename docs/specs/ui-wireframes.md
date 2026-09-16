# Đặc Tả Giao Diện & Visual Wireframe (UI/UX Blueprint)

Tài liệu này là Single Source of Truth (SSOT) về mặt **Visual & Wireframe** cho toàn bộ hệ thống Bao Bì Vạn Phát (Portal Cockpit + Desk Native + Mẫu in PDF). Giúp bất kỳ lập trình viên hay AI Agent nào tiếp quản cũng có thể tái hiện chính xác 100% bố cục mà không cần đoán mò.

---

## 1. Trang Danh Mục Cockpit (`CatalogView.vue`)

### 1.1 Bố Cục Tổng Thể (1-Line Header + Bảng Dữ Liệu Tinh Gọn)
```text
+-------------------------------------------------------------------------------------------------------------------+
| [LOGO VP]  [Sản phẩm (142)] [Trục in] [Khách hàng] [Nhà cung cấp] [Nguyên vật liệu]   [🔍 Tìm kiếm tên, mã KH...]  [+ Thêm mới] |
+-------------------------------------------------------------------------------------------------------------------+
| TÊN GỌI QUEN (ALIAS)       | CHẤT LIỆU               | KÍCH THƯỚC (R x D x Dày) |   ĐÁY   | ĐVT | TRẠNG THÁI          |
+----------------------------+-------------------------+--------------------------+---------+-----+---------------------+
| PE Hột Xoài Trắng Sữa 30x42| PE Trong / Trắng sữa    | 300 x 420 x 0.07 mm      |   —     | kg  | [● Có sẵn]          |
| Túi 8 Cạnh Cà Phê DS 500g  | PET12 / AL7 / PE Trong  | 130 x 300 x 70 mm        | Đáy PT  | cái | [● MTO - Riêng]     |
| Túi Đáy Đứng Vòi Nước Giặt | PA15 / PE Trắng Sữa     | 180 x 260 x 40 mm        | Đáy ĐĐ  | cái | [● MTO - Riêng]     |
| Cuộn Màng Ghép Snack Tôm   | OPP20 / MPET15 / CPP25  | Khổ 420 mm x Bước 220 mm |   —     | kg  | [● MTO - Riêng]     |
+-------------------------------------------------------------------------------------------------------------------+
| Hiển thị 1 - 20 / 142 sản phẩm                                                          [< Trang trước] [1] [2] [Trang sau >] |
+-------------------------------------------------------------------------------------------------------------------+
```

### 1.2 Đặc Tả Tương Tác & Visual Specs
- **Header:** 1 hàng ngang duy nhất (`h-14`), gồm:
  - 5 Tab thực thể: `sp` (Sản phẩm), `truc` (Trục in), `kh` (Khách hàng), `ncc` (Nhà cung cấp), `nvl` (Nguyên vật liệu).
  - Thanh tìm kiếm tức thời: Debounce 250ms, tự hủy request cũ bằng `AbortController`.
  - Nút "+ Thêm mới": Mở Quick CRUD Drawer tương ứng với tab đang đứng.
- **Bảng dữ liệu:**
  - Chiều cao dòng: 44px (chuẩn touch target và quét mắt nhanh).
  - Click vào dòng: Mở Drawer chi tiết (`BaseDrawer`).
  - Số liệu (Kích thước, Số lượng, Đơn giá): Căn phải, dùng font Monospace (`tabular-nums`).

---

## 2. Modal Báo Giá Bước 1 (`ModalStep1Sale.vue`)

### 2.1 Bố Cục Modal Tạo Báo Giá Nhanh (Dành cho Sales)
```text
+------------------------------------------------------------------------------------+
|                                    TẠO BÁO GIÁ NHANH                               [✕] |
+------------------------------------------------------------------------------------+
| 1. PHÂN LOẠI BAO BÌ                                                                |
|    (•) Hàng có sẵn (Túi PE/PP/HD - Bán chung)     ( ) Hàng đặt riêng (Màng ghép MTO)  |
|                                                                                    |
| 2. LOẠI TÚI / QUY CÁCH                                                             |
|    [ 3 Biên ]   [ Đáy Đứng ]   [ Xếp Hông ]   [ 8 Cạnh Đáy Phẳng ]   [ Cuộn Màng ] |
|                                                                                    |
| 3. CÔNG NGHỆ IN                                                                    |
|    [ Không in ]       [ In Lụa (1-3 màu) ]       [ In Ống Đồng (Trục) ]             |
|                                                                                    |
| 4. PHỤ KIỆN KÈM THEO                                                               |
|    [ Không / Tự hàn kín ]      [ Zipper ]      [ Gắn Vòi 10/16/22mm ]              |
|                                                                                    |
| 5. THÔNG TIN KHÁCH HÀNG & KÍCH THƯỚC                                               |
|    Khách hàng: [ Công ty TNHH Mỹ Phẩm DS Cosmetic                     | 🔍 Tìm ]   |
|                                                                                    |
|    Rộng (W mm): [ 180   ]    Dài (L mm): [ 260   ]    Đáy/Hông (G mm): [ 40    ]   |
|    Độ dày (Zem / Mic): [ 100 Mic ]                     Số lượng dự kiến: [ 10.000  ]|
+------------------------------------------------------------------------------------+
| [ Hủy bỏ ]                                                    [ Tiếp Tục Tính Giá ➔ ] |
+------------------------------------------------------------------------------------+
```

### 2.2 Quy Tắc Validation (Guard Rails)
- Nút **"Tiếp Tục Tính Giá ➔"** chỉ sáng khi:
  1. Đã chọn Loại túi.
  2. Đã chọn Công nghệ in.
  3. Đã chọn Phụ kiện.
  4. Đã điền Khách hàng và các kích thước $W > 0, L > 0$.
- Nếu chọn "In Ống Đồng": Tự động kích hoạt luồng kiểm tra hoặc tạo mới Trục In ở Bước 2.

---

## 3. Drawer Báo Giá Bước 2 (`DrawerStep2Director.vue`)

### 3.1 Bố Cục Drawer Tính Giá & Duyệt (Dành cho Giám Đốc / R&D)
```text
+------------------------------------------------------------------------------------+
| SOẠN BÁO GIÁ & DUYỆT CẤU TRÚC (BƯỚC 2)                                         [✕] |
+------------------------------------------------------------------------------------+
| THÔNG TIN QUY CÁCH TÚI                                                             |
| Khách: CÔNG TY MỸ PHẨM DS COSMETIC  | Loại: Túi Đáy Đứng Có Vòi                    |
| Kích thước: 180 x 260 x Đáy 40 mm   | Số con chạy: 2 con (Khổ màng: 450 mm)        |
+------------------------------------------------------------------------------------+
| CẤU TRÚC MÀNG GHÉP (R&D)                                                           |
| + Lớp 1 (In):      [ PA 15 mic  ] - Tỷ trọng 1.14 - Đơn giá: 72.000 đ/kg           |
| + Lớp 2 (Hàn dán): [ PE Trong 85 mic ] - Tỷ trọng 0.925 - Đơn giá: 42.000 đ/kg     |
| + Keo ghép:       [ Khô 1:1:4  ] - Định mức 1.8 g/m2 - Đơn giá: 85.000 đ/kg        |
| -> Định mức: 12.45 g/cái | Diện tích túi: 0.108 m2 | Tỷ lệ phế: 8.0%               |
+------------------------------------------------------------------------------------+
| ⚡ SO SÁNH 2 NẤC GIÁ BÁO KHÁCH                                                     |
|                                                                                    |
| [ NẤC 1: TRÒN CUỘN TỐI ƯU (Khuyên dùng) ]   | [ NẤC 2: ĐÚNG SỐ LƯỢNG YÊU CẦU ]     |
| - Số lượng:  14.200 cái (Hết 1 cuộn màng)   | - Số lượng:  10.000 cái (Theo yêu cầu)|
| - Giá thành: 1.620 đ/cái                    | - Giá thành: 1.890 đ/cái (Đệm dở màng)|
| - Giá bán:   2.100 đ/cái (+30% LN)          | - Giá bán:   2.450 đ/cái (+30% LN)    |
| - Thành tiền: 29.820.000 đ                  | - Thành tiền: 24.500.000 đ            |
+------------------------------------------------------------------------------------+
| TIỀN TRỤC IN ỐNG ĐỒNG (Bóc tách độc lập, thanh toán 100% khi duyệt mẫu)             |
| - Số lượng trục: 04 cây (Trục Dài 500mm x CV 450mm)                                |
| - Đơn giá: 1.800.000 đ/cây -> Tổng tiền trục: 7.200.000 đ                         |
+------------------------------------------------------------------------------------+
| [ ← Quay lại Bước 1 ]                             [ In Preview PDF ] [ Tạo Báo Giá ] |
+------------------------------------------------------------------------------------+
```

---

## 4. Các Drawer Chi Tiết Danh Mục (Quick View & Quick CRUD)

### 4.1 Drawer Chi Tiết Sản Phẩm (`DrawerItemDetail.vue`)
```text
+--------------------------------------------------------------------+
| CHI TIẾT SẢN PHẨM                                              [✕] |
+--------------------------------------------------------------------+
| [ HÌNH ẢNH MẪU / BẢN VẼ TÚI ]                                      |
|                                                                    |
| Tên gọi: Túi Đáy Đứng Nước Giặt 2L                                 |
| Mã nội bộ: MTO-00042           | Loại: Hàng đặt riêng              |
| Khách hàng sở hữu: CTY CP TIÊU DÙNG SÀI GÒN                        |
|                                                                    |
| THÔNG SỐ KỸ THUẬT:                                                 |
| - Cấu trúc màng: PA15 / PE100                                      |
| - Kích thước: 220 x 320 x Đáy 50 mm                                |
| - Phụ kiện: Vòi 16mm (Vị trí góc 45 độ)                            |
| - Trục in liên kết: TRUC-SG-001 (4 cây - Kho A2)                   |
|                                                                    |
| LỊCH SỬ ĐƠN HÀNG:                                                  |
| - ĐH-2026-0812: 20.000 cái (Đã giao)                               |
| - ĐH-2026-0519: 15.000 cái (Đã giao)                               |
+--------------------------------------------------------------------+
| [ Sửa thông tin ]                                      [ Đóng (Esc) ] |
+--------------------------------------------------------------------+
```

### 4.2 Drawer Chi Tiết Khách Hàng (`DrawerCustomerDetail.vue`)
```text
+--------------------------------------------------------------------+
| THÔNG TIN KHÁCH HÀNG                                           [✕] |
+--------------------------------------------------------------------+
| Tên viết tắt: DS COSMETIC                                          |
| Tên pháp nhân: CÔNG TY TNHH MỸ PHẨM DS COSMETIC                    |
| Mã số thuế: 0314892831          | Điện thoại: 0908.123.456         |
| Địa chỉ: Lô B2, KCN Tân Bình, Tây Thạnh, Tân Phú, TP.HCM           |
|                                                                    |
| CHÍNH SÁCH CÔNG NỢ & ĐẶT CỌC:                                      |
| - Tỷ lệ cọc sản xuất: 50% khi duyệt thiết kế                       |
| - Cọc trục in: 100% trước khi làm trục                             |
| - Hạn mức công nợ: 50.000.000 đ | Thời hạn: 15 ngày                |
|                                                                    |
| DANH SÁCH BAO BÌ ĐÃ ĐẶT (03 mẫu):                                  |
| 1. Túi Mặt Nạ Dưỡng Da 12x16 (PET/AL/PE)                           |
| 2. Túi Đáy Đứng Sữa Rửa Mặt 100ml (PA/PE)                          |
+--------------------------------------------------------------------+
| [ Tạo Đơn Hàng Mới ]                                   [ Đóng (Esc) ] |
+--------------------------------------------------------------------+
```

---

## 5. Trang Đăng Nhập (`www/login.html`)

### 5.1 Bố Cục Giao Diện Login Dark Mode
```text
+--------------------------------------------------------------------+
|                          [ BACKGROUND NHÀ XƯỞNG DARK ]             |
|                                                                    |
|                    +------------------------------+                |
|                    |      [ LOGO VẠN PHÁT ]       |                |
|                    |     BAO BÌ VẠN PHÁT          |                |
|                    |  Hệ Thống Điều Hành Sản Xuất |                |
|                    |------------------------------|                |
|                    | Email / Tên đăng nhập:       |                |
|                    | [ admin@vanphat.com        ] |                |
|                    |                              |                |
|                    | Mật khẩu:                    |                |
|                    | [ ••••••••••••••••         ] |                |
|                    |                              |                |
|                    | [✓] Duy trì đăng nhập        |                |
|                    |                              |                |
|                    | [     ĐĂNG NHẬP HỆ THỐNG   ] |                |
|                    +------------------------------+                |
|                                                                    |
+--------------------------------------------------------------------+
```

---

## 6. Mẫu In PDF Báo Giá / Đơn Đặt Hàng Chuẩn (`print-format-quotation.html`)

Dựa trên mẫu chứng từ thực tế của Vạn Phát (có logo, thông tin pháp lý, bảng sản phẩm 2 nấc giá, dòng trục in và điều khoản thanh toán).

### 6.1 Layout Khổ Giấy A4 (Dọc)
```text
+-------------------------------------------------------------------------------------------------------+
|  [ LOGO VP ]   CÔNG TY TNHH SXTM BAO BÌ VẠN PHÁT                                                      |
|                VP: C4/5B34 Bùi Thanh Khiết, Tân Túc, Bình Chánh, TP.HCM | Hotline: 028.36206746        |
+-------------------------------------------------------------------------------------------------------+
|                                           BÁO GIÁ & ĐƠN ĐẶT HÀNG                                      |
|                                            (Số: BG-2026/09-082)                                       |
|                                                                               Ngày: 16/09/2026        |
|  Kính gửi:                                                                                            |
|  Đơn vị: CÔNG TY TNHH MỸ PHẨM DS COSMETIC                                                             |
|  Địa chỉ: Lô B2, KCN Tân Bình, Tây Thạnh, Tân Phú, TP.HCM                                              |
|  Mã số thuế: 0314892831                    Điện thoại: 0908.123.456                                   |
+-----+----------------------------------+-----+----------+------------------+--------------------------+
| STT | NỘI DUNG SẢN PHẨM & QUY CÁCH     | ĐVT | SỐ LƯỢNG | ĐƠN GIÁ (VNĐ)    | THÀNH TIỀN (VNĐ)         |
+-----+----------------------------------+-----+----------+------------------+--------------------------+
|  1  | Túi Đáy Đứng Vòi Nước Giặt 2L    | Cái |   14.200 |            2.100 |               29.820.000 |
|     | - Cấu trúc: PA15 / PE Trong 85   |     |          | (Nấc 1: Tròn cuộn|                          |
|     | - KT: 180 x 260 x Đáy 40 mm      |     |          |  giá ưu đãi nhất)|                          |
|     | - Phụ kiện: Gắn vòi 16mm         |     |          |                  |                          |
+-----+----------------------------------+-----+----------+------------------+--------------------------+
|  2  | Trục In Ống Đồng (4 màu)         | Cây |        4 |        1.800.000 |                7.200.000 |
|     | - Thanh toán 100% khi duyệt mẫu  |     |          |                  |                          |
+-----+----------------------------------+-----+----------+------------------+--------------------------+
|                                                           CỘNG TIỀN HÀNG:  |               37.020.000 |
|                                                           THUẾ GTGT (8%):  |                2.961.600 |
|                                                           TỔNG CỘNG THANH TOÁN:           39.981.600 |
+-------------------------------------------------------------------------------------------------------+
| Số tiền bằng chữ: Ba mươi chín triệu chín trăm tám mươi mốt nghìn sáu trăm đồng chẵn.                 |
|                                                                                                       |
| * Ghi chú & Điều khoản:                                                                               |
| 1. Đơn giá: Đã bao gồm chi phí bao bì và đóng gói tiêu chuẩn xưởng Vạn Phát.                          |
| 2. Dung sai số lượng giao hàng: ±10% theo thực tế ca sản xuất ống đồng.                               |
| 3. Tiến độ giao hàng: 12 - 15 ngày làm việc kể từ ngày duyệt mẫu in (Chromalin) và nhận cọc.          |
| 4. Thanh toán: Đặt cọc 50% khi xác nhận đơn hàng, 100% tiền trục in. Còn lại thanh toán khi giao hàng.|
|                                                                                                       |
|       ĐẠI DIỆN KHÁCH HÀNG                                         ĐẠI DIỆN BAO BÌ VẠN PHÁT            |
|       (Ký, ghi rõ họ tên & đóng dấu)                              (Ký, ghi rõ họ tên & đóng dấu)      |
+-------------------------------------------------------------------------------------------------------+
```
