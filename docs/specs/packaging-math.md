# Đặc tả Kỹ thuật & Công thức Tính toán Sản xuất Bao bì Màng ghép Vạn Phát

> **Mục đích:** Tài liệu chuẩn mực kỹ thuật và công thức toán học nội bộ xưởng Bao Bì Vạn Phát, dùng làm căn cứ logic để lập trình phân hệ Báo giá (Quotation Engine) và Định mức vật tư (BOM) trên Portal và ERPNext Native.
> **Căn cứ thực tế & Nguồn dữ liệu:** Dữ liệu sản xuất thực tế tại file `MÀNG.xlsx` (sheet GHI CHÚ, TUỆ NHI, KIẾN TÂM, VẠN PHÁT), `TIẾN ĐỘ SẢN XUẤT.xlsx` (sheet THEO DÕI TỔNG, 888-ĐỎ, PHẤN THƠM), `THÔNG TIN TRỤC IN.xlsx` và các hợp đồng kinh tế đã ký kết (Kova, Samran, IGC, Baba, Minh Râu...).

---

## 1. Bảng Tỷ trọng Màng Thực tế Xưởng (Workshop Density)

Công thức xác định định lượng diện tích (GSM - Grams per Square Meter):
$$\text{GSM } (g/m^2) = \text{Độ dày } (\mu m) \times \text{Tỷ trọng } (\rho, g/cm^3)$$

Công thức tính diện tích định mức trên 1 kg màng (Yield):
$$\text{Yield } (m^2/kg) = \frac{1.000}{\text{GSM}} = \frac{1.000}{\text{Độ dày } (\mu m) \times \text{Tỷ trọng } (g/cm^3)}$$

### Bảng Tỷ trọng Chuẩn Sản xuất (Sheet "GHI CHÚ" - File `MÀNG.xlsx`)

| Tên vật liệu màng | Ký hiệu | Tỷ trọng ($\rho, g/cm^3$) | Ứng dụng thực tế tại Vạn Phát | Đơn giá mua TB (VNĐ/kg) |
| :--- | :--- | :---: | :--- | :---: |
| **Màng PE Trong** | PE_TRONG / LLDPE | **0.925** | Lớp hàn dán trong cùng, dẻo dai | 42.500 - 49.000 |
| **Màng PE Sữa** | PES / LLDPE Sữa | **0.930** | Lớp hàn dán trong túi nước giặt, cản sáng | 51.000 - 52.000 |
| **Màng PET** | PET | **1.340** | Lớp in ngoài cùng, chịu nhiệt sấy mực | 46.000 - 48.000 |
| **Màng PA (Nylon)** | PA / BOPA | **1.140** | Lớp gia cường giữa, chống bục rách, giữ hương | 81.000 |
| **Màng Nhôm nguyên chất** | AL | **2.700** | Lớp chắn sáng 100%, cản ẩm và oxy tuyệt đối | 160.000 |
| **Màng PET Mạ Nhôm** | MPET | **1.400** | Lớp chắn sáng kinh tế (ánh bạc) | 57.000 |
| **Màng Ngọc** | NGOC | **0.920** | Màng ngọc cản sáng, dùng trong túi khăn ướt | 45.000 |
| **Màng OPP** | OPP / BOPP | **0.905** | Màng bóng in ngoài (túi khô, bánh kẹo) | 43.000 |
| **Màng CPP** | CPP / R-CPP | **0.900** | Màng hàn dán chịu nhiệt tiệt trùng | 46.000 |

*Ghi chú kiểm chứng:* Thực tế đơn hàng sheet VẠN PHÁT: Màng PE Trong 75 mic, khổ 660mm, chiều dài 12.000m $\rightarrow$ Khối lượng $= 0.66\text{ m} \times 12.000\text{ m} \times 75\mu m \times 0.925 / 1.000 = 549.45\text{ kg}$ (khớp 100% sổ cân kho).

---

## 2. Công thức Kích thước & Diện tích Trải phẳng 4 Kiểu Túi

Quy ước ký hiệu:
* $W$: Chiều rộng túi (m).
* $L$: Chiều dài/cao túi (m).
* $G$: Độ mở đáy đứng hoặc độ sâu xếp hông (m).

### 2.1. Túi 3 biên (Three-side Seal)
$$A_{pouch} (m^2) = 2 \times W \times L$$

### 2.2. Túi Xếp hông / Hàn lưng giữa (Center Seal / Gusseted Pouch)
Bao gồm biên hàn lưng và mối hàn đáy ($S \approx 15\text{ mm} = 0.015\text{ m}$):
$$A_{pouch} (m^2) = 2 \times (W + G) \times (L + 0.015)$$

### 2.3. Túi Đáy đứng (Doypack / Stand-up Pouch)
Đáy gấp mở hình thuyền xếp gọn:
$$A_{pouch} (m^2) = 2 \times W \times \left(L + \frac{G}{2}\right)$$

### 2.4. Túi 8 cạnh Đáy phẳng (Flat Bottom / Box Pouch)
Gồm 2 mặt chính + 2 hông + 1 đáy phẳng:
$$A_{pouch} (m^2) = 2 \times W \times L + 2 \times G \times L + W \times G$$

---

## 3. Định mức Keo Ghép, Dung Môi & Phụ Kiện Vòi

