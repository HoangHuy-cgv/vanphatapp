# BẢNG ÁNH XẠ CHUẨN ERPNEXT NATIVE (VI - EN) & NAMING SERIES — BAO BÌ VẠN PHÁT

> **Mục đích:** Nguồn chân lý duy nhất (SSOT) cho toàn bộ Schema Database, DocTypes, Fieldnames, Naming Series, và REST API theo đúng chuẩn ERPNext Native v16.
> **Phạm vi áp dụng:** Bắt buộc cho 100% Agent, lập trình viên, backend services và frontend interfaces. Nghiêm cấm tự ý suy đoán, chế tạo trường ảo hoặc dùng từ ngữ ngoài bảng chuẩn này.

---

## 1. QUY CHUẨN NAMING SERIES TOÀN HỆ THỐNG (FRAFFE NATIVE V16)

Hệ thống sử dụng cơ chế Native Naming Series của Frappe Framework (`tabSeries`):
- **Master Data:** Dùng mã định danh duy nhất không reset theo thời gian (`prefix-.#####`).
- **Chứng từ giao dịch:** Tự động reset số thứ tự theo tháng (`prefix-.YY..MM.-.###`). Không dùng cron job hay code custom; Frappe tự động sinh mã mới vào 00:00 ngày đầu tháng.

| Phân hệ / Nghiệp vụ | DocType ERPNext Native | Cú pháp Naming Series Chuẩn | Ví dụ Sinh Mã | Chu kỳ Reset | Ghi chú vận hành |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Khách hàng** | `Customer` | `KH-.#####` | `KH-00001` | Không reset | Mã định danh đối tác khách hàng |
| **Nhà cung cấp** | `Supplier` | `NCC-.#####` | `NCC-00001` | Không reset | Mã đối tác cung ứng màng, trục, keo, gia công |
| **Trục in ống đồng** | `Item` *(Nhóm Trục In)* | `TRUC-{Mã laser NCC}` | `TRUC-G4006940` | Theo mã laser NCC | Mã quản lý tài sản trục in vật lý (item_code lấy trực tiếp TRUC-{Mã laser NCC}) |
| **Báo giá R&D** | `Quotation` | `BG-.YY..MM.-.###` | `BG-2609-001` | Hàng tháng | Mã báo giá R&D gửi khách hàng |
| **Đơn đặt hàng bán** | `Sales Order` | `DH-.YY..MM.-.###` | `DH-2609-001` | Hàng tháng | Trọng tâm buồng lái kinh doanh |
| **Đơn mua hàng NCC** | `Purchase Order` | `MH-.YY..MM.-.###` | `MH-2609-001` | Hàng tháng | Mua màng NVL, keo, gia công ngoài |
| **Lệnh sản xuất** | `Work Order` | `LSX-.YY..MM.-.###` | `LSX-2609-001` | Hàng tháng | Lệnh xưởng: In -> Ghép -> Cắt -> Vòi |
| **Phiếu giao hàng** | `Delivery Note` | `GH-.YY..MM.-.###` | `GH-2609-001` | Hàng tháng | Phiếu xuất kho giao hàng cho khách |
| **Phiếu nhận hàng** | `Purchase Receipt` | `NH-.YY..MM.-.###` | `NH-2609-001` | Hàng tháng | Phiếu nhập kho từ NCC hoặc xưởng gia công |
| **Hóa đơn bán hàng** | `Sales Invoice` | `HD-.YY..MM.-.###` | `HD-2609-001` | Hàng tháng | Hóa đơn tài chính và theo dõi nợ 131 |
| **Phiếu thu tiền cọc** | `Payment Entry` *(Receive)* | `PT-.YY..MM.-.###` | `PT-2609-001` | Hàng tháng | Thu tiền cọc hoặc thanh toán đợt cuối |
| **Phiếu chi tiền NCC** | `Payment Entry` *(Pay)* | `PC-.YY..MM.-.###` | `PC-2609-001` | Hàng tháng | Chi trả tiền mua màng, keo, gia công |

