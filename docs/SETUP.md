# SETUP (bench / deploy / import / measure)

## Flow CI/CD (binding cho agent — tiêu chuẩn local build → test pass → CI/CD deploy prod)

```
LOCAL (máy dev)              CI (GitHub Actions)              CD (VPS prod, tay Sếp bấm)
─────────────────            ──────────────────              ──────────────────────────
1. code theo slice     →     PR/push:                         merge main xong, Sếp duyệt:
2. unittest (xanh)            - gates-fe + gates-be CHẠY       2. git archive → VPS
3. 2 FE guard (xanh)             SONG SONG (~15s wall)           3. compose up -d
4. vite build                 - đỏ = CẤM merge                 4. migrate (CHỈ khi chạm backend)
5. budget-gate PASS           (branch protection)               5. nginx reload (frontend-only)
commit local                                               →  6. smoke /login + /portal
                                                               7. lỗi = rollback backup
```

Tối ưu 2026-09-16 (Sếp duyệt): CD path-filter — đổi thuần frontend thì skip
`bench migrate` (~20s saved) + `nginx -s reload` thay `restart frontend`
(10s → ~1s). CI tách 2 job song song (grep native, khỏi npm install).
Lưu ý: gates-be có thể chờ runner GitHub ~30s (hạ tầng free, không fix được
bằng config) — steps thực chỉ ~3s.

Quy định:

- Agent KHÔNG bao giờ deploy tay (không SSH chạy lệnh prod, không rsync tay). Mọi deploy đi qua CD, có backup + rollback.
- Secrets (SSH key, `.admin-pass`, GitHub Secrets) KHÔNG vào repo. Key VPS nằm trên máy dev (`~/Downloads/*.pem`, chmod 600), không commit.
- Local build ra artifacts (`public/frontend`, `www/portal.html`) phải commit vào git để CD dùng đúng bản đã test.
- Prod đang sống (`app.vanphat.io.vn` 200): CD không wipe khi chưa có lệnh Sếp. Deploy = update code + migrate, giữ data.

## Stack & Hạ tầng VPS

- **VPS:** AWS Lightsail Singapore (`13.213.13.201`, SSH user `ubuntu`, key `~/Downloads/LightsailDefaultKey-ap-southeast-1.pem` hoặc `~/.ssh/`, app root `/opt/vanphat`).
- **Docker Compose:** `infra/docker-compose.yml`, image `frappe/erpnext:v16.34.2` digest-pinned (`sha256:2feeb8...`).
- **Domain & Tunnel:** `https://app.vanphat.io.vn` qua Cloudflare Tunnel (`vanphat-erp` trỏ về `127.0.0.1:8080`).
- **Backup:** Script `infra/backup-r2.sh` đồng bộ hàng đêm lên Cloudflare R2 bucket `vanphat-erp-backups`.
- **Tài liệu Chi tiết:** Toàn bộ thông số, kiến trúc container, quản lý secrets và cheat sheet lệnh vận hành nằm tại [`infra/README.md`](file:///var/home/huy/vanphatapp/infra/README.md).

## Deploy tay (dự phòng khi CD chưa có — cần lệnh Sếp, có backup trước)

```bash
PEM=~/Downloads/LightsailDefaultKey-ap-southeast-1.pem
VPS=ubuntu@13.213.13.201
git archive HEAD apps scripts data/clean-data infra/docker-compose.yml | ssh -i $PEM $VPS "cd /opt/vanphat && tar -x"
ssh -i $PEM $VPS "cd /opt/vanphat && sudo docker compose -f infra/docker-compose.yml --env-file infra/.env up -d"
# bench --site app.vanphat.io.vn migrate, bench build --app vanphat_portal
```

## Fresh-site prerequisites (before `import_master_data.py`)

Site starts empty; wizard skips fixtures. Create in order: `All Item Groups` → Company (via `create_fiscal_year_and_company`: chart Standard, VND) → Warehouse Types (Transit/Stores/WIP/Finished/Goods-in-Transit/Scrap/Rejected/Spoilage) → Customer/Territory/Supplier Group roots → Countries (Vietnam/Cambodia) → Payment Terms + Templates (prepaid 50/50, 30-day rolling, per-lot, on-delivery variants) → Price Lists (sell/buy, set in Selling/Buying Settings) → Global Defaults `default_company`.

Then: `python /tmp/imp.py --site app.vanphat.io.vn --data-dir /tmp/clean-data` (inside `sites/` dir, bench env python). Gotchas fixed in script: Country ISO map, Workstation autoname (`workstation_name`), Operation Prompt name, fractional `Cái` UOM.

## Measure

```bash
ADMIN_PASS=$(ssh ubuntu@VPS "sudo cat /opt/vanphat/.admin-pass") python3 scripts/measure_p95.py [--seed 15]
```

2026-09-15: list/detail p95 đo qua tunnel vs in-VPS (xem log measure mới nhất; không ghi số cứng — code + log là truth).

## Browser-test prod (nick admin — không hỏi lại Sếp)

```bash
google-chrome --remote-debugging-port=9222 --no-sandbox &
ADMIN_PASS=$(ssh -i ~/Downloads/LightsailDefaultKey-ap-southeast-1.pem ubuntu@13.213.13.201 "sudo cat /opt/vanphat/.admin-pass") PORTAL_URL=https://app.vanphat.io.vn/portal node scripts/test-browser-portal.mjs
```

Script tự login Administrator + gieo cookie CDP, verify catalog rows + drawer thật, chứng từ TEST- cleanup.

## Frontend deploy

Build local (`vite build --base=/assets/vanphat_portal/frontend/` + copy entry), sync entry HTML via git, rsync `assets/` to VPS, `bench build --app vanphat_portal` (copies into `sites/assets`), recreate frontend container (bind-mount refresh).

## Tunnel

Setup once per `infra/cloudflare-tunnel.md`. Site name must equal public hostname.
