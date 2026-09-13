# BẢNG ÁNH XẠ CHUẨN ERPNEXT NATIVE (VI - EN) — BAO BÌ VẠN PHÁT
**Phiên bản:** ERPNext Native v16  
**Phạm vi áp dụng:** Bắt buộc cho toàn bộ Agent, Lập trình viên, Schema Database, REST API và Giao diện UI/UX. Nghiêm cấm tự ý bịa đặt hoặc dùng từ ngữ ngoài bảng chuẩn này.

---

## 1. DANH MỤC KHÁCH HÀNG (DocType `Customer`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` | Khóa chính tự sinh theo Naming Series (`CUST-.YYYY.-.#####`) | **Mã khách hàng** |
| `customer_name` | Tên pháp lý đầy đủ trên giấy phép ĐKKD, dùng in hóa đơn VAT và hợp đồng | **Tên pháp nhân** |
| `alias` | Tên rút gọn, tên thương mại nhận diện nhanh trên UI tác nghiệp hàng ngày (Unique) | **Tên gọi tắt** |
| `customer_type` | Phân loại tư cách pháp lý (`Company`, `Individual`, `Partnership`) | **Loại khách hàng** |
| `customer_group` | Phân loại kênh bán hoặc nhóm đối tượng khách hàng (`Customer Group`) | **Nhóm khách hàng** |
| `territory` | Phân vùng địa lý giao nhận hàng, chành xe (`Territory`) | **Khu vực** |
| `payment_terms` | Mẫu điều khoản thanh toán cọc và công nợ (`Payment Terms Template`) | **Điều khoản thanh toán** |
| `default_currency` | Đơn vị tiền tệ giao dịch hạch toán (Mặc định `VND`) | **Loại tiền tệ** |
| `default_price_list` | Bảng giá bán áp dụng mặc định cho khách (`Price List`) | **Bảng giá mặc định** |
| `credit_limits` *(Child Table)* | Bảng con theo dõi hạn mức công nợ theo từng công ty | **Hạn mức công nợ** |
| `credit_limit` *(trong bảng con)* | Số tiền tối đa cho phép nợ đối với khách trả sau | **Hạn mức nợ** |
| `bypass_credit_limit_check` | Cờ cho phép xuất hàng vượt hạn mức nợ | **Cho phép vượt hạn mức** |
| `tax_id` | Mã số thuế của doanh nghiệp khách hàng | **Mã số thuế** |
| `primary_address` | Địa chỉ văn phòng / nhà xưởng giao hàng chính thức | **Địa chỉ** |
| `customer_primary_contact` | Người đại diện giao dịch / mua hàng chính | **Người liên hệ** |
| `mobile_no` | Số điện thoại di động người liên hệ | **Số điện thoại** |
| `email_id` | Địa chỉ thư điện tử nhận hóa đơn, báo giá | **Email** |
| `customer_items` *(Child Table)* | Bảng con danh sách các sản phẩm in độc quyền của khách | **Mặt hàng đặt riêng** |
| `disabled` | Cờ khóa ngừng giao dịch với khách hàng này (0: Hoạt động, 1: Khóa) | **Ngừng giao dịch** |

---

