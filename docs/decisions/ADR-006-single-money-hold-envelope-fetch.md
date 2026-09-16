# ADR-006: Nhất quán tiền/HOLD/envelope/fetch — code khớp docs (tiếp ADR-002/ADR-005)

## Status
Accepted (2026-09-15 — em quyết định theo ủy quyền của Sếp; đối chiếu docs ↔ code cùng ngày)

## Date
2026-09-15

## Context
Sau ADR-005, em đối chiếu toàn bộ docs/policy với code thực tế và phát hiện 4 nhóm vênh
làm docs nói một đằng, code làm một nẻo:

1. **Ngữ nghĩa tiền 2 phiên bản.** `order.get_price_preview` tính
   `product_total = net_total + vat_amount` (tiền hàng **gồm VAT**, gồm cả trục —
   `order.py:316`, test khoá ở `test_api_characterization.py:133-134`), trong khi
   `list_orders`/`get_order_details` tính `product_total = net_total − cylinder_total`
   (tiền hàng **chưa VAT**, không trục — `order.py:510,572`). Cùng một đơn, modal tạo đơn
   và drawer đối soát ra 2 số "tiền hàng" khác nhau → `required_deposit` lệch nhau.
2. **Công thức HOLD 2 phiên bản** (plan item 11). List dùng mốc cứng
   `grand_total*0.5` (`order.py:539-547`), drawer dùng `required_deposit`
   (`_order_lifecycle`, `order.py:579-592`). Đơn Trả sau ở list vẫn có thể bị gán mốc 50%.
3. **Envelope list 2 chuẩn.** `order/item/bao_gia` trả `page_result` envelope
   (`{orders|items|quotations, page, page_length, total_count, total_pages}`), còn
   `customer/supplier/user.get_list` trả mảng trần. Frontend phải đỡ 2 dạng
   (`Array.isArray(data)` ở `OrdersView.vue:411`, `QuotesView.vue:351`, `useCatalogData.js:301,333`).
4. **Frontend lách luật vỏ-mỏng.** `ModalStep1Sale.vue:331` và `ArtworkBox.vue:113`
   gọi `fetch()` trực tiếp (bỏ qua `api()` → mất CSRF/toast/abort thống nhất);
   `OrdersView.vue:431` xin `page_length: 500` (vượt trần 100);
   `DrawerOrderDetail.vue:313` tự tính `rate = product_total/qty`;
   `QuotesView.vue:371` tự `reduce` qty + fallback `|| 5000` (+`useCreateOrderForm.js:85,100,226,278`,
   `useStep2DirectorForm.js:21,28`, `QuotesView.vue:323-324,404`);
   `useSession.js:4` hardcode `giamdoc@vanphat.com`;
   `useOrderDeposit.js:58-62,79-97` và `OrdersView.vue:473-474` tự set `order_state`/
   `completed_qty` ở client sau mutate (trái CONSTRAINTS §4.4).
5. **Docs mô tả quá khứ.** Backend spec §5 viết cache key "thiếu params → stale" nhưng code
   đã chứa mọi params (`item.py:138`); frontend spec §4 viết "3 route import tĩnh +
   keep-alive trần" nhưng `router/index.js:4-6` đã lazy 100% và `App.vue:107` đã
   `include+max`; frontend spec §3 hứa "đích frappe-ui v2" không kiểm chứng được;
   `bao_gia.py:1-6` còn docstring "shell API stubs ... fixed literal" dù đã là
   implementation thật.

## Decision
1. **Một ngữ nghĩa tiền duy nhất mọi màn (thay định nghĩa preview cũ):**
   `net_total`/`vat_amount`/`grand_total` là số native trên chứng từ;
   `cylinder_total` = giá NCC pass-through **chưa VAT**;
   `product_total = net_total − cylinder_total` (tiền hàng chưa VAT, không trục);
   `qty` = tổng số lượng **chỉ dòng túi/cuộn** (bỏ dòng trục);
   bất biến kiểm chứng `product_total + cylinder_total + vat_amount = grand_total`;
   `required_deposit = product_total × deposit_pct + cylinder_total`
   (`0` khi Trả sau; cặp `*_final = null` khi thiếu giá NCC — pending truthful).
   Test đặc tả cũ ở `test_api_characterization.py:133-134` phải sửa theo.
