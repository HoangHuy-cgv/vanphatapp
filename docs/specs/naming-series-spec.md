# QUY CHUẨN NAMING SERIES (ĐÁNH MÃ CHỨNG TỪ & MASTER DATA) — BAO BÌ VẠN PHÁT
**Hệ thống:** ERPNext Native v16 / Frappe Framework  
**Căn cứ phê duyệt:** Sếp duyệt ngày 13/09/2026  
**Nguyên tắc vận hành:** 
1. Master Data dùng mã định danh duy nhất không reset theo thời gian (`prefix-.#####`).
2. Chứng từ giao dịch tự động reset theo tháng bằng cơ chế Native Frappe (`prefix-.YY..MM.-.###`).

---

## 1. BẢNG QUY CHUẨN NAMING SERIES TOÀN HỆ THỐNG

| STT | Phân hệ / Nghiệp vụ | DocType ERPNext Native | Cú pháp Naming Series Chuẩn | Kết quả sinh mã | Chu kỳ Reset | Mục đích sử dụng |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Khách hàng** | `Customer` | `KH-.#####` | `KH-00001` | Không reset | Mã định danh khách hàng, in tem nhãn giao nhận |
| **2** | **Nhà cung cấp** | `Supplier` | `NCC-.#####` | `NCC-00001` | Không reset | Mã đối tác cung ứng màng, trục, keo, gia công |
| **3** | **Trục in ống đồng** | `Item` *(Nhóm TRUC)* | `TRUC-.#####` | `TRUC-00001` | Không reset | Mã quản lý tài sản khuôn trục in ống đồng vật lý |
| **4** | **Báo giá** | `Quotation` | `BG-.YY..MM.-.###` | `BG-2609-001` | Đầu mỗi tháng | Mã báo giá R&D cho khách hàng |
| **5** | **Đơn đặt hàng bán** | `Sales Order` | `DH-.YY..MM.-.###` | `DH-2609-001` | Đầu mỗi tháng | Trọng tâm vận hành (Cockpit), theo dõi cọc và giao |
| **6** | **Đơn mua hàng NCC** | `Purchase Order` | `MH-.YY..MM.-.###` | `MH-2609-001` | Đầu mỗi tháng | Mua màng NVL, túi mua ngoài, in lụa, gia công in |
| **7** | **Lệnh sản xuất** | `Work Order` | `LSX-.YY..MM.-.###` | `LSX-2609-001` | Đầu mỗi tháng | Lệnh xưởng: In $\rightarrow$ Ghép $\rightarrow$ Cắt $\rightarrow$ Đóng vòi |
| **8** | **Phiếu giao hàng** | `Delivery Note` | `GH-.YY..MM.-.###` | `GH-2609-001` | Đầu mỗi tháng | Phiếu xuất kho giao hàng cho khách / chành xe |
| **9** | **Phiếu nhận hàng NCC** | `Purchase Receipt` | `NH-.YY..MM.-.###` | `NH-2609-001` | Đầu mỗi tháng | Phiếu nhập kho từ NCC hoặc xưởng gia công ngoài |
| **10**| **Hóa đơn bán hàng** | `Sales Invoice` | `HD-.YY..MM.-.###` | `HD-2609-001` | Đầu mỗi tháng | Hóa đơn tài chính thanh toán công nợ |
| **11**| **Phiếu thu tiền (Cọc/Nốt)** | `Payment Entry` *(Receive)* | `PT-.YY..MM.-.###` | `PT-2609-001` | Đầu mỗi tháng | Ghi nhận tiền cọc hoặc thanh toán còn lại |
| **12**| **Phiếu chi tiền NCC** | `Payment Entry` *(Pay)* | `PC-.YY..MM.-.###` | `PC-2609-001` | Đầu mỗi tháng | Chi tiền trả NCC màng, keo, gia công |

---

## 2. NGUYÊN LÝ HOẠT ĐỘNG CỦA CƠ CHẾ NATIVE RESET HÀNG THÁNG

Frappe Framework quản lý số thứ tự tự động bằng bảng cơ sở dữ liệu `tabSeries`:
* Trường `name`: Lưu chuỗi tiền tố đã diễn giải (vd: `DH-2609-`).
* Trường `current`: Lưu số thứ tự nguyên tăng dần (`1, 2, 3...`).

**Quy trình tự động:**
1. Vào tháng 09/2026, tiền tố được phân giải thành `DH-2609-`. Các đơn tạo trong tháng 09 sẽ được gán số `DH-2609-001`, `DH-2609-002`...
2. Sang 00:00 ngày 01/10/2026, tiền tố tự động đổi thành `DH-2610-`. 
3. Frappe kiểm tra bảng `tabSeries` chưa có bản ghi `DH-2610-` $\rightarrow$ Tự động chèn bản ghi mới với `current = 1` và cấp số đầu tiên `DH-2610-001`.
4. Không cần thiết lập Cron job hay viết thêm Python hooks.
