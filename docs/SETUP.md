# SETUP (bench / deploy / import / measure)

## Stack

VPS (2 vCPU/3.7GB) + Docker compose (`infra/docker-compose.yml`, image `frappe/erpnext:v16.34.2` digest-pinned) + Cloudflare Tunnel (`app.vanphat.io.vn` → `127.0.0.1:8080`) + R2 backup. Tunnel + TLS Singapore adds ~200ms vs in-VPS.

## Fresh deploy (local is newest; prod wiped + redeployed from HEAD)

```bash
git archive HEAD apps scripts data/clean-data infra/docker-compose.yml | ssh ubuntu@VPS "cd /opt/vanphat && tar -x"
ssh ubuntu@VPS "cd /opt/vanphat && sudo docker compose -f infra/docker-compose.yml --env-file infra/.env up -d"
# new-site app.vanphat.io.vn, install-app vanphat_portal, migrate
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
