# ADR-007: Retire frappe-ui; adopt pure native `<dialog>` (`BaseModal` + `BaseDrawer`) & `vue-sonner` toast

## Status
Accepted (2026-09-15 — Sếp approved; supersedes ADR-003 modal/toast part, retains drawer part)

## Date
2026-09-15

## Context
- `ADR-003` adopted `frappe-ui` for modals (`Dialog`) and toast (`toast`), while keeping drawers on native `<dialog>` (`BaseDrawer`).
- In practice, `frappe-ui` is pinned at `1.0.0-beta.64` with breaking changes across beta tags (upstream migration guide lists silent breaks: Dialog `options` blob → flat props, `v-model` → `v-model:open`, slot renames — see `ui.frappe.io/docs/migration`), sparse docs, and 75 transitive dependencies (TipTap editor family, CodeMirror, ECharts, `highlight.js`, `dompurify`, `reka-ui`...) while the portal only uses `Dialog` + `toast` in 4 places (`App.vue`, `ModalCreateOrder`, `ModalStep1Sale`, `useToast.js`).
- Wrapping custom cockpit modals inside `frappe-ui/Dialog` risks Reka UI accessibility console warnings (`DialogContent requires a DialogTitle`) because `frappe-ui` forces its own internal opinionated layout.
- The user instructed to choose the most optimal and durable (bền bỉ) architecture for the long term.

## Decision
1. **Retire `frappe-ui` entirely**: remove `frappe-ui` dependency, `frappeui/vite` plugin, and Tailwind preset (`frappe-ui/tailwind`). Tailwind v3 runs standalone.
2. **Pure native `<dialog>` for all overlays**:
   - Drawers: `BaseDrawer.vue` (slide-over right, `min(680px, 100vw)`, native `<dialog>`).
   - Modals: `BaseModal.vue` (center modal, native `<dialog>`).
   - Free benefits: top-layer, native backdrop (`blur(2px)`), native `Esc` to close, native inert background, focus restore on close. 0 KB external bundle weight.
3. **Toast**: use `vue-sonner@2.0.9` directly (zero-dep, ~10KB gzip lib + CSS; `frappe-ui` itself depends on it — this removes one wrapper layer, not a new tech). Single `<Toaster theme="dark" position="top-right" rich-colors />` in `App.vue`; callers use `useToast`/`toast` contract unchanged.
4. **Confirm / Prompt**: `useConfirmDialog.js` + `ConfirmDialog.vue` (native `<dialog>` via `BaseModal`, `role="alertdialog"`). Contract is **callback-based** (same shape as `frappe-ui/dialog`: `dialog.confirm({ title, message, confirmLabel, cancelLabel, onConfirm })`) — NOT Promise-based. Single Step1→Step2 contract is `submit` event with form payload.

## Alternatives Considered

### Keep frappe-ui beta.64
- Pros: Reka-built a11y primitives for free, fast dev.
- Cons: beta churn + silent-break migration surface, 75 transitive deps for 2 used components, measured entry gzip 142KB.
- Rejected: risk/weight disproportionate to usage.

### Native 100%, self-written toast (zero external UI dep)
- Pros: ~45KB entry, zero upstream risk.
- Cons: rewrite swipe-animation + richColors + stacked toasts (~1 slice).
- Rejected for now: kept as fallback if `vue-sonner` goes unmaintained (single maintainer). `useToast` wrapper keeps the swap one-file.

### Headless primitive (Reka UI directly)
- Pros: best a11y (focus-trap, labelled-by built in).
- Cons: heaviest of the native options, overkill for modal/drawer/toast/confirm only.
- Rejected: native `<dialog>` covers the need at 0 KB.

## Consequences
- Measured entry gzip 142KB → 52KB (budget-gate warn 170 / fail 300). Baseline updated.
- Full code ownership: UI never breaks on upstream beta bumps.
- No `DialogContent`/`DialogTitle` console warnings (no Reka wrapper left).
- `ConfirmDialog` owns its a11y: `role="alertdialog"`, labelled title/message, labelled prompt input, `aria-label` close button, autofocus input. No focus-trap yet — acceptable for single-action confirms; revisit if multi-field prompts appear.