## 2. DANH MỤC SẢN PHẨM / VẬT TƯ (DocType `Item`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `item_code` | Mã định danh duy nhất quét barcode, tem kiện hàng (`TP-`, `NGCS-`, `TMD-`, `TRUC-`, `NVL-`, `BTP-`) | **Mã sản phẩm** |
| `item_name` | Tên thương mại ngắn gọn hiển thị trên UI (Tối đa 25 ký tự, không nhồi nhét quy cách kỹ thuật) | **Tên sản phẩm** |
| `description` | Mô tả kỹ thuật đầy đủ (kích thước, cấu trúc màng, độ dày, màu in, phụ kiện) dùng xuất văn bản/PDF | **Mô tả kỹ thuật** |
| `item_group` | Phân loại cây danh mục quản lý kho và tài khoản kế toán (`Item Group`) | **Nhóm hàng** |
| `stock_uom` | Đơn vị tính kho chuẩn mực (`Túi`, `Kg`, `m`, `Cây`, `Cái`) | **Đơn vị tính** |
| `brand` | Thương hiệu bao bì in trên sản phẩm (`888`, `BABA`, `Lamy`, `Vietcoat`, `Vinplus`...) | **Thương hiệu** |
| `is_stock_item` | Cờ theo dõi xuất-nhập-tồn kho vật lý (1: Theo dõi tồn kho, 0: Dịch vụ/Phi vật lý) | **Theo dõi tồn kho** |
| `is_sales_item` | Cờ cho phép đưa sản phẩm vào Báo giá và Đơn bán hàng | **Được phép bán** |
| `is_purchase_item` | Cờ cho phép đưa mặt hàng vào Đơn mua hàng NCC (NVL, trục, túi mua ngoài) | **Được phép mua** |
| `standard_rate` | Giá bán tiêu chuẩn tham chiếu | **Giá niêm yết** |
| `min_order_qty` | Sản lượng đặt hàng tối thiểu cho 1 lần chạy máy / mua hàng | **Số lượng tối thiểu** |
| `safety_stock` | Mức tồn kho an toàn để cảnh báo mua thêm vật tư | **Tồn kho an toàn** |
| `default_material_request_type` | Loại yêu cầu vật tư mặc định (`Purchase` cho hàng mua ngoài, `Manufacture` cho hàng sản xuất xưởng) | **Hình thức cung ứng** |
| `disabled` | Cờ đánh dấu sản phẩm đã ngừng kinh doanh trên thị trường | **Ngừng kinh doanh** |

---

## 3. ĐƠN BÁN HÀNG (DocType `Sales Order`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` | Số hiệu đơn đặt hàng duy nhất theo Naming Series (`SO-.YY.-.#####`) | **Mã đơn hàng** |
| `transaction_date` | Ngày lập và xác nhận đơn đặt hàng | **Ngày đặt hàng** |
| `delivery_date` | Ngày cam kết giao đủ hàng cho khách | **Ngày hẹn giao** |
| `customer` | Mã khách hàng liên kết (`Link: Customer`) | **Khách hàng** |
| `customer_name` | Tên pháp nhân khách hàng (kế thừa tự động từ Customer) | **Tên pháp nhân** |
| `payment_terms_template` | Mẫu điều khoản thanh toán áp dụng cho đơn | **Chính sách thanh toán** |
| `advance_paid` | Tổng số tiền cọc thực tế khách đã thanh toán | **Đã đặt cọc** |
| `net_total` | Tổng tiền hàng trước thuế VAT | **Tiền hàng trước thuế** |
| `total_taxes_and_charges` | Tổng tiền thuế VAT (8% hoặc 10%) | **Tiền thuế VAT** |
| `grand_total` | Tổng số tiền thanh toán cuối cùng của đơn hàng (đã gồm VAT và trục) | **Tổng thanh toán** |
| `rounded_total` | Số tiền làm tròn theo đồng tiền VND | **Tổng làm tròn** |
| `docstatus` | Trạng thái vòng đời chứng từ (0: Đơn nháp, 1: Đã duyệt chính thức, 2: Đã hủy) | **Trạng thái chứng từ** |
| `status` | Tiến độ giao hàng và thanh toán (`Draft`, `To Deliver and Bill`, `Completed`, `Cancelled`) | **Tiến độ đơn hàng** |
| `items` *(Child Table)* | Bảng con chi tiết các dòng sản phẩm và trục in trong đơn | **Danh sách mặt hàng** |

---

