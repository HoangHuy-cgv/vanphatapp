# Quy Chuẩn Giao Diện Buồng Lái Van Phát (Van Phat Industrial Cockpit Baseline)

> **Mục đích:** Tài liệu quy chuẩn kỹ thuật và định dạng hiển thị UI/UX mang tính pháp lệnh bắt buộc cho 100% các màn hình (Danh mục, Đơn hàng, Báo giá, Quản lý kho, Kế hoạch sản xuất, Kế toán, Người dùng) trong hệ thống ERP & Portal Bao Bì Vạn Phát.
> **Căn cứ xác lập:** Chỉ đạo trực tiếp từ Ban Giám đốc (Sếp), đối chiếu triết lý buồng lái công nghiệp Elon Musk (Industrial Minimalist Cockpit) và thiết kế chuẩn native ERPNext v16.

---

## 1. Triết Lý Cốt Lõi: Buồng Lái Vận Hành, Không Phải Cẩm Nang

Hệ thống ERP & Portal Van Phat là công cụ điều hành tốc độ cao dành cho Ban Giám đốc và đội ngũ vận hành nhà máy sản xuất bao bì màng ghép. Mọi chi tiết trên màn hình phải phục vụ mục tiêu: **Nhìn nhanh – Quyết định tức thì trong 1 giây – Không mỏi mắt – Không thao tác thừa**.

- **Triệt tiêu 100% Tutorial Prose:** Tuyệt đối cấm các đoạn văn bản hướng dẫn sử dụng, mô tả cho con người, subtitle giải thích dài dòng dưới tiêu đề.
- **Không cần đào tạo (Sếp chốt 2026-09-14):** người mới phải hoàn tất luồng chính mà không đọc hướng dẫn. Nhãn của nút chọn phải tự giải thích; nếu phải viết thêm chú thích mới hiểu thì thiết kế sai, không phải người dùng sai.
- **Chọn bằng click, không bằng dropdown (Sếp chốt 2026-09-14):** xem §7 — mặc định là nút chọn lớn nhìn-thấy-bấm-được, `<select>` chỉ còn cho trường hợp đặc biệt.
- **Visual tuân thủ flow raw-data (Sếp chốt 2026-09-14):** xem §7.1 — thứ tự màn hình phải trùng trình tự nghiệp vụ có thật trong dữ liệu nguồn, không bịa bước.
- **Mật độ thông tin cao & phẳng:** Ưu tiên cấu trúc bảng phẳng, chữ to rõ, đường viền thanh mảnh, không chia khối hộp lộn xộn.
- **Quy tắc 80/20 về dữ liệu:** Bảng chính ngoài màn hình chỉ hiển thị các trường sinh tử (80% nhu cầu tra cứu thường nhật). 20% thông tin chi tiết chuyên sâu đẩy hoàn toàn vào Drawer trượt bên phải.

---

## 2. Năm Trụ Cột Hiển Thị Pháp Lệnh (5 Mandatory Pillars)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ TRỤ CỘT 1: HEADER BUỒNG LÁI 1 DÒNG (Tabs + Quick Search + Action Button)               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TRỤ CỘT 2: BẢNG DỮ LIỆU KHÓA CỨNG 1 DÒNG (Single-line, 5–7 Cột, Zero Subtitle)         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TRỤ CỘT 3: TRẠNG THÁI CHỮ + MÀU 14PX IN ĐẬM (Text Bắt Buộc, Zero Khung, Zero Chấm)  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TRỤ CỘT 4: CHUẨN SỐ LIỆU CÔNG NGHIỆP (Tiêu đề ngắn 1-3 từ, Số Căn Phải Tabular-nums)  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TRỤ CỘT 5: DRAWER SLIDE-OVER ĐẢM NHIỆM 100% CHIỀU SÂU KỸ THUẬT                         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Trụ Cột 1: Header Buồng Lái 1 Dòng Duy Nhất (Single-Line Cockpit Header)

Toàn bộ thanh điều hướng, phân loại tab và công cụ tìm kiếm trên đầu mỗi trang bắt buộc phải nằm trên **cùng 1 dòng duy nhất** (`flex-shrink: 0`, chiều cao cố định, không ngắt dòng):

