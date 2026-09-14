# Handoff: Con Trỏ Vận Hành & Chuyển Giao Session

- **Mã Commit Gần Nhất**: `7c21643`
- **Trạng Thái CI/CD & Production Build**:
  - Vite build: Thành công 100% (`npm run build`, bundle 69.29 kB gzip).
  - Backend: `bao_gia.py` compiled cleanly, đã bổ sung native API `create_sales_order`.
- **Hạng Mục Vừa Hoàn Thành**:
  - Xóa bỏ 100% `src/data/mockData.js` (~966 dòng mock data).
  - Đấu nối `ModalCreateOrder.vue` trực tiếp vào API `create_sales_order` của ERPNext với Naming Series `DH-`.
  - Đấu nối `DrawerOrderDetail.vue` vào `record_order_deposit`, `accountant_approve_procurement`, `submit_sales_order`.
  - Đưa `OrdersView.vue`, `QuotesView.vue`, `CatalogView.vue` về chuẩn vỏ mỏng (thin client), nạp trực tiếp qua backend APIs.
- **Nhiệm Vụ Trọng Tâm Tiếp Theo**:
  - Tiến hành test luồng tạo đơn và duyệt cọc trực tiếp trên giao diện thực tế.
