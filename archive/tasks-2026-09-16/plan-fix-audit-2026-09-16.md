# Plan fix findings audit 2026-09-16

## Overview
Khắc phục 7 findings (P0 backend-correctness → P1 mega+config → P2 structure),
mỗi slice giữ hệ thống chạy + unittest xanh. Không đụng flow tiền/quyền ngoài
phạm vi finding. Push chỉ khi Sếp lệnh.

## Quy tắc slice (binding)
- `order.py` là API path (`vanphat_portal.api.order.*` mà frontend đang gọi) →
  khi chẻ module, giữ wrapper `@frappe.whitelist` mỏng trong `order.py`,
  logic dời sang submodule. Không đổi dotted path.
- Xóa fallback cọc im lặng: thiếu config → `frappe.throw` (fail loudly),
  không số mặc định trong code.
- Mỗi task xong: unittest + composables guard; task chạm tiền/API/large:
  review Tier 2 (3-agent + `scripts/review-gate.sh`) theo CONSTRAINTS.

## Task List

### Phase 0 — Research (không code)
- [x] Task 0: đọc DrawerStep2Director/ModalStep1Sale, chốt component map +
  nguồn native cho options dáng túi + field Van Phat Settings.

Chốt Task 0 (evidence trong repo):
- `ModalStep1Sale` đã có props `productTypes/printTechs/accessories`
  config-native, `QuotesView:137-141` đã truyền; `useQuoteDefaults.js` đọc
  `item.get_product_groups` + `item.get_print_config`. Nhưng template vẫn render
  nút cứng (ModalStep1Sale:27-61 `Túi đáy đứng/Cuộn màng ghép/...`), chưa `v-for`
  props → Task 4 = thay nút cứng bằng `v-for` props (props trống → ẩn khối
  truthful, form bắt chọn như `canContinue` hiện tại).
- Backend KHÔNG có `Van Phat Settings`; `order.py` có 3 điểm dùng
  `FALLBACK_DEPOSIT_PCT`: L191 (map), L229 (single), L597 (list). Task 1 =
  DocType Single mới `Van Phat Settings` + field `default_deposit_pct`,
  helper `_default_deposit_pct()` đọc Single (cache request), thiếu → throw.
  Fixture export để prod migrate có config.
- `order.py` đang 1028L, callers (tests `order._*` + frontend `order.*`)
  đều qua dotted path `vanphat_portal.api.order.*` → chẻ module phải giữ
  wrapper whitelist mỏng trong `order.py`, không đổi path.
- DrawerStep2Director logic đã nằm trong `useStep2DirectorForm` (template 214L
  + style); template còn 4 khối: top-summary / items-table / cylinder-row /
  finance+artwork+footer → Task 3 tách 4 children `components/quote/` theo đúng
  mẫu `order/` (props-down/events-up).
- ModalStep1Sale script ôm search KH + derived + submit; template 5 cụm
  (product/accessory/print/cylinder/customer+dims) → Task 5 tách 3 children +
  `useStep1SaleForm` composable.

### Phase 1 — P0 backend correctness
- [ ] Task 1: Single DocType `Van Phat Settings` (`default_deposit_pct`) +
  dời `FALLBACK_DEPOSIT_PCT = 0.5` vào đó; thiếu config → throw.
- [ ] Task 2: gộp `_order_status` + `_order_detail_status` thành 1 model
  duy nhất (short label + detail state + css + is_hold + can_submit);
  list + drawer cùng gọi. Xóa hàm thừa.

### Checkpoint P0
- [ ] unittest 61+ xanh, review Tier 2, commit atomic.

### Phase 2 — P1 mega + config native
- [ ] Task 3: tách `DrawerStep2Director.vue` (761L) theo component map Task 0.
- [ ] Task 4: options dáng túi/in ấn → nguồn native (Desk sửa, không rebuild);
  xóa ~13 chỗ hardcode `ModalStep1Sale.vue`.
- [ ] Task 5: tách `ModalStep1Sale.vue` (656L) theo component map Task 0.

### Checkpoint P1
- [ ] `npm run build` + budget-gate xanh, browser smoke prod pass, Tier 2.

### Phase 3 — P2 structure
- [ ] Task 6a: `order_pricing.py` (thuế/cọc/preview) + wrapper mỏng.
- [ ] Task 6b: `order_queries.py` (list/detail + maps) + wrapper mỏng.
- [ ] Task 6c: `order_actions.py` (deposit/approve/submit/create/make) + wrapper.
- [ ] Task 7: Views gầy hóa → `useOrdersList` / `useQuotesFlow`; Views chỉ
  composition + render.

### Checkpoint P2 (final)
- [ ] Full gates (unittest + composables + build + budget-gate + browser-test
  prod), Tier 2, commit atomic, báo Sếp chờ lệnh push.

## Deferred (ghi nhận, không làm đợt này)
- `BaseDetailDrawer` chung cho 4 Drawer KH/NCC/User/Item (284–405L trùng khung).
- SFC order `<template>` trước — sửa khi chạm file, không hàng loạt.

## Risks
| Risk | Impact | Mitigation |
|---|---|---|
| Đổi path whitelist gãy frontend | High | wrapper mỏng giữ path, grep caller trước/sau |
| Single mới thiếu trên prod | Med | fixtures export + migrate check, throw rõ tên config |
| Tách mega vỡ props/events | Med | props-down/events-up như mẫu `order/`, browser-test drawer |
