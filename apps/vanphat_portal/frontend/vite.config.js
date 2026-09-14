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
		// S8: es2022 thay es2015 (Vite 6 + esbuild 0.25; Chrome 92+/Safari 15.4+);
		// baseline-widely-available là alias Vite mới, esbuild chưa hiểu → dùng es2022 tương đương
		target: 'es2022',
		chunkSizeWarningLimit: 170,
		rollupOptions: {
			output: {
				manualChunks: {
					'vendor-vue': ['vue', 'vue-router'],
				},
			},
		},
	},
});
