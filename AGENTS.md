# Van Phat ERP & Portal (vanphatapp) - Agent Operating Directive

## 1. Operating Rules & Role Boundary
- **Language & Persona**: Vietnamese communication with User (`Sếp`). Assistant (`em`) pairs with User. User dictates business rules; Assistant dictates technical architecture and implementation.
- **Git Operations**: Never commit or push unless explicitly requested by User.
- **Database Operations**: Never execute mutating database scripts unless explicitly approved via `"Viết script"` / `"Chạy script"`.
- **Domain Knowledge Autonomy**: Search local context (`data/raw-data/`, `docs/specs/`) and packaging references autonomously before asking User. Master flexible packaging concepts independently: multi-layer film laminations (PET, PA, PE, MPET, AL), thickness (mic/µm), cylinder sets (Rotogravure G-code / Z-code), pouch types (stand-up/Doypack, 3-side seal, side gusset, center seal, 8-side flat bottom), spouts (10mm, 16mm, 22mm), and scrap/loss rates.

## 2. System Architecture & Tech Stack (Strict SSOT)
- **App Target**: Integrated ERP & Commercial Portal for Van Phat Packaging Manufacturing.
- **Architecture Paradigm**: Headless ERP with a thin client presentation shell. Single Source of Truth (SSOT).

### Primary Tech Stack
| Component | Technology | Scope & Responsibilities |
| :--- | :--- | :--- |
| **Backend Core (SSOT)** | **Frappe Framework v16 + ERPNext v16** (Python) | Holds 100% of business logic, packaging math (film consumption, surface density, scrap %), tiered pricing matrices, BOMs, inventory valuation, accounting, RBAC, and whitelisted REST APIs (`vanphat_portal.api`). |
| **Frontend Shell** | **Vue 3 + Frappe UI + Tailwind CSS** (Vite SPA) | Pure presentation shell (`apps/vanphat_portal/frontend/` mounted at `/portal`). Zero business calculations. Renders 5-pouch-type interactive quotation wizard and passes user intents to backend. |
| **Database** | **MariaDB 10.6+** | Single persistent datastore for ERPNext standard doc types and packaging custom fields. |
| **Production Runtime** | **Zero-Node Runtime** | Vite builds static assets to `apps/vanphat_portal/vanphat_portal/public/frontend/`. Served directly by Frappe Nginx / Gunicorn. No Node.js process runs on production. |

### Strict Exclusions
- **Forbidden Stacks**: React, Next.js, Svelte, HTMX, Alpine.js, ad-hoc Jinja apps.
- **Forbidden Libraries**: `openpyxl` is strictly prohibited due to high memory consumption and process stalls. All Excel reading tasks must use `fastexcel` or `python-calamine` (Rust-backed).
- **Forbidden Client-side Logic**: No film consumption calculations, unit pricing tiers, or BOM derivations inside `.vue` or `.js` files. All computations must resolve via backend Python APIs.

## 3. Data SSOT Scope
- **Raw SSOT Sources**: `data/raw-data/` (Excel files: `MÀNG.xlsx`, `TIẾN ĐỘ SẢN XUẤT.xlsx`, `TỔNG HỢP ĐƠN HÀNG ĐÃ CỌC CHƯA GIAO.xlsx`, debt ledgers).
- **Clean Master Datasets**: `data/clean-data/` (`item_master.csv`, `item_spec.csv`, `customer_brand_matrix.csv`).
- **Domain Specifications**: `docs/specs/` (`erpnext-packaging-masterdata-spec.md`, `packaging-calculation-spec.md`).
- **Item Coding Series**: `TP-` (Finished Pouches), `NVL-` (Raw Materials: Film, Resin, Solvents, Spouts), `BTP-` (Laminated Film Rolls), `TRUC-` (Rotogravure Cylinders).
- **Canonical Length UOM**: `m` (meters only; `Mét Dài` is strictly eliminated).

## 4. Consolidated Rules & Operational Policies (Single Source of Truth)