---

## 2. DANH MỤC KHÁCH HÀNG (DocType `Customer`)

| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Khóa chính tự sinh theo Naming Series (`KH-.#####`) | **Mã khách hàng** |
| `customer_name` | Tên pháp lý đầy đủ có dấu theo ĐKKD/Thuế (chỉ dùng khi xuất văn bản: HĐ VAT, hợp đồng kinh tế, báo giá in) | **Tên pháp nhân (Xuất văn bản)** |
| `alias` | Tên thương mại / tên gọi tắt (viết hoa/Title Case ngắn gọn, dùng làm tên chính trên UI/UX buồng lái) | **Tên gọi tắt (UI/UX)** |
| `customer_type` | Phân loại tư cách pháp lý (`Company`, `Individual`, `Partnership`) | **Loại khách hàng** |
| `customer_group` | Phân loại kênh khách (`Khách Hàng Bao Bì Màng Ghép`, `Khách Hàng Túi Màng Đơn`) | **Nhóm khách hàng** |
| `territory` | Phân vùng địa lý giao nhận, chành xe (`Territory`) | **Khu vực** |
| `payment_terms` | Mẫu điều khoản thanh toán cọc và công nợ (`Payment Terms Template`) | **Điều khoản thanh toán** |
| `default_currency` | Tiền tệ giao dịch hạch toán (Mặc định `VND`) | **Loại tiền tệ** |
| `default_price_list` | Bảng giá bán áp dụng mặc định cho khách | **Bảng giá mặc định** |
| `credit_limits` *(Child Table)* | Bảng con theo dõi hạn mức công nợ | **Hạn mức công nợ** |
| `credit_limit` *(Child Table)* | Số tiền tối đa cho phép nợ đối với khách trả sau | **Hạn mức nợ** |
| `bypass_credit_limit_check` | Cờ cho phép xuất hàng vượt hạn mức nợ | **Cho phép vượt hạn mức** |
| `tax_id` | Mã số thuế của doanh nghiệp khách hàng | **Mã số thuế** |
| `primary_address` | Địa chỉ văn phòng / nhà xưởng giao hàng chính thức | **Địa chỉ** |
| `customer_primary_contact` | Người đại diện giao dịch / mua hàng chính | **Người liên hệ** |
| `mobile_no` | Số điện thoại di động người liên hệ | **Số điện thoại** |
| `email_id` | Địa chỉ thư điện tử nhận hóa đơn, báo giá | **Email** |
| `customer_items` *(Child Table)* | Danh sách sản phẩm in độc quyền của khách | **Mặt hàng đặt riêng** |
| `disabled` | Cờ khóa ngừng giao dịch (0: Hoạt động, 1: Khóa) | **Ngừng giao dịch** |

---

## 3. DANH MỤC SẢN PHẨM & VẬT TƯ (DocType `Item`)

| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `item_code` | Mã định danh duy nhất quét barcode (`TP-`, `NGCS-`, `TMD-`, `TRUC-{Mã laser}`, `NVL-`, `BTP-`) | **Mã sản phẩm** |
| `item_name` | Tên sản phẩm chuẩn mực, ngắn gọn (Loại túi + Màu + Dung tích + Mẫu in/Brand), KHÔNG nhồi quy cách kỹ thuật; quy cách in kèm bên dưới từ các trường spec | **Tên sản phẩm (Xuất văn bản)** |
| `custom_alias` *(Custom Field)* | Tên thương mại rút gọn dùng riêng trên UI/UX buồng lái (Title Case, ngắn gọn: Bỏ "Túi", hiển thị bảng/drawer/dropdown) | **Tên gọi tắt (Alias UI/UX)** |
| `description` | Mô tả kỹ thuật chi tiết dựng từ spec (kích thước, cấu trúc màng, độ dày, màu in, phụ kiện) | **Mô tả kỹ thuật** |
| `item_group` | Phân loại cây danh mục quản lý kho và tài khoản kế toán | **Nhóm hàng** |
| `stock_uom` | Đơn vị tính kho chuẩn mực (`Túi`, `Kg`, `m`, `Cây`, `Cái`) | **Đơn vị tính** |
| `brand` | Thương hiệu bao bì (`888`, `TopGia`, `BABA`, `Lamy`, `Vietcoat`...) | **Thương hiệu** |
| `is_stock_item` | Cờ theo dõi xuất-nhập-tồn kho vật lý (1: Theo dõi tồn kho, 0: Dịch vụ) | **Theo dõi tồn kho** |
| `is_sales_item` | Cờ cho phép đưa sản phẩm vào Báo giá và Đơn bán hàng | **Được phép bán** |
| `is_purchase_item` | Cờ cho phép đưa mặt hàng vào Đơn mua hàng NCC | **Được phép mua** |
| `standard_rate` | Giá bán tiêu chuẩn tham chiếu | **Giá niêm yết** |
| `min_order_qty` | Sản lượng đặt hàng tối thiểu cho 1 lần chạy máy / mua hàng | **Số lượng tối thiểu** |
| `safety_stock` | Mức tồn kho an toàn để cảnh báo sản xuất / mua thêm | **Tồn kho an toàn** |
| `default_material_request_type` | Loại cung ứng mặc định (`Purchase`: Mua ngoài; `Manufacture`: Xưởng SX) | **Hình thức cung ứng** |
| `customer` | Khách hàng sở hữu mẫu in độc quyền (MTO) | **Khách hàng sở hữu** |
| `customer_items` *(Child Table native → `Item Customer Detail`)* | Bảng con mã biến thể KH: `customer_name` (Link Customer) + `customer_group` (tự fetch) + `ref_code` (Data, mã riêng của KH, reqd). 1 TP/BTP = đúng 1 dòng con 1 KH; NGCS/TMD/NVL/BTP/TRUC không dòng con (bán nhiều KH, phân biệt bằng in lụa `custom_screen_print_brand`) | **Mã biến thể KH (bảng con)** |
| `customer_code` *(native tự join)* | ERPNext tự nối các `ref_code` (qua `fill_customer_code`), dùng search mã biến thể | **Mã KH tổng hợp (tìm kiếm)** |
| `custom_structure_layers` | Cấu trúc màng ghép phân cách bằng dấu `/` (vd: `PET/MPET/PA/PE sữa`) | **Cấu trúc màng ghép** |
| `custom_thickness_mic` | Tổng độ dày màng ghép hoặc màng đơn ($\mu m$) | **Độ dày (mic)** |
| `custom_film_width_mm` | Khổ cuộn màng đưa vào máy ghép hoặc chia cuộn (mm) | **Khổ màng (mm)** |
| `custom_pouch_width_mm` | Khổ ngang thành phẩm túi W (mm) | **Chiều rộng túi W** |
| `custom_pouch_length_mm` | Chiều cao thành phẩm túi L (mm) | **Chiều dài túi L** |
| `custom_gusset_mm` | Kích thước nếp gấp đáy hoặc xếp hông G (mm) | **Độ mở đáy G** |
| `custom_cut_length_mm` | Bước cắt túi trên máy cắt dán (Pitch mm) | **Bước cắt dao** |
| `custom_print_tech` | Công nghệ in (`In trục ống đồng`, `In offset (Không trục)`, `In lụa`, `Không in`) | **Công nghệ in** |
| `custom_accessory_spec` | Phụ kiện miệng túi (`Hàn kín`, `Vòi 16mm`, `Vòi 10mm`, `Vòi 22mm`, `Khóa Zipper`) | **Phụ kiện miệng túi** |
| `custom_cylinder_item` | Liên kết tới mã bộ trục in ống đồng (`TRUC-`) | **Mã trục in liên kết** |
| `custom_cylinder_code` | Mã khắc laser định danh trên quả trục in của NCC (vd: `G4006940`) | **Mã laser trục** |
| `custom_cylinder_location` | Địa điểm lưu giữ bộ trục in (Kho Vạn Phát, Kho Kiến Tâm...) | **Kho giữ trục** |
| `disabled` | Cờ ngừng kinh doanh sản phẩm (1: Ngừng bán, 0: Đang bán) | **Ngừng kinh doanh** |

