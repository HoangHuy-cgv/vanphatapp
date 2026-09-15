# Vạn Phát App (vanphatapp)

> Hệ thống ERP & Portal Quản lý Sản xuất - Báo giá Bao bì Vạn Phát.

**Triple rule ghim (Sếp chốt 2026-09-15 — mọi dev tuân theo):**
1. **Backend native** — tiền, thuế, cọc, BOM, tồn kho, trạng thái, sinh mã do DocType/controller
   ERPNext native tính. API `vanphat_portal.api.*` chỉ là façade mỏng.
2. **Config native** — options, defaults, labels, thứ tự, ẩn/hiện từ Custom Field / Property Setter /
   DocType Layout / Item Group tree / `min_order_qty` / Payment Terms / Credit Limit / Tax Template.
   Đổi trong Desk → UI đổi theo, **không build lại**.
3. **Visual custom** — phần duy nhất viết tay: bố cục cockpit, Modal, Drawer, màu, nút click-chọn,
   diễn đạt flow bằng ngôn ngữ thân thiện. Cấm chứa tiền/thuế/trạng thái/cấu hình trong code visual.

Chi tiết: [AGENTS.md](AGENTS.md) (luật làm việc) · [CONSTRAINTS.md](CONSTRAINTS.md) (chuẩn đo được + máy kiểm)
· [docs/specs/](docs/specs/) (đặc tả) · [docs/decisions/](docs/decisions/) (ADR).

---

## 1. Giới thiệu & Kiến trúc
- **Core Stack**: Frappe v16 + ERPNext v16 + Vue 3.5 + `frappe-ui 1.0.0-beta.64` + Tailwind v3 + Vite 7.
- **Runtime**: Zero-Node (Vite build tĩnh, Nginx serve tại `/portal`).
- **Database & Infra**: MariaDB 10.6+, Docker Compose, Cloudflare Tunnel, Rclone R2.

---

## 2. Cấu trúc thư mục

```text
vanphatapp/
├── AGENTS.md                   # Quy tắc phát triển (triple rule + spec router)
├── CONSTRAINTS.md              # Chuẩn "tối ưu" + máy kiểm (floor/ratchet)
├── README.md                   # Tài liệu tổng quan (file này)
│
├── apps/vanphat_portal/        # Frappe custom app + Vue cockpit
│   ├── vanphat_portal/api/     # Façade mỏng: order/bao_gia/item/customer/supplier/user + _common
│   ├── vanphat_portal/www/     # Shell /portal + /login (không Desk customization)
│   ├── fixtures/               # Custom Field + Property Setter (config native ship theo app)
│   ├── frontend/src/           # Vue visual: views / components / composables / router
│   └── tests/                  # Test đặc tả Python (không cần bench)
│
├── data/clean-data/            # Master CSV thật để import bench (SSOT staging)
├── data/raw-data/              # File Excel gốc đối chiếu (không đọc ở runtime)
│
├── docs/
│   ├── decisions/              # ADR-001…006 (lý do kiến trúc, không xóa ADR cũ)
│   ├── specs/                  # 6 spec module (bản đồ ở specs/README.md)
│   └── handoff.md              # Con trỏ rolling <25 dòng (ghi đè mỗi session)
│
├── tasks/
│   ├── plan.md                 # Backlog (Sếp duyệt thứ tự) — Đã xong + Còn lại
│   └── todo.md                 # Việc slice hiện tại
│
├── scripts/
│   ├── constraints-check.py    # Máy kiểm (floor + ratchet + --init baseline)
│   ├── budget-gate.sh          # Trần bundle gzip
│   ├── serve-portal.mjs        # Preview LOCAL (đọc CSV thật; không thay bench)
│   ├── generate_master_data_csv.py + import_master_data.py  # Sinh + nạp master CSV
│   └── setup-vps-lightsail.sh  # Triển khai VPS
│
├── infra/                      # Docker stack, backup R2, Cloudflare Tunnel
└── archive/                    # Kho đóng băng (cấm đọc/sửa — AGENTS.md)
```

---

## 3. Khởi chạy & Vận hành

### Preview giao diện Portal (Local dev — KHÔNG thay bench staging)
```bash
node scripts/serve-portal.mjs
```
Truy cập: `http://localhost:8080/portal` hoặc `http://localhost:8080/login`.
Đọc `data/clean-data/*.csv` thật; đơn/báo giá tạo ở preview là file local tạm,
**không phải chứng từ ERPNext** — cấm đối soát thật bằng số preview.

### Verify trước khi commit
```bash
python3 -m unittest discover -s apps/vanphat_portal/tests -p "test_*.py"
node apps/vanphat_portal/frontend/check-composables.mjs
python3 scripts/constraints-check.py        # GATE: PASS mới commit
bash scripts/budget-gate.sh                 # sau mỗi lần build
```

### Triển khai trên VPS (AWS Lightsail)
```bash
bash scripts/setup-vps-lightsail.sh
```

---

## 4. Nguyên tắc dữ liệu & phát triển
- Mọi logic giá và quy cách sản phẩm tuân thủ `docs/specs/` + ADR trong `docs/decisions/`.
- Nguồn master thật để import bench: `data/clean-data/` ( generators ở `scripts/` ).
- Không `git push` khi chưa có lệnh explicit của Sếp (chưa có remote).
