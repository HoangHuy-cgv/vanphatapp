# Plan Rebuild 2026-09-16 — Build lại từ 0 (Sếp chốt)

## Quyết định Sếp đã chốt (qua vote)
- `rebuild_scope`: Giữ visual, rebuild backend.
- `data_source`: Giữ `data/clean-data/` hiện tại làm baseline.
- `infra_tooling`: Xóa hết infra/tooling, build lại sau.
- `questions_timing`: Chốt `docs/QUESTIONS-2026-09-15.md` (~35 câu) TRƯỚC khi code.

## Giữ (4 nhóm)
- **G1 Docs gốc:** `AGENTS.md`, `CONSTRAINTS.md`, `README.md`,
  `docs/ARCHITECTURE.md`, `docs/API.md`, `docs/UI.md`, `docs/DATA.md`,
  `docs/DECISIONS.md`, `docs/BACKLOG.md`, `docs/SETUP.md` (đánh dấu stale vì infra sắp xóa).
- **G2 Spec + ADR (cấm sửa khi rebuild):** `docs/specs/erpnext-fields.md`,
  `docs/specs/packaging-math.md`, `docs/specs/packaging-taxonomy.md`,
  `docs/decisions/ADR-001..007-*.md`.
- **G3 Template visual:** `frontend/src/components/` (~30 file: BaseModal, BaseDrawer,
  ConfirmDialog, TableFiller, Detail*, order/*, quote/*), `src/assets/portal.css`,
  `tailwind.config.js`, `public/samples/`, logo/bg-factory/fonts Inter, `check-ui.mjs`.
  Views + composables chứa logic tiền/số/config → đập cùng backend, không giữ.
- **G4 Data:** `data/raw-data/` (gốc đối chiếu), `data/clean-data/` + `data/templates/`
  (baseline, không import mù). `docs/QUESTIONS-2026-09-15.md` giữ tạm để chốt, xong thì archive.

## Bỏ, không mang sang repo rebuild
- `api/*.py`, `hooks.py`, `www/portal.py`, `www/login.py`,
  `frontend/src/views/` (3 file), composables logic, `router/index.js`, `useSession.js` cũ.
- `tasks/plan.md`, `tasks/todo.md` cũ, `docs/review/` (5 file), `docs/HANDOFF*`,
  `archive/`, `public/frontend/assets/` build cũ, `tests/` cũ
  (ngoại lệ: giữ ý tưởng `test_alias_convention.py` — alias Title Case — viết lại theo backend mới).
- Toàn bộ `infra/`, `scripts/`, `.github/workflows/`, `sg-rules/` (xóa theo lệnh Sếp, dựng lại sau).

## Phase rebuild
- **Phase 0 (chặn):** chốt QUESTIONS tiền/quyền/dữ liệu. Chưa chốt → chưa code.
- **Phase 1 (scaffold sạch):** repo mới chỉ gồm G1+G2+G3+G4 +
  `fixtures/custom_field.json` + `property_setter.json` (config native SSOT).
  Xóa build artifacts khỏi git.
- **Phase 2 (backend mới):** dựng lại `api/` thin facade theo Triple rule +
  `docs/API.md` + spec fields. Viết lại unittest từ 0.
- **Phase 3 (gắn visual cũ):** ráp G3 vào backend mới, xóa mọi money/qty/config
  hardcode trong Vue, chỉ giữ layout/Modal/Drawer/màu/click-select.
- **Phase 4 (khóa kiểm soát):** viết lại gates tối thiểu (unittest + 2 FE guard +
  budget-gate + review tiers). Không gates không merge.

## Rủi ro đã nêu (Sếp biết khi xóa infra/tooling)
Mất `scripts/import_master_data.py` → clean-data thành mồ côi, không import được.
Mất `review-gate.sh` + `budget-gate.sh` + `sg-rules/` + CI/CD → rebuild không phanh.
Đề xuất tối thiểu: đóng băng `import_master_data.py` + 2 gate + `sg-rules/` đọc-only;
`infra/docker-compose` + `.github` xóa theo lệnh, dựng lại sau.

## Backup đi kèm (2026-09-16)
- Git: branch `backup/master-2026-09-16-wip` + tag `backup-2026-09-16-wip`
  (tracked files + WIP build assets), tag `backup-2026-09-16-full` (gồm file này).
- Full disk: `archive/backups/vanphatapp-full-2026-09-16.tgz`
  (gồm cả file git-ignored: `data/raw-data/`, `.env`, `github.env`, `archive/` cũ —
  KHÔNG commit, KHÔNG push file này).
- Git bundle: `archive/backups/vanphatapp-git-2026-09-16.bundle` (`--all`).
- Cách restore: xem `archive/backups/RESTORE-2026-09-16.md`.
