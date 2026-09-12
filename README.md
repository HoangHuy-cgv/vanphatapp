# Vạn Phát App (vanphatapp)

> Hệ thống ERP & Portal Quản lý Sản xuất - Báo giá Bao bì Vạn Phát.

---

## 1. Giới thiệu & Kiến trúc
Đặc tả kiến trúc hệ thống, tech stack và quy tắc phát triển được định nghĩa duy nhất tại [AGENTS.md](AGENTS.md).
- **Core Stack**: Frappe v16 + ERPNext v16 + Vue 3 + Frappe UI + Tailwind CSS.
- **Runtime**: Zero-Node Runtime (Vite build tĩnh, Nginx serve tại `/portal`).
- **Database & Infra**: MariaDB 10.6+, Docker Compose, Cloudflare Tunnel, Rclone R2.

---

## 2. Cấu trúc thư mục

```text
vanphatapp/
├── AGENTS.md                   # Quy tắc phát triển dự án
├── README.md                   # Tài liệu tổng quan dự án
│
├── apps/vanphat_portal/        # Mã nguồn Frappe Custom App & Frontend Vue 3
│   ├── vanphat_portal/         # API backend (bao_gia.py, web controllers)
│   └── frontend/               # Giao diện Vue 3 (Modal 1 Sale, Drawer 2 Giám đốc)
│
├── data/raw-data/              # Dữ liệu nguồn SSOT gốc (Excel đơn cọc, màng, tiến độ SX, công nợ)
│
├── docs/                       # Tài liệu nghiệp vụ SSOT
│   ├── handoff.md              # Văn bản bàn giao & mục tiêu session
│   └── specs/                  # Đặc tả master data & công thức tính bao bì
│
├── infra/                      # Cấu hình Docker stack, backup R2 & Cloudflare Tunnel
│
├── scripts/                    # Scripts vận hành (serve-portal.mjs, setup-vps-lightsail.sh)
│
└── archive/                    # Kho đóng băng tài liệu & code tham khảo cũ
```

---

## 3. Khởi chạy & Vận hành

### Preview giao diện Portal (Local dev)
```bash
node scripts/serve-portal.mjs
```
Truy cập: `http://localhost:8080/portal` hoặc `http://localhost:8080/login`.

### Triển khai trên VPS (AWS Lightsail)
```bash
bash scripts/setup-vps-lightsail.sh
```

---

## 4. Nguyên tắc dữ liệu & phát triển
- Mọi logic giá và quy cách sản phẩm tuân thủ tài liệu tại `docs/specs/`.
- Nguồn dữ liệu số liệu duy nhất là `data/raw-data/`.
