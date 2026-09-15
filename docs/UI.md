# UI (`apps/vanphat_portal/frontend/src/`)

Stack: Vue 3.5 `<script setup>`, hash router (3 lazy routes: Orders/Quotes/Catalog, `keep-alive` read lists), native `<dialog>` (`BaseModal`, `BaseDrawer`, `ConfirmDialog`) + `vue-sonner`, Tailwind v3, Vite 7. Budget: entry gzip warn 170KB / fail 300KB (now 52KB).

## Rules

- HTTP only via `api()` in `composables/useSession.js` (CSRF + toast + AbortSignal; FormData without manual `Content-Type`). No raw `fetch`.
- Read `page_result` envelopes. No client money/qty math (`Intl.NumberFormat('vi-VN')` format only). No local mutation after POST — re-read server. No hardcoded identity/config/defaults.
- Search debounce 250–300ms + abort stale; render latest only.
- ≤8 options → click-select buttons (`role=radiogroup`/`radio`, keyboard, ≥44px touch). Dynamic lists (customer/supplier/item) → type-to-filter search-select (~50 rows max).
- Split components past 500 lines (warn 300).

## Cockpit baseline

- Tables show `custom_alias` (codes in tooltips only). 1-line header `[Tabs]+[Search]+[Action]`; 5–7 single-line cols (42–46px rows).
- Status = Vietnamese text + color (never color alone), 14px/600, contrast ≥ 4.5:1, no `#64748b` on dark. Numbers right-aligned bold `tabular-nums`.
- Depth in drawers: native `<dialog>` via `BaseDrawer` (Esc/backdrop close, focus restored). Center modals via `BaseModal` (native `<dialog>` + `showModal()`, backdrop `blur(2px)`). Confirm/alert via `useConfirmDialog` (callback-based: `dialog.confirm({ title, message, onConfirm })` — NOT Promise) + `ConfirmDialog` (`role="alertdialog"`). Toast notifications via `useToast` + `vue-sonner@2.0.9` (single `<Toaster>` in `App.vue`). No `tabindex` on `<dialog>`. Form inputs carry `id` + `name` + `aria-label`.
- Zero-training: button labels self-explain; follow raw-data flow order; hide empty steps.
- DoD: single-line, no redundant subtitles, text+color status, 1-row header, right numbers, clean cols, drawer integration, Inter only, zero client logic, a11y floor, responsive (1024/768/320), truthful feedback, click-select, config-native, raw-data flow.

## Guard

`check-composables.mjs` imports + instantiates every composable in Node (catches undefined-identifier bugs `vite build` misses). Must stay green; wired into `constraints-check.py`.
