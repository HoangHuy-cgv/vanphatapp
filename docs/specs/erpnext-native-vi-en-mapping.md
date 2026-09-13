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
| `name` | Mã định danh nhà cung cấp tự sinh (`SUPP-#####`) | **Mã nhà cung cấp** |
| `supplier_name` | Tên pháp nhân đầy đủ theo GPKD / Hóa đơn tài chính | **Tên nhà cung cấp** |
| `alias` | Tên gọi tắt / tên thương mại hiển thị trên UI cockpit & Đơn mua hàng PO (Native v16) | **Tên gọi tắt** |
| `supplier_group` | Nhóm nhà cung cấp (`Gia Công In & Túi Màng Ghép`, `Màng Thô NVL & Gia Công In`, `Hóa Chất & Keo Ghép`, `Hóa Chất & Dung Môi`, `Phụ Kiện Bao Bì`, `Vật Tư Đóng Gói`, `Gia Công Túi Màng Đơn`, `Gia Công In Lụa`, `Máy Móc & Phụ Tùng Cơ Khí`, `Nội Bộ & Phân Xưởng Vạn Phát`) | **Nhóm nhà cung cấp** |
| `supplier_type` | Phân loại tư cách pháp nhân (`Company`, `Individual`) | **Loại nhà cung cấp** |
| `country` | Quốc gia xuất xứ của nhà cung cấp (`Việt Nam`) | **Quốc gia** |
| `payment_terms` | Điều khoản thanh toán công nợ mua hàng với NCC (`Công nợ gối đầu 30 ngày`, `Theo từng lô`, ...) | **Điều khoản thanh toán** |
| `default_currency` | Tiền tệ giao dịch mua hàng (`VND`) | **Loại tiền tệ** |
| `tax_id` | Mã số thuế doanh nghiệp / hộ kinh doanh | **Mã số thuế** |
| `primary_address` | Địa chỉ nhà máy, xưởng gia công hoặc trụ sở | **Địa chỉ xưởng/trụ sở** |
| `supplier_primary_contact` | Người liên hệ đại diện kinh doanh của NCC | **Người liên hệ** |
| `supplier_primary_phone` | Số điện thoại liên hệ đặt hàng | **Điện thoại liên hệ** |
| `disabled` | Cờ ngừng mua hàng từ nhà cung cấp này (0: Đang giao dịch, 1: Ngừng) | **Ngừng hợp tác** |

---

## 8. LỆNH SẢN XUẤT XƯỞNG (DocType `Work Order`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
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

---

## 9. PHIẾU GIAO HÀNG / XUẤT KHO (DocType `Delivery Note`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` | Số phiếu xuất kho giao hàng (`GH-.YY..MM.-.###`) | **Mã phiếu giao** |
| `customer` | Mã khách hàng nhận hàng | **Khách hàng** |
| `posting_date` | Ngày thực hiện bốc hàng và xuất kho | **Ngày giao hàng** |
| `total_qty` | Tổng số lượng túi/kg thực tế giao cho khách | **Tổng số lượng giao** |
| `status` | Tiến độ giao nhận (`Draft`, `To Bill`, `Completed`, `Cancelled`) | **Trạng thái giao** |
| `items` *(Child Table)* | Bảng con chi tiết các kiện hàng, số lượng xuất giao | **Chi tiết hàng xuất** |

---

## 10. PHIẾU NHẬN HÀNG NCC / GIA CÔNG (DocType `Purchase Receipt`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` | Số phiếu nhập kho mua hàng (`NH-.YY..MM.-.###`) | **Mã phiếu nhận** |
| `supplier` | Mã nhà cung cấp màng, keo, trục, in lụa | **Nhà cung cấp** |
| `posting_date` | Ngày hàng về nhập kho xưởng Vạn Phát | **Ngày nhận hàng** |
| `status` | Tiến độ nhập kho (`Draft`, `To Bill`, `Completed`) | **Trạng thái nhận** |
| `items` *(Child Table)* | Chi tiết số lượng thực tế nhận (đối soát chênh lệch với đơn mua) | **Chi tiết hàng nhận** |

---

