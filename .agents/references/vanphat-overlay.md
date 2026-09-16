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
- Review trap thực chiến (từ pilot 2026-09-16, bắt được mà OCR rules built-in mù):
  open redirect (`redirect-to`/query param gán thẳng location không validate
  internal path `/` không `//`), hardcode route 2 chỗ gây drift, commit message
  ghi có test nhưng diff thiếu file test, CSV zero giá mất traceability
  (ghi note nguồn như pattern TMD-00004), mã mới lệch chứng từ gốc
  (TP-00035 3KG vs Q38 2KG), body Q-doc mâu thuẫn heading chốt,
  `standard_rate=0` thành giá mặc định, brand trống vs rule sở hữu,
  referential mã trục trong note, valuation=0 khi thiếu BOM.
- Tier 1: self-check checklist rút gọn. Tier 2: 3-agent + `review-gate.sh`.
  OCR đối trọng chỉ khi Sếp gọi tên (không tier riêng).

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

## Guard sớm (kèm CI gates-fe Floor-11 grep native)

- Sau mỗi slice chạy 4 lệnh: `unittest discover` BE + `check-composables.mjs`
  FE + `check-ui.mjs` FE + `bash scripts/budget-gate.sh` (sau build). Fail = block merge.
  CI gates-fe chạy thêm Floor-11 grep native (v-html, raw fetch ngoài
  useSession.js, Math.random ID, allow_guest, stub, suppression).
