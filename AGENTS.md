# AGENTS.md — Van Phat Packaging ERP & Portal

ERPNext v16 native backend + thin Vue cockpit for flexible-packaging factory (quotes, orders, deposits, catalog).

## Rules

1. Read `CONSTRAINTS.md` before writing code. Never weaken it to pass.
2. Respond in Vietnamese. User = `Sếp`, self = `em`. Report = numbers + decisions + blockers.
3. Ask vs decide: context còn mờ → STOP, hỏi Sếp qua `ask_user_question` (never plain text). Chỉ hỏi business flow logic (tiền, quyền, xóa dữ liệu, flow mới). Kỹ thuật chi tiết → tự quyết: research best practice cộng đồng trước, theo backend-native + config-native, visual-custom. Stack tech không đổi trừ khi Sếp yêu cầu. Đề xuất stack phải kèm research + trade-off, chờ Sếp chốt.
4. Disagreement = stop and clarify. Context còn mờ trong hướng của Sếp (nhất là tiền/quyền/dữ liệu) → halt, state risk + evidence, propose alternative, wait for Sếp's call. No silent compliance, no performative agreement. Kỹ thuật chi tiết đã research → tự quyết + ghi log, không hỏi.
5. Never invent schema — see `docs/DATA.md`. Never read `archive/`.
6. Load matching skill via `skill` tool before acting (map below). Never apply from memory. Skills under `.agents/skills/*` are upstream-sealed (never edit); repo custom lives in `.agents/references/vanphat-overlay.md` (load alongside the skill when it names project conventions).
7. Slices ~30min / 1–3 files. Parallelize independent work (background subagents/jobs); synthesize at end.
8. Context hygiene: checkpoint + continue. At ~75% context: commit WIP, summarize (decisions kept, journeys dropped), continue without asking.
9. Finish what you start: runs, verified, failures fixed.

## Skill map (load before acting — 12 skills đủ cho repo này, cắt từ 33 ngày 2026-09-16)

| Task | Skill |
|---|---|
| Whitelisted API, permissions, endpoints | `api-development` |
| DocType/bench/site/hooks/jobs | `frappe-app-dev` |
| Any `.vue`/router/Vite/dialogs/a11y | `vue-best-practices` |
| Quote/BOM/packaging math | `packaging-calculation-engine` |
| Logic/bugfix/behavior change | `test-driven-development` |
| Review trước merge (bắt buộc) | `code-review-and-quality` + `quality-code-review` + `.agents/references/vanphat-overlay.md` |
| Commit, branch, PR, version | `git-workflow-and-versioning` |
| CI/CD, deploy, pipeline | `ci-cd-and-automation` |
| Browser test vs prod | `browser-testing-with-devtools` |
| Đơn giản hóa code | `code-simplification` |
| Viết ADR, docs quyết định | `documentation-and-adrs` |
| Debug sâu, root-cause | `debugging-and-error-recovery` |

Ngoài map: khi task không khớp 12 dòng trên (define/plan/build/ship lạ, bảo mật,
hiệu năng, observability, migration...) → **load `using-agent-skills` trước** để
chain chọn skill đúng theo phase, rồi load skill nó chỉ. Không tự đoán skill ngoài map.

## Confusion protocol (context mờ → dừng, không đoán mò)

- Doc vs code conflict → surface with file:line evidence, propose, wait.
- Missing requirement → check code precedent; none → STOP and ask with options.
- Multi-step task → 1-line plan first (`1. ... 2. ... → executing unless redirected`).

## Triple rule (non-negotiable)

1. **Backend native** — money, tax, deposit, BOM, stock, status, naming computed by ERPNext DocTypes. `vanphat_portal.api.*` = thin facade, no duplicated logic. Details: `docs/API.md`.
2. **Config native** — options, defaults, labels, order, visibility from Custom Field / Property Setter / DocType Layout / Item Group tree / `min_order_qty` / Payment Terms / Credit Limit / Tax Template. Desk change reaches UI with **no rebuild**.
3. **Visual custom only** — layout, Modal, Drawer, color, click-select, friendly flow language. No money/tax/status/config/option lists in visual code. Details: `docs/UI.md`.

## Map (progressive disclosure — load on touch only)

| Touch | Load |
|---|---|
| API file (`api/*.py`) | `docs/API.md` |
| Vue file (`frontend/src/**`) | `docs/UI.md` |
| Data field, naming, DocType | `docs/DATA.md` |
| Infra, deploy, bench, import | `docs/SETUP.md` |
| Why a decision was made | `docs/DECISIONS.md` |
| Backlog, priorities | `docs/BACKLOG.md` |

## Working method

- Feature: spec (`docs/BACKLOG.md`) → thin slices + TDD → review (bắt buộc, theo tiers ở `CONSTRAINTS.md`) → ship.
- Trivial (typo, one file): implement directly, minimal verify + self-review Floor 11.
- No-merge-without-review: mọi diff chạm `apps/` hoặc `data/clean-data/` phải có review checklist (Approve/Request changes) trước commit cuối slice. Tier 1 (≤100 lines, không tiền/quyền/cọc): 1 agent. Tier 2 (còn lại): 3-agent + `scripts/review-gate.sh` (chi tiết tiers ở `CONSTRAINTS.md`).
- Code-first SSOT: code + tests + git history are truth. Docs hold intent + deltas only — never duplicate numbers/lists the code already states. Doc vs code conflict → code wins; surface it, fix the doc.

## Essentials (tóm tắt 3 dòng — chi tiết trong docs)

- Frontend: Vue 3 `<script setup>` + native `<dialog>` + vue-sonner, fetch chỉ via `api()` (`useSession.js`). Không logic tiền/số/config ở client. Chi tiết: `docs/UI.md`.
- Backend: lists trả `page_result`; một ngữ nghĩa tiền + một luật HOLD. Chi tiết: `docs/API.md`.
- UI: `custom_alias` trong bảng, header 1 dòng, trạng thái chữ Việt + màu, số căn phải `tabular-nums`.

## Never (review tay + CI native)

- `CONSTRAINTS.md` Floor 11 luật: mock ID, guest API, `get_all` có phân quyền, `v-html`, suppression, secret, stub, raw `fetch`, user/config hardcode, mock server.
- Business cấm: local-only mutation, hand-rolled money/tax, hardcoded commercial constants, raw-SQL prod mutation, `openpyxl`, `ignore_permissions` ở user API.
- Mock server / mock CSRF / mock API / local JSON preview (`serve-portal.mjs` đã xóa 2026-09-15). Browser test chỉ chạy vs prod: real API + real CSRF + real login; chứng từ test prefix `TEST-` và cleanup sau test (`scripts/test-browser-portal.mjs`). Không đối soát tiền/thuế/cọc bằng số preview local. Luồng duy nhất: build local → test pass → deploy prod (không bench staging).
- `git push` without explicit order. Commit atomically, conventional prefixes. Local commit khuyến khích (save points).

## Verify (native, guard = script có chủ chạy bằng runtime chuẩn)

- `python3 -m unittest discover -s apps/vanphat_portal/tests -p "test_*.py"`
- `node apps/vanphat_portal/frontend/check-composables.mjs` (runtime scope composable)
- `node apps/vanphat_portal/frontend/check-ui.mjs` (Design System token)
- `bash scripts/budget-gate.sh` (after build)