## 11. HÓA ĐƠN BÁN HÀNG & CÔNG NỢ (DocType `Sales Invoice`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` | Số hóa đơn tài chính (`HD-.YY..MM.-.###`) | **Mã hóa đơn** |
| `customer` | Khách hàng phát hành hóa đơn | **Khách hàng** |
| `posting_date` | Ngày ghi nhận doanh thu và công nợ | **Ngày hóa đơn** |
| `grand_total` | Tổng tiền thanh toán trên hóa đơn | **Tổng tiền hóa đơn** |
| `outstanding_amount` | Số tiền khách hàng còn nợ chưa thanh toán | **Còn phải thu** |
| `status` | Trạng thái hóa đơn (`Draft`, `Unpaid`, `Partially Paid`, `Paid`, `Overdue`) | **Tình trạng thanh toán** |

---

## 12. PHIẾU THU / CHI CỌC & THANH TOÁN (DocType `Payment Entry`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` | Số chứng từ thu/chi (`PT-.YY..MM.-.###` / `PC-.YY..MM.-.###`) | **Số phiếu thu/chi** |
| `payment_type` | Chiều dòng tiền (`Receive`: Thu tiền khách, `Pay`: Chi tiền NCC) | **Loại phiếu** |
| `party_type` | Loại đối tác (`Customer` hoặc `Supplier`) | **Đối tượng** |
| `party` | Mã đối tác khách hàng hoặc nhà cung cấp | **Đối tác** |
| `paid_amount` | Số tiền thực tế nhận cọc hoặc thanh toán (VND) | **Số tiền giao dịch** |
| `reference_no` | Mã tham chiếu ủy nhiệm chi / chuyển khoản ngân hàng | **Mã giao dịch NH** |
| `status` | Tình trạng chứng từ (`Draft`, `Submitted`, `Cancelled`) | **Trạng thái** |

---

## 13. DANH MỤC KHO HÀNG (DocType `Warehouse`)

| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` | Mã định danh kho theo quy chuẩn ERPNext (`[warehouse_code] - [company_abbr]`) | **Mã kho** |
| `warehouse_name` | Tên kho thực tế bằng tiếng Việt | **Tên kho** |
| `warehouse_type` | Loại hình kho chuẩn (`Stores`, `Work In Progress`, `Finished Goods`, `Scrap`) | **Loại kho** |
| `parent_warehouse` | Kho cha cấp trên trong cấu trúc cây kho (`All Warehouses`) | **Kho cấp trên** |
| `is_group` | Cờ phân định nhóm kho tổng hợp hay kho chi tiết thực tế (0: Kho chứa hàng) | **Là nhóm kho** |
| `account` | Tài khoản kế toán hàng tồn kho tương ứng (`152`, `154`, `155`, `153`) | **Tài khoản kho** |
| `description` | Mô tả chi tiết loại hàng hóa và vật tư lưu trữ trong kho | **Mô tả hàng lưu trữ** |
| `disabled` | Cờ ngừng sử dụng kho (0: Đang hoạt động, 1: Ngừng hoạt động) | **Ngừng sử dụng** |

---

## 14. CÔNG ĐOẠN & TRẠM MÁY (DocType `Operation` & `Workstation`)

### 14.1. Công Đoạn Sản Xuất (DocType `Operation`)
| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` | Mã định danh công đoạn (`GHEP-MANG`, `CAT-TUI`, `DONG-VOI`, `THOI-MANG`) | **Mã công đoạn** |
| `operation_name` | Tên tiếng Việt hiển thị trên lệnh sản xuất | **Tên công đoạn** |
| `workstation` | Trạm máy mặc định thực hiện công đoạn | **Trạm máy thực hiện** |
| `description` | Mô tả quy trình kỹ thuật vận hành máy | **Mô tả quy trình** |

