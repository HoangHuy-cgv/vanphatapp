import path from 'path';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import frameworkUI from '@framework/ui/vite';

// Build target: ../vanphat_portal/public/frontend (+ entry copied to ../vanphat_portal/www/portal.html)
export default defineConfig({
	plugins: [vue(), frameworkUI()],
	server: { port: 8090, host: '0.0.0.0' },
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src'),
		},
	},
	build: {
		outDir: '../vanphat_portal/public/frontend',
		emptyOutDir: true,
		target: 'es2015',
	},
});
