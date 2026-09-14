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
* **Màng thông thường (BOPP/PE trong, PET/PE sữa):** $2.0 - 2.5\text{ g/m}^2$.
* **Màng có lớp bạc/nhôm (PET/MPET/PE sữa, PET/AL/PE sữa):** $3.0 - 4.0\text{ g/m}^2$.
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
* **Vòi PE (Polyethylene):** Chỉ hàn dính với lớp trong cùng là **PE sữa / PE trong** (LDPE / LLDPE).
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

*Tiền trục in ống đồng (Tooling Cost):* Khách hàng chi trả riêng cho đơn hàng đầu tiên (Số trục $\times$ Đơn giá khắc trục/màu). Tuyệt đối KHÔNG gộp tiền trục vào đơn giá 1 túi thành phẩm.

---

## 7. Chiến lược Báo giá 2 Nấc & Tối ưu Hóa Sản xuất (SSOT Nghiệp vụ)

### 7.1. Bóc tách Độc lập Tiền Trục In Ống Đồng (Cylinder Isolation)
* Tiền trục in ống đồng ($TRUC$) là chi phí công cụ khuôn mẫu (tooling/mold asset) tính riêng cho đơn hàng đầu tiên của mẫu bao bì mới.
* **Nguyên tắc kế toán & định giá:** Tuyệt đối KHÔNG gộp tiền trục vào đơn giá túi thành phẩm ($TP$). Đơn giá túi chỉ phản ánh chi phí biến đổi (màng, keo, mực, vòi, điện, nhân công) và khấu hao máy chạy.

### 7.2. Tối ưu Khổ Màng Rộng Chạy 2 Con (2-Lane Wide-Web Optimization)
* Đối với các mẫu túi vừa và nhỏ có chiều rộng $W \le 360\text{ mm}$, xưởng bố trí:
  * Trục in dài: $750 - 900\text{ mm}$.
  * Màng mạ / màng in khổ to: $700 - 800\text{ mm}$.
  * Thiết kế chạy 2 lane (2 con song song).
* **Hiệu quả kinh tế & kỹ thuật:**
  * Nhân đôi sản lượng túi trên mỗi mét dài màng chạy máy in/ghép.
  * Tối ưu tốc độ máy in ống đồng và triệt tiêu nguy cơ cuộn màng bị cắt dở, dư biên xén không đồng đều.

### 7.3. Chiến lược Báo giá 2 Nấc & Cơ chế Dự phòng Rủi ro Màng Thừa (2-Tier Quotation & Surplus Buffer)
Khi khách hàng yêu cầu báo giá cho số lượng đặt hàng ($Q_{req}$), hệ thống luôn tính toán và trả về đồng thời 2 nấc giá:

1. **Nấc 1 - Tròn cuộn tối ưu (ĐƠN GIÁ TỐT NHẤT - Best Unit Price):**
   * Tính theo sản lượng túi tối đa thu được khi chạy trọn vẹn số cuộn màng tiêu chuẩn (bội số của cuộn màng cơ sở $1.500\text{ m}$).
   * *Đặc điểm:* Khách nhận toàn bộ số lượng túi thực tế ra máy ($Q_{opt} \ge Q_{req}$). Đơn giá túi rẻ nhất do chi phí setup máy được chia đều cho lô lớn và xưởng không chịu rủi ro tồn kho màng in thừa.

2. **Nấc 2 - Đúng số lượng yêu cầu (ĐƠN GIÁ CAO HƠN - Requested Quantity with Risk Buffer):**
   * Áp dụng khi khách kiên quyết chỉ lấy đúng số lượng $Q_{req}$ ($Q_{req} < Q_{opt}$).
   * *Cơ chế định giá bù đắp rủi ro:* Do quy trình in ống đồng và ghép màng bắt buộc phải chạy trọn cuộn màng ($1.500\text{ m}$), phần màng in dở còn lại xưởng không thể tái sử dụng cho khách hàng khác. Đơn giá báo cho khách hàng bắt buộc phải **CAO HƠN** để bù đắp:
     * Định phí setup máy in, máy ghép, máy cắt chia cho số lượng túi nhỏ hơn.
     * Chi phí dự phòng rủi ro màng in thừa mà công ty phải lưu kho hoặc hủy nếu khách hàng không tái đặt hàng (re-order).

3. **Hiệu ứng đòn bẩy thương mại (Upsell Leverage):**
   * Báo giá song song 2 nấc tạo ra đòn bẩy tâm lý rõ ràng cho đội ngũ kinh doanh (Sales): Chỉ cần thêm một khoản ngân sách nhỏ, khách hàng sẽ nhận được số lượng túi nhiều hơn đáng kể với đơn giá trên từng túi giảm mạnh.