### 3.1. Keo Ghép Khô (Dry Lamination)
* Căn cứ lệnh sản xuất thực tế tại sheet `888-ĐỎ` và `PHẤN THƠM` (`TIẾN ĐỘ SẢN XUẤT.xlsx`):
  * Tỷ lệ pha keo ghép 3 lớp (PET/PA/PES): **1 phần Đóng rắn CL-3196K + 1 phần Keo D-9822K + 4 phần Dung môi Ethyl Acetate (EA)**.
  * Chi phí keo ghép chuẩn hóa: **$450\text{ đ/m}^2$** diện tích màng ghép.

### 3.2. Bảng Giá Phụ Kiện Vòi (Spout Pricing)
Vòi nhựa PE gắn túi nước giặt / hóa mỹ phẩm (căn cứ đơn mua phụ kiện):
* **Vòi $\varnothing 10\text{ mm}$**: $180\text{ đ/cái}$ (túi nước súc miệng, thạch, mẫu thử).
* **Vòi $\varnothing 16\text{ mm}$**: $227\text{ đ/cái}$ (túi nước giặt tiêu chuẩn $1L - 3.8kg$, nước rửa chén).
* **Vòi $\varnothing 22\text{ mm}$**: $356\text{ đ/cái}$ (túi lớn $3.6kg - 5L$, hóa chất).
* **Hàn kín**: $0\text{ đ}$ (khách tự hàn miệng túi sau khi chiết rót đóng gói).

---

## 4. Tỷ lệ Hao hụt Sản xuất Thực tế (Scrap Rate)

Quy mô mẻ chạy theo cuộn màng tiêu chuẩn ($L_{roll} = 1.500\text{ m}$):
* **Chạy 1 cuộn ($1.500\text{ m}$)**: Hao hụt tổng công đoạn là **$8.0\%$** (do chiếm tỷ trọng setup in và ghép cao).
* **Chạy 2 cuộn ($3.000\text{ m}$)**: Hao hụt tổng công đoạn là **$6.5\%$**.
* **Chạy $\ge 3$ cuộn ($\ge 4.500\text{ m}$)**: Hao hụt chạy ổn định là **$5.5\%$**.

---

## 5. Chiến lược Báo giá 2 Nấc & Tối ưu Sản xuất Xưởng

### 5.1. Bóc tách Độc lập Tiền Trục In Ống Đồng
* Trục in ống đồng ($TRUC$) là tài sản khuôn in khắc kim loại do khách hàng chi trả riêng cho đơn hàng đầu tiên (đơn giá xưởng gia công DONGYUN: khoảng $3.150.000 - 3.800.000\text{ đ/cây}$, trung bình chuẩn hóa **$3.500.000\text{ đ/cây}$**).
* **Nguyên tắc kế toán & báo giá:** Tuyệt đối **KHÔNG gộp tiền trục vào đơn giá túi**. Tiền trục in được tách thành dòng riêng biệt trên Báo giá.

### 5.2. Tối ưu Khổ Màng Rộng Chạy 2 Con (2-Lane Wide-Web Optimization)
* Với túi có chiều rộng $W \le 360\text{ mm}$ (hầu hết túi nước giặt $1L - 3.8kg$): Xưởng bố trí trục in dài $750 - 900\text{ mm}$, chọn màng khổ to $700 - 800\text{ mm}$ chạy **2 con song song (2 lane)**.
* Hiệu quả: Số túi ra máy trên mỗi mét dài cuộn màng gấp đôi, tối ưu chi phí chạy máy.

### 5.3. Báo giá 2 Nấc (2-Tier Quotation Model)
Khi khách hàng yêu cầu báo giá cho số lượng $Q_{req}$:

1. **Nấc 1 - Tròn cuộn tối ưu (ĐƠN GIÁ TỐT NHẤT - Best Unit Price):**
   * Số lượng sản xuất tối ưu $Q_{opt}$ tính theo số trọn cuộn màng ($1.500\text{ m} \times \text{lanes} \times (1 - \text{Scrap}) / L_{cut}$).
   * Khách lấy trọn vẹn $Q_{opt} \ge Q_{req}$. Định phí setup máy ($3.500.000\text{ đ}$) được chia đều cho sản lượng lớn nhất. Đơn giá túi là rẻ nhất.

2. **Nấc 2 - Đúng số lượng yêu cầu (ĐƠN GIÁ CAO HƠN - Risk Buffer Price):**
   * Áp dụng khi khách nhất quyết chỉ nhận đúng $Q_{req} < Q_{opt}$.
   * Vì xưởng vẫn phải chạy trọn cuộn màng (không thể cắt dở cuộn màng in), phần túi dôi dư $Q_{surplus} = Q_{opt} - Q_{req}$ xưởng phải lưu kho.
   * Đơn giá nấc 2 phải chịu thêm:
     * Định phí setup máy chia cho số lượng nhỏ hơn ($Q_{req}$).
     * Chi phí đệm rủi ro lưu kho màng dở dang: $(Q_{surplus} \times \text{Chi phí NVL màng} \times 50\%) / Q_{req}$.

3. **Đòn bẩy bán hàng (Upsell Pitch):**
   * Hệ thống tự động tính: "Khách chỉ cần thêm $[X]\text{ đ}$ là nhận thêm trọn vẹn $[Q_{surplus}]$ túi với đơn giá rẻ hơn $[Y]\text{ đ/túi}$!".