## 4. CHI TIẾT MẶT HÀNG ĐƠN BÁN (DocType `Sales Order Item`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `item_code` | Mã định danh sản phẩm bán (`Link: Item`) | **Mã sản phẩm** |
| `item_name` | Tên sản phẩm rút gọn hiển thị trên bảng tác nghiệp | **Tên sản phẩm** |
| `description` | Quy cách kỹ thuật chi tiết của dòng hàng | **Mô tả kỹ thuật** |
| `qty` | Số lượng sản phẩm khách đặt mua | **Số lượng** |
| `stock_uom` | Đơn vị tính chuẩn của sản phẩm | **Đơn vị tính** |
| `rate` | Đơn giá bán cho 1 đơn vị sản phẩm (chưa VAT) | **Đơn giá** |
| `amount` | Thành tiền của dòng hàng (`qty * rate`) | **Thành tiền** |
| `delivered_qty` | Số lượng thực tế đã xuất kho giao cho khách | **Số lượng đã giao** |
| `billed_amt` | Số tiền đã phát hành hóa đơn tài chính | **Số tiền đã xuất HĐ** |

---

## 5. BÁO GIÁ R&D (DocType `Quotation`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` | Số hiệu báo giá theo Naming Series (`QT-.YY.-.#####`) | **Mã báo giá** |
| `transaction_date` | Ngày tính toán và phát hành báo giá | **Ngày báo giá** |
| `party_name` | Mã khách hàng nhận báo giá (`Link: Customer`) | **Khách hàng** |
| `customer_name` | Tên pháp nhân khách hàng | **Tên pháp nhân** |
| `valid_till` | Ngày hết hạn hiệu lực của mức giá chào | **Hiệu lực đến** |
| `order_type` | Loại hình báo giá (`Sales`, `Packaging R&D`) | **Loại báo giá** |
| `net_total` | Tổng giá trị hàng trước thuế | **Tiền hàng trước thuế** |
| `grand_total` | Tổng tiền báo giá cuối cùng gồm thuế và trục in | **Tổng tiền báo giá** |
| `status` | Trạng thái báo giá (`Draft`, `Open`, `Ordered`, `Lost`, `Expired`) | **Trạng thái báo giá** |

---

## 6. ĐƠN MUA HÀNG NCC (DocType `Purchase Order`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` | Số hiệu đơn mua hàng gửi nhà cung cấp (`PO-.YY.-.#####`) | **Mã đơn mua NCC** |
| `transaction_date` | Ngày phát hành đơn đặt hàng sang NCC | **Ngày đặt mua** |
| `supplier` | Mã nhà cung cấp màng, trục, túi ngoài, keo dung môi (`Link: Supplier`) | **Nhà cung cấp** |
| `supplier_name` | Tên pháp nhân nhà cung cấp | **Tên nhà cung cấp** |
| `schedule_date` | Ngày NCC cam kết giao hàng về kho Vạn Phát | **Ngày hẹn nhận** |
| `grand_total` | Tổng số tiền phải trả cho nhà cung cấp | **Tổng tiền mua** |
| `status` | Tiến độ nhập hàng và hóa đơn (`Draft`, `To Receive and Bill`, `Completed`) | **Tiến độ mua hàng** |
| `items` *(Child Table)* | Danh sách các loại vật tư, trục hoặc dịch vụ mua ngoài | **Danh sách vật tư mua** |

---

## 7. DANH MỤC NHÀ CUNG CẤP (DocType `Supplier`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` | Mã định danh nhà cung cấp tự sinh | **Mã nhà cung cấp** |
| `supplier_name` | Tên pháp nhân đầy đủ của nhà cung cấp | **Tên nhà cung cấp** |
| `supplier_group` | Nhóm nhà cung cấp (`Màng thô`, `Trục in`, `Gia công in lụa`, `Keo & Dung môi`) | **Nhóm nhà cung cấp** |
| `supplier_type` | Phân loại tư cách pháp nhân (`Company`, `Individual`) | **Loại nhà cung cấp** |
| `country` | Quốc gia xuất xứ của nhà cung cấp | **Quốc gia** |
| `payment_terms` | Điều khoản thanh toán công nợ mua hàng với NCC | **Điều khoản thanh toán** |
| `disabled` | Cờ ngừng mua hàng từ nhà cung cấp này | **Ngừng hợp tác** |
