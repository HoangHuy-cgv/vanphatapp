# TODO — slice nhất-quán ADR-006 (docs xong → sửa code → verify)

Đang làm: docs/rule/policy đã viết lại (ADR-006 + AGENTS + 2 specs + CONSTRAINTS §4 + plan).
Tiếp theo sửa code cho khớp docs mới:

1. Backend: preview `product_total` chưa VAT (ADR-006) + test đặc tả; HOLD list = drawer;
   master lists sang envelope `page_result`; `bao_gia.py` docstring; bỏ `item_code "TRUC-IN"` cứng.
2. Frontend: `api()` hỗ trợ FormData; 2 caller `fetch()` → `api()`; bỏ `page_length: 500`;
   bỏ client math (`DrawerOrderDetail` rate, `totalItemQty`, `QuotesView` reduce+`||5000`);
   bỏ set state local sau mutate (`useOrderDeposit`, `OrdersView`); bỏ user cứng.
3. Verify: unittest + guard + constraints (`--init` lại baseline) + build + budget-gate → commit.

Không thuộc slice này: `<select>` ModalCreateOrder + rút config ra native (plan item 13).