$$\text{Header} = [\text{Tab chính / Danh mục}] \quad+\quad [\text{Ô Tìm kiếm tức thì flex-1}] \quad+\quad [\text{Nút Tạo mới / Hành động chính}]$$

- **Triệt tiêu thanh lọc phụ (Sub-filter bar):** Tuyệt đối cấm các thanh filter chip phụ (như Túi ghép, Túi NGCS, Cuộn màng...) hoặc thanh dropdown dàn trải bên dưới header làm chật chội màn hình.
- **Tìm kiếm tức thì bao trùm (Global Quick Search):** Ô tìm kiếm chiếm khoảng trống linh hoạt (`flex-1`), lọc dữ liệu trực tiếp khi gõ (instant filter) trên nhiều trường (mã, tên, số điện thoại, MST).
- **Lọc nâng cao (nếu có):** Nếu nghiệp vụ bắt buộc có lọc khoảng ngày hoặc nhiều tiêu chí, phải gom vào 1 nút `Bộ lọc` mở Drawer/Modal riêng, không được bày sẵn ra giao diện chính.

---

### Trụ Cột 2: Bảng Dữ Liệu Khóa Cứng 1 Dòng (Single-Line Data Table Locking)

Mọi hàng và ô trong bảng dữ liệu bắt buộc tuân thủ quy tắc **Single-Line**:

1. **Khóa 1 dòng tuyệt đối:** `white-space: nowrap; overflow: hidden; text-overflow: ellipsis;`. Chiều cao mỗi hàng cố định chuẩn 42px – 46px. Tuyệt đối không để dữ liệu tự động xuống dòng làm phình hàng.
2. **Số lượng cột tối ưu (5–7 cột):** Chỉ giữ lại các cột mang tính quyết định trên màn hình chính. Không cố nhồi nhét quá 8 cột trên một bảng tiêu chuẩn.
3. **Nguyên tắc "Mỗi ô một thông tin duy nhất":**
   - Cột Tên chỉ hiển thị Tên thương mại rút gọn (`custom_alias`), tuyệt đối không kẹp mã nhỏ mờ bên dưới (`<div class="text-xs text-slate-500">Mã: ...</div>`).
   - Cột Mã đối tượng: Chỉ duy trì cột riêng cho các đối tượng kỹ thuật sản xuất có tiền tố rõ ràng (`TP-`, `NVL-`, `TRUC-`). Đối với Khách hàng, Nhà cung cấp, Người dùng: Bỏ cột mã trên bảng chính, mã sẽ xem trong Drawer.
4. **Ưu tiên diện tích cho tên pháp nhân / tên thương mại:** Nếu độ rộng màn hình bị co hẹp, ưu tiên ẩn các cột thứ yếu (ví dụ: ẩn cột Hạn mức tín dụng) để cột Tên pháp nhân hiển thị trọn vẹn 1 dòng không bị cắt cụt.

---

### Trụ Cột 3: Trạng Thái Chữ + Màu 14px (Text-Plus-Color Baseline — xem ADR-001)

Triệt tiêu phong cách badge dạng viên thuốc (pill badge) có khung viền và nền hộp mờ truyền thống. Thay thế bằng **chữ to 14px in đậm có text label tiếng Việt + màu**:

