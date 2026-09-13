# Handoff Chuyển Giao Session Mới — ERP & Portal Vạn Phát (vanphatapp)
*Thời điểm cập nhật: 2026-09-13 | Trọng tâm: Chuẩn hoá Danh mục Master Data & Raw-Data theo Wording ERPNext Native*

---

## 1. TỔNG KẾT HIỆN TRẠNG ĐÃ HOÀN THÀNH (SESSION NÀY)

### 1.1. Hoàn Thiện Toàn Diện Trang Đơn Hàng (`/orders`) — 100% Sạch & Chuẩn
1. **Chia 3 Tab Nghiệp Vụ Riêng Biệt (Phương án 2 SSOT)**:
   - Tab 1: **`Xưởng sản xuất`** (Theo dõi hàng tự gia công Ghép $\rightarrow$ Cắt $\rightarrow$ Vòi, cột `VẬT TƯ & MÁY`).
   - Tab 2: **`Túi NGCS`** (Theo dõi phôi túi nước giặt in sẵn & tiến độ NCC in lụa, cột `IN LỤA NCC`).
   - Tab 3: **`Mua ngoài trọn gói`** (Theo dõi túi màng đơn HD/PE/PP và túi mua đứt NCC, cột `HẠN GIAO NCC`).
   - Tích hợp **Smart SLA Alert**: Tự động tính hạn giao NCC (`Còn x ngày`, `Hôm nay giao`, `Trễ x ngày` đỏ rực báo động giục hàng).
   - Triệt tiêu 100% mã code rác (`DH-`, `TP-`, `KH-`) trên tiêu đề và dữ liệu hiển thị table.
2. **Modal Tạo Đơn Hàng Mới (`ModalCreateOrder.vue`) — 1 Bước Duy Nhất (Single-Step Cockpit)**:
   - Tách rời hoàn toàn khỏi form Báo giá. Header trang Đơn hàng đổi thành nút **`+ Tạo đơn hàng`**.
   - Thao tác trực tiếp trên **Sản phẩm ĐÃ CÓ MÃ trong danh mục**: Chọn mã hàng là tự bung kích thước, cấu trúc màng, đơn giá chuẩn, người dùng **không phải gõ lại**.
   - **Tự động thích ứng thông minh theo 2 quy trình sản xuất**:
     - **Quy trình 1: MTO Sản phẩm độc quyền theo khách (`Túi màng ghép` / `Cuộn màng ghép`)**: Chọn khách $\rightarrow$ Lọc sản phẩm độc quyền của khách (VD: `Minh Râu 3.2Kg` của `DS 888`) $\rightarrow$ Bung bảng nhập các **Mẫu in / Màu sắc** (`Màu Hồng 10.000`, `Màu Tím 10.000`), nút `+ Thêm mẫu in`, checkbox trục in.
     - **Quy trình 2: MTS Phôi dùng chung (`Túi NGCS` / `Túi màng đơn`)**: Chọn khách $\rightarrow$ Nhập thương hiệu in lụa của khách (VD: `FUSIMI - Nước giặt cao cấp`) $\rightarrow$ Bảng chọn **Nhiều mã phôi khác nhau** (`NGCS Đỏ lớn 5.000`, `NGCS Đen lớn 5.000`), nút `+ Thêm loại phôi`.
   - Tự động tính tiền hàng, thuế VAT 8%, tiền trục, tổng thanh toán và tiền cọc yêu cầu 50%.
3. **Drawer Chi Tiết Đơn Hàng Mới (`DrawerOrderDetail.vue`)**:
   - **Hỗ trợ Multi-SKU / Multi-Variants**: Liệt kê rõ từng dòng mẫu in/hương vị kèm thumbnail ảnh maquette riêng (`44px`, click bung Lightbox phóng to), số lượng, đơn giá, thành tiền.
   - **Ẩn triệt để 100% chất liệu không dùng**: Chỉ hiển thị các chip màng thực tế của sản phẩm (VD chỉ dùng `PET`, `PA`, `PE sữa` thì chỉ render đúng 3 chip này).
   - **Tài chính tối giản, font to rõ**: Tiền hàng, VAT 8%, Tiền trục, **TỔNG THANH TOÁN** (In đậm `18px`), Đã cọc, Còn phải thu.
   - **Tiến độ vận hành không nhãn rác**: Triệt tiêu chữ "Vật tư màng", "Công đoạn máy", "Sản lượng", hiển thị trực tiếp value kèm thanh tiến độ mỏng.
   - **Font chữ chuẩn**: Chuẩn hóa toàn bộ lên `14px - 16px`, tương phản cao, số liệu `tabular-nums`.
   - **Footer State Machine**: HOLD $\rightarrow$ Ô cọc nhanh tại chỗ; Đang chạy $\rightarrow$ Báo cáo xưởng; Sẵn sàng giao $\rightarrow$ `+ XUẤT GIAO HÀNG` full-width sáng xanh.

