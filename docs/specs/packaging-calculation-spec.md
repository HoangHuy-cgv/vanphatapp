# Đặc tả Kỹ thuật & Công thức Tính toán Sản xuất Bao bì Màng ghép Phức hợp (Flexible Packaging)

> **Mục đích:** Tài liệu chuẩn mực kỹ thuật và công thức toán học dùng làm căn cứ logic để lập trình các phân hệ: Báo giá (Quotation), Định mức nguyên vật liệu (BOM), Lệnh sản xuất (Work Order), Quản lý cuộn/lô (Batch/Reel Tracking) và Kiểm soát phế liệu/hao hụt.
> **Căn cứ pháp lý & nguồn kỹ thuật:** ASTM D792, ASTM D6988, ASTM F88, ASTM F2096, ISO 1183, Technical Data Sheet (TDS) từ Henkel Liofol, Toyo-Morton, Totani, Karlville và giáo trình *Plastic Films in Food Packaging* (Elsevier).

---

## 1. Bảng Thông số Vật lý & Hệ số Quy đổi Vật liệu

Công thức chuẩn xác định định lượng diện tích (GSM - Grams per Square Meter):
$$\text{GSM } (g/m^2) = \text{Độ dày } (\mu m) \times \text{Tỷ trọng } (\rho, g/cm^3)$$

Công thức tính diện tích định mức trên 1 kg màng (Yield):
$$\text{Yield } (m^2/kg) = \frac{1.000}{\text{GSM}} = \frac{1.000}{\text{Độ dày } (\mu m) \times \text{Tỷ trọng } (g/cm^3)}$$

### Bảng Tỷ trọng Chuẩn (ASTM D792 / ISO 1183)

| Tên vật liệu | Ký hiệu | Tỷ trọng ($\rho$) | Tiêu chuẩn đo lường | Đặc tính & Ứng dụng |
| :--- | :--- | :--- | :--- | :--- |
| **Linear Low-Density Polyethylene** | LLDPE / PE | **0.920** $g/cm^3$ | ASTM D792 / ISO 1183 | Lớp hàn dán trong cùng, dẻo dai, chịu va đập |
| **High-Density Polyethylene** | HDPE | **0.950** $g/cm^3$ | ASTM D792 | Độ cứng cao, chịu tải, cản ẩm tốt |
| **Biaxially Oriented Polypropylene** | BOPP | **0.905** $g/cm^3$ | ASTM D792 | Lớp in ngoài cùng, độ bóng/trong suốt cao |
| **Cast Polypropylene** | CPP / R-CPP | **0.900** $g/cm^3$ | ASTM D792 | Lớp hàn dán trong cùng chịu nhiệt cao (tiệt trùng) |
| **Polyethylene Terephthalate** | PET | **1.400** $g/cm^3$ | ASTM D792 | Lớp in ngoài, cơ lý cao, giữ hương, chịu nhiệt sấy |
| **Metalized PET** | MPET | **1.400** $g/cm^3$ | ASTM D792 | Màng PET mạ nhôm, cản ánh sáng, cản khí |
| **Nhôm nguyên chất** | AL Foil | **2.700** $g/cm^3$ | ASTM B209 / ISO 209 | Chắn sáng 100%, cản ẩm và oxy tuyệt đối |
| **Biaxially-oriented Polyamide** | BOPA (Nylon) | **1.150** $g/cm^3$ | ASTM D792 | Chống đâm thủng, chịu lạnh, dùng cho túi hút chân không |

---

## 2. Công thức Kích thước Khổ màng & Diện tích Túi

Quy ước ký hiệu:
* $W$: Chiều rộng túi thành phẩm (mm).
* $L$: Chiều dài/cao túi thành phẩm (mm).
* $G$: Độ sâu xếp hông hoặc đáy gấp (Gusset - mm).
* $S_{seal}$: Chiều rộng đường hàn biên/đáy (thường $5 - 10$ mm).
* $W_{trim}$: Biên xén mép dao cắt (thường $10 - 20$ mm trên cuộn màng).