1. **Text label bắt buộc (WCAG 1.4.1):** Màu KHÔNG BAO GIỜ là kênh duy nhất. Mọi trạng thái PHẢI có chữ phân biệt (VD "Chờ cọc" vs "Đã duyệt" vs "Quá hạn", "Gối đầu" vs "Thanh toán ngay"). Frontend hiện tại đã render text sẵn — giữ và chuẩn hóa, không phát minh thêm kênh.
2. **Triệt tiêu đóng hộp:** Không dùng `border`, không dùng `background`, không dùng `padding` bao quanh. Chữ nằm phẳng cùng hàng dữ liệu bảng.
3. **Bỏ dấu chấm và icon thừa:** Không thêm `●`, `✓` hay icon trước chữ. Text + màu đã đủ nhận diện trong 0.1 giây mà không vỡ layout 1 dòng.
4. **Cỡ chữ & kiểu dáng:** 14px, `font-weight: 600`, phông `Inter`, số `tabular-nums`.
5. **Bảng màu phân loại chuẩn mực + contrast ≥ 4.5:1 trên nền `#161b22`:**
   - 🟡 **Vàng Hổ Phách (`#fbbf24`)**: Điều khoản gối đầu, Chờ duyệt (Pending), Tạm dừng (On-hold), Cảnh báo mức an toàn.
   - 🔵 **Xanh Da Trời (`#7dd3fc` / `#4ea1e0`)**: Đặt cọc, Đang xử lý, Đang sản xuất (In-production), Lớp màng in ngoài (Print layer).
   - 🟣 **Tím Thạch Anh (`#c084fc`)**: Màng trung gian đặc biệt (PA/Nylon), Đang kiểm tra chất lượng (QC).
   - 🟢 **Xanh Ngọc Emerald (`#6ee7b7`)**: Nghiệm thu, Thanh toán ngay, Hoàn thành (Completed), Đang hoạt động (Active).
   - 🔴 **Đỏ Carmine (`#f87171`)**: Đã hủy (Cancelled), Quá hạn công nợ (Overdue), Ngừng hoạt động (Inactive).
   - 🔘 **Text thứ cấp (`#9ca3af`, KHÔNG dùng `#64748b`)**: tiêu đề cột, ĐVT, nhãn phụ — `#64748b` trên nền surface chỉ đạt 3.63:1, RỚT AA. Thay toàn bộ text-muted cũ bằng `#9ca3af`.
6. **Badge số lượng:** kèm `aria-label` tiếng Việt (VD `aria-label="8 đơn quá hạn"`).
7. **Phạm vi:** 100% trạng thái, điều khoản, nhãn phân loại trên toàn hệ thống (Table + Drawer).

---

### Trụ Cột 4: Chuẩn Số Liệu & Căn Lề Công Nghiệp (Industrial Numeric & Alignment)

1. **Tiêu đề cột cực ngắn gọn (1–3 từ):**
   - Đạt chuẩn: `Mã SP`, `Tên sản phẩm`, `Chất liệu`, `Kích thước`, `Đáy`, `ĐVT`, `Thanh toán`, `MST`, `Vật tư`, `Định mức`.
   - Cấm dùng: `Tên đầy đủ theo đăng ký kinh doanh`, `Điều khoản thanh toán quy định`, `Số lượng kế hoạch sản xuất`.
2. **Căn phải toàn bộ cột số (`text-right`):**
   - 100% các cột chứa số: Số lượng, Đơn giá, Thành tiền, Định mức BOM, Kích thước (R x D x Dày), Hạn mức công nợ bắt buộc phải căn lề phải (`text-align: right`).
   - Con số phải được in đậm (`font-weight: 600` hoặc `700`) và sử dụng định dạng số đồng khoảng `font-variant-numeric: tabular-nums`.
   - Đơn vị tính (m, kg, cái, mic, đ, %) gắn liền sau con số với khoảng cách 1 dấu cách mỏng.
3. **Cột chữ căn trái (`text-left`), Cột trạng thái/ĐVT ngắn căn giữa (`text-center`):** Giữ trục đọc của mắt thẳng hàng từ trên xuống dưới.
4. **Xóa sổ cột rác không có dữ liệu:** Nếu một bảng kỹ thuật không sử dụng trường đơn giá (ví dụ bảng BOM định mức nội bộ nhà máy), phải ẩn hoàn toàn cột Đơn giá và mở rộng cột Tên nguyên liệu. Tuyệt đối không để cột rỗng hiển thị hàng loạt dấu gạch ngang `—`.

---

### Trụ Cột 5: Drawer Slide-Over Đảm Nhiệm 100% Chiều Sâu Kỹ Thuật

Khi người dùng click vào bất kỳ hàng nào trên bảng chính, hệ thống sẽ kích hoạt một thanh trượt (Slide-over Drawer) từ cạnh phải màn hình:

1. **Header định danh cô đọng:** Hiển thị Mã đối tượng to rõ bên trái, giá trị tổng quát (Đơn giá chuẩn, Doanh thu năm, hoặc Trạng thái chính) bên phải. Tuyệt đối không lặp lại tên pháp lý dài ngoằng ở subtitle dưới mã.
2. **Phân khu chức năng bằng thẻ phẳng:** Các khối dữ liệu kỹ thuật (Thông số túi, Cấu trúc màng, Bộ trục in, Định mức BOM, Liên hệ) trình bày bằng ô thẻ phẳng tối giản, nhãn nhạt màu 11.5px, giá trị đậm 14px – 15px.
3. **Chuẩn dialog vận hành (APG):** Drawer có `role="dialog" aria-modal="true"` + `aria-label` tên đối tượng; focus trap bên trong khi mở; `Escape`/backdrop đóng; **restore focus về đúng nút/hàng đã trigger**; giữ scroll bảng chính; cấm keyboard trap (WCAG 2.1.2). Skeleton/spinner khi tải drawer truthful (`aria-busy`), cấm skeleton trang trí giả tiến độ.

