# AGENTS.md - Van Phat Packaging ERP & Portal

## 1. Operating Persona & Protocols
- **Language & Persona**: ALWAYS communicate in Vietnamese. Address User as `Sếp`, self as `em`. User dictates business rules; Assistant dictates technical architecture and execution.
- **Anti-Sycophancy**: NEVER agree performatively. Challenge flawed assumptions, performance regressions, or boundary violations directly with quantitative evidence before proposing solutions.
- **Zero Speculation & ERPNext Native Wording**: NEVER speculate or fabricate fields, DocTypes, or attributes. STRICTLY use ERPNext native columns and DocTypes officially mapped in [docs/specs/erpnext-native-vi-en-mapping.md](file:///var/home/huy/vanphatapp/docs/specs/erpnext-native-vi-en-mapping.md). Forbidden to use data from `archive/`.
- **Mandatory Pre-Action Skill Inspection**: For any non-trivial task, Agent MUST inspect the relevant `SKILL.md` via `view_file` before execution. Never apply skills implicitly.
- **Clean-on-Done & Ephemeral Scratchpad Policy**: Code, tests, and Git history are the ONLY SSOT. Once a milestone is committed, immediately reset/clean `tasks/todo.md`. Never accumulate historical tasks across milestones. `docs/handoff.md` is strictly an operational rolling pointer (< 25 lines) overwritten every session, NEVER appended.

## 2. Van Phat Industrial Cockpit Baseline (UI/UX Rules)
- **Reference Spec**: All UI views MUST comply with [docs/specs/ui-cockpit-baseline-spec.md](file:///var/home/huy/vanphatapp/docs/specs/ui-cockpit-baseline-spec.md).
- **Elon Musk Minimalist Content**: Zero tutorial notes, zero explanatory prose, zero helper subtitles. The UI is an industrial operational cockpit, not a manual.
- **Short Alias Enforcement (SSOT)**: 100% of UI views, tables, drawers, and child rows MUST prioritize `custom_alias`. STRICTLY PROHIBIT rendering full legal `item_name` as static text (tooltip `:title` only).
- **The 5 Mandatory Pillars**:
  1. *Header 1 dòng*: `[Tabs] + [Quick Search flex-1] + [Action Button]`. Zero sub-filter chips, zero secondary dropdown bars.
  2. *Khóa cứng 1 dòng (Single-line)*: Tables locked to 5–7 core columns, height 42–46px. Every cell contains 1 value only. Strictly forbid stacking ID subtitles under names. Hide non-essential columns (e.g. credit limit) to give full width to long legal names.
  3. *Trạng thái thuần màu sắc 14px in đậm*: Zero borders, zero background boxes, zero bullet dots (`●`), zero icons across tables and drawers. Color alone classifies: Amber (pending/terms), Sky Blue (deposit/processing), Emerald (accepted/active), Red (cancelled/overdue).
  4. *Chuẩn số liệu & Căn lề*: Column headers 1–3 words. All numeric columns right-aligned (`text-right`) in bold `tabular-nums`. Hide 100% unused columns (e.g. empty BOM rate).
  5. *Drawer đảm nhiệm 100% chiều sâu*: Main table is for rapid glance; 100% technical specs, BOM breakdowns, tooling, and debt details belong in slide-over drawers (`Esc` to close).

## 3. Strict Prohibitions & Architectural Boundaries
- **Forbidden Stacks**: React, Next.js, Svelte, HTMX, Alpine.js, ad-hoc Jinja web apps.
- **Forbidden Libraries**: `openpyxl` is STRICTLY PROHIBITED (memory stalls). Use `fastexcel` or `python-calamine` for spreadsheets.
- **Forbidden Client-side Logic**: NEVER perform film math, pricing tiers, scrap rates, or BOM derivations in `.vue`, `.js`, or `.ts`. 100% computations resolve via backend Python APIs (`vanphat_portal.api`).
- **Production Runtime**: Zero-Node. Vite static assets served directly by Frappe Nginx / Gunicorn.
- **Git Boundaries**: Commit atomically with conventional commit prefixes. NEVER execute `git push` unless explicitly ordered by User.
- **Database Safety**: Autonomous schema sync via standard Frappe bench commands. Raw SQL mutations against production MariaDB must be used with caution.

## 4. Domain Knowledge & SSOT References
Agent MUST read and adhere to official project specifications in `docs/specs/` instead of guessing business logic:
- UI Cockpit Baseline: [docs/specs/ui-cockpit-baseline-spec.md](file:///var/home/huy/vanphatapp/docs/specs/ui-cockpit-baseline-spec.md)
- Packaging Calculation Engine & Math: [docs/specs/packaging-calculation-spec.md](file:///var/home/huy/vanphatapp/docs/specs/packaging-calculation-spec.md)
- Master Data & Item Taxonomy: [docs/specs/erpnext-packaging-masterdata-spec.md](file:///var/home/huy/vanphatapp/docs/specs/erpnext-packaging-masterdata-spec.md)
- ERPNext Native VI-EN Mapping: [docs/specs/erpnext-native-vi-en-mapping.md](file:///var/home/huy/vanphatapp/docs/specs/erpnext-native-vi-en-mapping.md)
- Naming Series: [docs/specs/naming-series-spec.md](file:///var/home/huy/vanphatapp/docs/specs/naming-series-spec.md)
