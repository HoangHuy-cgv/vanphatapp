# TÀI LIỆU VẬN HÀNH HẠ TẦNG VPS & DEPLOYMENT — BAO BÌ VẠN PHÁT

> **Dành cho Agent và Kỹ sư Vận hành:** Tài liệu này ghi nhận toàn bộ thông số, cấu trúc hạ tầng máy chủ VPS, mạng, container, bảo mật và các lệnh vận hành thực tế của hệ thống ERPNext Vạn Phát.

---

## 1. Thông Số Hạ Tầng Máy Chủ (VPS Profile)

| Thông số | Giá trị thực tế | Ghi chú |
| :--- | :--- | :--- |
| **Nhà cung cấp Cloud** | **AWS Lightsail** | Khu vực: `ap-southeast-1` (Singapore) |
| **IP Tĩnh (Static Public IP)** | **`13.213.13.201`** | Gắn cố định vào instance Lightsail |
| **Hệ điều hành** | **Ubuntu 24.04 LTS** (x86_64) | RAM: 3.7GB (~4GB), 2 vCPU, 80GB SSD |
| **Tài khoản SSH** | **`ubuntu`** | Đăng nhập bắt buộc bằng SSH Key |
| **File SSH Private Key** | **`LightsailDefaultKey-ap-southeast-1.pem`** | Đặt tại máy dev: `~/Downloads/` hoặc `~/.ssh/` (phải `chmod 400`) |
| **Thư mục ứng dụng trên VPS** | **`/opt/vanphat`** | Nơi chứa compose, apps, sites và dữ liệu |
| **Tên Site ERPNext Native** | **`app.vanphat.io.vn`** | Cấu hình multi-tenant host header |
| **Tên miền công khai** | **`https://app.vanphat.io.vn`** | Truy cập Portal qua: `/portal`, Login qua: `/login` |

---

## 2. Mạng, Tên Miền & Bảo Mật (Cloudflare Tunnel)

Hệ thống sử dụng **Cloudflare Tunnel (Named Tunnel `vanphat-erp`)** để phục vụ traffic ra ngoài Internet:
1. **Không mở cổng HTTP/HTTPS trên Firewall:** Port 80 và 443 đóng hoàn toàn đối với Internet công cộng. VPS không cần mở port ngoài.
2. **Luồng dữ liệu:**
   $$\text{Client (Trình duyệt)} \xrightarrow{\text{HTTPS}} \text{Cloudflare Edge (WAF)} \xrightarrow{\text{Tunnel Outbound}} \text{Frontend Container (127.0.0.1:8080)}$$
3. **Cấu hình Tunnel trên VPS (`/etc/cloudflared/config.yml`):**
   ```yaml
   tunnel: <TUNNEL-ID>
   credentials-file: /etc/cloudflared/<TUNNEL-ID>.json
   ingress:
     - hostname: app.vanphat.io.vn
       service: http://127.0.0.1:8080
     - service: http_status:404
   ```
4. **Trạng thái dịch vụ Tunnel:** Chạy dưới dạng `systemd service` (`sudo systemctl status cloudflared`).

---

## 3. Cấu Trúc Docker Compose (`infra/docker-compose.yml`)

Toàn bộ dịch vụ chạy trong mạng nội bộ `vanphat_network`:

| Container Service | Image / Base | Cổng nội bộ | Vai trò & Trách nhiệm |
| :--- | :--- | :--- | :--- |
| **`db`** | `mariadb:11.8` | `3306` | Cơ sở dữ liệu MariaDB, collation `utf8mb4_unicode_ci`. Volume: `db-data`. |
| **`redis-cache`** | `redis:alpine` | `6379` | Bộ nhớ đệm Redis cache cho Frappe (TTL 300s, catalog cache). |
| **`redis-queue`** | `redis:alpine` | `6379` | Hàng đợi background jobs Celery/RQ. Volume: `redis-queue-data`. |
| **`configurator`** | `frappe/erpnext:v16.34.2` | — | Chạy 1 lần lúc start: sinh `apps.txt`, set cấu hình DB host, redis host. |
| **`backend`** | `frappe/erpnext:v16.34.2` | `8000` | Gunicorn WSGI app server xử lý API, ORM Frappe và logic nghiệp vụ. |
| **`websocket`** | `frappe/erpnext:v16.34.2` | `9000` | NodeJS SocketIO server cho real-time events. |
| **`frontend`** | `frappe/erpnext:v16.34.2` | `8080` (host) | Nginx reverse proxy, serve static assets và điều hướng traffic vào backend. |
| **`queue-worker`** | `frappe/erpnext:v16.34.2` | — | Worker nền hợp nhất (`short,default,long`) — tiết kiệm ~300MB RAM cho VPS 3.7GB. |
| **`scheduler`** | `frappe/erpnext:v16.34.2` | — | Frappe Scheduler (cron job nội bộ ERPNext). |

*Lưu ý quan trọng:* Docker image ERPNext được cố định chặt bằng SHA digest:
`frappe/erpnext:v16.34.2@sha256:2feeb8973c3581726b4abd451ccb69c18426ec547bd04f7a4fdee47f17d1c3f1` (tránh lỗi trôi version khi pull mới).

---

## 4. Quản Lý Secrets & Mật Khẩu (Credentials)