---

## 3. Hệ Thống Token Thiết Kế (SSOT Tokens)

### 3.1. Bảng Màu Công Nghiệp Tối (Industrial Dark Palette)

| Mã Màu | Biến CSS / Tên gọi | Ứng dụng thực tế |
| :--- | :--- | :--- |
| `#0b0f19` | `bg-base` | Nền chính của toàn bộ trang (Viewport canvas) |
| `#161b22` | `bg-surface` | Nền của Bảng dữ liệu, Drawer, Modal, Card chi tiết |
| `#1a1f27` | `bg-header-input` | Nền thanh Header, Header cột của Table (`th`), Input tìm kiếm |
| `rgba(255,255,255,0.08)` | `border-subtle` | Đường kẻ phân cách bảng, viền ô nhập liệu, viền Drawer |
| `#4ea1e0` | `accent-brand` | Màu nhấn thương hiệu Bao Bì Vạn Phát, nút hành động chính, mã hàng hóa |
| `#fbbf24` | `color-amber` | Chữ trạng thái Gối đầu, Chờ duyệt, Cảnh báo (14px bold) |
| `#7dd3fc` | `color-sky` | Chữ trạng thái Đặt cọc, Đang xử lý, Màng in (14px bold) |
| `#6ee7b7` | `color-emerald` | Chữ trạng thái Nghiệm thu, Hoàn thành, Hoạt động (14px bold) |
| `#f87171` | `color-red` | Chữ trạng thái Đã hủy, Quá hạn, Không hoạt động (14px bold) |
| `#f3f4f6` | `text-primary` | Văn bản chính, Tên sản phẩm, Tên khách hàng (14px) |
| `#9ca3af` | `text-secondary` | Tiêu đề cột (`th`), ĐVT, nhãn thuộc tính phụ (12px – 13px) |

### 3.2. Typography

- **Phông chữ duy nhất:** `Inter`, `-apple-system`, `BlinkMacSystemFont`, `sans-serif`.
- **Cấm hoàn toàn:** Không dùng phông mặc định của trình duyệt (`Arial`, `Times New Roman`) và không dùng phông lập trình (`monospace`, `JetBrains Mono`) trên giao diện người dùng.
- **Quy tắc Tabular Numbers:** Bắt buộc áp dụng class `tabular-nums` hoặc CSS `font-variant-numeric: tabular-nums; font-feature-settings: "tnum";` cho 100% các cột số, kích thước, tiền tệ, ngày tháng để các con số thẳng hàng tuyệt đối theo chiều dọc.

---

## 4. Bảng Đối Chiếu: Chuẩn Cũ (Phổ Thông) vs Chuẩn Buồng Lái Van Phát

| Hạng mục | ❌ Chuẩn UI Phổ Thông (Bị Cấm) |  Chuẩn Buồng Lái Van Phát (Bắt Buộc) |
| :--- | :--- | :--- |
| **Dòng dữ liệu** | Cho phép rớt 2-3 dòng, hàng cao thấp lộn xộn | Khóa cứng 1 dòng (`single-line`), cao 42-46px đồng nhất |
| **Mã & Tên** | Tên ở trên, mã kẹp nhỏ ở dưới trong cùng ô | Tách riêng hoặc chỉ hiển thị Tên/Alias, bỏ mã phụ |
| **Badge trạng thái** | Bo viền tròn, nền màu mờ, chữ nhỏ 11px | Bỏ viền, bỏ nền hộp, chữ to 14px in đậm thuần màu sắc |
| **Dấu chấm trạng thái** | Kẹp dấu chấm tròn `●` hoặc icon trước chữ | Bỏ dấu chấm, màu sắc chữ tự thân phân loại trực quan |
| **Cột bảng** | Nhồi 10-12 cột, cuộn ngang mệt mỏi | Giữ 5–7 cột cốt lõi to rõ, chi tiết đẩy vào Drawer |
| **Cột không dùng** | Để trống hoặc hiển thị hàng loạt dấu `—` | Ẩn hoàn toàn cột, mở rộng diện tích cho cột tên |
| **Căn lề số liệu** | Căn trái hoặc căn giữa theo mặc định | 100% số liệu căn phải (`text-right`), in đậm `tabular-nums` |
| **Thanh Header** | Bày 2-3 tầng gồm tabs, sub-filter chips, dropdowns | 1 tầng duy nhất: Tabs + Tìm kiếm tức thì + Nút Tạo |
| **Văn bản hướng dẫn** | Chú thích "Vui lòng chọn...", "Danh sách hiển thị..." | Xóa sổ 100% câu chữ giải thích cho con người |
| **Phông chữ** | Pha tạp Arial, Monospace | 100% phông `Inter` chuẩn native ERPNext v16 |

