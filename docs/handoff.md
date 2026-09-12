# Handoff Chuyển Giao Session Mới — ERP & Portal Vạn Phát (vanphatapp)
*Thời điểm cập nhật: 2026-09-12 | Trọng tâm: Chiến lược Copy-and-Customize Frontend từ frappe/crm & Đồng bộ Design System*

---

## 1. TỔNG KẾT HIỆN TRẠNG ĐÃ HOÀN THÀNH (SESSION NÀY)

### 1.1. Chuẩn hóa Quy trình Kỹ thuật & Tinh giản Mã nguồn
- **Chuẩn hóa cấu trúc tài liệu & Skill suite**:
  - Tách bạch rõ 3 cấp độ: Global (`~/.agents/AGENTS.md`), Repo (`vanphatapp/AGENTS.md`), Frontend (`frontend/AGENTS.md`).
  - Cài đặt đầy đủ 25 skills và 7 checklists chuẩn mực từ Addy Osmani suite.
- **Dọn dẹp & Tinh giản (Code Simplification)**:
  - `login.html`: Giảm từ 517 dòng còn 264 dòng, loại bỏ các timer layout giật lag, giữ nguyên dark UI và xác thực an toàn.
  - `App.vue`: Triệt tiêu hoàn toàn tính toán số học ở client (thuế, tiền trục), đạt chuẩn 100% Headless ERP SSOT.
  - `ModalStep1Sale.vue` & `DrawerStep2Director.vue`: Dọn sạch dead code, tối ưu CSS gom class.
  - **Kiểm thử Browser tự động bằng Chrome DevTools Protocol (CDP)**: 100% các nút bấm, switch button, toggle password, thêm/xóa dòng in, bật/tắt chip màng ghép đã được test và pass trên Chrome Headless v153 thật.

---

## 2. TRỌNG TÂM CHIẾN LƯỢC CHO SESSION TIẾP THEO: COPY-AND-CUSTOMIZE TỪ FRAPPE/CRM

### 2.1. Định Hướng Kiến Trúc (Hybrid Architecture)
Thay vì code thủ công từng trang từ đầu, Vạn Phát Portal sẽ áp dụng chiến lược **"Tận dụng khung nền có sẵn + Custom lõi bao bì"**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       VAN PHAT PACKAGING PORTAL                         │
├────────────────────────────────────┬────────────────────────────────────┤
│   TẦNG 1: GENERIC VIEWS TỪ CRM     │    TẦNG 2: CORE PACKAGING DOMAIN   │
│   (Copy pattern từ frappe/crm)     │   (Custom đặc thù theo AGENTS.md)  │
├────────────────────────────────────┼────────────────────────────────────┤
│ • Danh sách Khách hàng (Customer)  │ • Modal 1: Chọn quy cách dáng túi  │
│ • Danh sách Đơn hàng (Sales Order) │   & phụ kiện (vòi, zipper, hàn kín)│
│ • Bảng công nợ & lịch sử giao dịch │ • Drawer 2: Chọn 9 chip màng ghép  │
│ • Bộ lọc đa điều kiện (ListFilter) │   & bảng mẫu in, phân tách TRUC-   │
│ • Phân trang, Search realtime      │ • Engine tính giá 2-tier (1.500m)  │
│ • Shell Navigation & User Profile  │ • Logic vật lý: PE-PE, PP-CPP      │
└────────────────────────────────────┴────────────────────────────────────┘
```

### 2.2. Nhất Quán Màu Sắc & Phong Cách (Unified Industrial Dark Design System)
**Khẳng định: 100% NHẤT QUÁN ĐƯỢC VỀ MÀU SẮC, FONT CHỮ VÀ PHONG CÁCH.**

#### Cơ sở kỹ thuật:
Cả `vanphat_portal` và `frappe/crm` đều dùng chung thư viện **`frappe-ui`** kết hợp **Tailwind CSS**.
Để các page copy từ `frappe/crm` tự động "thay áo" sang phong cách Industrial Dark của Vạn Phát:
1. **Design Tokens chung (Tailwind Config & CSS Variables)**:
   - Màu nền chính (Background): `#0b0f19` (toàn trang), `#161b22` (panel/card/modal), `#1a1f27` (input/table header).
   - Đường viền (Border): `#3a424e` (subtle border `rgba(255,255,255,0.08)`).
   - Màu nhấn hành động (Accent): `#4ea1e0` (Primary Blue), `#0284c7` (Brand Blue).
   - Màu nghiệp vụ (Status Badges):
     - Màng in: `#38bdf8` (Sky Blue)
     - Màng cản: `#f59e0b` (Amber)
     - Màng dẻo PA: `#c084fc` (Purple)
     - Màng hàn dán: `#34d399` (Emerald)
2. **Font chữ & Typography**:
   - Toàn hệ thống thống nhất dùng duy nhất một font: `Inter` (hỗ trợ hiển thị số tabular-nums sắc nét cho kế toán và kích thước bao bì).
3. **Cơ chế Override tự động**:
   - Khi copy component từ `frappe/crm` sang, component đó sử dụng các class semantic của Frappe UI (ví dụ `text-ink-gray-9`, `bg-surface-gray-2`, `border-outline-gray-2`).
   - Ta chỉ cần map các token này trong `frontend/src/index.css` hoặc `tailwind.config.js`, toàn bộ các view mới sẽ tự động hòa vào tông màu tối công nghiệp của Vạn Phát mà không cần chỉnh sửa từng file Vue!

---

## 3. DANH MỤC CÔNG VIỆC CHO SESSION SAU (NEXT SESSION TODO)

1. **Bước 1: Thiết lập Design System Tokens chung (`tailwind.config.js` & `index.css`)**:
   - Khóa các biến CSS màu tối công nghiệp và font Inter để dùng chung cho cả portal.
2. **Bước 2: Xây dựng Trang Khách hàng (`Customer List`) theo mẫu `frappe/crm`**:
   - Tận dụng component `ListView` và composable `createListResource` từ `@frappe/ui`.
   - Kết nối trực tiếp vào REST API `/api/resource/Customer` của Frappe.
3. **Bước 3: Xây dựng Trang Đơn hàng (`Sales Order List`) theo mẫu `frappe/crm`**:
   - Hiển thị danh sách đơn hàng được sinh ra từ nút "Chốt" của Báo giá.
   - Thêm bộ lọc trạng thái: `Draft`, `To Deliver and Bill`, `Completed`.
4. **Bước 4: Tích hợp sâu luồng Soạn báo giá vào màn hình Customer**:
   - Nút "+ Báo giá" nằm ngay trong trang chi tiết Khách hàng, bấm là kích hoạt ngay Modal 1 và Drawer 2 đã hoàn thiện.

---

## 4. CÂU LỆNH MẪU KHI MỞ SESSION TIẾP THEO

```text
Đọc docs/handoff.md và tiếp tục triển khai theo định hướng đã thống nhất:
1. Đồng bộ Design System (dark theme tokens, font Inter) giữa vanphat_portal và frappe/crm.
2. Xây dựng trang Khách hàng (Customer List) và Đơn hàng (Sales Order List) dựa trên mẫu từ frappe/crm.
3. Kết nối mượt mà với Modal 1 và Drawer 2 báo giá bao bì hiện tại.
```