### 14.2. Trạm Máy Xưởng (DocType `Workstation`)
| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` / `workstation_name` | Tên/Mã trạm máy vật lý (`WS-GHEP-01`, `WS-CAT-01`, `WS-VOI-01`, `WS-THOI-01`) | **Mã trạm máy** |
| `production_capacity` | Số chuyền hoặc số dòng sản phẩm máy có thể chạy cùng lúc (Mặc định: 1) | **Công suất chuyền** |
| `hour_rate` | Chi phí chạy máy theo giờ (Quy định: 0.0 do xưởng tính công theo mét và cái) | **Chi phí giờ máy** |
| `description` | Thông số kỹ thuật, cấu hình máy | **Thông số máy** |

---

## 15. ĐỊNH MỨC SẢN XUẤT (DocType `BOM` & `BOM Item`)

### 15.1. Định Mức Tổng Thể (DocType `BOM`)
| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `name` / `bom_no` | Mã định mức duy nhất (`BOM-[item_code]-001`) | **Mã định mức BOM** |
| `item` | Mã mặt hàng sản xuất (Cuộn BTP hoặc Túi TP) | **Sản phẩm BOM** |
| `quantity` | Sản lượng định mức cơ sở ($1.000\text{ m}$ cuộn BTP hoặc $1.000\text{ Túi}$) | **Sản lượng định mức** |
| `uom` | Đơn vị tính của sản lượng định mức (`m` hoặc `Túi`) | **Đơn vị tính** |
| `is_active` | Cờ hiệu lực của định mức (1: Có hiệu lực) | **Đang áp dụng** |
| `is_default` | Định mức mặc định để tự động kéo vào Lệnh sản xuất | **Định mức mặc định** |
| `process_loss_percentage` | Tỷ lệ hao hụt sản xuất công nghệ (Ghép màng 2.0%, Cắt dán 2.5%) | **Tỷ lệ hao hụt (%)** |
| `with_operations` | Có theo dõi chi phí công đoạn theo giờ không (0: Tắt để tối giản) | **Kèm chi phí công đoạn** |
| `items` *(Child Table)* | Danh sách các vật tư cấu thành và định mức tiêu hao | **Chi tiết vật tư định mức** |

### 15.2. Chi Tiết Vật Tư Định Mức (DocType `BOM Item`)
| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `item_code` | Mã nguyên vật liệu hoặc bán thành phẩm đầu vào | **Mã vật tư** |
| `qty` | Định mức số lượng vật tư cần để sản xuất 1 lô cơ sở | **Định mức tiêu hao** |
| `uom` | Đơn vị tính của vật tư (`m`, `Kg`, `Cái`, `Túi`) | **Đơn vị tính** |
| `rate` | Đơn giá dự toán tham chiếu của vật tư (VND) | **Đơn giá dự toán** |
| `note` | Ghi chú kỹ thuật pha chế hoặc quy cách đóng thùng | **Ghi chú kỹ thuật** |

---

## 16. TÀI KHOẢN NGƯỜI DÙNG & PHÂN QUYỀN (DocType `User` & `Role`)

### 16.1. Tài Khoản Người Dùng (DocType `User`)
| ERPNext Native English | Ý nghĩa | Đề xuất map VI là... |
| :--- | :--- | :--- |
| `email` | Email đăng nhập hệ thống duy nhất (Khóa chính) | **Tài khoản đăng nhập** |
| `first_name` | Tên nhân sự hoặc tên gọi tác nghiệp hàng ngày | **Tên** |
| `last_name` | Họ và chữ lót | **Họ và chữ đệm** |
| `full_name` | Họ và tên đầy đủ hiển thị trên giao diện | **Họ và tên** |
| `user_type` | Phân loại người dùng (`System User`: Nhân viên nội bộ; `Website User`: Khách hàng/NCC) | **Loại tài khoản** |
| `role_profile_name` | Bộ vai trò phân quyền chuẩn gán cho nhân viên | **Hồ sơ vai trò** |
| `enabled` | Trạng thái tài khoản (1: Đang hoạt động, 0: Khóa) | **Trạng thái hoạt động** |

### 16.2. Bộ Vai Trò Quyền Hạn (Role Profiles & Roles)
| Role ERPNext | Tên Vai Trò Tiếng Việt | Phạm Vi Quyền Hạn & Chứng Từ Tác Nghiệp |
| :--- | :--- | :--- |
| `System Manager` | **Quản Trị Hệ Thống** | Toàn quyền kiểm soát hệ thống, cấu hình, Master Data, duyệt giá và hạn mức tín dụng. |
| `Sales User` | **Nhân Viên Kinh Doanh** | Lập Báo Giá (`Quotation`), Đơn Bán Hàng (`Sales Order`), xem thông tin Khách Hàng và Bảng giá. |
| `Accounts User` | **Kế Toán Viên** | Quản lý Hóa Đơn (`Sales/Purchase Invoice`), Phiếu Thu/Chi (`Payment Entry`), Theo dõi công nợ 131/331 và dòng tiền máy thổi. |
| `Manufacturing User` | **Quản Đốc Sản Xuất** | Lập và theo dõi Lệnh Sản Xuất (`Work Order`), kiểm tra Định Mức (`BOM`), điều độ máy cắt/ghép. |
| `Stock User` | **Thủ Kho** | Lập Phiếu Nhập Kho NVL (`Purchase Receipt`), Phiếu Giao Hàng (`Delivery Note`), Quản lý 5 kho vật lý. |

