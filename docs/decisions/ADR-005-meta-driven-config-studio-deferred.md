# ADR-005: Config native là SSOT của giao diện — cockpit chỉ viết visual; hoãn Frappe Studio

## Status
Accepted (2026-09-14 — em quyết định theo ủy quyền của Sếp sau research best practice; toàn bộ bằng chứng viện dẫn đã xác minh lại cùng ngày, xem §Xác minh)

## Date
2026-09-14

## Ngữ cảnh
Sếp chốt tiêu chí kiến trúc: **1) dùng ERPNext native cho backend, 2) config native, 3) phần custom
duy nhất được phép viết là visual UI/UX** cho các page tối giản (báo giá, danh mục) — với 3 ràng buộc UX:
tối giản để **không phải đào tạo**, visual **tuân thủ flow raw-data**, và chọn bằng **click chọn**
như Modal 1 **thay vì dropdown**.

Rà soát tìm được 4 tầng "config native" thật:
- **DocType Layout** (production-ready, docs 03/06/2026): nhiều form view cho cùng DocType, override
  `label/hidden/reqd/read_only/depends_on/default/in_list_view/in_standard_filter`, tự chuyển theo
  `Condition`, có child-table layout, gắn được vào workspace, ship qua fixtures.
- **Web Form / portal list** (native, no-code): form + list view, multi-step, client script, custom CSS,
  filter động xử lý ở server.