---

## 5. Check-list Nghiệm Thu Giao Diện (DoD - Definition of Done Cho UI)

Trước khi commit bất kỳ giao diện nào (Page, Drawer, Modal), kỹ sư/agent bắt buộc phải kiểm tra đạt 100% các tiêu chí sau:

1. [ ] **Single-Line Check:** 100% ô trong bảng không bị rớt dòng trên màn hình tiêu chuẩn (1366x768 trở lên).
2. [ ] **Zero Redundant Subtitle:** Không có ô nào kẹp mã nhỏ bên dưới tên.
3. [ ] **Trạng Thái Text + Màu (ADR-001):** 100% trạng thái có text label tiếng Việt phân biệt + màu chuẩn 14px bold (không viền, không nền hộp, không chấm). Không còn trạng thái color-alone.
4. [ ] **Header 1 Row:** Thanh header chỉ có 1 dòng duy nhất, không có thanh filter chip phụ thứ cấp.
5. [ ] **Right-Aligned Numbers:** 100% cột số lượng, định mức, kích thước, tiền tệ được căn lề phải với `tabular-nums`.
6. [ ] **Clean Columns:** Không có cột rác hiển thị dấu `—` hoặc rỗng số liệu.
7. [ ] **Drawer Integration:** Click vào hàng kích hoạt Drawer chi tiết; `Escape`/backdrop đóng; focus trap + restore về trigger; `role=dialog aria-modal`.
8. [ ] **Inter Font Consistency:** Kiểm tra bằng Chrome DevTools MCP đạt 100% node sử dụng font `Inter`.
9. [ ] **Zero Client Logic:** Không có phép tính toán tiền, logic đặt cọc, hoặc phân tab nghiệp vụ nào được viết bằng JavaScript ở client.
10. [ ] **A11y Floor:** Contrast text ≥ 4.5:1 (cấm `#64748b` trên nền tối); mọi input có `<label>`; badge số có `aria-label`; touch target ≥ 24px; không keyboard trap.
11. [ ] **Responsive Breakpoints:** 1024 sidebar icon-only; 768 drawer full-screen; 320 card thay table (không cuộn ngang ép).
12. [ ] **Feedback Truthful:** Skeleton có `aria-busy`; empty state nêu bước tiếp theo; error toast có nút retry.
13. [ ] **Click-To-Choose (§7):** mọi lựa chọn ≤ 8 phương án dùng nút chọn lớn có `role=radio` trong `role=radiogroup`, điều khiển được bằng bàn phím; không còn `<select>` cho các trường này.
14. [ ] **Config Native (ADR-005):** không có danh sách lựa chọn, giá trị mặc định hay label nào hardcode trong Vue — tất cả đến từ native meta / DocType Layout; đổi trong Desk là giao diện đổi, không build lại.
15. [ ] **Flow Raw-Data (§7.1):** thứ tự bước trên màn hình trùng trình tự nghiệp vụ trong dữ liệu nguồn; không có bước bịa, không có bước rỗng hiển thị.

---

## 6. Kiến Trúc Thin Presentation Layer (Zero Client-Side Logic)

Mục tiêu tối thượng của hệ thống là: **ERPNext Native làm Backend chịu 100% logic nghiệp vụ; Frontend Vue 3 là lớp vỏ mỏng (Thin Presentation Layer) thuần túy hiển thị dữ liệu.**