---

## 4. ĐƠN BÁN HÀNG (DocType `Sales Order` & `Sales Order Item`)

### 4.1. Đơn Bán Hàng Tổng Thể (DocType `Sales Order`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Số hiệu đơn đặt hàng duy nhất theo Naming Series (`DH-.YY..MM.-.###`) | **Mã đơn hàng** |
| `transaction_date` | Ngày lập và xác nhận đơn đặt hàng | **Ngày đặt hàng** |
| `delivery_date` | Ngày cam kết giao đủ hàng cho khách | **Ngày hẹn giao** |
| `customer` | Mã khách hàng liên kết (`Link: Customer`) | **Khách hàng** |
| `customer_name` | Tên pháp nhân khách hàng (kế thừa tự động từ Customer) | **Tên pháp nhân** |
| `payment_terms_template` | Mẫu điều khoản thanh toán áp dụng cho đơn | **Chính sách thanh toán** |
| `advance_paid` | Tổng số tiền cọc thực tế khách đã thanh toán | **Đã đặt cọc** |
| `net_total` | Tổng tiền hàng trước thuế VAT | **Tiền hàng trước thuế** |
| `total_taxes_and_charges` | Tổng tiền thuế VAT (8% hoặc 10%) | **Tiền thuế VAT** |
| `grand_total` | Tổng số tiền thanh toán cuối cùng của đơn hàng | **Tổng thanh toán** |
| `rounded_total` | Số tiền làm tròn theo đồng tiền VND | **Tổng làm tròn** |
| `docstatus` | Vòng đời chứng từ (0: Đơn nháp, 1: Đã duyệt chính thức, 2: Đã hủy) | **Trạng thái chứng từ** |
| `status` | Tiến độ xử lý (`Draft`, `To Deliver and Bill`, `Completed`, `Cancelled`) | **Tiến độ đơn hàng** |
| `items` *(Child Table)* | Danh sách các dòng mặt hàng và trục in trong đơn | **Danh sách mặt hàng** |

### 4.2. Chi Tiết Dòng Mặt Hàng (DocType `Sales Order Item`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `item_code` | Mã sản phẩm bán (`Link: Item`) | **Mã sản phẩm** |
| `item_name` | Tên pháp lý sản phẩm | **Tên sản phẩm** |
| `custom_screen_print_brand` | Tên brand in lụa lần 2 lên phôi có sẵn (NGCS / TMD) | **Brand in lụa** |
| `qty` | Số lượng sản phẩm khách đặt mua | **Số lượng** |
| `stock_uom` | Đơn vị tính chuẩn | **Đơn vị tính** |
| `rate` | Đơn giá bán cho 1 đơn vị sản phẩm (chưa VAT) | **Đơn giá** |
| `amount` | Thành tiền của dòng hàng (`qty * rate`) | **Thành tiền** |
| `delivered_qty` | Số lượng thực tế đã xuất kho giao cho khách | **Số lượng đã giao** |
| `billed_amt` | Số tiền đã phát hành hóa đơn tài chính | **Số tiền đã xuất HĐ** |

---

## 5. BÁO GIÁ R&D (DocType `Quotation` & `Quotation Item`)
 
### 5.1. Báo Giá Tổng Thể (DocType `Quotation`)

| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Số hiệu báo giá theo Naming Series (`BG-.YY..MM.-.###`) | **Mã báo giá** |
| `transaction_date` | Ngày tính toán và phát hành báo giá | **Ngày báo giá** |
| `quotation_to` | Đối tượng nhận báo giá (Cố định `Customer` theo chuẩn v16) | **Loại đối tượng** |
| `party_name` | Mã khách hàng nhận báo giá (`Link: Customer`, `KH-.#####`) | **Khách hàng** |
| `customer_name` | Tên pháp nhân khách hàng (kế thừa tự động từ Customer) | **Tên pháp nhân** |
| `valid_till` | Ngày hết hiệu lực của mức giá chào | **Hiệu lực đến** |
| `order_type` | Loại hình báo giá (`Sales`, `Packaging R&D`) | **Loại báo giá** |
| `net_total` | Tổng giá trị hàng trước thuế | **Tiền hàng trước thuế** |
| `grand_total` | Tổng tiền báo giá cuối cùng gồm thuế và trục in | **Tổng tiền báo giá** |
| `status` | Trạng thái (`Draft`, `Open`, `Ordered`, `Lost`, `Expired`) | **Trạng thái báo giá** |
| `items` *(Child Table)* | Danh sách sản phẩm túi và trục in báo giá | **Danh sách mặt hàng** |

### 5.2. Chi Tiết Dòng Mặt Hàng Báo Giá (DocType `Quotation Item`)

| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `item_code` | Mã sản phẩm báo giá (`Link: Item`) | **Mã sản phẩm** |
| `item_name` | Tên sản phẩm | **Tên sản phẩm** |
| `custom_screen_print_brand` | Tên thương hiệu/mẫu in lụa của khách hàng lên phôi có sẵn (NGCS / TMD) | **Brand in lụa (Khách)** |
| `qty` | Số lượng sản phẩm báo giá | **Số lượng** |
| `stock_uom` | Đơn vị tính chuẩn | **Đơn vị tính** |
| `rate` | Đơn giá chào bán cho 1 đơn vị sản phẩm (chưa VAT) | **Đơn giá** |
| `amount` | Thành tiền của dòng hàng (`qty * rate`) | **Thành tiền** |

---

## 6. ĐƠN MUA HÀNG NCC & NHẬP KHO (DocType `Purchase Order` & `Purchase Receipt`)

### 6.1. Đơn Mua Hàng NCC (DocType `Purchase Order`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Số hiệu đơn mua hàng gửi NCC (`MH-.YY..MM.-.###`) | **Mã đơn mua NCC** |
| `transaction_date` | Ngày phát hành đơn đặt hàng sang NCC | **Ngày đặt mua** |
| `supplier` | Mã nhà cung cấp màng, keo, trục (`Link: Supplier`) | **Nhà cung cấp** |
| `supplier_name` | Tên pháp nhân nhà cung cấp | **Tên nhà cung cấp** |
| `schedule_date` | Ngày NCC cam kết giao hàng về kho Vạn Phát | **Ngày hẹn nhận** |
| `grand_total` | Tổng số tiền phải trả cho NCC | **Tổng tiền mua** |
| `status` | Tiến độ nhập hàng và hóa đơn (`Draft`, `To Receive and Bill`, `Completed`) | **Tiến độ mua hàng** |
| `items` *(Child Table)* | Danh sách vật tư, màng ghép, keo, dung môi mua ngoài | **Danh sách vật tư mua** |

### 6.2. Phiếu Nhận Hàng NCC (DocType `Purchase Receipt`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Số phiếu nhập kho mua hàng (`NH-.YY..MM.-.###`) | **Mã phiếu nhận** |
| `supplier` | Mã nhà cung cấp | **Nhà cung cấp** |
| `posting_date` | Ngày hàng về nhập kho xưởng Vạn Phát | **Ngày nhận hàng** |
| `status` | Tiến độ nhập kho (`Draft`, `To Bill`, `Completed`) | **Trạng thái nhận** |
| `items` *(Child Table)* | Chi tiết số lượng thực tế nhận đối soát với đơn mua | **Chi tiết hàng nhận** |

---

## 7. DANH MỤC NHÀ CUNG CẤP (DocType `Supplier`)

| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Mã định danh nhà cung cấp tự sinh (`NCC-.#####`) | **Mã nhà cung cấp** |
| `supplier_name` | Tên pháp lý đầy đủ có dấu theo GPKD/Thuế (chỉ dùng khi xuất văn bản: Hợp đồng mua hàng, Hóa đơn VAT, Đơn mua hàng PO chính thức) | **Tên pháp nhân (Xuất văn bản)** |
| `alias` | Tên gọi tắt / tên thương mại rút gọn (viết hoa/Title Case, dùng làm tên chính trên UI/UX buồng lái) | **Tên gọi tắt (UI/UX)** |
| `supplier_group` | Nhóm NCC (`Gia Công In & Túi Màng Ghép`, `Màng Thô NVL & Gia Công In`, `Hóa Chất & Keo Ghép`, `Hóa Chất & Dung Môi`, `Phụ Kiện Bao Bì`, `Vật Tư Đóng Gói`, `Nội Bộ & Phân Xưởng Vạn Phát`) | **Nhóm nhà cung cấp** |
| `supplier_type` | Phân loại tư cách pháp nhân (`Company`, `Individual`) | **Loại nhà cung cấp** |
| `country` | Quốc gia xuất xứ của nhà cung cấp (`Việt Nam`) | **Quốc gia** |
| `payment_terms` | Điều khoản thanh toán công nợ mua hàng với NCC | **Điều khoản thanh toán** |
| `default_currency` | Tiền tệ giao dịch mua hàng (`VND`) | **Loại tiền tệ** |
| `tax_id` | Mã số thuế doanh nghiệp / hộ kinh doanh | **Mã số thuế** |
| `primary_address` | Địa chỉ nhà máy, xưởng gia công hoặc trụ sở | **Địa chỉ xưởng/trụ sở** |
| `supplier_primary_contact` | Người liên hệ đại diện kinh doanh của NCC | **Người liên hệ** |
| `mobile_no` | Số điện thoại liên hệ đặt hàng (fetch từ Contact) | **Điện thoại liên hệ** |
| `disabled` | Cờ ngừng giao dịch (0: Đang giao dịch, 1: Ngừng) | **Ngừng hợp tác** |

---

## 8. LỆNH SẢN XUẤT XƯỞNG (DocType `Work Order`, `Operation`, `Workstation`)

### 8.1. Lệnh Sản Xuất (DocType `Work Order`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Mã lệnh sản xuất tự sinh (`LSX-.YY..MM.-.###`) | **Mã lệnh sản xuất** |
| `production_item` | Mã mặt hàng cần sản xuất (`Link: Item`) | **Sản phẩm sản xuất** |
| `item_name` | Tên thương mại sản phẩm hiển thị trên UI | **Tên sản phẩm** |
| `bom_no` | Mã định mức vật tư kỹ thuật (`Link: BOM`) | **Mã định mức BOM** |
| `qty` | Sản lượng túi hoặc mét màng cần sản xuất theo lệnh | **Số lượng sản xuất** |
| `produced_qty` | Sản lượng thực tế các tổ máy đã hoàn thành nhập kho | **Số lượng hoàn thành** |
| `sales_order` | Đơn hàng bán liên kết nguồn phát sinh lệnh | **Đơn hàng liên kết** |
| `status` | Trạng thái thực tế (`Draft`, `Submitted`, `In Process`, `Completed`, `Stopped`) | **Tiến độ sản xuất** |
| `planned_start_date` | Thời điểm bắt đầu lên chuyền chạy máy | **Ngày bắt đầu** |
| `planned_end_date` | Thời điểm dự kiến xong hàng đóng thùng | **Ngày hoàn thành** |

### 8.2. Công Đoạn Sản Xuất (DocType `Operation`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Mã định danh công đoạn (`GHEP-MANG`, `CAT-TUI`, `DONG-VOI`, `THOI-MANG`) | **Mã công đoạn** |
| `operation_name` | Tên tiếng Việt hiển thị trên lệnh sản xuất | **Tên công đoạn** |
| `workstation` | Trạm máy mặc định thực hiện công đoạn | **Trạm máy thực hiện** |