2. **Một công thức HOLD duy nhất list + drawer:** HOLD ⟺ Trả trước
   AND `0 < advance_paid < required_deposit`. Trả sau **không bao giờ** HOLD
   (theo `order_state` Trả sau của `_order_lifecycle`). List bỏ mốc `grand_total*0.5`.
3. **Envelope list chuẩn cho mọi module:** mọi list API trả `page_result`
   (`_common.page_result`). `customer/supplier/user.get_list` migrate sang envelope;
   frontend bỏ nhánh `Array.isArray(data)` sau migrate.
4. **Hai lớp pagination (ghi rõ, không giả vờ một số):** giao dịch
   (orders/quotations/items) `default 15, max 100`; picker tham chiếu
   (customer/supplier/user cho ô chọn) `default 100, max 100` + filter server,
   vì picker hiện tải một lần cho ô chọn. Slice sau paginate picker + search server.
5. **Config UI là native, cấm hardcode mới:** option lists, defaults, labels, thứ tự,
   ẩn/hiện chỉ từ Custom Field / Property Setter / DocType Layout / Item Group tree /
   `min_order_qty`. Cấm fallback số thương mại (`|| 5000`, `qty: 10000/5000/100`,
   default vật liệu `['OPP','PE sữa']`, `'3.500.000 đ/cây'`, user/email cứng).
   Cái đã lỡ hardcode giữ nguyên trong ratchet và rút dần theo plan item 3 —
   **không thêm mới**.
6. **`api()` là đường fetch duy nhất (kể cả upload):** mở rộng `api()` hỗ trợ
   `FormData` (không set `Content-Type` tay để browser gắn boundary, vẫn gắn CSRF +
   toast + signal). Xoá mọi `fetch()` trực tiếp trong `src/`.
7. **Click-chọn là chuẩn, `<select>` chỉ còn tạm:** ≤ 8 phương án → nút
   `role=radiogroup`/`radio` điều khiển được bằng bàn phím (ModalStep1Sale đã đạt);
   > 8/dynamic (KH/NCC/Item) → ô Tìm-và-Chọn gõ-lọc. `<select>` còn lại trong
   `ModalCreateOrder.vue` là nợ plan item 3, không phải chuẩn.

## Alternatives Considered
- **Giữ song song 2 ngữ nghĩa tiền (preview gồm VAT, list không):** Pros — khỏi sửa
  test. Cons — cùng đơn 2 số tiền hàng, cọc lệch, Sếp không thể đối soát. Rejected.
- **Giữ mảng trần cho master lists:** Pros — khỏi sửa frontend. Cons — 2 hợp đồng API,
  debt vĩnh viễn. Rejected — migrate một lần gọn hơn.
- **Cho phép `fetch()` trực tiếp cho upload:** Pros — khỏi sửa `api()`. Cons — mất CSRF/
  toast/abort thống nhất, tiền lệ xấu. Rejected — mở rộng `api()` một lần.

## Consequences
- Sửa `order.py` preview + HOLD list, `bao_gia.py` docstring, `customer/supplier/user.py`
  envelope, `create_sales_order` bỏ `item_code "TRUC-IN"` cứng.
- Sửa `api()` + 2 caller `fetch()`, bỏ `page_length: 500`, bỏ client money/qty math,
  bỏ set state local sau mutate (đọc lại server), bỏ defaults cứng/user cứng.
- Cập nhật test đặc tả (preview product_total/required_deposit), chạy lại baseline
  ratchet (`--init`) vì nhiều số đo **giảm** (tốt lên).
- `<select>` trong ModalCreateOrder + rút config ra native vẫn là plan item 3, không
  nhồi vào slice nhất-quán này.
