# Plan: Backlog sau cleanup triple-rule (Sếp duyệt thứ tự)

## Đã xong
- **Simplify + tối ưu backend API**: `_common.py`, hết N+1, tiền native một ngữ nghĩa
  (`product_total = net_total − cylinder_total`, trục chưa VAT, `qty` bỏ trục), count báo giá
  khớp filter, POST tự commit, bỏ `FALLBACK_VAT_RATE`. 48 test trong `apps/vanphat_portal/tests/`.
- **Chuẩn "tối ưu" có máy kiểm**: `CONSTRAINTS.md` (triple rule ghim + 5 trục + floor 10 luật +
  ratchet) và `scripts/constraints-check.py` (floor trong pre-commit; `--init` ghi baseline).
- **Guard frontend**: `apps/vanphat_portal/frontend/check-composables.mjs` — import + khởi tạo
  mọi composable trong Node; bắt lỗi mà `vite build` không thấy.
- **Ghim `frappe-ui 1.0.0-beta.64`** (POC bỏ frappe-ui ở nhánh `poc/no-frappe-ui` giữ làm dự phòng).
- **ADR-005 (2026-09-14)**: config native là SSOT giao diện, visual custom duy nhất; cấm portal list
  native cho SO (frappe#42640 còn mở); hoãn Studio tới khi đủ 3 điều kiện. UI §7 + DoD 13–15
  (không đào tạo, click-chọn, flow raw-data).
- **ADR-006 (2026-09-15)**: một ngữ nghĩa tiền + một HOLD + một envelope + `api()` duy nhất.
- **Triple rule slice (2026-09-15, `b1de2ff`)**: 3 endpoints config native
  (`get_product_groups/get_payment_options/get_print_config`); ModalCreateOrder bỏ `<select>`
  cứng → nút click-chọn + search-select KH; DrawerStep2 vật liệu từ cấu trúc màng native;
  `qty` gợi ý từ `min_order_qty`; picker KH/NCC/User paginate + search server.
- **Cleanup**: xóa CSS chết, biến submit chết, ảnh mẫu cứng, `defineExpose` chết,
  `loadAllCatalogData` tải thừa; xóa JSON mock local; `serve-portal.mjs` gắn boundary LOCAL ONLY;
  docs/rule/policy/skill cùng một ngữ cảnh (triple rule).
- **Quyền native (2026-09-15, `3d71990`)**: 1 user nhiều role, Desk giữ "ai được làm gì";
  `_guards.py` (`require_roles`/`require_doc`); Sales tạo/chốt, Kế toán độc quyền cọc + duyệt HOLD;
  User list chỉ System Manager; bỏ whitelist cache; xóa `ignore_permissions`;
  `api_ungated 22→0`, 48 test (+2 case Sale bị chặn).
- **Wipe prod + deploy fresh + p95 thật (2026-09-15)**: local mới nhất, VPS wipe sạch,
  site mới từ HEAD + import 293 Item/117 KH + seed 15 SO; p95 list 213ms / detail 302ms
  qua tunnel, 13ms/7ms trong VPS (app nhanh, tunnel chậm — chi tiết backend spec §9);
  fix 4 bug bắt được khi đo thật (pypika alias, qb.Order, hook args, warehouse SO);
  `scripts/measure_p95.py` đo lại.

## Còn lại (chờ Sếp ra việc — KHÔNG đụng trước khi Sếp chốt)
1. **Flow cọc 2 bước** (quyền đã đóng — `api_ungated = 0`, 48 test): hiện `record_order_deposit`
   chỉ Kế toán bấm; Sếp chốt "sale yêu cầu → kế toán xác nhận" làm slice riêng (thêm nút yêu cầu
   cho Sales + hàng đợi xác nhận cho Kế toán).
2. **p95 — ĐÃ ĐO 2026-09-15** (site fresh từ HEAD local, wipe prod theo lệnh Sếp):
   `list_orders` p95 = 213ms, detail p95 = 302ms qua tunnel; trong VPS chỉ 13ms/7ms.
   Kết luận: app nhanh, tunnel Singapore +193ms. Chi tiết §9 backend spec.
   Tối ưu tiếp (Argo/cache edge/tách detail) chờ Sếp ra việc.
3. **Vitest**: chưa cài được (máy này không ra được npm registry + `~/.npm` không ghi được).
4. **Stack frontend**: giữ `frappe-ui` ghim version (POC dự phòng ở nhánh `poc/no-frappe-ui`).
   Rà lại Studio khi đủ 3 điều kiện mở lại (ADR-005 §5).
5. **Remote + push**: chưa có remote — Sếp cho URL + lệnh explicit.
6. **Nợ nghiệp vụ chờ Sếp**: enforce BTP `is_sales_item=0` ở Đơn bán; MST KH 0/117; cuộn màng tiêu
   chưa mã (BTP bán được hiện chỉ 00015); phân loại TMD theo `item_group`/prefix;
   golden test engine báo giá `calculate_packaging_quotation` (slice riêng, ADR-002).
