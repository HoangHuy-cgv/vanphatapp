---
name: packaging-calculation-engine
description: Technical calculation engine and commercial quotation algorithm for flexible packaging (màng ghép phức hợp) manufacturing, multi-layer film consumption, scrap rates, adhesive/solvent ratios, cylinder steps, 2-lane wide-web optimization, whole-roll batching with surplus risk buffer, and separate cylinder tooling quotation. Use when modifying or auditing quotation APIs, BOM generators, or verifying packaging math.
---

# Packaging Calculation Engine (Van Phat SSOT Production Standard)

This skill serves as the verified technical specification and procedural engine for flexible packaging (bao bì mềm màng ghép phức hợp) math, material consumption, and production pricing at Van Phat Packaging.

---

## 1. Domain Physics & Material Standards (ASTM D792 / ISO 1183)

### 1.1. Density ($\rho$ in $g/cm^3$) & Raw Material Price Matrix (VND/kg)
| Material Code | Material Name | Standard Density ($\rho$) | Production Density in `bao_gia.py` | Reference Price (VND/kg) | Role in Laminate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PET** | Polyethylene Terephthalate | 1.400 | **1.340** | 47,000 | Lớp in ngoài, bóng, chịu nhiệt |
| **PA** | Biaxially-oriented Polyamide (Nylon) | 1.150 | **1.140** | 81,000 | Chống đâm thủng, chịu lạnh/chân không |
| **PES** | PE Sữa (Opaque White PE) | 0.920–0.930 | **0.930** | 51,500 | Lớp hàn dán trong, cản sáng nước giặt |
| **PE** / **PE_TRONG** | LLDPE Trong suốt | 0.920 | **0.925** | 42,500 – 45,000 | Lớp hàn dán đa dụng |
| **MPET** | Metalized PET (Mạ nhôm) | 1.400 | **1.400** | 57,000 | Cản ánh sáng, cản oxy |
| **AL** | Lá nhôm nguyên chất (Foil) | 2.700 | **2.700** | 160,000 | Chắn sáng 100%, cản ẩm tuyệt đối |
| **BOPP / OPP** | Biaxially Oriented PP | 0.905 | **0.905** | 43,000 | Màng in thực phẩm/bánh kẹo |
| **CPP / R-CPP** | Cast Polypropylene | 0.900 | **0.900** | 46,000 | Lớp hàn nhiệt cao (tiệt trùng retort) |

### 1.2. Core Conversion Formulas
1. **Surface Density (GSM - Grams per Square Meter)**:
   $$\text{GSM } (g/m^2) = \text{Độ dày } (\mu m) \times \text{Tỷ trọng } (\rho, g/cm^3)$$
2. **Material Yield**:
   $$\text{Yield } (m^2/kg) = \frac{1,000}{\text{GSM}}$$
3. **Weight of Layer $i$ per Bag (grams)**:
   $$M_{layer\_i} (g) = A_{pouch} (m^2) \times \text{Độ dày } T_i (\mu m) \times \rho_i (g/cm^3)$$
4. **Raw Film Cost per Bag ($C_{film}$)**:
   $$C_{film} = \sum_{i} \left( \frac{M_{layer\_i}}{1,000} \times \text{Đơn giá màng } i \right)$$

---

## 2. Pouch Surface Area Calculations ($A_{pouch}$) for 5 Standard Types

Dimensions: $W$ (Width, m), $L$ (Height, m), $G$ (Gusset, m). Step cut: $L_{cut} = L\text{ (m)}$.

1. **Túi đáy đứng (Doypack / Stand-up Pouch - `day_dung_co_voi`, `day_dung_khong_voi`)**:
   $$A_{pouch} (m^2) = 2 \times W \times \left(L + \frac{G}{2}\right)$$
2. **Túi 3 biên (Three-side Seal - `3_bien`)**:
   $$A_{pouch} (m^2) = 2 \times W \times L$$
3. **Túi xếp hông / hàn lưng (Side Gusset / Center Seal - `xep_hong`, `lung`)**:
   $$A_{pouch} (m^2) = 2 \times (W + G) \times (L + 0.015)$$
4. **Túi 8 cạnh đáy phẳng (Flat Bottom / Box Pouch - `8_canh`)**:
   $$A_{pouch} (m^2) = 2 \times W \times L + 2 \times G \times L + W \times G$$

---

## 3. Commercial & Production Strategy (Quy Chuẩn Báo Giá Sếp Chốt)

### 3.1. Báo Giá Tiền Trục Riêng Biệt (Tooling Cost Isolation)
- **Nguyên tắc**: Tiền trục in ống đồng là chi phí công cụ khuôn mẫu khách chi trả riêng cho đơn đầu tiên (nếu khách chưa có trục in).
- **Tuyệt đối không gộp**: Không bao giờ chia nhỏ hay cộng dồn tiền trục vào đơn giá 1 túi thành phẩm.
- **Cách báo giá**:
  $$\text{Cylinder Quote} = \text{Số cây trục} \times \text{Đơn giá khắc trục} \quad (\approx 3.148.000 - 3.800.000\text{ VND/cây})$$