### 8.3. Trạm Máy Xưởng (DocType `Workstation`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` / `workstation_name` | Tên/Mã trạm máy vật lý (`WS-GHEP-01`, `WS-CAT-01`, `WS-VOI-01`, `WS-THOI-01`) | **Mã trạm máy** |
| `production_capacity` | Số chuyền chạy cùng lúc (Mặc định: 1) | **Công suất chuyền** |

---

## 9. ĐỊNH MỨC SẢN XUẤT (DocType `BOM` & `BOM Item`)

### 9.1. Định Mức Tổng Thể (DocType `BOM`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` / `bom_no` | Mã định mức duy nhất (`BOM-[item_code]-001`) | **Mã định mức BOM** |
| `item` | Mã mặt hàng sản xuất (Cuộn BTP hoặc Túi TP) | **Sản phẩm BOM** |
| `quantity` | Sản lượng định mức cơ sở ($1.000\text{ m}$ cuộn BTP hoặc $1.000\text{ Túi}$) | **Sản lượng định mức** |
| `uom` | Đơn vị tính của sản lượng định mức (`m` hoặc `Túi`) | **Đơn vị tính** |
| `is_active` | Cờ hiệu lực của định mức (1: Có hiệu lực) | **Đang áp dụng** |
| `is_default` | Định mức mặc định để tự động kéo vào Lệnh sản xuất | **Định mức mặc định** |
| `process_loss_percentage` | Tỷ lệ hao hụt sản xuất công nghệ (Ghép 2.0%, Cắt 2.5%) | **Tỷ lệ hao hụt (%)** |
| `with_operations` | Kèm chi phí công đoạn theo giờ không (0: Tắt) | **Kèm chi phí công đoạn** |
| `items` *(Child Table)* | Danh sách các vật tư cấu thành và định mức tiêu hao | **Chi tiết vật tư định mức** |

### 9.2. Chi Tiết Vật Tư Định Mức (DocType `BOM Item`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `item_code` | Mã nguyên vật liệu hoặc bán thành phẩm đầu vào | **Mã vật tư** |
| `qty` | Định mức số lượng vật tư cần để sản xuất 1 lô cơ sở | **Định mức tiêu hao** |
| `uom` | Đơn vị tính của vật tư (`m`, `Kg`, `Cái`, `Túi`) | **Đơn vị tính** |
| `rate` | Đơn giá dự toán tham chiếu (ẩn trên bảng buồng lái khi không có số liệu) | **Đơn giá dự toán** |
| `note` | Ghi chú kỹ thuật pha chế hoặc quy cách đóng gói | **Ghi chú kỹ thuật** |

---

## 10. GIAO NHẬN, CÔNG NỢ & DÒNG TIỀN (DocType `Delivery Note`, `Sales Invoice`, `Payment Entry`, `Warehouse`)

### 10.1. Phiếu Giao Hàng (DocType `Delivery Note`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Số phiếu xuất kho giao hàng (`GH-.YY..MM.-.###`) | **Mã phiếu giao** |
| `customer` | Mã khách hàng nhận hàng | **Khách hàng** |
| `posting_date` | Ngày thực hiện bốc hàng và xuất kho | **Ngày giao hàng** |
| `total_qty` | Tổng số lượng túi/kg thực tế giao cho khách | **Tổng số lượng giao** |
| `status` | Tiến độ giao nhận (`Draft`, `To Bill`, `Completed`, `Cancelled`) | **Trạng thái giao** |

