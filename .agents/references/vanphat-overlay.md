# VanPhat overlay — Frappe/ERPNext + portal conventions

File này là layer custom CỦA REPO (không thuộc upstream addyosmani).
Skill addy trong `.agents/skills/*` giữ nguyên văn upstream (sealed).
Khi skill addy yêu cầu "project conventions / CLAUDE.md or equivalent",
dùng các quy ước dưới đây thay vì suy luận.

## Review bổ sung (kèm `code-review-and-quality` 5 trục)

- Mọi review code Frappe/ERPNext: cross-examine thêm `quality-code-review`
  (Frappe-specific database traps, atomicity invariants, permission checks).
- Cấm trong user API: `ignore_permissions`, `get_all` trên dữ liệu phân quyền,
  `allow_guest=True` trên dữ liệu nội bộ, raw-SQL prod mutation,
  hand-rolled money/tax, hardcoded commercial constants.
  Chi tiết: `CONSTRAINTS.md` (Floor 11 luật = 0), `docs/API.md` (quyền `_guards.py`).

## Simplify theo stack repo (kèm `code-simplification`)

- Python: ưu tiên idiomatic Frappe ORM thay raw SQL (đúng permission/cache hooks):

```python
# Before
users = frappe.db.sql("SELECT name, email FROM `tabUser` WHERE enabled=1", as_dict=True)
# After
users = frappe.get_all("User", filters={"enabled": 1}, fields=["name", "email"])
```

- Dict lookup an toàn: `status = data.get("status") or "Draft"`.
- Vue 3 `<script setup>` (portal dùng Vue, không phải React):
  derived state qua `computed` thay vì watcher dư thừa; ternary lồng nhau
  trong UI logic thay bằng lookup map theo status text+màu.
  Chi tiết: `docs/UI.md` (native `<dialog>`, `custom_alias`, header 1 dòng,
  số Việt `tabular-nums`, HTTP chỉ via `api()`).

## Guard sớm (kèm `constraint-driven-development` floor-guard)

- Sau mỗi slice chạy 3 lệnh: `unittest discover` BE + `check-composables.mjs`
  FE + `scripts/constraints-check.py` (floor + ratchet). Fail = block merge.
- Cấm `constraints-check.py --init` chung commit với feature đang fail
  (baseline chỉ update khi số tốt lên + ADR riêng).
