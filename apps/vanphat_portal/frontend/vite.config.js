import path from 'path';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import frameworkUI from '@framework/ui/vite';

// Build target: ../vanphat_portal/public/frontend (+ entry copied to ../vanphat_portal/www/portal.html)
export default defineConfig({
	plugins: [vue(), frameworkUI()],
	server: { port: 8090, host: '0.0.0.0', allowedHosts: true },
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
