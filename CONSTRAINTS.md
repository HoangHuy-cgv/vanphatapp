# CONSTRAINTS — Chuẩn "tối ưu" của dự án Vạn Phát

Rà soát lần cuối: **2026-09-15** — chốt bởi Sếp + em.
Phạm vi: `apps/vanphat_portal` (ERPNext native backend + Vue cockpit shell).

**Triple rule ghim (mọi dev tuân theo — Sếp chốt 2026-09-15):**
1. **Backend native** — tiền, thuế, cọc, BOM, tồn kho, trạng thái, sinh mã do DocType/controller
   native tính. API `vanphat_portal.api.*` chỉ là façade mỏng, không nghiệp vụ trùng.
2. **Config native** — option lists, defaults, labels, thứ tự, ẩn/hiện chỉ từ Custom Field /
   Property Setter / DocType Layout / Item Group tree / `min_order_qty` / Payment Terms /
   Credit Limit / Tax Template. Đổi trong Desk → UI đổi theo, **không build lại**.
3. **Visual custom** — phần duy nhất được viết tay: bố cục cockpit, Modal, Drawer, màu,
   nút click-chọn, diễn đạt flow bằng ngôn ngữ thân thiện. Cấm chứa tiền/thuế/trạng thái/
   cấu hình/danh sách lựa chọn trong code visual.

Áp dụng cho **mọi thay đổi** trong repo. Đây là file ràng buộc duy nhất; spec mô tả *xây cái gì*,
file này định nghĩa *thế nào là đủ tốt để ship*. **Không được nới lỏng file này để một thay đổi đi qua.**

## Cách chạy

```bash
python3 scripts/constraints-check.py          # floor + ratchet (đầy đủ, ~1s)
python3 scripts/constraints-check.py floor    # chỉ luật cấm (~0.1s, chạy trong pre-commit)
python3 scripts/constraints-check.py --init   # ghi lại baseline = số đo hiện tại
bash scripts/budget-gate.sh                   # trần trọng lượng bundle (đã có từ trước)
```

Máy kiểm chạy **không cần bench, không cần mạng, không cần Node**. Đó là điều kiện để nó thực sự chạy.

## 1. Floor — luật cấm, phải bằng 0 ngay hôm nay

10 luật dưới đây đang bằng 0 trên code hiện tại. Vi phạm = `GATE: FAIL`, không có ngoại lệ:

| id | Luật |
|---|---|
| `mock_random_id` | Không `Math.random()` làm ID tài liệu |
| `guest_api` | Không `allow_guest=True` trên dữ liệu nội bộ |
| `permissioned_get_all` | Không `frappe.get_all` trên master data có phân quyền (dùng `get_list`) |
| `raw_html` | Không `v-html` |
| `suppression` | Không thêm comment tắt máy kiểm: `@ts-ignore`, `eslint-disable`, `# noqa`, `type: ignore`, `istanbul ignore`, `Stryker disable`, `nosemgrep`, `gitleaks:allow` |
| `secret` | Không khoá/bí mật trong source |
| `stub` | Không `NotImplementedError`/`TODO`/`FIXME` đứng thay chỗ implementation trong API |
| `raw_fetch` | Không `fetch(` trực tiếp trong `frontend/src` — mọi HTTP qua `api()` duy nhất (kể cả upload FormData) |
| `hardcoded_user` | Không email/user hardcode trong client (sidebar đọc từ `get_boot`) |
| `hardcoded_config` | Không option lists / defaults / labels / thứ tự hardcode mới trong Vue (config từ native — triple rule 2) |

Thêm luật cấm thì sửa `FLOOR_RULES` trong `scripts/constraints-check.py` — **siết thì im lặng, nới thì phải to tiếng** (ghi vào bảng Exceptions có người chịu trách nhiệm + ngày hết hạn).

## 2. Năm trục "tối ưu" — có số và có lệnh

Định nghĩa chốt 2026-09-14. Một trục chỉ được coi là ràng buộc khi cột "Máy kiểm" tồn tại và chạy được.

| # | Trục | Định nghĩa đo được | Máy kiểm | Chạy ở |
|---|---|---|---|---|
| 1 | **Sự thật (SSOT)** | Mọi con số hiển thị là field do API trả; client chỉ `Intl.NumberFormat`. Nhân/chia tiền, thuế, cọc, qty phải nằm ở backend. | `constraints-check.py` → `client_money_math`, `client_qty_reduce`, `client_magic_fallback`, `client_hardcoded_qty` | mỗi lần sửa |
| 2 | **Quyền** | Mỗi `@frappe.whitelist()` phải có cổng quyền (`has_permission`/role/`only_for`) hoặc nằm trong allowlist có lý do. Đường `frappe.qb` phải lọc theo quyền như `get_list`. | `constraints-check.py` → `api_ungated` (ledger parse AST) | mỗi lần commit |
| 3 | **Kiểm chứng** | Backend: 41 test xanh, không giảm. Frontend: **guard composable** (`check-composables.mjs`) phải xanh; test cho mọi composable có logic; coverage dòng đã sửa ≥ 80% (khi có Vitest). | `unittest discover` + `node check-composables.mjs` (đã nối vào `constraints-check.py`) | task end / CI |
| 4 | **Trọng lượng & tốc độ** | Entry JS ≤ 170KB gzip (warn) / 300KB (fail); async chunk ≤ 500KB. FCP < 0,8s; p95 API — **chưa đo được** (cần staging). | `scripts/budget-gate.sh` (đã có) + Lighthouse (**chưa cài**) | mỗi lần build |
| 5 | **Tiếp cận & tin cậy** | 0 vi phạm axe mức critical/serious (WCAG AA). Trạng thái đọc được bằng chữ tiếng Việt + màu, không chỉ màu. | `axe` (**chưa cài**, cần URL) | preview deploy |

