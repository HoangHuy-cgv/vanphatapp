import path from 'path';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// Build target: ../vanphat_portal/public/frontend (+ entry copied to ../vanphat_portal/www/portal.html)
// ADR-007: Retire frappe-ui — dùng Vite + Vue thuần túy, zero external UI framework plugin.
// SPEC auth 2 mode (Sếp duyệt 2026-09-16): local build mode (vite dev) vào
// thẳng /portal không cần login; prod giữ chặn Guest ở portal.py (server).
// Vite-side only: plugin dev chèn window.__VP_BUILD_MODE__ vào index.html,
// CHỈ khi `vite serve` (apply: serve) — build prod không có flag.
function buildModeBypass() {
	return {
		name: 'vp-build-mode-bypass',
		apply: 'serve',
		transformIndexHtml(html) {
			return html.replace(
				'<div id="app">',
				'<script>window.__VP_BUILD_MODE__ = 1;</script>\n\t\t<div id="app">',
			);
		},
	};
}

export default defineConfig({
	plugins: [vue(), buildModeBypass()],
	server: {
		port: 8090,
		host: '0.0.0.0',
		allowedHosts: true,
		proxy: {
			'^/(api|assets|files|login|app)': {
				target: 'https://app.vanphat.io.vn',
				changeOrigin: true,
				secure: false,
			},
		},
	},
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src'),
		},
	},
	build: {
		outDir: '../vanphat_portal/public/frontend',
		emptyOutDir: true,
		// P5 (Sếp duyệt, Chrome mới nhất): về default baseline-widely-available
		// (= chrome111/edge111/firefox114/safari16.4, mốc 2026-01-01, vite.dev/config/build-options).
		// Xóa es2022 cứng + manualChunks vendor-vue (Vite/Rolldown tự split; issue #12209).
		chunkSizeWarningLimit: 500,
		reportCompressedSize: true,
		modulePreload: { polyfill: false },
	},
});
