# Quy Chuẩn Giao Diện Buồng Lái Van Phát (Van Phat Industrial Cockpit Baseline)

> **Mục đích:** Tài liệu quy chuẩn kỹ thuật và định dạng hiển thị UI/UX mang tính pháp lệnh bắt buộc cho 100% các màn hình (Danh mục, Đơn hàng, Báo giá, Quản lý kho, Kế hoạch sản xuất, Kế toán, Người dùng) trong hệ thống ERP & Portal Bao Bì Vạn Phát.
> **Căn cứ xác lập:** Chỉ đạo trực tiếp từ Ban Giám đốc (Sếp), đối chiếu triết lý buồng lái công nghiệp Elon Musk (Industrial Minimalist Cockpit) và thiết kế chuẩn native ERPNext v16.

---

## 1. Triết Lý Cốt Lõi: Buồng Lái Vận Hành, Không Phải Cẩm Nang

Hệ thống ERP & Portal Van Phat là công cụ điều hành tốc độ cao dành cho Ban Giám đốc và đội ngũ vận hành nhà máy sản xuất bao bì màng ghép. Mọi chi tiết trên màn hình phải phục vụ mục tiêu: **Nhìn nhanh – Quyết định tức thì trong 1 giây – Không mỏi mắt – Không thao tác thừa**.

- **Triệt tiêu 100% Tutorial Prose:** Tuyệt đối cấm các đoạn văn bản hướng dẫn sử dụng, mô tả cho con người, subtitle giải thích dài dòng dưới tiêu đề.
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
│ TRỤ CỘT 3: TRẠNG THÁI THUẦN MÀU 14PX IN ĐẬM (Zero Khung Viền, Zero Hộp Nền, Zero Chấm)│
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

### Trụ Cột 3: Trạng Thái & Phân Loại Thuần Màu Sắc 14px (Pure Colored Text Baseline)

Triệt tiêu hoàn toàn phong cách badge dạng viên thuốc (pill badge) có khung viền và nền hộp mờ truyền thống. Thay thế bằng phong cách **Chữ to 14px thuần màu sắc**:

1. **Triệt tiêu đóng hộp:** Không dùng `border`, không dùng `background`, không dùng `padding` bao quanh. Chữ nằm phẳng, tự nhiên cùng hàng với dữ liệu bảng.
2. **Bỏ dấu chấm và icon thừa:** Không thêm dấu chấm tròn (`●`), dấu tích (`✓`) hay icon phía trước chữ. Bản thân màu sắc đã đủ để mắt người nhận diện phân loại trong 0.1 giây.
3. **Cỡ chữ & Kiểu dáng:** Chữ to rõ **14px**, in đậm `font-weight: 600`, phông chữ `Inter`, định dạng số `tabular-nums`.
4. **Bảng màu phân loại chuẩn mực:**
   - 🟡 **Vàng Hổ Phách (`#fbbf24`)**: Điều khoản gối đầu, Chờ duyệt (Pending), Tạm dừng (On-hold), Cảnh báo mức an toàn.
   - 🔵 **Xanh Da Trời (`#7dd3fc` / `#4ea1e0`)**: Đặt cọc, Đang xử lý, Đang sản xuất (In-production), Lớp màng in ngoài (Print layer).
   - 🟣 **Tím Thạch Anh (`#c084fc`)**: Màng trung gian đặc biệt (PA/Nylon), Đang kiểm tra chất lượng (QC).
   - 🟢 **Xanh Ngọc Emerald (`#6ee7b7`)**: Nghiệm thu, Thanh toán ngay, Hoàn thành (Completed), Đang hoạt động (Active).
   - 🔴 **Đỏ Carmine (`#f87171`)**: Đã hủy (Cancelled), Quá hạn công nợ (Overdue), Ngừng hoạt động (Inactive).
5. **Phạm vi áp dụng:** Áp dụng cho 100% các trạng thái, loại điều khoản thanh toán, và nhãn phân loại trên toàn hệ thống (kể cả trên Table và trong Drawer).

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
2. **Phân khu chức năng bằng thẻ phẳng:** Các khối dữ liệu kỹ thuật (Thông số túi, Cấu trúc màng, Bộ trục in, Định mức BOM, Liên hệ) được trình bày bằng các ô thẻ phẳng tối giản, nhãn nhạt màu kích thước nhỏ (11.5px), giá trị đậm to rõ (14px – 15px).
3. **Phím tắt vận hành nhanh:** Luôn hỗ trợ phím `Escape` để đóng Drawer ngay lập tức, click backdrop để thoát, giữ trạng thái cuộn của bảng chính bên dưới không bị nhảy vị trí.

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
3. [ ] **Pure Color Badges:** 100% trạng thái và điều khoản hiển thị bằng chữ to 14px in đậm thuần màu sắc (không viền, không nền hộp, không chấm).
4. [ ] **Header 1 Row:** Thanh header chỉ có 1 dòng duy nhất, không có thanh filter chip phụ thứ cấp.
5. [ ] **Right-Aligned Numbers:** 100% cột số lượng, định mức, kích thước, tiền tệ được căn lề phải với `tabular-nums`.
6. [ ] **Clean Columns:** Không có cột rác hiển thị dấu `—` hoặc rỗng số liệu.
7. [ ] **Drawer Integration:** Click vào hàng kích hoạt Drawer chi tiết; phím `Escape` đóng Drawer mượt mà.
8. [ ] **Inter Font Consistency:** Kiểm tra bằng Chrome DevTools MCP đạt 100% node sử dụng font `Inter`.