### 2.1. Túi 3 biên (Three-side Seal Pouch)
* **Khổ màng trải ($W_{web}$):** $W_{web} = 2 \times W + W_{trim}$ (hoặc 2 cuộn riêng úp mặt).
* **Bước cắt dao ($L_{cut}$):** $L_{cut} = L$.
* **Diện tích màng 1 túi ($A_{pouch}$):**
  $$A_{pouch} (m^2) = \frac{2 \times W \times L}{1.000.000}$$

### 2.2. Túi hàn lưng / Xếp hông (Center Seal / Gusseted Pouch)
* **Khổ màng trải ($W_{web}$):** $W_{web} = 2 \times (W + G) + S_{back} + W_{trim}$ (đường hàn lưng $S_{back} \approx 15 - 20$ mm).
* **Bước cắt dao ($L_{cut}$):** $L_{cut} = L + S_{bottom}$ ($S_{bottom} \approx 10 - 15$ mm).
* **Diện tích màng 1 túi ($A_{pouch}$):**
  $$A_{pouch} (m^2) = \frac{W_{web} \times L_{cut}}{1.000.000}$$

### 2.3. Túi đáy đứng (Doypack / Stand-up Pouch)
* **Diện tích màng 1 túi tiêu chuẩn ($A_{pouch}$):**
  $$A_{pouch} (m^2) = \frac{2 \times W \times (L + G_{bottom} / 2)}{1.000.000}$$

---

## 3. Công thức Ghép màng & Tiêu hao Keo / Dung môi (Dry Lamination)

### 3.1. Khối lượng từng lớp màng trên 1 túi
$$\text{Khối lượng lớp màng } i \text{ (gram)} = A_{pouch} (m^2) \times \text{Độ dày } T_i (\mu m) \times \text{Tỷ trọng } \rho_i (g/cm^3)$$

