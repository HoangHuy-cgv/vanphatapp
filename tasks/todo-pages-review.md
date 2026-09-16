# Todo: Fix review 3 pages portal (plan: tasks/plan-pages-review.md)

## S1: QuotesView grand fallback + figures truthful (High)
**Description:** Bỏ `grand = grand_total || sub` che invariant; grand lấy server nguyên, figures khởi tạo truthful.
**Acceptance criteria:**
- [ ] `QuotesView.vue` không còn fallback `|| sub` cho grand_total.
- [ ] figures rỗng/truthful khi server chưa trả (không số bịa).
- [ ] Không đổi logic backend.
**Verification:**
- [ ] Tests: `python3 -m unittest discover -s apps/vanphat_portal/tests -p "test_*.py"` xanh.
- [ ] Guard: `node apps/vanphat_portal/frontend/check-composables.mjs` + `node apps/vanphat_portal/frontend/check-ui.mjs` PASS.
- [ ] Gate: `bash scripts/review-gate.sh` PASS + Floor-11 grep CI xanh.
- [ ] Manual: báo giá preview hiện đúng grand server / trống khi pending.
**Dependencies:** None
**Files:** `apps/vanphat_portal/frontend/src/views/QuotesView.vue`
**Scope:** S (1 file)

## S2: target_margin + step1Data defaults → config-native (High, RESEARCH trước)
**Description:** Bỏ `target_margin: 0.30` + defaults cứng (Túi đáy đứng/Có vòi/In trục/Đã có trục) sang nguồn server; DB trống thì truthful empty.
**Acceptance criteria:**
- [ ] Không còn số/option cứng trong `QuotesView.vue` (margin, product_type, accessory, print_type, cylinder_status).
- [ ] Nguồn server rõ (endpoint/config) + truthful empty khi DB trống.
- [ ] Hỏi Sếp chốt nguồn margin trước khi code.
**Verification:** như S1 + review Tier 2 (chạm tiền/config).
**Dependencies:** S1
**Files:** `apps/vanphat_portal/frontend/src/views/QuotesView.vue` (+ backend nếu cần endpoint mới — hỏi Sếp)
**Scope:** M (1-3 files)

## S3: keyboard row + aria + nav chết (High a11y)
**Description:** `<tr>` clickable 3 views có tabindex/role/keydown; nút ✕ có aria-label; 2 nav chết disabled + title.
**Acceptance criteria:**
- [ ] Enter/Space mở được chi tiết từ keyboard ở 3 views.
- [ ] SR đọc được nút xóa search.
- [ ] Tổng quan/Sản xuất không còn focusable-chết.
**Verification:** như S1 + test tay keyboard prod (`TEST-` + cleanup).
**Dependencies:** None
**Files:** `views/OrdersView.vue`, `views/QuotesView.vue`, `views/CatalogView.vue`, `App.vue`
**Scope:** M (4 files — chia 2 commit: rows trước, nav sau)

## S4: debounce items + Abort search + clear timer (High perf)
**Description:** `onItemsChanged` debounce/coalesce; search Orders/Quotes dùng AbortController theo mẫu useCatalogData; clearTimeout unmount.
**Acceptance criteria:**
- [ ] Sửa dòng dồn dập không bắn 2 API nối tiếp mỗi keystroke.
- [ ] Response cũ không overwrite kết quả mới.
- [ ] Không timer rò sau unmount.
**Verification:** như S1.
**Dependencies:** None
**Files:** `views/QuotesView.vue`, `views/OrdersView.vue`, `composables/useCatalogData.js` (đối chiếu mẫu)
**Scope:** M (2-3 files)

## Checkpoint 1 (sau S1–S4)
- [ ] unittest + 2 FE guard + Floor-11 grep + review-gate xanh.
- [ ] Test tay prod (`TEST-` + cleanup): preview tiền đúng, keyboard mở row, search không race.
- [ ] Review với Sếp trước Phase 3.

## S5: badge/filter/deadcode/double-fetch (Medium)
**Description:** Badge Quotes dùng total; bỏ filter client trùng server; xóa onSendQuotation/onMarkLost; set tab trước khi load (fix double-fetch ?tab=).
**Acceptance criteria:**
- [ ] Badge = total_count, khớp Orders/Catalog.
- [ ] Search 1 lớp duy nhất (server).
- [ ] Không dead code; deep-link ?tab= fetch 1 lần.
**Verification:** như S1.
**Dependencies:** S1
**Files:** `views/QuotesView.vue`, `views/OrdersView.vue`
**Scope:** M (2 files)

## S6: keep-alive + remount + Suspense (Medium)
**Description:** keep-alive max=3 + onActivated refresh (hoặc bỏ comment hứa); bỏ `:key=activeOrderTab` remount; Suspense drawer/modal có fallback.
**Acceptance criteria:**
- [ ] max=3, chuyển tab data tươi (hoặc doc ghi rõ cache).
- [ ] Đổi tab giữ scroll/focus.
- [ ] Chunk chậm có skeleton.
**Verification:** như S1 + test tay chuyển tab.
**Dependencies:** S5
**Files:** `App.vue`, `views/OrdersView.vue`, `views/QuotesView.vue`, `views/CatalogView.vue`
**Scope:** M (4 files — chia 2 commit)

## S7: status/route/query/api-hardening (Medium+low)
**Description:** orderStatus fallback gọn; route SSOT (bỏ parse song song); query.order validate found; api() chặn URL tuyệt đối ngoài origin; artwork :src allowlist scheme.
**Acceptance criteria:**
- [ ] Không duplicate luật HOLD ở client ngoài label/class server.
- [ ] query.order lạ không mở drawer rỗng.
- [ ] api() không gắn CSRF cho cross-origin; :src chỉ http(s)/files/data:image.
**Verification:** như S1 + review Tier 2 (chạm api/).
**Dependencies:** None
**Files:** `views/OrdersView.vue`, `App.vue`, `composables/useSession.js`, `components/DrawerOrderDetail.vue`, `components/ArtworkBox.vue`
**Scope:** M (5 files — chia 2 commit: client-status trước, hardening sau)

## S8a: tách QuotesView ≤500L
**Description:** View chỉ composition surface; form/figures/list vào component + composable.
**Acceptance criteria:**
- [ ] `QuotesView.vue` ≤500L, behavior giữ nguyên.
**Verification:** như S1 + test tay flow báo giá prod (`TEST-` + cleanup).
**Dependencies:** S1–S5
**Files:** `views/QuotesView.vue` + files mới
**Scope:** L (chia nhỏ, tách dần)

## S8b: tách OrdersView ≤500L
**Description:** Tương tự S8a cho OrdersView.
**Acceptance criteria:**
- [ ] `OrdersView.vue` ≤500L, behavior giữ nguyên.
**Verification:** như S1 + test tay flow đơn hàng prod (`TEST-` + cleanup).
**Dependencies:** S5–S7
**Files:** `views/OrdersView.vue` + files mới
**Scope:** L (chia nhỏ, tách dần)

## S8c: composable useCockpitPagination chung
**Description:** Gộp prev/next/goto/keyboard ([ ]) copy-paste 3 nơi.
**Acceptance criteria:**
- [ ] 1 composable dùng chung, 3 nơi gọi.
**Verification:** như S1.
**Dependencies:** S8a, S8b
**Files:** `composables/useCockpitPagination.js` mới + 3 nơi gọi
**Scope:** M

## Checkpoint: Complete
- [ ] Quotes/Orders ≤500L (hoặc ADR ghi nợ).
- [ ] Tất cả gates xanh; Sếp duyệt close goal.