1. **ERPNext Administrator:**
   - User: `Administrator`
   - Password: Được lưu tại file `/opt/vanphat/.admin-pass` trên VPS.
   - Bản sao dự phòng dev: Trong file `.env` local (`ADMIN_PASS=RjhdeIVf7zZ15eF1P6S3`).
2. **Database Root Password:**
   - Quản lý qua biến môi trường `MYSQL_ROOT_PASSWORD` trong file `/opt/vanphat/infra/.env` (hoặc `.env` root).
3. **GitHub Secrets (Cấu hình trên GitHub Repository `vanphatapp`):**
   - `VPS_HOST`: `13.213.13.201`
   - `VPS_USER`: `ubuntu`
   - `VPS_SSH_KEY`: Toàn bộ nội dung private key file `LightsailDefaultKey-ap-southeast-1.pem`.

---

## 5. Cơ Chế Sao Lưu Độc Lập Lên Cloudflare R2 (Disaster Recovery)

* **Script sao lưu:** [`infra/backup-r2.sh`](file:///var/home/huy/vanphatapp/infra/backup-r2.sh).
* **Lịch chạy tự động:** Cronjob trên VPS lúc 02:00 sáng hàng ngày:
  ```cron
  0 2 * * * /opt/vanphat/infra/backup-r2.sh
  ```
* **Quy trình:**
  1. Chạy profile backup docker compose: `docker compose --profile backup run --rm backup` để dump MariaDB và nén thư mục `files/`.
  2. Dùng `rclone` đồng bộ thư mục `./backups` lên bucket Cloudflare R2: `r2:vanphat-erp-backups`.
  3. Dọn dẹp cục bộ: Giữ lại 7 ngày gần nhất trên VPS; R2 lưu trữ 30 ngày theo lifecycle rule.

---

## 6. Quy Trình Triển Khai CI/CD Tinh Gọn (.github/workflows/)

Quy trình tự động hóa đã được dọn sạch các tàn dư nặng nề (loại bỏ self-hosted runner ngốn RAM VPS, loại bỏ Chrome headless và test CDP trên prod):

### 6.1. CI Workflow (`.github/workflows/ci.yml`)
* **Môi trường:** Chạy 100% trên runner chính thức `ubuntu-latest` của GitHub (zero load trên VPS).
* **Nhiệm vụ:** Build Vite frontend + kiểm tra composables/UI tokens + kiểm tra budget gate + chạy unit test Python backend (< 45 giây).

### 6.2. CD Workflow (`.github/workflows/cd.yml`)
* **Trigger:** Khi push/merge vào nhánh `master` hoặc kích hoạt thủ công (`workflow_dispatch`).
* **Bước 1 (An toàn dữ liệu):** SSH vào VPS gọi `docker compose --profile backup` để backup nhanh database trước khi chạm vào mã nguồn.
* **Bước 2 (Sync code):** Dùng `git archive` đóng gói và giải nén trực tiếp vào `/opt/vanphat`.
* **Bước 3 (Migrate & Reload):**
  * Chạy `bench --site app.vanphat.io.vn migrate`.
  * Khởi động lại `backend` Gunicorn và reload Nginx `frontend`.
* **Bước 4 (Smoke Test):** Kiểm tra HTTP endpoint `/login` phản hồi 200 OK.

---

## 7. Sổ Tay Lệnh Vận Hành Nhanh Cho Agent (Cheat Sheet)

### Kết nối vào VPS
```bash
ssh -i ~/Downloads/LightsailDefaultKey-ap-southeast-1.pem ubuntu@13.213.13.201
```

### Xem trạng thái & tài nguyên
```bash
cd /opt/vanphat
sudo docker compose -f infra/docker-compose.yml ps
sudo docker stats --no-stream
```

### Xem logs container
```bash
# Xem log backend xử lý API
sudo docker compose -f infra/docker-compose.yml logs -f --tail=100 backend

# Xem log frontend Nginx
sudo docker compose -f infra/docker-compose.yml logs -f --tail=100 frontend

# Xem log database
sudo docker compose -f infra/docker-compose.yml logs -f --tail=50 db
```

### Chạy lệnh Bench trong Backend
```bash
# Vào shell backend
sudo docker compose -f infra/docker-compose.yml exec -it backend bash

# Chạy migrate schema
sudo docker compose -f infra/docker-compose.yml exec -T backend bench --site app.vanphat.io.vn migrate

# Chạy import dữ liệu master
sudo docker compose -f infra/docker-compose.yml exec -T backend bench --site app.vanphat.io.vn execute scripts/import_master_data.py

# Xóa Redis cache
sudo docker compose -f infra/docker-compose.yml exec -T backend bench --site app.vanphat.io.vn clear-cache
```

### Khởi động lại hoặc Cập nhật dịch vụ
```bash
# Restart nhẹ Gunicorn backend
sudo docker compose -f infra/docker-compose.yml restart backend

# Reload Nginx frontend
sudo docker compose -f infra/docker-compose.yml exec -T frontend nginx -s reload

# Khởi động lại toàn bộ stack
sudo docker compose -f infra/docker-compose.yml down
sudo docker compose -f infra/docker-compose.yml up -d
```

### Sao lưu thủ công khẩn cấp
```bash
sudo docker compose -f infra/docker-compose.yml --profile backup run --rm backup
```
