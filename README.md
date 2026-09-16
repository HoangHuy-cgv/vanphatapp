# Van Phat App

ERPNext v16 native backend + thin Vue cockpit for flexible-packaging factory (quotes, orders, deposits, catalog).

Triple rule: **backend native + config native + visual custom** (binding — see `AGENTS.md`).

## Layout

```text
AGENTS.md / CONSTRAINTS.md   # agent rules + quality bar
docs/                        # 7 files: ARCHITECTURE API UI DATA DECISIONS SETUP BACKLOG
apps/vanphat_portal/         # Frappe app: api/ + frontend/src/ + fixtures/ + tests/
data/clean-data/             # master CSVs (import source)
scripts/                     # checker, gates, import, measure
infra/                       # compose, tunnel, backup
```

## Commands

```bash
python3 -m unittest discover -s apps/vanphat_portal/tests -p "test_*.py"
node apps/vanphat_portal/frontend/check-composables.mjs
bash scripts/budget-gate.sh                 # after build
node scripts/test-browser-portal.mjs        # browser test vs STAGING bench (real API + real CSRF, never mock; creates TEST- orders/quotes, deletes after)
```

Deploy: local is newest; prod wiped + deployed fresh from HEAD (see `docs/SETUP.md`).
Never `git push` without explicit order.
