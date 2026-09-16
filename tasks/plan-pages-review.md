# Implementation Plan: Fix review 3 pages portal (Quotes/Orders/Catalog)

## Overview
Fix 5 high + 8 medium từ review Tier 2 (3-agent, 2026-09-16): tiền/config-native lọt ra client (QuotesView), keyboard a11y, debounce/abort race, tách mega-component >500L. Mỗi slice TDD + Tier review + gates xanh. Không đụng backend trừ S2 (cần Sếp chốt nguồn margin).

## Architecture Decisions
- Tiền/config: mọi số thương mại + option/default từ server (`docs/API.md`); client chỉ render, fallback truthful (0/empty), không tự cộng.
- Keyboard: row clickable = `tabindex=0 role=button` + Enter/Space (theo BaseDrawer pattern).
- Search race: AbortController theo mẫu `useCatalogData.js:61`, không debounce thủ công trần.
- Tách component: view chỉ composition surface, logic vào composable (theo CatalogView mẫu).

## Task List (todo chi tiết: tasks/todo-pages-review.md)

### Phase 1 — High tiền/config (S1, S2)
- S1: QuotesView grand fallback + figures truthful.
- S2: target_margin + step1Data defaults → config-native (RESEARCH backend trước; nguồn margin chờ Sếp chốt).

### Checkpoint 1
- unittest + 2 FE guard + Floor-11 grep + review-gate xanh (số lượng test xem code — không ghi số cứng).

### Phase 2 — a11y + perf (S3, S4, S5)
- S3: keyboard row 3 views + aria-label nút ✕ + 2 nav chết (hide/khóa + title).
- S4: debounce onItemsChanged + Abort search Orders/Quotes + clearTimeout unmount.
- S5: badge Quotes total + bỏ filter client trùng + xóa dead code + fix double-fetch ?tab=.

### Checkpoint 2
- Như trên + test tay keyboard/search trên prod (build local → test pass → deploy prod; không bench staging).

### Phase 3 — kiến trúc (S6, S7, S8)
- S6: keep-alive max=3 + onActivated refresh (hoặc bỏ comment hứa) + bỏ :key remount + Suspense fallback.
- S7: orderStatus fallback gọn + route SSOT + query.order validate + api() chặn URL tuyệt đối + artwork :src scheme.
- S8a/b/c: tách QuotesView/OrdersView + composable useCockpitPagination chung.

### Checkpoint: Complete
- Quotes/Orders ≤500L (hoặc ADR ghi nợ), gates xanh, Sếp duyệt.

## Risks and Mitigations
| Risk | Impact | Mitigation |
| S2 nguồn margin sai ý GĐ | High (tiền) | Research backend, hỏi Sếp trước khi code |
| Tách component vỡ behavior | Med | Mỗi slice 1 view, test tay prod (`TEST-` + cleanup), không gộp slice |
| VITEST blocked (fe_test_files=0) | Med | Verify bằng guard + review + test tay, ghi nợ backlog |

## Open Questions
- S2: target_margin + step1Data defaults lấy từ endpoint nào (get_print_config mở rộng hay backend default)? → hỏi Sếp sau research.
- 2 nav chết (Tổng quan/Sản xuất): hide hay disabled + "Sắp ra mắt"? → mặc định disabled + title, Sếp đổi ý thì bảo em.