### 3.2. Định mức Keo ghép khô (TDS Henkel Liofol / Toyo-Morton)
* **Màng thông thường (BOPP//PE, PET//PE):** $2.0 - 2.5\text{ g/m}^2$.
* **Màng có lớp bạc/nhôm (PET//MPET//PE, PET//AL//PE):** $3.0 - 4.0\text{ g/m}^2$.
* **Túi đựng chất lỏng có vòi, hóa mỹ phẩm:** $3.5 - 4.5\text{ g/m}^2$.

### 3.3. Tiêu hao Keo gốc và Dung môi Ethyl Acetate (EA)
* **Khối lượng keo khô 1 túi:** $M_{keo\_kho} \text{ (gram)} = A_{pouch} \times C_{dry}$.
* **Khối lượng keo thương mại cần mua (với hàm lượng chất rắn gốc $50\%$):**
  $$M_{keo\_mua} \text{ (kg)} = \frac{\text{Tổng keo khô (kg)}}{0.50}$$
* **Lượng dung môi EA bay hơi trong quá trình sấy (hao hụt):**
  $$M_{EA} \text{ (kg)} \approx 1.5 \times M_{keo\_mua} \text{ (kg)}$$

---

## 4. Quy chuẩn Kỹ thuật Đóng vòi (Spout Insertion)

### 4.1. Nguyên tắc tương thích nhiệt dẻo (Bắt buộc kiểm tra)
* **Vòi PE (Polyethylene):** Chỉ hàn dính với lớp trong cùng là **LLDPE / LDPE**.
* **Vòi PP (Polypropylene):** Chỉ hàn dính với lớp trong cùng là **CPP / R-CPP**.
* *Cấm tuyệt đối ghép chéo:* Không được dùng vòi PE cho màng CPP hoặc vòi PP cho màng PE do lệch nhiệt độ nóng chảy, gây bục xì 100%.

### 4.2. Tiêu chuẩn kích thước vòi
* $\varnothing 8.6\text{ mm} - 10\text{ mm}$: Thạch hút, nước uống đóng túi, mỹ phẩm nhỏ.
* $\varnothing 15\text{ mm} - 16\text{ mm}$: Nước rửa bát, dầu gội, tương ớt, sốt gia vị.
* $\varnothing 22\text{ mm} - 33\text{ mm}$: Nước giặt, nước xả vải dung tích lớn ($1.5L - 5L$), hóa chất.

### 4.3. Tiêu chuẩn kiểm tra độ kín
* **ASTM F88:** Phương pháp đo độ bền mối hàn dán (Seal Strength).
* **ASTM F2096:** Phương pháp ngâm nước tạo áp suất phát hiện rò rỉ bọt khí (Gross Leak Detection).

---

## 5. Ma trận Định mức Hao hụt & Phế liệu (Scrap Matrix)

Hao hụt đơn hàng gồm:
1. **Hao hụt Setup (Khởi động):** Số lượng cố định trên một lần lên máy.
2. **Hao hụt Running (Chạy ổn định):** Tỷ lệ % trên tổng sản lượng.

| Công đoạn | Hao hụt Setup | Tỷ lệ Running (%) | Tính chất xử lý phế |
| :--- | :--- | :--- | :--- |
| **1. Thổi màng PE** | $10 - 20$ kg/lệnh | **$2.0\% - 3.5\%$** | Phế sạch: Nhập kho thu hồi để tái sinh hạt PE |
| **2. In ống đồng (Gia công)** | $50 - 80$ mét dài canh màu | **$2.0\% - 3.0\%$** | Phế có mực: Bán phế liệu giá thấp |
| **3. Ghép khô** | $30 - 50$ mét dài canh sấy | **$1.5\% - 2.5\%$** | Phế biên keo: Tiêu hủy hoặc bán ve chai |
| **4. Cắt túi thường** | $20 - 50$ túi | **$1.5\% - 2.5\%$** | Mép cắt vụn, túi lỗi nhiệt |
| **5. Đóng vòi (nếu có)** | $30 - 50$ túi | **$2.0\% - 3.5\%$** | Túi hỏng ngàm hàn, rò rỉ áp suất |
| **Phụ kiện vòi** | $0$ | **$1.0\% - 1.5\%$** | Vòi nứt vỡ, lệch ren |

---

## 6. Công thức Tính Giá thành & Báo giá

### 6.1. Giá vốn đơn vị 1 túi ($C_{unit}$)
$$C_{unit} = \frac{\sum C_{vat\_lieu} + C_{in\_gia\_cong} + C_{phu\_kien} + C_{nhan\_cong\_may} - V_{phe\_thu\_hoi}}{Q \times (1 - \text{Hao hụt tổng})}$$

Trong đó:
* $\sum C_{vat\_lieu}$: Chi phí hạt PE + màng ngoài (BOPP/PET) + keo ghép + dung môi EA.
* $C_{in\_gia\_cong}$: Mét dài in $\times$ Đơn giá in/mét của nhà gia công.
* $C_{phu\_kien}$: Chi phí vòi (Spout) + Chi phí zipper (nếu có).
* $C_{nhan\_cong\_may}$: Định phí nhân công + Khấu hao máy + Điện năng từng công đoạn.
* $V_{phe\_thu\_hoi}$: Giá trị phế liệu thu hồi (trừ trực tiếp vào giá vốn).
* $Q$: Số lượng túi khách đặt.

### 6.2. Giá bán dự toán
$$\text{Giá bán} = \frac{C_{unit}}{1 - \text{Margin \%}}$$

*Tiền trục in ống đồng (Tooling Cost):* Khách hàng chi trả riêng cho đơn hàng đầu tiên (Số trục $\times$ Đơn giá khắc trục/màu).
