/** @type {import('tailwindcss').Config} */
// ADR-007: Retire frappe-ui — Tailwind v3 standalone, zero external UI preset.
// Portal dùng hex trực tiếp + CSS vars tự định nghĩa (portal.css); không còn
// preset/plugins/content-scan của frappe-ui (forms/typography/lucide/themePlugin).
export default {
	content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
};
