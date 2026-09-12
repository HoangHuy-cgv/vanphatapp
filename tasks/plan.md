# Implementation Plan: Code Simplification & Cleanup (Login, Báo Giá, Modal 1, Drawer 2)

## Overview
Refactor and simplify 4 key frontend components/pages to eliminate dead code, reduce cognitive complexity, streamline CSS bloat, and strictly enforce the zero-client-business-logic boundary (SSOT) while preserving 100% exact visual layout and functional behavior.

## Scope of Changes
1. `apps/vanphat_portal/vanphat_portal/www/login.html`: Eliminate brittle JS layout hacks (`alignWithTitle` timers, repeated `enforceConsistentFont` timers), consolidate autofill CSS, and modernize login submission logic.
2. `apps/vanphat_portal/frontend/src/App.vue`: Remove hardcoded client-side tax math (`Math.round(sub * 0.08)`) and cylinder cost assumptions, clean up redundant state, and streamline CSS.
3. `apps/vanphat_portal/frontend/src/components/ModalStep1Sale.vue`: Consolidate repetitive button classes, clean up customer debounce logic, and remove dead CSS.
4. `apps/vanphat_portal/frontend/src/components/DrawerStep2Director.vue`: Optimize 600+ lines of raw CSS, eliminate redundant watchers/formatters, and ensure clean props/event flow.

## Architecture Decisions
- **Strict SSOT**: All currency formatting and pricing figures come directly from backend responses (`vanphat_portal.api.bao_gia.*`). No client-side formula execution.
- **Visual Parity**: Keep exact dark-mode aesthetic (#0b0f17, industrial packaging theme, font-size 16px to prevent iOS auto-zoom).
- **CSS Optimization**: Consolidate repetitive utility classes, preserve CSS variables, eliminate dead selectors.
- **Atomic Execution**: Refactor each component one by one with build verification after each slice.

## Task List

### Phase 1: Login Page Refactor (`login.html`)
- [ ] Task 1: Clean up `login.html` CSS and JS hacks, retaining exact visual and autofill parity.

### Phase 2: Page Báo Giá Refactor (`App.vue`)
- [ ] Task 2: Remove client-side math, consolidate API callers, streamline state and CSS in `App.vue`.

### Phase 3: Modal 1 Refactor (`ModalStep1Sale.vue`)
- [ ] Task 3: Simplify switcher logic, search debounce, and CSS in `ModalStep1Sale.vue`.

### Phase 4: Drawer 2 Refactor (`DrawerStep2Director.vue`)
- [ ] Task 4: Simplify financial breakdown, material chips, watcher logic, and CSS in `DrawerStep2Director.vue`.

### Phase 5: Verification & Production Build
- [ ] Task 5: Verify Vite build (`yarn build`) and test frontend assets.

## Risks and Mitigations
| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Mobile autofill font zoom or white background flash in `login.html` | Medium | Retain pure CSS `-webkit-box-shadow: 0 0 0 50px #0f172a inset` and `font-size: 16px` without relying on flaky JS polling. |
| Breaking quotation calculation flow | High | Keep exact event names (`next`, `items-changed`, `submit`) and state shape between `App.vue`, `ModalStep1Sale.vue`, and `DrawerStep2Director.vue`. |
| Vite build failure | High | Run `yarn build` in `apps/vanphat_portal/frontend` after each modification. |