### 1.2. Kiểm Thử & Quản Lý Mã Nguồn
- **Vite Build**: Pass 100% trong ~1.05s, không lỗi cảnh báo.
- **Headless Chrome Visual Proof**: Đã chụp và đối soát trực quan 5 màn hình:
  - `modal_create_order_mto.png` (Modal MTO DS888)
  - `modal_create_order_ngcs.png` (Modal MTS FUSIMI)
  - `drawer_baba_variants.png` (BABA 2 Mẫu in + Trục)
  - `drawer_minhrau_variants.png` (Minh Râu 2 Màu)
  - `drawer_fusimi_ngcs.png` (NGCS 2 Mã phôi)
- **Git Commit**: `83f980c` trên branch `master`. Working tree sạch tinh 100%.

---

## 2. TRỌNG TÂM CHO SESSION TIẾP THEO: MASTER DATA & RAW-DATA THEO ERPNEXT NATIVE

Theo chỉ đạo của Sếp, session tiếp theo sẽ tập trung vào **phần lõi dữ liệu master**:

### 2.1. Hoàn Thiện Các Danh Mục Master Data (Catalogs)
1. **Danh mục Mặt Hàng (`Item`)**:
   - Phân cấp rõ ràng theo Item Group và tiền tố mã:
     - `TP-`: Thành phẩm túi (Doypack đáy đứng, 3 biên, 8 cạnh, túi dán lưng...).
     - `BTP-`: Bán thành phẩm màng cuộn ghép (OPP/PE, PET/AL/PE...).
     - `NVL-`: Nguyên vật liệu (Màng đơn cuộn lớn, hạt nhựa, keo ghép khô, dung môi EA, vòi nhựa 16mm/22mm).
     - `TRUC-`: Bộ trục in ống đồng Rotogravure.
   - Lưu trữ đầy đủ thông số kỹ thuật bao bì trong ERPNext: Chiều rộng ($W$), Chiều dài ($L$), Xếp hông/Đáy ($G$), Cấu trúc màng (Layers), Độ dày ($\mu m$), Phụ kiện vòi, Quy cách đóng gói.
2. **Danh mục Khách Hàng (`Customer`)**:
   - Danh sách khách hàng, bí danh (Alias), thương hiệu (Brand), hạn mức công nợ & hình thức thanh toán (`Trả trước cọc 50%` / `Trả sau công nợ`).
3. **Danh mục Nhà Cung Cấp (`Supplier`)**:
   - NCC in lụa: Mộc Ấn, Anh Tùng...
   - NCC màng đơn/túi mua ngoài: Trang Tín, Hà Linh...
   - NCC màng in/màng ghép: Kiến Tâm, Tân Cường Phát...
4. **Danh mục Xưởng & Sản Xuất**:
   - Trạm máy (`Workstation`): Máy ghép màng, Máy chia cuộn, Máy cắt túi đáy đứng, Máy đóng vòi tự động.
   - Công đoạn (`Operation`): In gia công $\rightarrow$ Ghép màng khô $\rightarrow$ Cắt dán túi $\rightarrow$ Đóng vòi $\rightarrow$ Đóng thùng KCS.

### 2.2. Chuẩn Hoá Raw-Data Theo Wording Chuẩn ERPNext Native
- **Tuyệt đối tuân thủ SSOT**: [docs/specs/erpnext-native-vi-en-mapping.md](file:///var/home/huy/vanphatapp/docs/specs/erpnext-native-vi-en-mapping.md).
- **Cấm suy diễn**: Không sử dụng trường tự chế hoặc dữ liệu từ `archive/`. Mọi DocType và Fieldname phải khớp 1:1 với schema ERPNext v16:
  - Báo giá: `Quotation`
  - Đơn bán hàng: `Sales Order` (Child table: `Sales Order Item`)
  - Đơn mua hàng: `Purchase Order`
  - Lệnh sản xuất: `Work Order`
  - Phiếu giao hàng: `Delivery Note`
  - Phiếu nhập kho mua hàng: `Purchase Receipt`
  - Hóa đơn bán hàng: `Sales Invoice`
  - Bút toán thanh toán: `Payment Entry`

---

## 3. CÂU LỆNH MẪU KHI MỞ ĐẦU SESSION TIẾP THEO

Sếp chỉ cần copy câu lệnh sau và gửi cho em:

```text
Đọc docs/handoff.md và bắt tay ngay vào việc:
Hoàn thiện toàn diện các danh mục Master Data (Item, Customer, Supplier, Workstation, Operation) và chuẩn hoá raw-data theo đúng 100% wording ERPNext Native (dựa trên docs/specs/erpnext-native-vi-en-mapping.md).
```