### Rule 1: Headless Presentation Boundary (Strict Presentation Shell)
- **Zero Business Calculations in Client**: Never write film consumption formulas, scrap rate logic, tiered unit pricing, or BOM derivations inside `.vue`, `.js`, or `.ts` files under `apps/vanphat_portal/frontend/`.
- **Backend Resolution Only**: All computations, quotes, and validations must resolve via backend Python APIs (`vanphat_portal.api`).
- **Unidirectional Intent**: Frontend only captures user inputs, dispatches backend API requests via `createResource` / `call()`, and presents returned results.

### Rule 2: Packaging Domain Standards, Coding Series & Canonical Units
- **Standardized Units**: Canonical length is strictly `m` (meters). Never use `Mét Dài`. Film thickness is measured in `mic` ($\mu m$). Currency is strictly `VND`.
- **Item Coding Taxonomy**:
  - `TP-`: Thành phẩm túi (Finished Pouches: Doypack, 3 biên, 4 biên, 8 cạnh, túi lưng).
  - `NVL-`: Nguyên vật liệu thô (Màng nguyên liệu, hạt nhựa, keo ghép, dung môi EA, vòi).
  - `BTP-`: Bán thành phẩm màng ghép cuộn.
  - `TRUC-`: Bộ trục in ống đồng (Rotogravure Cylinders).
- **Physical Law & Compatibility**: PE spouts only weld to PE sealant layer; PP spouts only weld to CPP sealant layer. Cross-welding is strictly prohibited.

### Rule 3: Safe Data Operations, Banned Libraries & Database Policy
- **Strict Prohibition of `openpyxl`**: Processing Excel files (`data/raw-data/`) must strictly use `fastexcel` or `python-calamine` (Rust-backed) to prevent memory exhaustion and process stalls.
- **Controlled Database Mutation**: Never execute mutating database scripts (INSERT, UPDATE, DELETE, ALTER) against MariaDB unless explicitly approved by User with keywords `"Viết script"` or `"Chạy script"`.
- **Zero-Node Production Runtime**: Production environment runs Frappe Nginx / Gunicorn serving the pre-built static Vite bundle (`apps/vanphat_portal/vanphat_portal/public/frontend/` -> `www/portal.html`). No server-side Node.js or PM2 process may run on production.
- **Git Safety**: Never commit or push to Git repositories without explicit User instruction.

### Rule 4: Production Quotation & Batching Directives (SSOT Sếp Chốt)
- **Cylinder Quote Isolation**: Tiền trục in ống đồng là chi phí công cụ khuôn mẫu tính riêng cho đơn hàng đầu (nếu khách chưa có trục). Tuyệt đối KHÔNG gộp tiền trục vào đơn giá 1 túi thành phẩm.
- **2-Lane Wide-web Optimization**: Với các khổ túi vừa/nhỏ ($W \le 360\text{mm}$), xưởng bố trí trục in dài ($750 - 900\text{mm}$) và màng khổ to ($700 - 800\text{mm}$) để chạy 2 con (2 lane). Tăng gấp đôi sản lượng/mét dài, tối ưu tốc độ máy và triệt tiêu nguy cơ cuộn màng bị cắt dở.
- **2-Tier Quotation & Surplus Risk Buffer Strategy**:
  - *Nấc 1 - Tròn cuộn tối ưu (ĐƠN GIÁ TỐT NHẤT)*: Khách đồng ý đặt đủ số lượng tròn cuộn màng ($1.500\text{m}$) để tiêu thụ 100% sản lượng ra máy. Đơn giá túi rẻ nhất do setup máy chia đều cho lô lớn và công ty không chịu rủi ro tồn dư.
  - *Nấc 2 - Đúng số lượng yêu cầu (ĐƠN GIÁ CAO HƠN)*: Khách chỉ lấy đúng số lượng lẻ (ít hơn số túi tròn cuộn), xưởng vẫn bắt buộc chạy trọn cuộn màng. Đơn giá báo cho khách bắt buộc phải **CAO HƠN** để bù đắp định phí setup và rủi ro chi phí màng thừa mà công ty phải ôm nếu khách không bao giờ đặt hàng lại (re-order).
  - *Hiệu ứng đòn bẩy up-sell*: Báo giá song song 2 nấc giúp Sale chỉ cho khách thấy chỉ cần thêm một khoản tiền nhỏ là lấy được trọn vẹn số túi của cả cuộn với đơn giá rẻ hơn nhiều.


