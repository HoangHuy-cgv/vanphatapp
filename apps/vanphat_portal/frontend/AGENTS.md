# AGENTS.md - Van Phat Portal Frontend Shell

## 1. Scope & Core Directive
- **Scope**: Covers all files under `apps/vanphat_portal/frontend/`.
- **Zero Business Logic (Strict SSOT)**:
  - NEVER implement packaging formulas, film consumption, GSM, scrap rates, cylinder step derivations, or pricing calculations in `.vue`, `.js`, or `.ts` files.
  - Frontend is STRICTLY a presentation shell. It captures user intent, dispatches API requests, and renders backend responses.
  - ALL calculations MUST resolve via backend API `vanphat_portal.api.quote.*`.

## 2. Tech Stack & Engineering Standards
- **Framework**: Vue 3 using Composition API with `<script setup>` and TypeScript. Options API is PROHIBITED.
- **UI Components**: MUST use official `frappe-ui` components (`Button`, `Dialog`, `FormControl`, `TextInput`, `Select`, `Badge`, `Tabs`, `ListView`) to maintain design consistency with Frappe ecosystem.
- **Community Pattern Leverage**: Generic list/detail views MUST reuse patterns and composables (`createListResource`, `useCall`) from `frappe/crm`. Unvetted dependencies or external bloatware (VoIP, mailers) are STRICTLY FORBIDDEN.
- **Styling**: Tailwind CSS adhering to Van Phat's Unified Industrial Dark tokens. All copied components MUST map to `#0b0f19` (base), `#161b22` (cards), `#1a1f27` (inputs), `#3a424e` (borders), `#4ea1e0` (accent).
- **Core Domain Isolation**: Core packaging workflows (`ModalStep1Sale`, `DrawerStep2Director`) MUST NOT be replaced by generic ERP forms.
- **Build Target**: Vite builds static bundle to `apps/vanphat_portal/vanphat_portal/public/frontend/` served by Frappe Nginx/Gunicorn. Zero-Node production runtime.

## 3. Data Fetching & State Management
- **API Dispatch**: MUST use `createResource` or `call()` from `frappe-ui` to communicate with backend whitelisted methods.
- **Debounce**: MUST debounce inputs that trigger backend recalculation (e.g., width, height, quantity) to prevent API throttling.
- **Async Handling**: MUST explicitly handle `loading`, `error`, and empty states for every resource call. Never assume instant network resolution.
- **Authentication**: Handle user sessions via `$session` or Frappe auth cookies; redirect unauthenticated users gracefully.

## 4. Verification & Testing
- **Runtime Verification**: MUST verify UI rendering, console cleanliness, and network payloads using `browser-testing-with-devtools` (Chrome DevTools MCP).
- **Unit Testing**: Component behavior and state machines tested with Vitest.