### 10.2. Hóa Đơn Bán Hàng & Công Nợ (DocType `Sales Invoice`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Số hóa đơn tài chính (`HD-.YY..MM.-.###`) | **Mã hóa đơn** |
| `customer` | Khách hàng phát hành hóa đơn | **Khách hàng** |
| `posting_date` | Ngày ghi nhận doanh thu và công nợ | **Ngày hóa đơn** |
| `grand_total` | Tổng tiền thanh toán trên hóa đơn | **Tổng tiền hóa đơn** |
| `outstanding_amount` | Số tiền khách hàng còn nợ chưa thanh toán | **Còn phải thu** |
| `status` | Tình trạng (`Draft`, `Unpaid`, `Partially Paid`, `Paid`, `Overdue`) | **Tình trạng thanh toán** |

### 10.3. Phiếu Thu / Chi Tiền (DocType `Payment Entry`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Số chứng từ thu/chi (`PT-.YY..MM.-.###` / `PC-.YY..MM.-.###`) | **Số phiếu thu/chi** |
| `payment_type` | Chiều dòng tiền (`Receive`: Thu tiền khách; `Pay`: Chi tiền NCC) | **Loại phiếu** |
| `party_type` | Loại đối tác (`Customer` hoặc `Supplier`) | **Đối tượng** |
| `party` | Mã đối tác khách hàng hoặc nhà cung cấp | **Đối tác** |
| `paid_amount` | Số tiền thực tế nhận cọc hoặc thanh toán (VND) | **Số tiền giao dịch** |
| `reference_no` | Mã tham chiếu ủy nhiệm chi / chuyển khoản ngân hàng | **Mã giao dịch NH** |
| `status` | Tình trạng chứng từ (`Draft`, `Submitted`, `Cancelled`) | **Trạng thái** |

### 10.4. Danh Mục Kho Hàng (DocType `Warehouse`)
| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `name` | Mã định danh kho theo quy chuẩn ERPNext | **Mã kho** |
| `warehouse_name` | Tên kho thực tế bằng tiếng Việt | **Tên kho** |
| `warehouse_type` | Loại hình kho (`Stores`, `Work In Progress`, `Finished Goods`, `Scrap`) | **Loại kho** |
| `account` | Tài khoản kế toán hàng tồn kho tương ứng (`152`, `154`, `155`, `153`) | **Tài khoản kho** |
| `disabled` | Cờ ngừng sử dụng kho (0: Hoạt động, 1: Ngừng) | **Ngừng sử dụng** |

---

## 11. TÀI KHOẢN NGƯỜI DÙNG & VAI TRÒ (DocType `User` & `Role`)

| ERPNext Native English | Ý nghĩa nghiệp vụ | Thuật ngữ Tiếng Việt chuẩn |
| :--- | :--- | :--- |
| `email` | Email đăng nhập hệ thống duy nhất (Khóa chính) | **Tài khoản đăng nhập** |
| `first_name` | Tên nhân sự hoặc tên gọi tác nghiệp | **Tên** |
| `last_name` | Họ và chữ lót | **Họ và chữ đệm** |
| `full_name` | Họ và tên đầy đủ | **Họ và tên** |
| `mobile_no` | Số điện thoại di động đăng nhập / liên hệ | **SĐT đăng nhập** |
| `role_profile_name` | Bộ hồ sơ vai trò phân quyền chuẩn | **Hồ sơ vai trò** |
| `department` | Phòng ban công tác | **Phòng ban** |
| `enabled` | Trạng thái tài khoản (1: Đang hoạt động, 0: Khóa) | **Trạng thái hoạt động** |

### Bảng Phân Quyền Vai Trò Chuẩn:
- `System Manager`: Quản trị toàn hệ thống, cấu hình và phân quyền.
- `Sales User`: Lập Báo giá (`Quotation`), Đơn hàng (`Sales Order`), xem Khách hàng và Bảng giá.
- `Accounts User`: Quản lý Hóa đơn (`Sales/Purchase Invoice`), Thu/Chi (`Payment Entry`), Công nợ 131/331.
- `Manufacturing User`: Lập Lệnh sản xuất (`Work Order`), kiểm tra Định mức (`BOM`).
- `Stock User`: Lập Phiếu nhập kho (`Purchase Receipt`), Phiếu giao hàng (`Delivery Note`), Quản lý kho.