- **v16 native**: Data Masking theo role, Workspace/Desktop Icon, Website Theme (SCSS).
- **Frappe Studio**: visual builder đúng tiêu chí nhất, nhưng repo ghi *"very early development stage…
  Not recommended for production use yet"*; **0 release**; docs chỉ 1 trang; issue cơ bản còn mở
  (current user #94, File Uploader #127, default value #128); **#225 chưa lên frappe-ui v1**; và trên
  production **chỉ chạy, không sửa được** (phải có dev bench + build lại).

Đồng thời phát hiện lỗ hổng đang mở [frappe#42640](https://github.com/frappe/frappe/issues/42640)
(08/09/2026, chưa ai nhận): portal list `/api/method/frappe.www.list.get` trả full doc **lộ field
permlevel** (reproduce trên v15.118.0 và develop/v16), và `read` ⇒ `print` (user `print=0` vẫn xem
được full print page). Tức "native = an toàn" là giả định sai.

## Quyết định

1. **Config native là SSOT của giao diện.** Field, label, thứ tự, bắt buộc, ẩn/hiện, giá trị mặc định,
   quyền, mask, branding, điều hướng **phải** đến từ: Custom Field / Property Setter (vào thẳng meta),
   **DocType Layout** (đọc thêm 1 query, cache TTL 300s, không nhân bản config), Data Masking, Website Theme.
   Cái gì sửa được trong Desk thì **cấm** viết vào Vue.
2. **Code custom chỉ còn ở tầng visual**: bố cục cockpit, Modal, Drawer, màu, chọn-nhanh. Không chứa
   tiền/thuế/trạng thái/cấu hình/danh sách lựa chọn.
3. **Giữ `frappe-ui` ghim exact `1.0.0-beta.64`** (ADR-003 vẫn hiệu lực). Từ chối đổi sang shadcn-vue:
   frappe-ui vốn dựng trên Reka UI nên không nâng cấp a11y, chỉ tăng khối lượng viết lại. POC bỏ
   frappe-ui (nhánh `poc/no-frappe-ui`, giảm 60% gzip) được giữ làm phương án dự phòng, **không** triển khai.
4. **Không dùng `www.list` / portal list native cho Sales Order** trên site này cho tới khi frappe#42640
   được vá: rủi ro lộ field permlevel ngoài tầm kiểm soát của mình.
5. **Hoãn Frappe Studio**, không cài production. Điều kiện mở lại (đủ cả 3): (a) có release gắn tag +
   đường production được tài liệu hoá (không chỉ "exports run"), (b) đã lên frappe-ui v1, (c) tài liệu
   vượt quá 1 trang giới thiệu. Việc nhúng **custom Vue component** trong Studio là điểm cộng: component
   visual viết theo ADR này dùng lại được, nên hướng meta-driven không bị bỏ đi.
6. **Mọi Custom Field mới phải kèm ADR + entry trong `docs/specs/erpnext-native-vi-en-mapping.md`**
   (theo AGENTS.md), và ưu tiên field native đã có (`custom_print_tech`, `custom_accessory_spec`).

## Hệ quả
- Phải rút config đang cứng trong code ra native. Danh sách đã kiểm chứng: danh sách vật liệu màng
  (`DrawerStep2Director.vue:59-120` — mỗi vật liệu là 1 khối template viết tay), mặc định vật liệu
  (`useStep2DirectorForm.js:21`), loại sản phẩm (`ModalCreateOrder.vue:51-52`), kiểu in/van
  (`ModalStep1Sale.vue:117`), `qty` mặc định 5000/100 và nhóm mặc định (`useCreateOrderForm.js:85,100,226,278`).
- Cockpit cần 1 lớp đọc meta + merge DocType Layout, cache theo user/role; thêm 1 nguồn cache key phải
  nằm trong invalidation hiện có (`doc_events`).
- Người dùng cuối đổi field/label/ẩn-hiện/quyền trong Desk **không cần build lại** — đây là tiêu chí
  nghiệm thu của ADR này.
- Studio phải được rà lại định kỳ; ghi vào `tasks/plan.md` để không quên.

## Phương án đã cân nhắc và loại
- **Nhúng thẳng Desk v16 + DocType Layout cho mọi màn**: native nhất nhưng UX bị trần Desk, trái yêu cầu
  visual tối giản của Sếp.
- **Dùng portal list / Web Form native cho danh sách đơn**: loại vì frappe#42640 (lộ field permlevel) +
  visual generic không đạt yêu cầu click-chọn/không-đào-tạo.
- **Đổi sang shadcn-vue**: loại (xem mục 3).
- **Đặt cược vào Frappe Studio ngay**: loại (xem mục 5).

## Xác minh bằng chứng (2026-09-14, trước khi chốt)

- **frappe#42640 còn Open, không assignee/label/milestone**, mở bởi Mahmoud-Soliman10 ngày 2026-09-08,
  reproduce trên v15.118.0 và develop (v16) tại commit `01efd01`. Cơ chế rò rỉ: `www/portal.py:75`
  thay mỗi dòng kết quả bằng `frappe.get_doc()` full document không lọc; `list_view_fields`
  (`portal.py:68`) chọn field `in_list_view` không kiểm tra permlevel; `row_template.html` in
  `doc.get(df.fieldname)` và serialize vào `raw_result` (`portal.py:88`). Phạm vi khẳng định: hàng
  (row set) vẫn đúng vì `frappe.get_list` áp role/User Permission/sharing/`if_owner`; cái rò là
  **giá trị field + in ấn**, không phải tập hàng.
- **Frappe Studio**: repo 279★/98 fork, nhánh `develop` (default), 0 release (API releases trả về `[]`),
  docs Studio chỉ 1 trang intro (cập nhật 2026-01-06). README cảnh báo production chỉ-run-không-sửa.
  Issue còn mở đúng như viện dẫn: current user #94 (2025-08-27), File Uploader #127 (2025-11-07),
  default value #128 (2025-11-10), single-tracking frappe-ui 1.0.0 #225 (netchampfaris, 2026-08-07,
  pin đang ở `1.0.0-beta.25`). Thêm kiểm chứng cùng ngày: các issue nền tảng (#26 prop controls,
  #52 session data/scripts on load, #68 `frappe.call()`/`frappe.boot`, #84 multi-events/component)
  vẫn Open từ 03–06/2025.
- **DocType Layout** (docs cập nhật 2026-06-03): đúng như viện dẫn — nhiều form view cho cùng một DocType,
  override `label/hidden/reqd/read_only/bold/allow_in_quick_entry/in_list_view/in_standard_filter/
  default/description/depends_on/mandatory_depends_on/read_only_depends_on`, chuyển layout theo
  `Condition` trên trạng thái document, layout kế thừa (`Based On`), chốt chuẩn (`Is Standard` export
  JSON theo module). Scope cứng: **chỉ áp cho Desk form view** — cockpit vẫn phải tự đọc meta + merge.
- **Config cứng trong Vue** (source, đọc trực tiếp 2026-09-14): `DrawerStep2Director.vue:59-62,117-120`
  template viết tay từng vật liệu (`OPP`, `PE sữa`); `useStep2DirectorForm.js:21` default vật liệu;
  `ModalCreateOrder.vue:49-52` 4 `<option>` nhóm sản phẩm; `ModalStep1Sale.vue:117-134`
  print_type (`In trục` default dòng 292); `useCreateOrderForm.js:85,100,226,278` nhóm và `qty`
  mặc định (`Túi màng ghép`/5000, `Túi màng đơn`→100). Field native đã tồn tại để thay thế:
  `custom_print_tech`/`custom_accessory_spec` có trong `fixtures/custom_field.json:130-146` và
  `api/item.py:51-52` đã select.
- **Quy mô production (POC `poc/no-frappe-ui`, đã đo)**: entry JS 145→49 kB gzip (-66%),
  CSS 54→6 kB gzip (-89%), tổng js+css 241→96 kB gzip (-60%).
- Giới hạn bằng chứng: không có bench/site thật để kiểm thử Studio, DocType Layout hay issue #42640
  ở runtime; tất cả xác minh trên là đọc source/docs/API công khai + code repo. Cần bench staging
  trước khi triển khai (plan item 6).
