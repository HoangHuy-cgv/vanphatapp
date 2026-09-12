# Todo List - Code Simplification & Cleanup

- [x] Task 1: Refactor and simplify `apps/vanphat_portal/vanphat_portal/www/login.html`
  - Acceptance: Clean, readable HTML/CSS/JS without brittle `setTimeout` layout hacks; exact visual styling and Frappe login submission preserved.
  - Verify: Check file diff, ensure no JS errors on load.
  - Files: `apps/vanphat_portal/vanphat_portal/www/login.html`

- [x] Task 2: Refactor and simplify `apps/vanphat_portal/frontend/src/App.vue`
  - Acceptance: Zero client-side arithmetic math (tax, cylinder total); streamline state management and scoped CSS.
  - Verify: `cd apps/vanphat_portal/frontend && yarn build`
  - Files: `apps/vanphat_portal/frontend/src/App.vue`

- [x] Task 3: Refactor and simplify `apps/vanphat_portal/frontend/src/components/ModalStep1Sale.vue`
  - Acceptance: Streamlined customer search timer, consolidated button styles, clean props/event emitting.
  - Verify: `cd apps/vanphat_portal/frontend && yarn build`
  - Files: `apps/vanphat_portal/frontend/src/components/ModalStep1Sale.vue`

- [x] Task 4: Refactor and simplify `apps/vanphat_portal/frontend/src/components/DrawerStep2Director.vue`
  - Acceptance: Concise CSS, clean material chip toggles, proper formatting, no dead code.
  - Verify: `cd apps/vanphat_portal/frontend && yarn build`
  - Files: `apps/vanphat_portal/frontend/src/components/DrawerStep2Director.vue`

- [x] Task 5: End-to-End Build & Visual Verification
  - Acceptance: Vite production build succeeds with 0 errors; static assets generated in `vanphat_portal/public/frontend/`.
  - Verify: `cd apps/vanphat_portal/frontend && yarn build`
  - Files: `apps/vanphat_portal/vanphat_portal/public/frontend/*`