Trục 3–5 chưa có máy kiểm đầy đủ. Ghi rõ ở đây để không ai nhầm khát vọng thành ràng buộc; mỗi lần cài thêm
một tool thì bổ sung dòng tương ứng vào bảng này **cùng ngày**.

## 3. Đang đo, chưa ép — ratchet (chỉ được tốt lên)

Baseline trong `.constraints-baseline.json`. Xấu đi = `GATE: FAIL`. Không đặt đích viển vông làm build đỏ vĩnh viễn.

| Số đo | Hôm nay | Hướng | Đích |
|---|---|---|---|
| Endpoint chưa có cổng quyền (trên 26 endpoint) | **0** | giữ 0 | 0 (đóng nợ quyền slice 2026-09-15: 25 endpoint gated + get_boot allowlist W2) |
| Danh tính user hardcode trong client | **1** | giảm | 0 |
| Client tự nhân/chia trên field tiền | **1** | giảm | 0 |
| Client tự cộng qty (`.reduce`) | **2** | giảm | 0 |
| Fallback số thương mại cứng (`\|\| 5000`) | **1** | giảm | 0 |
| `qty` mặc định cứng trong client | **6** | giảm | 0 (đưa vào master data native) |
| `catch` nuốt lỗi | **1** | giảm | 0 |
| Entry JS gzip | **142 KB** | giảm/giữ | ≤ 170 warn / 300 fail |
| File test frontend | **0** | tăng | ≥ 8 (các composable có logic) |
| Guard composable frontend xanh | **1** | giữ 1 | 1 (không được tắt) |
| Test backend xanh | **46** | tăng | không giảm |

**Bằng chứng máy kiểm có tác dụng (2026-09-14):** guard `check-composables.mjs` bắt được
`ReferenceError: serverPricingInitial is not defined` trong `useCreateOrderForm.js` — lỗi làm
**modal "Tạo đơn hàng" chết hoàn toàn** ở bản build production, và đã lọt qua `vite build` vì
Vite chỉ bundle chứ không phân tích phạm vi biến. Đã sửa + guard chạy trong `constraints-check.py`.

## 4. Biên giới kiến trúc (Sếp chốt 2026-09-14, bổ sung ADR-006 ngày 2026-09-15)

1. **ERPNext native là SSOT.** Tiền, thuế, cọc, BOM, tồn kho, trạng thái, sinh mã đều do DocType/controller native tính. API `vanphat_portal.api.*` chỉ là façade mỏng: nhận payload → gọi DocType native → trả JSON sạch. Một ngữ nghĩa tiền + một công thức HOLD cho mọi màn (ADR-006): `product_total = net_total − cylinder_total` (chưa VAT, không trục); HOLD ⟺ Trả trước AND `0 < advance_paid < required_deposit`.
2. **Portal sở hữu ~6 luồng nghiệp vụ** (báo giá, tạo đơn, duyệt cọc, xưởng, giao hàng, tra cứu). **Desk giữ config + master data + mọi thứ chưa thiết kế.**
3. **Quyền native (Sếp chốt 2026-09-15, ma trận trong `backend-native-api-spec.md` §6):** 1 user kiêm nhiệm
   nhiều role; Desk (Role Permission Manager + User Permissions) giữ "ai được làm gì", code chỉ gác
   cổng bằng `frappe.get_roles()` (role hành động) + `frappe.has_permission()` (DocType/doc-level).
   Mọi `@frappe.whitelist()` phải gated — `api_ungated = 0`, cấm `ignore_permissions` ở API người dùng. Không cố thay Desk toàn bộ: UI tự làm mất khả năng custom form, còn Desk v16 vẫn đang được Frappe phát triển song song (nguồn: [frappe.io/framework/version-16](https://frappe.io/framework/version-16), [thảo luận với founder Frappe 11/2025](https://discuss.frappe.io/t/frappe-crm-ui-v-s-desk-ui/156477)).
3. **Lớp vỏ không logic.** Client chỉ: thu thập input → gọi API (`api()` duy nhất, kể cả upload FormData) → hiển thị. Validate client chỉ để UX tức thì; tính hợp lệ nghiệp vụ do server quyết. Đọc envelope `page_result`, không đỡ mảng trần. Không math tiền/qty, không fallback số thương mại, không identity/config cứng.
4. **Kết quả mutate chỉ lấy từ response server.** Không tự set `order_state`/`completed_qty`/`is_hold` ở client; không báo thành công khi API trả lỗi. Mọi list API trả envelope thống nhất (ADR-006).
5. **Frontend stack đang khoá tạm:** Vue 3.5 + Vite 7 + vue-router 4 + Tailwind **v3** + `frappe-ui` ghim exact. Tailwind v4 chưa được: preset của frappe-ui v1 là v3. Đổi framework/UI library phải có số đo POC và Sếp duyệt. **Không cài Frappe Studio lên production** cho tới khi đủ 3 điều kiện mở lại (ADR-005 §5). **Không dùng `www.list` / portal list native cho Sales Order** cho tới khi frappe#42640 được vá (ADR-005 §4).

## 5. Exceptions

| ID | Luật | Đường dẫn | Lý do | Người | Hết hạn |
|---|---|---|---|---|---|
| W2 | `api_ungated` | `bao_gia.get_boot` | Chỉ trả session user + CSRF token của chính người đang đăng nhập | em | 2026-12-14 |

Ngoại lệ phải có người chịu trách nhiệm và ngày hết hạn. Không có ngoại lệ vô danh.
