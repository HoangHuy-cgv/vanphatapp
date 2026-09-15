# SETUP (bench / deploy / import / measure)

## Flow CI/CD (binding cho agent — tiêu chuẩn local build → test pass → CI/CD deploy prod)

```
LOCAL (máy dev)              CI (GitHub Actions)              CD (VPS prod, tay Sếp bấm)
─────────────────            ──────────────────              ──────────────────────────
1. code theo slice     →     PR/push:                         merge main xong, Sếp duyệt:
2. unittest 54/54             - constraints-check.py            1. backup R2 (tự động trong CD)
3. composables 9/9            - py unittest (không bench)       2. git archive → VPS
4. vite build                 - vite build + budget-gate       3. compose up -d
5. budget-gate PASS           - đỏ = CẤM merge                 4. migrate + bench build
6. constraints PASS           (branch protection)               5. smoke /login + /portal
commit local                                               →  6. lỗi = rollback backup
```

Quy định:

- Agent KHÔNG bao giờ deploy tay (không SSH chạy lệnh prod, không rsync tay). Mọi deploy đi qua CD, có backup + rollback.
- Secrets (SSH key, `.admin-pass`, GitHub Secrets) KHÔNG vào repo. Key VPS nằm trên máy dev (`~/Downloads/*.pem`, chmod 600), không commit.
- Local build ra artifacts (`public/frontend`, `www/portal.html`) phải commit vào git để CD dùng đúng bản đã test.
- Prod đang sống (`app.vanphat.io.vn` 200): CD không wipe khi chưa có lệnh Sếp. Deploy = update code + migrate, giữ data.

## Stack

VPS (13.213.13.201, key `~/Downloads/LightsailDefaultKey-ap-southeast-1.pem`, user `ubuntu`, `/opt/vanphat`) + Docker compose (`infra/docker-compose.yml`, image `frappe/erpnext:v16.34.2` digest-pinned) + Cloudflare Tunnel (`app.vanphat.io.vn` → `127.0.0.1:8080`) + R2 backup. Tunnel + TLS Singapore adds ~200ms vs in-VPS.

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

2026-09-15: list p95 213ms / detail 302ms via tunnel; 13ms/7ms in-VPS.

## Frontend deploy

Build local (`vite build --base=/assets/vanphat_portal/frontend/` + copy entry), sync entry HTML via git, rsync `assets/` to VPS, `bench build --app vanphat_portal` (copies into `sites/assets`), recreate frontend container (bind-mount refresh).

## Tunnel

Setup once per `infra/cloudflare-tunnel.md`. Site name must equal public hostname.