### 3.2. Tối Ưu Chạy 2 Lane (2 Con Trên Khổ To)
- Với các khổ túi vừa và nhỏ ($W \le 360\text{mm}$), xưởng bố trí trục in dài ($750 - 900\text{mm}$) và cuộn màng khổ rộng ($700 - 800\text{mm}$) để **chạy 2 con (2 lane)** đồng thời.
- **Lợi ích**:
  - Gấp đôi số túi thành phẩm trên mỗi mét dài cuộn màng.
  - Tối ưu hóa thời gian chạy máy in, máy ghép, máy chia cuộn.
  - Triệt tiêu tình trạng cuộn màng bị cắt dở dang.

### 3.3. Chiến Lược 2 Nấc Giá: Tròn Cuộn Tối Ưu vs. Bù Đắp Rủi Ro Đơn Lẻ
Xưởng luôn chạy tròn cuộn màng chuẩn ($L_{roll} = 1.500\text{m}$). Số túi chuẩn 1 cuộn:
$$N_{1\_roll} = \left\lfloor \frac{1,500 \times \text{lanes} \times (1 - Scrap)}{L_{cut}} \right\rfloor$$
Số cuộn cần lên máy: $N_{rolls} = \lceil Q_{desired} / N_{1\_roll} \rceil$. Tổng sản lượng: $Q_{optimal} = N_{rolls} \times N_{1\_roll}$.
Số túi dư nếu khách lấy $Q_{desired}$: $Q_{surplus} = Q_{optimal} - Q_{desired}$.

Hệ thống luôn chào 2 nấc giá song song cho Sale chốt đơn:

1. **Nấc 1: Đặt Tròn Cuộn Tối Ưu ($Q_{optimal}$ túi) — ĐƠN GIÁ TỐT NHẤT**:
   - Tiêu thụ trọn vẹn $100\%$ sản lượng cuộn màng, không có tồn dư rủi ro.
   - Định phí setup máy ($3.500.000\text{đ}$) chia đều trên số lượng lớn $Q_{optimal}$.
   - Khách nhận **đơn giá rẻ nhất (Best Price)**:
     $$Price_{optimal} = \frac{COGS_{optimal}}{1 - TargetMargin} \quad (\text{TargetMargin } = 30\%)$$

2. **Nấc 2: Đặt Theo Đúng Số Lượng Yêu Cầu ($Q_{desired}$ túi lẻ) — ĐƠN GIÁ CAO HƠN**:
   - Khách không đồng ý lấy tròn cuộn mà chỉ lấy đúng $Q_{desired}$, nhưng xưởng vẫn phải chạy trọn cuộn màng dẫn đến dư $Q_{surplus}$ túi.
   - **Rủi ro công ty**: Khách có thể không bao giờ đặt lại (re-order), phần hàng dư $Q_{surplus}$ trở thành chi phí lỗ / ứ đọng vốn.
   - **Cơ chế định giá**: Đơn giá của $Q_{desired}$ phải **CAO HƠN** để bù đắp:
     - Định phí setup máy gánh trên số lượng ít hơn: $\frac{Setup_{fixed}}{Q_{desired}}$.
     - Phần bù đắp rủi ro màng dở dang của $Q_{surplus}$ túi dư:
       $$SurplusRiskBuffer = \frac{Q_{surplus} \times (C_{film} + C_{glue}) \times (1 + Scrap) \times 0.5}{Q_{desired}}$$
     - Đơn giá bán: $Price_{desired} = \frac{COGS_{desired}}{1 - TargetMargin}$.
   - **Hiệu ứng đòn bẩy up-sell**: Khách nhận thấy chỉ cần bù thêm một khoản tiền nhỏ là sở hữu thêm toàn bộ $Q_{surplus}$ túi với đơn giá rẻ hơn nhiều, thúc đẩy khách chốt lấy trọn cuộn!

---

## 4. Spout Insertion Material Compatibility (Strict Engineering Rule)
- **PE Spout**: MUST ONLY weld to **LLDPE / PE** sealant layer.
- **PP Spout**: MUST ONLY weld to **CPP / R-CPP** sealant layer.
- **Strict Prohibition**: Never allow PE spout on CPP film or PP spout on PE film (causes 100% leakage failure due to melting temperature mismatch).

---

## 5. Architectural Boundaries
- All calculation procedures must execute via backend `@frappe.whitelist()` at `vanphat_portal.api.bao_gia.calculate_packaging_quotation`.
- Zero calculation logic inside Vue 3 components or presentation layer.
