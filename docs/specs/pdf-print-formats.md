# Danh Mục Mẫu In PDF Chuẩn (Print Formats Specification)

Tài liệu này tổng hợp và đặc tả chi tiết bộ **11 Mẫu In PDF Chuẩn** của Bao Bì Vạn Phát (được thiết kế bằng HTML/CSS Jinja2 phục vụ xuất PDF native trong ERPNext). Toàn bộ mã nguồn template HTML và các bản PDF mẫu đã được lưu trữ an toàn tại:
- Template HTML: [`docs/templates/`](file:///var/home/huy/vanphatapp/docs/templates/)
- File PDF mẫu thực tế & assets: [`data/print-formats/`](file:///var/home/huy/vanphatapp/data/print-formats/)

---

## 1. Bảng Tổng Hợp 11 Bộ Mẫu In PDF

| STT | Mẫu In Chứng Từ | File Template HTML | File PDF Mẫu Thực Tế | ERPNext DocType Liên Kết |
| :---: | :--- | :--- | :--- | :--- |
| **01** | **Báo Giá Bao Bì** | `bao-gia-template.html` / `print-format-quotation.html` | `bao-gia-van-phat-mau.pdf` | `Quotation` |
| **02** | **Đơn Đặt Hàng Bán** | `don-dat-hang-template.html` | `don-dat-hang-van-phat-mau.pdf` *(kèm bản Amyco, DS888)* | `Sales Order` |
| **03** | **Đơn Mua Màng NVL** | `don-mua-hang-mang-nvl-template.html` | `don-mua-hang-mang-mau.pdf` *(kèm Nam Sơn, Tạ Minh)* | `Purchase Order` |
| **04** | **Đơn Mua Trục In Ống Đồng**| `don-mua-hang-truc-in-template.html` | `don-mua-hang-truc-in-mau.pdf` *(kèm Dongyun)* | `Purchase Order` |
| **05** | **Đơn Đặt In Ống Đồng (Gia công)**| `don-mua-hang-in-ong-dong-template.html` | `don-mua-hang-in-ong-dong-mau.pdf` *(kèm IGC Tuệ Nhi)*| `Purchase Order` (Subcontracting) |
| **06** | **Đơn Mua Túi Màng Đơn** | `don-mua-hang-tui-mang-don-template.html` | `don-mua-hang-tui-mau.pdf` *(kèm Thanh Tùng, Tràng Tín)* | `Purchase Order` |
| **07** | **Đơn Mua Túi Màng Ghép** | `don-mua-hang-tui-mang-ghep-template.html` | `don-mua-hang-tui-mang-ghep-mau.pdf` | `Purchase Order` |
| **08** | **Đơn Mua Hàng / Vật Tư Baseline**| `don-mua-hang-baseline-template.html` | `don-mua-hang-baseline-vattu-mau.pdf` *(kèm Hóa chất Sungdo)* | `Purchase Order` |
| **09** | **Phiếu Xuất Kho Kiêm Giao Hàng** | `phieu-xuat-kho-template.html` | `phieu-xuat-kho-van-phat-mau.pdf` *(kèm DS888)* | `Delivery Note` |
| **10** | **Biên Bản Đối Soát Công Nợ** | `bien-ban-doi-soat-cong-no-template.html`| `bien-ban-doi-soat-cong-no-van-phat-mau.pdf` | Báo cáo tài chính / Đối soát |
| **11** | **Hợp Đồng Mua Bán Bao Bì** | `hop-dong-mua-ban-template.html` | `hop-dong-mua-ban-van-phat-mau.pdf` | `Contract` |

---

## 2. Tiêu Chuẩn Kỹ Thuật Khi Render PDF trong ERPNext

1. **Khổ giấy:** Chuẩn A4 portrait (210mm x 297mm), lề (margin): top 12mm, bottom 12mm, left 15mm, right 15mm.
2. **Font chữ:** Dùng Inter hoặc Roboto, hỗ trợ font-weight đầy đủ từ 400 đến 700, hỗ trợ hiển thị tiếng Việt UTF-8 chuẩn xác, không bị lỗi dấu gạch chéo hay vỡ font khi render qua `weasyprint` hoặc `wkhtmltopdf`.
3. **Màu sắc thương hiệu Vạn Phát:**
   - Màu chủ đạo (Primary): Đỏ Vạn Phát `#C92A2A` / `#D32F2F`.
   - Màu chữ tiêu đề: `#1E293B` (Slate-900).
   - Màu bảng viền: `#CBD5E1` (Slate-300).
   - Màu nền header bảng: `#F1F5F9` (Slate-100).
4. **Header Tiêu Đề Thư (`letter-head.html`):**
   - Logo Công ty TNHH SXTM Bao Bì Vạn Phát.
   - VPGD: C4/5B34 Bùi Thanh Khiết, Tân Túc, Bình Chánh, TP.HCM.
   - Hotline: 028.36206746 | Email: info@vanphat.com.
5. **Script Sinh PDF Tự Động:**
   - File [`docs/templates/render_all.py`](file:///var/home/huy/vanphatapp/docs/templates/render_all.py) có sẵn bộ fixture dữ liệu mẫu để render đồng loạt toàn bộ 11 file PDF kiểm thử chỉ bằng 1 lệnh duy nhất:
     ```bash
     python3 docs/templates/render_all.py
     ```