1. **Cấm tính toán tài chính & định mức ở client:** Toàn bộ công thức tính giá, chiết khấu, VAT, chia tách tiền trục, định mức BOM, và tồn kho khả dụng bắt buộc phải tính toán qua API Backend Python (`vanphat_portal.api`).
2. **Cấm tính nhẩm trạng thái & điều kiện đặt cọc:**
   - Trạng thái chứng từ (Đơn nháp, Chờ cọc, Đang sản xuất, Hoàn thành, HOLD) do Backend trả về trực tiếp theo trường `status` và `docstatus` của ERPNext native.
   - Tuyệt đối cấm viết code JS dạng `if (o.advance_paid < o.grand_total * 0.5) return 'HOLD'` trên file Vue.
3. **Phân tab nghiệp vụ điều khiển từ Backend:** Các bộ lọc tab lớn (Xưởng SX, Mua ngoài, NGCS) phải được phân loại qua query params gửi lên Backend API, không dùng `computed` ở frontend để tự suy đoán nhóm hàng.

---

## 7. Chuẩn Tương Tác: Click Chọn Thay Vì Dropdown (Sếp chốt 2026-09-14)

Nguyên tắc gốc: **người mới phải dùng được ngay, không cần đào tạo.** Chọn bằng *nhìn thấy – bấm*,
không bằng *mở danh sách ra rồi dò*.

1. **≤ 8 lựa chọn → bắt buộc nút chọn lớn (card/chip). Cấm `<select>`.** Mỗi nút hiển thị nhãn tiếng
   Việt đầy đủ (kèm quy cách/đơn vị khi cần), touch target ≥ 44px, trạng thái chọn thể hiện bằng
   **viền + nền + chữ đậm** (không dùng màu làm kênh duy nhất — theo ADR-001).
2. **> 8 lựa chọn, hoặc danh sách động (Khách hàng, NCC, Item) → ô Tìm-và-Chọn có gõ để lọc**, chỉ
   render tối đa ~50 dòng khớp. Cấm dropdown tĩnh dài bắt người dùng cuộn dò.
3. **Không hy sinh A11y để đổi lấy vẻ hiện đại:** nhóm nút chọn dùng `role="radiogroup"` + `role="radio"`
   (hoặc `<fieldset>`/`<legend>`), điều khiển được bằng phím mũi tên + `Space`/`Enter`, `aria-checked`
   đúng trạng thái. **Cấm** `div @click` trần không role — đây là bẫy dễ mắc nhất khi làm "click chọn".
4. **Thứ tự và tập lựa chọn lấy từ native** (Item Group tree, Item, BOM — xem ADR-005), không hardcode
   trong Vue; thứ tự hiển thị phải trùng thứ tự nghiệp vụ thật.
5. **Nhãn tự giải thích, không thêm prose:** nút phải tự nói nội dung (VD "Túi màng ghép (ghép 2–3 lớp)",
   "In trục (làm trục mới)", "In lụa (dùng phôi có sẵn)"), không thêm dòng hướng dẫn dưới tiêu đề.

### 7.1. Visual tuân thủ flow raw-data

- Mỗi màn hình phải đi đúng trình tự nghiệp vụ có thật trong dữ liệu nguồn (`data/clean-data`) và
  DocType native. Ví dụ luồng báo giá: **Khách → Nhóm sản phẩm → Quy cách (kích thước/đáy/độ dày) →
  Vật liệu màng (theo BOM) → Trục in → Giá**.
- Cấm bịa bước không có trong dữ liệu, cấm gộp/đảo bước vì lý do thẩm mỹ.
- Bước không có dữ liệu thì **ẩn bước đó**, tuyệt đối không hiện bước rỗng (đồng nhất với mục 4.4
  "Xóa sổ cột rác").

### 7.2. Config của giao diện phải là native (ADR-005)

- Danh sách lựa chọn, giá trị mặc định, label, thứ tự, ẩn/hiện **không được** viết trong Vue. Nguồn:
  Custom Field / Property Setter (vào thẳng meta), **DocType Layout**, Data Masking, Website Theme.
- Tiêu chí nghiệm thu: đổi một Custom Field hoặc DocType Layout trong Desk thì giao diện đổi theo
  **không cần build lại**.
